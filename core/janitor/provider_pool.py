"""Multi-provider pool for janitor LLM calls.

Tries providers in priority order. Skips a provider if:
  - API key is missing
  - Daily or minute rate limit is reached
  - Provider costs money and budget.daily_limit_usd is 0

Usage:
    from core.janitor.provider_pool import ProviderPool
    pool = ProviderPool()
    text = pool.call("Summarize this: ...")

Config read from config/janitor_providers.yaml (relative to git root).
Falls back to openrouter/free behaviour if config file is missing.
"""

import fcntl
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def _find_git_root(start: Optional[str] = None) -> Path:
    p = Path(start or os.getcwd())
    for candidate in [p] + list(p.parents):
        if (candidate / ".git").exists():
            return candidate
    return p


def _strip_comment(s: str) -> str:
    in_quote = False
    for i, ch in enumerate(s):
        if ch in ('"', "'"):
            in_quote = not in_quote
        if ch == "#" and not in_quote:
            return s[:i].rstrip()
    return s


def _scalar(s: str):
    s = s.strip()
    if s in ("null", "~", ""):
        return None
    if s in ("true", "True", "yes"):
        return True
    if s in ("false", "False", "no"):
        return False
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip())


def _load_config() -> dict:
    """Load janitor_providers.yaml using a fixed-indent parser.

    The file has a known 2-level structure:
      providers:          <- section (indent 0)
        name:             <- provider name (indent 2)
          key: value      <- provider field (indent 4)
      budget:             <- section (indent 0)
        key: value        <- budget field (indent 2)

    Falls back to openrouter/free only if file is missing.
    """
    # Central config wins over per-project config
    central = Path.home() / ".config" / "oneshot" / "janitor_providers.yaml"
    root = _find_git_root()
    cfg_path = central if central.exists() else (root / "config" / "janitor_providers.yaml")
    if not cfg_path.exists():
        return {
            "providers": {
                "openrouter_free": {
                    "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                    "model": "openrouter/free",
                    "cost_per_1k_tokens": 0.0,
                    "daily_limit": 1000,
                    "minute_limit": 20,
                    "env_key": "OPENROUTER_API_KEY",
                    "priority": 1,
                }
            },
            "budget": {"daily_limit_usd": 0.0, "monthly_limit_usd": 0.0, "alert_at_pct": 80},
        }

    result: dict = {"providers": {}, "budget": {}}
    current_section: Optional[str] = None
    current_provider: Optional[str] = None

    for raw_line in cfg_path.read_text().splitlines():
        line = _strip_comment(raw_line)
        if not line.strip():
            continue
        ind = _indent(line)
        content = line.strip()

        if ind == 0:
            # Top-level section key (e.g. "providers:" or "budget:")
            if content.endswith(":"):
                current_section = content[:-1]
                current_provider = None
            continue

        if current_section == "providers":
            if ind == 2 and content.endswith(":") and ":" not in content[:-1]:
                # Provider name (e.g. "openrouter_free:")
                current_provider = content[:-1]
                result["providers"][current_provider] = {}
            elif ind == 4 and current_provider and ":" in content:
                # Provider field (e.g. "endpoint: https://...")
                key, _, val = content.partition(":")
                result["providers"][current_provider][key.strip()] = _scalar(val.strip())

        elif current_section == "budget":
            if ind == 2 and ":" in content and not content.startswith("- "):
                # Budget field (e.g. "daily_limit_usd: 0.0")
                key, _, val = content.partition(":")
                result["budget"][key.strip()] = _scalar(val.strip())
            # paid_providers list items (indent 4) are skipped — they're for humans to read

    return result


# ---------------------------------------------------------------------------
# Usage + budget tracking
# ---------------------------------------------------------------------------

def _janitor_dir(root: Optional[Path] = None) -> Path:
    r = root or _find_git_root()
    d = r / ".janitor"
    d.mkdir(exist_ok=True)
    return d


class UsageTracker:
    """Tracks per-provider API calls using .janitor/usage.jsonl."""

    def __init__(self, root: Optional[Path] = None):
        self._path = _janitor_dir(root) / "usage.jsonl"
        self._cache: dict = {}
        self._cache_ts: float = 0
        self._TTL = 5.0  # seconds

    def _load(self) -> list:
        if not self._path.exists():
            return []
        entries = []
        with open(self._path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return entries

    def _counts(self, provider_name: str) -> tuple[int, int]:
        """Return (calls_this_minute, calls_today) for provider_name."""
        now = time.time()
        if now - self._cache_ts < self._TTL and provider_name in self._cache:
            return self._cache[provider_name]

        entries = self._load()
        minute_ago = now - 60
        day_ago = now - 86400
        minute_count = day_count = 0
        for e in entries:
            ts = e.get("ts", 0)
            if e.get("provider", "openrouter_free") != provider_name:
                continue
            if ts > minute_ago:
                minute_count += 1
            if ts > day_ago:
                day_count += 1

        self._cache[provider_name] = (minute_count, day_count)
        self._cache_ts = now
        return minute_count, day_count

    def within_limits(self, name: str, daily_limit: Optional[int], minute_limit: Optional[int]) -> bool:
        minute_count, day_count = self._counts(name)
        if daily_limit is not None and day_count >= daily_limit:
            return False
        if minute_limit is not None and minute_count >= minute_limit:
            return False
        return True

    def log(self, provider_name: str, model: str, tokens_in: int = 0, tokens_out: int = 0, cost_usd: float = 0.0):
        entry = {
            "ts": time.time(),
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "provider": provider_name,
            "model": model,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "cost_usd": cost_usd,
        }
        line = json.dumps(entry, separators=(",", ":")) + "\n"
        # Use an exclusive lock so concurrent cron + session-end writes stay safe.
        # flock is advisory but sufficient for single-machine, single-user use.
        try:
            with open(self._path, "a") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    f.write(line)
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
        except OSError:
            pass
        # Invalidate cache
        self._cache_ts = 0

    def mark_rate_limited(self, provider_name: str):
        self.log(provider_name, "rate_limited")

    def get_stats(self) -> dict:
        """Summary of today's usage per provider."""
        entries = self._load()
        now = time.time()
        day_ago = now - 86400
        by_provider: dict[str, dict] = {}
        for e in entries:
            if e.get("ts", 0) < day_ago:
                continue
            prov = e.get("provider", "openrouter_free")
            if prov not in by_provider:
                by_provider[prov] = {"calls": 0, "tokens_in": 0, "tokens_out": 0, "cost_usd": 0.0}
            by_provider[prov]["calls"] += 1
            by_provider[prov]["tokens_in"] += e.get("tokens_in", 0)
            by_provider[prov]["tokens_out"] += e.get("tokens_out", 0)
            by_provider[prov]["cost_usd"] += e.get("cost_usd", 0.0)
        return by_provider


class BudgetTracker:
    """Tracks spend against daily/monthly budget caps."""

    def __init__(self, daily_limit: float, monthly_limit: float, alert_pct: int, root: Optional[Path] = None):
        self.daily_limit = daily_limit
        self.monthly_limit = monthly_limit
        self.alert_pct = alert_pct
        self._path = _janitor_dir(root) / "budget.json"

    def _load(self) -> dict:
        if not self._path.exists():
            return {"date": str(date.today()), "spent_today": 0.0, "spent_month": 0.0, "calls": 0, "by_provider": {}}
        try:
            data = json.loads(self._path.read_text())
            if data.get("date") != str(date.today()):
                data["date"] = str(date.today())
                data["spent_today"] = 0.0
                data["calls"] = 0
                data["by_provider"] = {}
        except (json.JSONDecodeError, OSError):
            data = {"date": str(date.today()), "spent_today": 0.0, "spent_month": 0.0, "calls": 0, "by_provider": {}}
        return data

    def can_afford(self, cost_per_call: float) -> bool:
        if cost_per_call <= 0.0:
            return True
        if self.daily_limit <= 0.0:
            return False  # $0 budget — no paid calls
        data = self._load()
        return data["spent_today"] + cost_per_call <= self.daily_limit

    def charge(self, provider_name: str, cost_usd: float):
        if cost_usd <= 0.0:
            return
        data = self._load()
        data["spent_today"] = data.get("spent_today", 0.0) + cost_usd
        data["spent_month"] = data.get("spent_month", 0.0) + cost_usd
        data["calls"] = data.get("calls", 0) + 1
        by_prov = data.setdefault("by_provider", {})
        by_prov[provider_name] = by_prov.get(provider_name, 0) + 1
        data["limit_usd"] = self.daily_limit
        if self.daily_limit > 0:
            pct = (data["spent_today"] / self.daily_limit) * 100
            if pct >= self.alert_pct:
                print(f"[janitor] Budget alert: {pct:.0f}% of daily ${self.daily_limit:.2f} spent")
        try:
            self._path.write_text(json.dumps(data, indent=2))
        except OSError:
            pass


# ---------------------------------------------------------------------------
# Individual provider callers
# ---------------------------------------------------------------------------

class _CallResult:
    def __init__(self, text: str, model: str, tokens_in: int, tokens_out: int, cost_usd: float):
        self.text = text
        self.model = model
        self.tokens_in = tokens_in
        self.tokens_out = tokens_out
        self.cost_usd = cost_usd


class _RateLimitError(Exception):
    pass


def _http_call(endpoint: str, api_key: str, model: str,
               messages: list, max_tokens: int, timeout: int) -> _CallResult:
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.1,
    }).encode()

    req = urllib.request.Request(
        endpoint + ("chat/completions" if endpoint.endswith("/") else "/chat/completions")
        if not endpoint.endswith("completions") else endpoint,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/Khamel83/oneshot",
            "X-Title": "Janitor",
        },
    )

    last_error = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read())
                content = data["choices"][0]["message"]["content"] or ""
                model_used = data.get("model", model)
                usage = data.get("usage", {})
                tokens_in = usage.get("prompt_tokens", 0)
                tokens_out = usage.get("completion_tokens", 0)
                return _CallResult(content, model_used, tokens_in, tokens_out, 0.0)
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode()[:200]
            except Exception:
                pass
            last_error = f"HTTP {e.code}: {e.reason} — {body}"
            if e.code == 429:
                raise _RateLimitError("Rate limited")
            if e.code >= 500:
                time.sleep(2 ** attempt)
                continue
            break
        except (urllib.error.URLError, TimeoutError, KeyError, IndexError) as e:
            last_error = str(e)
            time.sleep(2 ** attempt)
            continue

    raise RuntimeError(f"HTTP call failed after 3 attempts: {last_error}")


def _codex_call(prompt: str, system: Optional[str], max_tokens: int) -> _CallResult:
    """Dispatch to Codex CLI subprocess. Returns response text."""
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    cmd = [
        "codex", "exec",
        "--sandbox", "danger-full-access",
        full_prompt,
    ]
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)  # force OAuth, not API key
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        output = result.stdout.strip()
        if not output and result.stderr:
            raise RuntimeError(f"codex stderr: {result.stderr[:200]}")
        return _CallResult(output, "codex", 0, 0, 0.0)
    except subprocess.TimeoutExpired:
        raise RuntimeError("Codex CLI timed out after 120s")
    except FileNotFoundError:
        raise RuntimeError("codex CLI not found in PATH")


# ---------------------------------------------------------------------------
# ProviderPool
# ---------------------------------------------------------------------------

@dataclass
class _Provider:
    name: str
    priority: int
    env_key: str
    cost_per_1k_tokens: float
    daily_limit: Optional[int]
    minute_limit: Optional[int]
    harness: Optional[str]       # "codex_cli" or None (HTTP)
    endpoint: Optional[str]
    model: Optional[str]

    def api_key(self) -> Optional[str]:
        return os.environ.get(self.env_key, "")

    def has_key(self) -> bool:
        return bool(self.api_key())

    def is_free(self) -> bool:
        return self.cost_per_1k_tokens <= 0.0


class ProviderPool:
    """Try providers in priority order for janitor LLM calls.

    Args:
        root: git root directory (auto-detected if None)
        verbose: print provider selection info
    """

    def __init__(self, root: Optional[str] = None, verbose: bool = False):
        self._root = Path(root) if root else _find_git_root()
        self._verbose = verbose
        cfg = _load_config()
        self._providers = self._build_providers(cfg.get("providers", {}))
        budget_cfg = cfg.get("budget", {})
        self._budget = BudgetTracker(
            daily_limit=float(budget_cfg.get("daily_limit_usd", 0.0)),
            monthly_limit=float(budget_cfg.get("monthly_limit_usd", 0.0)),
            alert_pct=int(budget_cfg.get("alert_at_pct", 80)),
            root=self._root,
        )
        self._usage = UsageTracker(root=self._root)

    def _build_providers(self, raw: dict) -> list[_Provider]:
        providers = []
        for name, cfg in raw.items():
            if not isinstance(cfg, dict):
                continue
            providers.append(_Provider(
                name=name,
                priority=int(cfg.get("priority", 99)),
                env_key=str(cfg.get("env_key", "")),
                cost_per_1k_tokens=float(cfg.get("cost_per_1k_tokens", 0.0)),
                daily_limit=cfg.get("daily_limit"),  # None = unlimited
                minute_limit=cfg.get("minute_limit"),
                harness=cfg.get("harness"),
                endpoint=cfg.get("endpoint"),
                model=cfg.get("model"),
            ))
        return sorted(providers, key=lambda p: p.priority)

    def call(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        timeout: int = 30,
    ) -> str:
        """Call the highest-priority available provider. Returns response text."""
        tried = []
        for provider in self._providers:
            if not provider.has_key():
                if self._verbose:
                    print(f"[janitor/pool] {provider.name}: skip (no key)")
                continue

            if not self._usage.within_limits(provider.name, provider.daily_limit, provider.minute_limit):
                if self._verbose:
                    print(f"[janitor/pool] {provider.name}: skip (rate limit)")
                continue

            # Cost check — skip paid providers if budget is $0
            if not provider.is_free() and not self._budget.can_afford(0.001):
                if self._verbose:
                    print(f"[janitor/pool] {provider.name}: skip (no budget for paid)")
                continue

            tried.append(provider.name)
            try:
                result = self._dispatch(provider, prompt, system, max_tokens, timeout)
                if self._verbose:
                    print(f"[janitor/pool] {provider.name}: ok via {result.model}")
                self._usage.log(
                    provider.name, result.model,
                    result.tokens_in, result.tokens_out, result.cost_usd,
                )
                if result.cost_usd > 0:
                    self._budget.charge(provider.name, result.cost_usd)
                return result.text
            except _RateLimitError:
                self._usage.mark_rate_limited(provider.name)
                if self._verbose:
                    print(f"[janitor/pool] {provider.name}: rate limited, trying next")
                continue
            except RuntimeError as e:
                if self._verbose:
                    print(f"[janitor/pool] {provider.name}: error: {e}")
                continue

        raise RuntimeError(
            f"All providers exhausted or unavailable. Tried: {tried or 'none (no keys set)'}"
        )

    def _dispatch(self, provider: _Provider, prompt: str, system: Optional[str],
                  max_tokens: int, timeout: int) -> _CallResult:
        if provider.harness == "codex_cli":
            return _codex_call(prompt, system, max_tokens)

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        endpoint = provider.endpoint or ""
        # Normalise endpoint to end with the right path
        if not endpoint.endswith("completions"):
            endpoint = endpoint.rstrip("/") + "/chat/completions"

        return _http_call(endpoint, provider.api_key(), provider.model or "",
                          messages, max_tokens, timeout)

    def status(self) -> dict:
        """Return current provider availability and usage stats."""
        stats = self._usage.get_stats()
        result = {}
        for p in self._providers:
            minute_count, day_count = self._usage._counts(p.name)
            result[p.name] = {
                "has_key": p.has_key(),
                "calls_today": day_count,
                "daily_limit": p.daily_limit,
                "remaining_today": (p.daily_limit - day_count) if p.daily_limit else None,
                "is_free": p.is_free(),
                "priority": p.priority,
            }
        return result


# ---------------------------------------------------------------------------
# Module-level singleton (lazy)
# ---------------------------------------------------------------------------

_pool: Optional[ProviderPool] = None


def get_pool(root: Optional[str] = None, verbose: bool = False) -> ProviderPool:
    """Get or create the module-level ProviderPool singleton."""
    global _pool
    if _pool is None:
        _pool = ProviderPool(root=root, verbose=verbose)
    return _pool


def call_janitor(
    prompt: str,
    system: Optional[str] = None,
    max_tokens: int = 1024,
    timeout: int = 30,
) -> str:
    """Top-level convenience function. Routes through the provider pool."""
    return get_pool().call(prompt, system=system, max_tokens=max_tokens, timeout=timeout)


def extract_structured_janitor(
    prompt: str,
    system: Optional[str] = None,
    schema_hint: Optional[str] = None,
) -> dict:
    """Call provider pool and parse JSON response."""
    if schema_hint:
        prompt += f"\n\nRespond with valid JSON only. No explanation. Expected shape: {schema_hint}"

    try:
        raw = call_janitor(prompt, system=system, max_tokens=2048, timeout=30)
    except RuntimeError as e:
        return {"raw": str(e), "status": "failed"}

    if not raw:
        return {"raw": "", "status": "empty_response"}

    stripped = raw.strip()

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    if stripped.startswith("```"):
        lines = stripped.split("\n")
        inner = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        try:
            return json.loads(inner.strip())
        except json.JSONDecodeError:
            pass

    match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', stripped, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {"raw": stripped, "status": "unstructured"}
