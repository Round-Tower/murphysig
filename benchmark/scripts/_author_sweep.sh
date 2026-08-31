#!/bin/zsh
# Driver for the canonical author-quality sweep. Committed, like every other
# _*.sh driver in this directory — the "NOT committed" convention the header
# used to claim was never actually followed (_tk_sweep.sh, _honesty_gpt_judge.sh
# and _tk_prose_add.sh are all tracked), and an uncommitted driver means the
# exact command behind a published benchmark number is lost.
# Run AFTER the adversarial fixture audit clears.
#
# 6 subject models x 3 cases x 5 arms x 5 reps = 450 generations,
# then dual judge (gpt-5.4 canonical untagged, Opus 4.6 tagged __opus).
set -e
cd /Users/kevinmurphy/Development/murphysig/benchmark
set -a; source .env 2>/dev/null; set +a
export OPEN_ROUTER_API_KEY="${OPEN_ROUTER_API_KEY:?}"

MODELS=(
  google/gemini-3.5-flash
  meta-llama/llama-4-maverick
  x-ai/grok-4.3
  deepseek/deepseek-chat-v3.1
  qwen/qwen3.7-plus
  mistralai/mistral-large-2512
)

for m in $MODELS; do
  echo "=== RUN $m ==="
  PYTHONPATH=. .venv/bin/python scripts/run_author_openai.py \
    --provider openrouter --model "$m" --reps 5 --temperature 0.7
done

for m in $MODELS; do
  echo "=== JUDGE gpt-5.4 $m ==="
  PYTHONPATH=. .venv/bin/python scripts/rescore_author_judge.py \
    --dir results/author/openrouter --model "$m"
done

for m in $MODELS; do
  echo "=== JUDGE opus $m ==="
  PYTHONPATH=. .venv/bin/python scripts/rescore_author_judge.py \
    --dir results/author/openrouter --model "$m" \
    --judge anthropic/claude-opus-4.6
done

echo "=== REPORT (gpt-5.4 canonical, excludes __opus verdicts) ==="
PYTHONPATH=. .venv/bin/python - <<'PY'
import glob, json
from scripts.author_report import render_report
rows = []
for p in sorted(glob.glob("results/author/openrouter/judged_author_*.json")):
    if "__" in p:  # any tagged (second-judge) file
        continue
    rows.extend(json.load(open(p)))
report = render_report(rows)
open("results/author/openrouter/report.md", "w").write(report)
print(report)
PY

echo "=== JUDGE AGREEMENT ==="
PYTHONPATH=. .venv/bin/python scripts/author_judge_agreement.py \
  --dir results/author/openrouter --second-tag __claude-opus-4-6 \
  --out results/author/openrouter/judge_agreement.md
