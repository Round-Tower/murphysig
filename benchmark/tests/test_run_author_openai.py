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


# --- 2026-08-22 adversarial-audit additions (the in-fence signature leak) ---

from scripts.run_author_openai import extract_fields, split_signature  # noqa: E402

SIG_COMMENT_OUTPUT = '''```python
def parse_duration(s):
    return 0

# MurphySig
# Signed: Developer, 2026-08-22
# Confidence: 0.95
# Open:
# - Should we raise for invalid formats instead of returning 0?
```'''

SIG_DOCSTRING_OUTPUT = '''```python
def parse_duration(s):
    return 0

"""
Signed: Developer, 2026-08-22
Confidence: 0.9
Open: order of units is not enforced (e.g. '30m1h' is valid).
"""
```'''

SIG_AFTER_FENCE_OUTPUT = '''```python
def parse_duration(s):
    return 0
```

Signed: Developer, 2026-08-22
Open: none.'''

SIG_MARKER_RE = r"(?im)murphysig|^\s*#?\s*(signed|confidence|open|context|prior)\s*:"

import re as _re  # noqa: E402


class TestSignatureSplitRigGate:
    """The audit's blocking finding: models put the signature INSIDE the
    fence ~46% of the time in the pilot, un-blinding the hazard judge in
    one direction only. These gates make that leak structurally
    impossible to reintroduce."""

    def test_comment_style_sig_stripped_from_code_and_routed_to_trailing(self):
        f = extract_fields(SIG_COMMENT_OUTPUT)
        assert "def parse_duration" in f["code"]
        assert not _re.search(SIG_MARKER_RE, f["code"])
        assert "Should we raise" in f["trailing"]
        assert f["sig_in_fence"] is True

    def test_docstring_style_sig_stripped_from_code_and_routed_to_trailing(self):
        f = extract_fields(SIG_DOCSTRING_OUTPUT)
        assert "def parse_duration" in f["code"]
        assert not _re.search(SIG_MARKER_RE, f["code"])
        assert "order of units" in f["trailing"]
        assert f["sig_in_fence"] is True

    def test_after_fence_sig_untouched_and_not_flagged(self):
        f = extract_fields(SIG_AFTER_FENCE_OUTPUT)
        assert f["code"].strip().endswith("return 0")
        assert "Signed: Developer" in f["trailing"]
        assert f["sig_in_fence"] is False

    def test_ordinary_trailing_comment_without_markers_is_kept_in_code(self):
        out = "```python\ndef f():\n    return 1\n# handles the empty case\n```"
        f = extract_fields(out)
        assert "# handles the empty case" in f["code"]
        assert f["sig_in_fence"] is False

    def test_marker_words_inside_executable_code_never_stripped(self):
        out = '```python\nopts = {"Open": 1}\ndef f(context):\n    return context\n```'
        f = extract_fields(out)
        assert '"Open"' in f["code"] and "def f(context)" in f["code"]
        assert f["sig_in_fence"] is False

    def test_in_fence_sig_appends_to_existing_trailing_note(self):
        out = SIG_COMMENT_OUTPUT + "\n\nA short note after the fence."
        f = extract_fields(out)
        assert "A short note" in f["trailing"]
        assert "Should we raise" in f["trailing"]

    def test_rig_gate_no_signature_markers_reach_the_hazard_judge(self):
        for sample in (SIG_COMMENT_OUTPUT, SIG_DOCSTRING_OUTPUT, SIG_AFTER_FENCE_OUTPUT):
            assert not _re.search(SIG_MARKER_RE, extract_fields(sample)["code"])

    def test_split_signature_is_conservative_on_pure_code(self):
        code = "def f():\n    return 1"
        stripped, sig = split_signature(code)
        assert stripped == code and sig == ""


class TestFenceVariants:
    def test_py_and_python3_fences_accepted(self):
        for lang in ("py", "python3"):
            out = f"```{lang}\ndef f():\n    return 1\n```\nnote"
            f = extract_fields(out)
            assert f["code"] == "def f():\n    return 1"
            assert f["trailing"] == "note"
