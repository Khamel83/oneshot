# Cross-Agent Learnings

> Dated entries. Any agent can append.
> Format: `YYYY-MM-DD — [agent] — finding`

2026-05-01 — Codex — Argus on homelab is healthy at `http://100.112.130.100:8270`; live `/api/search` accepts modes `discovery`, `grounding`, `recovery`, and `research`. Oneshot legacy modes are client-side aliases: `cheap` maps to `discovery` with `searxng`, and `precision` maps to `grounding` with `serper`/`tavily`.
2026-05-01 — Codex — Codex MCP requires Argus remote MCP to use streamable HTTP at `http://100.112.130.100:8271/mcp` with `bearer_token_env_var = "ARGUS_API_KEY"`; using the SSH alias `homelab-ts` or legacy SSE `/sse` causes startup failures.
2026-05-01 — Codex — For Codex Argus MCP startup, `~/.bashrc` must initialize `PATH` before vault-backed exports; otherwise clean shells can find `secrets` after startup but skip exporting `ARGUS_API_KEY`.
2026-05-01 — Codex — If Argus MCP still fails immediately after fixing `~/.bashrc`, check whether Codex was relaunched from an already-running shell. Existing shells do not inherit edited startup-file exports; run `source ~/.bashrc && hash -r` or open a new login shell before starting Codex.
