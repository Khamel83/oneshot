---
name: short
description: Quick iterations on existing projects. Load context, ask what's next, execute in burn-down mode.
---

# /short — Quick Iteration Operator

Fast operator for existing projects. Loads context, asks what you're working on, executes.

## Usage

```
/short
/short <scope>
```

## Behavior

When invoked:

1. **Load Context**
   - Read recent git commits: `git log --oneline -5`
   - Check TaskList for pending/in_progress tasks
   - Read DECISIONS.md, BLOCKERS.md, CHANGES.md if present

2. **Ask What's Next**
   ```
   "What are you working on?"
   ```

3. **Discover Skills** (if needed)
   - Query SkillsMP or local patterns for relevant skills
   - Apply matching skills without asking

4. **Execute in Burn-Down Mode**
   - Complete one task fully before starting next
   - If blocked > 2 attempts: log to BLOCKERS.md, skip, continue
   - No "pending review" - either done or blocked

5. **Show Summary on Completion**
   ```
   📊 Session Summary
   ├─ Tasks completed: X
   ├─ Files changed: Y
   ├─ Delegations: Z (avg reward: 0.N)
   └─ Next: [next task or "all done"]
   ```

## Scope

Optional scope limits work to matching files:

```
/short src/auth/*.ts    # Only work on auth files
```

## Decision Defaults (Don't Ask)

| Ambiguity | Default |
|-----------|---------|
| Multiple implementations | Simplest |
| Naming | Follow existing pattern |
| Refactor opportunity | Skip unless blocking |
| Error handling | Match surrounding code |

When truly ambiguous, pick option A, note in DECISIONS.md.

## Auto-Approved Actions

- Reading any file
- Writing to scope-matched files
- Running tests and linters
- Creating DECISIONS.md, BLOCKERS.md, CHANGES.md
- Git commit (not push)

## Requires Confirmation

- Destructive operations (rm -rf, DROP TABLE)
- Git push to shared branches
- External API calls that cost money
- Deploying to production

## Delegation Summary

After work completes, show:

```
📊 Delegation Summary
├─ N delegations, avg reward: X.XX
├─ Best: [agent type] (reward) - [description]
├─ Bottleneck: [agent type] (reward) - [tip]
└─ Tip: [optimization suggestion]
```
