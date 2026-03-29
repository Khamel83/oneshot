#!/usr/bin/env bash
# Validate API keys with actual test calls + usage info
# Checks: ZAI, Tavily, Exa, Apify, Context7, OpenAI, OpenRouter,
#         DeepSeek, Brave, Jina, GitHub, Cloudflare, Telegram
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
    local model
    model=$(echo "$body" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('model','unknown'))" 2>/dev/null || echo "unknown")
    echo "  ✓ Key active — $model"
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

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    "https://api.tavily.com/search" -H "Content-Type: application/json" \
    -d "{\"api_key\":\"$key\",\"query\":\"test\",\"max_results\":1}" 2>/dev/null)

  if [[ "$http_code" == "200" ]]; then
    echo "  ✓ Key active"
  elif [[ "$http_code" == "401" ]]; then
    echo "  ⚠️  HTTP 401 — invalid key"
    ISSUES=1
  elif [[ "$http_code" == "402" ]]; then
    echo "  ⚠️  HTTP 402 — credits exhausted"
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

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    "https://api.exa.ai/search" -H "x-api-key: $key" \
    -H "Content-Type: application/json" -d "{\"query\":\"test\",\"numResults\":1}" 2>/dev/null)

  if [[ "$http_code" == "200" ]]; then
    echo "  ✓ Key active"
  elif [[ "$http_code" == "402" ]]; then
    echo "  ⊘ Credits exhausted (top up at exa.ai when needed)"
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

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    "https://api.apify.com/v2/actor-runs" -H "Authorization: Bearer $key" 2>/dev/null)

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

  if [[ "$key" != ctx7sk-* ]]; then
    echo "  ⚠️  Key format outdated (needs ctx7sk- prefix)"
    ISSUES=1
    return
  fi

  echo "  ✓ Key format valid (ctx7sk-...)"
}

# ─── OpenAI ──────────────────────────────────────────────────────────────────
check_openai() {
  check "OpenAI"

  local key
  key=$(secrets_get "OPENAI_API_KEY" "research_keys" 2>/dev/null) || true
  if [[ -z "$key" ]]; then
    echo "  ⊘ Not set"
    return
  fi

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    "https://api.openai.com/v1/models" -H "Authorization: Bearer $key" 2>/dev/null)

  if [[ "$http_code" == "200" ]]; then
    echo "  ✓ Key active"
  else
    echo "  ⚠️  HTTP $http_code — key may be invalid"
    ISSUES=1
  fi
}

# ─── OpenRouter ───────────────────────────────────────────────────────────────
check_openrouter() {
  check "OpenRouter"

  local key
  key=$(secrets_get "OPENROUTER_API_KEY" 2>/dev/null) || true
  if [[ -z "$key" ]]; then
    echo "  ⊘ Not set"
    return
  fi

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    "https://openrouter.ai/api/v1/models" -H "Authorization: Bearer $key" 2>/dev/null)

  if [[ "$http_code" == "200" ]]; then
    echo "  ✓ Key active"
  elif [[ "$http_code" == "401" ]]; then
    echo "  ⚠️  HTTP 401 — invalid key"
    ISSUES=1
  else
    echo "  ⚠️  HTTP $http_code"
    ISSUES=1
  fi
}

# ─── DeepSeek ─────────────────────────────────────────────────────────────────
check_deepseek() {
  check "DeepSeek" "true"

  local key
  key=$(secrets_get "DEEPSEEK_API_KEY" "services" 2>/dev/null) || true
  if [[ -z "$key" ]]; then
    echo "  ⊘ Not set (optional)"
    return
  fi

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    "https://api.deepseek.com/v1/models" -H "Authorization: Bearer $key" 2>/dev/null)

  if [[ "$http_code" == "200" ]]; then
    echo "  ✓ Key active"
  elif [[ "$http_code" == "401" ]]; then
    echo "  ⚠️  HTTP 401 — invalid key"
    ISSUES=1
  else
    echo "  ⚠️  HTTP $http_code"
    ISSUES=1
  fi
}

# ─── Brave Search ──────────────────────────────────────────────────────────────
check_brave() {
  check "Brave Search" "true"

  local key
  key=$(secrets_get "BRAVE_API_KEY" "openclaw" 2>/dev/null) || true
  if [[ -z "$key" ]]; then
    echo "  ⊘ Not set (optional)"
    return
  fi

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    "https://api.search.brave.com/res/v1/web/search?q=test" \
    -H "Accept: application/json" -H "X-Subscription-Token: $key" 2>/dev/null)

  if [[ "$http_code" == "200" ]]; then
    echo "  ✓ Key active"
  elif [[ "$http_code" == "401" ]]; then
    echo "  ⚠️  HTTP 401 — invalid key"
    ISSUES=1
  else
    echo "  ⚠️  HTTP $http_code"
    ISSUES=1
  fi
}

# ─── Jina ─────────────────────────────────────────────────────────────────────
check_jina() {
  check "Jina" "true"

  local key
  key=$(secrets_get "JINA_API_KEY" "api" 2>/dev/null) || true
  if [[ -z "$key" ]]; then
    echo "  ⊘ Not set (optional)"
    return
  fi

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    "https://api.jina.ai/v1/embeddings" -H "Authorization: Bearer $key" 2>/dev/null)

  # 405 = auth ok, POST required (expected for GET)
  if [[ "$http_code" == "200" || "$http_code" == "405" ]]; then
    echo "  ✓ Key active"
  elif [[ "$http_code" == "401" ]]; then
    echo "  ⚠️  HTTP 401 — invalid key"
    ISSUES=1
  else
    echo "  ⚠️  HTTP $http_code"
    ISSUES=1
  fi
}

# ─── GitHub PAT ───────────────────────────────────────────────────────────────
check_github() {
  check "GitHub PAT"

  local key
  key=$(secrets_get "GITHUB_PAT" 2>/dev/null) || true
  if [[ -z "$key" ]]; then
    echo "  ⊘ Not set"
    return
  fi

  local http_code user
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    "https://api.github.com/user" -H "Authorization: Bearer $key" 2>/dev/null)
  user=$(curl -s --max-time 10 "https://api.github.com/user" \
    -H "Authorization: Bearer $key" 2>/dev/null \
    | python3 -c "import sys,json;print(json.load(sys.stdin).get('login','?'))" 2>/dev/null || echo "?")

  if [[ "$http_code" == "200" ]]; then
    echo "  ✓ Key active ($user)"
  elif [[ "$http_code" == "401" ]]; then
    echo "  ⚠️  HTTP 401 — invalid or expired"
    ISSUES=1
  else
    echo "  ⚠️  HTTP $http_code"
    ISSUES=1
  fi
}

# ─── Cloudflare ───────────────────────────────────────────────────────────────
check_cloudflare() {
  check "Cloudflare API"

  local key
  key=$(secrets_get "CLOUDFLARE_API_TOKEN" 2>/dev/null) || true
  if [[ -z "$key" ]]; then
    echo "  ⊘ Not set"
    return
  fi

  local http_code
  http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
    "https://api.cloudflare.com/client/v4/user/tokens/verify" -H "Authorization: Bearer $key" 2>/dev/null)

  if [[ "$http_code" == "200" ]]; then
    echo "  ✓ Key active"
  else
    echo "  ⚠️  HTTP $http_code — token may be expired"
    ISSUES=1
  fi
}

# ─── Telegram Bots ────────────────────────────────────────────────────────────
check_telegram() {
  check "Telegram Bots"

  local checked=0
  for prefix in openclaw penny; do
    local key
    key=$(secrets_get "TELEGRAM_BOT_TOKEN" "$prefix" 2>/dev/null) || true
    [[ -z "$key" ]] && continue

    local bot
    bot=$(curl -s --max-time 10 "https://api.telegram.org/bot$key/getMe" 2>/dev/null \
      | python3 -c "import sys,json;d=json.load(sys.stdin);print(f'@{d[\"result\"][\"username\"]}')" 2>/dev/null || true)
    [[ -z "$bot" ]] && { echo "  ⚠️  $prefix bot — invalid"; ISSUES=1; continue; }

    echo "  ✓ $bot ($prefix)"
    checked=$((checked + 1))
  done

  [[ $checked -eq 0 ]] && echo "  ⊘ No bots configured"
}

# ─── Run all checks ─────────────────────────────────────────────────────────

_is_validated_key() {
  case "$1" in
    ZAI_API_KEY|TAVILY_API_KEY|EXA_API_KEY|APIFY_TOKEN|CONTEXT7_API_KEY \
    |OPENAI_API_KEY|OPENROUTER_API_KEY|DEEPSEEK_API_KEY|BRAVE_API_KEY \
    |JINA_API_KEY|GITHUB_PAT|CLOUDFLARE_API_TOKEN|TELEGRAM_BOT_TOKEN \
    |TELEGRAM_BOT_TOKEN_BOYS|TELEGRAM_BOT_TOKEN_DADA|TELEGRAM_BOT_TOKEN_ATLAS_VOICE) return 0 ;;
    *) return 1 ;;
  esac
}

check_zai
check_tavily
check_exa
check_apify
check_context7
check_openai
check_openrouter
check_deepseek
check_brave
check_jina
check_github
check_cloudflare
check_telegram

exit $ISSUES
