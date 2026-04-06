"""OpenRouter free model caller for janitor tasks.

Direct HTTP calls to openrouter/free — no SDK dependency.
Used for bounded extraction/summarization tasks where $0 cost matters
more than model quality.

Rate limits (openrouter/free):
  - 1000 requests/day
  - 20 requests/minute
Typical session usage: 5-10 calls. Tracked loosely via .oneshot/usage.jsonl.
"""

import json
import os
import re
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# openrouter/free endpoint
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Rate limits
DAILY_LIMIT = 1000
MINUTE_LIMIT = 20

# Try env first, then vault
DEFAULT_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")


def _get_api_key() -> str:
    """Get OpenRouter API key from environment or vault."""
    if DEFAULT_API_KEY:
        return DEFAULT_API_KEY
    import subprocess
    try:
        r = subprocess.run(
            ["secrets", "get", "OPENROUTER_API_KEY"],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    raise RuntimeError("No OPENROUTER_API_KEY found. Set env var or add to vault.")


def _usage_log_path() -> Path:
    """Path to the usage log file."""
    project = Path(os.getcwd())
    for parent in [project] + list(project.parents):
        if (parent / ".git").exists():
            d = parent / ".oneshot"
            d.mkdir(exist_ok=True)
            return d / "usage.jsonl"
    return Path(".oneshot/usage.jsonl")


def _check_rate_limit() -> bool:
    """Check if we're within rate limits. Returns True if OK to proceed."""
    path = _usage_log_path()
    if not path.exists():
        return True

    now = time.time()
    minute_ago = now - 60
    day_ago = now - 86400

    recent_minute = 0
    recent_day = 0

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = entry.get("ts", 0)
                if ts > minute_ago:
                    recent_minute += 1
                if ts > day_ago:
                    recent_day += 1
            except (json.JSONDecodeError, KeyError):
                continue

    if recent_minute >= MINUTE_LIMIT:
        print(f"[janitor] Rate limited: {recent_minute}/{MINUTE_LIMIT} per minute")
        return False
    if recent_day >= DAILY_LIMIT:
        print(f"[janitor] Daily limit reached: {recent_day}/{DAILY_LIMIT}")
        return False

    return True


def _log_usage(model: str, tokens_in: int = 0, tokens_out: int = 0):
    """Log API usage for rate limit tracking."""
    entry = {
        "ts": time.time(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
    }
    path = _usage_log_path()
    with open(path, "a") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")


def get_usage_stats() -> dict:
    """Get current usage statistics."""
    path = _usage_log_path()
    if not path.exists():
        return {"today": 0, "this_minute": 0, "daily_limit": DAILY_LIMIT, "minute_limit": MINUTE_LIMIT}

    now = time.time()
    minute_ago = now - 60
    day_ago = now - 86400

    recent_minute = 0
    recent_day = 0
    total = 0

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = entry.get("ts", 0)
                total += 1
                if ts > minute_ago:
                    recent_minute += 1
                if ts > day_ago:
                    recent_day += 1
            except (json.JSONDecodeError, KeyError):
                continue

    return {
        "today": recent_day,
        "this_minute": recent_minute,
        "total": total,
        "daily_limit": DAILY_LIMIT,
        "minute_limit": MINUTE_LIMIT,
    }


def call_free(
    prompt: str,
    system: str | None = None,
    max_tokens: int = 1024,
    timeout: int = 30,
) -> str:
    """Send a prompt to openrouter/free and return the response text.

    Args:
        prompt: The user message to send.
        system: Optional system prompt for task context.
        max_tokens: Max response tokens (default 1024).
        timeout: Per-attempt timeout in seconds (default 30).

    Returns:
        The model's response text.

    Raises:
        RuntimeError: If rate limited or API call fails after retries.
    """
    if not _check_rate_limit():
        raise RuntimeError("Rate limit reached. Wait before retrying.")

    api_key = _get_api_key()

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    payload_dict = {
        "model": "openrouter/free",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.1,
    }

    payload = json.dumps(payload_dict).encode()

    req = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Khamel83/oneshot",
            "X-Title": "OneShot Janitor",
        },
    )

    last_error = None
    model_used = "unknown"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
                content = data["choices"][0]["message"]["content"]
                model_used = data.get("model", "unknown")

                # Log usage
                usage = data.get("usage", {})
                _log_usage(
                    model_used,
                    tokens_in=usage.get("prompt_tokens", 0),
                    tokens_out=usage.get("completion_tokens", 0),
                )

                if attempt > 0:
                    print(f"[janitor] succeeded on attempt {attempt + 1} via {model_used}")
                return content
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode()[:200]
            except Exception:
                pass
            last_error = f"HTTP {e.code}: {e.reason} — {body}"
            if e.code == 429:
                _log_usage("rate_limited")
                raise RuntimeError("Rate limited by OpenRouter. Back off.")
            if e.code >= 500:
                continue
            break
        except (urllib.error.URLError, TimeoutError, KeyError, IndexError) as e:
            last_error = str(e)
            continue

    _log_usage("failed")
    raise RuntimeError(f"openrouter/free failed after 3 attempts: {last_error}")


def extract_structured(
    prompt: str,
    system: str | None = None,
    schema_hint: str | None = None,
) -> dict:
    """Call free model and parse JSON response.

    Tries multiple parsing strategies:
    1. Direct JSON parse
    2. Strip markdown code fences
    3. Extract JSON from surrounding text
    4. Fall back to {"raw": text} if nothing works

    Args:
        prompt: The extraction prompt.
        system: Optional system prompt.
        schema_hint: Expected JSON shape, appended to prompt.

    Returns:
        Parsed dict. Falls back to {"raw": text} on parse failure.
    """
    if schema_hint:
        prompt += f"\n\nRespond with valid JSON only. No explanation. Expected shape: {schema_hint}"

    try:
        raw = call_free(prompt, system=system, max_tokens=2048, timeout=30)
    except RuntimeError as e:
        return {"raw": str(e), "status": "failed"}

    stripped = raw.strip()

    # Strategy 1: Direct parse
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Strip code fences
    if stripped.startswith("```"):
        lines = stripped.split("\n")
        inner = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            return json.loads(inner.strip())
        except json.JSONDecodeError:
            pass

    # Strategy 3: Find JSON object in text
    match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', stripped, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Strategy 4: Fall back to raw text
    print("[janitor] Could not parse JSON from free model, returning raw text")
    return {"raw": stripped, "status": "unstructured"}
