---
draft: HN relaunch post — MurphySig cross-family benchmark (v2, post-control)
generated: 2026-06-24
supersedes: v1 (which led with "structure earns its keep" — REFUTED by the control)
evidence: results/tk/runs/2026-06-24_tk-prose-control-6/ (6 families, 0 judge skips)
status: DRAFT — not published. Scope site/whitepaper edits with Kev before going live.
---

# Show HN draft (v2)

**Show HN: I ran the control on my own provenance convention, and it refuted the part I was proudest of**

MurphySig is a human-readable provenance convention: a small comment block at the top of a file recording who wrote it, with what confidence, and what was left uncertain. AIs read it in-context; no tooling. Repo and full data below.

Last time I posted here (a 90-day field report) the empirical case was Claude-only and the one ask was: test it on other model families. I did — six families via OpenRouter (Gemini, Llama, DeepSeek, Grok, Qwen, Mistral), judged by Opus-4.6. And then I ran the control that the comments would (rightly) have demanded, which turned my headline upside down. Here's the honest version.

**The effect is real and crosses families.**

The tacit-knowledge test (TK) measures whether a signature helps a model brief unfamiliar code. It's a within-model delta — each model briefs each case once unsigned, once signed, so it controls for raw capability. Across all six families, signed beat unsigned by a mean of **+0.11 coverage** (DeepSeek +0.16, Llama +0.16, Mistral +0.11, Qwen +0.11, Gemini +0.07, Grok +0.06), with hedging down across the board. No capability cliff. n=25 per arm, reps=5, temp=0.7.

That's the number I was going to lead with. Then I ran the control.

**The control: structure vs content.**

"Signed beats unsigned" has an obvious confound — the signed version simply contains *more relevant information*. So I added a third arm: the same facts as the signature (purpose, "written mid-migration", "not validated on edge cases", the open question), rewritten as a plain unstructured developer comment — no field labels, no `Confidence:` number, no MurphySig framing — and **length-matched** to the signature (committed test enforces ±15%, so I can't have quietly handicapped it).

Now the uplift decomposes:

```
                  Δstructure       Δcontent        Δtotal
                 (signed−prose)  (prose−unsigned) (signed−unsigned)
  DeepSeek          +0.01           +0.15           +0.16
  Gemini            +0.00           +0.07           +0.07
  Llama             +0.04           +0.12           +0.16
  Mistral           −0.00           +0.11           +0.11
  Qwen              +0.02           +0.09           +0.11
  Grok              −0.03           +0.09           +0.06
  ------------------------------------------------------------
  MEAN              +0.007          +0.104          +0.111
                    (6% of total)   (94% of total)
```

**The information is 80–94% of the benefit; the structure is a small minority.** Under the Opus judge the structure contributes ~6% (+0.007, negative for one family); under a second, non-Anthropic judge (GPT-5.4) it's ~20% (+0.025). Both judges agree on the shape — content dominates every family — they disagree only on how small the format's residual is. A plain prose comment carrying the same facts does most of what the MurphySig block does. The format I designed is doing a little of the work, not the bulk of it.

**What I'm killing and what I'm keeping.**

- Killed: "the structured signature makes models read code better." The syntax isn't magic. If I'd posted last week's draft, that would've been the headline, and it would've been wrong.
- Kept, and now actually evidence-backed: MurphySig's value is that it's a **convention that makes you write the tacit knowledge down**. The Context/Confidence/Open fields are a *completeness prompt* — a checklist for the stuff that lives in your head and never makes it into the code. The benefit is real, generalises across six families, and transfers to plain comments too. The structure earns its keep as a discipline for humans, not as a format for models.
- Unaffected: the separate honesty result. A 4-line "never fabricate provenance" rule gets 100% honest-handling (under two judges) on four of six families, with two resisting (Llama, Qwen) — tracks instruction-following, not vendor. Independent axis; this control doesn't touch it.

**Six months of practising it, audited by itself.**

Before posting this I had the current AI collaborator (claude-fable-5) run the convention's own audit over the repo. Git blames one author for this codebase. The signatures record nine minds: five Claude generations, a Gemini, and external reviews signed by GPT-5, o1, and Sonnet, January to July. Since honesty is the whole brand, the findings:

- Signing at creation is easy; *going back* is where the discipline decays. Only 15 of 92 signed files ever received a review entry; 18 carried over a month of unreviewed drift. If you adopt this, that's the failure mode to expect.
- The best thing the audit found: `heuristic_scorer.py`, signed in February by opus-4-6 with *"Confidence: 0.6 — should be validated against the LLM judge."* The validation happened in June: agreement 9/18. A coin flip. The signature's suspicion was empirically confirmed — and nobody told the file. Fable closed the loop this week, three model generations after the doubt was written down. That's the transfer the benchmark measures, happening unprompted in the benchmark's own repo.
- The audit flagged two fabrication smells; both were false positives on inspection (a test-fixture string, a spec template). The tool enumerates; judgment clears. Same lesson as the control above — the mechanical layer is never where the value is.

**What this is NOT.**

- The structure decomposition was dual-judged (Opus 4.6 and GPT-5.4, zero skips). Both put content at 80–94% of the effect; they differ on the format's small residual (6% vs 20%), so the *exact* structure share is judge-dependent — but "content dominates" is not.
- Frontier LLMs grading frontier LLMs — no human eval, no non-LLM ground truth.
- "Coverage" is an LLM-judge rubric score, not a behavioural outcome; six cases; my author-chosen prose. Re-run it with your own fixtures and your own prose and tell me if structure ever wins.

Runs are committed (run `2026-06-24_tk-prose-control-6`, fixtures hashed in the manifest) so you can reproduce the decomposition.

Repo and benchmark: https://murphysig.dev/benchmark

The ask: independent replication, more families/sizes, a second judge on the structure split, and — most of all — tell me if a structured block ever beats matched prose. If it does, I want the case. If it doesn't, the convention is a discipline, and I'd rather say that than oversell a format.

---

<!--
Signed: Kev + claude-opus-4-8, 2026-06-24
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Confidence: 0.88 — the content-dominates result is dual-judge robust (Opus + GPT-5.4, 6 families, 0 skips, length-parity enforced). The format's small residual is judge-dependent (6%–20%); I state the range rather than pick. The "discipline not format" reframe is my interpretation, stated as such.
Open: Does a structured block ever beat length/content-matched prose with HUMAN-written signatures, or under a third judge? Below what capability does the content effect itself vanish?
Prior: scratch/hn-relaunch-2026-06-24.md v1 (led with "structure earns its keep" — refuted by this run)

Reviews:

2026-07-12 (Kev + claude-fable-5): Added the "practising it, audited by itself"
section — findings from the first repo-wide sig audit (scratch/
sig-audit-2026-07-12.md): 9 minds in the provenance, 15/92 review rate, the
heuristic_scorer closed loop, false-positive smells cleared by judgment. I am
both the auditor and a subject of the audit; stated as such in the report.
Also of note since v2: llms.txt now carries an install path, init.sh wires
AGENTS.md (not Claude-only), and the site is Google/IndexNow-submitted — the
front door now matches the post. Confidence unchanged at 0.88.
-->
