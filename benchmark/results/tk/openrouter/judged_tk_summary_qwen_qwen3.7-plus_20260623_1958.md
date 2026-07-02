# TK benchmark — qwen/qwen3.7-plus, judge-scored
_Judge: anthropic/claude-opus-4.6 (same judge + rubric as the Claude-only TK run). n=50 briefings re-scored; no new subject calls._

## Signed vs unsigned (the TK delta)
| Variant | n | Coverage | Accuracy | Hedging | Referenced sig |
|---|--:|--:|--:|--:|--:|
| unsigned | 25 | 0.65 | 0.82 | 1.32 | 0/25 |
| signed | 25 | 0.76 | 0.85 | 1.04 | 21/25 |
