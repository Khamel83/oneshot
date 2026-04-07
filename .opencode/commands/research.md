---
description: Search via Argus search broker
agent: build
---

# /research — Argus Search

Search the web via Argus broker using `core.search.argus_client`.

## Usage

`/research <topic>` or `/research`

## Steps

1. Check Argus availability:
   ```bash
   python3 -c "from core.search.argus_client import is_available; print(is_available())"
   ```

2. Search (mode depends on task class):
   ```bash
   python3 -c "
   from core.search.argus_client import search
   result = search('TOPIC', mode='discovery', max_results=10)
   print(result)
   "
   ```

   Valid modes: `discovery`, `grounding`, `recovery`, `research`

3. Extract key findings from results and return structured summary.

## If Argus is Unavailable

Fall back to OpenCode's built-in `websearch` tool.
