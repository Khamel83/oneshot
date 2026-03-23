#!/bin/bash
# ONE_SHOT Bootstrap Script v13
# Usage: curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
#
# Options:
#   --upgrade    Update all skills to latest version (overwrites existing)
#   --help       Show this help
#
# NON-DESTRUCTIVE: Only adds to your project, never overwrites existing files.
# - Existing CLAUDE.md? Left untouched (prints reminder to reference AGENTS.md)
# - Existing .gitignore? Appends ONE_SHOT block only if not present
#
# Optional: ~/.age/key.txt for secrets encryption
# Get Age: sudo apt install age || brew install age
# Generate key: age-keygen -o ~/.age/key.txt

set -euo pipefail

# Parse arguments
UPGRADE_MODE=false
FORCE_MODE=false
for arg in "$@"; do
  case $arg in
    --upgrade)
      UPGRADE_MODE=true
      shift
      ;;
    --force)
      FORCE_MODE=true
      shift
      ;;
    --help)
      echo "ONE_SHOT Bootstrap Script v13"
      echo ""
      echo "Usage:"
      echo "  curl -sL .../oneshot.sh | bash                   # Install"
      echo "  curl -sL .../oneshot.sh | bash -s -- --upgrade   # Update skills"
      echo ""
      echo "Prerequisites:"
      echo "  age    sudo apt install age (optional, for secrets)"
      echo ""
      echo "Options:"
      echo "  --upgrade    Update all skills to latest version"
      echo "  --help       Show this help"
      echo ""
      echo "What gets installed globally (~/.claude/):"
      echo "  Skills:      10 skills in ~/.claude/skills/"
      echo "  install.sh:  symlink to oneshot-update at ~/.local/bin/"
      echo ""
      echo "What gets added to your project:"
      echo "  AGENTS.md    Operator spec (read-only, curl from oneshot)"
      echo "  CLAUDE.md    Project instructions (created if missing)"
      echo ""
      echo "Never touched:"
      echo "  Existing CLAUDE.md, your custom skills"
      exit 0
      ;;
  esac
done

ONESHOT_BASE="https://raw.githubusercontent.com/Khamel83/oneshot/master"
SKILLS_BASE="$ONESHOT_BASE/.claude/skills"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
if [ "$UPGRADE_MODE" = true ]; then
  echo -e "${BLUE}ONE_SHOT Upgrade v13${NC}"
  echo "====================="
else
  echo -e "${BLUE}ONE_SHOT Bootstrap v13${NC}"
  echo "========================"
fi
echo ""

# Check for Age key (optional)
if [ ! -f ~/.age/key.txt ]; then
  echo -e "  ${YELLOW}○${NC} Age key (optional for secrets): mkdir -p ~/.age && age-keygen -o ~/.age/key.txt"
fi

# =============================================================================
# 1. AGENTS.md - The operator spec (smart update, respects local changes)
# =============================================================================
update_agents_md() {
  local AGENTS_FILE="AGENTS.md"
  local FORCE_UPDATE="${1:-false}"

  if [[ ! -f "$AGENTS_FILE" ]]; then
    curl -sL "$ONESHOT_BASE/AGENTS.md" > "$AGENTS_FILE"
    echo -e "  ${GREEN}✓${NC} AGENTS.md (created)"
    return 0
  fi

  # In a git repo: check for local modifications
  if git rev-parse --git-dir >/dev/null 2>&1; then
    if git status --porcelain "$AGENTS_FILE" 2>/dev/null | grep -qE "^[AM]"; then
      if [[ "$FORCE_UPDATE" == "true" ]]; then
        echo -e "  ${YELLOW}⚠${NC} AGENTS.md (force overwrite with --force)"
      else
        echo -e "  ${YELLOW}○${NC} AGENTS.md (locally modified, use --force to update)"
        return 0
      fi
    fi
  fi

  curl -sL "$ONESHOT_BASE/AGENTS.md" > "$AGENTS_FILE"
  echo -e "  ${GREEN}✓${NC} AGENTS.md (updated)"
}

update_agents_md "$FORCE_MODE"

# =============================================================================
# 2. CLAUDE.md - Create minimal version if missing, never overwrite
# =============================================================================
if [ ! -f CLAUDE.md ]; then
  cat > CLAUDE.md << 'EOF'
# Project Instructions

> Read AGENTS.md for operator behaviors and skill routing.

## Overview
[Brief description of what this project does]

## Key Commands
```bash
# Setup
# Run
# Test
```

## Architecture
[Key architectural decisions]

## Conventions
[Project-specific conventions]
EOF
  echo -e "  ${GREEN}✓${NC} CLAUDE.md (created)"
else
  if ! grep -q "AGENTS.md" CLAUDE.md; then
    echo -e "  ${YELLOW}→${NC} CLAUDE.md (exists — add a reference to AGENTS.md if needed)"
  else
    echo -e "  ${GREEN}✓${NC} CLAUDE.md (exists, skipped)"
  fi
fi

# =============================================================================
# 3. Global skills — installed to ~/.claude/skills/ (not project-local)
# =============================================================================
SKILLS=(
  short
  full
  conduct
  handoff
  restore
  research
  freesearch
  doc
  vision
  secrets
)

mkdir -p "${HOME}/.claude/skills"
SKILLS_ADDED=0
SKILLS_UPDATED=0
SKILLS_SKIPPED=0

for skill in "${SKILLS[@]}"; do
  SKILL_FILE="${HOME}/.claude/skills/$skill/SKILL.md"
  if [ ! -f "$SKILL_FILE" ]; then
    mkdir -p "${HOME}/.claude/skills/$skill"
    if curl -sL "$SKILLS_BASE/$skill/SKILL.md" -o "$SKILL_FILE" 2>/dev/null; then
      SKILLS_ADDED=$((SKILLS_ADDED + 1))
    fi
  elif [ "$UPGRADE_MODE" = true ]; then
    if curl -sL "$SKILLS_BASE/$skill/SKILL.md" -o "$SKILL_FILE" 2>/dev/null; then
      SKILLS_UPDATED=$((SKILLS_UPDATED + 1))
    fi
  else
    SKILLS_SKIPPED=$((SKILLS_SKIPPED + 1))
  fi
done

# Also sync INDEX.md and SKILLS_REFERENCE.md
curl -sL "$SKILLS_BASE/../skills/INDEX.md" -o "${HOME}/.claude/skills/INDEX.md" 2>/dev/null || true
curl -sL "$SKILLS_BASE/../skills/SKILLS_REFERENCE.md" -o "${HOME}/.claude/skills/SKILLS_REFERENCE.md" 2>/dev/null || true

if [ "$UPGRADE_MODE" = true ]; then
  echo -e "  ${GREEN}✓${NC} ~/.claude/skills/ (${SKILLS_ADDED} added, ${SKILLS_UPDATED} updated, 10 total)"
else
  echo -e "  ${GREEN}✓${NC} ~/.claude/skills/ (${SKILLS_ADDED} added, ${SKILLS_SKIPPED} existing, 10 total)"
fi

# =============================================================================
# 4. Install oneshot-update to PATH
# =============================================================================
BIN_DIR="${HOME}/.local/bin"
mkdir -p "$BIN_DIR"
ONESHOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo "$HOME/github/oneshot")"

if [ -f "$ONESHOT_DIR/scripts/oneshot-update.sh" ]; then
  ln -sf "$ONESHOT_DIR/scripts/oneshot-update.sh" "$BIN_DIR/oneshot-update"
  echo -e "  ${GREEN}✓${NC} oneshot-update (linked to $BIN_DIR)"
else
  # Running via curl - download the update script
  curl -sL "$ONESHOT_BASE/scripts/oneshot-update.sh" -o "$BIN_DIR/oneshot-update" 2>/dev/null
  chmod +x "$BIN_DIR/oneshot-update"
  echo -e "  ${GREEN}✓${NC} oneshot-update (installed to $BIN_DIR)"
fi

# =============================================================================
# 5. .sops.yaml - Create if not exists (never overwrite)
# =============================================================================
if [ ! -f .sops.yaml ]; then
  cat > .sops.yaml << 'EOF'
# SOPS configuration for secrets encryption
# Uses Age encryption: https://github.com/FiloSottile/age
creation_rules:
  - age: age1kwu32vl7x3tx7dqphzykcf5cahgm4ejztm865f22fkwe5j6hwalqh0rau8
    path_regex: '.*\.encrypted$'
EOF
  echo -e "  ${GREEN}✓${NC} .sops.yaml (created)"
else
  echo -e "  ${GREEN}✓${NC} .sops.yaml (exists, skipped)"
fi

# =============================================================================
# 6. scripts/ — Project-level tooling
# =============================================================================
mkdir -p scripts

_install_script() {
  local name="$1"
  local file="scripts/$name"
  if [ ! -f "$file" ] || [ "$UPGRADE_MODE" = true ]; then
    if curl -sL "$ONESHOT_BASE/scripts/$name" -o "$file" 2>/dev/null; then
      chmod +x "$file"
      echo -e "  ${GREEN}✓${NC} $file ($([ "$UPGRADE_MODE" = true ] && echo updated || echo created))"
    else
      echo -e "  ${YELLOW}○${NC} $file (download failed)"
    fi
  else
    echo -e "  ${GREEN}✓${NC} $file (exists, skipped)"
  fi
}

_install_script oneshot-check.sh
_install_script skillsmp-search.sh
_install_script secrets-helper.sh

# =============================================================================
# 7. 1shot/ - Project working directory (visible in repo, not dot-prefixed)
# =============================================================================
mkdir -p 1shot/skills

# LLM-OVERVIEW.md — created if missing, never overwritten
if [ ! -f "1shot/LLM-OVERVIEW.md" ]; then
  PROJECT_NAME=$(basename "$(pwd)")
  TODAY=$(date +%Y-%m-%d)
  curl -sL "$ONESHOT_BASE/templates/LLM-OVERVIEW.md" 2>/dev/null \
    | sed "s/\[PROJECT NAME\]/$PROJECT_NAME/" \
    | sed "s/\[date\]/$TODAY/g" \
    > "1shot/LLM-OVERVIEW.md" || cat > "1shot/LLM-OVERVIEW.md" << EOF
# LLM-OVERVIEW: $PROJECT_NAME

> Complete context for any LLM to understand this project.
> **Last Updated**: $TODAY
> **Status**: Active Development

---

## 1. WHAT IS THIS?
[Describe what this project does]

## 2. ARCHITECTURE
[Key components and stack]

## 3. KEY FILES
| File | Purpose |
|------|---------|
| \`AGENTS.md\` | ONE_SHOT operator spec |
| \`CLAUDE.md\` | Project-specific Claude instructions |
| \`1shot/PROJECT.md\` | Current goals and acceptance criteria |

## 4. HOW TO RUN
\`\`\`bash
# [add commands here]
\`\`\`

## 5. CURRENT STATE
[What's working, what's in progress]
EOF
  echo -e "  ${GREEN}✓${NC} 1shot/LLM-OVERVIEW.md (created)"
else
  echo -e "  ${GREEN}✓${NC} 1shot/LLM-OVERVIEW.md (exists, skipped)"
fi

# .gitkeep so skills/ is tracked even when empty
if [ ! -f "1shot/skills/.gitkeep" ] && [ -z "$(ls -A 1shot/skills 2>/dev/null)" ]; then
  touch 1shot/skills/.gitkeep
fi

echo -e "  ${GREEN}✓${NC} 1shot/skills/ (ready for SkillsMP pulls)"

# Install skillsmp-search.sh for use in this project
mkdir -p scripts
if [ ! -f "scripts/skillsmp-search.sh" ] || [ "$UPGRADE_MODE" = true ]; then
  if curl -sL "$ONESHOT_BASE/scripts/skillsmp-search.sh" -o scripts/skillsmp-search.sh 2>/dev/null; then
    chmod +x scripts/skillsmp-search.sh
    echo -e "  ${GREEN}✓${NC} scripts/skillsmp-search.sh ($([ "$UPGRADE_MODE" = true ] && echo updated || echo created))"
  else
    echo -e "  ${YELLOW}○${NC} scripts/skillsmp-search.sh (download failed)"
  fi
else
  echo -e "  ${GREEN}✓${NC} scripts/skillsmp-search.sh (exists, skipped)"
fi

# =============================================================================
# 8. .gitignore - Append if block not present (never remove existing rules)
# =============================================================================
GITIGNORE_BLOCK="
# ONE_SHOT
.env
.env.local
*.key
.age/
!.env.example
!*.encrypted"

if [ -f .gitignore ]; then
  if ! grep -q "# ONE_SHOT" .gitignore; then
    echo "$GITIGNORE_BLOCK" >> .gitignore
    echo -e "  ${GREEN}✓${NC} .gitignore (appended ONE_SHOT rules)"
  else
    echo -e "  ${GREEN}✓${NC} .gitignore (already configured)"
  fi
else
  echo "$GITIGNORE_BLOCK" > .gitignore
  echo -e "  ${GREEN}✓${NC} .gitignore (created)"
fi

# =============================================================================
# Done
# =============================================================================
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                   ONE_SHOT v13 Ready!                      ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Start a session:${NC}"
echo "  claude ."
echo ""
echo -e "${BLUE}Then use:${NC}"
echo "  /short    Quick iteration on existing work"
echo "  /full     New project or major refactor"
echo "  /conduct  Multi-model orchestration until done"
echo ""
echo -e "${BLUE}Context management:${NC}"
echo "  /handoff  Save context before /clear"
echo "  /restore  Resume from handoff"
echo ""
echo -e "${BLUE}Research & docs:${NC}"
echo "  /research   Deep research via Gemini or search"
echo "  /freesearch Zero-token search via Exa"
echo "  /doc        Cache external docs locally"
echo ""
echo "Full docs: README.md and ~/.claude/skills/INDEX.md"
echo ""
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
  echo -e "${YELLOW}Add to your shell profile to use oneshot-update:${NC}"
  echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
  echo ""
fi
