#!/usr/bin/env bash
# Multi-level and PCA calibration (scripts/calib_image_levels.py) of CIFAR-10 re-runs on
# the plain server, after scripts/server_cifar_queue.sh.
#
#   bash scripts/server_calib_levels.sh <gpu> <run> [<run> ...]
#
# By default nothing starts until that GPU's training queue has printed "queue on GPU
# <gpu> finished". Sharing the GPU buys nothing: on an L40, sampling next to a training
# run slowed each of the two about 2x (training 40k->60k took 3989 s instead of ~2400 s),
# so together they got through about as much as one after the other, and the training
# timings stay comparable across runs only if the GPU is not shared.
#
# WAIT_QUEUE=0 starts at once instead; each run is then analysed as soon as the training
# queue has finished with it (its "size ... results/exp3/<run>" line in
# logs/queue_gpu*.log, printed after the checkpoints are stripped).
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

if [ "${WAIT_QUEUE:-1}" = "1" ]; then
  until grep -qs "queue on GPU $GPU finished" "logs/queue_gpu$GPU.log"; do sleep 120; done
fi
for name in "$@"; do
  until grep -qs "results/exp3/$name\$" logs/queue_gpu*.log; do sleep 120; done
  echo "[$(date '+%F %T')] $name on GPU $GPU"
  python -u -m scripts.calib_image_levels --work results/exp3 --runs "$name" \
    --n-test "${N_TEST:-64}" --M "${M:-64}" --out "$OUT" > "logs/levels_$name.log" 2>&1
  echo "  levels returned $?"
done
echo "[$(date '+%F %T')] levels on GPU $GPU finished"
