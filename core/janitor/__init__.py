"""Janitor — free background intelligence for Claude Code sessions.

Multi-provider pool: openrouter_free → qwen_studio → gemini_api → codex
Config: config/janitor_providers.yaml
"""

from core.janitor.jobs import (
    run_session_start,
    run_session_end,
    detect_test_gaps,
    scan_code_smells,
    detect_config_drift,
    build_dependency_map,
    evaluate_task_sufficiency,
    analyze_dispatch_traces,
    monitor_provider_health,
    generate_improvement_suggestions,
)
from core.janitor.worker import call_free, extract_structured, call_janitor, extract_structured_janitor

__all__ = [
    # Session hooks
    "run_session_start",
    "run_session_end",
    # Pure-compute jobs
    "detect_test_gaps",
    "scan_code_smells",
    "detect_config_drift",
    "build_dependency_map",
    "analyze_dispatch_traces",
    "monitor_provider_health",
    # LLM jobs
    "evaluate_task_sufficiency",
    "generate_improvement_suggestions",
    # Provider pool API
    "call_free",           # backwards-compatible shim
    "extract_structured",  # backwards-compatible shim
    "call_janitor",        # preferred new name
    "extract_structured_janitor",  # preferred new name
]
