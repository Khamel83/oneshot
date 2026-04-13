"""Harvest usage data from all registered projects into a central aggregate.

Runs weekly as part of the oneshot cron job.
Reads ~/.config/oneshot/projects.json → visits each project's .janitor/usage.jsonl
Writes ~/.config/oneshot/aggregate-usage.json

Fast: only reads files modified since last harvest.
"""

import json
import time
from datetime import date
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".config" / "oneshot"
_AGGREGATE = CONFIG_DIR / "aggregate-usage.json"


def harvest(since_days: int = 30) -> dict:
    """Aggregate usage across all registered projects. Returns summary dict."""
    from core.janitor.registry import list_projects

    projects = list_projects()
    if not projects:
        return {"status": "no_projects", "projects": 0}

    cutoff = time.time() - since_days * 86400
    summary: dict[str, dict] = {}  # project_name → stats
    total_calls = total_cost = 0

    for proj in projects:
        path = Path(proj["path"]) / ".janitor" / "usage.jsonl"
        if not path.exists():
            continue

        calls = 0
        cost = 0.0
        by_provider: dict[str, int] = {}

        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("ts", 0) < cutoff:
                    continue
                provider = e.get("provider", "openrouter_free")
                if provider in ("rate_limited", "failed"):
                    continue
                calls += 1
                cost += float(e.get("cost_usd", 0.0))
                by_provider[provider] = by_provider.get(provider, 0) + 1

        if calls > 0:
            name = proj["name"]
            summary[name] = {
                "path": proj["path"],
                "calls": calls,
                "cost_usd": round(cost, 6),
                "by_provider": by_provider,
                "last_seen": proj.get("last_seen", 0),
            }
            total_calls += calls
            total_cost += cost

    result = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "period_days": since_days,
        "projects_active": len(summary),
        "projects_registered": len(projects),
        "total_calls": total_calls,
        "total_cost_usd": round(total_cost, 6),
        "by_project": summary,
    }

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    _AGGREGATE.write_text(json.dumps(result, indent=2))
    return result


def print_report():
    """Print a human-readable usage report to stdout."""
    if not _AGGREGATE.exists():
        print("No harvest data yet. Run: python -m core.janitor.harvest")
        return

    try:
        data = json.loads(_AGGREGATE.read_text())
    except (json.JSONDecodeError, OSError):
        print("Harvest file unreadable.")
        return

    print(f"\nJanitor usage ({data.get('period_days', 30)}d)  "
          f"— {data.get('projects_active', 0)}/{data.get('projects_registered', 0)} projects active\n")

    fmt = "{:<22} {:>8} {:>10} {}"
    print(fmt.format("Project", "Calls", "Cost", "Providers"))
    print("-" * 60)

    for name, s in sorted(data.get("by_project", {}).items(),
                           key=lambda x: x[1]["calls"], reverse=True):
        providers = " ".join(f"{p}({n})" for p, n in s["by_provider"].items())
        cost = f"${s['cost_usd']:.4f}" if s["cost_usd"] > 0 else "$0"
        print(fmt.format(name[:22], s["calls"], cost, providers))

    print("-" * 60)
    total_cost = data.get("total_cost_usd", 0)
    print(fmt.format(
        "TOTAL",
        data.get("total_calls", 0),
        f"${total_cost:.4f}" if total_cost > 0 else "$0",
        "",
    ))
    print(f"\nAggregate: {_AGGREGATE}")


if __name__ == "__main__":
    import sys
    if "--report" in sys.argv:
        print_report()
    else:
        result = harvest()
        print(f"Harvested {result['projects_active']} projects, "
              f"{result['total_calls']} calls, ${result['total_cost_usd']:.4f}")
