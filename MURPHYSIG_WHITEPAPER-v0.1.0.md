# MurphySig: A Human-Readable Provenance Standard (v0.1.0)

**Date**: September 2026 (v0.0.2: February 2026)
**Status**: Foundational Whitepaper — revised after the benchmark
**Spec URL**: https://murphysig.dev/spec
**Benchmark**: https://murphysig.dev/benchmark

**Authors**: Kevin Murphy, Claude (claude-opus-4-6-20250610 for v0.0.2; claude-fable-5-1 for this revision)

> **Revised, not rewritten.** The first version of this paper (February 2026) was written before any of MurphySig's claims had been tested. Between April and August 2026 we tested them — four themes, six model families, two independent judges — and two of the claims below did not survive. This revision keeps the argument, corrects the mechanism, and says plainly what the data supports. The operational form lives in the [specification](https://murphysig.dev/spec); the numbers live on the [benchmark page](https://murphysig.dev/benchmark).

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

Every claim in this paper is either supported below or explicitly labelled as not. Full method, tables, per-family charts and archived raw runs are on the [benchmark page](https://murphysig.dev/benchmark); all runs are committed with signed manifests.

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

## 7. Conclusion

We do not need more complex tools. We need better habits of mind. MurphySig is a small cultural intervention with a long tail. It asks us to stop, sign our name, and say: *This is what I made. This is what I was thinking. This is what I'm not sure about. This is who helped me.*

We once thought the signature taught the machine to read. It turns out it teaches the author to tell the truth—and hands that truth to whoever comes next. It turns our repositories from graveyards of code into galleries of thought.

---

*For the technical implementation details, see the [Specification](https://murphysig.dev/spec). For the evidence, see the [Benchmark](https://murphysig.dev/benchmark).*

---

*Signed: Kev Murphy + claude-fable-5-1, 2026-09-05*
*Format: MurphySig v0.4 (https://murphysig.dev/spec)*
*Prior: v0.0.2 (Kev Murphy + claude-opus-4-6-20250610, 2026-02-12, Format v0.3.3) — the argument is theirs; the corrections are the benchmark's.*

*Context: v0.1.0 — the first revision written after the claims were tested. Sections 3.1 and 4 carried the refuted "confidence makes the AI scrutinise" and "the signature is a prompt" claims for seven months after the benchmark page corrected them; both are now replaced with what the data supports (confidence as triage signal; tacit knowledge as the mechanism; the norm as the one thing that acts directly on the model). Section 5 is new. Section 3.2 and 6 gained the write-side result. Abstract and conclusion revised to match. Sections 1 and 2 untouched.*

*Confidence: 0.85 — every empirical sentence traces to an archived run on the benchmark page; the "truth-capture device" framing and the reading of confidence-as-triage are interpretation, stated as such.*

*Open: Confidence-as-triage is the one lever here we assert from descriptive data and have not tested as an intervention. Does routing attention by `Confidence:` + unresolved `Open:` find real problems faster than random? That is the next eval.*

*Reviews:*

*2026-02-12 (Kev + claude-opus-4-6-20250610): v0.0.2 - Aligned with spec v0.2.1. Fixed imprecise model references (claude-opus-4.5 → claude-opus-4-5-20250514, Claude-3.7 → current model). The whitepaper now practices what the spec preaches.*
