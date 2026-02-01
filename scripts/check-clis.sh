#!/usr/bin/env bash
# Check if CLIs are installed and up to date
# Checks: Claude Code, Gemini CLI, Qwen CLI, Codex
# Usage: ./check-clis.sh [--fix]

set -euo pipefail

FIX_MODE="${1:-}"

# Add common binary locations to PATH (macOS Homebrew, Linux, nvm)
export PATH="$PATH:/opt/homebrew/bin:/usr/local/bin:$HOME/.nvm/versions/node/*/bin"

# Source nvm if available (for Node.js tools like claude)
if [[ -f "$HOME/.nvm/nvm.sh" ]]; then
  export NVM_DIR="$HOME/.nvm"
  . "$NVM_DIR/nvm.sh"
fi

ISSUES=0

# Check Claude Code CLI
check_claude_cli() {
  if ! command -v claude >/dev/null 2>&1; then
    if [[ "$FIX_MODE" == "--fix" ]]; then
      echo "⚠️  Claude Code CLI: not installed → installing..."
      if npm install -g @anthropic-ai/claude-code >/dev/null 2>&1; then
        # Refresh path after install
        if [[ -f "$HOME/.nvm/nvm.sh" ]]; then
          . "$NVM_DIR/nvm.sh"
        fi
        hash -r
        local version
        version=$(claude --version 2>/dev/null | head -1 || echo "unknown")
        echo "✓ Claude Code CLI: $version (newly installed)"
        return 0
      else
        echo "⚠️  Claude Code CLI: installation failed"
        return 1
      fi
    fi
    echo "⚠️  Claude Code CLI: not installed (npm install -g @anthropic-ai/claude-code)"
    return 1
  fi

  local version
  version=$(claude --version 2>/dev/null | head -1 || echo "unknown")

  # Check if version is outdated (2.0.x vs 2.1.x)
  if [[ "$FIX_MODE" == "--fix" ]] && [[ "$version" == *"2.0"* ]]; then
    echo "⚠️  Claude Code CLI: $version → updating..."
    if npm update -g @anthropic-ai/claude-code >/dev/null 2>&1; then
      hash -r
      version=$(claude --version 2>/dev/null | head -1 || echo "unknown")
      echo "✓ Claude Code CLI: $version (updated)"
      return 0
    fi
  fi

  echo "✓ Claude Code CLI: $version"
  return 0
}

# Check Gemini CLI
check_gemini_cli() {
  if ! command -v gemini >/dev/null 2>&1; then
    echo "⊘ Gemini CLI: not installed (optional)"
    return 0
  fi

  local version
  version=$(gemini --version 2>/dev/null || echo "unknown")
  echo "✓ Gemini CLI: $version"
  return 0
}

# Check Qwen CLI
check_qwen_cli() {
  if ! command -v qwen >/dev/null 2>&1; then
    echo "⊘ Qwen CLI: not installed (optional)"
    return 0
  fi

  local version
  version=$(qwen --version 2>/dev/null || echo "unknown")
  echo "✓ Qwen CLI: $version"
  return 0
}

# Check Codex CLI
check_codex_cli() {
  if ! command -v codex >/dev/null 2>&1; then
    echo "⊘ Codex CLI: not installed (optional)"
    return 0
  fi

  local version
  version=$(codex --version 2>/dev/null || echo "unknown")
  echo "✓ Codex CLI: $version"
  return 0
}

# Run all checks
check_claude_cli || ISSUES=1
check_gemini_cli || ISSUES=1
check_qwen_cli || ISSUES=1
check_codex_cli || ISSUES=1

exit $ISSUES
