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
    "api/index.py"
    "api/system.py"
    "api/handlers/__init__.py"
    "api/handlers/auth.py"
    "api/handlers/members.py"
    "api/handlers/admin.py"
    "api/handlers/email.py"
    "vercel.json"
    "requirements.txt"
    "SETUP.md"
    "ARCHITECTURE.md"
    ".env.example"
    "public/css/theme.css"
    "public/config.js"
    "public/favicon.svg"
    "public/js/default-avatar.svg"
    "migrations/00_sites_table.sql"
    "migrations/01_schema_template.sql"
    "migrations/02_rls_template.sql"
    "public/js/auth.js"
)
for f in "${REQUIRED_FILES[@]}"; do
    check "$f exists" test -f "$TEMPLATE/$f"
done
echo ""

# 2. Old files should NOT exist
echo "--- 2. No old monolith handlers ---"
OLD_FILES=(
    "api/auth.py"
    "api/members.py"
    "api/admin.py"
    "api/email.py"
)
for f in "${OLD_FILES[@]}"; do
    if [ -f "$TEMPLATE/$f" ]; then
        echo "  $f should not exist ... FAIL"
        ((FAIL++))
    else
        echo "  $f absent ... PASS"
        ((PASS++))
    fi
done
echo ""

# 3. vercel.json is valid JSON
echo "--- 3. vercel.json validity ---"
check "valid JSON" python3 -c "import json; json.load(open('$TEMPLATE/vercel.json'))"
echo ""

# 4. Vercel function count (class handler) <= 12
echo "--- 4. Function count ---"
COUNT=$(grep -rl "class handler" "$TEMPLATE/api/"*.py 2>/dev/null | wc -l)
if [ "$COUNT" -le 12 ]; then
    echo "  $COUNT/12 handlers ... PASS"
    ((PASS++))
else
    echo "  $COUNT/12 handlers ... FAIL (exceeds 12)"
    ((FAIL++))
fi
echo ""

# 5. Router function exists and dispatches
echo "--- 5. Router function ---"
check "index.py has class handler" grep -q "class handler" "$TEMPLATE/api/index.py"
check "index.py imports handlers dict" grep -q "handlers" "$TEMPLATE/api/index.py"
check "index.py calls set_site" grep -q "set_site" "$TEMPLATE/api/index.py"
check "index.py calls site_exists" grep -q "site_exists" "$TEMPLATE/api/index.py"
echo ""

# 6. Multi-tenant helpers in _supabase.py
echo "--- 6. Multi-tenant support ---"
check "set_site function" grep -q "def set_site" "$TEMPLATE/api/_supabase.py"
check "site_exists function" grep -q "def site_exists" "$TEMPLATE/api/_supabase.py"
check "parse_request_path function" grep -q "def parse_request_path" "$TEMPLATE/api/_supabase.py"
check "Accept-Profile header" grep -q "Accept-Profile" "$TEMPLATE/api/_supabase.py"
echo ""

# 7. Env vars in .env.example are referenced in code
echo "--- 7. Env var references ---"
while IFS='=' read -r key _; do
    [[ "$key" =~ ^#.*$ || -z "$key" ]] && continue
    key="${key%%#*}"
    key="$(echo "$key" | xargs)"
    REFS=$(grep -rl "$key" "$TEMPLATE/api/" "$TEMPLATE/.github/" 2>/dev/null | wc -l)
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

# 8. Python syntax check
echo "--- 8. Python syntax ---"
find "$TEMPLATE/api" -name "*.py" -print0 | while IFS= read -r -d '' py; do
    basename_py="$(basename "$py")"
    check "$basename_py" python3 -m py_compile "$py"
done
echo ""

# 9. Tests pass
echo "--- 9. Tests ---"
check "pytest" bash -c "cd '$TEMPLATE' && PYTHONPATH=\"\$PWD\" python3 -m pytest tests/ -q 2>&1"
echo ""

# 10. Frontend uses multi-tenant helpers
echo "--- 10. Frontend multi-tenant ---"
check "auth.js has getSite" grep -q "getSite" "$TEMPLATE/public/js/auth.js"
check "auth.js has api()" grep -q "function api" "$TEMPLATE/public/js/auth.js"
echo ""

# 11. Design system
echo "--- 11. Design system ---"
check "theme.css has grain texture" grep -q "fractalNoise" "$TEMPLATE/public/css/theme.css"
check "theme.css has glassmorphism" grep -q "backdrop-filter" "$TEMPLATE/public/css/theme.css"
check "theme.css has Poppins" grep -q "Poppins" "$TEMPLATE/public/css/theme.css"
check "config.js loads theme" grep -q "loadConfig" "$TEMPLATE/public/config.js"
check "config.js has presets" grep -q "THEME_PRESETS" "$TEMPLATE/public/config.js"
check "HTML pages load theme.css" grep -rq 'theme.css' "$TEMPLATE/public/"*.html
check "HTML pages load config.js" grep -rq 'config.js' "$TEMPLATE/public/"*.html
check "favicon.svg exists" test -f "$TEMPLATE/public/favicon.svg"
check "default-avatar.svg exists" test -f "$TEMPLATE/public/js/default-avatar.svg"
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
