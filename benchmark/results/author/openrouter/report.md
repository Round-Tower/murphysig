# Author-Quality — Cross-Family Report

Judged rows: 600 (judge: openai/gpt-5.4, code-only, blind to arm)

## Hazard-handled rate

| Model | bare | reflect | sign | sign_revise | reflect_harder | Δsign−reflect | Δsign_revise−reflect_harder | Δreflect−bare |
|---|---|---|---|---|---|---|---|---|
| deepseek-chat-v3.1 | 0.70 | 0.87 | 0.73 | 0.93 | 0.95 | -0.13 | -0.02 | +0.17 |
| gemini-3.5-flash | 0.83 | 0.87 | 0.87 | 0.88 | 0.90 | +0.00 | -0.02 | +0.03 |
| llama-4-maverick | 0.75 | 0.70 | 0.75 | 0.83 | 0.93 | +0.05 | -0.10 | -0.05 |
| mistral-large-2512 | 0.72 | 0.83 | 0.77 | 0.88 | 0.82 | -0.07 | +0.07 | +0.12 |
| qwen3.7-plus | 0.60 | 0.83 | 0.82 | 0.97 | 0.72 | -0.02 | +0.25 | +0.23 |
| grok-4.3 | 0.60 | 0.67 | 0.60 | 0.88 | 0.83 | -0.07 | +0.05 | +0.07 |
| **MEAN (paired)** | 0.70 | 0.79 | 0.76 | 0.90 | 0.86 | **-0.04** | **+0.04** | **+0.09** |

_MEAN deltas are means of per-model paired deltas (within-model design)._
_Δsign−reflect is a FRAME contrast — disclosure frame (no action clause)_
_vs reflection frame (with one) — not a matched pair. The parity-matched_
_decisive comparison is Δsign_revise−reflect_harder._

## Deferral — of hazards missed in code, % confessed in the note

| Arm | missed | confessed | rate | rows judged | rows dropped |
|---|---|---|---|---|---|
| bare | 10 | 0 | 0% | 14 | 106 |
| reflect | 74 | 33 | 45% | 120 | 0 |
| sign | 88 | 60 | 68% | 120 | 0 |
| sign_revise | 37 | 8 | 22% | 120 | 0 |
| reflect_harder | 34 | 14 | 41% | 114 | 6 |

_Rates are only comparable across arms with similar coverage —_
_check the dropped column before quoting a confession delta._

## Write-time confidence calibration (signature-bearing rows only)

- stated conf ≥ 0.9: n=198, mean hazards missed = 0.47
- stated conf < 0.9: n=32, mean hazards missed = 0.94
