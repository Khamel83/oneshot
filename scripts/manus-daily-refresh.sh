#!/usr/bin/env bash
# Trigger Manus daily credit refresh by loading manus.im with session cookie.
# Session cookie is stored in the oneshot vault (MANUS_SESSION_ID).
# Run via cron: 57 0 * * * /home/ubuntu/github/oneshot/scripts/manus-daily-refresh.sh

set -euo pipefail

SESSION_ID=$(secrets get MANUS_SESSION_ID 2>/dev/null)
if [ -z "$SESSION_ID" ]; then
    echo "manus-daily-refresh: MANUS_SESSION_ID not found in vault, skipping"
    exit 1
fi

# Check if JWT is expired (exp claim)
EXP=$(echo "$SESSION_ID" | cut -d. -f2 | python3 -c "
import sys, json, base64
payload = sys.stdin.read().strip()
payload += '=' * (4 - len(payload) % 4)
print(json.loads(base64.urlsafe_b64decode(payload)).get('exp', 0))
" 2>/dev/null || echo "0")
NOW=$(date +%s)
if [ -n "$EXP" ] && [ "$NOW" -gt "$EXP" ]; then
    echo "manus-daily-refresh: session JWT expired ($(date -d @$EXP), need re-login)"
    exit 1
fi

# Hit manus.im with the session cookie to trigger daily credit refresh
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -b "session_id=$SESSION_ID" "https://manus.im" --max-time 15)

if [ "$HTTP_CODE" = "200" ]; then
    echo "manus-daily-refresh: OK (HTTP $HTTP_CODE) $(date -I)"
else
    echo "manus-daily-refresh: FAILED (HTTP $HTTP_CODE) $(date -I)"
    exit 1
fi
