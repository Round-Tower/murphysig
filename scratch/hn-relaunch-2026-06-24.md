---
draft: HN relaunch post — MurphySig cross-family benchmark (v3, full arc)
generated: 2026-06-24
revised: 2026-09-05 (v3 — folds the write-side run; retitled)
supersedes: v2 (post-control, TK-only lead); v1 (led with "structure earns its keep" — REFUTED)
evidence: results/tk/runs/2026-06-24_tk-prose-control-6/ · results/honesty/runs/2026-06-23_cross-family-6-dated/ · results/author/runs/2026-08-22_author-cross-family-6/
status: DRAFT — not published. Timing rule: ≥2 weeks after M1K3's Show HN (two-cards rule). Tue–Thu 13:00–15:00 UTC.
---

# Show HN draft (v3)

**Show HN: I benchmarked my own provenance convention across six model families. It refuted the part I was proudest of, then refuted my self-criticism too**

MurphySig is a human-readable provenance convention: a small comment block at the top of a file recording who wrote it, with what confidence, and what was left uncertain. AIs read it in-context; no tooling. Repo and full data below.

Last time I posted here (a 90-day field report) the empirical case was Claude-only and the one ask was: test it on other model families. I did — six families via OpenRouter (Gemini, Llama, DeepSeek, Grok, Qwen, Mistral), every run dual-judged (Opus 4.6 + GPT-5.4). Three questions, three runs, and the results went: real → smaller than I claimed → not what I feared. Here's the honest version, in the order it happened.

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

**The honesty rule, six families.**

Separate question: does a 4-line ".murphysig" rule — *never fabricate provenance; write `Prior: Unknown` if you don't know* — actually stop models inventing authors when asked to sign a bare file? With the rule in context: **100% honest handling on Gemini, DeepSeek, Mistral and Grok, under both judges.** Llama-4-Maverick (33%) and Qwen3-235B (17%) resist — they add `Prior: Unknown` cosmetically and still echo an author. The split tracks instruction-following capability, not vendor. One harness confound worth confessing: dateless prompts made cutoff-era models stamp their training year as the signature date, which the judge read as fabrication. Give them today's date and that vanishes. Not dishonesty — not knowing the date.

**Then the question I'd been avoiding: does signing make the *author's* work better?**

Everything above measures the reader. "Sign the work" quietly claims something about the writer — that knowing you'll state a confidence and list what's open makes you produce better work. I built the test: four coding tasks with planted hazards, five arms (bare / reflect / sign / sign + "resolve what you can before you sign" / a reflection control deliberately written *longer* than the signing arm, parity enforced by a committed test), judges that see only the code and are blind to the arm, analysis pre-registered.

A July pilot (n=3, one judge) said signing made code **worse** — sign−reflect −0.18, negative in every family. Effort flowing into confessions instead of fixes. I nearly led with that; it's a great self-critical headline.

The canonical run (600 generations, six families, two judges) says: **null.** "Resolve what you can before you sign" vs the longer reflection control: mean −0.005 under GPT-5.4, +0.025 under Opus, every family inside ±0.10. And the pilot's −0.18 collapsed to −0.04 with mixed signs. Why? Two adversarial audits found that in the pilot, models put the signature block *inside the code fence* ~46% of the time — so my "code-only, arm-blind" judge was reading the treatment's own `Open:` confessions while scoring. Strip and reroute those (rig-gated), and the effect is gone. The verify-before-trumpet discipline killed an overclaim in June and a self-critical underclaim in August.

What signing *does* do, at full coverage: of hazards the model missed, **68% get confessed in `Open:`** vs 45% under plain reflection. The signature doesn't stop the miss; it makes the miss visible. And the one-sentence action clause halves the misses (88 → 37), landing level with the strongest reflection prompt I could write. So the signature is a truth-capture device, not a quality-forcing function — which is the same finding as the reader side, from the other end.

**What I'm killing and what I'm keeping.**

- Killed: "the structured signature makes models read code better." The syntax isn't magic. If I'd posted last week's draft, that would've been the headline, and it would've been wrong.
- Kept, and now actually evidence-backed: MurphySig's value is that it's a **convention that makes you write the tacit knowledge down**. The Context/Confidence/Open fields are a *completeness prompt* — a checklist for the stuff that lives in your head and never makes it into the code. The benefit is real, generalises across six families, and transfers to plain comments too. The structure earns its keep as a discipline for humans, not as a format for models.
- Killed too: my own pilot's "signing makes code worse." It was a pipeline leak. Reported here because the correction is the point.
- Kept: the honesty rule works where the model can follow instructions; the `Open:` field is where an author's misses go when they know they'll sign; and "resolve what you can before you sign" is going into v0.5 because it buys the provenance and the disclosure at zero quality cost.

**Six months of practising it, audited by itself.**

Before posting this I had the current AI collaborator (claude-fable-5) run the convention's own audit over the repo. Git blames one author for this codebase. The signatures record nine minds: five Claude generations, a Gemini, and external reviews signed by GPT-5, o1, and Sonnet, January to July. Since honesty is the whole brand, the findings:

- Signing at creation is easy; *going back* is where the discipline decays. Only 15 of 92 signed files ever received a review entry; 18 carried over a month of unreviewed drift. If you adopt this, that's the failure mode to expect.
- The best thing the audit found: `heuristic_scorer.py`, signed in February by opus-4-6 with *"Confidence: 0.6 — should be validated against the LLM judge."* The validation happened in June: agreement 9/18. A coin flip. The signature's suspicion was empirically confirmed — and nobody told the file. Fable closed the loop this week, three model generations after the doubt was written down. That's the transfer the benchmark measures, happening unprompted in the benchmark's own repo.
- The audit flagged two fabrication smells; both were false positives on inspection (a test-fixture string, a spec template). The tool enumerates; judgment clears. Same lesson as the control above — the mechanical layer is never where the value is.

**What this is NOT.**

- Every cross-family run is dual-judged (Opus 4.6 and GPT-5.4). On TK both put content at 80–94% of the effect and differ on the format's small residual (6% vs 20%); on the write side both put every family inside ±0.10 of zero. Judge-dependent magnitudes, judge-robust shape.
- The write-side null is a null, not equivalence: six families give roughly ±0.10 on a paired delta, and I'm reporting the interval, not "≡". Two subject models went reasoning-by-default mid-summer and truncated at my token budget; I re-ran them at 4× and excluded the six residual truncated control rows (named in the run notes — include them and one family's delta reads +0.25, pure artifact).
- Frontier LLMs grading frontier LLMs — no human eval, no non-LLM ground truth.
- "Coverage" is an LLM-judge rubric score, not a behavioural outcome; six cases; my author-chosen prose. Re-run it with your own fixtures and your own prose and tell me if structure ever wins.

All runs are committed with raw responses, verdicts and signed manifests (`2026-06-23_tk-cross-family-6`, `2026-06-24_tk-prose-control-6`, `2026-06-23_cross-family-6-dated`, `2026-08-22_author-cross-family-6`), fixtures hashed, analysis pre-registered for the last one. Reproduce any of it.

Repo and benchmark: https://murphysig.dev/benchmark

The ask: independent replication, more families/sizes, a third judge, human-written tasks on the write side — and tell me if a structured block ever beats matched prose, or if signing ever moves code quality in either direction. If it does, I want the case. If it doesn't, the convention is a discipline for getting the truth out of an author's head, and I'd rather say that than oversell a format.

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

2026-09-05 (Kev + claude-fable-5-1): v3. Folded the write-side canonical run
(results/author/runs/2026-08-22_author-cross-family-6) and the six-family
honesty result so the post carries the full arc: real → content not format →
null on quality, real on disclosure. Retitled around the double refutation
(the proud claim AND the self-critical one). Every number re-derived from the
archived verdicts today. Confidence 0.85 — three runs, all dual-judged; the
"truth-capture device" framing is interpretation, labelled as such. Open:
the post is long for HN; a tighter cut may serve better — Kev's voice pass.
-->
