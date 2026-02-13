# Findings: ONE_SHOT v11

**Last Updated**: 2026-02-13

## Research Notes

### 2026-02-13 - Native Tasks & Swarm Research
Researched Claude Code 2.1 native features for v11 migration.

**Native Tasks (TaskCreate, TaskGet, TaskUpdate, TaskList):**
- Shipped in Claude Code 2.1 (Jan 22, 2026)
- Persistent in `~/.claude/tasks/`
- Four primitives: TaskCreate, TaskGet, TaskUpdate, TaskList
- Tasks survive /clear and context compression
- No external CLI needed (unlike Beads)

**Swarm Mode / Agent Teams (Experimental):**
- Enable with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- Seven team primitives:
  1. **TeamCreate** - Create a team of agents
  2. **TaskCreate** - Create task with team_name parameter
  3. **TaskUpdate** - Update task status
  4. **TaskList** - List team tasks
  5. **Task** (with team_name) - Run task as teammate
  6. **SendMessage** - Peer-to-peer messaging between teammates
  7. **TeamDelete** - Delete a team
- **TeammateTool**: Direct peer-to-peer messaging
- Teammates can message each other, not just report to parent
- Shared task list across team

**Key Differences from Beads:**
| Feature | Beads | Native Tasks |
|---------|-------|--------------|
| CLI | External `bd` | Integrated |
| Persistence | SQLite | `~/.claude/tasks/` |
| Swarm support | No | Yes (experimental) |
| Peer messaging | No | Yes (SendMessage) |
| Dependencies | pip install | Built-in |

**External Model Support:**
- **NOT supported** - Agent teams only use Claude models
- Can specify which Claude model: "Use Sonnet for each teammate"
- No mention of GPT, Gemini, or other external models in docs

**Swarm Patterns (Best Practices):**
1. **Research & Review** - Multiple teammates investigate different aspects simultaneously
2. **Competing Hypotheses** - Teammates test different theories, challenge each other
3. **Cross-Layer Coordination** - Frontend, backend, tests each owned by different teammate
4. **New Modules** - Each teammate owns a separate piece

**Display Modes:**
- `in-process` - All in main terminal, Shift+Up/Down to select teammate
- `split-panes` - Each teammate in own pane (requires tmux or iTerm2)

**Key Workflows:**
- Plan approval mode: Teammate plans first, lead approves before implementation
- Delegate mode: Lead only coordinates (Shift+Tab), doesn't implement
- Direct messaging: Select teammate, type to message
- Task claiming: Lead assigns OR teammates self-claim unblocked tasks

**Limitations:**
- No session resumption with in-process teammates
- Task status can lag (manual fix sometimes needed)
- One team per session
- No nested teams
- Lead is fixed (can't transfer leadership)

---

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

### Current ONE_SHOT Skills (21 total as of v10.5)
- Planning: /interview, /cp, /run-plan, /implement
- Context: /handoff, /restore, /sessions
- Tasks: /beads (to be deprecated in v11)
- Debug: /diagnose, /codereview
- Multi-file: /batch, /remote
- Research: /research, /freesearch, /doc, /skill-discovery
- Communication: /audit, /secrets
- Thinking: /think
- Stack: /stack-setup, /update

### v11 Changes
- Add: /swarm (agent team orchestration)
- Deprecate: /beads (keep as fallback)
- Primary task system: Native Tasks (TaskCreate/Update/List)

## Errors Encountered

### Context Bloat Issue (v9)
**Date**: 2026-02-02
**Error**: Skills loading 15K chars at startup
**Impact**: 20% of context window gone before user says anything
**Solution**: Lazy-load full skill content, only load descriptions
**Status**: Resolved in v10 with progressive disclosure rules

### Outdated core.md (v11)
**Date**: 2026-02-13
**Error**: core.md says "Native task tools do not exist yet"
**Impact**: Using outdated Beads when better native option exists
**Solution**: Update core.md for v11, migrate to native tasks
**Status**: In progress

## Open Questions

1. **External models in swarms?** - Status: needs testing
   - Can swarms use non-Claude models?
   - How to configure if supported?

2. **Swarm patterns** - Status: needs documentation
   - Best practices for team orchestration
   - When to use SendMessage vs parent reporting
   - Task assignment patterns

## External References
- [Claude Code Release Notes](https://docs.anthropic.com/claude-code/release-notes) - v2.1 native tasks
- [v11 Task Plan](./task_plan.md) - Current plan
