"""Parallel dispatch runner for Codex and Gemini.

Usage:
    python -m core.dispatch.run --class implement_small --prompt "Fix the auth bug in login.py" --output /tmp/dispatch
    python -m core.dispatch.run --class implement_small --prompt "..." --parallel 3
    python -m core.dispatch.run --manifest 1shot/dispatch

Trace writing:
    Every dispatch writes a trace bundle to eval/traces/{date}/{task_class}-{HHMMSS}-{worker}/:
      trace.json     — full structured trace (primary artifact)
      prompt.md      — rendered prompt sent to worker
      output.raw     — raw worker output
      manifest.md    — human-readable summary (derived from trace.json)

New capabilities:
    --localize      Pre-dispatch LLM call to inject relevant file paths into prompt
    --verify CMD    Run verification command after dispatch; rollback if it fails
    --retry N       Multi-turn retry: feed error output back to worker (default: 1)
    --remote HOST   Dispatch to remote host via SSH (must be in config/workers.yaml)
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = REPO_ROOT / "config" / "lanes.yaml"
CLAW_INSTALL_PATH = Path.home() / "github" / "claw-code-agent"


def load_yaml(path: str) -> dict:
    import yaml
    with open(path) as f:
        return yaml.safe_load(f)


def resolve_lane(task_class: str, category: str = None) -> dict:
    """Resolve task class to lane config using the router module."""
    sys.path.insert(0, str(REPO_ROOT))
    from core.router.lane_policy import resolve
    return resolve(task_class, config_path=str(CONFIG_PATH), category=category)


def codex_command(prompt: str, output_file: str) -> list[str]:
    # Codex exec with --json writes JSONL to stdout and last message to -o file
    # Use </dev/null to prevent stdin blocking, capture stdout to the output file
    jsonl_file = output_file.replace(".json", ".jsonl")
    return [
        "bash", "-c",
        f"unset OPENAI_API_KEY OPENAI_BASE_URL && "
        f"codex exec --json --sandbox danger-full-access "
        f"-o {output_file} "
        f"{json.dumps(prompt)} "
        f"</dev/null > {jsonl_file} 2>&1"
    ]


def gemini_command(prompt: str, output_file: str) -> list[str]:
    return [
        "bash", "-c",
        f"gemini -p {json.dumps(prompt)} "
        f"--output-format json --approval-mode yolo "
        f"> {output_file} 2>/dev/null"
    ]


ZAI_MODELS = {"glm-5.1", "glm-5", "glm-5-turbo", "glm-4.7", "glm-4.6", "glm-4.5", "glm-4.5-air"}
ZAI_BASE_URL = "https://api.z.ai/api/coding/paas/v4"          # OpenAI-compatible (claw-code-agent)
ZAI_ANTHROPIC_URL = "https://api.z.ai/api/anthropic"           # Anthropic-compatible (claude CLI)
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def claw_code_command(prompt: str, output_file: str, model: str = "") -> list[str]:
    """Build Claw Code Agent CLI command.

    Routes GLM models to ZAI (free on plan), everything else to OpenRouter.
    """
    install = CLAW_INSTALL_PATH
    cwd = os.getcwd()
    resolved_model = model or os.environ.get("OPENAI_MODEL", "glm-5.1")

    if resolved_model in ZAI_MODELS:
        base_url = ZAI_BASE_URL
        api_key = os.environ.get("ZAI_API_KEY", "")
    else:
        base_url = OPENROUTER_BASE_URL
        api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY", "")

    key_part = f"OPENAI_API_KEY={shlex.quote(api_key)} " if api_key else ""
    return [
        "bash", "-c",
        f"cd {install} && "
        f"{key_part}"
        f"OPENAI_MODEL={shlex.quote(resolved_model)} "
        f"OPENAI_BASE_URL={shlex.quote(base_url)} "
        f"python3 -m src.main agent {json.dumps(prompt)} "
        f"--cwd {cwd} --allow-write --allow-shell "
        f"> {output_file} 2>/dev/null"
    ]


def glm_claude_command(prompt: str, output_file: str, model: str = "glm-5-turbo") -> list[str]:
    """Run claude CLI with ZAI as the Anthropic-compatible backend.

    This gives a full Claude Code session (all native tools: bash, read, edit, glob, grep)
    running on GLM-5-turbo via ZAI — free on the GLM Coding Plan (expires 2026-05-02).
    Equivalent to how codex/gemini are used but with the full claude toolchain.
    """
    zai_key = os.environ.get("ZAI_API_KEY", "")
    if not zai_key:
        # Fall back to vault
        try:
            zai_key = subprocess.run(
                ["bash", "-c", "secrets get ZAI_API_KEY 2>/dev/null"],
                capture_output=True, text=True
            ).stdout.strip()
        except Exception:
            pass
    return [
        "bash", "-c",
        f"ANTHROPIC_AUTH_TOKEN={shlex.quote(zai_key)} "
        f"ANTHROPIC_BASE_URL={shlex.quote(ZAI_ANTHROPIC_URL)} "
        f"ANTHROPIC_DEFAULT_SONNET_MODEL={shlex.quote(model)} "
        f"ANTHROPIC_DEFAULT_OPUS_MODEL={shlex.quote(model)} "
        f"ANTHROPIC_DEFAULT_HAIKU_MODEL=glm-4.5-air "
        f"claude --print --dangerously-skip-permissions "
        f"{json.dumps(prompt)} "
        f"> {output_file} 2>/dev/null"
    ]


def ssh_wrap(host: str, cmd: list[str]) -> list[str]:
    """Wrap a local worker command to run on a remote host via SSH.

    Args:
        host: SSH host alias (must be resolvable, e.g. via ~/.ssh/config or Tailscale).
        cmd: Local command list (e.g. ["bash", "-c", "codex exec ..."]).

    The command is passed as-is to the remote shell. File paths in the inner
    bash -c string must be absolute — the caller is responsible for this when
    targeting remote machines.
    """
    # SSH BatchMode=yes: fail immediately instead of prompting for password.
    # ConnectTimeout=10: don't hang forever on unreachable hosts.
    return [
        "ssh",
        "-o", "BatchMode=yes",
        "-o", "ConnectTimeout=10",
        "-o", "StrictHostKeyChecking=accept-new",
        host,
    ] + cmd


def load_workers_config() -> dict:
    """Load config/workers.yaml. Returns empty dict on any error."""
    try:
        return load_yaml(str(REPO_ROOT / "config" / "workers.yaml"))
    except Exception:
        return {}


def worker_ssh_host(worker_name: str) -> str | None:
    """Return the SSH host for a named worker entry, or None if not SSH transport."""
    cfg = load_workers_config()
    entry = cfg.get("workers", {}).get(worker_name, {})
    if entry.get("transport") == "ssh":
        return entry.get("host")
    return None


def worker_available(worker: str) -> bool:
    """Check if a worker is available on this machine.

    For ZAI-backed workers (glm_claude, claw_code), also checks plan_expires
    from workers.yaml. Returns False if the ZAI plan has expired.
    """
    if worker == "codex":
        return subprocess.run(
            ["bash", "-c", "command -v codex"],
            capture_output=True
        ).returncode == 0
    elif worker == "gemini_cli":
        return subprocess.run(
            ["bash", "-c", "command -v gemini"],
            capture_output=True
        ).returncode == 0
    elif worker == "claw_code":
        has_install = (CLAW_INSTALL_PATH / "src" / "main.py").exists()
        has_key = bool(
            os.environ.get("ZAI_API_KEY")
            or os.environ.get("OPENROUTER_API_KEY")
            or os.environ.get("OPENAI_API_KEY")
            or subprocess.run(
                ["bash", "-c", "secrets get ZAI_API_KEY 2>/dev/null"],
                capture_output=True
            ).stdout.strip()
            or subprocess.run(
                ["bash", "-c", "secrets get OPENROUTER_API_KEY 2>/dev/null"],
                capture_output=True
            ).stdout.strip()
        )
        return has_install and has_key
    elif worker == "glm_claude":
        has_claude = subprocess.run(
            ["bash", "-c", "command -v claude"], capture_output=True
        ).returncode == 0
        # Check env first, then fall back to vault (secrets CLI)
        has_key = bool(
            os.environ.get("ZAI_API_KEY")
            or subprocess.run(
                ["bash", "-c", "secrets get ZAI_API_KEY 2>/dev/null"],
                capture_output=True
            ).stdout.strip()
        )
        if not has_claude or not has_key:
            return False
        # Check ZAI plan expiry from workers.yaml
        if not _zai_plan_active():
            return False
        return True
    return True


def _zai_plan_active() -> bool:
    """Check if the ZAI GLM Coding Plan is still active.

    Reads plan_expires from config/workers.yaml (glm worker entry).
    Returns True if the plan has not expired or if the field is missing.
    """
    try:
        workers_config = load_yaml(str(REPO_ROOT / "config" / "workers.yaml"))
        plan_expires = workers_config.get("workers", {}).get("glm", {}).get("plan_expires")
        if not plan_expires:
            return True  # no expiry configured, assume active
        from datetime import date
        expiry = date.fromisoformat(plan_expires)
        return date.today() <= expiry
    except Exception:
        return True  # on any parse error, don't block


def clean_env() -> dict[str, str]:
    """Return a clean environment for worker subprocesses."""
    env = os.environ.copy()
    for key in ["OPENAI_API_KEY", "OPENAI_BASE_URL"]:
        env.pop(key, None)
    return env


def parse_codex_output(output_file: str) -> dict:
    """Parse Codex JSONL output into structured result."""
    result = {"worker": "codex", "messages": [], "errors": [], "usage": None}

    # Codex writes JSONL stream to stdout (captured as .jsonl) and last message to -o (.json)
    jsonl_file = output_file.replace(".json", ".jsonl")
    sources = []
    if os.path.exists(jsonl_file):
        sources.append(jsonl_file)
    if os.path.exists(output_file):
        # The -o file contains the last message as plain text
        try:
            with open(output_file) as f:
                last_msg = f.read().strip()
            if last_msg:
                result["messages"].append(last_msg)
        except Exception:
            pass

    if not sources:
        if not result["messages"]:
            result["errors"].append("No output file")
        return result

    for source in sources:
        try:
            with open(source) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if obj.get("type") == "item.completed":
                            item = obj.get("item", {})
                            if isinstance(item, dict) and item.get("type") == "agent_message":
                                result["messages"].append(item.get("text", ""))
                        elif obj.get("type") == "turn.completed":
                            result["usage"] = obj.get("usage")
                        elif obj.get("type") == "error":
                            msg = obj.get("message", str(obj))
                            if isinstance(msg, str):
                                result["errors"].append(msg)
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            result["errors"].append(str(e))

    return result


def parse_gemini_output(output_file: str) -> dict:
    """Parse Gemini JSON output into structured result."""
    result = {"worker": "gemini_cli", "messages": [], "errors": [], "usage": None}

    if not os.path.exists(output_file):
        result["errors"].append("No output file")
        return result

    try:
        with open(output_file) as f:
            data = json.load(f)
        result["messages"].append(data.get("response", ""))
        result["usage"] = data.get("stats")
        if data.get("error"):
            result["errors"].append(data["error"])
    except json.JSONDecodeError:
        # Try JSONL (stream-json)
        try:
            with open(output_file) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                        if obj.get("type") == "result":
                            result["messages"].append(str(obj.get("data", "")))
                        elif obj.get("type") == "error":
                            result["errors"].append(str(obj.get("data", obj)))
                    except json.JSONDecodeError:
                        continue
        except Exception as e:
            result["errors"].append(str(e))
    except Exception as e:
        result["errors"].append(str(e))

    return result


def parse_claw_code_output(output_file: str) -> dict:
    """Parse Claw Code Agent output into structured result."""
    result = {"worker": "claw_code", "messages": [], "errors": [], "usage": None}

    if not os.path.exists(output_file):
        result["errors"].append("No output file")
        return result

    # Try JSON first (if --response-schema-file was used)
    try:
        with open(output_file) as f:
            data = json.load(f)
        if isinstance(data, dict):
            # Structured output — extract response
            if data.get("response"):
                result["messages"].append(data["response"])
            elif data.get("text"):
                result["messages"].append(data["text"])
            result["usage"] = data.get("usage")
            if data.get("error"):
                result["errors"].append(data["error"])
            return result
    except (json.JSONDecodeError, ValueError):
        pass

    # Fall back to plain text — read the file as-is
    try:
        with open(output_file) as f:
            text = f.read().strip()
        if text:
            result["messages"].append(text)
    except Exception as e:
        result["errors"].append(str(e))

    return result


def get_config_sha() -> str:
    """Get the git SHA of config files for trace provenance."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%h", "--", "config/"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def write_trace(result: dict, prompt: str, task_class: str, category: str,
                lane: str, resolution: dict, trace_base_dir: str = ""):
    """Write a trace bundle for a dispatched task.

    Creates:
      trace.json     — full structured trace (primary artifact, IMMUTABLE)
      prompt.md      — rendered prompt sent to worker
      output.raw     — raw worker output (copied from dispatch output file)
      manifest.md    — human-readable summary (DERIVED from trace.json)
    """
    if not trace_base_dir:
        trace_base_dir = str(REPO_ROOT / "eval" / "traces")

    date_str = result["started"][:10]  # YYYY-MM-DD
    time_str = result["started"][11:19].replace(":", "")  # HHMMSS
    worker = result["worker"]
    trace_dir_name = f"{task_class}-{time_str}-{worker}"
    trace_dir = os.path.join(trace_base_dir, date_str, trace_dir_name)
    os.makedirs(trace_dir, exist_ok=True)

    # trace.json (primary artifact)
    trace = {
        "trace_id": f"{task_class}-{date_str}-{time_str}-{worker}",
        "schema_version": "1",
        "timestamp": result["started"],
        "harness_version": "14.2",
        "classification": {
            "description": prompt[:200],
            "task_class": task_class,
            "category": category,
            "inferred_by": "dispatch runner"
        },
        "routing": {
            "lane": lane,
            "workers": resolution.get("workers", []),
            "selected_worker": worker,
            "selection_reason": "first_available",
            "review_with": resolution.get("review_with", ""),
            "fallback_lane": resolution.get("fallback_lane"),
        },
        "prompt": {
            "template": "dispatch_v1",
            "word_count": len(prompt.split()),
            "file_path": "prompt.md"
        },
        "execution": {
            "worker": worker,
            "exit_code": result["exit_code"],
            "started": result["started"],
            "completed": result["completed"],
            "duration_seconds": result["duration"]
        },
        "output": {
            "errors": result.get("errors", []),
            "message_preview": (result.get("message", "") or "")[:200]
        },
        "retry": {
            "attempt": result.get("attempt", 1),
            "previous_traces": result.get("previous_traces", []),
            "escalated": False,
        },
        "verification": {
            "passed": result.get("verification_passed"),
            "output": result.get("verification_output", ""),
            "rolled_back": result.get("rolled_back", False),
        },
        "cost": {
            "estimated_cost_usd": 0,
            "worker_cost_basis": "subscription"
        },
        "config_snapshot": {
            "lanes_sha": get_config_sha(),
        },
        "status": result["status"]
    }

    with open(os.path.join(trace_dir, "trace.json"), "w") as f:
        json.dump(trace, f, indent=2)

    # prompt.md
    with open(os.path.join(trace_dir, "prompt.md"), "w") as f:
        f.write(prompt)

    # output.raw — copy from dispatch output file
    src_output = result.get("output_file", "")
    if src_output and os.path.exists(src_output):
        import shutil
        shutil.copy2(src_output, os.path.join(trace_dir, "output.raw"))

    # manifest.md — human-readable summary
    write_manifest(result, trace_dir)

    return trace_dir


def _build_worker_command(worker: str, prompt: str, output_file: str, model: str = "") -> list | None:
    """Build the command list for a worker. Returns None for unknown workers."""
    if worker == "codex":
        return codex_command(prompt, output_file)
    elif worker == "gemini_cli":
        return gemini_command(prompt, output_file)
    elif worker == "claw_code":
        return claw_code_command(prompt, output_file, model=model)
    elif worker == "glm_claude":
        return glm_claude_command(prompt, output_file, model=model or "glm-5-turbo")
    return None


def _run_attempt(cmd: list, env: dict, remote_host: str | None = None) -> tuple[int, str]:
    """Execute a command (optionally over SSH). Returns (exit_code, stderr)."""
    effective_cmd = ssh_wrap(remote_host, cmd) if remote_host else cmd
    try:
        proc = subprocess.run(
            effective_cmd, capture_output=True, text=True, timeout=300, env=env
        )
        return proc.returncode, (proc.stderr.strip() if proc.stderr else "")
    except subprocess.TimeoutExpired:
        return -1, "Timeout (300s)"
    except Exception as e:
        return -1, str(e)


def dispatch_single(task: dict, output_dir: str) -> dict:
    """Dispatch a single task to the appropriate worker and return result.

    Supports:
    - max_attempts: retry with error feedback (default 1 = single-shot)
    - verify_commands: list of shell cmds run after success; rollback stash if any fail
    - stash_ref: pre-existing stash from stash_before(); popped on verification failure
    - remote_host: SSH host to route the command to
    - localize: if True, inject relevant files into the prompt before dispatch
    """
    worker = task["worker"]
    original_prompt = task["prompt"]
    task_id = task["id"]
    model = task.get("model", os.environ.get("OPENAI_MODEL", ""))
    max_attempts = int(task.get("max_attempts", 1))
    verify_commands = task.get("verify_commands") or []
    stash_ref = task.get("stash_ref")
    remote_host = task.get("remote_host")
    project_dir = task.get("project_dir", os.getcwd())

    # File localization: inject relevant files into the prompt (one cheap LLM call)
    if task.get("localize"):
        try:
            from core.dispatch.localize import inject_file_context
            prompt = inject_file_context(original_prompt, project_dir=project_dir)
        except Exception:
            prompt = original_prompt
    else:
        prompt = original_prompt

    started = datetime.now(timezone.utc)
    previous_trace_ids: list[str] = []
    attempt = 0
    result: dict = {}

    for attempt in range(1, max_attempts + 1):
        output_file = os.path.join(output_dir, f"dispatch-{task_id}-a{attempt}.json")

        # On retry, append error context from previous attempt
        attempt_prompt = prompt
        if attempt > 1 and result:
            prev_errors = result.get("errors", [])
            prev_stderr = result.get("stderr", "")
            error_ctx = "\n".join(filter(None, prev_errors + [prev_stderr]))
            if error_ctx:
                attempt_prompt = (
                    f"{prompt}\n\n## Previous Attempt Failed\n\n"
                    f"Attempt {attempt - 1} produced these errors — please fix them:\n\n"
                    f"```\n{error_ctx[:1000]}\n```\n"
                )

        cmd = _build_worker_command(worker, attempt_prompt, output_file, model=model)
        if cmd is None:
            return {
                "task_id": task_id, "worker": worker, "status": "failed",
                "error": f"Unknown worker: {worker}",
                "started": started.isoformat(),
                "completed": started.isoformat(),
                "duration": 0, "exit_code": -1, "stderr": "",
                "output_file": output_file, "message": "", "errors": [], "usage": None,
                "attempt": 1, "previous_traces": [],
            }

        exit_code, stderr = _run_attempt(cmd, clean_env(), remote_host=remote_host)
        completed_dt = datetime.now(timezone.utc)

        # Parse output
        if worker == "codex":
            parsed = parse_codex_output(output_file)
        elif worker in ("claw_code", "glm_claude"):
            parsed = parse_claw_code_output(output_file)
        else:
            parsed = parse_gemini_output(output_file)

        status = "succeeded" if exit_code == 0 and not parsed["errors"] else "failed"
        last_message = parsed["messages"][-1] if parsed["messages"] else ""

        result = {
            "task_id": task_id,
            "worker": worker,
            "status": status,
            "exit_code": exit_code,
            "stderr": stderr,
            "started": started.isoformat(),
            "completed": completed_dt.isoformat(),
            "duration": round((completed_dt - started).total_seconds(), 1),
            "output_file": output_file,
            "message": last_message,
            "errors": parsed["errors"],
            "usage": parsed["usage"],
            "attempt": attempt,
            "previous_traces": list(previous_trace_ids),
        }

        if status == "succeeded":
            break

        previous_trace_ids.append(f"{task_id}-a{attempt}")

    # Verification gate: run post-dispatch commands to confirm correctness
    if result.get("status") == "succeeded" and verify_commands:
        try:
            from core.dispatch.safety import run_verification
            passed, verify_output = run_verification(verify_commands, project_dir)
            result["verification_passed"] = passed
            result["verification_output"] = verify_output
            if not passed:
                result["status"] = "failed"
                result["errors"] = result.get("errors", []) + [f"Verification failed:\n{verify_output[:500]}"]
                # Rollback if we have a stash
                if stash_ref is not None:
                    try:
                        from core.dispatch.safety import rollback
                        rolled_back = rollback(project_dir, stash_ref)
                        result["rolled_back"] = rolled_back
                    except Exception:
                        result["rolled_back"] = False
        except Exception as e:
            result["verification_passed"] = None
            result["verification_error"] = str(e)

    return result


def write_manifest(result: dict, manifest_dir: str):
    """Write a markdown manifest for a dispatched task."""
    os.makedirs(manifest_dir, exist_ok=True)
    path = os.path.join(manifest_dir, f"{result['task_id']}.md")

    status_icon = "OK" if result["status"] == "succeeded" else "FAIL"
    duration_str = f"{result['duration']}s"

    lines = [
        f"# Dispatch: {result['task_id']}",
        "",
        f"**Status**: {status_icon} — {result['status']}",
        f"**Worker**: {result['worker']}",
        f"**Duration**: {duration_str}",
        f"**Started**: {result['started']}",
        f"**Completed**: {result['completed']}",
        f"**Exit code**: {result['exit_code']}",
        f"**Output file**: `{result['output_file']}`",
        "",
    ]

    if result.get("usage"):
        lines.append(f"**Usage**: ```json\n{json.dumps(result['usage'], indent=2)}\n```")
        lines.append("")

    if result.get("message"):
        lines.extend(["## Output", "", result["message"][:2000], ""])

    if result.get("errors"):
        lines.extend(["## Errors", ""])
        for err in result["errors"]:
            lines.append(f"- {err}")
        lines.append("")

    if result.get("stderr"):
        lines.extend(["## Stderr", "", "```", result["stderr"][:1000], "```", ""])

    Path(path).write_text("\n".join(lines))


def dispatch_parallel(tasks: list[dict], max_parallel: int = 3,
                      output_dir: str = "/tmp/dispatch",
                      manifest_dir: str = "1shot/dispatch",
                      task_class: str = "", category: str = "",
                      lane: str = "", resolution: dict = None) -> list[dict]:
    """Dispatch multiple tasks in parallel and return results."""
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(manifest_dir, exist_ok=True)
    results = []
    _resolution = resolution or {}

    with ProcessPoolExecutor(max_workers=max_parallel) as executor:
        future_to_task = {
            executor.submit(dispatch_single, t, output_dir): t
            for t in tasks
        }
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                result = future.result()
                results.append(result)
                write_manifest(result, manifest_dir)
                # Write trace bundle (additive, doesn't affect dispatch)
                write_trace(
                    result, task.get("prompt", ""),
                    task_class=task_class or task.get("task_class", ""),
                    category=category or task.get("category", ""),
                    lane=lane or _resolution.get("lane", ""),
                    resolution=_resolution
                )
            except Exception as e:
                results.append({
                    "task_id": task["id"],
                    "worker": task.get("worker", "unknown"),
                    "status": "failed",
                    "error": str(e),
                })

    return sorted(results, key=lambda r: r["task_id"])


def main():
    parser = argparse.ArgumentParser(description="Dispatch tasks to Codex/Gemini/Claw workers")
    parser.add_argument("--class", dest="task_class", required=True,
                        help="Task class (implement_small, test_write, etc.)")
    parser.add_argument("--prompt", default=None,
                        help="Self-contained prompt for the worker")
    parser.add_argument("--worker", default=None,
                        help="Override worker (codex, gemini_cli, or claw_code)")
    parser.add_argument("--category", default=None,
                        help="Task category (coding, research, writing, review, general) for worker preference ordering")
    parser.add_argument("--model", default=None,
                        help="Model for claw_code worker (e.g. openai/gpt-4o-mini)")
    parser.add_argument("--output", default="/tmp/dispatch",
                        help="Output directory for dispatch files")
    parser.add_argument("--manifest", default="1shot/dispatch",
                        help="Manifest directory")
    parser.add_argument("--parallel", type=int, default=1,
                        help="Number of parallel dispatches (for batch mode)")
    parser.add_argument("--prompts-file", default=None,
                        help="JSON file with array of {id, prompt} for batch mode")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be dispatched without running")
    parser.add_argument("--localize", action="store_true",
                        help="Pre-dispatch LLM call to inject relevant file paths into prompt")
    parser.add_argument("--verify", default=None, metavar="CMD",
                        help="Shell command to run after dispatch; rollback on failure")
    parser.add_argument("--retry", type=int, default=1, metavar="N",
                        help="Max dispatch attempts with error feedback (default: 1)")
    parser.add_argument("--remote", default=None, metavar="HOST",
                        help="Dispatch to remote SSH host (must be in config/workers.yaml)")
    parser.add_argument("--stash", action="store_true",
                        help="Auto-stash before high-risk dispatch; rollback on verification failure")
    args = parser.parse_args()

    if not args.prompt and not args.prompts_file:
        parser.error("Either --prompt or --prompts-file is required")

    # Resolve lane
    resolution = resolve_lane(args.task_class, category=args.category)

    if args.dry_run:
        print(json.dumps({
            "task_class": args.task_class,
            "lane": resolution["lane"],
            "workers": resolution["workers"],
            "review_with": resolution["review_with"],
            "max_parallel": resolution.get("max_parallel", 3),
            "prompt_preview": args.prompt[:200],
        }, indent=2))
        return

    # Pick first available worker (implements strategy: first_available)
    worker = args.worker
    if not worker:
        for w in resolution["workers"]:
            if worker_available(w):
                worker = w
                break
        if not worker:
            worker = resolution["workers"][0]  # try anyway, may fail gracefully
    task_id = f"{args.task_class}-{int(time.time())}"

    # Auto-stash if --stash and high-risk task class
    stash_ref = None
    if args.stash:
        try:
            from core.dispatch.safety import stash_before, is_high_risk
            if is_high_risk(args.task_class):
                stash_ref = stash_before(os.getcwd())
                if stash_ref:
                    print(f"[dispatch] Stashed working changes: {stash_ref}", file=sys.stderr)
        except Exception as e:
            print(f"[dispatch] Stash failed (non-fatal): {e}", file=sys.stderr)

    verify_commands = [args.verify] if args.verify else []

    tasks = []
    model = args.model or ""
    if args.prompts_file:
        with open(args.prompts_file) as f:
            prompts = json.load(f)
        for i, p in enumerate(prompts):
            w = p.get("worker", worker)
            m = p.get("model", model)
            tasks.append({
                "id": f"{w}-{i}-{task_id}", "worker": w, "prompt": p["prompt"], "model": m,
                "max_attempts": args.retry, "localize": args.localize,
                "verify_commands": verify_commands, "stash_ref": stash_ref,
                "remote_host": args.remote, "project_dir": os.getcwd(),
            })
    else:
        tasks.append({
            "id": task_id, "worker": worker, "prompt": args.prompt, "model": model,
            "max_attempts": args.retry, "localize": args.localize,
            "verify_commands": verify_commands, "stash_ref": stash_ref,
            "remote_host": args.remote, "project_dir": os.getcwd(),
        })

    max_p = min(args.parallel, resolution.get("max_parallel", 3))
    results = dispatch_parallel(tasks, max_parallel=max_p,
                               output_dir=args.output,
                               manifest_dir=args.manifest,
                               task_class=args.task_class,
                               category=args.category or resolution.get("category", ""),
                               lane=resolution.get("lane", ""),
                               resolution=resolution)

    # Summary
    succeeded = sum(1 for r in results if r["status"] == "succeeded")
    failed = sum(1 for r in results if r["status"] == "failed")
    print(json.dumps({
        "dispatched": len(results),
        "succeeded": succeeded,
        "failed": failed,
        "results": results,
    }, indent=2))


if __name__ == "__main__":
    main()
