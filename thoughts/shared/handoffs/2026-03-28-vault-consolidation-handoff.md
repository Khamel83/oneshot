# Handoff: Vault Consolidation + Codex Fix

**Created**: 2026-03-28 21:20
**Context Used**: ~40% when created

## Quick Summary
Vault consolidation plan recovered from dead session (`7f1472f9`), validated by Gemini adversarial review, written to task files in `1shot/`, and pushed to master. Codex is broken (404 on `/responses` endpoint despite valid auth). Ready to execute.

## What's Done
- [x] Recovered plan from previous session JSONL logs (commit: d641456)
- [x] Wrote `1shot/PLAN.md` with full current state audit (~80 keys across 14 projects)
- [x] Gemini adversarial review — found 5 issues, all incorporated
- [x] Created 6 task files with self-contained context (task1.md through task6.md)
- [x] Committed and pushed to master (commit: d641456)
- [x] Diagnosed Codex issue: `OPENAI_BASE_URL` leaks from `zai()` shell, but fixing it reveals 404 from OpenAI's `/responses` endpoint directly

## In Progress
- [ ] Nothing — plan is ready, waiting for user to start execution

## Not Started
- [ ] Task 1: Validate all keys (read-only audit)
- [ ] Task 2: Consolidate into vault (4 new vault files)
- [ ] Task 3: Strip plaintext from project .env files
- [ ] Task 4: Cleanup (shell exports, age key perms, Codex config)
- [ ] Task 5: Verify (leak check, heartbeat, cross-machine sync)
- [ ] Task 6: Codex provider fix + cross-machine setup

## Active Files
- `1shot/PLAN.md` — Master plan with current state, phases, risk assessment, adversarial review findings
- `1shot/task1.md` through `1shot/task6.md` — Self-contained task files with full context
- `~/.codex/config.toml` — May need `openai_base_url` added (reverted during debugging)
- `~/.bashrc:200-207` — `zai()` function sets `OPENAI_BASE_URL` inline (not exported, but leaks to child processes)

## Key Decisions Made
1. Decision: Don't delete empty vault files | Rationale: Will need them when docker-compose migration happens later
2. Decision: Blank secret values + comment instead of `VAULT:...` references | Rationale: Standard env parsers don't resolve custom URI schemes (would break all apps)
3. Decision: Only validate API-style keys (not passwords/private keys) | Rationale: Can't "test" a DB password without risking mutations
4. Decision: Don't touch penny/.env or homelab/.env | Rationale: docker-compose reads them directly; vault is backup only
5. Decision: Batch vault additions into single commit | Rationale: 50+ individual commits is git spam

## Important Discoveries
- Codex auth is valid (ChatGPT Plus OAuth, token not expired) but OpenAI's `/responses` endpoint returns 404 — may be temporary outage or CLI bug
- `OPENAI_BASE_URL` leaks from `zai()` shell to child processes — `config.toml` override fixes it for Codex but the underlying 404 is a separate issue
- `penny/.env` has 32 keys, `homelab/.env` has 29 keys — these are 75% of the plaintext attack surface and are explicitly out of scope
- TELEGRAM_BOT_TOKEN is duplicated in 7+ locations
- `docs-cache/.env` and `anthropic-api-demo/.env` are pure vault duplicates — safe to delete entirely

## Blockers / Open Questions
| # | Question | Status |
|---|---------|--------|
| 1 | Codex 404 on `/responses` — need to investigate or wait for OpenAI fix | Open |
| 2 | Git history still contains plaintext keys — separate `git filter-repo` effort needed | Deferred |
| 3 | Homelab `sync-all-repos.sh` runs every 1 min (should be 5) — found in previous session, not yet changed | Noted |

## Next Steps (Prioritized)
1. **Immediate**: Tell Claude "run the vault consolidation plan" — skip `/conduct` intake, read `1shot/PLAN.md` and execute task1 through task5 in order
2. **Then**: Fix Codex (task6) — `codex logout && codex login`, add `openai_base_url` to config, set up on all 3 machines, add to heartbeat
3. **Later**: Git history scrubbing (separate effort), docker-compose vault migration for penny/homelab

## Resume
After `/clear`, say:
```
Read 1shot/PLAN.md and execute the vault consolidation plan. Start with task1.md (validate keys). Skip /conduct intake — plan is already approved.
```
