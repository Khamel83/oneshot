# Core Rules

**Authoritative source**: `docs/instructions/core.md`

See @docs/instructions/core.md

## Claude-Specific Additions

- AGENTS.md is READ-ONLY: `curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/AGENTS.md > AGENTS.md`
- Swarm Mode (experimental): `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Beads (deprecated): Use native Tasks instead

## Shared Memory

At session start, read `.claude/memory/memory.md`.
When you discover something useful for other agents, append a dated entry.
