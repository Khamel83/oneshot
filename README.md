# ONE_SHOT v8.1

**Tell it an idea. Come back with the thing built.**

A skill system for [Claude Code](https://claude.com/claude-code) that provides persistent task tracking, autonomous execution, multi-model CLI orchestration, and Gemini-powered research—all while minimizing Claude token usage through aggressive delegation.

---

## What Is ONE_SHOT?

ONE_SHOT turns Claude Code into a full autonomous development environment. It's not just a collection of prompts—it's a coordinated system of 43+ skills that:

- **Interviews you** to understand requirements (front-door)
- **Creates structured plans** for complex work (create-plan)
- **Tracks tasks persistently** across sessions (beads)
- **Executes autonomously** in background tmux sessions (resilient-executor)
- **Routes to specialized AI CLIs** to save tokens (dispatch)
- **Researches for free** via Gemini CLI (freesearch)
- **Recovers from failures** automatically (failure-recovery)

**Philosophy**: Context is scarce. Delegate aggressively. Write state to disk. Survive disconnections.

---

## Quick Start

### Prerequisites

```bash
# 1. Install beads (REQUIRED for task tracking)
npm install -g @beads/bd

# 2. Install Gemini CLI (for free research)
npm install -g @google/gemini-cli
gemini auth login
```

### Installation

```bash
# In your project directory
cd your-project
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
```

This creates:
```
your-project/
├── AGENTS.md           ← Skill router & orchestration
├── CLAUDE.md           ← Project-specific instructions
├── .beads/             ← Persistent task tracking
└── .claude/skills/     ← 43+ skills (symlinked from ~/.claude/skills/oneshot)
```

### Your First Build

```bash
# Open in Claude Code
claude .

# Say:
"build me a task manager CLI in Python"
```

Claude will:
1. Ask you targeted questions (front-door skill)
2. Create a structured implementation plan
3. Build it with persistent task tracking
4. Survive /clear, restarts, and disconnections

---

## Update ONE_SHOT

**Single command—always gets latest v8:**

```bash
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/upgrade-v8.sh | bash
```

This updates AGENTS.md, skills, and compresses context to ~2k tokens.

---

## Core Skills (What You Say)

| Say This | Skill | What Happens |
|----------|-------|--------------|
| **"build me..."** | front-door | Interview → spec → structured plan |
| **"plan this..."** | create-plan | Create implementation plan |
| **"implement"** | implement-plan | Execute plan with beads tracking |
| **"debug this"** | debugger | Systematic hypothesis-based debugging |
| **"review code"** | code-reviewer | Quality + security review |

**Example:**
```
You: "Build me a REST API for user management"

Claude: [Asks 5-7 targeted questions via front-door]
      [Creates structured plan with create-plan]
      [Implements with implement-plan + beads tracking]
      [Survives /clear with resume-handoff]
```

---

## Token-Saving Features

### `/freesearch` - Zero-Token Research

```bash
# Research WITHOUT burning Claude tokens
/freesearch "Polymarket API best practices"

# Routes to Gemini CLI directly
# Claude only uses tokens for summary (~500 vs 10,000+)
```

**How it works**: Calls `gemini --yolo "prompt"` via Bash. 0 Claude tokens for the actual research.

### `/dispatch` - Multi-Model Orchestration

```bash
# Route to the best CLI for the job
/dispatch "Research WebSocket patterns"    # → gemini (free)
/dispatch "Write a rate limiter function"  # → codex (code specialist)
/dispatch "Design a microservices architecture"  # → claude (reasoning)

# Available CLIs:
# - claude (2.1.25) - Max plan
# - codex (0.92.0) - OpenAI
# - gemini (0.26.0) - Google (FREE)
# - qwen (0.8.2) - 2K free requests/day
```

**Model selection matrix**:
| Task Pattern | Routes To | Why |
|--------------|-----------|-----|
| "research", "explain", "what is" | `gemini` | Free, has web search |
| "write code", "implement", "refactor" | `codex` | Optimized for code |
| "plan", "design", "architect" | `claude` | Best reasoning |
| Ambiguous | Ask user or default to `gemini` | Cheapest |

---

## Autonomous Mode

Build something, disconnect whenever. Work survives.

```bash
# Start headless build
oneshot-build "A CLI tool that converts markdown to PDF"

# Monitor progress anytime
oneshot status

# Watch it work live
oneshot attach
```

**Under the hood**: Uses tmux + resilient state saving. Your work survives:
- Terminal disconnections
- /clear commands
- Context exhaustion
- System restarts

---

## Beads = Persistent Memory

Tasks survive everything. Never lose track of what you're doing.

```bash
bd ready      # "What's next?" → Shows unblocked tasks
bd list       # All tasks with status
bd show 42    # Details of task #42
bd sync       # Save to git (CRITICAL before /clear)
```

**Beads integration**:
- Tasks tracked in `.beads/tasks.json`
- Synced to git automatically
- Survives /clear, /compact, restarts
- Supports dependencies and blockers

---

## Interview Depth Control

Control how thorough the front-door interview is:

| Command | Questions | When to Use |
|---------|-----------|-------------|
| `/full-interview` | All 13+ | Greenfield projects, avoid rework |
| `/quick-interview` | Q1, Q2, Q6, Q12 only | Experienced user, well-defined task |
| `/smart-interview` | Auto-detect | Reset to default behavior |

**Or set via environment:**
```bash
export ONESHOT_INTERVIEW_DEPTH=full|smart|quick
```

---

## SSH Aliases (All Your Machines)

**Install on any machine:**
```bash
curl -fsSL https://raw.githubusercontent.com/Khamel83/oneshot/master/ssh/install.sh | bash
```

**Then use:**
```bash
ssh oci          # OCI cloud (oci-dev)
ssh oci-ts       # Via Tailscale
ssh homelab      # Homelab server
ssh homelab-ts   # Via Tailscale
ssh macmini      # Mac mini (Apple Silicon)
ssh macmini-ts   # Via Tailscale
```

---

## Context Management

| Command | What Happens |
|---------|--------------|
| "create handoff" | Saves context to `.handoff.md` before /clear |
| "resume" | Restores from handoff + beads |
| "what's next" | Same as `bd ready` |
| `/compact` | Summarize conversation to free tokens |

---

## All 43 Skills

**Core (21)** - Auto-routed:
- front-door, autonomous-builder, resilient-executor, create-plan, implement-plan, beads, debugger, code-reviewer, freesearch, dispatch, deep-research, search-fallback, delegate-to-agent, parallel-validator, batch-processor, auto-updater, create-handoff, resume-handoff, failure-recovery, thinking-modes, secrets-vault-manager

**Advanced (22)** - On-demand:
- refactorer, test-runner, performance-optimizer, git-workflow, docker-composer, ci-cd-setup, push-to-cloud, remote-exec, observability-setup, database-migrator, api-designer, oci-resources, convex-resources, documentation-generator, the-audit, visual-iteration, secrets-sync, hooks-manager, skillsmp-browser, full-interview, quick-interview, smart-interview

**Full reference:** [.claude/skills/INDEX.md](.claude/skills/INDEX.md)

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bootstrap fails "beads not found" | `npm install -g @beads/bd` |
| Skill not triggering | Say `(ONE_SHOT)` to re-anchor |
| Agent stuck in loop | Check `.agent/LAST_ERROR.md` |
| Lost context after /clear | `bd ready` shows your tasks |
| `/freesearch` fails | `gemini auth login` |
| `/dispatch` fails | Check CLI is installed and authenticated |

---

## Shell Utilities

**Claude Code shortcuts** (cc = official, zai = GLM API):

```bash
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/claude-shell-setup.sh > ~/claude-shell-setup.sh
# Edit with your ZAI_API_KEY, then:
bash ~/claude-shell-setup.sh --install
```

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Request                             │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│   AGENTS.md (Skill Router) - 287 lines, ~2k tokens         │
│   - Keyword matching → skill selection                      │
│   - Auto-delegation thresholds                              │
│   - Slash command registry                                  │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Skill (e.g., front-door)                       │
│   - AskUserQuestion for interviews                          │
│   - Task tool for delegation                                │
│   - Write/Read for state persistence                        │
└──────────────────────────┬──────────────────────────────────┘
                           ↓
        ┌──────────────────┴──────────────────┐
        ↓                                     ↓
┌─────────────────┐                  ┌────────────────┐
│  Claude Code    │                  │  External CLIs │
│  (main context) │                  │  (via Bash)    │
│  - Planning     │                  │  - gemini      │
│  - Coordination │                  │  - codex       │
│  - Summary      │                  │  - qwen        │
└─────────────────┘                  └────────────────┘
        ↑                                     ↑
        └──────────────────┬──────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│               Beads (Persistent State)                      │
│   - .beads/tasks.json (git-tracked)                        │
│   - Survives /clear, restarts, disconnects                  │
└─────────────────────────────────────────────────────────────┘
```

**Token optimization strategy**:
1. **Aggressive delegation**: Spawn sub-agents for isolated work
2. **External CLI routing**: Use gemini/codex/qwen via /dispatch
3. **State to disk**: Write progress to files, not context
4. **Compression**: /compact summarizes conversation history
5. **Resume from handoff**: Don't keep history, restore from disk

---

## Project Structure

```
oneshot/
├── AGENTS.md              # Skill router (v8.1, 287 lines)
├── CLAUDE.md              # Global project instructions
├── README.md              # This file
├── SPEC.md                # Skill specifications
├── CHANGELOG.md           # Version history
├── oneshot.sh             # Main installer
├── upgrade-v8.sh          # Updater
├── install.sh             # Bootstrap
├── .claude/
│   └── skills/
│       ├── INDEX.md       # Skills catalog
│       ├── TEMPLATE.md    # Skill template
│       └── [43 skills]/   # Individual skill directories
│           └── SKILL.md
├── scripts/               # Utility scripts
├── examples/              # Example projects
├── tests/                 # Skill tests
├── docs/                  # Additional docs
├── secrets/               # SOPS-encrypted secrets template
├── ssh/                   # SSH alias installer
├── archive/               # Deprecated versions
├── dispatch/              # /dispatch output directory
└── research/              # /freesearch output directory
```

---

## Version History

**v8.1** (Current)
- 43 total skills (21 Core, 22 Advanced)
- `/freesearch` - Zero-token research via Gemini CLI
- `/dispatch` - Multi-model CLI orchestration (claude/codex/gemini/qwen)
- Ultra-compressed AGENTS.md (~2k tokens)
- Slash commands for all core skills

**v8.0**
- AGENTS.md compression (20k → 2k tokens)
- Auto-updater on session start
- Background research via Gemini CLI

**v7.5**
- Resilient executor (tmux-based)
- Parallel validation
- Batch processor

**v7.0**
- Beads integration for persistent task tracking
- Plan mode (create-plan → implement-plan)
- Failure recovery protocols

**v6.0**
- front-door skill (interview-first approach)
- Replaced oneshot-core

---

## Contributing

**To add a new skill:**

1. Create skill directory:
   ```bash
   mkdir -p ~/.claude/skills/oneshot/your-skill
   ```

2. Write SKILL.md using TEMPLATE.md

3. Add to AGENTS.md skill router (if core)

4. Add to INDEX.md

5. Test: Say "use the your-skill skill" in Claude Code

6. Submit PR to oneshot repo

---

**Links**

- [GitHub](https://github.com/Khamel83/oneshot)
- [Beads](https://github.com/steveyegge/beads) - Persistent task tracking
- [Example Project](examples/weather-cli)
- [Skills Reference](.claude/skills/INDEX.md)

---

**v8.1** | 43 Skills | Beads | Autonomous Builder | Gemini CLI Research | Multi-Model Dispatch | Ultra-Compressed Context | Slash Commands
