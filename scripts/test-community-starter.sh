#!/usr/bin/env bash
# test-community-starter.sh — Validate the community-starter template
# Run from oneshot repo root. Fails fast on first error.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE="$REPO_ROOT/templates/community-starter"
PASS=0
FAIL=0

check() {
    local name="$1"
    shift
    echo -n "  $name ... "
    if "$@"; then
        echo "PASS"
        ((PASS++))
    else
        echo "FAIL"
        ((FAIL++))
    fi
}

echo "=== Community Starter Validation ==="
echo ""

# 1. Required files
echo "--- 1. Required files ---"
REQUIRED_FILES=(
    "api/_supabase.py"
    "api/auth.py"
    "api/members.py"
    "api/admin.py"
    "api/email.py"
    "api/system.py"
    "vercel.json"
    "requirements.txt"
    "SETUP.md"
    ".env.example"
    "migrations/01_schema.sql"
    "migrations/02_rls.sql"
    "public/js/auth.js"
)
for f in "${REQUIRED_FILES[@]}"; do
    check "$f exists" test -f "$TEMPLATE/$f"
done
echo ""

# 2. vercel.json is valid JSON
echo "--- 2. vercel.json validity ---"
check "valid JSON" python3 -c "import json; json.load(open('$TEMPLATE/vercel.json'))"
echo ""

# 3. Vercel function count <= 12
echo "--- 3. Function count ---"
COUNT=$(grep -rl "class handler" "$TEMPLATE/api/"*.py 2>/dev/null | wc -l)
if [ "$COUNT" -le 12 ]; then
    echo "  $COUNT/12 handlers ... PASS"
    ((PASS++))
else
    echo "  $COUNT/12 handlers ... FAIL (exceeds 12)"
    ((FAIL++))
fi
echo ""

# 4. Env vars in .env.example are referenced in code
echo "--- 4. Env var references ---"
while IFS='=' read -r key _; do
    # Skip comments and empty lines
    [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
    # Strip any inline comment
    key="${key%%#*}"
    key="$(echo "$key" | xargs)"  # trim whitespace
    REFS=$(grep -rl "$key" "$TEMPLATE/api/" "$TEMPLATE/.github/" 2>/dev/null | wc -l)
    # Also check tests (accept refs in tests as valid)
    REFS_TESTS=$(grep -rl "$key" "$TEMPLATE/tests/" 2>/dev/null | wc -l)
    TOTAL=$((REFS + REFS_TESTS))
    if [ "$TOTAL" -gt 0 ]; then
        echo "  $key: $TOTAL refs ... PASS"
        ((PASS++))
    else
        echo "  $key: $TOTAL refs ... FAIL"
        ((FAIL++))
    fi
done < "$TEMPLATE/.env.example"
echo ""

# 5. Python syntax check
echo "--- 5. Python syntax ---"
for py in "$TEMPLATE/api/"*.py; do
    basename_py="$(basename "$py")"
    check "$basename_py" python3 -m py_compile "$py"
done
echo ""

# 6. Tests pass
echo "--- 6. Tests ---"
check "pytest" bash -c "cd '$TEMPLATE' && PYTHONPATH=\"\$PWD\" python3 -m pytest tests/ -q 2>&1"
echo ""

# Summary
echo "=== Results ==="
echo "  Passed: $PASS"
echo "  Failed: $FAIL"
echo ""

if [ "$FAIL" -gt 0 ]; then
    echo "VALIDATION FAILED"
    exit 1
else
    echo "ALL CHECKS PASSED"
    exit 0
fi
