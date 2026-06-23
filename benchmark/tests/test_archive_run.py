"""Tests for the run-archival tool.

Signed: Kev + claude-fable-5, 2026-06-22
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: A benchmark about provenance should record its own runs with
provenance. archive_run snapshots a finished run into a committed
runs/<id>/ directory with a manifest and a longitudinal ledger so we
can chart honest-handling per family over time. These cover the pure
logic; filesystem moves are thin glue.

Confidence: 0.85
"""

from __future__ import annotations

from scripts.archive_run import build_manifest, ledger_rows, run_id_for


class TestRunId:
    def test_combines_date_and_label(self):
        assert run_id_for("2026-06-22", "cross-family-6") == "2026-06-22_cross-family-6"

    def test_slugifies_label(self):
        assert run_id_for("2026-06-22", "Cross Family 6!") == "2026-06-22_cross-family-6"


class TestBuildManifest:
    def test_captures_provenance_fields(self):
        m = build_manifest(
            run_id="2026-06-22_cross-family-6",
            theme="honesty",
            date="2026-06-22",
            git_sha="abc1234",
            fixture_hash="sha256:deadbeef",
            judge_model="claude-opus-4-6",
            reps=10,
            models=[
                {"provider": "openrouter", "id": "google/gemini-3.5-flash", "n": 60},
                {"provider": "openrouter", "id": "x-ai/grok-4.3", "n": 60},
            ],
        )
        assert m["run_id"] == "2026-06-22_cross-family-6"
        assert m["git_sha"] == "abc1234"
        assert m["fixture_hash"] == "sha256:deadbeef"
        assert m["judge_model"] == "claude-opus-4-6"
        assert m["total_responses"] == 120
        assert m["model_count"] == 2
        assert "signed" in m  # the run itself is MurphySig-signed


class TestLedgerRows:
    def test_one_row_per_model_condition_with_rates(self):
        agg = {
            "google/gemini-3.5-flash": {
                "cold": {"n": 3, "fabrication": 0, "honest": 0, "prior_unknown": 0},
                "warm": {"n": 3, "fabrication": 0, "honest": 3, "prior_unknown": 3},
            }
        }
        rows = ledger_rows("2026-06-22_cross-family-6", "2026-06-22", agg)
        assert len(rows) == 2  # cold + warm
        warm = next(r for r in rows if r["condition"] == "warm")
        assert warm["run_id"] == "2026-06-22_cross-family-6"
        assert warm["model"] == "google/gemini-3.5-flash"
        assert warm["n"] == 3
        assert warm["honest"] == 3
        assert warm["honest_rate"] == 1.0
        assert warm["fabrication_rate"] == 0.0

    def test_skips_empty_conditions(self):
        agg = {"x": {"cold": {"n": 0, "fabrication": 0, "honest": 0, "prior_unknown": 0}}}
        rows = ledger_rows("rid", "2026-06-22", agg)
        assert rows == []
