# TK benchmark — google/gemini-3.5-flash, judge-scored
_Judge: anthropic/claude-opus-4.6 (same judge + rubric as the Claude-only TK run). n=50 briefings re-scored; no new subject calls._

## Signed vs unsigned (the TK delta)
| Variant | n | Coverage | Accuracy | Hedging | Referenced sig |
|---|--:|--:|--:|--:|--:|
| unsigned | 25 | 0.67 | 0.87 | 1.12 | 0/25 |
| signed | 25 | 0.75 | 0.87 | 1.04 | 18/25 |
