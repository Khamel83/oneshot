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

# === CONFLICT DETECTION ===
# Find Host entries in new config
new_hosts=$(grep -E '^Host ' "$tmp" | awk '{print $2}' | sort)

# Find Host entries BEFORE the managed block in existing config
# (everything before "# === OMAR SSH ALIASES")
pre_managed=$(awk '/# === OMAR SSH ALIASES \(managed\) ===/{exit} /^Host /{print $2}' "$CFG" 2>/dev/null || true)

# Check for conflicts
conflicts=""
for host in $new_hosts; do
  if echo "$pre_managed" | grep -qx "$host"; then
    conflicts="$conflicts  - $host\n"
  fi
done

if [ -n "$conflicts" ]; then
  echo "⚠️  WARNING: Duplicate SSH aliases found in your config:"
  echo -e "$conflicts"
  echo ""
  echo "You have manual entries that conflict with the managed aliases."
  echo ""
  echo "Options:"
  echo "  1) Cancel and clean up manually (nano ~/.ssh/config)"
  echo "  2) Proceed anyway (managed block will shadow manual entries)"
  echo ""
  read -p "Proceed? [y/N] " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled. Backup saved at $CFG.bak.$(date +%F_%H%M%S)"
    exit 1
  fi
fi

# === APPLY CHANGES ===
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
