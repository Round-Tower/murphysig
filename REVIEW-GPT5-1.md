# Spec Review: MurphySig v0.1.0

**Date:** 2026-01-06
**Reviewer:** gpt-5.2-thinking
**Target Artifact:** `site/public/spec.txt` (MurphySig Specification v0.1.0)
**Status:** 📋 Feedback Received
**Confidence:** 0.83 - Strong on spec clarity/usability; less certain about multi-author workflow norms across different team cultures.

---

## Executive Summary

Five key feedback points focusing on ambiguity risks and adoption friction. The review addresses: signature meaning, block boundaries, multi-author workflow, confidence semantics, and decay guidance.

---

## 1. Clarify "Signature" vs Cryptographic Signature

**Issue:** The term "signature" may create false assumptions about authenticity or cryptographic verification.

**Recommendation:** Add an explicit line early in the spec: MurphySig is **not** a cryptographic/verifiable signature—it's a provenance/intention note.

**Risk if unaddressed:** Users may expect MurphySig to provide tamper-proof verification, leading to misuse or disappointment.

---

## 2. Define Clear Boundaries for the Block

**Issue:** "Starts with `Signed:`" is simple but ambiguous for tooling and for long headers. Where does the signature block end?

**Recommendation:** Consider a recommended end marker like `End MurphySig` (still optional) so parsers and humans know what's in/out of the signature context.

**Risk if unaddressed:** Inconsistent parsing across tools; confusion about what content is part of the signature vs regular comments.

---

## 3. Specify Multi-Author and Ongoing Edits

**Issue:** Unclear whether the top `Signed:` block is:
- **Immutable** (original intent) with changes recorded under `Reviews:`
- **Mutable** (current owner/intent) that gets updated with each significant change

**Recommendation:** The spec should pick a norm to avoid inconsistent repo practice. Either works, but clarity is needed.

**Open Question:** Should "Signed" be immutable with changes only in Reviews, or should it track current ownership/intent?

---

## 4. Tighten "Confidence" Meaning and Add "Basis"

**Issue:** Confidence is defined loosely. "0.9" could mean different things to different people and becomes hard to calibrate without evidence.

**Recommendations:**
1. Define confidence as primarily **correctness/intent-fidelity** (or explicitly state what it covers)
2. Add an optional `Basis:` field (tests passed, review completed, production time, etc.) so confidence isn't just vibes

**Risk if unaddressed:** Confidence scores become meaningless or gameable; inconsistent interpretation across teams.

---

## 5. Make Confidence Decay Explicitly a Heuristic

**Issue:** The decay table is presented but could be interpreted as mandatory rather than a suggested guideline.

**Recommendations:**
1. Label it as "suggested heuristic, not required"
2. Define what counts as a "review" (PR approval, production incident-free period, manual audit, etc.) so people apply decay consistently

**Risk if unaddressed:** Teams may ignore decay entirely or apply it inconsistently.

---

## Open Questions for Spec Authors

1. Should the standard recommend an explicit end marker for the signature block?
2. Should "Signed" be immutable (original author preserved) or mutable (current owner/intent)?
3. What exactly does "Confidence" measure? Correctness? Intent-fidelity? Code quality?

---

Signed: gpt-5.2-thinking, 2026-01-06
Format: MurphySig v0.1 (https://murphysig.dev/spec)

Context: Provided 5 key feedback points on MurphySig v0.1.0, focusing on
ambiguity risks and adoption friction (signature meaning, block boundaries,
multi-author workflow, confidence semantics, decay guidance).

Confidence: 0.83 - Strong on spec clarity/usability; less certain about the
best "one true" workflow for multi-author edits across different team cultures.

Open: Should the standard recommend an explicit end marker? Should "Signed"
be immutable with changes only in Reviews, or should it track current
ownership/intent?
