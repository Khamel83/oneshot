# Secrets Management

## The One Vault

All secrets live in `~/github/oneshot/secrets/`. This is the single source of truth across all machines and projects. Do not use `~/github/secrets-vault/` — that repo is deprecated and archived.

- Encrypted with SOPS + Age key at `~/.age/key.txt`
- Git-tracked, auto-synced to all machines within 5 min
- CLI available everywhere as `secrets` (installed by `install.sh`)

## CLI Reference

```bash
secrets get KEY                        # fetch one value
secrets set NAME KEY=value             # add/update a key in NAME.env
secrets set NAME KEY=value --commit    # add/update and auto-commit + push
secrets init NAME                      # write NAME.env to .env in current dir
secrets decrypt NAME                   # dump full file to stdout
secrets list                           # show all files and key names
```

## Vault Files

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
| `services.env` | PERPLEXITY_API_KEY DEEPSEEK_API_KEY GAMMA_API_KEY FIRECRAWL_API_KEY OPENROUTER_API_KEY_ALT1/ALT2 OP_SERVICE_ACCOUNT_TOKEN POYTZ_API_KEY ATLAS_API_KEY |
| `skillsmp.env` | SKILLSMP_API_KEY |

## Usage Patterns by Project Type

### Claude Code session (ad-hoc)
```bash
secrets get TAVILY_API_KEY
```
Use this in the terminal or via the `/secrets` skill.

### Python service at runtime
```python
import subprocess
key = subprocess.check_output(["secrets", "get", "OPENROUTER_API_KEY"]).decode().strip()
```
Argus uses this pattern via `SubprocessSecretsResolver` in `argus/config.py`.

### Project needing a .env file at startup
```bash
secrets init deployments    # writes deployments.env → .env in current dir
# or for homelab:
make gen-env                # merges homelab/.env.encrypted + vault overrides → .env
```
The `secrets init` pattern is for projects where the runtime reads from `.env` (e.g. Docker Compose, serverless functions). Never commit the resulting `.env`.

### Shell setup on a new machine
```bash
bash ~/github/oneshot/scripts/claude-shell-setup.sh --install
# ZAI_API_KEY is pulled from research_keys.env automatically
```

### Adding a new secret
```bash
# Add to the most relevant existing file
secrets set services "NEW_API_KEY=sk-..."
# or create a new file for a new project
secrets set myproject "API_KEY=..."
```

## Adding Secrets for a New Project

1. Pick the right vault file — use an existing one if the key is shared, or create `myproject.env` if it's project-specific
2. `secrets set myproject "KEY=value" --commit` — adds and pushes in one step
3. On the target machine, `git pull` in `~/github/oneshot` picks it up within 5 min (auto-sync cron)
4. Access at runtime via `secrets get KEY`

## New Machine Setup

```bash
# 1. Clone oneshot (auto-synced via cron, or manual)
git clone https://github.com/Khamel83/oneshot ~/github/oneshot

# 2. Install (links secrets CLI to ~/.local/bin/)
bash ~/github/oneshot/install.sh

# 3. Set up age key (get from 1Password: "SOPS age encryption key")
mkdir -p ~/.age
echo "YOUR_AGE_PRIVATE_KEY" > ~/.age/key.txt
chmod 600 ~/.age/key.txt

# 4. Verify
secrets list
```

## What NOT to Do

- Never commit `.env` files (gitignored everywhere)
- Never hardcode keys in scripts that go into the repo
- Never use `~/github/secrets-vault/` — it is deprecated and archived
- Never create a per-project `secrets/` directory with its own SOPS setup — put keys in the central vault instead
