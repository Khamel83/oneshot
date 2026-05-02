# Codex CLI — Key Rules

**Working command** (all machines):
```bash
unset OPENAI_API_KEY
codex exec --sandbox danger-full-access "your prompt here"
```

**Why:** `OPENAI_API_KEY` in env overrides OAuth token → hits paid API (no credits) → 404/429.
`--full-auto` uses bwrap sandboxing which fails on OCI/homelab Linux kernels → use `danger-full-access`.

**Auth:** ChatGPT Plus OAuth stored in `~/.codex/auth.json`. If missing: `codex login --device-auth`

**Quick debug:**
| Symptom | Fix |
|---------|-----|
| 404 on wss responses | `unset OPENAI_API_KEY` |
| 401 Missing bearer | `codex login --device-auth` or copy auth.json from homelab |
| bwrap loopback error | Use `--sandbox danger-full-access` |
| insufficient_quota | `unset OPENAI_API_KEY` |

Full setup history and machine status: read this file in full at `.claude/rules/codex.md` (this file).
Detailed reference: ask to see the git history of this file.
