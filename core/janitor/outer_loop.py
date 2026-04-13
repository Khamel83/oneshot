"""V2 outer loop: suggestions.json → proposed patches → eval in worktree → PR evidence.

Reads .janitor/suggestions.json (written by generate_improvement_suggestions),
generates candidate patches for lane routing or task schema config, runs eval
in an isolated git worktree to measure improvement, and writes a PR evidence
report to .janitor/outer-loop-result.json.

This is advisory only — it never pushes a branch or opens a PR automatically.
A human reviews .janitor/outer-loop-result.json and decides whether to apply
the patch.

Usage:
    python -m core.janitor.outer_loop [--project-dir PATH] [--verbose] [--dry-run]

Output written to .janitor/outer-loop-result.json:
    {
      "generated_at": "...",
      "suggestions_processed": 3,
      "patches": [
        {
          "suggestion_type": "lane_preference",
          "description": "Move gemini_cli before codex in research lane",
          "diff": "--- a/config/lanes.yaml\n+++ b/config/lanes.yaml\n...",
          "eval_baseline": {"routing_correctness": 0.95},
          "eval_patched": {"routing_correctness": 0.97},
          "improvement": true,
          "status": "ready_to_apply"
        }
      ]
    }
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _find_git_root(start: Optional[str] = None) -> Path:
    p = Path(start or os.getcwd())
    for candidate in [p] + list(p.parents):
        if (candidate / ".git").exists():
            return candidate
    return p


def _janitor_dir(project_dir: str) -> Path:
    d = Path(project_dir) / ".janitor"
    d.mkdir(exist_ok=True)
    return d


def _log(msg: str, verbose: bool = False):
    if verbose:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"[{ts}] [outer-loop] {msg}", flush=True)


def _run(args: list[str], cwd: str, timeout: int = 60) -> tuple[int, str, str]:
    try:
        r = subprocess.run(args, capture_output=True, text=True, cwd=cwd, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", f"timeout after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


def _load_suggestions(project_dir: str) -> list[dict]:
    path = _janitor_dir(project_dir) / "suggestions.json"
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data.get("suggestions", [])
    except (json.JSONDecodeError, OSError):
        return []


def _run_eval(worktree_path: str, verbose: bool) -> dict:
    """Run scripts/eval.sh in a worktree and return parsed metrics.

    Returns dict with at minimum {"routing_correctness": float, "classification_accuracy": float}.
    Returns empty dict if eval fails.
    """
    eval_script = os.path.join(worktree_path, "scripts", "eval.sh")
    if not os.path.exists(eval_script):
        return {}

    rc, out, err = _run(
        ["bash", eval_script, "--json"],
        cwd=worktree_path,
        timeout=120
    )
    if rc != 0:
        if verbose:
            _log(f"eval.sh failed (rc={rc}): {err[:200]}")
        # Try parsing partial JSON output
        pass

    # Try to extract a JSON metrics object from stdout
    for line in reversed(out.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                continue
    return {}


def _create_worktree(project_dir: str, branch_name: str) -> Optional[str]:
    """Create a git worktree for isolated patch testing. Returns worktree path or None."""
    worktree_path = tempfile.mkdtemp(prefix="oneshot-outer-loop-")
    rc, _, err = _run(
        ["git", "worktree", "add", "--detach", worktree_path],
        cwd=project_dir,
        timeout=30
    )
    if rc != 0:
        shutil.rmtree(worktree_path, ignore_errors=True)
        return None
    return worktree_path


def _remove_worktree(project_dir: str, worktree_path: str):
    """Remove a git worktree cleanly."""
    _run(["git", "worktree", "remove", "--force", worktree_path], cwd=project_dir)
    shutil.rmtree(worktree_path, ignore_errors=True)


def _generate_patch_for_suggestion(suggestion: dict, project_dir: str, verbose: bool) -> Optional[str]:
    """Use the provider pool to generate a patch diff for a suggestion.

    Returns a unified diff string, or None if generation failed.
    """
    stype = suggestion.get("type", "")
    desc = suggestion.get("description", "")
    proposed = suggestion.get("proposed_change", "")
    target_file = suggestion.get("file", "")

    if not proposed or not target_file:
        return None

    # Read the target file
    target_path = Path(project_dir) / target_file
    if not target_path.exists():
        return None

    current_content = target_path.read_text()

    prompt = f"""You are helping improve an AI routing harness configuration.

Suggestion type: {stype}
Description: {desc}
Proposed change: {proposed}
Target file: {target_file}

Current file content:
```
{current_content[:3000]}
```

Generate a minimal, correct unified diff (git diff format) that implements the proposed change.
Output ONLY the diff — no explanation, no markdown fences. Start with "--- a/{target_file}".
If the change cannot be cleanly expressed as a diff, output "SKIP".
"""

    try:
        sys.path.insert(0, str(REPO_ROOT))
        from core.janitor.provider_pool import call_janitor
        raw = call_janitor(prompt, max_tokens=1024, timeout=30)
        raw = raw.strip()
        if raw == "SKIP" or not raw.startswith("---"):
            return None
        return raw
    except Exception as e:
        if verbose:
            _log(f"Patch generation failed for '{desc}': {e}")
        return None


def _apply_patch(diff: str, worktree_path: str) -> bool:
    """Apply a unified diff to the worktree. Returns True on success."""
    try:
        result = subprocess.run(
            ["git", "apply", "--whitespace=nowarn", "-"],
            input=diff, capture_output=True, text=True,
            cwd=worktree_path, timeout=15
        )
        return result.returncode == 0
    except Exception:
        return False


def run_outer_loop(
    project_dir: str,
    verbose: bool = False,
    dry_run: bool = False,
) -> dict:
    """Execute one outer loop pass. Returns result dict."""
    suggestions = _load_suggestions(project_dir)
    if not suggestions:
        _log("No suggestions found — run generate_improvement_suggestions() first", verbose)
        return {"status": "no_suggestions", "patches": []}

    _log(f"Processing {len(suggestions)} suggestions", verbose)

    # Run baseline eval on the current repo
    baseline_metrics: dict = {}
    if not dry_run:
        _log("Running baseline eval...", verbose)
        baseline_metrics = _run_eval(str(REPO_ROOT), verbose)
        _log(f"Baseline metrics: {baseline_metrics}", verbose)

    patches = []
    worktrees_created: list[tuple[str, str]] = []  # (project_dir, worktree_path)

    for i, suggestion in enumerate(suggestions):
        desc = suggestion.get("description", f"suggestion-{i}")
        confidence = suggestion.get("confidence", 0.0)

        # Skip low-confidence suggestions
        if confidence < 0.7:
            _log(f"Skip '{desc}' (confidence={confidence:.2f} < 0.70)", verbose)
            patches.append({
                "suggestion_type": suggestion.get("type"),
                "description": desc,
                "status": "skipped_low_confidence",
                "confidence": confidence,
            })
            continue

        _log(f"Processing suggestion {i+1}/{len(suggestions)}: {desc}", verbose)

        if dry_run:
            patches.append({
                "suggestion_type": suggestion.get("type"),
                "description": desc,
                "proposed_change": suggestion.get("proposed_change"),
                "file": suggestion.get("file"),
                "confidence": confidence,
                "status": "dry_run",
            })
            continue

        # Generate patch
        diff = _generate_patch_for_suggestion(suggestion, project_dir, verbose)
        if not diff:
            patches.append({
                "suggestion_type": suggestion.get("type"),
                "description": desc,
                "status": "patch_generation_failed",
                "confidence": confidence,
            })
            continue

        # Create isolated worktree and apply patch
        worktree_path = _create_worktree(project_dir, f"outer-loop-{i}")
        if not worktree_path:
            patches.append({
                "suggestion_type": suggestion.get("type"),
                "description": desc,
                "status": "worktree_failed",
                "confidence": confidence,
            })
            continue

        worktrees_created.append((project_dir, worktree_path))
        applied = _apply_patch(diff, worktree_path)

        if not applied:
            patches.append({
                "suggestion_type": suggestion.get("type"),
                "description": desc,
                "diff": diff,
                "status": "patch_apply_failed",
                "confidence": confidence,
            })
            continue

        # Run eval in patched worktree
        _log(f"Running eval in worktree for '{desc}'...", verbose)
        patched_metrics = _run_eval(worktree_path, verbose)

        # Compare metrics
        improvement = _is_improvement(baseline_metrics, patched_metrics)
        status = "ready_to_apply" if improvement else "no_improvement"

        patch_result = {
            "suggestion_type": suggestion.get("type"),
            "description": desc,
            "proposed_change": suggestion.get("proposed_change"),
            "file": suggestion.get("file"),
            "diff": diff,
            "confidence": confidence,
            "eval_baseline": baseline_metrics,
            "eval_patched": patched_metrics,
            "improvement": improvement,
            "status": status,
        }
        patches.append(patch_result)
        _log(f"  Result: {status} (improvement={improvement})", verbose)

    # Clean up all worktrees
    for pd, wt in worktrees_created:
        _remove_worktree(pd, wt)

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_dir": project_dir,
        "suggestions_processed": len(suggestions),
        "patches": patches,
        "ready_count": sum(1 for p in patches if p.get("status") == "ready_to_apply"),
    }

    # Write to .janitor/outer-loop-result.json
    out_path = _janitor_dir(project_dir) / "outer-loop-result.json"
    try:
        tmp = out_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(result, indent=2))
        tmp.replace(out_path)
        _log(f"Result written to {out_path}", verbose)
    except OSError as e:
        _log(f"Failed to write result: {e}", verbose)

    return result


def _is_improvement(baseline: dict, patched: dict) -> bool:
    """Return True if patched metrics are at least as good as baseline with ≥1 improvement."""
    if not baseline or not patched:
        return False

    metrics = ["routing_correctness", "classification_accuracy", "risk_accuracy"]
    improved = 0
    regressed = 0

    for m in metrics:
        if m not in baseline or m not in patched:
            continue
        delta = patched[m] - baseline[m]
        if delta > 0.01:
            improved += 1
        elif delta < -0.05:   # allow ≤5% regression
            regressed += 1

    return improved >= 1 and regressed == 0


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Outer loop V2: suggestions → patches → eval evidence"
    )
    parser.add_argument("--project-dir", default=None,
                        help="Project root (default: auto-detect from CWD)")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be patched without running eval")
    args = parser.parse_args()

    start_dir = args.project_dir or os.getcwd()
    project_dir = str(_find_git_root(start_dir))

    result = run_outer_loop(project_dir, verbose=args.verbose, dry_run=args.dry_run)

    ready = result.get("ready_count", 0)
    total = result.get("suggestions_processed", 0)
    print(f"Outer loop complete: {ready}/{total} patches ready to apply")
    if ready:
        print(f"Review: {project_dir}/.janitor/outer-loop-result.json")


if __name__ == "__main__":
    main()
