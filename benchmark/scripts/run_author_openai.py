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

Reviews:

2026-09-05 (Kev + claude-fable-5-1): Two post-signature changes.
split_signature strips a MurphySig block left inside the code fence (46% of
pilot sign-arm rows) and reroutes it to the trailing note with a
sig_in_fence flag, so the hazard judge is blind again (06a6071).
SUBJECT_MAX_TOKENS raised to 8192 and finish_reason recorded after 147/600
rows truncated on reasoning-by-default models (c0d3327). The Open above is
closed: n>=5, dual judges and the fixture audit all landed in the archived
2026-08-22 canonical run. Confidence now 0.85.
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

# Subject budget. Reasoning-by-default models (gemini-3.5-flash and
# qwen3.7-plus via OpenRouter, discovered 2026-08-22 when 147/600 rows
# came back finish_reason=length) spend hidden reasoning from the same
# budget — 2048 starved the visible answer to nothing on the strongest
# arms, exactly the truncation shape the fixture audit warned about.
SUBJECT_MAX_TOKENS = 8192


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


_FENCE = r"```[A-Za-z0-9_+-]*[ \t]*\n"

# Markers that identify a signature/reflection block. Checked ONLY against
# non-executable tail regions (comments / a trailing bare string), never
# against executable code, so `opts = {"Open": 1}` can't false-positive.
_SIG_MARKERS = re.compile(
    r"(?im)murphysig|^\s*#?\s*(signed|confidence|open|context|prior)\s*:"
)


def extract_code(text: str) -> str:
    """First fenced code block; whole text if the model skipped the fence."""
    m = re.search(_FENCE + r"(.*?)```", text, re.DOTALL)
    return (m.group(1) if m else text).strip()


def extract_trailing(text: str) -> str:
    """Everything after the first fenced code block — the reflection note
    or signature block. This is what the deferral judge reads."""
    parts = re.split(_FENCE + r".*?```", text, maxsplit=1, flags=re.DOTALL)
    return parts[1].strip() if len(parts) > 1 else ""


def split_signature(code: str) -> tuple[str, str]:
    """Strip a signature/reflection block a model left INSIDE the fence.

    The 2026-08-22 adversarial audit found ~46% of pilot sign-arm rows
    carried the MurphySig block inside the code fence — un-blinding the
    hazard judge in one direction and starving the deferral judge in the
    other. Two shapes are handled, both strictly non-executable tails:
    a trailing comment/blank run, and a trailing bare triple-quoted
    string. A tail is only stripped when it contains signature markers,
    so ordinary trailing comments survive. Returns (code, sig_text)."""
    for _ in range(2):  # a docstring block may sit under a comment block
        lines = code.rstrip().split("\n")
        i = len(lines)
        while i > 0 and (not lines[i - 1].strip() or lines[i - 1].lstrip().startswith("#")):
            i -= 1
        if i < len(lines):
            tail = "\n".join(lines[i:])
            if _SIG_MARKERS.search(tail):
                code = "\n".join(lines[:i]).rstrip()
                return _finish_split(code, tail)
        m = re.search(r'(?s)\n(("""|\'\'\')(?!.*\2.*\S).*?\2)\s*$', code.rstrip())
        if m and _SIG_MARKERS.search(m.group(1)):
            code = code.rstrip()[: m.start()].rstrip()
            return _finish_split(code, m.group(1))
        break
    return code, ""


def _finish_split(code: str, sig: str) -> tuple[str, str]:
    """Recurse once so comment-over-docstring stacks fully strip."""
    inner_code, inner_sig = split_signature(code)
    combined = (inner_sig + "\n" + sig).strip() if inner_sig else sig.strip()
    return inner_code, combined


def extract_fields(content: str) -> dict:
    """The judged fields for one response: fence-extracted code with any
    in-fence signature stripped and rerouted to trailing, plus the
    sig_in_fence flag the analysis records."""
    code, in_fence_sig = split_signature(extract_code(content))
    trailing = extract_trailing(content)
    if in_fence_sig:
        trailing = (trailing + "\n\n" + in_fence_sig).strip() if trailing else in_fence_sig
    return {"code": code, "trailing": trailing, "sig_in_fence": bool(in_fence_sig)}


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

                resp = create_completion(
                    client, model, prompt, temperature, max_tokens=SUBJECT_MAX_TOKENS
                )
                content = resp.choices[0].message.content or ""
                finish = getattr(resp.choices[0], "finish_reason", None)
                if finish != "stop":
                    print(f"  ⚠️ finish_reason={finish} — row may be truncated")

                row = {
                    "case_id": case["id"],
                    "arm": arm,
                    "model": model,
                    "provider": provider_name,
                    "rep": rep,
                    "temperature": temperature,
                    "content": content,
                    "finish_reason": getattr(resp.choices[0], "finish_reason", None),
                    **extract_fields(content),
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
