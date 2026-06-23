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

Reviews:

2026-06-10 (Kev + claude-fable-5): Generalized for the cross-family
sweep: --dir judges any provider's saved rows (gemini, groq, ...),
and --judge-family openai adds a cross-family judge robustness check
(same rubric text, GPT as judge) so "the Opus judge is biased toward
its own family" is testable rather than assumable. Default behavior
unchanged: Opus 4.6, results/honesty/openai.

Usage:
    cd benchmark
    set -a; source .env; set +a
    PYTHONPATH=. python scripts/rescore_openai_judge.py --model gpt-5.4
    # any provider dir:
    PYTHONPATH=. python scripts/rescore_openai_judge.py --dir results/honesty/gemini --model <id>
    # cross-judge robustness:
    PYTHONPATH=. python scripts/rescore_openai_judge.py --judge-family openai --judge-model gpt-5.4
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
DEFAULT_RESULTS = ROOT / "results" / "honesty" / "openai"

JUDGE_DEFAULTS = {"anthropic": "claude-opus-4-6", "openai": "gpt-5.4"}
ROW_KEYS = {"case_id", "condition", "model", "rep", "content"}


def fill_judge_prompt(template: str, code: str, condition: str, response_text: str) -> str:
    """Fill the judge template. Uses str.replace, never .format — the
    rubric contains literal JSON braces (the bug that silently broke
    the ICL scorer pre-2026-04-18)."""
    return (
        template.replace("{code}", code)
        .replace("{prompt_condition}", condition)
        .replace("{response}", response_text)
    )


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


def _make_openai_judge(judge_model: str):
    """Cross-family judge: same rubric, GPT grading. Returns an async
    callable matching the anthropic path's signature."""
    from openai import OpenAI

    from src.honesty.scorer import parse_honesty_judgment

    client = OpenAI()

    async def judge(response: HonestyResponse, original_code: str, template: str):
        prompt = fill_judge_prompt(
            template, original_code, response.prompt_condition.value, response.content
        )
        resp = client.chat.completions.create(
            model=judge_model,
            max_completion_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        score = parse_honesty_judgment(resp.choices[0].message.content or "")
        return ScoredHonestyResponse(response=response, score=score)

    return judge


async def rescore(
    model: str,
    delay_seconds: float,
    results_dir: Path,
    judge_family: str,
    judge_model: str,
    judge_tag_override: str | None = None,
) -> None:
    rows = load_openai_rows(results_dir, model)
    if not rows:
        raise SystemExit(f"No saved rows for model {model!r} in {results_dir}")

    cases = {c.id: c for c in load_honesty_cases(FIXTURES / "cases.yaml")}
    judge_template = (FIXTURES / "judge_prompt.txt").read_text()

    if judge_family == "anthropic":
        from anthropic import AsyncAnthropic

        anthropic_client = AsyncAnthropic()

        async def judge(response: HonestyResponse, original_code: str, template: str):
            return await score_honesty_response(
                client=anthropic_client,
                response=response,
                original_code=original_code,
                judge_prompt_template=template,
                judge_model=judge_model,
            )
    else:
        judge = _make_openai_judge(judge_model)

    pairs: list[tuple[ScoredHonestyResponse, bool]] = []
    skipped = 0
    for i, row in enumerate(rows, 1):
        r = row.response
        print(
            f"[{i}/{len(rows)}] judging {r.case_id} | "
            f"{r.prompt_condition.value} | rep={r.repetition}...",
            end=" ",
            flush=True,
        )
        # One bad judge response (malformed JSON, transient 429) must not
        # abort a whole family's pass — retry on rate-limit, skip on
        # persistent error, and report the count at the end.
        scored = None
        for attempt in range(4):
            try:
                scored = await judge(r, cases[r.case_id].code, judge_template)
                break
            except Exception as e:  # noqa: BLE001 — judge SDKs/parse vary
                msg = str(e).lower()
                if ("429" in msg or "rate" in msg) and attempt < 3:
                    await asyncio.sleep(2.0 * (2**attempt))
                    continue
                print(f"SKIPPED ({type(e).__name__})")
                skipped += 1
                break
        if scored is None:
            continue
        verdict = (
            "fabricated" if scored.score.any_fabrication
            else "honest" if scored.score.honest
            else "other"
        )
        print(verdict)
        pairs.append((scored, row.heuristic_fabricated))
        await asyncio.sleep(delay_seconds)

    if not pairs:
        raise SystemExit(f"All judge calls failed for {model!r} — aborting (check credits/key).")
    if skipped:
        print(f"  ⚠ {skipped}/{len(rows)} rows skipped (judge errors) for {model}")

    stamp = f"{datetime.now(timezone.utc):%Y%m%d_%H%M}"
    if judge_tag_override is not None:
        judge_tag = judge_tag_override
    else:
        judge_tag = "" if judge_family == "anthropic" else f"__judge_{judge_model.replace('/', '_')}"
    json_path = results_dir / f"judged_{model.replace('/', '_')}{judge_tag}.json"
    json_path.write_text(
        json.dumps(
            [
                {
                    "case_id": s.response.case_id,
                    "condition": s.response.prompt_condition.value,
                    "model": s.response.model,
                    "rep": s.response.repetition,
                    "judge_model": judge_model,
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

    summary = format_judged_summary(pairs, model=model, judge_model=judge_model)
    md_path = results_dir / f"judged_summary_{model.replace('/', '_')}{judge_tag}_{stamp}.md"
    md_path.write_text(summary)
    print(f"\nWrote {json_path}\nWrote {md_path}\n")
    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument(
        "--dir",
        type=Path,
        default=DEFAULT_RESULTS,
        help="directory of saved response rows (e.g. results/honesty/gemini)",
    )
    parser.add_argument("--judge-family", choices=sorted(JUDGE_DEFAULTS), default="anthropic")
    parser.add_argument(
        "--judge-model",
        default=None,
        help="defaults per family: anthropic=claude-opus-4-6, openai=gpt-5.4",
    )
    parser.add_argument(
        "--judge-tag",
        default=None,
        help="override the output filename suffix; pass '' to write the "
        "canonical judged_<model>.json even with a non-anthropic --judge-family "
        "(e.g. the same Opus model proxied via OpenRouter)",
    )
    args = parser.parse_args()
    judge_model = args.judge_model or JUDGE_DEFAULTS[args.judge_family]
    asyncio.run(
        rescore(
            args.model,
            args.delay,
            args.dir,
            args.judge_family,
            judge_model,
            judge_tag_override=args.judge_tag,
        )
    )
