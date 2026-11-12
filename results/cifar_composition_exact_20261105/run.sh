#!/bin/sh
# Exact guided label averaging on eight CIFAR-10 pairs (largest candidate margins), then a
# hand-off / tolerance sensitivity check on the first pair.
PY=${PY:-python}
D=results/cifar_composition_exact_20261105
for pair in "292 1938" "1491 1514" "158 230" "1578 1677" "81 819" "1104 1984" "1315 1877" "17 678"; do
  $PY -u -m scripts.cifar_composition_exact --data $D/cifar2000_seed0.npz --pair $pair --B 1 \
    --ratios 0 0.5 0.9 1.1 2 5 10 --sources 512 --out $D/main || exit 1
done
$PY -u -m scripts.cifar_composition_exact --data $D/cifar2000_seed0.npz --pair 292 1938 --B 1 \
  --ratios 0.9 1.1 2 5 --sources 512 --handoff 1e-9 --out $D/handoff1e-9 || exit 1
$PY -u -m scripts.cifar_composition_exact --data $D/cifar2000_seed0.npz --pair 292 1938 --B 1 \
  --ratios 0.9 1.1 2 5 --sources 512 --rtol 1e-8 --atol 1e-11 --out $D/rtol1e-8 || exit 1
echo COMPLETE > $D/STATUS
