#!/usr/bin/env bash
# Second-judge on the PROSE arm (scratch). Closes the "Opus-only" caveat on
# the structure decomposition: re-judge prose with gpt-5.4 (non-reasoning),
# then build a GPT-only structure table to compare Δstructure under both
# judges. Signed/unsigned GPT verdicts (__gpt) already exist from last run.
set -uo pipefail
cd /Users/kevinmurphy/Development/murphysig/benchmark
set -a; source .env; set +a
export OPENAI_API_KEY="$OPEN_ROUTER_API_KEY"
export OPENAI_BASE_URL="https://openrouter.ai/api/v1"

DIR=results/tk/openrouter
OUT=results/tk/_structure_gpt
MODELS=(
  "google/gemini-3.5-flash" "meta-llama/llama-4-maverick" "x-ai/grok-4.3"
  "deepseek/deepseek-chat-v3.1" "qwen/qwen3.7-plus" "mistralai/mistral-large-2512"
)

for m in "${MODELS[@]}"; do
  echo "######## GPT PROSE JUDGE: $m ########"
  PYTHONPATH=. .venv/bin/python scripts/rescore_tk_judge.py \
    --dir "$DIR" --model "$m" --variant prose \
    --judge-family openai --judge-model openai/gpt-5.4 --judge-tag "__prose_gpt" \
    --delay 0.2 2>&1 | grep -iE "skipped|wrote|coverage=" | tail -4
done

echo "######## BUILD GPT-ONLY STRUCTURE DIR ########"
rm -rf "$OUT"; mkdir -p "$OUT"
for m in "${MODELS[@]}"; do
  f="${m//\//_}"
  cp "$DIR/judged_tk_${f}__gpt.json" "$OUT/" 2>/dev/null || echo "MISSING gpt base $f"
  cp "$DIR/judged_tk_${f}__prose_gpt.json" "$OUT/" 2>/dev/null || echo "MISSING gpt prose $f"
done

echo "######## GPT STRUCTURE TABLE ########"
PYTHONPATH=. .venv/bin/python scripts/tk_cross_family_report.py --dir "$OUT" | tee "$OUT/structure_report_gpt.md"
echo "######## GPT PROSE JUDGE DONE ########"
