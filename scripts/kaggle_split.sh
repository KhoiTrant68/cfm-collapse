#!/usr/bin/env bash
# Instance versus optimisation variance on CIFAR-10, on Kaggle: a 2 x 2 grid of
# (problem_seed) x (seed) at one bandwidth, 20000 iterations each.
#
# Run it from one notebook cell with the GPU accelerator on and Internet on:
#
#     !curl -sL -o /tmp/s.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_split.sh
#     !bash /tmp/s.sh
#
# Everything is optional and set by environment variables:
#
#     DATA=/kaggle/input/cifar10-python   directory holding cifar-10-batches-py (else downloaded)
#     H=4.0                               label bandwidth; use 0.0 for the hard-conditioning control
#     ITERS=20000                         iterations per run
#     HOURS=8.0                           wall-clock budget; a run is not started unless it fits
#     RUNS="0:0 0:1 1:0 1:1"              problem_seed:seed pairs, in the order they are tried
#     SMOKE=1                             rehearsal: 200 iterations at N=64, two minutes, no result value
#     REPO=""                             an attached copy of the repo, used instead of cloning main
#
# A Kaggle session is limited to about nine hours, so two runs may not fit: whatever finishes is
# zipped with the run directories of the ones that did. Start the next session with
# PREV=<this session's output dataset> and the same RUNS; finished runs are skipped.
#
# What to bring back: results/exp3/exp3_cifar_ddpm_split_p{P}_s{S}/raw/metrics.csv for every run.
# Then, locally:  uv run python scripts/analyze_variance_split.py
set -uo pipefail

GIT_URL="https://github.com/KhoiTrant68/cfm-collapse.git"
DATA="${DATA:-}"
PREV="${PREV:-}"
H="${H:-4.0}"
ITERS="${ITERS:-20000}"
HOURS="${HOURS:-8.0}"
RUNS="${RUNS:-0:0 0:1 1:0 1:1}"
SMOKE="${SMOKE:-0}"
REPO="${REPO:-}"
OUTDIR="${OUTDIR:-/kaggle/working}"
WORK="${WORK:-$OUTDIR/cfm-collapse}"
CONFIG="configs/exp3_cifar_ddpm_split.yaml"
STAMP="$(date +%Y%m%d-%H%M%S)"
mkdir -p "$OUTDIR"
LOG="$OUTDIR/split-${STAMP}.log"
START=$(date +%s)

if [ "$SMOKE" = "1" ]; then
  ITERS=200
  HOURS=0.3
  RUNS="0:0 1:1"
fi

exec > >(tee -a "$LOG") 2>&1
echo "=== split session ${STAMP}: h=$H iters=$ITERS runs=[$RUNS] hours=$HOURS smoke=$SMOKE ==="

python - <<'PY'
import torch, sys
print(f"python {sys.version.split()[0]}  torch {torch.__version__}  cuda={torch.cuda.is_available()}")
if torch.cuda.is_available():
    p = torch.cuda.get_device_properties(0)
    print(f"gpu: {p.name}  {p.total_memory/1e9:.1f} GB")
else:
    print("gpu: NONE -- enable the accelerator, training is unusably slow without it")
PY

# ---- code: always from main unless REPO is given
if [ -z "$REPO" ]; then
  rm -rf "$OUTDIR/repo"
  if ! git clone -q --depth 1 --branch main "$GIT_URL" "$OUTDIR/repo"; then
    echo "ERROR: clone failed; turn Internet on in the notebook settings."; exit 2
  fi
  REPO="$OUTDIR/repo"
  echo "cloned main at $(git -C "$REPO" rev-parse --short HEAD)"
fi
[ -f "$REPO/$CONFIG" ] || { echo "ERROR: $REPO has no $CONFIG (push the latest main first)."; exit 2; }
grep -q 'problem_seed' "$REPO/src/train_exp3.py" || { echo "ERROR: src/train_exp3.py lacks problem_seed (push the latest main first)."; exit 2; }

mkdir -p "$WORK"
for d in src scripts configs; do cp -r "$REPO/$d" "$WORK/" 2>/dev/null; done
[ -f "$REPO/pyproject.toml" ] && cp "$REPO/pyproject.toml" "$WORK/"

# ---- CIFAR-10
mkdir -p "$WORK/data"
if [ -n "$PREV" ]; then
  HIT=$(find "$PREV" -maxdepth 8 -type d -name cifar-10-batches-py 2>/dev/null | head -1)
  [ -n "$HIT" ] && [ -f "$HIT/data_batch_1" ] && cp -r "$HIT" "$WORK/data/" && echo "cifar-10 copied from the previous session"
fi
if [ ! -f "$WORK/data/cifar-10-batches-py/data_batch_1" ]; then
  if [ -n "$DATA" ] && [ -d "$DATA/cifar-10-batches-py" ]; then
    cp -r "$DATA/cifar-10-batches-py" "$WORK/data/" && echo "cifar-10 copied from $DATA"
  else
    python - "$WORK/data" <<'PY' || exit 2
import sys
from torchvision import datasets
datasets.CIFAR10(root=sys.argv[1], train=True, download=True)
print("cifar-10 ready")
PY
  fi
fi

# ---- previous session's finished runs
if [ -n "$PREV" ]; then
  for r in $(find "$PREV" -maxdepth 8 -type d -path "*/exp3/exp3_cifar_ddpm_split_p*_s*" 2>/dev/null); do
    mkdir -p "$WORK/results/exp3"
    [ -d "$WORK/results/exp3/$(basename "$r")" ] || cp -r "$r" "$WORK/results/exp3/" && echo "restored $(basename "$r")"
  done
fi

# ---- train
cd "$WORK" || exit 2
DONE=()
for pair in $RUNS; do
  P="${pair%%:*}"; S="${pair##*:}"
  NAME="exp3_cifar_ddpm_split_p${P}_s${S}"
  CSV="results/exp3/$NAME/raw/metrics.csv"
  if [ -f "$CSV" ] && awk -F, -v it="$ITERS" 'NR>1 && $11+0>=it {f=1} END{exit !f}' "$CSV"; then
    echo "--- $NAME already reached $ITERS iterations, skipping"; DONE+=("$NAME"); continue
  fi
  ELAPSED=$(( $(date +%s) - START ))
  # a run needs roughly ITERS / 3 iterations per second on the slowest card; keep a margin
  NEED=$(( ITERS * 3 / 2 / 3 ))
  LEFT=$(python -c "print(int($HOURS*3600) - $ELAPSED)")
  if [ "$SMOKE" != "1" ] && [ "$LEFT" -lt "$NEED" ]; then
    echo "--- $NAME: ${LEFT}s left, needs about ${NEED}s; stopping here. Continue in a new session with PREV=."
    break
  fi
  echo "=== $NAME  ($(date +%H:%M:%S)) ==="
  EXTRA=()
  if [ "$SMOKE" = "1" ]; then
    EXTRA=(data.N=64 train.batch_size=16 eval.n_conditions=2 eval.M=8 eval.n_steps=10 "train.checkpoints=[100,200]")
  fi
  python -u -m src.train_exp3 --config "$CONFIG" \
      --set "run_name=$NAME" "seed=$S" "problem_seed=$P" "train.y_noise_h=$H" \
            "train.max_iters=$ITERS" "${EXTRA[@]}"
  echo "    rc=$? ($(date +%H:%M:%S))"
  DONE+=("$NAME")
done

# ---- send back the small artefacts only (checkpoints stay behind)
ZIP="$OUTDIR/split-results-${STAMP}.zip"
python - "$WORK" "$ZIP" <<'PY'
import sys, zipfile, pathlib
work, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
n = 0
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted((work / "results" / "exp3").glob("exp3_cifar_ddpm_split_p*_s*")):
        for f in p.rglob("*"):
            if f.is_file() and f.suffix in {".csv", ".json", ".yaml", ".png"} and f.stat().st_size < 20_000_000:
                z.write(f, f.relative_to(work)); n += 1
print(f"zipped {n} files -> {out}")
PY
echo "done: ${DONE[*]:-none}"
echo "log: $LOG"
