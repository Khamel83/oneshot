# Codex + Gemini CLI Authentication

## Executive Summary

**Codex CLI** uses ChatGPT OAuth authentication with tokens cached in `~/.codex/auth.json`. The file contains access tokens, refresh tokens, and metadata. You CAN copy `auth.json` to other machines (officially supported for headless/CI/CD setups), but tokens auto-refresh after ~8 days and should not be shared across concurrent machines. For Linux servers, use `codex login --device-auth` for headless OAuth flow, or copy `auth.json` from a local machine. **Gemini CLI** supports three auth methods: Google OAuth (interactive), Gemini API key (`GEMINI_API_KEY` env var), and Vertex AI. For headless Linux servers, API key authentication is simplest—just set `GEMINI_API_KEY` environment variable. API keys don't expire unless revoked, making them ideal for multi-machine deployments.

---

## Codex CLI Auth

### How it works

Codex supports two authentication methods:

1. **Sign in with ChatGPT** (OAuth) — for subscription access (Plus, Pro, Team, Edu, Enterprise)
2. **Sign in with API key** — for usage-based billing via OpenAI Platform

When using ChatGPT auth, Codex opens a browser window for OAuth login. After authentication, Codex caches login details locally and reuses them on subsequent runs. The CLI and IDE extension share the same cached credentials.

**Source:** https://developers.openai.com/codex/auth

### Device auth flow

For headless environments or when browser-based OAuth fails:

1. Run `codex login --device-auth` in the terminal
2. Codex displays a URL and one-time code
3. Open the URL on any device with a browser
4. Sign in and enter the code
5. Terminal session is authenticated

**Prerequisites:**
- Device code login must be enabled in ChatGPT security settings (personal account) or workspace permissions (admin)
- If device code isn't enabled, Codex falls back to standard browser OAuth

**Source:** https://developers.openai.com/codex/auth#login-on-headless-devices

### Multi-machine setup (copy vs re-auth)

**Yes, you CAN copy `~/.codex/auth.json` to other machines.** This is an officially supported pattern for:
- Headless servers
- CI/CD runners
- Docker containers
- Remote SSH machines

**How to copy:**

```bash
# Copy to remote machine over SSH
ssh user@remote 'mkdir -p ~/.codex'
scp ~/.codex/auth.json user@remote:~/.codex/auth.json

# Or one-liner without scp
ssh user@remote 'mkdir -p ~/.codex && cat > ~/.codex/auth.json' < ~/.codex/auth.json

# Copy into Docker container
CONTAINER_HOME=$(docker exec MY_CONTAINER printenv HOME)
docker exec MY_CONTAINER mkdir -p "$CONTAINER_HOME/.codex"
docker cp ~/.codex/auth.json MY_CONTAINER:"$CONTAINER_HOME/.codex/auth.json"
```

**Important rules:**
- Treat `auth.json` like a password — it contains access tokens
- Use ONE `auth.json` per runner or serialized workflow stream
- Do NOT share the same file across concurrent jobs or multiple machines
- Do NOT commit to git, paste in tickets, or share in chat

**Source:** https://developers.openai.com/codex/auth#login-on-headless-devices, https://developers.openai.com/codex/auth/ci-cd-auth

### Token expiry

- Codex **auto-refreshes tokens** during use before they expire
- Active sessions usually continue without requiring another browser login
- If `last_refresh` is older than **~8 days**, Codex refreshes the token bundle before the run continues
- If a request gets a `401`, Codex has a built-in refresh-and-retry path
- Refresh tokens can be revoked or expire, requiring re-authentication

**Source:** https://developers.openai.com/codex/auth/ci-cd-auth

### Linux server notes

**Recommended approaches for Linux servers:**

| Method | When to use | Command |
|--------|-------------|---------|
| Device code auth | First-time setup on headless server | `codex login --device-auth` |
| Copy auth.json | Already authenticated on local machine | `scp ~/.codex/auth.json server:~/.codex/` |
| API key auth | CI/CD automation, no ChatGPT subscription needed | Set `OPENAI_API_KEY` env var |

**Credential storage options:**

Configure via `cli_auth_credentials_store` in Codex config:
- `file` — stores in `~/.codex/auth.json` (default, best for servers)
- `keyring` — uses OS credential store
- `auto` — keyring if available, else file

For servers, use `file` storage to enable copying auth between machines.

**Source:** https://developers.openai.com/codex/auth#credential-storage

---

## Gemini CLI Auth

### How it works

Gemini CLI requires authentication with Google services. On first run, it prompts for one of three methods:

1. **Login with Google** (OAuth) — recommended for individual users
2. **Use Gemini API key** — from Google AI Studio
3. **Use Vertex AI** — for Google Cloud enterprise users

Credentials are cached locally for future sessions.

**Source:** https://geminicli.com/docs/get-started/authentication/

### OAuth vs API key

| Method | Best for | Browser required? | Expiry |
|--------|----------|-------------------|--------|
| **OAuth (Login with Google)** | Individual users, Google AI Pro/Ultra subscribers | Yes (first time) | Tokens refresh automatically |
| **Gemini API key** | Headless servers, CI/CD, multi-machine | No | Does not expire (unless revoked) |
| **Vertex AI (ADC)** | Google Cloud enterprise | Yes (first time) | Token refresh via ADC |
| **Vertex AI (Service Account)** | CI/CD, automation | No | Key doesn't expire |
| **Vertex AI (API key)** | Google Cloud API access | No | Does not expire |

**Source:** https://geminicli.com/docs/get-started/authentication/

### Multi-machine / headless server setup

**For headless Linux servers (no browser):**

**Option 1: Gemini API Key (simplest)**

```bash
# Get key from https://aistudio.google.com/app/apikey
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# Make persistent
echo 'export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"' >> ~/.bashrc
source ~/.bashrc

# Or use .env file
mkdir -p ~/.gemini
cat >> ~/.gemini/.env <<EOF
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
EOF
```

**Option 2: Copy cached credentials**

If already authenticated on a local machine:
```bash
# Credentials cached in ~/.gemini/ directory
scp -r ~/.gemini server:~/.gemini
```

**Option 3: Vertex AI with Service Account (enterprise)**

```bash
# Download service account JSON from Google Cloud
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/keyfile.json"
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

**Source:** https://geminicli.com/docs/get-started/authentication/#running-in-headless-mode

### Environment variable support

Gemini CLI supports these environment variables:

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Gemini API key authentication |
| `GOOGLE_API_KEY` | Google Cloud API key for Vertex AI |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI region (e.g., `us-central1`) |
| `GOOGLE_GENAI_USE_VERTEXAI=true` | Force Vertex AI mode |

**Persistence:** Gemini CLI auto-loads from `.gemini/.env` in project directory or `~/.gemini/.env` for user-wide settings.

**Source:** https://geminicli.com/docs/get-started/authentication/#persisting-environment-variables

---

## Recommended Setup Per Machine

| Machine | Codex | Gemini |
|---------|-------|--------|
| **MBA** (local Mac) | OAuth via browser (`codex login`), file-based storage | OAuth via browser (`gemini` → Login with Google) |
| **homelab** (Linux server) | Copy `auth.json` from MBA OR `codex login --device-auth` | `GEMINI_API_KEY` env var in `~/.gemini/.env` |
| **oci-dev** (cloud VM) | Copy `auth.json` from MBA OR `codex login --device-auth` | `GEMINI_API_KEY` env var in `~/.gemini/.env` |
| **macmini** (always-on Mac) | Copy `auth.json` from MBA OR `codex login` (has browser) | OAuth via browser OR `GEMINI_API_KEY` |

**Notes:**
- For Codex: Use ONE `auth.json` per machine, do not share across concurrent machines
- For Gemini: API keys are simplest for servers, no expiry concerns
- Both tools support file-based credential storage for easy multi-machine deployment

---

## Sources

1. **Codex CLI Authentication** — https://developers.openai.com/codex/auth
2. **Codex CLI CI/CD Auth** — https://developers.openai.com/codex/auth/ci-cd-auth
3. **Codex CLI Reference** — https://developers.openai.com/codex/cli/reference
4. **Gemini CLI Authentication** — https://geminicli.com/docs/get-started/authentication/
5. **Gemini CLI Auth (GitHub)** — https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html
