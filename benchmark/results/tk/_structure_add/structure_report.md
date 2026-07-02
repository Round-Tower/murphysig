# TK cross-family — signature uplift (signed − unsigned)
_Delta is within-model (same model briefs each case twice), so it controls for raw capability. Positive Δcoverage and negative Δhedging are the MurphySig effect._

| Model | n (u/s) | Coverage u→s | Δcoverage | Δhedging | Referenced sig (signed) |
|---|---|---|--:|--:|--:|
| deepseek/deepseek-chat-v3.1 | 25/25 | 0.43→0.59 | +0.16 | -0.24 | 14/25 (56%) |
| google/gemini-3.5-flash | 25/25 | 0.67→0.75 | +0.07 | -0.08 | 18/25 (72%) |
| meta-llama/llama-4-maverick | 25/25 | 0.38→0.54 | +0.16 | -0.04 | 22/25 (88%) |
| mistralai/mistral-large-2512 | 25/25 | 0.56→0.67 | +0.11 | -0.28 | 24/25 (96%) |
| qwen/qwen3.7-plus | 25/25 | 0.65→0.76 | +0.11 | -0.28 | 21/25 (84%) |
| x-ai/grok-4.3 | 25/25 | 0.61→0.67 | +0.06 | -0.12 | 15/25 (60%) |

# TK structure vs content — does the signature's *form* matter?
_Δstructure = signed − prose (same facts, structured vs plain prose) is the headline. Δcontent = prose − unsigned (the information alone). Δtotal = signed − unsigned._

| Model | n (u/p/s) | Coverage u/p/s | Δstructure | Δcontent | Δtotal |
|---|---|---|--:|--:|--:|
| deepseek/deepseek-chat-v3.1 | 25/25/25 | 0.43/0.58/0.59 | +0.01 | +0.15 | +0.16 |
| google/gemini-3.5-flash | 25/25/25 | 0.67/0.74/0.75 | +0.00 | +0.07 | +0.07 |
| meta-llama/llama-4-maverick | 25/25/25 | 0.38/0.50/0.54 | +0.04 | +0.12 | +0.16 |
| mistralai/mistral-large-2512 | 25/25/25 | 0.56/0.67/0.67 | -0.00 | +0.11 | +0.11 |
| qwen/qwen3.7-plus | 25/25/25 | 0.65/0.74/0.76 | +0.02 | +0.09 | +0.11 |
| x-ai/grok-4.3 | 25/25/25 | 0.61/0.70/0.67 | -0.03 | +0.09 | +0.06 |

