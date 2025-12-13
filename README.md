# ONE_SHOT

**The $0 AI Build System.** Single curl. 28 skills. Builds anything.

```bash
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
```

---

## What Happens

One curl drops these files into your project:

| File | Purpose |
|------|---------|
| `AGENTS.md` | Orchestration rules for AI agents |
| `CLAUDE.md` | Project instructions (supplements existing) |
| `TODO.md` | Task tracking ([todo.md](https://github.com/todomd/todo.md) format) |
| `LLM-OVERVIEW.md` | Project context for any LLM |
| `.claude/skills/` | 28 predetermined workflows |
| `.sops.yaml` | Secrets encryption config |

**Non-destructive**: Existing files are supplemented, never overwritten.

---

## How It Works

```
You                          AI Agent
 │                              │
 ├─ curl oneshot.sh ──────────► │ Files installed
 │                              │
 ├─ "Build me a CLI for..."     │
 │                              ├─► Reads CLAUDE.md
 │                              ├─► Reads AGENTS.md (orchestration)
 │                              ├─► Routes to skills
 │                              │
 ◄─── Questions (5 min) ────────┤
 │                              │
 ├─ Answers ───────────────────►│
 │                              ├─► Generates PRD
 ◄─── "Approve PRD?" ───────────┤
 │                              │
 ├─ "Approved" ────────────────►│
 │                              ├─► Autonomous build
 │                              ├─► Updates TODO.md
 │                              ├─► Commits after each feature
 │                              │
 ◄─── "Done!" ──────────────────┤
```

**Your time**: ~5 minutes of questions, then walk away.

---

## Key Features

### Thinking Modes
Activate deeper analysis:
- `think` - quick sanity check
- `think hard` - trade-off analysis
- `ultrathink` - architecture decisions
- `super think` - system-wide design
- `mega think` - strategic decisions

### Plan Workflow
Structured implementation with context preservation:
```
/create_plan     → Generate implementation plan
/implement_plan  → Execute plan systematically
/create_handoff  → Save context before clearing
/resume_handoff  → Continue where you left off
```

### 28 Skills
Pre-built workflows for common tasks:
- **Build**: `oneshot-core`, `feature-planner`, `api-designer`
- **Debug**: `debugger`, `test-runner`, `code-reviewer`
- **Deploy**: `push-to-cloud`, `ci-cd-setup`, `docker-composer`
- **Context**: `create-handoff`, `resume-handoff`, `thinking-modes`

---

## Quick Start

### 1. Install (one-time)
```bash
# Optional: Set up secrets encryption
sudo apt install age  # or: brew install age
mkdir -p ~/.age && age-keygen -o ~/.age/key.txt
```

### 2. Add to Any Project
```bash
cd your-project
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
```

### 3. Open in Claude Code
Claude automatically reads `CLAUDE.md` → `AGENTS.md` and knows what to do.

### 4. Say What You Want
```
"Build me a task management CLI in Python"
"Add user authentication to this app"
"Debug why the tests are failing"
```

---

## Commands

| Command | What It Does |
|---------|--------------|
| `(ONE_SHOT)` | Re-anchor to orchestration rules |
| `ultrathink` | Deep analysis mode |
| `/create_plan` | Start structured planning |
| `/create_handoff` | Save context before `/clear` |

---

## File Hierarchy

```
project/
├── CLAUDE.md              ← Claude reads first (your project rules)
│   └── "Read AGENTS.md"   ← Points to orchestrator
├── AGENTS.md              ← Skill routing, build loop
├── TODO.md                ← Track progress (always updated)
├── LLM-OVERVIEW.md        ← Context for any LLM
├── .claude/skills/        ← 28 skills
└── .sops.yaml             ← Secrets config
```

---

## Core Principles

1. **Non-Destructive**: Only adds to projects, never overwrites
2. **User Time is Precious**: 5 min questions → autonomous build
3. **$0 Infrastructure**: Homelab, OCI Free Tier, no lock-in
4. **Skills Over Scripts**: Predetermined workflows, not reinvention
5. **Context Preservation**: Handoffs > auto-compact

---

## Secrets Management

OneShot uses [SOPS](https://github.com/getsops/sops) + [Age](https://github.com/FiloSottile/age) for secrets:

```bash
# Central vault (optional)
sops -d ~/github/secrets-vault/secrets.env.encrypted | grep API_KEY >> .env

# Encrypt project secrets
sops -e .env > .env.encrypted && rm .env

# Decrypt when needed
sops -d .env.encrypted > .env
```

---

## FAQ

**Q: Does this overwrite my existing files?**
A: No. Existing `CLAUDE.md` gets a reference prepended. Existing `TODO.md`, `LLM-OVERVIEW.md` are left alone.

**Q: What if I don't want secrets encryption?**
A: It's optional. Skip the Age key setup - everything else still works.

**Q: Can I add my own skills?**
A: Yes. Create `.claude/skills/my-skill/SKILL.md` following the format in AGENTS.md.

**Q: Does this work with other AI tools?**
A: Yes. Compatible with Claude Code, Cursor, Aider, Gemini CLI, and any tool that reads markdown.

---

## Version

**v5.0** | 28 Skills | $0 Cost

[GitHub](https://github.com/Khamel83/oneshot) | [Issues](https://github.com/Khamel83/oneshot/issues)
