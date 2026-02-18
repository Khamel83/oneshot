#!/bin/bash
# oneshot-update.sh - Auto-update ONE_SHOT from GitHub
# Runs on session start, AUTO-UPDATES when new version found
# Rate limited to once per day

set -uo pipefail

ONESHOT_DIR="${ONESHOT_DIR:-$HOME/github/oneshot}"
SKILLS_SYMLINK="${SKILLS_SYMLINK:-$HOME/.claude/skills/oneshot}"
CACHE_FILE="${ONESHOT_DIR}/.cache/last-update-check"
LOG_FILE="${ONESHOT_DIR}/.cache/update.log"
GITHUB_REPO="Khamel83/oneshot"
UPDATE_CHECK_INTERVAL=86400  # 24 hours in seconds

# Detect current project directory (for syncing skills/agents)
# Uses ONESHOT_PROJECT_DIR env var, or finds .claude in current dir ancestry
detect_project_dir() {
    if [ -n "${ONESHOT_PROJECT_DIR:-}" ]; then
        echo "$ONESHOT_PROJECT_DIR"
        return 0
    fi

    # Walk up from current directory looking for .claude folder
    local dir="$PWD"
    while [ "$dir" != "/" ]; do
        if [ -d "$dir/.claude" ]; then
            echo "$dir"
            return 0
        fi
        dir=$(dirname "$dir")
    done

    # No .claude found, return empty (no project to sync to)
    echo ""
}

# Ensure cache directory exists
mkdir -p "$(dirname "$CACHE_FILE")"

# Log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Check if we should run (rate limiting)
should_check() {
    if [ ! -f "$CACHE_FILE" ]; then
        return 0  # Never checked, should check
    fi

    local last_check=$(cat "$CACHE_FILE" 2>/dev/null || echo 0)
    local now=$(date +%s)
    local diff=$((now - last_check))

    if [ "$diff" -gt "$UPDATE_CHECK_INTERVAL" ]; then
        return 0  # Time to check
    else
        return 1  # Too soon
    fi
}

# Get remote HEAD commit hash
get_remote_hash() {
    curl -s --connect-timeout 5 "https://api.github.com/repos/${GITHUB_REPO}/commits/master" \
        | grep '"sha"' | head -1 | cut -d'"' -f4
}

# Get local HEAD commit hash
get_local_hash() {
    git -C "$ONESHOT_DIR" rev-parse HEAD 2>/dev/null
}

# Perform update (silent, automatic)
do_update() {
    cd "$ONESHOT_DIR" || exit 1

    log "Starting auto-update..."

    # Stash any local changes
    git stash push -m "auto-updater stash $(date +%Y%m%d%H%M%S)" 2>/dev/null || true

    # Pull latest
    if git pull --rebase origin master 2>>"$LOG_FILE"; then
        log "Update successful"

        # Update the skills symlink if needed
        if [ ! -L "$SKILLS_SYMLINK" ]; then
            ln -sf "$ONESHOT_DIR/.claude/skills" "$SKILLS_SYMLINK"
            log "Updated symlink: $SKILLS_SYMLINK"
        fi

        # Create symlinks for all commands
        COMMANDS_DIR="$HOME/.claude/commands"
        mkdir -p "$COMMANDS_DIR"
        for cmd in "$ONESHOT_DIR/.claude/commands"/*.md; do
            [ -f "$cmd" ] || continue
            cmd_name=$(basename "$cmd")
            # Remove existing file (regular or symlink) and create fresh symlink
            rm -f "$COMMANDS_DIR/$cmd_name"
            ln -sf "$cmd" "$COMMANDS_DIR/$cmd_name"
        done
        log "Updated command symlinks in $COMMANDS_DIR"

        echo "UPDATED"
        return 0
    else
        log "Update failed, rolling back"
        git rebase --abort 2>/dev/null || true
        git stash pop 2>/dev/null || true
        echo "FAILED"
        return 1
    fi
}

# Sync skills and agents from oneshot to a project directory
sync_to_project() {
    local target_dir="${1:-$(detect_project_dir)}"

    if [ -z "$target_dir" ]; then
        log "No project directory found for sync"
        echo "NO_PROJECT"
        return 1
    fi

    if [ ! -d "$target_dir/.claude" ]; then
        log "Target .claude directory not found: $target_dir/.claude"
        echo "NO_CLAUDE_DIR"
        return 1
    fi

    log "Syncing to project: $target_dir"

    # Sync skills (use --delete to remove obsolete skills)
    if rsync -av --delete "$ONESHOT_DIR/.claude/skills/" "$target_dir/.claude/skills/" 2>>"$LOG_FILE"; then
        log "Skills synced successfully"
    else
        log "Skills sync failed"
        echo "SYNC_FAILED"
        return 1
    fi

    # Sync agents if they exist in both places
    if [ -d "$ONESHOT_DIR/.claude/agents" ] && [ -d "$target_dir/.claude/agents" ]; then
        if rsync -av --delete "$ONESHOT_DIR/.claude/agents/" "$target_dir/.claude/agents/" 2>>"$LOG_FILE"; then
            log "Agents synced successfully"
        else
            log "Agents sync failed"
        fi
    fi

    echo "SYNCED:$target_dir"
    return 0
}

# Update cache timestamp
update_cache() {
    echo "$(date +%s)" > "$CACHE_FILE"
}

# Auto-check and update (main mode for session start)
auto_update() {
    # Rate limit check
    if ! should_check; then
        echo "RATE_LIMITED"
        exit 0
    fi

    update_cache  # Mark that we checked

    local remote_hash=$(get_remote_hash)
    local local_hash=$(get_local_hash)

    if [ -z "$remote_hash" ]; then
        log "Could not reach GitHub API"
        echo "SKIP"
        exit 0
    fi

    if [ "$remote_hash" != "$local_hash" ]; then
        log "Update available: $local_hash -> $remote_hash"
        # AUTO-UPDATE without prompting
        do_update
    else
        log "Already up to date: $local_hash"
        echo "UP_TO_DATE"
    fi
}

# Main entrypoint
main() {
    local action="${1:-auto}"

    case "$action" in
        auto)
            # Default: auto-check and auto-update
            auto_update
            ;;
        check)
            # Just check, don't update (for status)
            if ! should_check; then
                echo "RATE_LIMITED"
                exit 0
            fi
            update_cache
            local remote_hash=$(get_remote_hash)
            local local_hash=$(get_local_hash)
            if [ "$remote_hash" != "$local_hash" ]; then
                echo "UPDATE_AVAILABLE"
            else
                echo "UP_TO_DATE"
            fi
            ;;
        force)
            # Force update now (bypass rate limit) AND sync to current project
            do_update
            update_cache

            # After successful update, sync to current project
            if [ "$?" -eq 0 ]; then
                sync_result=$(sync_to_project)
                if [[ "$sync_result" == SYNCED:* ]]; then
                    project="${sync_result#SYNCED:}"
                    log "Synced to project: $project"
                elif [ "$sync_result" = "NO_PROJECT" ]; then
                    log "No project found to sync to (not in a project directory)"
                elif [ "$sync_result" = "NO_CLAUDE_DIR" ]; then
                    log "Target project has no .claude directory"
                fi
            fi
            ;;
        sync)
            # Just sync to current project (after manual git pull)
            project_dir="${2:-}"
            sync_result=$(sync_to_project "$project_dir")
            echo "$sync_result"
            ;;
        status)
            echo "ONESHOT_DIR: $ONESHOT_DIR"
            echo "LOCAL_HASH: $(get_local_hash)"
            echo "REMOTE_HASH: $(get_remote_hash)"
            echo "LAST_CHECK: $(cat "$CACHE_FILE" 2>/dev/null || echo 'never')"
            echo "LOG: $LOG_FILE"
            ;;
        *)
            echo "Usage: oneshot-update.sh [auto|check|force|sync|status]"
            echo "  auto   - Check and auto-update if available (default, session start)"
            echo "  check  - Just check for updates (rate-limited)"
            echo "  force  - Force update from GitHub AND sync to current project"
            echo "  sync   - Sync skills/agents to current project (after manual git pull)"
            echo "  status - Show current status"
            exit 1
            ;;
    esac
}

main "$@"
