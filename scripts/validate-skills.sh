#!/bin/bash
# validate-skills.sh - Simple skill format validation
# Checks basic structure, not complex linting

set -e

SKILLS_DIR="${1:-.claude/skills}"
ERRORS=0

# Colors (optional, degrades gracefully)
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

log_error() {
    echo -e "${RED}ERROR${NC}: $1" >&2
    ((ERRORS++))
}

log_ok() {
    echo -e "${GREEN}OK${NC}: $1"
}

# Find all SKILL.md files
SKILL_FILES=$(find "$SKILLS_DIR" -name "SKILL.md" -type f 2>/dev/null)

if [ -z "$SKILL_FILES" ]; then
    echo "No SKILL.md files found in $SKILLS_DIR"
    exit 1
fi

echo "Validating skills in $SKILLS_DIR..."
echo ""

for skill_file in $SKILL_FILES; do
    skill_name=$(dirname "$skill_file" | xargs basename)
    skill_errors=0

    # Check 1: Has frontmatter
    if ! head -1 "$skill_file" | grep -q "^---$"; then
        log_error "$skill_name: Missing frontmatter (must start with ---)"
        ((skill_errors++))
        continue
    fi

    # Check 2: Has name field
    if ! grep -q "^name:" "$skill_file"; then
        log_error "$skill_name: Missing 'name:' field in frontmatter"
        ((skill_errors++))
    fi

    # Check 3: Has description field
    if ! grep -q "^description:" "$skill_file"; then
        log_error "$skill_name: Missing 'description:' field in frontmatter"
        ((skill_errors++))
    fi

    # Check 4: Has allowed-tools field
    if ! grep -q "^allowed-tools:" "$skill_file"; then
        log_error "$skill_name: Missing 'allowed-tools:' field in frontmatter"
        ((skill_errors++))
    fi

    # Check 5: Has closing frontmatter
    if [ "$(grep -c "^---$" "$skill_file")" -lt 2 ]; then
        log_error "$skill_name: Missing closing frontmatter (---)"
        ((skill_errors++))
    fi

    # Check 6: Line count bounds (50-500 reasonable range)
    lines=$(wc -l < "$skill_file")
    if [ "$lines" -lt 50 ]; then
        log_error "$skill_name: Too short ($lines lines, minimum 50)"
        ((skill_errors++))
    elif [ "$lines" -gt 500 ]; then
        log_error "$skill_name: Too long ($lines lines, maximum 500)"
        ((skill_errors++))
    fi

    # Check 7: Has Keywords section (for discoverability)
    if ! grep -q "^## Keywords" "$skill_file"; then
        log_error "$skill_name: Missing '## Keywords' section"
        ((skill_errors++))
    fi

    # Report status for this skill
    if [ $skill_errors -eq 0 ]; then
        log_ok "$skill_name ($lines lines)"
    fi
done

echo ""
echo "----------------------------------------"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}All skills validated successfully${NC}"
    exit 0
else
    echo -e "${RED}Found $ERRORS error(s)${NC}"
    exit 1
fi
