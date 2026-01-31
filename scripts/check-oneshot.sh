#!/usr/bin/env bash
# Check if ONE-SHOT repo is up to date

set -euo pipefail

ONESHOT_DIR="${ONESHOT_DIR:-$HOME/github/oneshot}"

if [[ ! -d "$ONESHOT_DIR" ]]; then
  echo "⚠️  ONE-SHOT: repo not found at $ONESHOT_DIR"
  exit 1
fi

cd "$ONESHOT_DIR"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "⚠️  ONE-SHOT: not a git repository"
  exit 1
fi

git fetch origin >/dev/null 2>&1

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/master 2>/dev/null || git rev-parse origin/main)

if [[ "$LOCAL" == "$REMOTE" ]]; then
  echo "✓ ONE-SHOT: up to date"
  exit 0
else
  echo "⚠️  ONE-SHOT: updates available (cd ~/github/oneshot && git pull)"
  exit 1
fi
