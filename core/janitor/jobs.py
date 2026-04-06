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
