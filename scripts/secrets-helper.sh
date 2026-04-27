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

# ─────────────────────────────────────────────────────────────────────────────
# KEY INDEX — which file holds which key (run `secrets list` for full dump)
# ─────────────────────────────────────────────────────────────────────────────
# api.env            JINA_API_KEY
# arb.env            POLYMARKET_PRIVATE_KEY DUNE_API_KEY UPSTASH_REDIS_REST_TOKEN NORDVPN_PRIVATE_KEY DISCORD_WEBHOOK_URL
# argus.env          ARGUS_BRAVE_API_KEY ARGUS_REMOTE_EXTRACT_KEY ARGUS_REMOTE_EXTRACT_URL
# argus_auth.env     NYTIMES/WSJ/BLOOMBERG/ESPN/LATIMES email+password pairs
# cloudflare.env     CLOUDFLARE_HYPERDRIVE_ID
# convex.env         CONVEX_TEAM_ACCESS_TOKEN CONVEX_TEAM_ID
# convex_deploy.env  CONVEX_DEPLOY_KEY CONVEX_DEPLOYMENT_URL
# coparent.env       TWILIO_* GOOGLE_CALENDAR_* GOOGLE_OAUTH_* OPENROUTER_API_KEY TELEGRAM_BOT_TOKEN
# deployments.env    VERCEL_TOKEN SUPABASE_* STRIPE_* NEXTAUTH_SECRET CRON_SECRET GOOGLE_MAPS_API_KEY
# gmail.env          GMAIL_CREDENTIALS_B64 GMAIL_TOKEN_B64 GMAIL_PROJECT GMAIL_ACCOUNT
# homelab_backup.env All homelab service keys (radarr/sonarr/authentik/cloudflare/tailscale/etc.)
# openclaw.env       BRAVE_API_KEY GEMINI_API_KEY OPENROUTER_API_KEY TELEGRAM_TOKEN_* HOMELAB_RPC_TOKEN
# penny.env          OPENROUTER_API_KEY TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID
# pypi.env           PYPI_API_TOKEN
# research_keys.env  EXA_API_KEY APIFY_TOKEN TAVILY_API_KEY ZAI_API_KEY OPENAI_API_KEY SERPER_API_KEY WOLFRAM_APP_ID ARGUS_DB_URL CRON_SECRET
# secrets.env        CLOUDFLARE_API_TOKEN CLOUDFLARE_ZONE_ID_* GITHUB_PAT DB_* JWT_SECRET EMAIL_* STRIPE_KEY REDIS_URL
# services.env       PERPLEXITY_API_KEY DEEPSEEK_API_KEY GAMMA_API_KEY DROPBOX_ACCESS_TOKEN ATLAS_API_KEY POYTZ_API_KEY OPENROUTER_API_KEY OPENROUTER_API_KEY_ALT1/ALT2 FIRECRAWL_API_KEY OP_SERVICE_ACCOUNT_TOKEN TELEGRAM_BOT_TOKEN_*
# skillsmp.env       SKILLSMP_API_KEY
# ─────────────────────────────────────────────────────────────────────────────

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
# NOTE: input file MUST end in .encrypted to match path_regex in .sops.yaml
# ─────────────────────────────────────────────────────────────────────────────
_sops_encrypt_dotenv() {
  local content="$1"
  local output="$2"

  local sops_dir="$ONESHOT_VAULT/.."
  if [ ! -f "$sops_dir/.sops.yaml" ]; then
    echo "secrets-helper: .sops.yaml not found at $sops_dir" >&2
    return 1
  fi

  local work_dir
  work_dir=$(mktemp -d)
  printf '%s\n' "$content" > "$work_dir/input.env.encrypted"
  (cd "$sops_dir" && SOPS_AGE_KEY_FILE="$AGE_KEY_FILE" sops -e \
    --input-type dotenv --output-type dotenv \
    "$work_dir/input.env.encrypted" > "$work_dir/output.encrypted")
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
    keys=$(_sops_decrypt "$file" 2>/dev/null | grep '=' | sed 's/=.*//' | grep -E '^[A-Z_][A-Z0-9_]*$' | tr '\n' ' ')
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
      keys=$(_sops_decrypt "$file" 2>/dev/null | grep '=' | sed 's/=.*//' | grep -E '^[A-Z_][A-Z0-9_]*$' | tr '\n' ' ')
      echo "  $name: $keys"
    done
  fi
}

# ─────────────────────────────────────────────────────────────────────────────
# Public: bootstrap .env in the current project from the vault
# Usage: secrets_init services  →  writes .env from services.env.encrypted
# ─────────────────────────────────────────────────────────────────────────────
secrets_init() {
  local name="${1:-}"

  if [ -z "$name" ]; then
    echo "Usage: secrets init <name>" >&2
    echo "  Decrypts <name>.env.encrypted from vault to .env" >&2
    return 1
  fi

  local source=""
  for dir in "secrets" "$ONESHOT_VAULT"; do
    if [ -f "$dir/${name}.env.encrypted" ]; then
      source="$dir/${name}.env.encrypted"
      break
    fi
  done

  if [ -z "$source" ]; then
    echo "secrets-helper: '$name.env.encrypted' not found in vault" >&2
    return 1
  fi

  if [ -f ".env" ]; then
    cp ".env" ".env.bak"
    echo "secrets-helper: backed up existing .env to .env.bak"
  fi

  _sops_decrypt "$source" > ".env"
  chmod 600 ".env"
  echo "secrets-helper: wrote .env from $source"
}

# ─────────────────────────────────────────────────────────────────────────────
# If run directly (not sourced): act as a CLI
# ─────────────────────────────────────────────────────────────────────────────
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  case "${1:-}" in
    get)     secrets_get "$2" "${3:-}" ;;
    init)    secrets_init "$2" ;;
      set)
      secrets_set "$2" "$3" "${4:-}"
      if [ $? -eq 0 ] && [ "${4:-}" = "--commit" ] && [ -d "$ONESHOT_VAULT/.git" ]; then
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
      echo "  set <name> <KEY=value> [--commit]  Set/update a secret"
      echo "  init <name>                   Write .env from vault"
      echo "  decrypt <name>               Decrypt full file to stdout"
      echo "  list                          List all files and key names"
      echo ""
      echo "Examples:"
      echo "  secrets-helper.sh get SKILLSMP_API_KEY"
      echo "  secrets-helper.sh set skillsmp 'SKILLSMP_API_KEY=sk_live_...'"
      echo "  secrets-helper.sh set skillsmp 'KEY=val' --commit"
      echo "  secrets-helper.sh init services"
      echo "  secrets-helper.sh decrypt openclaw"
      echo "  secrets-helper.sh list"
      ;;
  esac
fi
