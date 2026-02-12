# ONE_SHOT v10.3

**Your personal Claude Code configuration.**

---

## What ONE_SHOT Is

ONE_SHOT makes Claude Code work the way you want across all your projects:

- **Progressive disclosure** - Rules load by project type (~300 tokens vs 2000)
- **Slash commands** - Invoke when needed (/interview, /cp, /implement, /freesearch...)
- **Persistent tracking** - Beads survives /clear, restarts, disconnections
- **Wait for native** - Aligns with Claude's built-in features, doesn't duplicate them

---

## Quick Start (3 Steps)

```bash
# 1. In your project directory
cd your-project

# 2. Install ONE_SHOT
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash

# 3. Open in Claude Code
claude .

# Then say: "Build me [thing you want]"
```

---

## What Changed (v9 → v10.2)

### v9: Framework with 50+ Skills
- AGENTS.md routing table
- 52 skills auto-loaded
- Hooks injecting context
- ~5,800 tokens always-on
- "Build me X" triggered interview automatically

### v10: Personal Configuration (~93% token reduction)
- Removed AGENTS.md routing
- 16 slash commands (invoke when needed)
- 7 rules always loaded (~410 tokens)
- You type `/interview` when you want structure

### v10.1: Progressive Disclosure (+85% token savings)
- Rules split by project type (web, cli, service)
- Auto-detection from files
- ~300 tokens vs ~2000 in v9

### v10.2: Work Discipline + Beads Tightening
- Work discipline principles (plan first, commit per task, keep tasks small)
- Beads operational rules (session start/end prompts, blocked/big bead handling)
- beads_viewer (`bv`) as recommended TUI
- "Wait for Native" strategy — use beads now, switch to Claude native when it ships

---

## Slash Commands

| Command | What It Does |
|---------|--------------|
| `/interview` | Structured interview (triage → questions → spec) |
| `/cp` | Continuous planner (3-file: task_plan.md, findings.md, progress.md) |
| `/implement` | Execute plan with beads tracking |
| `/stack-setup` | Configure Astro + Cloudflare + Postgres stack |
| `/freesearch` | Research via Exa API (zero Claude tokens) |
| `/research` | Background research via Gemini CLI |
| `/think` | Multi-perspective analysis |
| `/diagnose` | Hypothesis-based debugging |
| `/codereview` | OWASP + quality review |
| `/deploy` | Deploy to oci-dev |
| `/remote` | Execute on homelab/macmini |
| `/audit` | Strategic communication filter |
| `/beads` | Persistent task tracking |
| `/handoff` | Save context before /clear |
| `/restore` | Resume from handoff |
| `/secrets` | SOPS/Age secret management |
| `/sessions` | View/search encrypted session logs |
| `/batch` | Parallel multi-file operations |

---

## Documentation Cache (docs-link)

Link cached external docs to any project:

```bash
cd your-project
docs-link add polymarket astro cloudflare tailscale  # Link docs
docs-link list                              # Show linked docs
docs-link available                         # Show all cached docs
```

Creates symlinks in `docs/external/` pointing to central cache at `~/github/docs-cache/`.

**Benefits:**
- Instant access to cached docs (no WebSearch needed)
- Saves Claude token quota
- Works offline
- Version-controlled documentation

---

## How It Works

### Progressive Disclosure

Rules load based on what you're working on:

| Project Type | Trigger | Rules Loaded |
|--------------|---------|--------------|
| Web app | `astro.config.*` or `wrangler.toml` | Core + Web rules |
| CLI | `setup.py` or `pyproject.toml` | Core + CLI rules |
| Service | `*.service` | Core + Service rules |
| Generic | Nothing detected | Core rules only |

### Session Workflow

```
You say what you want
    ↓
Claude reads relevant rules (~300 tokens)
    ↓
You invoke commands when needed (/interview, /cp, etc.)
    ↓
Progress tracked in beads (survives everything)
```

---

## Project Structure

After installation:

```
your-project/
├── AGENTS.md           # Skill router (curl from oneshot, read-only)
├── CLAUDE.md           # Your project-specific instructions
└── .beads/             # Persistent task tracking
```

Global config (installed once):

```
~/.claude/
├── CLAUDE.md           # Core identity
├── rules/              # Progressive disclosure rules
│   ├── core.md         # Always loaded
│   ├── web.md          # Web apps (Astro + Cloudflare + Better Auth + Postgres)
│   ├── cli.md          # CLIs (Python + Click)
│   └── service.md      # Services (Python + systemd)
└── commands/           # Slash commands (16 total)
```

---

## Task Tracking (Beads)

```bash
bd ready      # "What's next?" → Shows unblocked tasks
bd list       # All tasks with status
bd show 42    # Details of task #42
bd sync       # Save to git
```

Tasks survive `/clear`, restarts, disconnections.

---

## Prerequisites

```bash
# Required: Beads (task tracking)
npm install -g @beads/bd

# Required: docs-link (documentation cache manager)
# Installed via install.sh to ~/.local/bin/docs-link

# Optional: Gemini CLI (for background research)
npm install -g @google/gemini-cli
gemini auth login
```

---

## Updating ONE_SHOT

```bash
# Update your project
cd your-project
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash -s -- --upgrade

# Update the oneshot repo itself
cd ~/github/oneshot
git pull origin master
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Command not working | Check it's in `~/.claude/commands/` |
| Rules not loading | Check `~/.claude/rules/` exists |
| Lost context after `/clear` | Say "resume" or `/restore` |
| Beads not found | `npm install -g @beads/bd` |

---

## v9 vs v10.2 Comparison

See [V9-TO-V10.1.md](V9-TO-V10.1.md) for detailed comparison.

---

## Links

- **GitHub**: https://github.com/Khamel83/oneshot
- **Beads**: https://github.com/steveyegge/beads
- **Progressive Disclosure**: [.claude/rules/README.md](.claude/rules/README.md)

---

**v10.3** | New Stack (Astro + CF Pages/Workers + Better Auth + Postgres) | Progressive Disclosure | Slash Commands | Beads
