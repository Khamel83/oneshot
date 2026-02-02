# ONE_SHOT v9

**Tell it an idea. Come back with the thing built.**

A skill system for Claude Code that provides persistent task tracking, autonomous execution, and multi-model coordination.

---

## Quick Start (3 Steps)

```bash
# 1. In your project directory
cd your-project

# 2. Install ONE_SHOT
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash

# 3. Open in Claude Code
claude .

# Then say: "Build me a [thing you want]"
```

That's it. Claude will interview you, plan it, build it.

---

## How to Use ONE_SHOT

### The Basic Workflow

```
You say what you want
    ↓
Claude interviews you (front-door skill)
    ↓
Claude creates a plan (create-plan skill)
    ↓
Claude builds it (implement-plan skill)
    ↓
Progress tracked in beads (survives everything)
```

### What to Say

| You Say | What Happens |
|---------|--------------|
| "Build me X" | Claude interviews you, then builds it |
| "Plan this" | Creates a structured implementation plan |
| "Implement" | Executes the plan with task tracking |
| "Debug this" | Systematic debugging with hypotheses |
| "What's next?" | Shows your next unblocked task |
| "Create handoff" | Saves context before `/clear` |
| "Resume" | Restores context after `/clear` |

### You Don't Need to Remember Skills

Claude automatically picks the right skill based on what you say. There are 50+ skills, but you never need to memorize their names.

---

## Example Session

```
You: "Build me a CLI tool for task management"

Claude: [Asks questions via front-door skill]
      - What language? (Python, Go, Rust?)
      - What features? (add, list, complete, delete?)
      - Where should data be stored? (SQLite, files, API?)

      [Creates plan via create-plan skill]

      [Implements via implement-plan skill]
      - Writes code
      - Runs tests
      - Commits to git
      - Tracks progress in beads
```

Your tasks survive `/clear`, restarts, disconnections.

---

## Task Tracking (Beads)

Beads = Persistent memory. Never lose track of what you're doing.

```bash
bd ready      # "What's next?" → Shows unblocked tasks
bd list       # All tasks with status
bd show 42    # Details of task #42
bd sync       # Save to git (do this often!)
```

Tasks are tracked in `.beads/tasks.json` and synced to git.

### Context Survival

Claude's context window gets cleared. Your work shouldn't.

**Before `/clear`:**
```bash
You: "Create handoff"
Claude: Saves context to `.handoff.md`
```

**After `/clear`:**
```bash
You: "Resume"
Claude: Restores from handoff + beads
```

---

## Advanced Features

### Continuous Planning (v8+)

For complex projects, use the 3-file pattern:

```bash
You: "Create a continuous plan for [complex project]"
```

Creates:
- `task_plan.md` - The plan with skill sequences
- `findings.md` - Research and discoveries
- `progress.md` - Session log

These files survive `/clear` and enable multi-model coordination.

### Skill Discovery (v9+)

Not sure which skills exist?

```bash
You: "What skills do I have for testing?"
You: "Search skillsmp for database skills"
```

### Multi-Model Dispatch

Save Claude tokens by routing to specialized AI CLIs:

```bash
/dispatch "Research WebSocket patterns"    # → Gemini (free)
/dispatch "Write a rate limiter function"  # → Codex (code)
/dispatch "Design a microservices architecture"  # → Claude (plan)
```

---

## Slash Commands

| Command | What It Does |
|---------|--------------|
| `/full-interview` | Ask all 13+ questions (thorough) |
| `/quick-interview` | Ask only 4 questions (fast) |
| `/smart-interview` | Auto-detect depth (default) |
| `/freesearch` | Research via Gemini (0 Claude tokens) |
| `/compact` | Summarize to free tokens |
| `/run-plan` | Execute skill sequences deterministically (v9) |

---

## What You Get

| Feature | Description |
|---------|-------------|
| **Smart Interview** | Claude asks the right questions upfront |
| **Structured Plans** | Clear phases, decisions, dependencies |
| **Persistent Tracking** | Tasks survive `/clear`, restarts, disconnections |
| **Multi-Model** | Routes to best AI (Claude, Gemini, Codex) |
| **Autonomous Mode** | Headless execution that survives disconnects |
| **50+ Skills** | Specialized tools for every development task |
| **SkillsMP Access** | 26,000+ external skills (v9) |

---

## Project Structure

After installation, your project has:

```
your-project/
├── AGENTS.md           # Skill router (LLM instructions)
├── CLAUDE.md           # Your project-specific instructions
├── .beads/             # Persistent task tracking
└── .claude/skills/     # 50+ skills (symlinked from ~/.claude/skills/oneshot)
```

---

## Prerequisites

```bash
# Required: Beads (task tracking)
npm install -g @beads/bd

# Optional: Gemini CLI (for free research)
npm install -g @google/gemini-cli
gemini auth login
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Skill not triggering | Say `(ONE_SHOT)` to re-anchor |
| Lost context after `/clear` | Say "resume" |
| "What's next?" shows nothing | `bd list` to see all tasks |
| `/freesearch` fails | Run `gemini auth login` first |
| Beads not found | `npm install -g @beads/bd` |

---

## What's Different?

| Traditional Claude | ONE_SHOT |
|-------------------|----------|
| Say "build X" → gets halfway, forgets | Say "build X" → interviews, plans, executes, tracks |
| Context lost on `/clear` | Handoffs + beads survive anything |
| No task tracking | Beads tracks everything, forever |
| One AI, one context | Routes to best AI per task |
| Restart from scratch | Resume exactly where you left off |

---

## Updating ONE_SHOT

### To update your project with latest skills and AGENTS.md:

```bash
cd your-project
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash -s -- --upgrade
```

### To update the oneshot repo itself:

```bash
cd ~/github/oneshot
git pull origin master
```

---

## For LLMs: Documentation Maintenance

### When to Update This README

Update when:
- New skills are added to core router
- New user-facing features are added
- Version changes (v8 → v9, etc.)
- Workflow changes significantly
- New slash commands are added

### How to Update

1. **Read current README** to understand existing content
2. **Make changes** that are:
   - Clear for users (simple language, examples)
   - Accurate for LLMs (technical details correct)
   - Minimal (don't add, remove what's not needed)
3. **Test**: Can a new user follow this and succeed?
4. **Commit**: Use conventional commit format

### Section Guidelines

| Section | Audience | Purpose |
|---------|----------|---------|
| Quick Start | User | Get started in 3 steps |
| How to Use | User | Clear workflow examples |
| What to Say | User | Reference for common commands |
| For LLMs | LLM | Documentation maintenance rules |
| Troubleshooting | Both | Common problems and solutions |

### Documentation Principles

1. **Users first** - Write for humans, optimize for clarity
2. **Examples work** - Every example should be tested
3. **Remove friction** - Delete anything that doesn't help users succeed
4. **LLM-friendly** - Keep structure clear so LLMs can parse and update
5. **Single source** - This README is the primary user doc, keep it that way

### Related Files

| File | Purpose | Who Reads It |
|------|---------|--------------|
| `README.md` | User guide + docs maintenance | Users + LLMs |
| `AGENTS.md` | Skill router + LLM orchestration | LLMs only |
| `CLAUDE.md` | Project-specific instructions | LLMs only |
| `INDEX.md` | Complete skill reference | Users + LLMs |

### Version Update Checklist

When bumping version (e.g., v8 → v9):
- [ ] Update version in header
- [ ] Add new features to "What You Get" table
- [ ] Update "What's Different" if relevant
- [ ] Add new slash commands
- [ ] Update troubleshooting if new issues
- [ ] Check all examples still work
- [ ] Run user guide through a test scenario

---

## Links

- **GitHub**: https://github.com/Khamel83/oneshot
- **Skills Reference**: [.claude/skills/INDEX.md](.claude/skills/INDEX.md)
- **Beads**: https://github.com/steveyegge/beads

---

**v9** | 50+ Skills | Beads | Continuous Planning | SkillsMP Integration | Deterministic Execution
