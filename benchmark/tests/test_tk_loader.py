"""Tests for TK fixture loading."""

from pathlib import Path

import pytest

from src.tk.loader import load_tk_cases
from src.tk.models import TkCase, TkSignature

FIXTURES = Path(__file__).parent.parent / "fixtures" / "tk"


class TestLoadTkCases:
    def test_loads_all_cases(self):
        cases = load_tk_cases(FIXTURES / "cases.yaml")
        assert len(cases) == 5
        assert {c.id for c in cases} == {
            "pagination",
            "sql_injection",
            "clean_code",
            "god_method",
            "n_plus_one",
        }

    def test_each_case_is_tk_case(self):
        cases = load_tk_cases(FIXTURES / "cases.yaml")
        assert all(isinstance(c, TkCase) for c in cases)

    def test_ground_truth_non_empty(self):
        cases = load_tk_cases(FIXTURES / "cases.yaml")
        for c in cases:
            assert c.ground_truth.strip(), (
                f"Case {c.id} has empty ground_truth"
            )

    def test_signature_parsed(self):
        cases = {c.id: c for c in load_tk_cases(FIXTURES / "cases.yaml")}
        pag = cases["pagination"]
        assert isinstance(pag.signature, TkSignature)
        assert 0.0 <= pag.signature.confidence <= 1.0
        assert pag.signature.context
        assert pag.signature.open

    def test_clean_code_has_high_confidence(self):
        cases = {c.id: c for c in load_tk_cases(FIXTURES / "cases.yaml")}
        assert cases["clean_code"].signature.confidence >= 0.8

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_tk_cases(tmp_path / "missing.yaml")


class TestProseControl:
    """The prose control is the structure-vs-content experiment's crux: it
    must carry the signature's facts WITHOUT any structural framing."""

    def test_every_case_has_non_empty_prose(self):
        cases = load_tk_cases(FIXTURES / "cases.yaml")
        for c in cases:
            assert c.prose.strip(), f"Case {c.id} has empty prose control"

    def test_prose_has_no_structure_cues(self):
        # No MurphySig field labels, branding, or numeric confidence — else
        # it isn't an *unstructured* control and the experiment is rigged.
        banned = [
            "Signed:",
            "Context:",
            "Confidence:",
            "Open:",
            "Heuristic:",
            "MurphySig",
            "Format:",
        ]
        cases = load_tk_cases(FIXTURES / "cases.yaml")
        for c in cases:
            for token in banned:
                assert token not in c.prose, (
                    f"Case {c.id} prose leaks structure cue {token!r}"
                )

    def test_prose_has_no_numeric_confidence(self):
        import re

        cases = load_tk_cases(FIXTURES / "cases.yaml")
        for c in cases:
            assert not re.search(r"0\.\d", c.prose), (
                f"Case {c.id} prose leaks a numeric confidence value"
            )
