# Independent-seed training and evaluation — 2026-10-16

The user explicitly requested **chạy luôn đi** after the completed intervention
and CIFAR pilots and the statement that the ten new training runs had not yet
been started. This authorizes the ten-run independent-seed comparison below.
It does not establish novelty, posterior recovery, or ICLR readiness.

## Frozen comparison

- Problem/training seeds: **1001,1002,1003,1004,1005**, not selected by outcomes.
  Each seed is used for both h=0 and h=.1, giving ten runs. These are new
  linear-Gaussian problem instances, distinct from the exploratory seeds0–2.
- Data and architecture: N200,d2,k1,sigma_obs=.1; same prior/source scales;
  random operator; conditional MLP width128,depth4,time embedding64,SiLU.
- Adam,lr=.001,batch256,200000iterations, no early stopping, no learning-rate
  schedule, no weight decay, deterministic interpolant, no endpoint noise.
- Frozen checkpoints:1000,10000,30000,100000,200000.
- Training-time diagnostics:20train queries,2held-out queries,M64,RK4steps100,
  epsilon.001,512velocity points. Compared with the reference config, these
  changes reduce diagnostic overhead; optimizer, training budget and model are
  unchanged. Training/evaluation generators are separate. Held-out diagnostics
  are not used for selection, early stopping, or hyperparameter changes.
- Final evaluation at200k:20training queries fit bandwidth,64fresh queries
  evaluate the law,M512,RK4steps100/200/400,epsilon.001. Same source and query
  rules across h within each seed. Fresh query dataset seed20261016+problem_seed
  and fixed training-query indices from rounded linspace over0..199.

Primary metric: per-problem-seed mean normalized energy discrepancy of the
trained sampler from its Gaussian-label reference, with matched finite-time
reference-reference mean subtracted. Fit uses only the20training queries.
Report all five seeds and their paired h contrast; conditions are nested within
seeds, not independent model replicates. Laplace/Cauchy/kNN fits and same-moment
Gaussian controls are secondary. There is no equivalence claim or favorable-seed
selection. The reused evaluator has16reference-null pairs per condition: its
q95 envelope remains diagnostic, not a calibrated multiple-testing decision.

Kill/narrow rule: systematic full-law discrepancy narrows bandwidth to a moment
diagnostic. Failed solver screens prevent interpreting that discrepancy as purely
learned-field error. Failures are retained and stop their queue; no automatic
retraining, seed replacement or change of metric is configured.

## Preflight and benchmark

Server: SSH`guess`, account`guess03`, project`/mnt/home/guess03/cfm-collapse`.
Both L40 GPUs were idle with0MiBallocated. Disk563GBfree. Training code, solver,
model and problem hashes match local, including `src/train.py` SHA-256
`dd72962704d196ec493d6b20ad9eb5f7422b2853594a86bb5a55e74de8cf08f1`.
No old run name matched the planned seed range. Existing source/configs are
used directly; no new source upload was needed.

Benchmark: h0seed1001,2000iterations, same dimensions/model/batch/optimizer,
two diagnostic checkpoints, completed in15.1seconds including evaluation.
Finite training loss and output checkpoint confirmed. The apparent NaNs in
held-out velocity/own-atom fields are intentionally undefined diagnostics,
not nonfinite loss; these are not used for the final law comparison.

## Launched queues

- GPU0: h0, seeds1001→1005, queue PID2788237, started20:46:08 Asia/Bangkok.
- GPU1: h.1,seeds1001→1005, queue PID2792119, started20:46:23 Asia/Bangkok.
- One active model per GPU; the other eight runs are queued, not yet trained.
- Queue subprocesses ignore HUP and write separate logs; existing run-directory
  detection stops rather than overwriting. Each training job has a40-minute
  ceiling, each final evaluation a30-minute ceiling. First nonzero exit stops
  that queue and retains artifacts. No unrelated process was stopped.
- Rough scheduling estimate is1–2hours across both GPUs, with uncertainty from
  long-run training and M512/64-condition evaluation. This is not a completion
  promise; checkpoint timing will provide a better estimate.

Run names: `linear-gaussian-mlp-h0-seed{seed}-200k` and
`linear-gaussian-mlp-h0p1-seed{seed}-200k`.
Training outputs: `results/exp1/<run>/`.
Queue logs: `results/independent_seeds_20261016/logs/queue_h0.log` and
`queue_h0p1.log`, with separate per-run training/evaluation logs.
Final raw evaluation: `results/independent_seeds_20261016/eval_<run>/`.
Each run automatically proceeds from training to the existing validated
`results/theory_evidence_20261016/code/terminal_time/theory_evidence_pilot.py`
before the next seed. Its manifest records checkpoint/config/source hashes.

At20:46:56both first runs had written checkpoint10000 (one log was finishing
its evaluation). Training losses were finite. These are launch/progress checks,
not final results. No paper numbers have been updated.

## Completion verified after the user's status question

At21:49Asia/Bangkok, direct server inspection confirmed no training/evaluation
processes remaining and both GPUs idle (0MiB,0%compute). Both queues completed:

- h0: `QUEUE_COMPLETED 2026-10-16T21:29:51+07:00`.
- h.1: `QUEUE_COMPLETED 2026-10-16T21:30:14+07:00`.

All ten training exits and all ten evaluation exits were0. A separate artifact
check found exactly10evaluation directories, all10manifests with status
`completed`, and all10corresponding `ckpt_200000.pt` files present. The two queue
logs were copied to local `results/independent_seeds_20261016/logs/` for review.
These checks establish execution completion; final result aggregation and claim
interpretation have not yet been performed. The idle GPUs reflect completion,
not failure to launch.

## Final aggregation and raw verification

On the user's **tổng hợp đi**, all ten evaluation JSONs, controls and queue logs
were downloaded along with the ten full raw-sample files. Archive SHA-256 values
matched the server: JSON/logs
`aea1a5f32c04090b04a6bdf3adc180e072656ca18d45c8c66a32c9befdcbe3dd`, raw tar
`152619398f06a20ba55252112b50bc4af5584e38c264d2faaf074435a7dc2fe4`.

`scripts/summarize_independent_seeds.py --verify-raw` independently reproduced
640Gaussian model-reference energies,640same-moment-control energies,10Gaussian
variance-fit scales and paired solver displacements. Maximum absolute difference
between saved and direct NumPy energy calculations was1.15e-11. Truth/data/query
and source arrays matched across hwithin each seed. All controls passed.

Primary mean excess energy averaged across seeds was1.07393at h0and.0112775at
h.1; medians across seed means were.430079and.00811803,respectively. h0mean
includes an extreme unresolved condition from seed1004, which was not excluded.
Its query y1.61918 is outside its training-label range[-1.17355,1.18362];2/512
endpoints had norm>100, maxnorm2.95e7. Only639/640conditions passed the practical
solver screen. This off-training-label result is not a counterexample to an
empirical hard-conditioning theorem stated at training labels.

Among the four references fit by the frozen protocol, Gaussian had lowest mean
excess energy on5/5h.1seeds and0/5h0seeds. Reference-null q95counts remain
descriptive, because only16null pairs were used per condition. No formal
multiple-testing, universal full-law identity, or venue-readiness claim follows.

Final report and artifacts:
`results/independent_seeds_20261016/SUMMARY.md`, `summary.json`, `per_seed.csv`,
`independent_seeds.png/.pdf`. The figure was rendered and inspected. Whole-curve
training proxies are displayed separately from the final held-out distribution
metrics, with the caveat that training losses across different hbelong to
different objectives. No canonical-paper edits or new experiments were made
during aggregation.

Example of the exact training command pattern used by each queue:

```bash
env CFM_NUM_THREADS=4 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=0 \
 /mnt/home/guess03/clic/venv/bin/python -u -m src.train \
 --config configs/exp1_linear_gaussian.yaml --out results/exp1 --set \
 run_name=linear-gaussian-mlp-h0-seed1001-200k seed=1001 device=cuda \
 train.y_noise_h=0 train.max_iters=200000 \
 'train.checkpoints=[1000,10000,30000,100000,200000]' \
 eval.M=64 eval.n_eval_train=20 eval.n_heldout=2 eval.n_steps=100 eval.vel_points=512
```
