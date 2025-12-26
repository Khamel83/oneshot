#!/bin/bash
# sync-repos.sh - Background repo synchronization for homelab
# Runs via cron to keep ~/github repos in sync with remotes
#
# Crontab entry (every 15 minutes):
#   */15 * * * * /home/khamel83/github/oneshot/scripts/sync-repos.sh >> /tmp/sync-repos.log 2>&1
#
# Designed for: homelab.deer-panga.ts.net
# Purpose: Keep repos up-to-date so "sync and run" from oci-dev is fast

set -euo pipefail

LOG_PREFIX="[sync-repos $(date +%Y-%m-%d\ %H:%M:%S)]"
GITHUB_DIR="${HOME}/github"
SYNC_LOG="/tmp/sync-repos.log"

# Repos to keep synced (add as needed)
REPOS=(
    "oneshot"
    "homelab"
    # Add more repos here as needed
    # "atlas"
    # "my-project"
)

log() {
    echo "${LOG_PREFIX} $1"
}

sync_repo() {
    local repo="$1"
    local repo_path="${GITHUB_DIR}/${repo}"

    if [ ! -d "$repo_path" ]; then
        log "SKIP: $repo (not cloned at $repo_path)"
        return 0
    fi

    cd "$repo_path"

    # Check for uncommitted changes
    if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
        log "SKIP: $repo (uncommitted changes)"
        return 0
    fi

    # Get current branch
    local branch
    branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
    if [ -z "$branch" ] || [ "$branch" = "HEAD" ]; then
        log "SKIP: $repo (detached HEAD or no branch)"
        return 0
    fi

    # Fetch from origin
    if ! git fetch origin "$branch" --quiet 2>/dev/null; then
        log "ERROR: $repo (fetch failed)"
        return 1
    fi

    # Check if behind
    local behind
    behind=$(git rev-list HEAD..origin/"$branch" --count 2>/dev/null || echo "0")

    if [ "$behind" -gt 0 ]; then
        log "PULL: $repo ($behind commits behind on $branch)"
        if git pull --ff-only origin "$branch" --quiet 2>/dev/null; then
            log "OK: $repo updated"
        else
            log "ERROR: $repo (pull failed - may need manual merge)"
            return 1
        fi
    fi

    return 0
}

# Main
log "Starting sync for ${#REPOS[@]} repos in $GITHUB_DIR"

ERRORS=0
for repo in "${REPOS[@]}"; do
    if ! sync_repo "$repo"; then
        ((ERRORS++)) || true
    fi
done

if [ "$ERRORS" -gt 0 ]; then
    log "Completed with $ERRORS errors"
else
    log "Sync complete"
fi

# Trim log file if too large (> 1MB)
if [ -f "$SYNC_LOG" ]; then
    # Get file size (works on both Linux and macOS)
    local size
    if [[ "$OSTYPE" == "darwin"* ]]; then
        size=$(stat -f%z "$SYNC_LOG" 2>/dev/null || echo "0")
    else
        size=$(stat -c%s "$SYNC_LOG" 2>/dev/null || echo "0")
    fi

    if [ "$size" -gt 1048576 ]; then
        tail -1000 "$SYNC_LOG" > "${SYNC_LOG}.tmp" && mv "${SYNC_LOG}.tmp" "$SYNC_LOG"
        log "Log trimmed (was ${size} bytes)"
    fi
fi

exit $ERRORS
