#!/bin/bash
# Stop hook — fires after each Claude response
# Checks context percentage (written by statusline) and triggers handoff warning
# Claude treats hook output as user feedback, so it will act on this

CACHE_FILE="/tmp/claude-oneshot/context-pct"
MARKER_FILE="/tmp/claude-oneshot/handoff-triggered"

# No cache yet (first message), skip
if [ ! -f "$CACHE_FILE" ]; then
    exit 0
fi

PCT=$(cat "$CACHE_FILE")

# Already triggered this session, don't nag
if [ -f "$MARKER_FILE" ]; then
    exit 0
fi

if [ "$PCT" -ge 80 ]; then
    touch "$MARKER_FILE"
    echo "⚠️ Context at ${PCT}%. Run /handoff now to save your work before auto-compact."
fi
