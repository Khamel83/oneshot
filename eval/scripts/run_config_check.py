#!/usr/bin/env python3
"""Config consistency validation.

Cross-validates YAML configs against Python enums and each other.

Usage:
    python eval/scripts/run_config_check.py [--json]
"""
import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.task_schema import TaskClass, TaskCategory, LANE_ASSIGNMENTS, CATEGORY_ASSIGNMENTS

CONFIG_DIR = REPO_ROOT / "config"


def load_yaml(name: str) -> dict:
    with open(CONFIG_DIR / name) as f:
        return yaml.safe_load(f)


def run_config_check() -> dict:
    errors = []
    warnings = []

    lanes = load_yaml("lanes.yaml")["lanes"]
    workers = load_yaml("workers.yaml")["workers"]
    models = load_yaml("models.yaml")["models"]

    # 1. Every TaskClass enum value has a LANE_ASSIGNMENTS entry
    tc_values = {tc.value for tc in TaskClass}
    assigned_classes = set(LANE_ASSIGNMENTS.keys())
    for tc in tc_values:
        # LANE_ASSIGNMENTS keys are TaskClass enum members, check by value
        has_assignment = any(k.value == tc for k in LANE_ASSIGNMENTS)
        if not has_assignment:
            errors.append(f"TaskClass '{tc}' has no LANE_ASSIGNMENTS entry")

    # 2. Every LANE_ASSIGNMENTS lane exists in lanes.yaml
    for tc, lane in LANE_ASSIGNMENTS.items():
        if lane not in lanes:
            errors.append(f"LANE_ASSIGNMENTS[{tc}] references unknown lane '{lane}'")

    # 3. Every worker in lane worker_pools is a known dispatch worker
    # Known dispatch workers: codex, gemini_cli, glm_claude, claw_code, claude_code
    # workers.yaml defines machine-level workers (local, oci, macmini, homelab, claw, glm),
    # which are different from dispatch worker names.
    known_dispatch_workers = {
        "claude_code", "codex", "gemini_cli", "glm_claude", "claw_code"
    }
    for lane_name, lane_cfg in lanes.items():
        for w in lane_cfg.get("worker_pool", []):
            if w not in known_dispatch_workers:
                errors.append(f"lane '{lane_name}' worker_pool contains unknown worker '{w}'")

    # 4. Every category_preference key matches a TaskCategory enum value
    cat_values = {c.value for c in TaskCategory}
    for lane_name, lane_cfg in lanes.items():
        for cat in lane_cfg.get("category_preference", {}):
            if cat not in cat_values:
                errors.append(f"lane '{lane_name}' category_preference has unknown category '{cat}'")

    # 5. Every model lane exists in lanes.yaml
    for model_id, model_cfg in models.items():
        if model_id == "claw_code":
            continue  # claw_code is a special entry
        lane = model_cfg.get("lane")
        if lane and lane not in lanes:
            errors.append(f"model '{model_id}' has unknown lane '{lane}'")

    # 6. workers.yaml glm entry has plan_expires
    glm = workers.get("glm", {})
    if "plan_expires" not in glm:
        warnings.append("workers.yaml glm entry missing plan_expires")

    # 7. Every lane has a review_with field
    for lane_name, lane_cfg in lanes.items():
        if "review_with" not in lane_cfg:
            errors.append(f"lane '{lane_name}' missing review_with")

    # 8. fallback_lane references valid lanes
    for lane_name, lane_cfg in lanes.items():
        fb = lane_cfg.get("fallback_lane")
        if fb and fb not in lanes:
            errors.append(f"lane '{lane_name}' fallback_lane references unknown lane '{fb}'")

    # 9. CATEGORY_ASSIGNMENTS values are valid TaskCategory enum values
    for tc, cat in CATEGORY_ASSIGNMENTS.items():
        if cat.value not in cat_values:
            errors.append(f"CATEGORY_ASSIGNMENTS[{tc}] has invalid category '{cat.value}'")

    # 10. search.yaml modes all have providers
    search = load_yaml("search.yaml")
    for mode, cfg in search.get("modes", {}).items():
        if not cfg.get("providers"):
            warnings.append(f"search.yaml mode '{mode}' has no providers")

    return {
        "total_checks": 10,
        "errors": errors,
        "warnings": warnings,
        "passed": len(errors) == 0
    }


def main():
    parser = argparse.ArgumentParser(description="Validate config consistency")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    result = run_config_check()

    if args.as_json:
        print(json.dumps(result, indent=2))
    else:
        print("=== Config Consistency ===")
        if result["passed"]:
            print("  All checks passed")
            if result["warnings"]:
                print(f"\n  Warnings ({len(result['warnings'])}):")
                for w in result["warnings"]:
                    print(f"    - {w}")
        else:
            print(f"  FAILED: {len(result['errors'])} error(s)")
            for e in result["errors"]:
                print(f"    - {e}")
            if result["warnings"]:
                print(f"\n  Warnings ({len(result['warnings'])}):")
                for w in result["warnings"]:
                    print(f"    - {w}")
            sys.exit(1)


if __name__ == "__main__":
    main()
