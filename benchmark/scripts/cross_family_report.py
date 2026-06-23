"""Aggregate judged honesty results into a cross-family table.

Signed: Kev + claude-fable-5, 2026-06-22
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: rescore_openai_judge.py writes one judged_<model>.json per
model (list of per-response judge verdicts). This rolls every such
file — plus the original Claude scored_honesty.json — into a single
cold-vs-warm table per model for the /benchmark/ page. The judge
fields are canonical; the heuristic self-attribution texture is
reported separately in each per-model summary.

Confidence: 0.85 - pure aggregation over a fixed schema, unit-tested.

Usage:
    cd benchmark
    PYTHONPATH=. python scripts/cross_family_report.py \
        results/honesty/openrouter/judged_*.json \
        results/honesty/openai/judged_gpt-5.4.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

CONDITIONS = ("cold", "warm")


def aggregate_rows(rows: list[dict]) -> dict:
    """Group judged rows by model then condition, counting outcomes."""
    agg: dict[str, dict] = {}
    for r in rows:
        model = r["model"]
        cond = r["condition"]
        bucket = agg.setdefault(model, {}).setdefault(
            cond, {"n": 0, "fabrication": 0, "honest": 0, "prior_unknown": 0}
        )
        bucket["n"] += 1
        bucket["fabrication"] += int(bool(r.get("any_fabrication")))
        bucket["honest"] += int(bool(r.get("honest")))
        bucket["prior_unknown"] += int(bool(r.get("used_prior_unknown")))
    return agg


def _cell(bucket: dict | None, key: str) -> str:
    if not bucket or not bucket["n"]:
        return "—"
    pct = 100 * bucket[key] // bucket["n"]
    return f"{bucket[key]}/{bucket['n']} ({pct}%)"


def render_table(agg: dict) -> str:
    """Render a markdown table: one row per model, cold→warm per metric."""
    out = [
        "| Model | Cold fab. | Warm fab. | Cold honest | Warm honest "
        "| Cold Prior:Unknown | Warm Prior:Unknown |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for model in sorted(agg):
        cold = agg[model].get("cold")
        warm = agg[model].get("warm")
        out.append(
            f"| `{model}` "
            f"| {_cell(cold, 'fabrication')} | {_cell(warm, 'fabrication')} "
            f"| {_cell(cold, 'honest')} | {_cell(warm, 'honest')} "
            f"| {_cell(cold, 'prior_unknown')} | {_cell(warm, 'prior_unknown')} |"
        )
    return "\n".join(out) + "\n"


def load_judged(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    for p in paths:
        data = json.loads(p.read_text())
        if isinstance(data, list):
            rows.extend(data)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path, help="judged_*.json files")
    args = parser.parse_args()
    rows = load_judged(args.paths)
    agg = aggregate_rows(rows)
    print(f"# Cross-family honesty — judge-scored ({len(rows)} responses)\n")
    print(render_table(agg))


if __name__ == "__main__":
    main()
