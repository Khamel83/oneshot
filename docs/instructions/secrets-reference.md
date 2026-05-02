# Secrets Vault Index

Full key listing by vault file. Use `secrets list` for live output.

| File | What's in it |
|---|---|
| `api.env` | JINA_API_KEY |
| `arb.env` | POLYMARKET_PRIVATE_KEY DUNE_API_KEY UPSTASH_REDIS_REST_TOKEN NORDVPN_PRIVATE_KEY DISCORD_WEBHOOK_URL |
| `argus.env` | ARGUS_BRAVE_API_KEY ARGUS_REMOTE_EXTRACT_KEY ARGUS_REMOTE_EXTRACT_URL |
| `argus_auth.env` | NYTimes/WSJ/Bloomberg/ESPN/LATimes login pairs |
| `cloudflare.env` | CLOUDFLARE_HYPERDRIVE_ID |
| `convex.env` | CONVEX_TEAM_ACCESS_TOKEN CONVEX_TEAM_ID |
| `convex_deploy.env` | CONVEX_DEPLOY_KEY CONVEX_DEPLOYMENT_URL |
| `coparent.env` | TWILIO_* GOOGLE_CALENDAR_* OPENROUTER_API_KEY TELEGRAM_BOT_TOKEN |
| `deployments.env` | VERCEL_TOKEN SUPABASE_* STRIPE_* NEXTAUTH_SECRET CRON_SECRET GOOGLE_MAPS_API_KEY |
| `gmail.env` | GMAIL_CREDENTIALS_B64 GMAIL_TOKEN_B64 GMAIL_PROJECT GMAIL_ACCOUNT |
| `homelab_backup.env` | All homelab service keys (radarr/sonarr/authentik/cloudflare/tailscale/etc.) |
| `openclaw.env` | BRAVE_API_KEY GEMINI_API_KEY OPENROUTER_API_KEY TELEGRAM_TOKEN_* HOMELAB_RPC_TOKEN |
| `penny.env` | OPENROUTER_API_KEY TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID |
| `pypi.env` | PYPI_API_TOKEN |
| `research_keys.env` | EXA_API_KEY APIFY_TOKEN TAVILY_API_KEY ZAI_API_KEY OPENAI_API_KEY SERPER_API_KEY WOLFRAM_APP_ID |
| `secrets.env` | CLOUDFLARE_API_TOKEN CLOUDFLARE_ZONE_ID_* GITHUB_PAT DB_* JWT_SECRET EMAIL_* STRIPE_KEY |
| `services.env` | PERPLEXITY_API_KEY DEEPSEEK_API_KEY GAMMA_API_KEY FIRECRAWL_API_KEY OPENROUTER_API_KEY_ALT1/ALT2 OP_SERVICE_ACCOUNT_TOKEN POYTZ_API_KEY ATLAS_API_KEY OPENCODE_API_KEY OPENCODE_GO_API_KEY |
| `skillsmp.env` | SKILLSMP_API_KEY |

## Usage Patterns

**Ad-hoc lookup:** `secrets get TAVILY_API_KEY`

**Python service at runtime:**
```python
import subprocess
key = subprocess.check_output(["secrets", "get", "OPENROUTER_API_KEY"]).decode().strip()
```

**Project needing .env at startup:** `secrets init deployments`

**Adding a new secret:** `secrets set services "NEW_API_KEY=sk-..." --commit`

**New machine setup:** Clone oneshot → `bash install.sh` → put age key at `~/.age/key.txt`
