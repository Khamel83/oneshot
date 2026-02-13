# Skills Index

ONE_SHOT v11 - Native Tasks + Swarms. Migrated from Beads to native Tasks, added /swarm for agent teams.

**For command reference, see [docs/SKILLS.md](../../docs/SKILLS.md).**

---

## v11 Highlights

- **Native Tasks**: TaskCreate, TaskGet, TaskUpdate, TaskList (Beads deprecated)
- **/swarm**: Agent team orchestration (experimental)
- **External models**: NOT supported in swarms (Claude only)

---

## Where Commands Live

**Slash commands are loaded from `~/.claude/commands/`, NOT `~/.claude/skills/`.**

```
~/.claude/commands/stack-setup.md  →  /stack-setup (loaded by Claude)
~/.claude/skills/                  →  Reference docs only (NOT loaded)
```

To add a new command:
1. Create `~/.claude/commands/<name>.md` with frontmatter (name, description)
2. It auto-appears in the skills list on next session

---

## Core Infrastructure

| File | Purpose |
|-------|---------|
| `.claude/infrastructure/STACK.md` | Complete stack reference |
| `~/.claude/commands/stack-setup.md` | `/stack-setup` command |
| `AGENTS.md` | Skill router (curl from oneshot, read-only) |

---

## Stack Quick Reference

```
Frontend: Cloudflare Pages (Astro)
API:      Cloudflare Workers
Database: Postgres on OCI via Hyperdrive
Tunnel:   pg.khamel.com → 100.126.13.70:5432
Auth:     Better Auth + Google OAuth
Deploy:   Cloudflare Pages (free)
```

---

## See AGENTS.md

All skill routing and slash commands are defined in `AGENTS.md`. Use `/skill-name` to invoke.

For full skill catalog, see archive/v9/skills/INDEX.md (v9 had 50+ skills; v10 uses on-demand slash commands instead).
