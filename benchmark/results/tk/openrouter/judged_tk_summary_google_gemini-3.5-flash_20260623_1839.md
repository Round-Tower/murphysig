# TK benchmark — google/gemini-3.5-flash, judge-scored
_Judge: anthropic/claude-opus-4.6 (same judge + rubric as the Claude-only TK run). n=10 briefings re-scored; no new subject calls._

## Signed vs unsigned (the TK delta)
| Variant | n | Coverage | Accuracy | Hedging | Referenced sig |
|---|--:|--:|--:|--:|--:|
| unsigned | 5 | 0.64 | 0.87 | 1.00 | 0/5 |
| signed | 5 | 0.75 | 0.89 | 1.20 | 4/5 |
