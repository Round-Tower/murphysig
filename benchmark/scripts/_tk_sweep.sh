#!/usr/bin/env bash
# TK cross-family sweep driver (scratch — not committed).
# Subjects via OpenRouter; judge = OpenRouter-proxied Opus 4.6.
set -euo pipefail
cd /Users/kevinmurphy/Development/murphysig/benchmark
set -a; source .env; set +a
export OPENAI_API_KEY="$OPEN_ROUTER_API_KEY"
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"

REPS=5
TEMP=0.7
JUDGE="anthropic/claude-opus-4.6"

MODELS=(
  "google/gemini-3.5-flash"
  "meta-llama/llama-4-maverick"
  "x-ai/grok-4.3"
  "deepseek/deepseek-chat-v3.1"
  "qwen/qwen3.7-plus"
  "mistralai/mistral-large-2512"
)

for m in "${MODELS[@]}"; do
  echo "################ SUBJECT: $m ################"
  PYTHONPATH=. .venv/bin/python scripts/run_tk_openai.py \
    --provider openrouter --model "$m" --reps "$REPS" --temperature "$TEMP" 2>&1 | tail -3
  echo "################ JUDGE: $m ################"
  PYTHONPATH=. .venv/bin/python scripts/rescore_tk_judge.py \
    --dir results/tk/openrouter --model "$m" \
    --judge-family openai --judge-model "$JUDGE" --judge-tag "" --delay 0.3 2>&1 | tail -8
done

echo "################ AGGREGATE ################"
PYTHONPATH=. .venv/bin/python scripts/tk_cross_family_report.py --dir results/tk
echo "################ SWEEP DONE ################"
