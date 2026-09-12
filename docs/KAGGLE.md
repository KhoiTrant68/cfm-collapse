# Running the extended h=4 run on Kaggle

The one experiment the paper leaves open is whether the across-condition slope
$\beta$ keeps rising past 60000 iterations. It is still rising monotonically when
the published budget ends — $-0.03, -0.03, -0.05, +0.12, +0.20, +0.39$ at $M{=}96$,
and $0.481$ re-measured at $M{=}256$ — so the paper says only that $0.481$ is where
60000 iterations reached, and explicitly does **not** claim $\beta \to 1$.

`configs/exp3_cifar_ddpm_h4_long.yaml` runs the budget that would settle it:
240000 iterations, everything else identical to the published run's setup. Either outcome is a result.
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

That test runs on CPU, where training is deterministic, and it proves what it
needs to: the resume logic restores the optimiser, the scaler and the RNG streams
exactly. On a GPU the same statement cannot be tested as bit-identity, because GPU
training is not deterministic to begin with — cuDNN picks kernels at run time, so
two *uninterrupted* runs on the same card already differ in the last bits and
drift apart over many steps. A chained Kaggle run therefore differs from an
unchained one by exactly that much and no more: chaining adds nothing, but nor is
the result reproducible to the bit. The same holds, more strongly, when a later
session lands on a different card (a T4 one session, a P100 the next). None of
this touches the question the run answers, which is a trend over 240000
iterations and far larger than floating-point drift.

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

Turn the GPU accelerator **and Internet** on (Notebook settings → Internet). The
code always comes from `main`: every session clones it fresh, so whatever is on
`main` when the session starts is what runs, and nothing has to be uploaded.
Every command below is one notebook cell of this shape:

```
!curl -sL -o /tmp/s.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_session.sh
!bash /tmp/s.sh
```

The first line fetches the session script from `main`; the script clones the
rest. Download it to a file rather than piping it into `bash` — it runs several
heredocs, and a script read from stdin shares that stream. Settings go in front
of `bash` on the second line, e.g. `!SMOKE=1 bash /tmp/s.sh`.

CIFAR-10 is downloaded by torchvision into `/kaggle/working/cfm-collapse/data`
each session, which costs about 170 MB and a minute. To avoid that, attach a
CIFAR-10 dataset (a public one, or your local `data/cifar-10-batches-py`) and
pass `DATA=` pointing at the directory *containing* `cifar-10-batches-py`.

### Rehearse first (a few minutes)

```
!curl -sL -o /tmp/s.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_session.sh
!SMOKE=1 bash /tmp/s.sh
```

(add `DATA=/kaggle/input/cifar10-python` if you attached CIFAR-10 rather than
letting it download)

This runs 200 iterations of the real model on the real data, then deletes its
own checkpoints. It is there to catch the things that actually go wrong — the
dataset not attached, CIFAR-10 not found, a missing package — before a GPU
session is spent on them. It should end with `RUN COMPLETE at 200 iterations`.

The rehearsal trains at batch 16, and its throughput line says so; ignore it for
planning. A small batch leaves the GPU mostly idle, so that figure overstates the
real run several times over — on a T4 it reads about 6 it/s. The rehearsal then
times the real step at batch 128 (`scripts/bench_throughput.py`) and prints the
hours and sessions the full budget needs. **That** is the number to plan against,
and it is in the zip as `bench.txt`.

### Session 1

```
!curl -sL -o /tmp/s.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_session.sh
!HOURS=8.0 bash /tmp/s.sh
```

Save the notebook version when it finishes, so its output becomes a dataset.

### Session 2 and later

Attach the previous session's output as an input dataset, then:

```
!curl -sL -o /tmp/s.sh https://raw.githubusercontent.com/KhoiTrant68/cfm-collapse/main/scripts/kaggle_session.sh
!PREV=/kaggle/input/<previous-output> HOURS=8.0 bash /tmp/s.sh
```

`PREV` is copied forward first, so `metrics.csv`, the sample grids and the
archived checkpoints accumulate in one place instead of being scattered over
several notebook outputs. Repeat until the script prints `RUN COMPLETE`.

Every variable is optional and can be set inline: `DATA` (unset means download),
`PREV`, `HOURS` (default 8.0), `SMOKE`, `OUTDIR` (default `/kaggle/working`).
`REPO` is for a session without internet only: point it at an attached copy of
the repo and the script uses that instead of cloning `main`.

Because each session clones `main` afresh, a commit pushed to `main` between
sessions changes the code the rest of the run uses. The session log records the
commit it cloned (`cloned main at <sha>`); do not push changes to training, the
model or the config while the run is in progress.

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

Then check the 60000-iteration point before reading anything into the later
ones. The run shares its seed, data, mask, architecture and schedule with the
published one but not its GPU (that was a Quadro RTX 6000), so expect agreement,
not equality: $\beta$ near the published $0.481 \pm 0.037$, and an aggregate
ratio near seed 0's $2.255$, inside the $1.944$–$2.463$ that the three published
problem instances span. Far outside that and something other than hardware
changed — find it before the extension is read.
