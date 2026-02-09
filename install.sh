#!/bin/bash
# install.sh - Install ONE_SHOT commands to PATH

set -euo pipefail

ONESHOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BIN_DIR="${HOME}/.local/bin"

echo "Installing ONE_SHOT v7.4..."

# Create bin directory
mkdir -p "$BIN_DIR"

# Create symlinks for main commands
ln -sf "$ONESHOT_DIR/.claude/skills/resilient-executor/oneshot.sh" "$BIN_DIR/oneshot"
ln -sf "$ONESHOT_DIR/.claude/skills/autonomous-builder/oneshot-build.sh" "$BIN_DIR/oneshot-build"
ln -sf "$ONESHOT_DIR/.claude/skills/resilient-executor/oneshot-resilient.sh" "$BIN_DIR/oneshot-resilient"
ln -sf "$ONESHOT_DIR/.claude/skills/auto-updater/oneshot-update.sh" "$BIN_DIR/oneshot-update"

# Install docs-link for documentation cache management
ln -sf "$ONESHOT_DIR/scripts/docs-link" "$BIN_DIR/docs-link"

# Create skills symlink
mkdir -p "${HOME}/.claude/skills"
ln -sf "$ONESHOT_DIR/.claude/skills" "${HOME}/.claude/skills/oneshot"

echo ""
echo "Installed commands:"
echo "  oneshot           - Main command (build, run, attach, status, etc.)"
echo "  oneshot-build     - Autonomous builder"
echo "  oneshot-resilient - Resilient executor"
echo "  oneshot-update    - Manual update"
echo "  docs-link         - Documentation cache manager (add, list, remove, sync)"
echo ""

# Check if in PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "Add to your shell profile (~/.bashrc or ~/.zshrc):"
    echo ""
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

echo "Done! Run 'oneshot help' to get started."
