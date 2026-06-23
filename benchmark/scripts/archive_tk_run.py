"""Archive a finished TK run into a committed runs/ directory.

Signed: Kev + claude-opus-4-8, 2026-06-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)

Context: Mirrors archive_run.py for the TK theme. The flat
results/tk/<provider>/ dir is scratch (overwrites on re-run); this
snapshots a finished run into results/tk/runs/<run-id>/ — raw
briefings, judged verdicts, the per-question decomposition, a rendered
report, and a manifest recording the run's own provenance (git SHA,
fixture hash, judge, model ids, reps, temperature, the intent/code
axis headline). It appends one row PER MODEL to runs/index.jsonl — the
within-model signature uplift is TK's headline unit, so that's the
longitudinal ledger you chart over time. A provenance benchmark keeps
its own provenance.

Confidence: 0.8 — manifest/ledger logic is unit-tested
(tests/test_archive_tk_run.py); file collection is thin glob+copy glue;
run_id_for is reused (theme-agnostic) from archive_run.

Usage:
    cd benchmark
    PYTHONPATH=. python scripts/archive_tk_run.py \
        --label tk-cross-family-6 --reps 5 --temperature 0.7 \
        --judge-model anthropic/claude-opus-4.6 \
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
from scripts.rescore_tk_perquestion import (
    aggregate_perquestion,
    axis_summary,
)
from scripts.tk_cross_family_report import aggregate_tk, delta_table

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures" / "tk"
RESULTS = ROOT / "results" / "tk"
RUNS = RESULTS / "runs"
SIGNED_BY = "Kev + claude-opus-4-8"
FIXTURE_FILES = (
    "cases.yaml",
    "briefing_prompt.txt",
    "judge_prompt.txt",
    "perquestion_judge_prompt.txt",
)


def build_tk_manifest(
    *,
    run_id: str,
    date: str,
    git_sha: str,
    fixture_hash: str,
    judge_model: str,
    reps: int,
    temperature: float,
    models: list[dict],
    axis_delta: dict,
) -> dict:
    return {
        "run_id": run_id,
        "theme": "tk",
        "date": date,
        "git_sha": git_sha,
        "fixture_hash": fixture_hash,
        "judge_model": judge_model,
        "reps": reps,
        "temperature": temperature,
        "model_count": len(models),
        "total_responses": sum(m["n"] for m in models),
        "models": models,
        "axis_delta": axis_delta,
        "signed": SIGNED_BY,
        "format": "MurphySig v0.4 (https://murphysig.dev/spec)",
    }


def tk_ledger_rows(run_id: str, date: str, agg: dict) -> list[dict]:
    """One row per model — the within-model signature uplift."""
    rows: list[dict] = []
    for model in sorted(agg):
        u = agg[model].get("unsigned")
        s = agg[model].get("signed")
        if not u or not s:
            continue
        rows.append(
            {
                "run_id": run_id,
                "date": date,
                "model": model,
                "n_unsigned": u["n"],
                "n_signed": s["n"],
                "coverage_unsigned": round(u["coverage"], 4),
                "coverage_signed": round(s["coverage"], 4),
                "delta_coverage": round(s["coverage"] - u["coverage"], 4),
                "delta_hedging": round(s["hedging"] - u["hedging"], 4),
                "referenced_rate": round(s["referenced_signature"] / s["n"], 4)
                if s["n"]
                else 0.0,
            }
        )
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
        judged = working / f"judged_tk_{slug}.json"
        if judged.exists():
            shutil.copy2(judged, run_dir / "verdicts" / judged.name)
            verdict_rows.extend(json.loads(judged.read_text()))
        model_meta.append({"provider": provider, "id": model, "n": len(raw_files)})

    # Per-question decomposition (pooled) → the intent/code axis headline.
    axes = axis_summary(aggregate_perquestion(
        json.loads((working / "perquestion_judged.json").read_text())
    )) if (working / "perquestion_judged.json").exists() else {}
    axis_delta = {k: round(v["delta"], 4) for k, v in axes.items()}
    for extra in ("perquestion_judged.json", "perquestion_report.md"):
        src = working / extra
        if src.exists():
            shutil.copy2(src, run_dir / extra)

    agg = aggregate_tk(verdict_rows)
    manifest = build_tk_manifest(
        run_id=run_id,
        date=today,
        git_sha=_git_sha(),
        fixture_hash=_fixture_hash(),
        judge_model=judge_model,
        reps=reps,
        temperature=temperature,
        models=model_meta,
        axis_delta=axis_delta,
    )
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    report = (
        f"# {run_id} — judge-scored cross-family tacit knowledge\n\n"
        f"_Judge: {judge_model}. {manifest['total_responses']} briefings, "
        f"{manifest['model_count']} models, reps={reps}, temp={temperature}. "
        f"git {manifest['git_sha']}, fixtures {manifest['fixture_hash']}._\n\n"
        + delta_table(agg)
    )
    if axis_delta:
        report += (
            f"\n## Mechanism (per-question)\n\nIntent-axis uplift "
            f"{axis_delta.get('intent', 0):+.2f} vs code-axis "
            f"{axis_delta.get('code', 0):+.2f} — see perquestion_report.md.\n"
        )
    (run_dir / "report.md").write_text(report)

    RUNS.mkdir(parents=True, exist_ok=True)
    with (RUNS / "index.jsonl").open("a") as f:
        for row in tk_ledger_rows(run_id, today, agg):
            f.write(json.dumps(row) + "\n")

    return run_dir


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--label", required=True)
    parser.add_argument("--provider", default="openrouter")
    parser.add_argument("--model", action="append", dest="models", required=True)
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--judge-model", default="anthropic/claude-opus-4.6")
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
