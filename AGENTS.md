# ONE_SHOT v14 — Orchestration Control Plane

> Lane-based routing. Claude plans, workers execute. Argus searches.

## OPERATORS

### `/short` — Quick Iteration
1. Load context: git log -5, TaskList, DECISIONS.md, BLOCKERS.md
2. Ask: "What are you working on?"
3. Execute via dispatch protocol (non-premium tasks → Codex/Gemini)
4. Show delegation summary

### `/full` — Structured Work
1. Create/load IMPLEMENTATION_CONTEXT.md
2. Structured intake: goals, scope, architecture, constraints
3. Phase-based planning with milestones
4. Execute via dispatch protocol (parallel Codex/Gemini workers)
5. Context checkpoints (50% → suggest handoff, 70% → auto-handoff)
6. Verify and show completion summary

### `/conduct` — Multi-Model Orchestration
1. Detect available providers (read `config/workers.yaml`)
2. Ask clarifying questions — BLOCKING
3. Classify tasks by task class (see `docs/instructions/task-classes.md`)
4. Route: task class → lane → worker pool → reviewer
5. Dispatch non-premium tasks in parallel via dispatch protocol
6. Loop until goal is fully met

## DISPATCH PROTOCOL

All non-premium tasks use the dispatch protocol (`_shared/dispatch.md`):
- Claude builds self-contained prompts with full context
- Codex and Gemini execute in parallel (up to `max_parallel` per lane)
- Structured JSON output captured and validated
- Manifests written to `1shot/dispatch/{id}.md`

```
Claude (thinker) → classify → build prompt → dispatch to worker(s) → capture output → validate → commit
```

## TASK CLASSES & LANE ROUTING

Tasks are classified, then routed to lanes defined in `config/lanes.yaml`.

| Task Class | Default Lane | Worker Pool |
|-----------|-------------|-------------|
| plan | premium | claude_code (inline) |
| research | research | gemini_cli, codex |
| implement_small | cheap | gemini_cli, codex |
| implement_medium | balanced | codex, gemini_cli |
| test_write | cheap | gemini_cli, codex |
| review_diff | premium | claude_code (inline) |
| doc_draft | cheap | gemini_cli, codex |
| search_sweep | research | gemini_cli, codex + argus |
| summarize_findings | cheap | gemini_cli, codex |

Resolve routing: `python -m core.router.resolve --class <task_class>`
Parallel dispatch: `python3 -m core.dispatch.run --class <class> --prompts-file batch.json`

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
**Workers (Codex + Gemini)**: bounded implementation, tests, docs, search summarization
**Dispatch**: parallel execution with structured output and manifest tracking

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

## V2 FEATURES

- Risk-based autonomy gating: `RiskLevel` (low/medium/high) controls what requires confirmation
- Structured exploration artifact: `explore.json` from intake phase
- Machine-readable plan schema: `plan.json` via `core/plan_schema.py`
- TASK_SPEC template: `templates/TASK_SPEC.md` for formal task specification
- Mandatory verification gate after each build step
- Scope creep detection in the build loop
- Session-end feedback loop: handoff proposes CLAUDE.md/rule updates when patterns repeat

## VERSION

v14.1 | Parallel dispatch | Codex + Gemini workers | Manifest tracking
