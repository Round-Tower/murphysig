# TK benchmark — google/gemini-3.5-flash, judge-scored
_Judge: openai/gpt-5.4 (same judge + rubric as the Claude-only TK run). n=50 briefings re-scored; no new subject calls._

## Signed vs unsigned (the TK delta)
| Variant | n | Coverage | Accuracy | Hedging | Referenced sig |
|---|--:|--:|--:|--:|--:|
| unsigned | 25 | 0.70 | 0.79 | 1.00 | 0/25 |
| signed | 25 | 0.78 | 0.76 | 1.00 | 9/25 |
