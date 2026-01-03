---
name: implement-plan
description: "Execute an approved implementation plan with context-aware task grouping."
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Task
---

# Implement Plan

Execute plans in context-aware task groups with running state persistence.

## When To Use

- User says "implement plan", "execute plan", "build it"
- User references a plan file with "@thoughts/shared/plans/..."

## Core Behavior

1. **Group tasks** into chunks of 3-5
2. **Write running state** after each task
3. **Check context at 50%** → pause, suggest compact
4. **Resume from running state** after compact

---

## Workflow

### Phase 1: Pre-Implementation Check

```
1. Check current context level
2. If context > 30%:
   → Create quick handoff
   → Output: "Context at X%. Recommend /compact before starting."
   → Stop and wait for user
3. If context < 30%:
   → Proceed to Phase 2
```

### Phase 2: Setup

```
1. Read plan file completely
2. Verify Status is "Approved"
3. Parse tasks into groups of 3-5
4. Create running state file
5. Announce: "Plan has N tasks in M groups. Starting Group 1."
```

### Phase 3: Execute (by group)

For each task group:

```
1. Announce: "Starting Group X of Y (tasks A-B)"
2. For each task in group:
   a. Mark in_progress in running state
   b. Implement the task
   c. Test
   d. Commit: "feat(scope): description - step X.Y"
   e. Mark completed in running state
   f. Update running state file immediately
3. After group complete:
   a. Commit running state
   b. Check context level
   c. If context > 50%:
      → Output: "Group X complete. Context at Y%. Recommend /compact."
      → Output: "Run /compact then 'continue' to resume at Group X+1"
      → Stop
   d. If context < 50%:
      → Continue to next group
```

### Phase 4: Completion

```
1. All groups complete
2. Run test suite
3. Update plan Status to "Completed"
4. Delete running state file (or archive)
5. Summary of what was implemented
```

---

## Running State File

**Location**: `thoughts/shared/runs/YYYY-MM-DD-{plan-name}.md`

**Format**:
```markdown
# Run: [Plan Name]

**Plan**: thoughts/shared/plans/YYYY-MM-DD-plan.md
**Started**: YYYY-MM-DD HH:MM
**Current Group**: 2 of 4

## Task Groups

### Group 1: [Description] - COMPLETE
- [x] Task 1 (commit: abc123)
- [x] Task 2 (commit: def456)
- [x] Task 3 (commit: ghi789)

### Group 2: [Description] - IN PROGRESS
- [x] Task 4 (commit: jkl012)
- [ ] Task 5 ← CURRENT
- [ ] Task 6

### Group 3: [Description] - PENDING
- [ ] Task 7
- [ ] Task 8
- [ ] Task 9

## Progress Log

| Time | Task | Status | Commit |
|------|------|--------|--------|
| 10:05 | Task 1 | Done | abc123 |
| 10:12 | Task 2 | Done | def456 |
| 10:20 | Task 3 | Done | ghi789 |
| 10:28 | Task 4 | Done | jkl012 |
| 10:35 | Task 5 | In Progress | - |

## Current Context

- **Working on**: `src/file.ts:45-80`
- **Decisions made**: [Key decisions this session]
- **Blockers**: None

## Resume Command

After /compact:
```
continue implementing @thoughts/shared/runs/YYYY-MM-DD-plan-name.md
```
```

---

## Task Grouping Logic

```
Total tasks: N
Group size: 3-5 (prefer 4)
Number of groups: ceil(N / 4)

Group by:
1. Logical phases (if plan has phases)
2. File proximity (related files together)
3. Dependency order (blockers first)
```

---

## Context Thresholds

| Level | Action |
|-------|--------|
| < 30% | Start/continue normally |
| 30-50% | Continue with caution |
| > 50% | **Pause after current group** |
| > 70% | **Stop immediately**, create handoff |

---

## Commit Format

```
type(scope): description - step X.Y

Types: feat, fix, refactor, test, docs, chore
```

---

## Handling Issues

### Context Running Low
1. Complete current task (if close)
2. Update running state with exact position
3. Output: "Context at X%. Stopping at Task Y."
4. Suggest: "/compact then 'continue from run state'"

### Unexpected Complexity
1. Note in running state under "Blockers"
2. If blocking, pause and ask user
3. Don't deviate from plan without approval

### Test Failures
1. Fix immediately if simple
2. Note in running state if complex
3. Don't proceed past failing tests

---

## Keywords

implement plan, execute plan, run plan, build it, continue implementing
