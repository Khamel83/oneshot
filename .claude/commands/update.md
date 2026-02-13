# /update — Update ONE_SHOT + Full Health Check

Comprehensive update that handles everything "setup" related:

1. Pull latest ONE_SHOT from GitHub
2. Sync AGENTS.md to current project
3. Re-run install.sh
4. Run heartbeat health checks (CLIs, APIs, secrets, connections)

## Usage

```
/update              # Full update + health check
/update --check      # Just check if update available (no changes)
/update --quick      # Skip heartbeat checks (git pull only)
```

## Works From ANY Version

If you're on an old version without `/update`, run this from any terminal:

```bash
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/update.sh | bash
```

Or if you have the repo:
```bash
~/github/oneshot/scripts/update.sh
```

## Execution

```bash
set -e

# Get current version
CURRENT=$(grep -m1 "ONE_SHOT v" ~/github/oneshot/AGENTS.md 2>/dev/null | grep -oP 'v[\d.]+' || echo "unknown")
echo "Current: ONE_SHOT $CURRENT"

# Pull latest
cd ~/github/oneshot
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/master)

if [ "$LOCAL" = "$REMOTE" ]; then
  echo "Git: already up to date"
else
  echo "Git: pulling latest..."
  git pull origin master
fi

# Get new version
NEW=$(grep -m1 "ONE_SHOT v" AGENTS.md | grep -oP 'v[\d.]+' || echo "unknown")

# Sync AGENTS.md to current project if it has one
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo "$PWD")
if [ -f "$PROJECT_ROOT/AGENTS.md" ] && [ "$PROJECT_ROOT" != "$HOME/github/oneshot" ]; then
  cp ~/github/oneshot/AGENTS.md "$PROJECT_ROOT/AGENTS.md"
  echo "Synced: AGENTS.md → $PROJECT_ROOT"
fi

# Re-run install to update symlinks
bash ~/github/oneshot/install.sh 2>/dev/null

# Run heartbeat health checks
echo ""
echo "=== Health Checks ==="
if [ -x ~/github/oneshot/scripts/heartbeat.sh ]; then
  ~/github/oneshot/scripts/heartbeat.sh --force --safe 2>&1 || true
fi

echo ""
echo "=== Update Complete ==="
echo "Version: $CURRENT → $NEW"
```

## What Gets Updated/Checked

| Category | Actions |
|----------|---------|
| **Git** | Pull latest, sync AGENTS.md |
| **Install** | Re-run install.sh for symlinks |
| **CLIs** | Claude Code, Gemini, Qwen, Codex versions |
| **APIs** | ZAI, Tavily, Exa, Apify, Context7 keys |
| **Secrets** | SOPS/Age key, decrypt test |
| **Connections** | Tailscale, internet |
| **MCPs** | Running servers, config |

## Heartbeat Scripts

The heartbeat runs these check scripts (all in `~/github/oneshot/scripts/`):

| Script | Checks |
|--------|--------|
| `check-clis.sh` | AI CLIs installed and versions |
| `check-apis.sh` | API keys valid and set |
| `check-secrets.sh` | SOPS/Age configuration |
| `check-connections.sh` | Network connectivity |
| `check-mcps.sh` | MCP servers running |
| `check-glm.sh` | GLM model version |
| `sync-secrets.sh` | Secrets synced and decryptable |

## Rate Limiting

The heartbeat has built-in rate limiting (once per 23 hours). Using `/update` forces a run with `--force`.

## Automatic Heartbeat

To have heartbeat run automatically when you `cd` into projects:

```bash
~/github/oneshot/scripts/heartbeat-install.sh
```

This installs a shell hook that runs heartbeat in safe mode (no git pull) at most once per day.

## Files NOT Changed

| File | Reason |
|------|--------|
| `CLAUDE.md` | Project-specific, never touch |
| `.claude/rules/` | Project-specific |
| `.claude/continuous/` | Project state, never touch |
| `.beads/` | Task data, never touch |

## Version Source

Version is defined in ONE place: `AGENTS.md` header line.

```markdown
# ONE_SHOT v10.4
```
