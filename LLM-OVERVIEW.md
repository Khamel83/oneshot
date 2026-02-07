# LLM-OVERVIEW: ONE_SHOT

> Complete context for any LLM to understand this project.
> **Last Updated**: 2026-02-07
> **ONE_SHOT Version**: 10.2
> **Status**: Production / Active Development

---

## 1. WHAT IS ONE_SHOT?

### One-Line Description
A skill system for Claude Code that provides persistent task tracking, autonomous execution, and multi-model AI orchestration while minimizing token usage through aggressive delegation.

### The Problem It Solves

**Context exhaustion kills productivity.** When building complex projects with Claude Code:
- Conversations grow long and hit token limits
- `/clear` loses all task context
- No persistent memory across sessions
- Expensive Claude tokens used for routine tasks
- No coordination between multiple AI tools

**ONE_SHOT solves all of this.**

### What ONE_SHOT Provides

| Capability | How |
|------------|-----|
| **Persistent task tracking** | Beads integration (git-tracked tasks.json) |
| **Autonomous execution** | Resilient tmux sessions survive disconnects |
| **Token optimization** | Route to specialized CLIs (gemini/codex/qwen) |
| **Free research** | Gemini CLI via /freesearch (0 Claude tokens) |
| **Structured planning** | front-door interview → create-plan → implement-plan |
| **Context survival** | Handoffs + beads resume after /clear |
| **Auto-updates** | Skills sync from GitHub daily |

### Current State

- **Status**: Production / Active Development
- **Version**: 10.2
- **Slash Commands**: 16
- **Rules**: 7 (progressive disclosure)
- **Last Milestone**: Work discipline + beads operational rules
- **Next Milestone**: Wait for Claude native task tools

---

## 2. ARCHITECTURE OVERVIEW

### Tech Stack

| Component | Technology |
|-----------|------------|
| **Language** | Markdown (skills), Bash (scripts) |
| **Framework** | Claude Code CLI (2.1.25) |
| **Task Tracking** | Beads (npm package) |
| **External CLIs** | claude, codex, gemini, qwen |
| **Persistence** | Git + JSON files |
| **Execution** | tmux (resilient sessions) |

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **AGENTS.md** | Skill router - keyword matching → skill selection | Project root |
| **CLAUDE.md** | Global project instructions (editable per project) | Project root |
| **front-door** | Interview hub - triages and routes all requests | Skill |
| **beads** | Persistent task tracking via .beads/tasks.json | Skill |
| **create-plan** | Structured implementation planning | Skill |
| **implement-plan** | Execute plans with beads tracking | Skill |
| **freesearch** | Zero-token research via Gemini CLI | Skill |
| **dispatch** | Multi-model CLI orchestration | Skill |
| **INDEX.md** | Complete skills catalog | .claude/skills/ |

### Skill File Structure

```
.claude/skills/
├── INDEX.md           # Catalog of all 43 skills
├── TEMPLATE.md        # Template for new skills
└── [skill-name]/
    └── SKILL.md       # Skill definition (frontmatter + markdown)
```

**SKILL.md frontmatter:**
```yaml
---
name: skill-name
description: One-line description
homepage: https://github.com/Khamel83/oneshot
allowed_tools: Bash, Read, Glob, Grep, etc.
metadata: {"oneshot":{"emoji":"🎯","requires":{"bins":["gemini"]}}}
---
```

### Installation Flow

```bash
# User runs:
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash

# This creates:
# 1. AGENTS.md (skill router)
# 2. CLAUDE.md (project instructions)
# 3. Symlinks to ~/.claude/skills/oneshot/[43 skills]
```

---

## 3. KEY FILES

| File | Purpose | Lines |
|------|---------|-------|
| `AGENTS.md` | Skill router, slash commands, auto-delegation rules | 287 |
| `CLAUDE.md` | Global project instructions (edit per project) | 273 |
| `README.md` | User-facing documentation | ~400 |
| `SPEC.md` | Detailed skill specifications (front-door, etc.) | 300+ |
| `.claude/skills/INDEX.md` | Skills catalog with triggers | ~200 |
| `oneshot.sh` | Main installer | ~500 |
| `upgrade-v8.sh` | Updater script | ~150 |

---

## 4. CURRENT STATE

### What Works

✅ **Core System**
- Skill router with keyword matching
- 43 skills (21 auto-routed, 22 on-demand)
- Slash commands for all core skills
- Auto-updater on session start

✅ **Task Persistence**
- Beads integration
- Tasks survive /clear, restarts, disconnects
- Git-synced task state

✅ **Token Optimization**
- `/freesearch` - 0 Claude tokens for research
- `/dispatch` - Route to gemini/codex/qwen
- Ultra-compressed AGENTS.md (~2k tokens)

✅ **Autonomous Execution**
- Resilient tmux sessions
- Survives disconnects
- Background job management

✅ **Planning & Execution**
- front-door interview
- create-plan → implement-plan flow
- Handoffs for context survival

### What's In Progress

🔄 **Enhanced Testing**
- Skill test coverage
- Integration tests

🔄 **Documentation**
- LLM-OVERVIEW.md (this file)
- Improved README

### Known Limitations

⚠️ **Skill Discovery**
- 43 skills can be overwhelming
- INDEX.md helps but search could be better

⚠️ **External Dependencies**
- Requires beads npm package
- Requires Gemini CLI for /freesearch
- Requires various AI CLIs for /dispatch

⚠️ **Platform Support**
- SSH aliases assume Unix-like systems
- Some scripts bash-specific

---

## 5. HOW TO WORK ON THIS PROJECT

### Development Workflow

```bash
# 1. Clone
git clone https://github.com/Khamel83/oneshot
cd oneshot

# 2. Install dependencies
npm install -g @beads/bd
npm install -g @google/gemini-cli
gemini auth login

# 3. Test skills
cd examples/weather-cli
claude .

# 4. Say "build me..." to test front-door
# 5. Say "/freesearch test" to test freesearch
# 6. Say "/dispatch gemini test" to test dispatch
```

### Adding a New Skill

1. Create directory: `mkdir -p .claude/skills/oneshot/new-skill`
2. Copy TEMPLATE.md and customize
3. Add to AGENTS.md skill router (if core)
4. Add to INDEX.md
5. Test with "use the new-skill skill"
6. Submit PR

### Testing

```bash
# Run skill tests (if available)
cd tests
./test-skills.sh

# Manual test checklist:
# - [ ] front-door interview works
# - [ ] /freesearch returns output
# - [ ] /dispatch routes correctly
# - [ ] beads persist across /clear
# - [ ] autonomous-builder completes
```

---

## 6. PHILOSOPHY & DESIGN DECISIONS

### Core Principles

1. **Context is scarce** - Delegate aggressively to sub-agents
2. **State to disk** - Write progress, don't keep in context
3. **Survive everything** - /clear, disconnects, restarts
4. **Zero tokens when possible** - Use external CLIs via /dispatch
5. **User time > agent compute** - Ask questions upfront

### Design Trade-offs

| Decision | Rationale |
|----------|-----------|
| Markdown-based skills | Human-readable, git-friendly |
| Symlinked skills | Single source of truth |
| AGENTS.md compression | Load 2k vs 20k tokens per session |
| Beads for persistence | Git-tracked, survives everything |
| External CLIs | Token savings, specialized models |

---

## 7. TOKEN OPTIMIZATION STRATEGY

### How ONE_SHOT Saves Tokens

1. **Aggressive Delegation**
   - Spawn sub-agents for isolated work
   - Don't pollute main context

2. **External CLI Routing**
   - `/freesearch` → Gemini CLI (free)
   - `/dispatch` → codex/qwen (cheaper)
   - Main context = coordination only

3. **State to Disk**
   - Write progress to files
   - Resume from handoff
   - Don't carry history

4. **Compression**
   - `/compact` summarizes conversation
   - AGENTS.md is JSON-compact (~2k tokens)

5. **Lazy Loading**
   - Skills loaded on-demand
   - Not all in memory at once

### Token Comparison

| Approach | Tokens Used |
|----------|-------------|
| Direct Claude research | ~10,000 |
| `/freesearch` (Gemini CLI) | ~500 (summary only) |
| **Savings** | **95%** |

---

## 8. GLOSSARY

| Term | Definition |
|------|------------|
| **AGENTS.md** | Skill router - keyword patterns → skill selection |
| **Beads** | Persistent task tracking system (npm package) |
| **front-door** | Interview skill - triages all incoming requests |
| **handoff** | Context snapshot for resuming after /clear |
| **skill** | Reusable behavior pattern (markdown + tools) |
| **slash command** | `/skill-name` invocation |
| **dispatch** | Multi-model CLI router |
| **freesearch** | Zero-token research via Gemini CLI |
| **resilient-executor** | Tmux-based background execution |

---

## 9. RELATED PROJECTS

| Project | Relationship |
|---------|--------------|
| [Beads](https://github.com/steveyegge/beads) | Task tracking (npm dependency) |
| [Claude Code](https://claude.com/claude-code) | Target platform |
| [Penny](https://github.com/Khamel83/penny) | Voice-to-action system (uses similar patterns) |
| [ClawdBot/Moltbot](https://docs.openclaw.ai) | Multi-model orchestrator (inspiration for /dispatch) |

---

## 10. SUPPORT & CONTRIBUTING

### Getting Help

- **GitHub Issues**: https://github.com/Khamel83/oneshot/issues
- **Skills Reference**: .claude/skills/INDEX.md
- **Example Projects**: examples/weather-cli

### Contributing

1. Fork the repo
2. Create skill directory
3. Write SKILL.md
4. Update AGENTS.md and INDEX.md
5. Submit PR

**Skill Template**: .claude/skills/TEMPLATE.md

---

**Document Version**: 2.0
**Last Updated**: 2026-02-07
**Maintainer**: @Khamel83
