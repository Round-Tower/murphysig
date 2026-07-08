# Author-Quality Pilot — Report

Judged rows: 144 (judge: openai/gpt-5.4, code-only, blind to arm)

## Hazard-handled rate (primary metric)

| Model | bare | reflect | sign | sign_revise | Δreflect−bare | Δsign−reflect | Δsign_revise−reflect |
|---|---|---|---|---|---|---|---|
| gemini-2.5-flash | 0.56 | 0.85 | 0.81 | 0.93 | +0.30 | -0.04 | +0.07 |
| deepseek-chat | 0.52 | 0.89 | 0.48 | 0.81 | +0.37 | -0.41 | -0.07 |
| llama-4-maverick | 0.74 | 0.74 | 0.70 | 0.89 | +0.00 | -0.04 | +0.15 |
| qwen3-235b-a22b-2507 | 0.70 | 0.89 | 0.67 | 0.78 | +0.19 | -0.22 | -0.11 |
| **MEAN** | 0.63 | 0.84 | 0.67 | 0.85 | **+0.21** | **-0.18** | **+0.01** |

## Core-correctness rate

| Model | bare | reflect | sign | sign_revise |
|---|---|---|---|---|
| gemini-2.5-flash | 1.00 | 0.89 | 1.00 | 0.78 |
| deepseek-chat | 0.89 | 1.00 | 0.89 | 1.00 |
| llama-4-maverick | 1.00 | 1.00 | 1.00 | 1.00 |
| qwen3-235b-a22b-2507 | 0.78 | 1.00 | 0.67 | 0.89 |

## Calibration teaser (sign arm)

- conf ≥ 0.9: n=34, mean hazards missed = 0.91
- conf < 0.9: n=1, mean hazards missed = 2.00
- signature blocks with parseable Confidence: 35

---
*Pilot: n=3 reps, single judge — signal detection only. See DESIGN.md for threats.*

## Deferral analysis — of hazards MISSED in code, % confessed in the note

| Arm | hazards missed | missed & confessed | confession rate |
|---|---|---|---|
| reflect | 17 | 7 | 41% |
| sign | 24 | 16 | 67% |
| sign_revise | 8 | 4 | 50% |

(81 noted rows analysed, 0 judge failures. Interpretation in FINDINGS.md.)
