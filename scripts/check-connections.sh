#!/usr/bin/env bash
# Check external connections

set -euo pipefail

ISSUES=0

# Check Tailscale
if command -v tailscale >/dev/null 2>&1; then
  if tailscale status >/dev/null 2>&1; then
    echo "✓ Tailscale: connected"
  else
    echo "⚠️  Tailscale: not connected"
    ISSUES=1
  fi
else
  echo "⊘ Tailscale: not installed"
fi

# Check internet connectivity
if ping -c 1 -W 2 8.8.8.8 >/dev/null 2>&1; then
  echo "✓ Internet: connected"
else
  echo "⚠️  Internet: no connectivity"
  ISSUES=1
fi

exit $ISSUES
