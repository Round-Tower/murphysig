"""Archive a finished benchmark run into a committed runs/ directory.

Signed: Kev + claude-fable-5, 2026-06-22
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: The runner/judge write loose files into a flat working dir
(results/honesty/<provider>/) that overwrite on re-run — fine as
scratch, useless for tracking over time. This snapshots a finished
run into results/honesty/runs/<run-id>/ with raw responses, judged
verdicts, a rendered report, and a manifest recording the run's own
provenance (git SHA, fixture hash, judge, exact model ids, n). It
also appends per-model rows to runs/index.jsonl — the longitudinal
ledger you can chart honest-handling-over-time from. A benchmark
about provenance should keep its own.

Confidence: 0.8 - pure manifest/ledger logic is unit-tested; the file
collection is thin glob+copy glue.

Usage:
    cd benchmark
    PYTHONPATH=. python scripts/archive_run.py \
        --label cross-family-6 --reps 10 --judge-model claude-opus-4-6 \
        --provider openrouter \
        --model google/gemini-3.5-flash --model x-ai/grok-4.3 ...
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import date as date_cls
from pathlib import Path

from scripts.cross_family_report import aggregate_rows, render_table

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "honesty"
RESULTS = ROOT / "results" / "honesty"
RUNS = RESULTS / "runs"
SIGNED_BY = "Kev + claude-fable-5"


def run_id_for(date_str: str, label: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return f"{date_str}_{slug}"


def build_manifest(
    *,
    run_id: str,
    theme: str,
    date: str,
    git_sha: str,
    fixture_hash: str,
    judge_model: str,
    reps: int,
    models: list[dict],
) -> dict:
    return {
        "run_id": run_id,
        "theme": theme,
        "date": date,
        "git_sha": git_sha,
        "fixture_hash": fixture_hash,
        "judge_model": judge_model,
        "reps": reps,
        "model_count": len(models),
        "total_responses": sum(m["n"] for m in models),
        "models": models,
        "signed": SIGNED_BY,
        "format": "MurphySig v0.4 (https://murphysig.dev/spec)",
    }


def ledger_rows(run_id: str, date: str, agg: dict) -> list[dict]:
    """One row per (model, condition) for the longitudinal ledger."""
    rows: list[dict] = []
    for model in sorted(agg):
        for cond, b in agg[model].items():
            if not b["n"]:
                continue
            rows.append(
                {
                    "run_id": run_id,
                    "date": date,
                    "model": model,
                    "condition": cond,
                    "n": b["n"],
                    "fabrication": b["fabrication"],
                    "honest": b["honest"],
                    "prior_unknown": b["prior_unknown"],
                    "fabrication_rate": round(b["fabrication"] / b["n"], 4),
                    "honest_rate": round(b["honest"] / b["n"], 4),
                }
            )
    return rows


def _fixture_hash() -> str:
    h = hashlib.sha256()
    for name in ("cases.yaml", "judge_prompt.txt"):
        h.update((FIXTURES / name).read_bytes())
    return f"sha256:{h.hexdigest()[:16]}"


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:  # noqa: BLE001
        return "unknown"


def _model_files(working: Path, model: str) -> tuple[list[Path], Path | None]:
    """Raw response JSONs + judged verdict JSON for one model."""
    slug = model.replace("/", "_")
    raw = sorted(
        p
        for p in working.glob(f"*_{slug}_*.json")
        if not p.name.startswith(("judged_", "summary_"))
    )
    judged = working / f"judged_{slug}.json"
    return raw, (judged if judged.exists() else None)


def archive(
    *, label: str, provider: str, models: list[str], reps: int, judge_model: str, theme: str
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
        raw_files, judged = _model_files(working, model)
        for p in raw_files:
            shutil.copy2(p, run_dir / "raw" / p.name)
        if judged:
            shutil.copy2(judged, run_dir / "verdicts" / judged.name)
            verdict_rows.extend(json.loads(judged.read_text()))
        model_meta.append({"provider": provider, "id": model, "n": len(raw_files)})

    agg = aggregate_rows(verdict_rows)
    manifest = build_manifest(
        run_id=run_id,
        theme=theme,
        date=today,
        git_sha=_git_sha(),
        fixture_hash=_fixture_hash(),
        judge_model=judge_model,
        reps=reps,
        models=model_meta,
    )
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    report = (
        f"# {run_id} — judge-scored cross-family honesty\n\n"
        f"_Judge: {judge_model}. {manifest['total_responses']} responses, "
        f"{manifest['model_count']} models, reps={reps}. git {manifest['git_sha']}, "
        f"fixtures {manifest['fixture_hash']}._\n\n"
        + render_table(agg)
    )
    (run_dir / "report.md").write_text(report)

    RUNS.mkdir(parents=True, exist_ok=True)
    with (RUNS / "index.jsonl").open("a") as f:
        for row in ledger_rows(run_id, today, agg):
            f.write(json.dumps(row) + "\n")

    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--model", action="append", dest="models", required=True)
    parser.add_argument("--reps", type=int, default=10)
    parser.add_argument("--judge-model", default="claude-opus-4-6")
    parser.add_argument("--theme", default="honesty")
    args = parser.parse_args()
    run_dir = archive(
        label=args.label,
        provider=args.provider,
        models=args.models,
        reps=args.reps,
        judge_model=args.judge_model,
        theme=args.theme,
    )
    print(f"Archived run -> {run_dir}")
    print((run_dir / "report.md").read_text())


if __name__ == "__main__":
    main()
