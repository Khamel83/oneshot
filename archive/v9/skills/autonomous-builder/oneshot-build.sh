#!/bin/bash
# oneshot-build - Autonomous builder with resilient execution
# Runs in tmux, survives disconnect, persists state aggressively

set -uo pipefail

# Configuration
MAX_ITERATIONS="${MAX_ITERATIONS:-100}"
STUCK_THRESHOLD="${STUCK_THRESHOLD:-5}"
CHECKPOINT_INTERVAL="${CHECKPOINT_INTERVAL:-300}"  # 5 minutes
PROJECT_DIR="${PWD}"
AGENT_DIR="${PROJECT_DIR}/.agent"
SESSION_NAME="oneshot-build-$(date +%s)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${BLUE}[oneshot-build]${NC} $1"; }
success() { echo -e "${GREEN}[ok]${NC} $1"; }
error() { echo -e "${RED}[error]${NC} $1"; }

# Check dependencies
check_deps() {
    local missing=""
    command -v tmux &>/dev/null || missing="$missing tmux"
    command -v claude &>/dev/null || missing="$missing claude"
    command -v git &>/dev/null || missing="$missing git"

    if [ -n "$missing" ]; then
        error "Missing dependencies:$missing"
        exit 1
    fi
}

# Initialize .agent directory
init_agent() {
    mkdir -p "$AGENT_DIR"

    cat > "$AGENT_DIR/STATUS.md" << EOF
# ONE_SHOT Autonomous Build

**Started**: $(date)
**Session**: $SESSION_NAME
**Idea**: $IDEA
**Max Iterations**: $MAX_ITERATIONS

## Progress
EOF

    echo "0" > "$AGENT_DIR/ITERATIONS.md"
    echo "" > "$AGENT_DIR/LAST_STATE.md"
    echo "" > "$AGENT_DIR/HEARTBEAT"
    echo "" > "$AGENT_DIR/CHECKPOINTS.md"

    # Recovery instructions
    cat > "$AGENT_DIR/RECOVERY.md" << EOF
# Recovery Instructions

Session: $SESSION_NAME
Idea: $IDEA

## If Disconnected

1. Check session: tmux list-sessions | grep oneshot-build
2. Reattach: tmux attach -t $SESSION_NAME
3. If dead: bd sync && bd ready --json
4. Resume: oneshot-build "$IDEA"

## Monitoring

- Status: tail -f .agent/STATUS.md
- Log: less .agent/session.log
- Heartbeat: tail -5 .agent/HEARTBEAT
- Tasks: bd list --json
EOF

    success "Initialized $AGENT_DIR"
}

# The autonomous build prompt
BUILD_PROMPT='
You are running ONE_SHOT Autonomous Builder in RESILIENT mode.

CRITICAL PERSISTENCE RULES (FOLLOW EXACTLY):
1. Run `bd sync` IMMEDIATELY after EVERY task status change
2. Run `git commit` after EVERY file edit
3. Update .agent/STATUS.md after EVERY action
4. If ANY error occurs, run `bd sync` BEFORE anything else

BUILD PROCESS:
1. Use front-door skill to analyze the idea
2. Use create-plan skill to create structured plan
3. Parse plan into beads tasks: bd create "task" -p 1 --json
4. For each task:
   a. bd update <id> --status in_progress && bd sync
   b. Implement the task
   c. git add -A && git commit -m "feat: description"
   d. bd close <id> --reason "commit: xyz" && bd sync
   e. Update .agent/STATUS.md

LOOP DETECTION:
- If same bd ready output 5 times, you are stuck
- If stuck: bd sync, write to .agent/LAST_ERROR.md, stop gracefully

YOUR IDEA TO BUILD:
'

# Run the build in tmux
run_build() {
    local FULL_PROMPT="${BUILD_PROMPT}${IDEA}

Begin now. Remember: bd sync after EVERY action!"

    # Start tmux session
    tmux new-session -d -s "$SESSION_NAME" -x 200 -y 50

    # Start heartbeat
    tmux send-keys -t "$SESSION_NAME" "( while true; do echo \"\$(date '+%Y-%m-%d %H:%M:%S'): alive\" >> \"$AGENT_DIR/HEARTBEAT\"; sleep 30; done ) &" C-m

    # Start checkpointer
    tmux send-keys -t "$SESSION_NAME" "( while true; do sleep $CHECKPOINT_INTERVAL; git add -A 2>/dev/null && git diff --cached --quiet 2>/dev/null || git commit -m \"WIP: checkpoint \$(date +%H%M)\" 2>/dev/null; bd sync 2>/dev/null || true; echo \"Checkpoint: \$(date)\" >> \"$AGENT_DIR/CHECKPOINTS.md\"; done ) &" C-m

    # Small delay for background processes to start
    sleep 1

    # Run Claude with script logging
    # Escape single quotes in prompt
    local ESCAPED_PROMPT=$(echo "$FULL_PROMPT" | sed "s/'/'\\\\''/g")
    tmux send-keys -t "$SESSION_NAME" "cd \"$PROJECT_DIR\" && script -f \"$AGENT_DIR/session.log\" -c \"claude --dangerously-skip-permissions -p '$ESCAPED_PROMPT'\"" C-m

    success "Build started in tmux session: $SESSION_NAME"
}

# Show status
show_status() {
    echo ""
    log "=== Build Status ==="

    if [ -f "$AGENT_DIR/STATUS.md" ]; then
        head -20 "$AGENT_DIR/STATUS.md"
    fi

    echo ""
    log "=== Heartbeat ==="
    if [ -f "$AGENT_DIR/HEARTBEAT" ]; then
        tail -3 "$AGENT_DIR/HEARTBEAT"
    fi

    echo ""
    log "=== Active Sessions ==="
    tmux list-sessions 2>/dev/null | grep oneshot-build || echo "(none)"
}

# Main
main() {
    local CMD="${1:-}"

    case "$CMD" in
        status)
            show_status
            ;;
        attach)
            SESSION=$(tmux list-sessions -F "#{session_name}" 2>/dev/null | grep oneshot-build | head -1)
            if [ -z "$SESSION" ]; then
                error "No build session running"
                exit 1
            fi
            log "Attaching to: $SESSION"
            tmux attach -t "$SESSION"
            ;;
        kill)
            SESSION=$(tmux list-sessions -F "#{session_name}" 2>/dev/null | grep oneshot-build | head -1)
            if [ -n "$SESSION" ]; then
                bd sync 2>/dev/null || true
                tmux kill-session -t "$SESSION"
                success "Killed session: $SESSION"
            else
                log "No build session running"
            fi
            ;;
        "")
            echo "Usage: oneshot-build \"Your idea here\""
            echo "       oneshot-build status"
            echo "       oneshot-build attach"
            echo "       oneshot-build kill"
            exit 1
            ;;
        *)
            # It's an idea to build
            IDEA="$*"
            check_deps
            init_agent
            run_build

            echo ""
            log "=== Autonomous Build Started ==="
            echo ""
            echo "  Session:  $SESSION_NAME"
            echo "  Idea:     $IDEA"
            echo ""
            echo "  Commands:"
            echo "    Attach:   tmux attach -t $SESSION_NAME"
            echo "    Status:   oneshot-build status"
            echo "    Progress: tail -f .agent/STATUS.md"
            echo "    Kill:     oneshot-build kill"
            echo ""
            echo "  Session survives terminal disconnect!"
            echo ""
            ;;
    esac
}

main "$@"
