#!/usr/bin/env bash
# check-backup.sh — Daily encrypted recovery snapshot
# Generates secrets/backup-snapshot.env.encrypted with full system inventory.
# NO secret values — only names, fingerprints, and statuses.
# Part of the heartbeat system. Run manually: ./scripts/check-backup.sh
#
# To restore: sops -d secrets/backup-snapshot.env.encrypted

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/secrets-helper.sh"

VAULT_DIR="$(cd "$SCRIPT_DIR/../secrets" && pwd)"
SNAPSHOT_FILE="$VAULT_DIR/backup-snapshot.env.encrypted"
ISSUES=0

# ── Collect snapshot data ────────────────────────────────────────────────────

TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
HOSTNAME=$(hostname)

# Age identity
AGE_PUBKEY=$(age-keygen -y ~/.age/key.txt 2>/dev/null || echo "missing")

# Vault inventory (names + key counts, no values)
VAULT_LIST=$(secrets_list 2>/dev/null | grep -v "^===" | grep -v "^$" | sed 's/^  //' || echo "unavailable")

# Skills
SKILLS=$(ls ~/.claude/skills/ 2>/dev/null | grep -v _shared | grep -v INDEX | grep -v SKILLS_REFERENCE | grep -v "\.md" | sort | tr '\n' ' ' || echo "unknown")

# Git state
if git rev-parse --git-dir >/dev/null 2>&1; then
  GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "detached")
  GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
  GIT_DIRTY=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  if [[ "$GIT_DIRTY" == "0" ]]; then
    GIT_STATUS="clean"
  else
    GIT_STATUS="$GIT_DIRTY uncommitted"
  fi
else
  GIT_BRANCH="not a git repo"
  GIT_COMMIT="unknown"
  GIT_STATUS="unknown"
fi

# Machine reachability (quick SSH check)
MACHINES_OK=""
for machine in oci-dev homelab macmini; do
  if ssh -o ConnectTimeout=2 -o BatchMode=yes "$machine" true 2>/dev/null; then
    MACHINES_OK="${MACHINES_OK}${machine}:ok "
  else
    MACHINES_OK="${MACHINES_OK}${machine}:unreachable "
  fi
done

# Vault file count
VAULT_COUNT=$(find "$VAULT_DIR" -name "*.encrypted" -maxdepth 1 2>/dev/null | wc -l | tr -d ' ')

# ── Build snapshot ────────────────────────────────────────────────────────────

WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT

# Write temp .sops.yaml (avoids path_regex mismatch on /tmp files)
AGE_RECIPIENT=$(grep "age:" .sops.yaml 2>/dev/null | head -1 | awk '{print $3}' || echo "")
if [[ -z "$AGE_RECIPIENT" ]]; then
  AGE_RECIPIENT="$AGE_PUBKEY"
fi

cat > "$WORK_DIR/.sops.yaml" << EOF
creation_rules:
  - age: ${AGE_RECIPIENT}
EOF

# Write snapshot content using printf (avoids heredoc variable expansion issues under set -e)
{
  cat << HEADER
# ONE_SHOT Recovery Snapshot
# Generated: $TIMESTAMP
# Machine: $HOSTNAME
#
# This file contains NO secret values — only names, counts, and statuses.
# Use it to reconstruct your oneshot setup from scratch.
#
# ── HOW TO RESTORE ──────────────────────────────────────────────────────
# 1. Install age:       sudo apt install age   (or: brew install age)
# 2. Generate age key:  age-keygen -o ~/.age/key.txt
# 3. Replace the key:   paste the real private key into ~/.age/key.txt
# 4. Verify decrypt:    sops -d backup-snapshot.env.encrypted
# 5. Clone oneshot:     git clone https://github.com/Khamel83/oneshot.git
# 6. Vault decrypts:    secrets list   (should show all vault files)
# 7. Heartbeat:         ./scripts/heartbeat.sh --force
#
# ── HOW TO ENCRYPT / DECRYPT FILES ──────────────────────────────────────
# Encrypt:  echo "KEY=value" > file.env && sops -e --input-type dotenv --output-type dotenv file.env > file.env.encrypted && rm file.env
# Decrypt:  sops -d file.env.encrypted
# Edit:     sops file.env.encrypted   (opens decrypted, re-encrypts on save)
# Add key:  secrets set <vault_name> "NEW_KEY=value"   (auto-commits)
# Get key:  secrets get KEY_NAME
# List:     secrets list
#
# ── .sops.yaml (required in repo root) ──────────────────────────────────
# creation_rules:
#   - age: <your-age-pubkey>
#     path_regex: '.*\.encrypted$'
#
# ── REQUIREMENTS ────────────────────────────────────────────────────────
# - age (encryption tool)
# - sops (secret manager, install: https://github.com/getsops/sops)
# - ~/.age/key.txt (600 permissions, same key on all machines)
# - git access to github.com/Khamel83/oneshot
# ─────────────────────────────────────────────────────────────────────────

HEADER

  printf '## Age Identity\nPUBLIC_KEY=%s\n\n' "$AGE_PUBKEY"

  printf '## Machines\n'
  printf '# oci-dev|ubuntu|100.126.13.70|Primary dev, services, Claude Code\n'
  printf '# homelab|khamel83|100.112.130.100|Docker, 26TB storage\n'
  printf '# macmini|macmini|100.113.216.27|Apple Silicon GPU\n'

  printf '\n## Machine Status\n# %s\n' "$MACHINES_OK"

  # Vault list — prefix each line with # for dotenv compatibility
  printf '## Vault (%s encrypted files)\n' "$VAULT_COUNT"
  echo "$VAULT_LIST" | while IFS= read -r line; do
    printf '# %s\n' "$line"
  done

  printf '## Active Skills\n# %s\n' "$SKILLS"

  printf '## Git State\nBRANCH=%s\nCOMMIT=%s\nSTATUS=%s\n' "$GIT_BRANCH" "$GIT_COMMIT" "$GIT_STATUS"
} > "$WORK_DIR/snapshot.env"

# ── Encrypt ──────────────────────────────────────────────────────────────────

if ! command -v sops >/dev/null 2>&1; then
  echo "✓ Backup skipped (sops not installed)"
  exit 0
fi

cd "$SCRIPT_DIR/.."

if (cd "$WORK_DIR" && SOPS_AGE_KEY_FILE="$HOME/.age/key.txt" sops -e \
    --input-type dotenv --output-type dotenv snapshot.env > output.encrypted 2>/dev/null) && \
   [[ -f "$WORK_DIR/output.encrypted" && -s "$WORK_DIR/output.encrypted" ]]; then
  mv "$WORK_DIR/output.encrypted" "$SNAPSHOT_FILE"
  chmod 644 "$SNAPSHOT_FILE"

  # Auto-commit if there are changes
  if git diff --quiet "$SNAPSHOT_FILE" 2>/dev/null; then
    echo "✓ Backup snapshot (unchanged)"
  else
    git add "$SNAPSHOT_FILE" >/dev/null 2>&1
    if git commit -m "chore: daily backup snapshot $(date +%Y-%m-%d)" >/dev/null 2>&1; then
      echo "✓ Backup snapshot (committed)"
    else
      echo "✓ Backup snapshot (updated)"
    fi
  fi
else
  echo "⚠️  Backup snapshot failed (sops encryption error)"
  ISSUES=1
fi

exit $ISSUES
