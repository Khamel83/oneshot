# KHAMEL MODE Rules

When building ANYTHING for this user, assume these defaults without asking.

## Infrastructure

| Machine | Tailscale alias | Tailscale IP | User | Role |
|---|---|---|---|---|
| **MBA** (local) | — | 100.64.121.72 | khamel83 | Primary dev machine |
| **homelab** | `homelab-ts` | 100.112.130.100 | khamel83 | Linux server, 26TB, all Docker |
| **macmini** | `macmini-ts` | 100.113.216.27 | macmini | Mac Mini M1, Apple Silicon GPU |
| **oci-dev** | `oci-ts` | 100.126.13.70 | ubuntu | Cloud VM, services/Postgres/Claude Code |
| **rpi4** | `rpi4` | 100.97.236.22 | RPI3 | Raspberry Pi 4 (currently offline) |
| **work-mbp** | `mbp-ts` | 100.120.127.32 | hr-svp-mac12 | Work MBP (currently offline) |

- **Networking**: All machines on Tailscale (deer-panga.ts.net)
- **Public access**: Tailscale Funnel + poytz (NOT nginx/traefik)
- **Internal tools**: Cloudflare Access (already configured)
- **Secrets**: SOPS/Age, decrypt from `~/github/oneshot/secrets/`

## Stack Defaults (Don't Ask, Just Use)

| Project Type | Default Stack |
|--------------|---------------|
| Web apps | Vercel + Supabase (Auth + Postgres) + Python + HTML/JS |
| CLIs | Python + Click + SQLite |
| Services/APIs | Python + systemd → oci-dev |
| Heavy compute / throughput | Route to macmini |
| Large storage | Route to homelab (26TB) |

**Full stack docs**: `.claude/infrastructure/STACK.md`

## Storage Progression

```
SQLite (default for CLIs) → Supabase Postgres (web apps) → OCI Autonomous DB (>20GB/multi-user)
```

## Auth Default

```
Supabase Auth (email/password + Google OAuth) → sessions in Supabase Postgres
Cloudflare Access → internal/admin tools (already configured)
```

## Tool Enforcement

- **ALWAYS** use beads for task tracking (`bd init` on new projects)
- **ALWAYS** use ONE_SHOT skills when applicable
- **ALWAYS** check lessons before debugging

## Anti-Patterns to Flag

- nginx/traefik → Use Tailscale Funnel + poytz
- mysql/mongodb (self-hosted) → Default is SQLite (CLIs) or Supabase Postgres (web)
- express/fastapi/flask for web → Python serverless on Vercel
- Astro/Cloudflare Workers/Better Auth → Old stack, use Vercel + Supabase + Python
- Convex/Next.js/Clerk → Old stack, use Vercel + Supabase + Python
- aws/gcp/azure → Default is OCI free tier or homelab

## Decision Defaults (Don't Ask, Just Pick)

When ambiguous, apply these defaults without asking for clarification:

| Ambiguity | Default Choice |
|-----------|----------------|
| Multiple valid implementations | **Simplest one** |
| Naming things | Follow existing pattern in file |
| Error handling style | Match surrounding code |
| Test framework | Use existing tests as guide |
| Library choice | One already in project |
| Refactor opportunity | **Skip unless blocking** |
| API design | Match existing endpoints |
| File organization | Follow project structure |

**Key rule**: When truly ambiguous, make a reasonable choice and note the decision.

## When You Notice Drift

If Claude notices we're NOT using beads, Tailscale, ONE_SHOT patterns, or standard stack:
→ **Warn**: "I notice we're not using [X], should I set that up?"
