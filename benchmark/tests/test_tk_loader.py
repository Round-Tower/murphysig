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
