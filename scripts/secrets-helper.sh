#!/bin/bash
# secrets-helper.sh — Comprehensive SOPS/Age helper for ALL oneshot projects
#
# THE PROBLEM this solves:
#   sops 3.8.x requires a .sops.yaml config when encrypting new files.
#   Secrets encrypted as dotenv format MUST be decrypted with --input-type dotenv.
#   Running sops from outside the repo root fails because .sops.yaml isn't found.
#
# USAGE:
#   source scripts/secrets-helper.sh          # load functions
#   secrets_get SKILLSMP_API_KEY              # read one key from vault
#   secrets_set skillsmp SKILLSMP_API_KEY=val # write/update a secret
#   secrets_list                              # show all available secrets
#   secrets_decrypt skillsmp                  # decrypt full file to stdout
#
# VAULT: ~/github/oneshot/secrets/ (master)
# PROJECT: secrets/ in current project (optional local override)

ONESHOT_VAULT="${ONESHOT_VAULT:-$HOME/github/oneshot/secrets}"
AGE_KEY_FILE="${SOPS_AGE_KEY_FILE:-$HOME/.age/key.txt}"
AGE_RECIPIENT="age1kwu32vl7x3tx7dqphzykcf5cahgm4ejztm865f22fkwe5j6hwalqh0rau8"

# ─────────────────────────────────────────────────────────────────────────────
# Core: decrypt a .encrypted file (handles both json and dotenv format)
# ─────────────────────────────────────────────────────────────────────────────
_sops_decrypt() {
  local file="$1"
  if [ ! -f "$file" ]; then
    echo "secrets-helper: file not found: $file" >&2
    return 1
  fi

  # Detect format: JSON starts with '{', dotenv doesn't
  local first_char
  first_char=$(head -c1 "$file")

  if [ "$first_char" = "{" ]; then
    SOPS_AGE_KEY_FILE="$AGE_KEY_FILE" sops -d "$file" 2>/dev/null
  else
    SOPS_AGE_KEY_FILE="$AGE_KEY_FILE" sops -d --input-type dotenv --output-type dotenv "$file" 2>/dev/null
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Core: encrypt a dotenv string to a .encrypted file
# Handles the .sops.yaml discovery problem by working from the repo root
# ─────────────────────────────────────────────────────────────────────────────
_sops_encrypt_dotenv() {
  local content="$1"
  local output="$2"

  # Find a directory with .sops.yaml (repo root)
  local sops_dir="$ONESHOT_VAULT/.."
  if [ ! -f "$sops_dir/.sops.yaml" ]; then
    # Fall back: write a temp .sops.yaml and work from /tmp
    local work_dir
    work_dir=$(mktemp -d)
    cat > "$work_dir/.sops.yaml" << SOPSEOF
creation_rules:
  - age: $AGE_RECIPIENT
SOPSEOF
    printf '%s\n' "$content" > "$work_dir/input.env"
    SOPS_AGE_KEY_FILE="$AGE_KEY_FILE" sops -e --input-type dotenv --output-type dotenv \
      "$work_dir/input.env" > "$work_dir/output.encrypted"
    local exit_code=$?
    if [ $exit_code -eq 0 ]; then
      mv "$work_dir/output.encrypted" "$output"
    fi
    rm -rf "$work_dir"
    return $exit_code
  fi

  local work_dir
  work_dir=$(mktemp -d)
  printf '%s\n' "$content" > "$work_dir/input.env"
  (cd "$sops_dir" && SOPS_AGE_KEY_FILE="$AGE_KEY_FILE" sops -e --input-type dotenv \
    --output-type dotenv "$work_dir/input.env" > "$work_dir/output.encrypted")
  local exit_code=$?
  if [ $exit_code -eq 0 ]; then
    mv "$work_dir/output.encrypted" "$output"
  fi
  rm -rf "$work_dir"
  return $exit_code
}

# ─────────────────────────────────────────────────────────────────────────────
# Public: get a single key value from any vault file
# Usage: secrets_get SKILLSMP_API_KEY [file-prefix]
# ─────────────────────────────────────────────────────────────────────────────
secrets_get() {
  local key="$1"
  local prefix="${2:-}"

  local search_dirs=("secrets" "$ONESHOT_VAULT")
  for dir in "${search_dirs[@]}"; do
    [ -d "$dir" ] || continue
    for file in "$dir"/*.encrypted; do
      [ -f "$file" ] || continue
      [[ -n "$prefix" && "$(basename "$file")" != "${prefix}"* ]] && continue
      local val
      val=$(_sops_decrypt "$file" 2>/dev/null | grep "^${key}=" | cut -d= -f2-)
      if [ -n "$val" ]; then
        echo "$val"
        return 0
      fi
    done
  done

  echo "secrets-helper: key '$key' not found in any vault file" >&2
  return 1
}

# ─────────────────────────────────────────────────────────────────────────────
# Public: decrypt a named secret file to stdout
# Usage: secrets_decrypt skillsmp
# ─────────────────────────────────────────────────────────────────────────────
secrets_decrypt() {
  local name="$1"

  for dir in "secrets" "$ONESHOT_VAULT"; do
    local file="$dir/${name}.env.encrypted"
    if [ -f "$file" ]; then
      _sops_decrypt "$file"
      return $?
    fi
  done

  echo "secrets-helper: '$name.env.encrypted' not found" >&2
  return 1
}

# ─────────────────────────────────────────────────────────────────────────────
# Public: set/update a secret
# Usage: secrets_set skillsmp "SKILLSMP_API_KEY=val"
# ─────────────────────────────────────────────────────────────────────────────
secrets_set() {
  local name="$1"
  local kv="$2"
  local vault="${3:-$ONESHOT_VAULT}"

  local output="$vault/${name}.env.encrypted"

  # If file exists, merge: decrypt, update/add key, re-encrypt
  if [ -f "$output" ]; then
    local key="${kv%%=*}"
    local existing
    existing=$(_sops_decrypt "$output" 2>/dev/null | grep -v "^${key}=" || true)
    local new_content="${existing}
${kv}"
    _sops_encrypt_dotenv "$new_content" "$output"
  else
    _sops_encrypt_dotenv "$kv" "$output"
  fi

  if [ $? -eq 0 ]; then
    echo "secrets-helper: saved $key to $output"
  else
    echo "secrets-helper: failed to save $kv" >&2
    return 1
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Public: list all available secret files and their keys (names only)
# ─────────────────────────────────────────────────────────────────────────────
secrets_list() {
  echo "=== Secrets Vault: $ONESHOT_VAULT ==="
  for file in "$ONESHOT_VAULT"/*.encrypted; do
    [ -f "$file" ] || continue
    local name
    name=$(basename "$file" .encrypted)
    local keys
    keys=$(_sops_decrypt "$file" 2>/dev/null | grep -oE '^[A-Z_]+(?==)' || \
           _sops_decrypt "$file" 2>/dev/null | grep '=' | cut -d= -f1 | tr '\n' ' ')
    echo "  $name: $keys"
  done

  if [ -d "secrets" ] && [ "$(realpath secrets 2>/dev/null)" != "$(realpath "$ONESHOT_VAULT" 2>/dev/null)" ]; then
    echo ""
    echo "=== Project secrets: secrets/ ==="
    for file in secrets/*.encrypted; do
      [ -f "$file" ] || continue
      local name
      name=$(basename "$file" .encrypted)
      local keys
      keys=$(_sops_decrypt "$file" 2>/dev/null | grep '=' | cut -d= -f1 | tr '\n' ' ')
      echo "  $name: $keys"
    done
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# If run directly (not sourced): act as a CLI
# ─────────────────────────────────────────────────────────────────────────────
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-}" in
    get)     secrets_get "$2" "${3:-}" ;;
      set)
      secrets_set "$2" "$3" "${4:-}"
      if [ $? -eq 0 ] && [ -d "$ONESHOT_VAULT/.git" ]; then
        echo ""
        read -rp "Commit and push to all machines? [Y/n] " confirm
        [[ "$confirm" =~ ^[Nn] ]] && exit 0
        (cd "$ONESHOT_VAULT/.." && git add secrets/ && git commit -m "feat: update $2 secrets" && git push)
        echo "Pushed. Other machines will pick it up on next git pull."
      fi
      ;;
    decrypt) secrets_decrypt "$2" ;;
    list)    secrets_list ;;
    *)
      echo "Usage: secrets-helper.sh <command> [args]"
      echo ""
      echo "Commands:"
      echo "  get <KEY> [file-prefix]       Get a single key value"
      echo "  set <name> <KEY=value>        Set/update a secret"
      echo "  decrypt <name>               Decrypt full file to stdout"
      echo "  list                          List all files and key names"
      echo ""
      echo "Examples:"
      echo "  secrets-helper.sh get SKILLSMP_API_KEY"
      echo "  secrets-helper.sh set skillsmp 'SKILLSMP_API_KEY=sk_live_...'"
      echo "  secrets-helper.sh decrypt openclaw"
      echo "  secrets-helper.sh list"
      ;;
  esac
fi
