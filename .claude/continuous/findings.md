# Findings: ONE_SHOT v9 Refactor

**Last Updated**: 2026-02-02 12:04

## Research Notes

### 2026-02-02 - Skills Marketplace Research
Researched SkillsMP, Smithery.ai, and Claude Code skills system.

**Key Findings:**
- SkillsMP has 128,427+ skills (as of 2026-02-02)
- ONE_SHOT skills already use standard SKILL.md format
- Claude Code loads skill descriptions into context at startup
- Context bloat: ~15,000 chars for 51 skill descriptions
- Smithery.ai is for MCP servers (tool integrations), not skills

**Relevant Sources:**
- [SkillsMP](https://skillsmp.com) - 128K+ skills directory
- [Claude Code Skills Docs](https://code.claude.com/docs/en/skills) - Official documentation
- [Smithery.ai](https://smithery.ai/) - MCP marketplace (3,435 apps)

## Configuration Notes

### Current ONE_SHOT Skills (48 total)
- Orchestration: 5 skills (front-door, create-plan, continuous-planner, implement-plan, autonomous-builder)
- Task tracking: 4 skills (beads, handoffs, failure-recovery)
- Personal stack: 8 skills (push-to-cloud, remote-exec, secrets, dispatch, etc.)
- Execution: 13 skills (debugger, refactorer, test-runner, code-reviewer, etc.)
- Research/utils: 5 skills (deep-research, freesearch, delegate-to-agent, etc.)
- Meta-skills: 5 skills (auto-updater, skill-analytics, skills-browser, etc.)
- Interview modes: 3 skills (full, quick, smart)

### Files Modified
- `.claude/skills/` - All 48 skill directories

## Errors Encountered

### Context Bloat Issue
**Date**: 2026-02-02
**Error**: Skills loading 15K chars at startup
**Impact**: 20% of context window gone before user says anything
**Solution**: Lazy-load full skill content, only load descriptions
**Status**: In progress

## Open Questions

1. **SkillsMP API format?** - Status: need to research
   - How to query SkillsMP programmatically
   - Is there an API or just web scraping?
   - Could use webReader MCP to fetch skill pages

2. **Skill contracts** - Status: not implemented yet
   - Should skills define input/output explicitly?
   - How to validate skill outputs match expected inputs?

## External References
- [v9 Skills Audit](../docs/research/v9-skills-audit.md)
- [v9 Design Doc](../docs/research/v9-design.md)
- [Skills Marketplace Research](../docs/research/2026-02-02_skills_marketplaces_final.md)
