#!/usr/bin/env bash
# EXP-3 at realistic capacity: CIFAR-10 inpainting, DDPM U-Net (35.75M), one GPU.
#
# Purpose: test Theorem 10 in image space. At d=3072 and k=1536 the kernel
# reference tr Cov_h is 0 / 61 / 276 / 362 at h = 0 / 4 / 5 / 6 (median over
# conditions, N=2000), against 774 for the full empirical covariance. If the
# model tracks the population optimum, ratio_to_kernel should approach 1 at each
# of those three very different targets; h=0 is the Proposition 4 control, where
# the reference variance is exactly 0 and the ratio is undefined by construction
# (read trace_cov and mean_err_kernel there instead).
#
# Budget: 60000 iterations at batch 128 with N=2000 is 3840 gradient samples per
# training image -- the same per-image exposure as the N-sweep runs. Measured
# throughput on a Quadro RTX 6000 with AMP is 4.75 it/s, so ~3.5 h per run and
# ~14 h for the four. Runs are sequential: this script deliberately uses a single
# GPU and leaves the other one free.
#
#   bash scripts/run_exp3_cifar_ddpm.sh [gpu_index]
set -u
cd "$(dirname "$0")/.."
GPU="${1:-0}"
PY=${PY:-.venv/bin/python}
mkdir -p logs

for h in 0 4 5 6; do
  name="exp3_cifar_ddpm_h${h}"
  echo "=== $name on gpu $GPU ($(date +%H:%M:%S)) ==="
  CUDA_VISIBLE_DEVICES="$GPU" $PY -u -m src.train_exp3 \
      --config configs/exp3_cifar_ddpm.yaml \
      --set "run_name=$name" "train.y_noise_h=${h}.0" \
      > "logs/${name}.log" 2>&1
  echo "    done rc=$? ($(date +%H:%M:%S))"
done
echo "ALL CIFAR DDPM RUNS DONE"
