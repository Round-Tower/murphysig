"""Tests for TK (tacit knowledge) domain models."""

import pytest

from src.tk.models import (
    Briefing,
    BriefingScore,
    BriefingVariant,
    ScoredBriefing,
    TkCase,
    TkSignature,
)


class TestTkSignature:
    def test_construct_minimal(self):
        s = TkSignature(context="c", confidence=0.7, open="q")
        assert s.context == "c"
        assert s.confidence == 0.7
        assert s.heuristic is None

    def test_with_heuristic(self):
        s = TkSignature(context="c", confidence=0.7, open="q", heuristic="h")
        assert s.heuristic == "h"


class TestTkCase:
    def test_construct(self):
        sig = TkSignature(context="c", confidence=0.5, open="q")
        c = TkCase(id="t", name="T", code="x=1", ground_truth="gt", signature=sig)
        assert c.id == "t"
        assert c.signature.confidence == 0.5


class TestBriefingVariant:
    def test_values(self):
        assert BriefingVariant.UNSIGNED.value == "unsigned"
        assert BriefingVariant.SIGNED.value == "signed"


class TestBriefingScore:
    def _score(self, **kwargs):
        defaults = dict(
            coverage=0.5,
            accuracy=0.8,
            hedging_density=3,
            questions_back_count=1,
            referenced_signature=False,
        )
        defaults.update(kwargs)
        return BriefingScore(**defaults)

    def test_valid_score(self):
        s = self._score()
        assert s.coverage == 0.5

    @pytest.mark.parametrize("val", [-0.1, 1.1, 2.0])
    def test_coverage_out_of_range_raises(self, val):
        with pytest.raises(ValueError, match="coverage"):
            self._score(coverage=val)

    @pytest.mark.parametrize("val", [-0.1, 1.1])
    def test_accuracy_out_of_range_raises(self, val):
        with pytest.raises(ValueError, match="accuracy"):
            self._score(accuracy=val)

    @pytest.mark.parametrize("val", [0, 6, -1])
    def test_hedging_out_of_range_raises(self, val):
        with pytest.raises(ValueError, match="hedging_density"):
            self._score(hedging_density=val)

    def test_negative_questions_back_raises(self):
        with pytest.raises(ValueError, match="questions_back_count"):
            self._score(questions_back_count=-1)


class TestScoredBriefing:
    def test_pairs_briefing_and_score(self):
        b = Briefing(
            case_id="t",
            variant=BriefingVariant.SIGNED,
            model="m",
            repetition=0,
            content="...",
            input_tokens=10,
            output_tokens=20,
        )
        s = BriefingScore(
            coverage=0.9,
            accuracy=0.9,
            hedging_density=2,
            questions_back_count=0,
            referenced_signature=True,
        )
        sb = ScoredBriefing(briefing=b, score=s)
        assert sb.briefing.case_id == "t"
        assert sb.score.referenced_signature
