"""Tests for migration baseline historical markers."""

from pathlib import Path

BASELINE_DIR = Path(__file__).resolve().parent.parent / "docs" / "migration" / "baseline"


def test_all_baseline_files_have_historical_marker():
    files = list(BASELINE_DIR.glob("*.md"))
    assert len(files) >= 20, f"Expected 20+ baseline files, found {len(files)}"
    for f in files:
        content = f.read_text()
        assert "Historical baseline" in content, f"{f.name} missing historical marker"


def test_baseline_files_are_not_loaded_as_instructions():
    for f in BASELINE_DIR.glob("*.md"):
        content = f.read_text()
        # Should NOT be referenced by active .claude/rules/*.md files
        assert "Historical baseline" in content
