"""Aggregate eval/traces/ into a per-worker success rate table.

V1 of the outer loop plan (docs/meta-harness/outer_loop_plan.md).

Usage:
    python3 eval/scripts/worker_stats.py [--since 7d] [--json] [--project-dir PATH]

Options:
    --since    Only include traces from last N days (e.g. 7d, 30d). Default: all.
    --json     Output raw JSON instead of a human-readable table.
    --project-dir  Project root (default: auto-detect from CWD).

Examples:
    python3 eval/scripts/worker_stats.py
    python3 eval/scripts/worker_stats.py --since 7d
    python3 eval/scripts/worker_stats.py --json | jq '.rows[] | select(.success_rate < 0.7)'
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def _find_project_dir(start: str) -> Path:
    p = Path(start)
    for candidate in [p] + list(p.parents):
        if (candidate / ".git").exists():
            return candidate
    return p


def _parse_since(since: str) -> float | None:
    """Parse '7d', '30d', '24h' etc into a cutoff timestamp. None = all time."""
    if not since:
        return None
    since = since.strip().lower()
    if since.endswith("d"):
        days = float(since[:-1])
        return time.time() - days * 86400
    if since.endswith("h"):
        hours = float(since[:-1])
        return time.time() - hours * 3600
    return None


def _trace_timestamp(trace_path: Path) -> float:
    """Extract unix timestamp from a trace.json file."""
    try:
        data = json.loads(trace_path.read_text())
        ts_str = data.get("timestamp") or data.get("execution", {}).get("started")
        if ts_str:
            # ISO format: 2026-04-05T14:30:22Z
            ts_str = ts_str.replace("Z", "+00:00")
            return datetime.fromisoformat(ts_str).timestamp()
    except Exception:
        pass
    # Fall back to file mtime
    return trace_path.stat().st_mtime


def aggregate(project_dir: Path, since_ts: float | None = None) -> dict:
    """Walk eval/traces/ and aggregate per-worker per-category statistics."""
    traces_root = project_dir / "eval" / "traces"
    if not traces_root.exists():
        return {"rows": [], "traces_analyzed": 0, "generated_at": datetime.now(timezone.utc).isoformat()}

    trace_files = list(traces_root.rglob("trace.json"))

    # {(worker, category): {dispatches, successes, total_latency, retries, escalations}}
    stats: dict[tuple[str, str], dict] = {}
    analyzed = 0
    skipped_age = 0

    for tf in trace_files:
        if since_ts is not None:
            if _trace_timestamp(tf) < since_ts:
                skipped_age += 1
                continue

        try:
            data = json.loads(tf.read_text())
        except (json.JSONDecodeError, OSError):
            continue

        exec_block = data.get("execution") or {}
        routing_block = data.get("routing") or {}
        class_block = data.get("classification") or {}
        valid_block = data.get("validation") or {}
        retry_block = data.get("retry") or {}

        worker = exec_block.get("worker") or routing_block.get("selected_worker") or "unknown"
        category = class_block.get("category") or "unknown"
        task_class = class_block.get("task_class") or "unknown"
        lane = routing_block.get("lane") or "unknown"

        succeeded = bool(valid_block.get("passed"))
        duration = float(exec_block.get("duration_seconds") or 0)
        attempt = int(retry_block.get("attempt") or 1)
        escalated = bool(retry_block.get("escalated"))

        key = (worker, category)
        if key not in stats:
            stats[key] = {
                "worker": worker,
                "category": category,
                "lane": lane,
                "task_classes": set(),
                "dispatches": 0,
                "successes": 0,
                "total_latency": 0.0,
                "retries": 0,
                "escalations": 0,
            }
        s = stats[key]
        s["dispatches"] += 1
        s["successes"] += int(succeeded)
        s["total_latency"] += duration
        s["task_classes"].add(task_class)
        if attempt > 1:
            s["retries"] += 1
        if escalated:
            s["escalations"] += 1
        analyzed += 1

    rows = []
    for s in stats.values():
        d = s["dispatches"]
        rows.append({
            "worker": s["worker"],
            "category": s["category"],
            "lane": s["lane"],
            "task_classes": sorted(s["task_classes"]),
            "dispatches": d,
            "success_rate": round(s["successes"] / d, 3) if d else 0.0,
            "avg_latency_s": round(s["total_latency"] / d, 1) if d else 0.0,
            "retry_rate": round(s["retries"] / d, 3) if d else 0.0,
            "escalation_rate": round(s["escalations"] / d, 3) if d else 0.0,
        })

    rows.sort(key=lambda r: (r["worker"], r["category"]))

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "traces_analyzed": analyzed,
        "traces_skipped_by_age": skipped_age,
        "rows": rows,
    }


def print_table(data: dict):
    rows = data.get("rows", [])
    if not rows:
        print("No dispatch traces found.")
        return

    print(f"\nWorker dispatch statistics  ({data['traces_analyzed']} traces analyzed)")
    if data.get("traces_skipped_by_age", 0):
        print(f"  [{data['traces_skipped_by_age']} older traces excluded by --since filter]")
    print()

    # Header
    fmt = "{:<20} {:<14} {:<12} {:>10} {:>10} {:>12} {:>11} {:>14}"
    header = fmt.format(
        "Worker", "Category", "Lane", "Dispatches", "Success%", "AvgLatency", "Retry%", "Escalation%"
    )
    print(header)
    print("-" * len(header))

    for r in rows:
        flag = ""
        if r["success_rate"] < 0.7 and r["dispatches"] >= 5:
            flag = " ⚠"
        print(fmt.format(
            r["worker"][:20],
            r["category"][:14],
            r["lane"][:12],
            r["dispatches"],
            f"{r['success_rate']:.0%}",
            f"{r['avg_latency_s']:.0f}s",
            f"{r['retry_rate']:.0%}",
            f"{r['escalation_rate']:.0%}",
        ) + flag)

    print()
    # Highlight low-success workers
    warnings = [r for r in rows if r["success_rate"] < 0.7 and r["dispatches"] >= 5]
    if warnings:
        print("Workers with < 70% success rate (minimum 5 dispatches):")
        for r in warnings:
            print(f"  ⚠  {r['worker']} / {r['category']}: "
                  f"{r['success_rate']:.0%} success over {r['dispatches']} dispatches")
        print()

    # Suggest checking suggestions file
    print("Tip: run 'python -m core.janitor.cron --once --verbose' to generate improvement suggestions.")


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate dispatch trace stats by worker and category"
    )
    parser.add_argument("--since", default="", help="Only include traces from last N days/hours (e.g. 7d, 24h)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--project-dir", default=None, help="Project root (default: auto-detect)")
    args = parser.parse_args()

    start = args.project_dir or os.getcwd()
    project_dir = _find_project_dir(start)

    if not (project_dir / ".git").exists():
        print(f"No git repo found at or above {start}", file=sys.stderr)
        sys.exit(1)

    since_ts = _parse_since(args.since) if args.since else None
    data = aggregate(project_dir, since_ts=since_ts)

    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print_table(data)


if __name__ == "__main__":
    main()
