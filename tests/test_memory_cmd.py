"""Tests for repo-first memory commands."""

from pathlib import Path
import sys

from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from oneshot_cli.__main__ import cli
from oneshot_cli import memory


def test_memory_scaffold_creates_expected_layout(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(cli, ["memory", "scaffold"])

    assert result.exit_code == 0
    assert (tmp_path / "docs" / "agents" / "MEMORY_POLICY.md").exists()
    assert (tmp_path / "docs" / "agents" / "DECISIONS.md").exists()
    assert (tmp_path / ".oneshot" / "sessions").is_dir()
    assert (tmp_path / ".oneshot" / "abstractions").is_dir()


def test_memory_policy_defaults_to_isolated(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    memory.scaffold()

    policy = (tmp_path / "docs" / "agents" / "MEMORY_POLICY.md").read_text()

    assert "- mode: isolated" in policy
    assert "- allow_raw_cross_repo_retrieval: false" in policy


def test_promote_decision_writes_decision_and_provenance(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    memory.scaffold()

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "memory",
            "promote",
            "decision",
            "--title",
            "Adopt repo memory",
            "--summary",
            "Use docs/agents for stable memory.",
            "--rationale",
            "Keeps project truth in the repo.",
        ],
    )

    assert result.exit_code == 0
    decisions = (tmp_path / "docs" / "agents" / "DECISIONS.md").read_text()
    assert "Adopt repo memory" in decisions
    assert "Keeps project truth in the repo." in decisions
    provenance_files = list((tmp_path / ".oneshot" / "provenance").glob("*.md"))
    assert len(provenance_files) == 1


def test_promote_session_stays_in_operational_memory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    memory.scaffold()

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "memory",
            "promote",
            "session",
            "--title",
            "Planning pass",
            "--summary",
            "Covered memory architecture and repo policy.",
        ],
    )

    assert result.exit_code == 0
    session_files = list((tmp_path / ".oneshot" / "sessions").glob("*.md"))
    assert len(session_files) == 1
    assert "Planning pass" in session_files[0].read_text()
    assert (
        "Planning pass"
        not in (tmp_path / "docs" / "agents" / "DECISIONS.md").read_text()
    )


def test_retrieve_prefers_active_decision_over_superseded(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    memory.scaffold()
    decisions = tmp_path / "docs" / "agents" / "DECISIONS.md"
    decisions.write_text(
        "# Decisions\n\n"
        "## 2026-04-28 - Use repo memory\n"
        "- status: active\n"
        "- summary: repo memory is canonical\n\n"
        "## 2026-04-27 - Legacy memory\n"
        "- status: superseded\n"
        "- summary: repo memory is canonical\n"
    )

    results = memory.retrieve_same_repo(tmp_path, "canonical", limit=5)

    assert len(results) >= 2
    assert results[0].title == "2026-04-28 - Use repo memory"
    assert results[1].superseded is True


def test_abstract_writes_abstraction_record(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    memory.scaffold()

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "memory",
            "abstract",
            "--title",
            "Runbooks are portable",
            "--lesson",
            "Prefer portable runbook abstractions over repo-local command dumps.",
            "--category",
            "runbook",
        ],
    )

    assert result.exit_code == 0
    files = list((tmp_path / ".oneshot" / "abstractions").glob("*.md"))
    assert len(files) == 1
    abstraction = files[0].read_text()
    assert "Runbooks are portable" in abstraction
    assert "Prefer portable runbook abstractions" in abstraction


def test_index_and_cross_repo_search_returns_abstractions(tmp_path, monkeypatch):
    repo_a = tmp_path / "repo-a"
    repo_b = tmp_path / "repo-b"
    repo_a.mkdir()
    repo_b.mkdir()
    monkeypatch.setenv("ONESHOT_MEMORY_INDEX_ROOT", str(tmp_path / "global-index"))

    memory.scaffold(repo_a, mode="portable")
    memory.scaffold(repo_b, mode="portable")
    memory.create_abstraction(
        repo_a,
        title="Portable runbook pattern",
        lesson="Prefer abstractions before raw foreign memory.",
        category="runbook",
        trust="high",
        sensitivity="portable",
    )
    memory.index_repo_memory(repo_a)
    memory.index_repo_memory(repo_b)

    results = memory.search_cross_repo_abstractions(
        "foreign memory", current_repo=repo_b, limit=5
    )

    assert results["status"] == "ok"
    assert len(results["results"]) == 1
    assert results["results"][0]["repo_name"] == "repo-a"
    assert "Portable runbook pattern" in results["results"][0]["title"]


def test_search_degraded_mode_is_explicit(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    memory.scaffold()

    def boom():
        raise RuntimeError("index unavailable")

    monkeypatch.setattr(memory, "_connect_index", boom)

    runner = CliRunner()
    result = runner.invoke(cli, ["memory", "search", "anything"])

    assert result.exit_code == 0
    assert "degraded mode" in result.output
    assert "index unavailable" in result.output
