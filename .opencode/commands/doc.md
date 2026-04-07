---
description: Cache external documentation locally
agent: build
---

# /doc — Cache Documentation

Fetches external documentation and saves it locally for offline access.

## Usage

- `/doc <name> <url>` — Cache a document
- `/doc --list` — Show cached documents

## Steps

### Caching a Document

1. `$1` = name, `$2` = URL. If not provided, ask the user.

2. Fetch the URL content using `webfetch` tool or:
   ```bash
   curl -sL "$URL" | head -5000
   ```

3. Create directory and save:
   ```bash
   mkdir -p docs/external/{name}
   ```

4. Write fetched content to `docs/external/{name}/README.md`

5. Update index (`docs/external/.index.md` if it exists)

6. Confirm: "Cached `{name}` to `docs/external/{name}/README.md`"

### Listing Cached Docs

```bash
ls docs/external/ 2>/dev/null
cat docs/external/.index.md 2>/dev/null
```
