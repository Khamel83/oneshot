#!/usr/bin/env bash
# Auto-update ONE-SHOT repo from origin (only with --fix)

set -euo pipefail

ONESHOT_DIR="${ONESHOT_DIR:-$HOME/github/oneshot}"
FIX_MODE=false

# Parse arguments
for arg in "$@"; do
  case "$arg" in
    --fix) FIX_MODE=true ;;
    --check) FIX_MODE=false ;;
  esac
done

if [[ ! -d "$ONESHOT_DIR" ]]; then
  echo "⚠️  ONE-SHOT: repo not found at $ONESHOT_DIR"
  exit 1
fi

cd "$ONESHOT_DIR"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "⚠️  ONE-SHOT: not a git repository"
  exit 1
fi

# Check for updates (always)
git fetch origin >/dev/null 2>&1

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/master 2>/dev/null || git rev-parse origin/main)

if [[ "$LOCAL" == "$REMOTE" ]]; then
  echo "✓ ONE-SHOT: up to date"
  exit 0
fi

# Updates available
echo "⚠️  ONE-SHOT: update available ($LOCAL != $REMOTE)"

if [[ "$FIX_MODE" == true ]]; then
  echo "   Updating..."
  if git pull --quiet >/dev/null 2>&1; then
    echo "✓ ONE-SHOT: updated to latest"
    exit 0
  else
    echo "⚠️  ONE-SHOT: update failed (merge conflict or network)"
    exit 1
  fi
else
  echo "   Run with --fix to update"
  exit 0
fi
