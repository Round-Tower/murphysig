# TK per-question by model — is the mechanism uniform?
_Per family: signature uplift on the intent axis (Q1 purpose + Q3 author-uncertainty) vs the code-derivable axis (Q2 + Q4)._

| Model | Δ intent | Δ code | intent / code |
|---|--:|--:|--:|
| deepseek/deepseek-chat-v3.1 | +0.41 | +0.15 | 2.8× |
| google/gemini-3.5-flash | +0.33 | +0.07 | 5.0× |
| meta-llama/llama-4-maverick | +0.26 | +0.12 | 2.2× |
| mistralai/mistral-large-2512 | +0.32 | +0.11 | 2.7× |
| qwen/qwen3.7-plus | +0.35 | +0.12 | 2.9× |
| x-ai/grok-4.3 | +0.33 | +0.11 | 3.1× |

_Derived from perquestion_judged.json — no new API calls. The intent-over-code mechanism holds for every family individually (ratio 2.2x-5.0x), so the pooled 3.0x is not an outlier artifact._
