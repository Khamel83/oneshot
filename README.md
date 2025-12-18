# ONE_SHOT

**The $0 AI Build System.** Single curl. 25 skills. 4 agents. Builds anything.

[![CI](https://github.com/Khamel83/oneshot/actions/workflows/ci.yml/badge.svg)](https://github.com/Khamel83/oneshot/actions/workflows/ci.yml)

```bash
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
```

---

## What Happens

One curl drops these files into your project:

| File | Purpose |
|------|---------|
| `AGENTS.md` | **Skill & agent routing** - triggers the right skill/agent for what you say |
| `CLAUDE.md` | Project instructions (supplements existing, never overwrites) |
| `TODO.md` | Task tracking ([todo.md](https://github.com/todomd/todo.md) format) |
| `LLM-OVERVIEW.md` | Project context for any LLM |
| `.claude/skills/` | 25 skills (synchronous, shared context) |
| `.claude/agents/` | 4 native sub-agents (isolated context, background) |
| `.beads/` | Persistent task tracking (optional, if beads installed) |

**Non-destructive**: Existing files are supplemented, never overwritten.

---

## How Skills Get Triggered

AGENTS.md contains a **skill router** that matches what you say to the right skill:

| You Say | Skill Triggered | What Happens |
|---------|-----------------|--------------|
| "build me a CLI..." | `oneshot-core` | Questions → PRD → autonomous build |
| "plan the feature..." | `create-plan` | Structured planning with decisions |
| "implement the plan" | `implement-plan` | Systematic execution with commits |
| "it's broken / fix..." | `debugger` | Systematic debugging |
| "deploy to cloud" | `push-to-cloud` | OCI/cloud deployment |
| "ultrathink about..." | `thinking-modes` | Deep analysis with expert perspectives |
| "save context" | `create-handoff` | Preserve state before `/clear` |
| "resume from handoff" | `resume-handoff` | Continue exactly where you left off |
| "ready tasks / beads" | `beads` | Persistent task tracking across sessions |

---

## The 25 Skills

| Category | Skills | Purpose |
|----------|--------|---------|
| **Core** | `oneshot-core`, `failure-recovery`, `thinking-modes` | Orchestration, recovery, cognition |
| **Planning** | `create-plan`, `implement-plan`, `api-designer` | Design before building |
| **Context** | `create-handoff`, `resume-handoff`, `beads` | Session persistence, cross-session memory |
| **Development** | `debugger`, `test-runner`, `code-reviewer`, `refactorer`, `performance-optimizer` | Build & quality |
| **Operations** | `git-workflow`, `push-to-cloud`, `ci-cd-setup`, `docker-composer`, `observability-setup` | Deploy & maintain |
| **Data & Docs** | `database-migrator`, `documentation-generator`, `secrets-vault-manager`, `secrets-sync` | Support |
| **Communication** | `the-audit` | Strategic communication filter |
| **Agent Bridge** | `delegate-to-agent` | Route to native sub-agents |

**Why 25?** Consolidated skills, each does one thing well. Added beads for persistent memory.

---

## The 4 Agents

Native Claude Code sub-agents with **isolated context windows**:

| Agent | Model | Purpose |
|-------|-------|---------|
| `security-auditor` | sonnet | OWASP/secrets/auth security review |
| `deep-research` | haiku | Long codebase exploration |
| `background-worker` | haiku | Parallel test/build execution |
| `multi-agent-coordinator` | sonnet | Multi-agent orchestration |

### Skills vs Agents

| Aspect | Skills | Agents |
|--------|--------|--------|
| **Context** | Shared with main conversation | Isolated window |
| **Best for** | Quick, synchronous tasks | Long research, background work |
| **Model** | Inherits from session | Configurable per agent |

**When to use agents:**
- Task would read 10+ files (prevents context pollution)
- Security audit requiring isolation
- Long-running operations (tests, builds)
- Parallel exploration of multiple areas

---

## Thinking Modes

Activate deeper analysis:

| Level | Say This | Use For |
|-------|----------|---------|
| Think | "think about..." | Quick sanity check |
| Think Hard | "think hard about..." | Trade-off analysis |
| Ultrathink | "ultrathink..." | Architecture decisions |
| Super Think | "super think..." | System-wide design |
| Mega Think | "mega think..." | Strategic decisions |

> **Pro tip**: "ultrathink please do a good job" for maximum depth

---

## Plan Workflow

For complex implementations:

```
/create_plan [idea]      → thoughts/shared/plans/YYYY-MM-DD-desc.md
  └─ answer questions, get approval

/implement_plan @[plan]  → systematic execution with commits
  └─ context getting low?

/create_handoff          → thoughts/shared/handoffs/YYYY-MM-DD.md
  └─ /clear

/resume_handoff @[file]  → continue exactly where left off
```

**Why handoffs > auto-compact**: Explicit control, versioned, no context loss.

---

## Persistent Tasks (Beads)

Optional but powerful: [beads](https://github.com/steveyegge/beads) provides git-backed task tracking that survives sessions.

### Install (Optional)
```bash
npm install -g @beads/bd
```

### What Beads Adds

| Feature | TODO.md | Beads |
|---------|---------|-------|
| Session persistence | No | Yes (git-backed) |
| Dependencies | No | Full graph |
| Multi-agent safe | Conflicts | Hash-based IDs |
| Ready detection | Manual | `bd ready` |

### Key Commands
```bash
bd ready --json       # See unblocked tasks
bd create "Task" -p 1 # Create task (priority 1)
bd sync               # Push/pull (CRITICAL before session end)
```

### Workflow
1. Start session: `bd sync && bd ready --json`
2. Claim work: `bd update <id> --status in_progress`
3. Complete: `bd close <id> --reason "Done"`
4. End session: `bd sync` (always!)

**Why use both?** TODO.md for immediate visibility, beads for cross-session persistence.

---

## Quick Start

### 1. Add to Any Project
```bash
cd your-project
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
```

### 2. Open in Claude Code
Claude reads `CLAUDE.md` → `AGENTS.md` automatically.

### 3. Say What You Want
```
"Build me a task management CLI in Python"
"Add user authentication to this app"
"Debug why the tests are failing"
"ultrathink about the architecture"
```

---

## Upgrading

### Update to Latest Version

Re-run the bootstrap to get latest AGENTS.md and any new skills:
```bash
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
```

### Full Upgrade (Update All Skills)

Use `--upgrade` to overwrite existing skills with latest versions:
```bash
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash -s -- --upgrade
```

### What Gets Updated

| File | Normal | --upgrade |
|------|--------|-----------|
| `AGENTS.md` | Always | Always |
| `CLAUDE.md` ONE_SHOT block | Always | Always |
| Missing skills/agents | Added | Added |
| Existing skills/agents | Skipped | **Updated** |
| `TODO.md`, `LLM-OVERVIEW.md` | Never | Never |
| Your custom skills/agents | Never | Never |

**Note**: Custom skills and agents are never touched.

---

## File Hierarchy

```
project/
├── CLAUDE.md              ← Claude reads first
│   └── "Read AGENTS.md"   ← Points to skill/agent router
├── AGENTS.md              ← Skill & agent routing rules
├── TODO.md                ← Always updated during work
├── LLM-OVERVIEW.md        ← Project context
├── .claude/skills/        ← 25 skills
├── .claude/agents/        ← 4 native sub-agents
└── .beads/                ← Persistent tasks (optional)
```

**Important info at the top**: AGENTS.md puts the routers FIRST so they're in the early context window.

---

## Core Principles

1. **Non-Destructive**: Only adds, never overwrites
2. **Skills Always Triggered**: CLAUDE.md → AGENTS.md routing ensures skills fire
3. **TODO.md Always Updated**: Every task state change
4. **Context Preservation**: Handoffs > auto-compact
5. **$0 Infrastructure**: Homelab, OCI Free Tier, no lock-in

---

## Commands

| Command | What It Does |
|---------|--------------|
| `(ONE_SHOT)` | Re-anchor to skill routing rules |
| `/create_plan` | Start structured planning |
| `/create_handoff` | Save context before `/clear` |
| `ultrathink` | Deep analysis mode |

---

## FAQ

**Q: Does this overwrite my existing CLAUDE.md?**
A: No. It prepends a skill routing reference. Your content stays.

**Q: What if a skill doesn't trigger?**
A: Say `(ONE_SHOT)` to re-anchor, then try clearer trigger words.

**Q: Can I add my own skills?**
A: Yes. Create `.claude/skills/my-skill/SKILL.md`.

**Q: Works with other AI tools?**
A: Yes. Claude Code, Cursor, Aider, Gemini CLI - anything that reads markdown.

---

## Version

**v5.5** | 25 Skills | 4 Agents | $0 Cost | Non-Destructive

[GitHub](https://github.com/Khamel83/oneshot) | [Issues](https://github.com/Khamel83/oneshot/issues)

---

## Secrets Management

Encrypted secrets are stored in `secrets/` using [SOPS](https://github.com/getsops/sops) + [Age](https://github.com/FiloSottile/age).

### Setup (One Time)

```bash
# Install Age
sudo apt install age  # or: brew install age

# Generate key (save backup in 1Password)
mkdir -p ~/.age
age-keygen -o ~/.age/key.txt

# Export for SOPS
export SOPS_AGE_KEY_FILE=~/.age/key.txt
```

### Using Secrets

```bash
# Decrypt to use
sops -d secrets/homelab.env.encrypted > .env

# Encrypt after editing
sops -e .env > secrets/homelab.env.encrypted

# Edit in-place (decrypts, opens editor, re-encrypts)
sops secrets/homelab.env.encrypted
```

### Available Secret Files

| File | Contents |
|------|----------|
| `secrets/homelab.env.encrypted` | Homelab service credentials |
| `secrets/secrets.env.encrypted` | General API keys |

**Safe to commit**: Only encrypted files (`.encrypted`) are tracked. Plaintext `.env` files are gitignored.

---

## Research & Similar Projects

- [steveyegge/beads](https://github.com/steveyegge/beads) - Git-backed persistent task tracking (integrated in v5.5)
- [wshobson/agents](https://github.com/wshobson/agents) - 91 agents, 47 skills, plugin architecture
- [ruvnet/claude-flow](https://github.com/ruvnet/claude-flow) - Enterprise orchestration with hive-mind
- [Anthropic Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - Official guidance

OneShot is **lightweight files** vs heavyweight frameworks. Different philosophy, both valid.
