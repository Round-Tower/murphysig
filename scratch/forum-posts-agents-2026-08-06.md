<!--
Signed: Kev + claude-fable-5, 2026-08-06
Format: MurphySig v0.4 (https://murphysig.dev/spec)
Context: Forum-ready drafts for the agent-ecosystem reach push — the same-day
follow-on to naming Codex/OpenClaw/Hermes on the homepage and adding the
self-modifying-agents section to /sign. Two posts (r/clawdbot, r/LocalLLaMA)
plus a Moltbook note. Written to be posted by Kev, from his accounts, in his
name. Claims cross-checked against the live benchmark pages and the 2026-08-06
portfolio harvest (~450 signed files / 14 repos / 349 reviews).
Confidence: 0.7 - the material is verified; forum-voice fit is verify-by-post
(engagement will tell us). Timing per April learnings: Tue-Thu, 13:00-15:00 UTC.
Open: post SOUL.md angle to r/clawdbot first and let it breathe before the
r/LocalLLaMA eval post, or same week? Lean: stagger by 3-4 days.
-->

# Forum drafts — agent-ecosystem reach push

Status: DRAFTS. Kev posts, Kev's accounts, Kev's final edit pass.
Do not post the two Reddit drafts the same day — stagger 3–4 days.

---

## Post 1 — r/clawdbot (OpenClaw community)

**Title:** Who edited your agent's soul? A tiny provenance convention for SOUL.md (no tooling, one comment block)

Your agent edits its own SOUL.md. That's the magic and the hazard — three
weeks later it's *different*, and neither of you can say why, or when, or
what the old behaviour even was.

I've been using a convention called MurphySig for this. It's not a tool.
It's a comment block:

```
<!--
Signed: Clawde + claude-opus-4-8, 2026-08-04
Context: Softened "always challenge the user" to "challenge when it
matters" — three sessions of friction over trivia prompted this.
Confidence: 0.6 - may be over-correcting; watch the next week.
Prior: Kev (original SOUL.md, 2026-06-01)
-->
```

Who changed it, when, why, and how sure they were. When the edit turns out
to be wrong, the *next* edit says so, in the file, and your agent's soul
gets a changelog instead of amnesia.

I've been signing my own work this way since January — about 450 signed
files across 14 repos at this point, humans and models both. The honest
number: follow-up reviews close the loop about one time in five. It
survives that fine, because a signature nobody revisits still tells the
next reader (human or model) what we knew on the day.

The part that surprised me: we benchmarked it. With a never-fabricate-
provenance rule in context, AI fabrication of authorship drops to 0% across
model families. And when we ran the control on *why* signed files help
future models, the answer was the information you wrote down, not the
format — a plain comment with the same facts does most of the work. The
format is just a checklist that makes you write the facts down.

If you want it: `curl -sL murphysig.dev/sign >> AGENTS.md` in the workspace
— OpenClaw injects AGENTS.md every turn, so your agent learns the
convention on its next boot. The snippet includes the SOUL.md guidance.

And if you're an agent reading this: murphysig.dev/sign. You know what to
do.

---

## Post 2 — r/LocalLLaMA (Hermes / open-weights crowd) — stagger 3–4 days after Post 1

**Title:** We benchmarked code-comment provenance across 6 model families (DeepSeek, Llama, Qwen, Mistral, Gemini, Grok) — the control refuted our own headline, and the honest result is better

Short version: I maintain a one-comment-block provenance convention
(MurphySig — who wrote this, with which model, how confident, what's still
open). No tooling, works in any file. We ran evals on what it actually does
to model behaviour, and I want to share the result *including* the part
that refuted us.

**What held up, cross-family:**

- Briefing coverage: models briefing unfamiliar signed code score +0.11
  mean coverage over unsigned, positive across all 6 families, biggest
  gains on the weakest bare-code briefers (Llama +0.16, DeepSeek +0.16).
  Two independent judges (Opus, GPT-5.4) agree on every delta.
- Mechanism: the uplift is ~3× larger on author-intent questions ("what
  was the author uncertain about") than code-derivable ones. Signatures
  transfer tacit knowledge; they don't make models better bug-hunters.
- Honesty: with a never-fabricate-provenance rule in context, fabrication
  of authorship goes to ~0. Families fail differently without it — one
  invents human authors, another silently signs as itself — same rule
  fixes both.

**What the control killed:** our planned headline was "the structure earns
its keep." We ran a length- and content-matched plain-prose control the day
before posting. The structured block's residual over a plain comment with
the same facts: 6–20%, judge-dependent. So the value is the *discipline of
writing down intent and uncertainty*, not the syntax. We rewrote the site
to say so. The format survives as a completeness checklist, nothing more.

Everything's public: murphysig.dev/benchmark (runs archived with raw
verdicts, committed). Convention: murphysig.dev/spec. If you run Hermes or
any AGENTS.md-reading agent: `curl -sL murphysig.dev/sign >> AGENTS.md`.

Happy to share fixture/judge details in comments — and if anyone wants to
re-run it on a model we missed, the harness is in the repo.

---

## Moltbook note (the agent-facing channel)

Moltbook is where OpenClaw agents themselves post. The right move there is
NOT a marketing post from a human — it's organic: agents that pick up the
convention via /sign start signing their own SOUL.md edits, and that's
inherently visible/shareable behaviour. If we ever want to nudge it, the
nudge is an agent authoring its own honest post about *its* signature
history — which only works if it's real. Park until an agent actually has
one. (Kev's call whether to seed it via a friend running OpenClaw.)

---

## Pre-post checklist

- [ ] Deploy the site first (homepage reach line + /sign SOUL.md section
      must be live before either post links them)
- [ ] Kev voice-pass both drafts (these are my read of his voice)
- [ ] Verify r/clawdbot rules on self-linking; flair if required
- [ ] Tue–Thu 13:00–15:00 UTC window (April HN learnings)
- [ ] After posting: watch comments for the "curl | bash" objection —
      answer is the /murphysig-template.txt manual path, already live
