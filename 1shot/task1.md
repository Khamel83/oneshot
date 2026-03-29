# Task 1: Validate All Keys

## Context
We're consolidating ~80+ plaintext API keys scattered across 14 project `.env` files into the oneshot encrypted vault (`~/github/oneshot/secrets/`). This is the first step — validate everything before touching anything.

**Prerequisites**: None. This is read-only.

**Depends on**: Nothing
**Blocks**: Task 2, Task 3

---

## What To Do

### 1. Validate vault keys (API-style only)
For each key that has a real API endpoint, test it with a lightweight read-only call:

```bash
# ZAI (GLM)
ZAI_KEY=$(secrets get ZAI_API_KEY)
curl -s "https://api.z.ai/v1/models" -H "Authorization: Bearer $ZAI_KEY" | head -c 200

# Tavily
TAVILY_KEY=$(secrets get TAVILY_API_KEY)
curl -s "https://api.tavily.com/search" -H "Content-Type: application/json" \
  -d '{"api_key":"'"$TAVILY_KEY"'","query":"test","max_results":1}' | head -c 200

# Context7
CTX7_KEY=$(secrets get CONTEXT7_API_KEY)
curl -s "https://context7.com/api/v1/query" -H "x-api-key: $CTX7_KEY" | head -c 200

# Exa (expect 402 — credits exhausted)
EXA_KEY=$(secrets get EXA_API_KEY)
curl -s -o /dev/null -w "%{http_code}" "https://api.exa.ai/search" -H "x-api-key: $EXA_KEY"

# Jina
JINA_KEY=$(secrets get JINA_API_KEY)
curl -s -o /dev/null -w "%{http_code}" "https://api.jina.ai/v1/embeddings" -H "Authorization: Bearer $JINA_KEY"

# Apify
APIFY_KEY=$(secrets get APIFY_TOKEN)
curl -s -o /dev/null -w "%{http_code}" "https://api.apify.com/v2/acts" -H "Authorization: Bearer $APIFY_KEY"
```

### 2. Inventory plaintext keys in project .env files
Already done (see PLAN.md "Current State" section). Key findings:
- **Active projects** (8): atlas, arb, networth, poytz, boys, dada, kid-friendly-ai, trojan-research
- **Dormant projects** (3): atlas-voice, Notary, 529
- **Infra projects** (3): penny, homelab, front-door-web
- **Utility repos** (2): docs-cache, anthropic-api-demo

### 3. Categorize unvaulted keys
For each plaintext key, determine:
- Already in vault? → skip (it's a duplicate)
- API-style key? → validate, then vault
- Password/private key? → skip validation, just vault

### 4. Build the consolidation matrix

Create a table like:
| Key | Source Project | Target Vault File | Action |
|-----|---------------|-------------------|--------|
| OPENROUTER_API_KEY | atlas, atlas-voice, penny/.env | Already in secrets.env | Skip (dedup) |
| ATLAS_API_KEY | atlas/.env | services.env (new) | Vault |
| DEEPSEEK_API_KEY | trojan-research/.env | services.env (new) | Vault |
| ... | ... | ... | ... |

---

## DO NOT
- Modify any files
- Run `secrets set` yet
- Try to validate passwords, private keys, or DB credentials with API calls
- Touch penny/.env or homelab/.env (infra projects, out of scope)

## Deliverable
A completed categorization table of every key found, with target vault file and action.
