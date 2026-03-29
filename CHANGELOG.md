# Changelog

All notable changes to ONE_SHOT are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [13.2.0] - 2026-03-28

### Added
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
