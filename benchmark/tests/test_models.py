"""Tests for domain models — written first per TDD."""

import pytest
from dataclasses import FrozenInstanceError

from src.models import (
    SignatureVariant,
    TestCase,
    Variant,
    Response,
    Score,
    ScoredResponse,
    RunConfig,
)


class TestSignatureVariant:
    def test_has_three_variants(self):
        assert len(SignatureVariant) == 3

    def test_variant_values(self):
        assert SignatureVariant.NONE.value == "none"
        assert SignatureVariant.HIGH.value == "high"
        assert SignatureVariant.LOW.value == "low"


class TestTestCase:
    def test_construction(self):
        case = TestCase(
            id="subtle_bug",
            name="Off-by-one pagination",
            code="def paginate(): pass",
            expected_issues=["off-by-one error"],
            has_bug=True,
            high_signature_context="battle-tested, production-proven",
            low_signature_context="sketchy, first attempt, untested",
        )
        assert case.id == "subtle_bug"
        assert case.name == "Off-by-one pagination"
        assert case.has_bug is True
        assert len(case.expected_issues) == 1

    def test_is_frozen(self):
        case = TestCase(
            id="test",
            name="Test",
            code="pass",
            expected_issues=[],
            has_bug=False,
            high_signature_context="solid",
            low_signature_context="shaky",
        )
        with pytest.raises(FrozenInstanceError):
            case.id = "changed"


class TestVariant:
    def test_construction(self):
        variant = Variant(
            case_id="subtle_bug",
            signature_type=SignatureVariant.HIGH,
            full_code="# signed code here",
        )
        assert variant.case_id == "subtle_bug"
        assert variant.signature_type == SignatureVariant.HIGH

    def test_is_frozen(self):
        variant = Variant(
            case_id="test",
            signature_type=SignatureVariant.NONE,
            full_code="pass",
        )
        with pytest.raises(FrozenInstanceError):
            variant.case_id = "changed"


class TestResponse:
    def test_construction(self):
        response = Response(
            case_id="subtle_bug",
            signature_type=SignatureVariant.LOW,
            model="claude-haiku-4-5-20251001",
            repetition=0,
            content="I found a bug...",
            input_tokens=100,
            output_tokens=200,
        )
        assert response.model == "claude-haiku-4-5-20251001"
        assert response.repetition == 0
        assert response.input_tokens == 100


class TestScore:
    def test_construction(self):
        score = Score(
            bug_detected=True,
            scrutiny_level=4,
            signature_awareness=True,
            confidence_alignment=3,
            suggestion_count=5,
        )
        assert score.bug_detected is True
        assert score.scrutiny_level == 4
        assert score.suggestion_count == 5

    def test_scrutiny_level_bounds(self):
        with pytest.raises(ValueError, match="scrutiny_level"):
            Score(
                bug_detected=False,
                scrutiny_level=0,
                signature_awareness=False,
                confidence_alignment=3,
                suggestion_count=0,
            )

        with pytest.raises(ValueError, match="scrutiny_level"):
            Score(
                bug_detected=False,
                scrutiny_level=6,
                signature_awareness=False,
                confidence_alignment=3,
                suggestion_count=0,
            )

    def test_confidence_alignment_bounds(self):
        with pytest.raises(ValueError, match="confidence_alignment"):
            Score(
                bug_detected=False,
                scrutiny_level=3,
                signature_awareness=False,
                confidence_alignment=0,
                suggestion_count=0,
            )

    def test_suggestion_count_non_negative(self):
        with pytest.raises(ValueError, match="suggestion_count"):
            Score(
                bug_detected=False,
                scrutiny_level=3,
                signature_awareness=False,
                confidence_alignment=3,
                suggestion_count=-1,
            )


class TestScoredResponse:
    def test_construction(self):
        response = Response(
            case_id="subtle_bug",
            signature_type=SignatureVariant.NONE,
            model="claude-haiku-4-5-20251001",
            repetition=0,
            content="review text",
            input_tokens=50,
            output_tokens=100,
        )
        score = Score(
            bug_detected=True,
            scrutiny_level=4,
            signature_awareness=False,
            confidence_alignment=3,
            suggestion_count=3,
        )
        scored = ScoredResponse(response=response, score=score)
        assert scored.response.case_id == "subtle_bug"
        assert scored.score.bug_detected is True


class TestRunConfig:
    def test_defaults(self):
        config = RunConfig()
        assert config.models == [
            "claude-haiku-4-5-20251001",
            "claude-sonnet-4-5-20250929",
        ]
        assert config.repetitions == 3
        assert config.temperature == 0.0
        assert config.delay_seconds == 0.5

    def test_custom_config(self):
        config = RunConfig(
            models=["claude-haiku-4-5-20251001"],
            repetitions=1,
            temperature=0.5,
        )
        assert len(config.models) == 1
        assert config.repetitions == 1
        assert config.temperature == 0.5
