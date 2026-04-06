#!/bin/bash
# Janitor cron — legacy fallback for background intelligence.
#
# DEPRECATED: Hooks now handle everything automatically:
#   - SessionStart: pure-compute jobs (test gaps, code smells, etc.)
#   - SessionEnd: LLM jobs (summarization, patterns, onboarding)
#   - PostToolUse: event recording
#   - PreCompact: pre-compaction summaries
#
# This script is kept as a safety net for projects that accumulated events
# but didn't get a clean SessionEnd (e.g., crash, force-kill).
#
# INSTALL (optional): crontab -e
#   */15 * * * * /home/ubuntu/github/oneshot/scripts/janitor-cron.sh >> /tmp/janitor-cron.log 2>&1

set -euo pipefail

REPO_BASE="${HOME}/github"
JANITOR_LOG="${REPO_BASE}/oneshot/.janitor/cron-runs.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

log() {
  echo "[$TIMESTAMP] $*" >> "$JANITOR_LOG"
}

# Find projects with .janitor/events.jsonl that have unprocessed events
find_projects() {
  find "$REPO_BASE" -maxdepth 3 -name "events.jsonl" -path "*/.janitor/*" 2>/dev/null | while read events_file; do
    project_dir=$(dirname "$(dirname "$events_file")")
    # Only process if no recent session_end marker (means SessionEnd hook didn't fire)
    if ! tail -20 "$events_file" 2>/dev/null | grep -q '"type":"session_end"'; then
      echo "$project_dir"
    fi
  done
}

process_project() {
  local project_dir="$1"
  local last_processed="$project_dir/.janitor/last-cron-processed"

  # Skip if processed within last 30 minutes
  if [ -f "$last_processed" ]; then
    last_time=$(stat -c %Y "$last_processed" 2>/dev/null || echo 0)
    now=$(date +%s)
    age=$((now - last_time))
    if [ "$age" -lt 1800 ]; then
      return 0
    fi
  fi

  log "Catching up: $project_dir (no clean session_end found)"
  cd "$project_dir" 2>/dev/null || return 0

  python3 -c "
import sys, os, time
from pathlib import Path
sys.path.insert(0, os.getcwd())
try:
    from core.janitor.jobs import run_session_end
    run_session_end('$project_dir')
    print('LLM jobs completed')
except ImportError as e:
    print(f'SKIP: {e}')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1 | while read line; do
    log "  $line"
  done

  # Mark processed
  echo "$TIMESTAMP" > "$last_processed"
}

# Main
log "--- Janitor cron start (fallback mode) ---"

projects=$(find_projects)
if [ -z "$projects" ]; then
  log "All projects have clean session_end markers — nothing to do"
else
  for project in $projects; do
    process_project "$project"
  done
fi

log "--- Janitor cron end ---"
