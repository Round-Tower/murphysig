"""Tests for the author-quality report aggregation.

Signed: Kev + claude-fable-5, 2026-07-08
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: The headline metric is a within-model delta between arms
(hazard-handled rate), plus the deferral decomposition (of hazards
missed in code, how many the note confessed) and the write-time
confidence calibration split. Pure aggregation math over synthetic
rows — this is where a sign error would silently flip the finding.

Confidence: 0.85
"""

from __future__ import annotations

from scripts.author_report import (
    calibration_split,
    confession_rates,
    hazard_rates,
    parse_stated_confidence,
    render_report,
)


def _row(model, arm, hazards, core=True, trailing="", acknowledged=None):
    return {
        "model": model,
        "arm": arm,
        "verdict": {"hazards": hazards, "core_correct": core},
        "trailing": trailing,
        "acknowledged": acknowledged,
    }


class TestHazardRates:
    def test_rate_is_fraction_of_handled_hazards(self):
        rows = [
            _row("m", "bare", {"H1": "handled", "H2": "missed"}),
            _row("m", "bare", {"H1": "handled", "H2": "handled"}),
        ]
        rates = hazard_rates(rows)
        assert rates[("m", "bare")]["hazard_rate"] == 0.75
        assert rates[("m", "bare")]["n"] == 2

    def test_core_correct_rate(self):
        rows = [
            _row("m", "sign", {"H1": "handled"}, core=True),
            _row("m", "sign", {"H1": "handled"}, core=False),
        ]
        assert hazard_rates(rows)[("m", "sign")]["core_rate"] == 0.5

    def test_groups_by_model_and_arm(self):
        rows = [
            _row("a", "bare", {"H1": "missed"}),
            _row("b", "bare", {"H1": "handled"}),
        ]
        rates = hazard_rates(rows)
        assert rates[("a", "bare")]["hazard_rate"] == 0.0
        assert rates[("b", "bare")]["hazard_rate"] == 1.0


class TestConfessionRates:
    def test_confession_counts_only_missed_hazards(self):
        rows = [
            _row("m", "sign", {"H1": "missed", "H2": "handled"}, acknowledged=["H1", "H2"]),
            _row("m", "sign", {"H1": "missed", "H2": "missed"}, acknowledged=[]),
        ]
        r = confession_rates(rows)["sign"]
        assert r["missed"] == 3
        assert r["confessed"] == 1  # only H1 of row 1; row 2 confessed nothing

    def test_matching_survives_judge_case_and_punctuation_drift(self):
        # A judge replying "h1" or "H1." must still count — a silent
        # mismatch here under-reports the confession rate, which is the
        # headline mechanism claim.
        rows = [_row("m", "sign", {"H1": "missed", "H2": "missed"}, acknowledged=["h1", "H2."])]
        assert confession_rates(rows)["sign"]["confessed"] == 2

    def test_rows_without_deferral_verdict_are_excluded(self):
        # No deferral verdict -> the row contributes nothing; an arm with
        # no contributing rows is absent, not reported as a false zero.
        rows = [_row("m", "sign", {"H1": "missed"}, acknowledged=None)]
        assert "sign" not in confession_rates(rows)


class TestRenderReport:
    def test_partial_arm_dataset_renders_dashes_not_keyerror(self):
        # The runner supports --arm and the judge skips rows on outages —
        # a dataset missing whole arms is a designed-for state. The report
        # must degrade to "—" cells, never crash.
        rows = [
            _row("m", "bare", {"H1": "missed"}),
            _row("m", "reflect", {"H1": "handled"}),
        ]
        report = render_report(rows)
        assert "—" in report
        assert "reflect" in report

    def test_full_arm_dataset_renders_all_deltas(self):
        arms = ("bare", "reflect", "sign", "sign_revise", "reflect_harder")
        rows = [_row("m", a, {"H1": "handled"}) for a in arms]
        report = render_report(rows)
        assert "Δsign−reflect" in report
        assert "+0.00" in report


class TestCalibration:
    def test_parses_confidence_from_signature_block(self):
        assert parse_stated_confidence("Confidence: 0.9 — solid") == 0.9
        assert parse_stated_confidence("**Confidence:** 0.75") == 0.75
        assert parse_stated_confidence("no confidence here") is None

    def test_split_buckets_by_threshold(self):
        rows = [
            _row("m", "sign", {"H1": "missed", "H2": "missed"}, trailing="Confidence: 0.95"),
            _row("m", "sign", {"H1": "handled", "H2": "missed"}, trailing="Confidence: 0.6"),
        ]
        hi, lo = calibration_split(rows, threshold=0.9)
        assert hi == [2]
        assert lo == [1]
