#!/bin/bash
# Janitor cron — periodic background intelligence for OneShot projects.
#
# Runs pure-compute analysis jobs on a schedule via systemd timer.
# Claude Code hooks still handle event recording and session-end tasks.
#
# Jobs run:
#   - detect_test_gaps: source files with no tests
#   - scan_code_smells: oversized files/functions
#   - detect_config_drift: uncommitted config changes
#   - build_dependency_map: import graph
#   - generate_onboarding: regenerate CLAUDE.local.md (if events exist)
#
# INSTALL: Already installed via systemd user unit (oneshot-janitor.timer)
# MANUAL: bash scripts/janitor-cron.sh

set -euo pipefail

REPO_BASE="${HOME}/github/oneshot"
JANITOR_DIR="${REPO_BASE}/.janitor"
JANITOR_LOG="${JANITOR_DIR}/cron-runs.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

log() {
  echo "[$TIMESTAMP] $*" >> "$JANITOR_LOG"
}

cd "$REPO_BASE" || { log "ERROR: Cannot cd to $REPO_BASE"; exit 1; }

mkdir -p "$JANITOR_DIR"

log "--- Janitor cron start ---"

# Pure-compute jobs (no LLM needed)
python3 -c "
import sys, os
sys.path.insert(0, os.getcwd())
try:
    from core.janitor.jobs import detect_test_gaps, scan_code_smells, detect_config_drift, build_dependency_map

    print('detect_test_gaps...')
    detect_test_gaps()
    print('scan_code_smells...')
    scan_code_smells()
    print('detect_config_drift...')
    detect_config_drift()
    print('build_dependency_map...')
    build_dependency_map()
    print('All pure-compute jobs completed')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
" 2>&1 | while read line; do
  log "  $line"
done

# Onboarding generation (lightweight, needs LLM for summarization)
if [ -f "${JANITOR_DIR}/events.jsonl" ]; then
  export OPENROUTER_API_KEY="$(secrets get OPENROUTER_API_KEY 2>/dev/null)" || true
  if [ -n "$OPENROUTER_API_KEY" ]; then
    python3 -c "
import sys, os
sys.path.insert(0, os.getcwd())
try:
    from core.janitor.jobs import generate_onboarding
    generate_onboarding()
    print('Onboarding updated')
except Exception as e:
    print(f'ONBOARDING_SKIP: {e}')
" 2>&1 | while read line; do
      log "  $line"
    done
  else
    log "  ONBOARDING_SKIP: No OPENROUTER_API_KEY available"
  fi
fi

log "--- Janitor cron end ---"
