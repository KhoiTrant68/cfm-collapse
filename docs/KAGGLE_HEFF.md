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

## 2b. The long run: h = 4 continued to 240000 iterations

Over 60000 iterations h_eff falls towards h but ends at 1.13-1.34 h in every run, and
two runs level off while the others keep falling. Whether h_eff has a floor above h
decides how the central claim is worded. `configs/exp3_cifar_ddpm_heff_long.yaml`
continues the two session-A runs (`exp3_cifar_heff_h4_s0`, `_s1`) from their 60000
checkpoint to 240000. The learning rate is constant and the checkpoint carries Adam,
the AMP scaler and both RNG streams, so this is the same run as one trained to 240000
from the start, and it saves the first 60000 iterations (~9 h per run).

Attach **the output of session A part 2** (the version that ended with
`ALL RUNS COMPLETE` for `4:0 4:1`; its checkpoints go up to 60000) and run:

```
!curl -sL -o /tmp/h.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_heff.sh
!CONFIG=configs/exp3_cifar_ddpm_heff_long.yaml MIN_ITER=90000 PREV=/kaggle/input/<session-A-part-2-output> RUNS="4:0 4:1" bash /tmp/h.sh
```

The log should show `resuming from ... (iteration 60000 of 240000`. 180000 more
iterations at ~1.8 it/s is ~28 h per run, both runs side by side: about four sessions
at `HOURS=7.5`. Continue each with `PREV=` pointing at the previous session's output and
the same `CONFIG`, `MIN_ITER` and `RUNS`. `MIN_ITER=90000` analyses only the new
checkpoints (90k-240k, ~1.2 h per run) and writes `heff_<run>_from90k.json`, leaving
the 2k-60k results already in the repo untouched.

Output size grows to ~13 archived checkpoints per run (~11 GB for both), inside
Kaggle's 20 GB notebook output.

## 2c. A second dataset: MNIST

`configs/exp3_mnist_ddpm_heff.yaml` runs the same protocol on MNIST bottom-half
inpainting (same U-Net, N = 2000). Bandwidths are set against the condition-space
geometry (median nearest-neighbour distance 6.35): h = 2.5 and 3.0 give median n_eff
1.8 and 6.7 and a reference spanning 2.4 and 1.2 decades. MNIST downloads by itself.

```
!curl -sL -o /tmp/h.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_heff.sh
!CONFIG=configs/exp3_mnist_ddpm_heff.yaml PREFIX=exp3_mnist_heff RUNS="2.5:0 2.5:1" bash /tmp/h.sh
```

then `RUNS="2.5:2 3:0"` and `RUNS="3:1 3:2"`, each pair continued with `PREV=` like the
CIFAR-10 runs (keep the same `CONFIG` and `PREFIX`).

## 2d. Calibration at image scale on the finished runs (analysis only)

Does h_eff predict calibration beyond the synthetic problem? No reference posterior is
needed: for a held-out *test* image, its hidden half is a draw from the true conditional
law given its observed half, so a calibrated sampler must place it like one of its own
draws (per-pixel PIT uniform, 90% intervals covering 90%).
`scripts/calib_image_checkpoints.py` measures that at every archived checkpoint, on 64
test images with 64 samples each, plus the extraction rate.

The six 60k runs are finished, so a session only analyses them: attach the **part-2
output** of a pair (it holds the checkpoints up to 60000) and run

```
!curl -sL -o /tmp/h.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_heff.sh
!ANALYSIS=calib PREV=/kaggle/input RUNS="4:0 4:1" bash /tmp/h.sh
```

(`RUNS="4:2 5:0"` and `RUNS="5:1 5:2"` with the session-B and session-C part-2 outputs.)
Training is skipped because the runs are at their target; expect roughly 30-60 minutes
per pair. The zip carries `heff/calib_<run>.json`. For new runs, `ANALYSIS=both` does both
analyses in the session that finishes training.

Back home, put the `calib_<run>.json` files next to `heff_<run>.json` in
`results/exp3/_heff/` and run

```
uv run --with scipy python scripts/analyze_calib_image.py --dir results/exp3/_heff
```

It joins the two by iteration and reports, pooled over runs, the Spearman correlation of
h_eff (and h_eff/h, pixel sd, iteration) with 90% coverage, PIT error and extraction,
plus the correlation with the iteration partialled out: the synthetic test of the paper,
now at image scale and without a known posterior.

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
