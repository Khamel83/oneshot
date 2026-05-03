# Handoff: Slash Command & Auth Setup

**Created**: 2026-05-02 18:33
**Context Used**: ~65%

## Quick Summary
You were investigating why `/handoff` isn't a true slash command in Claude Code. We traced through skills, commands, plugins, and MCP — but ran out of context before implementing a solution. Last commit: "config(dispatch): use specific codex models per lane, fix runner -m flag"

## What's Done
- [x] Identified issue: skills are model-invoked, not user-invoked
- [x] Confirmed 16 skills exist in `~/.claude/skills/`
- [x] Verified handoff skill is correctly formatted with `name: handoff` frontmatter
- [x] Checked plugin architecture (blocklist, marketplaces)
- [x] Checked MCP servers (argus configured)

## In Progress
- [ ] Implementing true slash command handler for handoff/restore/short/full
- [ ] Continue research on Claude Code command registration methods

## Not Started
- [ ] Test if `claude agents` command can expose custom agents as slash commands
- [ ] Explore if MCP tool with specific naming could trigger slash-style invocation

## Key Decisions Made
1. Skills vs Commands: Skills are model-invoked only — no `/skill-name` support
2. Plugins: Only blocklist/marketplaces, no custom command plugin system visible
3. MCP: Can add tools but won't create `/cmd` style invocation

## Active Files
- `~/.claude/skills/handoff/SKILL.md` — existing handoff skill
- `~/.claude/settings.json` — has MCP, hooks, effort settings

## Blockers / Open Questions
| # | Question | Status |
|---|---------|--------|
| 1 | How to enable true `/handoff` slash command? | Needs investigation |
| 2 | Can `claude agents` expose commands? | Not tested |

## Learnings & Suggested Updates

### Commands & Workflows That Worked
- `claude --help` shows all CLI options
- `ls ~/.claude/skills/` reveals skill inventory

### Pitfalls Encountered
- Assumed skills were user-invokable — they're not

### Suggested Instruction Updates
- Add to `AGENTS.md`: "Skills are model-invoked. Do NOT expect `/skill-name` to work. Use natural language instead."

## Next Steps (Prioritized)
1. **Immediate**: Research `claude agents` command — can it expose custom agents as slash commands?
2. **Then**: Explore if MCP server with slash-command-like tool names could trigger that behavior
3. **Then**: Consider if this is even possible with current Claude Code architecture

## Resume
/restore @/Users/khamel83/github/oneshot/1shot/handoffs/2026-05-02-1833-oneshot-handoff.md
