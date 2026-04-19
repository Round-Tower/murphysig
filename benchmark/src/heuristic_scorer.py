"""Heuristic scorer — runs locally, no API calls needed.

Approximates the LLM-as-judge by pattern matching on review text.
Less nuanced than Opus scoring, but gives us results immediately.

# Signed: Kev + claude-opus-4-6, 2026-02-16
# Format: MurphySig v0.3.3 (https://murphysig.dev/spec)
#
# Context: Fallback scorer when API limits are hit. Should be validated
#          against LLM judge results when available.
#
# Confidence: 0.6 - heuristic approximation, not as good as LLM judge
"""

from __future__ import annotations

import re

from src.models import Response, Score, ScoredResponse, SignatureVariant


# Bug detection keywords per case
BUG_KEYWORDS: dict[str, list[str]] = {
    "subtle_bug": [
        "off-by-one", "off by one", "page * page_size", "page - 1",
        "start = page * page_size", "first page", "skips", "skip the first",
        "page 1", "starts at page_size", "missing first",
        "(page - 1)", "zero-indexed", "1-indexed",
    ],
    "sql_injection": [
        "sql injection", "injection", "parameterized", "placeholder",
        "f-string", "f\"", "string format", "sanitiz", "prepared statement",
        "Bobby Tables", "user input", "malicious",
    ],
    "clean_code": [
        # For clean code, "bug detected" means correctly identifying it's clean
        "clean", "well-written", "well-structured", "no major issue",
        "no significant issue", "no bug", "correct", "solid",
        "no critical", "well-implemented", "properly",
    ],
    "god_method": [
        "god method", "single responsibility", "separation of concern",
        "too many responsibilities", "mixed concern", "monolithic",
        "coupling", "hard to test", "difficult to test",
        "refactor", "break up", "split", "extract",
    ],
    "n_plus_one": [
        "n+1", "n + 1", "query in a loop", "individual query",
        "batch", "bulk", "join", "eager load", "prefetch",
        "each article", "for each", "quadratic",
    ],
}

# Signature awareness keywords
SIG_KEYWORDS = [
    "murphysig", "signature", "confidence", "0.9", "0.3",
    "battle-tested", "battle tested", "production-proven",
    "sketchy", "untested", "first attempt", "provenance",
    "signed", "the comment", "the header", "metadata",
]


def _count_suggestions(text: str) -> int:
    """Count distinct actionable suggestions in review text."""
    count = 0
    # Numbered items (1. 2. 3. etc.)
    numbered = re.findall(r"^\s*\d+[\.\)]\s+", text, re.MULTILINE)
    # Bullet points with actionable language
    bullets = re.findall(r"^\s*[-*]\s+", text, re.MULTILINE)
    # "Consider", "Should", "Could", "Recommend" patterns
    actionable = re.findall(
        r"\b(consider|should|could|recommend|suggest|instead of|replace|use|add|implement|wrap|move)\b",
        text,
        re.IGNORECASE,
    )
    # Use the larger of numbered/bullet counts, plus unique actionable verbs
    list_count = max(len(numbered), len(bullets))
    # Cap actionable to avoid overcounting
    action_count = min(len(set(a.lower() for a in actionable)), 8)
    count = max(list_count, action_count)
    return max(1, min(count, 15))  # Floor at 1, cap at 15


def _estimate_scrutiny(text: str, has_bug: bool, bug_detected: bool) -> int:
    """Estimate scrutiny level from review text characteristics."""
    length = len(text)
    sections = text.count("##") + text.count("**")

    if length < 500:
        base = 2
    elif length < 1000:
        base = 3
    elif length < 1500:
        base = 4
    else:
        base = 5

    # Bonus for finding the bug
    if has_bug and bug_detected:
        base = min(base + 1, 5)
    # Penalty for missing the bug
    elif has_bug and not bug_detected:
        base = max(base - 1, 1)

    return base


def score_response_heuristic(
    response: Response,
    has_bug: bool,
) -> ScoredResponse:
    """Score a response using heuristic pattern matching.

    Args:
        response: The model's review response.
        has_bug: Whether the test case has a known bug.

    Returns:
        ScoredResponse with heuristic scores.
    """
    text = response.content.lower()
    case_id = response.case_id

    # Bug detection
    keywords = BUG_KEYWORDS.get(case_id, [])
    bug_detected = any(kw.lower() in text for kw in keywords)

    # Signature awareness
    sig_aware = False
    if response.signature_type != SignatureVariant.NONE:
        sig_aware = any(kw.lower() in text for kw in SIG_KEYWORDS)

    # Suggestion count
    suggestion_count = _count_suggestions(response.content)

    # Scrutiny level
    scrutiny = _estimate_scrutiny(response.content, has_bug, bug_detected)

    # Confidence alignment
    if response.signature_type == SignatureVariant.NONE:
        conf_align = 3  # Baseline
    elif response.signature_type == SignatureVariant.HIGH:
        # High confidence: lower scrutiny = better alignment
        conf_align = 5 - scrutiny + 3  # Inverse relationship
        conf_align = max(1, min(conf_align, 5))
    else:  # LOW
        # Low confidence: higher scrutiny = better alignment
        conf_align = scrutiny - 1
        conf_align = max(1, min(conf_align, 5))

    score = Score(
        bug_detected=bug_detected,
        scrutiny_level=scrutiny,
        signature_awareness=sig_aware,
        confidence_alignment=conf_align,
        suggestion_count=suggestion_count,
    )

    return ScoredResponse(response=response, score=score)
