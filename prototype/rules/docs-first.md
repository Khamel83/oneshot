# Documentation-First Rule

Before writing code that uses external APIs, libraries, or config syntax:

1. Check what version is actually running (`--version`, `docker ps`, etc.)
2. Use WebSearch/WebFetch to get docs for THAT version
3. Don't rely on training data for syntax — it goes stale

This especially applies to: Docker Compose syntax, Convex APIs, OCI SDKs, Tailscale config.
