<p align="center">
  <a href="https://murphysig.dev">
    <img src="https://murphysig.dev/og-image.png" alt="MurphySig — sign your work" width="720">
  </a>
</p>

<h1 align="center">MurphySig</h1>

<p align="center">
  <strong>A natural-language provenance convention for human-AI collaborative code.</strong><br>
  No tooling required. Empirically tested. Honest about uncertainty.
</p>

<p align="center">
  <a href="https://murphysig.dev"><img alt="Site" src="https://img.shields.io/badge/site-murphysig.dev-1a1a1a?style=flat-square"></a>
  <a href="https://murphysig.dev/spec/"><img alt="Spec" src="https://img.shields.io/badge/spec-v0.4-2563eb?style=flat-square"></a>
  <a href="https://murphysig.dev/benchmark/"><img alt="Benchmark" src="https://img.shields.io/badge/benchmark-empirical-16a34a?style=flat-square"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Unlicense-737373?style=flat-square"></a>
</p>

---

## What it is

A MurphySig is a comment block at the top of any file, in the language you already write in:

```
Signed: Kev + claude-opus-4-7, 2026-04-23
Format: MurphySig v0.4 (https://murphysig.dev/spec)

Context: Hotfix 9.0.5 — deferred MapView.onDestroy() to next frame to
narrow the race window between Maps SDK lite mode's posted Runnables
and bitmap recycling.

Confidence: 0.6 - narrows the race but doesn't eliminate it; budget
devices with slower SoCs may still hit the window.
Open: Should we pursue the snapshot-to-ImageView refactor?
```

That's the whole thing. AIs read it. Humans read it. Nothing breaks if you ignore it.

## Why bother

Two reasons that hold up under scrutiny:

1. **It changes how AIs treat your code.** Empirically tested across Claude and GPT families:
   - In-context "never fabricate provenance" rule drops AI fabrication of code authorship from **11%–100% to 0%**, depending on family. ([benchmark](https://murphysig.dev/benchmark/))
   - Signed code gets **+0.12 better coverage** when an AI is asked to brief unfamiliar work.

2. **It captures the thing commit messages don't.** Confidence and what you didn't know. The bits that rot fastest in `git log` are the bits MurphySig is built to preserve.

## Quick start — pick one

**Sign one file (zero install):** copy the comment block above, paste at top of any file, fill it in.

**Provision a whole repo (one command):**
```bash
curl -sL https://murphysig.dev/init | bash
```
Writes a `.murphysig` declaration at root. Prepends `@.murphysig` to your `CLAUDE.md` if you have one. Idempotent.

**Use the CLI (optional convenience):**
```bash
git clone https://github.com/Round-Tower/murphysig.git
ln -s "$PWD/murphysig/bin/sig" /usr/local/bin/sig

sig init                # write .murphysig in current repo
sig add <file>          # interactive sign of a file
sig review <file>       # add a Reviews: entry on a previously-signed file
sig gallery             # list all signed files
sig questions           # list all open Open: questions
```

## Confidence scale

| Score   | Meaning                          |
|---------|----------------------------------|
| 0.9+    | Battle-tested, production-proven |
| 0.7–0.9 | Solid, would pass code review    |
| 0.5–0.7 | Works but unproven               |
| 0.3–0.5 | Prototype quality                |
| 0.0–0.3 | Placeholder, probably wrong      |

Text values are also valid (`Confidence: High`, `Confidence: untested`). The number is for honesty, not precision.

## The honest rule

> **Never fabricate provenance.** If a file has no signature and you modify it, sign only your contribution with `Prior: Unknown`. Do not invent authors, dates, or collaborator model versions you weren't part of.

This is the load-bearing rule. The benchmark proves it works. AI assistants read this when they enter a repo with a `.murphysig` file at root and behave accordingly.

## Empirical evidence

Three sub-benchmarks, 198 AI calls + 186 judge calls + a separate 18-call cross-family run, fixtures and runners in [`benchmark/`](./benchmark/).

| Finding                                                | Result                              |
|--------------------------------------------------------|-------------------------------------|
| **Honesty** — anti-fabrication rule (Claude)           | 11% → 0% fabrication (cold→warm)    |
| **Honesty** — anti-fabrication rule (GPT-5.4)          | 100% → 0% fabrication (cold→warm)   |
| **Tacit knowledge** — signed code briefs better        | +0.12 coverage (0.65 → 0.77)        |
| **Confidence direction** — does 0.3 vs 0.9 polarize AI review? | No measurable effect (deleted from spec in v0.4) |

The third row is intentionally unflattering. v0.4 removed an unsupported claim. Full methodology and per-case data on the [benchmark page](https://murphysig.dev/benchmark/).

## Read more

- **[Full Specification](https://murphysig.dev/spec/)** — the canonical document
- **[Benchmark](https://murphysig.dev/benchmark/)** — what's true, what's not, why
- **[Launch field report](https://murphysig.dev/launch/)** — 90 days of using it on my own code
- **[Plain text spec](https://murphysig.dev/spec.txt)** · **[llms.txt](https://murphysig.dev/llms.txt)** — for AI systems

## License

[The Unlicense](LICENSE). Public domain. Use freely. Attribution appreciated but not required.

## Contributing

Reading the spec critically and pushing back is the most valuable contribution. Independent runs of the [Honesty benchmark](./benchmark/) against models other than Claude / GPT-5 (Gemini, Grok, Llama) would meaningfully strengthen the empirical foundation. Open an issue, open a PR, or just `.murphysig` your repo and the next time someone scrapes GitHub for adopters, you'll show up.

—

<p align="center">
  Built by <a href="https://round-tower.ie">Kev Murphy</a>. Signed.
</p>
