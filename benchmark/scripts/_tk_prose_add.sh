#!/usr/bin/env bash
# TK prose-control add (scratch — not committed).
# Runs ONLY the prose arm for the 6 committed families, judges it with the
# SAME OpenRouter-proxied Opus 4.6 judge used for signed/unsigned, into a
# separate __prose verdict file (does not touch the committed base rows).
# Then builds a clean Opus-only dir and renders the structure table.
set -uo pipefail
cd /Users/kevinmurphy/Development/murphysig/benchmark
set -a; source .env; set +a
export OPENAI_API_KEY="$OPEN_ROUTER_API_KEY"
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"

REPS=5
TEMP=0.7
JUDGE="anthropic/claude-opus-4.6"
DIR=results/tk/openrouter
OUT=results/tk/_structure_add

MODELS=(
  "google/gemini-3.5-flash"
  "meta-llama/llama-4-maverick"
  "x-ai/grok-4.3"
  "deepseek/deepseek-chat-v3.1"
  "qwen/qwen3.7-plus"
  "mistralai/mistral-large-2512"
)

for m in "${MODELS[@]}"; do
  echo "################ PROSE SUBJECT: $m ################"
  PYTHONPATH=. .venv/bin/python scripts/run_tk_openai.py \
    --provider openrouter --model "$m" --variant prose \
    --reps "$REPS" --temperature "$TEMP" 2>&1 | tail -3
  echo "################ PROSE JUDGE: $m ################"
  PYTHONPATH=. .venv/bin/python scripts/rescore_tk_judge.py \
    --dir "$DIR" --model "$m" --variant prose \
    --judge-family openai --judge-model "$JUDGE" --judge-tag "__prose" \
    --delay 0.3 2>&1 | tail -6
done

echo "################ BUILD CLEAN OPUS-ONLY REPORT DIR ################"
rm -rf "$OUT"; mkdir -p "$OUT"
for m in "${MODELS[@]}"; do
  f="${m//\//_}"
  cp "$DIR/judged_tk_${f}.json" "$OUT/" 2>/dev/null || echo "MISSING base $f"
  cp "$DIR/judged_tk_${f}__prose.json" "$OUT/" 2>/dev/null || echo "MISSING prose $f"
done

echo "################ STRUCTURE TABLE ################"
PYTHONPATH=. .venv/bin/python scripts/tk_cross_family_report.py --dir "$OUT" | tee "$OUT/structure_report.md"
echo "################ PROSE ADD DONE ################"
