# TK cross-family — signature uplift (signed − unsigned)
_Delta is within-model (same model briefs each case twice), so it controls for raw capability. Positive Δcoverage and negative Δhedging are the MurphySig effect._

| Model | n (u/s) | Coverage u→s | Δcoverage | Δhedging | Referenced sig (signed) |
|---|---|---|--:|--:|--:|
| deepseek/deepseek-chat-v3.1 | 25/25 | 0.63→0.75 | +0.12 | -0.08 | 15/25 (60%) |
| google/gemini-3.5-flash | 25/25 | 0.70→0.78 | +0.08 | +0.00 | 9/25 (36%) |
| meta-llama/llama-4-maverick | 25/25 | 0.50→0.70 | +0.20 | -0.24 | 18/25 (72%) |
| mistralai/mistral-large-2512 | 25/25 | 0.61→0.74 | +0.13 | -0.40 | 21/25 (84%) |
| qwen/qwen3.7-plus | 25/25 | 0.69→0.81 | +0.12 | -0.16 | 20/25 (80%) |
| x-ai/grok-4.3 | 25/25 | 0.72→0.81 | +0.09 | -0.04 | 13/25 (52%) |

# TK structure vs content — does the signature's *form* matter?
_Δstructure = signed − prose (same facts, structured vs plain prose) is the headline. Δcontent = prose − unsigned (the information alone). Δtotal = signed − unsigned._

| Model | n (u/p/s) | Coverage u/p/s | Δstructure | Δcontent | Δtotal |
|---|---|---|--:|--:|--:|
| deepseek/deepseek-chat-v3.1 | 25/25/25 | 0.63/0.72/0.75 | +0.03 | +0.09 | +0.12 |
| google/gemini-3.5-flash | 25/25/25 | 0.70/0.77/0.78 | +0.00 | +0.08 | +0.08 |
| meta-llama/llama-4-maverick | 25/25/25 | 0.50/0.65/0.70 | +0.05 | +0.14 | +0.20 |
| mistralai/mistral-large-2512 | 25/25/25 | 0.61/0.72/0.74 | +0.02 | +0.11 | +0.13 |
| qwen/qwen3.7-plus | 25/25/25 | 0.69/0.78/0.81 | +0.03 | +0.09 | +0.12 |
| x-ai/grok-4.3 | 25/25/25 | 0.72/0.80/0.81 | +0.02 | +0.08 | +0.09 |

