#!/bin/bash
# audit-log.sh - Log all tool executions to .claude/audit.log
# Non-blocking: always exits 0

set -uo pipefail

# Read tool input from stdin
INPUT=$(cat)

# Extract fields
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unknown"')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.command // .tool_input.pattern // "-"')
SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // "unknown"')

# Ensure log directory exists
LOG_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude"
mkdir -p "$LOG_DIR"

# Append to audit log
TIMESTAMP=$(date -Iseconds)
echo "$TIMESTAMP | $TOOL_NAME | $FILE_PATH | $SESSION_ID" >> "$LOG_DIR/audit.log"

exit 0
