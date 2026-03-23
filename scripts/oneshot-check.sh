#!/bin/bash
# oneshot-check.sh - Validate that this project's oneshot integration is healthy
# Installed to projects by oneshot.sh installer
#
# Checks:
#   1. All required skills are installed globally (~/.claude/skills/)
#   2. AGENTS.md exists in project root
#   3. CLAUDE.md exists and references AGENTS.md
#   4. No stale SkillsMP references in project docs
#
# Usage: ./scripts/oneshot-check.sh

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

log_ok()   { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}○${NC} $1"; WARNINGS=$((WARNINGS + 1)); }
log_error(){ echo -e "${RED}✗${NC} $1"; ERRORS=$((ERRORS + 1)); }

echo ""
echo "ONE_SHOT Integration Check"
echo "=========================="
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# 1. Skills installed globally
# ─────────────────────────────────────────────────────────────────────────────
echo "=== Global Skills (~/.claude/skills/) ==="

REQUIRED_SKILLS=(short full conduct handoff restore research freesearch doc vision secrets)
MISSING=0

for skill in "${REQUIRED_SKILLS[@]}"; do
  if [ -f "${HOME}/.claude/skills/$skill/SKILL.md" ]; then
    log_ok "$skill"
  else
    log_error "$skill: not installed (run: oneshot-update or curl -sL .../oneshot.sh | bash)"
    MISSING=$((MISSING + 1))
  fi
done

if [ "$MISSING" -gt 0 ]; then
  echo ""
  echo "  To install missing skills:"
  echo "  curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 2. Project files
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== Project Files ==="

if [ -f "AGENTS.md" ]; then
  VERSION=$(grep -oE "v[0-9]+" AGENTS.md | head -1 || echo "unknown")
  log_ok "AGENTS.md ($VERSION)"
else
  log_error "AGENTS.md missing — run oneshot.sh to create it"
fi

if [ -f "CLAUDE.md" ]; then
  if grep -q "AGENTS.md" CLAUDE.md; then
    log_ok "CLAUDE.md (references AGENTS.md)"
  else
    log_warn "CLAUDE.md exists but doesn't reference AGENTS.md (add: '> Read AGENTS.md for operator behaviors')"
  fi
else
  log_warn "CLAUDE.md missing — run oneshot.sh to create a starter version"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 3. Stale references in project docs
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== Stale References in Project Docs ==="

# Check for SkillsMP refs in any markdown files this project owns
STALE=$(grep -rn "SkillsMP\|\.claude/commands/" \
  --include="*.md" \
  --exclude-dir=".git" \
  --exclude="AGENTS.md" \
  . 2>/dev/null \
  | grep -v "deprecated\|old way\|backup\|migration\|commands-backup" \
  || true)

if [ -n "$STALE" ]; then
  log_warn "Stale oneshot references found in project docs:"
  echo "$STALE" | sed 's/^/  /'
  echo "  These may be leftover from an older oneshot version."
else
  log_ok "No stale oneshot references"
fi

# ─────────────────────────────────────────────────────────────────────────────
# 4. oneshot-update available
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== Tooling ==="

if command -v oneshot-update &>/dev/null; then
  log_ok "oneshot-update in PATH"
else
  log_warn "oneshot-update not in PATH (add ~/.local/bin to PATH)"
fi

# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────
echo ""
echo "=========================================="
if [ "$ERRORS" -eq 0 ] && [ "$WARNINGS" -eq 0 ]; then
  echo -e "${GREEN}✓ oneshot integration is healthy${NC}"
  exit 0
elif [ "$ERRORS" -eq 0 ]; then
  echo -e "${YELLOW}✓ oneshot healthy with $WARNINGS warning(s)${NC}"
  exit 0
else
  echo -e "${RED}✗ $ERRORS error(s), $WARNINGS warning(s)${NC}"
  echo ""
  echo "Run 'oneshot-update' to fix skill installation issues."
  exit 1
fi
