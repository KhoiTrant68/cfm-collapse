#!/usr/bin/env bash
# EXP-3 N-sweep: MNIST inpainting at N in {100, 500, 2000}, 1 seed each,
# same architecture/schedule/checkpoints as the paper's default (N=500) run.
# Mirrors EXP-1's P6 sweep (N in {50,200,1000,5000}) for the image experiment.
#
# Cost note: default N=500 run already exists at results/exp3/exp3_mnist_seed0
# (and seed1/seed2). This script only runs the two NEW N values; if you also
# want a second seed per N for error bars, add `--set seed=1` runs after.
#
# Usage:
#   bash scripts/run_exp3_n_sweep.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "=== EXP-3 N-sweep: N=100 ==="
uv run python -m src.train_exp3 --config configs/exp3_inpainting_N100.yaml \
  --out results/exp3

echo "=== EXP-3 N-sweep: N=2000 ==="
uv run python -m src.train_exp3 --config configs/exp3_inpainting_N2000.yaml \
  --out results/exp3

echo "=== EXP-3 N-sweep: N=500 (default, reuse if already run) ==="
if [ ! -f results/exp3/exp3_mnist_seed0/raw/metrics.csv ]; then
  uv run python -m src.train_exp3 --config configs/exp3_inpainting.yaml \
    --out results/exp3 --set run_name=exp3_mnist_seed0
else
  echo "  found existing results/exp3/exp3_mnist_seed0 — skipping"
fi

echo "=== Aggregating into N-sweep table ==="
uv run python scripts/analyze_exp3_n_sweep.py
