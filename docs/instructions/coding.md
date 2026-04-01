# Coding Standards

## Project Type Detection

Auto-detect project type from files and use the corresponding stack defaults.

| Detection | Type | Stack |
|-----------|------|-------|
| `astro.config.*` or `wrangler.toml` | Web app | Astro + Cloudflare + Better Auth + Postgres |
| `setup.py` or `pyproject.toml` | CLI | Python + Click + SQLite |
| `*.service` systemd file | Service | Python + systemd → oci-dev |
| No detection | Generic | Defaults only |

## Storage Progression

```
SQLite (default for CLIs) → Postgres on OCI (web/services) → OCI Autonomous DB (>20GB/multi-user)
```

## CLI Projects (Python + Click)

- Use Click for CLI — don't suggest argparse or typer
- Use `@click.group()` for multi-command CLIs
- Use `@click.pass_context` for shared state
- SQLite via `sqlite3` module — no ORM for simple CLIs
- `pyproject.toml` for packaging, console scripts for entry points

## Web Apps (Astro + Cloudflare)

- Astro is the framework — don't suggest Next.js, Remix, SvelteKit
- `@astrojs/cloudflare` adapter for SSR
- Islands architecture: server-first, client directives for interactivity
- Cloudflare Workers for API — don't suggest Express or FastAPI
- Better Auth with Google OAuth — don't suggest Clerk, Auth0, NextAuth
- Postgres on OCI with direct Tailscale connection for local dev
- `postgres` npm package — don't use pg/knex/prisma/drizzle unless needed
- Deploy to Cloudflare Pages

## Services (Python + systemd)

- Deploy to oci-dev as systemd user services
- `~/.config/systemd/user/` for service files
- `Restart=on-failure`, `StandardOutput=journal`
- SQLite for service data, Tailscale for networking

## Anti-Patterns

| Don't suggest | Use instead |
|--------------|-------------|
| nginx, traefik, caddy | Tailscale Funnel |
| postgres, mysql, mongodb | SQLite → Postgres on OCI |
| express, fastapi, flask (for web) | Cloudflare Workers |
| AWS, GCP, Azure | OCI free tier or homelab |
| Docker for local dev | Direct execution |
| Convex, Next.js, Clerk, Vercel | Astro + CF + Better Auth |
| Lucia auth | Better Auth |
| Heavy ORMs | Lightweight or none |
