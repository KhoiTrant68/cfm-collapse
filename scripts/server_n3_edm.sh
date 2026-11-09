#!/usr/bin/env bash
# N3 (docs/plan/next_venue_plan_2026-11-09.md): field error of EDM denoisers against the exact
# field on CIFAR-10 (scripts/n3_edm_memorization.py).
#
#   stage 1  the public class-conditional EDM model (trained on all 50000 images; downloaded and
#            cached by EDM's dnnlib on first use);
#   stage 2  EDM models trained here on class-balanced subsets (scripts/make_edm_cifar_subset.py),
#            no augmentation, so the exact field over the subset is the training law.
#
# Prerequisites, done once by hand: a checkout of https://github.com/NVlabs/edm (EDM_REPO), a
# Python with its requirements (PYTHON), and CIFAR-10 for torchvision under CIFAR_ROOT.
#
#   GPU=2 EDM_REPO=/abs/edm PYTHON=/abs/python bash scripts/server_n3_edm.sh
#
# STAGES="1" or "2" runs one stage. SUBSETS and DURATION (Mimg per subset run) set stage 2; time
# a short run first, since the training cost on one GPU is the dominant term. A finished step is
# skipped on a rerun.
set -uo pipefail
GPU=${GPU?set GPU to the index of a free GPU}
EDM_REPO=${EDM_REPO?set EDM_REPO to a checkout of NVlabs/edm}
PYTHON=${PYTHON:-python}
CIFAR_ROOT=${CIFAR_ROOT:-data/cifar10}
STAGES=${STAGES:-"1 2"}
SUBSETS=${SUBSETS:-"500 1000 2000 5000"}
DURATION=${DURATION:-10}
BATCH=${BATCH:-128}
NPC=${NPC:-100}
OUT=${OUT:-results/n3_edm_20261109}
PUBLIC=${PUBLIC:-https://nvlabs-fi-cdn.nvidia.com/edm/pretrained/edm-cifar10-32x32-cond-vp.pkl}
export CUDA_VISIBLE_DEVICES=$GPU
mkdir -p "$OUT"
ROOT=$(pwd)

evaluate () {  # name network [indices]
  local name=$1 net=$2 ind=${3:-}
  [ -f "$OUT/$name/per_sample.npz" ] && { echo "[$name] evaluated"; return 0; }
  echo "[$name] evaluating"
  mkdir -p "$OUT/$name"
  $PYTHON -u -m scripts.n3_edm_memorization --network "$net" --edm-repo "$EDM_REPO" \
    --cifar-root "$CIFAR_ROOT" ${ind:+--indices "$ind"} --n-per-class "$NPC" --exact-path --cond-diff \
    --out "$OUT/$name" > "$OUT/$name/eval.log" 2>&1 || { echo "[$name] evaluation failed"; return 1; }
}

for st in $STAGES; do
  if [ "$st" = 1 ]; then
    evaluate public_cond_vp "$PUBLIC" || exit 1
  elif [ "$st" = 2 ]; then
    for n in $SUBSETS; do
      name=sub${n}_s0
      zip=$ROOT/data/edm_subsets/cifar10_sub${n}_s0.zip
      ind=$ROOT/data/edm_subsets/cifar10_sub${n}_s0_indices.npy
      [ -f "$zip" ] || $PYTHON -m scripts.make_edm_cifar_subset --cifar-root "$CIFAR_ROOT" --n "$n" --seed 0 \
        --out "$ROOT/data/edm_subsets" || exit 1
      tdir=$ROOT/$OUT/train_$name
      snap=$(ls "$tdir"/*/network-snapshot-*.pkl 2>/dev/null | sort | tail -1)
      if [ ! -f "$tdir/DONE" ]; then
        echo "[$name] training ${DURATION} Mimg"
        mkdir -p "$tdir"
        resume=(); st_file=$(ls "$tdir"/*/training-state-*.pt 2>/dev/null | sort | tail -1)
        [ -n "$st_file" ] && resume=(--resume "$st_file")
        (cd "$EDM_REPO" && $PYTHON -m torch.distributed.run --standalone --nproc_per_node=1 train.py \
          --outdir "$tdir" --data "$zip" --cond 1 --arch ddpmpp --batch "$BATCH" --augment 0 \
          --duration "$DURATION" --snap 50 --dump 100 --seed 0 "${resume[@]}") \
          > "$OUT/train_$name.log" 2>&1 || { echo "[$name] training failed"; exit 1; }
        touch "$tdir/DONE"
        snap=$(ls "$tdir"/*/network-snapshot-*.pkl | sort | tail -1)
      fi
      evaluate "$name" "$snap" "$ind" || exit 1
    done
  fi
done
$PYTHON -u -m scripts.n3_edm_memorization --summarize "$OUT" > "$OUT/summary.log" 2>&1
echo COMPLETE > "$OUT/STATUS"
