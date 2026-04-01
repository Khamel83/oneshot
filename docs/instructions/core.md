# Core Rules

These rules apply to every project, regardless of type.

## STOP BEING CLEVER

**YOU ARE A ROBOT. JUST DO THE SIMPLE THING FAST FIRST.**

- Don't edit databases directly when there's a UI
- Don't write scripts when a CLI exists
- Don't debug for an hour when restarting might fix it
- If there's a 30-second solution, do that before the 30-minute solution

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

**Exceptions** (ask first):
- Destructive operations (rm -rf, DROP TABLE, force push)
- Actions that affect others (deploying to production, sending messages)
- Spending money (API calls that cost $, provisioning cloud resources)

## Work Discipline

- **Plan first**: Always start with a plan before coding. Think, then do.
- **Commit per task**: Don't batch commits to end-of-session. Commit each completed task immediately.
- **Keep tasks small**: Break work so each subtask completes well within context.
- **Vanilla over complex**: Simple direct work beats elaborate orchestration for small tasks.

## Documentation-First Coding

Before writing code that uses external APIs, libraries, or configuration syntax:

1. Check local cached docs: `~/github/docs-cache/docs/cache/.index.md`
2. If insufficient, use WebSearch for current docs
3. Verify version compatibility
4. Write code using current syntax, not training data

## Task Management

Use native Tasks (TaskCreate, TaskUpdate, TaskList) for all task tracking.

- Persistent in `~/.claude/tasks/`
- Survive `/clear` and context compression
- Session start: `TaskList` → pick unblocked task → `TaskUpdate` in_progress
- Session end: `git status` → stage → commit → `TaskUpdate` completed → push

## Decision Defaults

| Ambiguity | Default |
|-----------|---------|
| Multiple implementations | Simplest one |
| Naming | Follow existing pattern |
| Error handling | Match surrounding code |
| Test framework | Use existing tests as guide |
| Library choice | One already in project |
| Refactor opportunity | Skip unless blocking |
