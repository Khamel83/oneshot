---
name: continuous
description: >
  Start continuous autonomous execution mode. Use when you want the agent to work
  through a queue of tasks without stopping for clarification. The agent will make
  reasonable decisions, log blockers, and skip tasks that can't be completed.
  Trigger with "/continuous" or "/continuous [scope]".
allowed-tools: Read, Write, Edit, Bash, TaskList, TaskGet, TaskUpdate, TaskCreate
---

# Continuous Mode - Autonomous Execution

Run multi-hour unattended work sessions by removing decision points and providing a deterministic execution loop.

## When To Use

Use continuous mode when:
- Multiple related tasks need completion
- Clear scope and acceptance criteria defined
- Work can proceed autonomously with minimal supervision
- User wants to step away and let agent work

**Don't use** when:
- Tasks require frequent user input
- Work is exploratory or undefined
- High-risk operations (deploy, data migration)

## Activation

```bash
# Activate continuous mode
/continuous

# Activate with scope filter
/continuous src/auth

# Activate with specific task IDs
/continuous --tasks task-1,task-2,task-3
```

## What It Does

1. **Loads continuous-mode.md rules** from `~/.claude/rules/`
2. **Creates tracking files** if not exist:
   - `DECISIONS.md` - Non-trivial choices made
   - `BLOCKERS.md` - Skipped tasks and why
   - `CHANGES.md` - Out-of-scope modifications
3. **Starts burn-down queue** from TaskList
4. **Executes tasks** in priority order
5. **Commits after each task** completion
6. **Stops on exit conditions** (see below)

## Execution Loop

```
┌─────────────────────────────────────────┐
│  1. TaskList → Get pending tasks        │
│  2. Filter by scope (if provided)       │
│  3. Pick highest priority unblocked     │
│  4. TaskUpdate → in_progress            │
│  5. Execute task                        │
│  6. Run ./scripts/ci.sh                 │
│  7. If pass: commit, mark completed     │
│  8. If fail: fix or skip (log blocker)  │
│  9. Repeat until done or exit condition │
└─────────────────────────────────────────┘
```

## Task Format for Continuous Execution

Tasks work best with these fields:

```json
{
  "subject": "Fix type errors in auth module",
  "description": "Run tsc and fix all type errors in src/auth/*.ts",
  "metadata": {
    "scope": ["src/auth/*.ts", "tests/auth/*.ts"],
    "acceptance_criteria": ["tsc passes", "tests pass"],
    "non_goals": ["refactor", "add features"],
    "blocked_action": "skip",
    "priority": 1
  }
}
```

**Key fields**:
- `scope`: File patterns this task can modify
- `acceptance_criteria`: How to know it's done
- `non_goals`: What NOT to do
- `blocked_action`: "skip" (default) or "stop" or "ask"

## Decision Defaults

When ambiguous, the agent will:

| Situation | Default |
|-----------|---------|
| Multiple approaches | Pick simplest |
| Naming | Match existing pattern |
| Error handling | Match surrounding code |
| Refactor opportunity | Skip unless blocking |
| Truly stuck | Log to BLOCKERS.md, continue |

## Exit Conditions

Continuous mode stops when:
- ✓ All tasks completed
- ✗ 3 consecutive blockers
- ⚠ User sends `/stop` or Ctrl+C
- ⚠ Context window warning (auto-handoff)

## Tracking Files

### DECISIONS.md
```markdown
## 2026-03-01 14:30 - Auth Token Format
**Choice**: JWT over opaque tokens
**Reason**: Existing code uses JWT in 3 places
**Alternatives considered**: Opaque tokens (simpler revocation)
```

### BLOCKERS.md
```markdown
## 2026-03-01 15:00 - Task #4: Migrate database
**Blocker**: Missing credentials for prod DB
**Attempts**: 2
**Action**: Skipped, needs human intervention
**Unblocks when**: Credentials added to secrets/
```

### CHANGES.md
```markdown
## 2026-03-01 15:30 - Out of scope change
**Task**: Fix auth types
**Change**: Modified src/utils/format.ts
**Reason**: Type error cascaded from auth change
**Approved by**: Continuous mode scope flexibility
```

## Verification

After each task:
```bash
./scripts/ci.sh
```

Runs: lint → typecheck → tests → validation

If failure:
1. Check if pre-existing
2. If new: fix or revert
3. If can't fix: log blocker, skip task

## Examples

### Example 1: Fix All Type Errors

```bash
# User runs
/continuous src/auth

# Agent:
# 1. Loads continuous rules
# 2. Gets tasks with scope matching src/auth
# 3. Task: "Fix type errors in auth"
# 4. Runs tsc, fixes errors
# 5. Runs ci.sh → passes
# 6. Commits: "fix(auth): resolve type errors"
# 7. Marks task complete
# 8. Moves to next task
```

### Example 2: Blocked Task

```bash
# Task: "Add OAuth provider"
# Blocker: Need client ID from user

# Agent logs to BLOCKERS.md:
# "Missing OAuth client ID - needs user to provide"
# Skips task, continues to next
```

## Keywords

continuous, autonomous, unattended, burn-down, queue, decision defaults, skip blockers, verify loop
