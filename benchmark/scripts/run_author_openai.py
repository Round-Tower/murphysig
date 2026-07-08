"""Author-quality (write-side) runner for OpenAI-compatible providers.

Signed: Kev + claude-fable-5, 2026-07-08
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: scratch/jam-2026-07-08-author-quality/author_pilot.py (same-day pilot)

Context: SPEC-v0.5 experiment #1 — does knowing you'll sign make the
AUTHOR's work better? The pilot found the signing frame alone trades
fixes for confessions (sign-reflect = -0.18 hazard-handled; but 67% of
misses confessed in Open vs reflect's 41%), and that an action clause
("resolve what you can before you sign") recovers full reflection-level
quality (0.85 vs 0.84). This promoted runner adds the pilot's missing
control: reflect_harder, length-matched to sign_revise, so the decisive
comparisons are parity-gated at BOTH tiers. Arm-comparative and
within-model, like TK — robust to capability gaps across families.

Confidence: 0.8 — prompt construction, parity gates, and extraction are
unit-tested (tests/test_run_author_openai.py); provider plumbing is
shared (scripts/providers.py) and already covered. The fixtures have
NOT had an adversarial audit yet — do that before a canonical run.
Open: n>=5, dual judges, fixture audit; then archive via the
archive_run pattern when the first canonical run lands.

Usage:
    cd benchmark
    set -a; source .env; set +a
    PYTHONPATH=. python scripts/run_author_openai.py --provider openrouter \
        --model google/gemini-2.5-flash --reps 5
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

from scripts.providers import create_completion, make_client, resolve_provider

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "author"
RESULTS_ROOT = ROOT / "results" / "author"

ARMS = ("bare", "reflect", "sign", "sign_revise", "reflect_harder")


def load_author_fixtures() -> tuple[list[dict], dict[str, str]]:
    """Return (cases, arm_templates) from fixtures/author/."""
    cases = yaml.safe_load((FIXTURES / "cases.yaml").read_text())["cases"]
    arms = yaml.safe_load((FIXTURES / "arms.yaml").read_text())["arms"]
    return cases, arms


def build_task_prompt(template: str, task: str) -> str:
    """Fill the arm template's {task} slot. str.replace, never .format —
    task text contains literal braces (dict literals)."""
    return template.replace("{task}", task)


def instruction_overhead_words(arms: dict[str, str], name: str) -> int:
    """Instruction words an arm adds beyond the bare arm. The parity
    gates compare these so no arm wins by sheer instruction length."""
    return len(arms[name].split()) - len(arms["bare"].split())


def extract_code(text: str) -> str:
    """First fenced code block; whole text if the model skipped the fence."""
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    return (m.group(1) if m else text).strip()


def extract_trailing(text: str) -> str:
    """Everything after the first fenced code block — the reflection note
    or signature block. This is what the deferral judge reads."""
    parts = re.split(r"```(?:python)?\s*\n.*?```", text, maxsplit=1, flags=re.DOTALL)
    return parts[1].strip() if len(parts) > 1 else ""


def resolve_arms(arg: str) -> tuple[str, ...]:
    return ARMS if arg == "all" else (arg,)


def run(
    provider_name: str,
    model: str,
    reps: int,
    temperature: float,
    arms_to_run: tuple[str, ...] = ARMS,
) -> None:
    cfg = resolve_provider(provider_name, os.environ)
    client = make_client(cfg)

    cases, arm_templates = load_author_fixtures()
    output_dir = RESULTS_ROOT / provider_name
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    total = len(cases) * len(arms_to_run) * reps
    n = 0

    for case in cases:
        for arm in arms_to_run:
            prompt = build_task_prompt(arm_templates[arm], case["task"])
            for rep in range(reps):
                n += 1
                print(f"[{n}/{total}] {case['id']} / {arm} / rep={rep}", flush=True)

                resp = create_completion(client, model, prompt, temperature)
                content = resp.choices[0].message.content or ""

                row = {
                    "case_id": case["id"],
                    "arm": arm,
                    "model": model,
                    "provider": provider_name,
                    "rep": rep,
                    "temperature": temperature,
                    "content": content,
                    "code": extract_code(content),
                    "trailing": extract_trailing(content),
                }
                rows.append(row)

                fname = f"{case['id']}_{arm}_{model.replace('/', '_')}_{rep}.json"
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
    print("Rows are unscored — replay through the blind judge:")
    print(
        f"  PYTHONPATH=. python scripts/rescore_author_judge.py "
        f"--dir results/author/{provider_name} --model {model}"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--model", required=True, help="provider's model id")
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument(
        "--arm",
        choices=("all", *ARMS),
        default="all",
        help="run a single arm instead of all five",
    )
    args = parser.parse_args()
    run(
        args.provider,
        args.model,
        args.reps,
        args.temperature,
        arms_to_run=resolve_arms(args.arm),
    )
