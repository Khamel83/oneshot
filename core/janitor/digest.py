"""Per-project daily digest.

Pulls 24h of activity from git, .janitor/events.jsonl, and signal-file diffs,
then asks a smart free model to summarize "what changed since yesterday" into
.janitor/digest.md.

Date-stamp gated via .janitor/last-digest so multiple cron runs per day are no-ops.
Run from janitor-cron.sh once per day.
"""

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def _janitor_dir(project_dir: str) -> Path:
    return Path(project_dir) / ".janitor"


def _ran_today(project_dir: str) -> bool:
    stamp = _janitor_dir(project_dir) / "last-digest"
    if not stamp.exists():
        return False
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return stamp.read_text().strip() == today


def _mark_ran(project_dir: str) -> None:
    stamp = _janitor_dir(project_dir) / "last-digest"
    stamp.write_text(datetime.now(timezone.utc).strftime("%Y-%m-%d"))


def _git_log_24h(project_dir: str) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "--since=24 hours ago", "--pretty=format:%h %s", "--no-merges"],
            cwd=project_dir, capture_output=True, text=True, timeout=10,
        )
        return out.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""


def _events_24h(project_dir: str) -> dict:
    """Bucket events from the last 24h by type."""
    events_path = _janitor_dir(project_dir) / "events.jsonl"
    if not events_path.exists():
        return {}

    cutoff = time.time() - 86400
    buckets: dict[str, list] = {
        "decision": [], "blocker": [], "discovery": [], "dead_end": [],
        "file_written": [], "commit": [],
    }
    counts: dict[str, int] = {}

    with open(events_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = ev.get("ts", 0)
            if isinstance(ts, str):
                try:
                    ts = datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
                except ValueError:
                    continue
            if ts < cutoff:
                continue
            kind = ev.get("type", "unknown")
            counts[kind] = counts.get(kind, 0) + 1
            if kind in buckets and len(buckets[kind]) < 10:
                content = ev.get("content") or ev.get("file") or ev.get("message") or ""
                if content:
                    buckets[kind].append(str(content)[:200])

    return {"counts": counts, "samples": {k: v for k, v in buckets.items() if v}}


def _changed_files_24h(project_dir: str) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "log", "--since=24 hours ago", "--name-only", "--pretty=format:"],
            cwd=project_dir, capture_output=True, text=True, timeout=10,
        )
        files = sorted({line for line in out.stdout.splitlines() if line.strip()})
        return files[:30]
    except (subprocess.SubprocessError, FileNotFoundError):
        return []


def _signal_summary(project_dir: str) -> dict:
    """Snapshot key counts from current signal files."""
    jdir = _janitor_dir(project_dir)
    summary = {}
    for name, key in [
        ("test-gaps.json", "untested_count"),
        ("code-smells.json", "oversized_file_count"),
        ("doc-staleness.json", "stale_count"),
        ("doc-orphans.json", "orphan_count"),
        ("blockers.json", "blocker_count"),
    ]:
        p = jdir / name
        if not p.exists():
            continue
        try:
            data = json.loads(p.read_text())
        except json.JSONDecodeError:
            continue
        if key in data:
            summary[key.replace("_count", "").replace("_", " ")] = data[key]
        elif isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, list):
                    summary[k] = len(v)
                    break
    return summary


def generate_digest(project_dir: str, force: bool = False) -> dict:
    """Generate the per-project daily digest.

    Returns {"status": "ran"|"fresh"|"no_data"|"failed", ...}
    """
    project_dir = str(Path(project_dir).resolve())
    if not force and _ran_today(project_dir):
        return {"status": "fresh", "reason": "already ran today"}

    git_log = _git_log_24h(project_dir)
    events = _events_24h(project_dir)
    changed_files = _changed_files_24h(project_dir)
    signals = _signal_summary(project_dir)

    has_activity = (
        bool(git_log) or events.get("counts") or changed_files
    )
    if not has_activity:
        _mark_ran(project_dir)
        return {"status": "no_data", "reason": "no activity in last 24h"}

    project_name = Path(project_dir).name

    parts = [f"Project: {project_name}\n"]
    if git_log:
        parts.append(f"## Commits (last 24h)\n{git_log}\n")
    if changed_files:
        parts.append("## Files changed\n" + "\n".join(f"- {f}" for f in changed_files) + "\n")
    if events.get("counts"):
        parts.append("## Event counts\n" + ", ".join(f"{k}={v}" for k, v in events["counts"].items()) + "\n")
    if events.get("samples"):
        parts.append("## Notable events")
        for kind, items in events["samples"].items():
            parts.append(f"\n### {kind}")
            for item in items[:5]:
                parts.append(f"- {item}")
        parts.append("")
    if signals:
        parts.append("## Current signals\n" + ", ".join(f"{k}={v}" for k, v in signals.items()) + "\n")

    context = "\n".join(parts)

    from core.janitor.worker import call_free

    try:
        summary = call_free(
            f"{context}\n\n"
            "Write a 5-bullet morning briefing for someone returning to this project tomorrow.\n\n"
            "RULES:\n"
            "- Each bullet is one sentence.\n"
            "- Lead with the most important thing first.\n"
            "- Cite specific files, commits, or counts. No vague language.\n"
            "- If nothing changed in a category, skip it -- do not pad.\n"
            "- Include 1 'next action' bullet at the end if there's an obvious one.",
            system=(
                "You are a project status briefer. Your reader has just sat down with coffee and wants "
                "to know in 30 seconds what happened yesterday on this project. Be specific, terse, useful."
            ),
            max_tokens=1024,
            quality="smart",
        )
    except RuntimeError as e:
        return {"status": "failed", "reason": str(e)}

    if not summary or not summary.strip():
        return {"status": "failed", "reason": "empty model response"}

    digest_path = _janitor_dir(project_dir) / "digest.md"
    header = (
        f"# {project_name} — daily digest\n"
        f"_Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}_\n\n"
    )
    digest_path.write_text(header + summary.strip() + "\n")
    _mark_ran(project_dir)

    return {
        "status": "ran",
        "project": project_name,
        "events_seen": sum(events.get("counts", {}).values()),
        "files_changed": len(changed_files),
        "commits": len(git_log.splitlines()) if git_log else 0,
    }


if __name__ == "__main__":
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    force = "--force" in sys.argv
    result = generate_digest(target, force=force)
    print(json.dumps(result, indent=2))
