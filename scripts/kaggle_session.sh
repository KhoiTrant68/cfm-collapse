#!/usr/bin/env bash
# One Kaggle session of the extended h=4 CIFAR-10 DDPM run.
#
# Run it from a single notebook cell:
#
#     !bash /kaggle/input/cfm-collapse/scripts/kaggle_session.sh
#
# Everything is configured by environment variables, all optional:
#
#     REPO=/kaggle/input/cfm-collapse     the repo dataset (read-only)
#     DATA=/kaggle/input/cifar10-python   directory holding cifar-10-batches-py
#     PREV=""                             previous session's output dataset
#     HOURS=8.0                           wall-clock budget (session limit is 9)
#     SMOKE=0                             1 = two-minute rehearsal, no GPU needed
#
# It copies the repo into /kaggle/working (the dataset is read-only), restores
# the previous session if PREV is set, trains until the budget expires, runs the
# analyses if the run finished, and zips the small artefacts to send back. The
# checkpoints stay in /kaggle/working and ride to the next session as the
# notebook's own output -- they are far too large to send.
set -uo pipefail

REPO="${REPO:-/kaggle/input/cfm-collapse}"
DATA="${DATA:-}"
PREV="${PREV:-}"
HOURS="${HOURS:-8.0}"
SMOKE="${SMOKE:-0}"
OUTDIR="${OUTDIR:-/kaggle/working}"
WORK="${WORK:-$OUTDIR/cfm-collapse}"
CONFIG="configs/exp3_cifar_ddpm_h4_long.yaml"
RUN="exp3_cifar_ddpm_h4_long"
STAMP="$(date +%Y%m%d-%H%M%S)"
mkdir -p "${OUTDIR:-/kaggle/working}"
LOG="$OUTDIR/session-${STAMP}.log"

if [ "$SMOKE" = "1" ]; then
  RUN="smoke_h4_long"
  HOURS="0.2"
fi

exec > >(tee -a "$LOG") 2>&1
echo "=== cfm-collapse session ${STAMP} ==="
echo "repo=$REPO  data=${DATA:-<repo default>}  prev=${PREV:-<none>}  hours=$HOURS  smoke=$SMOKE"

# --------------------------------------------------------------------------- #
# 1. environment
# --------------------------------------------------------------------------- #
python - <<'PY'
import torch, sys
print(f"python {sys.version.split()[0]}  torch {torch.__version__}  cuda={torch.cuda.is_available()}")
if torch.cuda.is_available():
    p = torch.cuda.get_device_properties(0)
    print(f"gpu: {p.name}  {p.total_memory/1e9:.1f} GB  capability {p.major}.{p.minor}")
else:
    print("gpu: NONE -- training will be unusably slow; enable the accelerator")
PY

if [ ! -d "$REPO/src" ]; then
  echo "ERROR: no src/ under REPO=$REPO. Attach the repo dataset, or set REPO=..."
  exit 2
fi

# --------------------------------------------------------------------------- #
# 2. writable copy of the repo (the input dataset is read-only)
# --------------------------------------------------------------------------- #
mkdir -p "$WORK"
for d in src scripts configs paper docs; do
  [ -d "$REPO/$d" ] && cp -r "$REPO/$d" "$WORK/" 2>/dev/null
done
[ -f "$REPO/pyproject.toml" ] && cp "$REPO/pyproject.toml" "$WORK/" 2>/dev/null
echo "repo copied to $WORK"

# --------------------------------------------------------------------------- #
# 3. CIFAR-10
# --------------------------------------------------------------------------- #
mkdir -p "$WORK/data"
if [ -n "$DATA" ]; then
  if [ -d "$DATA/cifar-10-batches-py" ]; then
    ln -sfn "$DATA/cifar-10-batches-py" "$WORK/data/cifar-10-batches-py"
    echo "cifar-10 linked from $DATA"
  else
    echo "WARNING: no cifar-10-batches-py under DATA=$DATA; will try to download"
  fi
else
  echo "no DATA given; torchvision will download CIFAR-10 (needs notebook internet ON)"
fi

# --------------------------------------------------------------------------- #
# 4. restore the previous session
# --------------------------------------------------------------------------- #
if [ -n "$PREV" ]; then
  SRC=""
  for cand in "$PREV/cfm-collapse/results" "$PREV/results" "$PREV"; do
    [ -d "$cand/exp3/$RUN" ] && SRC="$cand" && break
  done
  if [ -n "$SRC" ]; then
    mkdir -p "$WORK/results"
    cp -r "$SRC/exp3" "$WORK/results/"
    echo "restored previous session from $SRC"
    ls -la "$WORK/results/exp3/$RUN/checkpoints/" 2>/dev/null | tail -5
  else
    echo "WARNING: PREV=$PREV holds no results/exp3/$RUN; starting from scratch"
  fi
fi

# --------------------------------------------------------------------------- #
# 5. train
# --------------------------------------------------------------------------- #
cd "$WORK" || exit 2
EXTRA=()
if [ "$SMOKE" = "1" ]; then
  EXTRA=(--set "run_name=$RUN" train.max_iters=200 "train.checkpoints=[100,200]"
         "train.save_checkpoints=[200]" data.N=64 train.batch_size=16
         eval.n_conditions=2 eval.M=8 eval.n_steps=10)
fi

echo "--- training (budget ${HOURS}h) ---"
python -u scripts/kaggle_run.py \
    --config "$CONFIG" \
    --work "$WORK/results/exp3" \
    --max-hours "$HOURS" \
    "${EXTRA[@]}"
TRAIN_RC=$?
echo "--- training returned $TRAIN_RC ---"

# --------------------------------------------------------------------------- #
# 6. analyses, once the budget is actually finished
# --------------------------------------------------------------------------- #
if [ "$SMOKE" = "1" ]; then
  TARGET=200
else
  TARGET=$(python - "$CONFIG" <<'PY'
import sys, yaml
print(yaml.safe_load(open(sys.argv[1], encoding="utf-8"))["train"]["max_iters"])
PY
)
fi
DONE=$(python - "$WORK/results/exp3/$RUN" <<'PY'
import sys, glob, os, torch
ck = glob.glob(os.path.join(sys.argv[1], "checkpoints", "*.pt"))
print(max((int(torch.load(p, map_location="cpu")["iter"]) for p in ck), default=0))
PY
)
echo "progress: $DONE / $TARGET iterations"

ANALYSED=0
if [ "$SMOKE" != "1" ] && [ "$DONE" -ge "$TARGET" ] 2>/dev/null; then
  echo "--- re-evaluating checkpoints at M=256, 48 conditions ---"
  python -u -m scripts.reeval_exp3_cifar_ddpm --M 256 --n-conditions 48 \
      --runs "$RUN" --out "results/exp3/_cifar_ddpm_long" && ANALYSED=1
  echo "--- beta trajectory ---"
  python -u -m scripts.beta_trajectory --M 96 --n-conditions 48 \
      --runs "$RUN" \
      --out-json "results/exp3/_cifar_ddpm_long/beta_trajectory.json" \
      --fig "results/exp3/_cifar_ddpm_long/fig_beta_trajectory_long.png"
else
  echo "not finished yet (or smoke run): skipping the analyses"
fi

# --------------------------------------------------------------------------- #
# 7. zip what needs to come back -- small files only, never checkpoints
# --------------------------------------------------------------------------- #
OUTZIP="$OUTDIR/cfm-results-${STAMP}.zip"
STAGE="$OUTDIR/.stage-${STAMP}"
rm -rf "$STAGE"; mkdir -p "$STAGE"

R="$WORK/results/exp3/$RUN"
mkdir -p "$STAGE/run"
[ -f "$R/raw/metrics.csv" ] && cp "$R/raw/metrics.csv" "$STAGE/run/"
[ -f "$R/config.yaml" ]     && cp "$R/config.yaml" "$STAGE/run/"
[ -d "$R/figures" ]         && cp -r "$R/figures" "$STAGE/run/figures"
if [ -d "$WORK/results/exp3/_cifar_ddpm_long" ]; then
  cp -r "$WORK/results/exp3/_cifar_ddpm_long" "$STAGE/analysis"
fi
cp "$LOG" "$STAGE/session.log" 2>/dev/null
python - > "$STAGE/env.txt" <<'PY'
import torch, sys, platform
print("python", sys.version)
print("platform", platform.platform())
print("torch", torch.__version__, "cuda", torch.version.cuda)
if torch.cuda.is_available():
    p = torch.cuda.get_device_properties(0)
    print("gpu", p.name, f"{p.total_memory/1e9:.1f}GB", f"cc{p.major}.{p.minor}")
PY
python - "$R" >> "$STAGE/env.txt" <<'PY'
import sys, glob, os, torch
print("\ncheckpoints on disk:")
for p in sorted(glob.glob(os.path.join(sys.argv[1], "checkpoints", "*.pt"))):
    d = torch.load(p, map_location="cpu")
    print(f"  {os.path.basename(p):<20} iter={d['iter']:<8} "
          f"elapsed={d.get('elapsed_s',0)/3600:.2f}h  {os.path.getsize(p)/1e6:.0f} MB")
PY

( cd "$STAGE" && zip -qr "$OUTZIP" . )
rm -rf "$STAGE"

echo
echo "------------------ paste-able summary (if the zip is awkward) -----------"
python - "$R" "$DONE" "$TARGET" <<'PY'
import sys, os
run, done, target = sys.argv[1], sys.argv[2], sys.argv[3]
print(f"run={os.path.basename(run)}  progress={done}/{target}")
csv = os.path.join(run, "raw", "metrics.csv")
if not os.path.exists(csv):
    print("no metrics.csv yet"); raise SystemExit
import pandas as pd
d = pd.read_csv(csv)
cols = [c for c in ("iter", "train_loss", "trace_cov_mean", "trace_cov_kernel_mean",
                    "ratio_to_kernel_median", "n_eff_mean", "elapsed_s") if c in d]
print(d[cols].to_string(index=False, float_format=lambda v: f"{v:.4g}"))
PY
echo "-------------------------------------------------------------------------"

if [ "$SMOKE" = "1" ]; then
  rm -rf "$WORK/results/exp3/$RUN/checkpoints"
  echo "(smoke rehearsal: its checkpoints were deleted, they are ~430 MB each)"
fi
echo
echo "=================================================================="
echo "SEND BACK:  $OUTZIP   ($(du -h "$OUTZIP" | cut -f1))"
unzip -l "$OUTZIP" | tail -n +4 | head -20
echo "=================================================================="
if [ "$DONE" -lt "$TARGET" ] 2>/dev/null; then
  echo "NOT FINISHED. Save this notebook version, attach its output to the next"
  echo "session as a dataset, and re-run the same cell with:"
  echo "    PREV=/kaggle/input/<that-dataset> bash \$REPO/scripts/kaggle_session.sh"
  echo "The checkpoints are in $WORK/results -- they stay"
  echo "in the notebook output and must NOT be put in the zip."
else
  echo "RUN COMPLETE at $DONE iterations."
  [ "$ANALYSED" = "1" ] && echo "The zip contains the re-evaluation and the beta trajectory."
fi
exit $TRAIN_RC
