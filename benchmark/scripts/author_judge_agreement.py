"""Inter-judge agreement for the author-quality cross-family result.

Signed: Kev + claude-fable-5, 2026-08-22
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: scripts/tk_judge_agreement.py (same shape, author theme)

Context: The pre-registration (fixtures/author/PREREGISTRATION.md)
quotes the headline delta only if both judges agree on its SIGN per
model. This loads the canonical gpt-5.4 verdicts (judged_author_
<model>.json) and a second judge's tagged verdicts (e.g. __claude-
opus-4-6 from rescore_author_judge.py --judge anthropic/claude-opus-4.6)
and reports the paired Δ(sign_revise − reflect_harder) EACH judge
independently found, plus the frame-contrast delta for texture. Judges
disagreeing on scale while agreeing on delta is the healthy signature
(the TK lesson); disagreeing on sign kills the headline honestly.

Confidence: 0.85 — delta/concordance logic is unit-tested
(tests/test_author_judge_agreement.py); file loading is thin glue.

Usage:
    cd benchmark
    PYTHONPATH=. python scripts/author_judge_agreement.py \
        --dir results/author/openrouter --second-tag __claude-opus-4-6
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.author_report import hazard_rates

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = ROOT / "results" / "author" / "openrouter"
HEADLINE = ("sign_revise", "reflect_harder")
CONTRAST = ("sign", "reflect")


def _delta(rows: list[dict], pair: tuple[str, str]) -> float | None:
    rates = hazard_rates(rows)
    model = rows[0]["model"] if rows else None
    a, b = (model, pair[0]), (model, pair[1])
    if a not in rates or b not in rates:
        return None
    return rates[a]["hazard_rate"] - rates[b]["hazard_rate"]


def agreement_rows(
    by_model_a: dict[str, list], by_model_b: dict[str, list]
) -> list[dict]:
    """One row per model present under BOTH judges: each judge's paired
    headline delta and a sign-concordance flag."""
    rows: list[dict] = []
    for model in sorted(set(by_model_a) & set(by_model_b)):
        da = _delta(by_model_a[model], HEADLINE)
        db = _delta(by_model_b[model], HEADLINE)
        if da is None or db is None:
            continue
        rows.append(
            {
                "model": model,
                "delta_a": da,
                "delta_b": db,
                "contrast_a": _delta(by_model_a[model], CONTRAST),
                "contrast_b": _delta(by_model_b[model], CONTRAST),
                "concordant": (da >= 0) == (db >= 0),
            }
        )
    return rows


def render_agreement(rows: list[dict], judge_a: str, judge_b: str) -> str:
    lines = [
        "# Author-quality — inter-judge agreement",
        "",
        f"Headline Δ(sign_revise − reflect_harder), paired per model. "
        f"Judge A = {judge_a}, Judge B = {judge_b}.",
        "",
        f"| Model | Δ {judge_a} | Δ {judge_b} | concordant |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['model'].split('/')[-1]} | {r['delta_a']:+.2f} "
            f"| {r['delta_b']:+.2f} | {'✓' if r['concordant'] else '✗'} |"
        )
    n_conc = sum(1 for r in rows if r["concordant"])
    lines += [
        "",
        f"**{n_conc}/{len(rows)} concordant** on the headline's sign.",
        "",
        "_Frame contrast Δ(sign − reflect), for texture (not a matched pair):_",
        "",
    ]
    for r in rows:
        ca, cb = r.get("contrast_a"), r.get("contrast_b")
        if ca is not None and cb is not None:
            lines.append(
                f"- {r['model'].split('/')[-1]}: {ca:+.2f} (A) / {cb:+.2f} (B)"
            )
    return "\n".join(lines) + "\n"


def _load_by_model(dir_: Path, tag: str) -> dict[str, list]:
    out: dict[str, list] = {}
    for f in sorted(dir_.glob(f"judged_author_*{tag}.json")):
        stem = f.name[len("judged_author_") : -len(".json")]
        if tag:
            if not stem.endswith(tag):
                continue
        elif "__" in stem:
            continue  # tagged (second-judge) files are not canonical
        rows = json.loads(f.read_text())
        if rows:
            out.setdefault(rows[0]["model"], []).extend(rows)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=str(DEFAULT_DIR))
    parser.add_argument("--second-tag", required=True, help="e.g. __claude-opus-4-6")
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    dir_ = Path(args.dir)
    a = _load_by_model(dir_, "")
    b = _load_by_model(dir_, args.second_tag)
    rows = agreement_rows(a, b)
    ja = next((r[0].get("judge", "judge-A") for r in a.values() if r), "judge-A")
    jb = next((r[0].get("judge", "judge-B") for r in b.values() if r), "judge-B")
    text = render_agreement(rows, judge_a=ja, judge_b=jb)
    if args.out:
        Path(args.out).write_text(text)
    print(text)
