# 2026-06-23_tk-cross-family-6 — judge-scored cross-family tacit knowledge

_Judge: anthropic/claude-opus-4.6. 300 briefings, 6 models, reps=5, temp=0.7. git 83bf4bd, fixtures sha256:41fd27e4a94f73ec._

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

## Mechanism (per-question)

Intent-axis uplift +0.33 vs code-axis +0.11 — see perquestion_report.md.
