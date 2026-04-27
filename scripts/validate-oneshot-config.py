#!/usr/bin/env python3
"""Validate consistency between the legacy router config and oneshot CLI config."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
ONESHOT_CONFIG = REPO_ROOT / ".oneshot" / "config" / "models.yaml"
WORKERS_CONFIG = REPO_ROOT / "config" / "workers.yaml"

WORKER_HARNESS_BRIDGE = {
    "claude_code": "claude_review",
    "glm_claude": "zai",
    "opencode": "opencode_go",
    "claw_code": "claw_code",
    "openrouter_api": "openrouter_api",
}


def load_yaml(path: Path) -> dict:
    with open(path) as handle:
        return yaml.safe_load(handle) or {}


def validate() -> list[str]:
    errors: list[str] = []
    oneshot = load_yaml(ONESHOT_CONFIG)
    workers = load_yaml(WORKERS_CONFIG)

    providers = oneshot.get("providers", {})
    lanes = oneshot.get("lanes", {})
    templates = oneshot.get("runner_templates", {})
    worker_defs = workers.get("workers", {})

    for provider_name, provider in providers.items():
        if provider.get("kind") == "manual":
            continue
        if provider_name not in templates and provider_name not in {
            "claw_code",
            "openrouter_api",
        }:
            errors.append(f"provider '{provider_name}' has no runner template")

    for lane_name, lane in lanes.items():
        for provider_field, model_field in (
            ("current_provider", "current_model"),
            ("future_provider", "future_model"),
        ):
            provider_name = lane.get(provider_field)
            model_name = lane.get(model_field)
            if not provider_name or not model_name:
                errors.append(
                    f"lane '{lane_name}' missing {provider_field}/{model_field}"
                )
                continue

            provider = providers.get(provider_name)
            if not provider:
                errors.append(
                    f"lane '{lane_name}' references unknown provider '{provider_name}'"
                )
                continue

            if provider.get("kind") != "manual" and model_name not in provider.get(
                "models", {}
            ):
                errors.append(
                    f"lane '{lane_name}' references unknown model '{model_name}' on provider '{provider_name}'"
                )

    for worker_name, worker in worker_defs.items():
        harness = worker.get("harness")
        if not harness:
            errors.append(f"worker '{worker_name}' missing harness")
            continue

        bridged_provider = WORKER_HARNESS_BRIDGE.get(harness)
        if bridged_provider is None:
            errors.append(
                f"worker '{worker_name}' uses unknown harness bridge '{harness}'"
            )
            continue

        if bridged_provider not in providers and bridged_provider not in {
            "claw_code",
            "openrouter_api",
        }:
            errors.append(
                f"worker '{worker_name}' harness '{harness}' maps to missing provider '{bridged_provider}'"
            )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("=== OneShot Config Bridge ===")
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("=== OneShot Config Bridge ===")
    print("All checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
