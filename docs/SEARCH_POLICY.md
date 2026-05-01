# Search Policy

## Default: Argus

All worker search goes through **Argus** (`homelab:8270`).

- HTTP API: `http://100.112.130.100:8270`
- MCP server: `http://100.112.130.100:8271/sse`

Argus provides multi-provider search with automatic fallback, ranking (RRF), and budget enforcement.

## Rules

1. **Prefer Argus.** Don't let workers use raw web search APIs directly.
2. **Log queries.** When a worker performs a search, log the query in the task's `status.json` under `search_log[]`.
3. **Include source URLs.** Any claims backed by search results must include source URLs in `result.md`.
4. **Mode selection.**
   - `discovery` — broad exploration, multiple sources (SearXNG, Brave, Exa)
   - `grounding` — targeted queries, high relevance (Serper, Tavily)
   - `recovery` — fallback/recovery lookups (SearXNG, DuckDuckGo, Yahoo)
   - `research` — deep multi-source (all providers)
   - Legacy client aliases: `cheap` -> `discovery` with SearXNG only; `precision` -> `grounding`.
5. **No API keys in prompts.** Workers should not receive raw API keys. Auth is handled by the runner template (env var injection).
6. **Fallback.** If Argus is unreachable, the runner can use direct provider APIs as a fallback. Log the fallback in `search_log[]`.
7. **Cost awareness.** `grounding` and `research` modes can cost money. Default to `discovery` or the `cheap` alias for routine tasks.

## Configuration

Search behavior is configured in `.oneshot/config/models.yaml` under the `search:` block:

```yaml
search:
  preferred: argus
  argus:
    enabled: false  # will be true when runner execution is live
    mcp_server_name: argus
    cli_command: "argus search"
```

In the MVP, search is policy-only (docs + configuration). Live runner integration with Argus comes in a follow-up.

## Worker Search Access

When real runners ship, workers get Argus access via:

1. **MCP** — if the runner supports MCP servers (OpenCode), the Argus MCP server is available at the configured URL.
2. **HTTP** — direct API calls to `http://100.112.130.100:8270/api/search`.
3. **CLI** — `argus search` command if the Argus CLI is installed in the worktree.

The runner template handles auth injection — workers never see raw API keys.
