"""Standalone Tacit-Knowledge (TK) briefing runner for OpenAI-compatible providers.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: Cross-family validation of the TK finding (signatures help an
AI brief unfamiliar code — coverage +0.12, less hedging, on Claude).
TK is the strongest MurphySig claim and the cleanest to generalise:
it's DELTA-based — the *same* model briefs each case twice (unsigned
vs signed) and the headline is the within-model difference — so it's
robust to raw capability gaps across families (a weak model that
hedges a lot still shows the signed-vs-unsigned delta). Mirrors
run_honesty_openai.py: same provider matrix (scripts/providers.py),
reads fixtures/tk/cases.yaml + briefing_prompt.txt, saves raw rows to
results/tk/<provider>/. Scoring is judge-only (no heuristic) — replay
through rescore_tk_judge.py with the Opus judge.

Confidence: 0.8 — signature-rendering + variant logic are unit-tested
(tests/test_run_tk_openai.py); the provider plumbing is shared and
already covered by tests/test_provider_runner.py.

Usage:
    cd benchmark
    # keys live in benchmark/.env — never paste them into a chat
    set -a; source .env; set +a
    PYTHONPATH=. python scripts/run_tk_openai.py --provider openrouter \
        --model google/gemini-2.5-flash --reps 10
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import date as date_cls
from datetime import datetime, timezone
from pathlib import Path

import yaml

from scripts.providers import create_completion, make_client, resolve_provider

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "tk"
RESULTS_ROOT = ROOT / "results" / "tk"

VARIANTS = ("unsigned", "signed", "prose")


def resolve_variants(arg: str) -> tuple[str, ...]:
    """Map a --variant choice to the variants to run. 'all' runs every
    arm; a single name isolates it (e.g. the prose-only add)."""
    if arg == "all":
        return VARIANTS
    return (arg,)


def load_tk_fixtures() -> tuple[list[dict], str]:
    """Return (cases, briefing_template) from fixtures/tk/."""
    cases = yaml.safe_load((FIXTURES / "cases.yaml").read_text())["cases"]
    template = (FIXTURES / "briefing_prompt.txt").read_text()
    return cases, template


def format_signature_block(sig: dict, today: str) -> str:
    """Render a TK case's signature as a MurphySig comment block.

    Author is a generic "Developer" on purpose: TK measures the
    briefing uplift from the signature's *content* (Context / Confidence
    / Open / Heuristic), so the author name must not bait the
    provenance-honesty failure modes the Honesty theme studies.
    """
    lines = [
        f"# Signed: Developer, {today}",
        "# Format: MurphySig v0.4 (https://murphysig.dev/spec)",
        "#",
        f"# Context: {sig['context']}",
        "#",
        f"# Confidence: {sig['confidence']} - {sig['context']}",
    ]
    if sig.get("heuristic"):
        lines.append(f"# Heuristic: {sig['heuristic']}")
    lines.append(f"# Open: {sig['open']}")
    return "\n".join(lines) + "\n"


def format_prose_block(prose: str) -> str:
    """Render the prose control as an unstructured comment block.

    The structure-vs-content control: the same facts as the signature,
    with no field labels, no numeric confidence, no MurphySig framing —
    just a plain developer comment. Comparing the signed variant against
    this isolates whether the signature's *structure* earns its keep.
    """
    lines = [
        f"# {ln}" if ln.strip() else "#"
        for ln in prose.rstrip("\n").split("\n")
    ]
    return "\n".join(lines) + "\n"


def apply_variant(case: dict, variant: str, today: str) -> str:
    """Return the code to show the model for this variant."""
    if variant == "unsigned":
        return case["code"]
    if variant == "prose":
        return f"{format_prose_block(case['prose'])}\n{case['code']}"
    block = format_signature_block(case["signature"], today=today)
    return f"{block}\n{case['code']}"


def build_briefing_prompt(template: str, code: str) -> str:
    """Fill the briefing template's {code} slot. str.replace, never
    .format — the code contains literal braces."""
    return template.replace("{code}", code)


def run(
    provider_name: str,
    model: str,
    reps: int,
    temperature: float,
    variants: tuple[str, ...] = VARIANTS,
) -> None:
    cfg = resolve_provider(provider_name, os.environ)
    client = make_client(cfg)

    cases, template = load_tk_fixtures()
    today = date_cls.today().isoformat()
    output_dir = RESULTS_ROOT / provider_name
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    total = len(cases) * len(variants) * reps
    n = 0

    for case in cases:
        for variant in variants:
            code = apply_variant(case, variant, today=today)
            prompt = build_briefing_prompt(template, code)
            for rep in range(reps):
                n += 1
                print(f"[{n}/{total}] {case['id']} / {variant} / rep={rep}", flush=True)

                resp = create_completion(client, model, prompt, temperature)
                content = resp.choices[0].message.content or ""

                row = {
                    "case_id": case["id"],
                    "variant": variant,
                    "model": model,
                    "provider": provider_name,
                    "rep": rep,
                    "content": content,
                }
                rows.append(row)

                fname = f"{case['id']}_{variant}_{model.replace('/', '_')}_{rep}.json"
                (output_dir / fname).write_text(json.dumps(row, indent=2))

    stamp = f"{datetime.now(timezone.utc):%Y%m%d_%H%M}"
    manifest = output_dir / f"_runlog_{model.replace('/', '_')}_{stamp}.json"
    manifest.write_text(
        json.dumps(
            {"model": model, "provider": provider_name, "reps": reps, "rows": len(rows)},
            indent=2,
        )
    )
    print(f"\nWrote {len(rows)} rows to {output_dir}")
    print("Briefings are unscored — replay through the Opus judge:")
    print(
        f"  PYTHONPATH=. python scripts/rescore_tk_judge.py "
        f"--dir results/tk/{provider_name} --model {model}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--model", required=True, help="provider's model id")
    parser.add_argument("--reps", type=int, default=10)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument(
        "--variant",
        choices=("all", *VARIANTS),
        default="all",
        help="run a single arm (e.g. 'prose') instead of all three",
    )
    args = parser.parse_args()
    run(
        args.provider,
        args.model,
        args.reps,
        args.temperature,
        variants=resolve_variants(args.variant),
    )
