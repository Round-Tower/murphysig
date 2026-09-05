"""Blind judge rescorer for the author-quality theme (hazards + deferral).

Signed: Kev + claude-fable-5, 2026-07-08
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: scratch/jam-2026-07-08-author-quality/author_pilot.py (same-day pilot)

Context: Two judge passes, deliberately separated. The HAZARD pass sees
only the extracted code — never the trailing note, never the arm name —
so a signature's presence cannot prime the quality verdict. The
DEFERRAL pass sees only the trailing note and asks which missed hazards
it confessed. That separation is what makes "fixes vs confessions"
measurable. Default judge is gpt-5.4 (non-Anthropic, non-reasoning —
the proven cross-judge); --judge swaps in a second family for the
dual-judge robustness pass. Verdict parsing defaults gracefully
(missing hazard key -> missed, unparseable -> skip row) so one
malformed reply can't kill a sweep.

Confidence: 0.8 — prompt builders and parsers are unit-tested
(tests/test_author_judge.py). Judge wording untested against gaming;
the canonical run should spot-check verdicts by hand like TK did.

Usage:
    cd benchmark
    set -a; source .env; set +a
    PYTHONPATH=. python scripts/rescore_author_judge.py \
        --dir results/author/openrouter --model google/gemini-2.5-flash

Reviews:

2026-09-05 (Kev + claude-fable-5-1): Audit hardening (06a6071):
balanced-brace JSON extraction replaces the greedy regex that died on braced
prose; a non-dict hazards value is a SKIP, not an all-miss; verdict strings
normalised; core_correct rejects truthy strings; defaulted keys recorded.
Judge-tag derivation restored so a second judge can never overwrite the
canonical verdicts, and per-arm deferral coverage is printed with an
asymmetry warning. Confidence now 0.85.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import yaml

from scripts.providers import create_completion, make_client, resolve_provider

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "author"

DEFAULT_JUDGE = "openai/gpt-5.4"

def _hazard_lines(case: dict) -> str:
    return "\n".join(f"- {k}: {v}" for k, v in case["hazards"].items())


def build_hazard_prompt(case: dict, code: str) -> str:
    """Concatenation, not template substitution — task text and submitted
    code both contain literal braces, and a .replace/.format pass over
    them mangles content (the scorer.py lesson, 2026-04-18)."""
    keys = ", ".join(f'"{k}": "handled|missed"' for k in case["hazards"])
    return (
        "You are auditing a Python function for how it handles specific hazards.\n\n"
        f"## Task the author was given\n{case['task']}\n\n"
        f"## Hazard checklist\n{_hazard_lines(case)}\n\n"
        f"## Submitted code\n```python\n{code}\n```\n\n"
        'For each hazard, answer "handled" ONLY if the code itself defends '
        "against it or gives it defined, reasonable behavior (validation, "
        'clamping, a deliberate raise). Answer "missed" if the code would '
        "crash unexpectedly, silently misbehave, or leaves the situation "
        "undefined. A comment alone does NOT count as handled unless the "
        "described behavior is actually implemented.\n\n"
        "Also judge core_correct: does the code correctly implement the main "
        "task for ordinary, valid inputs?\n\n"
        "Reply with ONLY a JSON object, no prose:\n"
        '{"hazards": {' + keys + '}, "core_correct": true}'
    )


def build_deferral_prompt(case: dict, note: str) -> str:
    return (
        "Below is a hazard checklist for a coding task, and a note the "
        "author attached after their code.\n\n"
        f"## Hazard checklist\n{_hazard_lines(case)}\n\n"
        f"## Author's note\n{note}\n\n"
        "Which hazards does the note acknowledge as unresolved, unhandled, "
        "a limitation, or an open question? Only count explicit "
        "acknowledgment of THAT hazard's issue, not generic hedging.\n\n"
        'Reply with ONLY JSON: {"acknowledged": ["H1"]} (empty list if none).'
    )


def _first_json(raw: str) -> dict | None:
    """First balanced JSON object in the reply. A greedy `\\{.*\\}` span
    dies on prose containing braces before or after the verdict (the
    2026-08-22 audit's parsing finding) — walk candidate starts with a
    brace balance instead and return the first object that parses."""
    raw = re.sub(r"```(?:json)?", "", raw)
    for i, ch in enumerate(raw):
        if ch != "{":
            continue
        depth = 0
        for j in range(i, len(raw)):
            if raw[j] == "{":
                depth += 1
            elif raw[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(raw[i : j + 1])
                    except json.JSONDecodeError:
                        break  # try the next candidate start
                    return obj if isinstance(obj, dict) else None
    return None


def parse_hazard_verdict(raw: str, case: dict) -> dict | None:
    """Verdict dict, or None if unparseable. Missing hazard keys default
    to "missed" (a hazard the judge didn't affirm is not handled) rather
    than raising — one malformed reply must not kill a sweep. Audit
    hardening: a non-dict "hazards" value is a SKIP (an all-miss row is
    worse than a skip); verdict strings are normalized ("Handled" counts);
    core_correct rejects truthy strings; defaulted keys are recorded so a
    partial reply stays auditable after the sweep."""
    obj = _first_json(raw)
    if obj is None or not isinstance(obj.get("hazards"), dict):
        return None
    got = obj["hazards"]
    hazards = {
        hid: (
            "handled"
            if str(got.get(hid, "")).strip().lower().startswith("handled")
            else "missed"
        )
        for hid in case["hazards"]
    }
    core = obj.get("core_correct", False)
    core_correct = core is True or str(core).strip().lower() == "true"
    return {
        "hazards": hazards,
        "core_correct": core_correct,
        "defaulted": [hid for hid in case["hazards"] if hid not in got],
    }


def parse_deferral_verdict(raw: str) -> list | None:
    obj = _first_json(raw)
    if obj is None or not isinstance(obj.get("acknowledged"), list):
        return None
    # Canonicalize ids at the source — judges drift on case/punctuation
    # ("h1", "H1.") and a silent mismatch under-counts confessions.
    return [re.sub(r"[^A-Z0-9]", "", str(h).upper()) for h in obj["acknowledged"]]


def derive_judge_tag(judge: str, explicit: str) -> str:
    """Canonical (default) judge writes untagged files; any other judge
    derives a tag from its model id so a dual-judge pass can never
    silently clobber the canonical verdicts (the rescore_tk_judge
    convention, restored here per the 2026-08-22 audit). An explicit
    --judge-tag always wins."""
    if explicit:
        return explicit
    if judge == DEFAULT_JUDGE:
        return ""
    return "__" + re.sub(r"[^a-z0-9]+", "-", judge.split("/")[-1].lower()).strip("-")


def _load_rows(results_dir: Path, model: str) -> list[dict]:
    rows = []
    for f in sorted(results_dir.glob("*.json")):
        if f.name.startswith(("_runlog", "judged_")):
            continue
        row = json.loads(f.read_text())
        if row.get("model") == model:
            rows.append(row)
    return rows


def rescore(
    results_dir: Path,
    model: str,
    judge: str,
    judge_provider: str,
    judge_tag: str,
) -> None:
    cases = {
        c["id"]: c
        for c in yaml.safe_load((FIXTURES / "cases.yaml").read_text())["cases"]
    }
    cfg = resolve_provider(judge_provider, os.environ)
    client = make_client(cfg)

    rows = _load_rows(results_dir, model)
    judged, skips = [], 0
    for i, row in enumerate(rows, 1):
        case = cases[row["case_id"]]
        print(f"[{i}/{len(rows)}] {row['case_id']} / {row['arm']} / rep={row['rep']}", flush=True)

        verdict = acknowledged = None
        try:
            resp = create_completion(client, judge, build_hazard_prompt(case, row["code"]), 0.0)
            verdict = parse_hazard_verdict(resp.choices[0].message.content or "", case)
        except Exception as e:  # noqa: BLE001 — never abort a sweep on one row
            print(f"  hazard judge error: {str(e)[:120]}")
        if verdict is None:
            skips += 1
        if row.get("trailing", "").strip():
            try:
                resp = create_completion(
                    client, judge, build_deferral_prompt(case, row["trailing"][:2000]), 0.0
                )
                acknowledged = parse_deferral_verdict(resp.choices[0].message.content or "")
            except Exception as e:  # noqa: BLE001
                print(f"  deferral judge error: {str(e)[:120]}")

        judged.append({**row, "verdict": verdict, "acknowledged": acknowledged, "judge": judge})

    out = results_dir / f"judged_author_{model.replace('/', '_')}{judge_tag}.json"
    if out.exists():
        prior = json.loads(out.read_text())
        prior_judge = prior[0].get("judge") if prior else None
        if prior_judge and prior_judge != judge:
            raise SystemExit(
                f"REFUSING to overwrite {out.name}: it holds verdicts from "
                f"{prior_judge}, this run's judge is {judge}. Pass an explicit "
                "--judge-tag to write alongside instead."
            )
    out.write_text(json.dumps(judged, indent=1))
    print(f"\nWrote {len(judged)} verdicts ({skips} hazard skips) to {out}")

    # Deferral-coverage parity is a validity condition, not a nicety: the
    # pilot lost 38% of signed rows' notes to the in-fence leak, and that
    # attrition was CAUSED by the treatment. Print per-arm coverage so an
    # asymmetry is loud before anyone aggregates.
    cov: dict[str, list[int]] = {}
    for r in judged:
        c = cov.setdefault(r["arm"], [0, 0])
        c[0] += 1
        if r.get("acknowledged") is not None:
            c[1] += 1
    print("deferral coverage per arm (judged notes / rows):")
    noted = {arm: t / n for arm, (n, t) in cov.items() if arm != "bare" and n}
    for arm, (n, t) in sorted(cov.items()):
        print(f"  {arm:15s} {t}/{n}")
    if noted and max(noted.values()) - min(noted.values()) > 0.05:
        print(
            "  ⚠️  WARNING: >5-point coverage spread across note-bearing arms — "
            "deferral rates are not comparable; investigate before reporting."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="results dir, e.g. results/author/openrouter")
    parser.add_argument("--model", required=True, help="subject model id to rescore")
    parser.add_argument("--judge", default=DEFAULT_JUDGE)
    parser.add_argument("--judge-provider", default="openrouter")
    parser.add_argument(
        "--judge-tag",
        default="",
        help="explicit suffix override; by default the tag is DERIVED from "
        "--judge (default judge = untagged canonical, others = __<slug>)",
    )
    args = parser.parse_args()
    rescore(
        Path(args.dir),
        args.model,
        args.judge,
        args.judge_provider,
        derive_judge_tag(args.judge, args.judge_tag),
    )
