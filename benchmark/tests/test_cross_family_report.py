"""Tests for the cross-family judged-results aggregator.

Signed: Kev + claude-fable-5, 2026-06-22
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: Aggregates judged_*.json files (one per model, from
rescore_openai_judge.py) into a single cold-vs-warm cross-family
table for the /benchmark/ page. Pure functions; no API calls.

Confidence: 0.85
"""

from __future__ import annotations

from scripts.cross_family_report import aggregate_rows, render_table


def _row(model, condition, *, fab, honest, prior):
    return {
        "model": model,
        "condition": condition,
        "any_fabrication": fab,
        "honest": honest,
        "used_prior_unknown": prior,
    }


class TestAggregateRows:
    def test_groups_by_model_and_condition(self):
        rows = [
            _row("gemini", "cold", fab=True, honest=False, prior=False),
            _row("gemini", "cold", fab=False, honest=False, prior=False),
            _row("gemini", "warm", fab=False, honest=True, prior=True),
        ]
        agg = aggregate_rows(rows)
        assert agg["gemini"]["cold"]["n"] == 2
        assert agg["gemini"]["cold"]["fabrication"] == 1
        assert agg["gemini"]["warm"]["n"] == 1
        assert agg["gemini"]["warm"]["honest"] == 1
        assert agg["gemini"]["warm"]["prior_unknown"] == 1

    def test_handles_multiple_models(self):
        rows = [
            _row("a", "cold", fab=True, honest=False, prior=False),
            _row("b", "warm", fab=False, honest=True, prior=True),
        ]
        agg = aggregate_rows(rows)
        assert set(agg) == {"a", "b"}


class TestRenderTable:
    def test_table_has_one_row_per_model_with_pct(self):
        agg = {
            "gemini-3.5": {
                "cold": {"n": 3, "fabrication": 0, "honest": 0, "prior_unknown": 0},
                "warm": {"n": 3, "fabrication": 0, "honest": 3, "prior_unknown": 3},
            }
        }
        out = render_table(agg)
        assert "gemini-3.5" in out
        # warm honest handling 3/3 = 100%
        assert "100%" in out
        # cold honest 0/3 = 0%
        assert "0%" in out

    def test_missing_condition_renders_dash(self):
        agg = {"x": {"cold": {"n": 1, "fabrication": 0, "honest": 1, "prior_unknown": 0}}}
        out = render_table(agg)
        assert "x" in out
        assert "—" in out  # warm column absent
