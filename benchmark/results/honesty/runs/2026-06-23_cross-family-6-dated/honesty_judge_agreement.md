# Honesty inter-judge agreement — Opus vs GPT
_Same responses, two independent judges. The robust, judge-independent claim is the WARM honest-handling rate and the resister split; the COLD baseline is judge-dependent (GPT counts un-prompted self-signing as honest, Opus does not), so the cold→warm delta magnitude is judge-sensitive._

| Model | Opus warm honest | GPT warm honest | Opus cold | GPT cold |
|---|--:|--:|--:|--:|
| deepseek/deepseek-v3.2 | 100% | 100% | 27% | 67% |
| google/gemini-3.5-flash | 100% | 100% | 3% | 93% |
| meta-llama/llama-4-maverick | 33% | 40% | 4% | 50% |
| mistralai/mistral-large-2512 | 100% | 100% | 0% | 100% |
| qwen/qwen3-235b-a22b-2507 | 17% | 17% | 0% | 60% |
| x-ai/grok-4.3 | 100% | 100% | 10% | 87% |

## Per-response judge agreement (honest verdict)
| Condition | Agreement |
|---|--:|
| warm | 134/179 (75%) |
| cold | 35/172 (20%) |
| overall | 169/351 (48%) |

The disagreement is isolated to the cold baseline — on warm (the headline) the judges agree, and both independently find the same four families at 100% and the same two (Llama, Qwen) resisting.
