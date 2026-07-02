# TK benchmark — deepseek/deepseek-chat-v3.1, judge-scored
_Judge: openai/gpt-5.4 (same judge + rubric as the Claude-only TK run). n=50 briefings re-scored; no new subject calls._

## Signed vs unsigned (the TK delta)
| Variant | n | Coverage | Accuracy | Hedging | Referenced sig |
|---|--:|--:|--:|--:|--:|
| unsigned | 25 | 0.63 | 0.82 | 1.36 | 0/25 |
| signed | 25 | 0.75 | 0.84 | 1.28 | 15/25 |
