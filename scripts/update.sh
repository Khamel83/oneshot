#!/bin/bash
# ONE_SHOT Quick Install - Bootstrap from scratch
# Run this if you don't have oneshot at all
#
# curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/install.sh | bash

set -euo pipefail

ONESHOT_DIR="${ONESHOT_DIR:-$HOME/github/oneshot}"
BIN_DIR="${HOME}/.local/bin"

echo "=== ONE_SHOT Installer ==="

# Clone if doesn't exist
if [[ ! -d "$ONESHOT_DIR/.git" ]]; then
    echo "Cloning ONE_SHOT..."
    git clone git@github.com:Khamel83/oneshot.git "$ONESHOT_DIR"
else
    echo "ONE_SHOT already cloned at $ONESHOT_DIR"
fi

cd "$ONESHOT_DIR"

# Run the main install script
bash install.sh

echo ""
echo "Next: Add to your shell profile if needed:"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
