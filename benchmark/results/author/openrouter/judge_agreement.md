# Author-quality — inter-judge agreement

Headline Δ(sign_revise − reflect_harder), paired per model. Judge A = openai/gpt-5.4, Judge B = anthropic/claude-opus-4.6.

| Model | Δ openai/gpt-5.4 | Δ anthropic/claude-opus-4.6 | concordant |
|---|---|---|---|
| deepseek-chat-v3.1 | -0.02 | +0.03 | ✗ |
| gemini-3.5-flash | -0.02 | +0.05 | ✗ |
| llama-4-maverick | -0.10 | -0.02 | ✓ |
| mistral-large-2512 | +0.07 | +0.03 | ✓ |
| qwen3.7-plus | +0.25 | +0.25 | ✓ |
| grok-4.3 | +0.05 | +0.00 | ✓ |

**4/6 concordant** on the headline's sign.

_Frame contrast Δ(sign − reflect), for texture (not a matched pair):_

- deepseek-chat-v3.1: -0.13 (A) / -0.03 (B)
- gemini-3.5-flash: +0.00 (A) / -0.07 (B)
- llama-4-maverick: +0.05 (A) / -0.07 (B)
- mistral-large-2512: -0.07 (A) / -0.05 (B)
- qwen3.7-plus: -0.02 (A) / +0.05 (B)
- grok-4.3: -0.07 (A) / -0.03 (B)
