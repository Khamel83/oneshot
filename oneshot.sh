#!/bin/bash
# ONE_SHOT Bootstrap Script v5.2
# Usage: curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
#
# Options:
#   --upgrade    Update all skills to latest version (overwrites existing skills)
#   --help       Show this help
#
# NON-DESTRUCTIVE: This script only adds to your project, never overwrites existing files.
# - Existing CLAUDE.md? We prepend a reference to AGENTS.md
# - Existing TODO.md, LLM-OVERVIEW.md? We skip them
# - Existing skills? We add new ones, never remove yours (unless --upgrade)
#
# Requires: ~/.age/key.txt (your Age private key) for secrets encryption
# Get Age: sudo apt install age || brew install age
# Generate key: age-keygen -o ~/.age/key.txt

set -e

# Parse arguments
UPGRADE_MODE=false
for arg in "$@"; do
  case $arg in
    --upgrade)
      UPGRADE_MODE=true
      shift
      ;;
    --help)
      echo "ONE_SHOT Bootstrap Script v5.2"
      echo ""
      echo "Usage:"
      echo "  curl -sL .../oneshot.sh | bash           # Install (non-destructive)"
      echo "  curl -sL .../oneshot.sh | bash -s -- --upgrade  # Update all skills"
      echo ""
      echo "Options:"
      echo "  --upgrade    Update all skills to latest version"
      echo "  --help       Show this help"
      echo ""
      echo "What gets updated:"
      echo "  Always:      AGENTS.md, CLAUDE.md ONE_SHOT block"
      echo "  --upgrade:   All skills (overwrites existing)"
      echo "  Never:       TODO.md, LLM-OVERVIEW.md, your custom skills"
      exit 0
      ;;
  esac
done

ONESHOT_BASE="https://raw.githubusercontent.com/Khamel83/oneshot/master"
SKILLS_BASE="$ONESHOT_BASE/.claude/skills"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
if [ "$UPGRADE_MODE" = true ]; then
  echo -e "${BLUE}ONE_SHOT Upgrade v5.2${NC}"
  echo "====================="
else
  echo -e "${BLUE}ONE_SHOT Bootstrap v5.2${NC}"
  echo "========================"
fi
echo ""

# Check for Age key (optional)
if [ ! -f ~/.age/key.txt ]; then
  echo -e "${YELLOW}Note:${NC} No Age key at ~/.age/key.txt (optional for secrets encryption)"
  echo "  To create: mkdir -p ~/.age && age-keygen -o ~/.age/key.txt"
  echo ""
fi

# =============================================================================
# 1. AGENTS.md - The orchestrator (always update, this is OneShot's file)
# =============================================================================
curl -sL "$ONESHOT_BASE/AGENTS.md" > AGENTS.md 2>/dev/null || \
  curl -sL "$ONESHOT_BASE/README.md" > AGENTS.md
echo -e "  ${GREEN}✓${NC} AGENTS.md (orchestrator with skill routing)"

# =============================================================================
# 2. CLAUDE.md - Supplement if exists, create if not
# =============================================================================
CLAUDE_ONESHOT_BLOCK="<!-- ONE_SHOT v5.2 -->
# IMPORTANT: Read AGENTS.md - it contains skill routing rules.
#
# Skills are triggered automatically based on what you say:
#   \"build me...\"     → oneshot-core
#   \"plan...\"         → create-plan
#   \"implement...\"    → implement-plan
#   \"debug/fix...\"    → debugger
#   \"deploy...\"       → push-to-cloud
#   \"ultrathink...\"   → thinking-modes
#
# Always update TODO.md as you work.
<!-- /ONE_SHOT -->"

if [ -f CLAUDE.md ]; then
  if ! grep -q "<!-- ONE_SHOT" CLAUDE.md; then
    # Prepend OneShot block to existing CLAUDE.md
    echo "$CLAUDE_ONESHOT_BLOCK" | cat - CLAUDE.md > CLAUDE.md.tmp && mv CLAUDE.md.tmp CLAUDE.md
    echo -e "  ${GREEN}✓${NC} CLAUDE.md (supplemented - added skill routing reference)"
  else
    # Update existing OneShot block
    sed -i.bak '/<!-- ONE_SHOT/,/<!-- \/ONE_SHOT -->/d' CLAUDE.md 2>/dev/null || true
    echo "$CLAUDE_ONESHOT_BLOCK" | cat - CLAUDE.md > CLAUDE.md.tmp && mv CLAUDE.md.tmp CLAUDE.md
    rm -f CLAUDE.md.bak 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} CLAUDE.md (updated to v5.2)"
  fi
else
  # Create new CLAUDE.md with skill routing emphasis
  cat > CLAUDE.md << 'EOF'
<!-- ONE_SHOT v5.2 -->
# IMPORTANT: Read AGENTS.md - it contains skill routing rules.
#
# Skills are triggered automatically based on what you say:
#   "build me..."     → oneshot-core
#   "plan..."         → create-plan
#   "implement..."    → implement-plan
#   "debug/fix..."    → debugger
#   "deploy..."       → push-to-cloud
#   "ultrathink..."   → thinking-modes
#
# Always update TODO.md as you work.
<!-- /ONE_SHOT -->

# Project Instructions

## Overview
[Brief description of what this project does]

## Key Commands
```bash
# Setup
[setup commands]

# Run
[run commands]

# Test
[test commands]
```

## Architecture
[Key architectural decisions and patterns]

## Conventions
[Project-specific conventions and standards]

## Skill Usage
When working on this project, use these skills:
- Planning: `create-plan` → `implement-plan`
- Debugging: `debugger` → `test-runner`
- Deploying: `push-to-cloud` → `ci-cd-setup`
- Context: `create-handoff` before `/clear`
EOF
  echo -e "  ${GREEN}✓${NC} CLAUDE.md (created with skill routing)"
fi

# =============================================================================
# 3. TODO.md - Create if not exists (never overwrite)
# =============================================================================
if [ ! -f TODO.md ]; then
  cat > TODO.md << 'EOF'
# TODO

Project task tracking following [todo.md](https://github.com/todomd/todo.md) spec.

### Backlog
- [ ] [First task to do]

### In Progress

### Done ✓

---
*Updated by OneShot skills. Say `(ONE_SHOT)` to re-anchor.*
EOF
  echo -e "  ${GREEN}✓${NC} TODO.md (created)"
else
  echo -e "  ${GREEN}✓${NC} TODO.md (exists, skipped)"
fi

# =============================================================================
# 4. LLM-OVERVIEW.md - Create if not exists (never overwrite)
# =============================================================================
if [ ! -f LLM-OVERVIEW.md ]; then
  cat > LLM-OVERVIEW.md << 'EOF'
# LLM Overview

> Context for any LLM working on this project. No secrets.

## What This Project Does
[One paragraph description]

## Tech Stack
- Language: [e.g., TypeScript, Python]
- Framework: [e.g., Next.js, FastAPI]
- Database: [e.g., SQLite, PostgreSQL, none]
- Deployment: [e.g., Vercel, Docker, homelab]

## Project Structure
```
[key directories and their purpose]
```

## Key Files
| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project instructions |
| `AGENTS.md` | Skill routing |
| `TODO.md` | Task tracking |

## How to Run
```bash
[commands to run the project]
```

## Current State
- **Status**: [Planning / In Development / Production]
- **Last Updated**: [date]

## Important Context
[Anything an LLM should know before working on this project]
EOF
  echo -e "  ${GREEN}✓${NC} LLM-OVERVIEW.md (created)"
else
  echo -e "  ${GREEN}✓${NC} LLM-OVERVIEW.md (exists, skipped)"
fi

# =============================================================================
# 5. Skills - Consolidated 21 skills (additive only)
# =============================================================================
SKILLS=(
  # Core (3)
  oneshot-core failure-recovery thinking-modes
  # Planning (3)
  create-plan implement-plan api-designer
  # Context (2)
  create-handoff resume-handoff
  # Development (5)
  debugger test-runner code-reviewer refactorer performance-optimizer
  # Operations (5)
  git-workflow push-to-cloud ci-cd-setup docker-composer observability-setup
  # Data & Docs (3)
  database-migrator documentation-generator secrets-vault-manager
)

mkdir -p .claude/skills
SKILLS_ADDED=0
SKILLS_UPDATED=0
SKILLS_SKIPPED=0

for skill in "${SKILLS[@]}"; do
  if [ ! -f ".claude/skills/$skill/SKILL.md" ]; then
    # New skill - always download
    mkdir -p ".claude/skills/$skill"
    if curl -sL "$SKILLS_BASE/$skill/SKILL.md" -o ".claude/skills/$skill/SKILL.md" 2>/dev/null; then
      ((SKILLS_ADDED++)) || true
    fi
  elif [ "$UPGRADE_MODE" = true ]; then
    # Existing skill + upgrade mode - overwrite
    if curl -sL "$SKILLS_BASE/$skill/SKILL.md" -o ".claude/skills/$skill/SKILL.md" 2>/dev/null; then
      ((SKILLS_UPDATED++)) || true
    fi
  else
    ((SKILLS_SKIPPED++)) || true
  fi
done

if [ "$UPGRADE_MODE" = true ]; then
  echo -e "  ${GREEN}✓${NC} .claude/skills/ (${SKILLS_ADDED} added, ${SKILLS_UPDATED} updated, 21 total)"
else
  echo -e "  ${GREEN}✓${NC} .claude/skills/ (${SKILLS_ADDED} added, ${SKILLS_SKIPPED} existing, 21 total)"
fi

# =============================================================================
# 6. .sops.yaml - Create if not exists (never overwrite)
# =============================================================================
if [ ! -f .sops.yaml ]; then
  cat > .sops.yaml << 'EOF'
# SOPS configuration for secrets encryption
# Uses Age encryption: https://github.com/FiloSottile/age
creation_rules:
  - age: age1kwu32vl7x3tx7dqphzykcf5cahgm4ejztm865f22fkwe5j6hwalqh0rau8
    path_regex: '.*\.env(\.encrypted)?$'
EOF
  echo -e "  ${GREEN}✓${NC} .sops.yaml (created)"
else
  echo -e "  ${GREEN}✓${NC} .sops.yaml (exists, skipped)"
fi

# =============================================================================
# 7. .env.example - Create if not exists (never overwrite)
# =============================================================================
if [ ! -f .env.example ]; then
  cat > .env.example << 'EOF'
# Project secrets - copy to .env and fill in
# Encrypt: sops -e .env > .env.encrypted && rm .env
# Decrypt: sops -d .env.encrypted > .env

# Pull from central vault:
# sops -d ~/github/oneshot/secrets/secrets.env.encrypted | grep KEY_NAME >> .env

# Project-specific secrets:
EOF
  echo -e "  ${GREEN}✓${NC} .env.example (created)"
else
  echo -e "  ${GREEN}✓${NC} .env.example (exists, skipped)"
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
echo -e "${GREEN}Done!${NC} Project is now ONE_SHOT enabled."
echo ""
echo "  Files:"
echo "    AGENTS.md        - Skill routing (21 skills)"
echo "    CLAUDE.md        - Project instructions"
echo "    TODO.md          - Task tracking"
echo "    LLM-OVERVIEW.md  - Project context"
echo ""
echo "  Skill triggers (say these to activate):"
echo "    \"build me...\"     → oneshot-core"
echo "    \"plan...\"         → create-plan"
echo "    \"ultrathink...\"   → thinking-modes"
echo "    \"debug/fix...\"    → debugger"
echo "    \"deploy...\"       → push-to-cloud"
echo ""
echo "  Commands:"
echo "    (ONE_SHOT)       - Re-anchor to skill routing"
echo "    /create_plan     - Start structured planning"
echo "    /create_handoff  - Save context before /clear"
echo ""
