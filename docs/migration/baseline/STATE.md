# OneShot Baseline State — pre-router-refactor

Tagged: `pre-router-refactor`
Date: 2026-04-01

## Current Operator Behavior

### `/short` — Quick Iteration
- Loads context (git log -5, TaskList, DECISIONS.md, BLOCKERS.md)
- Asks what you're working on
- Executes in burn-down mode
- Codex: advisory review only (pre-flight + post-completion)
- No Gemini dependency

### `/full` — Structured Work
- Creates IMPLEMENTATION_CONTEXT.md
- Structured intake (goals, scope, architecture, constraints)
- Phase-based planning with milestones
- Codex: plan review + milestone review + challenge pass
- Gemini: research tasks if available

### `/conduct` — Multi-Model PMO Orchestrator
- Detects providers (`command -v codex`, `command -v gemini`)
- 5 required intake questions (BLOCKING)
- Creates 1shot/ directory with PROJECT.md, STATE.md, ROADMAP.md
- Routes work across Claude + Codex + Gemini
- Codex: adversarial challenge phase
- Gemini: research tasks
- Loops until goal met

### `/research` — Background Research
- Mode 1 (primary): Gemini CLI via `gemini --yolo "[prompt]"`
- Mode 2 (fallback): Perplexity → Tavily → Brave APIs
- Decrypts keys from `secrets/research_keys.env.encrypted`
- Spawns background sub-agent

### `/freesearch` — Zero-Token Search
- Checks docs cache first (`~/github/docs-cache/docs/cache/.index.md`)
- Falls back to Exa API via direct curl
- Decrypts Exa key from `secrets/research_keys.json.encrypted`

## File Inventory

| Location | Files | Lines |
|----------|-------|-------|
| `.claude/rules/` | 9 .md files | 756 |
| `.claude/skills/` | 11 SKILL.md + shared | 1,614 |
| `.claude/skills/_shared/` | providers.md | ~70 |
| Root | CLAUDE.md, AGENTS.md, README.md | ~430 |
| `scripts/` | 32 scripts | — |
| `secrets/` | 21 encrypted .env files | — |
| `templates/` | community-starter | — |

## Provider Dependencies

| Provider | Used By | Detection |
|----------|---------|-----------|
| Claude Code | All skills | Always available |
| Codex CLI | /conduct, /full, /short | `command -v codex` |
| Gemini CLI | /conduct, /full, /research | `command -v gemini` |
| Exa API | /freesearch | Key in vault |
| Argus | NOT YET | Running on :8005 but not referenced |
| OpenCode | NOT YET | Not installed |

## Key Architectural Notes

- Skills are Markdown prompts, not code
- Routing is provider-name-based (hardcoded in skill text)
- No centralized config — each skill has its own provider logic
- `.claude/rules/` uses progressive disclosure (core always loads, project-type loads on detection)
- `AGENTS.md` is curl-synced from master (read-only per core.md)
- Secrets: SOPS/Age encrypted in `secrets/`, accessed via `secrets` CLI
