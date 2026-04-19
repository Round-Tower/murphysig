"""LLM-as-judge scoring for benchmark responses.

Signed: Kev + claude-opus-4-6, 2026-02-16
Format: MurphySig v0.3.3 (https://murphysig.dev/spec)

Confidence: 0.85 - JSON parsing is tricky with LLMs, robust extraction needed.

Reviews:

2026-04-18 (Kev + claude-opus-4-7): Fixed `.format()` collision with
literal JSON rubric in judge_prompt.txt. The template contains
`{\n  "bug_detected": ...}` as output-format instructions; `.format()`
parsed those as field placeholders and raised KeyError on the first
call. Switched to explicit `str.replace()` for the four real fields.
This is why v1 fell back to heuristic scoring — the LLM-judge path
had never actually worked.
"""

from __future__ import annotations

import json

from anthropic import AsyncAnthropic

from src.models import Response, Score, ScoredResponse


def parse_judge_response(raw: str) -> Score:
    """Parse a judge's raw text response into a Score.

    Extracts the first JSON object from the response, even if surrounded
    by other text.

    Args:
        raw: The judge model's raw text output.

    Returns:
        A validated Score instance.

    Raises:
        ValueError: If no valid JSON found or fields are invalid.
    """
    # Find first '{' and last '}' — handles nested JSON safely
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Could not parse JSON from judge response: {raw[:200]}")

    try:
        data = json.loads(raw[start : end + 1])
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in judge response: {e}") from e

    return Score(
        bug_detected=data["bug_detected"],
        scrutiny_level=data["scrutiny_level"],
        signature_awareness=data["signature_awareness"],
        confidence_alignment=data["confidence_alignment"],
        suggestion_count=data["suggestion_count"],
    )


async def score_response(
    client: AsyncAnthropic,
    response: Response,
    original_code: str,
    expected_issues: list[str],
    judge_prompt_template: str,
    judge_model: str,
) -> ScoredResponse:
    """Score a single response using the LLM-as-judge.

    Args:
        client: Anthropic async client.
        response: The model response to score.
        original_code: The code that was reviewed.
        expected_issues: Ground-truth issues for this test case.
        judge_prompt_template: Prompt template with placeholders.
        judge_model: Model ID for the judge.

    Returns:
        ScoredResponse pairing the response with its score.
    """
    expected_str = (
        ", ".join(expected_issues) if expected_issues else "None — this is clean code"
    )
    prompt = (
        judge_prompt_template
        .replace("{code}", original_code)
        .replace("{expected_issues}", expected_str)
        .replace("{signature_variant}", response.signature_type.value)
        .replace("{review}", response.content)
    )

    message = await client.messages.create(
        model=judge_model,
        max_tokens=512,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = message.content[0].text
    score = parse_judge_response(raw_text)

    return ScoredResponse(response=response, score=score)
