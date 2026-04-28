"""Dispatch CLI contract tests."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

from click.testing import CliRunner
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from oneshot_cli.__main__ import cli
from oneshot_cli import tasks as task_module


def _setup_dispatch_test_env(tmp_path, monkeypatch, auth_value="super-secret-token"):
    tasks_dir = tmp_path / ".oneshot" / "tasks"
    worktree = tmp_path / "worktree"
    worktree.mkdir(parents=True)
    (worktree / "AGENTS.md").write_text("placeholder")

    monkeypatch.setattr(task_module, "TASKS_DIR", tasks_dir)
    monkeypatch.setattr(task_module, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(task_module, "_is_tree_dirty", lambda: False)
    monkeypatch.setattr(task_module, "_get_base_sha", lambda: "abc123")
    monkeypatch.setattr(task_module, "create", lambda task_id: worktree)
    monkeypatch.setattr(task_module, "branch_name", lambda task_id: f"worker/{task_id}")
    monkeypatch.setattr(
        task_module, "load_config", lambda: {"verification": {"test_command": None}}
    )
    monkeypatch.setattr(
        task_module,
        "get_lane",
        lambda cfg, lane: {"current_provider": "zai", "current_model": "glm_5_1"},
    )
    monkeypatch.setattr(
        task_module,
        "resolve_provider_model",
        lambda cfg, lane: ("zai", "glm_5_1", "glm-5.1"),
    )
    monkeypatch.setattr(
        task_module,
        "get_runner_template",
        lambda cfg, runner: {
            "command": "runner --token {auth_value} --model {model_id} --task {task_file}",
            "cwd": "{worktree_path}",
            "auth_env": "TEST_AUTH_TOKEN",
            "env": {},
        },
    )
    monkeypatch.setenv("TEST_AUTH_TOKEN", auth_value)
    return tasks_dir


def test_dispatch_help_describes_live_execution():
    runner = CliRunner()
    result = runner.invoke(cli, ["dispatch", "--help"])

    assert result.exit_code == 0
    assert "external worker and execute it in a worktree" in result.output
    assert "dry-run" not in result.output.lower()


def test_opencode_runner_template_uses_resolved_model_id_once():
    config_path = (
        Path(__file__).resolve().parent.parent / ".oneshot" / "config" / "models.yaml"
    )
    cfg = yaml.safe_load(config_path.read_text())

    command = cfg["runner_templates"]["opencode_go"]["command"]

    assert command.count("{model_id}") == 1
    assert command.endswith("--prompt-file {task_file}")
    assert "opencode-go/{model_id}" in command


def test_dispatch_worker_log_redacts_auth_value(tmp_path, monkeypatch):
    tasks_dir = _setup_dispatch_test_env(tmp_path, monkeypatch)

    def fake_run(*args, **kwargs):
        return MagicMock(returncode=0, stdout="ok\n", stderr="")

    monkeypatch.setattr(task_module.subprocess, "run", fake_run)

    task_id = task_module.dispatch("routine_coder", task_text="test task")
    worker_log = (tasks_dir / task_id / "worker.log").read_text()

    assert "super-secret-token" not in worker_log
    assert "$TEST_AUTH_TOKEN" in worker_log


def test_dispatch_marks_failed_status_and_logs_stderr(tmp_path, monkeypatch):
    tasks_dir = _setup_dispatch_test_env(tmp_path, monkeypatch)

    def fake_run(*args, **kwargs):
        return MagicMock(returncode=7, stdout="", stderr="boom\n")

    monkeypatch.setattr(task_module.subprocess, "run", fake_run)

    task_id = task_module.dispatch("routine_coder", task_text="test task")
    status = task_module._read_status(task_id)
    worker_log = (tasks_dir / task_id / "worker.log").read_text()

    assert status["status"] == "failed"
    assert "Exit code: 7" in worker_log
    assert "boom" in worker_log


def test_dispatch_marks_timeout_status(tmp_path, monkeypatch):
    tasks_dir = _setup_dispatch_test_env(tmp_path, monkeypatch)

    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd="runner", timeout=600)

    monkeypatch.setattr(task_module.subprocess, "run", fake_run)

    task_id = task_module.dispatch("routine_coder", task_text="test task")
    status = task_module._read_status(task_id)
    worker_log = (tasks_dir / task_id / "worker.log").read_text()

    assert status["status"] == "timeout"
    assert "Timeout: killed after 600s" in worker_log
