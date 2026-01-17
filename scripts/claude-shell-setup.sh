#!/bin/bash
# claude-shell-setup.sh - Portable Claude Code + ZAI setup
#
# USAGE:
#   1. Copy to new machine and edit the config values below
#   2. Run: bash claude-shell-setup.sh --install
#   3. Then: source ~/.bashrc
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
# ══════════════════════════════════════════════════════════════════

# Handle --install flag
if [[ "$1" == "--install" ]]; then
    # Validate API key was set
    if [[ "$ZAI_API_KEY" == "YOUR_ZAI_API_KEY_HERE" ]]; then
        echo "ERROR: Edit this script and set your ZAI_API_KEY first!" >&2
        echo "Get your key at: https://z.ai/devpack" >&2
        exit 1
    fi

    MARKER="##### Claude Code + ZAI shortcuts #####"
    BASHRC="$HOME/.bashrc"

    # Remove old block if exists
    if grep -q "$MARKER" "$BASHRC" 2>/dev/null; then
        sed -i "/$MARKER/,/##### end Claude Code + ZAI shortcuts #####/d" "$BASHRC"
        echo "Removed old Claude/ZAI block from .bashrc"
    fi

    # Append new block
    cat >> "$BASHRC" << 'BASHRC_BLOCK'

##### Claude Code + ZAI shortcuts #####
# Portable setup: github.com/Khamel83/oneshot/scripts/claude-shell-setup.sh
# To reinstall: bash claude-shell-setup.sh --install

ZAI_API_KEY="__ZAI_API_KEY__"
GLM_MODEL="__GLM_MODEL__"

unalias cc zai 2>/dev/null || true
unset -f cc zai 2>/dev/null || true

# cc - Claude Code via Anthropic Pro (assumes logged in)
cc() {
    claude --dangerously-skip-permissions "$@"
}

# zai - Claude Code via z.ai GLM API
zai() {
    if ! command -v claude >/dev/null 2>&1; then
        echo "zai: 'claude' CLI not found (npm install -g @anthropic-ai/claude-code)" >&2
        return 127
    fi
    [[ -z "$ZAI_API_KEY" ]] && { echo "zai: ZAI_API_KEY not set" >&2; return 1; }

    echo "zai: z.ai/$GLM_MODEL" >&2
    ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
    ANTHROPIC_AUTH_TOKEN="$ZAI_API_KEY" \
    ANTHROPIC_MODEL="$GLM_MODEL" \
        claude --dangerously-skip-permissions "$@"
}
##### end Claude Code + ZAI shortcuts #####
BASHRC_BLOCK

    # Replace placeholders with actual values
    sed -i "s|__ZAI_API_KEY__|$ZAI_API_KEY|g" "$BASHRC"
    sed -i "s|__GLM_MODEL__|$GLM_MODEL|g" "$BASHRC"

    echo "✓ Installed to $BASHRC"
    echo "✓ cc  = Claude Code (Anthropic Pro)"
    echo "✓ zai = Claude Code (z.ai $GLM_MODEL)"
    echo ""
    echo "Run: source ~/.bashrc"
    exit 0
fi

# If sourced directly (not --install), just define the functions
if [[ "$ZAI_API_KEY" == "YOUR_ZAI_API_KEY_HERE" ]]; then
    echo "WARNING: ZAI_API_KEY not set. Edit the script or set ZAI_API_KEY env var." >&2
fi

unalias cc zai 2>/dev/null || true
unset -f cc zai 2>/dev/null || true

cc() {
    claude --dangerously-skip-permissions "$@"
}

zai() {
    if ! command -v claude >/dev/null 2>&1; then
        echo "zai: 'claude' CLI not found (npm install -g @anthropic-ai/claude-code)" >&2
        return 127
    fi
    [[ -z "$ZAI_API_KEY" ]] && { echo "zai: ZAI_API_KEY not set" >&2; return 1; }

    echo "zai: z.ai/$GLM_MODEL" >&2
    ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
    ANTHROPIC_AUTH_TOKEN="$ZAI_API_KEY" \
    ANTHROPIC_MODEL="$GLM_MODEL" \
        claude --dangerously-skip-permissions "$@"
}
