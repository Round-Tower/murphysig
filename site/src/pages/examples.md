---
layout: ../layouts/MarkdownLayout.astro
title: Examples Gallery
description: Real-world examples of MurphySig across different contexts - code, documentation, commits, and creative work.
---

# Examples Gallery

MurphySig adapts to any context where provenance matters. Here's how it looks in practice.

---

## Code Comments

### JavaScript/TypeScript

```javascript
/**
 * Signed: Sarah Chen + claude-opus-4-5-20250514, 2026-01-15
 * Format: MurphySig v0.2 (https://murphysig.dev/spec)
 *
 * Context: Implementing OAuth2 token refresh logic. We chose a 5-minute
 * buffer before expiry to account for network latency and clock skew.
 *
 * Confidence: 0.75 - logic is solid, but edge cases around clock drift
 * need production validation
 *
 * Reviews:
 * 2026-03-20 (Sarah + claude-sonnet-4-5): Production hit one clock skew
 * edge case—added 10-minute buffer. New confidence: 0.9
 */
async function refreshTokenIfNeeded(token) {
  // Implementation...
}
```

### Python

```python
"""
Signed: Alex Rivera + gpt-5-20251201, 2026-02-10
Format: MurphySig v0.2 (https://murphysig.dev/spec)

Context: ML pipeline for user intent classification. Training on 50k
samples, using DistilBERT for speed over accuracy (product decision).

Confidence: 0.6 - accuracy is 87% but we haven't validated on edge cases
like multilingual input or highly ambiguous queries

Heuristic: We're prioritizing latency (p95 < 100ms) over accuracy here.
If accuracy drops below 85% in production, switch to full BERT.
"""
class IntentClassifier:
    # Implementation...
```

### Rust

```rust
/// Signed: Jordan Lee (solo), 2026-01-20
/// Format: MurphySig v0.2 (https://murphysig.dev/spec)
///
/// Context: Lock-free concurrent queue implementation. Heavily inspired
/// by Dmitry Vyukov's MPMC queue but adapted for our use case (single
/// producer, multiple consumers with priority).
///
/// Confidence: 0.4 - compiles, passes basic tests, but concurrency bugs
/// are sneaky. Needs fuzzing and formal verification before production.
///
/// Reflections:
/// 2026-06-15: After 3 months in production with zero issues, I now
/// understand why Vyukov's design is so elegant. Confidence would be 0.9
/// if I wrote this again.
pub struct SPMCQueue<T> {
    // Implementation...
}
```

---

## Document Headers

### Markdown Technical Spec

```markdown
# Authentication System Architecture

*Signed: Platform Team (Maria, Carlos, Jamie) + claude-opus-4-5-20251101, 2026-01-08*
*Format: MurphySig v0.2*

*Context: Post-security audit redesign. Moving from JWT to session tokens
with Redis backing. Decision made after weighing XSS risks vs. scalability.*

*Confidence: 0.8 - architecture is sound, but migration path for existing
users needs more detail*

## Overview
...
```

### Research Paper

```latex
% Signed: Dr. Emma Torres + claude-opus-4-5-20250514, 2025-12-01
% Format: MurphySig v0.2 (https://murphysig.dev/spec)
%
% Context: AI-assisted literature review and analysis. I wrote the core
% argument and interpretations; Claude helped synthesize 80+ papers and
% catch inconsistencies in citations.
%
% Confidence: 0.85 - argument is novel and well-supported, but the neural
% architecture comparison in Section 4.2 may oversimplify recent advances

\documentclass{article}
\title{Emergent Reasoning in Transformer Architectures}
...
```

---

## Git Commit Messages

### Feature Commit

```
feat: add real-time collaboration with WebSockets

Signed: Dev Team + cursor-0.42, 2026-01-12
Format: MurphySig v0.2

Context: Users requested Google Docs-style live editing. Chose
Socket.IO over raw WebSockets for fallback support (some corporate
firewalls block WS). Implemented operational transforms for conflict
resolution.

Confidence: 0.65 - happy path works well, but conflict resolution
under high concurrency needs load testing

Files changed: 12
Lines: +847, -23
```

### Bug Fix Commit

```
fix: resolve race condition in payment processing

Signed: Maya Patel + claude-sonnet-4-5-20251015, 2026-02-18
Format: MurphySig v0.2

Context: CRITICAL BUG - users reported duplicate charges. Root cause
was insufficient transaction isolation. Added database-level locks
and idempotency keys.

Confidence: 0.95 - fix is straightforward, added integration tests,
verified in staging with production-scale load

Reviews:
2026-02-20 (Maya): 48 hours in prod, zero duplicate charges, perf
impact negligible. Confidence confirmed at 0.95.
```

---

## Creative Work

### Blog Post

```markdown
---
title: "Building in Public: Lessons from 6 Months of Shipping Daily"
author: Kev Murphy
date: 2026-01-10
---

*Signed: Kev Murphy + claude-opus-4-5-20251101, 2026-01-10*
*Format: MurphySig v0.2*

*Context: Reflecting on my build-in-public journey. Claude helped
structure my scattered notes and tighten the prose, but the stories
and lessons are mine.*

*Confidence: 0.9 - I stand behind this. The writing feels honest.*

*Reflections:*
*2026-06-10: Re-reading this 5 months later—I was more burned out than*
*I admitted here. The optimism was real, but incomplete.*

---

Six months ago, I committed to shipping something every day...
```

### Design System Documentation

```markdown
# Button Component API

*Signed: Design System Team + cursor-0.44 + claude-opus-4-5, 2026-01-05*
*Format: MurphySig v0.2*

*Context: Multi-model collaboration. Cursor helped scaffold the component
structure, Claude reviewed for accessibility compliance. Final decisions
on variant naming and API design were team consensus.*

*Confidence: 0.7 - API feels clean, but we haven't validated with product
teams yet. Expecting iteration based on real-world usage.*

## Usage

...
```

---

## Standalone Files

### Configuration File

```yaml
# deployment/staging.yaml

# Signed: DevOps + gpt-5-20251201, 2026-01-22
# Format: MurphySig v0.2
#
# Context: Staging environment config for Kubernetes. Auto-generated
# from production config with scaling adjustments (2 replicas instead
# of 10, smaller resource limits).
#
# Confidence: 0.8 - tested in dev, should work in staging, but cloud
# provider quota limits might need adjustment

apiVersion: apps/v1
kind: Deployment
...
```

### Dataset Metadata

```json
{
  "dataset": "user-feedback-2026-q1",
  "signed": "Data Team (Lin, Marcus) + claude-opus-4-5-20251101",
  "date": "2026-03-31",
  "format": "MurphySig v0.2",
  "context": "Quarterly user feedback analysis. Manually labeled 5k responses, Claude helped identify themes and edge cases in remaining 45k. Human review on 10% sample showed 94% agreement.",
  "confidence": 0.85,
  "confidence_text": "High agreement on labeling, but 'neutral' category had most ambiguity",
  "rows": 50000,
  "columns": ["user_id", "feedback_text", "sentiment", "theme", "priority"]
}
```

---

## Multi-Model Evolution

```typescript
/**
 * Signed: Jamie + cursor-0.41 + claude-opus-4-5-20251101, 2026-01-10
 * Format: MurphySig v0.2
 *
 * Context: Search autocomplete feature. Cursor scaffolded the debounce
 * logic, Claude reviewed for edge cases (empty queries, special chars).
 * I wrote the API integration and caching strategy.
 *
 * Confidence: 0.7 - works well for English queries, untested on CJK input
 *
 * Reviews:
 * 2026-01-15 (Jamie + gpt-5): Added CJK tokenization. Tested with Japanese
 * and Chinese queries—works but needs better ranking. Confidence: 0.75
 *
 * 2026-02-01 (Jamie + claude-sonnet-4-5): Rewrote ranking algorithm based
 * on user analytics. Click-through rate improved 23%. Confidence: 0.9
 */
class SearchAutocomplete {
  // Implementation...
}
```

---

## Text Confidence (No Numerical Score)

```python
"""
Signed: Research Team + claude-opus-4-5-20250514, 2025-12-15
Format: MurphySig v0.2

Context: Exploratory analysis of A/B test results. Early-stage investigation,
not production code.

Confidence: Low - statistical significance is marginal (p=0.048), sample size
was smaller than planned due to early termination, and we haven't controlled
for confounding variables like time-of-day effects

Note: Use this analysis to inform next experiment, not for product decisions
"""
def analyze_experiment_results(data):
    # Implementation...
```

---

## Key Patterns

Across these examples, notice:

1. **Natural language over technical jargon** — Anyone can read it
2. **Confidence calibration** — Low confidence is valuable information
3. **Context explains "why"** — Not just what changed, but why it was built this way
4. **Reviews show evolution** — The work gets better over time
5. **Reflections add humanity** — The maker's voice, not just the code

MurphySig adapts to your workflow. Use what fits. Skip what doesn't. The goal is **honest provenance**, not bureaucracy.

---

*Ready to start? Read the [Specification](/spec) →*

---

*Signed: Kev Murphy + claude-sonnet-4-5-20260106, 2026-01-06*
*Format: MurphySig v0.2*

*Context: Examples gallery to showcase MurphySig across different contexts and languages. Demonstrates flexibility and real-world applicability.*

*Confidence: 0.8 - examples are realistic and diverse, but could use more edge cases (e.g., scientific notebooks, legal documents)*
