# Implementation Context

## Project
Build `/conduct` — a multi-model PMO orchestrator skill for the ONE_SHOT framework.

## Goals
- [ ] Create `1shot/` folder template structure (STATE.md, ROADMAP.md, config.json)
- [ ] Write `~/.claude/skills/conduct/SKILL.md` following `/full`'s format
- [ ] Register `/conduct` in `~/.claude/skills/INDEX.md`
- [ ] Smoke test: invoke `/conduct`, verify intake questions fire, verify `1shot/` created

## Architecture
- **Skill location**: `~/.claude/skills/conduct/SKILL.md`
- **Templates**: `~/.claude/skills/conduct/templates/`
- **Project state folder**: `1shot/` (in each project root, sorts to top)
- **Providers**: Claude (orchestrator) + Codex (`codex exec --full-auto`) + Gemini (printf pipe)
- **Loop**: synchronous bash CLI calls, no daemon
- **Routing**: 7-tier, simplified for 3 providers
- **Quality gate**: 75% consensus
- **Circuit breaker**: task fails 3x → ISSUES.md blocker → skip

## Sources
- Claude Octopus (`nyldn/claude-octopus`): dispatch patterns, .octo/ structure, consensus gate
- Ralph Wiggum (`frankbria/ralph-claude-code`): loop philosophy, circuit breaker
- `/full` SKILL.md: structural format to follow

## Milestones
1. Templates created (`1shot/` folder structure) - ✅ complete
2. SKILL.md written (full operator) - ✅ complete
3. INDEX.md updated - ✅ complete

## Decisions
- 2026-03-20 Use `1shot/` not `.octo/` — user wants visible folder, sorts to top
- 2026-03-20 Synchronous bash calls — no daemon, no async, Claude waits inline
- 2026-03-20 Hooks only for session recovery (80% context → handoff)
- 2026-03-20 Drop Perplexity — Pro plan gives only $5/mo API credit, not worth integrating
- 2026-03-20 PROJECT.md template inline in SKILL.md (same pattern as /full)

## Progress Log
- 2026-03-20 Started implementation via /full operator
- 2026-03-20 Created templates: STATE.md, ROADMAP.md, config.json
- 2026-03-20 Wrote ~/.claude/skills/conduct/SKILL.md
- 2026-03-20 Registered /conduct in INDEX.md
- 2026-03-20 All milestones complete
