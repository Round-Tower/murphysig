#!/usr/bin/env bash
#
# IndexNow submit — pings api.indexnow.org with every URL in the sitemap so
# Bing, Yandex, Seznam, and Naver re-crawl immediately after a deploy.
#
# Usage:
#   ./site/scripts/submit-indexnow.sh            # submit for real
#   ./site/scripts/submit-indexnow.sh --dry-run  # print the payload, no network
#
# Run AFTER a Netlify deploy — the endpoint verifies the key file is live at
# https://murphysig.dev/<key>.txt before accepting the submission.
#
# Signed: Kev + claude-fable-5, 2026-07-12
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
#
# Context: Part of the search-discoverability pass. The key file in
# site/public/ is the single source of truth (basename = key, per the
# IndexNow contract); the URL list comes from sitemap.xml so this never
# drifts from what we tell Google. Tested via tests/test_indexnow.sh.
#
# Confidence: 0.8 — payload shape is tested; the live POST path is untested
# until the first post-deploy run.
# Open: Worth wiring into deploy.sh so it fires automatically?

set -euo pipefail

HOST="murphysig.dev"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
PUBLIC="$ROOT/site/public"

KEY_FILE="$(find "$PUBLIC" -maxdepth 1 -name '*.txt' | grep -E '/[0-9a-f]{32}\.txt$' | head -1)"
if [ -z "$KEY_FILE" ]; then
    echo "✗  No IndexNow key file found in site/public/ (expected <32-hex>.txt)" >&2
    exit 1
fi
KEY="$(basename "$KEY_FILE" .txt)"

# URL list straight from the sitemap — the one place we curate what's indexable.
URLS="$(grep -o '<loc>[^<]*</loc>' "$PUBLIC/sitemap.xml" | sed -e 's|<loc>||' -e 's|</loc>||')"

URL_JSON="$(printf '%s\n' "$URLS" | sed -e 's|^|        "|' -e 's|$|",|' -e '$ s|,$||')"

PAYLOAD="$(cat <<EOF
{
    "host": "$HOST",
    "key": "$KEY",
    "keyLocation": "https://$HOST/$KEY.txt",
    "urlList": [
$URL_JSON
    ]
}
EOF
)"

if [ "${1:-}" = "--dry-run" ]; then
    printf '%s\n' "$PAYLOAD"
    exit 0
fi

echo "→  Submitting $(printf '%s\n' "$URLS" | wc -l | tr -d ' ') URLs to IndexNow…"
HTTP_CODE="$(curl -s -o /dev/null -w '%{http_code}' \
    -X POST 'https://api.indexnow.org/indexnow' \
    -H 'Content-Type: application/json; charset=utf-8' \
    --data "$PAYLOAD")"

if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "202" ]; then
    echo "✓  IndexNow accepted (HTTP $HTTP_CODE)"
else
    echo "✗  IndexNow returned HTTP $HTTP_CODE" >&2
    exit 1
fi
