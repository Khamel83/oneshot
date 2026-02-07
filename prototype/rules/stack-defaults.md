# Stack Defaults

Don't ask what stack to use. Use these:

| Project type | Stack |
|-------------|-------|
| Web apps | Convex + Next.js + Clerk → deploy to Vercel |
| CLIs | Python + Click + SQLite |
| Services/APIs | Python + systemd → deploy to oci-dev |
| Heavy compute | Route to macmini via SSH |
| Large storage | Route to homelab |

Storage progression: SQLite (default) → Convex (web apps) → OCI Autonomous DB (>20GB or multi-user).
