# Skills Index

ONE_SHOT v10.5 - Skills cleanup, context clearing workflow, comprehensive documentation. See docs/SKILLS.md for full reference.

---

## Core Infrastructure

These are foundational files, not skills:

| File | Purpose |
|-------|---------|
| `.claude/infrastructure/STACK.md` | Complete stack reference (Astro → CF Pages → Workers → Hyperdrive → Postgres) |
| `.claude/skills/stack-setup/SKILL.md` | Configure new projects with standard stack |
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
