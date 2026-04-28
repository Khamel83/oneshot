# Current Project Pointer

## Active Pass
- Name: OneShot repo-first memory architecture
- Date: 2026-04-28
- Dated project: `1shot/2026-04-28-memory-architecture-PROJECT.md`
- Dated roadmap: `1shot/2026-04-28-memory-architecture-ROADMAP.md`
- Dated state: `1shot/2026-04-28-memory-architecture-STATE.md`
- Dated spec: `1shot/2026-04-28-memory-architecture-SPEC.md`

## Previous Pass
- 2026-04-27 Plan L hardening
  - `1shot/2026-04-27-plan-l-hardening-PROJECT.md`
  - `1shot/2026-04-27-plan-l-hardening-ROADMAP.md`
  - `1shot/2026-04-27-plan-l-hardening-STATE.md`

## Pass Index
- `1shot/INDEX.md`

## Live Working Copies
- Current live intake: `1shot/PROJECT.md`
- Current live roadmap: `1shot/ROADMAP.md`
- Current live state: `1shot/STATE.md`
- Current live spec: `1shot/MEMORY_ARCHITECTURE_SPEC.md`
- Current live phase-1 implementation spec: `1shot/MEMORY_PHASE1_IMPLEMENTATION_SPEC.md`

## Current Goal
Design a repo-first memory system for OneShot that works for OneShot itself and for downstream customer repos, while keeping durable project memory in the target repo instead of in the OneShot repo.

## Current Next Step
Turn the architecture into a first implementation pass with exact file contracts, policy format, promotion rules, retrieval rules, and degraded-mode behavior.

## Current Status
- Phase-1 implementation wave shipped in the CLI:
  - repo memory scaffold
  - stable memory promotion with provenance
  - same-repo retrieval
  - abstraction file generation
  - local private SQLite-backed abstraction indexing
  - cross-repo abstraction search with degraded-mode signaling
- Remaining major work:
  - dual-home central private index integration
  - degraded-mode signaling
  - review-gate integration
