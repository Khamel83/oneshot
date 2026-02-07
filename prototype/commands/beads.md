# /beads — Persistent Task Tracking

Git-backed task tracking with dependencies. Survives /clear, session restarts, and terminal disconnects.

## Why Beads (not TODO.md)

| Aspect | TODO.md | Beads |
|--------|---------|-------|
| Persistence | Session only | Git-backed |
| Dependencies | None | Full graph |
| Ready detection | Manual | `bd ready` |
| Survives /clear | No | Yes |

Use TODO.md for immediate visibility. Use beads for persistent state.

## Session Start

```bash
bd sync                        # Pull latest state
bd ready --json                # See unblocked tasks
bd update <id> --status in_progress --json  # Claim a task
```

## During Work

```bash
bd create "Task title" -p 1 -t task --json       # Create task
bd dep add <child> <parent> --type blocks         # Add dependency
bd close <id> --reason "Completed" --json         # Complete task
bd sync                                            # Push changes
```

Priority: 0=critical, 1=high, 2=normal, 3=low, 4=backlog

## Session End (CRITICAL)

```bash
bd sync  # ALWAYS sync before ending
```

## Breaking Down Work

```bash
# Create epic
bd create "User Auth" -t epic --json  # → bd-a1b2

# Create child tasks
bd create "Login endpoint" --deps parent:bd-a1b2 -p 1 --json
bd create "Logout endpoint" --deps parent:bd-a1b2 -p 1 --json
```

## Multi-Agent Coordination

Hash-based IDs (bd-xxxx) prevent conflicts between agents.

```bash
# Agent claims task
bd update <id> --status in_progress --json && bd sync

# Other agents see the claim immediately
bd sync && bd ready --json
```

## Recovery After Disconnect

```bash
bd sync
bd list --status in_progress --json  # What was in progress?
bd ready --json                       # What's next?
```

## Initialize in New Project

```bash
bd init --stealth  # Keeps .beads/ local
```
