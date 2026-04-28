# Project: OpenCode Adapter Drift Fix

## Goal
Execute 8 recommendations to align .opencode/ config, task tracking, dispatch, and validation. No new orchestration — fix drift between plans, adapters, task state, and permissions.

## Acceptance Criteria
1. `.opencode/` presence validated in CI (test passes)
2. `scripts/tasks.py` is a thin wrapper around `python -m oneshot_cli.tasks`
3. `core/dispatch/run.py` supports `--dry-run` flag
4. `scripts/validate-oneshot-config.py` includes new checks
5. `core/dispatch/direct_api.py` has timeout, masked errors, response validation
6. `docs/migration/baseline/*` files marked as historical
7. `~/.claude/hooks/lessons-inject.sh` gates on `bd` availability
8. Each recommendation has at least one test/validation

## Scope
- IN: .opencode/ validation, task tracking consolidation, dispatch dry-run, direct_api hardening, CI tests, migration markers, Beads gate
- OUT: New orchestration features, lane changes, worker config changes, schema changes

## Constraints
- Don't break existing CI (scripts/ci.sh)
- Don't break dispatch workflow (/short, /conduct)
- Each recommendation gets a test
- Task tracking: `oneshot_cli/tasks.py` is canonical; `scripts/tasks.py` wraps it

## Implementation Order
1. .opencode/ presence validation
2. Cheap-worker bash permissions
3. Task tracking consolidation
4. Dispatch --dry-run
5. Success criteria → CI tests
6. Migration baseline markers
7. direct_api.py hardening
8. Beads fallback cleanup

## Risk
Low — all additive or consolidation changes. No schema changes.
