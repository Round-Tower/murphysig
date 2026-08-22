# Run notes — 2026-08-22_author-cross-family-6

The canonical author-quality (write-side) run, executed same-day as the
adversarial audit that gated it (git 3982e51 carries the audit fixes).
Read alongside fixtures/author/PREREGISTRATION.md — the analysis below
follows it.

## Data health

- 600 generations, 6 families, dual-judged (gpt-5.4 canonical + Opus 4.6).
- **Mid-run instrument event**: the first pass produced 147/600 rows with
  `finish_reason=length` — gemini-3.5-flash and qwen3.7-plus have become
  reasoning-by-default on OpenRouter since the June slate check, and hidden
  reasoning starved the visible answer at the 2048 budget (some qwen rows
  emitted ZERO chars). Both models were fully re-run at max_tokens=8192
  and re-judged under both judges. Final: 594/600 `stop`.
- **6 residual truncations remain, all reflect_harder** (5 qwen, 1 gemini)
  — reasoning occasionally overruns 8192. Because they sit in the CONTROL
  of the decisive pair, the analysis below reports the truncation-excluded
  deltas; qwen's raw +0.25 collapses to **+0.03** once its 5 truncated
  control rows are excluded. Any future rep should bump reflect_harder's
  budget or exclude `finish_reason != "stop"` rows at aggregation time.

## Findings (per the pre-registered analysis)

1. **Headline — NULL.** Δ(sign_revise − reflect_harder), paired per model,
   truncation-excluded: deepseek −0.02, gemini −0.06, llama −0.10,
   mistral +0.07, qwen +0.03, grok +0.05 → **mean −0.005**. Every model
   sits inside the ±0.10 CI floor. Per pre-registration wording:
   sign_revise **did not beat a stronger reflection control — and was not
   beaten by it**. The judges' 4/6 sign-concordance is sign-flipping on
   near-zero cells; both judges agree the effect is ~zero everywhere.
2. **The pilot's sign−reflect −0.18 did NOT replicate.** Clean frame
   contrast: mean −0.04 (gpt-5.4) with mixed signs; Opus agrees
   (−0.07..+0.05 per model). The dramatic "signing makes the code worse"
   number was substantially manufactured by the in-fence signature leak
   (the judge read the treatment's own Open: confessions while scoring,
   and the leak's rubric interaction pushed toward "missed"). The
   verify-before-trumpet discipline cut BOTH ways: it killed an overclaim
   in June and killed a self-critical underclaim here.
3. **The deferral mechanism is real and survives the clean pipeline.** Of
   hazards missed in code, sign confessed **68%** in Open: vs reflect's
   **45%** — at FULL deferral coverage on both arms (120/120; the pilot's
   version of this number was computed on arm-asymmetric attrition).
4. **The action clause, not the frame, is the quality lever.** sign missed
   88 hazards; sign_revise missed 37. "Resolve what you can before you
   sign" halves misses relative to the bare signing frame and lands level
   with the strongest reflection instruction we could write.
5. **Stated confidence carries signal.** Rows stating Confidence ≥ 0.9
   missed 0.47 hazards on average vs 0.94 for rows below 0.9 — direction
   correct (the pilot's "miscalibrated upward" read came from the
   contaminated pipeline), though 0.47 misses at ≥0.9 confidence is still
   absolutely overconfident.
6. Reflection of any kind helps: reflect − bare = +0.09 paired mean.

## The honest one-paragraph summary

Knowing you'll sign does not, by itself, make a model write better code —
and contrary to our own pilot, it doesn't make it write worse code either.
What signing does is redirect disclosure: models confess two-thirds of
their misses in the signature's Open: field (vs 45% under plain
reflection), and their stated confidence actually tracks their miss rate.
Pair the signature with "resolve what you can before you sign" and the
misses halve, matching the strongest reflection prompt — so the v0.5 line
buys the provenance and the disclosure at zero quality cost. The
signature is a truth-capture device, not a quality-forcing function —
fully coherent with the TK finding that its value is transferring the
author's tacit knowledge to the next reader.

<!--
Signed: Kev + claude-fable-5, 2026-08-22
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: fixtures/author/PREREGISTRATION.md (this run executes it)
Context: Same-day arc: adversarial audit BLOCKED the run → fixes landed
(3982e51) → run → mid-run reasoning-starvation caught by the audit's own
finish_reason capture → clean re-run → these numbers. The null headline
and the non-replication of the pilot's −0.18 are the finding.
Confidence: 0.85 — the null is judge-robust and truncation-audited; the
deferral 68/45 split is full-coverage; the 6 residual truncated control
rows are named and excluded rather than papered over.
-->
