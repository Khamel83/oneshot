#!/bin/bash
# PostToolUse hook: records tool calls to .oneshot/events.jsonl
# Fires AFTER every tool call during a Claude Code session.
# This is the automatic data collection — no manual action needed.
#
# Captures:
# - File reads and writes
# - Bash commands (summary, not full output)
# - Edit operations
# - Agent/delegation events
#
# INSTALL: Add to ~/.claude/settings.json under PostToolUse hooks

input=$(cat)

# Extract tool info
tool_name=$(echo "$input" | jq -r '.tool_name // "unknown"')
tool_input=$(echo "$input" | jq -r '.tool_input // "{}"')

# Find project root (directory with .git)
project_dir="$PWD"
while [ "$project_dir" != "/" ]; do
  if [ -d "$project_dir/.git" ]; then
    break
  fi
  project_dir=$(dirname "$project_dir")
done

# Skip if not in a git repo
if [ "$project_dir" = "/" ]; then
  exit 0
fi

oneshot_dir="$project_dir/.oneshot"
events_file="$oneshot_dir/events.jsonl"
mkdir -p "$oneshot_dir"

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Extract content based on tool type
content=""
files="[]"
event_type="action_taken"

case "$tool_name" in
  Read)
    file_path=$(echo "$tool_input" | jq -r '.file_path // .path // ""')
    content="Read $file_path"
    files=$(echo "$tool_input" | jq -c '[.file_path // .path // ""] | map(select(. != ""))')
    event_type="file_read"
    ;;
  Write)
    file_path=$(echo "$tool_input" | jq -r '.file_path // ""')
    content="Created $file_path"
    files=$(echo "$tool_input" | jq -c '[.file_path // ""] | map(select(. != ""))')
    event_type="file_written"
    ;;
  Edit)
    file_path=$(echo "$tool_input" | jq -r '.file_path // ""')
    old_str=$(echo "$tool_input" | jq -r '.old_string // ""' | head -c 80)
    content="Edited $file_path"
    if [ -n "$old_str" ]; then
      content="$content (context: ${old_str}...)"
    fi
    files=$(echo "$tool_input" | jq -c '[.file_path // ""] | map(select(. != ""))')
    event_type="file_written"
    ;;
  Bash)
    cmd=$(echo "$tool_input" | jq -r '.command // ""' | head -c 200)
    # Only record meaningful commands, not every git status
    case "$cmd" in
      git\ commit*|git\ push*)
        content="Git: $(echo "$cmd" | head -c 100)"
        event_type="commit"
        ;;
      git\ *)
        # Skip routine git commands to reduce noise
        exit 0
        ;;
      *)
        content="Ran: $(echo "$cmd" | head -c 100)"
        ;;
    esac
    ;;
  Glob|Grep)
    # Skip search operations — too noisy
    exit 0
    ;;
  Agent)
    # Already captured by delegation-log-hook.sh
    exit 0
    ;;
  *)
    content="$tool_name"
    ;;
esac

# Build session ID from CLAUDE_CODE_SESSION_ID or fallback
session_id="${CLAUDE_CODE_SESSION_ID:-$(date +%Y%m%d-%H%M%S)}"

# Write event (append-only, one JSON line)
jq -cn \
  --arg ts "$timestamp" \
  --arg session "$session_id" \
  --arg type "$event_type" \
  --arg content "$content" \
  --argjson files "$files" \
  --arg tool "$tool_name" \
  '{
    ts: $ts,
    session: $session,
    type: $type,
    content: $content,
    meta: {tool: $tool, auto: true},
    files: $files
  }' >> "$events_file" 2>/dev/null

# Always exit 0 — logging should never block anything
exit 0
