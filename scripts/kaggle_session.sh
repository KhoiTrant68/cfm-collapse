#!/usr/bin/env bash
# One Kaggle session of the extended h=4 CIFAR-10 DDPM run.
#
# Run it from one notebook cell, with Internet on (Settings -> Internet):
#
#     !curl -sL -o /tmp/s.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_session.sh
#     !bash /tmp/s.sh
#
# The code always comes from main: the script clones it fresh every session, so
# nothing has to be uploaded or attached. Everything else is configured by
# environment variables, all optional:
#
#     DATA=/kaggle/input/cifar10-python   directory holding cifar-10-batches-py;
#                                         left unset, CIFAR-10 is downloaded
#     PREV=""                             previous session's output dataset
#     HOURS=8.0                           wall-clock budget (session limit is 9)
#     SMOKE=0                             1 = two-minute rehearsal, no GPU needed
#     REPO=""                             offline only: an attached copy of the
#                                         repo, used instead of cloning main
#
# It copies the repo into /kaggle/working, restores
# the previous session if PREV is set, trains until the budget expires, runs the
# analyses if the run finished, and zips the small artefacts to send back. The
# checkpoints stay in /kaggle/working and ride to the next session as the
# notebook's own output -- they are far too large to send.
set -uo pipefail

REPO="${REPO:-}"
GIT_URL="https://github.com/KhoiTrant68/cfm-collapse.git"
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
echo "repo=${REPO:-<clone main>}  data=${DATA:-<repo default>}  prev=${PREV:-<none>}  hours=$HOURS  smoke=$SMOKE"

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

if [ -z "$REPO" ]; then
  echo "cloning main from $GIT_URL"
  rm -rf "$OUTDIR/repo"
  if ! git clone -q --depth 1 --branch main "$GIT_URL" "$OUTDIR/repo"; then
    echo "ERROR: clone failed. Enable notebook internet (Settings -> Internet)."
    exit 2
  fi
  REPO="$OUTDIR/repo"
  echo "cloned main at $(git -C "$REPO" rev-parse --short HEAD)"
elif [ ! -d "$REPO/src" ]; then
  echo "ERROR: no src/ under REPO=$REPO. Unset REPO to clone main instead."
  exit 2
fi
if [ ! -f "$REPO/$CONFIG" ]; then
  echo "ERROR: $REPO has no $CONFIG."
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
if [ -z "$DATA" ] && [ -n "$PREV" ]; then
  # Every session's output carries the CIFAR-10 it downloaded; reuse it rather
  # than fetch 170 MB again (one session spent 28 minutes on that).
  HIT=$(find "$PREV" -maxdepth 8 -type d -name cifar-10-batches-py 2>/dev/null | head -1)
  if [ -n "$HIT" ] && [ -f "$HIT/data_batch_1" ]; then
    # Copied, not linked: a symlink into /kaggle/input would dangle in this
    # session's output, and the session after would download again.
    rm -rf "$WORK/data/cifar-10-batches-py"
    cp -r "$HIT" "$WORK/data/" && echo "cifar-10 copied from the previous session ($HIT)"
  fi
fi
if [ -f "$WORK/data/cifar-10-batches-py/data_batch_1" ] && [ ! -L "$WORK/data/cifar-10-batches-py" ]; then
  :
elif [ -n "$DATA" ]; then
  if [ -d "$DATA/cifar-10-batches-py" ]; then
    ln -sfn "$DATA/cifar-10-batches-py" "$WORK/data/cifar-10-batches-py"
    echo "cifar-10 linked from $DATA"
  else
    echo "WARNING: no cifar-10-batches-py under DATA=$DATA; will try to download"
  fi
else
  echo "no DATA given; fetching CIFAR-10 with torchvision (needs internet ON)"
  python - "$WORK/data" <<'PY'
import sys
from torchvision import datasets
try:
    datasets.CIFAR10(root=sys.argv[1], train=True, download=True)
    print("cifar-10 ready under", sys.argv[1])
except Exception as exc:
    print("DOWNLOAD FAILED:", exc)
    print("Enable notebook internet, or attach CIFAR-10 and pass DATA=<dir>.")
    raise SystemExit(1)
PY
  if [ $? -ne 0 ]; then exit 2; fi
fi

# --------------------------------------------------------------------------- #
# 4. restore the previous session
# --------------------------------------------------------------------------- #
if [ -n "$PREV" ]; then
  SRC=""
  for cand in "$PREV/cfm-collapse/results" "$PREV/results" "$PREV"; do
    [ -d "$cand/exp3/$RUN" ] && SRC="$cand" && break
  done
  if [ -z "$SRC" ]; then
    # Kaggle has mounted notebook outputs at more than one depth; look deeper.
    HIT=$(find "$PREV" -maxdepth 8-type d -path "*/exp3/$RUN" 2>/dev/null | head -1)
    [ -n "$HIT" ] && SRC="$(dirname "$(dirname "$HIT")")"
  fi
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
  SMALL=(data.N=64 train.batch_size=16 eval.n_conditions=2 eval.M=8 eval.n_steps=10)
  EXTRA=(--set "run_name=$RUN" train.max_iters=200 "train.checkpoints=[100,200]"
         "train.save_checkpoints=[100,200]" "${SMALL[@]}")
  # The rehearsal stops at 100 and resumes to 200, so the resume path runs on
  # this GPU. verify_resume.py runs on CPU and missed a CUDA-only failure there;
  # part 2 picks up ckpt_100.pt by itself and exits non-zero if resuming fails.
  rm -rf "$WORK/results/exp3/$RUN"
  echo "--- rehearsal part 1: train to 100 and stop ---"
  if ! CFM_KAGGLE_SESSION=1 python -u scripts/kaggle_run.py --config "$CONFIG" \
      --work "$WORK/results/exp3" --max-hours "$HOURS" \
      --set "run_name=$RUN" train.max_iters=100 "train.checkpoints=[100]" \
      "train.save_checkpoints=[100]" "${SMALL[@]}"; then
    echo "REHEARSAL FAILED in part 1"
    exit 1
  fi
  echo "--- rehearsal part 2: resume from 100 and train to 200 ---"
fi

echo "--- training (budget ${HOURS}h) ---"
CFM_KAGGLE_SESSION=1 python -u scripts/kaggle_run.py \
    --config "$CONFIG" \
    --work "$WORK/results/exp3" \
    --max-hours "$HOURS" \
    "${EXTRA[@]}"
TRAIN_RC=$?
echo "--- training returned $TRAIN_RC ---"

BENCH="$OUTDIR/bench-${STAMP}.txt"
if [ "$SMOKE" = "1" ]; then
  # The rehearsal trains at batch 16, which leaves the GPU mostly idle, so the
  # throughput it just printed overstates the real run several times over.
  # Time the real step at the real batch before anyone plans sessions on it.
  echo "--- throughput at the REAL batch size (ignore the batch-16 figure above) ---"
  python -u scripts/bench_throughput.py --config "$CONFIG" --session-hours "${SESSION_HOURS:-8.0}" \
      2>&1 | tee "$BENCH"
fi

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
[ -f "$BENCH" ] && cp "$BENCH" "$STAGE/bench.txt"
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
  echo "    !curl -sL -o /tmp/s.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_session.sh"
  echo "    !PREV=/kaggle/input/<that-dataset> bash /tmp/s.sh"
  echo "The checkpoints are in $WORK/results -- they stay"
  echo "in the notebook output and must NOT be put in the zip."
else
  echo "RUN COMPLETE at $DONE iterations."
  [ "$ANALYSED" = "1" ] && echo "The zip contains the re-evaluation and the beta trajectory."
fi
exit $TRAIN_RC
