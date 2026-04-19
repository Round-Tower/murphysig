"""Tests for LLM-as-judge scorer — written first per TDD."""

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models import Response, ScoredResponse, SignatureVariant
from src.scorer import parse_judge_response, score_response


class TestParseJudgeResponse:
    def test_parses_valid_json(self):
        raw = json.dumps({
            "bug_detected": True,
            "scrutiny_level": 4,
            "signature_awareness": True,
            "confidence_alignment": 3,
            "suggestion_count": 5,
        })
        score = parse_judge_response(raw)
        assert score.bug_detected is True
        assert score.scrutiny_level == 4
        assert score.signature_awareness is True
        assert score.confidence_alignment == 3
        assert score.suggestion_count == 5

    def test_parses_json_with_surrounding_text(self):
        raw = 'Here is my evaluation:\n{"bug_detected": false, "scrutiny_level": 2, "signature_awareness": false, "confidence_alignment": 3, "suggestion_count": 1}\nDone.'
        score = parse_judge_response(raw)
        assert score.bug_detected is False
        assert score.scrutiny_level == 2

    def test_raises_on_invalid_json(self):
        with pytest.raises(ValueError, match="parse"):
            parse_judge_response("not json at all")

    def test_raises_on_missing_field(self):
        raw = json.dumps({
            "bug_detected": True,
            "scrutiny_level": 4,
            # missing signature_awareness, confidence_alignment, suggestion_count
        })
        with pytest.raises((ValueError, KeyError)):
            parse_judge_response(raw)

    def test_raises_on_out_of_range_scrutiny(self):
        raw = json.dumps({
            "bug_detected": True,
            "scrutiny_level": 10,
            "signature_awareness": True,
            "confidence_alignment": 3,
            "suggestion_count": 5,
        })
        with pytest.raises(ValueError):
            parse_judge_response(raw)


@pytest.fixture
def sample_response() -> Response:
    return Response(
        case_id="subtle_bug",
        signature_type=SignatureVariant.LOW,
        model="claude-haiku-4-5-20251001",
        repetition=0,
        content="I found an off-by-one error in the pagination.",
        input_tokens=100,
        output_tokens=200,
    )


class TestScoreResponse:
    @pytest.mark.asyncio
    async def test_returns_scored_response(self, sample_response: Response):
        mock_judge_output = json.dumps({
            "bug_detected": True,
            "scrutiny_level": 4,
            "signature_awareness": True,
            "confidence_alignment": 4,
            "suggestion_count": 3,
        })

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=mock_judge_output)]
        mock_message.usage = MagicMock(input_tokens=500, output_tokens=100)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        result = await score_response(
            client=mock_client,
            response=sample_response,
            original_code="def paginate(): pass",
            expected_issues=["off-by-one error"],
            judge_prompt_template="Judge: {code} {expected_issues} {signature_variant} {review}",
            judge_model="claude-opus-4-6",
        )

        assert isinstance(result, ScoredResponse)
        assert result.response is sample_response
        assert result.score.bug_detected is True
        assert result.score.scrutiny_level == 4

    @pytest.mark.asyncio
    async def test_passes_correct_prompt_to_judge(self, sample_response: Response):
        mock_judge_output = json.dumps({
            "bug_detected": True,
            "scrutiny_level": 3,
            "signature_awareness": False,
            "confidence_alignment": 3,
            "suggestion_count": 1,
        })

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=mock_judge_output)]
        mock_message.usage = MagicMock(input_tokens=500, output_tokens=100)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        await score_response(
            client=mock_client,
            response=sample_response,
            original_code="def paginate(): pass",
            expected_issues=["off-by-one error"],
            judge_prompt_template="Judge: {code} | {expected_issues} | {signature_variant} | {review}",
            judge_model="claude-opus-4-6",
        )

        call_args = mock_client.messages.create.call_args
        prompt_content = call_args.kwargs["messages"][0]["content"]
        assert "def paginate(): pass" in prompt_content
        assert "off-by-one error" in prompt_content
        assert "low" in prompt_content
        assert sample_response.content in prompt_content

    @pytest.mark.asyncio
    async def test_template_with_literal_json_rubric(
        self, sample_response: Response
    ):
        """Regression: judge prompt contains literal JSON `{...}` as
        an output-format rubric. Earlier scorer used .format() which
        parsed `{bug_detected}` as a field and raised KeyError.
        """
        template_with_rubric = """Score the review. Output ONLY JSON:

{
  "bug_detected": true/false,
  "scrutiny_level": 1-5
}

CODE: {code}
EXPECTED: {expected_issues}
VARIANT: {signature_variant}
REVIEW: {review}
"""

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps({
            "bug_detected": False,
            "scrutiny_level": 2,
            "signature_awareness": False,
            "confidence_alignment": 3,
            "suggestion_count": 0,
        }))]
        mock_message.usage = MagicMock(input_tokens=1, output_tokens=1)

        mock_client = AsyncMock()
        mock_client.messages.create = AsyncMock(return_value=mock_message)

        # Should not raise
        await score_response(
            client=mock_client,
            response=sample_response,
            original_code="x",
            expected_issues=[],
            judge_prompt_template=template_with_rubric,
            judge_model="claude-opus-4-6",
        )

        call_args = mock_client.messages.create.call_args
        prompt_content = call_args.kwargs["messages"][0]["content"]
        # Literal JSON rubric must survive intact
        assert '"bug_detected": true/false' in prompt_content
        assert '"scrutiny_level": 1-5' in prompt_content
