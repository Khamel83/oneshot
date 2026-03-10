---
name: full
description: Structured operator for new projects, refactors, and complex implementations.
---

# /full — Full Operator for Complex Work

Structured operator for new projects, refactors, and complex implementations.

## Usage

```
/full
/full <project-description>
```

## Behavior

When invoked:

### Phase 1: Intake

1. **Load or Create Context File**
   - Check for IMPLEMENTATION_CONTEXT.md
   - If missing, create it

2. **Structured Discovery**
   - What are you building?
   - What's the scope?
   - What's the target architecture?
   - Any constraints or preferences?

3. **Document Decisions**
   - Write to IMPLEMENTATION_CONTEXT.md
   - Note key decisions in DECISIONS.md

### Phase 2: Planning

1. **Phase-Based Plan**
   - Break into milestones
   - Define acceptance criteria
   - Identify dependencies

2. **Skill Discovery**
   - Query SkillsMP for relevant skills
   - Apply stack defaults from CLAUDE.md

3. **Create Task Queue**
   - Use native TaskCreate for each milestone
   - Set dependencies with addBlockedBy

### Phase 3: Execution

1. **Milestone Tracking**
   - Work through tasks in order
   - Commit after each milestone
   - Update IMPLEMENTATION_CONTEXT.md with progress

2. **Burn-Down Mode**
   - Complete one task fully before starting next
   - If blocked > 2 attempts: log to BLOCKERS.md, skip, continue

3. **Context Checkpoints**
   - At 50% context: suggest /handoff
   - At 70% context: auto-create handoff

### Phase 4: Completion

1. **Verification**
   - Run tests
   - Check acceptance criteria
   - Review changes

2. **Summary**
   ```
   📊 Implementation Complete
   ├─ Milestones: X/Y completed
   ├─ Files changed: Z
   ├─ Commits: N
   ├─ Delegations: M (avg reward: 0.NN)
   └─ Next steps: [if any]
   ```

## IMPLEMENTATION_CONTEXT.md Template

```markdown
# Implementation Context

## Project
[Description]

## Goals
- [ ] Goal 1
- [ ] Goal 2

## Architecture
[Stack decisions]

## Milestones
1. [Milestone 1] - [status]
2. [Milestone 2] - [status]

## Decisions
- [Date] [Decision] - [Reason]

## Progress Log
- [Date] [What was done]
```

## Decision Defaults

| Ambiguity | Default |
|-----------|---------|
| Stack | Follow CLAUDE.md defaults |
| Multiple implementations | Simplest |
| Naming | Follow existing pattern |
| Auth | Better Auth + Google OAuth |
| Database | SQLite → Postgres on OCI |
| Deploy | Cloudflare Pages |

## Auto-Approved Actions

- Reading any file
- Writing to scope-matched files
- Creating IMPLEMENTATION_CONTEXT.md, DECISIONS.md, BLOCKERS.md
- Running tests and linters
- Git commit (not push)
- Creating native tasks

## Requires Confirmation

- Destructive operations
- Git push to shared branches
- External API calls that cost money
- Deploying to production
- Major architecture changes
