# Search Rules

## Search Plane: Argus

All web search goes through a **single Argus instance running on homelab** (`100.112.130.100`).
Do not run Argus locally on other machines — point everything at homelab.

- **HTTP API**: `http://100.112.130.100:8270` — used by skills and Python client
- **MCP server**: `http://100.112.130.100:8271/sse` — registered in `~/.claude/settings.json` on all machines

**Argus supports**: SearXNG, Brave, Serper, Tavily, Exa — with automatic
provider selection, fallback, ranking (RRF), and budget enforcement.

### Search Modes

| Mode | Providers | Use Case |
|------|-----------|----------|
| discovery | searxng, brave, exa | Broad exploration, multiple sources |
| precision | serper, tavily | Targeted queries, high relevance |
| cheap | searxng only | Quick lookups, cost-sensitive |
| research | searxng, brave, exa, tavily | Deep research, comprehensive |

Config: `config/search.yaml`

### How to Use Argus

**Natural language (preferred)** — just ask Claude to search. The `mcp__argus__search_web`
MCP tool is available in every Claude Code session on every machine. No special command needed:
> "Search for recent fastapi performance tips"
> "Look up the Tailscale ACL syntax"

Claude will call `mcp__argus__search_web` automatically. This costs zero Claude tokens
for the search itself.

**`/freesearch [topic]`** — explicit zero-token search via Argus cheap mode (SearXNG).
Use when you want to be explicit or are in a non-Claude session.

**`/research [topic]`** — deep multi-source research spawned as a background agent.
Use for comprehensive research across multiple providers.

**From code**: Use the Python client (reads `config/search.yaml` for the homelab URL).
```python
from core.search.argus_client import search, health, is_available

results = search("fastapi best practices", mode="discovery")
```

**From CLI**: Direct curl to homelab.
```bash
curl -s -X POST http://100.112.130.100:8270/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "...", "mode": "discovery"}'
```

### Fallback

If Argus is unreachable (homelab down):
1. Check `config/search.yaml` for the mode's provider list
2. Call the first available provider directly
3. Never hardcode provider logic in skill prompts — always read from config

Gemini CLI is the last-resort fallback for `/research` only.

## /research Skill

Background research uses Argus as the primary backend:
1. Read search config for the appropriate mode
2. Query Argus with the research prompt
3. Use a cheap model to summarize findings
4. Optional: Claude final synthesis for complex topics

Fallback to Gemini CLI only if homelab Argus is unreachable.

## /freesearch Skill

Zero-token web search:
1. Check docs cache first (`~/github/docs-cache/docs/cache/.index.md`)
2. Query Argus in `cheap` mode (SearXNG only)
3. Return results directly

## Doc Caching

Cache external documentation locally for offline/fast access:
- Cache location: `~/github/docs-cache/docs/cache/`
- Check index first: `cat ~/github/docs-cache/docs/cache/.index.md`
- Use `/doc` skill to cache new documentation
