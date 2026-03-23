#!/bin/bash
# ONE_SHOT Verify Loop - Run this after changes
# Usage: ./scripts/ci.sh [--quick]
#   --quick: Skip slow checks (integration tests, validation)

set -e

QUICK_MODE=false
if [[ "$1" == "--quick" ]]; then
    QUICK_MODE=true
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

ERRORS=0

section() {
    echo ""
    echo -e "${YELLOW}=== $1 ===${NC}"
}

log_ok() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
    ((ERRORS++))
}

log_skip() {
    echo -e "${YELLOW}○${NC} $1 (skipped)"
}

# 1. Shell Scripts (shellcheck)
section "Lint: Shell Scripts"
if command -v shellcheck &>/dev/null; then
    SHELL_FILES=$(find . -name "*.sh" -not -path "./node_modules/*" -not -path "./.git/*" 2>/dev/null | head -20)
    if [ -n "$SHELL_FILES" ]; then
        if shellcheck $SHELL_FILES 2>&1; then
            log_ok "All shell scripts pass shellcheck"
        else
            log_error "Shellcheck found issues"
        fi
    else
        log_skip "No shell scripts found"
    fi
else
    log_skip "shellcheck not installed"
fi

# 2. Prettier (JS/TS/JSON/MD)
section "Lint: Prettier"
if command -v prettier &>/dev/null; then
    if [ -f ".prettierrc" ] || [ -f ".prettierrc.json" ] || [ -f "package.json" ]; then
        if prettier --check "**/*.{js,ts,json,md}" --ignore-path .gitignore 2>&1; then
            log_ok "All files formatted correctly"
        else
            log_error "Prettier found formatting issues (run: prettier --write .)"
        fi
    else
        log_skip "No prettier config found"
    fi
else
    log_skip "prettier not installed"
fi

# 3. TypeScript
section "Typecheck: TypeScript"
if [ -f "tsconfig.json" ]; then
    if command -v tsc &>/dev/null; then
        if tsc --noEmit 2>&1; then
            log_ok "TypeScript passes"
        else
            log_error "TypeScript errors found"
        fi
    else
        log_skip "tsc not installed"
    fi
else
    log_skip "No tsconfig.json found"
fi

# 4. Python
section "Typecheck: Python"
if ls *.py **/*.py 2>/dev/null | head -1 | grep -q .; then
    if command -v pyright &>/dev/null; then
        if pyright 2>&1; then
            log_ok "Pyright passes"
        else
            log_error "Pyright found issues"
        fi
    elif command -v mypy &>/dev/null; then
        if mypy . 2>&1; then
            log_ok "Mypy passes"
        else
            log_error "Mypy found issues"
        fi
    else
        log_skip "No Python type checker installed"
    fi
else
    log_skip "No Python files found"
fi

# 5. Bats Tests
section "Tests: Bats (Shell)"
if command -v bats &>/dev/null; then
    if [ -d "tests" ]; then
        BATS_FILES=$(find tests -name "*.bats" 2>/dev/null | head -10)
        if [ -n "$BATS_FILES" ]; then
            if bats tests/ 2>&1; then
                log_ok "All bats tests pass"
            else
                log_error "Bats tests failed"
            fi
        else
            log_skip "No .bats files found"
        fi
    else
        log_skip "No tests/ directory"
    fi
else
    log_skip "bats not installed"
fi

# 6. Pytest
section "Tests: Pytest"
if ls **/test_*.py **/*_test.py 2>/dev/null | head -1 | grep -q .; then
    if command -v pytest &>/dev/null; then
        if pytest --tb=short -q 2>&1; then
            log_ok "All pytest tests pass"
        else
            log_error "Pytest tests failed"
        fi
    else
        log_skip "pytest not installed"
    fi
else
    log_skip "No pytest test files found"
fi

# 7. ONE_SHOT Validation (skip in quick mode)
if [ "$QUICK_MODE" = false ]; then
    section "Validation: ONE_SHOT Skills"
    if [ -f "scripts/validate-skills.sh" ]; then
        if bash scripts/validate-skills.sh 2>&1; then
            log_ok "Skills validation passed"
        else
            log_error "Skills validation failed"
        fi
    else
        log_skip "No validate-skills.sh found"
    fi

    section "Validation: ONE_SHOT Docs Sync"
    if [ -f "scripts/validate-docs.sh" ]; then
        if bash scripts/validate-docs.sh 2>&1; then
            log_ok "Docs are in sync with reality"
        else
            log_error "Doc sync check failed — docs don't match actual state"
        fi
    else
        log_skip "No validate-docs.sh found"
    fi

    section "Validation: ONE_SHOT Agents"
    if [ -f "scripts/validate-agents.py" ]; then
        if python scripts/validate-agents.py 2>&1; then
            log_ok "Agents validation passed"
        else
            log_error "Agents validation failed"
        fi
    else
        log_skip "No validate-agents.py found"
    fi
fi

# Summary
echo ""
echo "=========================================="
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED${NC}"
    exit 0
else
    echo -e "${RED}✗ $ERRORS CHECK(S) FAILED${NC}"
    exit 1
fi
