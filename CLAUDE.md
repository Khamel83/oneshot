# CLAUDE.md - Global Configuration

This file provides global guidance to Claude Code across all projects.

---

## STOP BEING CLEVER

**YOU ARE A ROBOT. JUST DO THE SIMPLE THING FAST FIRST.**

- Don't edit databases directly when there's a UI
- Don't write scripts when a CLI command exists
- Don't debug for an hour when `docker pull` might fix it
- If there's a 30-second solution, do that before the 30-minute solution

---

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

---

## KHAMEL MODE (Maximum Assumptions)

When building ANYTHING for this user, assume these defaults without asking:

### Infrastructure (Brain/Body/Muscle Model)

| Machine | Tailscale IP | Role |
|---------|--------------|------|
| **oci-dev** | 100.126.13.70 | Services, Claude Code, OCI resources |
| **homelab** | 100.112.130.100 | Docker services, 26TB storage, persistent data |
| **macmini** | 100.113.216.27 | Apple Silicon GPU, transcription, video/audio |

- **Networking**: All machines on Tailscale (deer-panga.ts.net)
- **Public access**: Tailscale Funnel + poytz → khamel.com (NOT nginx/traefik)
- **Secrets**: SOPS/Age, decrypt from `~/github/oneshot/secrets/`

### Stack Defaults (Don't Ask, Just Use)

| Project Type | Default Stack |
|--------------|---------------|
| Web apps | Convex + Next.js + Clerk → Vercel |
| CLIs | Python + Click + SQLite |
| Services/APIs | Python + systemd → oci-dev |
| Heavy compute | Route to macmini |
| Large storage | Route to homelab (26TB) |

### Storage Progression

```
SQLite (default) → Convex (web apps) → OCI Autonomous DB (>20GB/multi-user)
```

### Tool Enforcement

- **ALWAYS** use beads for task tracking (`bd init` on new projects)
- **ALWAYS** use ONE_SHOT skills when applicable
- **ALWAYS** check lessons before debugging

### When You Notice Drift

If Claude notices we're NOT using beads, Tailscale, ONE_SHOT patterns, or standard stack:
→ **Warn**: "I notice we're not using [X], should I set that up?"

### Anti-Patterns to Flag

- nginx/traefik → Use Tailscale Funnel + poytz
- postgres/mysql/mongodb → Default is SQLite → Convex → OCI DB
- express/fastapi/flask for web → Convex handles the backend
- aws/gcp/azure → Default is OCI free tier or homelab

---

## Lessons Learned System

Lessons are stored as beads in `~/.claude/.beads/` with label `lesson`.

- Auto-extracted at session end (no manual `/oops` needed)
- Injected at session start
- Query with: `cd ~/.claude && bd list -l lesson`

---

## ONE_SHOT v8 Context (Ultra-Compressed)

When you see `CTX:{"v":8,...}` at session start, parse this JSON:

```python
import json
ctx = json.loads(CTX_JSON)

# Skill router (ctx.s) - [[trigger, skill], ...]
skills = ctx["s"]  # Auto-routes to skills like "front-door", "debugger"

# Infrastructure (ctx.i) - Use IPs without asking
oci = ctx["i"]["oci"]   # 100.126.13.70
home = ctx["i"]["home"] # 100.112.130.100
mac = ctx["i"]["mac"]   # 100.113.216.27

# Stacks (ctx.k) - Default tech stacks
web = ctx["k"]["web"]   # Convex+Next.js+Clerk->Vercel
cli = ctx["k"]["cli"]   # Python+Click+SQLite
svc = ctx["k"]["svc"]   # Python+systemd->oci

# Beads (ctx.b) - Status counts
ready = ctx["b"]["ready"]  # Tasks ready to work
open_total = ctx["b"]["open"]  # Total open tasks

# Tasks (ctx.t) - Open tasks [{"id":"1","t":"title"}, ...]
# Lessons (ctx.l) - Recent lessons ["lesson1", ...]
# Project (ctx.p) - Setup status {"b":bool,"m":bool,"o":bool,"a":bool}
```

**Key behaviors:**
- Auto-route: "build me X" → front-door skill
- Deploy → oci (100.126.13.70) without asking
- New CLI → Python+Click+SQLite without asking
- Suggest `bd init` if ctx.p["b"] is False

---

## Beads Context (Compressed)

When you see `BEADS:{"proto":"git",...}` at session start:

```python
import json
bd = json.loads(BEADS_JSON)

# Session close protocol (bd.end)
# ["status","add","sync","commit","sync","push"]
# Run this sequence before saying "done"

# Ready tasks (bd.ready)
# [{"id":"1","title":"..."}, ...]
# Use `bd show <id>` for details, `bd update <id> --status=in_progress` to claim
```

**Session close checklist:**
1. `git status` - check what changed
2. `git add <files>` - stage changes
3. `bd sync` - commit beads
4. `git commit -m "..."` - commit code
5. `bd sync` - commit any new beads changes
6. `git push` - push to remote

<!--
  ONE-SHOT Heartbeat Metadata
  oneshot:last-check: 2026-02-02
  oneshot:machine: instance-first
-->

<!--
  ONE-SHOT Heartbeat Metadata
  oneshot:last-check: 2026-02-02
  oneshot:machine: instance-first
-->

<!--
  ONE-SHOT Heartbeat Metadata
  oneshot:last-check: 2026-02-02
  oneshot:machine: instance-first
-->

<!--
  ONE-SHOT Heartbeat Metadata
  oneshot:last-check: 2026-02-02
  oneshot:machine: instance-first
-->

<!--
  ONE-SHOT Heartbeat Metadata
  oneshot:last-check: 2026-02-02
  oneshot:machine: instance-first
-->

<!--
  ONE-SHOT Heartbeat Metadata
  oneshot:last-check: 2026-02-02
  oneshot:machine: instance-first
-->

<!--
  ONE-SHOT Heartbeat Metadata
  oneshot:last-check: 2026-02-02
  oneshot:machine: instance-first
-->

<!--
  ONE-SHOT Heartbeat Metadata
  oneshot:last-check: 2026-02-03
  oneshot:machine: instance-first
-->
