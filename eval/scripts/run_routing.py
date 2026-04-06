#!/usr/bin/env python3
"""Routing benchmark runner.

Tests resolve() against expected lane, worker order, and review assignment.

Usage:
    python eval/scripts/run_routing.py [--json]
"""
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.router.lane_policy import resolve

BENCHMARKS_DIR = REPO_ROOT / "eval" / "benchmarks" / "routing"


def load_benchmarks() -> list[dict]:
    tasks = []
    if not BENCHMARKS_DIR.exists():
        return tasks
    for f in sorted(BENCHMARKS_DIR.glob("*.json")):
        with open(f) as fh:
            tasks.append(json.load(fh))
    return tasks


def run_routing(tasks: list[dict]) -> dict:
    total = len(tasks)
    lane_correct = 0
    worker_first_correct = 0
    review_correct = 0
    details = []

    for task in tasks:
        inp = task["input"]
        exp = task["expected"]
        tid = task["id"]

        try:
            result = resolve(inp["task_class"], category=inp.get("category"))
        except Exception as e:
            details.append({
                "id": tid, "error": str(e), "correct": False
            })
            continue

        # Check lane
        lane_ok = result["lane"] == exp["lane"]
        if lane_ok:
            lane_correct += 1

        # Check first worker
        worker_ok = result["workers"][0] == exp["workers_first"] if result["workers"] else False
        if worker_ok:
            worker_first_correct += 1

        # Check review
        review_ok = result["review_with"] == exp["review_with"]
        if review_ok:
            review_correct += 1

        correct = lane_ok and worker_ok and review_ok
        details.append({
            "id": tid,
            "lane": {"expected": exp["lane"], "got": result["lane"], "ok": lane_ok},
            "worker_first": {"expected": exp["workers_first"],
                             "got": result["workers"][0] if result["workers"] else None,
                             "ok": worker_ok},
            "review_with": {"expected": exp["review_with"], "got": result["review_with"], "ok": review_ok},
            "correct": correct
        })

    return {
        "total": total,
        "lane_correct": lane_correct,
        "worker_first_correct": worker_first_correct,
        "review_correct": review_correct,
        "accuracy": round(
            sum(1 for d in details if d.get("correct", False)) / max(total, 1) * 100, 1
        ),
        "details": details
    }


def main():
    parser = argparse.ArgumentParser(description="Run routing benchmarks")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    tasks = load_benchmarks()
    if not tasks:
        print("No routing benchmarks found", file=sys.stderr)
        sys.exit(1)

    result = run_routing(tasks)

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print(f"=== Routing ({result['total']} tasks) ===")
        print(f"  Lane correct:         {result['lane_correct']}/{result['total']}")
        print(f"  Worker first correct: {result['worker_first_correct']}/{result['total']}")
        print(f"  Review correct:       {result['review_correct']}/{result['total']}")
        print(f"  Overall accuracy:     {result['accuracy']}%")

        failures = [d for d in result["details"] if not d.get("correct", True)]
        if failures:
            print(f"\n  Failures ({len(failures)}):")
            for f in failures:
                if "error" in f:
                    print(f"    {f['id']}: ERROR - {f['error']}")
                    continue
                for check in ["lane", "worker_first", "review_with"]:
                    if not f[check]["ok"]:
                        print(f"    {f['id']} [{check}] expected={f[check]['expected']} got={f[check]['got']}")

        if result["accuracy"] < 95:
            print("\nREGRESSION DETECTED")
            sys.exit(1)
        else:
            print("\nOK")


if __name__ == "__main__":
    main()
