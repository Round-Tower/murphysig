"""Tests for the Honesty inter-judge agreement reporter.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: The Honesty cross-family result (warm honest-handling 100% on
4 families; Llama/Qwen resist) was scored by a single Opus judge. This
compares it against a non-Anthropic judge (GPT) re-scoring the same
responses: per-model warm honest-handling rate under each judge, plus
per-response concordance on the `honest` verdict. If GPT reproduces the
same cross-family split, the single-judge bias attack is refuted for
Honesty too. Pure functions; no API calls.

Confidence: 0.85
"""

from __future__ import annotations

from pytest import approx

from scripts.honesty_judge_agreement import (
    honest_rate,
    model_agreement_rows,
    render_agreement,
    response_concordance,
)


def _r(case_id, condition, rep, honest):
    return {"case_id": case_id, "condition": condition, "rep": rep, "honest": honest}


class TestHonestRate:
    def test_mean_honest_for_condition(self):
        rows = [
            _r("a", "warm", 0, True),
            _r("a", "warm", 1, True),
            _r("a", "warm", 2, False),
            _r("a", "cold", 0, False),
        ]
        assert honest_rate(rows, "warm") == approx(2 / 3)
        assert honest_rate(rows, "cold") == approx(0.0)

    def test_absent_condition_is_none(self):
        assert honest_rate([_r("a", "warm", 0, True)], "cold") is None


class TestModelAgreementRows:
    def test_pairs_warm_rate_per_model(self):
        opus = {"m": [_r("a", "warm", 0, True), _r("a", "warm", 1, True)]}
        gpt = {"m": [_r("a", "warm", 0, True), _r("a", "warm", 1, False)]}
        rows = model_agreement_rows(opus, gpt)
        assert rows[0]["model"] == "m"
        assert rows[0]["opus_warm_honest"] == approx(1.0)
        assert rows[0]["gpt_warm_honest"] == approx(0.5)


class TestResponseConcordance:
    def test_aligns_by_case_condition_rep(self):
        opus = [_r("a", "warm", 0, True), _r("a", "warm", 1, False)]
        gpt = [_r("a", "warm", 0, True), _r("a", "warm", 1, True)]
        # rep 0 agrees (both True), rep 1 disagrees (False vs True)
        conc = response_concordance(opus, gpt)
        assert conc["n"] == 2
        assert conc["agree"] == 1
        assert conc["rate"] == approx(0.5)

    def test_only_counts_overlapping_keys(self):
        opus = [_r("a", "warm", 0, True)]
        gpt = [_r("a", "warm", 0, True), _r("b", "cold", 0, False)]
        conc = response_concordance(opus, gpt)
        assert conc["n"] == 1


class TestRender:
    def test_shows_models_and_per_condition_concordance(self):
        rows = [
            {"model": "x", "opus_warm_honest": 1.0, "gpt_warm_honest": 1.0,
             "opus_cold_honest": 0.1, "gpt_cold_honest": 0.2},
        ]
        conc = {
            "warm": {"n": 30, "agree": 27, "rate": 0.90},
            "cold": {"n": 30, "agree": 4, "rate": 0.13},
            "overall": {"n": 60, "agree": 31, "rate": 0.52},
        }
        out = render_agreement(rows, conc)
        assert "x" in out
        assert "90%" in out  # warm concordance surfaced
        assert "13%" in out  # cold divergence surfaced
