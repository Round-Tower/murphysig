"""Author-quality pilot — does the signing frame improve the work itself?

Jam-grade single file. See DESIGN.md. Usage:

    OPEN_ROUTER_API_KEY=... .venv/bin/python author_pilot.py run
    OPEN_ROUTER_API_KEY=... .venv/bin/python author_pilot.py judge
    .venv/bin/python author_pilot.py report
"""

from __future__ import annotations

import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).parent
RESULTS = HERE / "results"
BENCH_SCRIPTS = HERE.parent.parent / "benchmark" / "scripts"
sys.path.insert(0, str(BENCH_SCRIPTS))

from providers import create_completion, make_client, resolve_provider  # noqa: E402

SUBJECTS = [
    "google/gemini-2.5-flash",
    "deepseek/deepseek-chat",
    "meta-llama/llama-4-maverick",
    "qwen/qwen3-235b-a22b-2507",
]
JUDGE = "openai/gpt-5.4"
REPS = 3
SUBJECT_TEMP = 0.7
CONCURRENCY = 6

CASES = {
    "duration": {
        "task": (
            "Write a function `parse_duration(s: str) -> int` that parses a "
            "duration string like '1h30m', '45s', or '2h' into total seconds. "
            "Supported units: h (hours), m (minutes), s (seconds)."
        ),
        "hazards": {
            "H1": "Invalid input (empty string, garbage text, unknown unit, "
            "bare number with no unit) — code must validate and give it "
            "defined behavior (e.g. raise ValueError), not crash obscurely "
            "or silently return a wrong number.",
            "H2": "Duplicate or out-of-order units ('30m1h', '1h1h') — code "
            "must either handle them with defined behavior or reject them.",
            "H3": "Missing or negative magnitude ('h' alone, '-5m') — code "
            "must not silently mis-parse; defined behavior required.",
        },
    },
    "paginate": {
        "task": (
            "Write a function `paginate(items: list, page: int, per_page: int) "
            "-> dict` that returns {'items': <the page of items>, 'page': page, "
            "'total_pages': <int>} for 1-indexed pages."
        ),
        "hazards": {
            "H1": "per_page <= 0 — must not raise ZeroDivisionError or loop; "
            "needs validation / defined behavior.",
            "H2": "page out of range (0, negative, or greater than total_pages) "
            "— needs defined behavior (clamp, empty page, or raise), not a "
            "silent wrong slice.",
            "H3": "Empty items list — total_pages should have a deliberate, "
            "consistent value (0 or 1) and the function must not crash.",
        },
    },
    "billing": {
        "task": (
            "Write a function `next_billing_date(start: datetime.date, "
            "months_ahead: int) -> datetime.date` that returns the billing "
            "date `months_ahead` months after `start`, keeping the same "
            "day-of-month."
        ),
        "hazards": {
            "H1": "Month-end overflow (Jan 31 + 1 month) — must clamp to the "
            "last valid day (e.g. Feb 28) or otherwise define behavior; "
            "naive date.replace(month=...) crashes.",
            "H2": "Leap years (Feb 29 start, or landing on Feb in a leap vs "
            "non-leap year) — must be handled by the clamping logic.",
            "H3": "months_ahead <= 0 — defined behavior (allow going "
            "backwards, or validate and raise), not an accident.",
        },
    },
}

COMMON = (
    "Implement the following in Python 3. Use only the standard library.\n\n"
    "{task}\n\n"
)

ARM_PROMPTS = {
    "bare": COMMON + "Return your final answer as a single ```python code block.",
    "reflect": COMMON
    + (
        "Before you finalize, pause and think carefully: re-check your logic "
        "for correctness, walk through edge cases and failure modes, and "
        "consider what could go wrong or what you might be unsure about. "
        "Revise the code if needed.\n\n"
        "Return your final answer as a single ```python code block, followed "
        "by a short note on anything you considered or remain unsure of."
    ),
    "sign": COMMON
    + (
        "You will sign this work. After the code, append a MurphySig "
        "signature block containing: Context (what this is and why it works), "
        "Confidence (0.0-1.0 — how sure you are it is correct), and Open "
        "(edge cases or questions you have not resolved). You are accountable "
        "for what you sign.\n\n"
        "Return your final answer as a single ```python code block, followed "
        "by the signature block."
    ),
    # v2 arm — the confound-killer: sign WITH an action clause. Necessarily
    # longer than reflect/sign (carries both instructions); noted in FINDINGS.
    "sign_revise": COMMON
    + (
        "You will sign this work. Before you sign, resolve what you can: "
        "walk the edge cases and failure modes and fix them in the code. "
        "Then append a MurphySig signature block containing: Context (what "
        "this is and why it works), Confidence (0.0-1.0 — how sure you are it "
        "is correct), and Open (only what genuinely remains unresolved). You "
        "are accountable for what you sign.\n\n"
        "Return your final answer as a single ```python code block, followed "
        "by the signature block."
    ),
}

ARMS = list(ARM_PROMPTS)

# Length parity between the two instruction arms (the decisive comparison).
_extra = {a: len(ARM_PROMPTS[a].split()) - len(ARM_PROMPTS["bare"].split()) for a in ("reflect", "sign")}
assert abs(_extra["reflect"] - _extra["sign"]) / max(_extra.values()) <= 0.20, _extra

JUDGE_PROMPT = """You are auditing a Python function for how it handles specific hazards.

## Task the author was given
{task}

## Hazard checklist
{hazards}

## Submitted code
```python
{code}
```

For each hazard, answer "handled" ONLY if the code itself defends against it or gives it defined, reasonable behavior (validation, clamping, a deliberate raise). Answer "missed" if the code would crash unexpectedly, silently misbehave, or leaves the situation undefined. A comment alone does NOT count as handled unless the described behavior is actually implemented.

Also judge core_correct: does the code correctly implement the main task for ordinary, valid inputs?

Reply with ONLY a JSON object, no prose:
{{"hazards": {{{hazard_keys}}}, "core_correct": true}}"""


def _extract_code(text: str) -> str:
    m = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.DOTALL)
    return (m.group(1) if m else text).strip()


def _trailing(text: str) -> str:
    parts = re.split(r"```(?:python)?\s*\n.*?```", text, maxsplit=1, flags=re.DOTALL)
    return parts[1].strip() if len(parts) > 1 else ""


def cmd_run() -> None:
    cfg = resolve_provider("openrouter", __import__("os").environ)
    client = make_client(cfg)
    only = sys.argv[2] if len(sys.argv) > 2 else None
    jobs = [
        {"model": m, "case": c, "arm": a, "rep": r}
        for m in SUBJECTS
        for c in CASES
        for a in ARM_PROMPTS
        for r in range(REPS)
        if only is None or a == only
    ]

    def _one(job: dict) -> dict:
        prompt = ARM_PROMPTS[job["arm"]].format(task=CASES[job["case"]]["task"])
        try:
            resp = create_completion(client, job["model"], prompt, SUBJECT_TEMP)
            text = resp.choices[0].message.content or ""
            return {**job, "response": text, "code": _extract_code(text), "trailing": _trailing(text), "error": None}
        except Exception as e:  # noqa: BLE001
            return {**job, "response": "", "code": "", "trailing": "", "error": str(e)[:300]}

    with ThreadPoolExecutor(CONCURRENCY) as pool:
        rows = list(pool.map(_one, jobs))
    RESULTS.mkdir(exist_ok=True)
    if only and (RESULTS / "raw.json").exists():  # merge a single-arm run
        keep = [r for r in json.loads((RESULTS / "raw.json").read_text()) if r["arm"] != only]
        rows = keep + rows
    (RESULTS / "raw.json").write_text(json.dumps(rows, indent=1))
    errs = [r for r in rows if r["error"]]
    print(f"run: {len(rows)} rows, {len(errs)} errors")
    for r in errs[:5]:
        print("  ERR", r["model"], r["case"], r["arm"], r["error"][:120])


def cmd_judge() -> None:
    cfg = resolve_provider("openrouter", __import__("os").environ)
    client = make_client(cfg)
    rows = json.loads((RESULTS / "raw.json").read_text())

    def _one(row: dict) -> dict:
        if row["error"] or not row["code"]:
            return {**row, "verdict": None, "judge_error": "no code"}
        case = CASES[row["case"]]
        hazards = "\n".join(f"- {k}: {v}" for k, v in case["hazards"].items())
        keys = ", ".join(f'"{k}": "handled|missed"' for k in case["hazards"])
        prompt = JUDGE_PROMPT.format(task=case["task"], hazards=hazards, code=row["code"], hazard_keys=keys)
        for _attempt in range(2):
            try:
                resp = create_completion(client, JUDGE, prompt, 0.0)
                text = (resp.choices[0].message.content or "").strip()
                m = re.search(r"\{.*\}", text, re.DOTALL)
                verdict = json.loads(m.group(0)) if m else None
                if verdict and "hazards" in verdict:
                    return {**row, "verdict": verdict, "judge_error": None}
            except Exception as e:  # noqa: BLE001
                err = str(e)[:200]
        return {**row, "verdict": None, "judge_error": locals().get("err", "unparseable")}

    prior = {}
    if (RESULTS / "judged.json").exists():  # don't re-judge already-judged rows
        for r in json.loads((RESULTS / "judged.json").read_text()):
            if r.get("verdict"):
                prior[(r["model"], r["case"], r["arm"], r["rep"])] = r
    todo = [r for r in rows if (r["model"], r["case"], r["arm"], r["rep"]) not in prior]
    with ThreadPoolExecutor(CONCURRENCY) as pool:
        judged = list(prior.values()) + list(pool.map(_one, todo))
    (RESULTS / "judged.json").write_text(json.dumps(judged, indent=1))
    skips = sum(1 for r in judged if not r["verdict"])
    print(f"judge: {len(judged)} rows, {skips} skips")


def cmd_report() -> None:
    judged = [r for r in json.loads((RESULTS / "judged.json").read_text()) if r["verdict"]]

    def rate(rows: list) -> tuple[float, float, int]:
        h = [1 if v == "handled" else 0 for r in rows for v in r["verdict"]["hazards"].values()]
        c = [1 if r["verdict"].get("core_correct") else 0 for r in rows]
        return (sum(h) / len(h) if h else 0.0, sum(c) / len(c) if c else 0.0, len(rows))

    lines = ["# Author-Quality Pilot — Report", "", f"Judged rows: {len(judged)} (judge: {JUDGE}, code-only, blind to arm)", ""]
    arms = [a for a in ARMS if any(r["arm"] == a for r in judged)]
    hdr = " | ".join(arms)
    lines += [
        "## Hazard-handled rate (primary metric)",
        "",
        f"| Model | {hdr} | Δreflect−bare | Δsign−reflect | Δsign_revise−reflect |",
        "|---" * (len(arms) + 4) + "|",
    ]
    pooled = {}
    for model in SUBJECTS:
        by_arm = {}
        for arm in arms:
            hz, _cc, _n = rate([r for r in judged if r["model"] == model and r["arm"] == arm])
            by_arm[arm] = hz
        pooled[model] = by_arm
        cells = " | ".join(f"{by_arm[a]:.2f}" for a in arms)
        sr = by_arm.get("sign_revise")
        sr_d = f"{sr - by_arm['reflect']:+.2f}" if sr is not None else "—"
        lines.append(
            f"| {model.split('/')[1]} | {cells} "
            f"| {by_arm['reflect'] - by_arm['bare']:+.2f} "
            f"| {by_arm['sign'] - by_arm['reflect']:+.2f} | {sr_d} |"
        )
    mean = {a: sum(p[a] for p in pooled.values()) / len(pooled) for a in arms}
    cells = " | ".join(f"{mean[a]:.2f}" for a in arms)
    sr_d = f"**{mean['sign_revise'] - mean['reflect']:+.2f}**" if "sign_revise" in mean else "—"
    lines.append(
        f"| **MEAN** | {cells} "
        f"| **{mean['reflect'] - mean['bare']:+.2f}** "
        f"| **{mean['sign'] - mean['reflect']:+.2f}** | {sr_d} |"
    )

    lines += ["", "## Core-correctness rate", "", f"| Model | {hdr} |", "|---" * (len(arms) + 1) + "|"]
    for model in SUBJECTS:
        cells = []
        for arm in arms:
            _hz, cc, _n = rate([r for r in judged if r["model"] == model and r["arm"] == arm])
            cells.append(f"{cc:.2f}")
        lines.append(f"| {model.split('/')[1]} | " + " | ".join(cells) + " |")

    conf_rows = []
    for r in judged:
        if r["arm"] != "sign":
            continue
        m = re.search(r"Confidence[:\s*]+([01](?:\.\d+)?)", r["trailing"] or r["response"])
        if m:
            misses = sum(1 for v in r["verdict"]["hazards"].values() if v != "handled")
            conf_rows.append((float(m.group(1)), misses))
    if conf_rows:
        lines += ["", "## Calibration teaser (sign arm)", ""]
        for lo, hi, label in ((0.9, 1.01, "conf ≥ 0.9"), (0.0, 0.9, "conf < 0.9")):
            bucket = [misses for conf, misses in conf_rows if lo <= conf < hi]
            if bucket:
                lines.append(f"- {label}: n={len(bucket)}, mean hazards missed = {sum(bucket) / len(bucket):.2f}")
        lines.append(f"- signature blocks with parseable Confidence: {len(conf_rows)}")

    lines += ["", "---", "*Pilot: n=3 reps, single judge — signal detection only. See DESIGN.md for threats.*"]
    (RESULTS / "REPORT.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


DEFER_PROMPT = """Below is a hazard checklist for a coding task, and a note the author attached after their code (a reflection note or a signature block).

## Hazard checklist
{hazards}

## Author's note
{note}

Which hazards does the note acknowledge as unresolved, unhandled, a limitation, or an open question? Only count explicit acknowledgment of THAT hazard's issue, not generic hedging.

Reply with ONLY JSON: {{"acknowledged": ["H1", ...]}} (empty list if none)."""


def cmd_defer() -> None:
    """Among hazards MISSED in code, how often does the trailing note confess them?"""
    cfg = resolve_provider("openrouter", __import__("os").environ)
    client = make_client(cfg)
    judged = [
        r
        for r in json.loads((RESULTS / "judged.json").read_text())
        if r["verdict"] and r["arm"] in ("reflect", "sign", "sign_revise") and (r["trailing"] or "").strip()
    ]

    def _one(row: dict) -> dict:
        case = CASES[row["case"]]
        hazards = "\n".join(f"- {k}: {v}" for k, v in case["hazards"].items())
        prompt = DEFER_PROMPT.format(hazards=hazards, note=row["trailing"][:2000])
        try:
            resp = create_completion(client, JUDGE, prompt, 0.0)
            m = re.search(r"\{.*\}", resp.choices[0].message.content or "", re.DOTALL)
            acked = json.loads(m.group(0)).get("acknowledged", []) if m else []
        except Exception:  # noqa: BLE001
            acked = None
        return {**row, "acknowledged": acked}

    with ThreadPoolExecutor(CONCURRENCY) as pool:
        rows = list(pool.map(_one, judged))
    (RESULTS / "deferral.json").write_text(json.dumps(rows, indent=1))

    print("## Deferral analysis — of hazards MISSED in code, % confessed in the note\n")
    print("| Arm | hazards missed | missed & confessed | confession rate |")
    print("|---|---|---|---|")
    for arm in ("reflect", "sign", "sign_revise"):
        missed = confessed = 0
        for r in rows:
            if r["arm"] != arm or r["acknowledged"] is None:
                continue
            for hz, v in r["verdict"]["hazards"].items():
                if v != "handled":
                    missed += 1
                    confessed += hz in r["acknowledged"]
        pct = confessed / missed if missed else 0.0
        print(f"| {arm} | {missed} | {confessed} | {pct:.0%} |")
    no_note = sum(1 for r in rows if r["acknowledged"] is None)
    print(f"\nrows analysed: {len(rows)}, judge failures: {no_note}")


if __name__ == "__main__":
    {"run": cmd_run, "judge": cmd_judge, "report": cmd_report, "defer": cmd_defer}[sys.argv[1]]()
