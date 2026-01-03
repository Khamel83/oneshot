# ONE_SHOT v7.4

**Tell it an idea. Come back with the thing built.**

A skill system for [Claude Code](https://claude.com/claude-code) that adds structured workflows, persistent task tracking, and autonomous execution to your projects.

**New in v7.4:** Resilient execution (survives disconnect), aggressive subagent delegation, auto-updates from GitHub.

> See it in action: [examples/weather-cli](examples/weather-cli) - a complete project built autonomously in 6 iterations.

---

## Prerequisites

```bash
# Beads CLI is REQUIRED for task tracking
npm install -g @beads/bd
# or: brew install steveyegge/beads/bd
# or: go install github.com/steveyegge/beads/cmd/bd@latest

# tmux is REQUIRED for resilient execution
brew install tmux  # macOS
apt install tmux   # Linux
```

## Install

```bash
git clone https://github.com/Khamel83/oneshot.git ~/github/oneshot
cd ~/github/oneshot && ./install.sh
```

This installs the `oneshot` command and sets up auto-updates.

---

## The `oneshot` Command

Everything is managed through one command. You never touch tmux directly.

```bash
# Build something autonomously (survives disconnect!)
oneshot build "A Python CLI that fetches weather data"

# Run any Claude prompt resiliently
oneshot run "implement the auth feature"

# Check what's happening
oneshot status

# Watch the work
oneshot attach

# Stop and save state
oneshot stop

# Resume later (picks up from beads state)
oneshot resume
```

### All Commands

```
oneshot build <idea>     Build something autonomously
oneshot run <prompt>     Run prompt in resilient session
oneshot attach           Connect to running session
oneshot status           Show current status
oneshot log              View full session log
oneshot follow           Follow log live
oneshot stop             Stop current session (saves state)
oneshot resume           Resume from beads state
oneshot list             List all sessions
oneshot killall          Stop all sessions
oneshot update           Update ONE_SHOT from GitHub
```

---

## Resilient Execution

**Your work survives if you disconnect.** All sessions run in tmux with:

- **Heartbeat** - Proves session is alive (every 30s)
- **Checkpointer** - Commits + syncs state (every 5 min)
- **Full logging** - Everything in `.agent/session.log`
- **Beads sync** - Task state saved after every action

If you disconnect:
1. Session keeps running
2. State keeps syncing
3. Reconnect with `oneshot attach`

If something crashes:
1. Beads state is synced
2. `oneshot resume` picks up where it left off

---

## Two Modes

### Interactive Mode (Default)
You're in the loop. Claude asks questions, you approve plans, you guide execution.

```
You: "Build me a task manager CLI in Python"
Claude: [asks clarifying questions]
Claude: [creates plan, asks for approval]
You: "looks good, implement it"
Claude: [builds it step by step]
```

### Autonomous Mode (Headless)
You give an idea. Come back later with a working artifact.

```bash
oneshot build "A CLI tool that converts markdown to PDF with syntax highlighting"

# Check progress anytime
oneshot status

# Watch it work
oneshot attach

# Disconnect whenever - it keeps running!
```

---

## When To Use What

| Situation | Mode | Why |
|-----------|------|-----|
| Complex feature, need control | Interactive | You guide decisions |
| Simple/well-defined idea | Autonomous | Just build it |
| Overnight batch work | Autonomous | Let it run |
| Learning the codebase | Interactive | Stay in the loop |
| Debugging | Interactive | Need back-and-forth |

---

## The 12 Core Skills

These trigger automatically based on what you say:

| You Say | Skill | What Happens |
|---------|-------|--------------|
| "build me...", "new project" | `front-door` | Interview → spec → plan |
| "just build it", "autonomous" | `autonomous-builder` | Headless execution |
| "plan this", "design" | `create-plan` | Structured planning |
| "implement", "build it" | `implement-plan` | Execute with beads tracking |
| "what's next", "ready tasks" | `beads` | Persistent task state |
| "bug", "fix", "broken" | `debugger` | Systematic debugging |
| "review", "is this safe" | `code-reviewer` | Quality check |
| "save context", "handoff" | `create-handoff` | Preserve before /clear |
| "resume", "continue" | `resume-handoff` | Pick up where left off |
| "stuck", "looping" | `failure-recovery` | Get unstuck |
| "think", "ultrathink" | `thinking-modes` | Deep analysis |
| "secrets", "env" | `secrets-vault-manager` | SOPS encryption |

**17 more skills** available on-demand. See INDEX.md.

---

## Core Workflow

### For New Features

```
1. "plan a feature that does X"     → create-plan
2. [approve the plan]
3. "implement it"                   → implement-plan
4. [context getting full?]
5. "save context"                   → create-handoff
6. /compact
7. "continue"                       → resume-handoff
8. [repeat until done]
```

### For Quick Fixes

```
1. "fix this bug: [description]"    → debugger
2. [Claude fixes it]
3. Done
```

### For Autonomous Builds

```bash
oneshot-build "Your idea"
# Wait...
# Check .agent/STATUS.md for progress
# bd list --json for task state
```

---

## Context Management

**Context is the scarce resource.** ONE_SHOT manages it:

| Problem | Solution |
|---------|----------|
| Context fills up | Handoff → /compact → resume |
| Lose track of tasks | Beads tracks persistently |
| Forget decisions | Beads stores in git |
| Agent loops | Loop detection stops gracefully |

### Beads = Persistent Memory

```bash
bd ready --json      # What's next?
bd list --json       # All tasks
bd sync              # Save to git (CRITICAL before session end)
```

Beads survives /clear, /compact, session restarts. Your tasks don't disappear.

---

## Files Created

```
project/
├── AGENTS.md           ← Skill router (read first)
├── CLAUDE.md           ← Project instructions
├── TODO.md             ← Session visibility
├── LLM-OVERVIEW.md     ← Project context
├── .claude/skills/     ← 29 skills
├── .beads/             ← Persistent tasks
└── scripts/
    └── oneshot-build   ← Autonomous builder script
```

For autonomous mode:
```
.agent/
├── STATUS.md         ← Real-time progress
├── ITERATIONS.md     ← Loop counter
└── LAST_ERROR.md     ← If something failed
```

---

## Quick Start

### 1. Install Prerequisites
```bash
npm install -g @beads/bd   # Required for task tracking
```

### 2. Add to Any Project
```bash
cd your-project
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
```

### 3. Interactive Mode
Open in Claude Code. Say what you want:
```
"Build me a REST API for user management"
```

### 4. Autonomous Mode
```bash
# oneshot-build is downloaded to scripts/ by the bootstrap
./scripts/oneshot-build "A Python CLI that fetches weather data"
tail -f .agent/STATUS.md  # Monitor progress
```

---

## Thinking Modes

For complex decisions:

| Say | Depth | Use For |
|-----|-------|---------|
| "think" | Light | Quick check |
| "think hard" | Medium | Trade-offs |
| "ultrathink" | Deep | Architecture |
| "super think" | Very deep | System design |
| "mega think" | Maximum | Strategic |

---

## Philosophy

1. **Context is scarce** - Load minimal, checkpoint often
2. **Beads for memory** - Don't lose state between sessions
3. **Commit often** - Every file edit, every task
4. **Best effort** - 50% working > 0% perfect
5. **Stop gracefully** - When stuck, save and stop

---

## Upgrading

```bash
# Normal update (adds missing files)
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash

# Full upgrade (updates all skills)
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash -s -- --upgrade
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bootstrap fails "beads not found" | Install beads: `npm install -g @beads/bd` |
| Skill not triggering | Say `(ONE_SHOT)` to re-anchor |
| Agent stuck in loop | Check `.agent/LAST_ERROR.md`, restart |
| Lost context | `bd ready --json` shows your tasks |
| Beads not initialized | `bd init --stealth` in project directory |

---

## Version

**v7.3** | 12 Core Skills | 17 Advanced | Beads Required | Autonomous Builder

---

## Links

- [GitHub](https://github.com/Khamel83/oneshot)
- [INDEX.md](.claude/skills/INDEX.md) - Full skill reference
- [Beads](https://github.com/steveyegge/beads) - Persistent task tracking
- [RepoMirror](https://github.com/repomirrorhq/repomirror) - Inspiration for autonomous mode
