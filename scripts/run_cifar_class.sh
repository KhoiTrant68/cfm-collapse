#!/usr/bin/env bash
# The class-conditional CIFAR runs, sequentially, after the seed queue drains.
#
# Distinct labels put us in the single-atom regime; class labels repeat about 200
# times at N=2000 and put us in the regime deployed models occupy, where the
# population endpoint is the class empirical measure and the predicted conditional
# variance is the within-class scatter rather than zero. That is a prediction of a
# specific large number, and a model that hits it looks healthy on every diversity
# metric while emitting only training images.
#
# h=0 is the headline: hard conditioning with ties. h=0.4 keeps the classes
# separate under the one-hot geometry (distance sqrt(2) between classes) and shows
# what partial cross-class mixing does to the reference.
#
#   ssh <host> 'cd <repo-root> && \
#     setsid nohup bash scripts/run_cifar_class.sh 0 \
#       > logs/cifar_class.log 2>&1 < /dev/null &'
set -u
cd "$(dirname "$0")/.."
GPU="${1:-0}"
PY=${PY:-.venv/bin/python}
mkdir -p logs

# Wait for anything still in flight, including the seed queue.
while pgrep -f "src.train_exp[3] " > /dev/null; do
  echo "  waiting for an in-flight run to finish ($(date +%H:%M:%S))"
  sleep 300
done

for h in 0 0.4; do
  name="exp3_cifar_class_h${h/./p}"
  if [ -f "results/exp3/${name}/raw/metrics.csv" ]; then
    echo "  [skip] $name"
    continue
  fi
  echo "=== $name ($(date +%H:%M:%S)) ==="
  CUDA_VISIBLE_DEVICES="$GPU" $PY -u -m src.train_exp3 \
      --config configs/exp3_cifar_class.yaml \
      --set "run_name=$name" "train.y_noise_h=${h}" \
      > "logs/${name}.log" 2>&1
  echo "    rc=$? ($(date +%H:%M:%S))"
done
echo "CIFAR CLASS DONE ($(date +%H:%M:%S))"
