#!/usr/bin/env bash
# ONE-SHOT Heartbeat - Auto-updating health system
# Usage: ./heartbeat.sh [--force] [--quiet] [--background]
#
# Auto-actions (once per day):
#   1. ONE-SHOT: Auto git pull from origin
#   2. GLM Model: Auto-update models.env and shell config
#   3. Secrets: Sync and verify decryptability
#   4. Checks: CLIs, API keys, MCPs, connections
#   5. Beads: Sync health data

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/state.sh"

# Source environment for API keys check
if [[ -z "${ZAI_API_KEY:-}" ]]; then
  if [[ -f "$HOME/.bashrc" ]]; then
    eval "$(grep "^ZAI_API_KEY=" "$HOME/.bashrc" 2>/dev/null | head -1)"
  fi
fi

# Parse arguments
QUIET=""
FORCE=""
BACKGROUND=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quiet|-q) QUIET="--quiet" ;;
    --force|-f) FORCE="--force" ;;
    --background|-b) BACKGROUND="--background" ;;
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
  if [[ -f "$script" ]]; then
    if "$script" "${QUIET:-}"; then
      RESULTS+=("✓ $name")
    else
      RESULTS+=("⚠️  $name")
    fi
  else
    RESULTS+=("⊘ $name (not found)")
  fi
}

# 1. Update ONE-SHOT repo first (pulls latest scripts/secrets)
check "ONE-SHOT" "$SCRIPT_DIR/check-oneshot.sh"

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
