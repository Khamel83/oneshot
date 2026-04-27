"""Tests for oneshot_cli/doctor_cmd.py."""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from oneshot_cli.doctor_cmd import (
    OK,
    MISSING,
    AUTH_REQUIRED,
    BLOCKED,
    ERROR,
    _expand_env,
    _expand_recursive,
    autofix,
    check_oc_launcher,
    check_codex_auth,
    check_gemini_auth,
    check_ssh_config,
    check_secrets_decrypt,
    detect_local_machine,
    format_results,
    load_machines,
    remote_fix_instructions,
    run_remote_checks,
    run_local_checks,
    summarize,
)


# ── Env var expansion ──


class TestEnvExpansion:
    def test_expand_default(self):
        assert _expand_env("${FOO:-bar}") == "bar"

    def test_expand_set(self):
        os.environ["TEST_DOCTOR_X"] = "override"
        try:
            assert _expand_env("${TEST_DOCTOR_X:-default}") == "override"
        finally:
            del os.environ["TEST_DOCTOR_X"]

    def test_expand_no_default(self):
        assert _expand_env("${NONEXISTENT_XYZ:-}") == ""

    def test_expand_in_dict(self):
        data = {"host": "${MY_HOST:-oci-ts}"}
        result = _expand_recursive(data)
        assert result["host"] == "oci-ts"

    def test_expand_nested_dict(self):
        data = {"machines": {"a": {"host": "${H:-local}"}}}
        result = _expand_recursive(data)
        assert result["machines"]["a"]["host"] == "local"


# ── Machine config loading ──


class TestMachinesConfig:
    def test_load_from_file(self, tmp_path):
        cfg = tmp_path / "machines.yaml"
        cfg.write_text("""
machines:
  test1:
    host: test1-ts
    role: worker
  test2:
    host: test2-ts
    role: server
    enabled: false
""")
        m = load_machines(cfg)
        assert "test1" in m["machines"]
        assert m["machines"]["test1"]["host"] == "test1-ts"
        assert m["machines"]["test2"]["enabled"] is False

    def test_missing_file_returns_empty(self, tmp_path):
        m = load_machines(tmp_path / "nonexistent.yaml")
        assert m["machines"] == {}


# ── Individual checks ──


class TestChecks:
    @patch("oneshot_cli.doctor_cmd._run")
    def test_check_python3_ok(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stderr="Python 3.12.3\n", stdout=""
        )
        from oneshot_cli.doctor_cmd import check_python3

        status, detail = check_python3()
        assert status == OK
        assert "3.12" in detail

    @patch("oneshot_cli.doctor_cmd._run")
    def test_check_python3_missing(self, mock_run):
        mock_run.return_value = MagicMock(returncode=127, stderr="", stdout="")
        from oneshot_cli.doctor_cmd import check_python3

        status, detail = check_python3()
        assert status == MISSING

    @patch("oneshot_cli.doctor_cmd._run")
    def test_check_git_ok(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="git version 2.43.0\n", stderr=""
        )
        from oneshot_cli.doctor_cmd import check_git

        status, _ = check_git()
        assert status == OK

    @patch("oneshot_cli.doctor_cmd._run")
    def test_check_git_missing(self, mock_run):
        mock_run.return_value = MagicMock(returncode=127, stdout="", stderr="")
        from oneshot_cli.doctor_cmd import check_git

        status, _ = check_git()
        assert status == MISSING


class TestOcLauncher:
    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=False)
    def test_missing_when_no_launcher(self, mock_has_binary):
        status, _ = check_oc_launcher()
        assert status == MISSING

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_ok_with_launcher_path(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="/home/test/.local/bin/oc\n", stderr=""
        )
        status, detail = check_oc_launcher()
        assert status == OK
        assert detail.endswith("/oc")


class TestGeminiAuth:
    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=False)
    def test_missing_when_no_binary(self, mock_has_binary):
        status, _ = check_gemini_auth()
        assert status == MISSING

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_ok_when_ready(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(returncode=0, stdout="READY", stderr="")
        status, detail = check_gemini_auth()
        assert status == OK
        assert "Gemini Code Assist" in detail

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_auth_required_on_error(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="not authenticated"
        )
        status, _ = check_gemini_auth()
        assert status == AUTH_REQUIRED

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_auth_required_on_timeout(self, mock_run, mock_has_binary):
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="gemini", timeout=45)
        status, _ = check_gemini_auth()
        assert status == AUTH_REQUIRED


class TestCodexAuth:
    def test_missing_when_no_binary(self):
        with patch("oneshot_cli.doctor_cmd._has_binary", return_value=False):
            status, _ = check_codex_auth()
            assert status == MISSING

    def test_auth_required_when_no_file(self, tmp_path):
        with (
            patch("oneshot_cli.doctor_cmd._has_binary", return_value=True),
            patch("oneshot_cli.doctor_cmd.Path.home", return_value=tmp_path),
        ):
            status, _ = check_codex_auth()
            assert status == AUTH_REQUIRED

    def test_ok_with_nested_refresh_token(self, tmp_path):
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir()
        auth_file = codex_dir / "auth.json"
        auth_file.write_text(
            json.dumps(
                {
                    "auth_mode": "oauth",
                    "tokens": {"refresh_token": "abc123", "access_token": "xyz"},
                }
            )
        )
        with (
            patch("oneshot_cli.doctor_cmd._has_binary", return_value=True),
            patch("oneshot_cli.doctor_cmd.Path.home", return_value=tmp_path),
        ):
            status, _ = check_codex_auth()
            assert status == OK

    def test_auth_required_with_invalid_json(self, tmp_path):
        codex_dir = tmp_path / ".codex"
        codex_dir.mkdir()
        (codex_dir / "auth.json").write_text("not json")
        with (
            patch("oneshot_cli.doctor_cmd._has_binary", return_value=True),
            patch("oneshot_cli.doctor_cmd.Path.home", return_value=tmp_path),
        ):
            status, _ = check_codex_auth()
            assert status == AUTH_REQUIRED


class TestSecretsDecrypt:
    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=False)
    def test_missing_when_no_binary(self, mock_has_binary):
        status, _ = check_secrets_decrypt()
        assert status == MISSING

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_ok_with_output(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="file1.env\nfile2.env\n", stderr=""
        )
        status, detail = check_secrets_decrypt()
        assert status == OK
        assert "2" in detail

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_blocked_on_passphrase(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="Error: passphrase required"
        )
        status, _ = check_secrets_decrypt()
        assert status == BLOCKED

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_error_unknown(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="something unexpected happened"
        )
        status, _ = check_secrets_decrypt()
        assert status == ERROR


class TestSshConfig:
    def test_ok_when_hosts_present(self, tmp_path):
        ssh_config = tmp_path / ".ssh" / "config"
        ssh_config.parent.mkdir(parents=True)
        ssh_config.write_text(
            "Host oci-ts\n  HostName 100.126.13.70\nHost macmini-ts\n  HostName 100.113.216.27\n"
        )
        with patch("oneshot_cli.doctor_cmd.Path.home", return_value=tmp_path):
            status, detail = check_ssh_config(["oci-ts", "macmini-ts"])
            assert status == OK
            assert "oci-ts" in detail
            assert "macmini-ts" in detail

    def test_missing_when_no_hosts(self, tmp_path):
        ssh_config = tmp_path / ".ssh" / "config"
        ssh_config.parent.mkdir(parents=True)
        ssh_config.write_text("Host github.com\n  HostName 1.2.3.4\n")
        with patch("oneshot_cli.doctor_cmd.Path.home", return_value=tmp_path):
            status, _ = check_ssh_config(["oci-ts"])
            assert status == MISSING

    def test_error_when_no_config(self, tmp_path):
        with patch(
            "oneshot_cli.doctor_cmd.Path.home", return_value=tmp_path / "nonexistent"
        ):
            status, _ = check_ssh_config(["oci-ts"])
            assert status == ERROR


# ── Output formatting ──


class TestOutputFormat:
    def test_format_includes_machine_name(self):
        results = [{"name": "python3", "status": OK, "detail": "3.12.3"}]
        output = format_results("oci", True, results)
        assert "oci" in output
        assert "this machine" in output

    def test_format_includes_status(self):
        results = [
            {"name": "python3", "status": OK, "detail": "3.12.3"},
            {"name": "codex", "status": MISSING, "detail": ""},
        ]
        output = format_results("test", False, results)
        assert "OK" in output
        assert "MISSING" in output


# ── Summarize ──


class TestSummarize:
    def test_all_ok_returns_zero(self):
        results = [{"name": "x", "status": OK, "detail": ""}]
        code, summary = summarize(results)
        assert code == 0
        assert summary == "all OK"

    def test_missing_returns_one(self):
        results = [{"name": "x", "status": MISSING, "detail": ""}]
        code, summary = summarize(results)
        assert code == 1
        assert "MISSING" in summary

    def test_auth_required_returns_two(self):
        results = [{"name": "x", "status": AUTH_REQUIRED, "detail": ""}]
        code, summary = summarize(results)
        assert code == 2
        assert "AUTH_REQUIRED" in summary

    def test_blocked_returns_two(self):
        results = [{"name": "x", "status": BLOCKED, "detail": ""}]
        code, summary = summarize(results)
        assert code == 2

    def test_mixed_returns_two(self):
        results = [
            {"name": "x", "status": OK, "detail": ""},
            {"name": "y", "status": MISSING, "detail": ""},
            {"name": "z", "status": AUTH_REQUIRED, "detail": ""},
        ]
        code, summary = summarize(results)
        assert code == 2
        assert "MISSING" in summary
        assert "AUTH_REQUIRED" in summary


# ── Local checks ──


class TestLocalChecks:
    @patch("oneshot_cli.doctor_cmd.check_python3", return_value=(OK, "3.12"))
    @patch("oneshot_cli.doctor_cmd.check_git", return_value=(OK, "2.43"))
    @patch("oneshot_cli.doctor_cmd.check_claude", return_value=(OK, "2.1"))
    @patch("oneshot_cli.doctor_cmd.check_opencode", return_value=(MISSING, ""))
    @patch(
        "oneshot_cli.doctor_cmd.check_oc_launcher",
        return_value=(OK, "/home/test/.local/bin/oc"),
    )
    @patch("oneshot_cli.doctor_cmd.check_opencode_auth", return_value=(MISSING, ""))
    @patch("oneshot_cli.doctor_cmd.check_gemini", return_value=(OK, "0.39"))
    @patch("oneshot_cli.doctor_cmd.check_gemini_auth", return_value=(OK, "ready"))
    @patch("oneshot_cli.doctor_cmd.check_codex", return_value=(OK, "0.118"))
    @patch(
        "oneshot_cli.doctor_cmd.check_codex_auth",
        return_value=(AUTH_REQUIRED, "no token"),
    )
    @patch(
        "oneshot_cli.doctor_cmd.check_secrets_cli",
        return_value=(OK, "/usr/bin/secrets"),
    )
    @patch(
        "oneshot_cli.doctor_cmd.check_secrets_decrypt", return_value=(OK, "14 files")
    )
    @patch("oneshot_cli.doctor_cmd.check_age_key", return_value=(OK, "~/.age/key.txt"))
    @patch("oneshot_cli.doctor_cmd.check_worktree_path", return_value=(OK, "writable"))
    @patch("oneshot_cli.doctor_cmd.check_repo_path", return_value=(OK, "exists"))
    @patch(
        "oneshot_cli.doctor_cmd.check_ssh_config",
        return_value=(OK, "oci-ts, macmini-ts"),
    )
    def test_returns_all_checks(self, *mocks):
        results = run_local_checks(["oci-ts", "macmini-ts"])
        names = [r["name"] for r in results]
        assert "python3" in names
        assert "oc launcher" in names
        assert "codex auth" in names
        assert "ssh config" in names
        assert len(results) == 16  # 15 checks + ssh config


class TestRemoteChecks:
    @patch("oneshot_cli.doctor_cmd.subprocess.run")
    def test_remote_checks_include_oc_launcher(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="opencode=OK 1.0\noc_launcher=OK /home/test/.local/bin/oc\ngemini_auth=AUTH_REQUIRED\n",
            stderr="",
        )

        results = run_remote_checks("oci-ts", ["oci-ts", "macmini-ts"])
        names = [r["name"] for r in results]

        assert "oc launcher" in names
        assert "worktree path" not in names
        assert "repo path" not in names


# ── Autofix ──


class TestAutofix:
    def test_no_fix_when_all_ok(self):
        results = [{"name": "python3", "status": OK, "detail": ""}]
        fixes = autofix(results)
        assert fixes == []

    def test_creates_worktree_dir(self, tmp_path):
        wt = tmp_path / "oneshot-worktrees"
        with (
            patch("oneshot_cli.doctor_cmd.Path.cwd", return_value=tmp_path / "repo"),
            patch("oneshot_cli.doctor_cmd.platform.system", return_value="Linux"),
        ):
            results = [{"name": "worktree path", "status": MISSING, "detail": str(wt)}]
            autofix(results)
            assert wt.exists()

    def test_creates_repo_dir(self, tmp_path):
        tasks = tmp_path / "repo" / ".oneshot" / "tasks"
        with (
            patch("oneshot_cli.doctor_cmd.Path.cwd", return_value=tmp_path / "repo"),
            patch("oneshot_cli.doctor_cmd.platform.system", return_value="Linux"),
        ):
            results = [{"name": "repo path", "status": MISSING, "detail": str(tasks)}]
            autofix(results)
            assert tasks.exists()

    def test_symlinks_secrets(self, tmp_path):
        local_bin = tmp_path / ".local" / "bin"
        secrets_src = tmp_path / "github" / "oneshot" / "scripts" / "secrets"
        secrets_src.parent.mkdir(parents=True)
        secrets_src.write_text("#!/bin/bash\necho hi")
        with (
            patch("oneshot_cli.doctor_cmd.Path.home", return_value=tmp_path),
            patch("oneshot_cli.doctor_cmd.platform.system", return_value="Linux"),
        ):
            results = [{"name": "secrets cli", "status": MISSING, "detail": ""}]
            autofix(results)
            assert (local_bin / "secrets").exists()
            assert (local_bin / "secrets").is_symlink()

    def test_symlinks_oc_launcher(self, tmp_path):
        local_bin = tmp_path / ".local" / "bin"
        launcher_src = tmp_path / "github" / "oneshot" / "scripts" / "oc"
        launcher_src.parent.mkdir(parents=True)
        launcher_src.write_text("#!/usr/bin/env bash\n")
        with (
            patch("oneshot_cli.doctor_cmd.Path.home", return_value=tmp_path),
            patch("oneshot_cli.doctor_cmd.platform.system", return_value="Linux"),
        ):
            results = [{"name": "oc launcher", "status": MISSING, "detail": ""}]
            autofix(results)
            assert (local_bin / "oc").exists()
            assert (local_bin / "oc").is_symlink()


class TestRemoteFixInstructions:
    def test_no_fix_instructions_when_all_ok(self):
        assert (
            remote_fix_instructions(
                "oci", [{"name": "python3", "status": OK, "detail": "3.12"}]
            )
            == []
        )

    def test_instructions_include_host_and_failed_checks(self):
        fixes = remote_fix_instructions(
            "oci",
            [
                {"name": "python3", "status": OK, "detail": "3.12"},
                {"name": "gemini auth", "status": AUTH_REQUIRED, "detail": ""},
                {"name": "oc launcher", "status": MISSING, "detail": ""},
            ],
        )
        joined = "\n".join(fixes)
        assert "Remote autofix not supported" in joined
        assert "oci" in joined
        assert "gemini auth, oc launcher" in joined


# ── Machine detection ──


class TestDetectLocalMachine:
    def test_returns_none_when_no_match(self):
        machines = {
            "other": {"host": "other-ts", "enabled": True},
        }
        with (
            patch(
                "oneshot_cli.doctor_cmd.socket.gethostname", return_value="weird-host"
            ),
            patch(
                "oneshot_cli.doctor_cmd.subprocess.run",
                return_value=MagicMock(returncode=0, stderr="", stdout="ok"),
            ),
        ):
            result = detect_local_machine(machines)
            assert result is None or result == "other"

    def test_skips_disabled(self):
        machines = {
            "disabled": {"host": "disabled-ts", "enabled": False},
        }
        with patch(
            "oneshot_cli.doctor_cmd.socket.gethostname", return_value="disabled"
        ):
            result = detect_local_machine(machines)
            assert result is None
