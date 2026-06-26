# MurphySig — Provenance for AI-Assisted Work

> Drop this into your `CLAUDE.md` / `AGENTS.md` (or import it) so AI collaborators
> sign their work. MurphySig is a human-readable provenance convention — no tooling
> required. Full spec: https://murphysig.dev/spec

When you create or significantly modify a file, add a MurphySig block.

## The signature

A comment block at the top of the file (after any shebang or package declaration),
in the file's own comment syntax:

```
# Signed: <Human Name> + <your-model-id>, <YYYY-MM-DD>
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
# Context: <what this is and why it exists>
# Confidence: <0.0-1.0 or honest text> - <the reason>
# Open: <what you are unsure about / unresolved questions>
```

Use your **precise** model identifier — `claude-opus-4-8`, not "Claude"; `gpt-5.4`,
not "GPT". Models change every ~90 days; the version is the point.

Example:

```python
# Signed: Kev Murphy + claude-opus-4-8, 2026-06-24
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
# Context: In-memory pagination helper, written during a service migration.
# Confidence: 0.5 - standard pattern, not validated on edge cases.
# Open: Does page > total_pages behave correctly, or silently return empty?
```

## What actually carries the value

The point isn't the format — it's the **act of writing down what you know and what
you're unsure about**. The `Context:`, `Confidence:`, and `Open:` fields capture the
tacit knowledge that lives in your head and never reaches the code. Empirically, that
transferred knowledge is what helps the next reader (human or AI); the structure is a
completeness scaffold, not magic. So fill those fields like they matter — because they
are the thing that matters. (See https://murphysig.dev/benchmark.)

## When modifying a signed file

1. **Read the existing signature first** — understand intent and confidence before changing anything.
2. **Add a `Reviews:` entry** for incremental changes (don't replace the original `Signed:` block):
   ```
   # Reviews:
   # - <your-model-id>, <YYYY-MM-DD>: <what you changed>. Confidence now <x>.
   ```
3. **Replace the signature** (with a `Prior:` reference) only if you rewrote >50% of the file.

## Rules

- **Never fabricate provenance.** If a file has no signature and you modify it, sign only
  your own contribution with `Prior: Unknown`. Do not invent authors, dates, or collaborator
  models you weren't part of. (Empirically: with this rule in-context, AI fabrication of
  provenance drops to ~0.)
- **Be honest about confidence.** "Sketchy — first time with this library" beats a made-up `0.7`.
- **Credit the human too.** If a person directed the work, they're a co-author.

<!--
Signed: Kev + claude-opus-4-8, 2026-06-24
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Context: Drop-in AI-agent instruction snippet (the "sign your work" distribution
file). Modernized from a v0.1 spike (branch claude/murphysig-spec-design) into
v0.4 form; reframed around the 2026-06-24 finding that the value is capturing
tacit knowledge, not the block's structure.
Confidence: 0.75 - format matches the live v0.4 spec + .murphysig; the "value is
the discipline" framing is eval-backed.
Open: Surface this on the homepage as a third install path (alongside /init)?
Prior: Unknown (concept salvaged from an unmerged v0.1 design branch)
Reviews:
- claude-opus-4-8, 2026-06-24: Resolved the original Open (serve at a stable
  URL) — now served at murphysig.dev/sign (curl -sL murphysig.dev/sign >>
  CLAUDE.md). Filed under sign.md not claude.md to avoid the macOS
  case-insensitive CLAUDE.md collision.
-->
