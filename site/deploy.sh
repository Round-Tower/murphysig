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

set -e

cd "$(dirname "$0")"

echo "Building MurphySig site..."
npm run build

echo "Deploying to Netlify..."
netlify deploy --prod --dir=dist

echo "Done!"
