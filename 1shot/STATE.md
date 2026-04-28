# Current State Pointer

Phase: plan -> complete
Started: 2026-04-28
Loop: 1
Tasks: 6/9 completed
Current focus: repo-local memory and local global abstraction index shipped; next pass should tackle dual-home service integration and review gates
Last updated: 2026-04-28
Dated state file: `1shot/2026-04-28-memory-architecture-STATE.md`
Dated phase-1 implementation spec: `1shot/2026-04-28-memory-phase1-implementation-SPEC.md`
Providers:
- codex: yes
- gemini: yes
- argus: yes
Notes:
- Top-level state now acts as a live pointer/current summary rather than the only record of the pass
- This pass now includes the first implementation wave: scaffold, promote, retrieve, and abstract commands
- This pass also includes a private local SQLite-backed abstraction index and degraded-mode signaling for cross-repo search
- Work memory belongs to target repos, not the OneShot repo
- Durable human-facing memory will live in `docs/agents/`
- Operational machine memory will live in `.oneshot/`
- Cross-repo retrieval remains allowed, but abstracted-first by default
- Stable memory is intended to be committed; transient state should usually remain local
- Phase-1 implementation contract now exists for the first coding pass
