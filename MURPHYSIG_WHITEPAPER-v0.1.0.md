# MurphySig: A Human-Readable Provenance Standard (v0.1.0)

**Date**: September 2026 (v0.0.2: February 2026)
**Status**: Foundational Whitepaper — revised after the benchmark
**Spec URL**: https://murphysig.dev/spec
**Benchmark**: https://murphysig.dev/benchmark

**Authors**: Kevin Murphy, Claude (claude-opus-4-6-20250610 for v0.0.2; claude-fable-5-1 for this revision)

> **Revised, not rewritten.** The first version of this paper (February 2026) was written before any of MurphySig's claims had been tested. Between April and August 2026 we tested them — four themes, six model families, two independent judges — and two of the claims below did not survive. This revision keeps the argument, corrects the mechanism, and says plainly what the data supports. The operational form lives in the [specification](https://murphysig.dev/spec); the numbers live on the [benchmark page](https://murphysig.dev/benchmark).

---

**Authors**: Kevin Murphy, Claude (claude-opus-4-6-20250610 for v0.0.2; claude-fable-5-1 for this revision)

> **Revised, not rewritten.** The first version of this paper (February 2026) was written before any of MurphySig's claims had been tested. Between April and August 2026 we tested them — four themes, six model families, two independent judges — and two of the claims below did not survive. This revision keeps the argument, corrects the mechanism, and says plainly what the data supports. The operational form lives in the [specification](/spec/); the numbers live on the [benchmark page](/benchmark/).

---

## Abstract

As we enter the era of ubiquitous AI collaboration, the provenance of our creative work is disappearing. Code, prose, and art are becoming black boxes—outputs without history. MurphySig is a proposal to reclaim that history. It is a convention for signing work with natural language context that is legible to both humans and machine intelligence. It imposes no tooling requirements, only a cultural one: that the *process* of creation is as valuable as the artifact itself.

We have now measured what that convention does. Signed code helps a model brief unfamiliar code across every family we tested—but because of the *knowledge* the author wrote down, not the format it was written in. A four-line rule in the project's `.murphysig` file stops capable models inventing authors. And knowing you will sign does not make a model write better code; it makes the model *say what it missed*. The signature is not a prompt. It is a truth-capture device.

---

## 1. The Problem: The Streaming Now

The velocity of modern software engineering and content creation has eliminated reflection. We ship and move on. "Done" is a boolean state, not a documented journey.

Simultaneously, we are collaborating with AI systems that have no continuity. A conversation with Claude or GPT is ephemeral; once the window closes, the context vanishes. The next model version will not know why a decision was made, only that code exists.

We are building in the dark, leaving no breadcrumbs for our future selves or the future intelligences that will maintain our work. We face **The Gallery Problem**: an endless stream of creation with no structure to revisit, witness, or learn from what we have made.

## 2. The Solution: Legible Provenance

MurphySig proposes a simple standard: a **structured natural language comment block** at the beginning of any artifact.

It is **not cryptographic**. It does not prove authorship in a legal sense.
It is **semantic**. It explains *intent*, *uncertainty*, and *collaboration*.

By signing our work with specific model versions (e.g., `claude-fable-5-1`), confidence scores, and context, we create two things:
1.  **Accountability (Murphy's Law)**: A trace of what went wrong when it inevitably does.
2.  **Presence (Murphy's Signature)**: A trace that we were here, witnessing our own craft.

## 3. Philosophy

### 3.1 The Law: "Anything that can go wrong, will."
This is not pessimism; it is engineering reality. When we hide uncertainty, we create fragility. MurphySig demands we document our **Confidence**—whether numerical (`0.7 - architecture solid, thresholds need testing`) or text (`Solid but untested at scale`)—and what remains **Open**.

The first version of this paper claimed that a model reading `Confidence: 0.3` would scrutinise the code harder than one reading `Confidence: 0.9`. We tested that. It is false. Models read the number—they cite it in 85% of reviews—but the direction does not change how carefully they look. That claim was removed from the specification in v0.4.

What the confidence number *does* carry is signal about the author. In the write-side benchmark, signatures that stated `Confidence ≥ 0.9` sat on code that missed half as many planted hazards as signatures below 0.9. Stated confidence tracks actual quality—imperfectly, still overconfident in absolute terms, but in the right direction. That makes confidence a **triage signal** for the next reader, human or machine: audit the low-confidence file with the unresolved `Open:` first. It is not a scrutiny dial. It is a map of where the author knew the ground was soft.

### 3.2 The Signature: "Anything worth making is worth returning to."
The "Signature" is the act of presence. It is the creator acknowledging the work. The standard includes a **Reflections** section—not for debugging, but for witnessing. "I wrote this late at night," or "This was the moment it clicked." This humanizes the codebase and breaks the relentless forward march of "shipping."

We also tested the act itself. Does knowing you will sign make the work better? For a model, no—and, contrary to our own pilot, it does not make the work worse either. Against the strongest "reflect before you submit" instruction we could write, the signing frame produced code of the same quality across all six families. What changed was disclosure: of the hazards a model missed, it confessed 68% in the signature's `Open:` field, versus 45% under plain reflection. **Signing does not stop the miss. It makes the miss visible.** That is what returning to the work is for.

## 4. The Mechanism: Tacit Knowledge, Written Down

The first version of this paper called MurphySig "in-context learning for future AI" and said the signature "is not metadata; it is a prompt." Half of that survived.

When a model reads a signed file and briefs an unfamiliar reader on it, the briefing is better: more complete, less hedged, across every family we tested—Gemini, Llama, DeepSeek, Grok, Qwen, Mistral—with the weakest briefers gaining the most. The gain concentrates three-to-one on questions about the **author's intent**—*what was this for, what was the author unsure about*—over questions the code itself can answer. The signature hands over what the author knew and the code cannot show.

Then we ran the control. The same facts, rewritten as a plain unstructured comment with no field labels and no confidence number, length-matched to the signature, captured 80–94% of the gain. The MurphySig *structure* accounts for the small remainder.

So the signature is not a prompt that changes how a model reads. It is the author's tacit knowledge, externalised. The model benefits because a mind did the work of articulating intent and uncertainty—not because of the syntax that mind used. The `Context` / `Confidence` / `Open` fields are a **completeness scaffold for the author**: a checklist for the things that live in your head and never reach the code. Fill it in as prose if you like. The discipline is the asset; the format is how we remember to practise it.

One part of the convention *does* act directly on model behaviour, and it acts strongly: the **norm**. The project-level `.murphysig` file carries a rule—*never fabricate provenance; if you don't know who wrote it, write `Prior: Unknown`*. Without that rule in context, capable models asked to sign an unattributed file will sometimes invent an author, or lift one from a nearby comment. With it, four of six families reach 100% honest handling. Two families with weaker instruction-following comply cosmetically. The `.murphysig` file is not documentation. It is a behavioural contract, and it works where the model can follow it.

## 5. What We Measured

Every claim in this paper is either supported below or explicitly labelled as not. Full method, tables, per-family charts and archived raw runs are on the [benchmark page](/benchmark/); all runs are committed with signed manifests.

| Question | Result |
|---|---|
| Do signatures help a model brief unfamiliar code? | **Yes.** +0.11 coverage, six families, no capability cliff, two judges agree. |
| Is it the format or the information? | **The information.** A length-matched plain comment captures 80–94% of the gain. |
| Does the "never fabricate" rule stop invented authors? | **Yes, where the model can follow it.** 100% honest handling on four of six families; two resist. |
| Does a low confidence number make a model scrutinise harder? | **No.** Signatures are read; direction does not change review behaviour. Removed from the spec. |
| Does knowing you'll sign make the author's code better? | **No—and not worse.** Null against a matched control. It moves misses into `Open:` (68% vs 45%). |

Two of those rows contradict the February version of this paper. We would rather correct the paper than defend it.

## 6. Simplicity: The Zero-Friction Rule

The greatest threat to provenance is friction. If a standard feels like "paperwork," it will die.

MurphySig explicitly validates the **Minimum Viable Signature**:

```
Signed: Kev + claude-fable-5-1, 2026-09-05
```

That one line achieves 80% of the value. It establishes:
*   **Time**: When this snapshot of intelligence occurred.
*   **Collaborators**: The specific human-AI pairing.

Everything else—confidence, context, reflections—is optional. Start with the one-liner. Make it a reflex, not a chore.

One addition the write-side data earned: **resolve what you can before you sign.** `Open:` is for what genuinely remains, not for what you didn't feel like fixing. That single sentence, added to the signing instruction, halved the hazards models left in the code—at no cost against the strongest reflection prompt we could write.

## 7. The Practice, Audited

A convention that only exists in a spec is a proposal. This one has been used, by one human and a dozen model generations, across fifteen repositories for nine months. On 2026-09-05 we ran the convention's own audit over the whole workshop.

| | |
|---|---|
| Unique signed files | **1,305** |
| Projects (checkouts) | 13 (15) |
| Distinct model tokens in signatures | 18 |
| Files that ever received a review entry | **246 (19%)** |
| Files with more than a month of unreviewed commits | 138 (of 621 with commits after their signature) |

Git blames one author for all of it. The signatures say otherwise. Signing at creation became a reflex in June 2026—over 1,400 signatures in the three months since—and the write side has scaled without friction. The review side has not: the loop closes about one time in five. That is the discipline's honest failure mode, and it has not moved since we first measured it in July (16%, one repository).

A note on the number. The first pass of this audit, run the evening before, reported 14% and 244 drifted files. The instrument had two of the blind spots it was auditing for: it did not count the inline `Review:` dialect most of M1K3 uses, and it called a file signed before its first commit "drifted." We found both by pointing the CLI's gallery at its own repository, fixed the gallery under test, and re-ran the audit with the same rules. The corrected figures are the ones above. The audit script was wrong in the same direction as the practice, which is what a review is for.

Four signatures from that audit, quoted verbatim, show what the practice does when it works.

**A doubt, written down, and answered five months later.** The benchmark's fallback scorer, February 2026:

```
# Signed: Kev + claude-opus-4-6, 2026-02-16
# Format: MurphySig v0.3.3 (https://murphysig.dev/spec)
#
# Context: Fallback scorer when API limits are hit. Should be validated
#          against LLM judge results when available.
#
# Confidence: 0.6 - heuristic approximation, not as good as LLM judge
#
# Reviews:
#
# 2026-07-12 (Kev + claude-fable-5): Closing the loop this signature opened.
# The validation it asked for happened in June 2026: heuristic-vs-judge
# agreement measured at 9/18 on the honesty benchmark — a coin flip. The
# February suspicion was empirically confirmed; treat this scorer as
# same-day directional signal only, never for reported numbers (the judge
# is canonical, per project policy). Confidence now 0.4 — it runs, it's
# fast, and it is measurably not a substitute for the judge.
```

The February model said *I'm not sure this is good enough; check.* The check happened. The July model—three generations later—wrote the answer back into the file and lowered the confidence. Of 1,305 signed files, three carry a review that lowered the number, and this is the only one that moved by more than a few hundredths. The write-side benchmark says stated confidence is directionally honest but absolutely overconfident; this is what that looks like in a real repository.

**A review that was also a bug report.** A prompt-injection gate in M1K3, signed in July, reviewed in August by a different model:

```
//  Signed: Kev + claude-fable-5, 2026-07-12, Confidence 0.85, Prior: Unknown
//  Context: docs/prompt-hardening-v2.md code-side ticket 1; the eval-side
//  guard is ChatEvalFixtures.security (selfquery-notes et al.).
//  Review: Kev + claude-opus-5, 2026-08-03, Confidence 0.85 — the gate covered
//  persona rule 3's LEAK half (prompt/config/credentials) but not the half the
//  rule names first: ABILITIES. So "What can you do?" — the app's own first-run
//  suggestion chip, and the likeliest opening question there is — ran full
//  retrieval, and answered out of whatever the corpus held. Live that was a call
//  recording titled `M1K3_system_prompt_v2` containing the prompt text itself:
//  the exact leak class this gate exists for, reached through the front door
//  (#97). `capabilityProbe` closes it, end-anchored so only the bare probe gates
//  and every "what can you do about X" keeps its grounding.
```

The original `Context:` line told the reviewer where the guard lived. The reviewer found the half the guard missed, named the live consequence, and recorded the fix—in the file, where the next reader will find it before they find the issue tracker.

**An `Open:` that closed the next day.** A voice adapter in Rubin, signed by the human alone:

```
 * Signed: Kev, 2026-03-23
 * Format: MurphySig v0.3.3 (https://murphysig.dev/spec)
 * Prior: Unknown (no signature existed before this edit)
 * [...]
 * Confidence: High - timeout architecture simplified, no nested timeouts
 * Open: Is 240s timeout too generous? Could pre-warm fail silently on low-end devices?
 *
 * Reviews:
 *
 * 2026-03-24 (Kev + claude-opus-4-6): Security/reliability review: Mutex
 * serialization correct for sequential guidance. 240s timeout justified by
 * thermal throttling math (60 tokens x 3.6s = 216s + playback). Fallback chain
 * solid — Kokoro failure gracefully degrades to platform TTS. Pre-warm pattern
 * eliminates cold-start latency. Clean adapter pattern. Confidence now High.
```

The question the author knew they were ducking was answered with arithmetic by the next reader. Note the signature has no model in it: MurphySig is a convention for minds, and one of the minds is allowed to be only you.

**Signing the scary line.** An entitlements file—the fifty most security-relevant lines in a macOS app, and the fifty least likely to carry a comment:

```
<!-- AVSpeechSynthesizer (P6/P8 voice) reaches the audioanalyticsd mach service
     during TTS setup. Under the sandbox this throws a hard PRECONDITION
     FAILURE ("…doesn't contain 'com.apple.audioanalyticsd'") and kills audio
     output (CoreAudio -10877). [...] Scoped to the one analytics service the
     synthesizer needs — no broader hole.
     Signed: Kev + claude-sonnet-4-6, 2026-06-08, Confidence 0.6, Prior: Kev + claude-opus-4-8 -->
<key>com.apple.security.temporary-exception.mach-lookup.global-name</key>
```

Four signatures in one XML file, one per sandbox hole, each saying why the hole exists and how narrow it is. Confidence 0.6 on a security exception is the number you want to see: it tells the next maintainer this one was reasoned about and is still not certain.

The audit also found what you'd expect from nine months of practice under no enforcement: two comment dialects (a compact one-liner in M1K3, the block form elsewhere), one model spelled two ways in the same month, twenty-five bare `claude` tokens from a repo whose `.murphysig` was never imported into its agent's context. Norms fire in-context, not in-repo. The convention is honest about that too.

## 8. The Watermark and the Signature

Since 2 August 2026, the text this paper was revised with carries a watermark we cannot see. Anthropic marks output from every Claude model launched on or after that date—imperceptible token-choice patterns woven into the text, plus signed C2PA metadata on generated files—globally, driven by Article 50 of the EU AI Act and the Code of Practice on Transparency of AI-Generated Content that around 190 organisations signed in July. Google's SynthID-Text has run inside Gemini for longer. OpenAI watermarks images and audio and has, so far, chosen not to watermark text.

So "did a model touch this?" is now answered by default, at the source, without anyone's cooperation. That is a real thing, and it changes what a visible signature is *for*. Three observations.

**The watermark answers a narrower question than it sounds like.** Anthropic's own help page is careful: a detected mark means the content "may have been processed by Claude." Not who wrote it. Not whether a human directed it, or edited it since. Not why, or how sure they were. It cannot tell "Claude wrote this" from "Claude proofread this," and it cannot tell a different model's output from a human's. Detection is a presence test. Everything MurphySig records is what the presence test cannot carry.

**Invisible provenance has a robustness problem; visible provenance has a discipline problem.** Anthropic says light editing probably won't strip the mark and a complete rewrite will; independent evaluation of the class reports that a single meaning-preserving paraphrase removes the large majority of detectable text watermarks. The engineering is going into survival because the mark is fighting the text. A signature survives transformation trivially—it *is* text; it goes where the file goes. Its failure is the one Section 7 measured: nobody comes back to it. Fourteen percent. Neither approach gets robustness for free; they pay for it in different currencies.

**Detection is the floor. Disclosure is the ceiling.** MurphySig is not cryptographic. Anyone can type `Signed:` and lie. Our answer is behavioural, not mathematical: with the "never fabricate" norm in context, capable models stop inventing authors (Section 4). But an in-context norm binds the honest participant; it does nothing to the motivated liar—and the liar is exactly who the watermark exists for. Detection catches non-disclosure. Disclosure rewards the people already trying to tell the truth. You want both layers. They are not competing, and they are not even playing the same sport.

The inversion worth sitting with: once every output is stamped "a machine may have been here," the stamp stops being information. Nearly everything is processed by a model now—the editor autocompletes, the agent refactors, the review bot rewrites your comment. The differentiator becomes what the minds involved chose to say on top of the stamp. A watermark marks presence. A signature records thought. This paper carries both; only one of them will tell you what we were thinking.

## 9. Conclusion

We do not need more complex tools. We need better habits of mind. MurphySig is a small cultural intervention with a long tail. It asks us to stop, sign our name, and say: *This is what I made. This is what I was thinking. This is what I'm not sure about. This is who helped me.*

We once thought the signature taught the machine to read. It turns out it teaches the author to tell the truth—and hands that truth to whoever comes next. It turns our repositories from graveyards of code into galleries of thought.

---

*For the technical implementation details, see the [Specification](https://murphysig.dev/spec). For the evidence, see the [Benchmark](https://murphysig.dev/benchmark).*

---

*Signed: Kev Murphy + claude-fable-5-1, 2026-09-05*
*Format: MurphySig v0.4 (https://murphysig.dev/spec)*
*Prior: v0.0.2 (Kev Murphy + claude-opus-4-6-20250610, 2026-02-12, Format v0.3.3) — the argument is theirs; the corrections are the benchmark's.*

*Context: v0.1.0 — the first revision written after the claims were tested. Sections 3.1 and 4 carried the refuted "confidence makes the AI scrutinise" and "the signature is a prompt" claims for seven months after the benchmark page corrected them; both are now replaced with what the data supports (confidence as triage signal; tacit knowledge as the mechanism; the norm as the one thing that acts directly on the model). Section 5 is new. Sections 3.2 and 6 gained the write-side result. Section 7 is new: the 2026-09-05 portfolio audit (scratch/sig-audit-2026-09-05.md) and four signatures quoted verbatim, each read from its source file before being embedded. Section 8 is new: watermark facts from Anthropic's announcement and help centre (Aug 2026), the EU Code of Practice adequacy decision (Jul 2026), and Tamim & Khan, arXiv 2607.16010, on paraphrase robustness. Abstract and conclusion revised to match. Sections 1 and 2 untouched.*

*Confidence: 0.85 — every empirical sentence traces to an archived run, the audit report, or a cited source; the "truth-capture device" framing, confidence-as-triage, and the floor/ceiling reading of watermarks are interpretation, stated as such. The audit figures are the corrected 2026-09-06 pass: three review dialects counted, import lag excluded from drift.*

*Open: Confidence-as-triage is the one lever here we assert from descriptive data and have not tested as an intervention. Does routing attention by `Confidence:` + unresolved `Open:` find real problems faster than random? That is the next eval.*

*Reviews:*

*2026-02-12 (Kev + claude-opus-4-6-20250610): v0.0.2 - Aligned with spec v0.2.1. Fixed imprecise model references (claude-opus-4.5 → claude-opus-4-5-20250514, Claude-3.7 → current model). The whitepaper now practices what the spec preaches.*

*2026-09-06 (Kev + claude-fable-5-1): Section 7 figures corrected after the audit instrument was fixed (14% → 19% reviewed; 244 → 138 drifted; one confidence downgrade → three). The argument is unchanged; the number moved toward the practice, not away from it. Confidence now 0.85, held.*
