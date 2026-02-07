#!/bin/bash
# ONE_SHOT v10 Install Script
#
# Installs v10 to ~/.claude/ (global Claude Code config)
# Archives v9 files in the oneshot repo
#
# Usage:
#   ./install-v10.sh
#
# What it does:
#   1. Archives current skills/hooks/agents to archive/v9/
#   2. Copies prototype/ files to ~/.claude/
#   3. Sets up hooks in settings.json
#   4. Makes hook scripts executable

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ONESHOT_DIR="$(dirname "$SCRIPT_DIR")"
PROTO_DIR="$ONESHOT_DIR/prototype"
CLAUDE_DIR="$HOME/.claude"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo "ONE_SHOT v10 Installer"
echo "======================"
echo "Source: $PROTO_DIR"
echo "Target: $CLAUDE_DIR"
echo ""

# Verify prototype exists
if [ ! -d "$PROTO_DIR/commands" ] || [ ! -d "$PROTO_DIR/rules" ]; then
    echo -e "${RED}ERROR${NC}: prototype/ directory missing commands/ or rules/"
    exit 1
fi

# Step 1: Archive v9
echo "Step 1: Archiving v9..."
ARCHIVE_DIR="$ONESHOT_DIR/archive/v9"
mkdir -p "$ARCHIVE_DIR"

if [ -d "$ONESHOT_DIR/.claude/skills" ]; then
    echo -e "  ${GREEN}[ARCHIVE]${NC} .claude/skills/ → archive/v9/skills/"
    cp -r "$ONESHOT_DIR/.claude/skills" "$ARCHIVE_DIR/skills" 2>/dev/null || true
fi

if [ -d "$ONESHOT_DIR/.claude/hooks" ]; then
    echo -e "  ${GREEN}[ARCHIVE]${NC} .claude/hooks/ → archive/v9/hooks/"
    cp -r "$ONESHOT_DIR/.claude/hooks" "$ARCHIVE_DIR/hooks" 2>/dev/null || true
fi

if [ -d "$ONESHOT_DIR/.claude/agents" ]; then
    echo -e "  ${GREEN}[ARCHIVE]${NC} .claude/agents/ → archive/v9/agents/"
    cp -r "$ONESHOT_DIR/.claude/agents" "$ARCHIVE_DIR/agents" 2>/dev/null || true
fi

if [ -f "$ONESHOT_DIR/AGENTS.md" ]; then
    echo -e "  ${GREEN}[ARCHIVE]${NC} AGENTS.md → archive/v9/AGENTS.md"
    cp "$ONESHOT_DIR/AGENTS.md" "$ARCHIVE_DIR/AGENTS.md" 2>/dev/null || true
fi

# Save current CLAUDE.md
if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
    echo -e "  ${GREEN}[BACKUP]${NC} ~/.claude/CLAUDE.md → archive/v9/CLAUDE.md.global-backup"
    cp "$CLAUDE_DIR/CLAUDE.md" "$ARCHIVE_DIR/CLAUDE.md.global-backup" 2>/dev/null || true
fi

# Step 2: Install v10 rules
echo ""
echo "Step 2: Installing rules..."
mkdir -p "$CLAUDE_DIR/rules"

for rule in "$PROTO_DIR"/rules/*.md; do
    name=$(basename "$rule")
    echo -e "  ${GREEN}[INSTALL]${NC} rules/$name"
    cp "$rule" "$CLAUDE_DIR/rules/$name"
done

# Step 3: Install v10 commands
echo ""
echo "Step 3: Installing commands..."
mkdir -p "$CLAUDE_DIR/commands"

for cmd in "$PROTO_DIR"/commands/*.md; do
    name=$(basename "$cmd")
    echo -e "  ${GREEN}[INSTALL]${NC} commands/$name"
    cp "$cmd" "$CLAUDE_DIR/commands/$name"
done

# Step 4: Install CLAUDE.md
echo ""
echo "Step 4: Installing CLAUDE.md..."
echo -e "  ${GREEN}[INSTALL]${NC} CLAUDE.md"
cp "$PROTO_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"

# Step 5: Install hooks
echo ""
echo "Step 5: Installing hooks..."
mkdir -p "$CLAUDE_DIR/hooks"

for hook in "$PROTO_DIR"/hooks/*.sh; do
    name=$(basename "$hook")
    echo -e "  ${GREEN}[INSTALL]${NC} hooks/$name"
    cp "$hook" "$CLAUDE_DIR/hooks/$name"
    chmod +x "$CLAUDE_DIR/hooks/$name"
done

# Step 6: Update settings.json with hook config
echo ""
echo "Step 6: Configuring hooks in settings.json..."

SETTINGS="$CLAUDE_DIR/settings.json"

if [ -f "$SETTINGS" ]; then
    # Merge hook config into existing settings
    python3 -c "
import json

with open('$SETTINGS', 'r') as f:
    settings = json.load(f)

with open('$PROTO_DIR/hooks/settings-snippet.json', 'r') as f:
    hooks_config = json.load(f)

# Merge statusLine
settings['statusLine'] = hooks_config['statusLine']

# Merge hooks (append, don't replace)
if 'hooks' not in settings:
    settings['hooks'] = {}

for event, event_hooks in hooks_config.get('hooks', {}).items():
    if event not in settings['hooks']:
        settings['hooks'][event] = []
    # Add new hooks, avoid duplicates
    existing_cmds = [h.get('hooks', [{}])[0].get('command', '') for h in settings['hooks'][event] if isinstance(h, dict)]
    for hook in event_hooks:
        hook_cmd = hook.get('hooks', [{}])[0].get('command', '')
        if hook_cmd not in existing_cmds:
            settings['hooks'][event].append(hook)

with open('$SETTINGS', 'w') as f:
    json.dump(settings, f, indent=2)
    f.write('\n')

print('  Settings updated')
" 2>/dev/null || {
        echo -e "  ${YELLOW}[WARN]${NC} Could not auto-merge settings.json"
        echo -e "  ${YELLOW}[WARN]${NC} Manually merge: $PROTO_DIR/hooks/settings-snippet.json → $SETTINGS"
    }
else
    echo -e "  ${GREEN}[CREATE]${NC} settings.json"
    cp "$PROTO_DIR/hooks/settings-snippet.json" "$SETTINGS"
fi

# Step 7: Summary
echo ""
echo "======================"
echo -e "${GREEN}v10 installed successfully${NC}"
echo ""

RULES_COUNT=$(ls "$CLAUDE_DIR/rules/"*.md 2>/dev/null | wc -l)
CMDS_COUNT=$(ls "$CLAUDE_DIR/commands/"*.md 2>/dev/null | wc -l)
HOOKS_COUNT=$(ls "$CLAUDE_DIR/hooks/"*.sh 2>/dev/null | wc -l)

echo "Installed:"
echo "  $RULES_COUNT rules     (auto-loaded contextually)"
echo "  $CMDS_COUNT commands   (invoked via /command)"
echo "  $HOOKS_COUNT hooks      (statusline + auto-handoff)"
echo ""
echo "Archived v9 to: $ARCHIVE_DIR"
echo ""
echo "Test it: open a new Claude Code session and type /interview"
echo ""
echo "To rollback to v9:"
echo "  cp archive/v9/CLAUDE.md.global-backup ~/.claude/CLAUDE.md"
echo "  rm -rf ~/.claude/rules/ ~/.claude/commands/"
echo "  # Restore skills symlink if needed"
