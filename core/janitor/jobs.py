"""Janitor jobs — background project intelligence.

Pure-compute jobs (zero API calls, zero cost):
  - detect_test_gaps: files changed without tests
  - scan_code_smells: oversized files and long functions
  - detect_config_drift: uncommitted config changes
  - build_dependency_map: import graph ranked by impact

LLM jobs (free via openrouter/free, requires OPENROUTER_API_KEY):
  - summarize_session: extract decisions/blockers from events
  - mine_patterns: recurring files, errors, decisions across sessions
  - generate_onboarding: "state of the project" summary
  - enrich_commits: semantic tags for recent commits

All jobs run at session boundaries via hooks. No cron needed.
Pure-compute runs at SessionStart. LLM jobs run at SessionEnd.
"""

import json
import os
import re
import subprocess
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


# --- Helpers ---

def _run_git(*args, project_dir: str, timeout: int = 10) -> str:
    try:
        r = subprocess.run(
            ["git"] + list(args),
            capture_output=True, text=True, timeout=timeout, cwd=project_dir,
        )
        return r.stdout.strip() if r.returncode == 0 else ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def _janitor_dir(project_dir: str) -> Path:
    d = Path(project_dir) / ".janitor"
    d.mkdir(exist_ok=True)
    return d


def _read_json(name: str, project_dir: str) -> Optional[dict]:
    path = _janitor_dir(project_dir) / name
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def _write_json(name: str, data: dict, project_dir: str):
    path = _janitor_dir(project_dir) / name
    path.write_text(json.dumps(data, indent=2))


# --- Pure-Compute Jobs ---

def detect_test_gaps(project_dir: Optional[str] = None, commits_back: int = 5) -> dict:
    changed = _run_git("diff", f"HEAD~{commits_back}", "--name-only", project_dir=project_dir or os.getcwd())
    if not changed:
        return {"gap_count": 0, "gaps": []}

    SOURCE_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"}
    source_changed = [
        f for f in changed.split("\n")
        if any(f.endswith(ext) for ext in SOURCE_EXT)
        and "/test" not in f and "/tests/" not in f
        and not f.startswith("test_") and not f.endswith("_test.py")
    ]

    all_files = _run_git("ls-files", project_dir=project_dir or os.getcwd())
    test_files = {f for f in all_files.split("\n") if "test" in f.lower()}

    gaps = []
    for src in source_changed:
        stem = Path(src).stem
        candidates = [f"tests/test_{stem}.py", f"tests/test_{stem}.ts", f"tests/{stem}.test.ts"]
        if not any(c in test_files for c in candidates):
            gaps.append({"source_file": src})

    return {"gap_count": len(gaps), "gaps": gaps}


def scan_code_smells(
    project_dir: Optional[str] = None,
    max_file_lines: int = 500,
    max_func_lines: int = 100,
) -> dict:
    project_dir = project_dir or os.getcwd()
    py_files = _run_git("ls-files", "*.py", project_dir=project_dir)
    if not py_files:
        return {"oversized_file_count": 0, "oversized_function_count": 0, "oversized_files": [], "oversized_functions": []}

    oversized_files = []
    oversized_functions = []

    for filepath in py_files.split("\n"):
        full_path = Path(project_dir) / filepath
        if not full_path.exists():
            continue
        lines = full_path.read_text().split("\n")
        if len(lines) > max_file_lines:
            oversized_files.append({"path": filepath, "lines": len(lines)})

        func_starts = [i for i, line in enumerate(lines) if line.strip().startswith("def ") and line.strip().endswith(":")]
        for idx, start in enumerate(func_starts):
            end = func_starts[idx + 1] if idx + 1 < len(func_starts) else len(lines)
            if end - start > max_func_lines:
                name = lines[start].strip().split("(")[0].replace("def ", "")
                oversized_functions.append({"path": filepath, "function": name, "lines": end - start})

    return {
        "oversized_files": sorted(oversized_files, key=lambda x: x["lines"], reverse=True),
        "oversized_functions": sorted(oversized_functions, key=lambda x: x["lines"], reverse=True)[:20],
        "oversized_file_count": len(oversized_files),
        "oversized_function_count": len(oversized_functions),
    }


def detect_config_drift(project_dir: Optional[str] = None, config_dir: str = "config") -> dict:
    project_dir = project_dir or os.getcwd()
    if not (Path(project_dir) / config_dir).exists():
        return {"drift_count": 0, "drifted_file_names": []}

    tracked = _run_git("ls-files", "--", config_dir, project_dir=project_dir)
    if not tracked:
        return {"drift_count": 0, "drifted_file_names": []}

    drifted = []
    for f in tracked.split("\n"):
        if _run_git("diff", "HEAD", "--", f, project_dir=project_dir, timeout=5).strip():
            drifted.append(f)

    return {"drift_count": len(drifted), "drifted_file_names": drifted}


def build_dependency_map(project_dir: Optional[str] = None) -> dict:
    project_dir = project_dir or os.getcwd()
    py_files = _run_git("ls-files", "*.py", project_dir=project_dir)
    if not py_files:
        return {"files_with_imports": 0, "impact_ranking": []}

    import_pattern = re.compile(r'^(?:from\s+(\S+)\s+import|import\s+(\S+))')
    graph = {}

    for filepath in py_files.split("\n"):
        full_path = Path(project_dir) / filepath
        if not full_path.exists():
            continue
        file_imports = set()
        for line in full_path.read_text().split("\n"):
            if line.strip().startswith("#"):
                continue
            m = import_pattern.match(line.strip())
            if m:
                module = m.group(1) or m.group(2)
                if (Path(project_dir) / f"{module.replace('.', '/')}.py").exists():
                    file_imports.add(module)
        if file_imports:
            graph[filepath] = sorted(file_imports)

    reverse_deps = {}
    for filepath, imports in graph.items():
        for imp in imports:
            reverse_deps.setdefault(imp, []).append(filepath)

    impact_ranking = sorted(
        [{"file": f"{m.replace('.', '/')}.py", "downstream_count": len(deps)}
         for m, deps in reverse_deps.items()],
        key=lambda x: x["downstream_count"],
        reverse=True,
    )[:10]

    return {"files_with_imports": len(graph), "impact_ranking": impact_ranking}


# --- LLM Jobs (require OPENROUTER_API_KEY) ---

def summarize_session(project_dir: Optional[str] = None) -> dict:
    """Extract decisions, blockers, discoveries from recent events."""
    from core.janitor.worker import extract_structured

    project_dir = project_dir or os.getcwd()
    events_path = _janitor_dir(project_dir) / "events.jsonl"
    if not events_path.exists():
        return {"status": "empty", "decisions": [], "blockers": [], "discoveries": []}

    # Read last 30 events
    events = []
    with open(events_path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    events = events[-30:]

    if not events:
        return {"status": "empty", "decisions": [], "blockers": [], "discoveries": []}

    turn_text = "\n".join(
        f"[{e.get('turn', '?')}] ({e['type']}) {e['content'][:200]}"
        for e in events
    )

    return extract_structured(
        f"Analyze these session events and extract:\n\n{turn_text}\n\n"
        "Extract any:\n"
        "1. Decisions made (approach chosen, tech selected, etc.)\n"
        "2. Blockers (things that are stuck or waiting)\n"
        "3. Discoveries (things learned, bugs found, patterns noticed)\n"
        "If nothing found for a category, return empty list.",
        system="You are a session analyst. Extract structured data from development session logs. Be concise.",
        schema_hint='{"decisions": [{"what": str, "why": str}], "blockers": [{"what": str, "reason": str}], "discoveries": [{"what": str}]}',
    )


def mine_patterns(project_dir: Optional[str] = None, days_back: int = 7) -> dict:
    """Mine recurring patterns from session events. 1 LLM call."""
    from core.janitor.worker import extract_structured

    project_dir = project_dir or os.getcwd()
    events_path = _janitor_dir(project_dir) / "events.jsonl"
    if not events_path.exists():
        return {"status": "no_events"}

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days_back)).isoformat()
    events = []
    with open(events_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                if e.get("ts", "")[:19] >= cutoff[:19]:
                    events.append(e)
            except json.JSONDecodeError:
                continue

    if len(events) < 10:
        return {"status": "too_few_events", "event_count": len(events)}

    # Pre-compute frequency tables (no LLM needed)
    file_touches: dict[str, list[str]] = {}
    error_types: dict[str, int] = {}
    decisions: dict[str, int] = {}

    for e in events:
        if e["type"] in ("file_read", "file_written"):
            for f in e.get("files", []):
                file_touches.setdefault(f, []).append(e.get("session", ""))
        if e["type"] == "error":
            error_types[e["content"][:80]] = error_types.get(e["content"][:80], 0) + 1
        if e["type"] == "decision":
            decisions[e["content"][:80]] = decisions.get(e["content"][:80], 0) + 1

    hot_files = {f: s for f, s in file_touches.items() if len(set(s)) >= 3}
    recurring_errors = {k: v for k, v in error_types.items() if v >= 2}
    revisited_decisions = {k: v for k, v in decisions.items() if v >= 2}

    pattern_text = ""
    if hot_files:
        pattern_text += "## Hot Files (3+ sessions)\n"
        for f, sessions in hot_files.items():
            pattern_text += f"- {f}: {len(set(sessions))} sessions\n"
    if recurring_errors:
        pattern_text += "\n## Recurring Errors\n"
        for err, count in recurring_errors.items():
            pattern_text += f"- [{count}x] {err}\n"
    if revisited_decisions:
        pattern_text += "\n## Revisited Decisions\n"
        for d, count in revisited_decisions.items():
            pattern_text += f"- [{count}x] {d}\n"

    if not pattern_text.strip():
        return {"status": "no_patterns"}

    result = extract_structured(
        f"Analyze patterns from {days_back} days of development:\n\n{pattern_text}\n\n"
        f"Identify actionable insights. Events: {len(events)}",
        system="You are a development pattern analyst. Identify recurring issues and suggest systemic fixes.",
        schema_hint='{"patterns": [{"type": str, "description": str, "frequency": str, "recommendation": str}]}',
    )

    result["events_analyzed"] = len(events)
    return result


def generate_onboarding(project_dir: Optional[str] = None) -> dict:
    """Generate 'state of the project' summary from all janitor data. 1 LLM call."""
    from core.janitor.worker import call_free

    project_dir = project_dir or os.getcwd()
    sections: dict[str, str] = {}

    # Event stats
    events_path = _janitor_dir(project_dir) / "events.jsonl"
    if events_path.exists():
        total = decisions = blockers = 0
        with open(events_path) as f:
            for line in f:
                if '"type":"decision"' in line:
                    decisions += 1
                elif '"type":"blocker"' in line:
                    blockers += 1
                elif line.strip():
                    total += 1
        if total:
            sections["events"] = f"{total} events, {decisions} decisions, {blockers} blockers"

    # Gather pre-computed data
    for key, name in [("test_gaps", "test-gaps.json"), ("code_smells", "code-smells.json"),
                       ("config_drift", "config-drift.json"), ("dep_graph", "dep-graph.json")]:
        data = _read_json(name, project_dir)
        if not data:
            continue
        if key == "test_gaps" and data.get("gap_count", 0) > 0:
            sections[key] = f"{data['gap_count']} gaps: " + ", ".join(g["source_file"] for g in data["gaps"][:5])
        elif key == "code_smells" and (data.get("oversized_file_count", 0) > 0 or data.get("oversized_function_count", 0) > 0):
            sections[key] = f"{data['oversized_file_count']} oversized files, {data['oversized_function_count']} long functions"
        elif key == "config_drift" and data.get("drift_count", 0) > 0:
            sections[key] = "Drifted: " + ", ".join(data["drifted_file_names"])
        elif key == "dep_graph" and data.get("impact_ranking"):
            sections[key] = ", ".join(f'{t["file"]} ({t["downstream_count"]} deps)' for t in data["impact_ranking"][:3])

    # Previous patterns
    patterns = _read_json("patterns.json", project_dir)
    if patterns and patterns.get("patterns"):
        sections["patterns"] = "; ".join(p.get("description", "")[:80] for p in patterns["patterns"][:3])

    context_text = "\n".join(f"## {k}\n{v}" for k, v in sections.items())
    if not context_text.strip():
        return {"status": "no_data"}

    summary = call_free(
        f"Generate a concise 'state of the project' onboarding summary:\n\n{context_text}\n\n"
        "Output markdown with: Project Status, Active Blockers, Recent Activity, "
        "Attention Items, Patterns, Recommended Next Steps. 200 words max.",
        system="You are a project onboarding assistant. Generate clear, actionable summaries.",
        max_tokens=2048,
    )

    # Save to .janitor/onboarding.md
    _janitor_dir(project_dir).joinpath("onboarding.md").write_text(summary)

    # Auto-export to CLAUDE.local.md so context survives without janitor
    claude_local = Path(project_dir) / "CLAUDE.local.md"
    header = "<!-- Auto-generated by janitor. Edit freely — janitor overwrites daily. -->\n\n"
    claude_local.write_text(header + summary)

    return {"status": "ok", "summary_length": len(summary)}


def enrich_commits(project_dir: Optional[str] = None, commits_back: int = 3) -> dict:
    """Enrich recent commit messages with semantic tags. 1 LLM call per new commit."""
    from core.janitor.worker import extract_structured

    project_dir = project_dir or os.getcwd()

    hashes = _run_git("log", f"-{commits_back}", "--format=%H", "--no-merges", project_dir=project_dir)
    if not hashes:
        return {"enriched_count": 0}

    existing = _read_json("commit-enrichments.json", project_dir) or {}
    new_enrichments = {}

    for h in hashes.split("\n"):
        if h in existing:
            continue
        msg = _run_git("log", "-1", "--format=%s", h, project_dir=project_dir)
        diff = _run_git("diff", f"{h}~1..{h}", "--stat", project_dir=project_dir, timeout=10)

        result = extract_structured(
            f"Enrich this git commit:\n\nMessage: {msg}\nChanged files:\n{diff}\n\nProvide summary and tags.",
            system="You are a commit analyzer. Extract meaning and categorize briefly.",
            schema_hint='{"summary": str, "tags": [str], "category": str}',
        )
        new_enrichments[h] = {"hash": h[:12], "message": msg, "enriched": result}

    if new_enrichments:
        existing.update(new_enrichments)
        _write_json("commit-enrichments.json", existing, project_dir)

    return {"enriched_count": len(new_enrichments), "total_enriched": len(existing)}


# --- Task Sufficiency Evaluator ---

EVAL_THRESHOLD = 0.75
EVAL_CONTEXT_BUDGET = 18000  # chars, leaving room for system prompt


def _parse_eval_result(raw_result: dict) -> dict:
    """Parse evaluation result with fallbacks for unreliable free model output."""
    if "score" in raw_result:
        try:
            score = float(raw_result["score"])
        except (ValueError, TypeError):
            score = 0.5
        score = max(0.0, min(1.0, score))
        return {
            "score": score,
            "feedback": raw_result.get("feedback", "")[:500],
            "issues": raw_result.get("issues", []),
            "status": "parsed",
        }

    # Fallback: try to extract score from unstructured text
    text = raw_result.get("raw", "")
    if not text:
        return {"score": 0.5, "feedback": "Evaluation returned empty", "issues": [], "status": "empty"}

    # Try common patterns: "score: 0.7", "7/10", "70%"
    score = 0.5
    m = re.search(r'(?:score|rating|confidence)[:\s]+(\d+\.?\d*)', text, re.I)
    if m:
        val = float(m.group(1))
        score = min(val / 10.0, 1.0) if val > 1.0 else val
    else:
        frac = re.search(r'(\d+)/10', text)
        if frac:
            score = float(frac.group(1)) / 10.0
        pct = re.search(r'(\d+)\s*%', text)
        if pct:
            score = float(pct.group(1)) / 100.0

    return {
        "score": max(0.0, min(1.0, score)),
        "feedback": text[:500],
        "issues": [],
        "status": "fallback_parse",
    }


def evaluate_task_sufficiency(project_dir: Optional[str] = None) -> dict:
    """Evaluate whether completed work in the session was sufficient. 1 LLM call."""
    from core.janitor.worker import extract_structured

    project_dir = project_dir or os.getcwd()
    janitor_dir = _janitor_dir(project_dir)
    events_path = janitor_dir / "events.jsonl"

    if not events_path.exists():
        return {"status": "no_events"}

    # Collect current session events (file_written + commit)
    session_events = []
    files_changed: set[str] = set()
    commit_messages: list[str] = []

    with open(events_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e["type"] in ("file_written", "commit", "action_taken"):
                session_events.append(e)
                if e["type"] == "file_written":
                    for fp in e.get("files", []):
                        files_changed.add(fp)
                elif e["type"] == "commit":
                    commit_messages.append(e["content"])

    if not session_events:
        return {"status": "no_work_done"}

    # Only use recent events (last 60) to stay in budget
    session_events = session_events[-60:]

    # 1. Session activity text
    activity_lines = []
    for e in session_events:
        activity_lines.append(f"  ({e['type']}) {e['content'][:150]}")
    session_activity = "\n".join(activity_lines)

    # 2. Git diff for changed files
    diff_budget = EVAL_CONTEXT_BUDGET - len(session_activity) - 4000  # reserve for state + rubric
    diff_text = ""
    if files_changed and diff_budget > 2000:
        # Determine how many commits back to look
        commits_back = min(len(commit_messages) + 1, 5)
        if commits_back < 2:
            commits_back = 2
        changed_list = list(files_changed)[:15]
        diff = _run_git("diff", f"HEAD~{commits_back}", "--", *changed_list,
                        project_dir=project_dir, timeout=10)
        if len(diff) > diff_budget:
            keep = diff_budget // 2
            diff_text = diff[:keep] + "\n... [truncated] ...\n" + diff[-keep:]
        else:
            diff_text = diff

    # 3. Project context (test gaps, code smells, session summary)
    context_parts = []
    tg = _read_json("test-gaps.json", project_dir)
    if tg and tg.get("gap_count", 0) > 0:
        files = [g["source_file"] for g in tg["gaps"][:8]]
        context_parts.append(f"Test gaps ({tg['gap_count']}): {', '.join(files)}")

    cs = _read_json("code-smells.json", project_dir)
    if cs:
        items = []
        for f in cs.get("oversized_files", [])[:3]:
            items.append(f"{f['path']} ({f['lines']}L)")
        for fn in cs.get("oversized_functions", [])[:3]:
            items.append(f"{fn['function']}() in {fn['path']} ({fn['lines']}L)")
        if items:
            context_parts.append(f"Code smells: {', '.join(items)}")

    summary = _read_json("last-summary.json", project_dir)
    if summary:
        summary_parts = []
        if summary.get("decisions"):
            summary_parts.append("Decisions: " + "; ".join(d.get("what", "")[:80] for d in summary["decisions"][:3]))
        if summary.get("blockers"):
            summary_parts.append("Blockers: " + "; ".join(b.get("what", "")[:80] for b in summary["blockers"][:3]))
        if summary_parts:
            context_parts.append("Session summary: " + " | ".join(summary_parts))

    project_context = "\n".join(context_parts) if context_parts else "No known issues."

    # Build the prompt
    chars_used = len(session_activity) + len(diff_text) + len(project_context)
    prompt = (
        "## Session Activity\n"
        f"{session_activity}\n\n"
        "## Code Changes\n"
        f"{diff_text or '(no diff available)'}\n\n"
        "## Project Context\n"
        f"{project_context}\n\n"
        "## Scoring Rubric\n"
        "- 1.0: Fully complete. All requirements met, tests pass, no regressions.\n"
        "- 0.8: Minor gaps. Works but missing edge case handling or docs.\n"
        "- 0.6: Significant gaps. Core functionality works but important aspects missing.\n"
        "- 0.4: Partial. Some work done but major requirements unmet.\n"
        "- 0.2: Minimal. Barely started or mostly wrong approach.\n"
        "- 0.0: Nothing useful produced.\n\n"
        "Evaluate the above work. Consider:\n"
        "1. Does the implementation match the apparent intent?\n"
        "2. Are edge cases handled?\n"
        "3. Is there test coverage for new code?\n"
        "4. Are there obvious bugs or regressions?\n"
        "5. Does it follow existing code patterns in the project?"
    )

    result = extract_structured(
        prompt,
        system="You are a code review evaluator. Given session activity and code changes, "
               "score whether the work was completed sufficiently. Be critical but fair.",
        schema_hint='{"score": float, "feedback": str, "issues": [str]}',
    )

    parsed = _parse_eval_result(result)
    parsed["chars_used"] = chars_used
    parsed["session"] = session_events[0].get("session", "unknown") if session_events else "unknown"
    parsed["ts"] = datetime.now(timezone.utc).isoformat()

    # Extract model from usage log (last entry)
    usage_path = janitor_dir / "usage.jsonl"
    if usage_path.exists():
        try:
            last_usage_line = usage_path.read_text().strip().split("\n")[-1]
            last_usage = json.loads(last_usage_line)
            parsed["model"] = last_usage.get("model", "unknown")
        except (json.JSONDecodeError, IndexError):
            parsed["model"] = "unknown"

    # Write to eval log (always)
    eval_log = janitor_dir / "task-evals.jsonl"
    with open(eval_log, "a") as f:
        f.write(json.dumps(parsed, separators=(",", ":")) + "\n")

    # Write to redo queue if below threshold
    if parsed["score"] < EVAL_THRESHOLD:
        redo_path = janitor_dir / "redo-queue.json"
        existing = []
        if redo_path.exists():
            try:
                existing = json.loads(redo_path.read_text())
            except json.JSONDecodeError:
                existing = []
        existing.append({
            "ts": parsed["ts"],
            "session": parsed["session"],
            "score": parsed["score"],
            "task_summary": f"{len(files_changed)} files changed, {len(commit_messages)} commits",
            "feedback": parsed["feedback"],
            "issues": parsed.get("issues", []),
        })
        redo_path.write_text(json.dumps(existing, indent=2))

    return parsed


# --- Event Stats ---

def event_stats(project_dir: Optional[str] = None) -> dict:
    project_dir = project_dir or os.getcwd()
    events_path = _janitor_dir(project_dir) / "events.jsonl"
    if not events_path.exists():
        return {"total": 0, "decisions": 0, "blockers": 0}

    total = decisions = blockers = 0
    with open(events_path) as f:
        for line in f:
            if not line.strip():
                continue
            total += 1
            if '"type":"decision"' in line:
                decisions += 1
            elif '"type":"blocker"' in line:
                blockers += 1
    return {"total": total, "decisions": decisions, "blockers": blockers}


# --- SessionStart: run pure-compute + inject results ---

def run_session_start(project_dir: Optional[str] = None) -> str:
    """Run all pure-compute jobs and return formatted context for injection.

    Called by context.sh at SessionStart. Reads any pre-computed LLM results.
    Returns a string for Claude's context, or empty string if nothing to report.
    """
    project_dir = project_dir or os.getcwd()
    if not (Path(project_dir) / ".git").exists():
        return ""

    parts = []

    # Onboarding summary (from previous session's LLM job, if exists)
    onboarding_path = _janitor_dir(project_dir) / "onboarding.md"
    if onboarding_path.exists():
        age = time.time() - onboarding_path.stat().st_mtime
        if age < 86400:  # fresh within 24h
            preview = onboarding_path.read_text()[:500].replace("\n", " ")
            parts.append(f"ONBOARDING: {preview}")

    # Event stats
    stats = event_stats(project_dir)
    if stats["total"] > 0:
        detail = []
        if stats["decisions"] > 0:
            detail.append(f"{stats['decisions']} decisions")
        if stats["blockers"] > 0:
            detail.append(f"{stats['blockers']} blockers")
        parts.append(f"{stats['total']} events" + (f" ({', '.join(detail)})" if detail else ""))

    # Pure-compute jobs (always run, always fresh)
    tg = detect_test_gaps(project_dir)
    _write_json("test-gaps.json", tg, project_dir)
    if tg["gap_count"] > 0:
        files = [g["source_file"] for g in tg["gaps"][:5]]
        parts.append(f"test gaps: {tg['gap_count']} — {', '.join(files)}")

    cs = scan_code_smells(project_dir)
    _write_json("code-smells.json", cs, project_dir)
    if cs["oversized_file_count"] > 0 or cs["oversized_function_count"] > 0:
        parts.append(f"{cs['oversized_file_count']} oversized files, {cs['oversized_function_count']} long functions")

    cd = detect_config_drift(project_dir)
    _write_json("config-drift.json", cd, project_dir)
    if cd["drift_count"] > 0:
        parts.append(f"config drift: {', '.join(cd['drifted_file_names'][:5])}")

    dg = build_dependency_map(project_dir)
    _write_json("dep-graph.json", dg, project_dir)
    if dg["impact_ranking"]:
        top = dg["impact_ranking"][:3]
        impact_str = ", ".join(f'{t["file"]} ({t["downstream_count"]} deps)' for t in top)
        parts.append(f"high-impact: {impact_str}")

    # Patterns (from previous LLM run, if exists and fresh)
    patterns_path = _janitor_dir(project_dir) / "patterns.json"
    if patterns_path.exists():
        age = time.time() - patterns_path.stat().st_mtime
        if age < 86400:  # stale after 24h
            patterns = _read_json("patterns.json", project_dir)
            if patterns and patterns.get("patterns"):
                parts.append(f"patterns: {'; '.join(p.get('description', '')[:60] for p in patterns['patterns'][:3])}")

    # Last eval score (from previous session)
    evals_path = _janitor_dir(project_dir) / "task-evals.jsonl"
    if evals_path.exists():
        try:
            last_line = evals_path.read_text().strip().split("\n")[-1]
            last_eval = json.loads(last_line)
            score = last_eval.get("score", "?")
            session = last_eval.get("session", "?")
            parts.append(f"last eval: score={score} (session {session})")
        except (json.JSONDecodeError, IndexError):
            pass

    # Redo signals (from evaluator, if score was below threshold)
    redo_path = _janitor_dir(project_dir) / "redo-queue.json"
    if redo_path.exists():
        try:
            redo_items = json.loads(redo_path.read_text())
            if redo_items:
                for item in redo_items[:3]:
                    score = item.get("score", "?")
                    feedback = item.get("feedback", "")[:200]
                    parts.append(f"REDO: score={score} — {feedback}")
                redo_path.write_text("[]")  # clear after reading
        except json.JSONDecodeError:
            pass

    if not parts:
        return ""

    return "JANITOR: " + " | ".join(parts)


# --- SessionEnd: run LLM jobs ---

def run_session_end(project_dir: Optional[str] = None) -> None:
    """Run LLM jobs at session end. Requires OPENROUTER_API_KEY.

    - summarize_session: always (if events exist)
    - enrich_commits: if new commits
    - mine_patterns + generate_onboarding: once per day (24h gate)
    """
    project_dir = project_dir or os.getcwd()
    if not (Path(project_dir) / ".git").exists():
        return

    janitor_dir = _janitor_dir(project_dir)
    events_path = janitor_dir / "events.jsonl"

    # Need events to do anything
    if not events_path.exists():
        return

    # Check for API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        return  # silently skip — pure-compute already ran at session start

    try:
        # Summarize session
        summary = summarize_session(project_dir)
        if summary.get("decisions") or summary.get("blockers"):
            janitor_dir.joinpath("last-summary.json").write_text(json.dumps(summary, indent=2))

        # Evaluate task sufficiency (NEW)
        try:
            evaluate_task_sufficiency(project_dir)
        except Exception:
            pass  # non-critical

        # Enrich commits
        try:
            enrich_commits(project_dir)
        except Exception:
            pass  # non-critical

        # Daily gate for expensive jobs
        daily_gate = janitor_dir / "last-daily-run"
        skip_daily = False
        if daily_gate.exists() and (time.time() - daily_gate.stat().st_mtime) < 86400:
            skip_daily = True

        if not skip_daily:
            try:
                patterns = mine_patterns(project_dir)
                if patterns.get("patterns"):
                    _write_json("patterns.json", patterns, project_dir)

                generate_onboarding(project_dir)
                daily_gate.write_text(str(time.time()))
            except Exception:
                pass  # non-critical

    except Exception:
        pass  # LLM jobs are best-effort, never block session end
