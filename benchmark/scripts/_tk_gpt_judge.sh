#!/usr/bin/env bash
# Dual-judge: re-judge TK briefings with a non-Anthropic judge (gpt-5.4). Scratch.
set -uo pipefail
cd /Users/kevinmurphy/Development/murphysig/benchmark
set -a; source .env; set +a
export OPENAI_API_KEY="$OPEN_ROUTER_API_KEY"
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"
MODELS=(
  "meta-llama/llama-4-maverick"
  "x-ai/grok-4.3"
  "deepseek/deepseek-chat-v3.1"
  "qwen/qwen3.7-plus"
  "mistralai/mistral-large-2512"
)
for m in "${MODELS[@]}"; do
  echo "######## GPT JUDGE: $m ########"
  PYTHONPATH=. .venv/bin/python scripts/rescore_tk_judge.py \
    --dir results/tk/openrouter --model "$m" \
    --judge-family openai --judge-model openai/gpt-5.4 --judge-tag "__gpt" --delay 0.2 2>&1 \
    | grep -E "skipped|Variant|unsigned \||signed \|" | tail -4
done
echo "######## AGREEMENT ########"
PYTHONPATH=. .venv/bin/python scripts/tk_judge_agreement.py --dir results/tk/openrouter --gpt-tag __gpt
echo "######## DUAL-JUDGE DONE ########"
