---
description: Build or refresh documentation and research packs through Argus
agent: build
---

# /doc — Build Documentation Corpus

Uses Argus on homelab to collect official docs, related research, and site summaries into the Argus-managed corpus.

## Usage

- `/doc <topic> <url>` — Build a docs + research pack
- `/doc site <url>` — Capture the important parts of a site with references
- `/doc recover <url>` — Recover a dead article
- `/doc --list` — Show where Argus stores imported docs locally if mirrored on this machine

## Steps

### Build a Docs + Research Pack

1. `$1` = topic, `$2` = official docs URL. If not provided, ask the user.
2. Use Argus, not ad hoc scraping:
   - `python -c "from core.search import argus_client; import json; print(json.dumps(argus_client.build_research_pack('<topic>', official_url='<url>'), indent=2))"`
3. Tell the user:
   - Argus stores the canonical corpus on homelab under `/mnt/main-drive/appdata/argus`
   - imported legacy docs-cache content lives under `/mnt/main-drive/appdata/argus/docs`
4. If the user wants a local project copy, mirror only the generated report or selected extracted docs into the project after the Argus run completes.

### Capture a Site Summary

1. `$2` = URL
2. Run:
   ```bash
   python -c "from core.search import argus_client; import json; print(json.dumps(argus_client.capture_site('<url>'), indent=2))"
   ```
3. Report the `run_id`, `status_url`, and the eventual `report_path` once available.

### Recover a Dead Article

1. `$2` = dead URL
2. Run:
   ```bash
   python -c "from core.search import argus_client; import json; print(json.dumps(argus_client.recover_article('<url>'), indent=2))"
   ```
3. Poll workflow status if the user wants the recovered report immediately.

### Listing Docs

Use:
- `python -c "from core.search import argus_client; import json; print(json.dumps({'base_url': argus_client.get_base_url(), 'api_key': bool(argus_client.get_api_key())}, indent=2))"`
- `echo ${DOCS_CACHE:-$HOME/.local/share/argus/argus/docs/cache}`
