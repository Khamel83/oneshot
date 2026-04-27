"""oneshot doctor — check machine readiness and autofix issues."""

from __future__ import annotations

import json
import os
import platform
import re
import socket
import subprocess
from pathlib import Path

import click
import yaml

from oneshot_cli.config import load_config

MACHINES_CONFIG = (
    Path(__file__).resolve().parents[1] / ".oneshot" / "config" / "machines.yaml"
)

# ── Status constants ──

OK = "OK"
MISSING = "MISSING"
AUTH_REQUIRED = "AUTH_REQUIRED"
BLOCKED = "BLOCKED_BY_PASSPHRASE"
ERROR = "UNKNOWN_ERROR"

# ── Env var expansion for YAML ──

_ENV_RE = re.compile(r"\$\{([^}:]+)(?::-([^}]*))?\}")


def _expand_env(value: str) -> str:
    """Expand ${VAR:-default} syntax in string values."""

    def _replace(m):
        var = m.group(1)
        default = m.group(2) or ""
        return os.environ.get(var, default)

    return _ENV_RE.sub(_replace, value)


def _expand_recursive(obj):
    """Walk a loaded YAML structure and expand env vars in all strings."""
    if isinstance(obj, str):
        return _expand_env(obj)
    if isinstance(obj, dict):
        return {k: _expand_recursive(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_expand_recursive(i) for i in obj]
    return obj


def load_machines(path: Path | None = None) -> dict:
    p = path or MACHINES_CONFIG
    if not p.exists():
        return {"machines": {}}
    with open(p) as f:
        raw = yaml.safe_load(f)
    return _expand_recursive(raw) if raw else {"machines": {}}


# ── Check functions ──
# Each returns (status, detail_string).


def _run(cmd: str, timeout: int = 10) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _has_binary(name: str) -> bool:
    return _run(f"command -v {name}", timeout=5).returncode == 0


def check_python3() -> tuple[str, str]:
    r = _run("python3 --version")
    if r.returncode != 0:
        return MISSING, ""
    ver = r.stderr.strip() or r.stdout.strip()
    return OK, ver


def check_git() -> tuple[str, str]:
    r = _run("git --version")
    if r.returncode != 0:
        return MISSING, ""
    return OK, r.stdout.strip()


def check_claude() -> tuple[str, str]:
    if not _has_binary("claude"):
        return MISSING, ""
    r = _run("claude --version")
    ver = r.stdout.strip() or r.stderr.strip()
    return OK, ver


def check_opencode() -> tuple[str, str]:
    if not _has_binary("opencode"):
        return MISSING, ""
    r = _run("opencode --version")
    ver = r.stdout.strip() or r.stderr.strip()
    return OK, ver.split("\n")[0]


def check_oc_launcher() -> tuple[str, str]:
    if not _has_binary("oc"):
        return MISSING, ""
    r = _run("command -v oc")
    launcher = r.stdout.strip() or "oc"
    return OK, launcher


def check_opencode_auth() -> tuple[str, str]:
    if not _has_binary("opencode"):
        return MISSING, ""
    r = _run("opencode auth list", timeout=15)
    if r.returncode != 0:
        return AUTH_REQUIRED, ""
    lines = [l.strip() for l in r.stdout.strip().splitlines() if l.strip()]
    providers = []
    for line in lines:
        if "oauth" in line.lower() or "api" in line.lower() or "plan" in line.lower():
            providers.append(line)
    if not providers:
        return AUTH_REQUIRED, "no providers found"
    return OK, ", ".join(providers[:3])


def check_gemini() -> tuple[str, str]:
    if not _has_binary("gemini"):
        return MISSING, ""
    r = _run("gemini --version")
    ver = r.stdout.strip() or r.stderr.strip()
    return OK, ver.split("\n")[0]


def check_gemini_auth() -> tuple[str, str]:
    if not _has_binary("gemini"):
        return MISSING, ""
    try:
        r = _run("gemini -p 'Say READY and nothing else.'", timeout=45)
    except subprocess.TimeoutExpired:
        return AUTH_REQUIRED, "timeout"
    combined = r.stdout + r.stderr
    if r.returncode != 0 or "READY" not in combined:
        return AUTH_REQUIRED, "auth or model error"
    return OK, "Gemini Code Assist"


def check_codex() -> tuple[str, str]:
    if not _has_binary("codex"):
        return MISSING, ""
    r = _run("codex --version")
    ver = r.stdout.strip() or r.stderr.strip()
    return OK, ver.split("\n")[0]


def check_codex_auth() -> tuple[str, str]:
    if not _has_binary("codex"):
        return MISSING, ""
    auth_path = Path.home() / ".codex" / "auth.json"
    if not auth_path.exists() or auth_path.stat().st_size == 0:
        return AUTH_REQUIRED, "~/.codex/auth.json missing"
    try:
        data = json.loads(auth_path.read_text())
        # refresh_token can be at top level or nested under tokens
        has_token = "refresh_token" in data or "refresh_token" in data.get("tokens", {})
        if not has_token:
            return AUTH_REQUIRED, "auth.json missing refresh_token"
    except (json.JSONDecodeError, OSError):
        return AUTH_REQUIRED, "auth.json invalid"
    return OK, "ChatGPT Plus OAuth"


def check_secrets_cli() -> tuple[str, str]:
    if not _has_binary("secrets"):
        return MISSING, ""
    return OK, str(Path.home() / ".local" / "bin" / "secrets")


def check_secrets_decrypt() -> tuple[str, str]:
    if not _has_binary("secrets"):
        return MISSING, ""
    r = _run("secrets list", timeout=15)
    if r.returncode != 0:
        stderr = r.stderr.strip().lower()
        if "passphrase" in stderr or "decrypt" in stderr or "age" in stderr:
            return BLOCKED, "age key or passphrase issue"
        if "sops" in stderr or "cannot" in stderr:
            return BLOCKED, "sops/age decrypt failed"
        return ERROR, r.stderr.strip()[:60]
    lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
    if not lines:
        return MISSING, "no vault files"
    return OK, f"{len(lines)} vault files"


def check_age_key() -> tuple[str, str]:
    key_path = Path.home() / ".age" / "key.txt"
    if not key_path.exists() or key_path.stat().st_size == 0:
        return MISSING, ""
    return OK, str(key_path)


def check_worktree_path() -> tuple[str, str]:
    wt_parent = Path.cwd().parent / "oneshot-worktrees"
    if not wt_parent.exists():
        return MISSING, str(wt_parent)
    if not os.access(wt_parent, os.W_OK):
        return ERROR, f"{wt_parent} not writable"
    return OK, str(wt_parent)


def check_repo_path() -> tuple[str, str]:
    tasks_dir = Path.cwd() / ".oneshot" / "tasks"
    if not tasks_dir.exists():
        return MISSING, str(tasks_dir)
    return OK, str(tasks_dir)


def check_ssh_config(machine_hosts: list[str]) -> tuple[str, str]:
    ssh_config = Path.home() / ".ssh" / "config"
    if not ssh_config.exists():
        return ERROR, "~/.ssh/config missing"
    try:
        config_text = ssh_config.read_text()
    except OSError:
        return ERROR, "cannot read ~/.ssh/config"
    found = []
    for host in machine_hosts:
        if re.search(
            rf"^Host\s+{re.escape(host)}\s*$", config_text, re.MULTILINE | re.IGNORECASE
        ):
            found.append(host)
    if not found:
        return MISSING, ""
    return OK, ", ".join(found)


# ── Check registry ──

LOCAL_CHECKS = [
    ("python3", check_python3),
    ("git", check_git),
    ("claude", check_claude),
    ("opencode", check_opencode),
    ("oc launcher", check_oc_launcher),
    ("opencode auth", check_opencode_auth),
    ("gemini", check_gemini),
    ("gemini auth", check_gemini_auth),
    ("codex", check_codex),
    ("codex auth", check_codex_auth),
    ("secrets cli", check_secrets_cli),
    ("secrets decrypt", check_secrets_decrypt),
    ("age key", check_age_key),
    ("worktree path", check_worktree_path),
    ("repo path", check_repo_path),
]


def run_local_checks(machine_hosts: list[str]) -> list[dict]:
    results = []
    for name, fn in LOCAL_CHECKS:
        try:
            status, detail = fn()
        except Exception as e:
            status, detail = ERROR, str(e)[:60]
        results.append({"name": name, "status": status, "detail": detail})
    # SSH config check uses all machine hosts
    try:
        status, detail = check_ssh_config(machine_hosts)
    except Exception as e:
        status, detail = ERROR, str(e)[:60]
    results.append({"name": "ssh config", "status": status, "detail": detail})
    return results


# ── Output formatting ──

CHECK_WIDTH = 22


def format_results(machine_name: str, is_local: bool, results: list[dict]) -> str:
    lines = []
    label = f"{machine_name} (this machine)" if is_local else machine_name
    lines.append(f"Machine: {label}")
    lines.append("")
    for r in results:
        name = r["name"]
        status = r["status"]
        detail = r.get("detail", "")
        pad = " " * max(0, CHECK_WIDTH - len(name))
        if status == OK:
            lines.append(f"  {name}{pad}{status:>3}  {detail}")
        else:
            lines.append(f"  {name}{pad}{status}  {detail}")
    return "\n".join(lines)


def summarize(results: list[dict]) -> tuple[int, str]:
    counts = {MISSING: 0, AUTH_REQUIRED: 0, BLOCKED: 0, ERROR: 0}
    for r in results:
        if r["status"] != OK:
            counts[r["status"]] = counts.get(r["status"], 0) + 1
    parts = []
    if counts[MISSING]:
        parts.append(f"{counts[MISSING]} MISSING")
    if counts[AUTH_REQUIRED]:
        parts.append(f"{counts[AUTH_REQUIRED]} AUTH_REQUIRED")
    if counts[BLOCKED]:
        parts.append(f"{counts[BLOCKED]} BLOCKED")
    if counts[ERROR]:
        parts.append(f"{counts[ERROR]} ERROR")
    summary = ", ".join(parts) if parts else "all OK"
    exit_code = 0
    if counts.get(BLOCKED, 0) or counts.get(AUTH_REQUIRED, 0):
        exit_code = 2
    elif counts.get(MISSING, 0) or counts.get(ERROR, 0):
        exit_code = 1
    return exit_code, summary


# ── Autofix ──


def autofix(results: list[dict]) -> list[str]:
    fixes = []
    is_linux = platform.system() == "Linux"
    is_mac = platform.system() == "Darwin"

    for r in results:
        name, status = r["name"], r["status"]
        if status == OK:
            continue

        if name == "python3" and status == MISSING:
            cmd = "sudo apt install -y python3" if is_linux else "brew install python3"
            fixes.append(f"  Installing python3: {cmd}")
            _run(cmd, timeout=120)

        elif name == "git" and status == MISSING:
            cmd = "sudo apt install -y git" if is_linux else "brew install git"
            fixes.append(f"  Installing git: {cmd}")
            _run(cmd, timeout=120)

        elif name == "claude" and status == MISSING:
            fixes.append(
                "  Installing claude: npm install -g @anthropic-ai/claude-code@latest"
            )
            _run("npm install -g @anthropic-ai/claude-code@latest", timeout=120)

        elif name == "opencode" and status == MISSING:
            oneshot_repo = Path.home() / "github" / "oneshot"
            install_sh = oneshot_repo / "install.sh"
            if install_sh.exists():
                fixes.append(f"  Running {install_sh}")
                _run(f"bash {install_sh}", timeout=120)
            else:
                fixes.append(f"  Cannot find {install_sh} — install opencode manually")

        elif name == "gemini" and status == MISSING:
            fixes.append(
                "  Installing gemini: npm install -g @google/gemini-cli@latest"
            )
            _run("npm install -g @google/gemini-cli@latest", timeout=120)

        elif name == "oc launcher" and status == MISSING:
            local_bin = Path.home() / ".local" / "bin"
            local_bin.mkdir(parents=True, exist_ok=True)
            src = Path.home() / "github" / "oneshot" / "scripts" / "oc"
            if src.exists():
                fixes.append(f"  Symlinking oc launcher: {src} -> {local_bin / 'oc'}")
                _run(f"ln -sf {src} {local_bin / 'oc'}")
            else:
                fixes.append(f"  Cannot find {src}")

        elif name == "codex" and status == MISSING:
            fixes.append("  Installing codex: npm install -g @openai/codex@latest")
            _run("npm install -g @openai/codex@latest", timeout=120)

        elif name == "codex auth" and status == AUTH_REQUIRED:
            fixes.append("  codex auth: run `codex login --device-auth` (interactive)")

        elif name == "gemini auth" and status == AUTH_REQUIRED:
            fixes.append("  gemini auth: run `gemini` to authenticate (interactive)")

        elif name == "opencode auth" and status == AUTH_REQUIRED:
            fixes.append(
                "  opencode auth: run `opencode auth login` for each provider (interactive)"
            )

        elif name == "secrets cli" and status == MISSING:
            local_bin = Path.home() / ".local" / "bin"
            local_bin.mkdir(parents=True, exist_ok=True)
            src = Path.home() / "github" / "oneshot" / "scripts" / "secrets"
            if src.exists():
                fixes.append(f"  Symlinking secrets: {src} -> {local_bin / 'secrets'}")
                _run(f"ln -sf {src} {local_bin / 'secrets'}")
            else:
                fixes.append(f"  Cannot find {src}")

        elif name == "secrets decrypt" and status == BLOCKED:
            fixes.append(
                "  secrets decrypt: check ~/.age/key.txt is correct age private key"
            )

        elif name == "age key" and status == MISSING:
            fixes.append(
                "  age key: copy age private key to ~/.age/key.txt (chmod 600)"
            )

        elif name == "worktree path" and status == MISSING:
            wt = Path.cwd().parent / "oneshot-worktrees"
            fixes.append(f"  Creating {wt}")
            wt.mkdir(parents=True, exist_ok=True)

        elif name == "repo path" and status == MISSING:
            tasks = Path.cwd() / ".oneshot" / "tasks"
            fixes.append(f"  Creating {tasks}")
            tasks.mkdir(parents=True, exist_ok=True)

    return fixes


# ── Remote checks via SSH ──

REMOTE_SCRIPT = r"""
export PATH="$PATH:/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$HOME/.nvm/versions/node/*/bin"
if [ -s "$HOME/.nvm/nvm.sh" ]; then
  export NVM_DIR="$HOME/.nvm"
  . "$NVM_DIR/nvm.sh"
fi

emit() {
  printf "%s=%s\n" "$1" "$2"
}

# python3
if command -v python3 >/dev/null 2>&1; then
  emit python3 "OK $(python3 --version 2>&1 | cut -d' ' -f2)"
else
  emit python3 MISSING
fi

# git
if command -v git >/dev/null 2>&1; then
  emit git "OK $(git --version 2>/dev/null | cut -d' ' -f3)"
else
  emit git MISSING
fi

# claude
if command -v claude >/dev/null 2>&1; then
  VER=$(claude --version 2>/dev/null | head -1)
  emit claude "OK ${VER}"
else
  emit claude MISSING
fi

# opencode
if command -v opencode >/dev/null 2>&1; then
  VER=$(opencode --version 2>/dev/null | head -1)
  emit opencode "OK ${VER}"
else
  emit opencode MISSING
fi

# oc launcher
if command -v oc >/dev/null 2>&1; then
  emit oc_launcher "OK $(command -v oc)"
else
  emit oc_launcher MISSING
fi

# opencode auth
if command -v opencode >/dev/null 2>&1; then
  AUTH=$(opencode auth list 2>/dev/null | grep -iE 'oauth|api|plan' | head -3 | tr '\n' ',' | sed 's/,$//')
  if [ -n "$AUTH" ]; then
    emit opencode_auth "OK ${AUTH}"
  else
    emit opencode_auth AUTH_REQUIRED
  fi
else
  emit opencode_auth MISSING
fi

# gemini
if command -v gemini >/dev/null 2>&1; then
  VER=$(gemini --version 2>/dev/null | head -1)
  emit gemini "OK ${VER}"
else
  emit gemini MISSING
fi

# gemini auth
if command -v gemini >/dev/null 2>&1; then
  RESP=$(python3 - <<'PY'
import subprocess
import sys

try:
    result = subprocess.run(
        ["gemini", "-p", "Say READY and nothing else."],
        capture_output=True,
        text=True,
        timeout=15,
    )
except subprocess.TimeoutExpired:
    sys.exit(124)
except Exception:
    sys.exit(1)

sys.stdout.write((result.stdout or "") + (result.stderr or ""))
sys.exit(result.returncode)
PY
)
  RC=$?
  if [ "$RC" -eq 0 ] && echo "$RESP" | grep -q READY; then
    emit gemini_auth "OK Gemini Code Assist"
  else
    emit gemini_auth AUTH_REQUIRED
  fi
else
  emit gemini_auth MISSING
fi

# codex
if command -v codex >/dev/null 2>&1; then
  VER=$(codex --version 2>/dev/null | head -1)
  emit codex "OK ${VER}"
else
  emit codex MISSING
fi

# codex auth
if command -v codex >/dev/null 2>&1; then
  if [ -s "$HOME/.codex/auth.json" ]; then
    if python3 -c "import json; d=json.load(open('$HOME/.codex/auth.json')); assert 'refresh_token' in d" 2>/dev/null; then
      emit codex_auth "OK ChatGPT Plus OAuth"
    else
      emit codex_auth AUTH_REQUIRED
    fi
  else
    emit codex_auth AUTH_REQUIRED
  fi
else
  emit codex_auth MISSING
fi

# secrets cli
if command -v secrets >/dev/null 2>&1; then
  emit secrets_cli "OK $(which secrets)"
else
  emit secrets_cli MISSING
fi

# secrets decrypt
if command -v secrets >/dev/null 2>&1; then
  OUT=$(secrets list 2>&1)
  RC=$?
  if [ $RC -eq 0 ] && [ -n "$OUT" ]; then
    COUNT=$(echo "$OUT" | grep -c '[^[:space:]]')
    emit secrets_decrypt "OK ${COUNT} vault files"
  else
    if echo "$OUT" | grep -qiE 'passphrase|decrypt|age'; then
      emit secrets_decrypt BLOCKED_BY_PASSPHRASE
    else
      emit secrets_decrypt UNKNOWN_ERROR
    fi
  fi
else
  emit secrets_decrypt MISSING
fi

# age key
if [ -s "$HOME/.age/key.txt" ]; then
  emit age_key "OK $HOME/.age/key.txt"
else
  emit age_key MISSING
fi

# ssh config
FOUND=""
for h in {hosts}; do
  if grep -qiE "^Host[[:space:]]+${h}[[:space:]]*$" "$HOME/.ssh/config" 2>/dev/null; then
    FOUND="${FOUND:+$FOUND, }$h"
  fi
done
if [ -n "$FOUND" ]; then
  emit ssh_config "OK $FOUND"
else
  emit ssh_config MISSING
fi
"""


def run_remote_checks(host: str, all_hosts: list[str]) -> list[dict]:
    """Run checks on a remote machine via SSH. Returns parsed results."""
    hosts_str = " ".join(all_hosts)
    script = REMOTE_SCRIPT.replace("{hosts}", hosts_str)

    try:
        r = subprocess.run(
            f"ssh -o ConnectTimeout=5 -o BatchMode=yes {host} 'bash -s'",
            shell=True,
            input=script,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return [{"name": "ssh", "status": ERROR, "detail": "connection timeout"}]
    except Exception as e:
        return [{"name": "ssh", "status": ERROR, "detail": str(e)[:60]}]

    if r.returncode != 0 and not r.stdout.strip():
        return [
            {
                "name": "ssh",
                "status": ERROR,
                "detail": (r.stderr or "ssh failed").strip()[:60],
            }
        ]

    results = []
    for line in r.stdout.strip().splitlines():
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if value in (MISSING, AUTH_REQUIRED, BLOCKED, ERROR):
            results.append({"name": key, "status": value, "detail": ""})
        elif value.startswith("OK "):
            detail = value[3:]
            results.append({"name": key, "status": OK, "detail": detail})
        else:
            results.append(
                {
                    "name": key,
                    "status": value.split()[0],
                    "detail": " ".join(value.split()[1:]),
                }
            )

    # Normalize key names (remote uses underscores for auth keys)
    for r in results:
        r["name"] = r["name"].replace("_", " ")

    return results


def remote_fix_instructions(host: str, results: list[dict]) -> list[str]:
    issues = [r for r in results if r["status"] != OK]
    if not issues:
        return []

    names = ", ".join(r["name"] for r in issues)
    return [
        f"  Remote autofix not supported for {host} in this command.",
        f"  Failing checks: {names}",
        f"  Run `./bin/oneshot doctor --fix` directly on {host} after SSHing there.",
    ]


def detect_local_machine(machines: dict) -> str | None:
    """Detect which machine config matches the current host."""
    hostname = socket.gethostname()
    # Try SSH self-test: if we can't SSH to a host, it might be us
    ssh_config = Path.home() / ".ssh" / "config"
    ssh_text = ssh_config.read_text() if ssh_config.exists() else ""

    for key, cfg in machines.items():
        if not cfg.get("enabled", True):
            continue
        host_alias = cfg.get("host", "")
        # Direct hostname match
        if hostname == key or hostname == host_alias or key in hostname:
            return key
        # Extract HostName from SSH config and compare to Tailscale IP
        pattern = (
            rf"^Host\s+{re.escape(host_alias)}\s*$\n((?:^  .*\n)*)^  HostName\s+(.+)$"
        )
        m = re.search(pattern, ssh_text, re.MULTILINE)
        if m:
            target_ip = m.group(2).strip()
            # Check if this IP matches any local interface
            try:
                local_ips = socket.getaddrinfo(hostname, None)
                if any(ip[4][0] == target_ip for ip in local_ips):
                    return key
            except socket.gaierror:
                pass
        # Fallback: try a quick SSH connection — if it fails with permission denied,
        # it's likely this machine
        try:
            r = subprocess.run(
                f"ssh -o ConnectTimeout=2 -o BatchMode=yes {host_alias} 'echo ok'",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if r.returncode != 0 and (
                "Permission denied" in r.stderr or "denied" in r.stderr.lower()
            ):
                return key
        except (subprocess.TimeoutExpired, Exception):
            pass
    return None


# ── Click command ──


@click.command()
@click.option(
    "--all-machines", "all_machines", is_flag=True, help="Check all machines via SSH."
)
@click.option("--fix", is_flag=True, help="Auto-fix issues where possible.")
def cli(all_machines: bool, fix: bool):
    """Check machine readiness for oneshot delegation harness."""
    machines_data = load_machines()
    machines = machines_data.get("machines", {})
    all_hosts = [cfg["host"] for cfg in machines.values() if cfg.get("enabled", True)]

    overall_exit = 0
    output_parts = []

    if all_machines:
        local_key = detect_local_machine(machines)
        for key, cfg in machines.items():
            if not cfg.get("enabled", True):
                continue
            host = cfg["host"]
            is_local = key == local_key

            if is_local:
                results = run_local_checks(all_hosts)
            else:
                results = run_remote_checks(host, all_hosts)

            output_parts.append(format_results(key, is_local, results))
            exit_code, summary = summarize(results)
            output_parts.append(f"\nResult: {summary}")
            output_parts.append("")
            overall_exit = max(overall_exit, exit_code)

            if fix and not is_local:
                fixes = remote_fix_instructions(key, results)
                if fixes:
                    output_parts.append(f"  Fix guidance for {key}...")
                    for f in fixes:
                        output_parts.append(f)
    else:
        results = run_local_checks(all_hosts)
        output_parts.append(format_results("local", True, results))
        exit_code, summary = summarize(results)
        output_parts.append(f"\nResult: {summary}")
        overall_exit = exit_code

        if fix:
            output_parts.append("")
            fixes = autofix(results)
            if fixes:
                output_parts.append("Applying fixes:")
                for f in fixes:
                    click.echo(f, err=True)
                # Re-run checks after fix
                output_parts.append("")
                results2 = run_local_checks(all_hosts)
                output_parts.append(format_results("local", True, results2))
                exit_code2, summary2 = summarize(results2)
                output_parts.append(f"\nResult after fix: {summary2}")
                overall_exit = exit_code2
            else:
                output_parts.append("Nothing to fix.")

    click.echo("\n".join(output_parts))
    raise SystemExit(overall_exit)
