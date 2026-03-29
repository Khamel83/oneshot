#!/bin/bash
# sync-all-projects.sh — Sync oneshot framework to all projects on oci-dev + homelab
# Usage: bash scripts/sync-all-projects.sh [--dry-run] [--local-only] [--homelab-only]

set -uo pipefail

ONESHOT_DIR="${ONESHOT_DIR:-$HOME/github/oneshot}"
GITHUB_DIR="$HOME/github"
HOMELAB_HOST="homelab"
HOMELAB_GITHUB_DIR="/home/khamel83/github"
DRY_RUN=false
LOCAL_ONLY=false
HOMELAB_ONLY=false
LOG=""
FAILED=()
SKIPPED=()
UPDATED=()

# Parse args
for arg in "$@"; do
  case "$arg" in
    --dry-run)     DRY_RUN=true ;;
    --local-only)  LOCAL_ONLY=true ;;
    --homelab-only) HOMELAB_ONLY=true ;;
  esac
done

log() { echo "$1"; LOG+="$1\n"; }
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

  log ""
  log "── $project_name ($project_dir)"

  # Skip if no .claude dir
  if [ ! -d "$claude_dir" ]; then
    warn "no .claude/ directory — skipping"
    SKIPPED+=("$project_name")
    return
  fi

  # Skip oneshot itself
  if [ "$project_name" = "oneshot" ]; then
    warn "skipping oneshot itself"
    SKIPPED+=("$project_name")
    return
  fi

  # Check it's a git repo
  if ! git -C "$project_dir" rev-parse HEAD &>/dev/null; then
    warn "not a git repo — skipping"
    SKIPPED+=("$project_name")
    return
  fi

  if $DRY_RUN; then
    ok "[dry-run] would sync skills, agents, AGENTS.md → $project_name"
    UPDATED+=("$project_name (dry-run)")
    return
  fi

  # 1. Sync skills/
  mkdir -p "$claude_dir/skills"
  if rsync -a --delete "$SKILLS_SRC" "$claude_dir/skills/" 2>/dev/null; then
    ok "skills synced"
    changed=true
  else
    err "skills sync failed"
    FAILED+=("$project_name:skills")
  fi

  # 2. Sync agents/ (only if project already has the dir — don't force it on minimalist projects)
  if [ -d "$claude_dir/agents" ]; then
    if rsync -a --delete "$AGENTS_SRC" "$claude_dir/agents/" 2>/dev/null; then
      ok "agents synced"
      changed=true
    else
      err "agents sync failed"
      FAILED+=("$project_name:agents")
    fi
  else
    ok "no agents/ dir — skipped (intentional)"
  fi

  # 3. Update AGENTS.md (READ-ONLY by spec — always pull from oneshot)
  if [ -f "$project_dir/AGENTS.md" ]; then
    if ! diff -q "$AGENTS_MD_SRC" "$project_dir/AGENTS.md" &>/dev/null; then
      cp "$AGENTS_MD_SRC" "$project_dir/AGENTS.md"
      ok "AGENTS.md updated"
      changed=true
    else
      ok "AGENTS.md already current"
    fi
  fi

  # 4. Ensure settings.local.json exists (empty object is fine)
  if [ ! -f "$claude_dir/settings.local.json" ]; then
    echo '{}' > "$claude_dir/settings.local.json"
    ok "settings.local.json created"
    changed=true
  fi

  # 5. Commit + push if anything changed
  if $changed; then
    cd "$project_dir" || return

    # Warn if there are pre-existing staged changes (we don't want to commit those)
    if ! git diff --cached --quiet 2>/dev/null; then
      warn "pre-existing staged changes detected — stashing them temporarily"
      git stash --staged -m "pre-sync staged changes (auto-stashed by sync-all-projects)" 2>/dev/null || true
    fi

    # Stage ONLY our framework files
    git add .claude/ AGENTS.md 2>/dev/null || true

    # Check if OUR specific files have staged changes
    if git diff --cached --quiet -- .claude/ AGENTS.md 2>/dev/null; then
      ok "no tracked changes after staging — already up to date"
    else
      # Commit ONLY the framework paths (leaves any other staged changes untouched)
      git commit -m "chore: sync oneshot framework (skills, agents, AGENTS.md)" \
        --no-verify -- .claude/ AGENTS.md 2>/dev/null \
        && ok "committed" \
        || { err "commit failed"; FAILED+=("$project_name:commit"); return; }

      git push 2>/dev/null \
        && ok "pushed" \
        || { err "push failed (remote may need manual push)"; FAILED+=("$project_name:push"); }
    fi

    # Restore any pre-existing staged changes we stashed
    if git stash list 2>/dev/null | grep -q "pre-sync staged changes"; then
      git stash pop 2>/dev/null && ok "restored pre-existing staged changes" || warn "stash pop failed — check git stash list"
    fi

    UPDATED+=("$project_name")
  else
    ok "already up to date — nothing to commit"
    UPDATED+=("$project_name (no changes)")
  fi
}

sync_homelab_project() {
  local project_name="$1"
  local remote_dir="$HOMELAB_GITHUB_DIR/$project_name"

  log ""
  log "── [homelab] $project_name ($remote_dir)"

  if $DRY_RUN; then
    ok "[dry-run] would rsync oneshot skills+agents → homelab:$remote_dir"
    UPDATED+=("homelab:$project_name (dry-run)")
    return
  fi

  # Sync skills via rsync over SSH
  ssh "$HOMELAB_HOST" "mkdir -p '$remote_dir/.claude/skills'" 2>/dev/null

  if rsync -az --delete \
      "$SKILLS_SRC" \
      "$HOMELAB_HOST:$remote_dir/.claude/skills/" 2>/dev/null; then
    ok "skills synced"
  else
    err "skills sync failed"
    FAILED+=("homelab:$project_name:skills")
    return
  fi

  # Sync agents/ if dir exists on homelab
  if ssh "$HOMELAB_HOST" "[ -d '$remote_dir/.claude/agents' ]" 2>/dev/null; then
    if rsync -az --delete \
        "$AGENTS_SRC" \
        "$HOMELAB_HOST:$remote_dir/.claude/agents/" 2>/dev/null; then
      ok "agents synced"
    else
      err "agents sync failed"
      FAILED+=("homelab:$project_name:agents")
    fi
  fi

  # Sync AGENTS.md if it exists there
  if ssh "$HOMELAB_HOST" "[ -f '$remote_dir/AGENTS.md' ]" 2>/dev/null; then
    if rsync -az "$AGENTS_MD_SRC" "$HOMELAB_HOST:$remote_dir/AGENTS.md" 2>/dev/null; then
      ok "AGENTS.md synced"
    fi
  fi

  # Ensure settings.local.json
  ssh "$HOMELAB_HOST" "[ -f '$remote_dir/.claude/settings.local.json' ] || echo '{}' > '$remote_dir/.claude/settings.local.json'" 2>/dev/null

  # Commit + push from homelab
  local commit_result
  commit_result=$(ssh "$HOMELAB_HOST" "
    set -e
    cd '$remote_dir' || exit 1
    git add .claude/ AGENTS.md 2>/dev/null || true
    if git diff --cached --quiet 2>/dev/null; then
      echo 'NO_CHANGE'
    else
      git commit -m 'chore: sync oneshot framework (skills, agents, AGENTS.md)' --no-verify 2>/dev/null && echo 'COMMITTED' || echo 'COMMIT_FAILED'
    fi
  " 2>/dev/null || echo "SSH_FAILED")

  # Match on sentinel lines (git commit output may precede them)
  case "$commit_result" in
    *NO_CHANGE*)
      ok "already up to date on homelab"
      UPDATED+=("homelab:$project_name")
      return
      ;;
    *COMMITTED*)
      ok "committed on homelab"
      ssh "$HOMELAB_HOST" "cd '$remote_dir' && git push 2>/dev/null" \
        && ok "pushed from homelab" \
        || { err "push failed from homelab"; FAILED+=("homelab:$project_name:push"); }
      ;;
    *COMMIT_FAILED*)
      err "commit failed on homelab"; FAILED+=("homelab:$project_name:commit")
      ;;
    SSH_FAILED)
      err "SSH command failed"; FAILED+=("homelab:$project_name:ssh")
      ;;
    *)
      err "unexpected result: $commit_result"; FAILED+=("homelab:$project_name:unknown")
      ;;
  esac

  UPDATED+=("homelab:$project_name")
}

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

log "╔══════════════════════════════════════════════╗"
log "║  oneshot sync-all-projects  $(date '+%Y-%m-%d %H:%M')  ║"
log "╚══════════════════════════════════════════════╝"
$DRY_RUN && log "  [DRY RUN — no changes will be made]"
log ""

# ── LOCAL (oci-dev) ────────────────────────────────────────────────────────
if ! $HOMELAB_ONLY; then
  log "▶ LOCAL PROJECTS (oci-dev)"

  # Projects with .claude/ dirs on oci-dev (from audit)
  LOCAL_PROJECTS=(
    arb
    archon
    atlas
    atlas-voice
    atlas_researcher
    dada
    divorce
    docs-cache
    gaas
    homelab
    networth
    oos
    ralex
    trojanhorse
    vig
    WFM
  )

  for project in "${LOCAL_PROJECTS[@]}"; do
    project_dir="$GITHUB_DIR/$project"
    if [ -d "$project_dir" ]; then
      sync_project "$project_dir"
    else
      warn "  $project — not found at $project_dir"
      SKIPPED+=("$project")
    fi
  done
fi

# ── HOMELAB ────────────────────────────────────────────────────────────────
if ! $LOCAL_ONLY; then
  log ""
  log "▶ HOMELAB PROJECTS"

  # Check homelab is reachable
  if ! ssh -o ConnectTimeout=5 "$HOMELAB_HOST" true 2>/dev/null; then
    err "homelab unreachable — skipping remote sync"
    FAILED+=("homelab:unreachable")
  else
    # Projects with .claude/ dirs on homelab (from audit, excluding duplicates we already did)
    HOMELAB_PROJECTS=(
      529
      alex
      arb
      archon
      atlas
      atlas_researcher
      atlas-voice
      divorce
      frugalos
      homelab
      networth
      Notary
      oos
      ralex
      trojanhorse
      vig
    )

    for project in "${HOMELAB_PROJECTS[@]}"; do
      sync_homelab_project "$project"
    done
  fi
fi

# ── SUMMARY ────────────────────────────────────────────────────────────────
log ""
log "═══════════════════════════════════════════"
log "SUMMARY"
log "  Updated : ${#UPDATED[@]}"
log "  Skipped : ${#SKIPPED[@]}"
log "  Failed  : ${#FAILED[@]}"

if [ ${#FAILED[@]} -gt 0 ]; then
  log ""
  log "FAILED:"
  for f in "${FAILED[@]}"; do log "  - $f"; done
fi

if [ ${#SKIPPED[@]} -gt 0 ]; then
  log ""
  log "SKIPPED:"
  for s in "${SKIPPED[@]}"; do log "  - $s"; done
fi

log ""
log "Done."

# Exit with error if any failures
[ ${#FAILED[@]} -eq 0 ]
