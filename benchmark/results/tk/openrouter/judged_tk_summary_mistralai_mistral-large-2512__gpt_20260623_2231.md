# TK benchmark — mistralai/mistral-large-2512, judge-scored
_Judge: openai/gpt-5.4 (same judge + rubric as the Claude-only TK run). n=50 briefings re-scored; no new subject calls._

## Signed vs unsigned (the TK delta)
| Variant | n | Coverage | Accuracy | Hedging | Referenced sig |
|---|--:|--:|--:|--:|--:|
| unsigned | 25 | 0.61 | 0.73 | 1.44 | 0/25 |
| signed | 25 | 0.74 | 0.77 | 1.04 | 21/25 |
