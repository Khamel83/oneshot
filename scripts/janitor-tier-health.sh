#!/bin/bash
# Janitor tier health smoke test.
#
# Hits every model in each tier with a tiny prompt, records success + latency
# to .janitor/tier-health.json. Run weekly (or on demand) to spot dead models
# before they cause fallback cascades.
#
# Usage: bash scripts/janitor-tier-health.sh [PROJECT_DIR]
#   PROJECT_DIR defaults to ~/github/oneshot

set -euo pipefail

export PATH="${HOME}/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:${PATH:-}"

ONESHOT_DIR="${HOME}/github/oneshot"
PROJECT_DIR="${1:-$ONESHOT_DIR}"
JANITOR_DIR="${PROJECT_DIR}/.janitor"
mkdir -p "$JANITOR_DIR"

export OPENROUTER_API_KEY="$(secrets get OPENROUTER_API_KEY 2>/dev/null)" || true

if [ -z "$OPENROUTER_API_KEY" ]; then
  echo "ERROR: No OPENROUTER_API_KEY" >&2
  exit 1
fi

python3 -c "
import json, time, urllib.request, urllib.error, sys
from datetime import datetime, timezone

ENDPOINT = 'https://openrouter.ai/api/v1/chat/completions'

# Same tiers as worker.py
TIERS = {
    'smart': [
        'openai/gpt-oss-120b:free',
        'qwen/qwen3-coder-480b-a35b-07-25:free',
        'nvidia/nemotron-3-super-120b-a12b-20230311:free',
    ],
    'cheap': [
        'nvidia/nemotron-3-nano-30b-a3b:free',
        'openai/gpt-oss-20b:free',
        'openrouter/free',
    ],
}

api_key = '$OPENROUTER_API_KEY'
results = {'ts': datetime.now(timezone.utc).isoformat(), 'tiers': {}}

for tier_name, models in TIERS.items():
    tier_results = []
    for model in models:
        start = time.time()
        entry = {'model': model, 'ok': False, 'latency_s': 0, 'model_used': model, 'error': None}
        try:
            body = json.dumps({
                'model': model,
                'messages': [{'role': 'user', 'content': 'Reply OK'}],
                'max_tokens': 5,
                'temperature': 0,
            }).encode()
            req = urllib.request.Request(ENDPOINT, data=body, headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read())
                entry['model_used'] = data.get('model', model)
                entry['latency_s'] = round(time.time() - start, 2)
                entry['ok'] = True
        except urllib.error.HTTPError as e:
            entry['latency_s'] = round(time.time() - start, 2)
            try:
                err_body = json.loads(e.read())
                entry['error'] = err_body.get('error', {}).get('message', str(e))
            except Exception:
                entry['error'] = str(e)
        except Exception as e:
            entry['latency_s'] = round(time.time() - start, 2)
            entry['error'] = str(e)
        tier_results.append(entry)
        status = 'OK' if entry['ok'] else 'FAIL'
        used = entry.get('model_used', '?')
        print(f'  {tier_name}/{model}: {status} ({entry[\"latency_s\"]}s) via {used}')
        if entry['error']:
            print(f'    error: {entry[\"error\"][:120]}')
        time.sleep(1)  # rate-limit courtesy
    results['tiers'][tier_name] = tier_results

out = '$JANITOR_DIR/tier-health.json'
with open(out, 'w') as f:
    json.dump(results, f, indent=2)
print(f'\nSaved to {out}')
" 2>&1

# Summary: any failures?
python3 -c "
import json
with open('$JANITOR_DIR/tier-health.json') as f:
    data = json.load(f)
fails = []
for tier, entries in data['tiers'].items():
    for e in entries:
        if not e['ok']:
            fails.append(f'{tier}: {e[\"model\"]} — {e.get(\"error\",\"?\")[:80]}')
if fails:
    print(f'\nWARNING: {len(fails)} model(s) failed:')
    for f in fails:
        print(f'  - {f}')
else:
    print('\nAll tiers healthy.')
"
