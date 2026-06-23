"""Inter-judge agreement for the TK cross-family result.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: The TK coverage numbers were scored by a single Opus judge.
The cheap, obvious attack is "Anthropic's judge prefers Anthropic's
convention." This loads the canonical Opus verdicts (judged_tk_
<model>.json) and a second non-Anthropic judge's verdicts (e.g.
judged_tk_<model>__gpt.json from rescore_tk_judge.py --judge-family
openai) and reports the within-model Δcoverage EACH judge independently
found. If both judges find a positive uplift for every family, the bias
attack is refuted — the effect is in the briefings, not the judge.

Confidence: 0.85 — delta/agreement logic is unit-tested
(tests/test_tk_judge_agreement.py); file loading is thin glue.

Usage:
    cd benchmark
    PYTHONPATH=. python scripts/tk_judge_agreement.py \
        --dir results/tk/openrouter --gpt-tag __gpt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = ROOT / "results" / "tk" / "openrouter"


def model_delta(rows: list[dict]) -> float | None:
    """Mean signed coverage − mean unsigned coverage; None if a variant
    is absent (delta undefined without a same-model baseline)."""
    means = {}
    for variant in ("unsigned", "signed"):
        vals = [r["coverage"] for r in rows if r["variant"] == variant]
        if not vals:
            return None
        means[variant] = sum(vals) / len(vals)
    return means["signed"] - means["unsigned"]


def agreement_rows(
    opus_by_model: dict[str, list], gpt_by_model: dict[str, list]
) -> list[dict]:
    """One row per model present under BOTH judges, with each judge's
    Δcoverage and a concordance flag."""
    rows: list[dict] = []
    for model in sorted(set(opus_by_model) & set(gpt_by_model)):
        od = model_delta(opus_by_model[model])
        gd = model_delta(gpt_by_model[model])
        if od is None or gd is None:
            continue
        rows.append(
            {
                "model": model,
                "opus_delta": od,
                "gpt_delta": gd,
                "both_positive": od > 0 and gd > 0,
            }
        )
    return rows


def render_agreement(rows: list[dict]) -> str:
    out = ["# TK inter-judge agreement — Opus vs GPT (Δcoverage signed − unsigned)\n"]
    out.append(
        "_Same briefings, two independent judges. Concordant positive deltas "
        "refute the single-judge bias attack._\n\n"
    )
    out.append("| Model | Opus Δ | GPT Δ | both positive |\n|---|--:|--:|:-:|\n")
    for r in rows:
        out.append(
            f"| {r['model']} | {r['opus_delta']:+.2f} | {r['gpt_delta']:+.2f} | "
            f"{'✓' if r['both_positive'] else '✗'} |\n"
        )
    concordant = sum(r["both_positive"] for r in rows)
    n = len(rows)
    if n:
        mo = sum(r["opus_delta"] for r in rows) / n
        mg = sum(r["gpt_delta"] for r in rows) / n
        out.append(
            f"\nBoth judges agree the uplift is positive for **{concordant}/{n}** "
            f"models. Mean Δcoverage: Opus {mo:+.2f}, GPT {mg:+.2f}.\n"
        )
    return "".join(out)


def _load_by_model(dir_: Path, tag: str) -> dict[str, list]:
    """Load judged_tk_*<tag>.json verdict files, keyed by model id."""
    by_model: dict[str, list] = {}
    for path in sorted(dir_.glob(f"judged_tk_*{tag}.json")):
        # Skip the other judge's files when tag is empty (Opus canonical).
        if not tag and "__" in path.stem.replace("judged_tk_", ""):
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        for row in data:
            by_model.setdefault(row["model"], []).append(row)
    return by_model


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--gpt-tag", default="__gpt")
    args = parser.parse_args()
    opus = _load_by_model(args.dir, "")
    gpt = _load_by_model(args.dir, args.gpt_tag)
    rows = agreement_rows(opus, gpt)
    if not rows:
        raise SystemExit("No overlapping models between the two judges.")
    report = render_agreement(rows)
    (args.dir / "judge_agreement.md").write_text(report)
    print(report)
