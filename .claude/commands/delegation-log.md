---
name: delegation-log
description: View and query the delegation audit log
---

# Delegation Log Viewer

Show recent delegation events from `.claude/delegation-log.jsonl`.

## Instructions

1. Read the file `.claude/delegation-log.jsonl` in the current project (or `~/.claude/delegation-log.jsonl` if project-level doesn't exist)
2. Parse the JSONL (one JSON object per line)
3. Display a summary table showing:
   - Timestamp
   - Task summary (truncated to 60 chars)
   - Agent type
   - Model used
   - Result (success/partial/failure)
   - Tool calls count
   - Duration

4. If the user provided arguments, filter:
   - `failures` → show only result=failure
   - `agent:<type>` → show only that agent type (e.g., `agent:Explore`)
   - `last:<N>` → show only last N entries
   - `stats` → show aggregate success rates by agent type

5. If no log file exists, say "No delegation log found. The log is created automatically when delegation rules from `.claude/rules/delegation.md` are active."

## Example Output

```
Delegation Log (last 10 events)
───────────────────────────────────────────────────────────────────
Time       | Task                          | Agent    | Model  | Result  | Calls | Duration
2026-02-13 | Find error handling patterns  | Explore  | haiku  | success | 8     | 12.3s
2026-02-13 | Research auth libraries        | general  | sonnet | partial | 15    | 45.2s
...

Summary: 8 delegations, 6 success, 1 partial, 1 failure
```
