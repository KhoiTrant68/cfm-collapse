#!/usr/bin/env bash
# Replacement for the sequential queue, which was leaving the machine idle.
#
# The EXP-1 runs are a 4-layer width-128 MLP at batch 256: measured 221 it/s with
# the GPU at 6% and the process pinned at ~105% CPU. They are bound by Python and
# CUDA launch overhead, not by compute, so running them one at a time wastes both
# the GPU and 23 of the 24 cores. They are launched together instead.
#
# The CIFAR runs do saturate the GPU (99%, 6.8 GB), so they get only modest
# parallelism: two at a time fits in 24 GB with headroom and measured 793s vs
# 665s for a 30k-iteration run, i.e. ~1.7x throughput rather than 2x.
#
# Everything still uses a single GPU.
#
#   bash scripts/run_queue_parallel.sh [gpu_index]
set -u
cd "$(dirname "$0")/.."
GPU="${1:-0}"
PY=${PY:-.venv/bin/python}
mkdir -p logs

echo "########## A. remaining EXP-1 P6 exposure runs, in parallel ($(date +%H:%M:%S)) ##########"
pids=()
for s in 1 2 3 4; do
  name="p6exp_N5000_seed${s}"
  if [ -f "results/exp1/${name}/raw/metrics.csv" ]; then
    echo "  [skip] $name"; continue
  fi
  CUDA_VISIBLE_DEVICES="$GPU" OMP_NUM_THREADS=2 $PY -u -m src.train \
      --config configs/exp1_linear_gaussian.yaml --out results/exp1 --set \
      "seed=${s}" "data.N=5000" "train.max_iters=1000000" \
      "model.conditional=true" "run_name=${name}" \
      > "logs/${name}.log" 2>&1 &
  pids+=($!)
  echo "  launched $name (pid $!)"
done
for p in "${pids[@]:-}"; do [ -n "$p" ] && wait "$p"; done
echo "  P6 exposure complete ($(date +%H:%M:%S))"

echo "########## B. CIFAR extra seeds, two at a time ($(date +%H:%M:%S)) ##########"
run_cifar () {
  local seed=$1 h=$2
  local name="exp3_cifar_ddpm_h${h}_seed${seed}"
  if [ -f "results/exp3/${name}/raw/metrics.csv" ]; then
    echo "  [skip] $name"; return
  fi
  CUDA_VISIBLE_DEVICES="$GPU" $PY -u -m src.train_exp3 \
      --config configs/exp3_cifar_ddpm.yaml \
      --set "run_name=$name" "train.y_noise_h=${h}.0" "seed=${seed}" \
      > "logs/${name}.log" 2>&1
  echo "    done $name ($(date +%H:%M:%S))"
}

for seed in 1 2; do
  for pair in "0 4" "5 6"; do
    set -- $pair
    echo "  seed=$seed h=$1,$2 ($(date +%H:%M:%S))"
    run_cifar "$seed" "$1" &
    a=$!
    run_cifar "$seed" "$2" &
    b=$!
    wait $a $b
  done
done

echo "QUEUE PARALLEL DONE ($(date +%H:%M:%S))"
