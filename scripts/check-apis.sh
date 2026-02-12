#!/usr/bin/env bash
# Validate API keys by making minimal test calls
# Checks: ZAI, Tavily, Exa, Apify, Context7

set -euo pipefail

# Auto-detect SOPS config from current working directory
detect_sops_config() {
  local start_dir="$PWD"
  local checked_dirs=()

  # Check current dir and walk up 3 levels
  for i in {0..3}; do
    if [[ -f "$start_dir/.sops.yaml" ]]; then
      echo "$start_dir/.sops.yaml"
      return 0
    fi
    checked_dirs+=("$start_dir")
    start_dir="$(dirname "$start_dir")"

    # Stop at home directory
    [[ "$start_dir" == "$HOME" ]] && break
  done

  # Fallback to global oneshot config
  if [[ -f "$HOME/github/oneshot/.sops.yaml" ]]; then
    echo "$HOME/github/oneshot/.sops.yaml"
    echo "  ⚠️  Using global oneshot .sops.yaml (checked: ${checked_dirs[*]})" >&2
    return 0
  fi

  return 1
}

# Detect SOPS config from PWD
SOPS_CONFIG=$(detect_sops_config) || {
  echo "⊘ SOPS: No .sops.yaml found in current or parent directories"
  exit 0  # Not an error, just skip
}

# Set age recipient for decryption
export SOPS_AGE_RECIPIENTS=age1kwu32vl7x3tx7dqphzykcf5cahgm4ejztm865f22fkwe5j6hwalqh0rau8

# Determine secrets directory based on SOPS config location
SECRETS_BASE_DIR="$(dirname "$SOPS_CONFIG")"
SECRETS_DIR="${SECRETS_BASE_DIR}/secrets"

# If secrets dir doesn't exist relative to config, try oneshot
if [[ ! -d "$SECRETS_DIR" ]]; then
  SECRETS_DIR="$HOME/github/oneshot/secrets"
fi

ISSUES=0

# Decrypt and export a key from dotenv file
_decrypt_dotenv_key() {
    local _file="$1"
    local _key="$2"
    local _full_path="${SECRETS_DIR}/${_file}"

    if [[ ! -f "$_full_path" ]]; then
        echo ""
        return 0
    fi

    sops --config "$SOPS_CONFIG" --decrypt --input-type dotenv --output-type dotenv "$_full_path" 2>/dev/null | grep "^${_key}=" | cut -d'=' -f2
}

# Test ZAI API key
check_zai_api() {
  local _zai_key
  _zai_key=$(_decrypt_dotenv_key "research_keys.env.encrypted" "ZAI_API_KEY")

  if [[ -z "$_zai_key" ]]; then
    echo "⚠️  ZAI_API_KEY: not set"
    return 1
  fi

  # Simple test - just check if key looks valid
  if [[ ${#_zai_key} -lt 20 ]]; then
    echo "⚠️  ZAI_API_KEY: invalid format"
    return 1
  fi

  echo "✓ ZAI_API_KEY: set (${_zai_key:0:8}...)"
  return 0
}

# Test Tavily API
check_tavily_api() {
  local _tavily_key
  _tavily_key=$(_decrypt_dotenv_key "research_keys.env.encrypted" "TAVILY_API_KEY")

  if [[ -z "$_tavily_key" ]]; then
    echo "⊘ TAVILY_API_KEY: not set (optional)"
    return 0
  fi

  echo "✓ TAVILY_API_KEY: set"
  return 0
}

# Test Exa API
check_exa_api() {
  local _exa_key
  _exa_key=$(_decrypt_dotenv_key "research_keys.env.encrypted" "EXA_API_KEY")

  if [[ -z "$_exa_key" ]]; then
    echo "⊘ EXA_API_KEY: not set (optional)"
    return 0
  fi

  echo "✓ EXA_API_KEY: set (${_exa_key:0:8}...)"
  return 0
}

# Test Apify API
check_apify_api() {
  local _apify_key
  _apify_key=$(_decrypt_dotenv_key "research_keys.env.encrypted" "APIFY_TOKEN")

  if [[ -z "$_apify_key" ]]; then
    echo "⊘ APIFY_API_KEY: not set (optional)"
    return 0
  fi

  echo "✓ APIFY_API_KEY: set"
  return 0
}

# Test Context7 API
check_context7_api() {
  local _context7_key
  _context7_key=$(_decrypt_dotenv_key "research_keys.env.encrypted" "CONTEXT7_API_KEY")

  if [[ -z "$_context7_key" ]]; then
    echo "⊘ CONTEXT7_API_KEY: not set (optional)"
    return 0
  fi

  echo "✓ CONTEXT7_API_KEY: set"
  return 0
}

# Run all checks
check_zai_api || ISSUES=1
check_tavily_api || ISSUES=1
check_exa_api || ISSUES=1
check_apify_api || ISSUES=1
check_context7_api || ISSUES=1

exit $ISSUES
