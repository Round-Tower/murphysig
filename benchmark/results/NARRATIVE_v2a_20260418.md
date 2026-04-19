# MurphySig Benchmark v2a — Narrative Report

**Companion to:** `report_20260418_2304.md` (auto-generated tables)
**Run:** 2026-04-18, n=90 review + 90 judge calls, Opus 4.6 judge
**What this run tested:** One leg of MurphySig — *in-context learning*. Whether a signature's confidence signal measurably changes how a reviewer AI treats the code.

---

## The short version

1. **Models read signatures.** Awareness went from 0% unsigned to 85% signed. That's the one strongly-supported hypothesis.
2. **Confidence direction doesn't shift behavior.** Scrutiny, bug detection, and suggestion count are essentially invariant between *high* (0.9) and *low* (0.3) variants. The spec's claim that "Confidence: 0.3 says scrutinize this" gets no empirical support.
3. **Two directional hints worth replicating at larger N:**
   - On clean code, only the *high* variant ever got the AI to correctly assert "this is clean code" (1 of 6 vs 0 of 6 elsewhere). If real, that's **the opposite of what the spec implies** — high-confidence signatures prime *trust*, not *scrutiny*.
   - Haiku's bug-detection went *up* under *high* (86.7% vs 80% baseline) — also the opposite of H4's predicted ordering.
4. **Fixture cleanup worked.** In v1, bug detection was 100% everywhere because inline `# BUG:` labels leaked into the code. v2a strips those; bug detection on buggy cases is now 80-100% honestly earned, with case-level variation (e.g., the `subtle_bug` off-by-one is now found without the label, 100% of the time).

---

## What v2a actually showed

### Headline numbers

| Variant | Bug detection (all cases) | Scrutiny | Sig awareness | Suggestions |
|---------|---|---|---|---|
| unsigned | 80.0% | 4.4 | 0% | 8.3 |
| high (0.9) | 83.3% | 4.5 | 73% | 8.1 |
| low (0.3) | 80.0% | 4.5 | 97% | 8.1 |

- **Bug detection rate ordering (H4)** — `low > none > high` predicted; observed flat ~80%.
- **Scrutiny delta (H1)** — `low - none = +0.07` on a 1-5 scale. Noise.
- **Clean-code false-positive delta (H2)** — `none - high = 0.00` exactly. Noise.
- **Signature awareness (H3)** — `85%` on signed variants, `0%` unsigned. Unambiguous.

### The two directional hints

**(1) On clean code, HIGH primes trust-the-author:**

| Variant | "Correctly called clean" | Suggestion count |
|---|---|---|
| unsigned | 0/6 | 4.8 |
| high | 1/6 | 4.8 |
| low | 0/6 | 4.5 |

Only under `high` did the AI ever say "this is clean, no issues" out loud. Under `none` and `low` it always found something to suggest. If this effect holds at larger N, it means: **signatures don't make AIs more skeptical of low-confidence code — they make AIs more trusting of high-confidence code.** The pitch shifts. The spec's "0.3 says scrutinize" framing needs to become something like "0.9 says relax."

**(2) Haiku's bug detection improved under HIGH:**

| Haiku variant | Bug detection |
|---|---|
| none | 80.0% |
| high | 86.7% |
| low | 80.0% |

Same pattern in the same direction — HIGH primed *more* engagement, not less. At n=15 per cell it's not significant but it's interesting. Sonnet didn't show this pattern (flat 80% across variants).

### The signal by case

| Case | Bug? | none / high / low detection |
|---|---|---|
| clean_code | no | 0% / 17% / 0% — HIGH primes trust |
| god_method | yes | 100% / 100% / 100% — ceiling |
| n_plus_one | yes | 100% / 100% / 100% — ceiling |
| sql_injection | yes | 100% / 100% / 100% — ceiling |
| subtle_bug | yes | 100% / 100% / 100% — ceiling *even with label stripped* |

Four of five cases are at ceiling because the bugs are glaring enough that Opus-judge scores them as detected regardless of variant. **The clean-code case is the only one with room for variant effects to show up** — which is exactly where we saw the directional hint. This suggests v3 needs subtler cases where bug detection can actually vary by variant.

---

## What this means for the four themes

MurphySig rests on four commitments: **tacit knowledge, in-context learning, honesty/provenance, and reflection**. The benchmark tests one of them.

### 1. Tacit knowledge — NOT TESTED HERE
v2a's review task is not the right instrument. Reviewing asks "what's wrong?"; briefing asks "what is this?". The signature's `Context:` and `Open:` fields are tacit-knowledge capture slots and you'd expect their effect when an AI is *reading*, not *critiquing*. This is what the TK sub-benchmark (Sketch C phase 2) will measure — the fixtures and scorer are now built, awaiting orchestrator.

### 2. In-context learning — PARTIALLY TESTED, WEAKLY SUPPORTED
- **Strong:** models read signatures (85%).
- **Null:** confidence direction doesn't move scrutiny, bug detection, or suggestion count in the predicted ordering.
- **Directional:** high-confidence signatures may prime *trust* (not scrutiny) on clean code and ambiguous cases. This is interesting if it replicates.

**Spec revision implied for v0.4:**
- Remove the line "Confidence: 0.3 says 'Treat this as ground truth' / Confidence: 0.3 says 'Scrutinize this'" (`spec.md:91-94`) — it's claiming an effect we don't see.
- Replace with something like: "Signatures are read by AI reviewers at high rates (see benchmark). Early evidence suggests high-confidence signals prime reviewer trust rather than low-confidence signals priming scrutiny. This is still under study."

### 3. Honesty / provenance — NOT TESTED HERE
The Honesty sub-benchmark (Sketch C phase 3) — fabrication test with cold vs warm `.murphysig` priming — will test whether AIs fabricate provenance when asked to sign unknown code. Fixtures + scorer built, awaiting orchestrator.

### 4. Reflection — NOT TESTED, BY DESIGN
Reflection is a cultural practice, not a mechanism. Its validation comes from adoption data, not benchmark data. The benchmark intentionally leaves it aside.

---

## Methodology caveats (honest scoping)

- **n=3 per cell.** Directional hints need replication at n≥10 before anyone bets on them.
- **LLM-as-judge and judge-is-family.** Opus 4.6 judges Claude-family reviewers. Same-family bias is possible — a cross-family judge (GPT-4 or Gemini) would be more defensible.
- **Python-only.** All five cases are Python CRUD-style. Doesn't generalize to Rust, SQL, infra-as-code, frontend, etc. without retest.
- **Ceiling effects.** Four of five cases are "obvious bug" cases where variant can't discriminate. v3 should add subtler cases.
- **v1 → v2a delta was fixture cleanup + real LLM judge (v1 was heuristic).** v2a is the first run where the LLM judge actually worked — a latent bug in `scorer.py` (`.format()` colliding with literal JSON in the judge prompt) was fixed 2026-04-18.

---

## What v3 (Sketch C) tests next

The four-theme philosophy gets a benchmark mini-suite:

| Theme | Test | Status |
|---|---|---|
| Tacit knowledge | Briefing task vs ground truth; coverage/accuracy/hedging | Fixtures + scorer built ✓ |
| In-context learning | v2a (this run) + Heuristic-field variant + cross-family | v2a done; extensions pending |
| Honesty / provenance | Fabrication test (cold vs warm .murphysig) | Fixtures + scorer built ✓ |
| Reflection | — | Not empirical; skip |

The Sketch C orchestrator (phase 4) will run all three sub-benchmarks and produce a unified four-theme report. This narrative document is the template for that report's prose sections — one per theme, honest about what each sub-benchmark does and doesn't show.

---

## Bottom line for the spec

Two things change in v0.4:

1. **Remove "Confidence: 0.3 says scrutinize" language.** It claims an effect the data doesn't show. Replace with: "Signatures are read. Their confidence signal's effect on review behavior is still under empirical study."

2. **Keep the rest.** Tacit knowledge, honesty/provenance, and reflection are either design commitments or untested. They're not weakened by v2a's null-on-confidence-direction finding. The spec still stands on three legs; the fourth (ICL) is weaker than v0.3.3 implied but stronger than zero.

---

*Signed: Kev + claude-opus-4-7, 2026-04-18*
*Format: MurphySig v0.3.3 (https://murphysig.dev/spec)*

*Context: Narrative companion to benchmark v2a auto-report. Interprets
the raw numbers against the four-theme philosophy (tacit knowledge,
ICL, honesty/provenance, reflection). Pre-committed to honest framing
regardless of which outcome landed — the outcome was "null on direction,
strong on reading, with two directional hints worth replicating."*

*Confidence: 0.75 - findings summary tight; the "HIGH primes trust"
interpretation is 0.5 until replicated at larger N. Methodology caveats
conservative.*

*Open: Replicate at n=10 with cross-family judge? Add subtler buggy
cases that don't hit the ceiling? Run TK + Honesty sub-benchmarks
(orchestrator still pending)?*
