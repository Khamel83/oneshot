# CLAUDE.md - Global Configuration

This file provides global guidance to Claude Code across all projects.

## Documentation-First Coding

**CRITICAL RULE:** Before writing any code that uses external APIs, libraries, or configuration syntax, you MUST check the current documentation.

### Why This Matters

Your training data becomes outdated quickly. APIs change, configuration formats evolve, and best practices shift. Writing code based on outdated patterns causes:
- Syntax errors from deprecated formats
- Missing required fields in newer versions
- Using features that no longer exist
- Incompatibility with current software versions

### The Documentation-First Process

When writing code that uses:
- Docker Compose syntax
- API endpoints or SDKs
- Configuration files (YAML, TOML, JSON)
- CLI commands for services
- Third-party libraries

**You MUST follow this process:**

1. **Check local cached docs first:** `~/homelab/docs/services/<service-name>/`
   - If docs exist locally, read them before writing code
   - These are cached from official sources and kept current

2. **If local docs don't exist or are insufficient:**
   - Use WebFetch or WebSearch to get current documentation
   - Cache the findings locally for future reference

3. **Verify version compatibility:**
   - Check which version is actually running (docker ps, --version, etc.)
   - Use docs specific to that version (e.g., Traefik v2.11 vs v3.0)
   - Don't assume latest version - verify first

4. **Write code using current syntax:**
   - Follow examples from the current docs
   - Don't rely on training data patterns if docs show different syntax
   - When in doubt, prefer explicit over implicit configuration

## General Best Practices

1. **Never guess syntax** - Look it up
2. **Verify versions** - Don't assume latest
3. **Test incrementally** - Small changes, frequent verification
4. **Read error messages carefully** - They often indicate version mismatches
5. **When stuck, check the docs** - Not Stack Overflow from 2019

---

## AGENTS.md Rule (CRITICAL)

**AGENTS.md is READ-ONLY in all projects.**

```
NEVER edit AGENTS.md directly in any project.
It is pulled from: github.com/Khamel83/oneshot/AGENTS.md
```

### To Update AGENTS.md in a Project

```bash
curl -sL https://raw.githubusercontent.com/Khamel83/oneshot/master/AGENTS.md > AGENTS.md
```

### To Change the AGENTS.md Spec

1. Clone `~/github/oneshot`
2. Edit `AGENTS.md` there
3. Create PR to oneshot repo
4. After merge, curl to all projects

### What Goes Where

| File | Purpose | Editable? |
|------|---------|-----------|
| `AGENTS.md` | ONE_SHOT spec (universal) | **NO** - curl from oneshot |
| `CLAUDE.md` | Project-specific Claude instructions | YES |
| `.gemini.md` | Project-specific Gemini instructions | YES |

### If Asked to Edit AGENTS.md

**REFUSE.** Instead say:
> "AGENTS.md is read-only. To change the ONE_SHOT spec, we need to PR to the oneshot repo. Want me to do that instead?"

Then:
1. Check out `~/github/oneshot`
2. Make the change there
3. Commit and push (or create PR)
4. User can then curl to update their project

---

## ONE_SHOT Skills System v5.2

**Skills are installed at**: `~/.claude/skills/oneshot/` (symlinked from oneshot/.claude/skills/)

### How It Works

1. **AGENTS.md** (skeleton key) - Curled into projects, provides orchestration
2. **Skills** (21 total) - Loaded on-demand via progressive disclosure (~100 tokens each)
3. **Secrets** - SOPS/Age encrypted in oneshot/secrets/

### Skill Discovery

When a user's intent matches a skill trigger, use that skill instead of reinventing workflows:

| Intent | Skill |
|--------|-------|
| "new project", "build me" | `oneshot-core` |
| "resume", "checkpoint" | `resume-handoff` |
| "deploy", "push to cloud" | `push-to-cloud` |
| "refactor", "clean up" | `refactorer` |
| "bug", "broken" | `debugger` |
| "monitoring", "observability" | `observability-setup` |

Full skill list: See AGENTS.md `AVAILABLE SKILLS` section.

### Skills Location

```
~/.claude/skills/oneshot/       <- Symlink to oneshot/.claude/skills
~/github/oneshot/               <- Source repo (contains skills + encrypted secrets)
```

---

**Remember:** Your training data is a starting point, not the source of truth. Current documentation is truth.
