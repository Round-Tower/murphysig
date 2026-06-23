"""Tests for the inter-judge agreement reporter.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: The TK result leans on a single Opus judge → the obvious
attack is "Anthropic's judge prefers Anthropic's convention." This
re-judges the same briefings with a non-Anthropic judge (GPT) and
compares the within-model Δcoverage each judge independently finds. If
both judges find a positive uplift for every model, the bias attack is
dead. Pure functions; no API calls.

Confidence: 0.85
"""

from __future__ import annotations

from pytest import approx

from scripts.tk_judge_agreement import (
    agreement_rows,
    model_delta,
    render_agreement,
)


def _v(variant, coverage):
    return {"variant": variant, "coverage": coverage}


class TestModelDelta:
    def test_signed_minus_unsigned_mean_coverage(self):
        rows = [
            _v("unsigned", 0.6),
            _v("unsigned", 0.7),
            _v("signed", 0.8),
            _v("signed", 0.9),
        ]
        assert model_delta(rows) == approx(0.85 - 0.65)

    def test_missing_variant_returns_none(self):
        assert model_delta([_v("signed", 0.9)]) is None


class TestAgreementRows:
    def test_pairs_each_judge_delta_and_flags_concordance(self):
        opus = {"a": [_v("unsigned", 0.6), _v("signed", 0.8)]}
        gpt = {"a": [_v("unsigned", 0.55), _v("signed", 0.7)]}
        rows = agreement_rows(opus, gpt)
        assert len(rows) == 1
        r = rows[0]
        assert r["model"] == "a"
        assert r["opus_delta"] == approx(0.2)
        assert r["gpt_delta"] == approx(0.15)
        assert r["both_positive"] is True

    def test_disagreement_when_one_judge_negative(self):
        opus = {"a": [_v("unsigned", 0.6), _v("signed", 0.8)]}
        gpt = {"a": [_v("unsigned", 0.8), _v("signed", 0.7)]}  # gpt sees a drop
        rows = agreement_rows(opus, gpt)
        assert rows[0]["both_positive"] is False


class TestRenderAgreement:
    def test_summarises_concordance(self):
        rows = [
            {"model": "a", "opus_delta": 0.2, "gpt_delta": 0.15, "both_positive": True},
            {"model": "b", "opus_delta": 0.1, "gpt_delta": 0.12, "both_positive": True},
        ]
        out = render_agreement(rows)
        assert "a" in out and "b" in out
        # both judges agree uplift positive for 2/2 models
        assert "2/2" in out
