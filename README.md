# ONE_SHOT v13

**Operator framework for Claude Code.** Three operators, seven utilities. Discover skills on demand.

**[Quick Start](#quick-start)** | **[Skills](#skills)** | **[Full Docs](docs/SKILLS.md)**

---

## Quick Start

```bash
# 1. In your project
cd your-project

# 2. Install
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash

# 3. Start Claude Code
claude .
```

Then use `/short` for quick iteration, `/full` for structured work, or `/conduct` to orchestrate across models.

---

## How It Works

**Progressive disclosure** - Rules load based on your project type:

| Your Project | Detects | Loads |
|--------------|---------|-------|
| Web app | `astro.config.*` or `wrangler.toml` | Core + Web rules |
| CLI | `setup.py` or `pyproject.toml` | Core + CLI rules |
| Service | `*.service` | Core + Service rules |
| Anything else | — | Core rules only |

~300 tokens always loaded (down from ~2000 in older versions).

---

## Skills

Skills live in `~/.claude/skills/` and are invoked as slash commands. Claude also discovers and applies them automatically based on context.

### Operators (3)

| Skill | Description |
|-------|-------------|
| [`/short`](docs/SKILLS.md#short) | Quick iteration - load context, ask, execute |
| [`/full`](docs/SKILLS.md#full) | Structured work - new projects, refactors |
| [`/conduct`](docs/SKILLS.md#conduct) | Multi-model PMO orchestrator - routes across Claude + Codex + Gemini, loops until done |

### Context (2)

| Skill | Description |
|-------|-------------|
| [`/handoff`](docs/SKILLS.md#handoff) | Save checkpoint before `/clear` |
| [`/restore`](docs/SKILLS.md#restore) | Resume from handoff |

### Research & Docs (3)

| Skill | Description |
|-------|-------------|
| [`/research`](docs/SKILLS.md#research) | Background research via Gemini CLI |
| [`/freesearch`](docs/SKILLS.md#freesearch) | Zero-token web search (Exa API) |
| [`/doc`](docs/SKILLS.md#doc) | Cache external docs locally |

### Utilities (2)

| Skill | Description |
|-------|-------------|
| [`/vision`](docs/SKILLS.md#vision) | Image/website analysis |
| [`/secrets`](docs/SKILLS.md#secrets) | SOPS/Age secret management |

---

## Stack Defaults

| Project Type | Stack |
|--------------|-------|
| Web apps | Astro + Cloudflare Pages/Workers + Better Auth + Postgres on OCI |
| CLIs | Python + Click + SQLite |
| Services | Python + systemd → oci-dev |
| Heavy compute | Route to macmini |
| Large storage | Route to homelab |

---

## Project Structure

After installation:

```
your-project/
├── AGENTS.md           # Operator spec (curl from oneshot, read-only)
└── CLAUDE.md           # Your project-specific instructions
```

Global config (installed once):

```
~/.claude/
├── CLAUDE.md           # Core identity
├── rules/              # Progressive disclosure rules
│   ├── core.md         # Always loaded
│   ├── web.md          # Web apps
│   ├── cli.md          # CLIs
│   └── service.md      # Services
├── skills/             # Skills (10 + 1 external)
└── tasks/              # Native task storage
```

---

## Key Files

| File | Purpose |
|------|---------|
| [AGENTS.md](AGENTS.md) | Operator behaviors and decision defaults |
| [CLAUDE.md](CLAUDE.md) | Your project-specific instructions |
| [docs/SKILLS.md](docs/SKILLS.md) | Full command reference |
| [.claude/rules/](.claude/rules/) | Progressive disclosure rules |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

## Prerequisites

```bash
# Optional: Gemini CLI (for /research)
npm install -g @google/gemini-cli && gemini auth login
```

---

## Secrets (SOPS/Age)

ONE_SHOT uses SOPS + Age for encrypted secrets. Age key at `~/.age/key.txt`.

**On new machines:**
```bash
# Copy age key from existing machine
scp user@known-machine:~/.age/key.txt ~/.age/key.txt

# Verify decryption works
sops -d secrets/research_keys.env.encrypted
```

---

## Documentation Cache

Link cached external docs to any project:

```bash
docs-link add polymarket astro cloudflare  # Link docs
docs-link list                              # Show linked
docs-link available                         # Show all cached
```

Creates symlinks in `docs/external/` → `~/github/docs-cache/`.

---

## Heartbeat Scripts

Automatic maintenance (run via systemd or cron):

| Script | Purpose |
|--------|---------|
| `heartbeat.sh` | Periodic maintenance |
| `check-oneshot.sh` | Verify ONE_SHOT is up to date |
| `check-apis.sh` | Check API keys and services |

```bash
~/.claude/scripts/heartbeat-install.sh
```

---

## Updating

```bash
# From any project
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/oneshot-update.sh | bash

# Or force reinstall
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Skill not working | Check `~/.claude/skills/` |
| Rules not loading | Check `~/.claude/rules/` exists |
| Lost context | `/restore` or say "resume" |
| Tasks not persisting | Check `~/.claude/tasks/` exists |

---

**v13.2** | 10+1 skills | Operators discover skills on demand | [Source](https://github.com/Khamel83/oneshot) | [Issues](https://github.com/Khamel83/oneshot/issues)
