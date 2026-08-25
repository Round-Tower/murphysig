"""Tests for author-theme inter-judge agreement.

Signed: Kev + claude-fable-5, 2026-08-22
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: tests/test_tk_judge_agreement.py (same shape, author theme)

Context: The pre-registration quotes the headline only if both judges
agree on its SIGN per model. This reporter computes each judge's
per-model paired deltas and the concordance flag — the artifact that
kills the "your judge prefers your convention" attack, or honestly
fails to.

Confidence: 0.85
"""

from __future__ import annotations

from pytest import approx

from scripts.author_judge_agreement import agreement_rows, render_agreement


def _judged(model, arm, handled, n=2):
    return [
        {
            "model": model,
            "arm": arm,
            "verdict": {
                "hazards": {"H1": "handled" if handled else "missed"},
                "core_correct": True,
            },
        }
        for _ in range(n)
    ]


class TestAgreementRows:
    def test_concordant_when_both_judges_find_same_sign(self):
        a = _judged("m", "sign_revise", True) + _judged("m", "reflect_harder", False)
        b = _judged("m", "sign_revise", True) + _judged("m", "reflect_harder", False)
        rows = agreement_rows({"m": a}, {"m": b})
        assert len(rows) == 1
        assert rows[0]["delta_a"] == approx(1.0)
        assert rows[0]["delta_b"] == approx(1.0)
        assert rows[0]["concordant"] is True

    def test_discordant_when_signs_differ(self):
        a = _judged("m", "sign_revise", True) + _judged("m", "reflect_harder", False)
        b = _judged("m", "sign_revise", False) + _judged("m", "reflect_harder", True)
        rows = agreement_rows({"m": a}, {"m": b})
        assert rows[0]["concordant"] is False

    def test_model_missing_an_arm_under_either_judge_is_skipped(self):
        a = _judged("m", "sign_revise", True)  # no reflect_harder
        b = _judged("m", "sign_revise", True) + _judged("m", "reflect_harder", False)
        assert agreement_rows({"m": a}, {"m": b}) == []


class TestRender:
    def test_render_contains_models_and_concordance_summary(self):
        a = _judged("m", "sign_revise", True) + _judged("m", "reflect_harder", False)
        rows = agreement_rows({"m": a}, {"m": a})
        text = render_agreement(rows, judge_a="gpt-5.4", judge_b="opus-4.6")
        assert "m" in text and "1/1 concordant" in text
