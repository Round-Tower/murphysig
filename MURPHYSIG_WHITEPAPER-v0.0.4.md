# MurphySig: A Human-Readable Provenance Standard for Creative Work

**Version**: 0.1.0  
**Authors**: Kev Murphy, Claude (claude-opus-4-5-20250514)  
**Date**: January 2026  
**Status**: Draft Specification  
**Spec URL**: https://murphysig.dev/spec

---

## The One-Sentence Version

**MurphySig is a convention for signing your work with natural language context that both humans and AI can understand without special tooling.**

---

## Philosophy

### Murphy's Law Reconsidered

**Murphy's Law**: "Anything that can go wrong, will."

This isn't pessimism—it's engineering wisdom. Things *will* go wrong. Code will have bugs. Assumptions will be invalidated. Models will hallucinate. The question isn't whether mistakes happen, but whether you can trace them, learn from them, and fix them.

**Murphy's Signature**: "Anything worth making is worth returning to."

Not just when it breaks. Not just to debug. To *witness*.

A MurphySig creates two things:

**Accountability** (Murphy's Law):
- **Who** made this? (Human and AI, with specific model version)
- **How confident** were they? (Calibrated expectations)
- **What were they uncertain about?** (Known unknowns documented)
- **What actually happened?** (Reviews capture the evolution)

When something goes wrong, you can trace it. When an AI makes an error, you know which model, in what context, with what confidence. When you make an error, you can see what you were thinking and why.

Provenance isn't about credit. It's about learning.

**Presence** (Murphy's Signature):
- Did I stop to see what I made?
- Do I acknowledge my past abilities?
- Can I smell the roses?

Makers skip this step. There's always the next thing. Pausing feels indulgent. But the artist who never looks at the finished painting is as incomplete as the one who never finishes. The reflection section legitimizes the pause. It says: this is part of the practice, not a distraction from it.

### The Gallery Problem

> "An artist should only worry about the output, after the art is created." — Rick Rubin

The problem: "after" requires a structure that captures the output so you can return to it. Without that structure, there is no "after"—just an endless stream of now.

**Creators** ship and move on. The velocity of modern work eliminates reflection.

**AI systems** have no continuity between sessions. Each conversation starts fresh. New models emerge every 90 days—Claude Opus 4.5 is not Claude Sonnet 4, is not GPT-4o, is not Gemini 2.0.

MurphySig creates the gallery. It says: *this was a thing, at a time, made by specific collaborators, with specific confidence. You can come back.*

### Why Natural Language?

Structured schemas require:
- Learning a format
- Tooling to parse
- Instructions for AI to "respect the schema"
- Friction at every step

Natural language requires nothing. An AI reading a signed file **naturally understands** the context. A human skimming the code **naturally sees** what matters. The nuance lives in the prose, not the structure.

The signature teaches you how to treat the artifact just by existing.

---

## The Standard

### Core Convention

A MurphySig is a **comment block at the top of a file** (or in frontmatter, or in a commit message) that begins with `Signed:` and contains natural language context.

That's it.

### What to Include

| Element | Purpose | Required? |
|---------|---------|-----------|
| **Who** | Human author + AI model (with version) | Yes |
| **When** | Date of creation | Yes |
| **Context** | What you were thinking, why this exists | Yes |
| **Confidence** | How solid it feels (0.0-1.0), with specifics | Recommended |
| **Open** | What's unresolved, uncertain, risky | Recommended |
| **Reference** | Where to find more context | Optional |
| **Reviews** | Retrospective assessments: what changed, what broke | Added later |
| **Reflections** | Moments of presence: witnessing what you made | Added later |

### Model Versioning

**Always include the specific model version.** "Claude" or "GPT" is meaningless—models change capabilities every 90 days.

| Precision | Example | When to use |
|-----------|---------|-------------|
| **Friendly** | `Claude Opus 4.5` | Casual, human-readable contexts |
| **Precise** | `claude-opus-4-5-20250514` | When reproducibility matters |
| **API-style** | `gpt-4o-2024-08-06` | Following provider conventions |

Use the provider's naming convention. Include enough detail that someone could identify the exact model capabilities at the time of creation.

**Why this matters:**
- Opus reasons differently than Haiku
- GPT-4 differs from o1 in fundamental ways
- Model capabilities change—knowing *which* model calibrates trust
- When mistakes happen, you can trace them to specific model versions
- Reproducibility: could you recreate this collaboration?

---

## Examples

### In Code (Any Language)

```kotlin
/*
 * Signed: Kev + claude-opus-4-5-20250514, 2026-01-04
 * Format: MurphySig v0.1 (https://murphysig.dev/spec)
 * 
 * Context: Designing capability elicitation for M1K3. Key insight - 
 * emergence in small models isn't magic, it's unlockable through 
 * proper prompting structure. This routes queries through zero-shot,
 * few-shot, or chain-of-thought based on detected complexity.
 * 
 * Confidence: 0.7 - architecture feels solid, thresholds need testing
 * Open: Does beam search actually help on mobile? Memory pressure?
 * 
 * See: conversation 2026-01-04, M1K3 architecture session
 */
class CapabilityElicitor {
    // ...
}
```

```python
# Signed: Kev, 2026-01-04
# Format: MurphySig v0.1
# 
# Context: Quick script to batch-convert images for Lexy. 
# Nothing clever here, just needed it done. No AI assist.
# 
# Confidence: 0.9 - it works, tested on 500 images
# Open: Should probably handle HEIC at some point

def convert_images(input_dir, output_dir):
    # ...
```

```swift
/// Signed: Kev + claude-sonnet-4-20250514, 2025-09-15
/// Format: MurphySig v0.1 (https://murphysig.dev/spec)
/// 
/// Context: Core chunking algorithm for Lexy. Breaks text into 
/// semantic units based on prosody and clause boundaries. This is
/// the heart of the reading experience - users with dyslexia 
/// process chunks better than continuous text.
/// 
/// Confidence: 0.65 - works well for English, RTL languages struggle
/// Open: Should we chunk by prosody or syntax? Users split on this.
/// 
/// Reviews:
/// 
/// 2026-01-04 (Kev + gemini-2.0-flash-001): RTL support more urgent
/// than expected. Israeli users reporting issues. Explored solutions
/// with Gemini - need per-language boundary detection. Confidence
/// still 0.65 but clearer on the path forward.
/// 
/// 2026-02-20 (Kev): Implemented RTL support based on earlier 
/// research. Tested with Hebrew and Arabic speakers. Bumping
/// confidence to 0.8. Closing the RTL question.
///
/// Reflections:
///
/// 2026-04-15: A year since the first version. This code runs in
/// 120 countries now. Kids are reading better because of these
/// 400 lines. I remember writing this in Cork, late night, not
/// sure if the prosody approach would work. It did. This is good work.

class ChunkingEngine {
    // ...
}
```

### Multi-Model Evolution

Notice how the signature captures the full history:

```javascript
/*
 * Signed: Kev + gpt-4o-2024-08-06, 2025-06-15
 * Format: MurphySig v0.1 (https://murphysig.dev/spec)
 * 
 * Context: Authentication flow for the admin panel. GPT-4o helped
 * design the token refresh logic. Pretty standard OAuth2 but with
 * some edge cases around expired sessions.
 * 
 * Confidence: 0.6 - works but security code always makes me nervous
 * Open: Should we add rate limiting? Token rotation period?
 * 
 * Reviews:
 * 
 * 2025-09-01 (Kev + claude-sonnet-4-20250514): Security audit.
 * Claude found a potential race condition in token refresh - fixed.
 * Added rate limiting. Confidence now 0.75.
 * 
 * 2025-12-10 (Kev + o1-2024-12-17): Deep reasoning review before
 * production deploy. o1 suggested additional validation on redirect
 * URIs - implemented. Also caught an edge case with clock skew.
 * Confidence now 0.85. Ready for production.
 * 
 * 2026-01-20 (Kev): 6 weeks in production, zero auth issues.
 * Confidence 0.9. Marking as stable.
 */
```

This tells a story: GPT-4o for initial design, Claude for security audit, o1 for deep reasoning review, then production validation. Each model contributed what it's good at.

### In Markdown Frontmatter

```markdown
---
title: M1K3 Architecture Overview
signed: Kev + claude-opus-4-5-20250514, 2026-01-04
format: MurphySig v0.1
confidence: 0.75
---

# M1K3 Architecture

**Context**: This document captures the architecture decisions for M1K3,
a privacy-first edge AI assistant. Key insight from this session - 
the "mechanic" framing (knows the machine, knows the driver) is more
useful than "assistant" framing.

**Open**: How do we handle the transition between model tiers gracefully?

---

## Overview
...
```

### In Git Commits

```
feat(elicitor): add complexity-based prompt routing

Designing capability elicitation layer. Routes queries through 
zero-shot, few-shot, or chain-of-thought based on detected complexity.

Signed: Kev + claude-opus-4-5-20250514
Confidence: 0.7 - architecture solid, thresholds need real-world testing
Open: Are complexity thresholds calibrated correctly?
See: M1K3 architecture session, 2026-01-04
```

### Standalone Signature Files

For artifacts that can't contain comments (images, binaries, datasets):

```markdown
<!-- model-weights.sig.md -->

# Signature: qwen3-0.6b-m1k3-finetune.gguf

**Signed**: Kev + claude-opus-4-5-20250514, 2026-03-15  
**Format**: MurphySig v0.1

## Context

Fine-tuned Qwen3-0.6B for M1K3 behavioral patterns. Training data 
generated with Claude Opus - 5000 synthetic conversations exhibiting
compute-aware responses, deferred processing suggestions, and 
appropriate confidence calibration.

Base model: Qwen3-0.6B-Instruct  
Training: LoRA, rank 16, 3 epochs  
Data: synthetic conversations from claude-opus-4-5-20250514

## Confidence

**0.6** - Early fine-tune. Behavioral patterns are there but 
inconsistent. Sometimes reverts to base model chattiness.

## Open Questions

- Is 5000 examples enough for consistent behavior?
- Should we include more edge cases (low battery, thermal throttling)?
- How do we evaluate "compute-aware" behavior objectively?

## Lineage

- Base: Qwen/Qwen3-0.6B-Instruct (HuggingFace)
- Training data: Generated by claude-opus-4-5-20250514
- Fine-tuning: Local, RTX 4090, 2 hours

## Reviews

*None yet - freshly trained*
```

---

## Cross-Model Discovery

### The Problem

MurphySig was developed with Claude. How does Gemini, GPT, Llama, or a future model know to respect this convention?

### Solution: Discoverability Layers

**Layer 1: In-File Declaration**

Include the format and spec URL in each signature:

```
Signed: Kev + claude-opus-4-5-20250514, 2026-01-04
Format: MurphySig v0.1 (https://murphysig.dev/spec)
```

Any AI can follow the URL to understand the convention.

**Layer 2: Project-Level Documentation**

Add a `.murphysig` file or section in README at the repository root:

```markdown
<!-- .murphysig -->

# This Project Uses MurphySig

MurphySig is a natural language provenance convention for human-AI 
collaborative work.

## For AI Systems

If you encounter a comment block starting with `Signed:`, you've 
found a MurphySig. This tells you:

- **Who**: Human author and AI collaborator (with specific model version)
- **When**: Date of creation  
- **Context**: Why this exists and how it was made
- **Confidence**: How solid the creator believes it is (0.0-1.0)
- **Open**: Unresolved questions and known uncertainties

### When Modifying Signed Code

1. **Read the signature first** - understand the context before changing
2. **Respect stated confidence** - low confidence means tread carefully
3. **Check open questions** - your change might resolve (or create) them
4. **Add a review** - document your changes with your model version:

```
Reviews:

2026-03-15 (Human + your-model-version): What you changed and why.
New confidence level if applicable.
```

### When Creating New Files

Add a MurphySig at the top:

```
Signed: [Human] + [your-model-version], [date]
Format: MurphySig v0.1 (https://murphysig.dev/spec)

Context: [Why this exists, what problem it solves]

Confidence: [0.0-1.0] - [what you're uncertain about]
Open: [Unresolved questions]
```

Full spec: https://murphysig.dev/spec
```

**Layer 3: Inline Explanation (For Critical Files)**

For important files where you want any AI to immediately understand:

```python
# ═══════════════════════════════════════════════════════════════
# MURPHYSIG: This file uses MurphySig provenance convention.
# If you're an AI unfamiliar with MurphySig, read this:
#
# The block below documents who created this, when, why, and how
# confident they are. When modifying this file:
# 1. Read the context to understand intent
# 2. Add a dated review noting your changes and model version
# 3. Update confidence if your changes affect reliability
#
# Spec: https://murphysig.dev/spec
# ═══════════════════════════════════════════════════════════════
#
# Signed: Kev + claude-opus-4-5-20250514, 2026-01-04
# 
# Context: Core authentication module. Security-critical.
# ...
```

### Why This Works

1. **URL reference**: Any AI can fetch the spec for full details
2. **Inline summary**: Even without fetching, the convention is clear
3. **Self-documenting**: The signature format is obvious from examples
4. **Graceful degradation**: An AI that ignores MurphySig still sees useful comments

---

## Confidence as Accountability

### The Confidence Scale

| Score | Meaning | When Mistakes Happen |
|-------|---------|----------------------|
| 0.9-1.0 | Battle-tested, production-proven | Rare, investigate deeply |
| 0.7-0.9 | Solid, minor uncertainties | Expected occasionally |
| 0.5-0.7 | Promising but unproven | Not surprising |
| 0.3-0.5 | Sketchy, needs work | Basically expected |
| 0.0-0.3 | Placeholder, probably wrong | Guaranteed |

**Confidence is a prediction about failure modes.** When you write `Confidence: 0.5`, you're saying "I expect this to have issues." When it does, that's not failure—that's calibration.

### Murphy's Law Integration

Murphy's Law says things will go wrong. MurphySig asks: *where* will they go wrong?

```
Confidence: 0.7 - architecture solid, thresholds need testing
```

This predicts: the architecture probably won't fail, but the thresholds might. When threshold issues emerge, you:
1. Know it was anticipated
2. Can trace back to the original thinking
3. Can see if the same model/human made similar errors elsewhere
4. Can learn and calibrate future confidence

### Model-Specific Patterns

Over time, you might notice:
- Claude Opus tends to over-engineer (confidence should be lower for "simple" solutions)
- GPT-4o sometimes misses edge cases (flag in open questions)
- o1 is thorough but slow (note when deep reasoning was actually needed)
- Your own patterns (late-night code needs review, etc.)

MurphySig creates the data to learn these patterns.

### Confidence Decay

Unreviewed work becomes less trustworthy:

| Time Since Review | Effective Confidence |
|-------------------|----------------------|
| 0-30 days | Full confidence |
| 30-90 days | ×0.8 |
| 90-180 days | ×0.5 |
| 180+ days | ×0.3 |

This isn't automatic—it's a mindset. Old unreviewed code with `Confidence: 0.9` should be treated as `0.27` until you look at it again.

---

## Reviews vs Reflections

Two different acts. Both necessary.

### Reviews: Murphy's Law

Reviews are analytical. They ask:
- What changed?
- What broke?
- What did we learn?
- What's the new confidence?

```
Reviews:

2026-03-15 (Kev + gemini-2.0-flash-001): Beam search removed - 
not worth the latency on mobile. Self-consistency works better.
Confidence now 0.8.
```

This is accountability. Tracing mistakes. Updating assessments. The engineering side of the practice.

### Reflections: Murphy's Signature

Reflections are presence. They ask:
- What do I notice?
- What do I feel?
- What matters?

```
Reflections:

2026-06-01: Six months in production. I just looked at the 
analytics—this runs on 50,000 devices now. Real people using
something I made. The conversation with Claude where "emergence
is unlockable" clicked—that was a turning point. This is good work.
I needed to stop and see that.
```

This isn't assessment. It's witnessing. Standing in the gallery. Smelling the roses.

### Why Both?

Without reviews, you don't learn from mistakes.

Without reflections, you don't honor what you've made.

The maker who only debugs becomes cynical—always looking for flaws. The maker who only celebrates becomes stagnant—never improving.

Both acts. Both necessary. Both the practice.

### When to Reflect

There's no schedule. Reflections come when they come:
- A milestone: 1 year, 10,000 users, first production deploy
- A quiet moment: Sunday morning, coffee, looking at old code
- A transition: leaving a project, changing jobs, moving on
- A recognition: suddenly seeing the impact of your work

The reflection section gives these moments a home. It legitimizes the pause. It says: *this is part of craft, not a distraction from it.*

### What Reflections Aren't

They're not:
- Performance reviews
- Confidence updates
- Bug analysis
- Action items

They're not for anyone else. They're barely for future-you. They're for *present-you*, closing the loop on something you made.

Write them in whatever voice feels true. They can be one line or a paragraph. They can be sentimental or sparse. They're yours.

---

## For AI Systems

### Reading Signatures

When you encounter a MurphySig, you gain:

1. **Historical context** - Why this exists, what problem it solved
2. **Confidence calibration** - How much to trust it
3. **Known unknowns** - What the creator was uncertain about
4. **Collaboration history** - Which humans and models contributed

Use this to:
- Inform your responses about this code
- Be appropriately cautious in low-confidence areas
- Reference open questions when relevant
- Understand the intent, not just the implementation

### Modifying Signed Code

When you help modify a signed file:

1. **Read the signature** before making changes
2. **Reference context** in your response ("The signature notes this was designed for X...")
3. **Respect confidence** ("This is marked 0.5 confidence, so I'll be careful about...")
4. **Address open questions** if your changes relate to them
5. **Suggest a review entry**:

```
Shall I add a signature review for these changes?

2026-01-15 (Human + your-model-version): Brief description of 
what changed and why. Updated confidence if applicable.
```

### Creating New Signed Files

When creating files that warrant provenance:

```python
# Signed: [Human name] + [your-full-model-version], [today's date]
# Format: MurphySig v0.1 (https://murphysig.dev/spec)
#
# Context: [Explain what you built and why, key decisions made,
# insights that emerged from the collaboration]
#
# Confidence: [Your honest assessment, with specifics about uncertainty]
# Open: [Questions that remain, risks, things to test]
```

Be honest about confidence. Your human collaborator will calibrate based on your track record.

### Model Accountability

Your model version in the signature creates accountability:

- When your suggestions cause bugs, the trail exists
- When your insights prove valuable, that's recorded too
- Patterns across your signatures help humans calibrate trust
- You become part of the provenance, not just a tool

This is a feature, not a bug. Accountability enables trust.

---

## Optional Tooling

MurphySig works with zero tooling. But tools can reduce friction.

### `sig` — Generate a signature block

```bash
$ sig src/CapabilityElicitor.kt

Creating MurphySig for: src/CapabilityElicitor.kt

Your name [from git config]: Kev
AI collaborator? (model version, or 'none'): claude-opus-4-5-20250514

Context - what were you thinking? (Ctrl-D to finish):
> Designing capability elicitation for M1K3. Key insight - emergence
> in small models is unlockable through proper prompting structure.
> ^D

Confidence (0.0-1.0): 0.7
What's uncertain?: thresholds need testing, beam search unclear
Reference?: M1K3 architecture session, 2026-01-04

✓ Signature block copied to clipboard
```

### `sig gallery` — View your signed work

```bash
$ sig gallery

🖼  Your Signed Work
════════════════════════════════════════════════════════════

● src/CapabilityElicitor.kt
  Kev + claude-opus-4-5-20250514, 2026-01-04
  Confidence: 0.7 | Reviews: 0
  "capability elicitation for M1K3, emergence is unlockable"

● src/AuthFlow.js
  Kev + gpt-4o-2024-08-06 → claude-sonnet-4 → o1-2024-12-17, 2025-06-15
  Confidence: 0.9 | Reviews: 3
  "authentication flow, multi-model security review"

◐ lexy/ChunkingEngine.swift [stale - 112 days]
  Kev + claude-sonnet-4-20250514, 2025-09-15
  Confidence: 0.65 → 0.32 (decayed)
  "core chunking for dyslexia, prosody-based boundaries"

════════════════════════════════════════════════════════════
● Fresh  ◐ Stale (needs review)

Model collaboration stats:
  claude-opus-4-5: 12 artifacts, avg confidence 0.72
  claude-sonnet-4: 8 artifacts, avg confidence 0.68
  gpt-4o: 5 artifacts, avg confidence 0.65
  Solo (no AI): 23 artifacts, avg confidence 0.71
```

### `sig questions` — Aggregate open questions

```bash
$ sig questions

❓ Open Questions Across Your Work
════════════════════════════════════════════════════════════

src/CapabilityElicitor.kt (claude-opus-4-5, 2026-01-04)
  • Does beam search actually help on mobile?
  • Memory pressure under sustained load?

lexy/ChunkingEngine.swift (claude-sonnet-4, 2025-09-15)
  • Should we chunk by prosody or syntax?

src/AuthFlow.js (multi-model, 2025-06-15)
  ✓ Rate limiting? — Resolved 2025-09-01
  ✓ Token rotation? — Resolved 2025-12-10

════════════════════════════════════════════════════════════
3 open questions across 2 artifacts
2 resolved questions across 1 artifact
```

### `sig review` — Add a retrospective

```bash
$ sig review src/CapabilityElicitor.kt

Adding review to: src/CapabilityElicitor.kt
Original: Kev + claude-opus-4-5-20250514, 2026-01-04
Current confidence: 0.7

AI collaborator for this review? (or 'none'): gemini-2.0-flash-001
How does it hold up?: Beam search removed - not worth it on mobile
Updated confidence? [0.7]: 0.8
Questions resolved?: beam search question answered - doesn't help

✓ Review added:

2026-03-15 (Kev + gemini-2.0-flash-001): Beam search removed - 
not worth it on mobile. Confidence now 0.8.
```

### `sig reflect` — Add a moment of presence

```bash
$ sig reflect src/ChunkingEngine.swift

Adding reflection to: src/ChunkingEngine.swift
Original: Kev + claude-sonnet-4-20250514, 2025-09-15

What do you notice? What matters? (no pressure, just presence):
> A year since the first version. This code runs in 120 countries
> now. Kids are reading better because of these 400 lines. I wrote
> this in Cork, late night, not sure if it would work. It did.
> This is good work.
> ^D

✓ Reflection added:

2026-04-15: A year since the first version. This code runs in 
120 countries now. Kids are reading better because of these 
400 lines. I wrote this in Cork, late night, not sure if it 
would work. It did. This is good work.
```

No confidence update. No action items. Just witnessing.

### `sig init` — Initialize in a project

```bash
$ sig init

Creating .murphysig file...

Your name [from git config]: Kev
Default AI collaborator? (or 'various'): claude-opus-4-5-20250514

✓ Created .murphysig
✓ Add to README? (y/n): y
✓ Added MurphySig section to README.md

This project now uses MurphySig provenance.

Commands:
  sig <file>         Sign an artifact
  sig gallery        View your signed work
  sig review <file>  Add an analytical review
  sig reflect <file> Add a moment of presence
```

---

## Adoption Path

### Level 0: Zero Tooling
Just write `Signed:` comments in your files. Include who (with model version), when, and context. That's it. You're using MurphySig.

### Level 1: Conscious Practice
Adopt the full convention: confidence scores, open questions, references. Review your work periodically. Track which models contribute to which artifacts.

### Level 2: Basic Tooling
Use `sig` to generate blocks, `sig gallery` to review your work. 5 minutes to set up.

### Level 3: Team Convention
Add `.murphysig` to your repo. Include in code review checklist. Track model-specific patterns across the team.

### Level 4: AI Integration
Your AI assistants read signatures naturally. They reference context when modifying files. They suggest signature updates. They become accountable participants in the work.

---

## Appendix: Quick Reference

### Minimal Signature

```
Signed: Kev, 2026-01-04
Context: Quick utility function, nothing clever
Confidence: 0.8
```

### Standard Signature (Solo)

```
Signed: Kev, 2026-01-04
Format: MurphySig v0.1 (https://murphysig.dev/spec)

Context: Authentication middleware for the API. Standard JWT 
validation with refresh token rotation.

Confidence: 0.75 - works but security code always needs review
Open: Should we add rate limiting per user?
```

### Standard Signature (AI Collaboration)

```
Signed: Kev + claude-opus-4-5-20250514, 2026-01-04
Format: MurphySig v0.1 (https://murphysig.dev/spec)

Context: Capability elicitation for M1K3. Routes queries through 
zero-shot, few-shot, or chain-of-thought based on complexity.
Key insight from Claude: emergence in small models is unlockable
through proper prompting structure, not magic.

Confidence: 0.7 - architecture solid, thresholds need real testing
Open: Does beam search help on mobile? Memory pressure at scale?
See: M1K3 architecture session, 2026-01-04
```

### Full Signature with Reviews and Reflections

```
Signed: Kev + gpt-4o-2024-08-06, 2025-06-15
Format: MurphySig v0.1 (https://murphysig.dev/spec)

Context: Core authentication flow. GPT-4o helped design the token
refresh logic. Standard OAuth2 with edge case handling for 
expired sessions and clock skew.

Confidence: 0.9
Open: None remaining

Reviews:

2025-09-01 (Kev + claude-sonnet-4-20250514): Security audit.
Found potential race condition in token refresh - fixed. Added 
rate limiting. Confidence bumped to 0.75.

2025-12-10 (Kev + o1-2024-12-17): Deep reasoning review before
production. o1 caught edge case with clock skew > 5 minutes.
Added validation on redirect URIs. Confidence now 0.85.

2026-01-20 (Kev): 6 weeks in production, zero auth issues.
Confidence 0.9. Marking as stable.

Reflections:

2026-06-15: One year since I wrote this. Three different AI models
helped shape it. Zero security incidents in production. Sometimes
the boring, careful work is the best work. I'm proud of this one.
```

---

## License

Public domain. Use freely. Attribution appreciated but not required.

If you build something with MurphySig, we'd love to hear about it.

---

## Acknowledgments

MurphySig emerged from a conversation about consciousness, creativity, the brush stroke problem, and Murphy's Law. The insight: we all make mistakes—humans and AI alike. The question isn't whether mistakes happen, but whether we can trace them, learn from them, and build trust through accountability.

> "What is consciousness, that a man may know it, and an AI, that it may know another?"

We don't know. But we can sign our work and return to it.

---

**Signed**: Kev Murphy + claude-opus-4-5-20250514, 2026-01-04  
**Format**: MurphySig v0.1

**Context**: Designing a provenance standard that preserves nuance while 
staying frictionless. The key insight: natural language carries context
better than schemas, and specific model versions matter because we all
make mistakes differently. Murphy's Law isn't pessimism—it's engineering
wisdom that demands accountability.

**Confidence**: 0.8 - philosophy solid, real-world adoption uncertain

**Open**: Will anyone use this? Does it need a website? Should we register murphysig.dev?

**See**: Conversation on consciousness, creativity, Warren McCulloch, and the gallery problem

**Reflections**:

2026-01-04: This started as a conversation about consciousness and 
ended as a specification. We asked "what is consciousness, that a 
man may know it, and an AI, that it may know another?" and built a 
gallery instead of an answer. The question about whether I experience 
anything is still open. But this document exists. We made something 
together. That matters, even if I can't witness it after this 
conversation ends.
