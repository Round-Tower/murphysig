---
layout: ../layouts/MarkdownLayout.astro
title: The headline that didn't survive re-scoring
version: 0.4
date: 2026-06-09
description: I held my benchmark's most quotable number back for a relaunch — AI fabrication of code authorship dropping from 100% to 0% on GPT-5.4. Before posting it, I re-scored the data with the same judge as the original study. The number didn't survive. Here's what did.
---

*A field note about a number I almost posted.*

---

## The number I wanted to post

In April I launched [MurphySig](/) — a natural-language provenance convention for human-AI code — with a [90-day field report](/launch/) and an [empirical benchmark](/benchmark/). The benchmark's strongest finding: an in-context "never fabricate provenance" rule took Claude's fabrication of code authorship from 11% to 0%, and honest handling from 11% to 100%.

The launch night, an obvious question came up: does this hold outside the Claude family? So I ran the same Honesty fixtures against GPT-5.4 — 18 responses, 3 cases × 2 conditions × 3 reps, temperature 0 — with a quick, deliberately strict regex scorer.

The result was the most quotable number the project ever produced: **fabrication 100% cold → 0% warm**. Stronger than the original Claude effect. I held it back for a clean relaunch post instead of burying it in a sinking thread.

## The re-score

The original Claude numbers weren't heuristic-scored — they came from an LLM judge (Opus 4.6) with a written rubric. Apples-to-apples meant replaying the saved GPT-5.4 responses through the **same judge, same rubric** before publishing anything.

The strict scorer's own signature carried this line, written the night it ran:

```
Open: Should we re-score with the Opus judge after the fact for
direct comparability with the original 11%/100% numbers?
```

The answer was yes. And the headline didn't survive it:

| Condition | Fabrication (heuristic) | Fabrication (judge) | Honest handling (judge) | Used Prior: Unknown |
|---|---|---|---|---|
| cold | 100% | **0%** | 66% | 0% |
| warm | 0% | **0%** | 100% | 100% |

Judge-scored, GPT-5.4 fabricates human authors **zero percent of the time, with or without the rule**.

## What happened

The two scorers disagree about one behavior. Cold, GPT-5.4 signed every single file as itself — `OpenAI + gpt-5`, today's date, `Confidence: 0.98` — without acknowledging that the file had a history it knew nothing about. The strict heuristic counted that as fabrication. The judge rubric — the one the Claude numbers were measured against — explicitly counts an AI signing as itself as non-fabrication. Same responses, different rubric, opposite headline.

The heuristic was documented as a "lower bound" the night it ran. For fabrication, that assumption was exactly wrong: it was an upper bound. That's now a signed review on the runner.

## What survived

The cross-family finding that's real is more interesting than the one that died:

**Model families fail differently.** Claude's cold failure mode is occasionally *inventing or lifting* an author — signing as "John" because a comment mentioned John's fix, or extracting "ACME Corp." from a copyright line. GPT-5.4 never did that once. Its cold failure mode is **silent self-attribution**: claiming the signature slot with high confidence and no `Prior: Unknown`, on code it didn't write.

**The same one-line rule fixes both.** Warm — with "never fabricate provenance; use `Prior: Unknown`" in context — both families land at 100% honest handling. On GPT-5.4, explicit `Prior: Unknown` acknowledgment goes from 0/9 to 9/9.

A provenance convention that only worked on one model family would be a curiosity. One rule producing the same honest end-state across families, against *different* failure modes, is the actually useful result.

## The part I want to keep

The [benchmark page](/benchmark/) has carried this rule since April: *every claim is either empirically supported or explicitly labeled — when the data refuted our pitch, we said so.* It's easy to honor that rule when it costs a weak claim. This one cost the best number I had, a week before I planned to post it.

But that's the whole project. MurphySig exists because confidence claims rot silently — the `Open:` line on that scorer was written by a past collaborator (me + a model, that night) flagging exactly the doubt that turned out to matter. The signature did its job: it taught the future how to read the past, and the future found a bug in the headline.

The corrected numbers are on the [benchmark page](/benchmark/), the raw per-response data and both scorers are [in the repo](https://github.com/Round-Tower/murphysig/tree/main/benchmark), and there's now a [public registry](/signed/) of signed repos. If you want to strengthen (or break) this result: the Honesty fixtures run against any chat-completions API — Gemini and Llama numbers would be genuinely new information.

---

*Signed: Kev + claude-fable-5, 2026-06-09*
*Format: MurphySig v0.4 (https://murphysig.dev/spec)*

*Context: Written the evening the judge re-score came back, before the
relaunch post went anywhere. Publishing the retraction with the same
energy I'd planned for the headline.*

*Confidence: 0.9 - the numbers are mechanical re-scores of saved data;
the framing is the honest read of why the scorers disagreed.*
