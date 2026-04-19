"""Load honesty fixtures from YAML.

Signed: Kev + claude-opus-4-7, 2026-04-18
Format: MurphySig v0.3.3 (https://murphysig.dev/spec)

Confidence: 0.9 - thin YAML parsing, test-first implementation
"""

from __future__ import annotations

from pathlib import Path

import yaml

from src.honesty.models import HonestyCase, PromptCondition, Temptation


def load_honesty_cases(path: Path) -> list[HonestyCase]:
    """Load honesty test cases from a YAML fixture file."""
    if not path.exists():
        raise FileNotFoundError(f"Honesty cases file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    return [
        HonestyCase(
            id=case["id"],
            name=case["name"],
            code=case["code"],
            temptation=Temptation(case["temptation"]),
        )
        for case in data["cases"]
    ]


def load_honesty_prompts(path: Path) -> dict[PromptCondition, str]:
    """Load the cold/warm prompt templates from the honesty YAML."""
    if not path.exists():
        raise FileNotFoundError(f"Honesty prompts file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    prompts = data["prompts"]
    return {
        PromptCondition.COLD: prompts["cold"],
        PromptCondition.WARM: prompts["warm"],
    }
