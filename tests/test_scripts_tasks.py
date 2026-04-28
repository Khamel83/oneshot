"""Tests for scripts/tasks.py — standalone JSON task tracker."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "tasks.py"


def _run(*args, env_tasks_file: Path | None = None):
    env = {"TASKS_FILE": str(env_tasks_file)} if env_tasks_file else {}
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, env=env,
    )
    return result


def test_list_empty():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump({"version": 1, "tasks": []}, f)
        f.flush()
        result = _run("list", env_tasks_file=Path(f.name))
    assert result.returncode == 0
    assert "No tasks" in result.stdout


def test_add_and_list():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump({"version": 1, "tasks": []}, f)
        f.flush()
        tf = Path(f.name)
        _run("add", "Test task", "--priority", "high", env_tasks_file=tf)
        result = _run("list", env_tasks_file=tf)
    assert "#1 Test task" in result.stdout
    assert result.returncode == 0


def test_show_task():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump({"version": 1, "tasks": []}, f)
        f.flush()
        tf = Path(f.name)
        _run("add", "Show me", env_tasks_file=tf)
        result = _run("show", "1", env_tasks_file=tf)
    assert "Show me" in result.stdout
    assert result.returncode == 0


def test_clear_done():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        json.dump({"version": 1, "tasks": []}, f)
        f.flush()
        tf = Path(f.name)
        _run("add", "Done task", env_tasks_file=tf)
        _run("update", "1", "done", env_tasks_file=tf)
        result = _run("clear-done", env_tasks_file=tf)
    assert "Cleared 1" in result.stdout
