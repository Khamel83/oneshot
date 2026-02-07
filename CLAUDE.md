# CLAUDE.md - ONE_SHOT Project Configuration

**This is the ONE_SHOT project's CLAUDE.md.** For your own projects, use a minimal version.

---

## Progressive Disclosure: Load Rules by Project Type

**Core rules always load**: `~/.claude/rules/core.md`

**Project-specific rules load based on detection**:

| Project Type | Trigger | Rules |
|--------------|---------|-------|
| Web app | `package.json` + `convex/` | `~/.claude/rules/web.md` |
| CLI | `setup.py` or `pyproject.toml` | `~/.claude/rules/cli.md` |
| Service | `*.service` or long-running `*.py` | `~/.claude/rules/service.md` |
| Generic | None detected | Core rules only |

**User-specific defaults**: `~/.claude/rules/khamel-mode.md`

---

## For This Project (ONE_SHOT)

ONE_SHOT is the framework itself. Read core rules + all project type rules for full context.

```
Core: ~/.claude/rules/core.md
Web: ~/.claude/rules/web.md
CLI: ~/.claude/rules/cli.md
Service: ~/.claude/rules/service.md
KhameL: ~/.claude/rules/khamel-mode.md
```

---

## Quick Reference

- **New project?** → `~/.claude/skills/oneshot/core/build/project.md` skill
- **Task tracking** → `/beads` command
- **Deployment** → oci-dev (100.126.13.70) via Tailscale
- **Stack defaults** → See `khamel-mode.md`

---

## Token Savings

| Before (full CLAUDE.md) | After (progressive) |
|------------------------|---------------------|
| ~2000 tokens | ~300 tokens |

**Savings: 85%**

---

<!--
  ONE-SHOT Heartbeat Metadata
  oneshot:last-check: 2026-02-06
  oneshot:machine: instance-first
-->
