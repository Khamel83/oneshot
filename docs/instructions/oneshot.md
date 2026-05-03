# OneShot Project-Specific Rules

This file contains rules specific to the OneShot framework itself.
For general coding/workflow rules, see the other instruction files.

## What OneShot Is

OneShot is a **control plane for Claude-first orchestration**:
- Claude Code is the primary planner and reviewer (thinker)
- OpenCode Go workers (deepseek-v4-flash, minimax-m2.7, kimi-k2.6) execute tasks via parallel dispatch (doers)
- Lane-based routing policy (`.oneshot/config/models.yaml`) drives task dispatch
- `./bin/oneshot dispatch` and `./bin/oneshot dispatch-many` handle execution, worktree management, and output capture
- Argus is the default search plane
- Instructions are the single source of truth (docs/instructions/)

## Project Structure

```
oneshot/
  config/ + .oneshot/config/  # YAML routing (legacy lanes, active models/providers)
  core/             # Python schemas, router, and dispatch runner
  docs/instructions/ # Neutral instruction source (this directory)
  .claude/rules/    # Thin imports to docs/instructions/
  .claude/skills/   # Operator and utility skill prompts
  .opencode/        # OpenCode adapter (installed, fully set up)
  oneshot_cli/      # CLI tool for dispatch and worktree management
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
| `/dispatch` | Dispatch a single task to a worker |
| `/status` | Check status of dispatched tasks |
| `/escalate` | Escalate a failed task to a stronger lane |
| `/research` | Background research via Argus |
| `/freesearch` | Zero-token web search via Argus |
| `/doc` | Cache external documentation |
| `/vision` | Image/website visual analysis |
| `/adversarial-review` | Adversarial second-opinion review |
| `/secrets` | SOPS/Age secrets management |
| `/debug` | Systematic debugging (4-phase) |
| `/tdd` | Test-driven development (RED-GREEN-REFACTOR) |
| `/janitor` | Background intelligence debrief |
| `/update` | Sync oneshot skills to current project |

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

Background intelligence layer (`core/janitor/`) that runs automatically via Claude Code hooks (global `~/.claude/settings.json` — all projects get it). Hooks live at `~/.claude/hooks/janitor-*.sh` (not in the oneshot repo — they must work across all machines and projects without requiring the repo at a specific path).

- **Project type detection**: classifies repos as `code`, `document`, or `hybrid` on every session start
- **Code signals** (code/hybrid): test gaps, code smells, dependency map
- **Document signals** (document/hybrid): staleness, orphans, clusters, size outliers, recent activity, cross-references
- **Universal signals** (all types): config drift, recent focus, critical files, knowledge risk, blockers, dead ends
- **Session recording**: file reads/writes/edits via PostToolUse hook → `.janitor/events.jsonl`
- **Onboarding generation**: project-type-aware summary → `CLAUDE.local.md` (runs at session end via openrouter/free)
- **Staleness gating**: signals are only regenerated when underlying data changes

Storage: `.janitor/` per project (events.jsonl, signal JSON files, onboarding-state.json).

The janitor lane routes to the `free` worker (OpenRouter free tier).
No review needed — these are housekeeping tasks.

## Shared Memory

Cross-agent knowledge surface at `.claude/memory/`. All agents (Claude, OpenCode, other workers) read and write to the same files, so learnings from one agent benefit all others.

**Structure:**
```
.claude/memory/
  memory.md           # Index — entry point, read at session start
  learnings.md        # Cross-agent dated discoveries
  tools/
    gemini.md         # Gemini CLI usage, quotas, cost
    other-agents.md   # OpenCode, Cursor, etc.
```

**How it works:**
1. Claude reads `.claude/memory/memory.md` at session start (via `.claude/rules/core.md`)
2. Dispatch prompts tell workers (opencode, minimax, kimi) to read it before starting tasks
3. Any agent that discovers something useful appends a dated entry: `YYYY-MM-DD — [agent] — finding`
4. AGENTS.md references it as the shared memory location

**What goes here:** Operational learnings, gotchas, quirks — descriptive knowledge that agents discover during sessions.

**What does NOT go here:** Rules, instructions, config (those stay in `docs/instructions/`, `.claude/rules/`, and YAML configs).

**Maintenance:**
- Entries are date-stamped so stale ones are visible
- Git-tracked — easy to see changes and revert
- Periodically prune entries older than 90 days or summarize into rules
- If a file exceeds ~100 lines, summarize and reset

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
| MBA (primary dev) | 100.64.121.72 | MacBook Air, primary dev, Claude Code |
| oci-dev | 100.126.13.70 | Cloud VM, services |
| homelab | 100.112.130.100 | Docker services, 26TB storage |
| macmini | 100.113.216.27 | Apple Silicon GPU, transcription |
