#!/bin/bash
# SessionEnd hook: marks session end and runs LLM jobs.
# LLM jobs are best-effort — if OPENROUTER_API_KEY isn't set, they silently skip.
# Pure-compute already ran at SessionStart, so nothing critical here.

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

# Run LLM jobs in background (don't block session end)
python3 -c "
import sys, os
sys.path.insert(0, '$project_dir')
try:
    from core.janitor.jobs import run_session_end
    run_session_end('$project_dir')
except Exception:
    pass
" &

exit 0
