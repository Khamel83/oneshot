#!/bin/bash
# claude-shell-setup.sh - Portable Claude Code + ZAI setup + Heartbeat integration
#
# USAGE:
#   1. Copy to new machine and edit the config values below
#   2. Run: bash claude-shell-setup.sh --install
#   3. Then: source ~/.bashrc (or source ~/.zshrc for zsh)
#
# COMMANDS AFTER INSTALL:
#   cc  - Claude Code via Anthropic Pro (assumes you're logged in)
#   zai - Claude Code via z.ai GLM API
#   oc  - OpenCode wrapper using OPENROUTER key from the vault when available
#
# UPDATING GLM VERSION:
#   When z.ai releases a new model (e.g., glm-4.8), just update GLM_MODEL
#   in your ~/.bashrc or re-run this script with the new version.
#
# GET YOUR ZAI API KEY:
#   https://z.ai/devpack → Sign up → Copy API key

# ╔════════════════════════════════════════════════════════════════╗
# ║  EDIT THESE VALUES BEFORE RUNNING --install                    ║
# ╚════════════════════════════════════════════════════════════════╝
ZAI_API_KEY="YOUR_ZAI_API_KEY_HERE"
GLM_MODEL="glm-5-turbo"          # Update when z.ai releases new version
SHELL_TYPE="${SHELL_TYPE:-bash}" # bash or zsh - auto-detected by --install
# ══════════════════════════════════════════════════════════════════

# Auto-detect shell type
if [[ -n "${ZSH_VERSION:-}" ]]; then
	SHELL_TYPE="zsh"
elif [[ -n "${BASH_VERSION:-}" ]]; then
	SHELL_TYPE="bash"
fi

# Handle --install flag
if [[ "$1" == "--install" ]]; then
	# Try vault first, fall back to hardcoded value, error if still placeholder
	if [[ "$ZAI_API_KEY" == "YOUR_ZAI_API_KEY_HERE" ]]; then
		_vault_key=$(secrets get ZAI_API_KEY 2>/dev/null)
		if [[ -n "$_vault_key" ]]; then
			ZAI_API_KEY="$_vault_key"
			echo "✓ ZAI_API_KEY loaded from vault"
		else
			echo "ERROR: ZAI_API_KEY not found in vault and not set in script." >&2
			echo "  Run: secrets set research_keys ZAI_API_KEY=<your-key>" >&2
			echo "  Or get your key at: https://z.ai/devpack" >&2
			exit 1
		fi
	fi

	# Auto-detect shell if not set
	if [[ -n "${ZSH_VERSION:-}" ]]; then
		SHELL_TYPE="zsh"
	elif [[ -n "${BASH_VERSION:-}" ]]; then
		SHELL_TYPE="bash"
	fi

	if [[ "$SHELL_TYPE" == "zsh" ]]; then
		SHELLRC="$HOME/.zshrc"
	else
		SHELLRC="$HOME/.bashrc"
	fi

	# Remove old block if exists (handles variants like "(oci-dev)" suffix)
	if grep -q "##### Claude Code + ZAI shortcuts" "$SHELLRC" 2>/dev/null; then
		sed -i.bak "/##### Claude Code + ZAI shortcuts/,/##### end Claude Code + ZAI shortcuts #####/d" "$SHELLRC"
		rm -f "${SHELLRC}.bak"
		echo "Removed old Claude/ZAI block from $SHELLRC"
	fi

	# Remove old heartbeat block if exists (for migration)
	if grep -q "##### ONE-SHOT Heartbeat #####" "$SHELLRC" 2>/dev/null; then
		sed -i.bak "/##### ONE-SHOT Heartbeat #####/,/##### end ONE-SHOT Heartbeat #####/d" "$SHELLRC"
		rm -f "${SHELLRC}.bak"
		echo "Removed old Heartbeat block from $SHELLRC"
	fi

	# Append new block
	cat >>"$SHELLRC" <<'SHELLRC_BLOCK'

##### Claude Code + ZAI shortcuts #####
# Portable setup: github.com/Khamel83/oneshot/scripts/claude-shell-setup.sh
# To reinstall: bash claude-shell-setup.sh --install

export ZAI_API_KEY="__ZAI_API_KEY__"
export GLM_MODEL="__GLM_MODEL__"

unalias cc zai oc 2>/dev/null || true
unset -f cc zai oc 2>/dev/null || true

# cc - Claude Code via Anthropic Pro (bypassPermissions via settings.json)
cc() {
    claude "$@"
}

# zai - Claude Code via z.ai GLM API (bypassPermissions via settings.json)
zai() {
    if ! command -v claude >/dev/null 2>&1; then
        echo "zai: 'claude' CLI not found (npm install -g @anthropic-ai/claude-code)" >&2
        return 127
    fi
    [[ -z "$ZAI_API_KEY" ]] && { echo "zai: ZAI_API_KEY not set" >&2; return 1; }

    echo "zai: z.ai/$GLM_MODEL" >&2
    ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
    ANTHROPIC_AUTH_TOKEN="$ZAI_API_KEY" \
    ANTHROPIC_MODEL="$GLM_MODEL" \
        claude "$@"
}

# oc - OpenCode wrapper with vault-backed OpenRouter auth when available
oc() {
    if ! command -v opencode >/dev/null 2>&1; then
        echo "oc: 'opencode' CLI not found" >&2
        return 127
    fi

    unset OPENAI_API_KEY OPENAI_BASE_URL ANTHROPIC_BASE_URL
    if command -v secrets >/dev/null 2>&1; then
        export OPENROUTER_API_KEY="$(secrets get OPENROUTER_API_KEY 2>/dev/null || true)"
    fi

    opencode "$@"
}

# saveplan - open $EDITOR on /tmp/claude-plan.md to paste a plan
alias saveplan='${EDITOR:-nano} /tmp/claude-plan.md'

# approveplan [project-dir] - write /tmp/claude-plan.md to <project>/.claude/CLAUDE.md,
# launch a fresh claude session, then offer to clean up on exit
approveplan() {
    local project="${1:-$PWD}"
    local plan_file="/tmp/claude-plan.md"
    local claude_md="$project/.claude/CLAUDE.md"
    local backup_file="/tmp/claude-plan-backup.md"
    local was_fresh=false

    if [[ ! -f "$plan_file" ]]; then
        echo "approveplan: no plan at $plan_file — run 'saveplan' first" >&2
        return 1
    fi

    mkdir -p "$project/.claude"

    if [[ ! -f "$claude_md" ]]; then
        was_fresh=true
    else
        cp "$claude_md" "$backup_file"
    fi

    cp "$plan_file" "$claude_md"
    echo "Plan written to $claude_md"

    (cd "$project" && claude)

    read -r -p "Remove plan from CLAUDE.md? [y/N] " answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        if [[ "$was_fresh" == "true" ]]; then
            rm "$claude_md"
            echo "Removed $claude_md"
        else
            mv "$backup_file" "$claude_md"
            echo "Restored original $claude_md"
        fi
    fi
    rm -f "$backup_file"
}
##### end Claude Code + ZAI shortcuts #####

##### ONE-SHOT Heartbeat #####
# Daily health checks on project enter (cd to directory with CLAUDE.md)
# Run manually: bash ~/github/oneshot/scripts/heartbeat.sh [--force] [--quiet]

_oneshot_heartbeat() {
    local heartbeat_script="${ONESHOT_DIR:-$HOME/github/oneshot}/scripts/heartbeat.sh"
    if [[ -f "$PWD/CLAUDE.md" ]] && [[ -x "$heartbeat_script" ]]; then
        "$heartbeat_script" --quiet --background 2>/dev/null &
    fi
}

oneshot-dismiss() {
    local suppressed="$HOME/.claude/state/suppressed-warnings"
    mkdir -p "$(dirname "$suppressed")"
    echo "$1" >> "$suppressed"
    echo "Dismissed: $1"
}
##### end ONE-SHOT Heartbeat #####
SHELLRC_BLOCK

	# Replace placeholders with actual values (escaped for safety)
	# Escape special characters in API key for sed
	escaped_key=$(printf '%s\n' "$ZAI_API_KEY" | sed 's/[[\.*^$()+?{|]/\\&/g')
	escaped_model=$(printf '%s\n' "$GLM_MODEL" | sed 's/[[\.*^$()+?{|]/\\&/g')
	sed -i.bak "s|__ZAI_API_KEY__|${escaped_key}|g" "$SHELLRC"
	sed -i.bak "s|__GLM_MODEL__|${escaped_model}|g" "$SHELLRC"
	rm -f "${SHELLRC}.bak"

	# Add shell-specific hook
	if [[ "$SHELL_TYPE" == "zsh" ]]; then
		# Remove old hook if exists
		sed -i.bak '/add-zsh-hook _oneshot_heartbeat/d' "$SHELLRC" 2>/dev/null || true
		rm -f "${SHELLRC}.bak"
		# Add zsh hook
		cat >>"$SHELLRC" <<'ZSH_HOOK'

# ONE-SHOT Heartbeat: zsh chpwd hook
autoload -U add-zsh-hook
add-zsh-hook chpwd _oneshot_heartbeat
ZSH_HOOK
	else
		# Remove old hook if exists
		sed -i.bak '/PROMPT_COMMAND.*_oneshot_heartbeat/d' "$SHELLRC" 2>/dev/null || true
		rm -f "${SHELLRC}.bak"
		# Add bash hook (unquoted heredoc so \$ becomes $ in the file)
		cat >>"$SHELLRC" <<BASH_HOOK

# ONE-SHOT Heartbeat: bash PROMPT_COMMAND hook
PROMPT_COMMAND="_oneshot_heartbeat\${PROMPT_COMMAND:+;\$PROMPT_COMMAND}"
BASH_HOOK
	fi

	echo "✓ Installed to $SHELLRC"
	echo "✓ cc  = Claude Code (Anthropic Pro, YOLO mode)"
	echo "✓ zai = Claude Code (z.ai $GLM_MODEL, YOLO mode)"
	echo "✓ oc  = OpenCode wrapper (vault-backed OpenRouter auth)"
	echo "✓ Heartbeat: Daily health checks on project enter"
	echo ""
	if [[ "$SHELL_TYPE" == "zsh" ]]; then
		echo "Run: source ~/.zshrc"
	else
		echo "Run: source ~/.bashrc"
	fi
	exit 0
fi

# If sourced directly (not --install), just define the functions
if [[ "$ZAI_API_KEY" == "YOUR_ZAI_API_KEY_HERE" ]]; then
	echo "WARNING: ZAI_API_KEY not set. Edit the script or set ZAI_API_KEY env var." >&2
fi

unalias cc zai oc 2>/dev/null || true
unset -f cc zai oc 2>/dev/null || true

# cc - Claude Code via Anthropic Pro (bypassPermissions via settings.json)
cc() {
	claude "$@"
}

# zai - Claude Code via z.ai GLM API (bypassPermissions via settings.json)
zai() {
	if ! command -v claude >/dev/null 2>&1; then
		echo "zai: 'claude' CLI not found (npm install -g @anthropic-ai/claude-code)" >&2
		return 127
	fi
	[[ -z "$ZAI_API_KEY" ]] && {
		echo "zai: ZAI_API_KEY not set" >&2
		return 1
	}

	echo "zai: z.ai/$GLM_MODEL" >&2
	ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
		ANTHROPIC_AUTH_TOKEN="$ZAI_API_KEY" \
		ANTHROPIC_MODEL="$GLM_MODEL" \
		claude "$@"
}

# oc - OpenCode wrapper with vault-backed OpenRouter auth when available
oc() {
	if ! command -v opencode >/dev/null 2>&1; then
		echo "oc: 'opencode' CLI not found" >&2
		return 127
	fi

	unset OPENAI_API_KEY OPENAI_BASE_URL ANTHROPIC_BASE_URL
	if command -v secrets >/dev/null 2>&1; then
		export OPENROUTER_API_KEY="$(secrets get OPENROUTER_API_KEY 2>/dev/null || true)"
	fi

	opencode "$@"
}

# saveplan - open $EDITOR on /tmp/claude-plan.md to paste a plan
alias saveplan='${EDITOR:-nano} /tmp/claude-plan.md'

# approveplan [project-dir] - write /tmp/claude-plan.md to <project>/.claude/CLAUDE.md,
# launch a fresh claude session, then offer to clean up on exit
approveplan() {
	local project="${1:-$PWD}"
	local plan_file="/tmp/claude-plan.md"
	local claude_md="$project/.claude/CLAUDE.md"
	local backup_file="/tmp/claude-plan-backup.md"
	local was_fresh=false

	if [[ ! -f "$plan_file" ]]; then
		echo "approveplan: no plan at $plan_file — run 'saveplan' first" >&2
		return 1
	fi

	mkdir -p "$project/.claude"

	if [[ ! -f "$claude_md" ]]; then
		was_fresh=true
	else
		cp "$claude_md" "$backup_file"
	fi

	cp "$plan_file" "$claude_md"
	echo "Plan written to $claude_md"

	(cd "$project" && claude)

	read -r -p "Remove plan from CLAUDE.md? [y/N] " answer
	if [[ "$answer" =~ ^[Yy]$ ]]; then
		if [[ "$was_fresh" == "true" ]]; then
			rm "$claude_md"
			echo "Removed $claude_md"
		else
			mv "$backup_file" "$claude_md"
			echo "Restored original $claude_md"
		fi
	fi
	rm -f "$backup_file"
}

# Heartbeat function (for manual use or sourcing)
_oneshot_heartbeat() {
	local heartbeat_script="${ONESHOT_DIR:-$HOME/github/oneshot}/scripts/heartbeat.sh"
	if [[ -f "$heartbeat_script" ]]; then
		"$heartbeat_script" "${@}"
	else
		echo "Heartbeat script not found at: $heartbeat_script" >&2
		return 1
	fi
}

oneshot-dismiss() {
	local suppressed="$HOME/.claude/state/suppressed-warnings"
	mkdir -p "$(dirname "$suppressed")"
	echo "$1" >>"$suppressed"
	echo "Dismissed: $1"
}
