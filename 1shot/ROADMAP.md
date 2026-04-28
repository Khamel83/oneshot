# Current Roadmap Pointer

## Active Pass
- Name: OneShot repo-first memory architecture
- Date: 2026-04-28
- Dated roadmap: `1shot/2026-04-28-memory-architecture-ROADMAP.md`
- Dated project: `1shot/2026-04-28-memory-architecture-PROJECT.md`
- Dated state: `1shot/2026-04-28-memory-architecture-STATE.md`
- Active spec: `1shot/MEMORY_ARCHITECTURE_SPEC.md`
- Phase-1 implementation spec: `1shot/MEMORY_PHASE1_IMPLEMENTATION_SPEC.md`

## Live Objective
Design and stage a repo-first memory system for OneShot without making the OneShot repo the home of project work, and make the design portable to downstream customer repos.

## Current Build Contract
- `1shot/MEMORY_PHASE1_IMPLEMENTATION_SPEC.md` defines the first coding pass:
  - exact repo-local files
  - memory policy format
  - promotion rules
  - retrieval behavior
  - degraded-mode contract

## Implementation Progress
- Shipped in current wave:
  - repo scaffold and policy file creation
  - stable memory promotion for decisions, blockers, runbooks, and session summaries
  - provenance records
  - same-repo retrieval ordering
  - abstraction file generation
  - local private SQLite-backed abstraction indexing
  - cross-repo abstraction search with degraded-mode signaling
- Not yet shipped:
  - dual-home private index service integration
  - review-gate enforcement for memory-affecting high-risk work

## Phase Plan

### Phase 0: Planning Reset
- Preserve passes by date and name instead of relying only on overwritten top-level files
- Capture current intake, scope, constraints, and risk in dated and live planning artifacts
- Record provider availability and baseline planning state
- Reseed the persistent task ledger for the memory program
- Exit criteria:
  - planning files reflect the memory pass
  - dated artifacts preserve the pass identity
  - task ledger is reseeded for this work

### Phase 1: Memory Contract
- Define the repo-first memory contract
- Lock responsibilities for:
  - `docs/agents/`
  - `.oneshot/`
  - external private index/search
- Define initial first-class memory categories:
  - decisions
  - session summaries
  - important commands/runbooks
  - blockers/resolutions
- Exit criteria:
  - memory ownership and storage boundaries are explicit

### Phase 2: Lifecycle + Policy
- Define memory lifecycle states:
  - captured
  - summarized
  - promoted
  - conflicted
  - superseded
  - archived
- Define write policy:
  - broad automatic signal capture
  - provenance on every durable write
  - conflict preservation instead of overwrite
- Define per-repo policy modes:
  - portable
  - isolated
  - sensitive
  - private/no-cross-repo
- Exit criteria:
  - write rules and repo policy modes are stable enough to implement

### Phase 3: Retrieval + Portability
- Define same-repo retrieval order
- Define cross-repo retrieval order
- Restrict cross-repo reuse to abstracted lessons by default
- Define what is portable vs non-portable:
  - tooling
  - infra
  - orchestration
  - debugging
  - runbook patterns
  - not business logic or repo-bound assumptions by default
- Exit criteria:
  - retrieval policy can be implemented without reopening trust questions

### Phase 4: Governance + Review Gates
- Define which work classes are high-risk
- Lock planner vs worker vs reviewer roles for memory-related work
- Define when cross-model quorum is required
- Define how memory changes are reviewed and promoted
- Exit criteria:
  - important work has a clear review path that is strong without being everywhere-all-at-once

### Phase 5: Infra Fit
- Define the external index role across homelab, OCI, and Tailscale
- Keep repo memory canonical; external index remains secondary
- Define degraded-mode behavior when index/search is down
- Define onboarding behavior for repos with no memory yet
- Exit criteria:
  - system can fail gracefully without losing repo truth

### Phase 6: Implementation Roadmap
- Break the architecture into buildable milestones
- Order work to reduce risk:
  1. repo memory scaffold
  2. repo policy modes
  3. write/promotion rules
  4. same-repo retrieval
  5. cross-repo abstractions
  6. conflict handling
  7. review gates
  8. central index hardening
- Exit criteria:
  - next pass can start implementation without redesigning the system

## Recommended Implementation Order

### Milestone 1: Repo Scaffold
- Create standard repo-local memory layout
- Add policy declaration support
- Add empty first-class memory documents
- Success measure:
  - operational fit
  - review governance anchor points exist

### Milestone 2: Stable Writes
- Add checkpoint and session summary capture
- Promote first-class durable categories into repo-local memory
- Preserve provenance on all writes
- Success measure:
  - reliable repo memory exists and can be trusted

### Milestone 3: Same-Repo Retrieval
- Retrieve canonical memory from the active repo only
- Rank `docs/agents/` above `.oneshot/`
- Surface conflicts and superseded entries explicitly
- Success measure:
  - current repo gets useful memory without cross-project contamination

### Milestone 4: Cross-Repo Abstractions
- Generate abstracted lessons from repo-local memory
- Keep a global private abstraction pool with sensitivity/trust tags
- Default to abstracted-first cross-repo retrieval
- Success measure:
  - safe retrieval across repos without importing raw local assumptions first

### Milestone 5: Governance
- Add high-risk review gates for memory-affecting work
- Require planner plus cross-model quorum only for high-risk changes
- Success measure:
  - memory and governance changes are reviewed proportionally to risk

### Milestone 6: Private Index Hardening
- Add resiliency, degraded mode, and operational checks for the central index
- Keep repo truth intact if indexing services fail
- Success measure:
  - system remains useful when external search is degraded

## Verification Criteria For The Next Pass
- Every architecture element maps to a concrete file or service responsibility
- No implementation milestone depends on unresolved ownership questions
- Same-repo and cross-repo retrieval rules are testable as behavior, not just prose
- Review policy clearly distinguishes normal work from high-risk work
- Repo-local truth remains usable even if the central index is unavailable

## File Targets For This Planning Pass
- `1shot/PROJECT.md`
- `1shot/ROADMAP.md`
- `1shot/STATE.md`
- `1shot/MEMORY_ARCHITECTURE_SPEC.md`
- `1shot/tasks.json`

## Open Risks To Revisit During Implementation
- Over-promotion of noisy session memory into durable repo memory
- Conflict accumulation with no reconciliation path
- Weak policy boundaries for sensitive repos
- Overly broad cross-repo abstractions that become misleading
- Operational drift between repo truth and external index state
