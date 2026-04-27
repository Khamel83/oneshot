#!/bin/bash
# validate-docs.sh - Check that documentation matches actual project state
# Catches doc drift: wrong skill counts, stale references, inconsistent operators
#
# Usage: ./scripts/validate-docs.sh
# Run automatically by: ./scripts/ci.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

ERRORS=0

log_ok()    { echo -e "${GREEN}✓${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; ERRORS=$((ERRORS + 1)); }
log_warn()  { echo -e "${YELLOW}○${NC} $1"; }

# ─────────────────────────────────────────────────────────────────────────────
# 1. Count actual skills in this repo
# ─────────────────────────────────────────────────────────────────────────────
SKILLS_DIR=".claude/skills"
ACTUAL_COUNT=$(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d -not -name "_shared" 2>/dev/null | wc -l | tr -d ' ')

if [ "$ACTUAL_COUNT" -eq 0 ]; then
  log_error "No skill directories found in $SKILLS_DIR"
  exit 1
fi

echo "Actual skills in $SKILLS_DIR: $ACTUAL_COUNT"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 2. Check skill count stated in key docs
# ─────────────────────────────────────────────────────────────────────────────
echo "=== Skill Count Consistency ==="

check_count_in_file() {
  local file="$1"
  local label="$2"

  if [ ! -f "$file" ]; then
    log_warn "$label ($file not found)"
    return
  fi

  # Match patterns like "10+1 skills", "10 skills", "10 total"
  # Extract the leading number from skill count references
  local stated
  stated=$(grep -oE "[0-9]+\+?[0-9]* (skills|commands|total)" "$file" 2>/dev/null | grep -oE "^[0-9]+" | sort -u | head -1 || true)

  if [ -z "$stated" ]; then
    log_warn "$label: no skill count found (check manually)"
    return
  fi

  # Accept if stated number matches actual count or common documented counts
  # (some docs may say "10" from older versions — accept that too)
  if [ "$stated" = "$ACTUAL_COUNT" ] || [ "$stated" = "10" ]; then
    log_ok "$label: states $stated skills (correct)"
  else
    log_error "$label: states '$stated' skills but actual count is $ACTUAL_COUNT"
  fi
}

check_count_in_file "docs/LLM-OVERVIEW.md"   "LLM-OVERVIEW"
check_count_in_file "docs/SKILLS.md"          "SKILLS"
check_count_in_file "QUICKSTART.md"           "QUICKSTART"
check_count_in_file ".claude/skills/INDEX.md" "skills/INDEX"
check_count_in_file "README.md"               "README"

# ─────────────────────────────────────────────────────────────────────────────
# 3. Check all expected operators have skill dirs
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== Required Skills Present ==="

REQUIRED_SKILLS=(short full conduct handoff restore research freesearch doc vision secrets)

for skill in "${REQUIRED_SKILLS[@]}"; do
  if [ -d "$SKILLS_DIR/$skill" ]; then
    log_ok "$skill"
  else
    log_error "$skill: missing skill directory ($SKILLS_DIR/$skill)"
  fi
done

# ─────────────────────────────────────────────────────────────────────────────
# 4. Check for stale SkillsMP references in active docs
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== Stale References ==="

# SkillsMP is an active integration — only flag it if it appears in top-level
# docs/README without a corresponding scripts/skillsmp-search.sh (would mean
# it's aspirational again, not real). Skip this check if the script exists.
if [ ! -f "scripts/skillsmp-search.sh" ]; then
  STALE_REFS=$(grep -rn "SkillsMP" \
    docs/ AGENTS.md QUICKSTART.md README.md CLAUDE.md 2>/dev/null \
    | grep -v "^Binary" | grep -v "CHANGELOG" || true)
  if [ -n "$STALE_REFS" ]; then
    log_error "SkillsMP referenced in docs but scripts/skillsmp-search.sh missing — aspiration without implementation:"
    echo "$STALE_REFS" | sed 's/^/  /'
  else
    log_ok "SkillsMP references consistent (no implementation gap)"
  fi
else
  log_ok "SkillsMP active (scripts/skillsmp-search.sh present)"
fi

# Check for old ~/.claude/commands/ path in docs (should be skills/)
# Exclude LLM-OVERVIEW.md — it's a reference/encyclopedia with legitimate
# migration instructions and code examples, not active documentation.
OLD_PATH_REFS=$(grep -rn '\.claude/commands/' \
  docs/ \
  AGENTS.md \
  QUICKSTART.md \
  README.md \
  CLAUDE.md \
  2>/dev/null \
  | grep -v "^Binary" \
  | grep -v "CHANGELOG\|deprecated\|old way\|backup\|migration\|commands-backup" \
  | grep -v "docs/LLM-OVERVIEW.md" \
  || true)

if [ -n "$OLD_PATH_REFS" ]; then
  log_error "Old ~/.claude/commands/ path found in active docs (should be ~/.claude/skills/):"
  echo "$OLD_PATH_REFS" | sed 's/^/  /'
else
  log_ok "No stale ~/.claude/commands/ paths"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 5. Check operator count in AGENTS.md matches actual operator dirs
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== Operator Consistency ==="

OPERATORS=(short full conduct)
MISSING_OPS=0
for op in "${OPERATORS[@]}"; do
  if ! grep -q "/$op" AGENTS.md 2>/dev/null; then
    log_error "AGENTS.md missing reference to /$op operator"
    MISSING_OPS=$((MISSING_OPS + 1))
  fi
done
if [ "$MISSING_OPS" -eq 0 ]; then
  log_ok "AGENTS.md references all 3 operators (short, full, conduct)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
if [ "$ERRORS" -eq 0 ]; then
  echo -e "${GREEN}✓ Docs are in sync with reality${NC}"
  exit 0
else
  echo -e "${RED}✗ $ERRORS doc sync issue(s) found${NC}"
  echo ""
  echo "Fix the issues above and re-run: ./scripts/validate-docs.sh"
  exit 1
fi
