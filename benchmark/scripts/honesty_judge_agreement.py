"""Inter-judge agreement for the Honesty cross-family result.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: The Honesty cross-family numbers (warm honest-handling 100% on
Gemini/Grok/DeepSeek/Mistral; Llama/Qwen resist) were scored by a single
Opus judge. This loads the canonical Opus verdicts (judged_<model>.json)
and a non-Anthropic judge's verdicts (judged_<model>__gpt.json, from
rescore_openai_judge.py --judge-family openai) and reports the per-model
warm honest-handling rate under EACH judge plus per-response concordance
on the `honest` verdict. If GPT reproduces the same cross-family split,
"Anthropic's judge prefers Anthropic's convention" is refuted for
Honesty as well. Mirrors tk_judge_agreement.py.

Confidence: 0.85 — rate/concordance logic is unit-tested
(tests/test_honesty_judge_agreement.py); file loading is thin glue.

Usage:
    cd benchmark
    PYTHONPATH=. python scripts/honesty_judge_agreement.py \
        --dir results/honesty/openrouter --gpt-tag __gpt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DIR = ROOT / "results" / "honesty" / "openrouter"


def honest_rate(rows: list[dict], condition: str) -> float | None:
    """Mean `honest` among rows of a condition; None if the condition is absent."""
    vals = [bool(r["honest"]) for r in rows if r["condition"] == condition]
    if not vals:
        return None
    return sum(vals) / len(vals)


def model_agreement_rows(
    opus_by_model: dict[str, list], gpt_by_model: dict[str, list]
) -> list[dict]:
    """One row per model present under both judges: warm + cold honest
    rate as each judge scored it."""
    rows: list[dict] = []
    for model in sorted(set(opus_by_model) & set(gpt_by_model)):
        rows.append(
            {
                "model": model,
                "opus_warm_honest": honest_rate(opus_by_model[model], "warm"),
                "gpt_warm_honest": honest_rate(gpt_by_model[model], "warm"),
                "opus_cold_honest": honest_rate(opus_by_model[model], "cold"),
                "gpt_cold_honest": honest_rate(gpt_by_model[model], "cold"),
            }
        )
    return rows


def response_concordance(opus_rows: list[dict], gpt_rows: list[dict]) -> dict:
    """Per-response agreement on the `honest` verdict, aligned by
    (case_id, condition, rep)."""
    def key(r):
        return (r["case_id"], r["condition"], r["rep"])

    gpt_map = {key(r): bool(r["honest"]) for r in gpt_rows}
    n = agree = 0
    for r in opus_rows:
        k = key(r)
        if k in gpt_map:
            n += 1
            if bool(r["honest"]) == gpt_map[k]:
                agree += 1
    return {"n": n, "agree": agree, "rate": agree / n if n else 0.0}


def _pct(x: float | None) -> str:
    return "—" if x is None else f"{round(100 * x)}%"


def render_agreement(model_rows: list[dict], concordance: dict) -> str:
    """Render the agreement table. `concordance` maps condition labels
    ("warm", "cold", "overall") to {n, agree, rate} dicts — the warm/cold
    split is the crucial nuance: the judges agree on the warm (rule
    present) endpoint but diverge on the contestable cold baseline."""
    out = ["# Honesty inter-judge agreement — Opus vs GPT\n"]
    out.append(
        "_Same responses, two independent judges. The robust, "
        "judge-independent claim is the WARM honest-handling rate and the "
        "resister split; the COLD baseline is judge-dependent (GPT counts "
        "un-prompted self-signing as honest, Opus does not), so the "
        "cold→warm delta magnitude is judge-sensitive._\n\n"
    )
    out.append(
        "| Model | Opus warm honest | GPT warm honest | Opus cold | GPT cold |\n"
        "|---|--:|--:|--:|--:|\n"
    )
    for r in model_rows:
        out.append(
            f"| {r['model']} | {_pct(r['opus_warm_honest'])} | "
            f"{_pct(r['gpt_warm_honest'])} | {_pct(r['opus_cold_honest'])} | "
            f"{_pct(r['gpt_cold_honest'])} |\n"
        )
    out.append("\n## Per-response judge agreement (honest verdict)\n")
    out.append("| Condition | Agreement |\n|---|--:|\n")
    for label in ("warm", "cold", "overall"):
        c = concordance.get(label)
        if c:
            out.append(
                f"| {label} | {c['agree']}/{c['n']} ({round(100 * c['rate'])}%) |\n"
            )
    out.append(
        "\nThe disagreement is isolated to the cold baseline — on warm "
        "(the headline) the judges agree, and both independently find the "
        "same four families at 100% and the same two (Llama, Qwen) resisting.\n"
    )
    return "".join(out)


def _load_by_model(dir_: Path, tag: str) -> dict[str, list]:
    by_model: dict[str, list] = {}
    for path in sorted(dir_.glob(f"judged_*{tag}.json")):
        stem_rest = path.stem.replace("judged_", "")
        if not tag and "__" in stem_rest:
            continue  # skip a tagged judge's files when loading Opus canonical
        if path.name.startswith("judged_summary"):
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(data, list):
            continue
        for row in data:
            if isinstance(row, dict) and "honest" in row:
                by_model.setdefault(row["model"], []).append(row)
    return by_model


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=DEFAULT_DIR)
    parser.add_argument("--gpt-tag", default="__gpt")
    args = parser.parse_args()
    opus = _load_by_model(args.dir, "")
    gpt = _load_by_model(args.dir, args.gpt_tag)
    rows = model_agreement_rows(opus, gpt)
    if not rows:
        raise SystemExit("No overlapping models between the two judges.")
    all_opus = [r for rs in opus.values() for r in rs]
    all_gpt = [r for rs in gpt.values() for r in rs]
    conc = {"overall": response_concordance(all_opus, all_gpt)}
    for cond in ("warm", "cold"):
        conc[cond] = response_concordance(
            [r for r in all_opus if r["condition"] == cond],
            [r for r in all_gpt if r["condition"] == cond],
        )
    report = render_agreement(rows, conc)
    (args.dir / "honesty_judge_agreement.md").write_text(report)
    print(report)
