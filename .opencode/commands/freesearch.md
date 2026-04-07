---
description: Quick web search via Argus (zero token cost)
agent: build
---

# /freesearch — Quick Search

Zero-token web search using Argus in discovery mode. Returns results directly without summarization.

## Usage

`/freesearch <query>`

## Steps

1. If no query provided (`$ARGUMENTS` is empty), ask the user what to search for.

2. Search via Argus:
   ```bash
   python3 -c "
   from core.search.argus_client import search
   result = search('$ARGUMENTS', mode='discovery', max_results=5)
   for r in result.get('results', []):
       title = r.get('title', '')
       url = r.get('url', '')
       print(f'- {title}')
       print(f'  {url}')
   "
   ```

3. Return results directly. No LLM summarization needed.

## If Argus is Unavailable

Fall back to OpenCode's built-in `websearch` tool.
