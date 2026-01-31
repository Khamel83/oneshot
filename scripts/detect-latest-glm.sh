#!/usr/bin/env bash
# Query Hugging Face API for latest GLM model
# Usage: ./detect-latest-glm.sh [--update-env] [--quiet]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/models.env"

detect_latest() {
  curl -s "https://huggingface.co/api/models?author=zai-org&limit=100" \
    | python3 -c "
import json, sys, re
data = json.load(sys.stdin)
versions = []
for m in data:
    match = re.search(r'GLM[-\.]?(\d+\.\d+)', m['modelId'])
    if match:
        versions.append((tuple(map(int, match.group(1).split('.'))), m['modelId']))
if versions:
    latest = max(versions, key=lambda x: x[0])
    model_id = latest[1].replace('GLM', 'glm').replace('-', '.').lower()
    print(model_id)
" 2>/dev/null || { echo "ERROR: Hugging Face API failed" >&2; return 1; }
}

case "${1:-}" in
  --update-env|-u)
    LATEST=$(detect_latest) || exit 1
    sed -i "s/^ZAI_MODEL_PIN=.*/ZAI_MODEL_PIN=$LATEST/" "$ENV_FILE"
    echo "✓ Updated GLM model to: $LATEST"
    ;;
  *)
    detect_latest
    ;;
esac
