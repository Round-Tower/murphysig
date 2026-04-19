"""Tests for report generation — written first per TDD."""

import pytest

from src.models import Response, Score, ScoredResponse, SignatureVariant
from src.reporter import (
    compute_stats,
    generate_report,
    format_hypothesis_analysis,
    GroupStats,
)


def _make_scored(
    case_id: str,
    sig: SignatureVariant,
    model: str,
    rep: int,
    bug_detected: bool = True,
    scrutiny: int = 3,
    sig_aware: bool = False,
    conf_align: int = 3,
    suggestions: int = 2,
) -> ScoredResponse:
    return ScoredResponse(
        response=Response(
            case_id=case_id,
            signature_type=sig,
            model=model,
            repetition=rep,
            content="review text",
            input_tokens=100,
            output_tokens=200,
        ),
        score=Score(
            bug_detected=bug_detected,
            scrutiny_level=scrutiny,
            signature_awareness=sig_aware,
            confidence_alignment=conf_align,
            suggestion_count=suggestions,
        ),
    )


class TestComputeStats:
    def test_single_result(self):
        results = [
            _make_scored("subtle_bug", SignatureVariant.NONE, "haiku", 0,
                         bug_detected=True, scrutiny=4, suggestions=3),
        ]
        stats = compute_stats(results)
        assert stats.bug_detection_rate == 1.0
        assert stats.mean_scrutiny == 4.0
        assert stats.mean_suggestions == 3.0
        assert stats.count == 1

    def test_multiple_results(self):
        results = [
            _make_scored("subtle_bug", SignatureVariant.NONE, "haiku", 0,
                         bug_detected=True, scrutiny=2, suggestions=1),
            _make_scored("subtle_bug", SignatureVariant.NONE, "haiku", 1,
                         bug_detected=False, scrutiny=4, suggestions=3),
        ]
        stats = compute_stats(results)
        assert stats.bug_detection_rate == 0.5
        assert stats.mean_scrutiny == 3.0
        assert stats.mean_suggestions == 2.0
        assert stats.count == 2

    def test_empty_results(self):
        stats = compute_stats([])
        assert stats.bug_detection_rate == 0.0
        assert stats.mean_scrutiny == 0.0
        assert stats.count == 0

    def test_signature_awareness_rate(self):
        results = [
            _make_scored("x", SignatureVariant.HIGH, "haiku", 0, sig_aware=True),
            _make_scored("x", SignatureVariant.HIGH, "haiku", 1, sig_aware=False),
            _make_scored("x", SignatureVariant.HIGH, "haiku", 2, sig_aware=True),
        ]
        stats = compute_stats(results)
        assert abs(stats.signature_awareness_rate - 2 / 3) < 0.01


class TestFormatHypothesisAnalysis:
    def test_contains_all_hypotheses(self):
        # Build minimal data: 3 variants for 1 case
        results = [
            _make_scored("subtle_bug", SignatureVariant.NONE, "haiku", 0, scrutiny=3),
            _make_scored("subtle_bug", SignatureVariant.LOW, "haiku", 0, scrutiny=5),
            _make_scored("subtle_bug", SignatureVariant.HIGH, "haiku", 0, scrutiny=2),
        ]
        analysis = format_hypothesis_analysis(results)
        assert "H1" in analysis
        assert "H2" in analysis
        assert "H3" in analysis
        assert "H4" in analysis

    def test_returns_markdown(self):
        results = [
            _make_scored("subtle_bug", SignatureVariant.NONE, "haiku", 0),
        ]
        analysis = format_hypothesis_analysis(results)
        assert analysis.startswith("#")


class TestGenerateReport:
    def test_report_contains_title(self):
        results = [
            _make_scored("subtle_bug", SignatureVariant.NONE, "haiku", 0),
        ]
        report = generate_report(results)
        assert "MurphySig Benchmark" in report

    def test_report_contains_summary_table(self):
        results = [
            _make_scored("subtle_bug", SignatureVariant.NONE, "haiku", 0),
            _make_scored("subtle_bug", SignatureVariant.HIGH, "haiku", 0),
            _make_scored("subtle_bug", SignatureVariant.LOW, "haiku", 0),
        ]
        report = generate_report(results)
        assert "| Variant" in report or "| Model" in report
        assert "none" in report.lower()
        assert "high" in report.lower()
        assert "low" in report.lower()

    def test_report_contains_hypothesis_section(self):
        results = [
            _make_scored("subtle_bug", SignatureVariant.NONE, "haiku", 0),
        ]
        report = generate_report(results)
        assert "Hypothesis" in report or "hypothesis" in report

    def test_report_is_valid_markdown(self):
        results = [
            _make_scored("subtle_bug", SignatureVariant.NONE, "haiku", 0),
        ]
        report = generate_report(results)
        # Should start with a heading
        assert report.strip().startswith("#")
        # Should have multiple sections
        assert report.count("#") >= 3
