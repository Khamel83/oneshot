"""Integration tests: OpenCode adapter success criteria.

Validates that the core pieces of the OpenCode adapter are in place and functional:
1. .opencode/opencode.json exists and is valid JSON
2. AGENTS.md exists at repo root
3. Router resolves for common task classes
4. Dispatch dry-run works
5. Task tracking wrapper works
6. Config validation passes
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestOpenCodeConfig:
    def test_opencode_json_exists(self):
        p = REPO_ROOT / ".opencode" / "opencode.json"
        assert p.is_file(), f"Missing {p}"

    def test_opencode_json_is_valid(self):
        p = REPO_ROOT / ".opencode" / "opencode.json"
        data = json.loads(p.read_text())
        assert "model" in data or "defaultModel" in data or "agents" in data

    def test_agents_dir_has_files(self):
        agents = list((REPO_ROOT / ".opencode" / "agents").glob("*.md"))
        assert len(agents) >= 2, f"Expected 2+ agent files, found {len(agents)}"

    def test_commands_dir_has_files(self):
        commands = list((REPO_ROOT / ".opencode" / "commands").glob("*.md"))
        assert len(commands) >= 4, f"Expected 4+ command files, found {len(commands)}"


class TestAGENTSmd:
    def test_agents_md_exists(self):
        assert (REPO_ROOT / "AGENTS.md").is_file()


class TestRouterResolves:
    def test_implement_small_resolves(self):
        r = subprocess.run(
            [sys.executable, "-m", "core.dispatch.run",
             "--class", "implement_small", "--prompt", "test", "--dry-run"],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Router failed: {r.stderr}"
        data = json.loads(r.stdout)
        assert data["lane"] is not None

    def test_doc_draft_resolves(self):
        r = subprocess.run(
            [sys.executable, "-m", "core.dispatch.run",
             "--class", "doc_draft", "--prompt", "test", "--dry-run"],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0
        data = json.loads(r.stdout)
        assert data["selected_worker"] is not None


class TestTaskTracking:
    def test_tasks_script_runs(self):
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "tasks.py"), "--help"],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0
        assert "task" in r.stdout.lower()


class TestConfigValidation:
    def test_validate_script_passes(self):
        r = subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "validate-oneshot-config.py")],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"Validation failed: {r.stdout}"
