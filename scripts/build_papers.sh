#!/usr/bin/env bash
# Compile paper_theory/ and/or paper_mechanism/ with tectonic on lab09.
# Usage (on lab09): bash scripts/build_papers.sh [paper_theory] [paper_mechanism]
# Needs the conda env /mnt/data/khoitm8/miniconda3/envs/cfm (conda-forge: tectonic).
set -u
source /mnt/data/khoitm8/env.sh
TECTONIC=/mnt/data/khoitm8/miniconda3/envs/cfm/bin/tectonic
ROOT=$(cd "$(dirname "$0")/.." && pwd)
dirs=("$@")
[ ${#dirs[@]} -eq 0 ] && dirs=(paper_theory paper_mechanism)
for d in "${dirs[@]}"; do
  log=/mnt/data/khoitm8/logs/tex_${d}.log
  (cd "$ROOT/$d" && "$TECTONIC" -X compile --keep-logs main.tex) >"$log" 2>&1
  rc=$?
  echo "== $d: rc=$rc, $(grep -o 'Output written on main.pdf ([0-9]* pages' "$ROOT/$d/main.log" 2>/dev/null)"
  grep -E '^error|^! ' "$log" "$ROOT/$d/main.log" 2>/dev/null | head -10
  grep -E 'undefined|multiply defined' "$ROOT/$d/main.log" 2>/dev/null | sort -u | head -20
  echo "overfull hboxes: $(grep -c 'Overfull \\hbox' "$ROOT/$d/main.log" 2>/dev/null)"
done
