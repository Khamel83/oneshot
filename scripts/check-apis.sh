#!/usr/bin/env bash
# Validate API keys using secrets-helper.sh (the right way)
# Checks: ZAI, Tavily, Exa, Apify, Context7, Claude
# Usage: ./check-apis.sh [--fix]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/secrets-helper.sh"

ISSUES=0
_checks=0
_pass=0
_fail=0

check() {
  local name="$1"
  local key="$2"
  local file_prefix="${3:-}"
  local optional="${4:-false}"

  _checks=$(( _checks + 1 ))

  local val=""
  val=$(secrets_get "$key" "$file_prefix" 2>/dev/null) || true

  if [[ -z "$val" ]]; then
    if [[ "$optional" == "true" ]]; then
      echo "⊘ $name: not set (optional)"
      return 0
    else
      echo "⚠️  $name: not set"
      _fail=$(( _fail + 1 ))
      ISSUES=1
      return 1
    fi
  fi

  # Validate format (key should be >10 chars for real API keys)
  if [[ ${#val} -lt 10 ]]; then
    echo "⚠️  $name: invalid (${val:0:6}... too short)"
    _fail=$(( _fail + 1 ))
    ISSUES=1
    return 1
  fi

  echo "✓ $name: set (${val:0:8}...)"
  _pass=$(( _pass + 1 ))
  return 0
}

echo "API Keys ($(hostname)):"

# Core keys (required for daily use)
check "ZAI_API_KEY"       "ZAI_API_KEY"       "research_keys" "false"
check "TAVILY_API_KEY"   "TAVILY_API_KEY"   "research_keys" "true"
check "EXA_API_KEY"      "EXA_API_KEY"      "research_keys" "true"
check "APIFY_TOKEN"      "APIFY_TOKEN"      "research_keys" "true"
check "CONTEXT7_API_KEY" "CONTEXT7_API_KEY" "research_keys" "true"

echo ""
echo "  $_pass/$_checks passed${_fail:+, $_fail issues}"

exit $ISSUES
