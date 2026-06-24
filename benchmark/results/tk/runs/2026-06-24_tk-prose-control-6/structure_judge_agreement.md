# Structure decomposition — dual-judge concordance (Opus 4.6 vs GPT-5.4)

_Δstructure = signed − prose. Both judges, 6 families, 0 skips. Content dominates under both; the format residual is small and judge-dependent._

| Model | Opus Δstruct | GPT Δstruct | Opus Δcontent | GPT Δcontent |
|---|--:|--:|--:|--:|
| deepseek_deepseek-chat-v3.1 | +0.010 | +0.033 | +0.149 | +0.085 |
| google_gemini-3.5-flash | +0.002 | +0.002 | +0.072 | +0.078 |
| meta-llama_llama-4-maverick | +0.040 | +0.055 | +0.118 | +0.144 |
| mistralai_mistral-large-2512 | -0.001 | +0.016 | +0.112 | +0.113 |
| qwen_qwen3.7-plus | +0.019 | +0.028 | +0.088 | +0.093 |
| x-ai_grok-4.3 | -0.027 | +0.016 | +0.086 | +0.076 |
| **MEAN** | **+0.007** | **+0.025** | **+0.104** | **+0.098** |

**Verdict:** content carries 94% (Opus) / 80% (GPT) of the uplift. The MurphySig *structure* is a small minority contributor under both judges; the value is capturing the tacit knowledge, not the format.
