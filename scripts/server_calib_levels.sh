#!/usr/bin/env bash
# Multi-level and PCA calibration (scripts/calib_image_levels.py) of CIFAR-10 re-runs on
# the plain server, alongside scripts/server_cifar_queue.sh.
#
#   bash scripts/server_calib_levels.sh <gpu> <run> [<run> ...]
#
# A run is analysed once the training queue has finished with it: its "size ...
# results/exp3/<run>" line in logs/queue_gpu*.log is printed after the checkpoints are
# stripped. Runs already finished start at once, so this can be launched while the
# training queue is still running; it then shares the GPU with it.
#
# N_TEST and M override the defaults (64 and 64, as in the queue's calibration step).
set -uo pipefail
GPU=$1; shift
cd "$(dirname "$0")/.."
VENV=${VENV:-$HOME/clic/venv}
# shellcheck disable=SC1091
source "$VENV/bin/activate"
export PYTHONPATH=. PYTHONWARNINGS=ignore OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=$GPU
OUT=results/exp3/_rerun
mkdir -p logs "$OUT"

for name in "$@"; do
  until grep -qs "results/exp3/$name\$" logs/queue_gpu*.log; do sleep 120; done
  echo "[$(date '+%F %T')] $name on GPU $GPU"
  python -u -m scripts.calib_image_levels --work results/exp3 --runs "$name" \
    --n-test "${N_TEST:-64}" --M "${M:-64}" --out "$OUT" > "logs/levels_$name.log" 2>&1
  echo "  levels returned $?"
done
echo "[$(date '+%F %T')] levels on GPU $GPU finished"
