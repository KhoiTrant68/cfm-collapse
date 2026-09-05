#!/usr/bin/env bash
# Remaining CIFAR seed runs, one at a time.
#
# run_queue_parallel.sh ran these two at a time on the strength of a measurement
# taken on a different model: SmallUNet at 0.5M parameters and batch 64, where two
# concurrent 30k-iteration runs took 793s against 665s alone, about 1.7x
# throughput. That model does not saturate the GPU. The DDPM U-Net at 35.75M and
# batch 128 does, and measured on this machine:
#
#   alone            60000 iters in 12589s   = 4.77 it/s
#   two concurrent    8000 iters in  3768s   = 2.12 it/s each, 4.25 it/s together
#
# Running two at a time is 11% *worse* in aggregate, and it also withholds every
# result until its partner finishes. Eight runs take 31.4 h paired against 28 h
# sequential. So: sequential, and results land every 3.5 h instead of every 7.9 h.
#
# Skips anything already finished, so it can be started while the current pair is
# still running -- it waits for them first.
#
#   bash scripts/run_cifar_seeds_sequential.sh [gpu_index]
set -u
cd "$(dirname "$0")/.."
GPU="${1:-0}"
PY=${PY:-.venv/bin/python}
mkdir -p logs

# Wait for whatever the previous driver left in flight.
while pgrep -f "src.train_exp[3] .*exp3_cifar_ddpm_h" > /dev/null; do
  echo "  waiting for the in-flight pair to finish ($(date +%H:%M:%S))"
  sleep 300
done

for seed in 1 2; do
  for h in 0 4 5 6; do
    name="exp3_cifar_ddpm_h${h}_seed${seed}"
    if [ -f "results/exp3/${name}/raw/metrics.csv" ]; then
      echo "  [skip] $name"
      continue
    fi
    echo "=== $name ($(date +%H:%M:%S)) ==="
    CUDA_VISIBLE_DEVICES="$GPU" $PY -u -m src.train_exp3 \
        --config configs/exp3_cifar_ddpm.yaml \
        --set "run_name=$name" "train.y_noise_h=${h}.0" "seed=${seed}" \
        > "logs/${name}.log" 2>&1
    echo "    rc=$? ($(date +%H:%M:%S))"
  done
done
echo "CIFAR SEEDS DONE ($(date +%H:%M:%S))"
