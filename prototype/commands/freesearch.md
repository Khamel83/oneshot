# /freesearch — Zero-Token Research via Exa API

Uses 0 Claude Code tokens. Calls Exa API directly via curl.

## Usage

`/freesearch [topic]`

## Process

1. Ask 2-3 clarifying questions (goal, depth, audience)
2. Create `docs/research/{date}_{topic}_in_progress.md`
3. Search Exa API via curl:

```bash
# Decrypt Exa key
EXA_KEY=$(sops --decrypt --output-type json ~/github/oneshot/secrets/research_keys.json.encrypted | grep -o '"EXA_API_KEY": "[^"]*"' | cut -d'"' -f4)

# Search
curl -s -X POST 'https://api.exa.ai/search' \
  -H "x-api-key: $EXA_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "[TOPIC]",
    "type": "auto",
    "numResults": 10,
    "contents": { "text": { "maxCharacters": 20000 } }
  }'
```

4. Write results to in-progress file
5. Create `docs/research/{date}_{topic}_final.md` with:
   - Executive summary
   - Key findings
   - Sources with links
   - Related topics
6. Return summary + file path

## Output

```
Key findings:
- [finding 1]
- [finding 2]

Full research: docs/research/YYYY-MM-DD_{topic}_final.md
```

## Notes

- Research takes 10-30 seconds
- Save to project `docs/research/` (not ~/github/oneshot/research/)
- Include user's goal in the search query for better results
