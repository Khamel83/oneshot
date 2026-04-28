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


def test_opencode_config_exists():
    assert MODULE.OPENCODE_CONFIG.is_file()


def test_opencode_agents_dir_exists():
    assert MODULE.OPENCODE_AGENTS_DIR.is_dir()
    agent_files = list(MODULE.OPENCODE_AGENTS_DIR.glob("*.md"))
    assert len(agent_files) >= 1


def test_cheap_worker_has_bash_false():
    agent_file = MODULE.OPENCODE_AGENTS_DIR / "cheap-worker.md"
    content = agent_file.read_text()
    assert "bash: false" in content or "bash:false" in content


def test_reviewer_has_bash_false():
    agent_file = MODULE.OPENCODE_AGENTS_DIR / "reviewer.md"
    content = agent_file.read_text()
    assert "bash: false" in content or "bash:false" in content
