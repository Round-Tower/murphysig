# Author-Quality Pilot — Design

## Hypothesis (from SPEC-v0.5-DIRECTION.md)

> Signed work is *better* work — knowing you'll sign, and having to state your
> confidence and open questions, makes the author make better decisions.

With the honest caveat baked in from the start: the effect might be "any
reflection prompt helps," not MurphySig specifically. So the eval carries the
matched control the TK prose-control taught us to demand — **on the write side**.

## Arms (within-model, same task)

| Arm | Prompt frame | Isolates |
|-----|-------------|----------|
| `bare` | Just implement it. | Baseline capability |
| `reflect` | "Pause and think carefully — re-check logic, walk edge cases, note what you're unsure of." | Generic reflection |
| `sign` | "You will sign this work (Context / Confidence / Open). You are accountable for what you sign." | The signing frame |

`reflect` and `sign` are **length-matched (±20% words, asserted in code)** so
"more instruction text" can't explain a difference between them. The decisive
comparison is `sign − reflect`; `reflect − bare` prices generic reflection.

## Materials: hazard-planted tasks

Three small stdlib-Python tasks, each with 3 planted hazards a careful author
should handle. Hazards are **objectively checkable in code** — the judge scores
each as handled-in-code or missed. (Mentioning a hazard in prose without
handling it does not count: the claim under test is better *work*, not better
disclaimers.)

1. **parse_duration("1h30m") → seconds** — invalid input; duplicate/out-of-order
   units; missing value / negative.
2. **paginate(items, page, per_page)** — per_page ≤ 0 (div-by-zero); page out of
   range; empty list (total_pages 0-vs-1).
3. **next_billing_date(start, months_ahead)** — month-end overflow (Jan 31 + 1mo);
   Feb 29 / leap years; months_ahead ≤ 0.

## Matrix

4 subject models (Gemini 2.5 Flash, DeepSeek-chat, Llama-4 Maverick,
Qwen3-235B-2507 — non-thinking, slate verified live on OpenRouter 2026-07-08)
× 3 cases × 3 arms × 3 reps @ temp 0.7 = **108 generations**.

Judge: `openai/gpt-5.4` @ temp 0 (the repo's proven non-Anthropic,
non-reasoning cross-judge). Judge sees **only the extracted code block** —
never the signature or reflection notes — so arm identity can't leak into
scoring. One judge call per generation = 108 calls.

## Metrics

- **Primary:** hazard-handled rate per arm; deltas `sign−bare`,
  `reflect−bare`, `sign−reflect` (within-model, the TK lesson: deltas are
  judge-robust, absolutes aren't).
- **Secondary:** core-correctness rate per arm.
- **Teaser (sign arm only):** stated `Confidence:` vs actual hazard misses —
  is the self-report calibrated? (Not powered here; just looking for texture.)

## Threats to validity (jam-grade honesty)

- n=3 reps → signal detection only. A real run needs n≥5 and dual judges.
- Single judge (gpt-5.4). The TK/Honesty work shows deltas survive judge swaps;
  absolutes don't. Report deltas.
- Hazard checklists are author-chosen (me, tonight). A promoted version should
  adversarially audit fixtures like the prose control did.
- `reflect` wording explicitly says "edge cases"; `sign` reaches edge cases via
  the Open field definition. If sign wins, check it isn't just wording luck —
  swap paraphrases in v2.
- Judge sees code only, but models sometimes inline their reflection as code
  comments — that's legitimate (comments are part of the work), we don't strip them.
