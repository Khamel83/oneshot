# Conduct State

Phase: plan -> complete
Started: 2026-04-28
Loop: 1
Tasks: 0/5 completed
Current focus: publish architecture spec, reseed tasks, hand off a build-ready roadmap
Last updated: 2026-04-28
Providers:
- codex: yes
- gemini: yes
- argus: yes
Notes:
- This pass is planning only: no implementation code changes
- Work memory belongs to target repos, not the OneShot repo
- Durable human-facing memory will live in `docs/agents/`
- Operational machine memory will live in `.oneshot/`
- Cross-repo retrieval remains allowed, but abstracted-first by default
- Stable memory is intended to be committed; transient state should usually remain local
- The plan is intended for OneShot itself and for downstream customer repos
