#!/bin/bash
# lessons-inject.sh - SessionStart hook
# Injects recent lessons learned into Claude context
#
# Usage: Add to .claude/settings.json:
# "SessionStart": [
#   {
#     "matcher": "",
#     "hooks": [{ "type": "command", "command": "~/.claude/hooks/lessons-inject.sh", "timeout": 5 }]
#   }
# ]

set -euo pipefail

BEADS_DIR="${HOME}/.claude"

# Check if global beads exists
if [ ! -d "${BEADS_DIR}/.beads" ]; then
    exit 0  # No lessons database yet, silent exit
fi

# Query recent lessons (last 5)
LESSONS=$(cd "${BEADS_DIR}" && bd list -l lesson --json 2>/dev/null || echo "[]")

# Count lessons
COUNT=$(echo "$LESSONS" | jq -r 'length' 2>/dev/null || echo "0")

if [ "$COUNT" -eq 0 ]; then
    exit 0  # No lessons to inject
fi

# Format lessons for context injection
echo "## Recent Lessons Learned (from past mistakes)"
echo ""
echo "These are mistakes we've made before - check if any apply to current work:"
echo ""

echo "$LESSONS" | jq -r '.[:5] | .[] | "- **\(.title | sub("^Lesson: "; ""))** [\(.labels | join(", "))]"' 2>/dev/null

echo ""
echo "Query more lessons: \`/lessons\` or \`/lessons [tag]\`"
