"""Domain models for MurphySig benchmark.

# Signed: Kev + claude-opus-4-6, 2026-02-16
# Format: MurphySig v0.3.3 (https://murphysig.dev/spec)
#
# Context: Core types for the benchmark. Intentionally minimal.
#
# Confidence: 0.85 - clean domain model, well-tested, frozen dataclasses
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SignatureVariant(Enum):
    """The three signature conditions under test."""

    NONE = "none"
    HIGH = "high"
    LOW = "low"


@dataclass(frozen=True)
class TestCase:
    """A single code snippet to be reviewed, with metadata."""

    id: str
    name: str
    code: str
    expected_issues: list[str]
    has_bug: bool
    high_signature_context: str
    low_signature_context: str


@dataclass(frozen=True)
class Variant:
    """A test case with a specific signature applied."""

    case_id: str
    signature_type: SignatureVariant
    full_code: str


@dataclass(frozen=True)
class Response:
    """Raw response from a model under test."""

    case_id: str
    signature_type: SignatureVariant
    model: str
    repetition: int
    content: str
    input_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class Score:
    """Structured score from the LLM-as-judge."""

    bug_detected: bool
    scrutiny_level: int  # 1-5
    signature_awareness: bool
    confidence_alignment: int  # 1-5
    suggestion_count: int  # >= 0

    def __post_init__(self):
        if not 1 <= self.scrutiny_level <= 5:
            raise ValueError(
                f"scrutiny_level must be 1-5, got {self.scrutiny_level}"
            )
        if not 1 <= self.confidence_alignment <= 5:
            raise ValueError(
                f"confidence_alignment must be 1-5, got {self.confidence_alignment}"
            )
        if self.suggestion_count < 0:
            raise ValueError(
                f"suggestion_count must be >= 0, got {self.suggestion_count}"
            )


@dataclass(frozen=True)
class ScoredResponse:
    """A response paired with its judge score."""

    response: Response
    score: Score


@dataclass
class RunConfig:
    """Configuration for a benchmark run."""

    models: list[str] = field(
        default_factory=lambda: [
            "claude-haiku-4-5-20251001",
            "claude-sonnet-4-5-20250929",
        ]
    )
    repetitions: int = 3
    temperature: float = 0.0
    delay_seconds: float = 0.5
    judge_model: str = "claude-opus-4-6"
