#!/usr/bin/env bash
# Everything still outstanding, run sequentially on a single GPU.
#
# Ordered by value so that stopping early still leaves the important work done:
#
#   1. Re-evaluate the CIFAR checkpoints (~30 min). Adds the NN-correct rate, the
#      literature-standard memorisation ratio -- which tests Proposition 14's
#      claim that the endpoint law stays atomic at every bandwidth -- and the
#      observation-space moment that Theorem 10 predicts exactly.
#   2. EXP-1 P6 with per-image exposure held fixed. The published P6 sweep has the
#      same budget/N confound the EXP-3 sweep turned out to have; this is the
#      control that was only flagged, never run.
#   3. Two further seeds for the CIFAR h-sweep, for error bars.
#
#   bash scripts/run_queue_all.sh [gpu_index]
set -u
cd "$(dirname "$0")/.."
GPU="${1:-0}"
PY=${PY:-.venv/bin/python}
mkdir -p logs

echo "########## 1. CIFAR re-evaluation ($(date +%H:%M:%S)) ##########"
CUDA_VISIBLE_DEVICES="$GPU" PYTHONPATH=. $PY -u scripts/reeval_exp3_cifar_ddpm.py \
    --M 256 --n-conditions 48 > logs/reeval_full.log 2>&1
echo "  rc=$? ($(date +%H:%M:%S))"

echo "########## 2. EXP-1 P6 exposure control ($(date +%H:%M:%S)) ##########"
PYTHONPATH=. $PY -u scripts/run_exp1_p6_exposure.py --seeds 5 --gpu "$GPU" \
    > logs/p6_exposure.log 2>&1
echo "  rc=$? ($(date +%H:%M:%S))"

echo "########## 3. CIFAR extra seeds ($(date +%H:%M:%S)) ##########"
for seed in 1 2; do
  for h in 0 4 5 6; do
    name="exp3_cifar_ddpm_h${h}_seed${seed}"
    if [ -f "results/exp3/${name}/raw/metrics.csv" ]; then
      echo "  [skip] $name"; continue
    fi
    echo "  $name ($(date +%H:%M:%S))"
    CUDA_VISIBLE_DEVICES="$GPU" $PY -u -m src.train_exp3 \
        --config configs/exp3_cifar_ddpm.yaml \
        --set "run_name=$name" "train.y_noise_h=${h}.0" "seed=${seed}" \
        > "logs/${name}.log" 2>&1
    echo "    rc=$? ($(date +%H:%M:%S))"
  done
done

echo "QUEUE ALL DONE ($(date +%H:%M:%S))"
