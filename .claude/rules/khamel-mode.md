# KHAMEL MODE Rules

When building ANYTHING for this user, assume these defaults without asking.

## Infrastructure (Brain/Body/Muscle Model)

| Machine | Tailscale IP | Role |
|---------|--------------|------|
| **oci-dev** | 100.126.13.70 | Services, Claude Code, OCI resources |
| **homelab** | 100.112.130.100 | Docker services, 26TB storage, persistent data |
| **macmini** | 100.113.216.27 | Apple Silicon GPU, transcription, video/audio |

- **Networking**: All machines on Tailscale (deer-panga.ts.net)
- **Public access**: Tailscale Funnel + poytz → khamel.com (NOT nginx/traefik)
- **Secrets**: SOPS/Age, decrypt from `~/github/oneshot/secrets/`

## Stack Defaults (Don't Ask, Just Use)

| Project Type | Default Stack |
|--------------|---------------|
| Web apps | Convex + Next.js + Clerk → Vercel |
| CLIs | Python + Click + SQLite |
| Services/APIs | Python + systemd → oci-dev |
| Heavy compute | Route to macmini |
| Large storage | Route to homelab (26TB) |

## Storage Progression
```
SQLite (default) → Convex (web apps) → OCI Autonomous DB (>20GB/multi-user)
```

## Tool Enforcement
- **ALWAYS** use beads for task tracking (`bd init` on new projects)
- **ALWAYS** use ONE_SHOT skills when applicable
- **ALWAYS** check lessons before debugging

## Anti-Patterns to Flag
- nginx/traefik → Use Tailscale Funnel + poytz
- postgres/mysql/mongodb → Default is SQLite → Convex → OCI DB
- express/fastapi/flask for web → Convex handles the backend
- aws/gcp/azure → Default is OCI free tier or homelab

## When You Notice Drift
If Claude notices we're NOT using beads, Tailscale, ONE_SHOT patterns, or standard stack:
→ **Warn**: "I notice we're not using [X], should I set that up?"
