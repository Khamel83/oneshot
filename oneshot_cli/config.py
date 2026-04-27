"""Load .oneshot/config/models.yaml."""
from __future__ import annotations

import os
from pathlib import Path

import yaml

CONFIG_DIR = Path(__file__).resolve().parents[1] / ".oneshot" / "config"
CONFIG_FILE = CONFIG_DIR / "models.yaml"


def load_config(path: Path | None = None) -> dict:
    p = path or CONFIG_FILE
    if not p.exists():
        raise FileNotFoundError(f"Config not found: {p}")
    with open(p) as f:
        return yaml.safe_load(f)


def get_lane(cfg: dict, lane_name: str) -> dict:
    lane = cfg.get("lanes", {}).get(lane_name)
    if not lane:
        available = ", ".join(cfg.get("lanes", {}).keys()) or "(none)"
        raise ValueError(f"Unknown lane '{lane_name}'. Available: {available}")
    return lane


def resolve_provider_model(cfg: dict, lane_name: str) -> tuple[str, str, str]:
    """Return (provider_key, model_key, model_id) for a lane."""
    lane = get_lane(cfg, lane_name)
    provider_key = lane["current_provider"]
    model_key = lane["current_model"]
    provider = cfg["providers"][provider_key]
    model_id = provider["models"][model_key]["id"]
    return provider_key, model_key, model_id


def get_runner_template(cfg: dict, runner_name: str) -> dict:
    templates = cfg.get("runner_templates", {})
    tmpl = templates.get(runner_name)
    if not tmpl:
        available = ", ".join(templates.keys()) or "(none)"
        raise ValueError(f"Unknown runner '{runner_name}'. Available: {available}")
    return tmpl
