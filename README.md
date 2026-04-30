# ONE_SHOT — Orchestration Control Plane for Claude Code and OpenCode

**v14.3** | Claude plans. Workers execute. Argus searches. Janitor runs in the background.

---

## What It Is

ONE_SHOT is an operator framework centered on Claude Code, with OpenCode-backed delegation support in the harness layer. It combines skills, routing policies, and background intelligence into a multi-model orchestration system.

- **Claude Code** is the planner and reviewer (never the doer for bounded tasks)
- **Codex, Gemini CLI, GLM** are the workers (parallel execution, structured output)
- **OpenCode-backed runners** are supported through `.oneshot/config/models.yaml` and `oneshot_cli/`
- **Lane-based routing** (`config/lanes.yaml`) drives task dispatch by class and category
- **Argus** is the search plane (SearXNG + Brave + Exa, running on homelab)
- **Janitor** is background intelligence ($0, always on, runs via `openrouter/free`)

---

## Install

```bash
bash install.sh
```

Or one-liner:
```bash
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
```

Installs skills to `~/.claude/skills/`, update command to `~/.local/bin/`, and writes `AGENTS.md` + `CLAUDE.md` to the current project.

**Update:**
```bash
oneshot-update        # auto-update if newer version found
oneshot-update force  # force now
```

**Readiness:**
```bash
./bin/oneshot doctor          # check this machine
./bin/oneshot doctor --all-machines
```

---

## Operators

### `/short` — Quick Iteration
Fast operator for existing projects. Loads context (git log, tasks, decisions), asks what you're working on, executes in burn-down mode.

### `/full` — Structured Work
Full operator for new projects and complex refactors. Structured intake → phase-based planning → parallel dispatch → verification.

### `/conduct` — Multi-Model Orchestration
PMO-style orchestrator. Asks clarifying questions first (blocking). Classifies tasks by class + category → routes to lane → dispatches workers in parallel → loops until goal is fully met.

### `oneshot memory` — Repo-First Memory Primitives
Customer-repo-facing memory commands for scaffolding and maintaining durable repo memory.

```bash
./bin/oneshot memory scaffold
./bin/oneshot memory promote decision --title "Use repo memory" --summary "Stable memory lives in docs/agents." --rationale "Keeps project truth local."
./bin/oneshot memory retrieve "repo memory"
./bin/oneshot memory index
./bin/oneshot memory search "portable runbook"
./bin/oneshot memory retrieve "repo memory" --include-cross-repo
./bin/oneshot memory abstract --title "Portable runbook pattern" --lesson "Prefer abstractions first" --category runbook
```

These commands operate on the current repo by default, not on the OneShot repo, so they can be used directly in downstream customer projects.
The private global index currently uses a local SQLite store and reports degraded mode explicitly if cross-repo search is unavailable.

---

## Routing

Tasks are classified by **task class** and **category**. The router selects the optimal worker within each lane.

```bash
python3 -m core.router.resolve --class implement_small --category coding
```

| Task Class | Lane | Category | Workers |
|---|---|---|---|
| `plan` | premium | general | claude_code |
| `implement_small` | cheap | coding | codex, manus, gemini_cli, glm_claude |
| `implement_medium` | balanced | coding | codex, gemini_cli |
| `test_write` | cheap | coding | codex, manus, gemini_cli, glm_claude |
| `review_diff` | premium | review | claude_code, codex |
| `doc_draft` | cheap | writing | manus, gemini_cli, codex, glm_claude |
| `research` | research | research | manus, gemini_cli, codex |
| `janitor_*` | janitor | general | free (openrouter/free) |

Full config: `config/lanes.yaml`, `config/workers.yaml`

---

## Workers

| Worker | Backend | Cost |
|---|---|---|
| `glm_claude` | ZAI / GLM-5-turbo | Free (until plan expiry) |
| `manus` | Manus API v2 | Credits-based (event/daily/monthly/add-on/free order) |
| `codex` | ChatGPT Plus | $20/mo subscription |
| `gemini_cli` | Google API | Free (sign-in) |
| `free` | openrouter/free | $0 always — janitor lane only |
| `claw_code` | OpenRouter | Pay-per-token — manual opt-in |

Auto-expiry: `glm_claude` checks `plan_expires` from `config/workers.yaml` and self-disables when expired. The `shot` terminal command auto-falls back to OpenRouter.

**Terminal shortcuts:**
```bash
shot "task"    # auto-route: GLM free → OpenRouter fallback
zai            # force GLM-5-turbo (free)
oc             # local OpenCode wrapper, if present on this machine
or             # force OpenRouter model
or --code      # force Qwen3-Coder (free on OpenRouter)
```

`oneshot doctor` checks whether the local `oc` launcher exists, but `install.sh` does not create that wrapper for you.

---

## Skills (10 total)

| Skill | Purpose |
|---|---|
| `/short` | Quick iteration on existing work |
| `/full` | New project or major refactor |
| `/conduct` | Multi-model orchestration until done |
| `/handoff` | Save context before `/clear` |
| `/restore` | Resume from handoff |
| `/research` | Background research via Argus |
| `/freesearch` | Zero-token search via Argus cheap mode |
| `/doc` | Build docs and research packs through Argus |
| `/vision` | Analyze images or websites |
| `/secrets` | SOPS/Age secrets management |

---

## Janitor (Background Intelligence)

Runs automatically — no manual action needed. Cost: $0.

1. **PostToolUse hook** records every file read/write/edit to `.janitor/events.jsonl`
2. **Cron** (every 15 min) finds unprocessed events, runs free model summarizer
3. **SessionEnd hook** marks session; cron picks up remaining data

Produces: test gap analysis, code smell detection, dependency maps, doc staleness, knowledge risk, onboarding summaries — all queryable via grep or `.janitor/*.json`.

Files: `core/janitor/` — `worker.py`, `recorder.py`, `jobs.py`

---

## Search

All web search routes through **Argus** on homelab (`100.112.130.100`):
- HTTP API: `http://100.112.130.100:8270`
- MCP server: registered in `~/.claude/settings.json`

Providers: SearXNG, Brave, Serper, Tavily, Exa — with automatic fallback and RRF ranking.

Config: `config/search.yaml`

---

## Secrets

SOPS/Age encrypted vault at `secrets/`. All machines use the same age key at `~/.age/key.txt`.

```bash
secrets get KEY                        # retrieve a value
secrets set NAME KEY=value [--commit]  # add/update
secrets list                           # show all vault files
```

Never commit plaintext. Use the `/secrets` skill to manage from Claude Code.

---

## Project Structure

```
oneshot/
  config/           # YAML routing policy (lanes, models, workers, search)
  core/             # Python schemas, router, dispatch runner, janitor
  docs/instructions/ # Operator instructions (single source of truth)
  .claude/rules/    # Thin imports to docs/instructions/
  .claude/skills/   # Operator and utility skill prompts
  templates/        # TASK_SPEC.md, plan.json schema, CLAUDE.md.j2
  secrets/          # SOPS/Age encrypted vault
  scripts/          # Build, eval, and maintenance scripts
  eval/             # Benchmark tasks and trace storage
```

---

## Typical Session

```
claude .          # open Claude Code in project
/short            # load context, ask what's next, burn down tasks
/handoff          # save context before ending or /clear
```

---

## Version History

See `CHANGELOG.md` for full history. Current: **v14.3** (Janitor lane, background intelligence, openrouter/free worker, category routing).

Major milestones:
- **v14** — Category-based routing, GLM worker, ZAI expiry guard, Janitor system
- **v13** — Operator framework (replaced 25+ commands with 3 operators + 7 utilities)
- **v12** — Agent Lightning delegation audit, intelligent delegation protocol
- **v11 and earlier** — See `archive/`

---

## License

MIT — use freely, modify, share.
