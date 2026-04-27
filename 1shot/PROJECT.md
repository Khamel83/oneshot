# Project: Plan L Hardening Pass for OneShot Delegation

## Goal
Execute a deterministic hardening pass on the `oneshot` delegation harness so the process is trustworthy enough to farm out work to Claude Code, OpenCode, and external workers without docs drift, false readiness signals, or secret leakage.

## Deliverable
Full execution for this session:
- normalize `1shot/` planning artifacts
- classify and seed concrete tasks for delegation
- ship core high-confidence fixes now
- verify with command output
- report pre-existing vs session changes explicitly

## Acceptance Criteria
- `1shot/PROJECT.md`, `1shot/STATE.md`, and `1shot/ROADMAP.md` reflect the current pass, not stale work
- Persistent task ledger exists for this pass and tasks are classified for routing/delegation
- `oneshot dispatch` behavior, CLI help text, and docs agree about whether execution is real or dry-run
- Dispatch path avoids writing secret values into `worker.log` or other rendered artifacts
- `oneshot doctor` checks local and remote readiness more accurately and includes explicit OpenCode launcher coverage
- OpenCode / `oc` support is treated as first-class in config and documentation
- CI/doc validation is improved enough that the known drift and avoidable failures are reduced with evidence
- A final summary distinguishes:
  - A: pre-existing dirty-tree changes
  - B: changes made in this session
  - C: recommended but deferred

## Scope
In:
- dispatch correctness and help/docs alignment
- doctor reliability and portability
- OpenCode support including `oc` launcher expectations
- secret-safe command logging
- docs alignment for README/QUICKSTART/delegation/doctor behavior
- CI hardening where directly relevant to this pass
- deterministic routing/task decomposition for future farm-out

Out:
- production deploys

## Constraints
- Do not rewrite the legacy router architecture wholesale in this pass
- Do not revert or clean unrelated pre-existing dirty-tree changes
- Prefer smallest correct fixes, but broader “Plan L” improvements are allowed when tightly connected to trustworthiness
- Verification must include real command output, not assertions

## Riskiest / Most Uncertain Part
The biggest risk is not one individual bug; it is process credibility: we could make many changes and still have Claude Code / OpenCode ignore intent or have the overall orchestration remain fundamentally unreliable.

## User Answers
- Primary deliverable: Full execution
- Done for this session: `1shot` docs ready, tasks classified, some fixes shipped
- In scope: dispatch correctness, doctor reliability, OpenCode support, secret-safe logging, docs alignment, CI hardening
- Out of scope: production deploys
- Biggest risk: process remains fundamentally broken or agents still do whatever they want

## Baseline Notes
- Repo is already dirty; treat those changes as A (pre-existing)
- Validation baseline was captured before edits
- Existing `1shot/` files were stale and belonged to prior work; they are being replaced as part of this session
