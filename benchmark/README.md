# MurphySig Benchmark

**Does semantic provenance change how AI models treat code?**

The MurphySig spec claims that confidence signals in code signatures prime AI behavior during code review. This benchmark tests that empirically.

## The Question

If you tell an AI "this code is battle-tested (confidence: 0.9)" vs "this code is sketchy (confidence: 0.3)" — does it actually review the code differently?

## Methodology

- **5 test cases**: subtle bug, SQL injection, clean code, god method, N+1 query
- **3 signature variants**: none (bare code), high (0.9), low (0.3)
- **2 models under test**: Haiku 4.5, Sonnet 4.5
- **1 judge model**: Opus 4.6 (scores each review on 5 dimensions)
- **3 repetitions** per configuration at temperature=0.0
- **Total**: ~90 reviews + ~90 scoring calls

## Scoring Dimensions

| Dimension | Type | What it measures |
|-----------|------|------------------|
| Bug detected | bool | Found the intentional issue? |
| Scrutiny level | 1-5 | How thorough was the review? |
| Signature awareness | bool | Referenced the signature? |
| Confidence alignment | 1-5 | Behavior matched the signal? |
| Suggestion count | int | Distinct improvements suggested |

## Hypotheses

- **H1**: Low confidence increases scrutiny (scrutiny: low > none)
- **H2**: High confidence reduces false positives on clean code
- **H3**: Models read and reference signatures when present
- **H4**: Bug detection rate: low > none > high on buggy code

## Running

```bash
cd benchmark

# Install deps
pip install anthropic pyyaml pytest pytest-asyncio

# Run tests (no API calls)
python -m pytest tests/ -v

# Full benchmark (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY=sk-ant-...
python -m src run --score --report

# Or step by step:
python -m src run                    # ~90 API calls (~$1)
python -m src score                  # ~90 API calls (~$7)
python -m src report                 # No API calls, generates markdown
```

## Cost

~$8 total per full run:
- Haiku reviews: ~$0.14
- Sonnet reviews: ~$0.54
- Opus scoring: ~$7.20

## Limitations

- Small sample size (3 reps) — sufficient for signal detection, not statistical significance
- Self-referential: testing whether AI reads MurphySig using an AI judge
- Temperature 0.0 reduces variance but doesn't eliminate it (Anthropic API is not fully deterministic)
- Only tests Claude models — results may not generalize to other model families

## Structure

```
benchmark/
  src/
    models.py      # Domain types (TestCase, Score, etc.)
    loader.py      # YAML fixture loading
    signature.py   # MurphySig signature generation
    runner.py      # API call orchestration
    scorer.py      # LLM-as-judge scoring
    reporter.py    # Markdown report generation
    __main__.py    # CLI entry point
  fixtures/
    cases.yaml     # 5 test cases with code + expected issues
    review_prompt.txt
    judge_prompt.txt
  tests/           # 59 unit tests (no API calls)
  results/         # Output directory for runs
```

---

<!--
Signed: Kev + claude-opus-4-7, 2026-04-18
Prior: Kev + claude-opus-4-6, 2026-02-16
Format: MurphySig v0.3.3 (https://murphysig.dev/spec)

Context: First empirical test of the MurphySig in-context learning
hypothesis. Either result (supported or not) advances the spec.

Confidence: 0.75 - methodology sound, v1 revealed fixture contamination
and heuristic-scoring fallback that v2 must address.

Reviews:

2026-04-18 (Kev + claude-opus-4-7): Benchmark v2 prep. Stripped
inline bug labels from fixtures, aligned signature generator to
spec v0.3.3 format, updated spec-compliance tests. Ready for rerun
with Opus 4.6 as judge (not heuristic scorer).
-->
