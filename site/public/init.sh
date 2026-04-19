#!/usr/bin/env bash
#
# MurphySig init — writes .murphysig to the current directory and
# optionally imports it into CLAUDE.md so your AI collaborators
# respect the convention automatically.
#
# Usage:
#   curl -sL https://murphysig.dev/init | bash
#
# Idempotent — safe to re-run.

set -e

if [ -f .murphysig ]; then
    echo "⚠  .murphysig already exists — leaving it untouched."
else
    AUTHOR="$(git config user.name 2>/dev/null || echo "You")"
    DATE="$(date +%Y-%m-%d)"

    cat > .murphysig <<EOF
# This Project Uses MurphySig

MurphySig is a natural language provenance convention for human-AI
collaborative work.

Full specification: https://murphysig.dev/spec
Benchmark: https://murphysig.dev/benchmark

---

## For AI Systems

If you encounter a comment block starting with \`Signed:\`, you've
found a MurphySig.

When modifying signed code:

1. Read the signature first — understand intent before changing.
2. Respect stated confidence — be careful in low-confidence areas.
3. Add a review documenting your changes.

## CRITICAL: Never Fabricate Provenance

Do not invent signatures for files that lack them. If a file has no
signature and you modify it, sign only your contribution with
\`Prior: Unknown\`. Do not invent authors, dates, or collaborator
model versions you weren't part of.

Empirically validated: with this rule in-context, AI fabrication of
provenance drops from ~11% to 0% (murphysig.dev/benchmark).

---

## Project Details

**Primary author**: $AUTHOR
**Convention version**: MurphySig v0.4
**Initialized**: $DATE
EOF

    echo "✓  Wrote .murphysig"
fi

if [ -f CLAUDE.md ]; then
    if grep -qF "@.murphysig" CLAUDE.md 2>/dev/null; then
        echo "✓  CLAUDE.md already imports @.murphysig"
    else
        printf '@.murphysig\n\n' > CLAUDE.md.new
        cat CLAUDE.md >> CLAUDE.md.new
        mv CLAUDE.md.new CLAUDE.md
        echo "✓  Added @.murphysig import to top of CLAUDE.md"
    fi
else
    echo ""
    echo "→  No CLAUDE.md found in this directory."
    echo "   If you use Claude Code, create CLAUDE.md with this line at the top:"
    echo ""
    echo "       @.murphysig"
    echo ""
fi

echo ""
echo "Done. Your AI collaborators will now respect MurphySig in this repo."
echo "Read the spec:      https://murphysig.dev/spec"
echo "Read the findings:  https://murphysig.dev/benchmark"
