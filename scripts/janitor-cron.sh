#!/bin/bash
# Janitor cron — runs background intelligence jobs across all projects.
# Designed to run from system crontab, independent of any Claude session.
#
# Handles the "I just quit" scenario:
# - Finds all projects with .oneshot/events.jsonl
# - Runs unprocessed events through the summarizer
# - Runs memory hygiene across all projects
# - Writes results back to .oneshot/
#
# INSTALL: crontab -e
#   */15 * * * * /home/ubuntu/github/oneshot/scripts/janitor-cron.sh >> /tmp/janitor-cron.log 2>&1
#
# Or run manually: ./scripts/janitor-cron.sh
#
# Rate budget: ~4-6 calls per run. At every 15 min = 96-192/day.
# Well within openrouter/free limits.

set -euo pipefail

REPO_BASE="${HOME}/github"
JANITOR_LOG="${REPO_BASE}/oneshot/.oneshot/cron-runs.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

log() {
  echo "[$TIMESTAMP] $*" >> "$JANITOR_LOG"
}

# Find all projects with .oneshot/events.jsonl that have unprocessed events
find_projects() {
  find "$REPO_BASE" -maxdepth 3 -name "events.jsonl" -path "*/.oneshot/*" 2>/dev/null | while read events_file; do
    project_dir=$(dirname "$(dirname "$events_file")")
    # Count lines — skip if empty or too small
    line_count=$(wc -l < "$events_file" | tr -d ' ')
    if [ "$line_count" -ge 3 ]; then
      echo "$project_dir"
    fi
  done
}

# Process a single project
process_project() {
  local project_dir="$1"
  local events_file="$project_dir/.oneshot/events.jsonl"
  local last_processed="$project_dir/.oneshot/last-processed"

  # Check if we already processed this file recently (within 10 minutes)
  if [ -f "$last_processed" ]; then
    last_time=$(stat -c %Y "$last_processed" 2>/dev/null || echo 0)
    now=$(date +%s)
    age=$((now - last_time))
    if [ "$age" -lt 600 ]; then
      return 0  # Processed within last 10 min, skip
    fi
  fi

  log "Processing: $project_dir"

  cd "$project_dir" 2>/dev/null || return 0

  python3 -c "
import sys, os
sys.path.insert(0, os.getcwd())
try:
    from core.janitor.recorder import SessionRecorder
    from core.janitor.jobs import summarize_recent_turns, memory_hygiene
    from core.janitor.worker import get_usage_stats

    # Get usage stats
    stats = get_usage_stats()
    print(f'Usage: {stats[\"today\"]}/1000 today, {stats[\"this_minute\"]}/20 this minute')

    # Summarize recent turns
    r = SessionRecorder()
    result = summarize_recent_turns(r, n=20)
    decisions = len(result.get('decisions', []))
    blockers = len(result.get('blockers', []))
    print(f'Extracted: {decisions} decisions, {blockers} blockers')

    # Mark as processed
    with open('.oneshot/last-processed', 'w') as f:
        f.write('$TIMESTAMP')

except ImportError:
    print(f'SKIP: core.janitor not importable in {os.getcwd()}')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1 | while read line; do
    log "  $line"
  done
}

# Run memory hygiene across all projects (once per run, not per project)
run_memory_hygiene() {
  log "Running memory hygiene"
  python3 -c "
import sys, os
sys.path.insert(0, os.path.expanduser('~/github/oneshot'))
try:
    from core.janitor.jobs import memory_hygiene
    result = memory_hygiene()
    overlaps = len(result.get('overlaps', []))
    print(f'Memory hygiene: {result.get(\"total_files\", 0)} files, {overlaps} overlaps')
except Exception as e:
    print(f'ERROR: {e}')
" 2>&1 | while read line; do
    log "  $line"
  done
}

# Main
log "--- Janitor cron start ---"
log "Rate limit: $(python3 -c "from core.janitor.worker import get_usage_stats; import json; print(json.dumps(get_usage_stats()))" 2>/dev/null || echo 'unavailable')"

# Find and process projects
projects=$(find_projects)
if [ -z "$projects" ]; then
  log "No projects with unprocessed events"
else
  for project in $projects; do
    process_project "$project"
  done
fi

# Memory hygiene (runs once per cron invocation)
run_memory_hygiene

log "--- Janitor cron end ---"
