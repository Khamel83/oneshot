#!/usr/bin/env bash
# Check GLM model version via Hugging Face API
# Returns: 0 if up to date, 1 if update available

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/models.env"

# Get current pinned version
if [[ -f "$ENV_FILE" ]]; then
  source "$ENV_FILE"
  CURRENT="${ZAI_MODEL_PIN:-unknown}"
else
  CURRENT="unknown"
fi

# Get latest from Hugging Face
LATEST=$("$SCRIPT_DIR/detect-latest-glm.sh" 2>/dev/null) || exit 2

if [[ "$LATEST" == "$CURRENT" ]]; then
  echo "✓ GLM: $CURRENT (up to date)"
  exit 0
else
  echo "⚠️  GLM: update available $CURRENT → $LATEST"
  exit 1
fi
