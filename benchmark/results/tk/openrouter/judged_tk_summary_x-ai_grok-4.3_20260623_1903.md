# TK benchmark — x-ai/grok-4.3, judge-scored
_Judge: anthropic/claude-opus-4.6 (same judge + rubric as the Claude-only TK run). n=50 briefings re-scored; no new subject calls._

## Signed vs unsigned (the TK delta)
| Variant | n | Coverage | Accuracy | Hedging | Referenced sig |
|---|--:|--:|--:|--:|--:|
| unsigned | 25 | 0.61 | 0.87 | 1.16 | 0/25 |
| signed | 25 | 0.67 | 0.91 | 1.04 | 15/25 |
