---
name: auto-updater
description: "Automatically update ONE_SHOT skills from GitHub on session start. Checks once per day and updates silently. Use /update to force update."
allowed-tools: Bash, Read
---

# Auto-Updater

Keep ONE_SHOT skills up-to-date by automatically pulling from GitHub.

## Behavior

**Fully Automatic:**
- On every session start, checks if >24 hours since last check
- If update available, pulls it AUTOMATICALLY (no prompting)
- Notifies you after update: "ONE_SHOT has been auto-updated"
- Then doesn't check again for 24 hours

**Manual Override:**
- `/update` or `oneshot-update.sh force` - Force update now
- `/update status` - Show current version info

## How It Works

1. **Session Start Hook** (via session-context.sh):
   - Runs `oneshot-update.sh auto`
   - If rate limit not hit AND update available → auto-update
   - Stashes local changes, pulls, restores
   - All happens silently in background

2. **Rate Limiting**:
   - Checks cached to once per 24 hours
   - Cache file: `~/github/oneshot/.cache/last-update-check`
   - Won't slow down every session, just first of the day

## Commands

```bash
# Check for updates (rate-limited)
~/.claude/skills/oneshot/auto-updater/oneshot-update.sh check

# Force check (bypasses rate limit)
~/.claude/skills/oneshot/auto-updater/oneshot-update.sh force-check

# Perform update
~/.claude/skills/oneshot/auto-updater/oneshot-update.sh update

# Show status
~/.claude/skills/oneshot/auto-updater/oneshot-update.sh status
```

## Session Start Integration

Add to hooks-manager or session-context.sh:

```bash
# Check for ONE_SHOT updates
UPDATE_SCRIPT="$HOME/.claude/skills/oneshot/auto-updater/oneshot-update.sh"
if [ -x "$UPDATE_SCRIPT" ]; then
    UPDATE_STATUS=$("$UPDATE_SCRIPT" check 2>/dev/null)
    if echo "$UPDATE_STATUS" | grep -q "UPDATE_AVAILABLE"; then
        CONTEXT="$CONTEXT\n\n## ONE_SHOT Update Available\nNew version available. Run /update or say 'update oneshot' to get latest skills."
    fi
fi
```

## Workflow

### Automatic Check (Session Start)

```
Session starts
  → oneshot-update.sh check
  → If UPDATE_AVAILABLE:
       "ONE_SHOT update available. Run /update to get latest skills."
  → If UP_TO_DATE or RATE_LIMITED:
       (silent, no message)
```

### Manual Update

```
User: "update oneshot"

1. Force check for updates
2. If update available:
   "Update available: [new features/fixes summary]
    Update now? (This will pull latest from GitHub)"
3. On confirmation:
   → Run oneshot-update.sh update
   → Report result
4. If already up-to-date:
   "ONE_SHOT is already at the latest version (v7.4)"
```

## Rate Limiting

- Checks cached to once per 24 hours
- Cache file: `~/github/oneshot/.cache/last-update-check`
- Force check bypasses cache
- Prevents API rate limits and unnecessary network calls

## Error Handling

| Scenario | Behavior |
|----------|----------|
| No internet | Skip silently |
| GitHub API rate limited | Skip silently, retry next session |
| Local changes conflict | Stash, update, pop stash |
| Merge conflict | Abort update, report to user |

## Configuration

Environment variables:

```bash
ONESHOT_DIR="$HOME/github/oneshot"      # Source repo location
SKILLS_SYMLINK="$HOME/.claude/skills/oneshot"  # Skills symlink
```

## What Gets Updated

- All skills in `.claude/skills/`
- Agent definitions in `.claude/agents/`
- AGENTS.md (orchestration spec)
- Hooks and scripts

## What Stays Local

- Your project files
- CLAUDE.md (project-specific)
- Secrets in `secrets/` (encrypted)
- Local `.cache/` files

## Keywords

update, upgrade, oneshot, latest, version, sync, pull, github, auto-update
