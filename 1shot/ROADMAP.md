# OpenCode Adapter — Roadmap

**Date**: 2026-04-07
**Plan**: `1shot/OPENCODE_ADAPTER_PLAN.md`

## Execution Order

Based on Codex review corrections: config/agents before commands, providers first.

### Phase 0: Provider + Config Bootstrap
- 0A: Add openrouter/openai/google providers to opencode.json
- 0B: Fix AGENTS.md reference (direct path, not indirection)
- 0C: Smoke test — verify providers respond

### Phase 5A: OneShot Primary Agent
- Define `.opencode/agents/oneshot.md` with dispatch capability via bash

### Phase 1: Foundation Fixes
- 1A: argus_client.py reads config/search.yaml
- 1B: research.md uses argus_client instead of raw curl
- 1D: cheap-worker.md — keep bash:false, document as bounded-only

### Phase 2: Command Translations
- 2A: /short command
- 2B: /conduct command (rewrite)
- 2C: /handoff command
- 2D: /restore command
- 2E: /freesearch command
- 2F: /doc command

### Phase 3: Persistent Task Tracking
- 3A: scripts/tasks.py CLI
- 3B: 1shot/tasks.json format + session start loading

### Phase 4: Janitor Cron
- 4A: Update janitor-cron.sh (remove DEPRECATED, wire pure-compute jobs)
- 4B: systemd timer

### Phase 6: MCP Integration
- 6A: Evaluate Argus as MCP server
- 6B: Add if viable, skip if not

## Dependencies

```
Phase 0 (providers, AGENTS.md) → Phase 5A (oneshot agent) → Phase 1 (foundation) → Phase 2 (commands)
Phase 3 (tasks.py) — independent, can run anytime after Phase 0
Phase 4 (janitor) — independent
Phase 6 (MCP) — last, after everything works
```

## Success Criteria

See PROJECT.md.
