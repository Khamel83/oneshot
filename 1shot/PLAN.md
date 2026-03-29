# Vault Consolidation Plan

**Goal**: Reconcile all API keys across oci-dev into the oneshot secrets vault. Remove plaintext secrets from project `.env` files. Verify nothing breaks.

**Source**: Recovered from session `7f1472f9` (ran out of context before execution). User approved this plan before `/clear`.

---

## Current State

### Vault (source of truth) — 13 files, ~50 keys
| File | Keys | Status |
|------|------|--------|
| `research_keys.env` | ZAI, TAVILY, EXA, APIFY, CONTEXT7 | Active (Exa credits exhausted) |
| `secrets.env` | DB_*, JWT, STRIPE, CF_*, GITHUB_PAT, OPENROUTER, EMAIL_*, REDIS_URL | Active |
| `gmail.env` | GMAIL_CREDENTIALS_B64, GMAIL_TOKEN_B64, GMAIL_PROJECT, GMAIL_ACCOUNT | Active |
| `convex.env` | CONVEX_TEAM_ACCESS_TOKEN, CONVEX_TEAM_ID | Active |
| `convex_deploy.env` | CONVEX_DEPLOY_KEY, CONVEX_DEPLOYMENT_URL | Active |
| `openclaw.env` | BRAVE_API_KEY, TELEGRAM_BOT_TOKEN, OPENCLAW_GATEWAY_TOKEN | Active |
| `penny.env` | OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID | Active |
| `api.env` | JINA_API_KEY | Active |
| `skillsmp.env` | SKILLSMP_API_KEY | Active |
| `cloudflare.env` | CLOUDFLARE_HYPERDRIVE_ID | Active |
| `homelab.env` | *(empty)* | Needs cleanup |
| `research.env` | *(empty)* | Needs cleanup |
| `research_keys.json` | *(empty)* | Needs cleanup |

### Plaintext keys in project `.env` files — 78+ keys across 14 projects

**Active projects (modified within 30 days):**
| Project | Last Activity | Keys at Risk | Notes |
|---------|--------------|--------------|-------|
| atlas | 82 min ago | GMAIL_APP_PASSWORD, ATLAS_API_KEY, OPENROUTER_API_KEY | Active dev |
| arb | 82 min ago | TELEGRAM_BOT_TOKEN, UPSTASH_REDIS_REST_TOKEN, POLYMARKET_PRIVATE_KEY, DUNE_API_KEY, NORDVPN_PRIVATE_KEY | Active dev |
| networth | 82 min ago | SUPABASE_DB_PASSWORD, VERCEL_TOKEN, PLAYER_PASSWORD | Active dev |
| poytz | 6 days ago | CLOUDFLARE_API_TOKEN | Active dev |
| boys | 3 weeks ago | TELEGRAM_BOT_TOKEN | Low activity |
| dada | 11 days ago | TELEGRAM_BOT_TOKEN, DROPBOX_ACCESS_TOKEN, GOOGLE_CREDENTIALS_FILE | Low activity |
| kid-friendly-ai | 3 days ago | (none found) | Active dev |
| trojan-research | 4 weeks ago | DEEPSEEK_API_KEY, TAVILY_API_KEY | Low activity |

**Dormant projects (2+ months):**
| Project | Last Activity | Keys at Risk | Action |
|---------|--------------|--------------|--------|
| atlas-voice | 4 months | PERPLEXITY_API_KEY, OPENROUTER_API_KEY, TELEGRAM_BOT_TOKEN | Archive |
| Notary | 4 months | NEXTAUTH_SECRET, STRIPE_*, GOOGLE_MAPS_API_KEY | Archive |
| 529 | 3 months | GAMMA_API_KEY | Archive |

**Infra projects (running services):**
| Project | Keys at Risk | Notes |
|---------|--------------|-------|
| penny | 32 keys | Homelab dashboard config, docker-compose reads `.env` directly |
| homelab | 29 keys | Core infra, docker-compose reads `.env` directly |
| front-door-web | ZAI_API_KEY | Small |

**Utility repos:**
| Project | Keys at Risk | Notes |
|---------|--------------|-------|
| docs-cache | EXA_API_KEY, JINA_API_KEY | Already in vault — pure duplicate |
| anthropic-api-demo | OPENROUTER_API_KEY | Already in vault — pure duplicate |

### Duplicate key analysis
| Key | Locations (vault + plaintext) |
|-----|-----|
| TELEGRAM_BOT_TOKEN | vault (openclaw, penny), penny/.env, homelab/.env, arb/.env, dada/.env, boys/.env, atlas-voice/.env |
| OPENROUTER_API_KEY | vault (secrets, penny), atlas-voice/.env, atlas/.env, penny/.env |
| CLOUDFLARE_API_TOKEN | vault (secrets), poytz/.env, penny/.env |
| ZAI_API_KEY | vault (research_keys), penny/.env, front-door-web/.env |
| TAVILY_API_KEY | vault (research_keys), trojan-research/.env |
| EXA_API_KEY | vault (research_keys), docs-cache/.env |
| JINA_API_KEY | vault (api), docs-cache/.env |

---

## Phase 1: Validate (task1.md)

**Goal**: Test every key, identify dead ones, know what's worth saving.

### Steps
1. For each key in the vault, make a real API call to verify it works
2. For each plaintext key in project `.env` files, check if it already exists in vault (dedup)
3. Identify keys that are clearly dead (expired, revoked, credits exhausted)
4. Categorize remaining unvaulted keys by where they should go

### Deliverables
- Validation results table (key, status, vault file, action)
- List of keys to vault (new additions)
- List of keys to skip (dead, project-specific, or not useful)

### Scope
- Read-only: no changes to any files
- Uses: `secrets get KEY`, curl to API endpoints, grep

---

## Phase 2: Consolidate (task2.md)

**Goal**: Move all valid keys into the vault. Create new vault files where needed.

### New vault files to create
| File | Keys | Reason |
|------|------|--------|
| `deployments.env` | VERCEL_TOKEN, NEXTAUTH_SECRET, SUPABASE_DB_PASSWORD, PLAYER_PASSWORD | Deployment/infra keys |
| `arb.env` | POLYMARKET_PRIVATE_KEY, DUNE_API_KEY, DISCORD_WEBHOOK_URL, UPSTASH_REDIS_REST_TOKEN | Project-specific |
| `homelab_backup.env` | RADARR_API_KEY, SONARR_API_KEY, PROWLARR_API_KEY, LIDARR_API_KEY, BAZARR_API_KEY, WHISPARR_API_KEY, TMDB_API_KEY, TMDB_READ_ACCESS_TOKEN, AUTHENTIK_*, CLOUDFLARE_TUNNEL_TOKEN, CLOUDFLARE_API_KEY, TAILSCALE_API_KEY | Backup of homelab infra |
| `services.env` | PERPLEXITY_API_KEY, DEEPSEEK_API_KEY, GAMMA_API_KEY, DROPBOX_ACCESS_TOKEN, GOOGLE_CREDENTIALS_FILE, ATLAS_API_KEY, GMAIL_APP_PASSWORD | Service-specific |

### Existing vault files to update
- `research_keys.env` — verify all 5 keys current
- `secrets.env` — add VERCEL_TOKEN if not present

### Cleanup
- Delete empty files: `homelab.env.encrypted`, `research.env.encrypted`, `research_keys.json.encrypted`

### Scope
- Write to: `~/github/oneshot/secrets/`
- Uses: `secrets set <file> 'KEY=value'` for each new key
- Each `secrets set` auto-prompts commit+push

---

## Phase 3: Strip (task3.md)

**Goal**: Remove plaintext secrets from project `.env` files. Keep non-sensitive config.

### Active projects — replace values with vault references
| Project | Action |
|---------|--------|
| atlas | Strip OPENROUTER_API_KEY, GMAIL_APP_PASSWORD, ATLAS_API_KEY |
| arb | Strip TELEGRAM_BOT_TOKEN, UPSTASH_REDIS_REST_TOKEN, POLYMARKET_PRIVATE_KEY, DUNE_API_KEY, NORDVPN_PRIVATE_KEY |
| networth | Strip SUPABASE_DB_PASSWORD, VERCEL_TOKEN, PLAYER_PASSWORD |
| poytz | Strip CLOUDFLARE_API_TOKEN |
| boys | Strip TELEGRAM_BOT_TOKEN |
| dada | Strip TELEGRAM_BOT_TOKEN, DROPBOX_ACCESS_TOKEN, GOOGLE_CREDENTIALS_FILE |
| trojan-research | Strip DEEPSEEK_API_KEY, TAVILY_API_KEY |
| front-door-web | Strip ZAI_API_KEY |

### Dormant projects — archive
| Project | Action |
|---------|--------|
| atlas-voice | Delete `.env` entirely (project dormant 4 months) |
| Notary | Delete `.env` entirely (project dormant 4 months) |
| 529 | Delete `.env` entirely (project dormant 3 months) |

### Utility repos — delete .env
| Project | Action |
|---------|--------|
| docs-cache | Delete `.env` (keys already in vault, all duplicates) |
| anthropic-api-demo | Delete `.env` (key already in vault, pure duplicate) |

### Infra projects — NO CHANGE
| Project | Reason |
|---------|--------|
| penny | docker-compose reads `.env` directly; vault is backup only |
| homelab | docker-compose reads `.env` directly; vault is backup only |

### Key rule: `.env` file handling
For active projects, replace secret values in-place:
```
# Before
OPENROUTER_API_KEY=sk-or-v1-abc123...

# After
OPENROUTER_API_KEY=VAULT:secrets.get.OPENROUTER_API_KEY
```

This way developers know to use `secrets get` but the file still exists for non-secret config.

### Scope
- Write to: `~/github/{project}/.env` for each active project
- Destructive: delete `.env` for dormant/utility projects (confirmed by user in previous session)
- Infra projects (penny, homelab): read-only backup to vault only

---

## Phase 4: Cleanup (task4.md)

**Goal**: Remove redundant key exports and leftover files.

### Steps
1. Check `~/.bashrc` for any remaining `export API_KEY=...` lines — remove if redundant with vault
2. Check `~/.zshrc`, `~/.zshenv`, `~/.profile` for same
3. Verify no keys are in `/etc/environment` or systemd env files that shouldn't be
4. Confirm all 3 vault cleanup files deleted (homelab.env, research.env, research_keys.json)

### Scope
- Write to: `~/.bashrc`, `~/.zshrc`, `~/.profile` (oci-dev only)
- Delete: 3 empty vault files

---

## Phase 5: Verify (task5.md)

**Goal**: Confirm no plaintext keys remain, everything still works.

### Leak check
```bash
# Grep for any remaining plaintext API keys outside vault
grep -rn 'sk-\|sk_or-\|ghp_\|tvly-\|ctx7sk-\|pat_\|AIza\|xoxb-\|ACT-' \
  ~/github --include="*.env" --include="*.json" --include="*.yaml" --include="*.yml" \
  --exclude-dir=oneshot/secrets --exclude-dir=.git
```

### Functionality check
1. Run heartbeat on oci-dev: `~/github/oneshot/scripts/heartbeat.sh`
2. Spot-check `secrets get ZAI_API_KEY` returns valid value
3. Spot-check `secrets get TAVILY_API_KEY` returns valid value
4. Verify no running services broke (check systemd status)

### Cross-machine sync
1. `cd ~/github/oneshot && git push` (vault changes)
2. SSH to homelab: `cd ~/github/oneshot && git pull` (verify vault pulls clean)
3. SSH to macmini: same

### Scope
- Read-only verification (no writes)
- May require SSH to homelab and macmini

---

## Risk Assessment

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| Service breaks after stripping .env | Medium | Only strip active projects; keep vault references; infra projects untouched |
| Lose a key that wasn't in vault | Low | Phase 1 validates ALL keys before any deletion |
| Git history contains plaintext keys | Medium | Out of scope for this plan (separate `git filter-branch` effort) |
| Homelab/macmini can't decrypt new vault files | Low | They share the same age key; test on pull |

---

## Adversarial Review (Gemini)

### CRITICAL
1. **`VAULT:secrets.get.KEY` placeholder will break apps** — Standard env parsers (dotenv, docker-compose, Node) do NOT resolve custom URI schemes. They'll pass the literal string to the app, causing auth failures.
   - **Fix**: Phase 3 must NOT replace values with reference strings. Instead, blank the values (keep the key name, empty value) and add a comment pointing to the vault. Apps that need the key at runtime should use `source <(secrets env <file>)` in their startup script, or `.env` should be generated from vault at deploy time.

2. **Blind API validation is dangerous** — Generic `curl` calls against 80+ services could hit mutating endpoints, trigger rate limits, or cause charges (especially STRIPE, POLYMARKET_PRIVATE_KEY). You can't "validate" a DB password or crypto key with a simple API call.
   - **Fix**: Only validate API-style keys (ZAI, Tavily, Context7, Exa, etc.). For passwords and private keys, skip validation — just copy to vault.

### HIGH
3. **75% of plaintext keys untouched** — penny (32) and homelab (29) = 61 keys left in plaintext. The vault consolidation covers only ~20% of the actual attack surface.
   - **Fix**: Accept as Phase 0 finding. Full docker-compose migration is a separate project. Document as known gap.

4. **Git history still contains all keys** — Removing plaintext from working tree while git history has them is security theater.
   - **Fix**: Add Phase 6 (separate task): `git filter-repo` to scrub history for all repos that had keys committed. OR accept the risk and document it.

5. **Deleting dormant project `.env` files breaks non-secret config** — `.env` files often contain PORT, NODE_ENV, DB_HOST (non-sensitive). Deleting the file kills the project.
   - **Fix**: Before deleting, extract non-secret lines and keep them. Only remove the secret values.

### MEDIUM
6. **50-80 individual git commits** from `secrets set` is git spam.
   - **Fix**: Batch all new keys into a single sops edit + one commit.

7. **Age key security not addressed** — If `~/.config/sops/age/keys.txt` is world-readable or in a backup, the vault is useless.
   - **Fix**: Add to Phase 4 — verify age key permissions are 600, owner-only.

### LOW
8. **Don't delete empty vault files** — `homelab.env.encrypted` will be needed when we eventually migrate docker-compose.
   - **Fix**: Keep them, just leave empty. Remove from cleanup list.

---

## Revised Phase Strategy (Post-Review)

| Phase | Change |
|-------|--------|
| Phase 1 | Only validate API-style keys (not passwords/private keys). Skip SUPABASE_DB_PASSWORD, POLYMARKET_PRIVATE_KEY, DB_PASSWORD, etc. |
| Phase 2 | Batch all vault additions into single commit. Don't delete empty vault files. |
| Phase 3 | Do NOT use `VAULT:...` placeholders. Instead: blank values + comment. Keep non-secret lines in dormant projects. |
| Phase 4 | Add age key permission check. |
| Phase 5 | Unchanged. |
| Phase 6 (NEW) | Git history scrub — separate task, assess per-repo. |

---

## Codex Fix

**Problem**: Codex inherits `OPENAI_BASE_URL=https://api.z.ai/api/coding/paas/v4` from the `zai()` shell wrapper. This routes Codex's OpenAI calls through ZAI's proxy, which doesn't support the Codex WebSocket protocol (401).

**Solution**: Codex uses its own OAuth-based auth (stored in `~/.codex/auth.json`). It needs to connect directly to `api.openai.com`. Fix:
1. Add `openai_base_url = "https://api.openai.com"` to `~/.codex/config.toml`
2. Or run Codex with `env -u OPENAI_BASE_URL codex ...`
3. The `zai()` function in `.bashrc` should NOT set `OPENAI_BASE_URL` globally — it's scoped correctly (inline), but any shell spawned FROM a zai session inherits it.

---

## Out of Scope
- Git history scrubbing (Phase 6, separate task)
- Migrating docker-compose services from `.env` to vault-based runtime injection
- Changing how docker-compose reads secrets
- Adding new API keys
- Codex provider setup (tracked separately)
