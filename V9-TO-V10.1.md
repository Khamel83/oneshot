# v9 → v10.1: What Changed

**For the user who wants to understand the difference.**

---

## Executive Summary

| Aspect | v9 | v10.1 | Change |
|--------|-----|-------|--------|
| **Philosophy** | Framework with auto-routing | Personal configuration | Simplified |
| **Skills** | 52 auto-loaded skills | 16 on-demand commands | -69% |
| **Always-on tokens** | ~5,800 | ~300 | **-95%** |
| **Discovery** | Auto-trigger on "build me" | Type `/interview` | Explicit |
| **Routing** | AGENTS.md table | You invoke commands | Removed |
| **Rules** | Hooks injection | Progressive disclosure | Modular |
| **Strategy** | Build everything | "Wait for native" | Aligned |

---

## The Big Shift: Framework → Configuration

### v9: Framework
```
You: "Build me a CLI"
  ↓
AGENTS.md routes to front-door skill
  ↓
Auto-triggers interview
  ↓
Creates plan
  ↓
Executes via implement-plan
```

**v9 was a framework** that orchestrated everything for you.

### v10.1: Configuration
```
You: "Build me a CLI" (just say it)
OR: "/interview" (if you want structure)
  ↓
Claude reads relevant rules (~300 tokens)
  ↓
You invoke commands as needed (/cp, /implement, etc.)
```

**v10.1 is configuration** that makes Claude work your way.

---

## Token Breakdown

### v9 Always-On Cost
| Component | Tokens |
|-----------|--------|
| CLAUDE.md | ~2,500 |
| AGENTS.md | ~2,800 |
| Hook context | ~500 |
| **Total** | **~5,800** |

### v10.1 Always-On Cost
| Component | Tokens |
|-----------|--------|
| Core rules | ~150 |
| Project rules (web/cli/service) | ~150 |
| **Total** | **~300** |

**Savings: 95%**

---

## What Was Removed

### v9 Features Removed in v10

| Feature | Why Removed |
|---------|-------------|
| AGENTS.md routing table | You invoke commands directly |
| 52 skills | Replaced with 16 commands |
| Auto-trigger on "build me" | Be explicit: `/interview` |
| Hooks (context injection) | Rules are simpler |
| Skills marketplace | Deferred to future |
| Skill discovery | Not needed for 16 commands |
| Multi-agent coordination | Claude handles natively |
| `/run-plan` deterministic execution | Over-engineering |

---

## What Was Added

### v10.1 New Features

| Feature | Description |
|---------|-------------|
| **Progressive disclosure** | Rules load by project type |
| **"Wait for native" strategy** | Don't duplicate Claude features |
| **Slash commands** | 16 commands, invoke when needed |
| **Native task tools** | Document TaskCreate/Update/Delete usage |
| **Explicit migration** | No auto-switch, user chooses |

---

## Command Mapping: v9 Skills → v10 Commands

| v9 Skill | v10 Command | Change |
|----------|-------------|--------|
| front-door | `/interview` | No longer auto-triggers |
| continuous-planner | `/cp` | Same |
| create-plan | `/cp` | Merged |
| implement-plan | `/implement` | Same |
| freesearch | `/freesearch` | Same |
| deep-research | `/research` | Same |
| thinking-modes | `/think` | Same |
| debugger | `/diagnose` | Same |
| code-reviewer | `/codereview` | Same |
| push-to-cloud | `/deploy` | Same |
| remote-exec | `/remote` | Same |
| the-audit | `/audit` | Same |
| beads | `/beads` | Same |
| create-handoff | `/handoff` | Same |
| resume-handoff | `/restore` | Same |
| secrets-vault-manager | `/secrets` | Same |
| batch-processor | `/batch` | Same |

---

## Rules: v9 Hooks → v10.1 Progressive Disclosure

### v9: Hooks
- `context-v8.py` - Injected compressed context
- `beads-v8.py` - Session close protocol
- `lessons-inject.sh` - Injected lessons at start

### v10.1: Progressive Disclosure
- `core.md` - Always loaded (AGENTS.md, skills, beads, native tools)
- `web.md` - Web apps (Convex + Next.js + Clerk)
- `cli.md` - CLIs (Python + Click + SQLite)
- `service.md` - Services (Python + systemd)
- `khamel-mode.md` - User-specific defaults

**Auto-detection:**
- `package.json` + `convex/` → web rules
- `setup.py` / `pyproject.toml` → cli rules
- `*.service` → service rules

---

## The "Wait for Native" Strategy (NEW in v10.1)

### What It Means

Claude Code is building native features. ONE_SHOT doesn't duplicate them.

| Native Feature | ONE_SHOT Response |
|----------------|-------------------|
| TaskCreate/Update/Delete | Document usage, use `/beads` as fallback |
| TeammateTool (swarm mode) | Wait for stable release |
| Native debug mode | Don't build `/diagnose` (keep for now) |
| Native plan mode | Don't conflict with `/plan` |

### Validation

Testing `claude-sneakpeek` confirmed:
- Native TaskCreate/Update/Delete exist
- Native TeammateTool operations exist
- **v10 simplification was correct**

---

## Migration Guide

### For New Projects

```bash
cd your-project
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/oneshot.sh | bash
```

### For Existing v9 Projects

```bash
cd your-project
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/scripts/migrate-v10.sh | bash
```

**What the migration does:**
1. Removes AGENTS.md
2. Cleans CLAUDE.md (keeps project-specific content)
3. Preserves .beads/
4. Updates .claude/settings.json

---

## Practical Differences

### Session Start

**v9:**
```
Claude loads: AGENTS.md (2800 tokens) + skills (2000 tokens) + hooks (500 tokens)
→ ~5300 tokens before you say anything
```

**v10.1:**
```
Claude loads: core.md (150 tokens) + project rules (150 tokens)
→ ~300 tokens before you say anything
```

### Building Something

**v9:**
```
You: "Build me a CLI"
Claude: [Auto-triggers interview]
```

**v10.1:**
```
You: "Build me a CLI" (Claude just starts)
OR: "/interview" (if you want the structured interview)
```

### Task Tracking

**Same in both:**
```bash
bd ready      # What's next?
bd list       # All tasks
bd sync       # Save to git
```

---

## Why v10.1 Is Better

| Aspect | v9 | v10.1 |
|--------|-----|-------|
| Token efficiency | ~5800 always-on | ~300 always-on |
| Simplicity | 52 skills to understand | 16 commands |
| Alignment | Builds own orchestration | Waits for native |
| Flexibility | Auto-everything | You choose when to invoke |
| Maintenance | Complex routing | Simple rules |

---

## Future: What's Coming

| Feature | Timeline | Notes |
|---------|----------|-------|
| Native task tools stable | When Anthropic ships | Will deprecate `/beads` gently |
| Progressive disclosure refinement | Future | More project types |
| Hybrid native/beads detection | When native available | Explicit migration |

---

## Summary

**v9**: Full framework with auto-routing, 52 skills, ~5800 tokens

**v10**: Simplified to 16 commands, ~425 tokens, 93% reduction

**v10.1**: Added progressive disclosure, ~300 tokens, 95% total reduction

**The philosophy shift**: From building everything to aligning with Claude's native direction.
