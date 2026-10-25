#!/usr/bin/env bash
# Learned guided label averaging (scripts/learned_composition.py) on the plain server:
# 5 seeds of each variant (default: all five, main variant first), PAR runs at a time on one GPU.
#
#   bash scripts/server_learned_composition.sh <gpu> [<parallel> [<variant> ...]]
#
# MODULE, OUT and LOGP (log-file prefix) select another experiment with the same interface, and
# EXTRA adds flags to every run (EXTRA=--eval-only re-evaluates the saved fields):
#   MODULE=scripts.learned_composition_2d OUT=results/learned_composition_2d_20261021 LOGP=lc2d \
#     bash scripts/server_learned_composition.sh 0 5 cfm_v distill_x_s cfm_x_s
#
# The exact references run on CPU separately:
#   python -u -m scripts.learned_composition_exact --workers 24
set -uo pipefail
GPU=$1; PAR=${2:-5}
VARIANTS=("${@:3}")
[ ${#VARIANTS[@]} -gt 0 ] || VARIANTS=(cfm_v distill_x_s cfm_x_s cfm_v_tis cfm_v_sep)
cd "$(dirname "$0")/.."
VENV=${VENV:-$HOME/clic/venv}
# shellcheck disable=SC1091
source "$VENV/bin/activate"
# The networks are tiny: one CPU thread per run is enough, and the server is shared.
export PYTHONPATH=. PYTHONWARNINGS=ignore OMP_NUM_THREADS=1 CUDA_VISIBLE_DEVICES=$GPU
export MODULE=${MODULE:-scripts.learned_composition} OUT=${OUT:-results/learned_composition_20261021}
export LOGP=${LOGP:-lc} EXTRA=${EXTRA:-}
mkdir -p logs "$OUT"
for v in "${VARIANTS[@]}"; do
  for seed in 0 1 2 3 4; do echo "$v $seed"; done
done | xargs -P "$PAR" -L 1 bash -c '
  python -u -m "$MODULE" --variant "$0" --seed "$1" --out "$OUT" $EXTRA > "logs/${LOGP}_$0_seed$1.log" 2>&1
  status=$?
  echo "[$(date "+%F %T")] $0 seed $1 returned $status"'
echo "[$(date '+%F %T')] $MODULE queue on GPU $GPU finished: ${VARIANTS[*]}"
