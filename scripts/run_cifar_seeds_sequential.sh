#!/usr/bin/env bash
# Remaining CIFAR seed runs, one at a time, in order of what they buy.
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
# result until its partner finishes. So: sequential, and results land every 3.5 h.
#
# ORDER. h=0 and h=4 already have two seeds. The next two runs are therefore the
# ones that take the table from "error bars on half the rows" to "error bars on
# every row"; the seed-2 runs only tighten bars that already exist. If the machine
# is lost again, the first two are the ones worth having finished.
#
# DETACHMENT. An earlier attempt died at 02:30 with every run still mid-flight,
# taking two 20000-iteration runs with it, because the driver was a child of the
# ssh session. Launch it detached:
#
#   ssh <host> 'cd <repo-root> && \
#     setsid nohup bash scripts/run_cifar_seeds_sequential.sh 0 \
#       > logs/cifar_seq.log 2>&1 < /dev/null &'
#
# DISK. Only the final weights are kept. Six checkpoints at 143 MB apiece is
# 858 MB per run, and that is what exhausted the machine's quota at 02:30,
# killing two runs 20000 iterations in. The metric trajectory is unaffected:
# evaluation still runs at every entry of train.checkpoints, only the writing
# out of intermediate weights is dropped.
#
# Skips anything already finished, so it is safe to re-run after a crash, and it
# waits out any run still in flight before starting.
set -u
cd "$(dirname "$0")/.."
GPU="${1:-0}"
PY=${PY:-.venv/bin/python}
mkdir -p logs

# Wait for whatever a previous driver left in flight.
while pgrep -f "src.train_exp[3] .*exp3_cifar_ddpm_h" > /dev/null; do
  echo "  waiting for an in-flight run to finish ($(date +%H:%M:%S))"
  sleep 300
done

# "h:seed", most valuable first.
for job in 5:1 6:1 0:2 4:2 5:2 6:2; do
  h="${job%%:*}"; seed="${job##*:}"
  name="exp3_cifar_ddpm_h${h}_seed${seed}"
  if [ -f "results/exp3/${name}/raw/metrics.csv" ]; then
    echo "  [skip] $name"
    continue
  fi
  echo "=== $name ($(date +%H:%M:%S)) ==="
  CUDA_VISIBLE_DEVICES="$GPU" $PY -u -m src.train_exp3 \
      --config configs/exp3_cifar_ddpm.yaml \
      --set "run_name=$name" "train.y_noise_h=${h}.0" "seed=${seed}" \
      "train.save_checkpoints=[60000]" \
      > "logs/${name}.log" 2>&1
  echo "    rc=$? ($(date +%H:%M:%S))"
done
echo "CIFAR SEEDS DONE ($(date +%H:%M:%S))"
