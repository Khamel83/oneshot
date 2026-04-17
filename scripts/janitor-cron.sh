#!/bin/bash
# Janitor cron — periodic background intelligence for ALL OneShot-enabled projects.
#
# Scans ~/github/ for repos with .janitor/ directories and runs analysis on each.
# The janitor code lives in oneshot; all imports reference it directly.
#
# INSTALL: Already installed via systemd user unit (oneshot-janitor.timer)
# MANUAL: bash scripts/janitor-cron.sh

set -euo pipefail

# Ensure user-local bins are on PATH (cron/launchd start with minimal PATH).
# Without this, `secrets` is not found and the LLM enrichment is silently skipped.
export PATH="${HOME}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"

ONESHOT_DIR="${HOME}/github/oneshot"
REPO_BASE="${HOME}/github"
export OPENROUTER_API_KEY="$(secrets get OPENROUTER_API_KEY 2>/dev/null)" || true

# Collect all repos with .janitor/ directories
PROJECTS=()
for dir in "$REPO_BASE"/*/; do
  [ -d "${dir}.janitor" ] && PROJECTS+=("$(cd "$dir" && pwd)")
done

if [ ${#PROJECTS[@]} -eq 0 ]; then
  exit 0
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

for project_dir in "${PROJECTS[@]}"; do
  project_name=$(basename "$project_dir")
  JANITOR_DIR="${project_dir}/.janitor"
  JANITOR_LOG="${JANITOR_DIR}/cron-runs.log"
  mkdir -p "$JANITOR_DIR"

  log() {
    echo "[$TIMESTAMP] $*" >> "$JANITOR_LOG"
  }

  log "--- Janitor cron start ---"

  # Pure-compute jobs + write results (no LLM needed)
  python3 -c "
import sys, os
sys.path.insert(0, '$ONESHOT_DIR')
try:
    from core.janitor.jobs import run_session_start
    result = run_session_start(project_dir='$project_dir')
    print('Pure-compute jobs completed' + (f': {result[:100]}' if result else ' (nothing to report)'))
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
" 2>&1 | while read line; do
    log "  $line"
  done

  # Onboarding generation (needs LLM via openrouter/free)
  if [ -f "${JANITOR_DIR}/events.jsonl" ]; then
    if [ -n "$OPENROUTER_API_KEY" ]; then
      python3 -c "
import sys, os
sys.path.insert(0, '$ONESHOT_DIR')
try:
    from core.janitor.jobs import generate_onboarding
    result = generate_onboarding(project_dir='$project_dir')
    status = result.get('status', '') if isinstance(result, dict) else ''
    if status == 'fresh':
        print('Onboarding fresh (no regeneration needed)')
    elif status == 'no_data':
        print('Onboarding skipped (no data)')
    else:
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
done
