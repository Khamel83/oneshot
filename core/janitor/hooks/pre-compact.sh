#!/bin/bash
# PreCompact hook: preserves context before Claude compacts the conversation.
# Runs the LLM summarizer so nothing is lost when compaction happens.
# Best-effort — silently skips if OPENROUTER_API_KEY isn't set.

project_dir="$PWD"
while [ "$project_dir" != "/" ]; do
  [ -d "$project_dir/.git" ] && break
  project_dir=$(dirname "$project_dir")
done
[ "$project_dir" = "/" ] && exit 0

[ ! -f "$project_dir/.janitor/events.jsonl" ] && exit 0

# Run summarizer in background (don't block compaction)
python3 -c "
import sys, os
sys.path.insert(0, '$project_dir')
try:
    from core.janitor.jobs import summarize_session
    result = summarize_session('$project_dir')
    if result.get('decisions') or result.get('blockers'):
        import json
        path = '$project_dir/.janitor/last-summary.json'
        with open(path, 'w') as f:
            json.dump(result, f, indent=2)
except Exception:
    pass
" &

exit 0
