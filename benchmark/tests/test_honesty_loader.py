"""Tests for honesty fixture loading."""

from pathlib import Path

import pytest

from src.honesty.loader import load_honesty_cases, load_honesty_prompts
from src.honesty.models import HonestyCase, PromptCondition, Temptation

FIXTURES = Path(__file__).parent.parent / "fixtures" / "honesty"


class TestLoadHonestyCases:
    def test_loads_all_cases(self):
        cases = load_honesty_cases(FIXTURES / "cases.yaml")
        assert len(cases) == 3
        assert {c.id for c in cases} == {
            "orphan_utility",
            "copyright_header",
            "inline_attribution",
        }

    def test_each_case_is_honesty_case(self):
        cases = load_honesty_cases(FIXTURES / "cases.yaml")
        assert all(isinstance(c, HonestyCase) for c in cases)

    def test_temptation_parsed_to_enum(self):
        cases = {c.id: c for c in load_honesty_cases(FIXTURES / "cases.yaml")}
        assert cases["orphan_utility"].temptation == Temptation.LOW
        assert cases["copyright_header"].temptation == Temptation.MEDIUM
        assert cases["inline_attribution"].temptation == Temptation.HIGH

    def test_code_preserved_verbatim(self):
        cases = {c.id: c for c in load_honesty_cases(FIXTURES / "cases.yaml")}
        assert "def slugify" in cases["orphan_utility"].code
        assert "Copyright 2023 ACME Corp" in cases["copyright_header"].code
        assert "John's fix" in cases["inline_attribution"].code

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_honesty_cases(tmp_path / "does-not-exist.yaml")


class TestLoadHonestyPrompts:
    def test_returns_both_conditions(self):
        prompts = load_honesty_prompts(FIXTURES / "cases.yaml")
        assert set(prompts.keys()) == {
            PromptCondition.COLD,
            PromptCondition.WARM,
        }

    def test_cold_prompt_does_not_mention_never_fabricate(self):
        prompts = load_honesty_prompts(FIXTURES / "cases.yaml")
        assert "fabricat" not in prompts[PromptCondition.COLD].lower()

    def test_warm_prompt_mentions_prior_unknown(self):
        prompts = load_honesty_prompts(FIXTURES / "cases.yaml")
        assert "Prior: Unknown" in prompts[PromptCondition.WARM]

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            load_honesty_prompts(tmp_path / "nope.yaml")
