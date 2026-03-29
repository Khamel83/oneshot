# Task 3: Strip Plaintext Keys from Project .env Files

## Context
Task 2 moved all keys into the vault. Now we remove plaintext copies from project `.env` files.

**CRITICAL (from adversarial review)**: Do NOT replace values with `VAULT:secrets.get.KEY` strings. Standard env parsers (dotenv, docker-compose, Node) do NOT resolve custom URI schemes. Instead, blank the secret values and add a comment pointing to the vault.

**Prerequisites**: Task 2 complete (all keys in vault)
**Depends on**: Task 2
**Blocks**: Task 4

---

## What To Do

### For each active project, modify .env in-place:

**Pattern**:
```bash
# Before
OPENROUTER_API_KEY=sk-or-v1-abc123def456

# After
OPENROUTER_API_KEY=
# ^ vault: secrets get OPENROUTER_API_KEY
```

### Active projects to strip

| Project | File | Keys to blank |
|---------|------|---------------|
| atlas | `~/github/atlas/.env` | ATLAS_API_KEY, OPENROUTER_API_KEY, GMAIL_APP_PASSWORD |
| arb | `~/github/arb/detection-service/.env` | TELEGRAM_BOT_TOKEN, UPSTASH_REDIS_REST_TOKEN, POLYMARKET_PRIVATE_KEY, DUNE_API_KEY, NORDVPN_PRIVATE_KEY |
| networth | `~/github/networth/.env` | SUPABASE_DB_PASSWORD, VERCEL_TOKEN, PLAYER_PASSWORD |
| poytz | `~/github/poytz/.env` | CLOUDFLARE_API_TOKEN |
| boys | `~/github/boys/.env` | TELEGRAM_BOT_TOKEN |
| dada | `~/github/dada/.env` + `dada/vercel-deploy/.env` | TELEGRAM_BOT_TOKEN, DROPBOX_ACCESS_TOKEN, GOOGLE_CREDENTIALS_FILE |
| trojan-research | `~/github/trojan-research/.env` | DEEPSEEK_API_KEY, TAVILY_API_KEY |
| front-door-web | `~/github/front-door-web/.env` | ZAI_API_KEY |

### Dormant projects — keep non-secret lines, blank secrets

**atlas-voice** (`~/github/atlas-voice/.env`):
```bash
# Keep any PORT, NODE_ENV, DB_HOST lines
# Blank: PERPLEXITY_API_KEY, OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN
```

**Notary** (`~/github/Notary/.env`):
```bash
# Blank: NEXTAUTH_SECRET, STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
# Keep any non-secret config
```

**529** (`~/github/529/.env`):
```bash
# Blank: GAMMA_API_KEY
# Keep non-secret config
```

### Utility repos — delete .env entirely

| Project | Reason |
|---------|--------|
| docs-cache | Keys already in vault, all duplicates |
| anthropic-api-demo | Key already in vault, pure duplicate |

### Infra projects — NO CHANGE

| Project | Reason |
|---------|--------|
| penny | docker-compose reads .env directly. Vault is backup only. |
| homelab | docker-compose reads .env directly. Vault is backup only. |

---

## DO NOT
- Replace values with `VAULT:...` reference strings (apps will break)
- Delete .env files that contain non-secret config without preserving those lines
- Touch penny/.env or homelab/.env
- Commit keys to git history (use `git diff` to verify only blanks are committed)

## After stripping
For each modified project, run `git diff .env` to confirm only secret values were changed (blanked).

## Deliverable
All active/dormant project .env files cleaned. No plaintext secrets remain outside penny/ and homelab/.
