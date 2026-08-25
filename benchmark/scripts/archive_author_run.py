"""Archive a finished author-quality run into a committed runs/ directory.

Signed: Kev + claude-fable-5, 2026-08-22
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: scripts/archive_tk_run.py (same shape, author theme)

Context: The flat results/author/<provider>/ dir is scratch (overwrites
on re-run); this snapshots a finished run into results/author/runs/
<run-id>/ — raw generations, judged verdicts (all judge tags, so a
dual-judge pass is banked alongside the default), a rendered report,
and a manifest recording the run's own provenance (git SHA, fixture
hash, judge, model ids, reps, temperature, and the two parity-gated
headline deltas). Ledger unit is one row PER MODEL carrying the
per-arm hazard rates and the decisive deltas — those deltas are the
claim, so they are what runs/index.jsonl charts over time. A
provenance benchmark keeps its own provenance.

Confidence: 0.85 — manifest/ledger logic is unit-tested
(tests/test_archive_author_run.py); file collection is thin glob+copy
glue reusing the theme-agnostic run_id_for.

Usage:
    cd benchmark
    PYTHONPATH=. python scripts/archive_author_run.py \
        --label author-cross-family-6 --reps 5 --temperature 0.7 \
        --judge-model openai/gpt-5.4 \
        --model google/gemini-3.5-flash --model x-ai/grok-4.3 ...
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import date as date_cls
from pathlib import Path

from scripts.archive_run import run_id_for  # theme-agnostic, already tested
from scripts.author_report import confession_rates, hazard_rates, render_report

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "author"
RESULTS = ROOT / "results" / "author"
RUNS = RESULTS / "runs"
SIGNED_BY = "Kev + claude-fable-5"
FIXTURE_FILES = ("cases.yaml", "arms.yaml")
DECISIVE = (("sign", "reflect"), ("sign_revise", "reflect_harder"))


def build_author_manifest(
    *,
    run_id: str,
    date: str,
    git_sha: str,
    fixture_hash: str,
    judge_model: str,
    reps: int,
    temperature: float,
    models: list[dict],
    headline: dict,
) -> dict:
    return {
        "run_id": run_id,
        "theme": "author",
        "date": date,
        "git_sha": git_sha,
        "fixture_hash": fixture_hash,
        "judge_model": judge_model,
        "reps": reps,
        "temperature": temperature,
        "model_count": len(models),
        "total_responses": sum(m["n"] for m in models),
        "models": models,
        "headline": headline,
        "signed": SIGNED_BY,
        "format": "MurphySig v0.4 (https://murphysig.dev/spec)",
    }


def author_ledger_rows(run_id: str, date: str, rates: dict) -> list[dict]:
    """One row per model — the per-arm rates + parity-gated deltas.
    A model missing either arm of a decisive pair is skipped (a partial
    row would chart a delta that was never measured)."""
    models = sorted({m for m, _a in rates})
    rows: list[dict] = []
    for model in models:
        by = {a: rates.get((model, a)) for a in
              ("bare", "reflect", "sign", "sign_revise", "reflect_harder")}
        if any(by[a] is None or by[b] is None for a, b in DECISIVE):
            continue
        row: dict = {"run_id": run_id, "date": date, "model": model}
        for arm, r in by.items():
            if r is not None:
                row[f"hazard_{arm}"] = round(r["hazard_rate"], 4)
        for a, b in DECISIVE:
            row[f"delta_{a}_{b}"] = round(
                by[a]["hazard_rate"] - by[b]["hazard_rate"], 4
            )
        row["n_per_arm"] = by["sign"]["n"]
        rows.append(row)
    return rows


def _fixture_hash() -> str:
    h = hashlib.sha256()
    for name in FIXTURE_FILES:
        h.update((FIXTURES / name).read_bytes())
    return f"sha256:{h.hexdigest()[:16]}"


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def _raw_files(working: Path, model: str) -> list[Path]:
    slug = model.replace("/", "_")
    return sorted(
        p
        for p in working.glob(f"*_{slug}_*.json")
        if not p.name.startswith(("judged_", "_runlog_"))
    )


def archive(
    *, label: str, provider: str, models: list[str], reps: int,
    temperature: float, judge_model: str,
) -> Path:
    working = RESULTS / provider
    today = date_cls.today().isoformat()
    run_id = run_id_for(today, label)
    run_dir = RUNS / run_id
    (run_dir / "raw").mkdir(parents=True, exist_ok=True)
    (run_dir / "verdicts").mkdir(parents=True, exist_ok=True)

    verdict_rows: list[dict] = []
    model_meta: list[dict] = []
    for model in models:
        slug = model.replace("/", "_")
        raw_files = _raw_files(working, model)
        for p in raw_files:
            shutil.copy2(p, run_dir / "raw" / p.name)
        # All judge tags for this model — the default judge's verdicts
        # plus any dual-judge pass (e.g. __opus) get banked together.
        for judged in sorted(working.glob(f"judged_author_{slug}*.json")):
            shutil.copy2(judged, run_dir / "verdicts" / judged.name)
            if judged.name == f"judged_author_{slug}.json":
                verdict_rows.extend(json.loads(judged.read_text()))
        model_meta.append({"provider": provider, "id": model, "n": len(raw_files)})

    rates = hazard_rates(verdict_rows)
    conf = confession_rates(verdict_rows)
    ledger = author_ledger_rows(run_id, today, rates)
    headline = {
        f"delta_{a}_{b}": round(
            sum(r[f"delta_{a}_{b}"] for r in ledger) / len(ledger), 4
        ) if ledger else None
        for a, b in DECISIVE
    }
    headline["confession_rate"] = {
        arm: round(c["rate"], 4) for arm, c in sorted(conf.items())
    }

    manifest = build_author_manifest(
        run_id=run_id,
        date=today,
        git_sha=_git_sha(),
        fixture_hash=_fixture_hash(),
        judge_model=judge_model,
        reps=reps,
        temperature=temperature,
        models=model_meta,
        headline=headline,
    )
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    report = (
        f"# {run_id} — author-quality (write-side) cross-family\n\n"
        f"_Judge: {judge_model} (code-only, blind to arm). "
        f"{manifest['total_responses']} generations, "
        f"{manifest['model_count']} models, reps={reps}, temp={temperature}. "
        f"git {manifest['git_sha']}, fixtures {manifest['fixture_hash']}._\n\n"
        + render_report(verdict_rows)
    )
    (run_dir / "report.md").write_text(report)

    RUNS.mkdir(parents=True, exist_ok=True)
    with (RUNS / "index.jsonl").open("a") as f:
        for row in ledger:
            f.write(json.dumps(row) + "\n")

    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--model", action="append", dest="models", required=True)
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--judge-model", default="openai/gpt-5.4")
    args = parser.parse_args()
    run_dir = archive(
        label=args.label,
        provider=args.provider,
        models=args.models,
        reps=args.reps,
        temperature=args.temperature,
        judge_model=args.judge_model,
    )
    print(f"Archived run -> {run_dir}")
    print((run_dir / "report.md").read_text())


if __name__ == "__main__":
    main()
