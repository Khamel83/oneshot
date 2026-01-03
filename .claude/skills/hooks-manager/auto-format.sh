#!/bin/bash
# auto-format.sh - Run project formatter after file writes
# Detects formatter from project config and applies to written file

set -euo pipefail

# Read tool input from stdin
INPUT=$(cat)

# Extract file path
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Skip if no file path
if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
    exit 0
fi

# Get file extension
EXT="${FILE_PATH##*.}"

# Detect and run appropriate formatter
case "$EXT" in
    js|jsx|ts|tsx|json|css|scss|html|vue|svelte)
        # Prettier
        if command -v prettier &>/dev/null; then
            prettier --write "$FILE_PATH" 2>/dev/null || true
        elif [ -f "node_modules/.bin/prettier" ]; then
            node_modules/.bin/prettier --write "$FILE_PATH" 2>/dev/null || true
        fi
        ;;
    py)
        # Python - try ruff first (faster), then black
        if command -v ruff &>/dev/null; then
            ruff format "$FILE_PATH" 2>/dev/null || true
        elif command -v black &>/dev/null; then
            black --quiet "$FILE_PATH" 2>/dev/null || true
        fi
        ;;
    go)
        # Go
        if command -v gofmt &>/dev/null; then
            gofmt -w "$FILE_PATH" 2>/dev/null || true
        fi
        ;;
    rs)
        # Rust
        if command -v rustfmt &>/dev/null; then
            rustfmt "$FILE_PATH" 2>/dev/null || true
        fi
        ;;
    yaml|yml)
        # YAML - prettier if available
        if command -v prettier &>/dev/null; then
            prettier --write "$FILE_PATH" 2>/dev/null || true
        fi
        ;;
    sh|bash)
        # Shell - shfmt if available
        if command -v shfmt &>/dev/null; then
            shfmt -w "$FILE_PATH" 2>/dev/null || true
        fi
        ;;
esac

exit 0
