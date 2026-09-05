#!/usr/bin/env bash
#
# Signed: Kev + claude-opus-4-7, 2026-04-23
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
# Prior: Unknown (no signature existed before this edit)
#
# Context: Pure-bash smoke tests for bin/sig. Drives each command via stdin pipes
# and asserts on emitted file contents. No external test runner — keeps the
# CLI's "no dependencies" promise. Each test runs in an isolated tmpdir so
# state can't leak between cases.
#
# Confidence: 0.7 — covers the five regressions caught by the audit. Doesn't
# exhaustively cover every comment style or every flag combination.
# Open: Should we wire this into CI? Currently runs only when invoked directly.
#
# Review: Kev + claude-fable-5-1, 2026-09-05 — added the drift/summary gallery test
# (git repo with a back-dated commit; hooks disabled in the fixture repo so the
# global pre-commit doesn't fire inside a test). Confidence 0.75.
#
# Review: Kev + claude-fable-5-1, 2026-09-05 — three more gallery tests (fenced
# example skipped, inline Review: counted, single-commit file has no drift); the
# drift fixture now makes a real second commit. Confidence 0.8.

set -uo pipefail

SIG="$(cd "$(dirname "$0")/.." && pwd)/bin/sig"
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
        echo "      got: $haystack" | head -3
    fi
}

assert_not_contains() {
    local haystack="$1" needle="$2" label="$3"
    if printf '%s' "$haystack" | grep -qF "$needle"; then
        FAIL=$((FAIL + 1))
        FAILED_NAMES+=("$label")
        echo "  ✗ $label"
        echo "      should NOT contain: $needle"
    else
        PASS=$((PASS + 1))
        echo "  ✓ $label"
    fi
}

mk_workspace() {
    local d
    d=$(mktemp -d)
    echo "$d"
}

# ─────────────────────────────────────────────────────────────────────────
echo "test_emits_v04_format_for_python"
{
    d=$(mk_workspace) && cd "$d"
    echo "def add(a, b): return a + b" > pkg.py
    printf "claude-opus-4-7\nA function\n0.8\nuncertainty rationale\nNone\n" \
        | "$SIG" add pkg.py > /dev/null 2>&1
    out=$(cat pkg.py)
    assert_contains "$out" "Format: MurphySig v0.4" "emits v0.4 in Format line"
    assert_not_contains "$out" "v0.3.3" "no longer emits v0.3.3"
    cd / && rm -rf "$d"
}

echo "test_emits_v04_format_for_kotlin"
{
    d=$(mk_workspace) && cd "$d"
    echo 'fun greet() = "hi"' > pkg.kt
    printf "claude-opus-4-7\nA greeter\n0.9\nnone\nNone\n" \
        | "$SIG" add pkg.kt > /dev/null 2>&1
    out=$(cat pkg.kt)
    assert_contains "$out" "Format: MurphySig v0.4" "kotlin block-comment also v0.4"
    cd / && rm -rf "$d"
}

echo "test_author_env_var_overrides_git"
{
    d=$(mk_workspace) && cd "$d"
    echo "x = 1" > pkg.py
    MURPHYSIG_AUTHOR="Kev" printf "claude-opus-4-7\nctx\n0.7\nrationale\nNone\n" \
        | MURPHYSIG_AUTHOR="Kev" "$SIG" add pkg.py > /dev/null 2>&1
    out=$(cat pkg.py)
    assert_contains "$out" "Signed: Kev + claude-opus-4-7" "MURPHYSIG_AUTHOR env wins over git"
    cd / && rm -rf "$d"
}

echo "test_author_file_overrides_git"
{
    d=$(mk_workspace) && cd "$d"
    echo "Kev" > .murphysig.author
    echo "x = 1" > pkg.py
    printf "claude-opus-4-7\nctx\n0.7\nrationale\nNone\n" \
        | "$SIG" add pkg.py > /dev/null 2>&1
    out=$(cat pkg.py)
    assert_contains "$out" "Signed: Kev + claude-opus-4-7" ".murphysig.author file wins over git"
    cd / && rm -rf "$d"
}

echo "test_gallery_handles_pipe_in_signature_content"
{
    d=$(mk_workspace) && cd "$d"
    cat > evil.py <<'EOF'
# Signed: Kev + claude-opus-4-7 | extra | pipes
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
#
# Context: A | with | many | pipes
#
# Confidence: 0.5 - rationale text
# Open: None
x = 1
EOF
    out=$("$SIG" gallery 2>&1)
    assert_contains "$out" "evil.py" "gallery still finds the file"
    assert_contains "$out" "0.5" "confidence is parsed even when sig content has pipes"
    cd / && rm -rf "$d"
}

echo "test_gallery_shows_drift_and_review_summary"
{
    d=$(mk_workspace) && cd "$d"
    git init -q . && git config user.email t@t && git config user.name t && git config core.hooksPath /dev/null
    cat > old.py <<'EOF'
# Signed: Kev + claude-opus-4-7, 2026-01-01
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
#
# Context: Test fixture
#
# Confidence: 0.7 - tested
# Open: None
x = 1
EOF
    cat > fresh.py <<'EOF'
# Signed: Kev + claude-opus-4-7, 2026-01-01
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
#
# Confidence: 0.7 - tested
#
# Reviews:
#
# 2026-03-01 (Kev + claude-opus-4-7): Reviewed. Confidence now 0.8.
y = 2
EOF
    git add . >/dev/null && GIT_AUTHOR_DATE=2026-01-01T12:00:00 GIT_COMMITTER_DATE=2026-01-01T12:00:00 git commit -qm signed
    echo "x = 2" >> old.py
    git add . >/dev/null && GIT_AUTHOR_DATE=2026-03-01T12:00:00 GIT_COMMITTER_DATE=2026-03-01T12:00:00 git commit -qm drifted
    out=$("$SIG" gallery 2>&1)
    assert_contains "$out" "Drift: 59d" "gallery shows days between signature and last commit"
    assert_contains "$out" "unreviewed" "gallery flags a drifted file with no review"
    assert_contains "$out" "1/2 reviewed (50%)" "gallery prints the review-rate summary"
    cd / && rm -rf "$d"
}

echo "test_review_has_period_before_confidence"
{
    d=$(mk_workspace) && cd "$d"
    cat > pkg.py <<'EOF'
# Signed: Kev + claude-opus-4-7, 2026-04-01
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
#
# Context: Test fixture
#
# Confidence: 0.7 - tested
# Open: None
x = 1
EOF
    "$SIG" review pkg.py --reviewer "Kev + claude-opus-4-7" \
        --text "Smoke check passed" --confidence 0.8 > /dev/null 2>&1
    out=$(cat pkg.py)
    assert_contains "$out" "Smoke check passed. Confidence now 0.8." \
        "review entry has period between text and Confidence sentence"
    cd / && rm -rf "$d"
}

echo "test_confidence_includes_rationale_when_provided"
{
    d=$(mk_workspace) && cd "$d"
    echo "x = 1" > pkg.py
    printf "claude-opus-4-7\nctx\n0.6\nedges untested\nNone\n" \
        | "$SIG" add pkg.py > /dev/null 2>&1
    out=$(cat pkg.py)
    assert_contains "$out" "Confidence: 0.6 - edges untested" \
        "confidence line includes the rationale"
    cd / && rm -rf "$d"
}

echo "test_gallery_ignores_signatures_inside_fenced_code_blocks"
{
    d=$(mk_workspace) && cd "$d"
    cat > README.md <<'EOF'
# Readme

```
Signed: Example + example-model, 2020-01-01
Confidence: 0.1 - this is only an example
```

Real prose here. Write `Confidence: 0.2` when you mean it.

<!--
Signed: Kev + claude-fable-5-1, 2026-09-05
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Confidence: 0.8 - the real one
-->
EOF
    out=$("$SIG" gallery 2>&1)
    assert_contains "$out" "Kev + claude-fable-5-1, 2026-09-05" "gallery reads the file's own signature, not the fenced example"
    assert_not_contains "$out" "example-model" "gallery skips Signed: lines inside code fences"
    assert_contains "$out" "0.8 - the real one" "fields come from the region holding the signature"
    cd / && rm -rf "$d"
}

echo "test_gallery_counts_inline_review_lines"
{
    d=$(mk_workspace) && cd "$d"
    cat > inline.py <<'EOF'
# Signed: Kev + claude-opus-4-7, 2026-04-01
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
# Confidence: 0.7 - tested
#
# Review: Kev + claude-fable-5-1, 2026-09-05 - tightened the parser. Confidence now 0.8.
x = 1
EOF
    cat > bullet.yaml <<'EOF'
# Signed: Kev + claude-opus-4-7, 2026-04-18
# Confidence: 0.6 - first draft
# Reviews:
# - claude-opus-4-8, 2026-06-24: Added a prose field.
# - claude-fable-5-1, 2026-09-05: Reviewed again.
a: 1
EOF
    out=$("$SIG" gallery 2>&1)
    assert_contains "$out" "Reviews: 1" "gallery counts an inline Review: line as a review"
    assert_contains "$out" "Reviews: 2" "gallery counts the YAML bullet review dialect"
    cd / && rm -rf "$d"
}

echo "test_gallery_no_drift_for_single_commit_file"
{
    d=$(mk_workspace) && cd "$d"
    git init -q . && git config user.email t@t && git config user.name t && git config core.hooksPath /dev/null
    cat > imported.py <<'EOF'
# Signed: Kev + claude-opus-4-6, 2026-02-16
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
# Confidence: 0.8 - signed before the repo existed
x = 1
EOF
    git add . >/dev/null && GIT_AUTHOR_DATE=2026-04-19T12:00:00 GIT_COMMITTER_DATE=2026-04-19T12:00:00 git commit -qm import
    out=$("$SIG" gallery 2>&1)
    assert_not_contains "$out" "Drift:" "a file whose only commit is its import has no drift"
    assert_contains "$out" "0 drifted" "footer counts no drift for signed-then-imported files"
    cd / && rm -rf "$d"
}

echo ""
if [ $FAIL -eq 0 ]; then
    echo "All $PASS assertions passed."
    exit 0
else
    echo "FAILED: $FAIL of $((PASS + FAIL)) assertions."
    for name in "${FAILED_NAMES[@]}"; do echo "  - $name"; done
    exit 1
fi
