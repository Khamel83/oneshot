#!/bin/bash
# SessionEnd hook: processes accumulated events when a Claude Code session ends.
# Runs session digest and file change analysis via openrouter/free.
# This fires automatically when you exit Claude, even without /handoff.
#
# INSTALL: Add to ~/.claude/settings.json under SessionEnd hooks

# Find project root
project_dir="$PWD"
while [ "$project_dir" != "/" ]; do
  if [ -d "$project_dir/.git" ]; then
    break
  fi
  project_dir=$(dirname "$project_dir")
done

if [ "$project_dir" = "/" ]; then
  exit 0
fi

events_file="$project_dir/.oneshot/events.jsonl"

# Skip if no events to process
if [ ! -f "$events_file" ] || [ ! -s "$events_file" ]; then
  exit 0
fi

# Count events — skip if too few to be worth processing
event_count=$(wc -l < "$events_file" | tr -d ' ')
if [ "$event_count" -lt 3 ]; then
  exit 0
fi

# Run janitor jobs in the background so they don't block session exit
# Use nohup so they survive the session process exiting
(
  cd "$project_dir" 2>/dev/null || exit 0

  # Generate session digest
  python3 -c "
from core.janitor.recorder import SessionRecorder
from core.janitor.jobs import generate_session_digest, analyze_file_changes

try:
    r = SessionRecorder()
    digest = generate_session_digest(r)

    # Save digest to .oneshot/last-digest.md
    with open('.oneshot/last-digest.md', 'w') as f:
        f.write(digest)

    # Analyze file changes
    changes = analyze_file_changes()
    import json
    with open('.oneshot/last-changes.json', 'w') as f:
        json.dump(changes, f, indent=2)

except Exception as e:
    print(f'[janitor session-end] error: {e}')
" 2>>"$project_dir/.oneshot/janitor-errors.log"
) &

exit 0
