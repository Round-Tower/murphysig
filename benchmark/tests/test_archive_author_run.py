"""Tests for author-quality run archival (the committed, immutable record).

Signed: Kev + claude-fable-5, 2026-08-22
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: tests/test_archive_tk_run.py (same shape, author theme)

Context: The author theme's ledger unit is one row PER MODEL carrying
the per-arm hazard-handled rates and the two parity-gated decisive
deltas (sign-reflect, sign_revise-reflect_harder) — those deltas ARE
the headline, so they are what the longitudinal ledger charts. Pure
manifest/ledger logic only; file copy is thin glue, same as TK.

Confidence: 0.85
"""

from __future__ import annotations

from pytest import approx

from scripts.archive_author_run import author_ledger_rows, build_author_manifest


class TestBuildAuthorManifest:
    def test_captures_provenance_and_headline_deltas(self):
        m = build_author_manifest(
            run_id="2026-08-22_author-cross-family-6",
            date="2026-08-22",
            git_sha="abc1234",
            fixture_hash="sha256:deadbeef",
            judge_model="openai/gpt-5.4",
            reps=5,
            temperature=0.7,
            models=[
                {"provider": "openrouter", "id": "google/gemini-3.5-flash", "n": 75},
                {"provider": "openrouter", "id": "x-ai/grok-4.3", "n": 75},
            ],
            headline={
                "delta_sign_reflect": -0.18,
                "delta_sign_revise_reflect_harder": 0.01,
                "confession_rate": {"sign": 0.67, "reflect": 0.41},
            },
        )
        assert m["run_id"] == "2026-08-22_author-cross-family-6"
        assert m["theme"] == "author"
        assert m["judge_model"] == "openai/gpt-5.4"
        assert m["total_responses"] == 150
        assert m["model_count"] == 2
        assert m["headline"]["delta_sign_reflect"] == -0.18
        assert "signed" in m


class TestAuthorLedgerRows:
    def test_one_row_per_model_with_decisive_deltas(self):
        rates = {
            ("google/gemini-3.5-flash", "bare"): {"hazard_rate": 0.60, "core_rate": 1.0, "n": 15},
            ("google/gemini-3.5-flash", "reflect"): {"hazard_rate": 0.80, "core_rate": 1.0, "n": 15},
            ("google/gemini-3.5-flash", "sign"): {"hazard_rate": 0.70, "core_rate": 1.0, "n": 15},
            ("google/gemini-3.5-flash", "sign_revise"): {"hazard_rate": 0.88, "core_rate": 1.0, "n": 15},
            ("google/gemini-3.5-flash", "reflect_harder"): {"hazard_rate": 0.84, "core_rate": 1.0, "n": 15},
        }
        rows = author_ledger_rows("rid", "2026-08-22", rates)
        assert len(rows) == 1
        r = rows[0]
        assert r["model"] == "google/gemini-3.5-flash"
        assert r["hazard_sign"] == 0.70
        assert r["hazard_reflect"] == 0.80
        assert r["delta_sign_reflect"] == approx(-0.10)
        assert r["delta_sign_revise_reflect_harder"] == approx(0.04)
        assert r["n_per_arm"] == 15

    def test_skips_model_missing_a_decisive_arm(self):
        rates = {
            ("x", "sign"): {"hazard_rate": 0.7, "core_rate": 1.0, "n": 15},
            ("x", "bare"): {"hazard_rate": 0.6, "core_rate": 1.0, "n": 15},
        }
        assert author_ledger_rows("rid", "2026-08-22", rates) == []
