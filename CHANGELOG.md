# Changelog

All notable changes to ONE_SHOT are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/).

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
