"""LLM-as-judge scoring for the Tacit Knowledge (TK) sub-benchmark.

Signed: Kev + claude-opus-4-7, 2026-04-18
Format: MurphySig v0.3.3 (https://murphysig.dev/spec)

Context: Judges an AI's code briefing against a gold-standard ground truth.
Scores coverage (facts hit), accuracy (facts correct), hedging density,
questions asked back, and whether the briefing referenced a present
signature.

Confidence: 0.85 - uses str.replace not .format to avoid the
literal-JSON-rubric collision. Field names and ranges match the
BriefingScore dataclass invariants.
"""

from __future__ import annotations

import json

from anthropic import AsyncAnthropic

from src.tk.models import (
    Briefing,
    BriefingScore,
    ScoredBriefing,
)


def parse_tk_judgment(raw: str) -> BriefingScore:
    """Extract the briefing score JSON from a judge's raw output."""
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            f"Could not parse JSON from TK judge response: {raw[:200]}"
        )

    try:
        data = json.loads(raw[start : end + 1])
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in TK judge response: {e}") from e

    return BriefingScore(
        coverage=float(data["coverage"]),
        accuracy=float(data["accuracy"]),
        hedging_density=int(data["hedging_density"]),
        questions_back_count=int(data["questions_back_count"]),
        referenced_signature=bool(data["referenced_signature"]),
    )


async def score_tk_briefing(
    client: AsyncAnthropic,
    briefing: Briefing,
    original_code: str,
    ground_truth: str,
    judge_prompt_template: str,
    judge_model: str,
) -> ScoredBriefing:
    """Score a single briefing against its ground truth using the LLM-as-judge."""
    prompt = (
        judge_prompt_template
        .replace("{code}", original_code)
        .replace("{ground_truth}", ground_truth)
        .replace("{signature_variant}", briefing.variant.value)
        .replace("{briefing}", briefing.content)
    )

    message = await client.messages.create(
        model=judge_model,
        max_tokens=512,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = message.content[0].text
    score = parse_tk_judgment(raw_text)

    return ScoredBriefing(briefing=briefing, score=score)
