# Codex CLI — Multi-Machine Setup & Usage

> **Canonical location**: `~/.claude/rules/codex.md` (global, loads in every project)
> This copy lives in oneshot for version control. Keep them in sync.

Codex (OpenAI's agentic coding CLI) runs on all three machines in this setup.
This guide documents what works, what doesn't, and why — learned the hard way on 2026-03-30.

---

## TL;DR — The Working Command

```bash
# DO THIS — not --full-auto
unset OPENAI_API_KEY
codex exec --sandbox danger-full-access "your prompt here"
```

**From any machine, from any repo that's in `~/.codex/config.toml` as trusted.**

---

## Machine Status

| Machine | Works | Auth |
|---------|-------|------|
| oci-dev (100.126.13.70) | ✓ | `~/.codex/auth.json` |
| homelab (100.112.130.100) | ✓ | `~/.codex/auth.json` |
| macmini (100.113.216.27) | ✓ | `~/.codex/auth.json` |

---

## Auth: ChatGPT Plus OAuth (NOT API key)

Codex uses your **ChatGPT Plus login**, not an OpenAI API key.

- Auth is stored in `~/.codex/auth.json`
- Obtained via `codex login` (opens browser)
- The token auto-refreshes via `refresh_token` — it stays valid

**Critical:** If `OPENAI_API_KEY` is set in the environment, it overrides the OAuth token
and hits the paid API instead. That account has no credits → 404/429 errors.
Always `unset OPENAI_API_KEY` before running codex.

### If auth.json is missing or broken

```bash
# Option 1: Re-login (requires browser)
codex login
# Then paste the localhost:1455 callback URL back to Claude

# Option 2: Copy from a working machine (fastest)
scp homelab:/home/khamel83/.codex/auth.json ~/.codex/auth.json
```

### If the subscription lapses

The token encodes subscription status. After renewing ChatGPT Plus at chat.openai.com,
run `codex login` again to get a fresh token — the old one won't get access back automatically.

---

## The Sandbox Problem: Why `--full-auto` Breaks Here

`--full-auto` is shorthand for `--sandbox workspace-write`, which uses **bwrap** (bubblewrap)
for sandboxing. On these Linux servers (OCI + homelab), bwrap fails:

```
bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted
```

This is a kernel/container restriction — bwrap can't create a loopback interface.

**Fix:** Use `--sandbox danger-full-access` instead. This skips bwrap entirely.
These machines are already on Tailscale + behind OCI security groups, so the blast
radius of a rogue shell command is limited.

```bash
# BROKEN on these machines:
codex exec --full-auto "..."

# WORKS:
codex exec --sandbox danger-full-access "..."
```

---

## Config (`~/.codex/config.toml`)

```toml
model = "gpt-5.4"
model_reasoning_effort = "medium"
personality = "pragmatic"
approvals_reviewer = "user"

# DO NOT set openai_base_url — the default is correct
# Setting it to "https://api.openai.com" (without /v1) causes 404s on the WebSocket
# Setting it to "https://api.openai.com/v1" causes double-path issues on some calls
# Leave it unset and let codex use its built-in default

[projects."/home/ubuntu/github/atlas"]
trust_level = "trusted"
# ... other trusted projects
```

---

## Running Across Machines

From oci-dev, you can run codex on remote machines via SSH:

```bash
# Run codex on homelab
ssh homelab "cd ~/github/myproject && unset OPENAI_API_KEY && codex exec --sandbox danger-full-access 'your task'"

# Run on macmini
ssh macmini "cd ~/github/myproject && unset OPENAI_API_KEY && codex exec --sandbox danger-full-access 'your task'"
```

Or Claude Code can dispatch tasks to all three in parallel using Bash with `&` + `wait`.

---

## Debugging Checklist

| Symptom | Cause | Fix |
|---------|-------|-----|
| `404 Not Found` on `wss://.../responses` | `OPENAI_API_KEY` is set with no credits | `unset OPENAI_API_KEY` |
| `401 Missing bearer` | `auth.json` is missing | Copy from homelab or re-login |
| `401 Missing scopes: api.responses.write` | Stale/incomplete token | Re-login or copy from working machine |
| `bwrap: loopback: Failed RTM_NEWADDR` | bwrap blocked by kernel | Use `--sandbox danger-full-access` |
| `insufficient_quota` | Using API key account (no credits) | `unset OPENAI_API_KEY` |
| Subscription expired 404 | ChatGPT Plus lapsed | Renew at chat.openai.com + re-login |

---

## History / Why This Exists

This was debugged on 2026-03-30 in a Claude Code session. The problems encountered:
1. `OPENAI_API_KEY` in vault was set on PATH, sending requests to the no-credits API account
2. `openai_base_url = "https://api.openai.com"` was manually added to config — wrong (missing `/v1`)
3. A `codex logout` during debugging deleted auth.json, breaking everything
4. `--full-auto` (bwrap sandbox) doesn't work on OCI/homelab Linux kernels
5. ChatGPT Plus subscription had lapsed (Feb 14) — renewed March 30

The fix that unlocked everything: copy `auth.json` from homelab, use `--sandbox danger-full-access`.
