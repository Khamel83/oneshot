#!/bin/bash
# Janitor is disabled by default.
# This script is intentionally an uninstaller so machine updates do not
# re-enable the global Claude hooks that generate large CLAUDE.local.md files.

set -euo pipefail

HOOK_DIR="$HOME/.claude/hooks"
SETTINGS_FILE="$HOME/.claude/settings.json"

for hook in context session-end record pre-compact; do
	dst="$HOOK_DIR/janitor-${hook}.sh"
	if [ -e "$dst" ] || [ -L "$dst" ]; then
		rm -f "$dst"
		echo "Removed: $dst"
	fi
done

if [ -f "$SETTINGS_FILE" ]; then
	python3 - "$SETTINGS_FILE" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
data = json.loads(path.read_text())
changed = False

for event, entries in list(data.get("hooks", {}).items()):
    for entry in entries:
        hooks = entry.get("hooks", [])
        kept = [
            hook for hook in hooks
            if "janitor-" not in hook.get("command", "")
            and "/janitor" not in hook.get("command", "")
        ]
        if len(kept) != len(hooks):
            changed = True
        entry["hooks"] = kept
    data["hooks"][event] = [entry for entry in entries if entry.get("hooks")]

if "hooks" in data:
    data["hooks"] = {event: entries for event, entries in data["hooks"].items() if entries}

if changed:
    path.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Removed janitor hook entries from {path}")
PY
fi

echo "Janitor hooks are disabled."
