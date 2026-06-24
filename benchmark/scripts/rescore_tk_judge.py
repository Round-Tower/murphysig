"""Re-score saved cross-family TK briefings with the canonical Opus judge.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: run_tk_openai.py saves raw briefings per family but doesn't
score them (TK has no heuristic — coverage/accuracy/hedging are judge
calls). This replays the saved briefings through the SAME production
TK judge path (src.tk.scorer.parse_tk_judgment, fixtures/tk/
judge_prompt.txt) used for the original Claude-only run, so the
cross-family deltas are directly comparable. Mirrors
rescore_openai_judge.py: --dir judges any provider's rows, the judge
can run via Anthropic or via an OpenAI-compatible endpoint
(OpenRouter-proxied Opus when Anthropic credits are dry), and a bad
judge response never aborts a whole family's pass (retry on
rate-limit, skip on persistent error).

Confidence: 0.85 — reuses the production parser verbatim; row loading
and prompt filling are unit-tested (tests/test_rescore_tk_judge.py).

Usage:
    cd benchmark
    set -a; source .env; set +a
    PYTHONPATH=. python scripts/rescore_tk_judge.py \
        --dir results/tk/openrouter --model google/gemini-2.5-flash
    # judge via OpenRouter-proxied Opus, canonical filenames:
    PYTHONPATH=. python scripts/rescore_tk_judge.py --dir results/tk/openrouter \
        --model <id> --judge-family openai --judge-model anthropic/claude-opus-4.6 \
        --judge-tag ""
"""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from src.tk.loader import load_tk_cases
from src.tk.models import Briefing, BriefingVariant, ScoredBriefing
from src.tk.scorer import parse_tk_judgment, score_tk_briefing

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "tk"
DEFAULT_RESULTS = ROOT / "results" / "tk" / "openrouter"

JUDGE_DEFAULTS = {"anthropic": "claude-opus-4-6", "openai": "gpt-5.4"}
ROW_KEYS = {"case_id", "variant", "model", "rep", "content"}


@dataclass(frozen=True)
class TkRow:
    case_id: str
    variant: str
    model: str
    rep: int
    content: str


def load_tk_rows(
    dir_: Path, model: str, variant: str | None = None
) -> list[TkRow]:
    """Load saved TK briefing rows for one model, skipping non-row files
    (run logs, judged outputs). When `variant` is given, load only that
    arm — used by the prose-only add to avoid re-judging (and re-paying
    for) the already-scored signed/unsigned arms."""
    rows: list[TkRow] = []
    for path in sorted(dir_.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(data, dict) or not ROW_KEYS <= data.keys():
            continue
        if data["model"] != model:
            continue
        if variant is not None and data["variant"] != variant:
            continue
        rows.append(
            TkRow(
                case_id=data["case_id"],
                variant=data["variant"],
                model=data["model"],
                rep=data["rep"],
                content=data["content"],
            )
        )
    rows.sort(key=lambda r: (r.case_id, r.variant, r.rep))
    return rows


def fill_tk_judge_prompt(
    template: str, code: str, ground_truth: str, variant: str, briefing: str
) -> str:
    """Fill the TK judge template. str.replace, never .format — the code
    and briefing contain literal braces."""
    return (
        template.replace("{code}", code)
        .replace("{ground_truth}", ground_truth)
        .replace("{signature_variant}", variant)
        .replace("{briefing}", briefing)
    )


def _briefing_from_row(row: TkRow) -> Briefing:
    return Briefing(
        case_id=row.case_id,
        variant=BriefingVariant(row.variant),
        model=row.model,
        repetition=row.rep,
        content=row.content,
        input_tokens=0,
        output_tokens=0,
    )


def _make_openai_tk_judge(judge_model: str):
    """Cross-family / proxied judge: same TK rubric, OpenAI-compatible
    endpoint. Returns an async callable matching the anthropic path."""
    from openai import OpenAI

    client = OpenAI()

    async def judge(row: TkRow, code: str, ground_truth: str, template: str):
        prompt = fill_tk_judge_prompt(template, code, ground_truth, row.variant, row.content)
        resp = client.chat.completions.create(
            model=judge_model,
            max_completion_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        score = parse_tk_judgment(resp.choices[0].message.content or "")
        return ScoredBriefing(briefing=_briefing_from_row(row), score=score)

    return judge


def _summary(scored: list[ScoredBriefing], model: str, judge_model: str) -> str:
    out = [f"# TK benchmark — {model}, judge-scored\n"]
    out.append(
        f"_Judge: {judge_model} (same judge + rubric as the Claude-only TK run). "
        f"n={len(scored)} briefings re-scored; no new subject calls._\n"
    )
    out.append("\n## Signed vs unsigned (the TK delta)\n")
    out.append("| Variant | n | Coverage | Accuracy | Hedging | Referenced sig |\n")
    out.append("|---|--:|--:|--:|--:|--:|\n")
    for variant in ("unsigned", "signed"):
        rs = [s for s in scored if s.briefing.variant.value == variant]
        if not rs:
            continue
        n = len(rs)
        cov = sum(s.score.coverage for s in rs) / n
        acc = sum(s.score.accuracy for s in rs) / n
        hedge = sum(s.score.hedging_density for s in rs) / n
        refd = sum(s.score.referenced_signature for s in rs)
        out.append(
            f"| {variant} | {n} | {cov:.2f} | {acc:.2f} | {hedge:.2f} | {refd}/{n} |\n"
        )
    return "".join(out)


async def rescore(
    model: str,
    delay_seconds: float,
    results_dir: Path,
    judge_family: str,
    judge_model: str,
    judge_tag_override: str | None = None,
    variant: str | None = None,
) -> None:
    rows = load_tk_rows(results_dir, model, variant=variant)
    if not rows:
        raise SystemExit(f"No saved TK rows for model {model!r} in {results_dir}")

    cases = {c.id: c for c in load_tk_cases(FIXTURES / "cases.yaml")}
    judge_template = (FIXTURES / "judge_prompt.txt").read_text()

    if judge_family == "anthropic":
        from anthropic import AsyncAnthropic

        anthropic_client = AsyncAnthropic()

        async def judge(row: TkRow, code: str, ground_truth: str, template: str):
            return await score_tk_briefing(
                client=anthropic_client,
                briefing=_briefing_from_row(row),
                original_code=code,
                ground_truth=ground_truth,
                judge_prompt_template=template,
                judge_model=judge_model,
            )
    else:
        judge = _make_openai_tk_judge(judge_model)

    scored: list[ScoredBriefing] = []
    skipped = 0
    for i, row in enumerate(rows, 1):
        print(
            f"[{i}/{len(rows)}] judging {row.case_id} | {row.variant} | rep={row.rep}...",
            end=" ",
            flush=True,
        )
        case = cases[row.case_id]
        result = None
        for attempt in range(4):
            try:
                result = await judge(row, case.code, case.ground_truth, judge_template)
                break
            except Exception as e:  # noqa: BLE001 — judge SDKs/parse vary
                msg = str(e).lower()
                if ("429" in msg or "rate" in msg) and attempt < 3:
                    await asyncio.sleep(2.0 * (2**attempt))
                    continue
                print(f"SKIPPED ({type(e).__name__})")
                skipped += 1
                break
        if result is None:
            continue
        print(f"coverage={result.score.coverage:.2f} hedge={result.score.hedging_density}")
        scored.append(result)
        await asyncio.sleep(delay_seconds)

    if not scored:
        raise SystemExit(f"All judge calls failed for {model!r} — aborting (check credits/key).")
    if skipped:
        print(f"  ⚠ {skipped}/{len(rows)} rows skipped (judge errors) for {model}")

    stamp = f"{datetime.now(timezone.utc):%Y%m%d_%H%M}"
    if judge_tag_override is not None:
        judge_tag = judge_tag_override
    else:
        judge_tag = "" if judge_family == "anthropic" else f"__judge_{judge_model.replace('/', '_')}"
    json_path = results_dir / f"judged_tk_{model.replace('/', '_')}{judge_tag}.json"
    json_path.write_text(
        json.dumps(
            [
                {
                    "case_id": s.briefing.case_id,
                    "variant": s.briefing.variant.value,
                    "model": s.briefing.model,
                    "rep": s.briefing.repetition,
                    "judge_model": judge_model,
                    "coverage": s.score.coverage,
                    "accuracy": s.score.accuracy,
                    "hedging_density": s.score.hedging_density,
                    "questions_back_count": s.score.questions_back_count,
                    "referenced_signature": s.score.referenced_signature,
                }
                for s in scored
            ],
            indent=2,
        )
    )

    summary = _summary(scored, model=model, judge_model=judge_model)
    md_path = results_dir / f"judged_tk_summary_{model.replace('/', '_')}{judge_tag}_{stamp}.md"
    md_path.write_text(summary)
    print(f"\nWrote {json_path}\nWrote {md_path}\n")
    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="provider's model id")
    parser.add_argument("--delay", type=float, default=1.0)
    parser.add_argument("--dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--judge-family", choices=sorted(JUDGE_DEFAULTS), default="anthropic")
    parser.add_argument("--judge-model", default=None)
    parser.add_argument(
        "--judge-tag",
        default=None,
        help="override the output filename suffix; pass '' to write the "
        "canonical judged_tk_<model>.json even with a non-anthropic judge "
        "(e.g. the same Opus model proxied via OpenRouter)",
    )
    parser.add_argument(
        "--variant",
        default=None,
        choices=("unsigned", "signed", "prose"),
        help="judge only this arm (e.g. 'prose') — the prose-only add, so "
        "the already-judged signed/unsigned arms aren't re-scored",
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
            variant=args.variant,
        )
    )
