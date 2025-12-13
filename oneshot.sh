#!/bin/bash
# ONE_SHOT Bootstrap Script v5.0
# Usage: curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
#
# NON-DESTRUCTIVE: This script only adds to your project, never overwrites existing files.
# - Existing CLAUDE.md? We prepend a reference to AGENTS.md
# - Existing TODO.md, LLM-OVERVIEW.md? We skip them
# - Existing skills? We add new ones, never remove yours
#
# Requires: ~/.age/key.txt (your Age private key) for secrets encryption
# Get Age: sudo apt install age || brew install age
# Generate key: age-keygen -o ~/.age/key.txt

set -e

ONESHOT_BASE="https://raw.githubusercontent.com/Khamel83/oneshot/master"
SKILLS_BASE="$ONESHOT_BASE/.claude/skills"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${BLUE}ONE_SHOT Bootstrap v5.0${NC}"
echo "========================"
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
echo -e "  ${GREEN}✓${NC} AGENTS.md (orchestrator)"

# =============================================================================
# 2. CLAUDE.md - Supplement if exists, create if not
# =============================================================================
CLAUDE_ONESHOT_BLOCK="<!-- ONE_SHOT -->
# Read AGENTS.md first - it contains orchestration rules and skill routing.
# Update TODO.md as you work. Update LLM-OVERVIEW.md for major changes.
<!-- /ONE_SHOT -->"

if [ -f CLAUDE.md ]; then
  if ! grep -q "<!-- ONE_SHOT -->" CLAUDE.md; then
    # Prepend OneShot block to existing CLAUDE.md
    echo "$CLAUDE_ONESHOT_BLOCK" | cat - CLAUDE.md > CLAUDE.md.tmp && mv CLAUDE.md.tmp CLAUDE.md
    echo -e "  ${GREEN}✓${NC} CLAUDE.md (supplemented - added AGENTS.md reference)"
  else
    echo -e "  ${GREEN}✓${NC} CLAUDE.md (already configured)"
  fi
else
  # Create new CLAUDE.md
  cat > CLAUDE.md << 'EOF'
<!-- ONE_SHOT -->
# Read AGENTS.md first - it contains orchestration rules and skill routing.
# Update TODO.md as you work. Update LLM-OVERVIEW.md for major changes.
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
EOF
  echo -e "  ${GREEN}✓${NC} CLAUDE.md (created template)"
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
*Updated by OneShot skills. Run `(ONE_SHOT)` to re-sync.*
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

> This file provides context for any LLM working on this project.
> Keep it updated. No secrets or private information.

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
| `[file]` | [what it does] |

## How to Run
```bash
[commands to run the project]
```

## Current State
- **Status**: [Planning / In Development / Production]
- **Last Updated**: [date]
- **Main Branch**: [main/master]

## Important Context
[Anything an LLM should know before working on this project]
EOF
  echo -e "  ${GREEN}✓${NC} LLM-OVERVIEW.md (created)"
else
  echo -e "  ${GREEN}✓${NC} LLM-OVERVIEW.md (exists, skipped)"
fi

# =============================================================================
# 5. Skills - Additive only (never remove existing skills)
# =============================================================================
SKILLS=(
  oneshot-core oneshot-resume failure-recovery
  project-initializer feature-planner git-workflow
  code-reviewer documentation-generator secrets-vault-manager
  skill-creator marketplace-browser designer debugger
  test-runner api-designer database-migrator performance-optimizer
  dependency-manager docker-composer ci-cd-setup refactorer push-to-cloud
  content-enricher thinking-modes create-plan implement-plan create-handoff resume-handoff
)

mkdir -p .claude/skills
SKILLS_ADDED=0
SKILLS_SKIPPED=0

for skill in "${SKILLS[@]}"; do
  if [ ! -f ".claude/skills/$skill/SKILL.md" ]; then
    mkdir -p ".claude/skills/$skill"
    if curl -sL "$SKILLS_BASE/$skill/SKILL.md" -o ".claude/skills/$skill/SKILL.md" 2>/dev/null; then
      ((SKILLS_ADDED++))
    fi
  else
    ((SKILLS_SKIPPED++))
  fi
done
echo -e "  ${GREEN}✓${NC} .claude/skills/ (${SKILLS_ADDED} added, ${SKILLS_SKIPPED} existing)"

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
# sops -d ~/github/secrets-vault/secrets.env.encrypted | grep KEY_NAME >> .env

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
echo "    AGENTS.md        - Orchestration rules (skill routing)"
echo "    CLAUDE.md        - Project instructions (references AGENTS.md)"
echo "    TODO.md          - Task tracking (todo.md format)"
echo "    LLM-OVERVIEW.md  - Project context for any LLM"
echo "    .claude/skills/  - ${#SKILLS[@]} skills"
echo ""
echo "  Next steps:"
echo "    1. Open in Claude Code"
echo "    2. Claude reads CLAUDE.md → AGENTS.md automatically"
echo "    3. Say what you want to build"
echo ""
echo "  Commands:"
echo "    (ONE_SHOT)       - Re-anchor to orchestration rules"
echo "    ultrathink       - Deep analysis mode"
echo "    /create_plan     - Start structured planning"
echo ""
