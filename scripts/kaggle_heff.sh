#!/usr/bin/env bash
# One Kaggle session of the CIFAR-10 effective-bandwidth runs (docs/KAGGLE_HEFF.md).
#
# Run it from one notebook cell, with the GPU (T4 x2 preferred) and Internet on:
#
#     !curl -sL -o /tmp/h.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_heff.sh
#     !RUNS="4:0 4:1" bash /tmp/h.sh
#
# Each entry of RUNS is <bandwidth>:<seed>. With two GPUs the two runs train side
# by side, one per GPU, so a session costs the quota of one. Everything is optional:
#
#     RUNS="4:0 4:1"     runs to train or continue, <h>:<seed>
#     PREV=""            previous session's output dataset, to continue from
#     HOURS=7.5          training budget; the rest of the 9 h session is analysis
#     DATA=""            directory holding cifar-10-batches-py (unset: download)
#     SMOKE=0            1 = a few-minute rehearsal on the real model and data
#     M=128  NCOND=48    samples and conditions for the h_eff analysis
#     REPO=""            offline only: an attached copy of the repo
#     CONFIG=configs/exp3_cifar_ddpm_heff.yaml   ..._heff_long.yaml continues the
#                        session-A runs from 60000 to 240000
#     MIN_ITER=0         analyse only checkpoints at or after this iteration
#     PREFIX=exp3_cifar_heff   run-name prefix; exp3_mnist_heff with the MNIST config
#     ANALYSIS=heff      heff | calib | both: h_eff fit, posterior-free calibration on
#                        held-out test images (scripts/calib_image_checkpoints.py), or both
#     NTEST=64 MCAL=64   test images and samples per image for the calibration analysis
#
# When a run reaches its max_iters, the session measures h_eff at every
# archived checkpoint on the GPU it already has and zips the JSON. Checkpoints
# (~430 MB each) stay in /kaggle/working and travel to the next session as the
# notebook's output; they never go in the zip.
set -uo pipefail

RUNS="${RUNS:-4:0 4:1}"
REPO="${REPO:-}"
GIT_URL="https://github.com/KhoiTrant68/cfm-collapse.git"
DATA="${DATA:-}"
PREV="${PREV:-}"
HOURS="${HOURS:-7.5}"
SMOKE="${SMOKE:-0}"
M="${M:-128}"
NCOND="${NCOND:-48}"
OUTDIR="${OUTDIR:-/kaggle/working}"
WORK="${WORK:-$OUTDIR/cfm-collapse}"
CONFIG="${CONFIG:-configs/exp3_cifar_ddpm_heff.yaml}"
MIN_ITER="${MIN_ITER:-0}"
ANALYSIS="${ANALYSIS:-heff}"     # heff | calib | both
NTEST="${NTEST:-64}"             # held-out test images for the calibration analysis
MCAL="${MCAL:-64}"               # samples per test image
STAMP="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTDIR"
LOG="$OUTDIR/heff-session-${STAMP}.log"
PREFIX="${PREFIX:-exp3_cifar_heff}"
if [ "$SMOKE" = "1" ]; then
  PREFIX="smoke_heff"; HOURS="0.3"; M=8; NCOND=4; NTEST=4; MCAL=8
fi

exec > >(tee -a "$LOG") 2>&1
echo "=== cfm-collapse h_eff session ${STAMP} ==="
echo "runs=[$RUNS] prev=${PREV:-<none>} hours=$HOURS smoke=$SMOKE M=$M conditions=$NCOND"
echo "config=$CONFIG min_iter=$MIN_ITER"

# --------------------------------------------------------------------------- #
# 1. environment and code
# --------------------------------------------------------------------------- #
NGPU=$(python -c "import torch; print(torch.cuda.device_count())" 2>/dev/null || echo 0)
python - <<'PY'
import torch, sys
print(f"python {sys.version.split()[0]}  torch {torch.__version__}")
for i in range(torch.cuda.device_count()):
    p = torch.cuda.get_device_properties(i)
    print(f"gpu {i}: {p.name}  {p.total_memory/1e9:.1f} GB")
if not torch.cuda.is_available():
    print("gpu: NONE -- enable the accelerator (GPU T4 x2)")
PY
echo "gpus available: $NGPU"

if [ -z "$REPO" ]; then
  rm -rf "$OUTDIR/repo"
  if ! git clone -q --depth 1 --branch main "$GIT_URL" "$OUTDIR/repo"; then
    echo "ERROR: clone failed. Enable notebook internet (Settings -> Internet)."; exit 2
  fi
  REPO="$OUTDIR/repo"
  echo "cloned main at $(git -C "$REPO" rev-parse --short HEAD)"
fi
if [ ! -f "$REPO/$CONFIG" ]; then echo "ERROR: $REPO has no $CONFIG"; exit 2; fi
mkdir -p "$WORK"
for d in src scripts configs; do cp -r "$REPO/$d" "$WORK/"; done
cp "$REPO/pyproject.toml" "$WORK/" 2>/dev/null
cd "$WORK" || exit 2

# --------------------------------------------------------------------------- #
# 2. CIFAR-10: previous session's copy, then DATA, then download
# --------------------------------------------------------------------------- #
mkdir -p "$WORK/data"
if [ -n "$PREV" ] && [ ! -f "$WORK/data/cifar-10-batches-py/data_batch_1" ]; then
  HIT=$(find "$PREV" -maxdepth 8 -type d -name cifar-10-batches-py 2>/dev/null | head -1)
  if [ -n "$HIT" ] && [ -f "$HIT/data_batch_1" ]; then
    cp -r "$HIT" "$WORK/data/" && echo "cifar-10 copied from $HIT"
  fi
fi
if [ ! -f "$WORK/data/cifar-10-batches-py/data_batch_1" ]; then
  if [ -n "$DATA" ] && [ -d "$DATA/cifar-10-batches-py" ]; then
    cp -r "$DATA/cifar-10-batches-py" "$WORK/data/" && echo "cifar-10 copied from $DATA"
  else
    python -c "from torchvision import datasets; datasets.CIFAR10(root='$WORK/data', train=True, download=True)" \
      || { echo "ERROR: CIFAR-10 download failed; enable internet or pass DATA="; exit 2; }
  fi
fi

# --------------------------------------------------------------------------- #
# 3. runs: names, previous sessions
# --------------------------------------------------------------------------- #
NAMES=(); HS=(); SEEDS=()
for spec in $RUNS; do
  h="${spec%%:*}"; s="${spec##*:}"
  NAMES+=("${PREFIX}_h${h}_s${s}"); HS+=("$h"); SEEDS+=("$s")
done
mkdir -p "$WORK/results/exp3"
for name in "${NAMES[@]}"; do
  [ "$SMOKE" = "1" ] && rm -rf "$WORK/results/exp3/$name"
  if [ -n "$PREV" ]; then
    HIT=$(find "$PREV" -maxdepth 8 -type d -path "*/exp3/$name" 2>/dev/null | head -1)
    if [ -n "$HIT" ]; then
      rm -rf "$WORK/results/exp3/$name"
      cp -r "$HIT" "$WORK/results/exp3/" && echo "restored $name from $HIT"
    fi
  fi
done

# --------------------------------------------------------------------------- #
# 4. train, one run per GPU
# --------------------------------------------------------------------------- #
train_one() {  # name h seed gpu [extra overrides...]
  local name=$1 h=$2 s=$3 gpu=$4; shift 4
  CUDA_VISIBLE_DEVICES=$gpu CFM_KAGGLE_SESSION=1 python -u scripts/kaggle_run.py \
      --config "$CONFIG" --work "$WORK/results/exp3" --max-hours "$HOURS" \
      --set "run_name=$name" "seed=$s" "train.y_noise_h=$h" "$@" \
      > "$OUTDIR/train-${name}-${STAMP}.log" 2>&1
  echo "[$name] training returned $? (log: train-${name}-${STAMP}.log)"
  tail -n 6 "$OUTDIR/train-${name}-${STAMP}.log"
}

SMALL=()
if [ "$SMOKE" = "1" ]; then
  SMALL=(data.N=64 train.batch_size=16 eval.n_conditions=2 eval.M=8 eval.n_steps=10)
fi

run_all() {  # stage extra-overrides...
  local pids=() k=0
  for k in "${!NAMES[@]}"; do
    local gpu=0
    [ "$NGPU" -gt 1 ] && gpu=$(( k % NGPU ))
    if [ "$NGPU" -gt 1 ] && [ "${#NAMES[@]}" -le "$NGPU" ]; then
      train_one "${NAMES[$k]}" "${HS[$k]}" "${SEEDS[$k]}" "$gpu" "$@" & pids+=($!)
    else
      train_one "${NAMES[$k]}" "${HS[$k]}" "${SEEDS[$k]}" "$gpu" "$@"
    fi
  done
  for p in "${pids[@]}"; do wait "$p"; done
}

if [ "$SMOKE" = "1" ]; then
  echo "--- rehearsal part 1: train to 100 and stop ---"
  run_all train.max_iters=100 "train.checkpoints=[100]" "train.save_checkpoints=[100]" "${SMALL[@]}"
  echo "--- rehearsal part 2: resume from 100 and train to 200 ---"
  run_all train.max_iters=200 "train.checkpoints=[100,200]" "train.save_checkpoints=[100,200]" "${SMALL[@]}"
  TARGET=200
else
  echo "--- training (budget ${HOURS} h, ${NGPU} GPU(s)) ---"
  run_all
  TARGET=$(python -c "import yaml; print(yaml.safe_load(open('$CONFIG', encoding='utf-8'))['train']['max_iters'])")
fi

# --------------------------------------------------------------------------- #
# 5. h_eff at every archived checkpoint, for runs that finished
# --------------------------------------------------------------------------- #
progress() {
  python - "$WORK/results/exp3/$1" <<'PY'
import sys, glob, os, torch
ck = glob.glob(os.path.join(sys.argv[1], "checkpoints", "*.pt"))
print(max((int(torch.load(p, map_location="cpu")["iter"]) for p in ck), default=0))
PY
}
ANALYSE=(); DONEALL=1
for name in "${NAMES[@]}"; do
  d=$(progress "$name"); echo "$name: $d / $TARGET iterations"
  if [ "$d" -ge "$TARGET" ] 2>/dev/null; then ANALYSE+=("$name"); else DONEALL=0; fi
done
pids=(); k=0
for name in "${ANALYSE[@]}"; do
  gpu=0; [ "$NGPU" -gt 1 ] && gpu=$(( k % NGPU )); k=$((k + 1))
  ( LOGA="$OUTDIR/heff-${name}-${STAMP}.log"; : > "$LOGA"
    if [ "$ANALYSIS" = "heff" ] || [ "$ANALYSIS" = "both" ]; then
      CUDA_VISIBLE_DEVICES=$gpu python -u -m scripts.heff_cifar_checkpoints \
        --work "$WORK/results/exp3" --runs "$name" --M "$M" --n-conditions "$NCOND" \
        --min-iter "$MIN_ITER" --out "$WORK/results/exp3/_heff" >> "$LOGA" 2>&1
      echo "[$name] h_eff analysis returned $?"
    fi
    if [ "$ANALYSIS" = "calib" ] || [ "$ANALYSIS" = "both" ]; then
      CUDA_VISIBLE_DEVICES=$gpu python -u -m scripts.calib_image_checkpoints \
        --work "$WORK/results/exp3" --runs "$name" --n-test "$NTEST" --M "$MCAL" \
        --min-iter "$MIN_ITER" --out "$WORK/results/exp3/_heff" >> "$LOGA" 2>&1
      echo "[$name] calibration analysis returned $?"
    fi
    cat "$LOGA" ) &
  if [ "$NGPU" -gt 1 ]; then pids+=($!); else wait $!; fi
done
for p in "${pids[@]}"; do wait "$p"; done

BENCH="$OUTDIR/bench-${STAMP}.txt"
if [ "$SMOKE" = "1" ] && [ "$NGPU" -gt 0 ]; then
  # The rehearsal trains at batch 16 and says nothing about the real rate. Time
  # the real step at batch 128, on every GPU at once, as the real session will run.
  echo "--- throughput at the REAL batch size, all GPUs busy (plan on this) ---"
  bpids=()
  for ((g = 0; g < NGPU; g++)); do
    CUDA_VISIBLE_DEVICES=$g python -u scripts/bench_throughput.py --config "$CONFIG" \
        --session-hours 7.5 > "$BENCH.gpu$g" 2>&1 & bpids+=($!)
  done
  for p in "${bpids[@]}"; do wait "$p"; done
  for ((g = 0; g < NGPU; g++)); do echo "gpu $g:"; tail -n 4 "$BENCH.gpu$g"; done | tee "$BENCH"
fi

# --------------------------------------------------------------------------- #
# 6. zip the small artefacts
# --------------------------------------------------------------------------- #
OUTZIP="$OUTDIR/heff-results-${STAMP}.zip"
STAGE="$OUTDIR/.stage-${STAMP}"; rm -rf "$STAGE"; mkdir -p "$STAGE"
for name in "${NAMES[@]}"; do
  R="$WORK/results/exp3/$name"; mkdir -p "$STAGE/$name"
  cp "$R/raw/metrics.csv" "$R/config.yaml" "$STAGE/$name/" 2>/dev/null
  cp "$OUTDIR/train-${name}-${STAMP}.log" "$STAGE/$name/" 2>/dev/null
  cp "$OUTDIR/heff-${name}-${STAMP}.log" "$STAGE/$name/" 2>/dev/null
done
[ -d "$WORK/results/exp3/_heff" ] && cp -r "$WORK/results/exp3/_heff" "$STAGE/heff"
cp "$LOG" "$STAGE/session.log"
[ -f "$BENCH" ] && cp "$BENCH" "$STAGE/bench.txt"
python - "$WORK/results/exp3" "${NAMES[@]}" > "$STAGE/env.txt" <<'PY'
import sys, glob, os, torch
print("torch", torch.__version__, "cuda", torch.version.cuda)
for i in range(torch.cuda.device_count()):
    print("gpu", i, torch.cuda.get_device_properties(i).name)
for name in sys.argv[2:]:
    print(f"\n{name}:")
    for p in sorted(glob.glob(os.path.join(sys.argv[1], name, "checkpoints", "*.pt"))):
        print(f"  {os.path.basename(p):<20} {os.path.getsize(p)/1e6:.0f} MB")
PY
( cd "$STAGE" && zip -qr "$OUTZIP" . ); rm -rf "$STAGE"

if [ "$SMOKE" = "1" ]; then
  for name in "${NAMES[@]}"; do rm -rf "$WORK/results/exp3/$name/checkpoints"; done
  echo "(rehearsal: checkpoints deleted)"
fi
echo
echo "=================================================================="
echo "SEND BACK:  $OUTZIP   ($(du -h "$OUTZIP" | cut -f1))"
echo "=================================================================="
if [ "$DONEALL" = "1" ]; then
  echo "ALL RUNS COMPLETE: ${NAMES[*]}"
else
  echo "NOT FINISHED. Save this version, attach its output as a dataset, and re-run:"
  echo "    !PREV=/kaggle/input/<that-dataset> RUNS=\"$RUNS\" bash /tmp/h.sh"
fi
