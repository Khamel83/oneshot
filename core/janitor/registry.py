"""Project registry — auto-register any git repo that runs janitor.

Writes to ~/.config/oneshot/projects.json (atomic, safe for concurrent calls).
Called once per SessionStart, adds ~1ms overhead.
"""

import json
import time
from pathlib import Path
from typing import Optional

CONFIG_DIR = Path.home() / ".config" / "oneshot"
_REGISTRY = CONFIG_DIR / "projects.json"


def auto_register(project_dir: str) -> None:
    """Record this project. No-op if already registered today."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    projects: dict = {}
    if _REGISTRY.exists():
        try:
            projects = json.loads(_REGISTRY.read_text())
        except (json.JSONDecodeError, OSError):
            pass

    key = str(project_dir)
    now = time.time()

    # Skip write if already seen in last hour (hot path optimisation)
    existing = projects.get(key, {})
    if now - existing.get("last_seen", 0) < 3600:
        return

    if key not in projects:
        projects[key] = {
            "path": key,
            "name": Path(key).name,
            "first_seen": now,
        }
    projects[key]["last_seen"] = now

    # Atomic write
    tmp = _REGISTRY.with_suffix(".tmp")
    tmp.write_text(json.dumps(projects, indent=2))
    tmp.replace(_REGISTRY)


def list_projects() -> list[dict]:
    """Return all registered projects, most-recently-seen first."""
    if not _REGISTRY.exists():
        return []
    try:
        data = json.loads(_REGISTRY.read_text())
        return sorted(data.values(), key=lambda x: x.get("last_seen", 0), reverse=True)
    except (json.JSONDecodeError, OSError):
        return []
