# ONE_SHOT Quick Commands

## Install (First Time)

```bash
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/install.sh | bash
```

## Update (Any Version)

```bash
oneshot-update force
```

Or if you don't have the command:
```bash
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/oneshot-update.sh | bash -s -- force
```

## All Commands

| Command | What it does |
|---------|--------------|
| `oneshot-update` | Check for updates (auto-update if found) |
| `oneshot-update force` | Force update + sync to current project |
| `oneshot-update check` | Just check, don't update |
| `oneshot-update status` | Show version and last check |
| `oneshot-update sync` | Sync to current project (no git pull) |

## From Claude

Inside a Claude Code session:
```
/update
```

This runs `oneshot-update force` + health checks.

## What Gets Updated

- `AGENTS.md` - Synced to your current project
- `~/.local/bin/oneshot-update` - Symlink to update script
- `~/.claude/skills/oneshot` - Symlink to skills

## What Doesn't Change

- `CLAUDE.md` - Project-specific, never touched
- `.claude/rules/` - Project-specific
- `.beads/` - Your task data
- `.claude/continuous/` - Project state

## Rate Limiting

Auto-check is rate limited to once per day. Use `force` to bypass.

## Files

| File | Purpose |
|------|---------|
| `scripts/install.sh` | Main installer |
| `scripts/oneshot-update.sh` | Updater (auto/check/force/sync/status) |
| `.claude/commands/update.md` | `/update` slash command |
