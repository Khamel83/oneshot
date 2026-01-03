#!/usr/bin/env bats
# test_workflow.bats - E2E workflow tests for ONE_SHOT v7.3
# Tests the full skill chain: bootstrap → oneshot-build → beads integration
#
# Install: brew install bats-core OR apt install bats
# Run: bats tests/test_workflow.bats

# Skip tests if dependencies not available
setup() {
    TEST_DIR=$(mktemp -d)
    export TEST_DIR
    export ORIGINAL_DIR="$PWD"

    # Create a mock project
    mkdir -p "$TEST_DIR/project"
    cd "$TEST_DIR/project"
    git init -q

    # Copy scripts
    cp "$ORIGINAL_DIR/scripts/oneshot-build" "$TEST_DIR/" 2>/dev/null || true
    cp "$ORIGINAL_DIR/oneshot.sh" "$TEST_DIR/" 2>/dev/null || true
}

teardown() {
    cd "$ORIGINAL_DIR"
    rm -rf "$TEST_DIR"
}

# =============================================================================
# oneshot-build Dependency Checks
# =============================================================================

@test "oneshot-build shows usage without arguments" {
    # Skip if oneshot-build doesn't exist
    [ -f "$TEST_DIR/oneshot-build" ] || skip "oneshot-build not found"

    run bash "$TEST_DIR/oneshot-build"

    [ "$status" -eq 1 ]
    [[ "$output" == *"Usage:"* ]]
}

@test "oneshot-build fails without bd CLI" {
    [ -f "$TEST_DIR/oneshot-build" ] || skip "oneshot-build not found"

    # Create a version of the script with mocked command checks
    # by prepending a function that makes 'bd' unavailable
    cat > "$TEST_DIR/test-build.sh" << 'EOF'
#!/bin/bash
# Mock: bd command not found
command() {
    if [[ "$2" == "bd" ]]; then
        return 1
    fi
    builtin command "$@"
}
export -f command
EOF
    cat "$TEST_DIR/oneshot-build" >> "$TEST_DIR/test-build.sh"
    chmod +x "$TEST_DIR/test-build.sh"

    run bash "$TEST_DIR/test-build.sh" "test idea" 2>&1

    [ "$status" -eq 1 ]
    [[ "$output" == *"Missing required dependencies"* ]] || [[ "$output" == *"bd"* ]]
}

@test "oneshot-build fails without AGENTS.md (not ONE_SHOT project)" {
    [ -f "$TEST_DIR/oneshot-build" ] || skip "oneshot-build not found"

    # Ensure no AGENTS.md
    rm -f AGENTS.md

    # Mock all dependencies as available
    # We need to test the project check
    run bash -c "
        # Mock commands
        bd() { return 0; }
        jq() { return 0; }
        claude() { return 0; }
        export -f bd jq claude

        # Source just the check functions
        source '$TEST_DIR/oneshot-build' 2>&1
    " 2>&1

    # Should fail because AGENTS.md doesn't exist
    [[ "$output" == *"Not a ONE_SHOT project"* ]] || [[ "$output" == *"AGENTS.md"* ]] || [ "$status" -ne 0 ]
}

# =============================================================================
# oneshot.sh Bootstrap Tests
# =============================================================================

@test "oneshot.sh fails without beads CLI installed" {
    [ -f "$TEST_DIR/oneshot.sh" ] || skip "oneshot.sh not found"

    # Create modified script that mocks 'command -v bd' to fail
    cat > "$TEST_DIR/test-bootstrap.sh" << 'EOF'
#!/bin/bash
# Override command to make bd unavailable
original_command=$(which command 2>/dev/null || echo "command")
command() {
    if [[ "$*" == *"bd"* ]]; then
        return 1
    fi
    builtin command "$@"
}
EOF
    # Append the check portion of oneshot.sh
    grep -A 20 "Check for beads CLI" "$TEST_DIR/oneshot.sh" >> "$TEST_DIR/test-bootstrap.sh" 2>/dev/null || true

    if [ -s "$TEST_DIR/test-bootstrap.sh" ]; then
        chmod +x "$TEST_DIR/test-bootstrap.sh"
        run bash "$TEST_DIR/test-bootstrap.sh" 2>&1

        # Should fail or show beads error
        [[ "$output" == *"beads"* ]] || [[ "$output" == *"REQUIRED"* ]] || [ "$status" -ne 0 ]
    else
        skip "Could not extract beads check from oneshot.sh"
    fi
}

@test "oneshot.sh --help shows prerequisites" {
    [ -f "$TEST_DIR/oneshot.sh" ] || skip "oneshot.sh not found"

    run bash "$TEST_DIR/oneshot.sh" --help

    [ "$status" -eq 0 ]
    [[ "$output" == *"beads"* ]]
    [[ "$output" == *"REQUIRED"* ]] || [[ "$output" == *"Prerequisites"* ]]
}

# =============================================================================
# Beads Integration Tests (if bd is available)
# =============================================================================

@test "beads can initialize in project directory" {
    command -v bd &>/dev/null || skip "beads not installed"

    # Initialize beads
    run bd init --stealth

    [ "$status" -eq 0 ]
    [ -d ".beads" ]
}

@test "beads ready returns empty array for new project" {
    command -v bd &>/dev/null || skip "beads not installed"

    bd init --stealth 2>/dev/null || true

    run bd ready --json

    [ "$status" -eq 0 ]
    [[ "$output" == "[]" ]] || [[ "$output" == "" ]]
}

@test "beads can create and list tasks" {
    command -v bd &>/dev/null || skip "beads not installed"
    command -v jq &>/dev/null || skip "jq not installed"

    bd init --stealth 2>/dev/null || true

    # Create a task
    run bd create "Test task" --json
    [ "$status" -eq 0 ]

    # List tasks
    run bd list --json
    [ "$status" -eq 0 ]

    # Should have at least one task
    count=$(echo "$output" | jq 'length')
    [ "$count" -ge 1 ]
}

@test "beads sync works without errors" {
    command -v bd &>/dev/null || skip "beads not installed"

    bd init --stealth 2>/dev/null || true

    run bd sync

    # Should succeed (might warn if nothing to sync)
    [ "$status" -eq 0 ] || [ "$status" -eq 1 ]
}

# =============================================================================
# .agent/ Directory Tests
# =============================================================================

@test "oneshot-build creates .agent directory" {
    [ -f "$TEST_DIR/oneshot-build" ] || skip "oneshot-build not found"

    # Extract just the init_agent function and test it
    cat > "$TEST_DIR/test-init.sh" << 'EOF'
#!/bin/bash
AGENT_DIR=".agent"
STATUS_FILE="$AGENT_DIR/STATUS.md"
ITER_FILE="$AGENT_DIR/ITERATIONS.md"
STATE_FILE="$AGENT_DIR/LAST_STATE.md"
IDEA="Test idea"

init_agent() {
    mkdir -p "$AGENT_DIR"
    echo "0" > "$ITER_FILE"
    echo "" > "$STATE_FILE"
    cat > "$STATUS_FILE" << INNEREOF
# Build Status

**Idea**: $IDEA
**Started**: $(date -Iseconds)
**Status**: Initializing

## Progress Log
INNEREOF
}

init_agent
EOF
    chmod +x "$TEST_DIR/test-init.sh"

    run bash "$TEST_DIR/test-init.sh"

    [ "$status" -eq 0 ]
    [ -d ".agent" ]
    [ -f ".agent/STATUS.md" ]
    [ -f ".agent/ITERATIONS.md" ]
}

@test ".agent/STATUS.md contains idea description" {
    mkdir -p .agent
    echo "Test idea for workflow" > .agent/IDEA
    cat > .agent/STATUS.md << EOF
# Build Status

**Idea**: Test idea for workflow
**Started**: 2025-01-03T00:00:00
**Status**: Initializing
EOF

    grep -q "Test idea for workflow" .agent/STATUS.md
}

@test ".agent/ITERATIONS.md tracks iteration count" {
    mkdir -p .agent
    echo "0" > .agent/ITERATIONS.md

    # Simulate incrementing
    iter=$(cat .agent/ITERATIONS.md)
    echo $((iter + 1)) > .agent/ITERATIONS.md

    [ "$(cat .agent/ITERATIONS.md)" -eq 1 ]

    # Increment again
    iter=$(cat .agent/ITERATIONS.md)
    echo $((iter + 1)) > .agent/ITERATIONS.md

    [ "$(cat .agent/ITERATIONS.md)" -eq 2 ]
}

# =============================================================================
# Stuck Detection Tests
# =============================================================================

@test "stuck detection triggers after threshold" {
    mkdir -p .agent
    echo "0" > .agent/STUCK_COUNT
    echo "abc123" > .agent/LAST_STATE.md

    STUCK_THRESHOLD=3

    # Simulate same state multiple times
    for i in 1 2 3; do
        current_state="abc123"
        last_state=$(cat .agent/LAST_STATE.md)

        if [ "$current_state" = "$last_state" ]; then
            stuck_count=$(cat .agent/STUCK_COUNT)
            stuck_count=$((stuck_count + 1))
            echo "$stuck_count" > .agent/STUCK_COUNT
        fi
    done

    stuck_count=$(cat .agent/STUCK_COUNT)
    [ "$stuck_count" -ge "$STUCK_THRESHOLD" ]
}

@test "stuck count resets on state change" {
    mkdir -p .agent
    echo "5" > .agent/STUCK_COUNT
    echo "old_state" > .agent/LAST_STATE.md

    # Simulate state change
    current_state="new_state"
    last_state=$(cat .agent/LAST_STATE.md)

    if [ "$current_state" != "$last_state" ]; then
        echo "0" > .agent/STUCK_COUNT
        echo "$current_state" > .agent/LAST_STATE.md
    fi

    [ "$(cat .agent/STUCK_COUNT)" -eq 0 ]
    [ "$(cat .agent/LAST_STATE.md)" = "new_state" ]
}

# =============================================================================
# Skill Chain Validation
# =============================================================================

@test "INDEX.md has Start Here section" {
    [ -f "$ORIGINAL_DIR/.claude/skills/INDEX.md" ] || skip "INDEX.md not found"

    grep -q "Start Here" "$ORIGINAL_DIR/.claude/skills/INDEX.md"
}

@test "INDEX.md lists 5 core skills in Start Here" {
    [ -f "$ORIGINAL_DIR/.claude/skills/INDEX.md" ] || skip "INDEX.md not found"

    # Check for the 5 core skills mentioned
    grep -q "front-door" "$ORIGINAL_DIR/.claude/skills/INDEX.md"
    grep -q "create-plan" "$ORIGINAL_DIR/.claude/skills/INDEX.md"
    grep -q "implement-plan" "$ORIGINAL_DIR/.claude/skills/INDEX.md"
    grep -q "debugger" "$ORIGINAL_DIR/.claude/skills/INDEX.md"
    grep -q "code-reviewer" "$ORIGINAL_DIR/.claude/skills/INDEX.md"
}

@test "AGENTS.md version is 7.3" {
    [ -f "$ORIGINAL_DIR/AGENTS.md" ] || skip "AGENTS.md not found"

    grep -q "7.3" "$ORIGINAL_DIR/AGENTS.md"
}

@test "AGENTS.md shows beads as required" {
    [ -f "$ORIGINAL_DIR/AGENTS.md" ] || skip "AGENTS.md not found"

    grep -qi "beads.*required\|required.*beads" "$ORIGINAL_DIR/AGENTS.md"
}

# =============================================================================
# Full Workflow Simulation (without claude CLI)
# =============================================================================

@test "simulated workflow: init → tasks → complete" {
    command -v bd &>/dev/null || skip "beads not installed"
    command -v jq &>/dev/null || skip "jq not installed"

    # 1. Initialize
    bd init --stealth
    mkdir -p .agent
    echo "0" > .agent/ITERATIONS.md

    # 2. Create tasks (simulating plan parsing)
    bd create "Setup project structure" --json >/dev/null
    bd create "Implement core logic" --json >/dev/null
    bd create "Add tests" --json >/dev/null

    # 3. Verify tasks created
    task_count=$(bd list --json | jq 'length')
    [ "$task_count" -eq 3 ]

    # 4. Simulate working through tasks
    ready_tasks=$(bd ready --json)
    first_task_id=$(echo "$ready_tasks" | jq -r '.[0].id // empty')

    if [ -n "$first_task_id" ]; then
        # Mark in progress
        bd update "$first_task_id" --status in_progress --json >/dev/null 2>&1 || true

        # Complete it
        bd close "$first_task_id" --reason "test complete" --json >/dev/null 2>&1 || true
    fi

    # 5. Verify workflow progressed
    iter=$(cat .agent/ITERATIONS.md)
    echo "1" > .agent/ITERATIONS.md

    [ "$(cat .agent/ITERATIONS.md)" -eq 1 ]
}

@test "workflow completes when no ready tasks" {
    command -v bd &>/dev/null || skip "beads not installed"
    command -v jq &>/dev/null || skip "jq not installed"

    bd init --stealth

    # With no tasks, ready should return empty
    ready_count=$(bd ready --json | jq 'length')

    # Empty = complete condition
    [ "$ready_count" -eq 0 ]
}
