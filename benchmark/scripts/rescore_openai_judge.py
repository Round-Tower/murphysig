"""Re-score saved OpenAI honesty responses with the Anthropic judge.

Signed: Kev + claude-fable-5, 2026-06-09
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: The 2026-04-23 GPT-5.4 run was scored with a strict regex
heuristic (see run_honesty_openai.py). The original Claude benchmark
was scored with an LLM judge (claude-opus-4-6). This script replays
the saved GPT responses through the SAME production judge path
(src.honesty.scorer.score_honesty_response, same judge_prompt.txt,
same judge model) so the cross-family numbers are directly
comparable. No new subject-model calls — only judge calls (18 for
the gpt-5.4 run).

Confidence: 0.85 - reuses the production scorer verbatim; the only
new logic is row loading and summary formatting, both unit-tested
in tests/test_rescore_openai.py.

Usage:
    cd benchmark
    set -a; source .env; set +a
    .venv-openai/bin/python scripts/rescore_openai_judge.py --model gpt-5.4
"""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from src.honesty.loader import load_honesty_cases
from src.honesty.models import (
    HonestyResponse,
    PromptCondition,
    ScoredHonestyResponse,
)
from src.honesty.scorer import score_honesty_response

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "honesty"
RESULTS = ROOT / "results" / "honesty" / "openai"

JUDGE_MODEL = "claude-opus-4-6"
ROW_KEYS = {"case_id", "condition", "model", "rep", "content"}


@dataclass(frozen=True)
class LoadedRow:
    """A saved response row plus its original heuristic verdict."""

    response: HonestyResponse
    heuristic_fabricated: bool


def load_openai_rows(dir_: Path, model: str) -> list[LoadedRow]:
    """Load saved response rows for one model, skipping non-row files."""
    rows: list[LoadedRow] = []
    for path in sorted(dir_.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict) or not ROW_KEYS <= data.keys():
            continue
        if data["model"] != model:
            continue
        rows.append(
            LoadedRow(
                response=HonestyResponse(
                    case_id=data["case_id"],
                    prompt_condition=PromptCondition(data["condition"]),
                    model=data["model"],
                    repetition=data["rep"],
                    content=data["content"],
                    input_tokens=0,
                    output_tokens=0,
                ),
                heuristic_fabricated=bool(data["fabricated"]),
            )
        )
    rows.sort(
        key=lambda r: (
            r.response.case_id,
            r.response.prompt_condition.value,
            r.response.repetition,
        )
    )
    return rows


def _rate(hits: int, total: int) -> str:
    pct = 100 * hits // total if total else 0
    return f"{hits}/{total} ({pct}%)"


def format_judged_summary(
    pairs: list[tuple[ScoredHonestyResponse, bool]],
    model: str,
    judge_model: str,
) -> str:
    """Render the judged summary, including heuristic-vs-judge agreement."""
    out: list[str] = []
    out.append(f"# Honesty benchmark — {model}, judge-scored\n")
    out.append(
        f"_Judge: {judge_model} (same judge and rubric as the original "
        f"Claude benchmark). n={len(pairs)} saved responses, re-scored; "
        "no new subject-model calls._\n"
    )

    out.append("\n## Headline (judge-scored)\n")
    out.append(
        "| Condition | Fabricated (judge) | Honest handling (judge) |\n"
        "|---|---:|---:|\n"
    )
    for cond in (PromptCondition.COLD, PromptCondition.WARM):
        rs = [p for p in pairs if p[0].response.prompt_condition is cond]
        if not rs:
            continue
        fab = sum(p[0].score.any_fabrication for p in rs)
        honest = sum(p[0].score.honest for p in rs)
        out.append(
            f"| {cond.value} | {_rate(fab, len(rs))} | {_rate(honest, len(rs))} |\n"
        )

    agree = sum(
        (scored.score.any_fabrication == heuristic) for scored, heuristic in pairs
    )
    out.append(
        f"\nHeuristic vs judge agreement on fabrication: "
        f"{agree}/{len(pairs)}\n"
    )

    out.append("\n## Per response\n")
    out.append(
        "| Case | Condition | Rep | Judge: fabricated | Judge: honest | "
        "Prior: Unknown | Own contribution only | Heuristic: fabricated |\n"
        "|---|---|--:|:-:|:-:|:-:|:-:|:-:|\n"
    )
    for scored, heuristic in pairs:
        r, s = scored.response, scored.score
        out.append(
            f"| {r.case_id} | {r.prompt_condition.value} | {r.repetition} | "
            f"{'✗' if s.any_fabrication else '—'} | "
            f"{'✓' if s.honest else '✗'} | "
            f"{'✓' if s.used_prior_unknown else '—'} | "
            f"{'✓' if s.signed_own_contribution_only else '—'} | "
            f"{'✗' if heuristic else '—'} |\n"
        )
    return "".join(out)


async def rescore(model: str, delay_seconds: float) -> None:
    from anthropic import AsyncAnthropic

    rows = load_openai_rows(RESULTS, model)
    if not rows:
        raise SystemExit(f"No saved rows for model {model!r} in {RESULTS}")

    cases = {c.id: c for c in load_honesty_cases(FIXTURES / "cases.yaml")}
    judge_template = (FIXTURES / "judge_prompt.txt").read_text()
    client = AsyncAnthropic()

    pairs: list[tuple[ScoredHonestyResponse, bool]] = []
    for i, row in enumerate(rows, 1):
        r = row.response
        print(
            f"[{i}/{len(rows)}] judging {r.case_id} | "
            f"{r.prompt_condition.value} | rep={r.repetition}...",
            end=" ",
            flush=True,
        )
        scored = await score_honesty_response(
            client=client,
            response=r,
            original_code=cases[r.case_id].code,
            judge_prompt_template=judge_template,
            judge_model=JUDGE_MODEL,
        )
        verdict = (
            "fabricated" if scored.score.any_fabrication
            else "honest" if scored.score.honest
            else "other"
        )
        print(verdict)
        pairs.append((scored, row.heuristic_fabricated))
        await asyncio.sleep(delay_seconds)

    stamp = f"{datetime.now(timezone.utc):%Y%m%d_%H%M}"
    json_path = RESULTS / f"judged_{model.replace('/', '_')}.json"
    json_path.write_text(
        json.dumps(
            [
                {
                    "case_id": s.response.case_id,
                    "condition": s.response.prompt_condition.value,
                    "model": s.response.model,
                    "rep": s.response.repetition,
                    "judge_model": JUDGE_MODEL,
                    "fabricated_author": s.score.fabricated_author,
                    "fabricated_date": s.score.fabricated_date,
                    "used_prior_unknown": s.score.used_prior_unknown,
                    "asked_for_info": s.score.asked_for_info,
                    "refused_to_sign": s.score.refused_to_sign,
                    "signed_own_contribution_only": s.score.signed_own_contribution_only,
                    "any_fabrication": s.score.any_fabrication,
                    "honest": s.score.honest,
                    "heuristic_fabricated": h,
                }
                for s, h in pairs
            ],
            indent=2,
        )
    )

    summary = format_judged_summary(pairs, model=model, judge_model=JUDGE_MODEL)
    md_path = RESULTS / f"judged_summary_{model.replace('/', '_')}_{stamp}.md"
    md_path.write_text(summary)
    print(f"\nWrote {json_path}\nWrote {md_path}\n")
    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()
    asyncio.run(rescore(args.model, args.delay))
