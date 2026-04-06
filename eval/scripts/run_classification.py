#!/usr/bin/env python3
"""Classification benchmark runner.

Tests infer_category() and infer_risk() against expected results.

Usage:
    python eval/scripts/run_classification.py [--set search|validation|holdout|all]
    python eval/scripts/run_classification.py --json  # JSON output
"""
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.task_schema import infer_category, infer_risk, TaskCategory, RiskLevel

BENCHMARKS_DIR = REPO_ROOT / "eval" / "benchmarks" / "classification"


def load_benchmark_set(split: str) -> list[dict]:
    """Load benchmark tasks from a split directory."""
    tasks = []
    d = BENCHMARKS_DIR / split
    if not d.exists():
        return tasks
    for f in sorted(d.glob("*.json")):
        with open(f) as fh:
            tasks.append(json.load(fh))
    return tasks


def run_classification(tasks: list[dict]) -> dict:
    """Run classification benchmarks and return results."""
    total = len(tasks)
    category_correct = 0
    category_total = 0
    risk_correct = 0
    risk_total = 0
    details = []

    for task in tasks:
        inp = task["input"]
        exp = task["expected"]
        tid = task["id"]

        # Test category
        if "category" in exp:
            got = infer_category(inp["description"]).value
            ok = got == exp["category"]
            category_correct += int(ok)
            category_total += 1
            details.append({
                "id": tid, "check": "category",
                "input": inp["description"][:60],
                "expected": exp["category"], "got": got, "correct": ok
            })

        # Test risk
        if "risk_level" in exp:
            got = infer_risk(inp["description"], inp.get("files")).value
            ok = got == exp["risk_level"]
            risk_correct += int(ok)
            risk_total += 1
            details.append({
                "id": tid, "check": "risk",
                "input": inp["description"][:60],
                "expected": exp["risk_level"], "got": got, "correct": ok
            })

    return {
        "total_tasks": total,
        "category": {
            "correct": category_correct,
            "total": category_total,
            "accuracy": round(category_correct / max(category_total, 1) * 100, 1)
        },
        "risk": {
            "correct": risk_correct,
            "total": risk_total,
            "accuracy": round(risk_correct / max(risk_total, 1) * 100, 1)
        },
        "details": details
    }


def main():
    parser = argparse.ArgumentParser(description="Run classification benchmarks")
    parser.add_argument("--set", dest="split", default="search",
                        choices=["search", "validation", "holdout", "all"])
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Output JSON instead of human-readable")
    args = parser.parse_args()

    if args.split == "all":
        sets = ["search", "validation", "holdout"]
    else:
        sets = [args.split]

    all_results = {}
    for split in sets:
        tasks = load_benchmark_set(split)
        if not tasks:
            print(f"Warning: No tasks found for split '{split}'", file=sys.stderr)
            continue
        result = run_classification(tasks)
        all_results[split] = result

    if args.as_json:
        print(json.dumps(all_results, indent=2))
    else:
        for split, result in all_results.items():
            cat = result["category"]
            risk = result["risk"]
            print(f"=== {split} ({result['total_tasks']} tasks) ===")
            if cat["total"] > 0:
                print(f"  Category accuracy: {cat['accuracy']}% ({cat['correct']}/{cat['total']})")
            if risk["total"] > 0:
                print(f"  Risk accuracy:     {risk['accuracy']}% ({risk['correct']}/{risk['total']})")

            failures = [d for d in result["details"] if not d["correct"]]
            if failures:
                print(f"  Failures ({len(failures)}):")
                for f in failures:
                    print(f"    {f['id']} [{f['check']}] expected={f['expected']} got={f['got']}")
                    print(f"      \"{f['input']}...\"")

        # Overall pass/fail
        any_regression = any(
            r["category"]["accuracy"] < 90 or r["risk"]["accuracy"] < 85
            for r in all_results.values()
        )
        if any_regression:
            print("\nREGRESSION DETECTED")
            sys.exit(1)
        else:
            print("\nOK")


if __name__ == "__main__":
    main()
