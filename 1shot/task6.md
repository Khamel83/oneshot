# Task 6: Codex Provider — Fix and Cross-Machine Setup

## Context
Codex CLI (OpenAI's coding agent) is part of the ONE_SHOT multi-provider toolchain. It needs to work on all 3 machines, authenticated with the user's ChatGPT Plus subscription ($20/mo).

**Current issues**:
1. On oci-dev: Codex gets 404 on `wss://api.openai.com/responses` despite valid auth
2. `OPENAI_BASE_URL` env var leaks from the `zai()` shell wrapper into Codex sessions
3. Codex status on homelab and macmini is unknown

**Prerequisites**: None (independent of vault consolidation)
**Depends on**: Nothing
**Blocks**: Conduct adversarial review phase

---

## What To Do

### 1. Investigate the 404 error on oci-dev
```bash
# Check Codex version and auth
codex --version
codex login status

# Test with clean env (no ZAI env vars)
env -u OPENAI_BASE_URL -u OPENAI_API_KEY codex exec --full-auto "Say hello"

# If 404 persists, try re-auth
codex logout
codex login
```

The 404 on `/responses` could be:
- Temporary OpenAI outage
- Codex CLI bug (check GitHub issues at `openai/codex`)
- Auth token format issue (the token is valid but Codex may need a different scope)

### 2. Fix the env var leak
Add to `~/.codex/config.toml`:
```toml
openai_base_url = "https://api.openai.com"
```

This ensures Codex always uses the real OpenAI endpoint regardless of shell env.

**Better fix**: Update the `zai()` function in `~/.bashrc` to NOT set `OPENAI_BASE_URL` globally. Instead, only pass it to claude:

```bash
zai() {
    unset OPENAI_BASE_URL OPENAI_API_KEY  # Clear before setting
    ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic" \
    ANTHROPIC_AUTH_TOKEN="..." \
    OPENAI_BASE_URL="https://api.z.ai/api/coding/paas/v4" \
    OPENAI_API_KEY="..." \
    claude --dangerously-skip-permissions --model glm-5-turbo "$@"
    unset OPENAI_BASE_URL OPENAI_API_KEY  # Clean up after
}
```

Actually the current approach is already scoped (inline env vars, not exported). The leak only happens when Codex is launched FROM a zai() shell session. The config.toml fix is sufficient.

### 3. Check Codex on homelab and macmini
```bash
# Homelab
ssh 100.112.130.100 'command -v codex && codex --version && codex login status'

# Macmini
ssh 100.113.216.27 'command -v codex && codex --version && codex login status'
```

### 4. Install Codex on machines that don't have it
```bash
ssh <machine> 'npm install -g @openai/codex'
```

### 5. Ensure Codex config is consistent across machines
Copy `~/.codex/config.toml` to homelab and macmini:
```bash
scp ~/.codex/config.toml 100.112.130.100:~/.codex/config.toml
scp ~/.codex/config.toml 100.113.216.27:~/.codex/config.toml
```

Each machine will need its own `codex login` (OAuth is per-device).

### 6. Add Codex to heartbeat
The heartbeat script should check Codex auth status:
```bash
# Add to heartbeat check-apis.sh
if command -v codex >/dev/null 2>&1; then
    codex login status 2>&1 | grep -q "Logged in" && echo "codex: ok" || echo "codex: auth expired"
fi
```

### 7. Add Codex to machine bootstrap
Ensure Codex is in the setup/bootstrap scripts for new machines, alongside gemini and claude.

---

## DO NOT
- Manually set OPENAI_API_KEY in .bashrc (Codex manages its own auth via OAuth)
- Share auth tokens between machines (each needs its own `codex login`)
- Skip the heartbeat integration (it needs to auto-detect expired auth)

## Deliverable
- Codex working on all 3 machines
- Config consistent across machines
- Heartbeat checking Codex auth status
- No env var leaks from zai() shell
