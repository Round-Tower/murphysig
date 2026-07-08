"""Tests for the author-quality (write-side) runner.

Signed: Kev + claude-fable-5, 2026-07-08
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: Promotion of scratch/jam-2026-07-08-author-quality. The
experiment is arm-comparative — the same model does the same task under
five instruction frames and the headline is the within-model delta —
so the prompt-construction and length-parity gates are the parts worth
pinning. Length parity is the rig gate: if an arm's instruction text is
much longer, "arm X wins" could be an instruction-length artifact.
These cover the pure logic; no API calls.

Confidence: 0.85
"""

from __future__ import annotations

from scripts.run_author_openai import (
    ARMS,
    build_task_prompt,
    extract_code,
    extract_trailing,
    instruction_overhead_words,
    load_author_fixtures,
)


class TestFixtures:
    def test_loads_cases_with_hazards(self):
        cases, arms = load_author_fixtures()
        assert len(cases) >= 3
        for c in cases:
            assert c["id"]
            assert c["task"]
            assert len(c["hazards"]) >= 3
            for hid, desc in c["hazards"].items():
                assert hid.startswith("H") and desc

    def test_all_five_arms_present(self):
        _cases, arms = load_author_fixtures()
        assert set(arms) == set(ARMS) == {
            "bare",
            "reflect",
            "sign",
            "sign_revise",
            "reflect_harder",
        }

    def test_every_arm_has_task_slot(self):
        _cases, arms = load_author_fixtures()
        for name, template in arms.items():
            assert "{task}" in template, name


class TestBuildTaskPrompt:
    def test_fills_task_slot(self):
        prompt = build_task_prompt("Before.\n\n{task}\n\nAfter.", "write parse(x)")
        assert "write parse(x)" in prompt
        assert prompt.startswith("Before.") and prompt.endswith("After.")

    def test_uses_replace_not_format(self):
        # Tasks may contain literal braces (dict literals in the task
        # text) — .format would raise KeyError. The repo has been bitten
        # by this before (scorer.py, 2026-04-18).
        prompt = build_task_prompt("{task}", 'return {"items": []}')
        assert '{"items": []}' in prompt


class TestLengthParityGates:
    """The rig gates. Each decisive comparison must be between arms of
    near-equal instruction length, or the result is confounded. Committed
    so the experiment can't silently drift unfair."""

    TOLERANCE = 0.20

    def _overhead(self):
        _cases, arms = load_author_fixtures()
        return {name: instruction_overhead_words(arms, name) for name in ARMS}

    def test_sign_matches_reflect(self):
        o = self._overhead()
        ratio = o["sign"] / o["reflect"]
        assert abs(1 - ratio) <= self.TOLERANCE, o

    def test_sign_revise_matches_reflect_harder(self):
        o = self._overhead()
        ratio = o["sign_revise"] / o["reflect_harder"]
        assert abs(1 - ratio) <= self.TOLERANCE, o

    def test_action_arms_are_longer_than_plain_arms(self):
        # sanity: the two tiers are distinct — the action tier carries
        # more instruction, which is exactly why it needs its own control.
        o = self._overhead()
        assert min(o["sign_revise"], o["reflect_harder"]) > max(o["sign"], o["reflect"])


class TestExtraction:
    def test_extracts_python_block(self):
        text = "intro\n```python\ndef f():\n    return 1\n```\nOutro note."
        assert extract_code(text) == "def f():\n    return 1"

    def test_bare_fence_also_accepted(self):
        text = "```\nx = 1\n```"
        assert extract_code(text) == "x = 1"

    def test_no_fence_falls_back_to_whole_text(self):
        assert extract_code("just code, no fence") == "just code, no fence"

    def test_trailing_is_text_after_code_block(self):
        text = "```python\nx = 1\n```\n\nConfidence: 0.9"
        assert extract_trailing(text) == "Confidence: 0.9"

    def test_trailing_empty_when_nothing_follows(self):
        assert extract_trailing("```python\nx = 1\n```") == ""
