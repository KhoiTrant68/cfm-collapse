#!/usr/bin/env bash
# Run the two missing 1D cells, one run at a time, without replacing existing output.
# PYTHON=/absolute/path/to/python bash scripts/server_composition_ablation.sh 1 results/composition_ablation_20261029
set -euo pipefail
cd "$(dirname "$0")/.."
GPU=${1:?GPU index required}
OUT=${2:?New output directory required}
PYTHON=${PYTHON:-python}
export CUDA_VISIBLE_DEVICES="$GPU" OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONUNBUFFERED=1
"$PYTHON" -c 'import torch, scipy, numpy; assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0))'
# mkdir without -p deliberately refuses a rerun into an existing campaign.
mkdir "$OUT"
mkdir "$OUT/logs"
trap 'code=$?; if [ "$code" -ne 0 ]; then printf "FAILED exit=%s at %s\n" "$code" "$(date -Is)" > "$OUT/STATUS"; fi' EXIT
git rev-parse HEAD > "$OUT/code_commit.txt"
git diff > "$OUT/code_diff.patch"
"$PYTHON" -m pip freeze > "$OUT/environment.txt"
nvidia-smi > "$OUT/gpu_at_start.txt"
printf 'variant\tseed\tstage\ttime\n' > "$OUT/progress.tsv"
for seed in 0 1 2 3 4; do
  for variant in cfm_v_s cfm_x; do
    printf 'RUNNING %s seed=%s\n' "$variant" "$seed" > "$OUT/STATUS"
    printf '%s\t%s\ttrain-start\t%s\n' "$variant" "$seed" "$(date -Is)" >> "$OUT/progress.tsv"
    # Saving the training summary before evaluation permits --eval-only recovery.
    "$PYTHON" -u -m scripts.learned_composition --variant "$variant" --seed "$seed" \
      --steps 200000 --batch 2048 --lr 0.003 --no-eval --out "$OUT" \
      > "$OUT/logs/${variant}_seed${seed}_train.log" 2>&1
    printf '%s\t%s\teval-start\t%s\n' "$variant" "$seed" "$(date -Is)" >> "$OUT/progress.tsv"
    "$PYTHON" -u -m scripts.learned_composition --variant "$variant" --seed "$seed" \
      --eval-only --out "$OUT" > "$OUT/logs/${variant}_seed${seed}_eval.log" 2>&1
    printf '%s\t%s\tcomplete\t%s\n' "$variant" "$seed" "$(date -Is)" >> "$OUT/progress.tsv"
  done
done
printf 'COMPLETE %s\n' "$(date -Is)" > "$OUT/STATUS"
