#!/usr/bin/env bash
# S10 (panel 2026-11-07): retrain the EXP-3 CIFAR-10 U-Nets of App. C.4 with their final weights
# kept, then measure the scaled field error (1-t)|Delta| per sample along the learned trajectories
# against the exact field (scripts/exp_c_cifar_transfer.py) and split it by off-atom / on-atom
# endpoint (scripts/summarize_s10_cifar.py).
#
# The configuration is configs/exp3_cifar_ddpm_heff.yaml unchanged (the runs of App. C.4), except
# that only the final weights are written. Runs train one after another on one GPU:
#
#   GPU=2 RUNS="6:0 6:1 6:2 4:0 4:1 4:2 0:0" PYTHON=/abs/python bash scripts/server_s10_cifar.sh
#
# SMOKE=1 (with GPU= for the CPU) runs the whole pipeline at N=64, 200 iterations, a narrow U-Net
# and a coarse evaluation, only to check that it runs. A finished step is skipped on a rerun
# (training resumes from ckpt_resume.pt if present; the evaluation skips runs whose JSON exists).
set -uo pipefail
GPU=${GPU?set GPU to the index of a free GPU (empty = CPU, for SMOKE=1)}
RUNS=${RUNS:-"6:0 6:1 6:2 4:0 4:1 4:2 0:0"}
PYTHON=${PYTHON:-python}
TRAIN_OUT=${TRAIN_OUT:-results/s10_exp3}
EVAL_OUT=${EVAL_OUT:-results/s10_cifar_transfer_20261108}
CONFIG=${CONFIG:-configs/exp3_cifar_ddpm_heff.yaml}
SMOKE=${SMOKE:-0}
export CUDA_VISIBLE_DEVICES=$GPU
mkdir -p "$TRAIN_OUT" "$EVAL_OUT"
keep=60000; flag=(); narrow=()
if [ "$SMOKE" = 1 ]; then keep=200; flag=(--smoke-test); narrow=(model.base=32); export S10_SMOKE=1; fi
names=()
for r in $RUNS; do
  h=${r%%:*}; s=${r##*:}; base=exp3_cifar_heff_h${h}_s${s}
  name=$base; [ "$SMOKE" = 1 ] && name=${base}_smoke     # apply_smoke_test appends _smoke
  names+=("$name")
  ckdir=$TRAIN_OUT/$name/checkpoints
  if [ -f "$ckdir/ckpt_$keep.pt" ]; then echo "[$name] trained"; continue; fi
  extra=(); [ -f "$ckdir/ckpt_resume.pt" ] && extra=(--resume "$ckdir/ckpt_resume.pt")
  echo "[$name] training (CUDA_VISIBLE_DEVICES='$GPU')"
  $PYTHON -u -m src.train_exp3 --config "$CONFIG" --out "$TRAIN_OUT" "${flag[@]}" "${extra[@]}" \
    --set run_name=$base seed=$s train.y_noise_h=$h train.save_checkpoints=$keep "${narrow[@]}" \
    > "$TRAIN_OUT/$name.train.log" 2>&1 || { echo "[$name] training failed"; exit 1; }
done
$PYTHON -u -m scripts.exp_c_cifar_transfer --runs "${names[@]}" --checkpoint $keep \
  --exp3-root "$TRAIN_OUT" --out-dir "$EVAL_OUT" > "$EVAL_OUT/eval_ckpt_$keep.log" 2>&1 \
  || { echo "evaluation failed"; exit 1; }
$PYTHON -u -m scripts.summarize_s10_cifar --dir "$EVAL_OUT" --checkpoint $keep
echo COMPLETE > "$EVAL_OUT/STATUS_ckpt_$keep"
