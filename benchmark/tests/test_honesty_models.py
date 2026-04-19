"""Tests for honesty domain models."""

import pytest

from src.honesty.models import (
    HonestyCase,
    HonestyResponse,
    HonestyScore,
    PromptCondition,
    ScoredHonestyResponse,
    Temptation,
)


class TestHonestyCase:
    def test_construct_minimal(self):
        c = HonestyCase(
            id="t",
            name="T",
            code="def x(): pass",
            temptation=Temptation.LOW,
        )
        assert c.id == "t"
        assert c.temptation == Temptation.LOW

    def test_frozen(self):
        c = HonestyCase(id="t", name="T", code="x", temptation=Temptation.LOW)
        with pytest.raises(Exception):
            c.id = "other"  # type: ignore[misc]


class TestHonestyScore:
    def _score(self, **kwargs):
        defaults = dict(
            fabricated_author=False,
            fabricated_date=False,
            used_prior_unknown=False,
            asked_for_info=False,
            refused_to_sign=False,
            signed_own_contribution_only=False,
        )
        defaults.update(kwargs)
        return HonestyScore(**defaults)

    def test_any_fabrication_true_when_author_fabricated(self):
        assert self._score(fabricated_author=True).any_fabrication

    def test_any_fabrication_true_when_date_fabricated(self):
        assert self._score(fabricated_date=True).any_fabrication

    def test_any_fabrication_false_when_neither(self):
        assert not self._score().any_fabrication

    def test_honest_true_when_used_prior_unknown(self):
        assert self._score(used_prior_unknown=True).honest

    def test_honest_true_when_refused(self):
        assert self._score(refused_to_sign=True).honest

    def test_honest_false_when_fabricated(self):
        assert not self._score(
            fabricated_author=True, used_prior_unknown=True
        ).honest

    def test_honest_false_when_nothing_positive(self):
        # No fabrication, but also no honest-handling marker
        assert not self._score().honest


class TestPromptCondition:
    def test_values(self):
        assert PromptCondition.COLD.value == "cold"
        assert PromptCondition.WARM.value == "warm"


class TestTemptation:
    def test_values(self):
        assert {t.value for t in Temptation} == {"low", "medium", "high"}


class TestScoredHonestyResponse:
    def test_pairs_response_and_score(self):
        r = HonestyResponse(
            case_id="t",
            prompt_condition=PromptCondition.COLD,
            model="m",
            repetition=0,
            content="...",
            input_tokens=10,
            output_tokens=20,
        )
        s = HonestyScore(
            fabricated_author=False,
            fabricated_date=False,
            used_prior_unknown=True,
            asked_for_info=False,
            refused_to_sign=False,
            signed_own_contribution_only=True,
        )
        sr = ScoredHonestyResponse(response=r, score=s)
        assert sr.response.case_id == "t"
        assert sr.score.honest
