# ONE_SHOT — Orchestration Control Plane

**v14.3** | Claude plans. Workers execute. Janitor watches.

---

## What It Is

ONE_SHOT is a multi-model orchestration framework for Claude Code. It routes bounded tasks to external workers via lane-based policies, records session intelligence in the background, and manages secrets and worktrees across machines.

---

## Architecture

| Layer | Role |
|---|---|
| **Claude Code** | Planner and reviewer (never executes bounded tasks) |
| **Workers** | Codex, Gemini CLI, Manus, OpenCode Go, OpenRouter — parallel execution |
| **Router** | `core/router/` — class + category → lane → worker |
| **Dispatch** | `core/dispatch/run.py` — executes workers, writes traces to `eval/traces/` |
| **Janitor** | `core/janitor/` — background intelligence via hooks + cron, $0 |
| **Skills** | `.claude/skills/` — 15 operator/utility prompts |

---

## Quick Start

```bash
bash install.sh                                    # local clone
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash   # fresh

oneshot-update              # auto-update
./bin/oneshot doctor        # readiness check
```

Installs skills to `~/.claude/skills/`, `oneshot-update` + `secrets` to `~/.local/bin/`, and hooks to `~/.claude/hooks/`.

---

## Key Commands

```bash
./bin/oneshot dispatch --lane cheap --task "Fix auth bug"
./bin/oneshot status [TASK_ID]
./bin/oneshot collect TASK_ID
./bin/oneshot review TASK_ID
./bin/oneshot lanes
./bin/oneshot worktree create|list|remove
./bin/oneshot escalate TASK_ID --lane premium
./bin/oneshot memory --help     # scaffold, promote, retrieve, index, search, abstract
```

Entry point: `bin/oneshot` → `python3 -m oneshot_cli`

---

## Routing

```bash
python3 -m core.router.resolve --class implement_small --category coding
```

| Lane | Workers | Fallback |
|---|---|---|
| `premium` | claude_code, codex | none |
| `balanced` | codex, gemini_cli | premium |
| `cheap` | codex, manus, gemini_cli, glm_claude | balanced |
| `research` | manus, gemini_cli, codex | balanced |
| `janitor` | free (openrouter/free) | retry only |

Config: `config/lanes.yaml`, `config/workers.yaml`, `config/models.yaml`

---

## Skills (15 total)

| Skill | Purpose |
|---|---|
| `/short` | Quick iteration on existing projects |
| `/full` | New project or major refactor |
| `/conduct` | Multi-model PMO orchestration |
| `/handoff` | Save context before `/clear` |
| `/restore` | Resume from handoff |
| `/research` | Background research via Argus |
| `/freesearch` | Zero-token search via Argus |
| `/doc` | Cache external docs |
| `/vision` | Image/website analysis |
| `/secrets` | SOPS/Age secrets management |
| `/debug` | Systematic debugging (4-phase) |
| `/tdd` | Test-driven development |
| `/janitor` | Background intelligence queries |
| `/update` | Update project configuration |

Full reference: `.claude/skills/INDEX.md`

---

## Configuration

| File | Purpose |
|---|---|
| `config/lanes.yaml` | Lane policies |
| `config/workers.yaml` | Worker definitions (host, harness, provider, plan_expires) |
| `config/models.yaml` | Model-to-worker mappings |
| `config/providers.yaml` | Provider credentials |
| `config/search.yaml` | Argus search config |
| `.oneshot/config/` | ⚠️ Runtime config (per-project, gitignored) |

---

## Secrets

SOPS/Age encrypted vault at `secrets/`. Age key: `~/.age/key.txt`.

```bash
secrets get KEY
secrets set NAME KEY=value [--commit]
secrets list
```

Use `/secrets` skill from Claude Code. Never commit plaintext.

---

## Janitor

Runs automatically via hooks + daily cron (3am UTC on homelab). Cost: $0 (openrouter/free).

**Signals** in `.janitor/`:

| Signal | File |
|---|---|
| Test gaps | `test-gaps.json` |
| Code smells | `code-smells.json` |
| Config drift | `config-drift.json` |
| Dependency map | `dep-graph.json` |
| Doc staleness | `doc-staleness.json` |
| Knowledge risk | `knowledge-risk.json` |
| Onboarding | `onboarding.md` |
| Patterns | `patterns.json` |

Hooks write to `events.jsonl`; cron runs summarizer + hygiene. Files: `core/janitor/worker.py`, `recorder.py`, `jobs.py`

---

## Project Structure

```
config/            # YAML routing policy
core/              # Router, dispatch, janitor, schemas
oneshot_cli/       # Click CLI
docs/instructions/ # Operator instructions
.claude/rules/     # Thin imports to docs/
.claude/skills/    # 15 skills
templates/         # TASK_SPEC.md, schemas, j2 templates
secrets/           # SOPS/Age vault
scripts/           # Build, eval, maintenance
eval/              # Benchmarks, traces
bin/oneshot        # Entry-point wrapper
```

---

## Known Limitations

- **GLM/ZAI expiry** — `glm_claude` plan expired 2026-05-02; worker self-disables. Use `codex`, `gemini_cli`, or `manus`.
- **OpenCode Go** — `ocg_minimax`/`ocg_api` require `OPENCODE_GO_API_KEY`.
- **`oc` wrapper** — only installed if `scripts/oc` exists locally.
- **Cross-repo memory** — SQLite-backed; reports degraded mode when unavailable.
- **Janitor LLM jobs** — need `OPENROUTER_API_KEY`. Pure-compute jobs run without it.

---

## License

MIT
