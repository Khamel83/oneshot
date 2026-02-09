#!/usr/bin/env bash
# State management for ONE-SHOT heartbeat
# Hybrid storage: ~/.claude/state/ (machine) + CLAUDE.md (project)

set -euo pipefail

STATE_DIR="$HOME/.claude/state"
mkdir -p "$STATE_DIR"

# Get last check date from global state
state_get_last_check() {
  if [[ -f "$STATE_DIR/last-health-check" ]]; then
    cat "$STATE_DIR/last-health-check"
  else
    echo "never"
  fi
}

# Set last check date in global state
state_set_last_check() {
  local date="$1"
  echo "$date" > "$STATE_DIR/last-health-check"
}

# Update CLAUDE.md with heartbeat metadata
state_update_claude_md() {
  local date="$1"
  local claude_md="CLAUDE.md"

  if [[ ! -f "$claude_md" ]]; then
    return 0
  fi

  # Remove old heartbeat comments (portable: macOS compatible)
  sed -i.bak '/<!-- oneshot:/d' "$claude_md" 2>/dev/null || true
  rm -f "${claude_md}.bak"

  # Add new heartbeat metadata at end
  cat >> "$claude_md" << EOF

<!--
  ONE-SHOT Heartbeat Metadata
  oneshot:last-check: $date
  oneshot:machine: $(hostname)
-->
EOF
}

# Sync state to oneshot repo
state_sync_to_repo() {
  local quiet="${1:-}"
  local oneshot_dir="${ONESHOT_DIR:-$HOME/github/oneshot}"

  if [[ ! -d "$oneshot_dir" ]]; then
    return 0
  fi

  cd "$oneshot_dir"

  # Commit state changes if any
  if git diff --quiet .claude/state/ 2>/dev/null; then
    return 0  # No changes
  fi

  [[ -z "$quiet" ]] && echo "   Syncing heartbeat state to oneshot repo..."

  git add .claude/state/ 2>/dev/null || true
  git commit -m "chore: Update heartbeat state

- Auto-generated from daily health check
- Machine: $(hostname)
- Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" 2>/dev/null || true
}

# Export functions for use in other scripts
export -f state_get_last_check state_set_last_check state_update_claude_md state_sync_to_repo
