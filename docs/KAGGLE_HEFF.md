# CIFAR-10 effective-bandwidth runs on Kaggle (experiment E3)

On the linear-Gaussian problem a trained flow follows the exact kernel reference at
one effective bandwidth h_eff, and h_eff falls towards the training bandwidth h as
training proceeds (`results/exp1/_heff`, `paper/figures/fig_heff_synthetic.png`). The
published CIFAR-10 runs kept only their final weights, so at image scale h_eff is known
at 60000 iterations alone (4.80, 5.75, 7.05 at h = 4, 5, 6; seed 0). These runs re-train
the published setup with the weights archived at seven points, and measure h_eff at
each of them on the GPU, inside the session.

| What | Where |
|---|---|
| Config | `configs/exp3_cifar_ddpm_heff.yaml` (the published setup; weights kept at 2k, 5k, 10k, 20k, 30k, 40k, 60k) |
| Session script | `scripts/kaggle_heff.sh` |
| Analysis | `scripts/heff_cifar_checkpoints.py` (h_eff from the variances, bandwidth from the means, 95% bootstrap intervals, β) |

## Before the first session

The session clones `main`, so the three files above must be **merged into `main`**
before anything runs, and nothing that touches training, the model or the config
should be pushed to `main` while runs are in progress. Every session log records the
commit it cloned (`cloned main at <sha>`).

Notebook settings: **Accelerator → GPU T4 x2**, **Internet → on**. With two GPUs a
session trains two runs side by side, one per GPU, for the quota of one session.
Attaching a CIFAR-10 dataset is optional; without one the session downloads it
(~170 MB) and later sessions reuse the copy in `PREV`.

## 1. Rehearsal (about 10 minutes)

```
!curl -sL -o /tmp/h.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_heff.sh
!SMOKE=1 RUNS="4:0 0:1" bash /tmp/h.sh
```

It trains the real model on 64 images to iteration 100, stops, resumes to 200 on each
GPU, runs the h_eff analysis on those two checkpoints, and times the real training step
(batch 128) on both GPUs at once. It should end with `ALL RUNS COMPLETE`. **Send back
the zip**: its `bench.txt` is the throughput to plan the sessions on.

## 2. The runs

Each entry of `RUNS` is `<h>:<seed>`; the seed redraws the training subset and mask as
well as the training randomness, as in the published three-instance runs. In order of
priority:

| Session | `RUNS` | Why |
|---|---|---|
| A | `"4:0 4:1"` | h = 4 is where the reference has range (4.6 decades); seed 0 also re-checks the published run |
| B | `"4:2 5:0"` | completes h = 4; starts h = 5 |
| C | `"5:1 5:2"` | completes h = 5 |
| D (optional) | `"0:0 0:1"` | hard conditioning: h_eff should fall towards 0 |
| E (optional) | `"0:2 6:0"` | completes h = 0; one run at the low-range bandwidth |

First session of a pair:

```
!curl -sL -o /tmp/h.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_heff.sh
!RUNS="4:0 4:1" bash /tmp/h.sh
```

If it ends with `NOT FINISHED`, save the notebook version, attach its output as a
dataset to a new session, and continue the **same** pair:

```
!curl -sL -o /tmp/h.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_heff.sh
!PREV=/kaggle/input/<that-output> RUNS="4:0 4:1" bash /tmp/h.sh
```

Training stops cleanly at `HOURS` (default 7.5), leaving ~1.5 h of the 9 h session for
the analysis and the zip. A session killed by the host resumes from `ckpt_resume.pt`,
losing at most one evaluation interval. The analysis runs only for runs that reached
60000 iterations; a run that finishes in a later session is analysed there.

Settings, all optional: `HOURS`, `DATA=<dir holding cifar-10-batches-py>`,
`M` (default 128) and `NCOND` (default 48) for the analysis, `REPO` for an offline
session with the repo attached.

## 3. What comes back

Each session writes `/kaggle/working/heff-results-<timestamp>.zip` (small): per run
`metrics.csv`, `config.yaml` and the training and analysis logs; `heff/heff_<run>.json`
for every analysed run; the session log; `env.txt` with the GPUs and the checkpoints
on disk; and, for the rehearsal, `bench.txt`. **Send the zip back.** The checkpoints
(~430 MB each, ~3 GB per run) stay in the notebook output; they are needed only to
continue an unfinished run.

## 4. The first number to check

`exp3_cifar_heff_h4_s0` is the published seed-0 run on a different GPU. At 60000
iterations expect agreement, not equality, with the published values: h_eff near
**4.80** and β near **0.481 ± 0.037**. Far from that, something other than hardware
changed; find it before reading the rest.
