# Task 2: Consolidate Keys Into Vault

## Context
Task 1 validated all keys and identified which ones need to move into the vault. This task moves them.

**Prerequisites**: Task 1 complete (validation table ready)
**Depends on**: Task 1
**Blocks**: Task 3, Task 4

---

## What To Do

### 1. Create new vault files using `secrets set`

Batch all keys into minimal commits. For each new vault file:

```bash
# services.env — service-specific keys
secrets set services 'PERPLEXITY_API_KEY=<value>'
secrets set services 'DEEPSEEK_API_KEY=<value>'
secrets set services 'GAMMA_API_KEY=<value>'
secrets set services 'DROPBOX_ACCESS_TOKEN=<value>'
secrets set services 'GOOGLE_CREDENTIALS_FILE=<value>'
secrets set services 'ATLAS_API_KEY=<value>'
secrets set services 'GMAIL_APP_PASSWORD=<value>'

# deployments.env — deployment/infra keys
secrets set deployments 'VERCEL_TOKEN=<value>'
secrets set deployments 'NEXTAUTH_SECRET=<value>'
secrets set deployments 'SUPABASE_DB_PASSWORD=<value>'
secrets set deployments 'PLAYER_PASSWORD=<value>'

# arb.env — project-specific
secrets set arb 'POLYMARKET_PRIVATE_KEY=<value>'
secrets set arb 'DUNE_API_KEY=<value>'
secrets set arb 'UPSTASH_REDIS_REST_TOKEN=<value>'
secrets set arb 'NORDVPN_PRIVATE_KEY=<value>'

# homelab_backup.env — backup of homelab infra (read-only reference)
secrets set homelab_backup 'RADARR_API_KEY=<value>'
secrets set homelab_backup 'SONARR_API_KEY=<value>'
# ... (all keys from homelab/.env)
```

### 2. Batching strategy
The `secrets set` command prompts for git commit+push after each key. To avoid 50+ commits:

**Option A**: Edit the encrypted file directly with `sops`, then commit once
```bash
sops -e <file> > ~/github/oneshot/secrets/<file>.encrypted
cd ~/github/oneshot && git add secrets/ && git commit -m "feat(secrets): add consolidated vault files"
```

**Option B**: Accept individual commits (the vault history is encrypted anyway)

### 3. Verify new vault files
After creating each file:
```bash
secrets list  # Should show all new files
secrets get PERPLEXITY_API_KEY  # Should return value
```

### 4. Cleanup (revised post-review)
- DO NOT delete empty vault files (`homelab.env`, `research.env`) — they'll be needed later
- Keep `research_keys.json.encrypted` (may be needed for JSON-format secrets)

---

## Keys to Vault (from Task 1 output)

### services.env (NEW)
| Key | Source |
|-----|--------|
| PERPLEXITY_API_KEY | atlas-voice/.env |
| DEEPSEEK_API_KEY | trojan-research/.env |
| GAMMA_API_KEY | 529/.env |
| DROPBOX_ACCESS_TOKEN | dada/.env |
| GOOGLE_CREDENTIALS_FILE | dada/.env (path reference) |
| ATLAS_API_KEY | atlas/.env |
| GMAIL_APP_PASSWORD | atlas/.env, penny/.env, homelab/.env |

### deployments.env (NEW)
| Key | Source |
|-----|--------|
| VERCEL_TOKEN | networth/.env |
| NEXTAUTH_SECRET | Notary/.env |
| SUPABASE_DB_PASSWORD | networth/.env |
| PLAYER_PASSWORD | networth/.env |

### arb.env (NEW)
| Key | Source |
|-----|--------|
| POLYMARKET_PRIVATE_KEY | arb/detection-service/.env |
| DUNE_API_KEY | arb/detection-service/.env |
| UPSTASH_REDIS_REST_TOKEN | arb/detection-service/.env |
| NORDVPN_PRIVATE_KEY | arb/detection-service/.env, penny/.env, homelab/.env |

### homelab_backup.env (NEW)
| Key | Source (all from homelab/.env or penny/.env) |
|-----|--------|
| RADARR_API_KEY, SONARR_API_KEY, PROWLARR_API_KEY | homelab/.env |
| LIDARR_API_KEY, BAZARR_API_KEY, WHISPARR_API_KEY | homelab/.env |
| TMDB_API_KEY, TMDB_READ_ACCESS_TOKEN | homelab/.env |
| AUTHENTIK_SECRET_KEY, AUTHENTIK_POSTGRES_PASSWORD | homelab/.env |
| AUTHENTIK_ADMIN_PASSWORD, CLOUDFLARE_TUNNEL_TOKEN | homelab/.env |
| CLOUDFLARE_API_KEY, TAILSCALE_API_KEY | homelab/.env |
| PIHOLE_WEBPASSWORD, PIHOLE_PASSWORD | homelab/.env |
| HOMEPAGE_ADMIN_PASSWORD | homelab/.env |
| POSTGRES_PASSWORD_IMMICH, POSTGRES_PASSWORD_PAPERLESS | homelab/.env |
| PAPERLESS_SECRET_KEY, PAPERLESS_ADMIN_PASSWORD | homelab/.env |
| MARIADB_PASSWORD_MONICA, CODE_SERVER_PASSWORD | homelab/.env |
| OBSIDIAN_LIVESYNC_PASSWORD, GOOGLE_CLIENT_SECRET | homelab/.env |
| PENNY_TUNNEL_TOKEN, JELLYSEERR_API_KEY, TELEGRAM_WEBHOOK_SECRET | penny/.env |
| COMPANION_ADMIN_PASSWORD, CONTROL_HOOKS_SECRET | penny/.env |
| NORDVPN_PRIVATE_KEY | penny/.env |

### Keys already in vault (skip — dedup)
| Key | Already in |
|-----|-----------|
| TELEGRAM_BOT_TOKEN | openclaw.env, penny.env |
| OPENROUTER_API_KEY | secrets.env, penny.env |
| CLOUDFLARE_API_TOKEN | secrets.env |
| ZAI_API_KEY | research_keys.env |
| TAVILY_API_KEY | research_keys.env |
| EXA_API_KEY | research_keys.env |
| JINA_API_KEY | api.env |

---

## DO NOT
- Touch penny/.env or homelab/.env (infra — they keep running)
- Delete .env files yet (that's Task 3)
- Forget to commit+push vault changes

## Deliverable
All new keys in vault. `secrets list` shows new files. Git pushed.
