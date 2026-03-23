# LLM-OVERVIEW: ONE_SHOT

> Complete context for any LLM to understand this project.
> **Last Updated**: 2026-03-22
> **ONE_SHOT Version**: 13
> **Status**: Production / Active Development

---

## 1. WHAT IS ONE_SHOT?

### One-Line Description
An operator framework for Claude Code that provides on-demand skill discovery, intelligent delegation, and context management while minimizing token usage.

### The Problem It Solves

**Context exhaustion kills productivity.** When building complex projects with Claude Code:
- Conversations grow long and hit token limits
- `/clear` loses all task context
- No persistent memory across sessions
- Too many commands create decision fatigue

**ONE_SHOT solves all of this.**

### What ONE_SHOT Provides

| Capability | How |
|------------|-----|
| **On-demand skill discovery** | Operators discover skills from `~/.claude/skills/` index |
| **Context management** | Handoffs + restore survive `/clear` |
| **Intelligent delegation** | Assess-comply-verify-escalate pattern |
| **Decision defaults** | Agents make reasonable choices autonomously |
| **Token optimization** | 10 skills vs 25+ in earlier versions |

### Current State

- **Status**: Production / Active Development
- **Version**: 13
- **Commands**: 10 total (3 operators + 7 utilities)
- **Rules**: Progressive disclosure (~300 tokens)
- **Architecture**: Operator framework with on-demand skill discovery

---

## 2. ARCHITECTURE OVERVIEW

### Tech Stack

| Component | Technology |
|-----------|------------|
| **Language** | Markdown (commands), Bash (scripts) |
| **Framework** | Claude Code CLI |
| **Task Tracking** | Native Tasks (TaskCreate/TaskGet/TaskUpdate/TaskList) |
| **External CLIs** | gemini (for /research) |
| **Persistence** | Git + handoff files |
| **Skill Discovery** | On-demand (operators read skill index) |

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **AGENTS.md** | Operator spec - `/short`, `/full`, `/conduct` behaviors | Project root |
| **CLAUDE.md** | Global project instructions (editable per project) | Project root |
| **`/short`** | Quick iteration operator | Skill |
| **`/full`** | Structured work operator | Skill |
| **`/conduct`** | Multi-model PMO orchestrator | Skill |
| **`/handoff`** | Context checkpoint before `/clear` | Skill |
| **`/restore`** | Resume from handoff | Skill |
| **`/research`** | Background research via Gemini | Skill |
| **`/freesearch`** | Zero-token web search via Exa API | Skill |
| **`/doc`** | Cache external docs locally | Skill |
| **`/vision`** | Image/website analysis | Skill |
| **`/secrets`** | SOPS/Age secret management | Skill |

### Skill Structure

```
~/.claude/skills/
├── short/             # Quick iteration operator
├── full/              # Structured work operator
├── conduct/           # Multi-model PMO orchestrator
├── handoff/           # Context checkpoint
├── restore/           # Resume from handoff
├── research/          # Background research
├── freesearch/        # Zero-token web search
├── doc/               # Doc caching
├── vision/            # Image/website analysis
└── secrets/           # Secrets management
```

### Installation Flow

```bash
# User runs:
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash

# This creates:
# 1. AGENTS.md (operator spec)
# 2. CLAUDE.md (project instructions)
# 3. Skills in ~/.claude/skills/ (10 skills)
# 4. Rules in ~/.claude/rules/ (progressive disclosure)
```

---

## 3. KEY FILES

| File | Purpose | Lines |
|------|---------|-------|
| `AGENTS.md` | Operator spec - behaviors, decision defaults, delegation | ~120 |
| `CLAUDE.md` | Global project instructions (edit per project) | ~100 |
| `README.md` | User-facing documentation | ~200 |
| `docs/SKILLS.md` | Command reference | ~175 |
| `docs/LLM-OVERVIEW.md` | This file - project context for LLMs | ~300 |
| `.claude/rules/core.md` | Core rules (always loaded) | ~150 |
| `.claude/rules/khamel-mode.md` | User-specific defaults | ~50 |
| `oneshot.sh` | Main installer | ~500 |

---

## 4. CURRENT STATE

### What Works

**Core System**
- 3 operators (short, full, conduct) with skill discovery
- 7 utility skills
- Progressive disclosure rules (~300 tokens)
- Native task tracking (built into Claude Code)

**Context Management**
- `/handoff` saves checkpoint
- `/restore` resumes from checkpoint
- Tasks persist across `/clear`

**Research & Docs**
- `/research` via Gemini CLI
- `/freesearch` via Exa API (zero tokens)
- `/doc` caches external documentation

**Security**
- `/secrets` for SOPS/Age encrypted secrets
- `/vision` for image/website analysis

### Known Limitations

**External Dependencies**
- Requires Gemini CLI for `/research`
- Requires Exa API key for `/freesearch`
- Requires SOPS/Age for `/secrets`

**Platform Support**
- Unix-like systems assumed
- Some scripts bash-specific

---

## 5. HOW TO WORK ON THIS PROJECT

### Development Workflow

```bash
# 1. Clone
git clone https://github.com/Khamel83/oneshot
cd oneshot

# 2. Install dependencies (optional)
npm install -g @google/gemini-cli
gemini auth login

# 3. Test
claude .

# 4. Try commands
# /short - quick iteration
# /full - structured work
# /handoff /restore - context management
```

### Adding a New Command

1. Create skill directory: `.claude/skills/new-command/SKILL.md`
2. Update docs/SKILLS.md
3. Update README.md
4. Update AGENTS.md if it changes operator behavior
5. Test manually
6. Submit PR

### Testing Checklist

- [ ] `/short` loads context and asks what you're working on
- [ ] `/full` creates IMPLEMENTATION_CONTEXT.md
- [ ] `/handoff` saves checkpoint
- [ ] `/restore` resumes from handoff
- [ ] `/freesearch` returns results (requires Exa API key)
- [ ] `/doc --list` shows cached docs

---

## 6. PHILOSOPHY & DESIGN DECISIONS

### Core Principles

1. **Context is scarce** - Fewer commands, on-demand discovery
2. **Decide autonomously** - Decision defaults prevent constant questions
3. **State to disk** - Handoffs survive `/clear`
4. **Operators, not menus** - 3 operators > 25+ menu commands
5. **User time > agent compute** - Make reasonable choices, don't ask

### Design Trade-offs

| Decision | Rationale |
|----------|-----------|
| 10 skills vs 25+ | Less decision fatigue, skill discovery on demand |
| Operators | Three entry points cover all use cases |
| Native tasks | Built into Claude Code, no external dependency |
| Progressive disclosure | ~300 tokens always-on vs ~2000 |

---

## 7. TOKEN OPTIMIZATION STRATEGY

### How ONE_SHOT Saves Tokens

1. **Progressive Disclosure**
   - Rules load based on project type
   - ~300 tokens always-on (down from ~2000)

2. **On-Demand Discovery**
   - Operators discover skills when needed
   - No large command catalog in memory

3. **State to Disk**
   - Handoffs save progress
   - Don't carry full history in context

4. **External Tools**
   - `/freesearch` uses Exa API (zero Claude tokens)
   - `/research` uses Gemini CLI

5. **Compression**
   - `/compact` summarizes conversation
   - Minimal always-loaded context

---

## 8. GLOSSARY

| Term | Definition |
|------|------------|
| **Operator** | Entry point skill that orchestrates work (`/short`, `/full`, `/conduct`) |
| **Handoff** | Context snapshot for resuming after `/clear` |
| **Skill discovery** | Finding relevant skills on demand from `~/.claude/skills/` index |
| **Native Tasks** | Claude Code's built-in task tracking |
| **Progressive disclosure** | Loading rules based on project type |
| **Decision defaults** | Pre-set choices for ambiguous situations |

---

## 9. RELATED PROJECTS

| Project | Relationship |
|---------|--------------|
| [Claude Code](https://claude.com/claude-code) | Target platform |
| [Penny](https://github.com/Khamel83/penny) | Voice-to-action system |

---

## 10. SUPPORT & CONTRIBUTING

### Getting Help

- **GitHub Issues**: https://github.com/Khamel83/oneshot/issues
- **Command Reference**: docs/SKILLS.md

### Contributing

1. Fork the repo
2. Create feature branch
3. Make changes
4. Update documentation
5. Submit PR

---

**Document Version**: 3.0
**Last Updated**: 2026-03-09
**Maintainer**: @Khamel83
