# Running the extended h=4 run on Kaggle

The one experiment the paper leaves open is whether the across-condition slope
$\beta$ keeps rising past 60000 iterations. It is still rising monotonically when
the published budget ends — $-0.03, -0.03, -0.05, +0.12, +0.20, +0.39$ at $M{=}96$,
and $0.481$ re-measured at $M{=}256$ — so the paper says only that $0.481$ is where
60000 iterations reached, and explicitly does **not** claim $\beta \to 1$.

`configs/exp3_cifar_ddpm_h4_long.yaml` runs the budget that would settle it:
240000 iterations, everything else identical to the published run, so its first
60000 iterations reproduce that run point by point. Either outcome is a result.
$\beta$ continuing toward 1 turns a partial confirmation into a strong one;
$\beta$ saturating identifies a real ceiling and moves the deficit from the
optimiser to the parameterisation.

## Why chaining is legitimate

240000 iterations is longer than any free session, so the run has to stop and
restart. That is only sound if a chained run **is** the uninterrupted run —
otherwise "$\beta$ is still rising" would be a statement about the chaining.

A checkpoint therefore carries the optimiser state, the AMP scaler and both RNG
streams, not just the weights, and `scripts/verify_resume.py` checks the
consequence directly: train straight through, train the same budget with a stop
in the middle, compare every weight.

```
$ python scripts/verify_resume.py
  resumed from archived checkpoint: 88 tensors, identical
  resumed after a clean stop: 88 tensors, identical
ok: a chained run is bit-identical to an uninterrupted one
```

Run it once on the host before trusting a chained result there — it takes about
a minute on CPU.

## Cost

Measured throughput on a Quadro RTX 6000 with AMP is 4.75 it/s, i.e. 3.5 h for
60000 iterations and ~14 h for 240000. A Kaggle P100 has no tensor cores, so
expect it to be slower; a T4 is closer but still not an RTX 6000. Do not plan
against a guess — the first session prints its own measured rate and the number
of sessions left:

```
throughput 2.31 it/s (8.3k iterations per hour)
remaining 180000 iterations ~ 21.6 h ~ 3 more session(s) at --max-hours 8.0
```

Kaggle allows 9 h per GPU session and roughly 30 h per week, so budget 3–5
sessions across one or two weeks. Keep `--max-hours` under the session limit —
8.0 against a 9 h limit leaves room for the final evaluation and checkpoint
write. The clean stop is what guarantees a resume point; a session killed by the
host instead falls back on `ckpt_resume.pt`, which is rewritten at every
evaluation, so a hard kill costs at most one evaluation interval.

## Setup

Turn the GPU accelerator on. Then pick one of two ways to get the code and the
data onto the machine.

### Nothing to upload (recommended)

Turn **Internet on** as well (Notebook settings → Internet). The session then
fetches everything itself: it clones the repo and lets torchvision download
CIFAR-10. One cell, no datasets to attach:

```
!curl -sL -o /tmp/s.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_session.sh
!bash /tmp/s.sh
```

That fetches the session script; the script clones the rest. Download it to a
file rather than piping it into `bash` — it runs several heredocs, and a script
read from stdin shares that stream.

If the long-run config is not on `main` yet the script stops immediately and says
so. Point both lines at the branch that has it:

```
!curl -sL -o /tmp/s.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/<branch>/scripts/kaggle_session.sh
!BRANCH=<branch> bash /tmp/s.sh
```

CIFAR-10 lands in `/kaggle/working/cfm-collapse/data` and is re-downloaded each
session, which costs about 170 MB and a minute. To avoid that, save it once as
your own Kaggle dataset and pass `DATA=` as below.

A private repo needs a token in the URL
(`https://<token>@github.com/...`). Put it in a Kaggle Secret rather than in the
notebook, or attach the repo as a dataset instead.

### Or attach datasets

1. **the repo** — everything except `results/`, `data/` and `.venv/`. It is
   small. Name it `cfm-collapse`, and the default `REPO` finds it.
2. **CIFAR-10** — an existing public CIFAR-10 dataset, or your local
   `data/cifar-10-batches-py` (178 MB). `DATA` points at the directory
   *containing* `cifar-10-batches-py`.

This needs no internet, and is the faster option if you are running several
sessions.

### Rehearse first (two minutes, no GPU needed)

```
!SMOKE=1 bash /kaggle/input/cfm-collapse/scripts/kaggle_session.sh
```

(add `DATA=/kaggle/input/cifar10-python` if you attached CIFAR-10 rather than
letting it download, and `REPO=`/`BRANCH=` if the defaults do not find the code)

This runs 200 iterations of the real model on the real data, then deletes its
own checkpoints. It is there to catch the things that actually go wrong — the
dataset not attached, CIFAR-10 not found, a missing package — before a GPU
session is spent on them. It should end with `RUN COMPLETE at 200 iterations`.

### Session 1

```
!HOURS=8.0 bash /kaggle/input/cfm-collapse/scripts/kaggle_session.sh
```

Save the notebook version when it finishes, so its output becomes a dataset.

### Session 2 and later

Attach the previous session's output as an input dataset, then:

```
!PREV=/kaggle/input/<previous-output> HOURS=8.0 \
    bash /kaggle/input/cfm-collapse/scripts/kaggle_session.sh
```

`PREV` is copied forward first, so `metrics.csv`, the sample grids and the
archived checkpoints accumulate in one place instead of being scattered over
several notebook outputs. Repeat until the script prints `RUN COMPLETE`.

Every variable is optional and can be set inline: `REPO` (default
`/kaggle/input/cfm-collapse`), `GIT_URL` and `BRANCH` (used when `REPO` is
absent), `DATA` (unset means download), `PREV`, `HOURS` (default 8.0), `SMOKE`,
`OUTDIR` (default `/kaggle/working`).

### What comes back, and what stays

Each session writes `/kaggle/working/cfm-results-<timestamp>.zip`, around 300 KB:
`metrics.csv`, the config, the per-checkpoint sample grids, the session log, and
an `env.txt` recording the GPU and the checkpoints on disk. When the run
finishes, the zip also carries the re-evaluation and the beta trajectory. That
zip is the thing to send back. The script also prints the metric table as text,
for when attaching a file is inconvenient.

The **checkpoints stay in `/kaggle/working`** and must not go in the zip: one is
~430 MB, because a resumable checkpoint carries Adam's moments as well as the
weights. They travel to the next session as the notebook's own output. With
weights archived at four iterations plus the rolling resume point, expect about
2.2 GB of output per session — well inside Kaggle's limit.

## When it finishes

The last session runs the analyses itself, on the GPU it already has, and puts
them in the zip:

```
python -m scripts.reeval_exp3_cifar_ddpm --M 256 --n-conditions 48 \
    --runs exp3_cifar_ddpm_h4_long --out results/exp3/_cifar_ddpm_long
python -m scripts.beta_trajectory --M 96 --n-conditions 48 \
    --runs exp3_cifar_ddpm_h4_long \
    --out-json results/exp3/_cifar_ddpm_long/beta_trajectory.json \
    --fig     results/exp3/_cifar_ddpm_long/fig_beta_trajectory_long.png
```

The first re-measures each archived checkpoint at the sample size the paper
reports ($M{=}256$; at the training-time $M{=}16$ a covariance trace carries a
36% relative sampling error and is for watching the run, not for reporting). The
second extends Figure `betatraj`. Run them by hand only if a session died
between the last checkpoint and the analysis step; note the `-m` form, which the
imports require, and `--runs`, without which they target the published runs
instead.

Then check the reproduction before reading anything into the new points: the run
shares its seed, data, architecture and schedule with the published one, so its
iteration-60000 numbers should land on the published $\beta = 0.481 \pm 0.037$ at
$R^2 = 0.785$. If they do not, the chaining or the host changed something, and
the extension says nothing until that is explained.
