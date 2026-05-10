# LLM Overview — oneshot
*Updated: 2026-05-10 07:35 UTC | Tier: standard | Auto-updated: daily cron*

## What This Is
**v14.3** | Claude plans. Workers execute. Janitor watches.

## Current State
*Status: 🟢 active from local git history*

**Active work:**
- 520b008 chore: bootstrap LLM-OVERVIEW files 2026-05-10
- 1635c56 fix: add PATH entries to managed block for secrets/npm-global/opencode
- 905e205 fix: ZAI_API_KEY warn-not-fail, fix SHELL_TYPE env override in --install
- 2244a9e feat: add cx/gem aliases, fix oc, canonicalize all shell functions
- 30873ff chore: janitor state update
- 63653eb fix(update): sync .claude/commands/ to projects on update

**Known issues:**
- No known issue found in recent commit subjects or local TODO/BLOCKERS docs.

**Recent changes (7 days):**
- `520b008 chore: bootstrap LLM-OVERVIEW files 2026-05-10`
- `ba658b6 chore: daily backup snapshot 2026-05-08`
- `5cebf65 chore: daily backup snapshot 2026-05-05`
- `40796fb chore: daily backup snapshot 2026-05-05`
- `96b246a Archive — replaced by Janus + Superpowers + Claude Octopus`
- `558f2eb chore: daily backup snapshot 2026-05-04`
- `d3ca0fb chore: daily backup snapshot 2026-05-04`
- `47e2335 docs: define oneshot lite architecture`
- `da22eb7 handoff: 2026-05-04 oneshot SKILL.md YAML fixes`
- `1635c56 fix: add PATH entries to managed block for secrets/npm-global/opencode`
- `905e205 fix: ZAI_API_KEY warn-not-fail, fix SHELL_TYPE env override in --install`
- `2244a9e feat: add cx/gem aliases, fix oc, canonicalize all shell functions`
- `30873ff chore: janitor state update`
- `63653eb fix(update): sync .claude/commands/ to projects on update`
- `cdeeae0 fix(commands): add slash commands as harness-level .md files`
- `df3d9d1 secrets: add ARGUS_REMOTE_URL to argus vault`

## Architecture
- Stack marker: No explicit stack marker found.
- Top-level entry: `1shot/`
- Top-level entry: `AGENTS.md`
- Top-level entry: `archive/`
- Top-level entry: `ARCHIVED.md`
- Top-level entry: `bin/`
- Top-level entry: `CENTRAL_SECRETS.md`
- Top-level entry: `CHANGELOG.md`
- Top-level entry: `CLAUDE.local.md`

## Key Commands
- `git status --short`
- `git log --oneline -5`

## Dependencies
- **Runs on:** Not declared in local repo evidence.
- **Calls out to:** See repo docs and config files.
- **Called by:** Not declared in local repo evidence.
- **Env vars required:** No `.env.example` keys found.

## Critical Rules
- Preserve repo-local instructions in `AGENTS.md`, `CLAUDE.md`, or README when present.
- Do not infer behavior from the repository name alone; verify against local docs and source.

## Gotchas
- Generated from local evidence only: git history, top-level structure, README/CLAUDE/AGENTS/docs, and env examples.
