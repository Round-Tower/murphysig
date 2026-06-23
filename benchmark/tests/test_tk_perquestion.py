"""Tests for the per-question TK re-judge (intent vs code-derivable axes).

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: The holistic coverage judge can't show WHERE a signature's
uplift comes from. The TK claim is "signatures transfer author intent
(why it exists, what the author was unsure about) — facts underivable
from code — not independent bug-finding". This re-judges the saved
briefings per briefing-question and groups them onto two axes:
intent (Q1 purpose + Q3 author-uncertainty) and code-derivable
(Q2 careful-when-modifying + Q4 edge-cases). If Δintent >> Δcode the
claim is proven. Pure functions; no API calls.

Confidence: 0.85
"""

from __future__ import annotations

from pytest import approx

from scripts.rescore_tk_perquestion import (
    QUESTION_AXIS,
    aggregate_perquestion,
    axis_summary,
    parse_perquestion,
)


class TestParsePerquestion:
    def test_extracts_four_coverages(self):
        raw = (
            'prose before {"q1_coverage": 0.8, "q2_coverage": 0.3, '
            '"q3_coverage": 0.9, "q4_coverage": 0.4} after'
        )
        out = parse_perquestion(raw)
        assert out == {"q1": 0.8, "q2": 0.3, "q3": 0.9, "q4": 0.4}

    def test_clamps_and_floats(self):
        raw = '{"q1_coverage": 1, "q2_coverage": 0, "q3_coverage": 0.5, "q4_coverage": 1.0}'
        out = parse_perquestion(raw)
        assert out["q1"] == 1.0
        assert isinstance(out["q1"], float)

    def test_missing_key_defaults_to_zero_not_crash(self):
        # A judge that drops a field must not kill a long pass.
        raw = '{"q1_coverage": 0.7, "q3_coverage": 0.9}'
        out = parse_perquestion(raw)
        assert out["q1"] == 0.7
        assert out["q2"] == 0.0
        assert out["q4"] == 0.0


class TestAxisMap:
    def test_intent_and_code_axes(self):
        assert QUESTION_AXIS["q1"] == "intent"
        assert QUESTION_AXIS["q3"] == "intent"
        assert QUESTION_AXIS["q2"] == "code"
        assert QUESTION_AXIS["q4"] == "code"


def _row(model, variant, q1, q2, q3, q4):
    return {
        "model": model,
        "variant": variant,
        "q1": q1,
        "q2": q2,
        "q3": q3,
        "q4": q4,
    }


class TestAggregatePerquestion:
    def test_per_question_means_signed_vs_unsigned(self):
        rows = [
            _row("a", "unsigned", 0.4, 0.6, 0.2, 0.6),
            _row("a", "unsigned", 0.6, 0.6, 0.4, 0.6),
            _row("a", "signed", 0.8, 0.6, 0.9, 0.6),
            _row("a", "signed", 0.8, 0.6, 0.9, 0.6),
        ]
        agg = aggregate_perquestion(rows)
        assert agg["q1"]["unsigned"] == approx(0.5)
        assert agg["q1"]["signed"] == approx(0.8)
        assert agg["q1"]["delta"] == approx(0.3)
        # Q2 is flat (code-derivable, no signature help)
        assert agg["q2"]["delta"] == approx(0.0)


class TestAxisSummary:
    def test_intent_delta_pools_q1_q3_code_pools_q2_q4(self):
        agg = {
            "q1": {"unsigned": 0.5, "signed": 0.8, "delta": 0.3},
            "q2": {"unsigned": 0.6, "signed": 0.6, "delta": 0.0},
            "q3": {"unsigned": 0.3, "signed": 0.9, "delta": 0.6},
            "q4": {"unsigned": 0.6, "signed": 0.65, "delta": 0.05},
        }
        axes = axis_summary(agg)
        # intent delta = mean(0.3, 0.6) = 0.45
        assert axes["intent"]["delta"] == approx(0.45)
        # code delta = mean(0.0, 0.05) = 0.025
        assert axes["code"]["delta"] == approx(0.025)
        # the claim: intent uplift dwarfs code uplift
        assert axes["intent"]["delta"] > axes["code"]["delta"]
