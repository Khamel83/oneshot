#!/bin/bash
# SessionStart hook: injects recent janitor intelligence into new sessions.
# Fires once at session start — tells Claude about accumulated project data.
#
# What it does:
# 1. Checks for .oneshot/last-digest.md (session digest from previous session)
# 2. Checks for unprocessed events (events accumulated but cron hasn't processed yet)
# 3. Outputs a brief context line for Claude to pick up
#
# INSTALL: Add to ~/.claude/settings.json under SessionStart hooks

project_dir="$PWD"
while [ "$project_dir" != "/" ]; do
  [ -d "$project_dir/.git" ] && break
  project_dir=$(dirname "$project_dir")
done
[ "$project_dir" = "/" ] && exit 0

oneshot_dir="$project_dir/.oneshot"
digest_file="$oneshot_dir/last-digest.md"
events_file="$oneshot_dir/events.jsonl"
changes_file="$oneshot_dir/last-changes.json"

output=""

# Check for recent session digest
if [ -f "$digest_file" ]; then
  age=$(find "$digest_file" -mmin -120 2>/dev/null | grep -q "." && echo "found")
  if [ -n "$age" ]; then
    digest_preview=$(head -5 "$digest_file" 2>/dev/null | tr '\n' ' | head -c 300)
    if [ -n "$digest_preview" ]; then
      output="JANITOR: Last session digest (within 2h): ${digest_preview}"
    fi
  fi
fi

# Check for unprocessed events (data collected but not yet summarized by cron)
if [ -f "$events_file" ]; then
  event_count=$(wc -l < "$events_file" | tr -d ' ')
  if [ "$event_count" -gt 20 ]; then
    decisions=$(grep -c '"type":"decision"' "$events_file" 2>/dev/null || echo 0)
    blockers=$(grep -c '"type":"blocker"' "$events_file" 2>/dev/null || echo 0)
    if [ "$decisions" -gt 0 ] || [ "$blockers" -gt 0 ]; then
      output="${output}"
      output="${output} JANITOR: ${event_count} events accumulated (${decisions} decisions, ${blockers} blockers) — may need processing."
    fi
  fi
fi

# Check for recent file changes analysis
if [ -f "$changes_file" ]; then
  age=$(find "$changes_file" -mmin -120 2>/dev/null | grep -q "." && echo "found")
  if [ -n "$age" ]; then
    hotspots=$(python3 -c "
import json
d = json.load(open('$changes_file'))
h = d.get('hotspot_files', [])
if h: print(', '.join(h[:5]))
" 2>/dev/null)
    if [ -n "$hotspots" ]; then
      output="${output}"
      output="${output} JANITOR: Hotspot files: ${hotspots}"
    fi
  fi
fi

if [ -n "$output" ]; then
  echo "{\"hookSpecificOutput\":{\"additionalContext\":\"JANITOR_CONTEXT:${output//\"/\\\"}\"}}"
fi

exit 0
