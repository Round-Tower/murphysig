"""Benchmark runner for the Tacit Knowledge (TK) sub-benchmark.

Signed: Kev + claude-opus-4-7, 2026-04-19
Format: MurphySig v0.4 (https://murphysig.dev/spec)

Context: Async orchestration for briefing tasks. For each case × variant
(unsigned/signed) × model × repetition, ask the AI to brief the code
using the standard question set. Save each briefing immediately for
crash resilience.

Confidence: 0.85 - mirrors src/runner.py shape, adapted for TK types.
"""

from __future__ import annotations

import asyncio
import json
from datetime import date as date_cls
from pathlib import Path

from anthropic import AsyncAnthropic

from src.models import RunConfig
from src.tk.loader import load_tk_cases
from src.tk.models import (
    Briefing,
    BriefingVariant,
    ScoredBriefing,
    TkCase,
    TkSignature,
)
from src.tk.scorer import score_tk_briefing


def _format_signature_block(sig: TkSignature, case_id: str) -> str:
    """Render a TkSignature as a MurphySig-compliant comment block."""
    today = date_cls.today().isoformat()
    lines = [
        f"# Signed: Developer, {today}",
        "# Format: MurphySig v0.4 (https://murphysig.dev/spec)",
        "#",
        f"# Context: {sig.context}",
        "#",
        f"# Confidence: {sig.confidence} - {sig.context}",
    ]
    if sig.heuristic:
        lines.append(f"# Heuristic: {sig.heuristic}")
    lines.append(f"# Open: {sig.open}")
    return "\n".join(lines) + "\n"


def apply_tk_variant(case: TkCase, variant: BriefingVariant) -> str:
    """Return the code to show the AI for this variant."""
    if variant == BriefingVariant.UNSIGNED:
        return case.code
    signature_block = _format_signature_block(case.signature, case.id)
    return f"{signature_block}\n{case.code}"


async def run_tk_briefing_single(
    client: AsyncAnthropic,
    model: str,
    prompt: str,
    case_id: str,
    variant: BriefingVariant,
    repetition: int,
    temperature: float,
) -> Briefing:
    """Send a single briefing request to a model."""
    message = await client.messages.create(
        model=model,
        max_tokens=1024,
        temperature=temperature,
        messages=[{"role": "user", "content": prompt}],
    )

    return Briefing(
        case_id=case_id,
        variant=variant,
        model=model,
        repetition=repetition,
        content=message.content[0].text,
        input_tokens=message.usage.input_tokens,
        output_tokens=message.usage.output_tokens,
    )


def _save_briefing(briefing: Briefing, results_dir: Path) -> None:
    """Save a single briefing to disk for crash resilience."""
    data = {
        "case_id": briefing.case_id,
        "variant": briefing.variant.value,
        "model": briefing.model,
        "repetition": briefing.repetition,
        "content": briefing.content,
        "input_tokens": briefing.input_tokens,
        "output_tokens": briefing.output_tokens,
    }
    filename = f"{briefing.case_id}_{briefing.variant.value}_{briefing.model}_{briefing.repetition}.json"
    (results_dir / filename).write_text(json.dumps(data, indent=2))


def load_briefings(results_dir: Path) -> list[Briefing]:
    """Load all saved briefings from a results directory."""
    briefings = []
    for path in sorted(results_dir.glob("*.json")):
        if path.name == "scored_briefings.json":
            continue
        data = json.loads(path.read_text())
        briefings.append(
            Briefing(
                case_id=data["case_id"],
                variant=BriefingVariant(data["variant"]),
                model=data["model"],
                repetition=data["repetition"],
                content=data["content"],
                input_tokens=data["input_tokens"],
                output_tokens=data["output_tokens"],
            )
        )
    return briefings


def save_scored_briefings(
    scored: list[ScoredBriefing], results_dir: Path
) -> None:
    """Save all scored briefings as a single JSON file."""
    data = []
    for sb in scored:
        data.append(
            {
                "case_id": sb.briefing.case_id,
                "variant": sb.briefing.variant.value,
                "model": sb.briefing.model,
                "repetition": sb.briefing.repetition,
                "content": sb.briefing.content,
                "input_tokens": sb.briefing.input_tokens,
                "output_tokens": sb.briefing.output_tokens,
                "score": {
                    "coverage": sb.score.coverage,
                    "accuracy": sb.score.accuracy,
                    "hedging_density": sb.score.hedging_density,
                    "questions_back_count": sb.score.questions_back_count,
                    "referenced_signature": sb.score.referenced_signature,
                },
            }
        )
    (results_dir / "scored_briefings.json").write_text(
        json.dumps(data, indent=2)
    )


def load_scored_briefings(results_dir: Path) -> list[ScoredBriefing]:
    """Load scored briefings from JSON."""
    from src.tk.models import BriefingScore

    path = results_dir / "scored_briefings.json"
    data = json.loads(path.read_text())
    results = []
    for item in data:
        briefing = Briefing(
            case_id=item["case_id"],
            variant=BriefingVariant(item["variant"]),
            model=item["model"],
            repetition=item["repetition"],
            content=item["content"],
            input_tokens=item["input_tokens"],
            output_tokens=item["output_tokens"],
        )
        score = BriefingScore(
            coverage=item["score"]["coverage"],
            accuracy=item["score"]["accuracy"],
            hedging_density=item["score"]["hedging_density"],
            questions_back_count=item["score"]["questions_back_count"],
            referenced_signature=item["score"]["referenced_signature"],
        )
        results.append(ScoredBriefing(briefing=briefing, score=score))
    return results


async def run_tk_benchmark(
    config: RunConfig,
    fixtures_dir: Path,
    results_dir: Path,
) -> list[Briefing]:
    """Run the full TK benchmark: 5 cases × 2 variants × N models × N reps."""
    client = AsyncAnthropic()
    cases = load_tk_cases(fixtures_dir / "cases.yaml")
    briefing_template = (fixtures_dir / "briefing_prompt.txt").read_text()

    briefings: list[Briefing] = []
    total = (
        len(cases)
        * len(BriefingVariant)
        * len(config.models)
        * config.repetitions
    )
    completed = 0

    for case in cases:
        for variant in BriefingVariant:
            code = apply_tk_variant(case, variant)
            prompt = briefing_template.replace("{code}", code)

            for model in config.models:
                for rep in range(config.repetitions):
                    completed += 1
                    short_model = (
                        model.split("-")[1] if "-" in model else model
                    )
                    label = (
                        f"[{completed}/{total}] TK {case.id} | "
                        f"{variant.value} | {short_model} | rep {rep}"
                    )
                    print(f"  {label}...", end=" ", flush=True)

                    briefing = await run_tk_briefing_single(
                        client=client,
                        model=model,
                        prompt=prompt,
                        case_id=case.id,
                        variant=variant,
                        repetition=rep,
                        temperature=config.temperature,
                    )
                    _save_briefing(briefing, results_dir)
                    briefings.append(briefing)

                    print(
                        f"done ({briefing.input_tokens}+"
                        f"{briefing.output_tokens} tokens)"
                    )
                    await asyncio.sleep(config.delay_seconds)

    return briefings


async def score_tk_all(
    briefings: list[Briefing],
    fixtures_dir: Path,
    results_dir: Path,
    config: RunConfig,
) -> list[ScoredBriefing]:
    """Score all TK briefings using the LLM-as-judge."""
    client = AsyncAnthropic()
    cases = load_tk_cases(fixtures_dir / "cases.yaml")
    case_map = {c.id: c for c in cases}
    judge_template = (fixtures_dir / "judge_prompt.txt").read_text()

    scored: list[ScoredBriefing] = []
    total = len(briefings)

    for i, briefing in enumerate(briefings, 1):
        case = case_map[briefing.case_id]
        short_model = (
            briefing.model.split("-")[1] if "-" in briefing.model else briefing.model
        )
        label = (
            f"[{i}/{total}] scoring TK {briefing.case_id} | "
            f"{briefing.variant.value} | {short_model}"
        )
        print(f"  {label}...", end=" ", flush=True)

        result = await score_tk_briefing(
            client=client,
            briefing=briefing,
            original_code=case.code,
            ground_truth=case.ground_truth,
            judge_prompt_template=judge_template,
            judge_model=config.judge_model,
        )
        scored.append(result)

        print(
            f"done (coverage={result.score.coverage:.2f}, "
            f"acc={result.score.accuracy:.2f}, "
            f"hedge={result.score.hedging_density}, "
            f"qs={result.score.questions_back_count})"
        )
        await asyncio.sleep(config.delay_seconds)

    save_scored_briefings(scored, results_dir)
    return scored
