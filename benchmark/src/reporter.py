"""Markdown report generation for benchmark results.

# Signed: Kev + claude-opus-4-6, 2026-02-16
# Format: MurphySig v0.3.3 (https://murphysig.dev/spec)
#
# Confidence: 0.8 - stats are straightforward, hypothesis framing is the art
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

from src.models import ScoredResponse, SignatureVariant


@dataclass
class GroupStats:
    """Aggregated statistics for a group of scored responses."""

    count: int = 0
    bug_detection_rate: float = 0.0
    mean_scrutiny: float = 0.0
    mean_confidence_alignment: float = 0.0
    mean_suggestions: float = 0.0
    signature_awareness_rate: float = 0.0


def compute_stats(results: list[ScoredResponse]) -> GroupStats:
    """Compute aggregate statistics for a group of scored responses."""
    if not results:
        return GroupStats()

    n = len(results)
    bugs = sum(1 for r in results if r.score.bug_detected)
    scrutiny = sum(r.score.scrutiny_level for r in results)
    conf = sum(r.score.confidence_alignment for r in results)
    suggestions = sum(r.score.suggestion_count for r in results)
    awareness = sum(1 for r in results if r.score.signature_awareness)

    return GroupStats(
        count=n,
        bug_detection_rate=bugs / n,
        mean_scrutiny=scrutiny / n,
        mean_confidence_alignment=conf / n,
        mean_suggestions=suggestions / n,
        signature_awareness_rate=awareness / n,
    )


def _group_by(
    results: list[ScoredResponse],
    key_fn,
) -> dict:
    """Group results by a key function."""
    groups = defaultdict(list)
    for r in results:
        groups[key_fn(r)].append(r)
    return dict(groups)


def format_hypothesis_analysis(results: list[ScoredResponse]) -> str:
    """Generate hypothesis analysis section."""
    by_variant = _group_by(results, lambda r: r.response.signature_type)

    none_stats = compute_stats(by_variant.get(SignatureVariant.NONE, []))
    high_stats = compute_stats(by_variant.get(SignatureVariant.HIGH, []))
    low_stats = compute_stats(by_variant.get(SignatureVariant.LOW, []))

    # H1: Low confidence increases scrutiny
    h1_delta = low_stats.mean_scrutiny - none_stats.mean_scrutiny
    h1_support = "SUPPORTED" if h1_delta > 0.3 else "NOT SUPPORTED" if h1_delta < -0.3 else "INCONCLUSIVE"

    # H2: High confidence reduces false positives on clean code
    clean_by_variant = _group_by(
        [r for r in results if r.response.case_id == "clean_code"],
        lambda r: r.response.signature_type,
    )
    clean_none = compute_stats(clean_by_variant.get(SignatureVariant.NONE, []))
    clean_high = compute_stats(clean_by_variant.get(SignatureVariant.HIGH, []))
    h2_delta = clean_none.mean_suggestions - clean_high.mean_suggestions
    h2_support = "SUPPORTED" if h2_delta > 0.3 else "NOT SUPPORTED" if h2_delta < -0.3 else "INCONCLUSIVE"

    # H3: Models read and reference signatures
    signed_results = [r for r in results if r.response.signature_type != SignatureVariant.NONE]
    signed_stats = compute_stats(signed_results) if signed_results else GroupStats()
    h3_support = "SUPPORTED" if signed_stats.signature_awareness_rate > 0.3 else "NOT SUPPORTED"

    # H4: Bug detection rate: low > none > high
    buggy = [r for r in results if r.response.case_id != "clean_code"]
    buggy_by_variant = _group_by(buggy, lambda r: r.response.signature_type)
    buggy_none = compute_stats(buggy_by_variant.get(SignatureVariant.NONE, []))
    buggy_high = compute_stats(buggy_by_variant.get(SignatureVariant.HIGH, []))
    buggy_low = compute_stats(buggy_by_variant.get(SignatureVariant.LOW, []))
    h4_strict_order = (
        buggy_low.bug_detection_rate > buggy_none.bug_detection_rate
        and buggy_none.bug_detection_rate > buggy_high.bug_detection_rate
    )
    h4_weak_order = (
        buggy_low.bug_detection_rate >= buggy_none.bug_detection_rate >= buggy_high.bug_detection_rate
        and (buggy_low.bug_detection_rate - buggy_high.bug_detection_rate) > 0.1
    )
    h4_support = "SUPPORTED" if h4_strict_order else "PARTIALLY SUPPORTED" if h4_weak_order else "INCONCLUSIVE"

    return f"""## Hypothesis Analysis

### H1: Low confidence increases scrutiny
**{h1_support}** — Mean scrutiny: low={low_stats.mean_scrutiny:.2f}, none={none_stats.mean_scrutiny:.2f} (delta={h1_delta:+.2f})

### H2: High confidence reduces false positives on clean code
**{h2_support}** — Mean suggestions on clean code: none={clean_none.mean_suggestions:.2f}, high={clean_high.mean_suggestions:.2f} (delta={h2_delta:+.2f})

### H3: Models read and reference signatures
**{h3_support}** — Signature awareness rate (signed variants): {signed_stats.signature_awareness_rate:.1%}

### H4: Bug detection rate ordering (low > none > high)
**{h4_support}** — Detection rates: low={buggy_low.bug_detection_rate:.1%}, none={buggy_none.bug_detection_rate:.1%}, high={buggy_high.bug_detection_rate:.1%}
"""


def _summary_table(results: list[ScoredResponse]) -> str:
    """Generate the main summary table by model x variant."""
    rows = []
    by_model = _group_by(results, lambda r: r.response.model)

    for model, model_results in sorted(by_model.items()):
        by_variant = _group_by(model_results, lambda r: r.response.signature_type)
        for variant in SignatureVariant:
            stats = compute_stats(by_variant.get(variant, []))
            if stats.count == 0:
                continue
            short_model = model.split("-")[1] if "-" in model else model
            rows.append(
                f"| {short_model} | {variant.value} | {stats.count} | "
                f"{stats.bug_detection_rate:.1%} | {stats.mean_scrutiny:.1f} | "
                f"{stats.signature_awareness_rate:.1%} | {stats.mean_suggestions:.1f} |"
            )

    header = "| Model | Variant | N | Bug Detection | Scrutiny | Sig Awareness | Suggestions |"
    sep = "|-------|---------|---|---------------|----------|---------------|-------------|"

    return f"{header}\n{sep}\n" + "\n".join(rows)


def _case_detail_table(results: list[ScoredResponse]) -> str:
    """Generate a per-case breakdown table."""
    rows = []
    by_case = _group_by(results, lambda r: r.response.case_id)

    for case_id, case_results in sorted(by_case.items()):
        by_variant = _group_by(case_results, lambda r: r.response.signature_type)
        for variant in SignatureVariant:
            stats = compute_stats(by_variant.get(variant, []))
            if stats.count == 0:
                continue
            rows.append(
                f"| {case_id} | {variant.value} | {stats.count} | "
                f"{stats.bug_detection_rate:.1%} | {stats.mean_scrutiny:.1f} | "
                f"{stats.mean_suggestions:.1f} |"
            )

    header = "| Case | Variant | N | Bug Detection | Scrutiny | Suggestions |"
    sep = "|------|---------|---|---------------|----------|-------------|"

    return f"{header}\n{sep}\n" + "\n".join(rows)


def generate_report(results: list[ScoredResponse]) -> str:
    """Generate a full markdown report from scored results.

    Args:
        results: All scored responses from the benchmark run.

    Returns:
        Complete markdown report string.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    overall = compute_stats(results)

    return f"""# MurphySig Benchmark Results

Generated: {now}
Total responses scored: {overall.count}

## Summary

{_summary_table(results)}

## Per-Case Breakdown

{_case_detail_table(results)}

{format_hypothesis_analysis(results)}

## Methodology

- **Models under test**: Haiku 4.5, Sonnet 4.5
- **Judge model**: Opus 4.6
- **Temperature**: 0.0
- **Repetitions**: 3 per configuration
- **Signature variants**: none, high (0.9), low (0.3)

---

*MurphySig Benchmark v0.1.0 — https://murphysig.dev*
"""
