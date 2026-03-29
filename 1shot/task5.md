# Task 5: Verify — Leak Check, Heartbeat, Cross-Machine Sync

## Context
All keys consolidated, plaintext stripped, shell cleaned. Final verification pass.

**Prerequisites**: Task 4 complete
**Depends on**: Task 4
**Blocks**: Nothing (last task)

---

## What To Do

### 1. Leak check — grep for remaining plaintext API keys
```bash
grep -rn 'sk-\|sk_or-\|ghp_\|tvly-\|ctx7sk-\|AIza\|xoxb-\|ACT_\|pat_' \
  ~/github --include="*.env" --include="*.json" --include="*.yaml" --include="*.yml" \
  --exclude-dir=oneshot/secrets --exclude-dir=.git
```

Expected results:
- **Matches in `oneshot/secrets/`** — OK (encrypted files will contain key names but not values)
- **Matches in `penny/.env` and `homelab/.env`** — OK (infra, out of scope)
- **Matches elsewhere** — FAIL, need to strip

### 2. Heartbeat check (oci-dev)
```bash
~/github/oneshot/scripts/heartbeat.sh
```

All checks should pass. If any fail, investigate.

### 3. Vault access spot-check
```bash
secrets get ZAI_API_KEY | wc -c  # Should be > 10
secrets get TAVILY_API_KEY | wc -c  # Should be > 10
secrets get PERPLEXITY_API_KEY | wc -c  # New key, should work
secrets list | grep services  # New file should appear
secrets list | grep deployments  # New file should appear
```

### 4. Cross-machine sync
```bash
# Push vault changes
cd ~/github/oneshot && git push

# Verify on homelab
ssh 100.112.130.100 'cd ~/github/oneshot && git pull'
ssh 100.112.130.100 'secrets list | grep services'

# Verify on macmini
ssh 100.113.216.27 'cd ~/github/oneshot && git pull'
ssh 100.113.216.27 'secrets list | grep services'
```

### 5. Service health check
```bash
# Check that no services broke (systemd on homelab/oci-dev)
ssh 100.112.130.100 'systemctl --user list-units --state=failed' 2>/dev/null
```

---

## DO NOT
- Make any changes (read-only verification)
- Push to non-oneshot repos

## Deliverable
- Leak report (what was found, what's expected)
- Heartbeat pass/fail
- Cross-machine sync confirmation
- Final status report
