#!/bin/bash
# oneshot - Unified command for all ONE_SHOT operations
# Manages tmux sessions automatically - you never touch tmux directly

set -uo pipefail

ONESHOT_DIR="${ONESHOT_DIR:-$HOME/github/oneshot}"
SKILLS_DIR="${ONESHOT_DIR}/.claude/skills"
SESSION_PREFIX="oneshot"
AGENT_DIR=".agent"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Logging
log() { echo -e "${BLUE}▶${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }
header() { echo -e "\n${BOLD}${CYAN}$1${NC}\n"; }

#######################################
# TMUX SESSION MANAGEMENT (All Automatic)
#######################################

# Get the current/active oneshot session (if any)
get_active_session() {
    tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "^${SESSION_PREFIX}" | head -1
}

# Get all oneshot sessions
get_all_sessions() {
    tmux list-sessions -F "#{session_name}:#{session_created}:#{session_attached}" 2>/dev/null | grep "^${SESSION_PREFIX}" || true
}

# Kill old sessions (keep only most recent)
cleanup_old_sessions() {
    local sessions=$(get_all_sessions)
    local count=$(echo "$sessions" | grep -c "^${SESSION_PREFIX}" 2>/dev/null || echo 0)

    if [ "$count" -gt 3 ]; then
        log "Cleaning up old sessions..."
        echo "$sessions" | sort -t: -k2 -n | head -n $((count - 2)) | cut -d: -f1 | while read session; do
            tmux kill-session -t "$session" 2>/dev/null || true
        done
    fi
}

# Create a new session and run command
create_session() {
    local name="$1"
    local cmd="$2"
    local project_dir="${3:-$PWD}"

    # Initialize .agent directory
    mkdir -p "$project_dir/$AGENT_DIR"

    # Create session
    tmux new-session -d -s "$name" -c "$project_dir" -x 200 -y 50

    # Start heartbeat in background
    tmux send-keys -t "$name" "( while true; do echo \"\$(date '+%Y-%m-%d %H:%M:%S'): alive\" >> \"$AGENT_DIR/HEARTBEAT\"; sleep 30; done ) &" C-m

    # Start checkpointer in background (every 5 min)
    tmux send-keys -t "$name" "( while true; do sleep 300; git add -A 2>/dev/null && git diff --cached --quiet 2>/dev/null || git commit -m \"WIP: checkpoint \$(date +%H%M)\" 2>/dev/null; bd sync 2>/dev/null || true; done ) &" C-m

    # Small delay
    sleep 0.5

    # Run the main command with logging
    tmux send-keys -t "$name" "script -f \"$AGENT_DIR/session.log\" -c '$cmd'" C-m

    echo "$name"
}

# Attach to session (or show output if already attached elsewhere)
smart_attach() {
    local session="$1"

    if [ -z "$session" ]; then
        error "No session to attach to"
        return 1
    fi

    # Check if session exists
    if ! tmux has-session -t "$session" 2>/dev/null; then
        error "Session '$session' not found"
        return 1
    fi

    # Check if already attached
    local attached=$(tmux list-sessions -F "#{session_name}:#{session_attached}" | grep "^$session:" | cut -d: -f2)

    if [ "$attached" = "1" ]; then
        warn "Session already attached in another terminal"
        log "Showing live output instead..."
        echo ""
        tail -f "$AGENT_DIR/session.log" 2>/dev/null || tail -f .agent/session.log 2>/dev/null
    else
        tmux attach -t "$session"
    fi
}

#######################################
# MAIN COMMANDS
#######################################

# Build something (autonomous mode)
cmd_build() {
    local idea="$*"

    if [ -z "$idea" ]; then
        error "Please provide an idea to build"
        echo "Usage: oneshot build \"A CLI tool that does X\""
        return 1
    fi

    header "ONE_SHOT Autonomous Build"

    cleanup_old_sessions

    local session="${SESSION_PREFIX}-build-$(date +%s)"
    local prompt="You are running ONE_SHOT Autonomous Builder.

PERSISTENCE RULES (CRITICAL):
- bd sync after EVERY task change
- git commit after EVERY file edit
- Update .agent/STATUS.md regularly

BUILD THIS:
$idea

Start with front-door, then create-plan, then implement-plan.
Use beads for task tracking. Begin now."

    # Initialize status
    mkdir -p "$AGENT_DIR"
    cat > "$AGENT_DIR/STATUS.md" << EOF
# Autonomous Build
**Started**: $(date)
**Idea**: $idea
**Session**: $session

## Progress
Starting...
EOF

    # Create and run
    create_session "$session" "claude --dangerously-skip-permissions -p '$prompt'" "$PWD"

    success "Build started!"
    echo ""
    echo "  ${BOLD}Session:${NC}  $session"
    echo "  ${BOLD}Idea:${NC}     $idea"
    echo ""
    echo "  ${BOLD}Commands:${NC}"
    echo "    oneshot attach     - Watch the build"
    echo "    oneshot status     - Check progress"
    echo "    oneshot log        - View full log"
    echo ""
    echo "  ${GREEN}Session survives if you disconnect!${NC}"
}

# Run a prompt resiliently
cmd_run() {
    local prompt="$*"

    if [ -z "$prompt" ]; then
        error "Please provide a prompt"
        echo "Usage: oneshot run \"implement the auth feature\""
        return 1
    fi

    header "ONE_SHOT Resilient Run"

    cleanup_old_sessions

    local session="${SESSION_PREFIX}-run-$(date +%s)"
    local full_prompt="You are running in RESILIENT mode.

PERSISTENCE RULES:
- bd sync after task changes
- git commit after file edits

YOUR TASK:
$prompt

Begin now."

    mkdir -p "$AGENT_DIR"
    echo "Started: $(date)" > "$AGENT_DIR/STATUS.md"
    echo "Task: $prompt" >> "$AGENT_DIR/STATUS.md"

    create_session "$session" "claude -p '$full_prompt'" "$PWD"

    success "Started resilient session!"
    echo ""
    echo "  ${BOLD}Session:${NC} $session"
    echo ""
    echo "  Run ${BOLD}oneshot attach${NC} to watch"
}

# Attach to current session
cmd_attach() {
    local session=$(get_active_session)

    if [ -z "$session" ]; then
        warn "No active ONE_SHOT session"
        echo ""
        echo "Start one with:"
        echo "  oneshot build \"your idea\""
        echo "  oneshot run \"your prompt\""
        return 1
    fi

    log "Attaching to: $session"
    smart_attach "$session"
}

# Show status
cmd_status() {
    header "ONE_SHOT Status"

    # Active sessions
    echo "${BOLD}Sessions:${NC}"
    local sessions=$(get_all_sessions)
    if [ -z "$sessions" ]; then
        echo "  (none running)"
    else
        echo "$sessions" | while IFS=: read -r name created attached; do
            local status="running"
            [ "$attached" = "1" ] && status="attached"
            echo "  • $name ($status)"
        done
    fi
    echo ""

    # Current project status
    if [ -f "$AGENT_DIR/STATUS.md" ]; then
        echo "${BOLD}Current Project:${NC}"
        head -15 "$AGENT_DIR/STATUS.md" | sed 's/^/  /'
        echo ""
    fi

    # Heartbeat
    if [ -f "$AGENT_DIR/HEARTBEAT" ]; then
        echo "${BOLD}Last Heartbeat:${NC}"
        tail -1 "$AGENT_DIR/HEARTBEAT" | sed 's/^/  /'
        echo ""
    fi

    # Beads status
    if command -v bd &>/dev/null && [ -d .beads ]; then
        echo "${BOLD}Beads Tasks:${NC}"
        bd ready 2>/dev/null | head -5 | sed 's/^/  /' || echo "  (no ready tasks)"
        echo ""
    fi
}

# Show log
cmd_log() {
    if [ -f "$AGENT_DIR/session.log" ]; then
        less "$AGENT_DIR/session.log"
    else
        error "No session log found"
    fi
}

# Follow log live
cmd_follow() {
    if [ -f "$AGENT_DIR/session.log" ]; then
        log "Following session log (Ctrl+C to stop)..."
        tail -f "$AGENT_DIR/session.log"
    else
        error "No session log found"
    fi
}

# Stop current session
cmd_stop() {
    local session=$(get_active_session)

    if [ -z "$session" ]; then
        warn "No active session to stop"
        return 0
    fi

    log "Syncing beads state..."
    bd sync 2>/dev/null || true

    log "Stopping session: $session"
    tmux kill-session -t "$session" 2>/dev/null

    success "Session stopped"
    echo "State saved in beads. Resume with: oneshot resume"
}

# Resume from beads state
cmd_resume() {
    header "ONE_SHOT Resume"

    if ! command -v bd &>/dev/null; then
        error "Beads not installed"
        return 1
    fi

    bd sync 2>/dev/null || true

    local ready=$(bd ready --json 2>/dev/null | head -1)
    if [ -z "$ready" ] || [ "$ready" = "[]" ]; then
        warn "No tasks to resume"
        echo "Start fresh with: oneshot build \"your idea\""
        return 0
    fi

    log "Found tasks to resume"

    local session="${SESSION_PREFIX}-resume-$(date +%s)"
    local prompt="Resume from beads state.

Run bd ready --json and continue implementing the next task.
Remember: bd sync after every task completion.

Begin now."

    create_session "$session" "claude -p '$prompt'" "$PWD"

    success "Resumed!"
    echo "Run ${BOLD}oneshot attach${NC} to watch"
}

# List all sessions
cmd_list() {
    header "ONE_SHOT Sessions"

    local sessions=$(get_all_sessions)
    if [ -z "$sessions" ]; then
        echo "No active sessions"
    else
        echo "$sessions" | while IFS=: read -r name created attached; do
            local status="${GREEN}running${NC}"
            [ "$attached" = "1" ] && status="${CYAN}attached${NC}"
            echo -e "  • $name - $status"
        done
    fi
}

# Kill all sessions
cmd_killall() {
    log "Syncing beads state..."
    bd sync 2>/dev/null || true

    log "Killing all ONE_SHOT sessions..."
    tmux list-sessions -F "#{session_name}" 2>/dev/null | grep "^${SESSION_PREFIX}" | while read session; do
        tmux kill-session -t "$session" 2>/dev/null
        echo "  Killed: $session"
    done

    success "All sessions stopped"
}

# Update oneshot
cmd_update() {
    header "ONE_SHOT Update"

    local update_script="$SKILLS_DIR/auto-updater/oneshot-update.sh"
    if [ -x "$update_script" ]; then
        "$update_script" force
    else
        error "Update script not found"
        return 1
    fi
}

# Help
cmd_help() {
    cat << 'EOF'

  ╔═══════════════════════════════════════════════════════════╗
  ║                    ONE_SHOT v7.4                          ║
  ║         Resilient, Autonomous AI Development              ║
  ╚═══════════════════════════════════════════════════════════╝

  USAGE: oneshot <command> [args]

  BUILD & RUN
    build <idea>     Autonomous build (headless, resilient)
    run <prompt>     Run prompt in resilient session

  SESSION MANAGEMENT (all automatic)
    attach           Connect to running session
    status           Show current status
    log              View full session log
    follow           Follow log live (tail -f)
    stop             Stop current session (saves state)
    resume           Resume from beads state
    list             List all sessions
    killall          Stop all sessions

  MAINTENANCE
    update           Update ONE_SHOT from GitHub

  EXAMPLES
    oneshot build "A Python CLI that fetches weather data"
    oneshot run "add authentication to the API"
    oneshot attach
    oneshot status

  Sessions run in tmux and survive terminal disconnect.
  State is saved continuously - resume anytime with 'oneshot resume'.

EOF
}

#######################################
# MAIN
#######################################

main() {
    # Check for tmux
    if ! command -v tmux &>/dev/null; then
        error "tmux is required. Install with:"
        echo "  brew install tmux  (macOS)"
        echo "  apt install tmux   (Linux)"
        exit 1
    fi

    local cmd="${1:-help}"
    shift 2>/dev/null || true

    case "$cmd" in
        build)      cmd_build "$@" ;;
        run)        cmd_run "$@" ;;
        attach|a)   cmd_attach ;;
        status|s)   cmd_status ;;
        log|l)      cmd_log ;;
        follow|f)   cmd_follow ;;
        stop)       cmd_stop ;;
        resume|r)   cmd_resume ;;
        list|ls)    cmd_list ;;
        killall)    cmd_killall ;;
        update)     cmd_update ;;
        help|--help|-h) cmd_help ;;
        *)
            error "Unknown command: $cmd"
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
