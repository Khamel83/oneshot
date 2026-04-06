#!/bin/bash
# PostToolUse hook: records tool calls to .janitor/events.jsonl
# Fires AFTER every tool call during a Claude Code session.
# Optimized: uses printf instead of jq (one process instead of 3-4).
#
# INSTALL: Add to ~/.claude/settings.json under PostToolUse hooks

input=$(cat)

# Fast field extraction with parameter expansion (no jq needed for simple fields)
tool_name="${input#*\"tool_name\":\"}"
tool_name="${tool_name%%\"*}"

# Skip noise early — before any further processing
case "$tool_name" in
  WebFetch|WebSearch|mcp__*|TaskCreate|TaskUpdate|TaskList|TaskGet|CronCreate|CronDelete|CronList|AskUserQuestion)
    exit 0
    ;;
esac

# Find project root (directory with .git)
project_dir="$PWD"
while [ "$project_dir" != "/" ]; do
  [ -d "$project_dir/.git" ] && break
  project_dir=$(dirname "$project_dir")
done
[ "$project_dir" = "/" ] && exit 0

janitor_dir="$project_dir/.janitor"
events_file="$janitor_dir/events.jsonl"
mkdir -p "$janitor_dir"

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
session_id="${CLAUDE_CODE_SESSION_ID:-$(date +%Y%m%d-%H%M%S)}"

# Extract file_path from tool_input (works for Read/Write/Edit which have file_path field)
# Simple string extraction: find "file_path":"..." and take value up to next "
file_path=""
case "$tool_name" in
  Read|Write|Edit)
    file_path="${input#*\"file_path\":\"}"
    file_path="${file_path%%\"*}"
    ;;
esac

# Extract tool_output for dead-end detection (lightweight: just check for failure signals)
# Strip backslash escapes then check for non-zero exit code
has_failed_output=0
if echo "$input" | tr -d '\\' | grep -qE '"exit_code"\s*:\s*[1-9]'; then
    has_failed_output=1
fi

# Build event based on tool type
case "$tool_name" in
  Glob|Grep)
    # Dead-end detection: check if results indicate no matches
    # Extract the pattern/query for context
    query="${input#*\"pattern\":\"}"
    query="${query%%\"*}"
    [ -z "$query" ] && query="${input#*\"glob_pattern\":\"}"
    query="${query%%\"*}"
    [ -z "$query" ] && query="${input#*\"query\":\"}"
    query="${query%%\"*}"
    query="${query:0:100}"

    # Check for no results in the raw input (no output content after tool_output)
    is_empty=0
    case "$input" in
      *"\"tool_output\":\"\""*|*"\"tool_output\":\"\[\"]"*)
        is_empty=1
        ;;
    esac
    # Also check for common "no results" messages in output
    if echo "$input" | grep -qE '"tool_output":"[^"]*([Nn]o (matches|results)|0 results|found 0|empty)'; then
      is_empty=1
    fi

    if [ "$is_empty" -eq 1 ] && [ -n "$query" ]; then
      printf '{"ts":"%s","session":"%s","type":"dead_end","content":"No results for: %s","meta":{"tool":"%s","auto":true},"files":[]}\n' \
        "$timestamp" "$session_id" "$query" "$tool_name" >> "$events_file"
    fi
    exit 0
    ;;
  Read)
    [ -z "$file_path" ] && exit 0
    printf '{"ts":"%s","session":"%s","type":"file_read","content":"Read %s","meta":{"tool":"Read","auto":true},"files":["%s"]}\n' \
      "$timestamp" "$session_id" "$file_path" "$file_path" >> "$events_file"
    ;;
  Write)
    [ -z "$file_path" ] && exit 0
    printf '{"ts":"%s","session":"%s","type":"file_written","content":"Created %s","meta":{"tool":"Write","auto":true},"files":["%s"]}\n' \
      "$timestamp" "$session_id" "$file_path" "$file_path" >> "$events_file"
    ;;
  Edit)
    [ -z "$file_path" ] && exit 0
    printf '{"ts":"%s","session":"%s","type":"file_written","content":"Edited %s","meta":{"tool":"Edit","auto":true},"files":["%s"]}\n' \
      "$timestamp" "$session_id" "$file_path" "$file_path" >> "$events_file"
    ;;
  Bash)
    # Extract command from tool_input
    cmd="${input#*\"command\":\"}"
    cmd="${cmd%%\"*}"
    cmd="${cmd:0:200}"
    # Dead-end detection: failed commands (non-zero exit code)
    if [ "$has_failed_output" -eq 1 ]; then
      printf '{"ts":"%s","session":"%s","type":"dead_end","content":"Failed: %s","meta":{"tool":"Bash","auto":true},"files":[]}\n' \
        "$timestamp" "$session_id" "${cmd:0:100}" >> "$events_file"
    fi
    case "$cmd" in
      git\ commit*|git\ push*)
        printf '{"ts":"%s","session":"%s","type":"commit","content":"Git: %s","meta":{"tool":"Bash","auto":true},"files":[]}\n' \
          "$timestamp" "$session_id" "${cmd:0:100}" >> "$events_file"
        ;;
      git\ *)
        exit 0  # skip routine git
        ;;
      *)
        printf '{"ts":"%s","session":"%s","type":"action_taken","content":"Ran: %s","meta":{"tool":"Bash","auto":true},"files":[]}\n' \
          "$timestamp" "$session_id" "${cmd:0:100}" >> "$events_file"
        ;;
    esac
    ;;
  *)
    exit 0  # skip everything else
    ;;
esac

exit 0
