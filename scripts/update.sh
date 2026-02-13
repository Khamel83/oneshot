#!/bin/bash
# ONE_SHOT Updater - Works from ANY version
# Usage: curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/update.sh | bash
#
# Or: ~/github/oneshot/scripts/update.sh

set -euo pipefail

ONESHOT_DIR="${ONESHOT_DIR:-$HOME/github/oneshot}"
ONESHOT_REPO="git@github.com:Khamel83/oneshot.git"

echo "=== ONE_SHOT Updater ==="
echo ""

# 1. Ensure repo exists
if [[ ! -d "$ONESHOT_DIR/.git" ]]; then
    echo "Cloning ONE_SHOT..."
    git clone "$ONESHOT_REPO" "$ONESHOT_DIR"
else
    echo "Updating ONE_SHOT..."
    cd "$ONESHOT_DIR"
    git fetch origin
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/master)
    if [[ "$LOCAL" == "$REMOTE" ]]; then
        echo "Git: already up to date"
    else
        git pull origin master
    fi
fi

cd "$ONESHOT_DIR"

# 2. Get version
VERSION=$(grep -m1 "ONE_SHOT v" AGENTS.md 2>/dev/null | grep -oP 'v[\d.]+' || echo "unknown")
echo "Version: $VERSION"

# 3. Run install script
if [[ -f "install.sh" ]]; then
    bash install.sh
fi

# 4. Run heartbeat if available
if [[ -x "scripts/heartbeat.sh" ]]; then
    echo ""
    echo "=== Health Check ==="
    scripts/heartbeat.sh --force --safe 2>&1 || true
fi

# 5. Sync AGENTS.md to current directory if it's a project
if [[ -f "$PWD/AGENTS.md" ]] && [[ "$PWD" != "$ONESHOT_DIR" ]]; then
    cp "$ONESHOT_DIR/AGENTS.md" "$PWD/AGENTS.md"
    echo "Synced: AGENTS.md → $PWD"
fi

echo ""
echo "=== Done ==="
echo "ONE_SHOT $VERSION installed."
echo ""
echo "Quick commands:"
echo "  /update    - Run this again from Claude"
echo "  /beads     - Task tracking"
echo "  /deploy    - Push to cloud"
