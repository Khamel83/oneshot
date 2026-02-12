#!/usr/bin/env bash
# ONE-SHOT Heartbeat - Auto-updating health system
# Usage: ./heartbeat.sh [--force] [--quiet] [--background] [--safe]
#
# Auto-actions (once per day):
#   1. ONE-SHOT: Check for updates (no pull unless --fix + --force)
#   2. GLM Model: Auto-update models.env and shell config
#   3. Secrets: Sync and verify decryptability
#   4. Checks: CLIs, API keys, MCPs, connections
#   5. Beads: Sync health data
#
# Options:
#   --safe: Skip check-oneshot (prevent cascade)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/state.sh"

# Source environment for API keys check
if [[ -z "${ZAI_API_KEY:-}" ]]; then
  if [[ -f "$HOME/.bashrc" ]]; then
    ZAI_API_KEY=$(grep "export ZAI_API_KEY=" "$HOME/.bashrc" 2>/dev/null | sed 's/^[[:space:]]*export ZAI_API_KEY=//' | head -1 | tr -d '"')
    export ZAI_API_KEY
  fi
fi

# Parse arguments
QUIET=""
FORCE=""
BACKGROUND=""
SAFE_MODE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quiet|-q) QUIET="--quiet" ;;
    --force|-f) FORCE="--force" ;;
    --background|-b) BACKGROUND="--background" ;;
    --safe|-s) SAFE_MODE="--safe" ;;
  esac
  shift
done

# Check if we should run today
TODAY=$(date +%Y-%m-%d)
LAST_CHECK=$(state_get_last_check)

if [[ "$FORCE" != "--force" ]] && [[ "$LAST_CHECK" == "$TODAY" ]]; then
  [[ -z "$QUIET" ]] && echo "Heartbeat: already checked today ($TODAY)"
  exit 0
fi

[[ -z "$QUIET" ]] && echo "Heartbeat: running daily auto-update..."

# Run auto-actions and checks
RESULTS=()

# Auto-actions first (in order)
check() {
  local name="$1"
  local script="$2"
  local fix_flag=""
  # Pass --fix to CLI check if in force mode (for auto-updates)
  [[ "$FORCE" == "--force" && "$script" == *"check-clis.sh" ]] && fix_flag="--fix"
  if [[ -f "$script" ]]; then
    if "$script" "${QUIET:-}" $fix_flag; then
      RESULTS+=("✓ $name")
    else
      RESULTS+=("⚠️  $name")
    fi
  else
    RESULTS+=("⊘ $name (not found)")
  fi
}

# 1. Check ONE-SHOT repo (skip in safe mode)
if [[ "$SAFE_MODE" == "--safe" ]]; then
  RESULTS+=("○ ONE-SHOT (safe mode, skipped)")
else
  check "ONE-SHOT" "$SCRIPT_DIR/check-oneshot.sh"
fi

# 2. Auto-update GLM model if newer version available
check "GLM Model" "$SCRIPT_DIR/check-glm.sh"

# 3. Sync and verify secrets
check "Secrets" "$SCRIPT_DIR/sync-secrets.sh"

# 4. Health checks (informational, can't auto-fix)
check "CLI Versions" "$SCRIPT_DIR/check-clis.sh"
check "API Keys" "$SCRIPT_DIR/check-apis.sh"
check "MCP Servers" "$SCRIPT_DIR/check-mcps.sh"
check "Connections" "$SCRIPT_DIR/check-connections.sh"

# Update state
state_set_last_check "$TODAY"

# Update project CLAUDE.md if in a project
if [[ -f "CLAUDE.md" ]]; then
  state_update_claude_md "$TODAY"
fi

# Sync to beads
if [[ -x "$SCRIPT_DIR/beads-sync.sh" ]]; then
  "$SCRIPT_DIR/beads-sync.sh" "${QUIET:-}" &
fi

# Output results
if [[ -z "$QUIET" ]]; then
  echo ""
  echo "Heartbeat Results:"
  for result in "${RESULTS[@]}"; do
    echo "   $result"
  done
  echo ""
fi

exit 0
