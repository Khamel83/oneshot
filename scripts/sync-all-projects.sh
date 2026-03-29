#!/bin/bash
# sync-all-projects.sh — Sync oneshot framework to all local projects, push to GitHub
# Homelab/macmini pick up changes via their existing git pull cron jobs.
#
# Usage: bash scripts/sync-all-projects.sh [--dry-run]

set -uo pipefail

ONESHOT_DIR="${ONESHOT_DIR:-$HOME/github/oneshot}"
GITHUB_DIR="$HOME/github"
DRY_RUN=false
FAILED=()
SKIPPED=()
UPDATED=()

# Parse args
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
  esac
done

log() { echo "$1"; }
ok()  { log "  ✓ $1"; }
warn(){ log "  ⚠ $1"; }
err() { log "  ✗ $1"; }

# ---------------------------------------------------------------------------
# What "syncing" means for a project:
#
#  1. Sync skills/  from oneshot  (rsync --delete, so stale skills removed)
#  2. Sync agents/ from oneshot   (only if project already has agents/)
#  3. Pull latest AGENTS.md from oneshot master (it's READ-ONLY by spec)
#  4. Ensure settings.local.json exists (create if missing)
#  5. git add + commit + push (skip if nothing changed)
#
# Other machines (homelab, macmini) pull these commits via their existing
# repo sync cron jobs — no SSH/rsync needed.
# ---------------------------------------------------------------------------

SKILLS_SRC="$ONESHOT_DIR/.claude/skills/"
AGENTS_SRC="$ONESHOT_DIR/.claude/agents/"
AGENTS_MD_SRC="$ONESHOT_DIR/AGENTS.md"

sync_project() {
  local project_dir="$1"
  local project_name
  project_name=$(basename "$project_dir")
  local claude_dir="$project_dir/.claude"
  local changed=false

  # Skip oneshot itself
  if [ "$project_name" = "oneshot" ]; then
    SKIPPED+=("$project_name")
    return
  fi

  # Check it's a git repo
  if ! git -C "$project_dir" rev-parse HEAD &>/dev/null; then
    SKIPPED+=("$project_name")
    return
  fi

  if $DRY_RUN; then
    ok "$project_name [dry-run]"
    UPDATED+=("$project_name")
    return
  fi

  # 1. Sync skills/
  mkdir -p "$claude_dir/skills"
  if rsync -a --delete "$SKILLS_SRC" "$claude_dir/skills/" 2>/dev/null; then
    changed=true
  else
    err "$project_name: skills sync failed"
    FAILED+=("$project_name:skills")
    return
  fi

  # 2. Sync agents/ (only if project already has the dir)
  if [ -d "$claude_dir/agents" ]; then
    rsync -a --delete "$AGENTS_SRC" "$claude_dir/agents/" 2>/dev/null
  fi

  # 3. Update AGENTS.md if it exists
  if [ -f "$project_dir/AGENTS.md" ]; then
    if ! diff -q "$AGENTS_MD_SRC" "$project_dir/AGENTS.md" &>/dev/null; then
      cp "$AGENTS_MD_SRC" "$project_dir/AGENTS.md"
      changed=true
    fi
  fi

  # 4. Ensure settings.local.json exists
  if [ ! -f "$claude_dir/settings.local.json" ]; then
    echo '{}' > "$claude_dir/settings.local.json"
    changed=true
  fi

  # 5. Commit + push if anything changed
  if ! $changed; then
    return
  fi

  cd "$project_dir" || return

  # Stash any pre-existing staged changes
  local had_stash=false
  if ! git diff --cached --quiet 2>/dev/null; then
    git stash --staged -m "pre-sync staged changes" 2>/dev/null && had_stash=true || true
  fi

  git add .claude/ AGENTS.md 2>/dev/null || true

  if git diff --cached --quiet -- .claude/ AGENTS.md 2>/dev/null; then
    # Restore stash if nothing actually changed
    if $had_stash; then git stash pop 2>/dev/null || true; fi
    return
  fi

  git commit -m "chore: sync oneshot framework (skills, agents, AGENTS.md)" \
    --no-verify -- .claude/ AGENTS.md 2>/dev/null \
    && git push 2>/dev/null \
    && ok "$project_name" \
    || { err "$project_name: commit/push failed"; FAILED+=("$project_name"); }

  # Restore pre-existing staged changes
  if $had_stash; then
    git stash pop 2>/dev/null || true
  fi

  UPDATED+=("$project_name")
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

log "oneshot sync $(date '+%Y-%m-%d %H:%M')"
$DRY_RUN && log "  [DRY RUN]"

# Auto-discover projects with .claude/ dirs (top-level only)
mapfile -t PROJECTS < <(
  for d in "$GITHUB_DIR"/*/; do
    [ -d "$d/.claude" ] && echo "$d"
  done 2>/dev/null | sort
)

log "  ${#PROJECTS[@]} project(s) with .claude/"

for project_dir in "${PROJECTS[@]}"; do
  sync_project "$project_dir"
done

# Summary
log ""
log "synced: ${#UPDATED[@]} | skipped: ${#SKIPPED[@]} | failed: ${#FAILED[@]}"

if [ ${#FAILED[@]} -gt 0 ]; then
  log "FAILED: ${FAILED[*]}"
fi

log ""

[ ${#FAILED[@]} -eq 0 ]
