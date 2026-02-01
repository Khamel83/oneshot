#!/usr/bin/env bash
# Sync secrets from oneshot repo to local machine
# Secrets are already pulled via git pull, this ensures accessibility

set -euo pipefail

# Add common binary locations to PATH (macOS Homebrew, Linux, nvm)
export PATH="$PATH:/opt/homebrew/bin:/usr/local/bin:$HOME/.nvm/versions/node/*/bin"

ONESHOT_DIR="${ONESHOT_DIR:-$HOME/github/oneshot}"
SECRETS_DIR="$ONESHOT_DIR/secrets"

if [[ ! -d "$SECRETS_DIR" ]]; then
  echo "⊘ Secrets: no secrets directory in oneshot"
  exit 0
fi

# Check if we can decrypt secrets (SOPS/Age key available)
SOPS_KEY="${SOPS_AGE_KEY_FILE:-$HOME/.age/key.txt}"

if [[ ! -f "$SOPS_KEY" ]]; then
  echo "⚠️  Secrets: SOPS/Age key not found - cannot decrypt"
  exit 1
fi

# Test decrypting one secret file
SECRET_FILE=$(find "$SECRETS_DIR" -name "*.encrypted" -o -name "*.env.encrypted" 2>/dev/null | head -1)

if [[ -n "$SECRET_FILE" ]]; then
  if SOPS_AGE_KEY_FILE="$SOPS_KEY" sops --decrypt --input-type dotenv --output-type dotenv "$SECRET_FILE" >/dev/null 2>&1; then
    echo "✓ Secrets: synced and decryptable"
    exit 0
  else
    echo "⚠️  Secrets: found but decryption failed"
    exit 1
  fi
else
  echo "⊘ Secrets: no encrypted files found"
  exit 0
fi
