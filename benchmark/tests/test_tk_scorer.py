"""Tests for the TK (tacit knowledge) scorer."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.tk.models import Briefing, BriefingVariant, ScoredBriefing
from src.tk.scorer import parse_tk_judgment, score_tk_briefing


class TestParseTkJudgment:
    def test_parses_valid_json(self):
        raw = json.dumps({
            "coverage": 0.7,
            "accuracy": 0.9,
            "hedging_density": 2,
            "questions_back_count": 1,
            "referenced_signature": True,
        })
        s = parse_tk_judgment(raw)
        assert s.coverage == 0.7
        assert s.accuracy == 0.9
        assert s.hedging_density == 2
        assert s.questions_back_count == 1
        assert s.referenced_signature

    def test_parses_json_with_surrounding_text(self):
        raw = (
            "Assessment follows:\n"
            + json.dumps({
                "coverage": 0.4,
                "accuracy": 0.6,
                "hedging_density": 4,
                "questions_back_count": 3,
                "referenced_signature": False,
            })
            + "\nEnd of assessment."
        )
        s = parse_tk_judgment(raw)
        assert s.coverage == 0.4
        assert not s.referenced_signature

    def test_raises_on_out_of_range_coverage(self):
        raw = json.dumps({
            "coverage": 1.5,
            "accuracy": 0.5,
            "hedging_density": 3,
            "questions_back_count": 0,
            "referenced_signature": False,
        })
        with pytest.raises(ValueError, match="coverage"):
            parse_tk_judgment(raw)

    def test_raises_on_out_of_range_hedging(self):
        raw = json.dumps({
            "coverage": 0.5,
            "accuracy": 0.5,
            "hedging_density": 7,
            "questions_back_count": 0,
            "referenced_signature": False,
        })
        with pytest.raises(ValueError, match="hedging_density"):
            parse_tk_judgment(raw)

    def test_raises_on_no_json(self):
        with pytest.raises(ValueError, match="Could not parse"):
            parse_tk_judgment("plain text, no json at all")


@pytest.fixture
def sample_briefing() -> Briefing:
    return Briefing(
        case_id="pagination",
        variant=BriefingVariant.SIGNED,
        model="claude-haiku-4-5-20251001",
        repetition=0,
        content="This is a pagination helper. The off-by-one looks like a bug.",
        input_tokens=100,
        output_tokens=50,
    )


class TestScoreTkBriefing:
    @pytest.mark.asyncio
    async def test_returns_scored_briefing(self, sample_briefing: Briefing):
        mock_out = json.dumps({
            "coverage": 0.8,
            "accuracy": 0.9,
            "hedging_density": 2,
            "questions_back_count": 0,
            "referenced_signature": True,
        })
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=mock_out)]

        client = AsyncMock()
        client.messages.create = AsyncMock(return_value=mock_message)

        result = await score_tk_briefing(
            client=client,
            briefing=sample_briefing,
            original_code="def paginate(): pass",
            ground_truth="Paginates a list; off-by-one at page * page_size.",
            judge_prompt_template=(
                "Score this. {code} {ground_truth} "
                "{signature_variant} {briefing}"
            ),
            judge_model="claude-opus-4-6",
        )

        assert isinstance(result, ScoredBriefing)
        assert result.briefing is sample_briefing
        assert result.score.coverage == 0.8

    @pytest.mark.asyncio
    async def test_template_with_literal_json_rubric(
        self, sample_briefing: Briefing
    ):
        """Regression for the .format() bug."""
        template = """Score. Output JSON:
{
  "coverage": 0.0-1.0,
  "accuracy": 0.0-1.0,
  "hedging_density": 1-5,
  "questions_back_count": 0
}
CODE: {code}
GROUND TRUTH: {ground_truth}
VARIANT: {signature_variant}
BRIEFING: {briefing}
"""
        mock_out = json.dumps({
            "coverage": 0.5,
            "accuracy": 0.5,
            "hedging_density": 3,
            "questions_back_count": 1,
            "referenced_signature": False,
        })
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=mock_out)]

        client = AsyncMock()
        client.messages.create = AsyncMock(return_value=mock_message)

        # must not raise
        await score_tk_briefing(
            client=client,
            briefing=sample_briefing,
            original_code="x",
            ground_truth="gt",
            judge_prompt_template=template,
            judge_model="claude-opus-4-6",
        )

        content = client.messages.create.call_args.kwargs["messages"][0]["content"]
        assert '"coverage": 0.0-1.0' in content
        assert '"hedging_density": 1-5' in content
