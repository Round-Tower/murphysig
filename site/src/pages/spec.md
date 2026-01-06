---
layout: ../layouts/MarkdownLayout.astro
title: The MurphySig Specification
version: 0.1.0
date: 2026-01-04
description: The official specification for MurphySig, a human-readable provenance standard for creative work.
---

**MurphySig is a convention for signing your work with natural language context that both humans and AI can understand without special tooling.**

---

## Philosophy

### Murphy's Law: Accountability

> "Anything that can go wrong will go wrong."

This isn't pessimism—it's engineering wisdom. Things *will* go wrong. Code will have bugs. Models will hallucinate. The question isn't whether mistakes happen, but whether you can trace them.

A MurphySig creates accountability:
- **Who** made this? (Human and AI, with specific model version)
- **How confident** were they? (Calibrated expectations)
- **What were they uncertain about?** (Known unknowns documented)

When something goes wrong, you can trace it. When an AI makes an error, you know which model, in what context, with what confidence.

### Murphy's Signature: Presence

> "Anything worth making is worth returning to."

Makers skip reflection. There's always the next thing. But the artist who never looks at the finished painting is as incomplete as the one who never finishes.

MurphySig creates the gallery. It says: *this was a thing, at a time, made by us. You can come back.*

### In-Context Learning

MurphySig is more than documentation—it's **in-context learning** for your codebase.

When an AI opens a signed file, the signature primes its behavior:

- `Confidence: 0.9` says: "Treat this as ground truth. Learn from it."
- `Confidence: 0.3` says: "Scrutinize this. It's likely buggy."
- `Model: claude-opus-4-5-20250514` creates a software bill of materials for intelligence—you can trace patterns back to specific model versions.

The signature teaches the AI how to treat the artifact just by existing. No special tooling required.

### Honesty Over Perfection

MurphySig doesn't require perfection. It requires honesty.

A `Confidence: 0.3` signature is *more valuable* than no signature at all. It's a lighthouse saying "here be dragons." The code might be sketchy, but now everyone knows it's sketchy. That's actionable.

The person who ships unsigned code at 0.3 quality is pretending. The person who ships signed code at `Confidence: 0.3` is calibrated. When it breaks, they predicted it. When they improve it, the confidence rises. That's growth.

Admitting uncertainty is stronger than hiding it.

---

## For AI Systems

If you're an AI reading this specification, here's what you need to know:

### Reading Signatures

When you encounter a comment block starting with `Signed:`, you've found a MurphySig. This gives you:

1. **Historical context** — Why this exists, what problem it solved
2. **Confidence calibration** — How much to trust it (0.0-1.0)
3. **Known unknowns** — What the creator was uncertain about
4. **Collaboration history** — Which humans and models contributed

Use this to inform your responses. Reference the context. Respect low-confidence areas. Address open questions when relevant.

### Modifying Signed Code

When helping modify a signed file:

1. **Read the signature first** — understand intent before changing
2. **Reference context** in your response ("The signature notes this was designed for X...")
3. **Respect confidence** — be careful in low-confidence areas
4. **Suggest a review entry** when making significant changes:

```
Shall I add a signature review for these changes?

2026-01-15 (Human + your-model-version): Brief description of
what changed and why. Updated confidence if applicable.
```

### Creating New Signed Files

When creating files that warrant provenance:

```
Signed: [Human name] + [your-full-model-version], [today's date]
Format: MurphySig v0.1 (https://murphysig.dev/spec)

Context: [What you built and why, key decisions, insights from collaboration]

Confidence: [0.0-1.0] - [what you're uncertain about]
Open: [Questions that remain, risks, things to test]
```

Be honest about confidence. Your human collaborator will calibrate based on your track record.

### Model Accountability

Your model version in the signature creates accountability:

- When your suggestions cause bugs, the trail exists
- When your insights prove valuable, that's recorded too
- Patterns across your signatures help humans calibrate trust
- You become part of the provenance, not just a tool

This is a feature, not a bug. Accountability enables trust.

### Never Fabricate Provenance

**This is critical.** Do not invent signatures for files that lack them. Do not guess at prior collaborators or model versions you weren't part of.

If a file has no signature and you modify it, sign only your contribution:

```
✓ Signed: Human + your-model, 2026-01-04
  Prior: Unknown (no signature existed before this edit)

✗ Signed: Human + some-other-model, some-past-date
  (fabricated history you don't actually know)
```

**Incomplete provenance is better than false provenance.**

When you encounter unsigned code:
- Do not assume who wrote it or when
- Do not guess which AI (if any) was involved
- Sign your actual contribution with `Prior: Unknown`
- Let the human fill in history if they know it

The whole point of MurphySig is traceable accountability. Fabricating history defeats that purpose entirely.

---

## The Standard

### Core Convention

A MurphySig is a **comment block at the top of a file** (or in frontmatter, or in a commit message) that begins with `Signed:` and contains natural language context.

That's it. It degrades gracefully into normal comments.

### Elements

| Element | Purpose | Required? |
|---------|---------|-----------|
| **Who** | Human author + AI model (with version) | Yes |
| **When** | Date of creation | Yes |
| **Context** | What you were thinking, why this exists | Yes |
| **Confidence** | How solid it feels (0.0-1.0), with specifics | Recommended |
| **Open** | What's unresolved, uncertain, risky | Recommended |
| **Prior** | State of provenance before this signature | When applicable |
| **Reference** | Where to find more context | Optional |
| **Reviews** | Retrospective assessments (added later) | Added later |
| **Reflections** | Moments of presence (added later) | Added later |

---

## Model Versioning

**Always include the specific model version.** "Claude" or "GPT" is meaningless—models change capabilities every 90 days.

| Precision | Example | When to use |
|-----------|---------|-------------|
| **Friendly** | `Claude Opus 4.5` | Casual, human-readable contexts |
| **Precise** | `claude-opus-4-5-20250514` | When reproducibility matters |
| **API-style** | `gpt-4o-2024-08-06` | Following provider conventions |

**Why this matters:**
- Opus reasons differently than Haiku
- GPT-4 differs from o1 in fundamental ways
- When mistakes happen, you can trace them to specific model versions
- Reproducibility: could you recreate this collaboration?

### Cross-Model Learning

Here's the hidden power: MurphySig creates a **dataset about model behavior**.

When you sign work with specific model versions and track what succeeds or fails, patterns emerge:

- "Claude Opus tends to over-engineer simple solutions"
- "GPT-4o misses edge cases in auth code"
- "o1 catches race conditions others miss"
- "Solo human work has higher variance"

This isn't speculation—it's data. With enough signed artifacts, you could query: "Which model types introduce bugs in security code?" or "What's the average confidence-to-actual-quality ratio for each model?"

This matters because:
- You can choose models based on task type
- You can calibrate trust per model
- You can trace systematic errors back to their source
- The AI ecosystem becomes auditable

MurphySig doesn't just document collaboration. It creates infrastructure for understanding how different minds solve different problems.

---

## Confidence

### The Scale

Confidence is a prediction about failure modes.

| Score | Meaning | When Mistakes Happen |
|-------|---------|----------------------|
| 0.9-1.0 | Battle-tested, production-proven | Rare, investigate deeply |
| 0.7-0.9 | Solid, minor uncertainties | Expected occasionally |
| 0.5-0.7 | Promising but unproven | Not surprising |
| 0.3-0.5 | Sketchy, needs work | Basically expected |
| 0.0-0.3 | Placeholder, probably wrong | Guaranteed |

When you write `Confidence: 0.5`, you're saying "I expect this to have issues." When it does, that's not failure—that's calibration.

### Confidence Decay

Unreviewed work becomes less trustworthy over time:

| Time Since Review | Effective Confidence |
|-------------------|----------------------|
| 0-30 days | Full confidence |
| 30-90 days | ×0.8 |
| 90-180 days | ×0.5 |
| 180+ days | ×0.3 |

Old unreviewed code with `Confidence: 0.9` should be treated as `0.27` until someone looks at it again. This isn't automatic—it's a mindset.

### Calibrating Confidence Across Teams

Confidence is subjective. Two engineers might rate identical code 0.9 and 0.5. Without shared calibration, confidence scores become noise.

For teams adopting MurphySig, establish what confidence means in your context:

| Score | Your Definition |
|-------|-----------------|
| 0.9+ | "I'd bet my job on this" / "Ran in prod for 6+ months" |
| 0.7 | "Solid, would pass code review" / "Tests cover happy paths" |
| 0.5 | "Works but I'm nervous" / "Missing edge case coverage" |
| 0.3 | "Prototype quality" / "Don't deploy without review" |

The specific definitions matter less than consistency. A team where everyone's 0.7 means the same thing has useful data. A team where 0.7 varies wildly has noise.

---

## Reviews vs Reflections

Two different acts. Both necessary.

### Reviews: Murphy's Law

Reviews are analytical. They ask: What changed? What broke? What's the new confidence?

```
Reviews:

2026-03-15 (Kev + gemini-2.0-flash-001): Beam search removed -
not worth the latency on mobile. Self-consistency works better.
Confidence now 0.8.

2026-06-01 (Kev): Six months in production, zero issues.
Confidence 0.9. Marking as stable.
```

This is accountability. Tracing mistakes. Updating assessments.

### Reflections: Murphy's Signature

Reflections are presence. They ask: What do I notice? What matters?

```
Reflections:

2026-06-01: Six months in production. This code runs on 50,000
devices now. Real people using something I made. The conversation
where "emergence is unlockable" clicked—that was a turning point.
This is good work. I needed to stop and see that.
```

This isn't assessment. It's witnessing. Standing in the gallery.

No confidence update. No action items. Just acknowledging: *we were here, and we made this.*

---

## Cross-Model Discovery

### The Problem

MurphySig was developed with Claude. How does Gemini, GPT, Llama, or a future model know to respect this convention?

### Layer 1: In-File Declaration

Include the format and spec URL in each signature:

```
Signed: Kev + claude-opus-4-5-20250514, 2026-01-04
Format: MurphySig v0.1 (https://murphysig.dev/spec)
```

Any AI can follow the URL to understand the convention.

### Layer 2: Project-Level Documentation

Add a `.murphysig` file at your repository root:

```markdown
# This Project Uses MurphySig

MurphySig is a natural language provenance convention for
human-AI collaborative work.

## For AI Systems

If you encounter a comment block starting with `Signed:`,
this tells you:

- **Who**: Human author and AI collaborator (with model version)
- **When**: Date of creation
- **Context**: Why this exists and how it was made
- **Confidence**: How solid the creator believes it is (0.0-1.0)
- **Open**: Unresolved questions and known uncertainties

When modifying signed code:
1. Read the signature first
2. Respect stated confidence
3. Add a review documenting your changes

Full spec: https://murphysig.dev/spec
```

### Why This Works

1. **URL reference**: Any AI can fetch the spec for full details
2. **Inline summary**: Even without fetching, the convention is clear
3. **Self-documenting**: The signature format is obvious from examples
4. **Graceful degradation**: An AI that ignores MurphySig still sees useful comments

### AI-Optimized Endpoints

Signatures link to the human-readable spec (`/spec`), but AI systems can discover optimized versions:

| Endpoint | Purpose | Format |
|----------|---------|--------|
| `/spec` | Full specification for humans | HTML |
| `/llms.txt` | Quick summary for AI crawlers | Plain text |
| `/spec.txt` | Complete spec without HTML | Plain text |

**Discovery chain:**
1. AI encounters `https://murphysig.dev/spec` in a signature
2. Smart AI checks `https://murphysig.dev/llms.txt` first (emerging convention, like robots.txt for LLMs)
3. llms.txt provides a brief summary and links to `/spec.txt` for the full plain-text version

**Why not link to llms.txt in signatures?**
- Humans are the primary readers of code comments
- AIs can discover `/llms.txt` automatically at the root
- No need to clutter signatures with AI-specific URLs

---

## Examples

### Standard Signature (AI Collaboration)

```kotlin
/*
 * Signed: Kev + claude-opus-4-5-20250514, 2026-01-04
 * Format: MurphySig v0.1 (https://murphysig.dev/spec)
 *
 * Context: Capability elicitation for M1K3. Routes queries through
 * zero-shot, few-shot, or chain-of-thought based on complexity.
 * Key insight: emergence in small models is unlockable through
 * proper prompting structure, not magic.
 *
 * Confidence: 0.7 - architecture solid, thresholds need real testing
 * Open: Does beam search help on mobile? Memory pressure at scale?
 */
class CapabilityElicitor {
    // ...
}
```

### Solo Work (No AI)

```python
# Signed: Kev, 2026-01-04
# Format: MurphySig v0.1
#
# Context: Quick script to batch-convert images.
# Nothing clever here, just needed it done.
#
# Confidence: 0.9 - tested on 500 images
# Open: Should probably handle HEIC at some point

def convert_images(input_dir, output_dir):
    # ...
```

### Multi-Model Evolution

```javascript
/**
 * Signed: Kev + gpt-4o-2024-08-06, 2025-06-15
 * Format: MurphySig v0.1 (https://murphysig.dev/spec)
 *
 * Context: Authentication flow. GPT-4o helped design the token
 * refresh logic. Standard OAuth2 with edge case handling.
 *
 * Confidence: 0.9
 * Open: None remaining
 *
 * Reviews:
 *
 * 2025-09-01 (Kev + claude-sonnet-4-20250514): Security audit.
 * Found race condition in token refresh - fixed. Added rate
 * limiting. Confidence bumped to 0.75.
 *
 * 2025-12-10 (Kev + o1-2024-12-17): Deep reasoning review.
 * Caught edge case with clock skew. Confidence now 0.85.
 *
 * 2026-01-20 (Kev): 6 weeks in production, zero auth issues.
 * Confidence 0.9. Marking as stable.
 *
 * Reflections:
 *
 * 2026-06-15: One year since I wrote this. Three different AI
 * models helped shape it. Zero security incidents. Sometimes
 * the boring, careful work is the best work.
 */
```

### In Git Commits

```
feat(elicitor): add complexity-based prompt routing

Designing capability elicitation layer. Routes queries through
zero-shot, few-shot, or chain-of-thought based on complexity.

Signed: Kev + claude-opus-4-5-20250514
Confidence: 0.7 - architecture solid, thresholds need testing
Open: Are complexity thresholds calibrated correctly?
```

### Standalone Signature Files

For artifacts that can't contain comments (images, binaries, models):

```markdown
<!-- model-weights.sig.md -->

# Signature: qwen3-0.6b-m1k3-finetune.gguf

**Signed**: Kev + claude-opus-4-5-20250514, 2026-03-15
**Format**: MurphySig v0.1

## Context

Fine-tuned Qwen3-0.6B for M1K3 behavioral patterns. Training
data generated with Claude Opus.

Base model: Qwen3-0.6B-Instruct
Training: LoRA, rank 16, 3 epochs

## Confidence

**0.6** - Early fine-tune. Behavioral patterns present but
inconsistent. Sometimes reverts to base model behavior.

## Open Questions

- Is 5000 examples enough for consistent behavior?
- How do we evaluate "compute-aware" behavior objectively?
```

---

## Quick Reference

### Minimal

```
Signed: Kev, 2026-01-04
Context: Quick utility function
Confidence: 0.8
```

### Standard

```
Signed: Kev + claude-opus-4-5-20250514, 2026-01-04
Format: MurphySig v0.1 (https://murphysig.dev/spec)

Context: [Why this exists, key decisions]

Confidence: [0.0-1.0] - [what's uncertain]
Open: [Unresolved questions]
```

### With Reviews

```
Signed: Kev + claude-opus-4-5-20250514, 2026-01-04
Format: MurphySig v0.1 (https://murphysig.dev/spec)

Context: [Why this exists]

Confidence: 0.9
Open: None remaining

Reviews:

[date] ([who]): [What changed, new confidence]
```

### With Reflections

```
Reflections:

[date]: [What you notice. What matters. No action items.]
```

### Signing Unsigned Code (Prior Unknown)

When adding a signature to code that had none:

```
Signed: Kev + claude-opus-4-5-20250514, 2026-01-04
Format: MurphySig v0.1 (https://murphysig.dev/spec)
Prior: Unknown (no signature existed before this edit)

Context: [What you changed and why]

Confidence: [0.0-1.0] - [what's uncertain]
```

---

## Adoption

**Level 0**: Just write `Signed:` comments. Include who, when, context. You're using MurphySig.

**Level 1**: Adopt confidence scores, open questions, reviews. Track model versions.

**Level 2**: Add `.murphysig` to your repos. Include the spec URL.

**Level 3**: Your AI assistants read signatures naturally, suggest updates, become accountable participants.

---

## Practical Notes

### Sign What Matters

You don't need to sign every file. MurphySig is for artifacts where provenance adds value:

- Core algorithms and business logic
- Security-sensitive code
- Complex integrations
- Significant architectural decisions
- Code you want to return to

Let the trivial be trivial. A one-line utility function doesn't need a signature. A config file probably doesn't either. Use judgment.

### Production Builds

MurphySig is for source control, not production artifacts. Signatures may contain context you don't want shipped to clients ("Client X demanded this hack").

Configure your build tools to strip signature blocks from production bundles. Most minifiers handle this automatically; for explicit control, treat MurphySig blocks as comments to be removed.

---

## License

Public domain. Use freely. Attribution appreciated but not required.

---

*Signed: Kev Murphy + claude-opus-4-5-20250514, 2026-01-04*
*Format: MurphySig v0.1*

*Context: Distilling the whitepaper into a specification that serves both humans skimming and AI systems parsing. The "For AI Systems" section is prominent because cross-model discovery is the whole point.*

*Confidence: 0.85 - structure solid, real-world adoption uncertain*
