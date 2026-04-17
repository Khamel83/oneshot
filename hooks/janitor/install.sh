#!/bin/bash
# Install janitor hooks — symlinks from this repo to ~/.claude/hooks/
# Run once per machine: ./hooks/janitor/install.sh

HOOK_DIR="$HOME/.claude/hooks"
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)/janitor"

mkdir -p "$HOOK_DIR"

for hook in context session-end record pre-compact; do
    src="$REPO_DIR/${hook}.sh"
    dst="$HOOK_DIR/janitor-${hook}.sh"
    if [ -L "$dst" ]; then
        rm "$dst"
    elif [ -f "$dst" ]; then
        mv "$dst" "${dst}.bak"
        echo "Backed up existing ${dst}.bak"
    fi
    ln -s "$src" "$dst"
    echo "Linked: $dst -> $src"
done

echo "Done. 4 janitor hooks installed."
