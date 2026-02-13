# ONE_SHOT v10.4

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

## How to Use ONE_SHOT

### Daily Workflow

1. **Start a session** → Claude reads your project's rules automatically
2. **Say what you want** → "Build me a weather CLI", "Fix the login bug"
3. **Track progress** → Tasks saved in `.beads/`, survives everything
4. **Use slash commands** → When you need structure: `/interview`, `/cp`, `/diagnose`

### Key Commands

| You Say | What Happens |
|---------|--------------|
| "Build me X" | Claude plans and builds |
| `/interview` | Structured requirements gathering |
| `/cp` | Continuous planner (3-file pattern) |
| `/implement` | Execute plan with beads tracking |
| `/diagnose` | Hypothesis-based debugging |
| `/stack-setup` | Configure Astro + Cloudflare + Postgres |
| `/deploy` | Deploy to oci-dev |

### Check Scripts (Automated)

ONE_SHOT includes heartbeat scripts that run periodically to keep your setup current:

| Script | Purpose |
|--------|---------|
| `heartbeat.sh` | Periodic maintenance (run via systemd or cron) |
| `check-oneshot.sh` | Verify ONE_SHOT is up to date |
| `check-apis.sh` | Check API keys and services |

Install heartbeat with 23-hour rate limiting:
```bash
~/.claude/scripts/heartbeat-install.sh
```

### Stack Defaults

ONE_SHOT uses opinionated defaults (don't ask, just use):

| Project Type | Stack |
|--------------|-------|
| Web apps | Astro + Cloudflare Pages/Workers + Better Auth + Postgres on OCI |
| CLIs | Python + Click + SQLite |
| Services | Python + systemd → oci-dev |
| Heavy compute | Route to macmini |
| Large storage | Route to homelab |

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

## Secrets (SOPS/Age)

ONE_SHOT uses SOPS + Age for encrypted secrets. The age key is at `~/.age/key.txt` and SOPS config is at `.sops.yaml`.

**On new machines:**
```bash
# Copy age key from existing machine
scp user@known-machine:~/.age/key.txt ~/.age/key.txt

# Then verify decryption works
sops -d secrets/research_keys.env.encrypted
```

**Encrypted files:**
- `secrets/research_keys.env.encrypted` - API keys (ZAI, Exa, Tavily, Apify, Context7)
- `secrets/homelab.env.encrypted` - Homelab credentials
- `secrets/*.env.encrypted` - Project-specific secrets

---

## Updating ONE_SHOT

**Works from ANY version - even if your install is broken:**

```
run curl -sSL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/oneshot-update.sh | bash -s -- force
```

Or just say to Claude:
```
curl the oneshot updater and run it with force
```

**If you have the command installed:**
```bash
oneshot-update force    # Update + sync to current project
oneshot-update status   # Check current version
```

**From Claude Code:**
```
/update
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

## Version History

See [CHANGELOG.md](CHANGELOG.md) for detailed changes.

---

## Links

- **GitHub**: https://github.com/Khamel83/oneshot
- **Beads**: https://github.com/steveyegge/beads
- **Progressive Disclosure**: [.claude/rules/README.md](.claude/rules/README.md)

---

**v10.4** | Check scripts + Heartbeat installer | Progressive Disclosure | Slash Commands | Beads
