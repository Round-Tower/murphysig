"""Load TK fixtures from YAML.

Signed: Kev + claude-opus-4-7, 2026-04-18
Format: MurphySig v0.3.3 (https://murphysig.dev/spec)

Confidence: 0.9 - thin YAML parsing; signature fields nested under each case
"""

from __future__ import annotations

from pathlib import Path

import yaml

from src.tk.models import TkCase, TkSignature


def load_tk_cases(path: Path) -> list[TkCase]:
    """Load TK test cases (code + ground_truth + signature) from YAML."""
    if not path.exists():
        raise FileNotFoundError(f"TK cases file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    return [_parse_case(raw) for raw in data["cases"]]


def _parse_case(raw: dict) -> TkCase:
    sig_raw = raw["signature"]
    signature = TkSignature(
        context=sig_raw["context"],
        confidence=float(sig_raw["confidence"]),
        open=sig_raw["open"],
        heuristic=sig_raw.get("heuristic"),
    )
    return TkCase(
        id=raw["id"],
        name=raw["name"],
        code=raw["code"],
        ground_truth=raw["ground_truth"],
        signature=signature,
    )
