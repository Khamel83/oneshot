"""Janitor — free background intelligence for Claude Code sessions."""

from core.janitor.jobs import (
    run_session_start,
    run_session_end,
    detect_test_gaps,
    scan_code_smells,
    detect_config_drift,
    build_dependency_map,
)
from core.janitor.worker import call_free, extract_structured

__all__ = [
    "run_session_start",
    "run_session_end",
    "detect_test_gaps",
    "scan_code_smells",
    "detect_config_drift",
    "build_dependency_map",
    "call_free",
    "extract_structured",
]
