"""Janitor LLM caller — multi-provider pool with openrouter/free backwards compatibility.

Routes through ProviderPool (config/janitor_providers.yaml) which tries providers
in priority order: openrouter_free → qwen_studio → gemini_api → codex.

Backwards-compatible API:
  call_free(prompt, system, max_tokens, timeout) — unchanged signature
  extract_structured(prompt, system, schema_hint) — unchanged signature

New preferred API:
  call_janitor(prompt, system, max_tokens, timeout) — same as call_free
  extract_structured_janitor(prompt, system, schema_hint) — same as extract_structured

Rate limits and usage are tracked per-provider in .janitor/usage.jsonl.
Budget is tracked in .janitor/budget.json (defaults to $0 — free providers only).
"""

from __future__ import annotations

import os
from typing import Optional

# Re-export the pool-based functions as the primary interface
from core.janitor.provider_pool import (
    call_janitor,
    extract_structured_janitor,
    get_pool,
    ProviderPool,
)

# ---------------------------------------------------------------------------
# Backwards-compatible shims
# ---------------------------------------------------------------------------

def call_free(
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = 1024,
    timeout: int = 30,
) -> str:
    """Send a prompt to the janitor provider pool and return the response text.

    Backwards-compatible shim over call_janitor(). Existing callers work unchanged.
    Previously called openrouter/free directly; now routes through ProviderPool
    which falls back to qwen_studio, gemini_api, codex when openrouter hits its limit.
    """
    return call_janitor(prompt, system=system, max_tokens=max_tokens, timeout=timeout)


def extract_structured(
    prompt: str,
    system: Optional[str] = None,
    schema_hint: Optional[str] = None,
) -> dict:
    """Call provider pool and parse JSON response.

    Backwards-compatible shim over extract_structured_janitor().
    Tries: direct parse, strip code fences, extract JSON from text,
    fall back to {"raw": text}.
    """
    return extract_structured_janitor(prompt, system=system, schema_hint=schema_hint)


def get_usage_stats() -> dict:
    """Get current usage statistics across all providers."""
    pool = get_pool()
    return pool.status()


__all__ = [
    "call_free",
    "extract_structured",
    "call_janitor",
    "extract_structured_janitor",
    "get_usage_stats",
    "get_pool",
    "ProviderPool",
]
