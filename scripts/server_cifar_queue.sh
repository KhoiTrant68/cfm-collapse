#!/usr/bin/env bash
# One GPU's queue of CIFAR-10 DDPM re-runs on a plain Linux server (no Kaggle).
#
#   bash scripts/server_cifar_queue.sh <gpu> <h:seed> [<h:seed> ...]
#
# For every run: train with configs/exp3_cifar_ddpm_heff.yaml (weights archived at
# 2k-60k), then on the same GPU
#   1. h_eff at every archived checkpoint        scripts/heff_cifar_checkpoints.py
#   2. posterior-free calibration on test images scripts/calib_image_checkpoints.py
#   3. the 60k checkpoint at 48 conditions, M=256 scripts/reeval_exp3_cifar_ddpm.py
# and finally drop the optimizer state from the archived checkpoints (430 MB -> 143 MB
# each; every analysis loads only "model_state"). A run whose 60k checkpoint already
# exists is not retrained, so the queue can be restarted after an interruption.
#
# SMOKE=1 runs the whole chain on 64 images for 200 iterations, to test the plumbing.
set -uo pipefail
GPU=$1; shift
cd "$(dirname "$0")/.."
VENV=${VENV:-$HOME/clic/venv}
# shellcheck disable=SC1091
source "$VENV/bin/activate"
export PYTHONPATH=. PYTHONWARNINGS=ignore OMP_NUM_THREADS=8 CUDA_VISIBLE_DEVICES=$GPU
SMOKE=${SMOKE:-0}
OUT=results/exp3/_rerun
mkdir -p logs "$OUT"

if [ "$SMOKE" = "1" ]; then
  TRAIN_X=(data.N=64 train.batch_size=16 train.max_iters=200 "train.checkpoints=[100,200]"
           "train.save_checkpoints=[100,200]" eval.n_conditions=2 eval.M=8 eval.n_steps=10)
  HEFF_X=(--M 8 --n-conditions 8); CALIB_X=(--n-test 4 --M 8); REEVAL_X=(--M 8 --n-conditions 8)
  LAST=200; PREFIX=smoke_cifar_heff
else
  TRAIN_X=(); HEFF_X=(--M 128 --n-conditions 48); CALIB_X=(--n-test 64 --M 64)
  REEVAL_X=(--M 256 --n-conditions 48); LAST=60000; PREFIX=exp3_cifar_heff
fi

for spec in "$@"; do
  h=${spec%%:*}; s=${spec##*:}; name=${PREFIX}_h${h}_s${s}
  echo "[$(date '+%F %T')] $name on GPU $GPU"
  if [ ! -f "results/exp3/$name/checkpoints/ckpt_${LAST}.pt" ]; then
    python -u -m src.train_exp3 --config configs/exp3_cifar_ddpm_heff.yaml --out results/exp3 \
      --set "run_name=$name" "seed=$s" "train.y_noise_h=$h" "${TRAIN_X[@]}" \
      > "logs/train_$name.log" 2>&1
    echo "  train returned $?"
  fi
  if [ ! -f "results/exp3/$name/checkpoints/ckpt_${LAST}.pt" ]; then
    echo "  no final checkpoint; skipping analyses"; continue
  fi
  python -u -m scripts.heff_cifar_checkpoints --work results/exp3 --runs "$name" \
    "${HEFF_X[@]}" --out "$OUT" > "logs/heff_$name.log" 2>&1;   echo "  heff returned $?"
  python -u -m scripts.calib_image_checkpoints --work results/exp3 --runs "$name" \
    "${CALIB_X[@]}" --out "$OUT" > "logs/calib_$name.log" 2>&1; echo "  calib returned $?"
  python -u scripts/reeval_exp3_cifar_ddpm.py --runs "$name" "${REEVAL_X[@]}" \
    --out "$OUT/reeval_$name" > "logs/reeval_$name.log" 2>&1;   echo "  reeval returned $?"
  python - "results/exp3/$name/checkpoints" <<'PY'
import glob, os, sys, torch
keep = ("iter", "model_state", "config", "rows", "loss_ema", "elapsed_s")
for p in sorted(glob.glob(os.path.join(sys.argv[1], "ckpt_*.pt"))):
    ck = torch.load(p, map_location="cpu", weights_only=False)
    if "opt_state" in ck:
        torch.save({k: ck[k] for k in keep if k in ck}, p + ".tmp")
        os.replace(p + ".tmp", p)
print("  checkpoints stripped:", len(glob.glob(os.path.join(sys.argv[1], "ckpt_*.pt"))))
PY
  du -sh "results/exp3/$name" | sed 's/^/  size /'
done
echo "[$(date '+%F %T')] queue on GPU $GPU finished"
