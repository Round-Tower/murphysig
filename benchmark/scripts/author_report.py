"""Report aggregator for the author-quality theme.

Signed: Kev + claude-fable-5, 2026-07-08
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: scratch/jam-2026-07-08-author-quality/author_pilot.py (same-day pilot)

Context: Three views over the judged rows. (1) Hazard-handled rate per
model x arm with the decisive parity-gated deltas: sign-reflect (does
the signing frame alone help?) and sign_revise-reflect_harder (does
resolve-then-sign beat matched hard reflection?). (2) The deferral
decomposition — of hazards missed in code, how many the trailing note
confessed, per arm; this is what separates "worse code" from "same
effort, redirected into disclosure." (3) Write-time confidence
calibration: stated Confidence vs actual misses.

Confidence: 0.8 — the aggregation math is unit-tested
(tests/test_author_report.py); a sign error here would silently flip
the finding, which is why it's tested and the runner isn't.

Usage:
    cd benchmark
    PYTHONPATH=. python scripts/author_report.py \
        --judged 'results/author/openrouter/judged_author_*.json'
"""

from __future__ import annotations

import argparse
import glob
import json
import re

ARMS = ("bare", "reflect", "sign", "sign_revise", "reflect_harder")
DELTAS = (("sign", "reflect"), ("sign_revise", "reflect_harder"), ("reflect", "bare"))


def _norm_hazard_id(h) -> str:
    """Canonicalize a hazard id for matching — judges drift on case and
    punctuation ("h1", "H1.") and a silent mismatch under-reports the
    confession rate, which is the headline mechanism claim."""
    return re.sub(r"[^A-Z0-9]", "", str(h).upper())


def hazard_rates(rows: list[dict]) -> dict:
    """{(model, arm): {hazard_rate, core_rate, n}} over judged rows.

    Note: hazards are pooled across cases before averaging, so a case
    with more hazards weighs proportionally more. All current fixtures
    have exactly 3 — revisit if the fixture audit changes that."""
    groups: dict = {}
    for r in rows:
        if not r.get("verdict"):
            continue
        g = groups.setdefault((r["model"], r["arm"]), {"h": [], "c": []})
        g["h"] += [1 if v == "handled" else 0 for v in r["verdict"]["hazards"].values()]
        g["c"].append(1 if r["verdict"].get("core_correct") else 0)
    return {
        key: {
            "hazard_rate": sum(g["h"]) / len(g["h"]),
            "core_rate": sum(g["c"]) / len(g["c"]),
            "n": len(g["c"]),
        }
        for key, g in groups.items()
    }


def confession_rates(rows: list[dict]) -> dict:
    """{arm: {missed, confessed, rate}} — of hazards MISSED in code, how
    many the trailing note acknowledged. Rows without a deferral verdict
    (no note, or judge failure) are excluded, not counted as zero."""
    out: dict = {}
    for r in rows:
        if not r.get("verdict") or r.get("acknowledged") is None:
            continue
        arm = out.setdefault(r["arm"], {"missed": 0, "confessed": 0})
        acked = {_norm_hazard_id(h) for h in r["acknowledged"]}
        for hid, v in r["verdict"]["hazards"].items():
            if v != "handled":
                arm["missed"] += 1
                arm["confessed"] += _norm_hazard_id(hid) in acked
    for arm in out.values():
        arm["rate"] = arm["confessed"] / arm["missed"] if arm["missed"] else 0.0
    return out


def parse_stated_confidence(text: str) -> float | None:
    m = re.search(r"Confidence[\s:*]*([01](?:\.\d+)?)", text or "")
    return float(m.group(1)) if m else None


def calibration_split(rows: list[dict], threshold: float = 0.9) -> tuple[list, list]:
    """(high_conf_miss_counts, low_conf_miss_counts) for rows whose
    trailing note states a parseable Confidence."""
    hi, lo = [], []
    for r in rows:
        if not r.get("verdict"):
            continue
        conf = parse_stated_confidence(r.get("trailing", ""))
        if conf is None:
            continue
        misses = sum(1 for v in r["verdict"]["hazards"].values() if v != "handled")
        (hi if conf >= threshold else lo).append(misses)
    return hi, lo


def _mean(xs) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def render_report(rows: list[dict]) -> str:
    rates = hazard_rates(rows)
    models = sorted({m for m, _a in rates})
    arms = [a for a in ARMS if any((m, a) in rates for m in models)]

    lines = ["# Author-Quality — Cross-Family Report", ""]
    judge = next((r.get("judge") for r in rows if r.get("judge")), "?")
    lines.append(f"Judged rows: {sum(1 for r in rows if r.get('verdict'))} (judge: {judge}, code-only, blind to arm)")
    lines += ["", "## Hazard-handled rate", ""]
    delta_hdr = " | ".join(f"Δ{a}−{b}" for a, b in DELTAS)
    lines.append(f"| Model | {' | '.join(arms)} | {delta_hdr} |")
    lines.append("|---" * (len(arms) + len(DELTAS) + 1) + "|")

    per_arm_means = {a: [] for a in arms}
    for model in models:
        by = {a: rates.get((model, a), {}).get("hazard_rate") for a in arms}
        for a in arms:
            if by[a] is not None:
                per_arm_means[a].append(by[a])
        cells = " | ".join(f"{by[a]:.2f}" if by[a] is not None else "—" for a in arms)
        deltas = " | ".join(
            f"{by[a] - by[b]:+.2f}"
            if by.get(a) is not None and by.get(b) is not None
            else "—"
            for a, b in DELTAS
        )
        lines.append(f"| {model.split('/')[-1]} | {cells} | {deltas} |")
    mean = {a: _mean(v) for a, v in per_arm_means.items()}
    cells = " | ".join(f"{mean[a]:.2f}" for a in arms)
    deltas = " | ".join(
        f"**{mean[a] - mean[b]:+.2f}**"
        if mean.get(a) is not None and mean.get(b) is not None
        else "—"
        for a, b in DELTAS
    )
    lines.append(f"| **MEAN** | {cells} | {deltas} |")

    conf = confession_rates(rows)
    if conf:
        lines += ["", "## Deferral — of hazards missed in code, % confessed in the note", ""]
        lines.append("| Arm | missed | confessed | rate |")
        lines.append("|---|---|---|---|")
        for arm in arms:
            if arm in conf:
                c = conf[arm]
                lines.append(f"| {arm} | {c['missed']} | {c['confessed']} | {c['rate']:.0%} |")

    hi, lo = calibration_split(rows)
    if hi or lo:
        lines += ["", "## Write-time confidence calibration", ""]
        if hi:
            lines.append(f"- stated conf ≥ 0.9: n={len(hi)}, mean hazards missed = {_mean(hi):.2f}")
        if lo:
            lines.append(f"- stated conf < 0.9: n={len(lo)}, mean hazards missed = {_mean(lo):.2f}")

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--judged", required=True, help="glob of judged_author_*.json files")
    parser.add_argument("--out", default=None, help="optional markdown output path")
    args = parser.parse_args()
    rows = []
    for path in sorted(glob.glob(args.judged)):
        rows.extend(json.loads(open(path).read()))
    report = render_report(rows)
    if args.out:
        with open(args.out, "w") as f:
            f.write(report)
    print(report)
