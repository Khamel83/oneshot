"""Standalone cron entrypoint for the janitor.

Runs background intelligence jobs on a schedule, independent of Claude Code sessions.
Install with: bash scripts/install-janitor-cron.sh

Usage:
    python -m core.janitor.cron [--once] [--verbose] [--project-dir PATH]

Job schedule (all gates are based on last-run timestamps in .janitor/cron-state.json):
  Every run  (~hourly): pure-compute signals + provider health
  Hourly:               trace analysis (if new traces since last run)
  Daily:                session summarize, mine patterns, generate onboarding
  Weekly:               improvement suggestions (requires >= 20 traces)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_project_dir(start: str) -> str:
    p = Path(start)
    for candidate in [p] + list(p.parents):
        if (candidate / ".git").exists():
            return str(candidate)
    return start


def _janitor_dir(project_dir: str) -> Path:
    d = Path(project_dir) / ".janitor"
    d.mkdir(exist_ok=True)
    return d


def _cron_state(project_dir: str) -> dict:
    path = _janitor_dir(project_dir) / "cron-state.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _save_cron_state(project_dir: str, state: dict):
    path = _janitor_dir(project_dir) / "cron-state.json"
    try:
        path.write_text(json.dumps(state, indent=2))
    except OSError:
        pass


def _should_run(job_name: str, interval_seconds: int, state: dict) -> bool:
    last = state.get(job_name, 0)
    return (time.time() - last) >= interval_seconds


def _mark_ran(job_name: str, state: dict):
    state[job_name] = time.time()


def _log(msg: str, verbose: bool = False):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    return line


def _append_cron_log(project_dir: str, msg: str):
    log_path = _janitor_dir(project_dir) / "cron-runs.log"
    try:
        with open(log_path, "a") as f:
            f.write(msg + "\n")
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Job runners
# ---------------------------------------------------------------------------

def _run_pure_compute(project_dir: str, verbose: bool) -> list[str]:
    """Run all zero-cost pure-compute jobs. Always runs every cron tick."""
    from core.janitor import jobs

    results = []
    for fn_name, write_key, describe in [
        ("detect_test_gaps",      "test-gaps.json",       "test gaps"),
        ("scan_code_smells",      "code-smells.json",     "code smells"),
        ("detect_config_drift",   "config-drift.json",    "config drift"),
        ("build_dependency_map",  "dep-graph.json",       "dep graph"),
        ("detect_recent_focus",   "recent-focus.json",    "recent focus"),
        ("detect_unresolved_blockers", "blockers.json",   "blockers"),
        ("detect_critical_files", "critical-files.json",  "critical files"),
    ]:
        try:
            fn = getattr(jobs, fn_name)
            result = fn(project_dir)
            if write_key:
                (Path(project_dir) / ".janitor" / write_key).write_text(
                    json.dumps(result, indent=2)
                )
            if verbose:
                _log(f"  {describe}: ok", verbose)
            results.append(describe)
        except Exception as e:
            if verbose:
                _log(f"  {describe}: error — {e}", verbose)
    return results


def _run_trace_analysis(project_dir: str, verbose: bool) -> str:
    """Analyze dispatch traces if new ones exist since last run."""
    from core.janitor.jobs import analyze_dispatch_traces

    traces_root = Path(project_dir) / "eval" / "traces"
    if not traces_root.exists():
        return "skip (no traces dir)"

    try:
        result = analyze_dispatch_traces(project_dir)
        n = result.get("traces_analyzed", 0)
        if result.get("status") == "no_traces":
            return "skip (no traces yet)"
        return f"ok ({n} traces)"
    except Exception as e:
        return f"error: {e}"


def _run_provider_health(project_dir: str, verbose: bool) -> str:
    from core.janitor.jobs import monitor_provider_health
    try:
        result = monitor_provider_health(project_dir)
        avail = result.get("available_count", 0)
        total = len(result.get("providers", {}))
        return f"ok ({avail}/{total} providers available)"
    except Exception as e:
        return f"error: {e}"


def _run_daily_llm_jobs(project_dir: str, verbose: bool) -> list[str]:
    """Run daily LLM jobs: summarize, patterns, onboarding."""
    from core.janitor.jobs import summarize_session, mine_patterns, generate_onboarding
    from core.janitor.jobs import _write_json, _janitor_dir as jdir

    results = []

    # summarize_session
    try:
        summary = summarize_session(project_dir)
        if summary.get("decisions") or summary.get("blockers"):
            (jdir(project_dir) / "last-summary.json").write_text(
                json.dumps(summary, indent=2)
            )
        results.append(f"summarize: ok ({len(summary.get('decisions', []))} decisions)")
    except Exception as e:
        results.append(f"summarize: error — {e}")

    # mine_patterns
    try:
        patterns = mine_patterns(project_dir)
        if patterns.get("patterns"):
            _write_json("patterns.json", patterns, project_dir)
        results.append(f"patterns: ok ({len(patterns.get('patterns', []))} found)")
    except Exception as e:
        results.append(f"patterns: error — {e}")

    # generate_onboarding
    try:
        onb = generate_onboarding(project_dir)
        results.append(f"onboarding: {onb.get('status', 'ok')}")
    except Exception as e:
        results.append(f"onboarding: error — {e}")

    return results


def _run_weekly_suggestions(project_dir: str, verbose: bool) -> str:
    """Generate improvement suggestions from trace stats."""
    from core.janitor.jobs import generate_improvement_suggestions
    try:
        result = generate_improvement_suggestions(project_dir)
        if result.get("status") in ("no_stats", "insufficient_data", "no_rows"):
            return f"skip ({result.get('status')}: {result.get('message', '')})"
        n = len(result.get("suggestions", []))
        return f"ok ({n} suggestions written to .janitor/suggestions.json)"
    except Exception as e:
        return f"error: {e}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

HOUR = 3600
DAY = 86400
WEEK = 86400 * 7


def run_once(project_dir: str, verbose: bool = False) -> dict:
    """Execute one full cron pass. Returns a summary of what ran."""
    state = _cron_state(project_dir)
    summary = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "project_dir": project_dir,
        "ran": [],
        "skipped": [],
    }

    # 1. Pure-compute jobs — always run
    if verbose:
        _log("Running pure-compute jobs...")
    ran = _run_pure_compute(project_dir, verbose)
    summary["ran"].extend(ran)
    _mark_ran("pure_compute", state)

    # 2. Provider health — always run
    ph_result = _run_provider_health(project_dir, verbose)
    if verbose:
        _log(f"Provider health: {ph_result}")
    summary["ran"].append(f"provider_health: {ph_result}")
    _mark_ran("provider_health", state)

    # 3. Trace analysis — hourly
    if _should_run("trace_analysis", HOUR, state):
        if verbose:
            _log("Running trace analysis...")
        ta_result = _run_trace_analysis(project_dir, verbose)
        if verbose:
            _log(f"Trace analysis: {ta_result}")
        summary["ran"].append(f"trace_analysis: {ta_result}")
        _mark_ran("trace_analysis", state)
    else:
        summary["skipped"].append("trace_analysis (< 1h since last run)")

    # Check if any LLM provider key is available
    has_llm_key = any([
        os.environ.get("OPENROUTER_API_KEY"),
        os.environ.get("QWEN_API_KEY"),
        os.environ.get("GEMINI_API_KEY"),
        os.environ.get("OPENAI_API_KEY"),
    ])

    if not has_llm_key:
        if verbose:
            _log("No LLM provider keys found — skipping LLM jobs")
        summary["skipped"].append("daily_llm (no provider keys)")
        summary["skipped"].append("weekly_suggestions (no provider keys)")
        _save_cron_state(project_dir, state)
        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        return summary

    # 4. Daily LLM jobs
    if _should_run("daily_llm", DAY, state):
        if verbose:
            _log("Running daily LLM jobs...")
        llm_results = _run_daily_llm_jobs(project_dir, verbose)
        for r in llm_results:
            if verbose:
                _log(f"  {r}")
        summary["ran"].extend(llm_results)
        _mark_ran("daily_llm", state)
    else:
        summary["skipped"].append("daily_llm (< 24h since last run)")

    # 5. Weekly suggestions
    if _should_run("weekly_suggestions", WEEK, state):
        if verbose:
            _log("Running improvement suggestion generation...")
        sugg_result = _run_weekly_suggestions(project_dir, verbose)
        if verbose:
            _log(f"Suggestions: {sugg_result}")
        summary["ran"].append(f"suggestions: {sugg_result}")
        _mark_ran("weekly_suggestions", state)
    else:
        summary["skipped"].append("weekly_suggestions (< 7d since last run)")

    _save_cron_state(project_dir, state)
    summary["finished_at"] = datetime.now(timezone.utc).isoformat()
    return summary


def main():
    parser = argparse.ArgumentParser(
        description="Janitor cron — continuous background intelligence for OneShot projects"
    )
    parser.add_argument("--once", action="store_true", help="Run one pass and exit (default)")
    parser.add_argument("--verbose", action="store_true", help="Print job-level progress")
    parser.add_argument(
        "--project-dir",
        default=None,
        help="Project root directory (default: auto-detect from CWD)",
    )
    args = parser.parse_args()

    start_dir = args.project_dir or os.getcwd()
    project_dir = _find_project_dir(start_dir)

    if not (Path(project_dir) / ".git").exists():
        print(f"[janitor/cron] No git repo found at or above {start_dir}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        _log(f"Starting janitor cron for {project_dir}")

    summary = run_once(project_dir, verbose=args.verbose)

    # Always log to cron-runs.log
    ts = summary.get("started_at", "?")
    ran_count = len(summary.get("ran", []))
    skipped_count = len(summary.get("skipped", []))
    log_line = f"{ts} ran={ran_count} skipped={skipped_count}"
    _append_cron_log(project_dir, log_line)

    if args.verbose:
        _log(f"Done: {ran_count} jobs ran, {skipped_count} skipped")
        for item in summary.get("ran", []):
            _log(f"  + {item}")
        for item in summary.get("skipped", []):
            _log(f"  - {item}")


if __name__ == "__main__":
    main()
