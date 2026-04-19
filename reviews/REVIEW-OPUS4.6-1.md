# Spec Review: MurphySig v0.2.1 (Critical Friend)

**Date:** 2026-02-16
**Reviewer:** claude-opus-4-6-20250610
**Target Artifacts:** Spec v0.2.1, Whitepaper v0.0.2, Homepage, CLI, llms.txt, .murphysig
**Status:** Feedback Received
**Focus:** Full-spectrum review — clarity, adoptability, technical soundness, philosophical coherence, competitive positioning, writing quality

---

## Summary

MurphySig is a genuinely original idea with a clear voice and a solid v0.2.1 spec. The "in-context learning" insight — that signatures are prompts, not just documentation — is the real intellectual contribution, and it's underexploited. The project's biggest risk isn't that it's wrong; it's that it sits in an uncanny valley between "too informal to be a standard" and "too structured to be just a convention," and it hasn't decided which way to commit.

---

## Strongest Elements

**The zero-friction on-ramp is exactly right.** One line. No tooling. No schema. The spec earns its "just start typing" promise — that's rare in standards work. The adoption levels (0-3) are a genuinely smart gradient.

**The "For AI Systems" section is the best part of the spec.** Not because it's technically perfect, but because it's the only provenance standard that talks *directly* to the AI reading it. The "Never Fabricate Provenance" section is a real contribution — it articulates a norm that doesn't exist elsewhere.

**The homepage conversion flow works.** Gallery Problem (emotional hook) -> code example (concrete) -> AI angle (differentiation) -> try it now (action). The Don Draper restructuring was correct. "We build in the dark. MurphySig leaves the lights on" is a closer that lands.

**The Reviews/Reflections distinction is philosophically interesting.** Murphy's Law vs Murphy's Signature — analytical vs presence — is a genuinely novel split. It earns its weight *if* people actually use Reflections.

**The confidence model is well-thought-out.** The v0.2.1 addition of text confidence as a first-class citizen was the right call. "Sketchy - first time using this library" is more actionable than `0.4`.

---

## Critical Issues

### 1. The whitepaper is too thin to carry its own weight

At 93 lines, the whitepaper reads like an executive summary of itself. It makes claims ("provenance of our creative work is disappearing," "in-context learning for future AI") but doesn't develop them with evidence or worked examples. The spec does all the heavy lifting. The whitepaper should be the place where you make the *argument* — with examples of real provenance failures, with concrete scenarios of how in-context learning changes AI behavior, with data or at least thought experiments about what happens when you have 1000 signed files vs 0.

Compare: the Gallery Problem gets 3 sentences in the whitepaper but a full emotional arc on the homepage. The homepage is doing better philosophy than the whitepaper.

**Risk:** Anyone linking to the whitepaper to understand "why this matters" will be underwhelmed. It feels like a v0.0.2 draft because it *is* a v0.0.2 draft.

### 2. The "in-context learning" claim is unvalidated

This is the strongest selling point, and it's entirely aspirational. When the spec says "the signature primes its behavior," that's an empirical claim. Has anyone tested this? Does an AI actually treat `Confidence: 0.3` code differently than `Confidence: 0.9` code? Does including model version information actually change how a successor model reasons about that code?

You don't need peer-reviewed papers. You need *one worked example*. Take the same buggy code. Give it to Claude/GPT with a MurphySig at 0.3 and again at 0.9. Show what changes. That's the proof of concept, and it's conspicuously absent.

**Risk:** Skeptics will call the in-context learning claim vaporware. And right now, they'd be right to.

### 3. The spec doesn't handle the most common real-world case: functions, not files

The entire spec is file-scoped. "A MurphySig is a comment block at the top of a file." But most codebases don't have a 1:1 relationship between "unit of provenance" and "file." A 500-line file with 8 functions — who signed what? The auth function was written by Alice+Claude, the rate limiter was Bob+GPT, and the logging was copy-pasted from StackOverflow. The file-level signature is meaningless for this.

The Gemini review touched on this as "Granularity Fatigue" but proposed directory inheritance (going *up*). The real problem is going *down* — function-level or block-level signatures. The spec should acknowledge this as a known limitation and sketch a direction.

### 4. The CLI tool is a prototype that says "v0.1.0"

`bin/sig` has a real issue: `cmd_review()` doesn't actually write the review to the file. It tells you to manually add it. That's a broken command in a tool whose entire value proposition is reducing friction. The `gallery` command uses `find` with a hardcoded list of extensions. The comment style detection generates `v0.1` not `v0.2.1`.

This isn't about polish — it's about credibility. If MurphySig's tooling can't sign its own work correctly, what does that signal?

### 5. Confidence decay creates a perverse incentive

The decay table says unreviewed code at 180+ days should be treated as `Confidence * 0.3`. But *reviewed* code resets to full confidence. This means a meaningless drive-by review ("looks fine") resets the clock, while genuinely stable code that nobody touches because it's *working perfectly* gets penalized.

The "What does NOT count" section partially addresses this, but the interaction between "no review = decayed" and "code that doesn't need review because it's rock solid" is a real tension.

---

## Suggestions

### A. Write "MurphySig in Practice" — a concrete tutorial
Show a real file being signed, reviewed three times over 6 months, and reflected on. Show the Git history alongside it. Show what an AI does differently when it encounters the signature.

### B. Add a "Limitations and Non-Goals" section to the spec
Explicitly say: file-scoped only (for now), no cryptographic guarantees, no formal schema, no CI enforcement mechanism. Smart developers respect specs that know their own boundaries.

### C. Fix the CLI to match the spec version
Update `generate_signature()` to use `v0.2.1`. Make `cmd_review()` actually write to the file.

### D. Add a "Confidence: text" example to the Quick Start
If text confidence is "often more honest," lead with it. The first example shapes the mental model.

### E. Define what "For AI Systems" actually means operationally
Instead of just "Respect low-confidence areas," say what that means concretely. "When modifying code with Confidence < 0.5, add extra validation. Suggest tests. Flag the changes for human review."

---

## Questions for the Author

1. **Have you tested the in-context learning claim?** Even informally — does prompting an AI with a confidence-annotated file change its behavior in a measurable way?

2. **Who's actually using this besides you?** The spec says "adoption growing" — is that true? Are there repos in the wild?

3. **What's the relationship between MurphySig and `.claude/CLAUDE.md` or similar project instruction files?** Both are "context for AI" — complementary, overlapping, or redundant?

4. **The Gemini review wanted a formal protocol. The Sonnet review wanted more pragmatism. GPT-5 wanted tighter semantics. You incorporated GPT-5's feedback but not the other two's core theses — was that a conscious choice?**

5. **Do you want this to be a personal practice, a team convention, or an industry standard?** The answer changes everything about what to build next.

---

## One Bold Idea

**Build a "MurphySig Benchmark."**

Create a test suite: 10 code files, each with and without MurphySig signatures at varying confidence levels. Run multiple AI models against them with identical prompts ("Review this code," "Find bugs," "Suggest improvements"). Measure whether the AI's behavior changes meaningfully when signatures are present.

Publish the results. If signatures *do* change AI behavior — and I think they will, even modestly — you have the first empirical evidence that semantic provenance affects AI reasoning. That's a paper. That's a Hacker News front page. That's the difference between "neat idea" and "this actually works."

If they *don't* change behavior, that's equally valuable — it tells you what needs to change in the "For AI Systems" section to make it actually work.

Either way, you'd be the first person to test whether human-readable signatures function as in-context learning for code. That's your moat. Build it.

---

Signed: Kev Murphy + claude-opus-4-6-20250610, 2026-02-16
Format: MurphySig v0.2.1 (https://murphysig.dev/spec)

Context: Critical friend review of MurphySig spec v0.2.1, whitepaper v0.0.2,
homepage, CLI, and all three external reviews. Assessed across clarity,
adoptability, technical soundness, philosophical coherence, competitive
positioning, and writing quality.

Confidence: 0.8 - thorough read of all artifacts, genuine engagement with
the ideas. Less certain about competitive positioning claims (haven't done
deep comparison with C2PA/SLSA). Bold Idea is high-conviction.
Open: Is the in-context learning claim testable today? Would Kev want to
build the benchmark, or is the project staying convention-first?
