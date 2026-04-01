"""Model registry - reads config/models.yaml and provides lookup functions."""

from pathlib import Path
from typing import Optional

import yaml

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"


def load_models(config_path: Optional[str] = None) -> dict:
    path = config_path or str(CONFIG_DIR / "models.yaml")
    with open(path) as f:
        return yaml.safe_load(f)


def models_for_lane(lane: str, config_path: Optional[str] = None) -> list[str]:
    """Return model IDs assigned to a given lane."""
    models = load_models(config_path)
    return [k for k, v in models.get("models", {}).items() if v.get("lane") == lane]


def can_plan(model_id: str, config_path: Optional[str] = None) -> bool:
    """Check if a model is allowed to plan."""
    models = load_models(config_path)
    return models.get("models", {}).get(model_id, {}).get("can_plan", False)


def can_review(model_id: str, config_path: Optional[str] = None) -> bool:
    """Check if a model is allowed to review."""
    models = load_models(config_path)
    return models.get("models", {}).get(model_id, {}).get("can_review", False)


def get_model_info(model_id: str, config_path: Optional[str] = None) -> dict:
    """Get full model info dict."""
    models = load_models(config_path)
    return models.get("models", {}).get(model_id, {})
