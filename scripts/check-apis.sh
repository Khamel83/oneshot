#!/usr/bin/env bash
# Validate API keys with actual test calls + usage info
# Checks: ZAI, Tavily, Exa, Apify, Context7
# Usage: ./check-apis.sh [--fix]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/secrets-helper.sh"

ISSUES=0

check() {
  local name="$1"
  local optional="${2:-false}"

  if [[ "$optional" == "true" ]]; then
    echo "── $name (optional) ──"
  else
    echo "── $name ──"
  fi
}

# ─── ZAI (GLM Coding Plan) ─────────────────────────────────────────────────
check_zai() {
  check "ZAI (GLM Coding Plan)"

  local key="${ZAI_API_KEY:-}"
  if [[ -z "$key" ]]; then
    key=$(secrets_get "ZAI_API_KEY" "research_keys" 2>/dev/null) || true
  fi
  if [[ -z "$key" ]]; then
    echo "  ⚠️  Key not set"
    ISSUES=1
    return
  fi

  # Test: call ZAI chat completions with minimal request
  local resp
  resp=$(curl -s -w "\n%{http_code}" "https://api.z.ai/api/anthropic/v1/messages" \
    -H "Content-Type: application/json" \
    -H "x-api-key: $key" \
    -H "anthropic-version: 2023-06-01" \
    -d '{"model":"glm-5-turbo","max_tokens":5,"messages":[{"role":"user","content":"hi"}]}' 2>/dev/null)

  local http_code
  http_code=$(echo "$resp" | tail -1)
  local body
  body=$(echo "$resp" | sed '$d')

  if [[ "$http_code" == "200" ]]; then
    echo "  ✓ Key active — API responding"
    # Try to get model from response
    local model
    model=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('model','unknown'))" 2>/dev/null || echo "unknown")
    echo "    Model: $model"
  elif [[ "$http_code" == "429" ]]; then
    echo "  ⚠️  Key valid — rate limited (429)"
    ISSUES=1
  else
    echo "  ⚠️  HTTP $http_code — may be invalid or expired"
    ISSUES=1
  fi
}

# ─── Tavily ───────────────────────────────────────────────────────────────────
check_tavily() {
  check "Tavily" "true"

  local key
  key=$(secrets_get "TAVILY_API_KEY" "research_keys" 2>/dev/null) || true
  if [[ -z "$key" ]]; then
    echo "  ⊘ Not set (optional)"
    return
  fi

  local resp
  resp=$(curl -s -w "\n%{http_code}" "https://api.tavily.com/search" \
    -H "Content-Type: application/json" \
    -d "{\"api_key\":\"$key\",\"query\":\"test\",\"max_results\":1}" 2>/dev/null)

  local http_code
  http_code=$(echo "$resp" | tail -1)
  local body
  body=$(echo "$resp" | sed '$d')

  if [[ "$http_code" == "200" ]]; then
    echo "  ✓ Key active"
  elif [[ "$http_code" == "401" ]]; then
    echo "  ⚠️  HTTP 401 — invalid key"
    ISSUES=1
  elif [[ "$http_code" == "402" ]]; then
    echo "  ⚠️  HTTP 402 — credits exhausted (top up at exa.ai)"
    ISSUES=1
  else
    echo "  ⚠️  HTTP $http_code"
    ISSUES=1
  fi
}

# ─── Exa ────────────────────────────────────────────────────────────────────
check_exa() {
  check "Exa" "true"

  local key
  key=$(secrets_get "EXA_API_KEY" "research_keys" 2>/dev/null) || true
  if [[ -z "$key" ]]; then
    echo "  ⊘ Not set (optional)"
    return
  fi

  local resp
  resp=$(curl -s -w "\n%{http_code}" "https://api.exa.ai/search" \
    -H "x-api-key: $key" \
    -H "Content-Type: application/json" \
    -d "{\"query\":\"test\",\"numResults\":1}" 2>/dev/null)

  local http_code
  http_code=$(echo "$resp" | tail -1)

  if [[ "$http_code" == "200" ]]; then
    echo "  ✓ Key active"
  elif [[ "$http_code" == "402" ]]; then
    echo "  ⊘ Credits exhausted (top up at exa.ai when needed)"
    # Don't count as issue — it's optional and just needs a top-up
  elif [[ "$http_code" == "401" ]]; then
    echo "  ⚠️  HTTP 401 — invalid key"
    ISSUES=1
  else
    echo "  ⚠️  HTTP $http_code"
    ISSUES=1
  fi
}

# ─── Apify ───────────────────────────────────────────────────────────────────
check_apify() {
  check "Apify" "true"

  local key
  key=$(secrets_get "APIFY_TOKEN" "research_keys" 2>/dev/null) || true
  if [[ -z "$key" ]]; then
    echo "  ⊘ Not set (optional)"
    return
  fi

  local resp
  resp=$(curl -s -w "\n%{http_code}" "https://api.apify.com/v2/actor-runs" \
    -H "Authorization: Bearer $key" 2>/dev/null)

  local http_code
  http_code=$(echo "$resp" | tail -1)

  if [[ "$http_code" == "200" ]]; then
    echo "  ✓ Key active"
  elif [[ "$http_code" == "401" ]]; then
    echo "  ⚠️  HTTP 401 — key may be invalid"
    ISSUES=1
  else
    echo "  ⚠️  HTTP $http_code"
    ISSUES=1
  fi
}

# ─── Context7 ─────────────────────────────────────────────────────────────────
check_context7() {
  check "Context7" "true"

  local key
  key=$(secrets_get "CONTEXT7_API_KEY" "research_keys" 2>/dev/null) || true
  if [[ -z "$key" ]]; then
    echo "  ⊘ Not set (optional)"
    return
  fi

  # Check key format (Context7 requires ctx7sk- prefix)
  if [[ "$key" != ctx7sk-* ]]; then
    echo "  ⚠️  Key format outdated (needs ctx7sk- prefix, current: ${key:0:6}...)"
    echo "    Get new key at context7.com — old 'ctx7_' keys no longer work"
    ISSUES=1
    return
  fi

  # Context7 is a Claude plugin (context7@claude-plugins-official) — auth handled internally.
  # We can only validate the key format, not make a test API call.
  echo "  ✓ Key format valid (ctx7sk-...)"
}

# ─── Run all checks ─────────────────────────────────────────────────────────

# Known keys (handled above with real API tests)
declare -A KNOWN_KEYS=(
  [ZAI_API_KEY]=1 [TAVILY_API_KEY]=1 [EXA_API_KEY]=1
  [APIFY_TOKEN]=1 [CONTEXT7_API_KEY]=1
)

check_zai
check_tavily
check_exa
check_apify
check_context7

# Catch-all: any key in the vault we don't explicitly handle — format check only
echo "── Other Keys ──"
for file in "$ONESHOT_VAULT"/*.encrypted; do
  [ -f "$file" ] || continue
  while IFS='=' read -r key value; do
    [[ -z "$key" || "$key" == \#* ]] && continue
    [[ "${KNOWN_KEYS[$key]:-}" == "1" ]] && continue
    echo "  ✓ $key (${#value} chars)"
  done < <(_sops_decrypt "$file" 2>/dev/null || true)
done

exit $ISSUES
