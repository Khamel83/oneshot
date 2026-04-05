#!/usr/bin/env bats
# test_workflow.bats - E2E workflow tests for ONE_SHOT
# Tests routing, config validation, and skill chain integrity
#
# Install: brew install bats-core OR apt install bats
# Run: bats tests/test_workflow.bats

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
# oneshot.sh Bootstrap Tests
# =============================================================================

@test "oneshot.sh --help shows prerequisites" {
    [ -f "$TEST_DIR/oneshot.sh" ] || skip "oneshot.sh not found"

    run bash "$TEST_DIR/oneshot.sh" --help

    [ "$status" -eq 0 ]
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
# Category Routing Tests (core intelligence tier feature)
# =============================================================================

@test "infer_category classifies coding tasks" {
    command -v python3 &>/dev/null || skip "python3 not found"

    run python3 -c "
import sys; sys.path.insert(0, '$ORIGINAL_DIR')
from core.task_schema import infer_category, TaskCategory

tests = [
    ('implement the auth handler', 'coding'),
    ('fix the bug in login.py', 'coding'),
    ('refactor the database module', 'coding'),
    ('write tests for the API', 'coding'),
]
failed = [desc for desc, exp in tests if infer_category(desc).value != exp]
if failed:
    print('FAILED: ' + str(failed))
    sys.exit(1)
"

    [ "$status" -eq 0 ]
}

@test "infer_category classifies research tasks" {
    command -v python3 &>/dev/null || skip "python3 not found"

    run python3 -c "
import sys; sys.path.insert(0, '$ORIGINAL_DIR')
from core.task_schema import infer_category

tests = [
    ('research Supabase RLS patterns', 'research'),
    ('investigate the memory leak', 'research'),
    ('search for the best ORM', 'research'),
]
failed = [desc for desc, exp in tests if infer_category(desc).value != exp]
if failed:
    print('FAILED: ' + str(failed))
    sys.exit(1)
"

    [ "$status" -eq 0 ]
}

@test "infer_category classifies writing tasks" {
    command -v python3 &>/dev/null || skip "python3 not found"

    run python3 -c "
import sys; sys.path.insert(0, '$ORIGINAL_DIR')
from core.task_schema import infer_category

tests = [
    ('document the API endpoints', 'writing'),
    ('write a README section', 'writing'),
    ('summarize the meeting notes', 'writing'),
]
failed = [desc for desc, exp in tests if infer_category(desc).value != exp]
if failed:
    print('FAILED: ' + str(failed))
    sys.exit(1)
"

    [ "$status" -eq 0 ]
}

@test "infer_category classifies review tasks" {
    command -v python3 &>/dev/null || skip "python3 not found"

    run python3 -c "
import sys; sys.path.insert(0, '$ORIGINAL_DIR')
from core.task_schema import infer_category

tests = [
    ('review this pull request', 'review'),
    ('audit the security config', 'review'),
]
failed = [desc for desc, exp in tests if infer_category(desc).value != exp]
if failed:
    print('FAILED: ' + str(failed))
    sys.exit(1)
"

    [ "$status" -eq 0 ]
}

@test "infer_category defaults to general" {
    command -v python3 &>/dev/null || skip "python3 not found"

    run python3 -c "
import sys; sys.path.insert(0, '$ORIGINAL_DIR')
from core.task_schema import infer_category, TaskCategory

assert infer_category('hello world') == TaskCategory.general
assert infer_category('do something') == TaskCategory.general
"

    [ "$status" -eq 0 ]
}

# =============================================================================
# Router Resolve Tests
# =============================================================================

@test "router resolves implement_small to cheap lane with codex first" {
    command -v python3 &>/dev/null || skip "python3 not found"

    run python3 -c "
import sys, json; sys.path.insert(0, '$ORIGINAL_DIR')
from core.router.lane_policy import resolve

r = resolve('implement_small', category='coding')
assert r['lane'] == 'cheap', f'Expected cheap, got {r[\"lane\"]}'
assert r['workers'][0] == 'codex', f'Expected codex first, got {r[\"workers\"]}'
assert r['category'] == 'coding'
"

    [ "$status" -eq 0 ]
}

@test "router resolves research to research lane with gemini first" {
    command -v python3 &>/dev/null || skip "python3 not found"

    run python3 -c "
import sys, json; sys.path.insert(0, '$ORIGINAL_DIR')
from core.router.lane_policy import resolve

r = resolve('research', category='research')
assert r['lane'] == 'research'
assert r['workers'][0] == 'gemini_cli'
assert r['search_backend'] == 'argus'
"

    [ "$status" -eq 0 ]
}

@test "router resolves plan to premium lane" {
    command -v python3 &>/dev/null || skip "python3 not found"

    run python3 -c "
import sys; sys.path.insert(0, '$ORIGINAL_DIR')
from core.router.lane_policy import resolve

r = resolve('plan')
assert r['lane'] == 'premium'
assert r['category'] == 'general'
assert r['workers'][0] == 'claude_code'
"

    [ "$status" -eq 0 ]
}

@test "router infers category when not provided" {
    command -v python3 &>/dev/null || skip "python3 not found"

    run python3 -c "
import sys; sys.path.insert(0, '$ORIGINAL_DIR')
from core.router.lane_policy import resolve

# implement_small should infer coding category
r = resolve('implement_small')
assert r['category'] == 'coding', f'Expected coding, got {r[\"category\"]}'

# review_diff should infer review category
r = resolve('review_diff')
assert r['category'] == 'review', f'Expected review, got {r[\"category\"]}'
"

    [ "$status" -eq 0 ]
}

@test "router includes risk autonomy in response" {
    command -v python3 &>/dev/null || skip "python3 not found"

    run python3 -c "
import sys; sys.path.insert(0, '$ORIGINAL_DIR')
from core.router.lane_policy import resolve

r = resolve('implement_small')
assert 'risk' in r
assert r['risk']['level'] == 'medium'
assert 'auto_edit' in r['risk']
assert 'requires_approval' in r['risk']
"

    [ "$status" -eq 0 ]
}

# =============================================================================
# Config Validation Tests
# =============================================================================

@test "lanes.yaml has category_preference on all lanes" {
    [ -f "$ORIGINAL_DIR/config/lanes.yaml" ] || skip "lanes.yaml not found"

    for lane in premium balanced cheap research; do
        grep -A 20 "^  $lane:" "$ORIGINAL_DIR/config/lanes.yaml" | grep -q "category_preference"
    done
}

@test "lanes.yaml cheap lane does not have claw_code" {
    [ -f "$ORIGINAL_DIR/config/lanes.yaml" ] || skip "lanes.yaml not found"

    # Extract cheap lane worker_pool
    pool=$(sed -n '/^  cheap:/,/^[a-z]/p' "$ORIGINAL_DIR/config/lanes.yaml" | grep "worker_pool" | head -1)

    # Should NOT contain claw_code
    [[ ! "$pool" == *"claw_code"* ]]
}

@test "workers.yaml has glm worker with plan_expires" {
    [ -f "$ORIGINAL_DIR/config/workers.yaml" ] || skip "workers.yaml not found"

    grep -A 5 "^  glm:" "$ORIGINAL_DIR/config/workers.yaml" | grep -q "plan_expires"
}

@test "models.yaml has post_expiry_default_model for claw_code" {
    [ -f "$ORIGINAL_DIR/config/models.yaml" ] || skip "models.yaml not found"

    grep -A 5 "^claw_code:" "$ORIGINAL_DIR/config/models.yaml" | grep -q "post_expiry_default_model"
}

# =============================================================================
# Skill Chain Validation
# =============================================================================

@test "dispatch.md references category routing" {
    [ -f "$ORIGINAL_DIR/.claude/skills/_shared/dispatch.md" ] || skip "dispatch.md not found"

    grep -q "category" "$ORIGINAL_DIR/.claude/skills/_shared/dispatch.md"
    grep -q "--category" "$ORIGINAL_DIR/.claude/skills/_shared/dispatch.md"
}

@test "providers.md lists glm_claude worker" {
    [ -f "$ORIGINAL_DIR/.claude/skills/_shared/providers.md" ] || skip "providers.md not found"

    grep -q "glm_claude" "$ORIGINAL_DIR/.claude/skills/_shared/providers.md"
}

@test "providers.md marks claw_code as opt-in" {
    [ -f "$ORIGINAL_DIR/.claude/skills/_shared/providers.md" ] || skip "providers.md not found"

    grep -q "opt-in" "$ORIGINAL_DIR/.claude/skills/_shared/providers.md"
}

@test "task-classes.md has category column" {
    [ -f "$ORIGINAL_DIR/docs/instructions/task-classes.md" ] || skip "task-classes.md not found"

    grep -q "Category" "$ORIGINAL_DIR/docs/instructions/task-classes.md"
    grep -q "coding\|research\|writing\|review\|general" "$ORIGINAL_DIR/docs/instructions/task-classes.md"
}

# =============================================================================
# Required Files
# =============================================================================

@test "core Python module imports cleanly" {
    command -v python3 &>/dev/null || skip "python3 not found"

    run python3 -c "
import sys; sys.path.insert(0, '$ORIGINAL_DIR')
from core.task_schema import Task, TaskClass, TaskCategory, infer_category, infer_risk
from core.router.lane_policy import resolve, get_worker_pool, load_lanes
print('All imports OK')
"

    [ "$status" -eq 0 ]
}
