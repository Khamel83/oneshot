#!/bin/bash
# oneshot-resilient.sh - Run Claude in a disconnect-proof tmux session
# Survives terminal disconnect, SSH drops, and system sleep

set -uo pipefail

# Configuration
SESSION_PREFIX="${ONESHOT_TMUX_SESSION:-oneshot}"
CHECKPOINT_INTERVAL="${ONESHOT_CHECKPOINT_INTERVAL:-300}"  # 5 minutes
PROJECT_DIR="${PWD}"
AGENT_DIR="${PROJECT_DIR}/.agent"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[oneshot]${NC} $1"; }
warn() { echo -e "${YELLOW}[warn]${NC} $1"; }
error() { echo -e "${RED}[error]${NC} $1"; }
success() { echo -e "${GREEN}[ok]${NC} $1"; }

# Check dependencies
check_deps() {
    if ! command -v tmux &> /dev/null; then
        error "tmux is required. Install with: brew install tmux (mac) or apt install tmux (linux)"
        exit 1
    fi
    if ! command -v claude &> /dev/null; then
        error "claude CLI not found in PATH"
        exit 1
    fi
}

# Initialize .agent directory
init_agent_dir() {
    mkdir -p "$AGENT_DIR"

    echo "# ONE_SHOT Resilient Session" > "$AGENT_DIR/STATUS.md"
    echo "Started: $(date)" >> "$AGENT_DIR/STATUS.md"
    echo "Session: $SESSION_NAME" >> "$AGENT_DIR/STATUS.md"
    echo "Project: $PROJECT_DIR" >> "$AGENT_DIR/STATUS.md"
    echo "" >> "$AGENT_DIR/STATUS.md"

    # Create recovery instructions
    cat > "$AGENT_DIR/RECOVERY.md" << EOF
# Recovery Instructions

Session: $SESSION_NAME

## If Disconnected

1. Check if session still running:
   tmux list-sessions | grep $SESSION_NAME

2. Reattach to running session:
   tmux attach -t $SESSION_NAME

3. If session died, check beads state:
   bd sync
   bd ready --json

4. Resume work:
   claude -p "Resume from beads. Run bd ready and continue."

## Check Progress

- Current status: cat .agent/STATUS.md
- Session log: less .agent/session.log
- Heartbeat: tail -5 .agent/HEARTBEAT
- Git history: git log --oneline -10
- Beads tasks: bd list --json

## Force Checkpoint

bd sync && git add -A && git commit -m "checkpoint \$(date +%H%M)"
EOF

    success "Initialized $AGENT_DIR"
}

# Heartbeat process (runs in background inside tmux)
start_heartbeat() {
    while true; do
        echo "$(date '+%Y-%m-%d %H:%M:%S'): alive" >> "$AGENT_DIR/HEARTBEAT"
        sleep 30
    done
}

# Checkpoint process (runs in background inside tmux)
start_checkpointer() {
    while true; do
        sleep "$CHECKPOINT_INTERVAL"
        if [ -d .git ]; then
            git add -A 2>/dev/null
            if ! git diff --cached --quiet 2>/dev/null; then
                git commit -m "WIP: checkpoint $(date +%H%M)" 2>/dev/null
                echo "$(date): checkpoint committed" >> "$AGENT_DIR/CHECKPOINTS.md"
            fi
        fi
        if command -v bd &> /dev/null; then
            bd sync 2>/dev/null || true
        fi
    done
}

# Main execution function
run_resilient() {
    local PROMPT="$1"

    # Wrap the prompt with resilience instructions
    local FULL_PROMPT="
You are running in RESILIENT mode. Your session survives disconnection.

CRITICAL PERSISTENCE RULES:
1. Run 'bd sync' after EVERY task completion
2. Commit after EVERY file change (git commit -m 'feat: description')
3. Update .agent/STATUS.md with current progress regularly
4. If something fails, run 'bd sync' before stopping

YOUR TASK:
$PROMPT

Begin now. Remember to persist state frequently.
"

    # Start the Claude session with script for logging
    cd "$PROJECT_DIR"

    # Export functions for background processes
    export AGENT_DIR
    export -f start_heartbeat
    export -f start_checkpointer
    export CHECKPOINT_INTERVAL

    # Create the tmux session with multiple panes/processes
    tmux new-session -d -s "$SESSION_NAME" -x 200 -y 50

    # Start heartbeat in background
    tmux send-keys -t "$SESSION_NAME" "( while true; do echo \"\$(date '+%Y-%m-%d %H:%M:%S'): alive\" >> \"$AGENT_DIR/HEARTBEAT\"; sleep 30; done ) &" C-m

    # Start checkpointer in background
    tmux send-keys -t "$SESSION_NAME" "( while true; do sleep $CHECKPOINT_INTERVAL; git add -A 2>/dev/null && git diff --cached --quiet 2>/dev/null || git commit -m \"WIP: checkpoint \$(date +%H%M)\" 2>/dev/null; bd sync 2>/dev/null || true; done ) &" C-m

    # Run Claude with script for logging
    tmux send-keys -t "$SESSION_NAME" "cd \"$PROJECT_DIR\" && script -f \"$AGENT_DIR/session.log\" -c 'claude --dangerously-skip-permissions -p \"$FULL_PROMPT\"'" C-m

    success "Started resilient session: $SESSION_NAME"
}

# List running sessions
list_sessions() {
    log "Running ONE_SHOT sessions:"
    tmux list-sessions 2>/dev/null | grep "$SESSION_PREFIX" || echo "  (none)"
}

# Attach to session
attach_session() {
    local SESSION="${1:-}"
    if [ -z "$SESSION" ]; then
        # Find most recent oneshot session
        SESSION=$(tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "$SESSION_PREFIX" | head -1)
    fi

    if [ -z "$SESSION" ]; then
        error "No ONE_SHOT session found"
        exit 1
    fi

    log "Attaching to: $SESSION"
    tmux attach -t "$SESSION"
}

# Kill session
kill_session() {
    local SESSION="${1:-}"
    if [ -z "$SESSION" ]; then
        error "Specify session name to kill"
        exit 1
    fi

    # Sync beads before killing
    if command -v bd &> /dev/null; then
        bd sync 2>/dev/null || true
    fi

    tmux kill-session -t "$SESSION" 2>/dev/null
    success "Killed session: $SESSION"
}

# Show status
show_status() {
    if [ -f "$AGENT_DIR/STATUS.md" ]; then
        cat "$AGENT_DIR/STATUS.md"
    fi

    echo ""
    echo "=== Heartbeat ==="
    if [ -f "$AGENT_DIR/HEARTBEAT" ]; then
        tail -5 "$AGENT_DIR/HEARTBEAT"
    else
        echo "(no heartbeat file)"
    fi

    echo ""
    echo "=== Active Sessions ==="
    tmux list-sessions 2>/dev/null | grep "$SESSION_PREFIX" || echo "(none)"

    echo ""
    echo "=== Beads State ==="
    if command -v bd &> /dev/null; then
        bd ready --json 2>/dev/null | head -10 || echo "(beads not available)"
    fi
}

# Usage
usage() {
    cat << EOF
Usage: oneshot-resilient.sh <command> [args]

Commands:
  run <prompt>     Start resilient Claude session with prompt
  attach [name]    Attach to running session
  list             List running sessions
  kill <name>      Kill a session (syncs beads first)
  status           Show current status
  help             Show this help

Examples:
  oneshot-resilient.sh run "Implement the auth feature"
  oneshot-resilient.sh attach
  oneshot-resilient.sh list
  oneshot-resilient.sh status

Environment:
  ONESHOT_TMUX_SESSION      Session name prefix (default: oneshot)
  ONESHOT_CHECKPOINT_INTERVAL  Checkpoint interval in seconds (default: 300)
EOF
}

# Main
main() {
    check_deps

    local CMD="${1:-help}"
    shift || true

    case "$CMD" in
        run)
            if [ -z "${1:-}" ]; then
                error "Please provide a prompt"
                usage
                exit 1
            fi
            SESSION_NAME="${SESSION_PREFIX}-$(date +%s)"
            init_agent_dir
            run_resilient "$*"

            echo ""
            log "Session is running in background"
            log "Attach with: tmux attach -t $SESSION_NAME"
            log "Check status: cat .agent/STATUS.md"
            log "Session survives disconnect!"
            ;;
        attach)
            attach_session "${1:-}"
            ;;
        list)
            list_sessions
            ;;
        kill)
            kill_session "${1:-}"
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            error "Unknown command: $CMD"
            usage
            exit 1
            ;;
    esac
}

main "$@"
