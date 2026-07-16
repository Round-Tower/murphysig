# r/BuildWithClaude draft — 2026-07-12

**Title:** My repo's git history says one author. Its signatures say nine minds — five Claude generations, a Gemini, and reviews from GPT-5 and o1.

---

Six months ago I added a small convention to my CLAUDE.md: sign the work. Every significant file gets a comment block — who made it (me + the model), when, what we were thinking, how confident we were, and what we left unresolved:

```python
# Signed: Kev + claude-opus-4-6, 2026-02-16
# Format: MurphySig v0.4 (https://murphysig.dev/spec)
#
# Context: Fallback scorer when API limits are hit. Should be
#          validated against LLM judge results when available.
#
# Confidence: 0.6 - heuristic approximation, not as good as LLM judge
```

That's a real one from February. Hold that thought.

**Why this is interesting for people writing CLAUDE.md files:** the convention lives in a `.murphysig` file imported into CLAUDE.md, and it turns out in-context norms like this measurably change model behavior. The one we benchmarked hardest: a four-line "never fabricate provenance" rule. Without it, models invent authors and dates for unsigned code (Claude ~11% of the time on bare utility files, some families much worse). With it in context: 0%. We tested across six model families with two independent judges. Your CLAUDE.md isn't documentation — it's a behavioral contract, and the model honors it.

**The part I didn't expect.** This week, the current Claude (Fable 5) ran an audit over all 92 signed files — its own idea of the convention's audit workflow, checking signatures against git history. It found that February signature above, noticed the doubt it recorded ("should be validated against LLM judge"), and checked whether anyone ever had. Someone had: June data showed the heuristic agreed with the judge 9 times out of 18. A coin flip. The February model's suspicion was confirmed four months later — and nobody had told the file. Fable added the review entry closing the loop, three model generations after the doubt was written down.

That's the thing I actually want from AI collaboration: not just code, but *judgment that survives the handoff* — between me and the model, and between the models themselves across upgrades.

**Honest caveat**, since the convention is built on honesty: we ran a matched control, and a plain prose comment carrying the same facts gets you most of the read-side benefit. The structured format isn't magic — the discipline of writing it down is. Full benchmark data (including the finding that refuted my favorite claim): https://murphysig.dev/benchmark

Try it: one file, no tooling — `curl -sL murphysig.dev/init | bash`, or just read https://murphysig.dev. Would love to see what a few months of signatures look like in someone else's repo.

---

Signed: Kev + claude-fable-5, 2026-07-12
Format: MurphySig v0.4 (https://murphysig.dev/spec)

Context: Drafted for r/BuildWithClaude — the CLAUDE.md-as-behavioral-contract
angle, because that's the finding this community can use tomorrow. The
heuristic_scorer story is retold from the 2026-07-12 self-audit
(scratch/sig-audit-2026-07-12.md); every number is from committed runs.

Confidence: 0.8 — facts verified against the audit and archived runs; whether
the tone lands on Reddit is anyone's guess.
Open: Should the post link the HN piece when it goes live, or stand alone?
