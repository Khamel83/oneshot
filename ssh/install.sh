#!/usr/bin/env bash
set -euo pipefail

# Override if you ever move branches or repos:
REPO_RAW_BASE="${REPO_RAW_BASE:-https://raw.githubusercontent.com/Khamel83/oneshot/master}"
CONF_URL="${CONF_URL:-$REPO_RAW_BASE/ssh/aliases.conf}"

mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

CFG="$HOME/.ssh/config"
touch "$CFG"
chmod 600 "$CFG"

cp "$CFG" "$CFG.bak.$(date +%F_%H%M%S)"

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

curl -fsSL "$CONF_URL" -o "$tmp"

# Remove any prior managed block, then append the latest block from GitHub.
perl -0777 -i -pe '
  s{(?ms)^[ \t]*# === OMAR SSH ALIASES \(managed\) ===\n.*?^[ \t]*# === END OMAR SSH ALIASES ===\n?}{}g;
  s/\n{3,}/\n\n/g;
' "$CFG"

printf "\n%s\n" "$(cat "$tmp")" >> "$CFG"

# Basic sanity display (won't fail if ssh -G unsupported)
ssh -G oci 2>/dev/null | egrep 'hostname|user|identityfile' | head -n 10 || true

echo "OK: SSH aliases installed/updated from $CONF_URL"
echo "Try: ssh oci | ssh oci-ts | ssh homelab | ssh homelab-ts | ssh macmini | ssh macmini-ts"
