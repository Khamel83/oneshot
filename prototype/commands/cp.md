# /cp — Continuous Planner (3-File Pattern)

Create a living plan that survives session breaks, /clear, and context compression.

## Core Principle

```
Context Window = RAM (volatile, limited)
Filesystem = Disk (persistent, unlimited)
→ Anything important gets written to disk.
```

## The 3 Files

| File | Purpose | When Updated |
|------|---------|--------------|
| `task_plan.md` | Single source of truth: phases, decisions, dependencies | When requirements/decisions change |
| `findings.md` | Research, errors, open questions, discoveries | When discovering new information |
| `progress.md` | Session log, actions taken, test results, next steps | After every action |

**Location:** `$PROJECT_DIR/.claude/continuous/` (or `~/.claude/plans/<name>-continuous/`)

## Workflow

### Creating a New Plan

1. Gather requirements (what, why, who, done criteria, constraints)
2. Create directory: `mkdir -p .claude/continuous`
3. Write `task_plan.md` with phases, decisions, dependencies
4. Initialize `findings.md` with empty sections
5. Initialize `progress.md` with first session entry
6. If beads available: create epic + phase tasks with `bd create`

### During Work (CRITICAL)

**READ before decisions:**
1. Read `task_plan.md` — current state
2. Read `findings.md` — existing research
3. Read `progress.md` — last checkpoint

**UPDATE after actions:**
1. Update `progress.md` with what you did
2. Update `findings.md` with new discoveries
3. Update `task_plan.md` ONLY when requirements change

### For Subagents

Always inject this when spawning sub-agents:
```
Plan files at: {path}
BEFORE any decision: read task_plan.md
AFTER any action: update progress.md
ON discovery: update findings.md
```

### Session Recovery (after /clear or disconnect)

1. Read all 3 files
2. Find last checkpoint in progress.md
3. Continue from "Next Steps" section

## Multi-Model Coordination

The 3 files are model-agnostic. Any AI can read/write them:
- Opus (planning): Updates task_plan.md
- GLM (execution): Updates progress.md
- Gemini (research): Updates findings.md

## Best Practices

- ALWAYS read before writing (don't duplicate work)
- Update progress.md frequently (after every action)
- Keep findings.md organized by date/topic
- Only update task_plan.md for actual decisions
- Create checkpoints before risky operations
