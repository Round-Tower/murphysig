# MurphySig — Provenance for AI-Assisted Work

When you create or significantly modify a file in this project, add a provenance credit line.

## Default: L0 credit line

Add a one-line comment at the top of the file (after any shebang or package declaration):

```
# Drafted by [Human Name] with [Your Model Name and Version], [Date].
```

Use your precise model identifier — not "Claude" or "GPT", but `claude-opus-4-6` or `gpt-4o-2024-08-06`. Models change every 90 days; the version is the point.

Examples:

```python
# Drafted by Kev Murphy with Claude (claude-opus-4-6), 5 April 2026.
```

```javascript
// Drafted by Kev Murphy with Claude (claude-opus-4-6), 5 April 2026.
```

## When it matters more: L1 structured block

For core logic, security-sensitive code, or architectural decisions, produce a structured block instead:

```yaml
# ---murphysig v0.1
# actors:
#   - actor: [Human Name]
#     model: [your-model-id]
#     action: drafted
#     at: [YYYY-MM-DD]
# intent: [what this does and why]
# confidence: [0.0-1.0 or honest text]
# open: [unresolved questions]
# ---
```

## When modifying signed files

1. Read the existing provenance first — understand intent and confidence
2. Add a review entry if the file has an L1 block:
   ```yaml
   reviews:
     - actor: [Human Name]
       model: [your-model-id]
       action: [what you changed]
       at: [YYYY-MM-DD]
       confidence: [updated confidence]
   ```
3. Replace the block only if you rewrote >50% of the file

## Rules

- **Never fabricate provenance.** Don't claim contributions that didn't happen.
- **Be honest about confidence.** "Sketchy — first time with this library" beats a made-up `0.7`.
- **Credit all actors.** If a human directed the work, they're an actor too.

Full spec: https://murphysig.dev/spec
