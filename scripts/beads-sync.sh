#!/usr/bin/env bash
# Sync heartbeat results to beads for daily collection
# Usage: ./beads-sync.sh [--quiet]

set -euo pipefail

QUIET="${1:-}"

# Check if beads is available
if ! command -v bd >/dev/null 2>&1; then
  [[ -z "$QUIET" ]] && echo "⊘ Beads: not available (optional)"
  exit 0
fi

# Create a heartbeat bead
TODAY=$(date +%Y-%m-%d)
HEARTBEAT_MSG="Heartbeat check completed: $TODAY"

# Add bead with lesson label
bd add -l heartbeat -m "$HEARTBEAT_MSG" >/dev/null 2>&1 || true

[[ -z "$QUIET" ]] && echo "✓ Beads: synced heartbeat data"
exit 0
