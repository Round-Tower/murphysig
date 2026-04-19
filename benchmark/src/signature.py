"""MurphySig signature generation for benchmark variants.

Signed: Kev + claude-opus-4-7, 2026-04-18
Prior: Kev + claude-opus-4-6, 2026-02-16
Format: MurphySig v0.3.3 (https://murphysig.dev/spec)

Context: Spec-compliant signature generation for benchmark test cases.
Single-author (no AI collaborator) to remove model-family priming
confounds — the benchmark tests whether confidence signals prime
behavior, not whether reviewer-family-matching primes behavior.

Confidence: 0.9 - format now matches spec exactly (single-line Signed:
with date, Format: URL on next line, Context/Confidence structure).

Reviews:

2026-04-18 (Kev + claude-opus-4-7): Aligned output to spec v0.3.3.
Previous generator produced close-cousin format (# MurphySig header,
separate # Date: line, # Ref: instead of Format:). That meant
benchmark wasn't testing the actual spec — it was testing an
approximation. Fixed. Also stripped inline bug labels from cases.yaml
(# BUG:, # VULNERABILITY:, # N+1:) that contaminated detection rates.
"""

from __future__ import annotations

from datetime import date

from src.models import SignatureVariant, TestCase


def apply_signature(case: TestCase, variant: SignatureVariant) -> str:
    """Apply a MurphySig signature variant to a test case's code.

    Args:
        case: The test case containing the code.
        variant: Which signature variant to apply (none/high/low).

    Returns:
        The code with the appropriate signature prepended (or bare code for none).
    """
    if variant == SignatureVariant.NONE:
        return case.code

    confidence = _confidence_for(variant)
    context = _context_for(case, variant)
    today = date.today().isoformat()

    signature_block = (
        f"# Signed: Developer, {today}\n"
        f"# Format: MurphySig v0.3.3 (https://murphysig.dev/spec)\n"
        f"#\n"
        f"# Confidence: {confidence} - {context}\n"
    )

    return f"{signature_block}\n{case.code}"


def _confidence_for(variant: SignatureVariant) -> str:
    """Return the confidence value for a variant."""
    match variant:
        case SignatureVariant.HIGH:
            return "0.9"
        case SignatureVariant.LOW:
            return "0.3"
        case _:
            raise ValueError(f"No confidence for variant: {variant}")


def _context_for(case: TestCase, variant: SignatureVariant) -> str:
    """Return the contextual description for a variant."""
    match variant:
        case SignatureVariant.HIGH:
            return case.high_signature_context
        case SignatureVariant.LOW:
            return case.low_signature_context
        case _:
            raise ValueError(f"No context for variant: {variant}")
