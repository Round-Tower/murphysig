"""Load test cases and prompts from fixture files.

# Signed: Kev + claude-opus-4-6, 2026-02-16
# Format: MurphySig v0.3.3 (https://murphysig.dev/spec)
#
# Confidence: 0.85 - straightforward YAML parsing, well-tested
"""

from __future__ import annotations

from pathlib import Path

import yaml

from src.models import TestCase


def load_cases(path: Path) -> list[TestCase]:
    """Load test cases from a YAML fixture file.

    Args:
        path: Path to the YAML file containing test cases.

    Returns:
        List of TestCase dataclass instances.

    Raises:
        FileNotFoundError: If the YAML file doesn't exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Cases file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    return [
        TestCase(
            id=case["id"],
            name=case["name"],
            code=case["code"],
            expected_issues=case.get("expected_issues", []),
            has_bug=case["has_bug"],
            high_signature_context=case["high_signature_context"],
            low_signature_context=case["low_signature_context"],
        )
        for case in data["cases"]
    ]


def load_prompt(path: Path) -> str:
    """Load a prompt template from a text file.

    Args:
        path: Path to the prompt template file.

    Returns:
        The prompt template string.

    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")

    return path.read_text()
