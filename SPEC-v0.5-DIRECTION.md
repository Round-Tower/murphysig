# MurphySig — v0.5 Direction Note

> Forward-looking design note, not a spec change. Captures the thesis and the
> candidate experiments that came out of the 2026-06-24 structure-vs-content
> control. Nothing here is canonical until validated and folded into the spec.

---

## The trigger

The TK structure-vs-content control (run `2026-06-24_tk-prose-control-6`,
6 families, dual-judged Opus 4.6 + GPT-5.4) showed that the briefing uplift is
**80–94% the information and only 6–20% the MurphySig structure.** A
length/content-matched plain comment carrying the same facts does most of what
the signature block does.

The sharp reading isn't "structure ≈ content." It's:

> **The value lives entirely on the *write* side, not the read side.** The
> model didn't benefit from MurphySig's syntax — it benefited from a mind
> having done the work of articulating intent and uncertainty. The format was
> never the asset; the act of reflection was.

**The trap this rules out:** any spec improvement that adds more *model-facing
structure* (more fields, tighter grammar, machine-parseable schemas). The data
predicts ~zero return on that. The bold direction has to be a deeper *act*, not
a richer *format*.

---

## The bolder thesis

> MurphySig isn't documentation, and it isn't a prompt-injection trick. It's
> **the interface for handing judgment across minds and across time** —
> human→AI, AI→AI, you→future-you. As code gets cheap and *intent* becomes the
> bottleneck, signing is how the scarce thing (why, and how sure) survives the
> handoff into an increasingly AI-maintained world.

Two empirically load-bearing levers the spec currently under-exploits:

1. **In-context norms change AI behavior.** Honesty result: `.murphysig`
   "never fabricate" took fabrication 11%→0% and `Prior: Unknown` 0%→100%. The
   `.murphysig` file is a *behavioral contract*, and it provably works.
2. **Externalizing tacit knowledge transfers it.** TK result: +0.11 across six
   families, concentrated on the *author-intent* axis (≈3× the code-derivable
   axis). Writing the "why / unsure" down moves it to the next mind.

So the spec's real identity: **a norm-carrier that elicits and transmits tacit
knowledge.** Less "format," more "constitution + capture ritual."

---

## Candidate spec moves (tagged by current evidence)

| Move | What | Status |
|---|---|---|
| Reframe the lead | Spec opens with "a discipline for capturing intent + uncertainty," not "an AI-legible block." | ✅ eval-backed |
| Norms as a first-class section | A short, **opt-in, individually-validated** set of behavioral norms for AI collaborators. "Never fabricate" is proven norm #1; others added only after an eval. | ✅ (honesty) |
| `Open:` becomes resolvable | Make the uncertainty field trackable across time — an Open question a later signature *closes*. Highest-content field in the data (Q3 moved most). Turns signatures into a living risk/uncertainty ledger an agent can query before editing. | 🟡 plausible |
| Confidence = triage, not scrutiny | The honest replacement for the refuted ICL claim: confidence + unresolved Open is a *routing signal* ("audit this first"), not a scrutiny dial. Define it for agents. | 🟡 needs eval |
| Write-side reflection prompt | Spec offers the author *questions to answer*, not just fields to fill. Captures the metacognition benefit at write-time. | 🔴 aspirational |

---

## The boldest defensible bet — the author-side effect

The control measured *reader* benefit. The bigger, untested claim is on the
author:

> **Hypothesis: signed work is *better* work** — not because the reader gains,
> but because knowing you'll sign, and having to state your confidence and your
> open questions, makes the *author* (human or AI) make better decisions.

If it replicates, MurphySig stops being a knowledge-transfer convention and
becomes a **quality-forcing function** — a much bigger claim, and one nobody
has measured.

**Honest caveat (apply the discipline we just learned):** the author effect
might also be "any reflection prompt helps," not MurphySig specifically. So the
eval needs the same matched control we just ran — MurphySig reflection vs a
generic "think carefully" prompt — on the *write* side this time.

---

## Three candidate experiments (eval-driven, all with matched controls)

1. **Author-quality (the bold one).** Same model + task, with/without "you will
   sign this; state confidence + open questions." Judge *output quality*, not
   the briefing. Control arm: generic "think carefully" prompt, to isolate
   MurphySig from reflection-in-general.
2. **Norm transfer at scale.** Test additional candidate norms beyond "never
   fabricate" (e.g. "state what you didn't verify," "leave an `Open:` for the
   next maintainer," "don't silently widen scope"). Only norms that move
   behavior earn a place in the spec; label validated vs aspirational.
3. **Confidence-as-triage.** Give an agent a repo of signed files and a budget;
   does routing attention by `Confidence:` + unresolved `Open:` find the real
   problems faster than unsigned/random? Validates the actionable replacement
   for the refuted scrutiny claim.

---

## Recommended sequencing

Chase **author-quality** first — it's the most on-brand ("sign the work"),
the boldest, and reuses the existing harness shape. It's the experiment that
could move the public claim from "validated as helpful for readers" to
"validated as a way to do better work." `Open:` resolvability and
confidence-as-triage are strong second moves once there's appetite for a v0.5
spec bump.

And the spec should practice what it preaches: carry its *own* `Open:` —
"does the structure ever earn its keep with human-written signatures or a third
judge? does signing improve the author's work, or just the reader's?" — instead
of presenting as settled.

---

<!--
Signed: Kev + claude-opus-4-8, 2026-06-24
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Confidence: 0.6 — the reframe (discipline > format) and the two proven levers
are eval-backed; the bolder "judgment handoff" thesis and the author-quality
hypothesis are reasoned bets, explicitly unvalidated. This is a direction, not
a finding.
Open: Does signing improve the AUTHOR's work, not just the reader's — and does
it survive a matched "think carefully" control? Which behavioral norms beyond
"never fabricate" actually move AI behavior? Does confidence+Open routing beat
random attention allocation?
Prior: Unknown (new design note; thesis emerged from run 2026-06-24_tk-prose-control-6)
-->
