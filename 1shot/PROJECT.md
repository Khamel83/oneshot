# OneShot v2 Redesign — Conduct Session

**Date**: 2026-04-04
**Phase**: Intake → Plan
**Research basis**: `docs/research/oneshot-v2-redesign.md`

## Goal

Plan all 10 redesign items from the v2 research report. Implement items 1-7. Defer 8-10 with clear handoff notes.

## Deliverables (items 1-7)

1. **Risk field on Task + autonomy gating** — Add `risk_level` to task schema, use alongside lane routing to gate autonomy
2. **Mandatory verification gate** — Non-optional verify step in /conduct and /full operators
3. **TASK_SPEC.md template** — Standardized task spec template for complex tasks
4. **Session-end → repo feedback loop** — Extend /handoff to propose CLAUDE.md/instruction updates
5. **Exploration artifact (JSON)** — Structured explore output persisted to 1shot/
6. **Scope creep detection** — Compare git diff --stat against planned file list in build loop
7. **Machine-readable plan schema** — JSON plan schema alongside ROADMAP.md

## Deferred (items 8-10)

8. Parallel exploration wiring — wire existing dispatch runner into exploration phase
9. Formal adapter interface (AgentHarness) — defer until more harnesses added
10. Evaluation framework — defer until oneshot is more mature

## Acceptance Criteria

- All 7 items implemented with code + tests
- `ci.sh` passes
- Existing skills (/short, /full, /conduct) still work
- `/handoff` proposes CLAUDE.md updates
- `/conduct` produces structured exploration artifact
- `/conduct` enforces verification gate
- `/conduct` detects scope creep
- Demo run of /conduct showing new features
- ROADMAP.md covers all 10 items (with defer notes for 8-10)
- Updated docs/instructions/ where needed

## Scope (IN)

- `core/` Python modules (task_schema, router, new schemas)
- `.claude/skills/` operator prompts (conduct, full, short, handoff)
- `docs/instructions/` documentation
- `templates/` new templates (TASK_SPEC)
- `scripts/` ci.sh enhancements
- `config/` policy files

## Scope (OUT)

- TypeScript rewrite of core
- New harness adapters (OpenCode, etc.)
- Changes to community-starter template
- Changes to secrets/ system
- UI/visual components

## Constraints

- Python only for new code (no TypeScript)
- Don't break existing routing/lane system — extend it
- Keep it simple — JSON schemas, not full frameworks
- Subagent optimization: push heavy work (file reads, research, exploration) into subagents to keep main context lean
- Strict scope discipline — this session is about items 1-7 only

## Riskiest / Most Uncertain

**Scope creep of this very task.** Mitigation: strict task list, circuit breaker, no "while we're at it" additions.
