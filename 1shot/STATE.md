# OneShot Conduct State

**Session**: 2026-04-07 opencode-adapter
**Phase**: complete
**Loop**: 1
**Blockers**: 0

## Progress

- [x] Provider detection: codex (yes), gemini (yes), opencode (v1.3.13), argus (up)
- [x] Plan reviewed: `1shot/OPENCODE_ADAPTER_PLAN.md` (Codex-reviewed v2)
- [x] Intake confirmed: all 7 phases, argus up
- [x] PROJECT.md written
- [x] ROADMAP.md written
- [x] 13 tasks created with dependencies
- [x] All 13 tasks completed
- [x] Verify: argus_client reads config, tasks.py works, router resolves, OpenCode loads with oneshot agent
- [x] No Claude Code regressions (no .claude/ files touched)
- [x] Phase 6 (MCP): Argus is REST API only, no MCP interface. Deferred.

## Files Changed

### New Files (7)
- `.opencode/agents/oneshot.md` — Primary agent with dispatch capability
- `.opencode/commands/short.md` — /short command
- `.opencode/commands/handoff.md` — /handoff command
- `.opencode/commands/restore.md` — /restore command
- `.opencode/commands/freesearch.md` — /freesearch command
- `.opencode/commands/doc.md` — /doc command
- `scripts/tasks.py` — Persistent task tracking CLI

### Modified Files (6)
- `.opencode/opencode.json` — Added 3 providers, fixed AGENTS.md reference, set default agent
- `.opencode/commands/conduct.md` — Full rewrite with 5-phase workflow
- `.opencode/commands/research.md` — Uses argus_client instead of raw curl
- `.opencode/agents/cheap-worker.md` — Documented as bounded-only, no dispatch authority
- `core/search/argus_client.py` — Reads config/search.yaml for base_url
- `scripts/janitor-cron.sh` — Updated to run pure-compute jobs, sources API key for onboarding

### Systemd (new, not tracked)
- `~/.config/systemd/user/oneshot-janitor.service`
- `~/.config/systemd/user/oneshot-janitor.timer`

## Notes

- OpenRouter provider verified working via smoke test
- OpenAI provider: quota exceeded (no credits on API key account, same as codex)
- Google/Gemini provider: GEMINI_API_KEY not in vault, needs to be added
- Argus `cheap` mode no longer exists (available: discovery, grounding, recovery, research)
- Janitor timer created but NOT enabled (needs `systemctl --user enable oneshot-janitor.timer`)
