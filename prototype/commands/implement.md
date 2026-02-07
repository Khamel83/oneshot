# /implement — Execute Plan with Beads Tracking

Execute an approved plan with persistent beads-backed progress tracking.

## Pre-Implementation

```bash
# Init beads if needed
[ ! -d .beads ] && bd init --stealth
bd sync
```

If context > 30%, recommend `/compact` before starting.

## Setup: Parse Plan into Beads Tasks

```bash
# Create epic
bd create "Implement: [Plan Name]" -t epic --json
# Create task groups with dependencies
bd create "Group 1: [Desc]" --deps parent:$EPIC_ID -p 1 --json
bd create "Task 1.1: [Desc]" --deps parent:$GROUP1_ID -p 1 --json
# Group 2 blocked by Group 1
bd dep add $GROUP2_ID $GROUP1_ID --type blocks
```

Group 3-5 tasks per group. Dependencies between groups.

## Execute (by group)

For each task:
1. `bd update $TASK_ID --status in_progress --json`
2. Implement the task
3. Test
4. Commit: `feat(scope): description - step X.Y`
5. `bd close $TASK_ID --reason "commit: abc123" --json`
6. Check context level

**Context thresholds:**
| Level | Action |
|-------|--------|
| < 30% | Continue normally |
| 30-50% | Continue with caution |
| > 50% | **Pause, bd sync, suggest /compact** |
| > 70% | **Stop immediately, bd sync** |

## Parallel Execution

When `bd ready --json` returns multiple tasks, check if they touch different files.
If file-disjoint: spawn background agents for each in parallel.
If same files: sequential.

```
Task:
  subagent_type: general-purpose
  description: "Implement Task A"
  prompt: "Implement: [desc]\nFiles: [list]\nCommit when done."
  run_in_background: true
```

## Resuming After /compact

```bash
bd sync
bd ready --json      # Next unblocked task
bd list --status in_progress --json  # Any in-progress?
```

User says "continue" and you pick up exactly where beads says.

## Session End (Critical)

```bash
bd sync  # ALWAYS sync before ending
```
