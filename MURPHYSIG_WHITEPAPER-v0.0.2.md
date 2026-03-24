# MurphySig: A Human-Readable Provenance Standard (v0.0.2)

**Date**: February 2026
**Authors**: Kevin Murphy, Claude (claude-opus-4-6-20250610)
**Status**: Foundational Whitepaper
**Spec URL**: https://murphysig.dev/spec

---

## Abstract

As we enter the era of ubiquitous AI collaboration, the provenance of our creative work is disappearing. Code, prose, and art are becoming black boxes—outputs without history. MurphySig is a proposal to reclaim that history. It is a convention for signing work with natural language context that is legible to both humans and machine intelligence. It imposes no tooling requirements, only a cultural one: that the *process* of creation is as valuable as the artifact itself.

---

## 1. The Problem: The Streaming Now

The velocity of modern software engineering and content creation has eliminated reflection. We ship and move on. "Done" is a boolean state, not a documented journey.

Simultaneously, we are collaborating with AI systems that have no continuity. A conversation with Claude or GPT is ephemeral; once the window closes, the context vanishes. The next model version will not know why a decision was made, only that code exists.

We are building in the dark, leaving no breadcrumbs for our future selves or the future intelligences that will maintain our work. We face **The Gallery Problem**: an endless stream of creation with no structure to revisit, witness, or learn from what we have made.

## 2. The Solution: Legible Provenance

MurphySig proposes a simple standard: a **structured natural language comment block** at the beginning of any artifact.

It is **not cryptographic**. It does not prove authorship in a legal sense.
It is **semantic**. It explains *intent*, *uncertainty*, and *collaboration*.

By signing our work with specific model versions (e.g., `claude-opus-4-5-20250514`), confidence scores, and context, we create two things:
1.  **Accountability (Murphy's Law)**: A trace of what went wrong when it inevitably does.
2.  **Presence (Murphy's Signature)**: A trace that we were here, witnessing our own craft.

## 3. Philosophy

### 3.1 The Law: "Anything that can go wrong, will."
This is not pessimism; it is engineering reality. When we hide uncertainty, we create fragility. MurphySig demands we document our **Confidence**—whether numerical (`0.7 - architecture solid, thresholds need testing`) or text (`Solid but untested at scale`).

This transforms uncertainty from a liability into data. When an AI system reads a file signed with `Confidence: 0.3`, it treats that code differently than `Confidence: 0.9`. It learns.

### 3.2 The Signature: "Anything worth making is worth returning to."
The "Signature" is the act of presence. It is the creator acknowledging the work. The standard includes a **Reflections** section—not for debugging, but for witnessing. "I wrote this late at night," or "This was the moment it clicked." This humanizes the codebase and breaks the relentless forward march of "shipping."

## 4. The Mechanism: In-Context Learning for the Future

MurphySig is designed as **in-context learning** for future AI.

When a future model reads a file from 2026, the MurphySig tells it:
*   Which specific model version contributed (calibrating its trust in the code patterns).
*   What the human intended (bridging the gap between implementation and goal).
*   What was known to be shaky (directing attention to likely bugs).

The signature is not metadata; it is a prompt. It teaches the future how to treat the past.

## 5. Simplicity: The Zero-Friction Rule

The greatest threat to provenance is friction. If a standard feels like "paperwork," it will die.

MurphySig explicitly validates the **Minimum Viable Signature**:

```
Signed: Kev + claude-opus-4-6-20250610, 2026-02-12
```

That one line achieves 80% of the value. It establishes:
*   **Time**: When this snapshot of intelligence occurred.
*   **Collaborators**: The specific human-AI pairing.

Everything else—confidence, context, reflections—is optional. Start with the one-liner. Make it a reflex, not a chore.

## 6. Conclusion

We do not need more complex tools. We need better habits of mind. MurphySig is a small cultural intervention with a long tail. It asks us to stop, sign our name, and say: *This is what I made. This is what I was thinking. This is who helped me.*

It turns our repositories from graveyards of code into galleries of thought.

---

*For the technical implementation details, see the [Specification](https://murphysig.dev/spec).*

---

*Signed: Kev Murphy + claude-opus-4-6-20250610, 2026-02-12*
*Format: MurphySig v0.3.3 (https://murphysig.dev/spec)*

*Context: v0.0.2 whitepaper evolution. Aligned model version references with spec guidance (precise IDs, not friendly names). Added text confidence as equal to numerical. Updated minimum viable example to current date and model.*

*Confidence: 0.9 - surgical fixes only, core argument unchanged*

*Reviews:*

*2026-02-12 (Kev + claude-opus-4-6-20250610): v0.0.2 - Aligned with spec v0.2.1. Fixed imprecise model references (claude-opus-4.5 → claude-opus-4-5-20250514, Claude-3.7 → current model). The whitepaper now practices what the spec preaches.*
