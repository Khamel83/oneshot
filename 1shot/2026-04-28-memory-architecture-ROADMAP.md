# OneShot Memory Roadmap

**Date**: 2026-04-28
**Execution mode**: `/conduct`
**Objective**: design and stage a repo-first memory system for OneShot without making the OneShot repo the home of project work, and do so in a way that downstream customer repos can adopt safely.

## Phase Plan

### Phase 0: Planning Reset
- Replace stale `1shot/` artifacts from the prior pass without losing history
- Capture current intake, scope, constraints, and risk in dated planning artifacts
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
  - memory ownership and storage boundaries are explicit for OneShot and customer repos

### Phase 2: Lifecycle + Policy
- Define memory lifecycle states
- Define automatic write policy and provenance requirements
- Define per-repo policy modes
- Exit criteria:
  - write rules and repo policy modes are stable enough to implement

### Phase 3: Retrieval + Portability
- Define same-repo retrieval order
- Define cross-repo retrieval order
- Restrict cross-repo reuse to abstracted lessons by default
- Define portable vs non-portable memory classes
- Exit criteria:
  - retrieval policy can be implemented without reopening trust questions

### Phase 4: Governance + Review Gates
- Define which work classes are high-risk
- Lock planner vs worker vs reviewer roles for memory-related work
- Define when cross-model quorum is required
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
- Order work to reduce risk
- Exit criteria:
  - next pass can start implementation without redesigning the system
