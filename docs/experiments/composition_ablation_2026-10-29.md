# Missing 1D composition ablations — 29 October 2026

## Question and fixed protocol

Does the boundary-layer input help learned guided averaging retain the exact midpoint basin
within each output/loss choice? Complete the two missing cells, rather than retraining the
existing 39-run collection. No claim of eventual endpoint convergence is inferred from finite cutoffs.

| Variant | Output | Training loss | Extra input | Seeds |
|---|---|---|---|---|
| cfm_v (existing) | velocity | velocity MSE | none | 0–4 |
| cfm_v_s (new) | velocity | velocity MSE | asinh(tx/(1-t)^2) | 0–4 |
| cfm_x (new) | data | data MSE | none | 0–4 |
| cfm_x_s (existing) | data | data MSE | asinh(tx/(1-t)^2) | 0–4 |

All new runs: 200,000 steps, batch 2048, lr 0.003, AdamW without weight decay, cosine schedule,
gradient clipping at 1, dropout 0.1, uniform time sampling, MLP width 128/depth 4. Synthetic
two-atom samples are generated online; no dataset download or exact targets are needed.
Reuse B=1,2,3, the existing guidance grid, 2048 shared Gaussian sources (seed 20261021),
ROS2 tolerances 1e-5 and 1e-7 for L3, cutoffs 1e-2 to 1e-5 and radii 0.02/0.05/0.1.

Adding the feature adds 128 first-layer weights; this is a feature ablation, not a perfectly
parameter-matched comparison. Comparisons between velocity and data still change both
parametrization and loss weighting. GPU RNG streams need not match the historical hardware;
the saved source seed ensures paired evaluation, not identical training batches across machines.

Prediction to test: the feature may help retain the boundary-layer slope, but the velocity
output may still fail to retain the basin. All five seeds are run regardless of which variant
looks better. Distillation remains only a positive control.

## Execution and recovery

The remote checkout is `/home/jovyan/cfm-research-khoi/cfm-collapse`.
Use the existing `/home/jovyan/miniforge3/envs/lifemate/bin/python` without installing into it.
GPU 1 is the A30; GPU 0 is not used. Record the environment and code revision with each campaign.

```bash
cd /home/jovyan/cfm-research-khoi/cfm-collapse
export PYTHON=/home/jovyan/miniforge3/envs/lifemate/bin/python
CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=1 "$PYTHON" -m unittest scripts.test_learned_composition_ablation scripts.test_learned_composition_exact
for variant in cfm_v_s cfm_x; do
  CUDA_VISIBLE_DEVICES=1 OMP_NUM_THREADS=1 "$PYTHON" -u -m scripts.learned_composition \
    --variant "$variant" --seed 0 --steps 300 --smoke --out results/composition_ablation_preflight_20261029
done
# Only launch after both smoke runs and the tests pass.
tmux new-session -d -s cfm-ablation-20261029 \
  'PYTHON=/home/jovyan/miniforge3/envs/lifemate/bin/python bash scripts/server_composition_ablation.sh 1 results/composition_ablation_20261029'
```

The queue runs sequentially and refuses an existing campaign directory. Each run saves a
checkpoint and training summary before evaluation. Per-stage logs, `STATUS` and `progress.tsv`
provide local monitoring without an external tracker. A nonzero exit stops the queue and records
failure. Inspect the error before restarting; retain partial outputs. A completed training stage
can be evaluated with `--eval-only --out results/composition_ablation_20261029` and the matching
variant/seed. Training interruption requires restarting that run: optimizer states are not saved.
tmux survives browser disconnects, not server shutdown or allocation expiry.

## Analysis and cost

Primary comparison: seed-wise midpoint occupancy at B=1, w=2wc, gap 1e-5, radius 0.05,
against each existing counterpart and exact paired sources. Report all seed values, mean and
SD; any t-interval with five seeds is descriptive and fragile. Secondary checks: all guidance
levels/B values, cutoff/radius sensitivity, tolerance disagreement, boundary-layer field error
and slopes. Midpoint occupancy is distinct from off-training-atom occupancy (which also includes
points outside all three endpoint neighborhoods). Keep solver failures visible.

Historic 1D timing: roughly 11–12 minutes training and 2.1–3.4 hours total per run on the prior
machine. Ten sequential runs imply 21–34 hours as a planning reference, not an A30 benchmark.
Measure the first completed run before refining the ETA (report times in Asia/Bangkok).
Ten checkpoints occupy roughly 2.4 MB; saved trajectories/diagnostics and logs add storage.
No API costs. Loss-weighting controls and 2D ablations are not part of this first queue.
