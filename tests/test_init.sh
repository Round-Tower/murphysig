#!/usr/bin/env bash
#
# Signed: Kev + claude-fable-5, 2026-07-12
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
#
# Context: Pure-bash smoke tests for site/public/init.sh (the curl | bash
# installer). Same zero-dependency pattern as test_sig.sh — isolated tmpdirs,
# stdin-free runs, assertions on emitted files and stdout. Written first (TDD)
# for the AGENTS.md discovery path; the CLAUDE.md cases lock in behavior that
# previously had no coverage.
#
# Confidence: 0.8 — covers the discovery matrix (neither / CLAUDE.md / AGENTS.md
# / both) and idempotency. Doesn't test the git-config author fallback chain.
# Open: Should CI run these? Currently invoked directly, like test_sig.sh.

set -uo pipefail

INIT="$(cd "$(dirname "$0")/.." && pwd)/site/public/init.sh"
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

assert_count() {
    local file="$1" needle="$2" expected="$3" label="$4"
    local actual
    actual="$(grep -cF "$needle" "$file")"
    if [ "$actual" = "$expected" ]; then
        PASS=$((PASS + 1))
        echo "  ✓ $label"
    else
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$label")
        echo "  ✗ $label"
        echo "      expected $expected occurrence(s) of '$needle', got $actual"
    fi
}

mk_workspace() {
    local dir
    dir="$(mktemp -d)"
    cd "$dir" || exit 1
}

echo "test: fresh run writes .murphysig"
mk_workspace
OUT="$(bash "$INIT" 2>&1)"
assert_contains "$OUT" "Wrote .murphysig" "reports the write"
assert_contains "$(cat .murphysig)" "Never Fabricate Provenance" "file carries the honesty rule"
assert_contains "$(cat .murphysig)" "$(date +%Y-%m-%d)" "file is stamped with today"

echo "test: re-run leaves existing .murphysig untouched"
OUT="$(bash "$INIT" 2>&1)"
assert_contains "$OUT" "already exists" "reports idempotent skip"

echo "test: CLAUDE.md gains the @.murphysig import, once"
mk_workspace
printf '# My Project\n' > CLAUDE.md
bash "$INIT" > /dev/null 2>&1
assert_contains "$(head -1 CLAUDE.md)" "@.murphysig" "import is prepended"
bash "$INIT" > /dev/null 2>&1
assert_count CLAUDE.md "@.murphysig" 1 "import is not duplicated on re-run"

echo "test: AGENTS.md gains a MurphySig reference, once"
mk_workspace
printf '# Agent Guide\n' > AGENTS.md
bash "$INIT" > /dev/null 2>&1
assert_contains "$(head -1 AGENTS.md)" ".murphysig" "reference is prepended"
bash "$INIT" > /dev/null 2>&1
assert_count AGENTS.md ".murphysig" 1 "reference is not duplicated on re-run"

echo "test: both CLAUDE.md and AGENTS.md handled in one run"
mk_workspace
printf '# My Project\n' > CLAUDE.md
printf '# Agent Guide\n' > AGENTS.md
OUT="$(bash "$INIT" 2>&1)"
assert_contains "$OUT" "CLAUDE.md" "mentions CLAUDE.md"
assert_contains "$OUT" "AGENTS.md" "mentions AGENTS.md"
assert_contains "$(head -1 CLAUDE.md)" "@.murphysig" "CLAUDE.md import present"
assert_contains "$(head -1 AGENTS.md)" ".murphysig" "AGENTS.md reference present"

echo "test: hint covers both discovery files when neither exists"
mk_workspace
OUT="$(bash "$INIT" 2>&1)"
assert_contains "$OUT" "CLAUDE.md" "hint mentions CLAUDE.md"
assert_contains "$OUT" "AGENTS.md" "hint mentions AGENTS.md"

echo ""
echo "passed: $PASS  failed: $FAIL"
if [ "$FAIL" -gt 0 ]; then
    printf '  failed: %s\n' "${FAILED_NAMES[@]}"
    exit 1
fi
