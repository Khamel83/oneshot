#!/usr/bin/env bash
# ONE-SHOT Heartbeat - Daily health check system
# Usage: ./heartbeat.sh [--force] [--quiet] [--background]
#
# Checks (once per day):
#   - GLM model version (Hugging Face API)
#   - CLI versions (Claude Code, Gemini, Qwen, Codex)
#   - API key validation (ZAI, Tavily, Exa, Apify, Context7)
#   - MCP server health
#   - SOPS/Age secrets
#   - Connections (Tailscale, internet)
#   - ONE-SHOT repo sync
#   - Beads sync

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/state.sh"

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

[[ -z "$QUIET" ]] && echo "Heartbeat: running daily health check..."

# Run all checks
RESULTS=()

# Check each component
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

check "GLM Model" "$SCRIPT_DIR/check-glm.sh"
check "CLI Versions" "$SCRIPT_DIR/check-clis.sh"
check "API Keys" "$SCRIPT_DIR/check-apis.sh"
check "MCP Servers" "$SCRIPT_DIR/check-mcps.sh"
check "Secrets" "$SCRIPT_DIR/check-secrets.sh"
check "Connections" "$SCRIPT_DIR/check-connections.sh"
check "ONE-SHOT" "$SCRIPT_DIR/check-oneshot.sh"

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

# Sync state to oneshot repo
state_sync_to_repo "${QUIET:-}"

exit 0
