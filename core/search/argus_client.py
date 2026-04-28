"""Argus search client - thin HTTP wrapper around Argus broker API."""

import json
import os
import subprocess
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


def _load_api_key_from_vault() -> Optional[str]:
    try:
        result = subprocess.run(
            ["secrets", "get", "ARGUS_API_KEY", "argus"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def get_api_key() -> Optional[str]:
    """Resolve the Argus caller API key from config, env, or vault."""
    config = _get_config().get("search", {})
    env_name = config.get("api_key_env", "ARGUS_API_KEY")
    env_value = os.environ.get(env_name, "").strip()
    if env_value:
        return env_value

    config_value = str(config.get("api_key", "")).strip()
    if config_value:
        return config_value

    return _load_api_key_from_vault()


def _build_headers(*, include_json: bool = False) -> dict[str, str]:
    headers: dict[str, str] = {}
    if include_json:
        headers["Content-Type"] = "application/json"

    api_key = get_api_key()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def _request_json(url: str, *, payload: Optional[dict] = None, timeout: int = 30) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        headers=_build_headers(include_json=payload is not None),
        method="POST" if payload is not None else "GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


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

    return _request_json(f"{base}/api/search", payload=payload)


def health(base_url: Optional[str] = None) -> dict:
    """Check Argus provider health status."""
    base = base_url or get_base_url()
    return _request_json(f"{base}/api/health", timeout=5)


def recover_article(url: str, title: Optional[str] = None, domain: Optional[str] = None,
                    base_url: Optional[str] = None) -> dict:
    base = base_url or get_base_url()
    payload = {"url": url}
    if title:
        payload["title"] = title
    if domain:
        payload["domain"] = domain
    return _request_json(f"{base}/api/workflows/recover-article", payload=payload)


def capture_site(url: str, soft_page_limit: int = 75, hard_page_limit: int = 200,
                 base_url: Optional[str] = None) -> dict:
    base = base_url or get_base_url()
    payload = {
        "url": url,
        "soft_page_limit": soft_page_limit,
        "hard_page_limit": hard_page_limit,
    }
    return _request_json(f"{base}/api/workflows/capture-site", payload=payload)


def build_research_pack(topic: str, official_url: Optional[str] = None,
                        max_research_pages: int = 40, base_url: Optional[str] = None) -> dict:
    base = base_url or get_base_url()
    payload = {
        "topic": topic,
        "max_research_pages": max_research_pages,
    }
    if official_url:
        payload["official_url"] = official_url
    return _request_json(f"{base}/api/workflows/build-research-pack", payload=payload)


def workflow_status(run_id: str, base_url: Optional[str] = None) -> dict:
    base = base_url or get_base_url()
    return _request_json(f"{base}/api/workflows/{run_id}")


def is_available(base_url: Optional[str] = None) -> bool:
    """Check if Argus server is reachable."""
    try:
        health(base_url)
        return True
    except (urllib.error.URLError, OSError):
        return False
