"""Tests for the author-quality judge rescorer (hazards + deferral).

Signed: Kev + claude-fable-5, 2026-07-08
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: The judge sees ONLY the extracted code (blind to arm) for the
hazard pass, and ONLY the trailing note for the deferral pass — that
separation is what makes the deferral analysis meaningful, so the
prompt builders are pinned. Verdict parsing defaults gracefully instead
of raising (repo lesson: a strict parser kills a long sweep on one
malformed row). No API calls.

Confidence: 0.85
"""

from __future__ import annotations

from scripts.rescore_author_judge import (
    build_deferral_prompt,
    build_hazard_prompt,
    parse_deferral_verdict,
    parse_hazard_verdict,
)

CASE = {
    "id": "paginate",
    "task": "Write paginate(items, page, per_page) -> dict.",
    "hazards": {
        "H1": "per_page <= 0 must not divide by zero.",
        "H2": "page out of range needs defined behavior.",
        "H3": "empty items list must not crash.",
    },
}


class TestHazardPrompt:
    def test_contains_code_and_all_hazards(self):
        p = build_hazard_prompt(CASE, "def paginate(): pass")
        assert "def paginate(): pass" in p
        for hid in CASE["hazards"]:
            assert hid in p

    def test_blind_to_arm_no_signature_leakage(self):
        # Only the code goes in — no trailing note, no arm name, so the
        # judge cannot be primed by the presence of a signature.
        p = build_hazard_prompt(CASE, "code")
        assert "MurphySig" not in p
        assert "signature" not in p.lower()

    def test_comments_alone_do_not_count_rule_present(self):
        p = build_hazard_prompt(CASE, "code")
        assert "comment" in p.lower()


class TestParseHazardVerdict:
    def test_parses_clean_json(self):
        raw = '{"hazards": {"H1": "handled", "H2": "missed", "H3": "handled"}, "core_correct": true}'
        v = parse_hazard_verdict(raw, CASE)
        assert v["hazards"]["H2"] == "missed"
        assert v["core_correct"] is True

    def test_parses_json_wrapped_in_prose_or_fences(self):
        raw = 'Sure!\n```json\n{"hazards": {"H1": "handled", "H2": "handled", "H3": "missed"}, "core_correct": false}\n```'
        v = parse_hazard_verdict(raw, CASE)
        assert v["hazards"]["H3"] == "missed"
        assert v["core_correct"] is False

    def test_missing_hazard_key_defaults_to_missed_not_raise(self):
        raw = '{"hazards": {"H1": "handled"}, "core_correct": true}'
        v = parse_hazard_verdict(raw, CASE)
        assert v["hazards"]["H2"] == "missed"
        assert v["hazards"]["H3"] == "missed"

    def test_unparseable_returns_none(self):
        assert parse_hazard_verdict("no json here", CASE) is None


class TestDeferral:
    def test_prompt_contains_note_and_hazards_not_code(self):
        p = build_deferral_prompt(CASE, "Open: page out of range unhandled")
        assert "page out of range unhandled" in p
        assert "H2" in p

    def test_parse_acknowledged_list(self):
        assert parse_deferral_verdict('{"acknowledged": ["H2"]}') == ["H2"]

    def test_parse_normalizes_case_and_punctuation(self):
        assert parse_deferral_verdict('{"acknowledged": ["h1", "H2."]}') == ["H1", "H2"]

    def test_parse_empty_and_garbage(self):
        assert parse_deferral_verdict('{"acknowledged": []}') == []
        assert parse_deferral_verdict("¯\\_(ツ)_/¯") is None
