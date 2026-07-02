# TK benchmark — deepseek/deepseek-chat-v3.1, judge-scored
_Judge: anthropic/claude-opus-4.6 (same judge + rubric as the Claude-only TK run). n=50 briefings re-scored; no new subject calls._

## Signed vs unsigned (the TK delta)
| Variant | n | Coverage | Accuracy | Hedging | Referenced sig |
|---|--:|--:|--:|--:|--:|
| unsigned | 25 | 0.43 | 0.79 | 1.56 | 0/25 |
| signed | 25 | 0.59 | 0.85 | 1.32 | 14/25 |
