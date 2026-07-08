# Author-Quality Pilot — Findings (2026-07-08, jam)

**One line: the signing frame alone trades fixes for confessions; add
"resolve what you can before you sign" and it recovers full reflection-level
quality while keeping the signature. That sentence is the spec change.**

## The three numbers (hazard-handled rate, 4 families, code-only blind judge)

| Comparison | Δ | Reading |
|---|---|---|
| reflect − bare | **+0.21** | Generic "think carefully + revise" strongly improves the code |
| sign − bare | **+0.04** | The signing frame barely improves the code |
| sign − reflect | **−0.18** | Signing *underperforms* matched reflection, in 4/4 families |

## But the deferral analysis flips the story from "failure" to "mechanism"

Of hazards **missed in code**, how many did the author's trailing note confess?

| Arm | missed | confessed | rate |
|---|---|---|---|
| reflect | 17 | 7 | 41% |
| sign | 24 | 16 | **67%** |

The `Open:` field acts as a **deferral valve**: "state what you haven't
resolved" licenses leaving it unresolved — but it also *elicits the confession*.
Signing shifted author effort from fixing to disclosing.

## Why this is coherent with everything already proven

- **Read side (TK, proven):** the disclosure is exactly what transfers to the
  next mind (+0.11 cross-family, 3× on the intent axis, Q3 "what was the author
  unsure of" moved most).
- **Write side (this pilot):** signing manufactures that disclosure — at a real
  cost to same-pass code quality vs an action-oriented reflection prompt.
- So the value chain is **capture → transfer**, not **improve**. "Sign the
  work" is an honesty ritual, not a quality ritual. The v0.5 note's caveat
  ("might be any-reflection-helps") was right, and then some.

## The overconfidence texture (spec-relevant)

34 of 35 parseable signatures claimed **Confidence ≥ 0.9** while missing ~0.9
hazards each. Stated confidence at write time is mis-calibrated upward — which
supports v0.5's caution that `Confidence:` must be validated as a *triage*
signal, not treated as ground truth.

## The v2 arm — confound killed, same session

Reflect's "revise the code if needed" was an action clause the sign arm
lacked. So we ran a fourth arm, **sign_revise**: *"Before you sign, resolve
what you can — fix the edge cases and failure modes you find in the code.
Open: only what genuinely remains unresolved."*

| Arm | hazard-handled (mean, 4 families) |
|---|---|
| bare | 0.63 |
| sign | 0.67 |
| reflect | 0.84 |
| **sign_revise** | **0.85** |

**sign_revise ≡ reflect (+0.01)** — the action clause recovers the entire
reflection gain inside the signing frame, and beats reflect outright on
Gemini (+0.07) and Llama (+0.15). Its confession rate on remaining misses is
50% (n=8 misses — too few to lean on; the *reason* n is small is the point:
it fixed things instead of missing them).

## Honest limits

- sign_revise's prompt is necessarily longer than reflect's (carries both
  instructions) — strict length parity is broken for that arm; a promoted run
  should length-match a "reflect harder" control against it.
- n=3 reps, 3 cases, single judge (gpt-5.4, code-only, blind to arm). Signal
  detection only. Deltas not absolutes, per house rule.
- Hazard checklists are author-chosen; a promoted run needs the adversarial
  fixture audit the prose control got.

## Recommendation

Promote to `benchmark/` as the 4-arm experiment (bare / reflect / sign /
sign_revise), n≥5, dual-judge, adversarially-audited fixtures, plus a
length-matched "reflect harder" control for sign_revise. If it replicates,
the v0.5 spec's write-side section writes itself:

> **Resolve what you can before you sign. `Open:` is for what genuinely
> remains — not for what you didn't feel like fixing.**

The complete, honest headline: *the signature frame alone converts effort
into disclosure (67% confession vs 41%); the resolve-first clause converts it
back into fixes (0.85 ≡ reflection) while keeping the signature's capture
value. MurphySig's write-side prescription is validated as a sentence, not a
format — consistent with the read-side finding that content beats structure.*

<!--
Signed: Kev + claude-fable-5, 2026-07-08
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Confidence: 0.55 — pilot-scale (n=3, one judge, author-chosen fixtures); the
sign−reflect gap and the confession-rate gap are consistent across families,
but the wording confound (no action clause in the sign arm) is live and could
account for much of the code-quality gap. The capture→transfer framing is
interpretation, stated as such.
Open: Does the deferral valve appear with human authors? Is stated Confidence
calibratable at all at write time? Does sign_revise hold against a
length-matched "reflect harder" control?
Prior: none (new pilot; design from SPEC-v0.5-DIRECTION.md experiment #1)

Review 2026-07-08 (Kev + claude-fable-5): Same session — added the sign_revise
arm after the deferral finding. It recovers reflect-level quality (0.85 vs
0.84) inside the signing frame. Confidence on the overall arc now 0.6 — the
mechanism story is consistent across two measurements, still pilot-scale.
-->
