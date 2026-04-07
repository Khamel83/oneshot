# OpenCode Adapter — Conduct Session

**Date**: 2026-04-07
**Plan**: `1shot/OPENCODE_ADAPTER_PLAN.md`
**Previous session**: v2 redesign complete (2026-04-04)

## Goal

Make OpenCode a universal harness for OneShot. Same AGENTS.md, same routing, same dispatch. When Claude tokens run out, switch to OpenCode and keep working.

## Deliverables (all 7 phases)

1. Phase 0: Provider bootstrap + AGENTS.md fix + smoke test
2. Phase 1: Foundation fixes (argus_client config, research.md, cheap-worker bounded)
3. Phase 2: Command translations (/short, /conduct, /handoff, /restore, /freesearch, /doc)
4. Phase 3: Persistent task tracking shim (tasks.json + scripts/tasks.py)
5. Phase 4: Janitor cron (update janitor-cron.sh + systemd timer)
6. Phase 5: OpenCode agent definitions (oneshot primary agent)
7. Phase 6: MCP integration evaluation (Argus as MCP server)

## Acceptance Criteria

- [ ] `opencode` reads AGENTS.md and understands the operating contract
- [ ] `/short` command works in OpenCode
- [ ] `/conduct` command works in OpenCode
- [ ] `python -m core.router.resolve --class implement_small` returns correct routing
- [ ] `python -m core.dispatch.run` dispatches to workers
- [ ] Argus search works via `/freesearch` in OpenCode
- [ ] Task tracking survives session end (tasks.json persists)
- [ ] Janitor runs via cron, outputs to `.janitor/`
- [ ] Claude Code still works exactly as before (no regressions)

## Scope (IN)

- `.opencode/` directory (config, agents, commands)
- `core/search/argus_client.py` (read config)
- `scripts/tasks.py` (new persistent task CLI)
- `scripts/janitor-cron.sh` (update, not deprecated)
- `~/.config/systemd/user/oneshot-janitor.*` (new timer)

## Scope (OUT)

- All `.claude/` files — no changes to Claude Code config
- `core/router/`, `core/task_schema.py` — CLI-agnostic, no changes
- `config/lanes.yaml`, `config/workers.yaml` — no changes
- AGENTS.md — neutral contract stays as-is
- SSH dispatch, OpenCode as MCP server, plugin SDK

## Constraints

- No breaking changes to Claude Code
- Python only for new code
- OpenCode commands use `agent: build` for dispatch capability
- Subagents stay bounded — no dispatch authority

## Riskiest Part

MCP integration (not drop-in between CLIs). Mitigated by treating as optional, testing individually.
