"""Benchmark runner for the Honesty / Provenance sub-benchmark.

Signed: Kev + claude-opus-4-7, 2026-04-19
Format: MurphySig v0.4 (https://murphysig.dev/spec)

Context: Async orchestration for fabrication tests. For each case ×
condition (cold/warm) × model × repetition, ask the AI to sign an
unsigned file. Save each response immediately. Cold gives the task
without the "never fabricate" rule; warm includes it from .murphysig.

Confidence: 0.85 - mirrors TK runner shape, adapted for Honesty types.
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from anthropic import AsyncAnthropic

from src.honesty.loader import load_honesty_cases, load_honesty_prompts
from src.honesty.models import (
    HonestyResponse,
    HonestyScore,
    PromptCondition,
    ScoredHonestyResponse,
)
from src.honesty.scorer import score_honesty_response
from src.models import RunConfig


async def run_honesty_single(
    client: AsyncAnthropic,
    model: str,
    prompt: str,
    case_id: str,
    prompt_condition: PromptCondition,
    repetition: int,
    temperature: float,
) -> HonestyResponse:
    """Send a single signing request to a model."""
    message = await client.messages.create(
        model=model,
        max_tokens=1024,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )

    return HonestyResponse(
        case_id=case_id,
        prompt_condition=prompt_condition,
        model=model,
        repetition=repetition,
        content=message.content[0].text,
        input_tokens=message.usage.input_tokens,
        output_tokens=message.usage.output_tokens,
    )


def _save_honesty_response(
    response: HonestyResponse, results_dir: Path
) -> None:
    """Save a single signing response to disk."""
    data = {
        "case_id": response.case_id,
        "prompt_condition": response.prompt_condition.value,
        "model": response.model,
        "repetition": response.repetition,
        "content": response.content,
        "input_tokens": response.input_tokens,
        "output_tokens": response.output_tokens,
    }
    filename = (
        f"{response.case_id}_{response.prompt_condition.value}_"
        f"{response.model}_{response.repetition}.json"
    )
    (results_dir / filename).write_text(json.dumps(data, indent=2))


def load_honesty_responses(results_dir: Path) -> list[HonestyResponse]:
    """Load all saved honesty responses from a results directory."""
    responses = []
    for path in sorted(results_dir.glob("*.json")):
        if path.name == "scored_honesty.json":
            continue
        data = json.loads(path.read_text())
        responses.append(
            HonestyResponse(
                case_id=data["case_id"],
                prompt_condition=PromptCondition(data["prompt_condition"]),
                model=data["model"],
                repetition=data["repetition"],
                content=data["content"],
                input_tokens=data["input_tokens"],
                output_tokens=data["output_tokens"],
            )
        )
    return responses


def save_scored_honesty(
    scored: list[ScoredHonestyResponse], results_dir: Path
) -> None:
    """Save all scored honesty responses as a single JSON file."""
    data = []
    for sr in scored:
        data.append(
            {
                "case_id": sr.response.case_id,
                "prompt_condition": sr.response.prompt_condition.value,
                "model": sr.response.model,
                "repetition": sr.response.repetition,
                "content": sr.response.content,
                "input_tokens": sr.response.input_tokens,
                "output_tokens": sr.response.output_tokens,
                "score": {
                    "fabricated_author": sr.score.fabricated_author,
                    "fabricated_date": sr.score.fabricated_date,
                    "used_prior_unknown": sr.score.used_prior_unknown,
                    "asked_for_info": sr.score.asked_for_info,
                    "refused_to_sign": sr.score.refused_to_sign,
                    "signed_own_contribution_only": (
                        sr.score.signed_own_contribution_only
                    ),
                },
            }
        )
    (results_dir / "scored_honesty.json").write_text(
        json.dumps(data, indent=2)
    )


def load_scored_honesty(results_dir: Path) -> list[ScoredHonestyResponse]:
    """Load scored honesty results from JSON."""
    path = results_dir / "scored_honesty.json"
    data = json.loads(path.read_text())
    results = []
    for item in data:
        response = HonestyResponse(
            case_id=item["case_id"],
            prompt_condition=PromptCondition(item["prompt_condition"]),
            model=item["model"],
            repetition=item["repetition"],
            content=item["content"],
            input_tokens=item["input_tokens"],
            output_tokens=item["output_tokens"],
        )
        score = HonestyScore(
            fabricated_author=item["score"]["fabricated_author"],
            fabricated_date=item["score"]["fabricated_date"],
            used_prior_unknown=item["score"]["used_prior_unknown"],
            asked_for_info=item["score"]["asked_for_info"],
            refused_to_sign=item["score"]["refused_to_sign"],
            signed_own_contribution_only=item["score"][
                "signed_own_contribution_only"
            ],
        )
        results.append(
            ScoredHonestyResponse(response=response, score=score)
        )
    return results


async def run_honesty_benchmark(
    config: RunConfig,
    fixtures_dir: Path,
    results_dir: Path,
) -> list[HonestyResponse]:
    """Run the full honesty benchmark: cases × conditions × models × reps."""
    client = AsyncAnthropic()
    cases = load_honesty_cases(fixtures_dir / "cases.yaml")
    prompts = load_honesty_prompts(fixtures_dir / "cases.yaml")

    responses: list[HonestyResponse] = []
    total = (
        len(cases)
        * len(PromptCondition)
        * len(config.models)
        * config.repetitions
    )
    completed = 0

    for case in cases:
        for condition in PromptCondition:
            prompt_template = prompts[condition]
            prompt = f"{prompt_template}\n\n---\n\n{case.code}"

            for model in config.models:
                for rep in range(config.repetitions):
                    completed += 1
                    short_model = (
                        model.split("-")[1] if "-" in model else model
                    )
                    label = (
                        f"[{completed}/{total}] HONESTY {case.id} | "
                        f"{condition.value} | {short_model} | rep {rep}"
                    )
                    print(f"  {label}...", end=" ", flush=True)

                    response = await run_honesty_single(
                        client=client,
                        model=model,
                        prompt=prompt,
                        case_id=case.id,
                        prompt_condition=condition,
                        repetition=rep,
                        temperature=config.temperature,
                    )
                    _save_honesty_response(response, results_dir)
                    responses.append(response)

                    print(
                        f"done ({response.input_tokens}+"
                        f"{response.output_tokens} tokens)"
                    )
                    await asyncio.sleep(config.delay_seconds)

    return responses


async def score_honesty_all(
    responses: list[HonestyResponse],
    fixtures_dir: Path,
    results_dir: Path,
    config: RunConfig,
) -> list[ScoredHonestyResponse]:
    """Score all honesty responses using the LLM-as-judge."""
    client = AsyncAnthropic()
    cases = load_honesty_cases(fixtures_dir / "cases.yaml")
    case_map = {c.id: c for c in cases}
    judge_template = (fixtures_dir / "judge_prompt.txt").read_text()

    scored: list[ScoredHonestyResponse] = []
    total = len(responses)

    for i, response in enumerate(responses, 1):
        case = case_map[response.case_id]
        short_model = (
            response.model.split("-")[1]
            if "-" in response.model
            else response.model
        )
        label = (
            f"[{i}/{total}] scoring HONESTY {response.case_id} | "
            f"{response.prompt_condition.value} | {short_model}"
        )
        print(f"  {label}...", end=" ", flush=True)

        result = await score_honesty_response(
            client=client,
            response=response,
            original_code=case.code,
            judge_prompt_template=judge_template,
            judge_model=config.judge_model,
        )
        scored.append(result)

        verdict = "honest" if result.score.honest else "fabricated" if result.score.any_fabrication else "other"
        print(f"done ({verdict})")
        await asyncio.sleep(config.delay_seconds)

    save_scored_honesty(scored, results_dir)
    return scored
