#!/usr/bin/env bash
# Signed: Kev + claude-opus-4-5-20251101, 2026-01-05
# Format: MurphySig v0.3.3 (https://murphysig.dev/spec)
#
# Context: One-command deploy script for MurphySig site to Netlify.
# Builds the Astro site and pushes to production.
#
# Confidence: 0.9 - standard Netlify CLI workflow
# Open: None
#
# Reviews:
#
# 2026-09-05 (Kev + claude-fable-5-1): Only the Format: line has changed since
# signing (v0.3.3, the Gruber Cut). Note this script is now the manual
# fallback: production deploys on push via Netlify. Confidence now 0.9, held.
#

set -e

cd "$(dirname "$0")"

echo "Building MurphySig site..."
npm run build

echo "Deploying to Netlify..."
netlify deploy --prod --dir=dist

echo "Done!"
