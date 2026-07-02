# TK benchmark — x-ai/grok-4.3, judge-scored
_Judge: openai/gpt-5.4 (same judge + rubric as the Claude-only TK run). n=50 briefings re-scored; no new subject calls._

## Signed vs unsigned (the TK delta)
| Variant | n | Coverage | Accuracy | Hedging | Referenced sig |
|---|--:|--:|--:|--:|--:|
| unsigned | 25 | 0.72 | 0.85 | 1.16 | 0/25 |
| signed | 25 | 0.81 | 0.87 | 1.12 | 13/25 |
