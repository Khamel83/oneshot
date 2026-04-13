"""Janitor jobs — background project intelligence.

Pure-compute jobs (zero API calls, zero cost):
  - detect_test_gaps: files changed without tests
  - scan_code_smells: oversized files and long functions
  - detect_config_drift: uncommitted config changes
  - build_dependency_map: import graph ranked by impact
  - analyze_dispatch_traces: aggregate eval/traces/ into worker stats
  - monitor_provider_health: check remaining quota per provider

LLM jobs (via provider pool — openrouter/free + qwen_studio + gemini_api + codex):
  - summarize_session: extract decisions/blockers from events
  - mine_patterns: recurring files, errors, decisions across sessions
  - generate_onboarding: "state of the project" summary
  - enrich_commits: semantic tags for recent commits
  - generate_improvement_suggestions: routing improvements from trace stats

All jobs run at session boundaries via hooks AND via cron (core.janitor.cron).
Pure-compute runs at SessionStart. LLM jobs run at SessionEnd and on cron schedule.
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
def detect_project_type(project_dir: Optional[str] = None) -> str:
    """Classify project as 'code', 'document', or 'hybrid' based on repo contents."""
    project_dir = project_dir or os.getcwd()
    p = Path(project_dir)

    code_exts = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb", ".c", ".cpp", ".h"}
    doc_exts = {".md", ".txt", ".rst", ".csv", ".json", ".yaml", ".yml", ".toml", ".org", ".html"}
    build_markers = {"pyproject.toml", "setup.py", "package.json", "Cargo.toml", "go.mod",
                     "vercel.json", "Makefile", "CMakeLists.txt", "tsconfig.json"}

    all_files = _run_git("ls-files", project_dir=project_dir)
    if not all_files:
        return "document"

    code_files = doc_files = 0
    has_build = False

    for f in all_files.split("\n"):
        if not f:
            continue
        ext = Path(f).suffix.lower()
        basename = Path(f).name
        if ext in code_exts:
            code_files += 1
        if ext in doc_exts:
            doc_files += 1
        if basename in build_markers:
            has_build = True

    if code_files > 5 and has_build:
        return "hybrid" if doc_files > code_files * 2 else "code"
    if code_files >= 3 and has_build:
        return "code"
    if code_files > 0 and doc_files > 0:
        return "hybrid" if code_files >= 3 else "document"
    if code_files >= 3:
        return "code"
    return "document"


def _data_hash(sections: dict) -> str:
    import hashlib
    blob = json.dumps(sections, sort_keys=True)
    return hashlib.md5(blob.encode()).hexdigest()[:12]


def _onboarding_is_fresh(project_dir: str, state_hash: str, max_age_hours: int = 1) -> bool:
    state_path = _janitor_dir(project_dir) / "onboarding-state.json"
    if not state_path.exists():
        return False
    try:
        state = json.loads(state_path.read_text())
    except (json.JSONDecodeError, OSError):
        return False
    if state.get("hash") != state_hash:
        return False
    last_gen = state.get("ts", 0)
    events_path = _janitor_dir(project_dir) / "events.jsonl"
    if events_path.exists():
        with open(events_path) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    evt = json.loads(line)
                    evt_ts = evt.get("ts", "")
                    if evt_ts and evt_ts > time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(last_gen)):
                        return False
                except (json.JSONDecodeError, ValueError):
                    continue
    return (time.time() - last_gen) < (max_age_hours * 3600)



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



# --- Pure-Compute Jobs: Document Signals ---


def detect_document_staleness(project_dir: Optional[str] = None, stale_days: int = 30) -> dict:
    """Find documents not modified in N days, ranked by staleness."""
    project_dir = project_dir or os.getcwd()
    doc_exts = {".md", ".txt", ".rst", ".csv", ".json", ".yaml", ".yml", ".org", ".html"}
    cutoff = time.time() - (stale_days * 86400)

    all_files = _run_git("ls-files", project_dir=project_dir)
    stale = []
    fresh = 0

    for f in all_files.split("\n"):
        if not f or Path(f).suffix.lower() not in doc_exts:
            continue
        full_path = Path(project_dir) / f
        if not full_path.exists():
            continue
        try:
            mtime = full_path.stat().st_mtime
        except OSError:
            continue
        if mtime < cutoff:
            days_ago = int((time.time() - mtime) / 86400)
            stale.append({"file": f, "days_since_edit": days_ago, "last_modified": datetime.fromtimestamp(mtime).isoformat()[:10]})
        else:
            fresh += 1

    stale.sort(key=lambda x: x["days_since_edit"], reverse=True)
    return {"stale_count": len(stale), "fresh_count": fresh, "stale_threshold_days": stale_days, "stale_files": stale[:20]}


def detect_orphan_documents(project_dir: Optional[str] = None) -> dict:
    """Find documents not referenced/linked from any other file."""
    project_dir = project_dir or os.getcwd()
    doc_exts = {".md", ".txt", ".rst", ".org", ".html"}
    all_files = _run_git("ls-files", project_dir=project_dir)

    referenced = set()
    link_pattern = re.compile(r'(?:\[[^\]]*\]\(([^)]+)\)|\[\[([^\]]+)\]\]|include\s+["\']([^"\']+)["\'])', re.IGNORECASE)

    doc_files = [f for f in all_files.split("\n") if f and Path(f).suffix.lower() in doc_exts]
    non_binary = [f for f in all_files.split("\n") if f and Path(f).suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz"}]

    for f in non_binary:
        full_path = Path(project_dir) / f
        if not full_path.exists():
            continue
        try:
            content = full_path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        for match in link_pattern.finditer(content):
            ref = match.group(1) or match.group(2) or match.group(3) or ""
            ref_clean = Path(ref).stem.lower() if ref else ""
            if ref_clean:
                referenced.add(ref_clean)

    orphans = []
    for f in doc_files:
        stem = Path(f).stem.lower()
        if stem in {"readme", "index", "license", "licence"}:
            continue
        if stem not in referenced:
            orphans.append(f)

    return {"orphan_count": len(orphans), "orphan_files": orphans[:20], "total_documents": len(doc_files)}


def detect_document_clusters(project_dir: Optional[str] = None) -> dict:
    """Group documents by directory structure to identify topic clusters."""
    project_dir = project_dir or os.getcwd()
    doc_exts = {".md", ".txt", ".rst", ".csv", ".json", ".yaml", ".yml", ".org", ".html"}

    all_files = _run_git("ls-files", project_dir=project_dir)
    clusters: dict[str, list[str]] = {}

    for f in all_files.split("\n"):
        if not f or Path(f).suffix.lower() not in doc_exts:
            continue
        parts = Path(f).parts
        top_dir = parts[0] if len(parts) > 1 else "(root)"
        clusters.setdefault(top_dir, []).append(f)

    sorted_clusters = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)
    cluster_list = [{"directory": d, "file_count": len(files), "files": files[:5]} for d, files in sorted_clusters[:10]]

    return {"cluster_count": len(clusters), "total_documents": sum(len(v) for v in clusters.values()), "clusters": cluster_list}


def detect_size_outliers(project_dir: Optional[str] = None, threshold_kb: int = 100) -> dict:
    """Find unusually large files that may need splitting or attention."""
    project_dir = project_dir or os.getcwd()
    threshold_bytes = threshold_kb * 1024

    all_files = _run_git("ls-files", project_dir=project_dir)
    outliers = []

    for f in all_files.split("\n"):
        if not f:
            continue
        full_path = Path(project_dir) / f
        if not full_path.exists():
            continue
        try:
            size = full_path.stat().st_size
        except OSError:
            continue
        if size > threshold_bytes:
            try:
                with open(full_path, "rb") as fh:
                    is_binary = b"\x00" in fh.read(8192)
            except OSError:
                is_binary = True
            outliers.append({"file": f, "size_kb": round(size / 1024, 1), "type": "binary" if is_binary else "text"})

    outliers.sort(key=lambda x: x["size_kb"], reverse=True)
    return {"outlier_count": len(outliers), "threshold_kb": threshold_kb, "outliers": outliers[:20]}


def detect_recent_document_activity(project_dir: Optional[str] = None, days: int = 7) -> dict:
    """Track recent document changes with who changed what."""
    project_dir = project_dir or os.getcwd()
    doc_exts = {".md", ".txt", ".rst", ".csv", ".json", ".yaml", ".yml", ".org", ".html"}
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    log = _run_git("log", f"--since={since}", "--name-only", "--format=%H %an", project_dir=project_dir)
    if not log:
        return {"changes_count": 0, "recent_changes": []}

    changes = []
    current_author = None
    files_in_commit = []

    for line in log.split("\n"):
        line = line.strip()
        if not line:
            continue
        if not any(line.endswith(ext) for ext in doc_exts):
            if files_in_commit:
                changes.append({"files": files_in_commit, "author": current_author})
            parts = line.split(" ", 1)
            current_author = parts[1] if len(parts) > 1 else "unknown"
            files_in_commit = []
        else:
            files_in_commit.append(line)

    if files_in_commit:
        changes.append({"files": files_in_commit, "author": current_author})

    file_activity: dict[str, dict] = {}
    for change in changes:
        for f in change["files"]:
            if Path(f).suffix.lower() in doc_exts:
                if f not in file_activity:
                    file_activity[f] = {"file": f, "change_count": 0, "authors": set()}
                file_activity[f]["change_count"] += 1
                file_activity[f]["authors"].add(change["author"])

    sorted_activity = sorted(
        [{"file": k, "change_count": v["change_count"], "authors": list(v["authors"])}
         for k, v in file_activity.items()],
        key=lambda x: x["change_count"],
        reverse=True,
    )

    return {"changes_count": len(sorted_activity), "time_window_days": days, "recent_changes": sorted_activity[:20]}


def detect_cross_references(project_dir: Optional[str] = None) -> dict:
    """Find which documents link to other documents in the repo."""
    project_dir = project_dir or os.getcwd()
    doc_exts = {".md", ".txt", ".rst", ".org", ".html"}
    link_pattern = re.compile(r'(?:\]\(([^)]+)\)|\[\[([^\]]+)\]\])')

    all_files = _run_git("ls-files", project_dir=project_dir)
    doc_files = [f for f in all_files.split("\n") if f and Path(f).suffix.lower() in doc_exts]
    references: list[dict] = []

    for f in doc_files:
        full_path = Path(project_dir) / f
        if not full_path.exists():
            continue
        try:
            content = full_path.read_text()
        except (OSError, UnicodeDecodeError):
            continue

        links = []
        for match in link_pattern.finditer(content):
            target = match.group(1) or match.group(2) or ""
            target = target.split("#")[0].strip()
            if target and not target.startswith(("http://", "https://", "mailto:")):
                links.append(target)

        if links:
            references.append({"file": f, "total_links": len(links), "_all_targets": links, "targets": links[:10]})

    ref_count: dict[str, int] = {}
    for ref in references:
        # Count all links for accuracy, not just the truncated preview
        for target in ref.get("_all_targets", ref["targets"]):
            ref_count[target] = ref_count.get(target, 0) + 1

    most_referenced = sorted(ref_count.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "documents_with_links": len(references),
        "total_references": sum(len(r["targets"]) for r in references),
        "most_referenced": [{"file": f, "references": c} for f, c in most_referenced],
        "details": references[:20],
    }

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
    """Generate 'state of the project' summary from all janitor data. 1 LLM call.

    Branches on project type (code/document/hybrid) to use appropriate signals and prompt.
    """
    from core.janitor.worker import call_free

    project_dir = project_dir or os.getcwd()
    project_dir_path = Path(project_dir)
    project_name = project_dir_path.name
    project_type = detect_project_type(project_dir)
    sections: dict[str, str] = {}

    # Event stats (universal)
    events_path = _janitor_dir(project_dir) / "events.jsonl"
    if events_path.exists():
        total = decisions = blockers = discoveries = 0
        recent_decisions = []
        with open(events_path) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    evt = json.loads(line)
                    evt_type = evt.get("type", "")
                except json.JSONDecodeError:
                    evt_type = ""
                if evt_type == "decision":
                    decisions += 1
                    recent_decisions.append(evt.get("content", "")[:100])
                elif evt_type == "blocker":
                    blockers += 1
                elif evt_type == "discovery":
                    discoveries += 1
                else:
                    total += 1
        if total or decisions or blockers:
            sections["events"] = f"{total} events, {decisions} decisions, {blockers} blockers, {discoveries} discoveries"
        if recent_decisions:
            sections["recent_decisions"] = "; ".join(recent_decisions[-5:])

    # Code-only signals
    if project_type in ("code", "hybrid"):
        for key, name in [("test_gaps", "test-gaps.json"), ("code_smells", "code-smells.json"),
                           ("dep_graph", "dep-graph.json")]:
            data = _read_json(name, project_dir)
            if not data:
                continue
            if key == "test_gaps" and data.get("gap_count", 0) > 0:
                sections[key] = f"{data['gap_count']} gaps: " + ", ".join(g["source_file"] for g in data["gaps"][:5])
            elif key == "code_smells" and (data.get("oversized_file_count", 0) > 0 or data.get("oversized_function_count", 0) > 0):
                parts = []
                for ff in data["oversized_files"][:3]:
                    parts.append(f"{ff['path']} ({ff['lines']} lines)")
                for fn in data["oversized_functions"][:3]:
                    parts.append(f"{fn['path']}:{fn['function']} ({fn['lines']} lines)")
                sections[key] = "; ".join(parts) if parts else ""
            elif key == "dep_graph" and data.get("impact_ranking"):
                sections[key] = ", ".join(f'{t["file"]} ({t["downstream_count"]} deps)' for t in data["impact_ranking"][:3])
            if not sections.get(key):
                sections.pop(key, None)

    # Document-only signals
    if project_type in ("document", "hybrid"):
        for key, name in [("doc_staleness", "doc-staleness.json"), ("doc_orphans", "doc-orphans.json"),
                           ("doc_clusters", "doc-clusters.json"), ("doc_size_outliers", "doc-size-outliers.json"),
                           ("doc_crossrefs", "doc-crossrefs.json"), ("doc_recent_activity", "doc-recent-activity.json")]:
            data = _read_json(name, project_dir)
            if not data:
                continue
            if key == "doc_staleness" and data.get("stale_count", 0) > 0:
                sections[key] = "; ".join(f'{s["file"]} ({s["days_since_edit"]}d stale)' for s in data["stale_files"][:5])
            elif key == "doc_orphans" and data.get("orphan_count", 0) > 0:
                sections[key] = f"{data['orphan_count']}/{data['total_documents']} orphaned: " + ", ".join(data["orphan_files"][:5])
            elif key == "doc_clusters" and data.get("cluster_count", 0) > 0:
                sections[key] = "; ".join(f'{c["directory"]} ({c["file_count"]} docs)' for c in data["clusters"][:5])
            elif key == "doc_size_outliers" and data.get("outlier_count", 0) > 0:
                sections[key] = "; ".join(f'{o["file"]} ({o["size_kb"]}KB, {o["type"]})' for o in data["outliers"][:5])
            elif key == "doc_crossrefs" and data.get("most_referenced"):
                sections[key] = "; ".join(f'{r["file"]} ({r["references"]} refs)' for r in data["most_referenced"][:5])
            elif key == "doc_recent_activity" and data.get("recent_changes"):
                sections[key] = "; ".join(f'{a["file"]} ({a["change_count"]}x by {a["authors"][0]})' for a in data["recent_changes"][:5])
            if not sections.get(key):
                sections.pop(key, None)

    # Universal signals (all project types)
    for key, name in [("config_drift", "config-drift.json"), ("patterns", "patterns.json"),
                       ("recent_focus", "recent-focus.json"), ("dead_ends", "dead-ends.json"),
                       ("blockers", "blockers.json"), ("critical_files", "critical-files.json"),
                       ("knowledge_risk", "knowledge-risk.json")]:
        data = _read_json(name, project_dir)
        if not data:
            continue
        if key == "config_drift" and data.get("drift_count", 0) > 0:
            sections[key] = "Drifted: " + ", ".join(data["drifted_file_names"])
        elif key == "patterns" and data.get("patterns"):
            sections[key] = "; ".join(p.get("description", "")[:100] for p in data["patterns"][:3])
        elif key == "recent_focus" and data.get("files"):
            sections[key] = ", ".join(data["files"][-5:])
        elif key == "dead_ends" and data.get("dead_ends"):
            sections[key] = "; ".join(f'{d["query"]} ({d["count"]}x)' for d in data["dead_ends"][:3])
        elif key == "blockers" and data.get("blockers"):
            sections[key] = "; ".join(b.get("content", "")[:100] for b in data["blockers"][:5])
        elif key == "critical_files" and data.get("critical_files"):
            sections[key] = "; ".join(f'{c["file"]} ({c["sessions"]} sessions, {c["downstream_deps"]} deps)' for c in data["critical_files"][:3])
        elif key == "knowledge_risk" and data.get("at_risk"):
            sections[key] = "; ".join(f'{r["file"]} (sole contributor: {r["contributors"][0]}, {r["edit_count"]} edits)' for r in data["at_risk"][:3])
        if not sections.get(key):
            sections.pop(key, None)

    context_text = "\n".join(f"## {k}\n{v}" for k, v in sections.items())
    if not context_text.strip():
        return {"status": "no_data", "project_type": project_type}

    # Staleness gate
    state_hash = _data_hash(sections)
    if _onboarding_is_fresh(project_dir, state_hash):
        return {"status": "fresh", "reason": "no new data since last onboarding", "project_type": project_type}

    # Branch prompt by project type
    if project_type == "document":
        summary = call_free(
            f"Project: {project_name} (type: document repository)\n\n"
            f"Raw signals collected by background analysis:\n\n{context_text}\n\n"
            "Generate an onboarding summary for an AI agent starting a session on this document repository.\n\n"
            "RULES:\n"
            "- Every finding MUST include a file path. No vague references.\n"
            "- Prefer specific numbers: '3 stale docs (45+ days)' not 'some old files'.\n"
            "- Skip any section where there is nothing to report.\n"
            "- Do NOT invent findings. Only report what the signals above show.\n"
            "- This is a DOCUMENT repository, not a codebase. Focus on content health.\n\n"
            "OUTPUT FORMAT (use exactly these headers, skip empty ones):\n"
            "# Document Status\n1-2 sentences: what is this repo and what state is it in?\n\n"
            "# Stale Content\nDocuments not updated in a long time. Why this matters.\n\n"
            "# Orphan Documents\nDocuments not linked/referenced from anywhere.\n\n"
            "# Recent Activity\nWhat was worked on last. Include file paths and who changed them.\n\n"
            "# Attention Items\nRanked by urgency: stale docs, orphans, size outliers, knowledge risk.\n\n"
            "# Recommended Next Steps\nNumbered, most actionable first. Reference specific files.\n\n"
            "MAX 400 words. Be dense -- every sentence should contain a file path or a number.",
            system=(
                "You are a project intelligence analyst specializing in document repositories. "
                "Convert raw signals into a concise, actionable briefing. "
                "The agent needs to know: what's stale, what's orphaned, what changed recently, "
                "and what to do next -- all with specific file references. "
                "Never pad with generic advice. Never say 'consider reviewing' without saying WHAT file and WHY."
            ),
            max_tokens=2048,
        )
    else:
        code_sub = "python package"
        if (project_dir_path / "vercel.json").exists() or (project_dir_path / "supabase").is_dir():
            code_sub = "web app"
        elif list(project_dir_path.glob("*.service")):
            code_sub = "service"
        summary = call_free(
            f"Project: {project_name} (type: {code_sub})\n\n"
            f"Raw signals collected by background analysis:\n\n{context_text}\n\n"
            "Generate an onboarding summary for an AI coding agent starting a session on this project.\n\n"
            "RULES:\n"
            "- Every finding MUST include a file path (e.g. core/auth.py). No vague references.\n"
            "- Prefer specific numbers over vague descriptions. '3 files, 0 tests' not 'some files need tests'.\n"
            "- Skip any section where there is nothing to report.\n"
            "- Do NOT invent findings. Only report what the signals above show.\n\n"
            "OUTPUT FORMAT (use exactly these headers, skip empty ones):\n"
            "# Project Status\n1-2 sentences: what state is this project in?\n\n"
            "# Active Blockers\nList each blocker with the file or decision that's stuck.\n\n"
            "# Recent Activity\nWhat was worked on last. Include file paths.\n\n"
            "# Attention Items\nRanked by urgency: test gaps, knowledge risk, oversized files, config drift.\n\n"
            "# Recommended Next Steps\nNumbered, most actionable first. Reference specific files.\n\n"
            "MAX 400 words. Be dense -- every sentence should contain a file path or a number.",
            system=(
                "You are a project intelligence analyst. Your job is to convert raw codebase signals "
                "into a concise, actionable briefing for an AI coding agent. "
                "The agent needs to know: what's broken, what's risky, what was just worked on, "
                "and what to do next -- all with specific file references. "
                "Never pad with generic advice. Never say 'consider reviewing' without saying WHAT to review and WHERE."
            ),
            max_tokens=2048,
        )

    # Save onboarding + staleness state
    _janitor_dir(project_dir).joinpath("onboarding.md").write_text(summary)
    _janitor_dir(project_dir).joinpath("onboarding-state.json").write_text(
        json.dumps({"hash": state_hash, "ts": time.time()})
    )

    # Build source index
    janitor = _janitor_dir(project_dir)
    sources = []
    source_labels = {
        "test-gaps.json": "untested files",
        "code-smells.json": "oversized files/functions",
        "dep-graph.json": "dependency impact ranking",
        "doc-staleness.json": "stale documents",
        "doc-orphans.json": "orphan/unlinked documents",
        "doc-clusters.json": "document topic clusters",
        "doc-size-outliers.json": "unusually large files",
        "doc-crossrefs.json": "cross-reference map",
        "doc-recent-activity.json": "recent document changes",
        "config-drift.json": "uncommitted config changes",
        "patterns.json": "recurring patterns",
        "recent-focus.json": "last session's focus",
        "dead-ends.json": "recurring failed searches",
        "blockers.json": "unresolved blockers",
        "critical-files.json": "high-touch x high-impact files",
        "knowledge-risk.json": "low bus factor files",
        "onboarding.md": "full onboarding summary",
        "events.jsonl": "raw event log",
    }
    for fname, label in source_labels.items():
        path = janitor / fname
        if path.exists() and path.stat().st_size > 2:
            sources.append(f"- `.janitor/{fname}` -- {label}")

    # Auto-export to CLAUDE.local.md
    claude_local = Path(project_dir) / "CLAUDE.local.md"
    header = "<!-- Auto-generated by janitor. Edit freely -- janitor overwrites daily. -->\n\n"
    if sources:
        source_block = "\n\n## Project Intelligence Sources\n\nRead these files for details on demand:\n\n" + "\n".join(sources)
    else:
        source_block = ""
    claude_local.write_text(header + summary + source_block)

    return {"status": "ok", "summary_length": len(summary), "project_type": project_type}



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


def _ensure_opencode_config(project_dir: str) -> None:
    """Ensure .opencode/opencode.json exists with instructions pointing to CLAUDE.local.md."""
    import json
    oc_dir = Path(project_dir) / ".opencode"
    oc_file = oc_dir / "opencode.json"
    if oc_file.exists():
        return
    oc_dir.mkdir(parents=True, exist_ok=True)
    config = {
        "$schema": "https://opencode.ai/config.json",
        "instructions": ["../AGENTS.md", "../CLAUDE.local.md"],
    }
    oc_file.write_text(json.dumps(config, indent=2) + "\n")


def detect_recent_focus(project_dir: Optional[str] = None, max_files: int = 10) -> dict:
    """Find recently-accessed files and commands from events.jsonl."""
    project_dir = project_dir or os.getcwd()
    jd = _janitor_dir(project_dir)
    events = jd / "events.jsonl"
    if not events.exists():
        return {"files": [], "commands": [], "session_count": 0}
    files = []
    commands = []
    sessions = set()
    cutoff = (datetime.now() - timedelta(days=3)).isoformat() + "Z"
    with open(events) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            sessions.add(e.get("session", ""))
            if e.get("ts", "") < cutoff:
                continue
            if e.get("type") == "file_read" and e.get("files"):
                for fp in e["files"]:
                    short = fp.replace(project_dir + "/", "") if project_dir else fp
                    files.append(short)
            elif e.get("type") == "file_written" and e.get("files"):
                for fp in e["files"]:
                    short = fp.replace(project_dir + "/", "") if project_dir else fp
                    files.append(short)
            elif e.get("type") == "action_taken":
                content = e.get("content", "")
                if content and len(content) < 200:
                    commands.append(content)
    return {"files": files[-max_files:], "commands": commands[-max_files:], "session_count": len(sessions)}


def detect_recurring_dead_ends(project_dir: Optional[str] = None) -> dict:
    """Find queries that led to dead ends multiple times."""
    project_dir = project_dir or os.getcwd()
    jd = _janitor_dir(project_dir)
    events = jd / "events.jsonl"
    result_file = jd / "dead-ends.json"
    # If we already have LLM-computed dead ends, just return those
    if result_file.exists():
        try:
            return json.loads(result_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    # Pure-compute fallback: look for blocker events
    blockers = {}
    if not events.exists():
        return {"dead_ends": []}
    with open(events) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("type") == "blocker":
                content = e.get("content", "")[:100]
                if content:
                    blockers[content] = blockers.get(content, 0) + 1
    dead_ends = [{"query": q, "count": c} for q, c in sorted(blockers.items(), key=lambda x: -x[1]) if c > 1]
    return {"dead_ends": dead_ends}


def detect_unresolved_blockers(project_dir: Optional[str] = None) -> dict:
    """Find unresolved blockers from events."""
    project_dir = project_dir or os.getcwd()
    jd = _janitor_dir(project_dir)
    result_file = jd / "blockers.json"
    if result_file.exists():
        try:
            return json.loads(result_file.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    if not (jd / "events.jsonl").exists():
        return {"blockers": []}
    blockers = []
    with open(jd / "events.jsonl") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            if e.get("type") == "blocker":
                blockers.append({"content": e.get("content", ""), "ts": e.get("ts", ""), "session": e.get("session", "")})
    return {"blockers": blockers[-10:]}


def detect_critical_files(project_dir: Optional[str] = None, top_n: int = 5) -> dict:
    """Find files touched across the most sessions (high bus-factor risk)."""
    project_dir = project_dir or os.getcwd()
    jd = _janitor_dir(project_dir)
    events = jd / "events.jsonl"
    if not events.exists():
        return {"critical_files": []}
    file_sessions = {}  # file -> set of sessions
    with open(events) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            session = e.get("session", "")
            for fp in e.get("files", []):
                short = fp.replace(project_dir + "/", "") if project_dir else fp
                if short not in file_sessions:
                    file_sessions[short] = set()
                file_sessions[short].add(session)
    # Check deps for downstream count
    deps_data = _read_json("dep-graph.json", project_dir)
    dep_counts = {}
    if deps_data:
        # New shape: {"nodes": [...]}
        if "nodes" in deps_data:
            for node in deps_data["nodes"]:
                dep_counts[node.get("file", node.get("name", ""))] = node.get("downstream_count", 0)
        # Old shape: {"impact_ranking": [{"file": ..., "downstream_deps": ...}]}
        elif "impact_ranking" in deps_data:
            for item in deps_data["impact_ranking"]:
                dep_counts[item.get("file", "")] = item.get("downstream_deps", 0)
    ranked = sorted(file_sessions.items(), key=lambda x: -len(x[1]))
    result = []
    for file, sessions in ranked[:top_n]:
        result.append({
            "file": file,
            "sessions": len(sessions),
            "downstream_deps": dep_counts.get(file, 0),
        })
    return {"critical_files": result}


def detect_knowledge_risk(project_dir: Optional[str] = None, top_n: int = 5) -> dict:
    """Find files with few contributors (bus factor risk) using git blame."""
    result = []
    pd = project_dir or "."
    # Get list of tracked files (non-binary, non-generated)
    files_output = _run_git("ls-files", project_dir=pd)
    if not files_output.strip():
        return {"at_risk": []}
    files = [f for f in files_output.strip().split("\n") if f]
    # Filter to interesting files (docs, code, config — not .janitor)
    skip = {".janitor/", "node_modules/", ".git/", "__pycache__/"}
    files = [f for f in files if not any(f.startswith(s) for s in skip)]
    # For each file, get unique authors via git log
    file_authors = {}
    for fp in files[:100]:  # limit to avoid slow runs
        log_output = _run_git("log", "--format=%an", "--follow", "--", fp, project_dir=pd)
        authors = set(a.strip() for a in log_output.strip().split("\n") if a.strip())
        if authors:
            edit_count = len(log_output.strip().split("\n"))
            file_authors[fp] = {"contributors": sorted(authors), "edit_count": edit_count}
    # Risk = sole contributor + high edit count
    at_risk = sorted(
        [(f, d) for f, d in file_authors.items() if len(d["contributors"]) <= 1 and d["edit_count"] >= 5],
        key=lambda x: -x[1]["edit_count"],
    )
    return {"at_risk": [{"file": f, "contributors": d["contributors"], "edit_count": d["edit_count"]} for f, d in at_risk[:top_n]]}


# --- Continuous Intelligence Jobs ---


def analyze_dispatch_traces(project_dir: Optional[str] = None) -> dict:
    """Aggregate eval/traces/ into per-worker success stats. Pure-compute, no LLM.

    Reads trace.json from every dispatch bundle and computes:
      - success rate per worker per category
      - average latency per worker
      - retry and escalation rates

    Writes results to .janitor/worker-stats.json.
    Returns immediately with {"status": "no_traces"} if no traces exist yet.
    """
    project_dir = project_dir or os.getcwd()
    traces_root = Path(project_dir) / "eval" / "traces"
    if not traces_root.exists():
        return {"status": "no_traces", "traces_analyzed": 0}

    trace_files = list(traces_root.rglob("trace.json"))
    if not trace_files:
        return {"status": "no_traces", "traces_analyzed": 0}

    # worker → category → {dispatches, successes, total_latency, retries, escalations}
    stats: dict[str, dict[str, dict]] = {}
    total = 0

    for tf in trace_files:
        try:
            data = json.loads(tf.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        worker = (data.get("execution") or {}).get("worker") or (data.get("routing") or {}).get("selected_worker")
        category = (data.get("classification") or {}).get("category", "unknown")
        if not worker:
            continue

        succeeded = (data.get("validation") or {}).get("passed", False)
        duration = (data.get("execution") or {}).get("duration_seconds") or 0
        retry_attempt = (data.get("retry") or {}).get("attempt", 1)
        escalated = (data.get("retry") or {}).get("escalated", False)

        w = stats.setdefault(worker, {})
        c = w.setdefault(category, {
            "dispatches": 0, "successes": 0, "total_latency": 0.0,
            "retries": 0, "escalations": 0,
        })
        c["dispatches"] += 1
        if succeeded:
            c["successes"] += 1
        c["total_latency"] += float(duration)
        if retry_attempt > 1:
            c["retries"] += 1
        if escalated:
            c["escalations"] += 1
        total += 1

    # Build summary rows
    rows = []
    for worker, cats in stats.items():
        for category, s in cats.items():
            d = s["dispatches"]
            rows.append({
                "worker": worker,
                "category": category,
                "dispatches": d,
                "success_rate": round(s["successes"] / d, 3) if d else 0,
                "avg_latency_s": round(s["total_latency"] / d, 1) if d else 0,
                "retry_rate": round(s["retries"] / d, 3) if d else 0,
                "escalation_rate": round(s["escalations"] / d, 3) if d else 0,
            })

    rows.sort(key=lambda r: (r["worker"], r["category"]))
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "traces_analyzed": total,
        "rows": rows,
    }
    _write_json("worker-stats.json", result, project_dir)
    return result


def monitor_provider_health(project_dir: Optional[str] = None) -> dict:
    """Check remaining quota for each configured provider. Pure-compute.

    Reads .janitor/usage.jsonl and config/janitor_providers.yaml.
    Writes .janitor/provider-health.json with remaining daily calls per provider.
    """
    project_dir = project_dir or os.getcwd()

    # Read provider config limits
    from core.janitor.provider_pool import _load_config
    cfg = _load_config()
    provider_cfgs = cfg.get("providers", {})

    # Count today's calls per provider from usage log
    usage_path = _janitor_dir(project_dir) / "usage.jsonl"
    now = time.time()
    day_ago = now - 86400
    calls_today: dict[str, int] = {}

    if usage_path.exists():
        with open(usage_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    ts = entry.get("ts", 0)
                    if ts < day_ago:
                        continue
                    prov = entry.get("provider", "openrouter_free")
                    calls_today[prov] = calls_today.get(prov, 0) + 1
                except (json.JSONDecodeError, ValueError):
                    continue

    health = {}
    for name, pcfg in provider_cfgs.items():
        if not isinstance(pcfg, dict):
            continue
        used = calls_today.get(name, 0)
        limit = pcfg.get("daily_limit")  # None = unlimited
        env_key = pcfg.get("env_key", "")
        has_key = bool(os.environ.get(env_key, ""))
        remaining = (limit - used) if (limit is not None) else None

        if not has_key:
            status = "no_key"
        elif remaining is not None and remaining <= 0:
            status = "exhausted"
        elif remaining is not None and remaining < (limit * 0.1 if limit else 0):
            status = "low"
        else:
            status = "ok"

        health[name] = {
            "status": status,
            "calls_today": used,
            "daily_limit": limit,
            "remaining": remaining,
            "has_key": has_key,
            "priority": pcfg.get("priority", 99),
        }

    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "providers": health,
        "available_count": sum(1 for v in health.values() if v["status"] == "ok"),
    }
    _write_json("provider-health.json", result, project_dir)
    return result


def generate_improvement_suggestions(project_dir: Optional[str] = None, min_traces: int = 20) -> dict:
    """Synthesize worker stats into plain-language improvement suggestions. 1 LLM call.

    Requires analyze_dispatch_traces() to have run first (needs worker-stats.json).
    Requires at least min_traces total dispatches for meaningful statistics.

    Writes .janitor/suggestions.json with structured suggestions.
    Returns {"status": "insufficient_data"} if not enough traces yet.
    """
    from core.janitor.worker import extract_structured_janitor

    project_dir = project_dir or os.getcwd()
    stats = _read_json("worker-stats.json", project_dir)
    if not stats:
        return {"status": "no_stats", "message": "Run analyze_dispatch_traces() first"}

    total_traces = stats.get("traces_analyzed", 0)
    if total_traces < min_traces:
        return {
            "status": "insufficient_data",
            "traces_analyzed": total_traces,
            "min_required": min_traces,
            "message": f"Need {min_traces - total_traces} more traces for reliable suggestions",
        }

    rows = stats.get("rows", [])
    if not rows:
        return {"status": "no_rows"}

    # Build a compact summary table for the LLM
    table_lines = ["Worker | Category | Dispatches | SuccessRate | AvgLatency | RetryRate"]
    table_lines.append("-" * 75)
    for r in rows:
        table_lines.append(
            f"{r['worker']:<18} | {r['category']:<12} | {r['dispatches']:>10} | "
            f"{r['success_rate']:>11.0%} | {r['avg_latency_s']:>9.0f}s | {r['retry_rate']:>9.0%}"
        )

    table = "\n".join(table_lines)

    result = extract_structured_janitor(
        f"Analyze this dispatch trace data ({total_traces} total dispatches) and suggest "
        f"routing improvements for the OneShot harness:\n\n{table}\n\n"
        "The harness routes tasks through lanes. Each lane has an ordered worker pool.\n"
        "Identify patterns like:\n"
        "  - Workers with very low success rate for a category (< 70%) → move to lower priority\n"
        "  - Workers with high success + low latency for a category → move to higher priority\n"
        "  - High retry rates → possible worker reliability issues\n"
        "  - Missing workers for a category → consider adding one\n\n"
        "Only suggest changes backed by the data. Minimum 5 dispatches per worker/category pair.",
        system=(
            "You are a harness optimization analyst for an AI orchestration system. "
            "Convert dispatch trace statistics into concrete, actionable routing improvements. "
            "Each suggestion must reference specific worker names, category names, and success rates. "
            "Be concise. Do not suggest changes without statistical backing."
        ),
        schema_hint=(
            '{"suggestions": [{'
            '"type": "lane_preference|worker_remove|worker_add|reliability_flag", '
            '"worker": str, "category": str, "confidence": float, '
            '"description": str, "evidence": str, '
            '"proposed_change": str, "file": str'
            '}]}'
        ),
    )

    if "suggestions" not in result:
        return {"status": "parse_failed", "raw": result.get("raw", ""), "traces_analyzed": total_traces}

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "traces_analyzed": total_traces,
        "rows_analyzed": len(rows),
        "suggestions": result["suggestions"],
    }
    _write_json("suggestions.json", output, project_dir)
    return output


# --- SessionStart: run pure-compute + inject results ---

def run_session_start(project_dir: Optional[str] = None) -> str:
    """Run all pure-compute jobs and return formatted context for injection.

    Called by context.sh at SessionStart. Reads any pre-computed LLM results.
    Returns a string for Claude's context, or empty string if nothing to report.
    Dispatches code signals for code/hybrid projects, document signals for document/hybrid projects.
    """
    project_dir = project_dir or os.getcwd()
    if not (Path(project_dir) / ".git").exists():
        return ""

    # Auto-register this project in the central registry (~/.config/oneshot/projects.json)
    try:
        from core.janitor.registry import auto_register
        auto_register(project_dir)
    except Exception:
        pass  # never block session start

    # Detect project type and persist for downstream use
    project_type = detect_project_type(project_dir)
    _write_json("project-type.json", {"type": project_type}, project_dir)

    # Ensure OpenCode can read project intelligence
    _ensure_opencode_config(project_dir)

    parts = []

    # Onboarding summary (from previous session's LLM job, if exists)
    onboarding_path = _janitor_dir(project_dir) / "onboarding.md"
    if onboarding_path.exists():
        age = time.time() - onboarding_path.stat().st_mtime
        if age < 86400:  # fresh within 24h
            preview = onboarding_path.read_text()[:500].replace("\n", " ")
            parts.append(f"ONBOARDING: {preview}")

    # Event stats (universal)
    stats = event_stats(project_dir)
    if stats["total"] > 0:
        detail = []
        if stats["decisions"] > 0:
            detail.append(f"{stats['decisions']} decisions")
        if stats["blockers"] > 0:
            detail.append(f"{stats['blockers']} blockers")
        parts.append(f"{stats['total']} events" + (f" ({', '.join(detail)})" if detail else ""))

    # --- Code signals (code and hybrid) ---
    if project_type in ("code", "hybrid"):
        tg = detect_test_gaps(project_dir)
        _write_json("test-gaps.json", tg, project_dir)
        if tg["gap_count"] > 0:
            files = [g["source_file"] for g in tg["gaps"][:5]]
            parts.append(f"test gaps: {tg['gap_count']} -- {', '.join(files)}")

        cs = scan_code_smells(project_dir)
        _write_json("code-smells.json", cs, project_dir)
        if cs["oversized_file_count"] > 0 or cs["oversized_function_count"] > 0:
            parts.append(f"{cs['oversized_file_count']} oversized files, {cs['oversized_function_count']} long functions")

        dg = build_dependency_map(project_dir)
        _write_json("dep-graph.json", dg, project_dir)
        if dg["impact_ranking"]:
            top = dg["impact_ranking"][:3]
            impact_str = ", ".join(f'{t["file"]} ({t["downstream_count"]} deps)' for t in top)
            parts.append(f"high-impact: {impact_str}")

    # --- Document signals (document and hybrid) ---
    if project_type in ("document", "hybrid"):
        ds = detect_document_staleness(project_dir)
        _write_json("doc-staleness.json", ds, project_dir)
        if ds["stale_count"] > 0:
            top_stale = ds["stale_files"][:3]
            stale_str = ", ".join(f'{s["file"]} ({s["days_since_edit"]}d)' for s in top_stale)
            parts.append(f"stale docs: {ds['stale_count']} -- {stale_str}")

        od = detect_orphan_documents(project_dir)
        _write_json("doc-orphans.json", od, project_dir)
        if od["orphan_count"] > 0:
            parts.append(f"orphan docs: {od['orphan_count']}/{od['total_documents']}")
            for o in od["orphan_files"][:3]:
                parts.append(f"  - {o}")

        dc = detect_document_clusters(project_dir)
        _write_json("doc-clusters.json", dc, project_dir)
        if dc["cluster_count"] > 1:
            top_clusters = dc["clusters"][:3]
            cluster_str = ", ".join(f'{c["directory"]} ({c["file_count"]} files)' for c in top_clusters)
            parts.append(f"doc clusters: {cluster_str}")

        so = detect_size_outliers(project_dir)
        _write_json("doc-size-outliers.json", so, project_dir)
        if so["outlier_count"] > 0:
            parts.append(f"size outliers: {so['outlier_count']} files over {so['threshold_kb']}KB")

        cr = detect_cross_references(project_dir)
        _write_json("doc-crossrefs.json", cr, project_dir)
        if cr["most_referenced"]:
            top_ref = cr["most_referenced"][:3]
            ref_str = ", ".join(f'{r["file"]} ({r["references"]} refs)' for r in top_ref)
            parts.append(f"most referenced: {ref_str}")

        rda = detect_recent_document_activity(project_dir)
        _write_json("doc-recent-activity.json", rda, project_dir)
        if rda["recent_changes"]:
            top_active = rda["recent_changes"][:3]
            active_str = ", ".join(f'{a["file"]} ({a["change_count"]}x by {a["authors"][0]})' for a in top_active)
            parts.append(f"recent doc activity: {active_str}")

    # --- Universal signals (all project types) ---
    cd = detect_config_drift(project_dir)
    _write_json("config-drift.json", cd, project_dir)
    if cd["drift_count"] > 0:
        parts.append(f"config drift: {', '.join(cd['drifted_file_names'][:5])}")

    rf = detect_recent_focus(project_dir)
    _write_json("recent-focus.json", rf, project_dir)
    if rf["files"]:
        parts.append(f"recent: {', '.join(rf['files'][-5:])}")

    de = detect_recurring_dead_ends(project_dir)
    _write_json("dead-ends.json", de, project_dir)
    if de["dead_ends"]:
        dead_str = "; ".join(f'{d["query"]} ({d["count"]}x)' for d in de["dead_ends"][:3])
        parts.append(f"recurring dead ends: {dead_str}")

    ub = detect_unresolved_blockers(project_dir)
    _write_json("blockers.json", ub, project_dir)
    if ub["blockers"]:
        parts.append(f"unresolved blockers: {len(ub['blockers'])}")

    cf = detect_critical_files(project_dir)
    _write_json("critical-files.json", cf, project_dir)
    if cf["critical_files"]:
        crit_str = ", ".join(
            f'{c["file"]} ({c["sessions"]} sessions, {c["downstream_deps"]} deps)'
            for c in cf["critical_files"][:3]
        )
        parts.append(f"critical files: {crit_str}")

    kr = detect_knowledge_risk(project_dir)
    _write_json("knowledge-risk.json", kr, project_dir)
    if kr["at_risk"]:
        risk_str = "; ".join(
            f'{r["file"]} ({r["contributors"][0]}, {r["edit_count"]} edits)'
            for r in kr["at_risk"][:3]
        )
        parts.append(f"knowledge risk: {risk_str}")

    # Provider health (from previous cron run, if exists)
    ph = _read_json("provider-health.json", project_dir)
    if ph:
        avail = ph.get("available_count", 0)
        total_providers = len(ph.get("providers", {}))
        if avail < total_providers:
            exhausted = [n for n, v in ph.get("providers", {}).items() if v.get("status") == "exhausted"]
            if exhausted:
                parts.append(f"providers exhausted: {', '.join(exhausted)}")

    # Improvement suggestions (advisory, from latest cron run)
    sugg = _read_json("suggestions.json", project_dir)
    if sugg and sugg.get("suggestions"):
        age = 0
        sugg_path = _janitor_dir(project_dir) / "suggestions.json"
        if sugg_path.exists():
            age = time.time() - sugg_path.stat().st_mtime
        if age < 86400 * 7:  # only show if < 1 week old
            parts.append(f"routing suggestions: {len(sugg['suggestions'])} (see .janitor/suggestions.json)")

    # Patterns (from previous LLM run, if exists and fresh)
    patterns_path = _janitor_dir(project_dir) / "patterns.json"
    if patterns_path.exists():
        age = time.time() - patterns_path.stat().st_mtime
        if age < 86400:
            patterns = _read_json("patterns.json", project_dir)
            if patterns and patterns.get("patterns"):
                parts.append(f"patterns: {'; '.join(p.get('description', '')[:60] for p in patterns['patterns'][:3])}")

    # Last eval score
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

    # Redo queue
    redo_path = _janitor_dir(project_dir) / "redo-queue.json"
    if redo_path.exists():
        try:
            redo_items = json.loads(redo_path.read_text())
            if redo_items:
                for item in redo_items[:3]:
                    score = item.get("score", "?")
                    feedback = item.get("feedback", "")[:200]
                    parts.append(f"REDO: score={score} -- {feedback}")
                redo_path.write_text("[]")
        except json.JSONDecodeError:
            pass

    if not parts:
        return ""

    return "JANITOR: " + " | ".join(parts)



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

    # Provider health (pure-compute, always run)
    try:
        monitor_provider_health(project_dir)
    except Exception:
        pass

    # Trace analysis (pure-compute, always run if traces exist)
    try:
        analyze_dispatch_traces(project_dir)
    except Exception:
        pass

    # Check for any LLM provider key
    has_llm_key = any([
        os.environ.get("OPENROUTER_API_KEY"),
        os.environ.get("QWEN_API_KEY"),
        os.environ.get("GEMINI_API_KEY"),
        os.environ.get("OPENAI_API_KEY"),
    ])
    if not has_llm_key:
        return  # silently skip — pure-compute already ran

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

        # Weekly gate for suggestion generation (requires ≥20 traces)
        weekly_gate = janitor_dir / "last-weekly-run"
        skip_weekly = False
        if weekly_gate.exists() and (time.time() - weekly_gate.stat().st_mtime) < 86400 * 7:
            skip_weekly = True

        if not skip_weekly:
            try:
                result = generate_improvement_suggestions(project_dir)
                if result.get("status") == "ok" or result.get("suggestions"):
                    weekly_gate.write_text(str(time.time()))
            except Exception:
                pass  # non-critical

    except Exception:
        pass  # LLM jobs are best-effort, never block session end
