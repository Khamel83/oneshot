#!/bin/bash
# SessionEnd hook: marks session end and runs LLM jobs.
# Finds oneshot repo dynamically — works across all machines/projects.

project_dir="$PWD"
while [ "$project_dir" != "/" ]; do
  [ -d "$project_dir/.git" ] && break
  project_dir=$(dirname "$project_dir")
done
[ "$project_dir" = "/" ] && exit 0

# Mark session end in events.jsonl
janitor_dir="$project_dir/.janitor"
events_file="$janitor_dir/events.jsonl"
[ ! -f "$events_file" ] && exit 0

timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
session_id="${CLAUDE_CODE_SESSION_ID:-unknown}"
printf '{"ts":"%s","session":"%s","type":"session_end","content":"Session ended","meta":{"auto":true},"files":[]}\n' \
  "$timestamp" "$session_id" >> "$events_file"

# Find oneshot repo: check common locations
ONESHOT_DIR=""
for candidate in "$HOME/github/oneshot" "$HOME/oneshot" "$HOME/projects/oneshot"; do
  [ -d "$candidate/core/janitor" ] && { ONESHOT_DIR="$candidate"; break; }
done
[ -z "$ONESHOT_DIR" ] && exit 0

# Run LLM jobs in background (don't block session end)
export OPENROUTER_API_KEY="$(secrets get OPENROUTER_API_KEY 2>/dev/null)" || true
python3 -c "
import sys, os
sys.path.insert(0, '$ONESHOT_DIR')
try:
    from core.janitor.jobs import run_session_end
    run_session_end('$project_dir')
except Exception:
    pass
" &

exit 0
