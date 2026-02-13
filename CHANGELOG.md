# Changelog

All notable changes to ONE_SHOT are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/).

## [11.0.0] - 2026-02-13

### Breaking Changes
- **Beads deprecated** - Native Tasks (TaskCreate/TaskGet/TaskUpdate/TaskList) are now primary. `/beads` shows deprecation notice. Beads CLI still works as fallback.

### Added
- **Native Tasks** - Claude's built-in task tools are now the primary task tracking system
- **/swarm command** - Agent team orchestration for parallel work (experimental, requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`)
- **Swarm patterns documentation** - Research & review, competing hypotheses, cross-layer coordination
- **docs/SWARMS.md** - Comprehensive swarm usage guide (to be created)

### Changed
- **core.md** - Updated task management from "wait for native" to "use native"
- **/implement** - Now uses native Tasks instead of Beads
- **/restore** - Checks native Tasks first, then Beads fallback
- **SKILLS.md** - Added /swarm, marked /beads as deprecated, updated task tracking section

### Documentation
- Updated README.md to v11 with native tasks and swarm support
- Updated AGENTS.md to v11
- Updated .claude/skills/INDEX.md to v11

### Research Findings
- External models NOT supported in swarms (Claude models only)
- Swarm best for: research/review, competing hypotheses, cross-layer coordination
- Swarm NOT for: sequential tasks, same-file edits, routine tasks

---

## [10.5.0] - 2026-02-13

### Added
- **Context clearing workflow** - `/implement` and `/run-plan` now recommend clearing context first so plans are fresh
- **SKILLS.md documentation** - Comprehensive reference for all 22 slash commands with clear explanations
- **doc.md** - Added context clearing workflow section

### Changed
- **implement.md** - Added pre-implementation context clearing workflow
- **run-plan.md** - Added pre-execution context clearing workflow

### Removed
- `/convexify` - No longer using Convex stack (replaced by /stack-setup in v10.3)
- `/deploy` - Redundant since most work happens on oci-dev anyway

### Documentation
- Updated README.md to v10.5, removed /deploy references
- Updated AGENTS.md to v10.5
- Updated .claude/skills/INDEX.md to v10.5

---

## [10.4.0] - 2026-02-12

### Added
- `check-oneshot.sh --fix` flag (pull only when explicitly requested)
- `oneshot.sh` smart AGENTS.md updates (respects local changes, --force to override)
- `check-apis.sh` PWD-based SOPS config detection (works from any directory)
- `heartbeat.sh --safe` mode (skips check-oneshot to prevent cascade updates)
- `heartbeat-install.sh` installer with 23-hour rate limiting
- All check scripts now idempotent (safe to run multiple times)

### Changed
- check-oneshot.sh defaults to check-only mode (no automatic pulls)

---

## [10.3.0] - 2026-02-12

### Added
- **New Standard Stack** - Complete migration from Convex+Next.js+Clerk+Vercel to Astro+Cloudflare Pages/Workers+Better Auth+Postgres on OCI
- **Infrastructure Documentation** - `.claude/infrastructure/STACK.md` with complete stack reference (architecture, database ops, Cloudflare Tunnel, deployment, auth, backups)
- **Stack Setup Skill** - `.claude/skills/stack-setup/SKILL.md` for automated project configuration with the new stack
- **Stack Quick Reference** - Added to AGENTS.md for instant lookup

### Changed
- **khamel-mode.md** - Updated stack defaults (Astro + CF Pages/Workers + Better Auth + Postgres)
- **web.md** - Complete rewrite for Astro + Cloudflare + Better Auth + Postgres stack
- **Detection patterns** - Changed from `convex/` to `astro.config.*` or `wrangler.toml`
- **Public access** - Changed from Tailscale Funnel + poytz to Cloudflare Tunnel + Cloudflare Pages
- **Storage progression** - Updated from SQLite → Convex → OCI DB to SQLite → Postgres on OCI → OCI Autonomous DB
- **Auth default** - Better Auth + Google OAuth (sessions in Postgres) replaces Clerk
- **Anti-patterns** - Added Convex/Next.js/Clerk/Vercel as old stack to avoid

### Removed
- `/convexify` slash command (replaced by /stack-setup for new stack)

### Fixed
- All detection tables updated for new stack triggers
- context-v8.py stack reference updated

---

## [10.2.0] - 2026-02-08

### Added
- **Work Discipline** - Core rules for planning first, committing per task, keeping tasks small
- **Beads Operational Rules** - Session start/end prompts, blocked bead handling, bead splitting guidance
- **beads_viewer (`bv`)** - Recommended TUI for visual bead management
- **Documentation Maintenance** - AGENTS.md section for LLMs on when/how to update docs
- **Code Quality** - All hooks reviewed and fixed (no bare except, proper error handling, macOS compatibility)

### Changed
- AGENTS.md footer updated to v10.2 with work discipline features
- core.md expanded with session start/end prompts
- Documentation maintenance patterns codified

### Fixed
- docs-check.sh: Fixed unsafe glob patterns
- context-v8.py: Fixed bare except, proper exception handling
- beads-v8.py: Fixed bare except, proper exception handling
- state.sh: Fixed macOS sed compatibility
- detect-latest-glm.sh: Fixed macOS sed compatibility
- claude-shell-setup.sh: Fixed sed injection risk

---

## [10.1.0] - 2026-02-06

### Added
- **Progressive disclosure** - Rules split by project type (web, cli, service)
- **Auto-detection** - Rules load based on project files (package.json, setup.py, *.service)
- **"Wait for native" strategy** - Documentation for Claude's native TaskCreate/Update/Delete tools
- **Modular rules** - `.claude/rules/` with core.md, web.md, cli.md, service.md, khamel-mode.md
- **V9-TO-V10.1.md** - Comprehensive migration guide

### Changed
- CLAUDE.md reduced from 374 lines to ~62 lines
- Token usage: ~300 always-on (down from ~2000 in v10)
- README rewritten for v10.1 clarity

### Token Savings Progression
- v9: ~5,800 tokens always-on
- v10: ~425 tokens always-on (93% reduction from v9)
- v10.1: ~300 tokens always-on (95% total reduction from v9)

### Removed
- No removals - this is a refinement of v10

---

## [10.0.0] - 2025-XX-XX

### Added
- **16 slash commands** - On-demand invocation (/interview, /cp, /implement, /freesearch, /research, /think, /diagnose, /codereview, /deploy, /remote, /audit, /beads, /handoff, /restore, /secrets, /batch)
- **7 rules files** - Always-loaded context (~410 tokens total)
- **"Personal configuration" philosophy** - Not a framework, not distributable

### Changed
- Simplified from framework to configuration
- Commands invoke on-demand vs auto-loading 52 skills

### Removed
- AGENTS.md routing table (no longer needed)
- 52 auto-loaded skills
- Hooks for context injection
- Auto-trigger on "build me"

### Token Savings
- 93% reduction from v9 (~5,800 → ~425 tokens)

---

## [9.0.0] - 2025-XX-XX

### Added
- **Framework with 52 skills** - Auto-loaded skill system
- **AGENTS.md routing table** - Pattern matching to skills
- **Auto-interview** - "Build me X" triggered structured interview
- **Skill marketplace integration** - SkillsMP access
- **Continuous planning** - 3-file pattern (task_plan.md, findings.md, progress.md)

### Token Cost
- ~5,800 tokens always-on (CLAUDE.md + AGENTS.md + hooks + skills)

---

## [8.2] - 2026-01-31

### Added
- **Heartbeat System** - Daily automatic health checks and updates
  - Auto-updates ONE-SHOT repo via `git pull`
  - Auto-updates GLM model version in `models.env` and shell configs
  - Verifies secrets decryptability (SOPS/Age)
  - Auto-installs Claude Code CLI if missing
  - Auto-upgrades Claude Code 2.0.x → 2.1.x
  - Tracks last check date in project CLAUDE.md
  - Syncs health data to beads
- **Fleet Management** - Multi-machine health monitoring
  - `scripts/fleet-status.sh` - Check all machines at once
  - `--fix` flag for auto-repair across fleet
  - Supports macOS Homebrew, Linux, nvm environments
- **SOPS/Age Secrets** - Encrypted secrets management
  - Age key distribution across machines
  - `scripts/sync-secrets.sh` - Verify decryptability
  - `scripts/secrets-vault-manager` skill for managing secrets
- **Shell Setup Improvements**
  - `scripts/claude-shell-setup.sh` - Unified setup for bash/zsh
  - Auto-configures `cc` (Anthropic Pro) and `zai` (GLM API) shortcuts
  - Heartbeat PROMPT_COMMAND/chpwd hooks for auto-runs

### Changed
- **Heartbeat auto-runs** when `cd` to directories with `CLAUDE.md`
- **GLM model updates** now commit and push to git automatically
- **check-clis.sh** now sources nvm and adds Homebrew to PATH
- **sync-secrets.sh** passes SOPS_AGE_KEY_FILE to sops commands

### Fixed
- PROMPT_COMMAND escaping bug (quoted heredoc → unquoted for variable expansion)
- check-glm.sh now handles both old (`${ZAI_MODEL:-glm-X.X}`) and new (`GLM_MODEL=`) formats
- ZAI_API_KEY detection - now exports variable for child processes
- Age key not found errors - fixed PATH issues on macOS Homebrew

### Documentation
- Updated README.md with Heartbeat and Fleet Management sections
- Added comprehensive machine setup documentation
- Documented Age key distribution process

## [8.1] - 2025-01-29

### Added
- **Slash commands** - All skills can now be invoked via `/skill-name`
- **Slash command documentation** - New section in AGENTS.md listing all slash commands
- **deep-research skill documentation** - Gemini CLI + free search APIs (Perplexity, Context7, Tavily)
- **search-fallback skill documentation** - Perplexity, Context7, Tavily, Brave, Bing APIs
- **Interview depth slash commands** - `/full-interview`, `/quick-interview`, `/smart-interview` documented
- **Research slash commands** - `/deep-research`, `/search-fallback` documented

### Changed
- Version: 8.0 → 8.1
- Core skills count: 17 → 19 (added deep-research, search-fallback to core routing)
- Skill count: 29 → 41 (actual count of skills in the system)
- AGENTS.md enhanced with slash command references in skill router
- INDEX.md updated with deep-research and search-fallback entries
- README.md updated with research capability and skill count

### Documentation
- AGENTS.md now has SLASH COMMANDS section documenting all `/` commands
- deep-research skill now documented as core with Gemini CLI primary mode
- search-fallback skill now documented with 5 API options
- All documentation updated to reflect v8.1

## [5.5] - 2025-12-18

### Added
- **beads** skill - Git-backed persistent task tracking with dependencies
  - Cross-session memory (survives /clear and session restarts)
  - Task dependency graphs with `bd ready` for unblocked work
  - Multi-agent coordination via hash-based IDs (bd-xxxx)
  - CLI + hooks approach (1-2k tokens vs 10-50k for MCP)
- **the-audit** skill - Strategic communication filter (added to SKILLS array)
- Beads initialization in oneshot.sh (optional, if bd CLI installed)
- Beads integration in create-handoff (state capture before /clear)
- Beads integration in resume-handoff (sync on resume)
- Beads-based coordination in multi-agent-coordinator
- `.beads/` cache files to .gitignore template

### Changed
- Skill count: 23 → 25 (added beads, the-audit)
- Context category: 2 → 3 skills (now includes beads)
- Version: 5.3 → 5.5
- AGENTS.md updated with beads pattern in skill router
- CLAUDE.md template includes beads trigger

### Documentation
- Updated README.md with beads section and persistent tasks
- Updated skills INDEX.md with beads and the-audit
- Added Communication category to INDEX.md

## [5.3] - 2024-12-15

### Added
- **Native Sub-agents** (4 agents) for isolated context work:
  - `security-auditor` - OWASP/secrets/auth security review (sonnet)
  - `deep-research` - Long codebase exploration (haiku)
  - `background-worker` - Parallel task execution (haiku)
  - `multi-agent-coordinator` - Multi-agent orchestration (sonnet)
- **delegate-to-agent** skill - Bridge skill to route tasks to native sub-agents
- `.claude/agents/` directory with INDEX.md and TEMPLATE.md
- Agent router in AGENTS.md with pattern matching
- "Skills vs Agents" decision guide in AGENTS.md
- Agent validation job in CI pipeline
- Agent installation in oneshot.sh bootstrap

### Changed
- Skill count: 22 → 23 (added delegate-to-agent)
- Version: 5.2 → 5.3
- oneshot.sh now installs both skills and agents
- CLAUDE.md template includes agent triggers
- CI now validates both skills and agents

### Documentation
- Updated README.md with agents section
- Updated skills INDEX.md with delegate-to-agent
- Added agent chains to skill chains documentation

## [5.2] - 2024-12-14

### Added
- **observability-setup** skill - logging, metrics, health checks, alerts
- GraphQL content to api-designer (schema, resolvers, N+1 patterns)
- NoSQL content to database-migrator (MongoDB, Redis migrations)
- Accessibility (WCAG/ARIA) checklist to code-reviewer
- Extended persona library to thinking-modes
- CI pipeline with skill validation and tests
- Skill INDEX.md catalog
- Skill TEMPLATE.md for creating new skills
- `--upgrade` flag to oneshot.sh for updating existing skills
- `--help` flag to oneshot.sh

### Fixed
- Stale `oneshot-resume` reference → `resume-handoff`
- secrets-vault paths → `oneshot/secrets/`
- Added `Edit` tool to 11 skills

### Changed
- Skill count: 20 → 21
- Version: 5.1 → 5.2

## [5.1] - 2024-12-13

### Added
- Consolidated 20 skills from 28 (eliminated overlap)
- Non-destructive installation (never overwrites)
- AGENTS.md skill router with pattern matching
- Thinking modes (5 levels)
- Plan workflow (create-plan → implement-plan)
- Handoff system (create-handoff → resume-handoff)

### Changed
- oneshot.sh: Bootstrap script with additive-only behavior
- Skills downloaded from GitHub, not bundled

## [5.0] - 2024-12-12

### Added
- Non-destructive skill orchestration
- Skill chaining support
- CLAUDE.md supplementing (prepend, not overwrite)

## [4.1] - 2024-12-11

### Added
- thinking-modes skill
- create-plan skill
- implement-plan skill
- create-handoff skill
- resume-handoff skill

## [4.0] - 2024-12-10

### Added
- Initial oneshot.sh bootstrap script
- TODO.md format (replacing checkpoint.yaml)
- push-to-cloud skill for OCI-Dev deployment
