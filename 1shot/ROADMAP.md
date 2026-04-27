# Plan L Roadmap

**Date**: 2026-04-27
**Execution mode**: `/conduct`
**Objective**: make the delegation harness deterministic enough to trust and farm out

## Deterministic Phase Plan

### Phase 0: Intake Lock
- Rewrite stale `1shot` artifacts for the current pass
- Capture user answers, scope, risk, and acceptance criteria in `PROJECT.md`
- Capture current execution state in `STATE.md`
- Seed persistent task ledger (`1shot/tasks.json` via `scripts/tasks.py`)
- Exit criteria:
  - current `1shot` files reflect this pass
  - task list exists and is classifiable

### Phase 1: Correctness First
- Fix dispatch contract drift:
  - CLI help text
  - docs language
  - any behavior edge cases found while aligning the contract
- Add or update tests covering the chosen contract
- Exit criteria:
  - `dispatch` contract is explicit and test-backed

### Phase 2: Doctor Reliability
- Improve `oneshot doctor` signal quality:
  - add launcher coverage for `oc`
  - reduce false-negative remote/path noise
  - improve portability where practical
- Add/update doctor tests
- Exit criteria:
  - doctor output better matches machine reality in this repo

### Phase 3: OpenCode + Secret Safety
- Fix OpenCode-specific config/runner assumptions
- Prevent auth value leakage into command logs / rendered command text
- Align runner/model semantics where currently ambiguous
- Exit criteria:
  - command logs are secret-safe
  - OpenCode runner behavior is documented and internally consistent

### Phase 4: Docs Alignment
- Update docs that currently lie about behavior or omit `oc`
- Priorities:
  - `docs/DELEGATION_MODEL.md`
  - `docs/WORKTREE_FLOW.md`
  - `README.md`
  - `QUICKSTART.md`
  - doctor docs/readiness docs as needed
- Exit criteria:
  - validation drift reduced
  - main operator docs describe real behavior

### Phase 5: CI Hardening
- Triage current `scripts/ci.sh` failures that are directly caused by avoidable harness/doc drift
- Improve CI signal quality where small targeted fixes are enough
- Exit criteria:
  - validation matrix is cleaner than baseline
  - remaining failures, if any, are understood and explicitly reported

### Phase 6: Verify + Challenge + Report
- Run the full validation matrix again
- Check acceptance criteria one by one with evidence
- Summarize A / B / C
- Exit criteria:
  - user can see what changed, what remains risky, and what can now be delegated safely

## File Targets by Phase

### Phase 1
- `oneshot_cli/dispatch_cmd.py`
- `oneshot_cli/tasks.py`
- tests covering dispatch behavior

### Phase 2
- `oneshot_cli/doctor_cmd.py`
- `oneshot_cli/__main__.py` if command wiring needs cleanup
- `tests/test_doctor.py`

### Phase 3
- `.oneshot/config/models.yaml`
- `oneshot_cli/tasks.py`
- possibly docs that define `oc` expectations

### Phase 4
- `docs/DELEGATION_MODEL.md`
- `docs/WORKTREE_FLOW.md`
- `README.md`
- `QUICKSTART.md`
- `docs/MACHINE_READINESS.md` if retained

### Phase 5
- `scripts/ci.sh`
- any directly implicated validation docs/scripts

## Validation Matrix

Run before final completion:
- `bash scripts/validate-docs.sh`
- `bash scripts/validate-skills.sh`
- `python3 scripts/validate-agents.py`
- `bash scripts/eval.sh`
- `PYTHONDONTWRITEBYTECODE=1 pytest -p no:cacheprovider`
- `bash scripts/ci.sh`

## Delegation Readiness

Work becomes safe to farm out once:
- task ledger is explicit
- dispatch contract is truthful
- doctor checks `oc` / OpenCode deterministically enough
- logs do not leak secrets
- docs stop contradicting runtime behavior
