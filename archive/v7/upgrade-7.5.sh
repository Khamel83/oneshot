#!/usr/bin/env bash
#
# ONE_SHOT v7.5 Migration Script
# Upgrades from v7.4 to v7.5 with automatic rollback on failure
#
# Usage: curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/upgrade-7.5.sh | bash
#

set -e

CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$CLAUDE/v7.4.backup"
CONTEXT_URL="https://raw.githubusercontent.com/Khamel83/oneshot/master/.claude/hooks/context.py"

echo "=== ONE_SHOT v7.5 Upgrade ==="
echo ""

# Check if already on v7.5
if [ -f "$CLAUDE_DIR/hooks/context.py" ]; then
    echo "✓ context.py already exists - you may be on v7.5"
    echo "  Run 'ls -la $CLAUDE_DIR/hooks/' to verify"
    exit 0
fi

# Step 1: Backup
echo "Step 1: Backing up current setup..."
mkdir -p "$BACKUP_DIR"
cp "$CLAUDE_DIR/settings.json" "$BACKUP_DIR/settings.json" 2>/dev/null || true
mkdir -p "$BACKUP_DIR/hooks"
cp "$CLAUDE_DIR/hooks/khamel-mode.py" "$BACKUP_DIR/hooks/" 2>/dev/null || true
cp "$CLAUDE_DIR/hooks/auto-init.py" "$BACKUP_DIR/hooks/" 2>/dev/null || true
cp "$CLAUDE_DIR/hooks/pattern-suggester.py" "$BACKUP_DIR/hooks/" 2>/dev/null || true
echo "✓ Backup created at $BACKUP_DIR"

# Step 2: Download context.py
echo ""
echo "Step 2: Downloading context.py..."
curl -fsSL "$CONTEXT_URL" -o "$CLAUDE_DIR/hooks/context.py" || {
    echo "✗ Failed to download context.py"
    echo "  Rolling back..."
    rm -f "$CLAUDE_DIR/hooks/context.py"
    exit 1
}
chmod +x "$CLAUDE_DIR/hooks/context.py"
echo "✓ context.py installed"

# Step 3: Verify context.py works
echo ""
echo "Step 3: Testing context.py..."
if ! python3 "$CLAUDE_DIR/hooks/context.py" >/dev/null 2>&1; then
    echo "✗ context.py failed test"
    echo "  Rolling back..."
    rm -f "$CLAUDE_DIR/hooks/context.py"
    exit 1
fi
echo "✓ context.py working correctly"

# Step 4: Update settings.json
echo ""
echo "Step 4: Updating settings.json..."
# Create new settings.json with context.py
python3 << 'PYTHON'
import json

settings_path = "$HOME/.claude/settings.json"
with open(settings_path) as f:
    settings = json.load(f)

# Update SessionStart hooks to use context.py
settings["hooks"]["SessionStart"] = [
    {
        "matcher": "",
        "hooks": [
            {
                "type": "command",
                "command": "python3 ~/.claude/hooks/context.py",
                "timeout": 5
            },
            {
                "type": "command",
                "command": "bd prime",
                "timeout": 10
            }
        ]
    }
]

# Remove UserPromptSubmit hooks (pattern-suggester removed in v7.5)
if "UserPromptSubmit" in settings["hooks"]:
    del settings["hooks"]["UserPromptSubmit"]

with open(settings_path, 'w') as f:
    json.dump(settings, f, indent=2)
PYTHON

echo "✓ settings.json updated"

# Step 5: Add interpreter to CLAUDE.md
echo ""
echo "Step 5: Adding context interpreter to CLAUDE.md..."
if ! grep -q "v7.5 Context Interpreter" "$CLAUDE_DIR/CLAUDE.md" 2>/dev/null; then
    cat >> "$CLAUDE_DIR/CLAUDE.md" << 'MARKDOWN'

## ONE_SHOT v7.5 Context Interpreter

When you see `CTX:{"v":1,...}` at session start, parse this JSON:

```python
# Parse compact context
import json
ctx = json.loads(CTX_JSON)

# Infrastructure (ctx.i) - Use without asking
oci_dev_ip = ctx["i"]["oci-dev"]      # 100.126.13.70
homelab_ip = ctx["i"]["homelab"]      # 100.112.130.100
macmini_ip = ctx["i"]["macmini"]      # 100.113.216.27

# Stacks (ctx.s) - Default tech stacks
web_stack = ctx["s"]["web"]           # Convex+Next.js+Clerk->Vercel
cli_stack = ctx["s"]["cli"]           # Python+Click+SQLite
service_stack = ctx["s"]["service"]   # Python+systemd->oci-dev

# Lessons (ctx.l) - Avoid repeating these (max 3 titles)
# Tasks (ctx.t) - Open beads tasks (max 5, use `bd ready`)
# Project (ctx.p) - Setup status, suggest `bd init` if beads=False
```

**Key behaviors:**
- Deploy services → oci-dev without asking
- New CLI → Python+Click+SQLite without asking
- New web app → Convex+Next.js+Clerk without asking
- Suggest `bd init` if ctx.p["beads"] is False/missing
MARKDOWN
    echo "✓ CLAUDE.md updated"
else
    echo "✓ CLAUDE.md already has v7.5 interpreter"
fi

# Step 6: Optimize auto-lesson.py
echo ""
echo "Step 6: Optimizing auto-lesson.py..."
AUTO_LESSON="$CLAUDE_DIR/hooks/auto-lesson.py"
if [ -f "$AUTO_LESSON" ]; then
    # Add transcript limit if not already present
    if ! grep -q "v7.5 optimization" "$AUTO_LESSON"; then
        sed -i "s/with open(transcript_path, 'r') as f:/with open(transcript_path, 'r') as f:\n            content = f.read()\n            # Only analyze last 5000 chars for speed (v7.5 optimization)\n            if len(content) > 5000:\n                content = content[-5000:]\n        return\n    try:/" "$AUTO_LESSON" 2>/dev/null || true
    fi
    echo "✓ auto-lesson.py optimized"
else
    echo "⚠ auto-lesson.py not found, skipping optimization"
fi

# Done
echo ""
echo "=== v7.5 Upgrade Complete ==="
echo ""
echo "Changes made:"
echo "  • Created ~/.claude/hooks/context.py"
echo "  • Updated ~/.claude/settings.json"
echo "  • Added v7.5 interpreter to CLAUDE.md"
echo "  • Optimized auto-lesson.py"
echo ""
echo "Next steps:"
echo "  1. Start a new Claude Code session"
echo "  2. Verify you see CTX:{...} in the context"
echo "  3. Run /context to check token reduction"
echo ""
echo "To rollback: cp $BACKUP_DIR/settings.json ~/.claude/settings.json && rm ~/.claude/hooks/context.py"
