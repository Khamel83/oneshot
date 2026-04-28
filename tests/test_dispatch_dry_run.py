"""Tests for core.dispatch.run --dry-run mode."""

import json
import subprocess
import sys
from pathlib import Path

DISPATCH_SCRIPT = Path(__file__).resolve().parent.parent / "core" / "dispatch" / "run.py"


def _dry_run(task_class="implement_small", prompt="test"):
    result = subprocess.run(
        [sys.executable, "-m", "core.dispatch.run",
         "--class", task_class, "--prompt", prompt, "--dry-run"],
        capture_output=True, text=True, timeout=30,
    )
    return json.loads(result.stdout), result.returncode


def test_dry_run_returns_valid_json():
    data, code = _dry_run()
    assert code == 0


def test_dry_run_includes_required_fields():
    data, _ = _dry_run()
    for field in ("task_class", "lane", "workers", "worker_availability",
                   "selected_worker", "review_with", "would_dispatch"):
        assert field in data, f"Missing field: {field}"


def test_dry_run_would_dispatch_true():
    data, _ = _dry_run()
    assert data["would_dispatch"] is True


def test_dry_run_no_actual_execution():
    data, _ = _dry_run(prompt="echo HACKED")
    assert data["would_dispatch"] is True
    assert "echo HACKED" not in str(data.get("worker_availability", {}))


def test_dry_run_different_task_classes():
    for tc in ("implement_small", "implement_medium", "doc_draft", "review_diff"):
        data, code = _dry_run(task_class=tc)
        assert code == 0
        assert data["task_class"] == tc
