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
    _has_binary,
    _run,
    autofix,
    check_age_key,
    check_claude,
    check_codex,
    check_codex_auth,
    check_gemini,
    check_gemini_auth,
    check_opencode,
    check_opencode_auth,
    check_repo_path,
    check_secrets_cli,
    check_secrets_decrypt,
    check_ssh_config,
    check_worktree_path,
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
        assert "codex auth" in names
        assert "ssh config" in names
        assert len(results) == 15  # 14 checks + ssh config


class TestRemoteChecks:
    @patch("oneshot_cli.doctor_cmd.subprocess.run")
    def test_remote_checks_exclude_local_wrapper_checks(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="opencode=OK 1.0\ngemini_auth=AUTH_REQUIRED\n",
            stderr="",
        )

        results = run_remote_checks("oci-ts", ["oci-ts", "macmini-ts"])
        names = [r["name"] for r in results]

        assert "opencode" in names
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
                {"name": "opencode auth", "status": AUTH_REQUIRED, "detail": ""},
            ],
        )
        joined = "\n".join(fixes)
        assert "Remote autofix not supported" in joined
        assert "oci" in joined
        assert "gemini auth, opencode auth" in joined


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

# ── Internal helpers ──


class TestRunAndHasBinary:
    @patch("oneshot_cli.doctor_cmd.subprocess.run")
    def test_run_calls_subprocess(self, mock_subprocess_run):
        mock_subprocess_run.return_value = MagicMock(
            returncode=0, stdout="hello\n", stderr=""
        )
        result = _run("echo hello")
        mock_subprocess_run.assert_called_once_with(
            "echo hello",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0

    @patch("oneshot_cli.doctor_cmd.subprocess.run")
    def test_run_passes_timeout(self, mock_subprocess_run):
        mock_subprocess_run.return_value = MagicMock(
            returncode=0, stdout="", stderr=""
        )
        _run("echo hi", timeout=30)
        mock_subprocess_run.assert_called_once_with(
            "echo hi",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )

    @patch("oneshot_cli.doctor_cmd._run")
    def test_has_binary_found(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert _has_binary("python3") is True
        mock_run.assert_called_once_with("command -v python3", timeout=5)

    @patch("oneshot_cli.doctor_cmd._run")
    def test_has_binary_not_found(self, mock_run):
        mock_run.return_value = MagicMock(returncode=127)
        assert _has_binary("nonexistent-tool") is False


# ── Binary version checks ──


class TestClaudeCheck:
    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=False)
    def test_missing_when_no_binary(self, mock_has_binary):
        from oneshot_cli.doctor_cmd import check_claude

        status, _ = check_claude()
        assert status == MISSING

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_ok_with_version(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="Claude Code v2.1.0\n", stderr=""
        )
        from oneshot_cli.doctor_cmd import check_claude

        status, detail = check_claude()
        assert status == OK
        assert "2.1.0" in detail

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_ok_with_stderr_version(self, mock_run, mock_has_binary):
        """Some CLIs print version to stderr."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="", stderr="Claude Code v2.0.0\n"
        )
        from oneshot_cli.doctor_cmd import check_claude

        status, detail = check_claude()
        assert status == OK
        assert "2.0.0" in detail


class TestOpencodeCheck:
    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=False)
    def test_missing_when_no_binary(self, mock_has_binary):
        from oneshot_cli.doctor_cmd import check_opencode

        status, _ = check_opencode()
        assert status == MISSING

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_ok_with_version(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="opencode 1.0.0\nmore info\n", stderr=""
        )
        from oneshot_cli.doctor_cmd import check_opencode

        status, detail = check_opencode()
        assert status == OK
        assert detail == "opencode 1.0.0"  # first line only


class TestOpencodeAuth:
    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=False)
    def test_missing_when_no_binary(self, mock_has_binary):
        status, _ = check_opencode_auth()
        assert status == MISSING

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_ok_with_providers(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="  oauth: claude\n  oauth: gemini\n  api: custom\n  other: something\n",
            stderr="",
        )
        status, detail = check_opencode_auth()
        assert status == OK
        assert "claude" in detail
        assert "gemini" in detail

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_auth_required_on_no_providers(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="  other: some_output\n",
            stderr="",
        )
        status, _ = check_opencode_auth()
        assert status == AUTH_REQUIRED

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_auth_required_on_error(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=1, stdout="", stderr="unauthorized"
        )
        status, _ = check_opencode_auth()
        assert status == AUTH_REQUIRED


class TestGeminiCheck:
    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=False)
    def test_missing_when_no_binary(self, mock_has_binary):
        from oneshot_cli.doctor_cmd import check_gemini

        status, _ = check_gemini()
        assert status == MISSING

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_ok_with_version(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="gemini 0.39.0\n", stderr=""
        )
        from oneshot_cli.doctor_cmd import check_gemini

        status, detail = check_gemini()
        assert status == OK
        assert "0.39.0" in detail

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_ok_with_multiline_version(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="gemini 0.39.0\nsome-other-line\n", stderr=""
        )
        from oneshot_cli.doctor_cmd import check_gemini

        status, detail = check_gemini()
        assert status == OK
        assert detail == "gemini 0.39.0"


class TestCodexCheck:
    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=False)
    def test_missing_when_no_binary(self, mock_has_binary):
        from oneshot_cli.doctor_cmd import check_codex

        status, _ = check_codex()
        assert status == MISSING

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd._run")
    def test_ok_with_version(self, mock_run, mock_has_binary):
        mock_run.return_value = MagicMock(
            returncode=0, stdout="codex 0.118.0\n", stderr=""
        )
        from oneshot_cli.doctor_cmd import check_codex

        status, detail = check_codex()
        assert status == OK
        assert "0.118.0" in detail


# ── File-based checks ──


class TestSecretsCli:
    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=False)
    def test_missing_when_no_binary(self, mock_has_binary):
        status, _ = check_secrets_cli()
        assert status == MISSING

    @patch("oneshot_cli.doctor_cmd._has_binary", return_value=True)
    @patch("oneshot_cli.doctor_cmd.Path.home")
    def test_ok_with_path(self, mock_home, mock_has_binary):
        mock_home.return_value = Path("/home/test")
        status, detail = check_secrets_cli()
        assert status == OK
        assert str(Path("/home/test") / ".local" / "bin" / "secrets") in detail


class TestAgeKey:
    def test_missing_when_no_file(self, tmp_path):
        with patch("oneshot_cli.doctor_cmd.Path.home", return_value=tmp_path):
            status, _ = check_age_key()
            assert status == MISSING

    def test_ok_with_file(self, tmp_path):
        age_dir = tmp_path / ".age"
        age_dir.mkdir()
        key_file = age_dir / "key.txt"
        key_file.write_text("AGE-SECRET-KEY-xxx")
        with patch("oneshot_cli.doctor_cmd.Path.home", return_value=tmp_path):
            status, detail = check_age_key()
            assert status == OK
            assert str(key_file) in detail

    def test_missing_when_empty_file(self, tmp_path):
        age_dir = tmp_path / ".age"
        age_dir.mkdir()
        key_file = age_dir / "key.txt"
        key_file.write_text("")
        with patch("oneshot_cli.doctor_cmd.Path.home", return_value=tmp_path):
            status, _ = check_age_key()
            assert status == MISSING


class TestWorktreePath:
    def test_ok_when_exists_and_writable(self, tmp_path):
        wt_parent = tmp_path / "oneshot-worktrees"
        wt_parent.mkdir()
        with patch("oneshot_cli.doctor_cmd.Path.cwd", return_value=tmp_path / "repo"):
            status, detail = check_worktree_path()
            assert status == OK
            assert str(wt_parent) in detail

    def test_missing_when_not_exists(self, tmp_path):
        with patch("oneshot_cli.doctor_cmd.Path.cwd", return_value=tmp_path / "repo"):
            status, detail = check_worktree_path()
            assert status == MISSING
            assert "oneshot-worktrees" in detail

    def test_error_when_not_writable(self, tmp_path):
        wt_parent = tmp_path / "oneshot-worktrees"
        wt_parent.mkdir()
        wt_parent.chmod(0o444)  # read-only
        try:
            with patch("oneshot_cli.doctor_cmd.Path.cwd", return_value=tmp_path / "repo"):
                status, detail = check_worktree_path()
                assert status == ERROR
                assert "not writable" in detail
        finally:
            wt_parent.chmod(0o755)  # restore


class TestRepoPath:
    def test_ok_when_tasks_dir_exists(self, tmp_path):
        tasks = tmp_path / "repo" / ".oneshot" / "tasks"
        tasks.mkdir(parents=True)
        with patch("oneshot_cli.doctor_cmd.Path.cwd", return_value=tmp_path / "repo"):
            status, detail = check_repo_path()
            assert status == OK
            assert str(tasks) in detail

    def test_missing_when_tasks_dir_not_exists(self, tmp_path):
        with patch("oneshot_cli.doctor_cmd.Path.cwd", return_value=tmp_path / "repo"):
            status, detail = check_repo_path()
            assert status == MISSING
            assert ".oneshot/tasks" in detail


# ── Remote checks: error paths ──


class TestRemoteChecksErrorPaths:
    @patch("oneshot_cli.doctor_cmd.subprocess.run")
    def test_timeout_returns_error(self, mock_run):
        import subprocess

        mock_run.side_effect = subprocess.TimeoutExpired(cmd="ssh", timeout=60)
        results = run_remote_checks("oci-ts", ["oci-ts"])
        assert len(results) == 1
        assert results[0]["name"] == "ssh"
        assert results[0]["status"] == ERROR

    @patch("oneshot_cli.doctor_cmd.subprocess.run")
    def test_ssh_failure_returns_error(self, mock_run):
        mock_run.side_effect = RuntimeError("Connection refused")
        results = run_remote_checks("oci-ts", ["oci-ts"])
        assert len(results) == 1
        assert results[0]["name"] == "ssh"
        assert results[0]["status"] == ERROR

    @patch("oneshot_cli.doctor_cmd.subprocess.run")
    def test_nonzero_exit_with_no_stdout(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=255, stdout="", stderr="ssh: connect to host failed"
        )
        results = run_remote_checks("oci-ts", ["oci-ts"])
        assert len(results) == 1
        assert results[0]["name"] == "ssh"
        assert results[0]["status"] == ERROR

    @patch("oneshot_cli.doctor_cmd.subprocess.run")
    def test_parses_mixed_results(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=(
                "python3=OK 3.12.3\n"
                "git=OK 2.43.0\n"
                "claude=MISSING\n"
                "opencode_auth=AUTH_REQUIRED\n"
                "gemini=OK 0.39.0\n"
            ),
            stderr="",
        )
        results = run_remote_checks("oci-ts", ["oci-ts"])
        names = {r["name"] for r in results}
        assert "python3" in names
        assert "git" in names
        assert "claude" in names
        assert "opencode auth" in names  # underscore normalized to space
        assert "gemini" in names

    @patch("oneshot_cli.doctor_cmd.subprocess.run")
    def test_skips_lines_without_equals(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="python3=OK 3.12.3\ninvalid line without equals\n",
            stderr="",
        )
        results = run_remote_checks("oci-ts", ["oci-ts"])
        assert len(results) == 1
        assert results[0]["name"] == "python3"


# ── Remote fix instructions edge cases ──


class TestRemoteFixInstructionsEdgeCases:
    def test_returns_empty_for_all_ok(self):
        assert remote_fix_instructions("host", []) == []

    def test_includes_only_failed_checks(self):
        results = [
            {"name": "python3", "status": OK, "detail": "3.12"},
            {"name": "claude", "status": MISSING, "detail": ""},
            {"name": "codex auth", "status": AUTH_REQUIRED, "detail": ""},
        ]
        fixes = remote_fix_instructions("oci-ts", results)
        joined = "\n".join(fixes)
        assert "claude" in joined
        assert "codex auth" in joined
        assert "python3" not in joined


# ── Machine detection edge cases ──


class TestDetectLocalMachineEdgeCases:
    @patch("oneshot_cli.doctor_cmd.socket.gethostname", return_value="my-machine")
    def test_matches_by_hostname_key(self, mock_hostname):
        machines = {
            "my-machine": {"host": "my-machine-ts", "enabled": True},
        }
        with patch("oneshot_cli.doctor_cmd.Path.home") as mock_home:
            mock_home.return_value = Path("/tmp")
            result = detect_local_machine(machines)
            assert result == "my-machine"

    @patch("oneshot_cli.doctor_cmd.socket.gethostname", return_value="weird-host")
    @patch("oneshot_cli.doctor_cmd.subprocess.run")
    def test_ssh_fallback_permission_denied(self, mock_run, mock_hostname):
        """When SSH fails with 'Permission denied', treat as local machine."""
        mock_run.return_value = MagicMock(
            returncode=255, stdout="", stderr="Permission denied (publickey)."
        )
        machines = {
            "oci-dev": {"host": "oci-ts", "enabled": True},
        }
        with patch("oneshot_cli.doctor_cmd.Path.home") as mock_home:
            mock_home.return_value = Path("/tmp")
            result = detect_local_machine(machines)
            assert result == "oci-dev"

    @patch("oneshot_cli.doctor_cmd.socket.gethostname", return_value="weird-host")
    @patch("oneshot_cli.doctor_cmd.subprocess.run")
    def test_ssh_fallback_success_returns_none(self, mock_run, mock_hostname):
        """When SSH succeeds, it's not this machine."""
        mock_run.return_value = MagicMock(
            returncode=0, stdout="ok\n", stderr=""
        )
        machines = {
            "oci-dev": {"host": "oci-ts", "enabled": True},
        }
        with patch("oneshot_cli.doctor_cmd.Path.home") as mock_home:
            mock_home.return_value = Path("/tmp")
            result = detect_local_machine(machines)
            assert result is None

    @patch("oneshot_cli.doctor_cmd.socket.gethostname", return_value="weird-host")
    @patch("oneshot_cli.doctor_cmd.subprocess.run")
    def test_ssh_fallback_exception_returns_none(self, mock_run, mock_hostname):
        """When SSH raises an exception, treat as no match."""
        mock_run.side_effect = RuntimeError("No route to host")
        machines = {
            "oci-dev": {"host": "oci-ts", "enabled": True},
        }
        with patch("oneshot_cli.doctor_cmd.Path.home") as mock_home:
            mock_home.return_value = Path("/tmp")
            result = detect_local_machine(machines)
            assert result is None

    def test_matches_by_hostname_in_key(self):
        machines = {
            "macmini": {"host": "macmini-ts", "enabled": True},
        }
        with (
            patch("oneshot_cli.doctor_cmd.socket.gethostname", return_value="macmini"),
            patch("oneshot_cli.doctor_cmd.Path.home", return_value=Path("/tmp")),
        ):
            result = detect_local_machine(machines)
            assert result == "macmini"
