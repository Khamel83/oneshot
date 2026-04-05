# OneShot v2 Redesign — Roadmap

**Session**: 2026-04-04
**Research**: `docs/research/oneshot-v2-redesign.md`

## Phases

### Phase A: Foundations (parallel, no dependencies)

- **A1. Risk field** — Add `RiskLevel` to task schema, autonomy rules to lane policy
- **A2. Verify gate** — Make verification non-optional in /conduct and /full
- **A3. TASK_SPEC template** — Create standardized task spec template
- **A4. Feedback loop** — Extend /handoff to propose CLAUDE.md updates

### Phase B: Integration (depends on A3)

- **B1. Explore artifact** — Structured exploration output to `1shot/explore.json`
- **B2. Scope guard** — Detect scope creep by comparing diff to planned files

### Phase C: Schema (depends on A1, A3)

- **C1. Plan schema** — Machine-readable plan alongside ROADMAP.md

### Phase D: Docs + Demo

- **D1. Update instructions** — task-classes.md, workflow.md, oneshot.md
- **D2. Demo run** — Run /conduct with new features, verify everything works

## Deferred (items 8-10)

- **8. Parallel exploration** — Wire dispatch into explore phase
- **9. Adapter interface** — Formal AgentHarness TS interface
- **10. Evaluation framework** — Benchmark matrix + metrics

These are documented in ROADMAP for future sessions. No code changes needed now.

## Subagent Strategy

Throughout implementation:
- **Explore subagents**: Push all file reading, codebase exploration into subagents
- **Main context**: Stay lean — coordination, decisions, task tracking only
- **Each subagent returns**: Compact summary, not full file contents
- **Pattern**: Hub-and-spoke — main agent delegates, subagents execute and report back

## Success Criteria

- All 7 items have working code
- `ci.sh` passes
- Existing skills (/short, /full, /conduct) still work
- `/handoff` proposes CLAUDE.md updates
- `/conduct` produces `explore.json`, enforces verify, detects scope creep
- `1shot/plan.json` is valid against schema
- Demo run completes successfully
