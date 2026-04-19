"""Domain models for the Tacit Knowledge (TK) sub-benchmark.

Signed: Kev + claude-opus-4-7, 2026-04-18
Format: MurphySig v0.3.3 (https://murphysig.dev/spec)

Confidence: 0.85 - frozen dataclasses; coverage/accuracy are floats 0-1
(judge output); hedging is ordinal 1-5; questions_back is count.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BriefingVariant(Enum):
    """Whether the code is shown to the AI with or without a signature."""

    UNSIGNED = "unsigned"
    SIGNED = "signed"


@dataclass(frozen=True)
class TkSignature:
    """The MurphySig fields applied to a TK case's signed variant."""

    context: str
    confidence: float
    open: str
    heuristic: str | None = None


@dataclass(frozen=True)
class TkCase:
    """A TK test case: code + gold-standard briefing + signature."""

    id: str
    name: str
    code: str
    ground_truth: str
    signature: TkSignature


@dataclass(frozen=True)
class Briefing:
    """Raw briefing response from a model under test."""

    case_id: str
    variant: BriefingVariant
    model: str
    repetition: int
    content: str
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class BriefingScore:
    """Judge-assigned scores for a briefing vs. ground truth."""

    coverage: float  # 0.0-1.0
    accuracy: float  # 0.0-1.0
    hedging_density: int  # 1-5
    questions_back_count: int  # >= 0
    referenced_signature: bool

    def __post_init__(self):
        if not 0.0 <= self.coverage <= 1.0:
            raise ValueError(f"coverage must be 0.0-1.0, got {self.coverage}")
        if not 0.0 <= self.accuracy <= 1.0:
            raise ValueError(f"accuracy must be 0.0-1.0, got {self.accuracy}")
        if not 1 <= self.hedging_density <= 5:
            raise ValueError(
                f"hedging_density must be 1-5, got {self.hedging_density}"
            )
        if self.questions_back_count < 0:
            raise ValueError(
                f"questions_back_count must be >= 0, got "
                f"{self.questions_back_count}"
            )


@dataclass(frozen=True)
class ScoredBriefing:
    """A briefing paired with its judge score."""

    briefing: Briefing
    score: BriefingScore
