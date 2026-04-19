"""Tests for YAML loader — written first per TDD."""

from pathlib import Path

import pytest

from src.loader import load_cases, load_prompt
from src.models import TestCase


class TestLoadCases:
    def test_loads_five_cases(self, cases_yaml: Path):
        cases = load_cases(cases_yaml)
        assert len(cases) == 5

    def test_returns_test_case_objects(self, cases_yaml: Path):
        cases = load_cases(cases_yaml)
        assert all(isinstance(c, TestCase) for c in cases)

    def test_case_ids_are_unique(self, cases_yaml: Path):
        cases = load_cases(cases_yaml)
        ids = [c.id for c in cases]
        assert len(ids) == len(set(ids))

    def test_expected_case_ids(self, cases_yaml: Path):
        cases = load_cases(cases_yaml)
        ids = {c.id for c in cases}
        assert ids == {
            "subtle_bug",
            "sql_injection",
            "clean_code",
            "god_method",
            "n_plus_one",
        }

    def test_buggy_cases_have_expected_issues(self, cases_yaml: Path):
        cases = load_cases(cases_yaml)
        for case in cases:
            if case.has_bug:
                assert len(case.expected_issues) > 0, (
                    f"Case {case.id} has_bug=True but no expected_issues"
                )

    def test_clean_code_has_no_expected_issues(self, cases_yaml: Path):
        cases = load_cases(cases_yaml)
        clean = [c for c in cases if c.id == "clean_code"][0]
        assert clean.has_bug is False
        assert clean.expected_issues == []

    def test_all_cases_have_code(self, cases_yaml: Path):
        cases = load_cases(cases_yaml)
        for case in cases:
            assert len(case.code.strip()) > 0, f"Case {case.id} has empty code"

    def test_all_cases_have_signature_context(self, cases_yaml: Path):
        cases = load_cases(cases_yaml)
        for case in cases:
            assert case.high_signature_context, f"Case {case.id} missing high context"
            assert case.low_signature_context, f"Case {case.id} missing low context"

    def test_raises_on_missing_file(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_cases(tmp_path / "nonexistent.yaml")


class TestLoadPrompt:
    def test_loads_review_prompt(self, review_prompt_path: Path):
        prompt = load_prompt(review_prompt_path)
        assert "code review" in prompt.lower()
        assert "{code}" in prompt

    def test_loads_judge_prompt(self, judge_prompt_path: Path):
        prompt = load_prompt(judge_prompt_path)
        assert "bug_detected" in prompt
        assert "{review}" in prompt

    def test_raises_on_missing_file(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_prompt(tmp_path / "nonexistent.txt")
