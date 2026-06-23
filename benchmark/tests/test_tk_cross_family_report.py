"""Tests for the TK cross-family delta aggregator.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: Aggregates judged_tk_*.json (one per model) into the TK
headline — the WITHIN-MODEL delta (signed minus unsigned) on coverage
and hedging, plus the signed-variant referenced-signature rate. The
delta is the claim ("signatures help this model brief better"), so it
must survive raw capability gaps between families. Pure functions; no
API calls.

Confidence: 0.85
"""

from __future__ import annotations

from pytest import approx

from scripts.tk_cross_family_report import aggregate_tk, delta_table


def _row(model, variant, *, coverage, accuracy=0.8, hedging=2, refd=False):
    return {
        "model": model,
        "variant": variant,
        "coverage": coverage,
        "accuracy": accuracy,
        "hedging_density": hedging,
        "questions_back_count": 0,
        "referenced_signature": refd,
    }


class TestAggregateTk:
    def test_means_per_model_and_variant(self):
        rows = [
            _row("gemini", "unsigned", coverage=0.6, hedging=3),
            _row("gemini", "unsigned", coverage=0.7, hedging=3),
            _row("gemini", "signed", coverage=0.8, hedging=1, refd=True),
            _row("gemini", "signed", coverage=0.9, hedging=1, refd=True),
        ]
        agg = aggregate_tk(rows)
        g = agg["gemini"]
        assert g["unsigned"]["n"] == 2
        assert g["unsigned"]["coverage"] == approx(0.65)
        assert g["unsigned"]["hedging"] == 3.0
        assert g["signed"]["coverage"] == approx(0.85)
        assert g["signed"]["referenced_signature"] == 2  # count

    def test_multiple_models(self):
        rows = [
            _row("a", "signed", coverage=0.9),
            _row("b", "unsigned", coverage=0.4),
        ]
        agg = aggregate_tk(rows)
        assert set(agg) == {"a", "b"}


class TestDeltaTable:
    def test_delta_is_signed_minus_unsigned(self):
        agg = {
            "gemini": {
                "unsigned": {"n": 3, "coverage": 0.65, "accuracy": 0.8,
                             "hedging": 3.0, "referenced_signature": 0},
                "signed": {"n": 3, "coverage": 0.85, "accuracy": 0.82,
                           "hedging": 1.5, "referenced_signature": 3},
            }
        }
        out = delta_table(agg)
        assert "gemini" in out
        # Δcoverage = 0.85 - 0.65 = +0.20
        assert "+0.20" in out
        # Δhedging = 1.5 - 3.0 = -1.50 (less hedging when signed — good)
        assert "-1.50" in out
        # referenced-signature rate on the signed variant = 3/3 = 100%
        assert "100%" in out

    def test_missing_variant_renders_dash_not_crash(self):
        agg = {
            "x": {
                "signed": {"n": 1, "coverage": 0.9, "accuracy": 0.9,
                           "hedging": 1.0, "referenced_signature": 1},
            }
        }
        out = delta_table(agg)
        assert "x" in out
        assert "—" in out  # no unsigned baseline → delta undefined
