# Changelog

All notable changes to ONE_SHOT are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [14.3.0] - 2026-04-05

### Added
- **Janitor lane** — dedicated lane for $0 background intelligence tasks via `openrouter/free`
- **Janitor task classes** — `janitor_summarize`, `janitor_extract`, `janitor_hygiene`, `janitor_analyze` (always route to janitor lane, no review)
- **`free` worker** — `config/workers.yaml` entry using openrouter/free model router ($0, no expiry)
- **Session recorder** — `core/janitor/recorder.py`: append-only JSONL event log with SQLite index. Records user requests, actions, files touched, decisions, blockers, discoveries. ~200B/event.
- **Free model caller** — `core/janitor/worker.py`: direct OpenRouter API calls with rate limiting (1000/day, 20/min tracked in `.oneshot/usage.jsonl`), structured JSON extraction with 4-level parse fallback
- **Janitor jobs** — `core/janitor/jobs.py`: 5 implemented jobs (turn summarizer, memory hygiene, session digest, file change analysis, stale file detection)
- **Jobs catalog** — `core/janitor/jobs_catalog.md`: ~20 additional jobs spec'd by value and effort
- **PostToolUse hook** — `.claude/hooks/janitor-record.sh`: automatically records file reads/writes/edits to events.jsonl on every tool call. Zero-overhead (single printf, no jq).
- **SessionEnd hook** — `.claude/hooks/janitor-session-end.sh`: writes session_end marker; cron does the actual processing
- **System cron** — `scripts/janitor-cron.sh`: runs every 15min across all projects, finds unprocessed events, runs summarizer + memory hygiene. Safety net for "I just quit" scenarios
- **`.oneshot/` runtime data** — `.gitignore`d directory for events.jsonl, usage.jsonl, intelligence.db

### Performance
- API key cached after first lookup (was subprocess per call)
- Rate limit counters cached in memory with 5s TTL (was O(n) file scan per call)
- Event reads use `tail`/`grep` (O(1)) instead of full-file JSON parse (O(n))
- Hook uses printf instead of jq (0 process forks vs 3-4)

## [14.2.0] - 2026-04-04

### Added
- **Category-based routing** — `TaskCategory` enum (coding, research, writing, review, general) with `infer_category()` keyword classifier
- **`CATEGORY_ASSIGNMENTS`** — automatic category inference from task class when not explicitly provided
- **`category_preference`** blocks in all lanes (premium, balanced, cheap, research) — workers reordered by best fit for each category
- **`infer_category()`** — keyword-based task classification with priority: writing > review > coding > research > general
- **ZAI expiry guard** — `worker_available()` checks `plan_expires` from `config/workers.yaml`, auto-disables `glm_claude` when expired
- **`post_expiry_default_model`** — `claw_code` in `config/models.yaml` defaults to `deepseek/deepseek-v3.2` when ZAI plan expires
- **`shot` shell function** — terminal auto-router: picks best model (GLM free, falls back to OpenRouter on expiry), `--code` flag for Qwen3-Coder
- **GLM Claude dispatch** — full Claude Code session on GLM-5-turbo via ZAI as dispatchable worker
- **Python router `--category` flag** — `python3 -m core.router.resolve --class <class> --category <cat>` returns category-ordered workers
- **Category routing tests** — 12 infer_category tests + 5 router resolve tests in `tests/test_workflow.bats`
- **CI: `test-router` job** — Python-based category routing and router validation in GitHub Actions
- **CI: config consistency checks** — validates category_preference on all lanes, claw_code exclusion, plan_expires presence

### Changed
- **`claw_code` disabled in cheap lane pool** — removed from `worker_pool`, available as manual opt-in via `--worker claw_code`
- **`resolve()` returns category** — routing response now includes `category` field (inferred or explicit)
- **`dispatch.md`** — Step 1 now classifies category, passes `--category` to resolver, added glm_claude as dispatchable worker, replaced hardcoded codex/gemini preference with category-driven table
- **`/short` and `/full` operators** — dispatch step now uses `--category` flag for category-ordered worker selection
- **`providers.md`** — added category routing table, claw_code marked opt-in, glm_claude documented
- **`task-classes.md`** — added category column and preferred workers to each task class, updated worker table
- **`AGENTS.md`** — updated to v14.2 with category routing, intelligence tiers, terminal entry points

### Fixed
- **`infer_category` priority** — writing/review keywords checked before coding to prevent "document the API endpoints" misclassifying as coding

---

## [13.2.0] - 2026-03-28

### Added
- **Encrypted backup snapshot** - `check-backup.sh` creates daily `secrets/backup-snapshot.env.encrypted` with vault inventory, machine status, age pubkey, git state, and restore instructions (no secret values)
- **Vault consolidation** - ~80 API keys from 14 projects consolidated into encrypted SOPS/Age vault
- **14 API key validators** - `check-apis.sh` upgraded from 5 to 14 real HTTP validation checks (ZAI, OpenAI, Tavily, Exa, Apify, Context7, OpenRouter, DeepSeek, Brave, Jina, GitHub PAT, Cloudflare, Telegram bots)
- **New vault files** - services.env, deployments.env, arb.env, homelab_backup.env
- **OPENAI_API_KEY** - First confirmed OpenAI key vaulted
- **POYTZ_API_KEY** - Generated and vaulted
- **Cross-machine vault sync** - `secrets get` works on all 3 machines (oci-dev, homelab, macmini)

### Changed
- **check-apis.sh** - Removed broken catch-all section, added `--max-time 10` to all curl calls
- **.bashrc** (all machines) - Replaced plaintext ZAI_API_KEY/TAVILY_API_KEY with vault lookups
- **~/.codex/config.toml** - Added `openai_base_url` to prevent ZAI proxy interference
- **~/.ssh/config** - Cleaned up duplicate Host entries, single canonical alias per machine
- **fleet-status.sh** - Uses SSH aliases instead of raw IPs

### Removed
- **cc-mirror-keys.env** - Duplicate keys hijacking alphabetical resolution
- **Plaintext .env files** - Stripped from atlas, arb, networth, poytz, docs-cache, anthropic-api-demo
- **Project-level 1shot/ plan files** - Vault consolidation plan complete, task files deleted
- **Stale files** - IMPLEMENTATION_CONTEXT.md, .claude/continuous/, docs/external/ (old stack refs)
- **Plaintext secrets/cloudflare.env** - Values already in encrypted vault

### Security
- Git history scrubbed for atlas and trojan-research repos (git-filter-repo)

---

## [13.1.0] - 2026-03-22

### Added
- **`/conduct` operator** - Multi-model PMO orchestrator. Asks clarifying questions first, creates a structured plan, routes work across Claude + Codex + Gemini, loops until goal is fully met.
- **10 skills total** - Now 3 operators + 7 utilities (up from 9 skills / 2 operators)

### Changed
- **AGENTS.md** - Updated to include `/conduct` operator spec
- **docs/SKILLS.md** - Updated to reflect 3 operators
- **docs/LLM-OVERVIEW.md** - Updated skill counts, paths, and removed SkillsMP references
- **Skill path** - `~/.claude/commands/` → `~/.claude/skills/` (corrected in all docs)

---

## [13.0.0] - 2026-03-09

### Breaking Changes
- **Operator framework** - Replaced 25+ menu commands with 2 operators (`/short`, `/full`) that discover skills on demand
- **Removed commands**: /interview, /cp, /run-plan, /implement, /sessions, /diagnose, /codereview, /batch, /remote, /delegation-*, /swarm, /think, /audit, /stack-setup, /update, /beads, /skill-discovery, /continuous
- **Skills archived** - v9 skills compressed to `archive/v9-skills.tar.gz`

### Added
- **`/short` operator** - Quick iteration: load context, ask, execute in burn-down mode
- **`/full` operator** - Structured work: intake, plan, execute with checkpoints
- **9 commands total** - 2 operators + 7 utilities (down from 25+)
- **On-demand skill discovery** - Operators discover skills via SkillsMP when needed
- **Decision defaults** - Agents make reasonable choices autonomously

### Changed
- **AGENTS.md** - Now operator spec instead of skill router
- **docs/SKILLS.md** - Command reference for 9 commands
- **README.md** - Updated for v13 operator framework
- **docs/LLM-OVERVIEW.md** - Updated to reflect v13 architecture

### Removed
- Menu-based command system (replaced by operators)
- Skills directory (archived to v9-skills.tar.gz)
- Multiple planning commands (consolidated into operators)
- Delegation audit commands (simplified into operator behavior)

### Architecture
- **Before**: 25+ menu commands, pre-defined skill catalog
- **After**: 2 operators + 7 utilities, skill discovery on demand

---

## [12.2.0] - 2026-02-19

### Added
- **Agent Lightning Integration** - Enriched delegation spans with span_id, session_id, tool_sequence, and reward
- **Delegation audit log** - `.claude/delegation-log.jsonl` with automatic logging via SubagentStop hook
- **/delegation-log** - View and query delegation audit trail
- **/delegation-trajectory** - View session-level execution trajectories (Agent Lightning spans)
- **/delegation-stats** - Reward-weighted performance stats and routing recommendations
- **Credit assignment heuristics** - Identify which delegations contributed most (+credit) vs bottlenecks (+blame)

### Changed
- **Delegation rules v12.2** - Based on DeepMind "Intelligent AI Delegation" paper + Microsoft Agent Lightning
- **Assess-Verify-Escalate-Trace loop** - Formalized delegation protocol with 3-attempt fallback chain
- **core.md** - Updated from v12.1 to v12.2 Intelligent Delegation section
- **delegation.md** - Enhanced with Agent Lightning concepts (spans, trajectories, credit assignment)

---

## Older versions (v4.0 – v11.0)

See `archive/` or git history for changes prior to v12.0.
