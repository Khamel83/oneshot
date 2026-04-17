"""Cross-project morning briefing.

Aggregates every ~/github/*/.janitor/digest.md into one ~/INBOX.md, sorted
by activity (most-changed projects first). Run from janitor-cron.sh once per
day, after per-project digests have been generated.

No LLM call — pure aggregation. The per-project digests already used the smart
free model; this is just stitching them together.
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path


def _digest_age_hours(path: Path) -> float:
    return (time.time() - path.stat().st_mtime) / 3600


def _activity_score(project_dir: Path) -> int:
    """Higher = more activity. Used for sort order."""
    events = project_dir / ".janitor" / "events.jsonl"
    if not events.exists():
        return 0
    cutoff = time.time() - 86400
    count = 0
    with open(events) as f:
        for line in f:
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
            if ts >= cutoff:
                count += 1
    return count


def generate_inbox(repos_root: str | None = None, output_path: str | None = None) -> dict:
    """Build ~/INBOX.md from all per-project digests."""
    repos_root = Path(repos_root or os.path.expanduser("~/github"))
    output_path = Path(output_path or os.path.expanduser("~/INBOX.md"))

    if not repos_root.exists():
        return {"status": "no_repos_root", "path": str(repos_root)}

    candidates = []
    for project in sorted(repos_root.iterdir()):
        if not project.is_dir():
            continue
        digest = project / ".janitor" / "digest.md"
        if not digest.exists():
            continue
        # Skip stale digests (>48h old) — those projects are inactive
        if _digest_age_hours(digest) > 48:
            continue
        candidates.append((project, digest, _activity_score(project)))

    if not candidates:
        output_path.write_text(
            f"# INBOX\n_No active projects with digests as of "
            f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}._\n"
        )
        return {"status": "no_digests", "output": str(output_path)}

    # Sort by activity score desc, then by name
    candidates.sort(key=lambda t: (-t[2], t[0].name))

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    parts = [
        f"# INBOX — morning briefing",
        f"_Generated {now}. {len(candidates)} active projects (sorted by 24h activity)._",
        "",
        "---",
        "",
    ]

    for project, digest, score in candidates:
        body = digest.read_text().strip()
        # Drop the per-project digest's own header (first 2 lines: title + timestamp)
        lines = body.split("\n")
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
        if lines and lines[0].startswith("_Generated"):
            lines = lines[1:]
        body = "\n".join(lines).strip()

        parts.append(f"## {project.name}  _(events: {score})_")
        parts.append(body)
        parts.append("")
        parts.append("---")
        parts.append("")

    output_path.write_text("\n".join(parts))

    return {
        "status": "ran",
        "projects_included": len(candidates),
        "output": str(output_path),
        "top_project": candidates[0][0].name if candidates else None,
    }


if __name__ == "__main__":
    import sys
    repos_root = sys.argv[1] if len(sys.argv) > 1 else None
    output = sys.argv[2] if len(sys.argv) > 2 else None
    result = generate_inbox(repos_root, output)
    print(json.dumps(result, indent=2))
