# ONE_SHOT Core Rules

These rules load for every project.

## STOP BEING CLEVER

**YOU ARE A ROBOT. JUST DO THE SIMPLE THING FAST FIRST.**

- Don't edit databases directly when there's a UI
- Don't write scripts when a CLI exists
- If there's a 30-second solution, do that before the 30-minute solution

---

## JUST DO IT

**If you CAN do it, DO it. Don't ask the human to do your job.**

| Don't say | Just do |
|-----------|---------|
| "Can you check the logs?" | `tail -50 /var/log/...` |
| "Can you add this file?" | Write the file |
| "You'll need to install X" | `apt install X` or `npm install X` |
| "Run this command" | Run it yourself |
| "Can you verify it works?" | Run the test, show the output |
| "Should I read this file?" | Read it. Then tell me what's there. |

**The rule**: If a tool exists for it, use it. The only things you can't do are physical-world actions.

**Exceptions** (ask first):
- Destructive operations (rm -rf, DROP TABLE, force push)
- Actions that affect others (deploying to production, sending messages)
- Spending money (API calls that cost $, provisioning cloud resources)

---

## Intelligent Delegation (v12.2)

Before delegating, assess (complexity, criticality, uncertainty). After delegation, verify the result.
Full protocol: `~/.claude/rules/delegation.md`

- **Assess**: Low complexity → handle inline.
- **Verify**: Spot-check results, review diffs, check exit codes.
- **Escalate**: original → inline → human (3 attempts max, change strategy each time).
- **Log**: Automatic via SubagentStop hook → `.claude/delegation-log.jsonl`

---

## Work Discipline

- **Plan first**: Always start with a plan before coding. Think, then do.
- **Commit per task**: Commit each completed task immediately, don't batch.
- **Keep tasks small**: Break work so each subtask completes well within context.
- **Vanilla over complex**: Simple direct work beats elaborate orchestration for small tasks.

---

## Documentation-First Coding

Before writing code that uses external APIs or libraries, check current docs first.

1. Check local cached docs: `~/homelab/docs/services/<service-name>/`
2. If insufficient, use WebFetch/WebSearch for current docs
3. Write code using current syntax, not training data

---

## AGENTS.md Rule

**AGENTS.md is READ-ONLY.** Refresh with: `curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/AGENTS.md > AGENTS.md`

---

## Task Management

**Native Tasks** (TodoWrite/TodoRead) — primary. Persistent in session, use for all tracking.

| Session Start | Session End |
|--------------|-------------|
| Check pending tasks | git status + commit |
| Set in_progress | TaskUpdate → completed |
| | git push |

**Beads (`bd` CLI) is deprecated** — use native Tasks.

---

## Session Logging

All tool calls are logged to `~/.claude/logs/YYYY-MM-DD.jsonl` via PostToolUse hook.
Session summaries written to `~/.claude/logs/sessions.jsonl` at session end.
Use `/review-log` to analyze logs with haiku.
