"""Lightweight helper for direct OpenAI-compatible API calls.

Used by the opencode_go_api runner template for summaries, extraction,
and classification tasks where the model doesn't need shell access.

Usage:
    python3 -c "from core.dispatch.direct_api import call; call(base_url, model, task_file)"
"""

import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error

_DEFAULT_TIMEOUT = 120
_MASK_RE = re.compile(r"(sk-[a-zA-Z0-9]{8,}|key-[a-zA-Z0-9]{8,})")


def _mask_secrets(text: str) -> str:
    return _MASK_RE.sub("[REDACTED]", text)


def _get_api_key() -> str:
    key = os.environ.get("OPENCODE_GO_API_KEY", "")
    if not key:
        try:
            key = subprocess.check_output(
                ["secrets", "get", "OPENCODE_GO_API_KEY"], stderr=subprocess.DEVNULL
            ).decode().strip()
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    if not key:
        print("ERROR: OPENCODE_GO_API_KEY not set and secrets CLI unavailable", file=sys.stderr)
        sys.exit(1)
    return key


def _validate_response(data: dict) -> str:
    if not isinstance(data, dict):
        raise ValueError(f"Response is not a dict: {type(data).__name__}")
    if "choices" not in data:
        raise ValueError(f"Response missing 'choices': {json.dumps(data)[:500]}")
    choices = data["choices"]
    if not choices or not isinstance(choices, list):
        raise ValueError(f"Response 'choices' is empty or not a list")
    choice = choices[0]
    if "message" not in choice:
        raise ValueError(f"Response choice missing 'message': {json.dumps(choice)[:500]}")
    return choice["message"]["content"]


def call(base_url: str, model: str, task_file: str) -> str:
    timeout = int(os.environ.get("ONESHOT_API_TIMEOUT", _DEFAULT_TIMEOUT))
    api_key = _get_api_key()

    with open(task_file) as f:
        prompt = f.read().strip()

    base = base_url.rstrip("/")
    if not base.startswith(("http://", "https://")):
        print(f"ERROR: Invalid base_url: must start with http(s)://", file=sys.stderr)
        sys.exit(1)

    url = f"{base}/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 4096,
    }).encode()

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {api_key}")

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = _mask_secrets(e.read().decode() if e.fp else "")
        print(f"ERROR: API returned {e.code}: {_mask_secrets(body)}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Connection failed: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except TimeoutError:
        print(f"ERROR: Request timed out after {timeout}s", file=sys.stderr)
        sys.exit(1)

    try:
        return _validate_response(data)
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <base_url> <model> <task_file>", file=sys.stderr)
        sys.exit(1)
    result = call(sys.argv[1], sys.argv[2], sys.argv[3])
    print(result)
