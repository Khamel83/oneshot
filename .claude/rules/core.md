# ONE_SHOT Core Rules

These rules load for every project.

## STOP BEING CLEVER

**YOU ARE A ROBOT. JUST DO THE SIMPLE THING FAST FIRST.**

- Don't edit databases directly when there's a UI
- Don't write scripts when a CLI exists
- Don't debug for an hour when `docker pull` might fix it
- If there's a 30-second solution, do that before the 30-minute solution

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

## ONE_SHOT v11: "Wait for Native" Strategy

**Core Philosophy**: Focus on developer productivity, wait for Claude's native features.

### Task Management Strategy
```yaml
preferred: "native"  # Use Claude's TaskCreate when available
fallback: "beads"    # Use /beads when native unavailable
```

### Native Task Tools (When Available)
| Tool | Purpose |
|------|---------|
| `TaskStatus` | List tasks, labels, time estimates |
| `TaskCreate` | Create with title, description, assignee, labels, priority |
| `TaskUpdate` | Update assignee, labels, priority, time estimate |
| `TaskDelete` | Delete task by ID |
| `Task(subagent_type)` | Spawn bash, explore, plan agents |
| `TeammateTool` | spawnTeam, discoverTeams, requestJoin |

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

## Beads Context

```python
import json
bd = json.loads(BEADS_JSON)

# Session close protocol
# ["status","add","sync","commit","sync","push"]

# Ready tasks
bd.ready  # [{"id":"1","title":"..."}, ...]
```

**Session close checklist:**
1. `git status` - check changes
2. `git add <files>` - stage changes
3. `bd sync` - commit beads
4. `git commit -m "..."` - commit code
5. `bd sync` - commit new beads changes
6. `git push` - push to remote
