#!/bin/bash
# secrets-scan.sh - Block writes containing potential secrets
# Exit 0: No secrets found
# Exit 2: Secrets detected (blocks the write)

set -euo pipefail

# Read tool input from stdin
INPUT=$(cat)

# Extract file content from tool_input
CONTENT=$(echo "$INPUT" | jq -r '.tool_input.content // empty')
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Skip if no content (e.g., Read operations)
if [ -z "$CONTENT" ]; then
    exit 0
fi

# Skip certain file types that legitimately contain key-like strings
case "$FILE_PATH" in
    *.md|*.txt|*.log|*.test.*|*_test.*|*.spec.*)
        exit 0
        ;;
esac

# Patterns that indicate secrets (high confidence)
PATTERNS=(
    # API keys with common prefixes
    'sk-[a-zA-Z0-9]{20,}'           # OpenAI, Stripe secret keys
    'pk_live_[a-zA-Z0-9]{20,}'      # Stripe publishable
    'sk_live_[a-zA-Z0-9]{20,}'      # Stripe secret
    'ghp_[a-zA-Z0-9]{36}'           # GitHub PAT
    'gho_[a-zA-Z0-9]{36}'           # GitHub OAuth
    'ghu_[a-zA-Z0-9]{36}'           # GitHub user-to-server
    'ghs_[a-zA-Z0-9]{36}'           # GitHub server-to-server
    'github_pat_[a-zA-Z0-9_]{82}'   # GitHub fine-grained PAT
    'xox[baprs]-[a-zA-Z0-9-]+'      # Slack tokens
    'AKIA[0-9A-Z]{16}'              # AWS access key
    'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*'  # JWT tokens

    # Generic patterns
    'password\s*[=:]\s*["\x27][^"\x27]{8,}["\x27]'
    'api_key\s*[=:]\s*["\x27][^"\x27]{16,}["\x27]'
    'secret\s*[=:]\s*["\x27][^"\x27]{16,}["\x27]'
    'token\s*[=:]\s*["\x27][^"\x27]{20,}["\x27]'

    # Private keys
    '-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'
)

# Check content against patterns
for pattern in "${PATTERNS[@]}"; do
    if echo "$CONTENT" | grep -qiE "$pattern"; then
        echo "Potential secret detected matching pattern. Please use environment variables or SOPS encryption." >&2
        exit 2
    fi
done

exit 0
