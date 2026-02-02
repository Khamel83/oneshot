#!/usr/bin/env bash
#
# ONE_SHOT v9 Upgrade Script
# Ultra-compressed context: 2k tokens (down from 20k)
#
set -e

CLAUDE_DIR="$HOME/.claude"
BACKUP_DIR="$CLAUDE_DIR/v7.5.backup"
BASE_URL="https://raw.githubusercontent.com/Khamel83/oneshot/master/.claude/hooks"

echo "=== ONE_SHOT v9 Upgrade ==="
echo "Target: ~2k system tokens (down from ~20k)"
echo ""

# Backup
echo "Step 1: Backup..."
mkdir -p "$BACKUP_DIR"
cp "$CLAUDE_DIR/settings.json" "$BACKUP_DIR/" 2>/dev/null || true
cp "$CLAUDE_DIR/hooks/context.py" "$BACKUP_DIR/" 2>/dev/null || true
echo "✓ Backed up to $BACKUP_DIR"

# Download v9 hooks
echo ""
echo "Step 2: Download v9 hooks..."
curl -fsSL "$BASE_URL/context-v9.py" -o "$CLAUDE_DIR/hooks/context.py" || {
    echo "✗ Download failed"
    exit 1
}
curl -fsSL "$BASE_URL/beads-v9.py" -o "$CLAUDE_DIR/hooks/beads.py" || {
    echo "✗ Download failed"
    exit 1
}
chmod +x "$CLAUDE_DIR/hooks/context.py"
chmod +x "$CLAUDE_DIR/hooks/beads.py"
echo "✓ Hooks installed"

# Update settings.json
echo ""
echo "Step 3: Update settings.json..."
python3 << 'PYTHON'
import json
p = "$HOME/.claude/settings.json"
with open(p) as f:
    s = json.load(f)
s["hooks"]["SessionStart"] = [{
    "matcher": "",
    "hooks": [
        {"type": "command", "command": "python3 ~/.claude/hooks/context.py", "timeout": 5},
        {"type": "command", "command": "python3 ~/.claude/hooks/beads.py", "timeout": 5}
    ]
}]
s["hooks"]["PreCompact"] = [{
    "matcher": "",
    "hooks": [
        {"type": "command", "command": "python3 ~/.claude/hooks/pre-compact.py", "timeout": 10},
        {"type": "command", "command": "python3 ~/.claude/hooks/beads.py", "timeout": 5}
    ]
}]
if "UserPromptSubmit" in s["hooks"]:
    del s["hooks"]["UserPromptSubmit"]
with open(p, 'w') as f:
    json.dump(s, f, indent=2)
PYTHON
echo "✓ Settings updated"

# Update CLAUDE.md
echo ""
echo "Step 4: Update CLAUDE.md..."
if grep -q "v7.5 Context Interpreter" "$CLAUDE_DIR/CLAUDE.md" 2>/dev/null; then
    # Remove v7.5 section
    sed -i '/## ONE_SHOT v7.5 Context Interpreter/,/^--$/d' "$CLAUDE_DIR/CLAUDE.md"
fi
if ! grep -q "v9 Context" "$CLAUDE_DIR/CLAUDE.md" 2>/dev/null; then
    cat >> "$CLAUDE_DIR/CLAUDE.md" << 'EOF'

## ONE_SHOT v9 Context (Ultra-Compressed)

When you see `CTX:{"v":8,...}` at session start, parse this JSON:

```python
import json
ctx = json.loads(CTX_JSON)

# Skill router (ctx.s) - [[trigger, skill], ...]
skills = ctx["s"]  # Auto-routes to skills like "front-door", "debugger"

# Infrastructure (ctx.i) - Use IPs without asking
oci = ctx["i"]["oci"]   # 100.126.13.70
home = ctx["i"]["home"] # 100.112.130.100
mac = ctx["i"]["mac"]   # 100.113.216.27

# Stacks (ctx.k) - Default tech stacks
web = ctx["k"]["web"]   # Convex+Next.js+Clerk->Vercel
cli = ctx["k"]["cli"]   # Python+Click+SQLite
svc = ctx["k"]["svc"]   # Python+systemd->oci

# Beads (ctx.b) - Status counts
ready = ctx["b"]["ready"]  # Tasks ready to work
open_total = ctx["b"]["open"]  # Total open tasks

# Tasks (ctx.t) - Open tasks [{"id":"1","t":"title"}, ...]
# Lessons (ctx.l) - Recent lessons ["lesson1", ...]
# Project (ctx.p) - Setup status {"b":bool,"m":bool,"o":bool,"a":bool}
```

**Key behaviors:**
- Auto-route: "build me X" → front-door skill
- Deploy → oci (100.126.13.70) without asking
- New CLI → Python+Click+SQLite without asking
- Suggest `bd init` if ctx.p["b"] is False

## Beads Context (Compressed)

When you see `BEADS:{"proto":"git",...}` at session start:

```python
import json
bd = json.loads(BEADS_JSON)

# Session close protocol (bd.end)
# ["status","add","sync","commit","sync","push"]
# Run this sequence before saying "done"

# Ready tasks (bd.ready)
# [{"id":"1","title":"..."}, ...]
# Use `bd show <id>` for details, `bd update <id> --status=in_progress` to claim
```

**Session close checklist:**
1. `git status` - check what changed
2. `git add <files>` - stage changes
3. `bd sync` - commit beads
4. `git commit -m "..."` - commit code
5. `bd sync` - commit any new beads changes
6. `git push` - push to remote
EOF
fi
echo "✓ CLAUDE.md updated"

# Test
echo ""
echo "Step 5: Test hooks..."
python3 "$CLAUDE_DIR/hooks/context.py" >/dev/null 2>&1 || {
    echo "✗ context.py failed"
    exit 1
}
python3 "$CLAUDE_DIR/hooks/beads.py" >/dev/null 2>&1 || {
    echo "✗ beads.py failed"
    exit 1
}
echo "✓ Hooks working"

echo ""
echo "=== v9 Upgrade Complete ==="
echo ""
echo "Next: Start new Claude Code session, run /context to verify ~2k tokens"
echo "Rollback: cp $BACKUP_DIR/settings.json ~/.claude/settings.json"
