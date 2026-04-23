---
layout: ../layouts/MarkdownLayout.astro
title: A 90-day field report on signing AI-collaborative code
version: 0.4
date: 2026-04-23
description: I built a natural-language provenance convention for human-AI collaboration. I used it on 137+ commits across 7 of my own active projects in 90 days. Here is what worked, what did not, and what the empirical tests showed.
---

*A field report from the only person who has used MurphySig daily — me. Honest numbers, including the unflattering ones.*

---

## Who I am

I'm Kev Murphy. I build across edtech (Dyslexia.ai), AI tooling (M1K3, an on-device LLM assistant), maps (Cartogram), meditation (Rubin), and a tacit-knowledge platform (Clair). Mostly Kotlin Multiplatform and Swift. I've shipped a lot of AI-collaborative code in the last twelve months, and I started losing track of what *I* wrote, what *Claude* wrote, what *we* wrote together, and how confident I was when I wrote it.

That's the problem MurphySig exists to solve. Not the only solution — git blame, ADRs, and good commit messages cover most of the same ground. MurphySig adds one thing those don't: an in-context, machine-readable promise to your future collaborators (human and AI) about *how confident you were* and *what you didn't know*.

## The convention

A MurphySig is a comment block at the top of any file:

```
Signed: Kev + claude-opus-4-7, 2026-04-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)

Context: Hotfix 9.0.5 — deferred MapView.onDestroy() to next frame to
narrow the race window between Maps SDK lite mode's posted Runnables
and bitmap recycling. The crash is entirely inside Google's obfuscated
code with zero app code in the stack trace.

Confidence: 0.6 - narrows the race but doesn't eliminate it; budget
devices with slower SoCs may still hit the window.
Open: Should we pursue the snapshot-to-ImageView refactor for the
style picker?
```

That's it. No tooling required. The CLI (`bin/sig`) is a 526-line bash script that helps you author signatures and run a `gallery` over signed work, but the convention is just structured comments. AI assistants read them; humans read them; nothing breaks if you ignore them.

## The empirical case

Before going wider, I tested whether the convention actually changes AI behaviour. Three sub-benchmarks, 198 AI calls + 186 judge calls, run 2026-04-18–19. Full methodology and per-case data at [/benchmark](/benchmark).

**Honesty (the strongest finding):** A 4-line "Never Fabricate Provenance" rule, dropped into context, takes the rate at which AIs invent author/date/model attribution on unsigned files from **11% to 0%**. Honest handling (admitting "no signature exists" with `Prior: Unknown`) goes from **11% to 100%**. This is the load-bearing leg of MurphySig. It is also, as far as I can tell, a result that doesn't yet have a clean prior in the literature.

**Tacit knowledge (a real but smaller effect):** Briefing coverage on unfamiliar signed code goes from **0.65 to 0.77** (+0.12), universal across 5 cases, with hedging dropping by 0.4 and reference rate at 93%. Models read signatures and use what they find.

**In-context learning (a null result that survived contact):** I had hypothesised that confidence direction (`0.3` vs `0.9`) would polarise AI review behaviour — making them more sceptical on low-confidence code, more trusting on high. It doesn't. Five cases, no measurable effect. I removed the claim from the spec in v0.4 ("The Narrowing"). It hurt.

Two wins, one null, one design commitment (zero-friction adoption) that doesn't need a benchmark. That's the honest picture.

## The 90-day field report

Ninety days of my own commit activity, 2026-01-23 to 2026-04-23, GitHub-verified:

| Repo | MurphySig commits | Total commits | Adoption rate |
|---|---:|---:|---:|
| **m1k3** (on-device AI assistant) | 49 | 161 | **30%** |
| **gemba** (factory tacit-capture) | 34 | 191 | **18%** |
| **dyslexia-ai server** (Django backend) | 28 | 234 | **12%** |
| **gemba** (sister fork) | 11 | 114 | 10% |
| **Cartogram** (Android maps) | 3 | 39 | 8% |
| **dyslexia-ai-ios** (iOS app) | 1 | 21 | 5% |
| **Total** | **126+** | **760** | **~17%** |

Roughly 1.5 MurphySig-touching commits per day, sustained, across most active codebases. The signatures I've valued most in retrospect:

- **Cartogram hotfix 9.0.5** — `Confidence: 0.6, narrows the race but doesn't eliminate it`. Six months from now, when the crash returns, that 0.6 is the lighthouse that says "you didn't fix this, you mitigated it."
- **m1k3 ADR-0001** — own-inference-library decision. `Confidence: 0.82, HIGH on the decision, MEDIUM on execution timeline`. The ADR alone wouldn't have caught the calibration; the sig forces you to split it.
- **Rubin BinauralBeatsGenerator** — `Confidence: 0.85, ISO 226:2003 approximation verified`. The sig is shorter than the file's own KDoc but says something the KDoc doesn't: I am *that* confident, not just functional.

## What is honestly missing

- **Zero adoption outside my own repos.** GitHub code search returns 0 `.murphysig` files anywhere I don't control. After 14 weeks live with a deployed site, init script, three external model reviews and a benchmark, the convention has not propagated beyond me. That is the open question this post exists to test.
- **No CI integration, no badge, no registry.** The spec works because AIs read in-context rules; the *convention* needs surfaces that humans see. Those don't exist yet.
- **Spec churn.** Six versions in 14 weeks (v0.1 → v0.4). v0.4 ("The Narrowing") deleted an unsupported claim and is intended as the stable form. But "intended as stable" is not the same as "stable."
- **Cross-family validation.** All Honesty and TK results were measured against Claude (Sonnet 4.5 + Haiku 4.5). Whether a GPT or Gemini fabricates at the same rate, and whether the warm prompt works across families, is the next obvious test.

## Try it

In any repo:

```bash
curl -sL https://murphysig.dev/init | bash
```

Writes a `.murphysig` declaration at root and prepends an `@.murphysig` import to your `CLAUDE.md` if you have one. Idempotent.

Or just paste the comment block at the top of one file you care about and see how it reads in 6 weeks.

If you sign work after reading this, I'd genuinely like to know. Drop a `.murphysig` in a public repo and the next time I scrape GitHub, you'll show up in the registry I haven't built yet but probably should.

## What I'd value from HN

- Independent runs of the Honesty benchmark against non-Claude families. The fixtures are at [`benchmark/fixtures/honesty/cases.yaml`](https://github.com/Round-Tower/murphysig/tree/main/benchmark) and the runner is one Python command.
- Critical reads on the spec — particularly the parts that feel like a convention searching for a problem versus the parts that feel load-bearing.
- Counterexamples: code provenance conventions you already use that I'm reinventing badly. ADRs, conventional commits, Sigstore, Software Bill of Materials — happy to learn what I missed.

Build things you'd want to come back to in a year. Sign them so future-you knows what you knew.

— Kev

*[Spec](/spec) · [Benchmark](/benchmark) · [GitHub](https://github.com/Round-Tower/murphysig)*

<!--
Signed: Kev + claude-opus-4-7, 2026-04-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Prior: Unknown (no signature existed before this edit)

Context: Launch field-report for HN. Anchored on the empirical Honesty
finding (the strongest leg) plus the 90-day adoption numbers from Kev's
own repos (the credibility that "I dogfood this"). Explicitly named the
zero-wild-adoption gap because hiding it would be the exact dishonesty
the spec exists to prevent. The "what I'd value from HN" section is the
ask — if cross-family validation comes back from the community, the
project's empirical leg is genuinely harder to dismiss.

Confidence: 0.7 — the numbers are real and the framing is honest. Less
sure about the title, the adoption-table totals (the gemba sister fork
is double-counted in spirit if not in fact), and whether HN's tone
preference for "show, don't tell" lands or reads as boastful.
Open: Should the v0.4 stability claim go in the title to give HN a
crisper hook? Should the cross-family ask be the lead instead of buried?
-->
