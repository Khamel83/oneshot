# Task 4: Cleanup — Shell Exports, Age Key Security, Empty Files

## Context
Keys are in vault, plaintext is stripped. Now clean up loose ends.

**Prerequisites**: Task 3 complete
**Depends on**: Task 3
**Blocks**: Task 5

---

## What To Do

### 1. Check shell config for redundant key exports
```bash
grep -n 'export.*API_KEY\|export.*TOKEN\|export.*SECRET' ~/.bashrc ~/.zshrc ~/.profile ~/.bashenv 2>/dev/null
```

If any keys are exported that now exist in the vault, they can be removed (services should use `secrets get` instead). However, be careful — some keys may be needed by running shell sessions or cron jobs.

### 2. Verify age key security
```bash
ls -la ~/.config/sops/age/keys.txt
# Should be: -rw------- (600), owned by ubuntu
stat -c '%a %U' ~/.config/sops/age/keys.txt
```

If permissions are too open, fix:
```bash
chmod 600 ~/.config/sops/age/keys.txt
```

### 3. Verify age key on all machines
```bash
# oci-dev
ssh 100.112.130.100 'stat -c "%a %U" ~/.config/sops/age/keys.txt'
# macmini
ssh 100.113.216.27 'stat -c "%a %U" ~/.config/sops/age/keys.txt'
```

### 4. Empty vault files
Keep them (per adversarial review — they'll be needed when we eventually migrate docker-compose).

### 5. Codex config fix
Add to `~/.codex/config.toml`:
```toml
openai_base_url = "https://api.openai.com"
```
This prevents the ZAI `OPENAI_BASE_URL` env var from leaking into Codex sessions.

**NOTE**: As of 2026-03-28, Codex is returning 404 on the `/responses` endpoint even with correct auth. This may be a temporary OpenAI issue or CLI bug. Re-authenticate with `codex logout && codex login` if the issue persists.

---

## DO NOT
- Delete empty vault files
- Remove key exports that are actively used by running services
- Touch penny/ or homelab/ configs

## Deliverable
Clean shell configs, verified age key permissions, Codex config fixed.
