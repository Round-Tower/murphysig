#!/usr/bin/env bash
#
# Signed: Kev + claude-fable-5, 2026-07-12
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
#
# Context: Tests for the IndexNow submit script. Network is never touched —
# the script's --dry-run mode prints the JSON payload it would POST, and we
# assert on that plus the key-file invariants (name is 32 hex chars, content
# equals basename — the IndexNow verification contract).
#
# Confidence: 0.8 — covers payload shape and key contract. The live POST path
# is a curl one-liner, exercised only in production after deploys.

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SUBMIT="$ROOT/site/scripts/submit-indexnow.sh"
PASS=0
FAIL=0
FAILED_NAMES=()

assert_contains() {
    local haystack="$1" needle="$2" label="$3"
    if printf '%s' "$haystack" | grep -qF "$needle"; then
        PASS=$((PASS + 1))
        echo "  ✓ $label"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$label")
        echo "  ✗ $label"
        echo "      expected to contain: $needle"
    fi
}

echo "test: key file exists and honors the IndexNow contract"
KEY_FILE="$(find "$ROOT/site/public" -maxdepth 1 -name '*.txt' | grep -E '/[0-9a-f]{32}\.txt$' | head -1)"
if [ -n "$KEY_FILE" ]; then
    PASS=$((PASS + 1)); echo "  ✓ key file present"
    KEY="$(basename "$KEY_FILE" .txt)"
    assert_contains "$(cat "$KEY_FILE")" "$KEY" "key file content equals its basename"
else
    FAIL=$((FAIL + 2)); FAILED_NAMES+=("key file present" "key file content equals its basename")
    echo "  ✗ key file present"; echo "  ✗ key file content equals its basename"
    KEY="MISSING"
fi

echo "test: dry-run payload is a valid IndexNow submission"
OUT="$(bash "$SUBMIT" --dry-run 2>&1)"
assert_contains "$OUT" '"host": "murphysig.dev"' "payload names the host"
assert_contains "$OUT" "$KEY" "payload carries the key"
assert_contains "$OUT" "https://murphysig.dev/$KEY.txt" "payload states the keyLocation"
assert_contains "$OUT" "https://murphysig.dev/" "payload includes the homepage"
assert_contains "$OUT" "https://murphysig.dev/llms.txt" "payload includes llms.txt"
assert_contains "$OUT" "https://murphysig.dev/benchmark/" "payload includes benchmark (from sitemap)"

echo ""
echo "passed: $PASS  failed: $FAIL"
if [ "$FAIL" -gt 0 ]; then
    printf '  failed: %s\n' "${FAILED_NAMES[@]}"
    exit 1
fi
