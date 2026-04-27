"""Tests for scripts/validate-oneshot-config.py."""

import importlib.util
from pathlib import Path

SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "validate-oneshot-config.py"
)
SPEC = importlib.util.spec_from_file_location("validate_oneshot_config", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_worker_harness_bridge_has_expected_aliases():
    assert MODULE.WORKER_HARNESS_BRIDGE["claude_code"] == "claude_review"
    assert MODULE.WORKER_HARNESS_BRIDGE["glm_claude"] == "zai"
    assert MODULE.WORKER_HARNESS_BRIDGE["opencode"] == "opencode_go"


def test_repo_config_bridge_is_currently_valid():
    assert MODULE.validate() == []
