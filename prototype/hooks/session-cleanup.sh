#!/bin/bash
# SessionStart hook — clears stale markers from previous sessions
rm -f /tmp/claude-oneshot/handoff-triggered
rm -f /tmp/claude-oneshot/context-pct
