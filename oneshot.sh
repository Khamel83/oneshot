#!/bin/bash
# ONE_SHOT Bootstrap Script
# Usage: curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
#
# Requires: ~/.age/key.txt (your Age private key)
# Get Age: sudo apt install age || brew install age
# Generate key: age-keygen -o ~/.age/key.txt

set -e

ONESHOT_BASE="https://raw.githubusercontent.com/Khamel83/oneshot/master"
SKILLS_BASE="https://raw.githubusercontent.com/Khamel83/secrets-vault/master/.claude/skills"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "ONE_SHOT Bootstrap"
echo "=================="

# Check for Age key
if [ ! -f ~/.age/key.txt ]; then
  echo -e "${YELLOW}Warning:${NC} No Age key found at ~/.age/key.txt"
  echo "  To create one: mkdir -p ~/.age && age-keygen -o ~/.age/key.txt"
  echo "  Continuing without secrets encryption..."
  echo ""
fi

# 1. AGENTS.md (orchestrator)
curl -sL "$ONESHOT_BASE/README.md" > AGENTS.md
echo -e "  ${GREEN}✓${NC} AGENTS.md"

# 2. All skills
SKILLS=(
  oneshot-core oneshot-resume failure-recovery
  project-initializer feature-planner git-workflow
  code-reviewer documentation-generator secrets-vault-manager
  skill-creator marketplace-browser designer debugger
  test-runner api-designer database-migrator performance-optimizer
  dependency-manager docker-composer ci-cd-setup refactorer push-to-cloud
)

mkdir -p .claude/skills
for skill in "${SKILLS[@]}"; do
  mkdir -p ".claude/skills/$skill"
  curl -sL "$SKILLS_BASE/$skill/SKILL.md" > ".claude/skills/$skill/SKILL.md" 2>/dev/null || true
done
echo -e "  ${GREEN}✓${NC} .claude/skills/ (${#SKILLS[@]} skills)"

# 3. SOPS config (uses your Age public key)
cat > .sops.yaml << 'EOF'
creation_rules:
  - age: age1kwu32vl7x3tx7dqphzykcf5cahgm4ejztm865f22fkwe5j6hwalqh0rau8
    path_regex: '.*\.env(\.encrypted)?$'
EOF
echo -e "  ${GREEN}✓${NC} .sops.yaml"

# 4. .env.example
cat > .env.example << 'EOF'
# Project secrets - copy to .env and fill in
# Encrypt: sops -e .env > .env.encrypted && rm .env
# Decrypt: sops -d .env.encrypted > .env

# Common API keys (copy from secrets-vault if needed)
# sops -d ~/github/secrets-vault/secrets.env.encrypted | grep KEY_NAME

# Project-specific secrets below:
EOF
echo -e "  ${GREEN}✓${NC} .env.example"

# 5. Update .gitignore
GITIGNORE_BLOCK="
# ONE_SHOT secrets
.env
.env.local
*.key
.age/
!.env.example
!*.encrypted"

if [ -f .gitignore ]; then
  if ! grep -q "# ONE_SHOT secrets" .gitignore; then
    echo "$GITIGNORE_BLOCK" >> .gitignore
    echo -e "  ${GREEN}✓${NC} .gitignore (updated)"
  else
    echo -e "  ${GREEN}✓${NC} .gitignore (already configured)"
  fi
else
  echo "$GITIGNORE_BLOCK" > .gitignore
  echo -e "  ${GREEN}✓${NC} .gitignore (created)"
fi

echo ""
echo "Done! Project is now ONE_SHOT enabled."
echo ""
echo "  AGENTS.md          - orchestration rules"
echo "  .claude/skills/    - 22 skills for Claude Code"
echo "  .sops.yaml         - secrets encryption config"
echo ""
echo "Next: Open in Claude Code and say 'utilize agents.md'"
echo ""
