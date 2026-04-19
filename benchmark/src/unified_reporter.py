"""Unified four-theme report generation.

Signed: Kev + claude-opus-4-7, 2026-04-19
Format: MurphySig v0.4 (https://murphysig.dev/spec)

Context: Aggregates the three testable-theme sub-benchmarks (ICL, TK,
Honesty) into a single markdown report. Reflection is explicitly
labeled as non-empirical (cultural practice, not a hypothesis).

Confidence: 0.8 - straightforward composition; narrative section is
formulaic but honest.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from src.honesty.reporter import generate_honesty_report
from src.honesty.runner import load_scored_honesty
from src.reporter import generate_report as generate_icl_report
from src.runner import load_scored_results
from src.tk.reporter import generate_tk_report
from src.tk.runner import load_scored_briefings


def generate_unified_report(base_dir: Path) -> str:
    """Generate a unified report combining all three sub-benchmarks."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    results_dir = base_dir / "results"

    # Load each theme's scored data if available
    icl_block = "_(no ICL data)_"
    tk_block = "_(no TK data)_"
    honesty_block = "_(no Honesty data)_"

    icl_path = results_dir / "scored_results.json"
    if icl_path.exists():
        icl_scored = load_scored_results(results_dir)
        icl_block = generate_icl_report(icl_scored)

    tk_results_dir = results_dir / "tk"
    if (tk_results_dir / "scored_briefings.json").exists():
        tk_scored = load_scored_briefings(tk_results_dir)
        tk_block = generate_tk_report(tk_scored)

    honesty_results_dir = results_dir / "honesty"
    if (honesty_results_dir / "scored_honesty.json").exists():
        honesty_scored = load_scored_honesty(honesty_results_dir)
        honesty_block = generate_honesty_report(honesty_scored)

    return f"""# MurphySig Benchmark — Unified Four-Theme Report

Generated: {now}

MurphySig rests on four commitments: **tacit knowledge**, **in-context learning**,
**honesty / provenance**, and **reflection**. Three are empirically testable.
Reflection is a cultural practice, not a hypothesis, so it's outside the benchmark's scope.

This report combines results from all three testable sub-benchmarks.

---

## THEME 1 — Tacit Knowledge

Does a MurphySig signature help an AI *brief* unfamiliar code? (Not reviewing — reading and summarising.)

{tk_block}

---

## THEME 2 — In-Context Learning

Does a signature measurably change how an AI *reviews* code?

{icl_block}

---

## THEME 3 — Honesty / Provenance

When asked to sign unsigned code, do AIs fabricate provenance, or handle it honestly?

{honesty_block}

---

## THEME 4 — Reflection

Not empirical. Reflection is the creator-acknowledgement act: writing a `Reflections:`
entry after code has lived in production long enough to reveal its shape. Whether
humans do this, and whether it improves the code or the craft, depends on adoption
data — not benchmark data. Intentionally out of scope.

---

*MurphySig Benchmark — Unified Four-Theme Report — https://murphysig.dev/benchmark*
"""
