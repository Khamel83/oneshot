#!/bin/bash
# session-context.sh - Inject project context on session start
# Outputs additionalContext JSON for Claude to consume

set -uo pipefail

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-.}"

# Build context from available files
CONTEXT=""

# Check for LLM-OVERVIEW.md
if [ -f "$PROJECT_DIR/LLM-OVERVIEW.md" ]; then
    OVERVIEW=$(head -100 "$PROJECT_DIR/LLM-OVERVIEW.md" 2>/dev/null || true)
    if [ -n "$OVERVIEW" ]; then
        CONTEXT="$CONTEXT\n\n## Project Overview\n$OVERVIEW"
    fi
fi

# Check for TODO.md with in-progress items
if [ -f "$PROJECT_DIR/TODO.md" ]; then
    TODOS=$(grep -E "^\s*-\s*\[[ x]\]|In Progress|Current" "$PROJECT_DIR/TODO.md" 2>/dev/null | head -20 || true)
    if [ -n "$TODOS" ]; then
        CONTEXT="$CONTEXT\n\n## Current Tasks\n$TODOS"
    fi
fi

# Check for recent handoff
HANDOFF_DIR="$PROJECT_DIR/thoughts/shared/handoffs"
if [ -d "$HANDOFF_DIR" ]; then
    LATEST_HANDOFF=$(ls -t "$HANDOFF_DIR"/*.md 2>/dev/null | head -1 || true)
    if [ -n "$LATEST_HANDOFF" ]; then
        HANDOFF_DATE=$(basename "$LATEST_HANDOFF" | cut -d'-' -f1-3)
        TODAY=$(date +%Y-%m-%d)
        # Only include if from today or yesterday
        if [[ "$HANDOFF_DATE" == "$TODAY" ]] || [[ "$HANDOFF_DATE" == $(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null) ]]; then
            CONTEXT="$CONTEXT\n\n## Recent Handoff Available\nFile: $LATEST_HANDOFF\nRun /resume-handoff to continue from where you left off."
        fi
    fi
fi

# Output JSON if we have context
if [ -n "$CONTEXT" ]; then
    # Escape for JSON
    ESCAPED=$(echo -e "$CONTEXT" | jq -Rs .)
    cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": $ESCAPED
  }
}
EOF
fi

exit 0
