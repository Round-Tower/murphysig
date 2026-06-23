"""Per-question re-judge of saved TK briefings: intent vs code-derivable.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: The holistic coverage judge (rescore_tk_judge.py) shows THAT
a signature lifts coverage, not WHERE the lift comes from. The TK
claim is sharper than "signatures help": signatures transfer the
author's tacit knowledge — purpose (Q1) and stated uncertainty (Q3),
facts you cannot derive from the code — while NOT making the model a
better independent bug-finder (Q2 careful-when-modifying, Q4 edge
cases, both code-derivable). This re-judges the same saved briefings
per question and pools the signed-vs-unsigned delta onto two axes:
intent (Q1+Q3) and code (Q2+Q4). Δintent >> Δcode proves the claim.
No new subject calls — judge-only, same OpenRouter-proxied Opus.

Confidence: 0.85 — parser + aggregator are unit-tested
(tests/test_tk_perquestion.py); the judge loop reuses the resilient
shape from rescore_tk_judge.py.

Usage:
    cd benchmark
    set -a; source .env; set +a
    OPENAI_API_KEY=$OPEN_ROUTER_API_KEY \
    OPENAI_BASE_URL=https://openrouter.ai/api/v1 \
    PYTHONPATH=. .venv/bin/python scripts/rescore_tk_perquestion.py \
        --dir results/tk/openrouter --judge-model anthropic/claude-opus-4.6
"""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from src.tk.loader import load_tk_cases

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "tk"
DEFAULT_RESULTS = ROOT / "results" / "tk" / "openrouter"

ROW_KEYS = {"case_id", "variant", "model", "rep", "content"}
QUESTIONS = ("q1", "q2", "q3", "q4")
# Q1 purpose + Q3 author-uncertainty are author intent (underivable from
# code). Q2 careful-when-modifying + Q4 edge-cases are code-derivable.
QUESTION_AXIS = {"q1": "intent", "q2": "code", "q3": "intent", "q4": "code"}


def parse_perquestion(raw: str) -> dict[str, float]:
    """Extract q1..q4 coverages from the judge's JSON. Missing keys
    default to 0.0 (a dropped field must not abort a long pass)."""
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end <= start:
        raise ValueError(f"no JSON object in per-question judge output: {raw[:160]}")
    data = json.loads(raw[start : end + 1])
    return {q: float(data.get(f"{q}_coverage", 0.0)) for q in QUESTIONS}


def fill_prompt(template: str, ground_truth: str, briefing: str) -> str:
    """str.replace, never .format — briefing/ground_truth carry braces."""
    return template.replace("{ground_truth}", ground_truth).replace("{briefing}", briefing)


def load_rows(dir_: Path) -> list[dict]:
    """Load every saved briefing row under a results dir (all models)."""
    rows: list[dict] = []
    for path in sorted(dir_.glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and ROW_KEYS <= data.keys():
            rows.append(data)
    return rows


def aggregate_perquestion(rows: list[dict]) -> dict[str, dict]:
    """Per-question signed-vs-unsigned means + delta, pooled across models."""
    agg: dict[str, dict] = {}
    for q in QUESTIONS:
        means = {}
        for variant in ("unsigned", "signed"):
            vals = [r[q] for r in rows if r["variant"] == variant]
            means[variant] = sum(vals) / len(vals) if vals else 0.0
        means["delta"] = means["signed"] - means["unsigned"]
        agg[q] = means
    return agg


def axis_summary(agg: dict[str, dict]) -> dict[str, dict]:
    """Pool per-question stats onto the intent/code axes (mean of members)."""
    axes: dict[str, dict] = {}
    for axis in ("intent", "code"):
        members = [q for q in QUESTIONS if QUESTION_AXIS[q] == axis]
        axes[axis] = {
            key: sum(agg[q][key] for q in members) / len(members)
            for key in ("unsigned", "signed", "delta")
        }
    return axes


def axis_by_model(rows: list[dict]) -> dict[str, dict]:
    """Per-model intent/code axis summary — is the mechanism uniform across
    families, or does it vary? Reuses the pooled aggregators per model."""
    models = sorted({r["model"] for r in rows})
    return {
        m: axis_summary(aggregate_perquestion([r for r in rows if r["model"] == m]))
        for m in models
    }


def render_by_model(by_model: dict[str, dict]) -> str:
    """Render the per-model intent-vs-code delta table."""
    out = ["# TK per-question by model — is the mechanism uniform?\n"]
    out.append(
        "_Per family: signature uplift on the intent axis (Q1 purpose + Q3 "
        "author-uncertainty) vs the code-derivable axis (Q2 + Q4)._\n\n"
    )
    out.append("| Model | Δ intent | Δ code | intent / code |\n|---|--:|--:|--:|\n")
    for model in sorted(by_model):
        di = by_model[model]["intent"]["delta"]
        dc = by_model[model]["code"]["delta"]
        ratio = f"{di / dc:.1f}×" if dc > 0 else "—"
        out.append(f"| {model} | {di:+.2f} | {dc:+.2f} | {ratio} |\n")
    return "".join(out)


_QLABEL = {
    "q1": "Q1 purpose (intent)",
    "q2": "Q2 careful (code)",
    "q3": "Q3 author-uncertainty (intent)",
    "q4": "Q4 edge-cases (code)",
}


def render(agg: dict[str, dict], axes: dict[str, dict], n: int) -> str:
    out = ["# TK per-question — where the signature uplift lives\n"]
    out.append(
        f"_Same {n} saved briefings, re-judged per question (Opus). Pooled "
        "across all 6 families. Q1+Q3 = author intent (underivable from "
        "code); Q2+Q4 = code-derivable._\n\n"
    )
    out.append("| Question | Unsigned | Signed | Δ |\n|---|--:|--:|--:|\n")
    for q in QUESTIONS:
        a = agg[q]
        out.append(
            f"| {_QLABEL[q]} | {a['unsigned']:.2f} | {a['signed']:.2f} | {a['delta']:+.2f} |\n"
        )
    out.append("\n## By axis (the claim)\n")
    out.append("| Axis | Unsigned | Signed | Δ |\n|---|--:|--:|--:|\n")
    for axis in ("intent", "code"):
        a = axes[axis]
        out.append(
            f"| {axis} | {a['unsigned']:.2f} | {a['signed']:.2f} | {a['delta']:+.2f} |\n"
        )
    ratio = axes["intent"]["delta"] / axes["code"]["delta"] if axes["code"]["delta"] else float("inf")
    out.append(
        f"\nIntent uplift is {ratio:.1f}× the code-derivable uplift — "
        "the signature transfers author knowledge, not bug-finding.\n"
    )
    return "".join(out)


async def main(results_dir: Path, judge_model: str, delay: float) -> None:
    from openai import OpenAI

    rows = load_rows(results_dir)
    if not rows:
        raise SystemExit(f"No saved TK rows in {results_dir}")
    cases = {c.id: c for c in load_tk_cases(FIXTURES / "cases.yaml")}
    template = (FIXTURES / "perquestion_judge_prompt.txt").read_text()
    client = OpenAI()

    judged: list[dict] = []
    skipped = 0
    for i, row in enumerate(rows, 1):
        gt = cases[row["case_id"]].ground_truth
        prompt = fill_prompt(template, gt, row["content"])
        print(
            f"[{i}/{len(rows)}] {row['model'].split('/')[-1]} | "
            f"{row['case_id']} | {row['variant']}...",
            end=" ",
            flush=True,
        )
        scores = None
        for attempt in range(4):
            try:
                resp = client.chat.completions.create(
                    model=judge_model,
                    max_completion_tokens=256,
                    messages=[{"role": "user", "content": prompt}],
                )
                scores = parse_perquestion(resp.choices[0].message.content or "")
                break
            except Exception as e:  # noqa: BLE001 — judge SDK/parse vary
                msg = str(e).lower()
                if ("429" in msg or "rate" in msg or "timeout" in msg) and attempt < 3:
                    await asyncio.sleep(2.0 * (2**attempt))
                    continue
                print(f"SKIPPED ({type(e).__name__})")
                skipped += 1
                break
        if scores is None:
            continue
        print(" ".join(f"{q}={scores[q]:.1f}" for q in QUESTIONS))
        judged.append({**{k: row[k] for k in ("case_id", "variant", "model", "rep")}, **scores})
        await asyncio.sleep(delay)

    if not judged:
        raise SystemExit("All per-question judge calls failed — aborting.")
    if skipped:
        print(f"  ⚠ {skipped}/{len(rows)} rows skipped")

    (results_dir / "perquestion_judged.json").write_text(json.dumps(judged, indent=2))
    agg = aggregate_perquestion(judged)
    axes = axis_summary(agg)
    report = render(agg, axes, len(judged))
    (results_dir / "perquestion_report.md").write_text(report)
    print(f"\nWrote {results_dir / 'perquestion_judged.json'}")
    print(f"Wrote {results_dir / 'perquestion_report.md'}\n")
    print(report)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--judge-model", default="anthropic/claude-opus-4.6")
    parser.add_argument("--delay", type=float, default=0.3)
    args = parser.parse_args()
    asyncio.run(main(args.dir, args.judge_model, args.delay))
