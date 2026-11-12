#!/bin/sh
# Solver sensitivity of the exact CIFAR-10 composition on the seven pairs not covered by run.sh
# (pair 292/1938 is already in handoff1e-9/ and rtol1e-8/). Same sources and ratios around the
# threshold; one setting per invocation so the two settings can run in parallel:
#   sh run_sensitivity.sh handoff   or   sh run_sensitivity.sh rtol
PY=${PY:-python}
D=results/cifar_composition_exact_20261105
case "$1" in
  handoff) EXTRA="--handoff 1e-9"; OUT=$D/handoff1e-9 ;;
  rtol)    EXTRA="--rtol 1e-8 --atol 1e-11"; OUT=$D/rtol1e-8 ;;
  *) echo "usage: run_sensitivity.sh handoff|rtol"; exit 2 ;;
esac
for pair in "1491 1514" "158 230" "1578 1677" "81 819" "1104 1984" "1315 1877" "17 678"; do
  $PY -u -m scripts.cifar_composition_exact --data $D/cifar2000_seed0.npz --pair $pair --B 1 \
    --ratios 0.9 1.1 2 --sources 512 $EXTRA --out $OUT || exit 1
done
echo COMPLETE > $D/STATUS_sensitivity_$1
