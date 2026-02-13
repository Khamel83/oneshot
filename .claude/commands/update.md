# /update — Update ONE_SHOT from GitHub

Syncs the latest ONE_SHOT version from GitHub to:
1. `~/github/oneshot` (source repo)
2. Current project's `AGENTS.md`
3. Global rules/skills if changed

## Usage

```
/update              # Pull latest and sync to current project
/update --check      # Check if update available (don't apply)
/update --global     # Update global ~/.claude/ only
/update --project    # Update current project only (no git pull)
```

## Execution

```bash
# Check current version
CURRENT=$(grep -m1 "ONE_SHOT v" ~/github/oneshot/AGENTS.md 2>/dev/null | grep -oP 'v[\d.]+' || echo "unknown")
echo "Current: $CURRENT"

# Pull latest
cd ~/github/oneshot
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/master)

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "Already up to date ($CURRENT)"
  exit 0
fi

git pull origin master

# Get new version
NEW=$(grep -m1 "ONE_SHOT v" AGENTS.md | grep -oP 'v[\d.]+' || echo "unknown")
echo "Updated: $NEW"

# Sync AGENTS.md to current project if in a git repo
if [ -f "AGENTS.md" ] && git rev-parse --git-dir > /dev/null 2>&1; then
  cp ~/github/oneshot/AGENTS.md ./AGENTS.md
  echo "Synced AGENTS.md to $(pwd)"
fi

# Re-run install to update symlinks
bash ~/github/oneshot/install.sh

echo "Done. Updated ONE_SHOT $CURRENT → $NEW"
```

## What Gets Updated

| File | Scope |
|------|-------|
| `AGENTS.md` | Current project |
| `~/.local/bin/oneshot*` | Global commands |
| `~/.claude/skills/oneshot` | Skill symlinks |

## Files NOT Updated Automatically

| File | Reason |
|------|--------|
| `CLAUDE.md` | Project-specific, manual merge |
| `.claude/rules/` | Project-specific |
| `.claude/continuous/` | Project state, never touch |

## Versioning

Version is defined in ONE place: `AGENTS.md` header line.

```markdown
# ONE_SHOT v10.4
```

All other version references should be removed or point to AGENTS.md.
