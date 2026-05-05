# Archived

OneShot has been replaced by a three-layer architecture:

| Layer | What | Maintainer |
|-------|------|------------|
| **Janus** | Work packets, task visibility, CLI, MCP, dashboard | You |
| **Superpowers** | Workflow discipline (brainstorming, TDD, code review, etc.) | Obra/community |
| **Claude Octopus** | Multi-model orchestration and lane routing | Nyldn/community |
| **Homelab** | Infrastructure, secrets, Argus, Janitor | You |

Skills migrated to Superpowers. Secrets migrated to homelab. Secrets vault:
`~/github/homelab/secrets/` — accessed via `secrets get/set/list` CLI.

See `~/github/Janus/` for the active hub and `~/github/homelab/` for fleet infrastructure.
