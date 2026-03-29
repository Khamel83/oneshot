#!/usr/bin/env bash
# Check if CLIs are installed and up to date
# Checks: Claude Code, Codex, Gemini CLI
# Usage: ./check-clis.sh [--fix]
#
# Packages:
#   @anthropic-ai/claude-code  — Claude Code
#   @openai/codex             — Codex CLI
#   @google/gemini-cli        — Gemini CLI

set -euo pipefail

FIX_MODE="${1:-}"

# Ensure npm global binaries are on PATH (macOS Homebrew, Linux, nvm)
export PATH="$PATH:/opt/homebrew/bin:/usr/local/bin:$HOME/.nvm/versions/node/*/bin"
if [[ -f "$HOME/.nvm/nvm.sh" ]]; then
  export NVM_DIR="$HOME/.nvm"
  . "$NVM_DIR/nvm.sh"
fi

ISSUES=0

check_cli() {
  local name="$1"
  local pkg="$2"
  local cmd="$3"

  if ! command -v "$cmd" >/dev/null 2>&1; then
    if [[ "$FIX_MODE" == "--fix" ]]; then
      echo "⚠️  $name: installing $pkg..."
      if npm install -g "$pkg@latest" >/dev/null 2>&1; then
        hash -r
        echo "✓ $name: $(command $cmd 2>/dev/null | head -1 || echo 'installed')"
        return 0
      else
        echo "⚠️  $name: install failed"
        ISSUES=1
        return 1
      fi
    fi
    echo "⚠️  $name: not installed"
    ISSUES=1
    return 1
  fi

  echo "✓ $name: $($cmd --version 2>/dev/null | head -1 || echo 'unknown')"
  return 0
}

check_cli "Claude Code" "@anthropic-ai/claude-code" "claude" || true
check_cli "Codex CLI"   "@openai/codex"             "codex"  || true
check_cli "Gemini CLI"  "@google/gemini-cli"        "gemini" || true

# secrets CLI — symlink to PATH if missing
if command -v secrets >/dev/null 2>&1; then
  echo "✓ secrets CLI: installed"
else
  if [[ "$FIX_MODE" == "--fix" ]]; then
    mkdir -p ~/.local/bin
    ln -sf ~/github/oneshot/scripts/secrets ~/.local/bin/secrets
    echo "✓ secrets CLI: installed (symlinked to ~/.local/bin)"
  else
    echo "⚠️  secrets CLI: not on PATH"
    ISSUES=1
  fi
fi

exit $ISSUES
