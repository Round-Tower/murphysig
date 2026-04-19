"""Analyze saved responses with heuristic scoring. No API calls.

Usage:
    python -m src.analyze

# Signed: Kev + claude-opus-4-6, 2026-02-16
# Format: MurphySig v0.3.3 (https://murphysig.dev/spec)
#
# Confidence: 0.7 - heuristic analysis, to be validated with LLM judge later
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.heuristic_scorer import score_response_heuristic
from src.loader import load_cases
from src.reporter import generate_report
from src.runner import load_responses, save_scored_results


def main():
    base = Path(__file__).parent.parent
    fixtures_dir = base / "fixtures"
    results_dir = base / "results"

    # Load cases for bug metadata
    cases = load_cases(fixtures_dir / "cases.yaml")
    case_map = {c.id: c for c in cases}

    # Load saved responses
    responses = load_responses(results_dir)
    print(f"Loaded {len(responses)} responses")

    # Count by case
    from collections import Counter
    case_counts = Counter(r.case_id for r in responses)
    for case_id, count in sorted(case_counts.items()):
        print(f"  {case_id}: {count} responses")

    # Score heuristically
    scored = []
    for r in responses:
        case = case_map[r.case_id]
        sr = score_response_heuristic(r, has_bug=case.has_bug)
        scored.append(sr)

    # Save scored results
    save_scored_results(scored, results_dir)
    print(f"\nScored {len(scored)} responses (heuristic)")

    # Generate report
    report = generate_report(scored)

    # Add methodology note
    report = report.replace(
        "## Methodology",
        "## Methodology\n\n"
        "> **Note:** This report uses **heuristic scoring** (keyword matching, "
        "text analysis) rather than LLM-as-judge scoring. Results are "
        "directionally indicative but should be validated with Opus judge "
        "scoring when API access is restored.\n>\n"
        "> **Partial data:** 73/90 reviews captured. The `n_plus_one` case has "
        "only 1/18 responses (Haiku, none variant). 4/5 test cases are complete.\n",
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_path = results_dir / f"report_heuristic_{timestamp}.md"
    report_path.write_text(report)
    print(f"\nReport written to {report_path}")
    print("\n" + "=" * 60)
    print(report)


if __name__ == "__main__":
    main()
