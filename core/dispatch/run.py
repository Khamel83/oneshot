"""Parallel dispatch runner for Codex and Gemini.

Usage:
    python -m core.dispatch.run --class implement_small --prompt "Fix the auth bug in login.py" --output /tmp/dispatch
    python -m core.dispatch.run --class implement_small --prompt "..." --parallel 3
    python -m core.dispatch.run --manifest 1shot/dispatch
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


def resolve_lane(task_class: str) -> dict:
    """Resolve task class to lane config using the router module."""
    sys.path.insert(0, str(REPO_ROOT))
    from core.router.lane_policy import resolve
    return resolve(task_class, str(CONFIG_PATH))


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
        f"--output-format json --yolo "
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


def worker_available(worker: str) -> bool:
    """Check if a worker is available on this machine."""
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
        )
        return has_install and has_key
    elif worker == "glm_claude":
        has_claude = subprocess.run(
            ["bash", "-c", "command -v claude"], capture_output=True
        ).returncode == 0
        has_key = bool(os.environ.get("ZAI_API_KEY"))
        return has_claude and has_key
    return True


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


def dispatch_single(task: dict, output_dir: str) -> dict:
    """Dispatch a single task to the appropriate worker and return result."""
    worker = task["worker"]
    prompt = task["prompt"]
    task_id = task["id"]
    output_file = os.path.join(output_dir, f"dispatch-{task_id}.json")
    started = datetime.now(timezone.utc)

    # Build command
    if worker == "codex":
        cmd = codex_command(prompt, output_file)
    elif worker == "gemini_cli":
        cmd = gemini_command(prompt, output_file)
    elif worker == "claw_code":
        model = task.get("model", os.environ.get("OPENAI_MODEL", ""))
        cmd = claw_code_command(prompt, output_file, model=model)
    elif worker == "glm_claude":
        model = task.get("model", "glm-5-turbo")
        cmd = glm_claude_command(prompt, output_file, model=model)
    else:
        return {"task_id": task_id, "worker": worker, "status": "failed",
                "error": f"Unknown worker: {worker}"}

    # Execute
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                             env=clean_env())
        exit_code = proc.returncode
        stderr = proc.stderr.strip() if proc.stderr else ""
    except subprocess.TimeoutExpired:
        exit_code = -1
        stderr = "Timeout (300s)"
    except Exception as e:
        exit_code = -1
        stderr = str(e)

    completed = datetime.now(timezone.utc)
    duration = (completed - started).total_seconds()

    # Parse output
    if worker == "codex":
        parsed = parse_codex_output(output_file)
    elif worker in ("claw_code", "glm_claude"):
        parsed = parse_claw_code_output(output_file)
    else:
        parsed = parse_gemini_output(output_file)

    # Determine status
    status = "succeeded" if exit_code == 0 and not parsed["errors"] else "failed"
    last_message = parsed["messages"][-1] if parsed["messages"] else ""

    return {
        "task_id": task_id,
        "worker": worker,
        "status": status,
        "exit_code": exit_code,
        "stderr": stderr,
        "started": started.isoformat(),
        "completed": completed.isoformat(),
        "duration": round(duration, 1),
        "output_file": output_file,
        "message": last_message,
        "errors": parsed["errors"],
        "usage": parsed["usage"],
    }


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
                      manifest_dir: str = "1shot/dispatch") -> list[dict]:
    """Dispatch multiple tasks in parallel and return results."""
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(manifest_dir, exist_ok=True)
    results = []

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
    args = parser.parse_args()

    if not args.prompt and not args.prompts_file:
        parser.error("Either --prompt or --prompts-file is required")

    # Resolve lane
    resolution = resolve_lane(args.task_class)

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

    tasks = []
    model = args.model or ""
    if args.prompts_file:
        with open(args.prompts_file) as f:
            prompts = json.load(f)
        for i, p in enumerate(prompts):
            w = p.get("worker", worker)
            m = p.get("model", model)
            tasks.append({"id": f"{w}-{i}-{task_id}", "worker": w, "prompt": p["prompt"], "model": m})
    else:
        tasks.append({"id": task_id, "worker": worker, "prompt": args.prompt, "model": model})

    max_p = min(args.parallel, resolution.get("max_parallel", 3))
    results = dispatch_parallel(tasks, max_parallel=max_p,
                               output_dir=args.output,
                               manifest_dir=args.manifest)

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
