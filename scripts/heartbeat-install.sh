#!/usr/bin/env bash
# ONE_SHOT Heartbeat Installer
# Installs shell hooks for auto-heartbeat with rate limiting

set -euo pipefail

HEARTBEAT_LOG="${HEARTBEAT_LOG:-/tmp/heartbeat.log}"
ONESHOT_DIR="${ONESHOT_DIR:-$HOME/github/oneshot}"
HEARTBEAT_SCRIPT="$ONESHOT_DIR/scripts/heartbeat.sh"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}ONE_SHOT Heartbeat Installer${NC}"
echo "================================"
echo ""
echo "This will install heartbeat hooks that:"
echo "  - Run automatically when you cd into projects with CLAUDE.md"
echo "  - Rate limited to once per 23 hours"
echo "  - Log to $HEARTBEAT_LOG"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Cancelled."
  exit 0
fi

# Rate limiting function (23 hours = 82800 seconds)
oneshot_heartbeat_guarded() {
  # Only run in directories with CLAUDE.md
  [[ -f "CLAUDE.md" ]] || return 0

  # Check last run time
  local last_run_file="$HOME/.cache/oneshot-heartbeat-last"
  local now=$(date +%s)
  local last_run=0

  if [[ -f "$last_run_file" ]]; then
    last_run=$(cat "$last_run_file" 2>/dev/null || echo 0)
  fi

  # 23 hours = 82800 seconds
  local elapsed=$((now - last_run))
  if [[ $elapsed -lt 82800 ]]; then
    return 0  # Skip, ran recently
  fi

  # Update last run time
  mkdir -p "$HOME/.cache"
  echo "$now" > "$last_run_file"

  # Run heartbeat in background with logging
  if [[ -x "$HEARTBEAT_SCRIPT" ]]; then
    "$HEARTBEAT_SCRIPT" --safe >>"$HEARTBEAT_LOG" 2>&1 &
  fi
}

# Install bash hook
install_bash_hook() {
  local hook_code='
# ONE_SHOT Heartbeat
oneshot_heartbeat_guarded() {
  if [[ -f "CLAUDE.md" ]]; then
    local last_run_file="$HOME/.cache/oneshot-heartbeat-last"
    local now=$(date +%s)
    local last_run=$(cat "$last_run_file" 2>/dev/null || echo 0)
    if [[ $((now - last_run)) -gt 82800 ]]; then
      mkdir -p "$HOME/.cache"
      echo "$now" > "$last_run_file"
      "$HOME/github/oneshot/scripts/heartbeat.sh" --safe >>/tmp/heartbeat.log 2>&1 &
    fi
  fi
}
PROMPT_COMMAND="oneshot_heartbeat_guarded;$PROMPT_COMMAND"
'

  local bashrc="$HOME/.bashrc"
  local marker="# ONE_SHOT Heartbeat"

  # Backup .bashrc
  cp "$bashrc" "$bashrc.backup.$(date +%Y%m%d_%H%M%S)"

  # Remove old hook if exists
  if grep -q "$marker" "$bashrc" 2>/dev/null; then
    sed -i "/$marker/,/^PROMPT_COMMAND=\"oneshot_heartbeat_guarded/d" "$bashrc" 2>/dev/null || \
    perl -i -ne "print unless /$marker/../^PROMPT_COMMAND=\"oneshot_heartbeat_guarded/" "$bashrc"
  fi

  # Add new hook
  echo "" >> "$bashrc"
  echo "$marker" >> "$bashrc"
  echo "$hook_code" >> "$bashrc"

  echo -e "${GREEN}✓${NC} Bash hook installed to ~/.bashrc"
}

# Install zsh hook
install_zsh_hook() {
  local zshrc="$HOME/.zshrc"
  local marker="# ONE_SHOT Heartbeat"

  # Backup .zshrc
  cp "$zshrc" "$zshrc.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true

  # Remove old hook if exists
  if grep -q "$marker" "$zshrc" 2>/dev/null; then
    sed -i "/$marker/,/^oneshot_heartbeat_guarded/d" "$zshrc" 2>/dev/null || true
  fi

  # Add new hook (zsh uses chpwd function)
  cat >> "$zshrc" << 'EOF'

# ONE_SHOT Heartbeat
oneshot_heartbeat_guarded() {
  if [[ -f "CLAUDE.md" ]]; then
    local last_run_file="$HOME/.cache/oneshot-heartbeat-last"
    local now=$(date +%s)
    local last_run=$(cat "$last_run_file" 2>/dev/null || echo 0)
    if [[ $((now - last_run)) -gt 82800 ]]; then
      mkdir -p "$HOME/.cache"
      echo "$now" > "$last_run_file"
      "$HOME/github/oneshot/scripts/heartbeat.sh" --safe >>/tmp/heartbeat.log 2>&1 &
    fi
  fi
}
chpwd() { oneshot_heartbeat_guarded }
EOF

  echo -e "${GREEN}✓${NC} Zsh hook installed to ~/.zshrc"
}

# Main
if [[ -n "${BASH_VERSION:-}" ]]; then
  install_bash_hook
elif [[ -n "${ZSH_VERSION:-}" ]]; then
  install_zsh_hook
else
  echo -e "${YELLOW}⚠${NC} Unknown shell. Only bash and zsh are supported."
  exit 1
fi

# Create log file
touch "$HEARTBEAT_LOG"

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "The heartbeat will run:"
echo "  - When you cd into a directory with CLAUDE.md"
echo "  - At most once per 23 hours"
echo "  - In safe mode (no git pull)"
echo ""
echo "Log file: $HEARTBEAT_LOG"
echo ""
echo "To test immediately:"
echo "  source ~/.bashrc  # or ~/.zshrc"
echo "  cd ~/github/oneshot  # Should trigger heartbeat"
echo ""
