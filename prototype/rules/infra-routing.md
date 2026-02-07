# Infrastructure

All machines on Tailscale (deer-panga.ts.net). Use Tailscale IPs directly.

| Machine | IP | Role |
|---------|------|------|
| oci-dev | 100.126.13.70 | Services, APIs, Claude Code, OCI resources |
| homelab | 100.112.130.100 | Docker services, 26TB storage, persistent data |
| macmini | 100.113.216.27 | Apple Silicon GPU, transcription, video/audio |

Route heavy compute to macmini. Route large storage to homelab. Default deploy target is oci-dev.
Public access uses Tailscale Funnel + poytz → khamel.com. Never suggest nginx or traefik.
