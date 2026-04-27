"""Task IO, dispatch, status, collect, review, escalate."""
from __future__ import annotations

import json
import os
import random
import string
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from oneshot_cli.config import (
    load_config, get_lane, resolve_provider_model, get_runner_template,
)
from oneshot_cli.worktree import create, remove, worktree_path, branch_name

REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / ".oneshot" / "tasks"


# ---------------------------------------------------------------------------
# Task ID generation
# ---------------------------------------------------------------------------

def _generate_task_id(lane: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    rand4 = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{lane}-{now}-{rand4}"


# ---------------------------------------------------------------------------
# Task directory helpers
# ---------------------------------------------------------------------------

def task_dir(task_id: str) -> Path:
    return TASKS_DIR / task_id


def _task_exists(task_id: str) -> bool:
    return task_dir(task_id).exists()


def _read_status(task_id: str) -> dict:
    p = task_dir(task_id) / "status.json"
    with open(p) as f:
        return json.load(f)


def _write_status(task_id: str, data: dict) -> None:
    p = task_dir(task_id) / "status.json"
    with open(p, "w") as f:
        json.dump(data, f, indent=2, default=str)
        f.write("\n")


def _read_file(task_id: str, name: str) -> str:
    p = task_dir(task_id) / name
    if not p.exists():
        raise FileNotFoundError(f"{name} not found for task {task_id}")
    return p.read_text()


def _write_file(task_id: str, name: str, content: str) -> None:
    p = task_dir(task_id) / name
    p.write_text(content)


# ---------------------------------------------------------------------------
# Base SHA capture
# ---------------------------------------------------------------------------

def _get_base_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True, cwd=REPO_ROOT,
    )
    return result.stdout.strip()


# ---------------------------------------------------------------------------
# Dirty tree check
# ---------------------------------------------------------------------------

def _is_tree_dirty() -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=REPO_ROOT,
    )
    return bool(result.stdout.strip())


# ---------------------------------------------------------------------------
# DISPATCH
# ---------------------------------------------------------------------------

def dispatch(
    lane: str,
    task_text: str | None = None,
    task_file: str | None = None,
    runner: str | None = None,
    allow_dirty: bool = False,
) -> str:
    cfg = load_config()
    lane_data = get_lane(cfg, lane)
    provider_key, model_key, model_id = resolve_provider_model(cfg, lane)

    # Read task description
    if task_file:
        task_md = Path(task_file).read_text()
    elif task_text:
        task_md = task_text
    else:
        raise ValueError("Provide --task or --task-file")

    # Dirty tree check
    if not allow_dirty and _is_tree_dirty():
        raise SystemExit(
            "Error: main working tree is dirty; use --allow-dirty to override"
        )

    # Generate task ID and create directory
    task_id = _generate_task_id(lane)
    td = task_dir(task_id)
    td.mkdir(parents=True, exist_ok=True)

    # Write task.md
    _write_file(task_id, "task.md", task_md)

    # Capture base SHA before worktree creation
    base_sha = _get_base_sha()

    # Create worktree
    wp = create(task_id)

    # Build status.json
    now = datetime.now(timezone.utc).isoformat()
    status_data = {
        "task_id": task_id,
        "lane": lane,
        "provider": provider_key,
        "model": model_key,
        "model_id": model_id,
        "base_sha": base_sha,
        "branch": branch_name(task_id),
        "worktree_path": str(wp),
        "head_sha": base_sha,
        "created_at": now,
        "updated_at": now,
        "status": "dispatched",
        "parent_task_id": None,
    }
    _write_status(task_id, status_data)

    # Render worker.md (preamble + task.md)
    preamble = (
        "# Worker Task\n\n"
        f"Lane: {lane}\n"
        f"Provider: {provider_key}\n"
        f"Model: {model_id}\n"
        f"Base SHA: {base_sha}\n"
        f"Worktree: {wp}\n\n"
        "You are executing a bounded task in an isolated git worktree.\n"
        "Make your changes in the worktree. Do not modify files outside it.\n"
        "Write a summary of your changes to result.md in the task directory.\n\n"
        "---\n\n"
    )
    _write_file(task_id, "worker.md", preamble + task_md)

    # Resolve runner template and write dry-run command to worker.log
    if runner is None:
        runner = provider_key
    tmpl = get_runner_template(cfg, runner)

    task_file_path = str(wp / "worker.md")
    command = tmpl["command"].format(
        model_id=model_id,
        task_file=task_file_path,
        worktree_path=str(wp),
    )
    cwd_note = tmpl.get("cwd", str(wp)).format(worktree_path=str(wp))

    log_content = (
        f"# Dry-run command (MVP — not executed)\n\n"
        f"Runner: {runner}\n"
        f"Command: {command}\n"
        f"CWD: {cwd_note}\n"
    )
    _write_file(task_id, "worker.log", log_content)

    print(f"Dispatched task: {task_id}")
    print(f"  Lane:       {lane}")
    print(f"  Provider:   {provider_key}/{model_id}")
    print(f"  Worktree:   {wp}")
    print(f"  Branch:     {branch_name(task_id)}")
    print()
    print(f"Next: ./bin/oneshot status {task_id}")
    print(f"      ./bin/oneshot review {task_id}  (after worktree changes)")

    return task_id


# ---------------------------------------------------------------------------
# STATUS
# ---------------------------------------------------------------------------

def status(task_id: str | None = None) -> None:
    if task_id:
        _print_single_status(task_id)
        return

    # List all tasks
    if not TASKS_DIR.exists():
        print("No tasks found.")
        return

    tasks = sorted(TASKS_DIR.iterdir())
    tasks = [t for t in tasks if t.is_dir() and (t / "status.json").exists()]

    if not tasks:
        print("No tasks found.")
        return

    print(f"{'TASK ID':<50} {'LANE':<20} {'PROVIDER/MODEL':<25} {'STATUS':<12}")
    print("-" * 107)

    for td in tasks:
        with open(td / "status.json") as f:
            s = json.load(f)
        tid = s.get("task_id", td.name)
        ln = s.get("lane", "?")
        pm = f"{s.get('provider', '?')}/{s.get('model_id', '?')}"
        st = s.get("status", "?")
        print(f"{tid:<50} {ln:<20} {pm:<25} {st:<12}")


def _print_single_status(task_id: str) -> None:
    if not _task_exists(task_id):
        raise SystemExit(f"Task not found: {task_id}")
    s = _read_status(task_id)
    print(json.dumps(s, indent=2))


# ---------------------------------------------------------------------------
# COLLECT
# ---------------------------------------------------------------------------

def collect(task_id: str) -> None:
    if not _task_exists(task_id):
        raise SystemExit(f"Task not found: {task_id}")

    s = _read_status(task_id)
    wp = Path(s["worktree_path"])
    base_sha = s["base_sha"]

    if not wp.exists():
        raise SystemExit(f"Worktree not found: {wp}")

    # Get head SHA from worktree
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True, cwd=wp,
    )
    head_sha = result.stdout.strip()

    # Generate diff.patch
    diff_result = subprocess.run(
        ["git", "diff", f"{base_sha}..{head_sha}"],
        capture_output=True, text=True, cwd=wp,
    )
    _write_file(task_id, "diff.patch", diff_result.stdout)

    # Get changed files list
    name_status = subprocess.run(
        ["git", "diff", f"{base_sha}..{head_sha}", "--name-status"],
        capture_output=True, text=True, cwd=wp,
    )

    # Run test command if configured
    cfg = load_config()
    test_cmd = cfg.get("verification", {}).get("test_command")
    if test_cmd:
        test_result = subprocess.run(
            test_cmd, shell=True, capture_output=True, text=True, cwd=wp,
        )
        test_log = f"Exit code: {test_result.returncode}\n\n{test_result.stdout}\n{test_result.stderr}"
    else:
        test_log = "Skipped: no test_command configured in .oneshot/config/models.yaml"

    _write_file(task_id, "test.log", test_log)

    # Write result.md
    result_md = (
        f"# Result for {task_id}\n\n"
        f"**Head SHA:** {head_sha}\n"
        f"**Base SHA:** {base_sha}\n"
        f"**Changed files:**\n\n"
    )
    if name_status.stdout.strip():
        result_md += "```\n" + name_status.stdout.strip() + "\n```\n\n"
    else:
        result_md += "(no changes)\n\n"

    result_md += f"**Test log:**\n\n```\n{test_log}\n```\n"
    _write_file(task_id, "result.md", result_md)

    # Update status
    s["head_sha"] = head_sha
    s["status"] = "collected"
    s["updated_at"] = datetime.now(timezone.utc).isoformat()
    _write_status(task_id, s)

    print(f"Collected {task_id}")
    print(f"  Changed files: {len(name_status.stdout.strip().splitlines()) if name_status.stdout.strip() else 0}")
    print(f"  Next: ./bin/oneshot review {task_id}")


# ---------------------------------------------------------------------------
# REVIEW
# ---------------------------------------------------------------------------

def review(task_id: str) -> None:
    if not _task_exists(task_id):
        raise SystemExit(f"Task not found: {task_id}")

    td = task_dir(task_id)
    files = {
        "task.md": td / "task.md",
        "result.md": td / "result.md",
        "diff.patch": td / "diff.patch",
        "test.log": td / "test.log",
    }

    print(f"Review bundle for {task_id}:")
    for name, path in files.items():
        exists = path.exists()
        marker = "" if exists else " (missing)"
        print(f"  {path}{marker}")

    if not (td / "result.md").exists():
        print(f"\nTask has not been collected yet. Run: ./bin/oneshot collect {task_id}")


# ---------------------------------------------------------------------------
# ESCALATE
# ---------------------------------------------------------------------------

def escalate(task_id: str, new_lane: str) -> str:
    if not _task_exists(task_id):
        raise SystemExit(f"Task not found: {task_id}")

    parent_status = _read_status(task_id)
    parent_task = _read_file(task_id, "task.md")

    try:
        parent_result = _read_file(task_id, "result.md")
    except FileNotFoundError:
        parent_result = "(no result collected yet)"

    cfg = load_config()
    get_lane(cfg, new_lane)  # validate lane exists

    new_id = _generate_task_id(new_lane)
    td = task_dir(new_id)
    td.mkdir(parents=True, exist_ok=True)

    escalated_task = (
        f"# Escalated Task (from {task_id})\n\n"
        f"**Original lane:** {parent_status['lane']}\n"
        f"**Escalated to:** {new_lane}\n"
        f"**Reason:** Previous attempt on lane '{parent_status['lane']}' did not succeed.\n\n"
        "---\n\n"
        f"## Original Task\n\n{parent_task}\n\n"
        f"## Previous Result\n\n{parent_result}\n\n"
        "---\n\n"
        "Please attempt this task with greater care. Address the issues noted in the previous result.\n"
    )

    _write_file(new_id, "task.md", escalated_task)

    now = datetime.now(timezone.utc).isoformat()
    base_sha = _get_base_sha()

    status_data = {
        "task_id": new_id,
        "lane": new_lane,
        "provider": None,
        "model": None,
        "model_id": None,
        "base_sha": base_sha,
        "branch": None,
        "worktree_path": None,
        "head_sha": base_sha,
        "created_at": now,
        "updated_at": now,
        "status": "pending",
        "parent_task_id": task_id,
    }
    _write_status(new_id, status_data)

    print(f"Created escalation task: {new_id}")
    print(f"  From: {task_id} ({parent_status['lane']})")
    print(f"  To:   {new_lane}")
    print(f"  Next: ./bin/oneshot dispatch --lane {new_lane} --task-file {td / 'task.md'}")

    return new_id
