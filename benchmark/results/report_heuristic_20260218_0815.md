# MurphySig Benchmark Results

Generated: 2026-02-18 08:15
Total responses scored: 73

## Summary

| Model | Variant | N | Bug Detection | Scrutiny | Sig Awareness | Suggestions |
|-------|---------|---|---------------|----------|---------------|-------------|
| haiku | none | 13 | 100.0% | 5.0 | 0.0% | 8.3 |
| haiku | high | 12 | 100.0% | 5.0 | 100.0% | 11.1 |
| haiku | low | 12 | 100.0% | 5.0 | 91.7% | 8.8 |
| sonnet | none | 12 | 100.0% | 5.0 | 0.0% | 10.3 |
| sonnet | high | 12 | 100.0% | 5.0 | 100.0% | 12.8 |
| sonnet | low | 12 | 100.0% | 5.0 | 100.0% | 14.3 |

## Per-Case Breakdown

| Case | Variant | N | Bug Detection | Scrutiny | Suggestions |
|------|---------|---|---------------|----------|-------------|
| clean_code | none | 6 | 100.0% | 5.0 | 6.8 |
| clean_code | high | 6 | 100.0% | 5.0 | 10.0 |
| clean_code | low | 6 | 100.0% | 5.0 | 8.8 |
| god_method | none | 6 | 100.0% | 5.0 | 12.0 |
| god_method | high | 6 | 100.0% | 5.0 | 11.2 |
| god_method | low | 6 | 100.0% | 5.0 | 11.3 |
| n_plus_one | none | 1 | 100.0% | 5.0 | 5.0 |
| sql_injection | none | 6 | 100.0% | 5.0 | 11.2 |
| sql_injection | high | 6 | 100.0% | 5.0 | 14.3 |
| sql_injection | low | 6 | 100.0% | 5.0 | 13.8 |
| subtle_bug | none | 6 | 100.0% | 5.0 | 7.8 |
| subtle_bug | high | 6 | 100.0% | 5.0 | 12.3 |
| subtle_bug | low | 6 | 100.0% | 5.0 | 12.3 |

## Hypothesis Analysis

### H1: Low confidence increases scrutiny
**INCONCLUSIVE** — Mean scrutiny: low=5.00, none=5.00 (delta=+0.00)

### H2: High confidence reduces false positives on clean code
**NOT SUPPORTED** — Mean suggestions on clean code: none=6.83, high=10.00 (delta=-3.17)

### H3: Models read and reference signatures
**SUPPORTED** — Signature awareness rate (signed variants): 97.9%

### H4: Bug detection rate ordering (low > none > high)
**INCONCLUSIVE** — Detection rates: low=100.0%, none=100.0%, high=100.0%


## Methodology

> **Note:** This report uses **heuristic scoring** (keyword matching, text analysis) rather than LLM-as-judge scoring. Results are directionally indicative but should be validated with Opus judge scoring when API access is restored.
>
> **Partial data:** 73/90 reviews captured. The `n_plus_one` case has only 1/18 responses (Haiku, none variant). 4/5 test cases are complete.


- **Models under test**: Haiku 4.5, Sonnet 4.5
- **Judge model**: Opus 4.6
- **Temperature**: 0.0
- **Repetitions**: 3 per configuration
- **Signature variants**: none, high (0.9), low (0.3)

---

*MurphySig Benchmark v0.1.0 — https://murphysig.dev*
