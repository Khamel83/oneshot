# Search Rules

## Search Plane: Argus

All web search goes through Argus, the unified search broker running on port 8005.

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

### Using Argus

**From skills**: Route search tasks to Argus via the config.
The search mode is determined by the task class (see `task-classes.md`).

**From code**: Use the Python client.
```python
from core.search.argus_client import search, health, is_available

results = search("fastapi best practices", mode="discovery")
```

**From CLI**: Use curl or the Argus CLI.
```bash
curl -X POST http://localhost:8005/api/search \
  -d '{"query": "...", "mode": "discovery"}'
```

### Fallback

If Argus is unreachable:
1. Check `config/search.yaml` for the mode's provider list
2. Call the first available provider directly
3. Never hardcode provider logic in skill prompts — always read from config

## /research Skill

Background research uses Argus as the primary backend:
1. Read search config for the appropriate mode
2. Query Argus with the research prompt
3. Use a cheap model to summarize findings
4. Optional: Claude final synthesis for complex topics

Legacy fallback: Gemini CLI is available as a secondary research tool.

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
