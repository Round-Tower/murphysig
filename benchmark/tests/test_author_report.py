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

    def test_rows_without_deferral_verdict_are_excluded_but_counted(self):
        # No deferral verdict -> the row contributes nothing to the rate,
        # but its exclusion is COUNTED (2026-08-22 audit: drop patterns
        # were arm-asymmetric, so silent absence hid the attrition).
        rows = [_row("m", "sign", {"H1": "missed"}, acknowledged=None)]
        out = confession_rates(rows)
        assert out["sign"]["rows_judged"] == 0
        assert out["sign"]["rows_dropped"] == 1
        assert out["sign"]["missed"] == 0


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


# --- 2026-08-22 adversarial-audit additions ---

from scripts.author_report import group_rows_by_judge, paired_delta_means  # noqa: E402


class TestJudgeGrouping:
    def test_rows_partition_by_judge_never_pooled(self):
        rows = [
            {**_row("m", "sign", {"H1": "handled"}), "judge": "openai/gpt-5.4"},
            {**_row("m", "sign", {"H1": "missed"}), "judge": "anthropic/claude-opus-4.6"},
        ]
        groups = group_rows_by_judge(rows)
        assert set(groups) == {"openai/gpt-5.4", "anthropic/claude-opus-4.6"}
        assert all(len(g) == 1 for g in groups.values())


class TestPairedDeltaMeans:
    def test_mean_is_of_per_model_deltas_not_delta_of_means(self):
        # Model a: sign 0.9, reflect 0.8 (delta +0.1)
        # Model b: sign 0.2, reflect 0.4 (delta -0.2)
        # Model c has ONLY reflect (a judge-skip shape) and must be
        # excluded from the pair, not allowed to skew a pooled mean.
        rates = {
            ("a", "sign"): {"hazard_rate": 0.9, "core_rate": 1, "n": 5},
            ("a", "reflect"): {"hazard_rate": 0.8, "core_rate": 1, "n": 5},
            ("b", "sign"): {"hazard_rate": 0.2, "core_rate": 1, "n": 5},
            ("b", "reflect"): {"hazard_rate": 0.4, "core_rate": 1, "n": 5},
            ("c", "reflect"): {"hazard_rate": 0.99, "core_rate": 1, "n": 5},
        }
        d = paired_delta_means(rates)
        assert abs(d[("sign", "reflect")] - (-0.05)) < 1e-9

    def test_pair_with_no_complete_model_is_absent(self):
        rates = {("a", "sign"): {"hazard_rate": 0.9, "core_rate": 1, "n": 5}}
        assert ("sign", "reflect") not in paired_delta_means(rates)


class TestConfessionCoverage:
    def test_confession_rates_report_dropped_rows_per_arm(self):
        rows = [
            _row("m", "sign", {"H1": "missed"}, trailing="note",
                 acknowledged=["H1"]),
            _row("m", "sign", {"H1": "missed"}, trailing="note",
                 acknowledged=None),  # judge failure — must be counted as dropped
        ]
        out = confession_rates(rows)
        assert out["sign"]["rate"] == 1.0
        assert out["sign"]["rows_dropped"] == 1
        assert out["sign"]["rows_judged"] == 1
