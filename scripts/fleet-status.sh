#!/usr/bin/env bash
# ONE-SHOT Fleet Status - Check all machines
# Usage: ./fleet-status.sh [--fix]

set -euo pipefail

MACHINES=(
  "homelab:khamel83@100.112.130.100"
  "macmini:macmini@100.113.216.27"
  "oci:ubuntu@100.126.13.70"
)

# Detect if we're on a machine (skip SSH to self)
CURRENT_HOST=$(hostname)

FIX_MODE="${1:-}"

check_machine() {
  local name="$1"
  local target="$2"

  echo "=== $name ==="

  # Skip if we're on this machine
  if [[ "$name" == "oci" && "$CURRENT_HOST" == "instance-first" ]]; then
    echo "  ℹ️  (this machine)"
    claude --version 2>/dev/null || echo "  ⚠️  Claude: not in PATH"
    echo ""
    return 0
  fi

  # Check SSH connectivity
  if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$target" "echo ok" >/dev/null 2>&1; then
    echo "  ✗ SSH: unreachable"
    return 1
  fi
  echo "  ✓ SSH: connected"

  # Check Claude Code version (handles nvm, npm-global, and standard paths)
  local claude_ver
  claude_ver=$(ssh "$target" '
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
    export PATH="$HOME/.npm-global/bin:$PATH"
    claude --version 2>/dev/null || echo "not installed"
  ')
  if [[ "$claude_ver" == *"2.1"* ]]; then
    echo "  ✓ Claude: $claude_ver"
  else
    echo "  ⚠️  Claude: $claude_ver"
    if [[ "$FIX_MODE" == "--fix" ]]; then
      echo "     → Installing Claude Code..."
      ssh "$target" '
        export NVM_DIR="$HOME/.nvm"
        [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
        npm install -g @anthropic-ai/claude-code 2>&1 | tail -2
      '
    fi
  fi

  # Check oneshot repo
  local oneshot_status
  oneshot_status=$(ssh "$target" 'cd ~/github/oneshot 2>/dev/null && git fetch --quiet && git status -sb | head -1' 2>/dev/null || echo "not cloned")
  if [[ "$oneshot_status" == *"behind"* ]]; then
    echo "  ⚠️  oneshot: needs pull"
    if [[ "$FIX_MODE" == "--fix" ]]; then
      ssh "$target" 'cd ~/github/oneshot && git pull'
    fi
  elif [[ "$oneshot_status" == "not cloned" ]]; then
    echo "  ✗ oneshot: not cloned"
  else
    echo "  ✓ oneshot: up to date"
  fi

  # Check GLM model (portable grep without -P)
  local glm_ver
  glm_ver=$(ssh "$target" 'grep -o "glm-[0-9.]*" ~/.bashrc ~/.zshrc 2>/dev/null | head -1 | cut -d: -f2' || echo "not set")
  echo "  ℹ️  GLM: ${glm_ver:-not configured}"

  echo ""
}

echo "ONE-SHOT Fleet Status ($(date +%Y-%m-%d))"
echo "==========================================="
echo ""

for machine in "${MACHINES[@]}"; do
  name="${machine%%:*}"
  target="${machine#*:}"
  check_machine "$name" "$target" || true
done

echo "Run with --fix to auto-repair issues"
