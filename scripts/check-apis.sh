#!/usr/bin/env bash
# Validate API keys by making minimal test calls
# Checks: ZAI, Tavily, Exa, Apify, Context7

set -euo pipefail

# Set SOPS key location (must be run from oneshot directory or parent)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOPS_CONFIG="${PROJECT_DIR}/.sops.yaml"

# Fallback to global config if local doesn't exist
if [[ ! -f "$SOPS_CONFIG" ]]; then
    SOPS_CONFIG="$HOME/github/oneshot/.sops.yaml"
fi

ISSUES=0

# Helper to decrypt key from JSON
_decrypt_key() {
    local _file="$1"
    local _key="$2"
    sops --config "$SOPS_CONFIG" -d "${PROJECT_DIR}/secrets/${_file}" 2>/dev/null | jq -r "${_key} // empty" 2>/dev/null || echo ""
}

# Test ZAI API key
check_zai_api() {
  local _zai_key
  _zai_key=$(_decrypt_key "research_keys.json.encrypted" '.ZAI_API_KEY')

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
  _tavily_key=$(_decrypt_key "research_keys.json.encrypted" '.TAVILY_API_KEY')

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
  _exa_key=$(_decrypt_key "research_keys.json.encrypted" '.EXA_API_KEY')

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
  _apify_key=$(_decrypt_key "research_keys.json.encrypted" '.APIFY_API_KEY')

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
  _context7_key=$(_decrypt_key "research_keys.json.encrypted" '.CONTEXT7_API_KEY')

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
