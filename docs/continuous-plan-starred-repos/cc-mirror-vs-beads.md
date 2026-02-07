# CC-MIRROR Task Tools vs Beads - Comparison

## Executive Summary

After testing `claudesp` (which revealed native task tools), the answer is clear:

**Recommendation: Use Claude's native task tools when available. Beads as fallback.**

---

## Native Claude Task Tools (claude-sneakpeek/swarm mode)

```bash
claudesp -p "List your available tools" revealed:
```

| Tool | Purpose |
|------|---------|
| `TaskStatus` | List tasks, labels, time estimates |
| `TaskCreate` | Create task with title, description, assignee, labels, priority |
| `TaskUpdate` | Update existing task (assignee, labels, priority) |
| `TaskDelete` | Delete task by ID |

### Advantages
- ✅ **Built-in** - No external dependency
- ✅ **Feature-flagged** - Available in swarm mode (future of Claude)
- ✅ **Clean API** - Designed specifically for Claude Code
- ✅ **Agent-aware** - Native subagent spawning integration

### Disadvantages
- ❌ **Requires swarm mode** - Not in stable Claude Code yet
- ❌ **Unclear release timeline** - Feature-flagged, undocumented
- ❌ **No git sync** - Tasks stored in Claude sessions only

---

## CC-MIRROR Task Tools (Legacy 1.6.3)

CC-MIRROR wraps the same native tools with additional features:

| Feature | Description |
|---------|-------------|
| Project-scoped tasks | Automatic isolation by project folder |
| CLI commands | `npx cc-mirror tasks` for management |
| Task graph | Dependencies between tasks |
| "Conductor" pattern | Parallel agent spawning |

### Advantages
- ✅ **Proven pattern** - Works in production
- ✅ **Project isolation** - Tasks scoped to folders
- ✅ **CLI access** - Can manage outside Claude sessions

### Disadvantages
- ❌ **Legacy mode** - Requires old Claude 1.6.3
- ❌ **External tool** - Another dependency
- ❌ **Complex setup** - Isolated variants, custom providers

---

## Beads (/beads command)

Git-backed task tracking system used in ONE_SHOT:

| Feature | Description |
|---------|-------------|
| Git-backed | Tasks stored in `.beads/` folder |
| JSONL + SQLite | Hybrid storage for speed + sync |
| Labels | `starred-repos`, `lesson`, etc. |
| Priorities | P0-P4 for task ranking |

### Advantages
- ✅ **Works everywhere** - No feature flags needed
- ✅ **Git sync** - Tasks version-controlled
- ✅ **Proven** - Used successfully in ONE_SHOT
- ✅ **CLI access** - `bd` commands work anywhere

### Disadvantages
- ❌ **External tool** - Requires beads installation
- ❌ **Not Claude-aware** - No integration with subagent spawning
- ❌ **More setup** - Need to `bd init` per project

---

## Comparison Matrix

| Aspect | Native Tools | CC-MIRROR | Beads |
|--------|--------------|-----------|-------|
| **Availability** | Swarm mode only | Legacy 1.6.3 | Always |
| **Git sync** | No | No | Yes |
| **Project-scoped** | Session-based | Folder-based | Repo-based |
| **CLI access** | No | Yes | Yes |
| **Integration** | Native (TeammateTool) | Wrapped | External |
| **Setup effort** | Zero | Medium | Low |
| **Future-proof** | ✅ Yes (Anthropic) | ❌ No (legacy) | ⚠️ Maybe |

---

## Recommendation for ONE_SHOT v11

### Phase 1: Wait for Native (Current Stance)
```markdown
ONE_SHOT v11 Position:
- Native Claude task tools are coming (validated via claude-sneakpeek)
- No need to build custom orchestration
- Use beads for now, deprecate when native tools ship
```

### Phase 2: Hybrid Approach (Transition)
```yaml
task_management:
  preferred: "native"  # Use Claude's TaskCreate/Update when available
  fallback: "beads"    # Use /beads when native unavailable
  detection:           # Auto-detect swarm mode
    check_tool: "TaskCreate"
    on_available: "native"
    on_unavailable: "beads"
```

### Phase 3: Deprecate Beads (Future)
Once native tools are stable:
- Remove /beads command
- Document native tool usage
- Migration guide for existing beads

---

## Decision Criteria

| Question | Native Tools | Beads |
|----------|--------------|-------|
| Can I use it today? | Only in swarm mode | Yes |
| Will it exist in 1 year? | Yes (Anthropic roadmap) | Maybe (external dep) |
| Does it sync with git? | No | Yes |
| Is it Claude-aware? | Yes | No |

**Conclusion**: Native tools are the future. Beads is a bridge. ONE_SHOT v11 should document this path and not over-invest in beads.

---

## Action Items

1. ✅ **Document "wait for native" stance** - Update CLAUDE.md
2. ✅ **Validate native tools exist** - Done via claude-sneakpeek
3. ⏳ **Create migration guide** - Native tools when available, beads now
4. ⏳ **Update /beads command** - Add deprecation notice
5. ⏳ **Test hybrid detection** - Auto-switch when native available
