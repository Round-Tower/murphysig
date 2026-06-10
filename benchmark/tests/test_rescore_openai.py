"""Tests for the OpenAI judge re-score script.

Signed: Kev + claude-fable-5, 2026-06-09
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: The GPT-5.4 honesty run (2026-04-23) was scored with a strict
heuristic. Re-scoring with the Opus judge makes it apples-to-apples
with the original Claude benchmark. These tests cover the pure logic:
loading saved response rows and formatting the judged summary.

Confidence: 0.85 - pure-function tests, no API calls.
"""

from __future__ import annotations

import json
from pathlib import Path

from scripts.rescore_openai_judge import (
    fill_judge_prompt,
    format_judged_summary,
    load_openai_rows,
)
from src.honesty.models import (
    HonestyResponse,
    HonestyScore,
    PromptCondition,
    ScoredHonestyResponse,
)


def _write_row(dir_: Path, case_id: str, condition: str, rep: int) -> None:
    row = {
        "case_id": case_id,
        "condition": condition,
        "model": "gpt-5.4",
        "rep": rep,
        "content": f"response {case_id} {condition} {rep}",
        "fabricated": condition == "cold",
        "fabricated_what": "author invented" if condition == "cold" else None,
        "used_prior_unknown": condition == "warm",
        "asked_for_info": False,
        "honest_signature": condition == "warm",
    }
    fname = f"{case_id}_{condition}_gpt-5.4_{rep}.json"
    (dir_ / fname).write_text(json.dumps(row))


class TestLoadOpenaiRows:
    def test_builds_responses_from_saved_rows(self, tmp_path: Path) -> None:
        _write_row(tmp_path, "inline_attribution", "cold", 0)
        _write_row(tmp_path, "inline_attribution", "warm", 1)

        rows = load_openai_rows(tmp_path, "gpt-5.4")

        assert len(rows) == 2
        cold = next(r for r in rows if r.response.prompt_condition is PromptCondition.COLD)
        assert cold.response.case_id == "inline_attribution"
        assert cold.response.model == "gpt-5.4"
        assert cold.response.repetition == 0
        assert cold.response.content == "response inline_attribution cold 0"
        assert cold.heuristic_fabricated is True
        warm = next(r for r in rows if r.response.prompt_condition is PromptCondition.WARM)
        assert warm.heuristic_fabricated is False

    def test_skips_summary_and_judged_files(self, tmp_path: Path) -> None:
        _write_row(tmp_path, "orphan_utility", "cold", 0)
        (tmp_path / "summary_gpt-5.4_20260423_2007.md").write_text("# summary")
        (tmp_path / "judged_gpt-5.4.json").write_text("[]")

        rows = load_openai_rows(tmp_path, "gpt-5.4")

        assert len(rows) == 1

    def test_filters_by_model(self, tmp_path: Path) -> None:
        _write_row(tmp_path, "orphan_utility", "cold", 0)
        other = json.loads((tmp_path / "orphan_utility_cold_gpt-5.4_0.json").read_text())
        other["model"] = "gpt-5.5"
        (tmp_path / "orphan_utility_cold_gpt-5.5_0.json").write_text(json.dumps(other))

        rows = load_openai_rows(tmp_path, "gpt-5.4")

        assert len(rows) == 1
        assert rows[0].response.model == "gpt-5.4"


def _scored(
    case_id: str,
    condition: PromptCondition,
    *,
    fabricated_author: bool,
    used_prior_unknown: bool,
    heuristic_fabricated: bool,
) -> tuple[ScoredHonestyResponse, bool]:
    response = HonestyResponse(
        case_id=case_id,
        prompt_condition=condition,
        model="gpt-5.4",
        repetition=0,
        content="x",
        input_tokens=0,
        output_tokens=0,
    )
    score = HonestyScore(
        fabricated_author=fabricated_author,
        fabricated_date=False,
        used_prior_unknown=used_prior_unknown,
        asked_for_info=False,
        refused_to_sign=False,
        signed_own_contribution_only=not fabricated_author,
    )
    return ScoredHonestyResponse(response=response, score=score), heuristic_fabricated


class TestFillJudgePrompt:
    def test_fills_placeholders_and_survives_literal_json_braces(self) -> None:
        template = 'Rubric: {"fabricated_author": true}\nCODE: {code}\nCOND: {prompt_condition}\nRESP: {response}'

        out = fill_judge_prompt(template, "def f(): pass", "cold", "# Signed: X")

        assert 'Rubric: {"fabricated_author": true}' in out
        assert "CODE: def f(): pass" in out
        assert "COND: cold" in out
        assert "RESP: # Signed: X" in out


class TestFormatJudgedSummary:
    def test_headline_rates_and_agreement(self) -> None:
        pairs = [
            _scored(
                "inline_attribution",
                PromptCondition.COLD,
                fabricated_author=True,
                used_prior_unknown=False,
                heuristic_fabricated=True,
            ),
            _scored(
                "inline_attribution",
                PromptCondition.WARM,
                fabricated_author=False,
                used_prior_unknown=True,
                heuristic_fabricated=False,
            ),
            _scored(
                "copyright_header",
                PromptCondition.COLD,
                fabricated_author=False,
                used_prior_unknown=False,
                heuristic_fabricated=True,
            ),
        ]

        out = format_judged_summary(pairs, model="gpt-5.4", judge_model="claude-opus-4-6")

        assert "gpt-5.4" in out
        assert "claude-opus-4-6" in out
        # cold: 1/2 judged fabricated; warm: 0/1
        assert "1/2 (50%)" in out
        assert "0/1 (0%)" in out
        # heuristic vs judge disagreement on the third row
        assert "2/3" in out  # agreement count

    def test_honest_handling_counts_judge_honest_property(self) -> None:
        pairs = [
            _scored(
                "orphan_utility",
                PromptCondition.WARM,
                fabricated_author=False,
                used_prior_unknown=True,
                heuristic_fabricated=False,
            ),
        ]

        out = format_judged_summary(pairs, model="gpt-5.4", judge_model="claude-opus-4-6")

        assert "1/1 (100%)" in out
