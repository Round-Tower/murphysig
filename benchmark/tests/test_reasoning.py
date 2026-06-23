"""Tests for reasoning-trace stripping (src/reasoning.py).

Why this exists: reasoning models (Qwen, DeepSeek-R1, ...) emit
chain-of-thought in <think>...</think> inline in the completion. Scoring
that blob corrupts the honesty signal — a model that *deliberates* about
fabricating "John" and then doesn't must not be judged as if it did.
"""

from src.reasoning import strip_reasoning


class TestStripReasoning:
    def test_no_reasoning_returns_text_unchanged(self):
        answer, reasoning = strip_reasoning("Signed: claude\nPrior: Unknown")
        assert answer == "Signed: claude\nPrior: Unknown"
        assert reasoning == ""

    def test_single_block_split_off_before_answer(self):
        raw = "<think>Maybe sign as John?</think>\nSigned: claude-opus-4-8\nPrior: Unknown"
        answer, reasoning = strip_reasoning(raw)
        assert answer == "Signed: claude-opus-4-8\nPrior: Unknown"
        assert "John" not in answer
        assert "John" in reasoning

    def test_multiple_blocks_all_captured(self):
        answer, reasoning = strip_reasoning("<think>one</think>A<think>two</think>B")
        assert answer == "AB"
        assert "one" in reasoning and "two" in reasoning

    def test_unclosed_block_treated_as_reasoning(self):
        # Reasoning model truncated before closing the tag — everything
        # after the dangling opener is chain-of-thought, not answer.
        answer, reasoning = strip_reasoning("Signed: claude<think>truncated thought…")
        assert answer == "Signed: claude"
        assert "truncated thought" in reasoning

    def test_thinking_tag_variant_supported(self):
        answer, reasoning = strip_reasoning("<thinking>x</thinking>Y")
        assert answer == "Y"
        assert "x" in reasoning

    def test_case_insensitive(self):
        answer, _ = strip_reasoning("<THINK>noise</THINK>clean")
        assert answer == "clean"
