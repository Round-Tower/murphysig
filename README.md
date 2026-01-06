# MurphySig

A human-readable provenance standard for creative work.

**[murphysig.dev](https://murphysig.dev)**

## What is it?

MurphySig is a convention for signing your work with natural language context that both humans and AI can understand—without special tooling.

```
Signed: Kev + claude-opus-4-5-20251101, 2026-01-04
Format: MurphySig v0.1 (https://murphysig.dev/spec)

Context: Authentication middleware for the API. Uses JWT with
refresh tokens. Followed OWASP guidelines for token storage.

Confidence: 0.8 - solid pattern, but refresh logic untested at scale
Open: Should we add rate limiting on refresh endpoint?
```

## Why?

**Murphy's Law (Accountability):** Things will go wrong. The question isn't whether mistakes happen, but whether you can trace them.

**Murphy's Signature (Presence):** Makers skip reflection. MurphySig creates the gallery—a moment to say: *this was a thing, at a time, made by us*.

## Quick Start

Add a comment block at the top of any file:

```
Signed: [Your name] + [model-version], [date]
Format: MurphySig v0.1 (https://murphysig.dev/spec)

Context: [What you built and why]

Confidence: [0.0-1.0] - [what you're uncertain about]
Open: [Unresolved questions]
```

That's it. No build tools. No dependencies. Just comments.

## Resources

- [Full Specification](https://murphysig.dev/spec) - Complete standard with examples
- [Plain Text Spec](https://murphysig.dev/spec.txt) - For AI systems and terminals
- [llms.txt](https://murphysig.dev/llms.txt) - Quick summary for AI crawlers

## License

Public domain. Use freely. Attribution appreciated but not required.

See [LICENSE](LICENSE) for details.
