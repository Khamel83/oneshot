#!/bin/bash
# install.sh - Install ONE_SHOT to system (local clone)
# Use this when you have the repo cloned locally.
# For fresh installs: curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash

set -euo pipefail

ONESHOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${HOME}/.local/bin"
HOOKS_DIR="${HOME}/.claude/hooks"

# Sync hooks from repo to ~/.claude/hooks/ (won't overwrite existing files)
install_hooks() {
    local src="$ONESHOT_DIR/.claude/hooks"
    [ -d "$src" ] || return 0

    mkdir -p "$HOOKS_DIR"
    local count=0
    for f in "$src"/*.sh; do
        [ -f "$f" ] || continue
        local name=$(basename "$f")
        if [ -f "$HOOKS_DIR/$name" ]; then
            echo "  $name (exists, skipped)"
        else
            cp "$f" "$HOOKS_DIR/$name"
            chmod +x "$HOOKS_DIR/$name"
            echo "  $name (installed)"
            count=$((count + 1))
        fi
    done
    if [ "$count" -gt 0 ]; then
        echo "  $count hook(s) installed"
    fi
}

# Read version from AGENTS.md
VERSION=$(grep -m1 "ONE_SHOT v" "$ONESHOT_DIR/AGENTS.md" 2>/dev/null | sed 's/.*\(v[0-9.]*\).*/\1/' || echo "unknown")

echo "Installing ONE_SHOT $VERSION..."

# Create bin directory
mkdir -p "$BIN_DIR"

# Remove old broken symlinks (v9 and earlier)
rm -f "$BIN_DIR/oneshot" "$BIN_DIR/oneshot-build" "$BIN_DIR/oneshot-resilient" 2>/dev/null || true

# Create oneshot-update symlink
ln -sf "$ONESHOT_DIR/scripts/oneshot-update.sh" "$BIN_DIR/oneshot-update"
echo "  oneshot-update    - Update ONE_SHOT from GitHub"

# Install docs-link for documentation cache management (if it exists)
if [ -f "$ONESHOT_DIR/scripts/docs-link" ]; then
    ln -sf "$ONESHOT_DIR/scripts/docs-link" "$BIN_DIR/docs-link"
    echo "  docs-link         - Documentation cache manager"
fi

# Sync skills to global ~/.claude/skills/ (COPY not symlink - works across machines)
if [ -d "$ONESHOT_DIR/.claude/skills" ]; then
    mkdir -p "${HOME}/.claude/skills"
    echo "Syncing skills to ~/.claude/skills/..."
    cp -r "$ONESHOT_DIR/.claude/skills/"* "${HOME}/.claude/skills/" 2>/dev/null || true
    echo "  10+1 skills synced"
fi

# Sync hooks to ~/.claude/hooks/ (won't overwrite existing)
if [ -d "$ONESHOT_DIR/.claude/hooks" ]; then
    echo "Syncing hooks to ~/.claude/hooks/..."
    install_hooks
fi

echo ""
echo "ONE_SHOT $VERSION installed."
echo ""
echo "Skills available in Claude Code:"
echo "  /short     - Quick iteration"
echo "  /full      - Structured work"
echo "  /conduct   - Multi-model orchestration"
echo "  /handoff   - Save context"
echo "  /restore   - Resume from handoff"
echo "  /research  - Background research"
echo "  /freesearch - Zero-token search"
echo "  /doc       - Cache external docs"
echo "  /vision    - Image/website analysis"
echo "  /secrets   - SOPS/Age secrets"
echo ""
echo "See ~/.claude/skills/INDEX.md for full reference."

# Check if in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "Add to your shell profile (~/.bashrc or ~/.zshrc):"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

echo "Done! To update: oneshot-update"
