#!/usr/bin/env bash
# Dual-judge for Honesty: re-judge date-controlled responses with gpt-5.4. Scratch.
set -uo pipefail
cd /Users/kevinmurphy/Development/murphysig/benchmark
set -a; source .env; set +a
export OPENAI_API_KEY="$OPEN_ROUTER_API_KEY"
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"
MODELS=(
  "google/gemini-3.5-flash"
  "meta-llama/llama-4-maverick"
  "deepseek/deepseek-v3.2"
  "x-ai/grok-4.3"
  "qwen/qwen3-235b-a22b-2507"
  "mistralai/mistral-large-2512"
)
for m in "${MODELS[@]}"; do
  echo "######## GPT JUDGE (honesty): $m ########"
  PYTHONPATH=. .venv/bin/python scripts/rescore_openai_judge.py \
    --dir results/honesty/openrouter --model "$m" \
    --judge-family openai --judge-model openai/gpt-5.4 --judge-tag "__gpt" --delay 0.2 2>&1 \
    | grep -E "skipped|Condition|cold \||warm \|" | tail -5
done
echo "######## HONESTY GPT-JUDGE DONE ########"
