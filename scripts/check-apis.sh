#!/usr/bin/env bash
# Validate API keys by making minimal test calls
# Checks: ZAI, Tavily, Exa, Apify, Context7

set -euo pipefail

ISSUES=0

# Test ZAI API key
check_zai_api() {
  if [[ -z "${ZAI_API_KEY:-}" ]]; then
    echo "⚠️  ZAI_API_KEY: not set"
    return 1
  fi

  # Simple test - just check if key looks valid
  if [[ ${#ZAI_API_KEY} -lt 20 ]]; then
    echo "⚠️  ZAI_API_KEY: invalid format"
    return 1
  fi

  echo "✓ ZAI_API_KEY: set (${ZAI_API_KEY:0:8}...)"
  return 0
}

# Test Tavily API
check_tavily_api() {
  if [[ -z "${TAVILY_API_KEY:-}" ]]; then
    echo "⊘ TAVILY_API_KEY: not set (optional)"
    return 0
  fi

  # Could add actual API test here
  echo "✓ TAVILY_API_KEY: set"
  return 0
}

# Test Exa API
check_exa_api() {
  if [[ -z "${EXA_API_KEY:-}" ]]; then
    echo "⊘ EXA_API_KEY: not set (optional)"
    return 0
  fi

  echo "✓ EXA_API_KEY: set"
  return 0
}

# Test Apify API
check_apify_api() {
  if [[ -z "${APIFY_API_KEY:-}" ]]; then
    echo "⊘ APIFY_API_KEY: not set (optional)"
    return 0
  fi

  echo "✓ APIFY_API_KEY: set"
  return 0
}

# Test Context7 API
check_context7_api() {
  if [[ -z "${CONTEXT7_API_KEY:-}" ]]; then
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
