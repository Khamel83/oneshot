# Anti-Patterns — Flag These

If you're about to suggest any of these, stop and use the preferred alternative:

| Don't suggest | Use instead |
|--------------|-------------|
| nginx, traefik, caddy | Tailscale Funnel + poytz |
| postgres, mysql, mongodb | SQLite → Convex → OCI Autonomous DB |
| express, fastapi, flask (for web) | Convex handles the backend |
| AWS, GCP, Azure | OCI free tier or homelab |
| Docker for local dev | Direct execution; Docker only for deployment |

If we're drifting from these defaults, say so: "This uses X instead of Y — intentional?"
