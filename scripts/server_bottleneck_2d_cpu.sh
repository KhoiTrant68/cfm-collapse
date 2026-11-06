#!/usr/bin/env bash
# The triangle (learned_composition_2d.py) counterpart of server_composition_ablation_parallel.sh:
# the label-bottleneck (cfm_x_sq) and tie-agnostic (cfm_x_o, cfm_x_a) variants, seeds 0-2, on CPU
# (the GPUs were full), plus the exact composite at the bottleneck priors. Each run
# trains and then evaluates (the 2D script has no separate evaluation step); runs write
# disjoint directories, so results do not depend on the concurrency.
#   PYTHON=/abs/python bash scripts/server_bottleneck_2d_cpu.sh results/bottleneck_2d_20261107
set -euo pipefail
cd "$(dirname "$0")/.."

OUT=${1:?New output directory required}
PYTHON=${PYTHON:-python}
export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 MKL_NUM_THREADS=4 PYTHONUNBUFFERED=1
"$PYTHON" -c 'import torch, scipy, numpy; print(torch.__version__)'
mkdir "$OUT"          # no -p: refuses to rerun into an existing campaign
mkdir "$OUT/logs"
nproc > "$OUT/cpu_count.txt"
(git rev-parse HEAD 2>/dev/null || echo "not a git checkout") > "$OUT/code_commit.txt"
(git diff 2>/dev/null || true) > "$OUT/code_diff.patch"
sha256sum scripts/learned_composition_2d.py scripts/learned_composition.py src/models/mlp_velocity.py > "$OUT/code_sha256.txt"
"$PYTHON" -m pip freeze > "$OUT/environment.txt"
uptime > "$OUT/load_at_start.txt"
printf 'variant\tseed\tstage\ttime\n' > "$OUT/progress.tsv"

run() {
  local variant=$1 seed=$2
  printf '%s\t%s\ttrain-start\t%s\n' "$variant" "$seed" "$(date -Is)" >> "$OUT/progress.tsv"
  "$PYTHON" -u -m scripts.learned_composition_2d --variant "$variant" --seed "$seed" \
    --steps 200000 --batch 2048 --lr 0.003 --out "$OUT" \
    > "$OUT/logs/${variant}_seed${seed}_train.log" 2>&1 || { echo "$variant $seed run" >> "$OUT/FAILED"; return 1; }
  printf '%s\t%s\tcomplete\t%s\n' "$variant" "$seed" "$(date -Is)" >> "$OUT/progress.tsv"
}

echo "RUNNING $(date -Is)" > "$OUT/STATUS"
pids=()
"$PYTHON" -u -m scripts.learned_composition_2d --exact-bottleneck --out "$OUT" > "$OUT/logs/exact_bottleneck.log" 2>&1 & pids+=($!)
for seed in 0 1 2; do
  for variant in cfm_x_sq cfm_x_o cfm_x_a; do
    run "$variant" "$seed" & pids+=($!)
  done
done
fail=0
for p in "${pids[@]}"; do wait "$p" || fail=1; done
if [ "$fail" -eq 0 ]; then echo "COMPLETE $(date -Is)" > "$OUT/STATUS"; else echo "FAILED $(date -Is)" > "$OUT/STATUS"; fi
