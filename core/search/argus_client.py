"""Argus search client - thin HTTP wrapper around Argus broker API."""

import json
import urllib.error
import urllib.request
from typing import Optional

DEFAULT_BASE_URL = "http://localhost:8005"


def search(query: str, mode: str = "discovery", base_url: Optional[str] = None,
           max_results: Optional[int] = None) -> dict:
    """Search via Argus broker. Returns normalized results.

    Args:
        query: Search query string.
        mode: Search mode (discovery, precision, cheap, research).
        base_url: Argus server URL. Defaults to localhost:8005.
        max_results: Override max results from config.
    """
    base = base_url or DEFAULT_BASE_URL
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
    base = base_url or DEFAULT_BASE_URL
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
