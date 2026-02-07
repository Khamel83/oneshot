#!/bin/bash
# ONE_SHOT v10 Migration Script
# Migrates existing projects from v9/v8/v7 to v10
#
# What it does:
#   - Removes AGENTS.md (routing table no longer needed)
#   - Strips ONE_SHOT boilerplate from CLAUDE.md (preserves project-specific content)
#   - Removes old hook registrations from .claude/settings.json
#   - Preserves .beads/ data (used by /beads command)
#   - Reports what changed
#
# Usage:
#   ./migrate-v10.sh [project-dir]
#   ./migrate-v10.sh ~/github/my-project
#   ./migrate-v10.sh .

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

PROJECT_DIR="${1:-.}"
PROJECT_DIR=$(cd "$PROJECT_DIR" && pwd)

echo "ONE_SHOT v10 Migration"
echo "======================"
echo "Project: $PROJECT_DIR"
echo ""

CHANGES=0

# 1. Detect current version
detect_version() {
    if [ -f "$PROJECT_DIR/AGENTS.md" ]; then
        if grep -q "v9" "$PROJECT_DIR/AGENTS.md" 2>/dev/null; then
            echo "v9"
        elif grep -q "v8" "$PROJECT_DIR/AGENTS.md" 2>/dev/null; then
            echo "v8"
        else
            echo "v7-or-earlier"
        fi
    else
        echo "none"
    fi
}

VERSION=$(detect_version)
echo -e "Detected ONE_SHOT version: ${YELLOW}${VERSION}${NC}"
echo ""

# 2. Remove AGENTS.md
if [ -f "$PROJECT_DIR/AGENTS.md" ]; then
    echo -e "${GREEN}[REMOVE]${NC} AGENTS.md (routing table no longer needed in v10)"
    rm "$PROJECT_DIR/AGENTS.md"
    CHANGES=$((CHANGES + 1))
else
    echo -e "${YELLOW}[SKIP]${NC} AGENTS.md not found"
fi

# 3. Clean CLAUDE.md — strip ONE_SHOT boilerplate
if [ -f "$PROJECT_DIR/CLAUDE.md" ]; then
    # Check if it contains ONE_SHOT boilerplate
    if grep -q "ONE_SHOT\|AGENTS.md\|KHAMEL MODE\|oneshot" "$PROJECT_DIR/CLAUDE.md" 2>/dev/null; then
        echo -e "${GREEN}[CLEAN]${NC} CLAUDE.md — stripping ONE_SHOT boilerplate"

        # Backup first
        cp "$PROJECT_DIR/CLAUDE.md" "$PROJECT_DIR/CLAUDE.md.v9-backup"

        # Strip common ONE_SHOT sections (between markers)
        # Keep project-specific content
        python3 -c "
import re
import sys

with open('$PROJECT_DIR/CLAUDE.md', 'r') as f:
    content = f.read()

# Remove ONE_SHOT sections (between ## headers)
sections_to_remove = [
    r'## AGENTS\.md Rule.*?(?=\n## |\Z)',
    r'## ONE_SHOT Skills System.*?(?=\n## |\Z)',
    r'## ONE_SHOT v\d+ Context.*?(?=\n## |\Z)',
    r'## Beads Context.*?(?=\n## |\Z)',
    r'## Lessons Learned System.*?(?=\n## |\Z)',
    r'<!--\s*ONE-SHOT Heartbeat.*?-->',
]

for pattern in sections_to_remove:
    content = re.sub(pattern, '', content, flags=re.DOTALL)

# Clean up multiple blank lines
content = re.sub(r'\n{3,}', '\n\n', content)

with open('$PROJECT_DIR/CLAUDE.md', 'w') as f:
    f.write(content.strip() + '\n')
" 2>/dev/null || {
            echo -e "${YELLOW}[WARN]${NC} Python cleanup failed, manual review needed"
        }

        CHANGES=$((CHANGES + 1))
    else
        echo -e "${YELLOW}[SKIP]${NC} CLAUDE.md has no ONE_SHOT boilerplate"
    fi
else
    echo -e "${YELLOW}[SKIP]${NC} No CLAUDE.md found"
fi

# 4. Clean .claude/settings.json — remove old hooks
SETTINGS="$PROJECT_DIR/.claude/settings.json"
if [ -f "$SETTINGS" ]; then
    if grep -q "context-v8\|beads-v8\|lessons-inject\|heartbeat" "$SETTINGS" 2>/dev/null; then
        echo -e "${GREEN}[CLEAN]${NC} .claude/settings.json — removing old hook registrations"
        cp "$SETTINGS" "${SETTINGS}.v9-backup"

        # Remove old hook entries (best effort with python)
        python3 -c "
import json
with open('$SETTINGS', 'r') as f:
    settings = json.load(f)

# Remove old hooks
if 'hooks' in settings:
    for event in list(settings['hooks'].keys()):
        hooks = settings['hooks'][event]
        if isinstance(hooks, list):
            settings['hooks'][event] = [
                h for h in hooks
                if not any(old in str(h) for old in ['context-v8', 'beads-v8', 'lessons-inject', 'heartbeat'])
            ]
            # Remove empty events
            if not settings['hooks'][event]:
                del settings['hooks'][event]
    if not settings['hooks']:
        del settings['hooks']

with open('$SETTINGS', 'w') as f:
    json.dump(settings, f, indent=2)
" 2>/dev/null || {
            echo -e "${YELLOW}[WARN]${NC} JSON cleanup failed, manual review needed"
        }

        CHANGES=$((CHANGES + 1))
    else
        echo -e "${YELLOW}[SKIP]${NC} .claude/settings.json has no old hooks"
    fi
fi

# 5. Check for .beads/ (preserve)
if [ -d "$PROJECT_DIR/.beads" ]; then
    echo -e "${YELLOW}[KEEP]${NC} .beads/ directory preserved (used by /beads command)"
fi

# 6. Check for old skill references
if [ -d "$PROJECT_DIR/.claude/skills" ]; then
    SKILL_COUNT=$(ls -d "$PROJECT_DIR/.claude/skills"/*/ 2>/dev/null | wc -l)
    if [ "$SKILL_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}[INFO]${NC} Found $SKILL_COUNT skill directories in .claude/skills/"
        echo -e "       These are project-local skills. v10 uses ~/.claude/commands/ globally."
        echo -e "       You can remove .claude/skills/ if these were ONE_SHOT skills."
    fi
fi

# 7. Summary
echo ""
echo "======================"
echo -e "Changes made: ${GREEN}${CHANGES}${NC}"
if [ "$CHANGES" -gt 0 ]; then
    echo ""
    echo "Backup files created:"
    [ -f "$PROJECT_DIR/CLAUDE.md.v9-backup" ] && echo "  - CLAUDE.md.v9-backup"
    [ -f "${SETTINGS}.v9-backup" ] && echo "  - .claude/settings.json.v9-backup"
    echo ""
    echo "To undo: restore from .v9-backup files"
fi
echo ""
echo "v10 uses ~/.claude/ (global) for rules and commands."
echo "No per-project AGENTS.md or skills needed."
echo "Project-specific rules go in .claude/rules/ (if any)."
echo ""
echo "Done."
