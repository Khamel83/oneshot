"""Argus search client - thin HTTP wrapper around Argus broker API."""

import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

DEFAULT_BASE_URL = "http://localhost:8005"

# Config file paths to search (first found wins)
_CONFIG_PATHS = [
    Path(__file__).resolve().parent.parent.parent / "config" / "search.yaml",
    Path("config/search.yaml"),
]


def _load_config() -> dict:
    """Load search config from config/search.yaml. Returns empty dict if not found."""
    import yaml
    for path in _CONFIG_PATHS:
        if path.is_file():
            with open(path) as f:
                return yaml.safe_load(f) or {}
    return {}


_config_cache = None


def _get_config() -> dict:
    """Lazily load and cache config."""
    global _config_cache
    if _config_cache is None:
        _config_cache = _load_config()
    return _config_cache


def get_base_url() -> str:
    """Get Argus base URL from config or default."""
    config = _get_config()
    return config.get("search", {}).get("base_url", DEFAULT_BASE_URL)


def search(query: str, mode: str = "discovery", base_url: Optional[str] = None,
           max_results: Optional[int] = None) -> dict:
    """Search via Argus broker. Returns normalized results.

    Args:
        query: Search query string.
        mode: Search mode (discovery, precision, cheap, research).
        base_url: Argus server URL. Defaults to localhost:8005.
        max_results: Override max results from config.
    """
    base = base_url or get_base_url()
    payload = {"query": query, "mode": mode}
    if max_results:
        payload["max_results"] = max_results

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{base}/api/search",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def health(base_url: Optional[str] = None) -> dict:
    """Check Argus provider health status."""
    base = base_url or get_base_url()
    req = urllib.request.Request(f"{base}/api/health")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


def is_available(base_url: Optional[str] = None) -> bool:
    """Check if Argus server is reachable."""
    try:
        health(base_url)
        return True
    except (urllib.error.URLError, OSError):
        return False
