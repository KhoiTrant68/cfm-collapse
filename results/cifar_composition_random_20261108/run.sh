#!/bin/sh
# (a) Exact guided label averaging on twelve mutual-nearest-neighbour CIFAR-10 pairs drawn at random
#     (seed 20261108, scripts/cifar_mutual_pairs.py) from the 73 not used in the main run.
# (b) Solver sensitivity of the eight main pairs at w/w_c = 5 and 10 (hand-off 1e-9; rtol 1e-8).
# Every pair and setting is one CPU process with two threads; all run in parallel.
PY=${PY:-python}
D=results/cifar_composition_random_20261108
DATA=results/cifar_composition_exact_20261105/cifar2000_seed0.npz
MAIN="292 1938|1491 1514|158 230|1578 1677|81 819|1104 1984|1315 1877|17 678"
RAND="882 1210|1443 1695|836 1735|101 1926|447 673|311 1983|118 1188|1180 1879|987 1426|814 1293|185 936|967 1681"
export CUDA_VISIBLE_DEVICES="" OMP_NUM_THREADS=2 MKL_NUM_THREADS=2
mkdir -p $D/logs
launch() {  # name list ratios out extra...
  name=$1; list=$2; ratios=$3; out=$4; shift 4
  echo "$list" | tr '|' '\n' | while read i j; do
    $PY -u -m scripts.cifar_composition_exact --data $DATA --pair $i $j --B 1 \
      --ratios $ratios --sources 512 "$@" --out $out > $D/logs/${name}_${i}_${j}.log 2>&1 &
  done
}
launch random "$RAND" "0.9 1.1 2 5" $D/random
launch handoff "$MAIN" "5 10" $D/handoff1e-9_large --handoff 1e-9
launch rtol "$MAIN" "5 10" $D/rtol1e-8_large --rtol 1e-8 --atol 1e-11
