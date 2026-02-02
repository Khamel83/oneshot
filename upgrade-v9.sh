#!/usr/bin/env bash
#
# ONE_SHOT v9.0 Upgrade Script
# Play Calling: Explicit skill sequences, SkillsMP integration
#
set -e

echo "ONE_SHOT v9.0 Upgrade"
echo "===================="
echo ""
echo "This will upgrade your ONE_SHOT installation to v9.0"
echo ""
echo "What's new in v9:"
echo "  - Skill Sequence tables in task_plan.md (explicit skill orchestration)"
echo "  - skill_discovery.py (automatic skill matching to goals)"
echo "  - SkillsMP marketplace integration (26,000+ external skills)"
echo "  - /run-plan skill (deterministic skill execution)"
echo "  - Synthesized documentation (README for users + LLMs)"
echo ""
echo "Project is now at: github.com/Khamel83/oneshot"
echo ""

# Confirm
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

# Get oneshot directory
ONESHOT_DIR="$HOME/github/oneshot"
if [ ! -d "$ONESHOT_DIR" ]; then
  echo "✗ oneshot directory not found at $ONESHOT_DIR"
  echo "  Please clone: git clone https://github.com/Khamel83/oneshot.git ~/github/oneshot"
  exit 1
fi

# Pull latest
echo "→ Pulling latest from master..."
cd "$ONESHOT_DIR"
git pull origin master
echo "✓ Updated to latest version"

echo ""
echo "=== v9.0 Upgrade Complete ==="
echo ""
echo "New features available:"
echo "  /continuous-plan  - Create plan with skill sequences"
echo "  /run-plan         - Execute skills deterministically"
echo "  /skillsmp-search  - Search external skills marketplace"
echo ""
echo "For full details: https://github.com/Khamel83/oneshot#readme"
echo ""
echo "Next: Start new Claude Code session to use v9 features"

