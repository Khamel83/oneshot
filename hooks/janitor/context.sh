#!/bin/bash
# SessionStart hook: runs pure-compute jobs + injects results.
# Finds oneshot repo dynamically — works across all machines/projects.

project_dir="$PWD"
while [ "$project_dir" != "/" ]; do
  [ -d "$project_dir/.git" ] && break
  project_dir=$(dirname "$project_dir")
done
[ "$project_dir" = "/" ] && exit 0

# Find oneshot repo: check common locations
ONESHOT_DIR=""
for candidate in "$HOME/github/oneshot" "$HOME/oneshot" "$HOME/projects/oneshot"; do
  [ -d "$candidate/core/janitor" ] && { ONESHOT_DIR="$candidate"; break; }
done
[ -z "$ONESHOT_DIR" ] && exit 0

python3 -c "
import sys, os, json
sys.path.insert(0, '$ONESHOT_DIR')

project_dir = '$project_dir'

# Run pure-compute jobs
try:
    from core.janitor.jobs import run_session_start
    text = run_session_start(project_dir)
except Exception:
    text = ''

# Check for pending tasks
tasks_note = ''
tasks_file = os.path.join(project_dir, '.janitor', 'pending-tasks.md')
if os.path.isfile(tasks_file) and os.path.getsize(tasks_file) > 0:
    content = open(tasks_file).read()
    blockers = content.count('[blocker]')
    tasks = content.count('[high]') + content.count('[medium]') + content.count('[low]')
    if blockers > 0 or tasks > 0:
        tasks_note = f' | JANITOR_TASKS: {tasks} pending tasks, {blockers} blockers need your input. Read .janitor/pending-tasks.md.'

ctx = ''
if text:
    ctx = 'JANITOR_CONTEXT:' + text
if tasks_note:
    ctx += tasks_note

if ctx:
    print(json.dumps({
        'hookEventName': 'SessionStart',
        'hookSpecificOutput': {'additionalContext': ctx}
    }))
" 2>/dev/null

exit 0
