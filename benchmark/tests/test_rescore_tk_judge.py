"""Tests for the TK judge re-score path.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: Mirrors rescore_openai_judge.py for the TK theme — replays
saved cross-family briefings through the canonical Opus judge so the
coverage/hedging numbers are comparable to the Claude-only TK run.
These cover row loading + judge-prompt filling; the async judge loop
is thin glue over the production parse_tk_judgment.

Confidence: 0.85
"""

from __future__ import annotations

import json

from scripts.rescore_tk_judge import (
    fill_tk_judge_prompt,
    load_tk_rows,
)


def _write_row(dir_, case_id, variant, model, rep, content="briefing text"):
    row = {
        "case_id": case_id,
        "variant": variant,
        "model": model,
        "provider": "openrouter",
        "rep": rep,
        "content": content,
    }
    fname = f"{case_id}_{variant}_{model.replace('/', '_')}_{rep}.json"
    (dir_ / fname).write_text(json.dumps(row))


class TestLoadTkRows:
    def test_loads_matching_model_only(self, tmp_path):
        _write_row(tmp_path, "pagination", "signed", "google/gemini-2.5", 0)
        _write_row(tmp_path, "pagination", "unsigned", "google/gemini-2.5", 0)
        _write_row(tmp_path, "pagination", "signed", "x-ai/grok-4", 0)
        rows = load_tk_rows(tmp_path, "google/gemini-2.5")
        assert len(rows) == 2
        assert all(r.model == "google/gemini-2.5" for r in rows)

    def test_skips_non_row_json(self, tmp_path):
        _write_row(tmp_path, "pagination", "signed", "m", 0)
        (tmp_path / "_runlog_m_x.json").write_text(json.dumps({"model": "m", "rows": 1}))
        (tmp_path / "judged_m.json").write_text(json.dumps([{"foo": "bar"}]))
        rows = load_tk_rows(tmp_path, "m")
        assert len(rows) == 1
        assert rows[0].case_id == "pagination"

    def test_sorted_by_case_variant_rep(self, tmp_path):
        _write_row(tmp_path, "pagination", "signed", "m", 1)
        _write_row(tmp_path, "pagination", "signed", "m", 0)
        _write_row(tmp_path, "pagination", "unsigned", "m", 0)
        rows = load_tk_rows(tmp_path, "m")
        assert [(r.case_id, r.variant, r.rep) for r in rows] == [
            ("pagination", "signed", 0),
            ("pagination", "signed", 1),
            ("pagination", "unsigned", 0),
        ]

    def test_variant_filter_judges_one_arm_only(self, tmp_path):
        # The prose-only add: judge just the prose rows without re-scoring
        # (and paying for) the already-judged signed/unsigned arms.
        _write_row(tmp_path, "pagination", "signed", "m", 0)
        _write_row(tmp_path, "pagination", "unsigned", "m", 0)
        _write_row(tmp_path, "pagination", "prose", "m", 0)
        rows = load_tk_rows(tmp_path, "m", variant="prose")
        assert len(rows) == 1
        assert rows[0].variant == "prose"

    def test_no_variant_filter_loads_all(self, tmp_path):
        _write_row(tmp_path, "pagination", "signed", "m", 0)
        _write_row(tmp_path, "pagination", "prose", "m", 0)
        assert len(load_tk_rows(tmp_path, "m")) == 2


class TestFillTkJudgePrompt:
    def test_fills_all_four_slots(self):
        template = (
            "CODE:\n{code}\nGT:\n{ground_truth}\n"
            "VARIANT: {signature_variant}\nBRIEFING:\n{briefing}"
        )
        out = fill_tk_judge_prompt(
            template,
            code="def f(): pass",
            ground_truth="it does X",
            variant="signed",
            briefing="this code does X",
        )
        assert "{code}" not in out
        assert "{ground_truth}" not in out
        assert "{signature_variant}" not in out
        assert "{briefing}" not in out
        assert "def f(): pass" in out
        assert "it does X" in out
        assert "VARIANT: signed" in out
        assert "this code does X" in out

    def test_uses_replace_not_format(self):
        # Briefing/code may contain literal braces — .format would explode.
        template = "B: {briefing}"
        out = fill_tk_judge_prompt(
            template, code="", ground_truth="", variant="unsigned",
            briefing="dict is {a: 1}",
        )
        assert "dict is {a: 1}" in out
