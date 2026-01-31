#!/bin/bash
# claude-shell-setup.sh - Portable Claude Code + ZAI setup + Heartbeat integration
#
# USAGE:
#   1. Copy to new machine and edit the config values below
#   2. Run: bash claude-shell-setup.sh --install
#   3. Then: source ~/.bashrc (or source ~/.zshrc for zsh)
#
# COMMANDS AFTER INSTALL:
#   cc  - Claude Code via Anthropic Pro (assumes you're logged in)
#   zai - Claude Code via z.ai GLM API
#
# UPDATING GLM VERSION:
#   When z.ai releases a new model (e.g., glm-4.8), just update GLM_MODEL
#   in your ~/.bashrc or re-run this script with the new version.
#
# GET YOUR ZAI API KEY:
#   https://z.ai/devpack → Sign up → Copy API key

# ╔════════════════════════════════════════════════════════════════╗
# ║  EDIT THESE VALUES BEFORE RUNNING --install                    ║
# ╚════════════════════════════════════════════════════════════════╝
ZAI_API_KEY="YOUR_ZAI_API_KEY_HERE"
GLM_MODEL="glm-4.7"  # Update when z.ai releases new version
SHELL_TYPE="${SHELL_TYPE:-bash}"  # bash or zsh - auto-detected by --install
# ══════════════════════════════════════════════════════════════════

# Auto-detect shell type
if [[ -n "${ZSH_VERSION:-}" ]]; then
  SHELL_TYPE="zsh"
elif [[ -n "${BASH_VERSION:-}" ]]; then
  SHELL_TYPE="bash"
fi

# Handle --install flag
if [[ "$1" == "--install" ]]; then
    # Validate API key was set
    if [[ "$ZAI_API_KEY" == "YOUR_ZAI_API_KEY_HERE" ]]; then
        echo "ERROR: Edit this script and set your ZAI_API_KEY first!" >&2
        echo "Get your key at: https://z.ai/devpack" >&2
        exit 1
    fi

    # Auto-detect shell if not set
    if [[ -n "${ZSH_VERSION:-}" ]]; then
        SHELL_TYPE="zsh"
    elif [[ -n "${BASH_VERSION:-}" ]]; then
        SHELL_TYPE="bash"
    fi

    MARKER="##### Claude Code + ZAI shortcuts #####"
    if [[ "$SHELL_TYPE" == "zsh" ]]; then
        SHELLRC="$HOME/.zshrc"
    else
        SHELLRC="$HOME/.bashrc"
    fi

    # Remove old block if exists (handles variants like "(oci-dev)" suffix)
    if grep -q "##### Claude Code + ZAI shortcuts" "$SHELLRC" 2>/dev/null; then
        sed -i "/##### Claude Code + ZAI shortcuts/,/##### end Claude Code + ZAI shortcuts #####/d" "$SHELLRC"
        echo "Removed old Claude/ZAI block from $SHELLRC"
    fi

    # Remove old heartbeat block if exists (for migration)
    if grep -q "##### ONE-SHOT Heartbeat #####" "$SHELLRC" 2>/dev/null; then
        sed -i "/##### ONE-SHOT Heartbeat #####/,/##### end ONE-SHOT Heartbeat #####/d" "$SHELLRC"
        echo "Removed old Heartbeat block from $SHELLRC"
    fi

    # Append new block
    cat >> "$SHELLRC" << 'SHELLRC_BLOCK'

##### Claude Code + ZAI shortcuts #####
# Portable setup: github.com/Khamel83/oneshot/scripts/claude-shell-setup.sh
# To reinstall: bash claude-shell-setup.sh --install

ZAI_API_KEY="__ZAI_API_KEY__"
GLM_MODEL="__GLM_MODEL__"

unalias cc zai 2>/dev/null || true
unset -f cc zai 2>/dev/null || true

# cc - Claude Code via Anthropic Pro (YOLO mode)
cc() {
    claude --dangerously-skip-permissions "$@"
}

# zai - Claude Code via z.ai GLM API (YOLO mode)
zai() {
    if ! command -v claude >/dev/null 2>&1; then
        echo "zai: 'claude' CLI not found (npm install -g @anthropic-ai/claude-code)" >&2
        return 127
    fi
    [[ -z "$ZAI_API_KEY" ]] && { echo "zai: ZAI_API_KEY not set" >&2; return 1; }

    echo "zai: z.ai/$GLM_MODEL (YOLO mode)" >&2
    ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
    ANTHROPIC_AUTH_TOKEN="$ZAI_API_KEY" \
    ANTHROPIC_MODEL="$GLM_MODEL" \
        claude --dangerously-skip-permissions "$@"
}
##### end Claude Code + ZAI shortcuts #####

##### ONE-SHOT Heartbeat #####
# Daily health checks on project enter (cd to directory with CLAUDE.md)
# Run manually: bash ~/github/oneshot/scripts/heartbeat.sh [--force] [--quiet]

_oneshot_heartbeat() {
    local heartbeat_script="${ONESHOT_DIR:-$HOME/github/oneshot}/scripts/heartbeat.sh"
    if [[ -f "$PWD/CLAUDE.md" ]] && [[ -x "$heartbeat_script" ]]; then
        "$heartbeat_script" --quiet --background 2>/dev/null &
    fi
}

oneshot-dismiss() {
    local suppressed="$HOME/.claude/state/suppressed-warnings"
    mkdir -p "$(dirname "$suppressed")"
    echo "$1" >> "$suppressed"
    echo "Dismissed: $1"
}
##### end ONE-SHOT Heartbeat #####
SHELLRC_BLOCK

    # Replace placeholders with actual values
    sed -i "s|__ZAI_API_KEY__|$ZAI_API_KEY|g" "$SHELLRC"
    sed -i "s|__GLM_MODEL__|$GLM_MODEL|g" "$SHELLRC"

    # Add shell-specific hook
    if [[ "$SHELL_TYPE" == "zsh" ]]; then
        # Remove old hook if exists
        sed -i '/add-zsh-hook _oneshot_heartbeat/d' "$SHELLRC" 2>/dev/null || true
        # Add zsh hook
        cat >> "$SHELLRC" << 'ZSH_HOOK'

# ONE-SHOT Heartbeat: zsh chpwd hook
autoload -U add-zsh-hook
add-zsh-hook chpwd _oneshot_heartbeat
ZSH_HOOK
    else
        # Remove old hook if exists
        sed -i '/PROMPT_COMMAND.*_oneshot_heartbeat/d' "$SHELLRC" 2>/dev/null || true
        # Add bash hook (unquoted heredoc so \$ becomes $ in the file)
        cat >> "$SHELLRC" << BASH_HOOK

# ONE-SHOT Heartbeat: bash PROMPT_COMMAND hook
PROMPT_COMMAND="_oneshot_heartbeat\${PROMPT_COMMAND:+;\$PROMPT_COMMAND}"
BASH_HOOK
    fi

    echo "✓ Installed to $SHELLRC"
    echo "✓ cc  = Claude Code (Anthropic Pro, YOLO mode)"
    echo "✓ zai = Claude Code (z.ai $GLM_MODEL, YOLO mode)"
    echo "✓ Heartbeat: Daily health checks on project enter"
    echo ""
    if [[ "$SHELL_TYPE" == "zsh" ]]; then
        echo "Run: source ~/.zshrc"
    else
        echo "Run: source ~/.bashrc"
    fi
    exit 0
fi

# If sourced directly (not --install), just define the functions
if [[ "$ZAI_API_KEY" == "YOUR_ZAI_API_KEY_HERE" ]]; then
    echo "WARNING: ZAI_API_KEY not set. Edit the script or set ZAI_API_KEY env var." >&2
fi

unalias cc zai 2>/dev/null || true
unset -f cc zai 2>/dev/null || true

# cc - Claude Code via Anthropic Pro (YOLO mode)
cc() {
    claude --dangerously-skip-permissions "$@"
}

# zai - Claude Code via z.ai GLM API (YOLO mode)
zai() {
    if ! command -v claude >/dev/null 2>&1; then
        echo "zai: 'claude' CLI not found (npm install -g @anthropic-ai/claude-code)" >&2
        return 127
    fi
    [[ -z "$ZAI_API_KEY" ]] && { echo "zai: ZAI_API_KEY not set" >&2; return 1; }

    echo "zai: z.ai/$GLM_MODEL (YOLO mode)" >&2
    ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
    ANTHROPIC_AUTH_TOKEN="$ZAI_API_KEY" \
    ANTHROPIC_MODEL="$GLM_MODEL" \
        claude --dangerously-skip-permissions "$@"
}

# Heartbeat function (for manual use or sourcing)
_oneshot_heartbeat() {
    local heartbeat_script="${ONESHOT_DIR:-$HOME/github/oneshot}/scripts/heartbeat.sh"
    if [[ -f "$heartbeat_script" ]]; then
        "$heartbeat_script" "${@}"
    else
        echo "Heartbeat script not found at: $heartbeat_script" >&2
        return 1
    fi
}

oneshot-dismiss() {
    local suppressed="$HOME/.claude/state/suppressed-warnings"
    mkdir -p "$(dirname "$suppressed")"
    echo "$1" >> "$suppressed"
    echo "Dismissed: $1"
}
