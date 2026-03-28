#!/bin/bash
# Syncs oneshot skills to ~/.claude/skills/ so they're available in all projects.
# Called by: SessionStart hook + git post-merge hook
# Rules are handled separately via symlink (~/.claude/rules → oneshot/.claude/rules)

ONESHOT_SKILLS="$(dirname "$0")/../skills"
GLOBAL_SKILLS="$HOME/.claude/skills"
GLOBAL_RULES="$HOME/.claude/rules"
ONESHOT_RULES="$(dirname "$0")/../rules"

# Ensure global dirs exist
mkdir -p "$GLOBAL_SKILLS"

# Sync skills: add/update from oneshot. Never delete — global may have non-oneshot skills.
for skill_dir in "$ONESHOT_SKILLS"/*/; do
    [ -d "$skill_dir" ] || continue
    cp -r "$skill_dir" "$GLOBAL_SKILLS/"
done

# Ensure rules symlink is correct (recreate if missing or pointing wrong)
if [ ! -L "$GLOBAL_RULES" ] || [ "$(readlink "$GLOBAL_RULES")" != "$(realpath "$ONESHOT_RULES")" ]; then
    rm -rf "$GLOBAL_RULES"
    ln -s "$(realpath "$ONESHOT_RULES")" "$GLOBAL_RULES"
fi

exit 0
