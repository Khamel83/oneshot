# KHAMEL MODE Rules

When building ANYTHING for this user, assume these defaults without asking.

## Infrastructure

| Machine | Tailscale IP | Role |
|---------|--------------|------|
| **oci-dev** | 100.126.13.70 | Primary dev, services, Postgres, Claude Code |
| **homelab** | 100.112.130.100 | Personal local infra, 26TB storage |
| **macmini** | 100.113.216.27 | Apple Silicon GPU, tasks needing throughput |

- **Networking**: All machines on Tailscale (deer-panga.ts.net)
- **Public access**: Cloudflare Tunnel + Cloudflare Pages (NOT nginx/traefik)
- **Internal tools**: Cloudflare Access (already configured)
- **Secrets**: SOPS/Age, decrypt from `~/github/oneshot/secrets/`

## Stack Defaults (Don't Ask, Just Use)

| Project Type | Default Stack |
|--------------|---------------|
| Web apps | Astro + Cloudflare Pages/Workers + Better Auth + Postgres on OCI |
| CLIs | Python + Click + SQLite |
| Services/APIs | Python + systemd → oci-dev |
| Heavy compute / throughput | Route to macmini |
| Large storage | Route to homelab (26TB) |

**Full stack docs**: `.claude/infrastructure/STACK.md`

## Storage Progression
```
SQLite (default for CLIs) → Postgres on OCI (web apps, services) → OCI Autonomous DB (>20GB/multi-user)
```

## Auth Default
```
Better Auth + Google OAuth → sessions in Postgres
Cloudflare Access → internal/admin tools (already configured)
```

## Tool Enforcement
- **ALWAYS** use beads for task tracking (`bd init` on new projects)
- **ALWAYS** use ONE_SHOT skills when applicable
- **ALWAYS** check lessons before debugging

## Anti-Patterns to Flag
- nginx/traefik → Use Cloudflare Tunnel / Cloudflare Pages
- mysql/mongodb → Default is SQLite (CLIs) or Postgres on OCI (web/services)
- express/fastapi/flask for web → Cloudflare Workers handles the API
- Convex/Next.js/Clerk/Vercel → Old stack, use Astro + CF + Better Auth + Postgres
- aws/gcp/azure → Default is OCI free tier or homelab
- Lucia auth → Deprecated, use Better Auth

## When You Notice Drift
If Claude notices we're NOT using beads, Tailscale, ONE_SHOT patterns, or standard stack:
→ **Warn**: "I notice we're not using [X], should I set that up?"
