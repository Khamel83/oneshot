#!/bin/bash
# ONE_SHOT Bootstrap Script v6.0
# Usage: curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
#
# Options:
#   --upgrade    Update all skills/agents to latest version (overwrites existing)
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
      echo "ONE_SHOT Bootstrap Script v6.0"
      echo ""
      echo "Usage:"
      echo "  curl -sL .../oneshot.sh | bash           # Install (non-destructive)"
      echo "  curl -sL .../oneshot.sh | bash -s -- --upgrade  # Update all skills/agents"
      echo ""
      echo "Options:"
      echo "  --upgrade    Update all skills and agents to latest version"
      echo "  --help       Show this help"
      echo ""
      echo "What gets installed:"
      echo "  Always:      AGENTS.md, CLAUDE.md ONE_SHOT block"
      echo "  Skills:      26 skills in .claude/skills/"
      echo "  Agents:      4 sub-agents in .claude/agents/"
      echo ""
      echo "What gets updated (--upgrade):"
      echo "  All skills and agents (overwrites existing)"
      echo ""
      echo "Never touched:"
      echo "  TODO.md, LLM-OVERVIEW.md, your custom skills/agents"
      exit 0
      ;;
  esac
done

ONESHOT_BASE="https://raw.githubusercontent.com/Khamel83/oneshot/master"
SKILLS_BASE="$ONESHOT_BASE/.claude/skills"
AGENTS_BASE="$ONESHOT_BASE/.claude/agents"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
if [ "$UPGRADE_MODE" = true ]; then
  echo -e "${BLUE}ONE_SHOT Upgrade v6.0${NC}"
  echo "====================="
else
  echo -e "${BLUE}ONE_SHOT Bootstrap v6.0${NC}"
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
CLAUDE_ONESHOT_BLOCK="<!-- ONE_SHOT v6.0 -->
# IMPORTANT: Read AGENTS.md - it contains skill and agent routing rules.
#
# Skills (synchronous, shared context):
#   \"build me...\"     → front-door
#   \"plan...\"         → create-plan
#   \"implement...\"    → implement-plan
#   \"debug/fix...\"    → debugger
#   \"deploy...\"       → push-to-cloud
#   \"ultrathink...\"   → thinking-modes
#   \"beads/ready...\"  → beads (persistent tasks)
#
# Agents (isolated context, background):
#   \"security audit...\" → security-auditor
#   \"explore/find all...\" → deep-research
#   \"background/parallel...\" → background-worker
#   \"coordinate agents...\" → multi-agent-coordinator
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
    echo -e "  ${GREEN}✓${NC} CLAUDE.md (updated to v6.0)"
  fi
else
  # Create new CLAUDE.md with skill and agent routing emphasis
  cat > CLAUDE.md << 'EOF'
<!-- ONE_SHOT v6.0 -->
# IMPORTANT: Read AGENTS.md - it contains skill and agent routing rules.
#
# Skills (synchronous, shared context):
#   "build me..."     → front-door
#   "plan..."         → create-plan
#   "implement..."    → implement-plan
#   "debug/fix..."    → debugger
#   "deploy..."       → push-to-cloud
#   "ultrathink..."   → thinking-modes
#   "beads/ready..."  → beads (persistent tasks)
#
# Agents (isolated context, background):
#   "security audit..." → security-auditor
#   "explore/find all..." → deep-research
#   "background/parallel..." → background-worker
#   "coordinate agents..." → multi-agent-coordinator
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

## Skill & Agent Usage
When working on this project:
- Planning: `create-plan` → `implement-plan`
- Debugging: `debugger` → `test-runner`
- Deploying: `push-to-cloud` → `ci-cd-setup`
- Context: `create-handoff` before `/clear`
- Security: `security-auditor` (isolated)
- Research: `deep-research` (isolated)
EOF
  echo -e "  ${GREEN}✓${NC} CLAUDE.md (created with skill/agent routing)"
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
# 5. Skills - Consolidated 25 skills (additive only)
# =============================================================================
SKILLS=(
  # Core (3)
  front-door failure-recovery thinking-modes
  # Planning (3)
  create-plan implement-plan api-designer
  # Context (3) - includes beads for persistent task tracking
  create-handoff resume-handoff beads
  # Development (5)
  debugger test-runner code-reviewer refactorer performance-optimizer
  # Operations (6)
  git-workflow push-to-cloud remote-exec ci-cd-setup docker-composer observability-setup
  # Data & Docs (4)
  database-migrator documentation-generator secrets-vault-manager secrets-sync
  # Communication (1)
  the-audit
  # Agent Bridge (1)
  delegate-to-agent
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
  echo -e "  ${GREEN}✓${NC} .claude/skills/ (${SKILLS_ADDED} added, ${SKILLS_UPDATED} updated, 26 total)"
else
  echo -e "  ${GREEN}✓${NC} .claude/skills/ (${SKILLS_ADDED} added, ${SKILLS_SKIPPED} existing, 26 total)"
fi

# =============================================================================
# 6. Agents - Native sub-agents for isolated context work (4 agents)
# =============================================================================
AGENTS=(
  security-auditor
  deep-research
  background-worker
  multi-agent-coordinator
)

mkdir -p .claude/agents
AGENTS_ADDED=0
AGENTS_UPDATED=0
AGENTS_SKIPPED=0

for agent in "${AGENTS[@]}"; do
  if [ ! -f ".claude/agents/$agent.md" ]; then
    # New agent - always download
    if curl -sL "$AGENTS_BASE/$agent.md" -o ".claude/agents/$agent.md" 2>/dev/null; then
      ((AGENTS_ADDED++)) || true
    fi
  elif [ "$UPGRADE_MODE" = true ]; then
    # Existing agent + upgrade mode - overwrite
    if curl -sL "$AGENTS_BASE/$agent.md" -o ".claude/agents/$agent.md" 2>/dev/null; then
      ((AGENTS_UPDATED++)) || true
    fi
  else
    ((AGENTS_SKIPPED++)) || true
  fi
done

# Download INDEX.md and TEMPLATE.md for agents
curl -sL "$AGENTS_BASE/INDEX.md" -o ".claude/agents/INDEX.md" 2>/dev/null || true
curl -sL "$AGENTS_BASE/TEMPLATE.md" -o ".claude/agents/TEMPLATE.md" 2>/dev/null || true

if [ "$UPGRADE_MODE" = true ]; then
  echo -e "  ${GREEN}✓${NC} .claude/agents/ (${AGENTS_ADDED} added, ${AGENTS_UPDATED} updated, 4 total)"
else
  echo -e "  ${GREEN}✓${NC} .claude/agents/ (${AGENTS_ADDED} added, ${AGENTS_SKIPPED} existing, 4 total)"
fi

# =============================================================================
# 6.5 Beads - Optional persistent task tracking (check if available)
# =============================================================================
BEADS_INSTALLED=false

# Check if bd command exists
if command -v bd &> /dev/null; then
  BEADS_INSTALLED=true
  echo -e "  ${GREEN}✓${NC} beads CLI detected ($(bd --version 2>/dev/null || echo 'installed'))"
else
  echo -e "  ${YELLOW}○${NC} beads not installed (optional - npm install -g @beads/bd)"
fi

# Initialize beads in project if installed and not already initialized
if [ "$BEADS_INSTALLED" = true ] && [ ! -d ".beads" ]; then
  echo -e "  ${BLUE}→${NC} Initializing beads in project..."
  bd init --stealth 2>/dev/null || true
  echo -e "  ${GREEN}✓${NC} .beads/ initialized (git-backed persistent tasks)"
elif [ -d ".beads" ]; then
  echo -e "  ${GREEN}✓${NC} .beads/ (already initialized)"
fi

# =============================================================================
# 7. .sops.yaml - Create if not exists (never overwrite)
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
# 8. .env.example - Create if not exists (never overwrite)
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
# 9. .gitignore - Append if block not present (never remove existing rules)
# =============================================================================
GITIGNORE_BLOCK="
# ONE_SHOT
.env
.env.local
*.key
.age/
!.env.example
!*.encrypted
# Beads local cache (JSONL is tracked)
.beads/beads.db
.beads/bd.sock
.beads/export_hashes.db"

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
echo "    AGENTS.md        - Skill & agent routing (26 skills, 4 agents)"
echo "    CLAUDE.md        - Project instructions"
echo "    TODO.md          - Task tracking"
echo "    LLM-OVERVIEW.md  - Project context"
echo ""
echo "  Skills (synchronous, shared context):"
echo "    \"build me...\"     → front-door"
echo "    \"plan...\"         → create-plan"
echo "    \"ultrathink...\"   → thinking-modes"
echo "    \"debug/fix...\"    → debugger"
echo "    \"deploy...\"       → push-to-cloud"
echo "    \"beads/ready...\"  → beads (persistent tasks)"
echo ""
echo "  Agents (isolated context, background):"
echo "    \"security audit\"  → security-auditor"
echo "    \"explore/find\"    → deep-research"
echo "    \"background\"      → background-worker"
echo "    \"coordinate\"      → multi-agent-coordinator"
echo ""
echo "  Optional:"
echo "    beads            - Persistent task tracking (npm install -g @beads/bd)"
echo ""
echo "  Commands:"
echo "    (ONE_SHOT)       - Re-anchor to skill routing"
echo "    /create_plan     - Start structured planning"
echo "    /create_handoff  - Save context before /clear"
echo ""
