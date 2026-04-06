"""Janitor jobs — bounded background tasks using openrouter/free.

Each job is a self-contained function that:
1. Reads raw data (from recorder, filesystem, etc.)
2. Sends a bounded extraction prompt to the free model
3. Writes structured output (to recorder, files, etc.)

Jobs are designed to be cheap ($0), fast (<30s), and idempotent.
They can run during idle time via CronCreate or on-demand.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.janitor.recorder import SessionRecorder
from core.janitor.worker import call_free, extract_structured


# --- Job: Turn Summarizer ---

def summarize_recent_turns(recorder: SessionRecorder, n: int = 10) -> dict:
    """Extract decisions, blockers, and progress from recent turns.

    Reads the last N events from the JSONL log and asks the free model
    to extract structured decisions, blockers, and discoveries.
    """
    events = recorder.get_recent_events(n)
    if not events:
        return {"status": "empty", "decisions": [], "blockers": [], "discoveries": []}

    # Build a compact text representation
    turn_text = "\n".join(
        f"[{e['turn']}] ({e['type']}) {e['content'][:200]}"
        for e in events
    )

    result = extract_structured(
        f"Analyze these session events and extract:\n\n{turn_text}\n\n"
        "Extract any:\n"
        "1. Decisions made (approach chosen, tech selected, etc.)\n"
        "2. Blockers (things that are stuck or waiting)\n"
        "3. Discoveries (things learned, bugs found, patterns noticed)\n"
        "4. Progress summary (what was accomplished)\n"
        "If nothing found for a category, return empty list.",
        system="You are a session analyst. Extract structured data from development session logs. Be concise.",
        schema_hint='{"decisions": [{"what": str, "why": str}], "blockers": [{"what": str, "reason": str}], "discoveries": [{"what": str}], "progress": str}',
    )

    # Record the summary back to the log
    if result.get("decisions"):
        for d in result["decisions"]:
            recorder.record_decision(
                d.get("what", ""),
                alternatives=d.get("alternatives", []),
            )
    if result.get("blockers"):
        for b in result["blockers"]:
            recorder.record_blocker(b.get("what", ""), b.get("reason", ""))

    recorder.record_summary(
        f"Turn summary: {len(result.get('decisions', []))} decisions, "
        f"{len(result.get('blockers', []))} blockers, "
        f"{len(result.get('discoveries', []))} discoveries",
        source="janitor_summarize",
    )

    return result


# --- Job: Memory Hygiene ---

def memory_hygiene(memory_dir: Optional[str] = None) -> dict:
    """Deduplicate and compact memory files.

    Reads all memory .md files, asks the free model to identify
    overlapping content, and reports what should be merged.
    Does NOT modify files — reports only. Caller decides what to merge.
    """
    if not memory_dir:
        memory_dir = os.path.expanduser("~/.claude/projects/-home-ubuntu-github-oneshot/memory")

    mem_path = Path(memory_dir)
    if not mem_path.exists():
        return {"status": "no_memory_dir", "files": 0, "overlaps": []}

    # Read all memory files (skip MEMORY.md index)
    files = {}
    for f in sorted(mem_path.glob("*.md")):
        if f.name == "MEMORY.md":
            continue
        content = f.read_text()
        if content.strip():
            files[f.name] = content[:1000]  # first 1000 chars for comparison

    if len(files) < 2:
        return {"status": "too_few_files", "files": len(files), "overlaps": []}

    # Build a compact comparison prompt
    file_list = "\n".join(f"## {name}\n{content[:500]}" for name, content in files.items())

    result = extract_structured(
        f"Analyze these memory files for overlapping or duplicate content:\n\n{file_list}\n\n"
        "Identify which files cover overlapping topics and should be merged.\n"
        "Be conservative — only flag clear overlaps, not tangential connections.",
        system="You are a memory system analyst. Identify duplicate or overlapping content in knowledge base files.",
        schema_hint='{"overlaps": [{"files": [str], "topic": str, "overlap_description": str, "recommendation": str}]}',
    )

    result["total_files"] = len(files)
    result["total_bytes"] = sum(len(c) for c in files.values())
    return result


# --- Job: Session Digest ---

def generate_session_digest(recorder: SessionRecorder) -> str:
    """Generate a full session digest from the event log.

    Produces a structured markdown summary suitable for handoff
    or session-end review.
    """
    events = recorder.get_events_by_session(recorder.session_id)
    if not events:
        return "No events this session."

    events_text = "\n".join(
        f"- [{e['turn']}] ({e['type']}) {e['content'][:150]}"
        for e in events
        if e["type"] != "summary"  # skip self-referential summaries
    )

    digest = call_free(
        f"Generate a structured session digest from these events:\n\n{events_text}\n\n"
        "Output a markdown section with:\n"
        "## What Was Asked (user requests)\n"
        "## What Was Done (actions taken)\n"
        "## Decisions (with reasoning)\n"
        "## Files Changed (list)\n"
        "## Blockers (if any)\n"
        "## Next Steps (what should happen next)\n"
        "Be specific with file names and code references. Keep it factual.",
        system="You are a session summarizer. Generate factual, structured digests of development sessions.",
        max_tokens=2048,
    )

    recorder.record_summary(digest, source="session_digest")
    return digest


# --- Job: File Change Tracker ---

def analyze_file_changes(project_dir: Optional[str] = None) -> dict:
    """Analyze recent git changes and categorize them.

    Uses git diff/log to understand what changed and why,
    then uses the free model to categorize changes.
    """
    import subprocess

    if not project_dir:
        project_dir = os.getcwd()

    # Get recent commits (last 10)
    try:
        r = subprocess.run(
            ["git", "log", "--oneline", "-10", "--name-status"],
            capture_output=True, text=True, timeout=5, cwd=project_dir
        )
        if r.returncode != 0:
            return {"status": "git_error"}
        log_text = r.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {"status": "git_unavailable"}

    # Get current diff (uncommitted)
    try:
        r = subprocess.run(
            ["git", "diff", "--stat"],
            capture_output=True, text=True, timeout=5, cwd=project_dir
        )
        diff_stat = r.stdout if r.returncode == 0 else ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        diff_stat = ""

    if not log_text.strip() and not diff_stat.strip():
        return {"status": "no_changes"}

    result = extract_structured(
        f"Analyze these git changes and categorize them:\n\n"
        f"## Recent Commits\n{log_text}\n\n"
        f"## Uncommitted Changes\n{diff_stat}\n\n"
        "Categorize the changes and identify patterns.",
        system="You are a codebase analyst. Categorize git changes by type and identify patterns.",
        schema_hint='{"categories": {"features": int, "bugs": int, "refactors": int, "docs": int, "config": int, "tests": int}, "patterns": [str], "hotspot_files": [str]}',
    )

    return result


# --- Job: Stale File Detection ---

def detect_stale_files(project_dir: Optional[str] = None, days: int = 30) -> dict:
    """Find files not modified in N days that might need attention."""
    import subprocess

    if not project_dir:
        project_dir = os.getcwd()

    try:
        r = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, timeout=10, cwd=project_dir
        )
        if r.returncode != 0:
            return {"status": "git_error"}
        tracked_files = r.stdout.strip().split("\n")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return {"status": "git_unavailable"}

    # Find files not modified in N days
    cutoff = days * 86400  # seconds
    now = time.time() if (time := __import__("time")) else 0
    stale = []
    important_stale = []

    for f in tracked_files:
        fpath = Path(project_dir) / f
        if not fpath.exists():
            continue
        age = now - fpath.stat().st_mtime
        if age > cutoff:
            stale.append({"path": f, "age_days": int(age / 86400)})
            # Flag potentially important stale files
            name_lower = f.lower()
            if any(kw in name_lower for kw in ["config", "readme", "setup", "install", "deploy"]):
                important_stale.append({"path": f, "age_days": int(age / 86400)})

    return {
        "total_tracked": len(tracked_files),
        "stale_count": len(stale),
        "important_stale": important_stale,
        "stale_by_age": {
            "30-60 days": len([s for s in stale if 30 <= s["age_days"] < 60]),
            "60-90 days": len([s for s in stale if 60 <= s["age_days"] < 90]),
            "90+ days": len([s for s in stale if s["age_days"] >= 90]),
        },
    }
