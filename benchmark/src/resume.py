"""Resume benchmark — finish missing reviews, then score all with Opus.

Usage:
    python -m src.resume

# Signed: Kev + claude-opus-4-6, 2026-02-18
# Format: MurphySig v0.3.3 (https://murphysig.dev/spec)
#
# Confidence: 0.8 - thin resume script, delegates to existing modules
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

from anthropic import AsyncAnthropic

from src.loader import load_cases, load_prompt
from src.models import RunConfig, SignatureVariant
from src.reporter import generate_report
from src.runner import (
    _save_response,
    load_responses,
    run_single,
    score_all,
)
from src.signature import apply_signature


async def finish_reviews(
    config: RunConfig,
    fixtures_dir: Path,
    results_dir: Path,
) -> None:
    """Run only the missing review calls."""
    client = AsyncAnthropic()
    cases = load_cases(fixtures_dir / "cases.yaml")
    review_template = load_prompt(fixtures_dir / "review_prompt.txt")

    # Find what's already saved
    existing = {p.stem for p in results_dir.glob("*.json") if p.name != "scored_results.json"}

    missing = []
    for case in cases:
        for variant in SignatureVariant:
            for model in config.models:
                for rep in range(config.repetitions):
                    filename = f"{case.id}_{variant.value}_{model}_{rep}"
                    if filename not in existing:
                        missing.append((case, variant, model, rep))

    if not missing:
        print("All reviews already complete!")
        return

    print(f"\n=== Finishing {len(missing)} missing reviews ===\n")

    for i, (case, variant, model, rep) in enumerate(missing, 1):
        code = apply_signature(case, variant)
        prompt = review_template.format(code=code)
        short = model.split("-")[1] if "-" in model else model

        print(f"  [{i}/{len(missing)}] {case.id} | {variant.value} | {short} | rep {rep}...", end=" ", flush=True)

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
        print(f"done ({response.input_tokens}+{response.output_tokens} tokens)")
        await asyncio.sleep(config.delay_seconds)


async def main():
    base = Path(__file__).parent.parent
    fixtures_dir = base / "fixtures"
    results_dir = base / "results"
    config = RunConfig()

    # Step 1: Finish missing reviews
    await finish_reviews(config, fixtures_dir, results_dir)

    # Step 2: Load all responses
    responses = load_responses(results_dir)
    print(f"\nTotal responses: {len(responses)}")

    # Step 3: Score with Opus
    print(f"\n=== Scoring {len(responses)} responses with Opus ===\n")
    scored = await score_all(responses, fixtures_dir, results_dir, config)

    # Step 4: Generate report
    report = generate_report(scored)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_path = results_dir / f"report_{timestamp}.md"
    report_path.write_text(report)

    print(f"\nReport written to {report_path}")
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    asyncio.run(main())
