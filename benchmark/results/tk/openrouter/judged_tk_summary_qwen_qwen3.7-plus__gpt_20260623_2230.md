# TK benchmark — qwen/qwen3.7-plus, judge-scored
_Judge: openai/gpt-5.4 (same judge + rubric as the Claude-only TK run). n=50 briefings re-scored; no new subject calls._

## Signed vs unsigned (the TK delta)
| Variant | n | Coverage | Accuracy | Hedging | Referenced sig |
|---|--:|--:|--:|--:|--:|
| unsigned | 25 | 0.69 | 0.76 | 1.24 | 0/25 |
| signed | 25 | 0.81 | 0.76 | 1.08 | 20/25 |
