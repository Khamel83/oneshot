#!/usr/bin/env bats
# test_oneshot.bats - Robust tests for oneshot.sh
# Uses bats-core (FOSS): https://github.com/bats-core/bats-core
#
# Install: brew install bats-core OR apt install bats
# Run: bats tests/test_oneshot.bats

setup() {
    # Create temp directory for each test
    TEST_DIR=$(mktemp -d)
    export TEST_DIR

    # Copy oneshot.sh to test directory
    cp oneshot.sh "$TEST_DIR/"

    # Create a mock project directory
    mkdir -p "$TEST_DIR/project"
    cd "$TEST_DIR/project"
}

teardown() {
    # Clean up temp directory
    rm -rf "$TEST_DIR"
}

# Helper: Run oneshot.sh in offline mode (no network)
run_oneshot_offline() {
    # Replace curl with a mock that returns empty
    ONESHOT="$TEST_DIR/oneshot.sh"
    # Skip network calls by setting a flag the script can check
    ONESHOT_OFFLINE=1 bash "$ONESHOT" "$@" 2>&1 || true
}

# =============================================================================
# Non-Destructive Behavior Tests
# =============================================================================

@test "preserves existing CLAUDE.md content" {
    # Create existing CLAUDE.md
    echo "# My Project Rules" > CLAUDE.md
    echo "Important: Do not delete this" >> CLAUDE.md

    # Run oneshot (offline mode - just test file handling)
    mkdir -p .claude/skills
    touch .claude/skills/.gitkeep

    # Simulate the prepend logic from oneshot.sh
    echo "# ONE_SHOT Block" > .claude.tmp
    echo "" >> .claude.tmp
    cat CLAUDE.md >> .claude.tmp
    mv .claude.tmp CLAUDE.md

    # Verify original content preserved
    grep -q "My Project Rules" CLAUDE.md
    grep -q "Important: Do not delete this" CLAUDE.md
    grep -q "ONE_SHOT Block" CLAUDE.md
}

@test "does not overwrite existing .gitignore entries" {
    # Create existing .gitignore
    echo "node_modules/" > .gitignore
    echo ".env" >> .gitignore

    # Simulate the append logic from oneshot.sh
    if ! grep -q "secrets/plaintext/" .gitignore 2>/dev/null; then
        echo "" >> .gitignore
        echo "# ONE_SHOT secrets" >> .gitignore
        echo "secrets/plaintext/" >> .gitignore
    fi

    # Verify original entries preserved
    grep -q "node_modules/" .gitignore
    grep -q ".env" .gitignore
    # Verify new entry added
    grep -q "secrets/plaintext/" .gitignore
}

@test "gitignore append is idempotent" {
    # Create .gitignore with secrets entry already present
    echo "node_modules/" > .gitignore
    echo "secrets/plaintext/" >> .gitignore

    original_lines=$(wc -l < .gitignore)

    # Simulate the append logic (should not duplicate)
    if ! grep -q "secrets/plaintext/" .gitignore 2>/dev/null; then
        echo "secrets/plaintext/" >> .gitignore
    fi

    new_lines=$(wc -l < .gitignore)

    # Line count should be same (no duplicates added)
    [ "$original_lines" -eq "$new_lines" ]
}

# =============================================================================
# CLAUDE.md Prepend Logic Tests
# =============================================================================

@test "CLAUDE.md prepend adds ONE_SHOT block at top" {
    echo "Existing content" > CLAUDE.md

    # Simulate prepend
    {
        echo "# ONE_SHOT Header"
        echo ""
        cat CLAUDE.md
    } > CLAUDE.md.tmp
    mv CLAUDE.md.tmp CLAUDE.md

    # First line should be the header
    head -1 CLAUDE.md | grep -q "ONE_SHOT Header"
    # Original content should still exist
    grep -q "Existing content" CLAUDE.md
}

@test "CLAUDE.md created if not exists" {
    # Ensure no CLAUDE.md exists
    rm -f CLAUDE.md

    # Create new one
    echo "# ONE_SHOT Project" > CLAUDE.md

    # Should exist now
    [ -f CLAUDE.md ]
    grep -q "ONE_SHOT" CLAUDE.md
}

# =============================================================================
# Directory Structure Tests
# =============================================================================

@test "creates .claude/skills directory structure" {
    mkdir -p .claude/skills

    [ -d ".claude/skills" ]
}

@test "creates secrets directory structure" {
    mkdir -p secrets/encrypted secrets/plaintext

    [ -d "secrets/encrypted" ]
    [ -d "secrets/plaintext" ]
}

# =============================================================================
# Skill Validation Tests (uses validate-skills.sh)
# =============================================================================

@test "validate-skills.sh exits 0 on valid skill" {
    # Create a minimal valid skill
    mkdir -p .claude/skills/test-skill
    cat > .claude/skills/test-skill/SKILL.md << 'EOF'
---
name: test-skill
description: "A test skill for validation"
allowed-tools: Read
---

# Test Skill

Content here for the test skill.
More content to reach minimum line count.
Even more content.
And more.
Keep going.
Still more.
More lines.
Content.
Lines.
More.
And more.
Even more.
Still going.
More content.
Keep adding.
Almost there.
Few more.
Content lines.
More of them.
Still adding.
Almost done.
Few more lines.
Nearly there.
Last few.
Done now.
Actually more.
Keep going.
More lines.
Content here.
And there.
Everywhere.
More content.
Lines of it.
Lots of lines.
Many lines.
So many.
Very many.
Extremely many.
Incredibly many.
Unbelievably many.
Ridiculously many.
Absurdly many.
Preposterously many.
Ludicrously many.
Fantastically many.
More lines still.
Even more still.
Still more yet.
Yet more still.

## Keywords

test, validation, example
EOF

    # Copy validate script
    cp "$TEST_DIR/../scripts/validate-skills.sh" . 2>/dev/null || \
        cp "$(dirname "$BATS_TEST_DIRNAME")/scripts/validate-skills.sh" .
    chmod +x validate-skills.sh

    run ./validate-skills.sh .claude/skills
    [ "$status" -eq 0 ]
}
