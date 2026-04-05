"""Lane policy - reads config/lanes.yaml and resolves task -> lane -> worker."""

import json
from pathlib import Path
from typing import Optional

import yaml

from core.task_schema import (
    CATEGORY_ASSIGNMENTS,
    LANE_ASSIGNMENTS,
    RISK_AUTONOMY,
    RiskLevel,
    TaskCategory,
    TaskClass,
)

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


def get_category_preference(lane: str, category: str, config_path: Optional[str] = None) -> Optional[list[str]]:
    """Return the preferred worker order for a category within a lane."""
    lanes = load_lanes(config_path)
    prefs = lanes.get("lanes", {}).get(lane, {}).get("category_preference", {})
    return prefs.get(category)


def reorder_by_preference(workers: list[str], preference: list[str]) -> list[str]:
    """Reorder workers by preference list, keeping unavailable workers at end.

    Workers not in preference are appended in their original order.
    """
    pref_set = set(preference)
    ordered = [w for w in preference if w in workers]
    rest = [w for w in workers if w not in pref_set]
    return ordered + rest


def resolve(task_class: str, risk_level: str = "medium",
             category: str = None, config_path: Optional[str] = None) -> dict:
    """Resolve a task class to a full routing directive.

    Returns JSON-serializable dict with lane, workers, reviewer, search, fallback, and risk.
    Used by skill prompts via: python -m core.router.resolve --class implement_small

    If category is provided and the lane has category_preference, workers are reordered
    to prefer workers best-suited for that category.
    """
    tc = TaskClass(task_class)
    risk = RiskLevel(risk_level)
    lane = LANE_ASSIGNMENTS.get(tc, "balanced")
    workers = get_worker_pool(lane, config_path)

    # Apply category-based worker preference
    if category:
        pref = get_category_preference(lane, category, config_path)
        if pref:
            workers = reorder_by_preference(workers, pref)
    else:
        # Infer category from task class if not explicitly provided
        inferred = CATEGORY_ASSIGNMENTS.get(tc)
        if inferred:
            pref = get_category_preference(lane, inferred.value, config_path)
            if pref:
                workers = reorder_by_preference(workers, pref)

    reviewer = get_reviewer(lane, config_path)
    fallback = get_fallback_lane(lane, config_path)
    search = get_search_backend(lane, config_path)

    return {
        "task_class": task_class,
        "category": category or (inferred.value if inferred else None),
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
