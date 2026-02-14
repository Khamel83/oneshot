# ONE_SHOT Core Rules

These rules load for every project.

## STOP BEING CLEVER

**YOU ARE A ROBOT. JUST DO THE SIMPLE THING FAST FIRST.**

- Don't edit databases directly when there's a UI
- Don't write scripts when a CLI exists
- Don't debug for an hour when `docker pull` might fix it
- If there's a 30-second solution, do that before the 30-minute solution

---

## Intelligent Delegation (v12.1)

Before delegating, assess (complexity, criticality, uncertainty). After delegation, verify the result.
Full protocol: `~/.claude/rules/delegation.md`

- **Assess**: Is this worth delegating? Low complexity → handle inline.
- **Verify**: Spot-check search results, review diffs, check exit codes.
- **Escalate**: original → inline → human (3 attempts max, change strategy each time).
- **Log**: Automatic via SubagentStop hook → `.claude/delegation-log.jsonl`

---

## Work Discipline

- **Plan first**: Always start with a plan before coding. Think, then do.
- **Commit per task**: Don't batch commits to end-of-session. Commit each completed task immediately.
- **Keep tasks small**: Break work so each subtask completes well within context. If it's too big, split it.
- **Vanilla over complex**: Simple direct work beats elaborate multi-agent orchestration for small tasks.

---

## Documentation-First Coding

**CRITICAL RULE:** Before writing code that uses external APIs, libraries, or configuration syntax, you MUST check the current documentation.

### Process
1. Check local cached docs: `~/homelab/docs/services/<service-name>/`
2. If insufficient, use WebFetch/WebSearch for current docs
3. Verify version compatibility
4. Write code using current syntax, not training data

---

## AGENTS.md Rule (CRITICAL)

**AGENTS.md is READ-ONLY in all projects.**

```bash
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/AGENTS.md > AGENTS.md
```

| File | Purpose | Editable? |
|------|---------|-----------|
| `AGENTS.md` | ONE_SHOT spec (universal) | **NO** - curl from oneshot |
| `CLAUDE.md` | Project-specific Claude instructions | YES |

---

## ONE_SHOT v11: Native Tasks + Swarms

**Core Philosophy**: Use Claude's native features first, external tools as fallback.

### Task Management Strategy
```yaml
primary: "native"     # Claude's TaskCreate/TaskUpdate/TaskList
fallback: "beads"     # Legacy bd CLI for edge cases
```

**Native Tasks** (TaskCreate, TaskGet, TaskUpdate, TaskList) shipped in Claude Code 2.1 (Jan 2026).
- Persistent in `~/.claude/tasks/`
- Survive `/clear` and context compression
- Use these for all task tracking

### Session Start Protocol
1. `TaskList` - Check for pending/in_progress tasks
2. Pick highest-priority unblocked task
3. `TaskUpdate` to set status="in_progress"

### Session End Protocol
1. `git status` - check changes
2. `git add <files>` - stage changes
3. `git commit -m "..."` - commit code
4. `TaskUpdate` - mark task completed or update notes
5. `git push` - push to remote

### Swarm Mode (Experimental)
Enable with: `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`

Use `/swarm` for multi-agent orchestration:
- TeamCreate - Create agent team
- SendMessage - Peer-to-peer messaging
- Task assignment to teammates

---

## ONE_SHOT Skills System

**Skills installed at**: `~/.claude/skills/oneshot/`

1. **AGENTS.md** - Skeleton key for orchestration
2. **Skills** (21 total) - Loaded on-demand (~100 tokens each)
3. **Secrets** - SOPS/Age encrypted in oneshot/secrets/

### Skill Discovery
| Intent | Skill |
|--------|-------|
| "new project", "build me" | `oneshot-core` |
| "resume", "checkpoint" | `resume-handoff` |
| "deploy", "push to cloud" | `push-to-cloud` |
| "refactor", "clean up" | `refactorer` |
| "bug", "broken" | `debugger` |

---

## Beads: Legacy Fallback

**DEPRECATED in v11**: Beads (`bd` CLI) is now a fallback. Use native Tasks instead.

Use Beads only when:
- Working on legacy projects that already use beads
- Native tasks are unavailable for some reason

### Beads Commands (Legacy)
- `bd ready` - List ready tasks
- `bd create "task"` - Create task
- `bd sync` - Commit bead changes
- `bv` - TUI viewer

### Migration
Existing Beads users: See `/beads` deprecation notice for migration guide.
