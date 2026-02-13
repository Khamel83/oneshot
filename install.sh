#!/bin/bash
# install.sh - Install ONE_SHOT to system

set -euo pipefail

ONESHOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${HOME}/.local/bin"

# Read version from AGENTS.md
VERSION=$(grep -m1 "ONE_SHOT v" "$ONESHOT_DIR/AGENTS.md" 2>/dev/null | grep -oP 'v[\d.]+' || echo "unknown")

echo "Installing ONE_SHOT $VERSION..."

# Create bin directory
mkdir -p "$BIN_DIR"

# Remove old broken symlinks (v7 and earlier)
rm -f "$BIN_DIR/oneshot" "$BIN_DIR/oneshot-build" "$BIN_DIR/oneshot-resilient" 2>/dev/null || true

# Create oneshot-update symlink
ln -sf "$ONESHOT_DIR/scripts/oneshot-update.sh" "$BIN_DIR/oneshot-update"
echo "  oneshot-update    - Update ONE_SHOT from GitHub"

# Install docs-link for documentation cache management (if it exists)
if [ -f "$ONESHOT_DIR/scripts/docs-link" ]; then
    ln -sf "$ONESHOT_DIR/scripts/docs-link" "$BIN_DIR/docs-link"
    echo "  docs-link         - Documentation cache manager"
fi

# Create skills symlink (for skill files if needed)
mkdir -p "${HOME}/.claude/skills"
ln -sf "$ONESHOT_DIR/.claude/skills" "${HOME}/.claude/skills/oneshot" 2>/dev/null || true

# Sync commands to global ~/.claude/commands/
if [ -d "$ONESHOT_DIR/.claude/commands" ]; then
    mkdir -p "${HOME}/.claude/commands"
    for cmd in "$ONESHOT_DIR/.claude/commands"/*.md; do
        [ -f "$cmd" ] && ln -sf "$cmd" "${HOME}/.claude/commands/" 2>/dev/null || true
    done
fi

echo ""
echo "ONE_SHOT $VERSION installed."
echo ""
echo "Commands available via /slash-commands in Claude:"
echo "  /update           - Update ONE_SHOT from GitHub"
echo "  /deploy           - Push to OCI-Dev Cloud"
echo "  /research         - Background research"
echo "  /beads            - Task tracking"
echo "  /handoff          - Save context"
echo ""
echo "See AGENTS.md for full skill router and commands."

# Check if in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "Add to your shell profile (~/.bashrc or ~/.zshrc):"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

echo "Done! To update in the future, run: /update"
