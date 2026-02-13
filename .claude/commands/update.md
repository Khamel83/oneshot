# /update — Update ONE_SHOT + Health Check

Runs `oneshot-update force` + heartbeat health checks.

## Usage

```
/update              # Force update + health check
/update --check      # Just check if update available
/update --status     # Show current version/state
```

## Execution

```bash
# Run the updater
oneshot-update force

# Run health checks
echo ""
echo "=== Health Check ==="
~/github/oneshot/scripts/heartbeat.sh --force --safe 2>&1 || true
```

## All Update Commands

| Command | What it does |
|---------|--------------|
| `oneshot-update` | Check, auto-update if available |
| `oneshot-update force` | Force update + sync to project |
| `oneshot-update check` | Just check, don't update |
| `oneshot-update status` | Show version, last check |
| `oneshot-update sync` | Sync to current project only |

## Works From ANY Version

If `/update` doesn't exist, run from terminal:

```bash
# Quick install (first time)
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/install.sh | bash

# Force update (any version)
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/oneshot-update.sh | bash -s -- force
```

## What Gets Updated

| File | Action |
|------|--------|
| `AGENTS.md` | Synced to current project |
| `~/.local/bin/oneshot-update` | Symlink created |
| `~/.claude/skills/oneshot` | Symlink created |

## What Doesn't Change

- `CLAUDE.md` - Project-specific
- `.claude/rules/` - Project-specific
- `.beads/` - Your task data
