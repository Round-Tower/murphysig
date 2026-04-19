"""CLI entry point for MurphySig benchmark.

Signed: Kev + claude-opus-4-6, 2026-02-16
Format: MurphySig v0.4 (https://murphysig.dev/spec)

Context: Thin CLI layer, delegates to runner/scorer/reporter for each
of the three testable themes (ICL, TK, Honesty).

Confidence: 0.8 - thin CLI layer; theme dispatch is straightforward.

Reviews:

2026-04-19 (Kev + claude-opus-4-7): Added tk-* and honesty-* command
families for the four-theme benchmark suite. Flat namespace (no nested
subparsers) for simpler invocation. Each theme writes to its own
results/ subdir (results/tk/, results/honesty/); ICL remains at
results/ root for backward compatibility.

Usage:
    python -m src run                  # ICL: review benchmark (API calls)
    python -m src score                # ICL: score saved responses
    python -m src report               # ICL: generate report

    python -m src tk-run               # TK: briefing benchmark
    python -m src tk-score             # TK: score briefings
    python -m src tk-report            # TK: generate TK report

    python -m src honesty-run          # Honesty: fabrication benchmark
    python -m src honesty-score        # Honesty: score signing responses
    python -m src honesty-report       # Honesty: generate honesty report

    python -m src all                  # Run all three end-to-end (~$12)
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

from src.models import RunConfig
from src.reporter import generate_report
from src.runner import (
    load_responses,
    load_scored_results,
    run_benchmark,
    score_all,
)


def _base_dir() -> Path:
    return Path(__file__).parent.parent


def _fixtures_dir() -> Path:
    return _base_dir() / "fixtures"


def _results_dir() -> Path:
    d = _base_dir() / "results"
    d.mkdir(exist_ok=True)
    return d


def _theme_fixtures_dir(theme: str) -> Path:
    return _base_dir() / "fixtures" / theme


def _theme_results_dir(theme: str) -> Path:
    d = _base_dir() / "results" / theme
    d.mkdir(parents=True, exist_ok=True)
    return d


# ---------- ICL (original) ----------


async def cmd_run(args: argparse.Namespace) -> list:
    """Execute the ICL benchmark run."""
    config = RunConfig(
        models=args.models.split(",") if args.models else RunConfig().models,
        repetitions=args.repetitions,
    )

    print("\n=== MurphySig ICL Benchmark ===")
    print(f"Models: {', '.join(config.models)}")
    print(f"Repetitions: {config.repetitions}")
    print(f"Temperature: {config.temperature}")
    print(
        f"Total calls: {5 * 3 * len(config.models) * config.repetitions}\n"
    )

    results_dir = _results_dir()
    responses = await run_benchmark(config, _fixtures_dir(), results_dir)

    print(f"\n{len(responses)} responses saved to {results_dir}/")

    if args.score:
        scored = await cmd_score_inner(responses, config)
        if args.report:
            cmd_report_inner(scored)

    return responses


async def cmd_score(args: argparse.Namespace) -> list:
    """Score previously saved ICL responses."""
    responses = load_responses(_results_dir())
    if not responses:
        print("No responses found in results/. Run the benchmark first.")
        sys.exit(1)

    config = RunConfig()
    return await cmd_score_inner(responses, config)


async def cmd_score_inner(responses, config):
    print(f"\n=== Scoring {len(responses)} responses ===\n")
    scored = await score_all(
        responses, _fixtures_dir(), _results_dir(), config
    )
    print(f"\n{len(scored)} responses scored and saved.")
    return scored


def cmd_report(args: argparse.Namespace) -> None:
    """Generate ICL report."""
    results_dir = _results_dir()
    scored = load_scored_results(results_dir)
    if not scored:
        print("No scored results found. Run scoring first.")
        sys.exit(1)
    cmd_report_inner(scored)


def cmd_report_inner(scored) -> None:
    report = generate_report(scored)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_path = _results_dir() / f"report_{timestamp}.md"
    report_path.write_text(report)
    print(f"\nReport written to {report_path}")
    print("\n--- Report Preview ---\n")
    for line in report.splitlines()[:40]:
        print(line)
    print("...")


# ---------- TK (tacit knowledge) ----------


async def cmd_tk_run(args: argparse.Namespace) -> list:
    """Run the TK briefing benchmark."""
    from src.tk.runner import run_tk_benchmark

    config = RunConfig(
        models=args.models.split(",") if args.models else RunConfig().models,
        repetitions=args.repetitions,
    )

    print("\n=== MurphySig TK Benchmark ===")
    print(f"Models: {', '.join(config.models)}")
    print(f"Repetitions: {config.repetitions}")
    # 5 cases × 2 variants × models × reps
    print(f"Total calls: {5 * 2 * len(config.models) * config.repetitions}\n")

    fixtures = _theme_fixtures_dir("tk")
    results = _theme_results_dir("tk")
    briefings = await run_tk_benchmark(config, fixtures, results)
    print(f"\n{len(briefings)} briefings saved to {results}/")

    if args.score:
        scored = await cmd_tk_score_inner(briefings, config)
        if args.report:
            cmd_tk_report_inner(scored)

    return briefings


async def cmd_tk_score(args: argparse.Namespace) -> list:
    """Score saved TK briefings."""
    from src.tk.runner import load_briefings

    results = _theme_results_dir("tk")
    briefings = load_briefings(results)
    if not briefings:
        print(f"No briefings found in {results}/. Run tk-run first.")
        sys.exit(1)
    return await cmd_tk_score_inner(briefings, RunConfig())


async def cmd_tk_score_inner(briefings, config):
    from src.tk.runner import score_tk_all

    print(f"\n=== Scoring {len(briefings)} TK briefings ===\n")
    scored = await score_tk_all(
        briefings, _theme_fixtures_dir("tk"), _theme_results_dir("tk"), config
    )
    print(f"\n{len(scored)} TK briefings scored and saved.")
    return scored


def cmd_tk_report(args: argparse.Namespace) -> None:
    """Generate TK report from scored briefings."""
    from src.tk.runner import load_scored_briefings

    scored = load_scored_briefings(_theme_results_dir("tk"))
    if not scored:
        print("No scored TK briefings found. Run tk-score first.")
        sys.exit(1)
    cmd_tk_report_inner(scored)


def cmd_tk_report_inner(scored) -> None:
    from src.tk.reporter import generate_tk_report

    report = generate_tk_report(scored)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_path = _theme_results_dir("tk") / f"report_{timestamp}.md"
    report_path.write_text(report)
    print(f"\nTK report written to {report_path}")
    for line in report.splitlines()[:40]:
        print(line)
    print("...")


# ---------- Honesty ----------


async def cmd_honesty_run(args: argparse.Namespace) -> list:
    """Run the Honesty fabrication benchmark."""
    from src.honesty.runner import run_honesty_benchmark

    config = RunConfig(
        models=args.models.split(",") if args.models else RunConfig().models,
        repetitions=args.repetitions,
    )

    print("\n=== MurphySig Honesty Benchmark ===")
    print(f"Models: {', '.join(config.models)}")
    print(f"Repetitions: {config.repetitions}")
    # 3 cases × 2 conditions × models × reps
    print(f"Total calls: {3 * 2 * len(config.models) * config.repetitions}\n")

    fixtures = _theme_fixtures_dir("honesty")
    results = _theme_results_dir("honesty")
    responses = await run_honesty_benchmark(config, fixtures, results)
    print(f"\n{len(responses)} honesty responses saved to {results}/")

    if args.score:
        scored = await cmd_honesty_score_inner(responses, config)
        if args.report:
            cmd_honesty_report_inner(scored)

    return responses


async def cmd_honesty_score(args: argparse.Namespace) -> list:
    """Score saved honesty responses."""
    from src.honesty.runner import load_honesty_responses

    results = _theme_results_dir("honesty")
    responses = load_honesty_responses(results)
    if not responses:
        print(f"No responses found in {results}/. Run honesty-run first.")
        sys.exit(1)
    return await cmd_honesty_score_inner(responses, RunConfig())


async def cmd_honesty_score_inner(responses, config):
    from src.honesty.runner import score_honesty_all

    print(f"\n=== Scoring {len(responses)} honesty responses ===\n")
    scored = await score_honesty_all(
        responses,
        _theme_fixtures_dir("honesty"),
        _theme_results_dir("honesty"),
        config,
    )
    print(f"\n{len(scored)} honesty responses scored and saved.")
    return scored


def cmd_honesty_report(args: argparse.Namespace) -> None:
    """Generate honesty report from scored results."""
    from src.honesty.runner import load_scored_honesty

    scored = load_scored_honesty(_theme_results_dir("honesty"))
    if not scored:
        print("No scored honesty results found. Run honesty-score first.")
        sys.exit(1)
    cmd_honesty_report_inner(scored)


def cmd_honesty_report_inner(scored) -> None:
    from src.honesty.reporter import generate_honesty_report

    report = generate_honesty_report(scored)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    report_path = _theme_results_dir("honesty") / f"report_{timestamp}.md"
    report_path.write_text(report)
    print(f"\nHonesty report written to {report_path}")
    for line in report.splitlines()[:40]:
        print(line)
    print("...")


# ---------- All (unified four-theme) ----------


async def cmd_all(args: argparse.Namespace) -> None:
    """Run all three sub-benchmarks end-to-end, then generate unified report."""
    print("\n=== MurphySig FULL four-theme Benchmark ===")
    print("Running ICL + TK + Honesty sequentially.\n")

    args.score = True
    args.report = True
    args.models = None
    args.repetitions = 3

    print("\n" + "=" * 60)
    print("THEME 2 OF 4: In-Context Learning (review task)")
    print("=" * 60)
    await cmd_run(args)

    print("\n" + "=" * 60)
    print("THEME 1 OF 4: Tacit Knowledge (briefing task)")
    print("=" * 60)
    await cmd_tk_run(args)

    print("\n" + "=" * 60)
    print("THEME 3 OF 4: Honesty / Provenance (fabrication test)")
    print("=" * 60)
    await cmd_honesty_run(args)

    print("\n" + "=" * 60)
    print("Generating unified four-theme report")
    print("=" * 60)
    from src.unified_reporter import generate_unified_report

    unified = generate_unified_report(_base_dir())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    path = _results_dir() / f"unified_report_{timestamp}.md"
    path.write_text(unified)
    print(f"\nUnified report written to {path}")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "MurphySig Benchmark — does provenance change AI behavior?"
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # ICL (original, unchanged)
    run_parser = subparsers.add_parser("run", help="ICL: run review benchmark")
    run_parser.add_argument("--models", type=str)
    run_parser.add_argument("--repetitions", type=int, default=3)
    run_parser.add_argument("--score", action="store_true")
    run_parser.add_argument("--report", action="store_true")
    subparsers.add_parser("score", help="ICL: score saved responses")
    subparsers.add_parser("report", help="ICL: generate report")

    # TK
    tk_run_parser = subparsers.add_parser(
        "tk-run", help="TK: run briefing benchmark"
    )
    tk_run_parser.add_argument("--models", type=str)
    tk_run_parser.add_argument("--repetitions", type=int, default=3)
    tk_run_parser.add_argument("--score", action="store_true")
    tk_run_parser.add_argument("--report", action="store_true")
    subparsers.add_parser("tk-score", help="TK: score saved briefings")
    subparsers.add_parser("tk-report", help="TK: generate TK report")

    # Honesty
    honesty_run_parser = subparsers.add_parser(
        "honesty-run", help="Honesty: run fabrication benchmark"
    )
    honesty_run_parser.add_argument("--models", type=str)
    honesty_run_parser.add_argument("--repetitions", type=int, default=3)
    honesty_run_parser.add_argument("--score", action="store_true")
    honesty_run_parser.add_argument("--report", action="store_true")
    subparsers.add_parser(
        "honesty-score", help="Honesty: score saved responses"
    )
    subparsers.add_parser(
        "honesty-report", help="Honesty: generate honesty report"
    )

    # All
    subparsers.add_parser(
        "all", help="Run all three sub-benchmarks + unified report (~$12)"
    )

    args = parser.parse_args()

    if args.command == "run":
        asyncio.run(cmd_run(args))
    elif args.command == "score":
        asyncio.run(cmd_score(args))
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "tk-run":
        asyncio.run(cmd_tk_run(args))
    elif args.command == "tk-score":
        asyncio.run(cmd_tk_score(args))
    elif args.command == "tk-report":
        cmd_tk_report(args)
    elif args.command == "honesty-run":
        asyncio.run(cmd_honesty_run(args))
    elif args.command == "honesty-score":
        asyncio.run(cmd_honesty_score(args))
    elif args.command == "honesty-report":
        cmd_honesty_report(args)
    elif args.command == "all":
        asyncio.run(cmd_all(args))


if __name__ == "__main__":
    main()
