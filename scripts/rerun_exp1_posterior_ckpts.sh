#!/usr/bin/env bash
# Retrain the five EXP-1 runs used by the posterior-distance measurement, keeping
# only the final checkpoint.
#
# Their checkpoints were deleted when the GPU server hit its disk quota, and the
# measurement has to be redone because the Sinkhorn estimator it used was wrong
# (scripts/verify_sinkhorn.py). Everything here is deterministic in the config's
# seed, so these reproduce the same runs; only the final checkpoint is written,
# which is all analyze_posterior_distance_exp1.py reads.
set -euo pipefail
cd "$(dirname "$0")/.."
OUT=results/exp1/_recompute
mkdir -p "$OUT"
for r in exp1_cond_seed0 p7y_h0.01_seed0 p7y_h0.05_seed0 p7y_h0.1_seed0 p7y_h0.5_seed0; do
  echo "=== $r"
  uv run python -m src.train --config "results/exp1/$r/config.yaml" --out "$OUT" \
      --set 'train.checkpoints=[200000]'
done
echo "=== all five retrained into $OUT"
