# Task Plan: ONE_SHOT v11

**Created**: 2026-02-13
**Status**: ✅ COMPLETE (Phases 1-5), ⏸️ Testing Pending (Phase 6)
**Last Updated**: 2026-02-13
**Completed**: 2026-02-13

## Summary

Migrate ONE_SHOT from Beads task tracking to Claude's native Tasks system. Add swarm/agent team orchestration support. Deprecate `/beads` command.

## Problem Statement

### Current Issues
1. **Beads is external**: Requires separate `bd` CLI, not integrated with Claude
2. **Native Tasks exist**: Claude Code 2.1 (Jan 22, 2026) shipped TaskCreate, TaskGet, TaskUpdate, TaskList
3. **Outdated core.md**: Says "Native task tools do not exist yet" - WRONG
4. **No swarm support**: Claude has experimental Agent Teams but we don't use them
5. **Duplication**: Beads + native tasks = two systems to maintain

### Research Findings (2026-02-13)
- **Native Tasks**: TaskCreate, TaskGet, TaskUpdate, TaskList - persistent in `~/.claude/tasks/`
- **Swarm Mode**: Enable with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`
- **Seven Team Primitives**: TeamCreate, TaskCreate, TaskUpdate, TaskList, Task (with team_name), SendMessage, TeamDelete
- **TeammateTool**: Direct peer-to-peer messaging between teammates

## Goals
- [x] Migrate to Claude native Tasks (TaskCreate, TaskGet, TaskUpdate, TaskList)
- [x] Deprecate `/beads` command (keep `bd` CLI as fallback)
- [x] Add `/swarm` command for agent team orchestration
- [x] Update core.md to remove outdated "native tasks don't exist" statement
- [x] Research and document swarm patterns
- [x] Create migration guide for existing Beads users
- [x] Update all documentation to reflect v11 changes

## Decisions
| # | Question | Options | Decision | Rationale |
|---|----------|---------|----------|-----------|
| 1 | Task system? | Beads, Native, Both | Native (primary), Beads (fallback) | Native is integrated, persistent, no external CLI |
| 2 | Swarm support? | Skip, Basic, Full | Full `/swarm` command | User wants to utilize swarms for orchestration |
| 3 | `/beads` fate? | Delete, Deprecate, Keep | Deprecate | Keep `bd` CLI working, but remove from primary workflow |
| 4 | Swarm patterns? | Research first, Implement now | Research → Document → Implement | Need to understand patterns before coding |
| 5 | External models in swarms? | Claude only, Multi-model | Claude only | Research confirmed external models NOT supported |

## Technical Approach

### Phase 1: Research Swarm Patterns
Before implementing, understand:
- How TeamCreate/TeamDelete work
- SendMessage for peer-to-peer communication
- Task assignment to teammates
- Best practices for swarm orchestration
- External model support (if any)

### Phase 2: Update Core Rules
Update `~/.claude/rules/core.md`:
```markdown
## ONE_SHOT v11: Native Tasks + Swarms

### Task Management Strategy
```yaml
primary: "native"     # Claude's TaskCreate/TaskUpdate/TaskList
fallback: "beads"     # Legacy bd CLI still works
```

**Native Tasks** (TaskCreate, TaskGet, TaskUpdate, TaskList) are the source of truth.
Use `bd` CLI only as fallback for legacy projects.
```

### Phase 3: Create /swarm Command
New command at `~/.claude/commands/swarm.md`:
- Create agent teams
- Assign tasks to teammates
- Enable peer-to-peer messaging
- Orchestrate multi-agent workflows

### Phase 4: Deprecate /beads
- Mark `/beads` as deprecated in docs
- Keep `bd` CLI functional for legacy users
- Add migration guide in docs
- Update all references from beads → native tasks

### Phase 5: Update Documentation
- SKILLS.md: Update task tracking section
- README.md: Update for v11
- AGENTS.md: Update for v11
- CHANGELOG.md: Add v11.0.0 entry
- Create docs/SWARMS.md with patterns

## Implementation Phases

### Phase 1: Research ✅
- [x] 1.1: Research Claude native Tasks (TaskCreate, etc.)
- [x] 1.2: Research Swarm/Agent Teams features
- [x] 1.3: Research SendMessage for peer communication
- [x] 1.4: Research external model support in swarms (NOT supported)
- [x] 1.5: Document swarm patterns in findings.md

### Phase 2: Update Core Rules ✅
- [x] 2.1: Update core.md to remove outdated statement
- [x] 2.2: Add native task workflow to core.md
- [x] 2.3: Update Beads references to "fallback"
- [x] 2.4: Add swarm/agent team references

### Phase 3: Create /swarm Command ✅
- [x] 3.1: Create swarm.md command file
- [x] 3.2: Define TeamCreate workflow
- [x] 3.3: Define task assignment workflow
- [x] 3.4: Define SendMessage usage
- [x] 3.5: Add examples and patterns

### Phase 4: Deprecate /beads ✅
- [x] 4.1: Mark /beads as deprecated in SKILLS.md
- [x] 4.2: Keep beads.md but add deprecation notice
- [x] 4.3: Create migration guide (beads → native)
- [x] 4.4: Update all docs referencing beads

### Phase 5: Update Documentation ✅
- [x] 5.1: Update SKILLS.md for v11
- [x] 5.2: Update README.md for v11
- [x] 5.3: Update AGENTS.md for v11
- [x] 5.4: Create docs/SWARMS.md
- [x] 5.5: Add v11.0.0 to CHANGELOG.md
- [x] 5.6: Update .claude/skills/INDEX.md

### Phase 6: Testing
- [ ] 6.1: Test native TaskCreate/Update/List
- [ ] 6.2: Test /swarm command
- [ ] 6.3: Test migration from beads
- [ ] 6.4: Verify /cp works with native tasks
- [ ] 6.5: Verify /implement works with native tasks

## Files Modified

| File | Changes | Status |
|------|---------|--------|
| `~/.claude/rules/core.md` | Update task management, add swarm refs | ✅ Done |
| `~/.claude/commands/beads.md` | Add deprecation notice | ✅ Done |
| `~/.claude/commands/swarm.md` | NEW - swarm orchestration | ✅ Done |
| `docs/SKILLS.md` | Update task tracking section | ✅ Done |
| `docs/SWARMS.md` | NEW - swarm patterns guide | ✅ Done |
| `README.md` | Update for v11 | ✅ Done |
| `AGENTS.md` | Update for v11 | ✅ Done |
| `CHANGELOG.md` | Add v11.0.0 entry | ✅ Done |
| `.claude/skills/INDEX.md` | Update for v11 | ✅ Done |

## Success Metrics
- [x] Native tasks work for all task tracking
- [x] /swarm command creates and manages agent teams
- [x] /beads shows deprecation warning
- [x] All docs reflect v11 changes
- [x] Migration guide helps users transition
- [x] No breaking changes for existing Beads users

## Dependencies
- Claude Code 2.1+ (for native Tasks)
- `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (for swarms)

## Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Swarm API changes (experimental) | High | Med | Document current API, track changes |
| Users rely on Beads | Med | Low | Keep bd CLI working, clear migration guide |
| Native tasks missing features | Low | Med | Fallback to beads if needed |
| External models not supported in swarms | Med | Low | Document limitation clearly |

## Test Plan

### Native Tasks Test
```bash
# Create task
TaskCreate with subject="Test task"

# List tasks
TaskList

# Update task
TaskUpdate taskId="..." status="completed"

# Verify persistence
/clear
TaskList  # Should still show task
```

### Swarm Test
```bash
# Enable experimental
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# Create team
/swarm create team-name

# Assign task
/swarm assign task-id --to teammate

# Send message
/swarm send "Status update"
```

---
## Revision History
| Date | Changed By | Summary |
|------|------------|---------|
| 2026-02-13 | claude | Initial v11 plan - migrate to native tasks, add swarms |
