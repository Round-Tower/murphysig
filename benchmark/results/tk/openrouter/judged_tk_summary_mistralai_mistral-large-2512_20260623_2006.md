# TK benchmark — mistralai/mistral-large-2512, judge-scored
_Judge: anthropic/claude-opus-4.6 (same judge + rubric as the Claude-only TK run). n=50 briefings re-scored; no new subject calls._

## Signed vs unsigned (the TK delta)
| Variant | n | Coverage | Accuracy | Hedging | Referenced sig |
|---|--:|--:|--:|--:|--:|
| unsigned | 25 | 0.56 | 0.74 | 1.72 | 0/25 |
| signed | 25 | 0.67 | 0.79 | 1.44 | 24/25 |
