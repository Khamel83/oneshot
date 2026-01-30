# ONE_SHOT v8.1

**Tell it an idea. Come back with the thing built.**

Skill system for [Claude Code](https://claude.com/claude-code) with persistent task tracking, autonomous execution, and Gemini CLI research.

---

## Quick Start

```bash
# 1. Install beads (REQUIRED for task tracking)
npm install -g @beads/bd

# 2. Install ONE_SHOT in your project
cd your-project
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash

# 3. Open in Claude Code and say:
"build me a REST API for user management"
```

---

## Update ONE_SHOT

**Single command - always gets latest v8:**
```bash
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/upgrade-v8.sh | bash
```

This updates AGENTS.md, skills, and compresses context (~2k tokens).

---

## SSH Aliases (All Your Machines)

**Install on any machine:**
```bash
curl -fsSL https://raw.githubusercontent.com/Khamel83/oneshot/master/ssh/install.sh | bash
```

**Then use:**
- `ssh oci` / `ssh oci-ts` (OCI cloud)
- `ssh homelab` / `ssh homelab-ts` (Homelab server)
- `ssh macmini` / `ssh macmini-ts` (Mac mini)

---

## Core Skills (What You Say)

| Say This | What Happens |
|----------|--------------|
| **"build me..."** | Interview → spec → plan |
| **"implement"** | Execute plan with beads tracking |
| **"debug this"** | Systematic hypothesis-based debugging |
| **"review code"** | Quality + security review |
| **"research..."** | Background research via Gemini CLI or APIs |

**Example:**
```
You: "Build me a task manager CLI in Python"
Claude: [asks questions, creates plan, implements]
```

**All skills:** [.claude/skills/INDEX.md](.claude/skills/INDEX.md)

---

## Two Modes

### Interactive (Default)
You're in the loop. Claude asks, you approve.

### Autonomous (Headless)
```bash
# Build something, disconnect whenever
oneshot build "A CLI tool that converts markdown to PDF"

# Check progress
oneshot status

# Watch it work
oneshot attach
```

---

## Beads = Persistent Memory

```bash
bd ready      # What's next?
bd list       # All tasks
bd sync       # Save to git (CRITICAL before session end)
```

Beads survives /clear, /compact, restarts. Your tasks don't disappear.

---

## Files Created

```
project/
├── AGENTS.md           ← Skill router (v8.1)
├── CLAUDE.md           ← Project instructions
├── .beads/             ← Persistent tasks
└── .claude/skills/     ← 41 skills (symlinked)
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Bootstrap fails "beads not found" | `npm install -g @beads/bd` |
| Skill not triggering | Say `(ONE_SHOT)` to re-anchor |
| Agent stuck in loop | Check `.agent/LAST_ERROR.md` |
| Lost context | `bd ready` shows your tasks |

---

## Shell Utilities

**Claude Code shortcuts** (cc = official, zai = GLM API):
```bash
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/claude-shell-setup.sh > ~/claude-shell-setup.sh
# Edit with your ZAI_API_KEY, then: bash ~/claude-shell-setup.sh --install
```

---

**v8.1** | 41 Skills | Beads | Autonomous Builder | Gemini CLI Research | Ultra-compressed Context | Slash Commands

---

[GitHub](https://github.com/Khamel83/oneshot) | [Beads](https://github.com/steveyegge/beads) | [Example](examples/weather-cli)
