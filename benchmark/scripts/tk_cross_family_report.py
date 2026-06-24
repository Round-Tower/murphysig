"""Aggregate judged TK results into the cross-family delta table.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: TK's claim is delta-based — "a MurphySig signature helps THIS
model brief unfamiliar code better" — measured as the within-model
difference between the signed and unsigned variants. Reporting absolute
coverage across families would conflate the signature effect with raw
capability; the delta (signed − unsigned, same model, same cases)
controls for capability, which is exactly why TK generalises across
families more cleanly than Honesty did. This reads every
judged_tk_*.json under results/tk/ and renders one row per model:
Δcoverage, Δhedging, and the signed-variant referenced-signature rate.

Confidence: 0.85 — aggregation + delta logic are unit-tested
(tests/test_tk_cross_family_report.py); file discovery is thin glue.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_ROOT = ROOT / "results" / "tk"

VARIANTS = ("unsigned", "signed")


def aggregate_tk(rows: list[dict]) -> dict[str, dict]:
    """Group judged rows by model × variant, computing means and the
    referenced-signature count."""
    buckets: dict[str, dict[str, list[dict]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for r in rows:
        buckets[r["model"]][r["variant"]].append(r)

    agg: dict[str, dict] = {}
    for model, by_variant in buckets.items():
        agg[model] = {}
        for variant, rs in by_variant.items():
            n = len(rs)
            agg[model][variant] = {
                "n": n,
                "coverage": sum(x["coverage"] for x in rs) / n,
                "accuracy": sum(x["accuracy"] for x in rs) / n,
                "hedging": sum(x["hedging_density"] for x in rs) / n,
                "referenced_signature": sum(
                    bool(x["referenced_signature"]) for x in rs
                ),
            }
    return agg


def _fmt_delta(value: float) -> str:
    return f"{value:+.2f}"


def delta_table(agg: dict[str, dict]) -> str:
    """Render the cross-family TK delta table. The delta columns are the
    headline; a model missing either variant renders '—' (delta
    undefined without a same-model baseline)."""
    out = ["# TK cross-family — signature uplift (signed − unsigned)\n"]
    out.append(
        "_Delta is within-model (same model briefs each case twice), so it "
        "controls for raw capability. Positive Δcoverage and negative "
        "Δhedging are the MurphySig effect._\n\n"
    )
    out.append(
        "| Model | n (u/s) | Coverage u→s | Δcoverage | Δhedging | Referenced sig (signed) |\n"
        "|---|---|---|--:|--:|--:|\n"
    )
    for model in sorted(agg):
        u = agg[model].get("unsigned")
        s = agg[model].get("signed")
        if not u or not s:
            ncol = f"{u['n'] if u else 0}/{s['n'] if s else 0}"
            out.append(f"| {model} | {ncol} | — | — | — | — |\n")
            continue
        d_cov = s["coverage"] - u["coverage"]
        d_hedge = s["hedging"] - u["hedging"]
        refd_pct = 100 * s["referenced_signature"] // s["n"] if s["n"] else 0
        out.append(
            f"| {model} | {u['n']}/{s['n']} | "
            f"{u['coverage']:.2f}→{s['coverage']:.2f} | "
            f"{_fmt_delta(d_cov)} | {_fmt_delta(d_hedge)} | "
            f"{s['referenced_signature']}/{s['n']} ({refd_pct}%) |\n"
        )
    return "".join(out)


def structure_table(agg: dict[str, dict]) -> str:
    """Render the structure-vs-content decomposition.

    The headline is Δstructure = signed − prose: does the signature's
    *structure* earn its keep over the same facts written as an
    unstructured developer comment? Δcontent = prose − unsigned isolates
    the effect of the information alone; Δtotal = signed − unsigned is the
    full uplift. A model missing the prose variant renders '—' for the
    structure/content columns (delta undefined without that arm)."""
    out = ["# TK structure vs content — does the signature's *form* matter?\n"]
    out.append(
        "_Δstructure = signed − prose (same facts, structured vs plain prose) "
        "is the headline. Δcontent = prose − unsigned (the information alone). "
        "Δtotal = signed − unsigned._\n\n"
    )
    out.append(
        "| Model | n (u/p/s) | Coverage u/p/s | Δstructure | Δcontent | Δtotal |\n"
        "|---|---|---|--:|--:|--:|\n"
    )
    for model in sorted(agg):
        u = agg[model].get("unsigned")
        p = agg[model].get("prose")
        s = agg[model].get("signed")
        ncol = f"{u['n'] if u else 0}/{p['n'] if p else 0}/{s['n'] if s else 0}"
        covcol = "/".join(
            f"{c['coverage']:.2f}" if c else "—" for c in (u, p, s)
        )
        d_struct = _fmt_delta(s["coverage"] - p["coverage"]) if (s and p) else "—"
        d_content = _fmt_delta(p["coverage"] - u["coverage"]) if (p and u) else "—"
        d_total = _fmt_delta(s["coverage"] - u["coverage"]) if (s and u) else "—"
        out.append(
            f"| {model} | {ncol} | {covcol} | "
            f"{d_struct} | {d_content} | {d_total} |\n"
        )
    return "".join(out)


def load_judged_rows(results_root: Path) -> list[dict]:
    """Read every judged_tk_*.json under results/tk/**."""
    rows: list[dict] = []
    for path in sorted(results_root.glob("**/judged_tk_*.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if isinstance(data, list):
            rows.extend(d for d in data if isinstance(d, dict) and "variant" in d)
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=RESULTS_ROOT)
    args = parser.parse_args()
    rows = load_judged_rows(args.dir)
    if not rows:
        raise SystemExit(f"No judged_tk_*.json found under {args.dir}")
    agg = aggregate_tk(rows)
    print(delta_table(agg))
    print(structure_table(agg))
