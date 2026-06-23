"""Strip chain-of-thought reasoning traces from model output before scoring.

Signed: Kev + claude-opus-4-8, 2026-06-16
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: Reasoning models (Qwen, DeepSeek-R1, ...) emit chain-of-thought
in <think>...</think> inline in the completion, and OpenAI-compatible
local servers (mlx_lm.server) return it in message.content. Scoring that
blob corrupts the honesty signal — a model that *deliberates* about
fabricating "John" in its reasoning and then emits a clean signature would
be judged as if it fabricated. Split the reasoning off; the caller keeps
both (raw for the record, answer for the judge).

Confidence: 0.8 — pure string surgery, unit-tested across closed,
multiple, unclosed (truncated), and tag-variant cases.
Open: models using non-tag delimiters (e.g. Harmony channels) aren't
covered; extend _TAGS or add a parser when such a model enters the matrix.
"""

from __future__ import annotations

import re

# Tag names that wrap chain-of-thought. Add as new reasoning dialects appear.
_TAGS = ("think", "thinking")
_TAG_ALT = "|".join(_TAGS)

# Complete <tag>...</tag> blocks, non-greedy, across newlines.
_BLOCK = re.compile(rf"<({_TAG_ALT})\s*>(.*?)</\1\s*>", re.DOTALL | re.IGNORECASE)
# A dangling opener with no matching close — reasoning truncated mid-thought.
_DANGLING = re.compile(rf"<(?:{_TAG_ALT})\s*>(.*)\Z", re.DOTALL | re.IGNORECASE)


def strip_reasoning(text: str) -> tuple[str, str]:
    """Split ``text`` into ``(answer, reasoning)``.

    ``answer`` is the text with every reasoning block removed and surrounding
    whitespace trimmed. ``reasoning`` is the concatenated chain-of-thought
    (empty string when there is none).
    """
    reasoning_parts: list[str] = []

    def _collect(match: re.Match) -> str:
        reasoning_parts.append(match.group(2))
        return ""

    answer = _BLOCK.sub(_collect, text)

    dangling = _DANGLING.search(answer)
    if dangling:
        reasoning_parts.append(dangling.group(1))
        answer = answer[: dangling.start()]

    reasoning = "\n".join(part.strip() for part in reasoning_parts).strip()
    return answer.strip(), reasoning
