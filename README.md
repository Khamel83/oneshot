# ONE_SHOT v12

**Your personal Claude Code configuration.**

One install gives you: progressive disclosure rules, slash commands, native task tracking, intelligent delegation, and swarm mode.

**[Quick Start](#quick-start)** | **[All Commands](#slash-commands)** | **[What's New](#whats-new)** | **[Full Docs](docs/SKILLS.md)**

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

Then just describe what you're working on. ONE_SHOT loads the right rules automatically.

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

## Slash Commands

Click any command for full documentation.

### Planning & Execution

| Command | Description |
|---------|-------------|
| [`/interview`](docs/SKILLS.md#interview) | Structured requirements gathering before coding |
| [`/cp`](docs/SKILLS.md#cp-continuous-planner) | Living 3-file plan that survives `/clear` |
| [`/run-plan`](docs/SKILLS.md#run-plan) | Execute plan from `task_plan.md` step-by-step |
| [`/implement`](docs/SKILLS.md#implement) | Execute plan with native task tracking |

### Context & Recovery

| Command | Description |
|---------|-------------|
| [`/handoff`](docs/SKILLS.md#handoff) | Save checkpoint before `/clear` |
| [`/restore`](docs/SKILLS.md#restore) | Resume from handoff |
| [`/sessions`](docs/SKILLS.md#sessions) | Browse encrypted session history |

### Task Tracking

| Command | Description |
|---------|-------------|
| Native Tasks | Built-in: `TaskCreate`, `TaskList`, `TaskUpdate`, `TaskGet` |
| [`/beads`](docs/SKILLS.md#beads-️-deprecated) | Legacy CLI-based tracking (deprecated) |

### Debugging & Quality

| Command | Description |
|---------|-------------|
| [`/diagnose`](docs/SKILLS.md#diagnose) | Hypothesis-based debugging |
| [`/codereview`](docs/SKILLS.md#codereview) | OWASP + quality review |

### Research & Docs

| Command | Description |
|---------|-------------|
| [`/research`](docs/SKILLS.md#research) | Background research via Gemini CLI |
| [`/freesearch`](docs/SKILLS.md#freesearch) | Zero-token web search via Exa API |
| [`/doc`](docs/SKILLS.md#doc) | Cache external docs locally |
| [`/skill-discovery`](docs/SKILLS.md#skill-discovery) | Find skills matching your goal |

### Multi-File & Remote

| Command | Description |
|---------|-------------|
| [`/batch`](docs/SKILLS.md#batch) | Parallel operations across 10+ files |
| [`/remote`](docs/SKILLS.md#remote) | Execute on homelab/macmini via SSH |

### Delegation (v12.2)

| Command | Description |
|---------|-------------|
| [`/delegation-log`](docs/SKILLS.md#delegation-log) | View delegation audit trail |
| [`/delegation-trajectory`](docs/SKILLS.md#delegation-trajectory) | See session execution paths |
| [`/delegation-stats`](docs/SKILLS.md#delegation-stats) | Reward-weighted performance stats |

### Parallel Work

| Command | Description |
|---------|-------------|
| [`/swarm`](docs/SKILLS.md#swarm) | Multi-agent teams (experimental) |

### Utilities

| Command | Description |
|---------|-------------|
| [`/think`](docs/SKILLS.md#think) | Multi-perspective analysis |
| [`/audit`](docs/SKILLS.md#audit) | Strategic communication filter |
| [`/secrets`](docs/SKILLS.md#secrets) | SOPS/Age secret management |
| [`/stack-setup`](docs/SKILLS.md#stack-setup) | Configure Astro + Cloudflare + Postgres |
| [`/update`](docs/SKILLS.md#update) | Update ONE_SHOT from GitHub |
| [`/vision`](.claude/commands/vision.md) | Visual inspection via MCP |

---

## What's New

### v12.2 (2026-02-19)
- **Agent Lightning integration** - Delegation spans with `span_id`, `session_id`, `tool_sequence`, `reward`
- **New commands**: `/delegation-log`, `/delegation-trajectory`, `/delegation-stats`
- **Credit assignment** - See which delegations helped vs. bottlenecked

### v11.0 (2026-02-13)
- **Native Tasks** - Built-in `TaskCreate`/`TaskList`/`TaskUpdate` (Beads deprecated)
- **/swarm** - Multi-agent team orchestration

### v10.3 (2026-02-12)
- **New stack** - Astro + Cloudflare + Better Auth + Postgres (replaced Convex+Next.js)

[Full changelog →](CHANGELOG.md)

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
├── AGENTS.md           # Skill router (curl from oneshot, read-only)
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
├── commands/           # Slash commands
└── tasks/              # Native task storage (persistent)
```

---

## Key Files

| File | Purpose |
|------|---------|
| [AGENTS.md](AGENTS.md) | Skill routing (LLM-only, curl from repo) |
| [CLAUDE.md](CLAUDE.md) | Your project-specific instructions |
| [docs/SKILLS.md](docs/SKILLS.md) | Full command reference |
| [.claude/rules/](.claude/rules/) | Progressive disclosure rules |
| [.claude/commands/](.claude/commands/) | Slash command definitions |
| [CHANGELOG.md](CHANGELOG.md) | Version history |

---

## Prerequisites

```bash
# Optional: Gemini CLI (for /research)
npm install -g @google/gemini-cli && gemini auth login

# Optional: Beads CLI (legacy task tracking)
npm install -g @beads/bd
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

Encrypted files in `secrets/`:
- `research_keys.env.encrypted` - API keys (ZAI, Exa, Tavily, etc.)
- `homelab.env.encrypted` - Homelab credentials
- `*.env.encrypted` - Project-specific secrets

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
/update

# Or force reinstall
curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/oneshot-update.sh | bash -s -- force
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Command not working | Check `~/.claude/commands/` |
| Rules not loading | Check `~/.claude/rules/` exists |
| Lost context | `/restore` or say "resume" |
| Tasks not persisting | Check `~/.claude/tasks/` exists |
| Beads not found | `npm install -g @beads/bd` |

---

**v12.2** | [Source](https://github.com/Khamel83/oneshot) | [Issues](https://github.com/Khamel83/oneshot/issues)
