"""MurphySig Benchmark — Tacit Knowledge (TK) sub-benchmark.

Signed: Kev + claude-opus-4-7, 2026-04-18
Format: MurphySig v0.3.3 (https://murphysig.dev/spec)

Context: Tests whether a MurphySig signature reduces an AI's uncertainty
when briefing on unfamiliar code. Compares AI briefings against a rich
gold-standard `ground_truth` held separately. Hypothesis: signed code
produces briefings with higher coverage, higher accuracy, less hedging,
and fewer questions-back than unsigned code.

Confidence: 0.8 - novel task shape; scoring rubric is well-defined but
untested at scale.
"""
