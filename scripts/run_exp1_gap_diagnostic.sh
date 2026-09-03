#!/usr/bin/env bash
# Optimization-gap diagnostic (cheap, Huong A): rerun the extended cosine-
# schedule budget sweep at h=0.1 (5 seeds), to check whether the optimality
# gap L(v_theta) - L(v*_h) shrinks with iteration budget at nonzero bandwidth
# too -- the same pattern already shown at h=0 in Table 1 / Figure 3a.
# Reuses the existing exp1_extended_schedule.yaml infrastructure; only h changes.
#
# Usage:
#   bash scripts/run_exp1_gap_diagnostic.sh
set -euo pipefail
cd "$(dirname "$0")/.."

for s in 0 1 2 3 4; do
  echo "=== h=0.1 extended schedule, seed $s ==="
  uv run python -m src.train --config configs/exp1_extended_schedule_h01.yaml \
    --out results/exp1 \
    --set seed=$s run_name=exp1_ext_sched_h01_seed$s
done

echo "=== Analyzing (reusing existing extended-schedule analysis script) ==="
uv run python scripts/analyze_exp1_extended_schedule.py \
  --sched "results/exp1/exp1_ext_sched_h01_seed*" \
  --fixed_lr results/exp1/exp1_ext_sched_seed0 \
  --out results/exp1/_analysis_gap_diagnostic_h01
