# Changelog

All notable changes to ONE_SHOT are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/).

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
