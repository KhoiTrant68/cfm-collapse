#!/usr/bin/env bash
# Proposals 1 and 2 of reports/Khoảng trống novelty sai số muộn.md on the N3 EDM models:
#   mu    late one-sided Lipschitz constant of the denoiser along sampling (scripts/n3_jacobian_mu.py)
#   swap  denoiser swap in both directions (scripts/n3_swap.py)
# for the public EDM model and a model trained on a subset (default: the sub1000 model of the timing
# run). Steps run one after another on one GPU; a finished step is skipped on a rerun.
#
#   GPU=2 bash scripts/server_n3_followup.sh
#   GPU=2 MODELS=sub SUB=<train dir> SUB_IND=<indices.npy> SUBNAME=sub500 OUT=<dir> bash scripts/server_n3_followup.sh
set -uo pipefail
GPU=${GPU?set GPU to the index of a free GPU}
PYTHON=${PYTHON:-.venv-s10/bin/python}
EDM_REPO=${EDM_REPO:-$HOME/cfm-research/edm}
PUBLIC=${PUBLIC:-$HOME/cfm-research/edm-checkpoints/edm-cifar10-32x32-cond-vp.pkl}
SUB=${SUB:-results/n3_edm_timing_20261110/train_sub1000_s0}
SUB_IND=${SUB_IND:-data/edm_subsets/cifar10_sub1000_s0_indices.npy}
SUBNAME=${SUBNAME:-sub1000}
MODELS=${MODELS:-"public sub"}
MU_NPC_SUB=${MU_NPC_SUB:-10}
OUT=${OUT:-results/n3_followup_20261111}
export CUDA_VISIBLE_DEVICES=$GPU
mkdir -p "$OUT"

step () {  # name done-file command...
  local name=$1 done=$2; shift 2
  [ -f "$done" ] && { echo "[$name] done before"; return 0; }
  echo "[$name] start $(date -u +%H:%M)"
  "$@" > "$OUT/$name.log" 2>&1 && echo "[$name] ok $(date -u +%H:%M)" || echo "[$name] FAILED, see $OUT/$name.log"
}

common=(--edm-repo "$EDM_REPO" --cifar-root data)
for m in $MODELS; do
  if [ "$m" = public ]; then
    step swap_public "$OUT/swap_public/swap_per_sample.npz" $PYTHON -u -m scripts.n3_swap --network "$PUBLIC" \
      "${common[@]}" --n-per-class 50 --out "$OUT/swap_public"
    step mu_public "$OUT/mu_public/mu_per_sample.npz" $PYTHON -u -m scripts.n3_jacobian_mu --network "$PUBLIC" \
      "${common[@]}" --n-per-class 20 --iters 20 --out "$OUT/mu_public"
  else
    sub_net=$(ls "$SUB"/*/network-snapshot-*.pkl | sort | tail -1)
    echo "$SUBNAME snapshot: $sub_net"
    step swap_$SUBNAME "$OUT/swap_$SUBNAME/swap_per_sample.npz" $PYTHON -u -m scripts.n3_swap --network "$sub_net" \
      "${common[@]}" --indices "$SUB_IND" --n-per-class 50 --out "$OUT/swap_$SUBNAME"
    step mu_$SUBNAME "$OUT/mu_$SUBNAME/mu_per_sample.npz" $PYTHON -u -m scripts.n3_jacobian_mu --network "$sub_net" \
      "${common[@]}" --indices "$SUB_IND" --n-per-class "$MU_NPC_SUB" --iters 20 --out "$OUT/mu_$SUBNAME"
  fi
done
$PYTHON -m scripts.n3_jacobian_mu --summarize "$OUT" > "$OUT/mu_summary.log" 2>&1
$PYTHON -m scripts.n3_swap --summarize "$OUT" > "$OUT/swap_summary.log" 2>&1
echo COMPLETE > "$OUT/STATUS"
