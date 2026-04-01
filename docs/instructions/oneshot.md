# OneShot Project-Specific Rules

This file contains rules specific to the OneShot framework itself.
For general coding/workflow rules, see the other instruction files.

## What OneShot Is

OneShot is a **control plane for Claude-first orchestration**:
- Claude Code is the primary planner and reviewer
- Lane-based routing policy (config/lanes.yaml) drives task dispatch
- Model-agnostic worker pool (config/models.yaml) supports any backend
- Argus is the default search plane
- Instructions are the single source of truth (docs/instructions/)

## Project Structure

```
oneshot/
  config/           # YAML routing policy (lanes, models, workers, search, providers)
  core/             # Python schemas and utilities
  docs/instructions/ # Neutral instruction source (this directory)
  .claude/rules/    # Thin imports to docs/instructions/
  .claude/skills/   # Operator and utility skill prompts
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

## AGENTS.md

AGENTS.md is the **neutral operating contract** — not Claude-specific.
It references config/lanes.yaml for routing and defines task classes.
Any code assistant (Claude, OpenCode, etc.) can read it directly.

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
