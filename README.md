# ONE_SHOT v14

**Control plane for Claude-first orchestration.** Lane-based routing, Argus search, model-agnostic workers.

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
- **Workers**: Lane-based pool (cheap models via OpenRouter, Codex, Gemini)
- **Search**: Argus broker (SearXNG, Brave, Serper, Tavily, Exa)
- **Instructions**: Single source of truth at `docs/instructions/`

### Lane-Based Routing

Tasks are classified, then routed to lanes:

| Lane | Use Case | Workers |
|------|----------|---------|
| premium | Planning, review | Claude, Codex |
| balanced | Medium implementation | Gemini Flash, Codex, MiniMax |
| cheap | Small tasks, docs, tests | StepFun, MiMo, MiniMax |
| research | Search-heavy tasks | Gemini, Argus |

Config: `config/lanes.yaml`, `config/models.yaml`

### CLI Resolver

```bash
python -m core.router.resolve --class implement_small
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
│   ├── lanes.yaml       # Lane definitions and worker pools
│   ├── models.yaml      # Model capabilities and costs
│   ├── workers.yaml     # Machine placement
│   ├── search.yaml      # Argus search modes
│   └── providers.yaml   # Environment variable mapping
├── core/                # Python schemas and utilities
│   ├── task_schema.py   # Task class definitions
│   └── router/          # Lane policy, model registry, CLI resolver
├── docs/instructions/   # Neutral instruction source (authoritative)
├── .claude/rules/       # Thin imports to docs/instructions/
├── .claude/skills/      # Operator and utility skill prompts
├── .opencode/           # OpenCode adapter (future activation)
├── templates/           # Jinja2 templates for CLAUDE.md/AGENTS.md
└── secrets/             # SOPS/Age encrypted vault
```

---

## Stack Defaults

| Project Type | Stack |
|--------------|-------|
| Web apps | Astro + Cloudflare + Better Auth + Postgres |
| CLIs | Python + Click + SQLite |
| Services | Python + systemd → oci-dev |

---

## Prerequisites

Optional:
```bash
# Codex CLI (adversarial review)
npm install -g @openai/codex

# Gemini CLI (research fallback)
npm install -g @google/gemini-cli && gemini auth login

# Argus (search broker — recommended)
# See https://github.com/Khamel83/argus
```

---

## Updating

```bash
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/oneshot-update.sh | bash
```

---

**v14.0** | Lane-based routing | Argus search plane | [Source](https://github.com/Khamel83/oneshot) | [Issues](https://github.com/Khamel83/oneshot/issues)
