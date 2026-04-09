# OneShot Project-Specific Rules

This file contains rules specific to the OneShot framework itself.
For general coding/workflow rules, see the other instruction files.

## What OneShot Is

OneShot is a **control plane for Claude-first orchestration**:
- Claude Code is the primary planner and reviewer (thinker)
- Codex and Gemini execute tasks via parallel dispatch (doers)
- Lane-based routing policy (config/lanes.yaml) drives task dispatch
- Dispatch protocol (`_shared/dispatch.md`) handles prompt construction, parallel execution, output capture
- Argus is the default search plane
- Instructions are the single source of truth (docs/instructions/)

## Project Structure

```
oneshot/
  config/           # YAML routing policy (lanes, models, workers, search, providers)
  core/             # Python schemas, router, and dispatch runner
  docs/instructions/ # Neutral instruction source (this directory)
  .claude/rules/    # Thin imports to docs/instructions/
  .claude/skills/   # Operator and utility skill prompts
  .opencode/        # OpenCode adapter (installed, pending interactive auth)
  templates/        # Project templates (AGENTS.md.j2, CLAUDE.md.j2)
  secrets/          # SOPS/Age encrypted vault
  scripts/          # Build, deployment, and maintenance scripts
```

## Progressive Disclosure

Instructions load based on project type:
- **Core rules** always load (~300 tokens)
- **Project-specific** rules load based on file detection

## Skill Catalog

### Operators
| Skill | Purpose |
|-------|---------|
| `/short` | Quick iteration, burn-down mode |
| `/full` | Structured work with milestones |
| `/conduct` | Multi-model orchestration with lane routing |

### Utilities
| Skill | Purpose |
|-------|---------|
| `/handoff` | Save context before `/clear` |
| `/restore` | Resume from handoff |
| `/research` | Background research via Argus |
| `/freesearch` | Zero-token web search via Argus |
| `/doc` | Cache external documentation |
| `/vision` | Image/website visual analysis |
| `/secrets` | SOPS/Age secrets management |
| `/debug` | Systematic debugging (4-phase: investigate → analyze → hypothesize → fix) |
| `/tdd` | Test-driven development (RED-GREEN-REFACTOR cycle) |

## v2 Capabilities

New structured artifacts and schemas available to operators:
- `templates/TASK_SPEC.md` — Template for task specification documents
- `core/plan_schema.py` — Machine-readable plan schema (plan.json)
- `core/task_schema.py` — Task schema with `infer_risk()` for risk classification (low/medium/high)

## AGENTS.md

AGENTS.md is the **neutral operating contract** — not Claude-specific.
It references config/lanes.yaml for routing and defines task classes.
Any code assistant (Claude, OpenCode, etc.) can read it directly.

## Janitor System

Background intelligence layer (`core/janitor/`) that runs automatically via Claude Code hooks (global `~/.claude/settings.json` — all projects get it):

- **Project type detection**: classifies repos as `code`, `document`, or `hybrid` on every session start
- **Code signals** (code/hybrid): test gaps, code smells, dependency map
- **Document signals** (document/hybrid): staleness, orphans, clusters, size outliers, recent activity, cross-references
- **Universal signals** (all types): config drift, recent focus, critical files, knowledge risk, blockers, dead ends
- **Session recording**: file reads/writes/edits via PostToolUse hook → `.janitor/events.jsonl`
- **Onboarding generation**: project-type-aware summary → `CLAUDE.local.md` (runs at session end via openrouter/free)
- **Staleness gating**: signals are only regenerated when underlying data changes

Storage: `.janitor/` per project (events.jsonl, signal JSON files, onboarding-state.json).

The janitor lane (`janitor` task classes) routes exclusively to the `free` worker.
No review needed — these are housekeeping tasks.

## Secrets

SOPS/Age encrypted vault at `secrets/`. Use the `secrets` CLI:
```bash
secrets get KEY                        # retrieve a value
secrets set NAME KEY=value [--commit]  # add/update
secrets list                           # show all vault files
```

Never echo secrets in output. Never commit plaintext secrets.

## Infrastructure

| Machine | IP | Role |
|---------|------|------|
| oci-dev | 100.126.13.70 | Primary dev, services, Claude Code |
| homelab | 100.112.130.100 | Docker services, 26TB storage |
| macmini | 100.113.216.27 | Apple Silicon GPU, transcription |
