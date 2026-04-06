#!/bin/bash
# SessionStart hook: runs pure-compute jobs + injects results.
# No cron dependency — everything runs here at session start.

project_dir="$PWD"
while [ "$project_dir" != "/" ]; do
  [ -d "$project_dir/.git" ] && break
  project_dir=$(dirname "$project_dir")
done
[ "$project_dir" = "/" ] && exit 0

result=$(python3 -c "
import sys, os
sys.path.insert(0, '$project_dir')
try:
    from core.janitor.jobs import run_session_start
    print(run_session_start('$project_dir'))
except Exception:
    pass
" 2>/dev/null)

if [ -n "$result" ]; then
  echo "{\"hookSpecificOutput\":{\"additionalContext\":\"JANITOR_CONTEXT:${result//\"/\\\"}\"}}"
fi

exit 0
