# Pre-registration — canonical author-quality run

Written 2026-08-22, BEFORE the canonical run. Committed with the fixtures it
governs (fixture hash binds them in the run manifest). Analysis decisions
below are locked; anything post-hoc gets labelled post-hoc in the writeup.

## Design

- 6 subject families (the TK/Honesty slate, verified live on OpenRouter
  2026-08-22): gemini-3.5-flash, llama-4-maverick, grok-4.3,
  deepseek-chat-v3.1, qwen3.7-plus, mistral-large-2512.
- 4 cases × 5 arms × 5 reps, temperature 0.7 → 100 rows/model, 600 total.
- Dual judge: gpt-5.4 (canonical, untagged) + claude-opus-4.6 (tagged),
  both code-only-blind on the hazard pass, note-only on the deferral pass.
  In-fence signatures are stripped and rerouted pre-judge (rig-gated by
  TestSignatureSplitRigGate — the 2026-08-22 audit's blocking fix).

## Locked analysis

1. **Headline**: mean of per-model paired deltas for
   **Δsign_revise − reflect_harder** (hazard-handled rate). reflect_harder
   is a deliberately-advantaged control: a sign_revise win is conservative;
   a tie/loss is reported as "did not beat a stronger reflection control",
   never as equivalence.
2. **Secondary (labelled frame contrast)**: Δsign − reflect. This compares
   disclosure-framing vs action-framing and is NOT a matched pair. It is
   evidence about what the signing frame redirects effort toward, not "the
   signature's effect on quality".
3. **Mechanism**: per-arm confession rates (of hazards missed in code, %
   acknowledged in the note), quoted ONLY if deferral coverage across
   note-bearing arms is within 5 points (the rescore prints it; the report
   carries judged/dropped columns).
4. **Ceiling rule**: any hazard scoring ≥0.95 across ALL arms pooled is
   reported separately from the headline mean, not silently averaged in.
5. **No equivalence claims**: with 6 families the 95% CI on a paired delta
   is roughly ±0.10 (pilot SD ≈ 0.12); a point estimate near zero is
   reported with its interval, never as "≡".
6. **Judge robustness**: the headline is quoted only if both judges agree
   on its SIGN per the agreement report; magnitudes may differ (the TK
   lesson: judges disagree on scale, agree on delta).
7. **Calibration**: stated-Confidence vs misses, signature-bearing rows
   only, descriptive.

## Honesty notes

- The pilot's published-nowhere numbers (sign−reflect −0.18, confession
  67%/41%) came from a contaminated pipeline (in-fence signature leak,
  arm-asymmetric deferral attrition) and are superseded by this run. If
  the clean run disagrees with the pilot, the clean run wins and the
  contamination story gets told.
- Fixtures were adversarially audited 2026-08-22; billing H2 replaced,
  duration H2 tightened, split_amount added for flagship headroom.

<!--
Signed: Kev + claude-fable-5, 2026-08-22
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (new file)
Context: Locks the canonical run's analysis before data exists, per the
audit's M6. The two challenger reports it responds to live in the session
transcript; their must-fix list is implemented in the same commit.
Confidence: 0.85 — the locked choices follow directly from measured pilot
pathologies; the ±0.10 CI arithmetic is a planning estimate, not a promise.
-->
