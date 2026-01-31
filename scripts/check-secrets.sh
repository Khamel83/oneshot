#!/usr/bin/env bash
# Check SOPS/Age secrets availability

set -euo pipefail

ISSUES=0

# Check SOPS/Age key file
SOPS_KEY="${SOPS_AGE_KEY_FILE:-$HOME/.age/key.txt}"

if [[ ! -f "$SOPS_KEY" ]]; then
  echo "⚠️  SOPS/Age key: not found at $SOPS_KEY"
  ISSUES=1
else
  echo "✓ SOPS/Age key: found"
fi

# Check if age command works
if command -v age >/dev/null 2>&1; then
  echo "✓ Age CLI: installed"
else
  echo "⚠️  Age CLI: not installed"
  ISSUES=1
fi

# Check if sops command works
if command -v sops >/dev/null 2>&1; then
  echo "✓ SOPS CLI: installed"
else
  echo "⚠️  SOPS CLI: not installed"
  ISSUES=1
fi

exit $ISSUES
