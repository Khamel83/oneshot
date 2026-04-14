#!/bin/bash
# Auto-handoff statusline monitor
# Writes context percentage to cache file for stop hook to read
# Also displays context usage in the status bar

input=$(cat)

PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
MODEL=$(echo "$input" | jq -r '.model.display_name // "unknown"')
REMAINING=$(echo "$input" | jq -r '.context_window.remaining_percentage // 100' | cut -d. -f1)

# Write to cache for stop hook
CACHE_DIR="/tmp/claude-oneshot"
mkdir -p "$CACHE_DIR"
echo "$PCT" > "$CACHE_DIR/context-pct"

# Color coding
if [ "$PCT" -ge 80 ]; then
    echo "$MODEL | ctx: ${PCT}% ⚠️ HANDOFF SOON"
elif [ "$PCT" -ge 60 ]; then
    echo "$MODEL | ctx: ${PCT}%"
else
    echo "$MODEL | ctx: ${PCT}%"
fi
