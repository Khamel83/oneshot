"""Lane policy - reads config/lanes.yaml and resolves task -> lane -> worker."""

import json
from pathlib import Path
from typing import Optional

import yaml

from core.task_schema import LANE_ASSIGNMENTS, RISK_AUTONOMY, RiskLevel, TaskClass

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"


def load_lanes(config_path: Optional[str] = None) -> dict:
    path = config_path or str(CONFIG_DIR / "lanes.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def get_worker_pool(lane: str, config_path: Optional[str] = None) -> list[str]:
    """Return the worker pool for a given lane."""
    lanes = load_lanes(config_path)
    return lanes.get("lanes", {}).get(lane, {}).get("worker_pool", [])


def get_reviewer(lane: str, config_path: Optional[str] = None) -> str:
    """Return the reviewer harness for a given lane."""
    lanes = load_lanes(config_path)
    return lanes.get("lanes", {}).get(lane, {}).get("review_with", "claude_code")


def get_fallback_lane(lane: str, config_path: Optional[str] = None) -> Optional[str]:
    """Return the fallback lane for escalation on failure."""
    lanes = load_lanes(config_path)
    return lanes.get("lanes", {}).get(lane, {}).get("fallback_lane")


def get_search_backend(lane: str, config_path: Optional[str] = None) -> Optional[str]:
    """Return the search backend for a lane (e.g., 'argus')."""
    lanes = load_lanes(config_path)
    return lanes.get("lanes", {}).get(lane, {}).get("search_backend")


def resolve(task_class: str, risk_level: str = "medium", config_path: Optional[str] = None) -> dict:
    """Resolve a task class to a full routing directive.

    Returns JSON-serializable dict with lane, workers, reviewer, search, fallback, and risk.
    Used by skill prompts via: python -m core.router.resolve --class implement_small
    """
    tc = TaskClass(task_class)
    risk = RiskLevel(risk_level)
    lane = LANE_ASSIGNMENTS.get(tc, "balanced")
    workers = get_worker_pool(lane, config_path)
    reviewer = get_reviewer(lane, config_path)
    fallback = get_fallback_lane(lane, config_path)
    search = get_search_backend(lane, config_path)

    return {
        "task_class": task_class,
        "lane": lane,
        "workers": workers,
        "review_with": reviewer,
        "search_backend": search,
        "fallback_lane": fallback,
        "risk": {
            "level": risk.value,
            **RISK_AUTONOMY[risk],
        },
    }
