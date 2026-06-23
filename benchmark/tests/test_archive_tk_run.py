"""Tests for TK run archival (the committed, immutable record).

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: Mirrors archive_run.py for the TK theme. A provenance
benchmark records its own runs with provenance. TK's ledger unit is
one row PER MODEL (the within-model signature uplift = the headline),
not per condition. Pure manifest/ledger logic only; the file copy is
thin glue.

Confidence: 0.85
"""

from __future__ import annotations

from pytest import approx

from scripts.archive_tk_run import build_tk_manifest, tk_ledger_rows


class TestBuildTkManifest:
    def test_captures_provenance_and_axis_headline(self):
        m = build_tk_manifest(
            run_id="2026-06-23_tk-cross-family-6",
            date="2026-06-23",
            git_sha="abc1234",
            fixture_hash="sha256:deadbeef",
            judge_model="anthropic/claude-opus-4.6",
            reps=5,
            temperature=0.7,
            models=[
                {"provider": "openrouter", "id": "google/gemini-3.5-flash", "n": 50},
                {"provider": "openrouter", "id": "x-ai/grok-4.3", "n": 50},
            ],
            axis_delta={"intent": 0.33, "code": 0.11},
        )
        assert m["run_id"] == "2026-06-23_tk-cross-family-6"
        assert m["theme"] == "tk"
        assert m["judge_model"] == "anthropic/claude-opus-4.6"
        assert m["temperature"] == 0.7
        assert m["total_responses"] == 100
        assert m["model_count"] == 2
        assert m["axis_delta"]["intent"] == 0.33
        assert "signed" in m


class TestTkLedgerRows:
    def test_one_row_per_model_with_delta(self):
        agg = {
            "google/gemini-3.5-flash": {
                "unsigned": {"n": 25, "coverage": 0.67, "accuracy": 0.87,
                             "hedging": 1.12, "referenced_signature": 0},
                "signed": {"n": 25, "coverage": 0.75, "accuracy": 0.87,
                           "hedging": 1.04, "referenced_signature": 18},
            }
        }
        rows = tk_ledger_rows("2026-06-23_tk-cross-family-6", "2026-06-23", agg)
        assert len(rows) == 1
        r = rows[0]
        assert r["model"] == "google/gemini-3.5-flash"
        assert r["coverage_unsigned"] == 0.67
        assert r["coverage_signed"] == 0.75
        assert r["delta_coverage"] == approx(0.08)
        assert r["delta_hedging"] == approx(-0.08)
        assert r["referenced_rate"] == approx(18 / 25)

    def test_skips_model_missing_a_variant(self):
        agg = {
            "x": {
                "signed": {"n": 5, "coverage": 0.9, "accuracy": 0.9,
                           "hedging": 1.0, "referenced_signature": 5},
            }
        }
        assert tk_ledger_rows("rid", "2026-06-23", agg) == []
