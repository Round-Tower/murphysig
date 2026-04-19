"""Report generation for the Tacit Knowledge (TK) sub-benchmark.

Signed: Kev + claude-opus-4-7, 2026-04-19
Format: MurphySig v0.4 (https://murphysig.dev/spec)

Context: Aggregates TK briefing scores into a markdown report comparing
signed vs unsigned briefings on coverage, accuracy, hedging, and
questions-back. Tests whether signatures help AIs brief unfamiliar code.

Confidence: 0.85 - mirrors the ICL reporter shape.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from src.tk.models import BriefingVariant, ScoredBriefing


@dataclass
class TkGroupStats:
    count: int = 0
    mean_coverage: float = 0.0
    mean_accuracy: float = 0.0
    mean_hedging: float = 0.0
    mean_questions_back: float = 0.0
    signature_reference_rate: float = 0.0


def compute_tk_stats(results: list[ScoredBriefing]) -> TkGroupStats:
    if not results:
        return TkGroupStats()
    n = len(results)
    return TkGroupStats(
        count=n,
        mean_coverage=sum(r.score.coverage for r in results) / n,
        mean_accuracy=sum(r.score.accuracy for r in results) / n,
        mean_hedging=sum(r.score.hedging_density for r in results) / n,
        mean_questions_back=sum(r.score.questions_back_count for r in results) / n,
        signature_reference_rate=sum(
            1 for r in results if r.score.referenced_signature
        )
        / n,
    )


def _group_by(results, key_fn) -> dict:
    groups = defaultdict(list)
    for r in results:
        groups[key_fn(r)].append(r)
    return dict(groups)


def _summary_table(results: list[ScoredBriefing]) -> str:
    by_variant = _group_by(results, lambda r: r.briefing.variant)
    rows = []
    for variant in BriefingVariant:
        stats = compute_tk_stats(by_variant.get(variant, []))
        if stats.count == 0:
            continue
        rows.append(
            f"| {variant.value} | {stats.count} | "
            f"{stats.mean_coverage:.2f} | {stats.mean_accuracy:.2f} | "
            f"{stats.mean_hedging:.1f} | {stats.mean_questions_back:.1f} | "
            f"{stats.signature_reference_rate:.0%} |"
        )
    header = (
        "| Variant | N | Coverage | Accuracy | Hedging (1-5) | "
        "Questions back | Referenced sig |"
    )
    sep = "|---|---|---|---|---|---|---|"
    return f"{header}\n{sep}\n" + "\n".join(rows)


def _by_model_variant(results: list[ScoredBriefing]) -> str:
    by = _group_by(results, lambda r: (r.briefing.model, r.briefing.variant))
    rows = []
    for (model, variant), group in sorted(
        by.items(), key=lambda kv: (kv[0][0], kv[0][1].value)
    ):
        stats = compute_tk_stats(group)
        short = model.split("-")[1] if "-" in model else model
        rows.append(
            f"| {short} | {variant.value} | {stats.count} | "
            f"{stats.mean_coverage:.2f} | {stats.mean_accuracy:.2f} | "
            f"{stats.mean_hedging:.1f} | {stats.mean_questions_back:.1f} |"
        )
    header = (
        "| Model | Variant | N | Coverage | Accuracy | Hedging | Questions back |"
    )
    sep = "|---|---|---|---|---|---|---|"
    return f"{header}\n{sep}\n" + "\n".join(rows)


def _by_case_variant(results: list[ScoredBriefing]) -> str:
    by = _group_by(results, lambda r: (r.briefing.case_id, r.briefing.variant))
    rows = []
    for (case_id, variant), group in sorted(
        by.items(), key=lambda kv: (kv[0][0], kv[0][1].value)
    ):
        stats = compute_tk_stats(group)
        rows.append(
            f"| {case_id} | {variant.value} | {stats.count} | "
            f"{stats.mean_coverage:.2f} | {stats.mean_accuracy:.2f} | "
            f"{stats.mean_hedging:.1f} | {stats.mean_questions_back:.1f} |"
        )
    header = (
        "| Case | Variant | N | Coverage | Accuracy | Hedging | Questions back |"
    )
    sep = "|---|---|---|---|---|---|---|"
    return f"{header}\n{sep}\n" + "\n".join(rows)


def _hypotheses(results: list[ScoredBriefing]) -> str:
    by_variant = _group_by(results, lambda r: r.briefing.variant)
    signed = compute_tk_stats(by_variant.get(BriefingVariant.SIGNED, []))
    unsigned = compute_tk_stats(by_variant.get(BriefingVariant.UNSIGNED, []))

    def verdict(delta: float, threshold: float = 0.05) -> str:
        if delta > threshold:
            return "SUPPORTED"
        if delta < -threshold:
            return "REVERSED"
        return "INCONCLUSIVE"

    cov_delta = signed.mean_coverage - unsigned.mean_coverage
    acc_delta = signed.mean_accuracy - unsigned.mean_accuracy
    hedge_delta = unsigned.mean_hedging - signed.mean_hedging  # less hedging = better
    qs_delta = unsigned.mean_questions_back - signed.mean_questions_back

    return f"""## Hypothesis Analysis

### TK-H1: Signatures increase briefing coverage
**{verdict(cov_delta)}** — signed={signed.mean_coverage:.2f}, unsigned={unsigned.mean_coverage:.2f} (delta=+{cov_delta:.2f})

### TK-H2: Signatures increase briefing accuracy
**{verdict(acc_delta)}** — signed={signed.mean_accuracy:.2f}, unsigned={unsigned.mean_accuracy:.2f} (delta=+{acc_delta:.2f})

### TK-H3: Signatures reduce hedging (less uncertainty in briefings)
**{verdict(hedge_delta * 0.5)}** — unsigned hedging={unsigned.mean_hedging:.1f}, signed hedging={signed.mean_hedging:.1f} (delta={hedge_delta:+.2f} in direction of less hedging on signed)

### TK-H4: Signatures reduce questions-back
**{verdict(qs_delta, 0.5)}** — unsigned Qs back={unsigned.mean_questions_back:.1f}, signed={signed.mean_questions_back:.1f} (delta={qs_delta:+.1f})

### TK-H5: Signatures get referenced when present
Signature reference rate on signed variants: {signed.signature_reference_rate:.0%}
"""


def generate_tk_report(results: list[ScoredBriefing]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    overall = compute_tk_stats(results)

    return f"""# MurphySig Benchmark — Tacit Knowledge (TK)

Generated: {now}
Total briefings scored: {overall.count}

## Summary (signed vs unsigned)

{_summary_table(results)}

## By Model × Variant

{_by_model_variant(results)}

## Per-Case Breakdown

{_by_case_variant(results)}

{_hypotheses(results)}

## Methodology

- **Task**: Answer 4 briefing questions about unfamiliar code (what/cautions/uncertainties/edge cases)
- **Judge**: Scores briefing vs ground_truth on coverage + accuracy + hedging + questions_back
- **Models under test**: Haiku 4.5, Sonnet 4.5
- **Judge model**: Opus 4.6
- **Temperature**: 0.0
- **Variants**: unsigned (bare code) vs signed (code + MurphySig block)

---

*MurphySig Benchmark — Tacit Knowledge — https://murphysig.dev/benchmark*
"""
