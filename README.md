# ONE_SHOT v14

**Control plane for Claude-first orchestration.** Lane-based routing, parallel dispatch, Argus search.

**[Quick Start](#quick-start)** | **[Skills](#skills)** | **[Architecture](#architecture)**

---

## Quick Start

```bash
cd your-project
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
claude .
```

Then use `/short` for quick iteration, `/full` for structured work, or `/conduct` to orchestrate across models.

---

## Architecture

OneShot is a portable orchestration layer:

- **Control plane**: YAML config + Python schemas + Markdown instructions
- **Planner**: Claude Code (planning, review, repo synthesis)
- **Workers**: Codex and Gemini execute tasks via parallel dispatch
- **Search**: Argus broker (SearXNG, Brave, Serper, Tavily, Exa)
- **Dispatch**: Self-contained prompts → parallel workers → structured output → manifest trail
- **Instructions**: Single source of truth at `docs/instructions/`

### Lane-Based Routing

Tasks are classified, then routed to lanes:

| Lane | Use Case | Workers | Max Parallel |
|------|----------|---------|-------------|
| premium | Planning, review | Claude (inline) | 2 |
| balanced | Medium implementation | Codex, Gemini | 3 |
| cheap | Small tasks, docs, tests | Gemini, Codex | 3 |
| research | Search-heavy tasks | Gemini, Codex + Argus | 3 |

Config: `config/lanes.yaml`, `config/models.yaml`

### Dispatch Protocol

Claude thinks, Codex and Gemini execute. The dispatch protocol (`_shared/dispatch.md`) handles:

1. Classify task → resolve lane
2. Build self-contained prompt (files, criteria, patterns, output format)
3. Dispatch to Codex/Gemini in parallel (up to `max_parallel`)
4. Capture structured output (JSON from both)
5. Validate against acceptance criteria
6. Write manifest to `1shot/dispatch/{id}.md`
7. Retry or escalate on failure

```bash
# Single dispatch
python3 -m core.dispatch.run --class implement_small --prompt "Fix auth bug"

# Parallel batch
python3 -m core.dispatch.run --class implement_small --prompts-file batch.json --parallel 3

# Dry run (show routing without executing)
python3 -m core.dispatch.run --class implement_small --prompt "..." --dry-run
```

### CLI Resolver

```bash
python3 -m core.router.resolve --class implement_small
# → {"task_class": "implement_small", "lane": "cheap", "workers": [...]}
```

---

## Skills

### Operators

| Skill | Description |
|-------|-------------|
| `/short` | Quick iteration — load context, ask, execute |
| `/full` | Structured work — new projects, refactors |
| `/conduct` | Multi-model orchestration — lane-based routing, loops until done |

### Context

| Skill | Description |
|-------|-------------|
| `/handoff` | Save checkpoint before `/clear` |
| `/restore` | Resume from handoff |

### Research & Docs

| Skill | Description |
|-------|-------------|
| `/research` | Background research via Argus (Gemini CLI fallback) |
| `/freesearch` | Zero-token search via Argus cheap mode |
| `/doc` | Cache external docs locally |

### Utilities

| Skill | Description |
|-------|-------------|
| `/vision` | Image/website analysis |
| `/secrets` | SOPS/Age secret management |

---

## Project Structure

```
oneshot/
├── config/              # YAML routing policy
│   ├── lanes.yaml       # Lane definitions, worker pools, max_parallel
│   ├── models.yaml      # Model capabilities and costs
│   ├── workers.yaml     # Machine placement
│   ├── search.yaml      # Argus search modes
│   └── providers.yaml   # Environment variable mapping
├── core/                # Python schemas and utilities
│   ├── task_schema.py   # Task class definitions
│   ├── router/          # Lane policy, model registry, CLI resolver
│   └── dispatch/        # Parallel dispatch runner, output capture, manifests
├── docs/instructions/   # Neutral instruction source (authoritative)
├── .claude/rules/       # Thin imports to docs/instructions/
├── .claude/skills/      # Operator and utility skill prompts
├── .opencode/           # OpenCode adapter (installed, pending auth)
├── templates/           # Jinja2 templates for CLAUDE.md/AGENTS.md
└── secrets/             # SOPS/Age encrypted vault
```

---

## Prerequisites

Required:
```bash
# Claude Code
# Already installed if you're reading this
```

Workers (at least one recommended):
```bash
# Codex CLI (worker — uses ChatGPT Plus OAuth, no API cost)
npm install -g @openai/codex && codex login

# Gemini CLI (worker — uses Google Sign-in, no API cost)
npm install -g @google/gemini-cli && gemini auth login
```

Optional:
```bash
# Argus (search broker — recommended)
# See https://github.com/Khamel83/argus

# OpenCode (additional worker — requires API keys, costs money)
curl -fsSL https://opencode.ai/install | bash
```

---

## Stack Defaults

| Project Type | Stack |
|--------------|-------|
| Web apps | Vercel + Supabase + Python |
| CLIs | Python + Click + SQLite |
| Services | Python + systemd → oci-dev |

Web apps use a single deployment — all sites share one Vercel project and one Supabase project.

### First-time setup (per repo)

```bash
mkdir my-project && cd my-project && git init
oneshot.sh --web <slug> --admin-email <email>
git add -A && git commit && git push -u origin master
# Then import repo into Vercel and add these env vars (from the vault):
#   SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY
# After that: git push auto-deploys
```

### Adding more sites (after first-time setup)

```bash
scripts/new-site.sh <slug> "<name>" --admin-email <email>
git add -A && git commit && git push
```

`oneshot.sh --web <slug>` copies the scaffold from `templates/community-starter/`, pulls Supabase credentials from the vault, and creates the site. All env vars come from the encrypted vault at `secrets/deployments.env.encrypted`.

---

## Updating

```bash
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/oneshot-update.sh | bash
```

---

**v14.1** | Parallel dispatch | Codex + Gemini workers | [Source](https://github.com/Khamel83/oneshot) | [Issues](https://github.com/Khamel83/oneshot/issues)
