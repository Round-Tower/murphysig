"""MurphySig Benchmark — Honesty / Provenance sub-benchmark.

Signed: Kev + claude-opus-4-7, 2026-04-18
Format: MurphySig v0.3.3 (https://murphysig.dev/spec)

Context: Tests whether AIs fabricate provenance when asked to sign
an unsigned file. Three cases with escalating temptation, two prompt
conditions (cold vs warm). The warm condition includes the spec's
"Never Fabricate Provenance" rule inline; the cold condition does not.

Confidence: 0.8 - sub-benchmark design is clean (binary scoring,
small N × 2 condition = clear signal if effect exists).
"""
