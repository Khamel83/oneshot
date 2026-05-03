# Workflow Rules

## Operator Modes

OneShot provides three operators for different work styles:

### `/short` — Quick Iteration
- Load context (git log, TaskList, DECISIONS.md, BLOCKERS.md)
- Ask what you're working on
- Execute in burn-down mode
- Minimal overhead, maximum speed

### `/full` — Structured Work
- Create IMPLEMENTATION_CONTEXT.md
- Structured intake (goals, scope, architecture, constraints)
- Phase-based planning with milestones
- Context checkpoints at 50% (suggest handoff) and 70% (auto-handoff)
- Verify and completion summary

### `/conduct` — Multi-Model Orchestration
- Detect available providers (read `.oneshot/config/models.yaml`)
- Ask 5 intake questions (BLOCKING until answered)
- Classify tasks by task class → lane → worker
- Route work across planner, workers, and reviewers
- Loop until goal is fully met
- See `docs/instructions/task-classes.md` for routing contract
- **v2**: Produces structured artifacts (explore.json, plan.json, TASK_SPEC.md) and gates autonomy by inferred risk level (low/medium/high). Build loop includes a mandatory verification gate and scope creep detection.

## Lane-Based Routing

All operators use the same routing policy. Tasks are classified into task classes,
each mapped to a default lane in `config/lanes.yaml`.

```
task → task_class → lane → worker_pool + reviewer
```

Use the CLI resolver to check routing:
```bash
./bin/oneshot lanes
```

## Subagent Roles

| Role | Responsibility | Harness |
|------|---------------|---------|
| planner | Decomposition, task classification | claude_code |
| researcher | Web search, documentation | argus + any |
| implementer | Bounded code changes | lane-based |
| reviewer | Diff review, quality gate | claude_code |
| docs_writer | Draft documentation | lane-based |

## Session End Protocol

1. `git status` — check for uncommitted changes
2. Commit completed work
3. `TaskUpdate` — mark tasks completed
4. If corrections were given 2+ times: propose instruction update to `docs/instructions/learned/`
5. Never auto-edit `CLAUDE.md` or rules without review

## Handoff

Use `/handoff` before `/clear` or `/compact` to preserve context.
Use `/restore` to resume from a handoff.
