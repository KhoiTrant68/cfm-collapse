#!/usr/bin/env bash
# Train an EDM model on a 500-image class-balanced CIFAR-10 subset long enough to memorize
# (stage 2 of scripts/server_n3_edm.sh), evaluate it, then run the mu and swap follow-ups on it.
#
#   GPU=2 bash scripts/server_n3_sub500_chain.sh
set -uo pipefail
GPU=${GPU?set GPU}
ROOT=$(pwd)
export PYTHON=${PYTHON:-$ROOT/.venv-s10/bin/python}
export EDM_REPO=${EDM_REPO:-$HOME/cfm-research/edm}
TRAIN_OUT=${TRAIN_OUT:-results/n3_edm_sub500_20261111}
FOLLOW_OUT=${FOLLOW_OUT:-results/n3_followup_sub500_20261111}
echo "[chain] training start $(date -u '+%F %H:%M')"
GPU=$GPU STAGES=2 SUBSETS=500 DURATION=${DURATION:-10} BATCH_GPU=${BATCH_GPU:-16} CIFAR_ROOT=data \
  OUT=$TRAIN_OUT bash scripts/server_n3_edm.sh || { echo "[chain] training/eval failed"; exit 1; }
echo "[chain] follow-up start $(date -u '+%F %H:%M')"
GPU=$GPU MODELS=sub SUB=$TRAIN_OUT/train_sub500_s0 SUB_IND=data/edm_subsets/cifar10_sub500_s0_indices.npy \
  SUBNAME=sub500 MU_NPC_SUB=20 OUT=$FOLLOW_OUT PYTHON=.venv-s10/bin/python bash scripts/server_n3_followup.sh
echo "[chain] done $(date -u '+%F %H:%M')"
