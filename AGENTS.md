# ONE_SHOT v14 — Orchestration Control Plane

> Lane-based routing. Claude plans, workers execute. Argus searches.

## OPERATORS

### `/short` — Quick Iteration
1. Load context: git log -5, TaskList, DECISIONS.md, BLOCKERS.md
2. Ask: "What are you working on?"
3. Execute in burn-down mode
4. Show delegation summary

### `/full` — Structured Work
1. Create/load IMPLEMENTATION_CONTEXT.md
2. Structured intake: goals, scope, architecture, constraints
3. Phase-based planning with milestones
4. Execute with context checkpoints (50% → suggest handoff, 70% → auto-handoff)
5. Verify and show completion summary

### `/conduct` — Multi-Model Orchestration
1. Detect available providers (read `config/workers.yaml`)
2. Ask clarifying questions — BLOCKING
3. Classify tasks by task class (see `docs/instructions/task-classes.md`)
4. Route: task class → lane → worker pool → reviewer
5. Loop until goal is fully met

## TASK CLASSES & LANE ROUTING

Tasks are classified, then routed to lanes defined in `config/lanes.yaml`.

| Task Class | Default Lane | Worker Pool |
|-----------|-------------|-------------|
| plan | premium | claude_code, codex |
| research | research | gemini_cli, argus |
| implement_small | cheap | openrouter pool |
| implement_medium | balanced | mixed pool |
| test_write | cheap | openrouter pool |
| review_diff | premium | claude_code, codex |
| doc_draft | cheap | openrouter pool |
| search_sweep | research | argus + cheap summarizer |
| summarize_findings | cheap | openrouter pool |

Resolve routing: `python -m core.router.resolve --class <task_class>`

## UTILITY COMMANDS

| Command | Purpose |
|---------|---------|
| `/handoff` | Save context before /clear |
| `/restore` | Resume from handoff |
| `/research` | Background research via Argus |
| `/freesearch` | Zero-token search via Argus (cheap mode) |
| `/doc` | Cache external documentation |
| `/vision` | Image/website analysis |
| `/secrets` | SOPS/Age secrets management |

## PLANNER/WORKER SPLIT

**Planner (Claude)**: planning, decomposition, repo synthesis, review, sensitive edits
**Workers (lane-based)**: bounded implementation, tests, docs, search summarization

## DECISION DEFAULTS

| Ambiguity | Default |
|-----------|---------|
| Multiple implementations | Simplest |
| Naming | Follow existing pattern |
| Refactor opportunity | Skip unless blocking |
| Lane selection | Use task class routing |

## AUTO-APPROVED

Reading files, writing to scope-matched files, running tests, git commit (not push), creating tasks.

## REQUIRES CONFIRMATION

Destructive ops, git push, external API calls that cost money, production deploy.

## VERSION

v14.0 | Lane-based routing | Argus search plane | Config-driven
