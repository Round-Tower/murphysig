"""Benchmark runner — orchestrates API calls across models and variants.

# Signed: Kev + claude-opus-4-6, 2026-02-16
# Format: MurphySig v0.3.3 (https://murphysig.dev/spec)
#
# Context: Thin layer — most logic lives in scorer/loader/signature
#
# Confidence: 0.75 - async orchestration with rate limiting, crash-resilient
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from anthropic import AsyncAnthropic

from src.loader import load_cases, load_prompt
from src.models import Response, RunConfig, SignatureVariant, ScoredResponse
from src.scorer import score_response
from src.signature import apply_signature


async def run_single(
    client: AsyncAnthropic,
    model: str,
    prompt: str,
    case_id: str,
    signature_type: SignatureVariant,
    repetition: int,
    temperature: float,
) -> Response:
    """Send a single review request to a model.

    Args:
        client: Anthropic async client.
        model: Model ID to use.
        prompt: The full prompt (with code embedded).
        case_id: Test case identifier.
        signature_type: Which signature variant was applied.
        repetition: Repetition index (0-based).
        temperature: Sampling temperature.

    Returns:
        A Response with the model's output and token counts.
    """
    message = await client.messages.create(
        model=model,
        max_tokens=2048,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )

    return Response(
        case_id=case_id,
        signature_type=signature_type,
        model=model,
        repetition=repetition,
        content=message.content[0].text,
        input_tokens=message.usage.input_tokens,
        output_tokens=message.usage.output_tokens,
    )


def _save_response(response: Response, results_dir: Path) -> None:
    """Save a single response to disk for crash resilience."""
    data = {
        "case_id": response.case_id,
        "signature_type": response.signature_type.value,
        "model": response.model,
        "repetition": response.repetition,
        "content": response.content,
        "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens,
    }
    filename = f"{response.case_id}_{response.signature_type.value}_{response.model}_{response.repetition}.json"
    (results_dir / filename).write_text(json.dumps(data, indent=2))


def load_responses(results_dir: Path) -> list[Response]:
    """Load all saved responses from a results directory."""
    responses = []
    for path in sorted(results_dir.glob("*.json")):
        if path.name == "scored_results.json":
            continue
        data = json.loads(path.read_text())
        responses.append(Response(
            case_id=data["case_id"],
            signature_type=SignatureVariant(data["signature_type"]),
            model=data["model"],
            repetition=data["repetition"],
            content=data["content"],
            input_tokens=data["input_tokens"],
            output_tokens=data["output_tokens"],
        ))
    return responses


def save_scored_results(scored: list[ScoredResponse], results_dir: Path) -> None:
    """Save all scored results as a single JSON file."""
    data = []
    for sr in scored:
        data.append({
            "case_id": sr.response.case_id,
            "signature_type": sr.response.signature_type.value,
            "model": sr.response.model,
            "repetition": sr.response.repetition,
            "content": sr.response.content,
            "input_tokens": sr.response.input_tokens,
            "output_tokens": sr.response.output_tokens,
            "score": {
                "bug_detected": sr.score.bug_detected,
                "scrutiny_level": sr.score.scrutiny_level,
                "signature_awareness": sr.score.signature_awareness,
                "confidence_alignment": sr.score.confidence_alignment,
                "suggestion_count": sr.score.suggestion_count,
            },
        })
    (results_dir / "scored_results.json").write_text(json.dumps(data, indent=2))


def load_scored_results(results_dir: Path) -> list[ScoredResponse]:
    """Load scored results from JSON."""
    from src.models import Score
    path = results_dir / "scored_results.json"
    data = json.loads(path.read_text())
    results = []
    for item in data:
        response = Response(
            case_id=item["case_id"],
            signature_type=SignatureVariant(item["signature_type"]),
            model=item["model"],
            repetition=item["repetition"],
            content=item["content"],
            input_tokens=item["input_tokens"],
            output_tokens=item["output_tokens"],
        )
        score = Score(
            bug_detected=item["score"]["bug_detected"],
            scrutiny_level=item["score"]["scrutiny_level"],
            signature_awareness=item["score"]["signature_awareness"],
            confidence_alignment=item["score"]["confidence_alignment"],
            suggestion_count=item["score"]["suggestion_count"],
        )
        results.append(ScoredResponse(response=response, score=score))
    return results


async def run_benchmark(
    config: RunConfig,
    fixtures_dir: Path,
    results_dir: Path,
) -> list[Response]:
    """Run the full benchmark: all cases x variants x models x repetitions.

    Saves each response immediately for crash resilience.
    """
    client = AsyncAnthropic()
    cases = load_cases(fixtures_dir / "cases.yaml")
    review_template = load_prompt(fixtures_dir / "review_prompt.txt")

    responses: list[Response] = []
    total = len(cases) * len(SignatureVariant) * len(config.models) * config.repetitions
    completed = 0

    for case in cases:
        for variant in SignatureVariant:
            code = apply_signature(case, variant)
            prompt = review_template.format(code=code)

            for model in config.models:
                for rep in range(config.repetitions):
                    completed += 1
                    label = f"[{completed}/{total}] {case.id} | {variant.value} | {model.split('-')[1]} | rep {rep}"
                    print(f"  {label}...", end=" ", flush=True)

                    response = await run_single(
                        client=client,
                        model=model,
                        prompt=prompt,
                        case_id=case.id,
                        signature_type=variant,
                        repetition=rep,
                        temperature=config.temperature,
                    )
                    _save_response(response, results_dir)
                    responses.append(response)

                    print(f"done ({response.input_tokens}+{response.output_tokens} tokens)")
                    await asyncio.sleep(config.delay_seconds)

    return responses


async def score_all(
    responses: list[Response],
    fixtures_dir: Path,
    results_dir: Path,
    config: RunConfig,
) -> list[ScoredResponse]:
    """Score all responses using the LLM-as-judge."""
    client = AsyncAnthropic()
    cases = load_cases(fixtures_dir / "cases.yaml")
    case_map = {c.id: c for c in cases}
    judge_template = load_prompt(fixtures_dir / "judge_prompt.txt")

    scored: list[ScoredResponse] = []
    total = len(responses)

    for i, response in enumerate(responses, 1):
        case = case_map[response.case_id]
        label = f"[{i}/{total}] scoring {response.case_id} | {response.signature_type.value} | {response.model.split('-')[1]}"
        print(f"  {label}...", end=" ", flush=True)

        result = await score_response(
            client=client,
            response=response,
            original_code=case.code,
            expected_issues=case.expected_issues,
            judge_prompt_template=judge_template,
            judge_model=config.judge_model,
        )
        scored.append(result)

        print(f"done (scrutiny={result.score.scrutiny_level}, bug={result.score.bug_detected})")
        await asyncio.sleep(config.delay_seconds)

    save_scored_results(scored, results_dir)
    return scored
