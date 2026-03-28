---
name: review-log
description: Review a session log with haiku to summarize tool usage, spot loops/retries, and flag waste. Trigger on: "review log", "what happened today", "session summary", "log review", "what did we do", "analyze log".
---

# Review Log Skill

Reviews `~/.claude/logs/YYYY-MM-DD.jsonl` using haiku to summarize what happened.

## Usage

```
/review-log           # today's log
/review-log 2026-03-27  # specific date
```

## Steps

1. Determine date: use argument if provided, else today (`date +%Y-%m-%d`)
2. Read `~/.claude/logs/<date>.jsonl`
3. If file doesn't exist or is empty, report "No log found for <date>"
4. Spawn a Task with `model: haiku` with the log contents and this prompt:

```
Analyze this Claude Code session log (JSONL, one tool call per line).

Report:
1. Total tool calls
2. Top 5 tools by call count
3. Any tool called 3+ times consecutively (loop signal) — list the tool and count
4. Any entries with ok=false — list tool name and input summary
5. One-sentence summary of what work appears to have been done

Be concise. Plain text, no markdown headers.
```

5. Print haiku's response directly to the user.

## Notes

- Log format: `{"ts":"...","session":"...","tool":"...","input":"...","ok":true}`
- Sessions log (per-session summaries): `~/.claude/logs/sessions.jsonl`
- Delegation spans: `.claude/delegation-log.jsonl` (project) or `~/.claude/delegation-log.jsonl`
