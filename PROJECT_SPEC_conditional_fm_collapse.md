# PROJECT SPEC — Posterior Variance Collapse in Conditional Flow Matching

> **Read this whole file carefully before writing code.**
> This is a **theoretical research** project, not a SOTA engineering project.
> The goal of the code is to **verify a theorem numerically**, not to score high on a benchmark.
> If the numbers **do not match** the theoretical prediction, that is important information: report it honestly, and do NOT tune to force the desired result.

> **Status (2026-10-11).** This is the original specification, kept as the record of
> what was planned. The theory was later rewritten in `docs/THEORY.md` and the paper; in
> particular the "contrast lemma" of §2.2 Step 4 was corrected (the unconditional
> minimiser also memorises, see Cor 6), and P5/P6 turned out not to be determined by the
> population theory (Part E). `results/RESULTS.md` records what was found.

---

## 0. TL;DR for the agent

You will implement 3 experiments of increasing complexity to verify a theorem about **posterior variance collapse** in conditional flow matching (CFM):

1. **EXP-1 (Linear-Gaussian)**: the posterior has a closed form → exact verification. **Highest priority.**
2. **EXP-2 (Gaussian Mixture)**: tests mode collapse / selective memorization.
3. **EXP-3 (small image inpainting)**: a qualitative illustration.

Everything runs on 1 GPU with 24GB. EXP-1 and EXP-2 also run on CPU.

**Main deliverable:** a `RESULTS.md` report with figures that confirm (or refute) the theoretical predictions of Section 2.

---

## 1. Research context

### 1.1 The problem

Conditional flow matching is widely used to solve Bayesian inverse problems: learn a velocity field `v(x_t, t, y)` that transports a source distribution to the **posterior** `p(x | y)`.

arXiv 2603.14135 ("Solving physics-constrained inverse problems with conditional flow matching") observes empirically that with long training (overtraining) the generated distribution suffers from:
- **variance collapse**: the posterior variance is severely underestimated;
- **selective memorization**: generated samples gather around training points with similar observations.

They give only "a simplified theoretical analysis" and fix it with **early stopping** (a heuristic).

arXiv 2510.18118 ("Gradient Variance Reveals Failure Modes in Flow-Based Generative Models") proves for the **unconditional** case that, with a deterministic interpolant, there is a vector field reaching loss = 0 by memorizing the training pairing (Proposition 2). They also argue that standard CFM does **not** memorize because `x₀` is resampled independently every epoch, which breaks the bijection `(x_t, t) ↦ (x₀, x₁)`.

### 1.2 The central hypothesis of this project

> **In the conditional case, the "resample x₀" protection is disabled, because the conditioning variable `y` acts as an identifier of its training sample.**

This is the new point: conditioning makes injectivity **stronger**, not weaker.

---

## 2. Theory to verify

### 2.1 Setup

- A joint distribution `ρ(x, y)` on `ℝ^d × ℝ^k`.
- A training set `{(x⁽ⁱ⁾, y⁽ⁱ⁾)}_{i=1}^N` drawn i.i.d. from `ρ`.
- A source `π₀` (e.g. `N(0, I)`), **resampled independently every time**.
- A linear interpolant (deterministic, noise-free):
  ```
  x_t = (1 - t) x₀ + t x₁,   t ~ U(0,1)
  ```
- Loss:
  ```
  L(v) = E_{t, x₀~π₀, (x₁,y)~ρ̂}  || (x₁ - x₀) - v(x_t, t, y) ||²
  ```
  where `ρ̂` is the empirical measure.

### 2.2 Theorem (Conditional Minimizer Collapses)

The minimizer over any class of measurable functions is `v*(x, t, y) = E[x₁ - x₀ | x_t = x, t, y]`.

**Step 1.** Under `ρ̂`, the variable `y` is **discrete**, with atoms at `y⁽ⁱ⁾`. If the marginal `ρ_Y` is atomless, the `y⁽ⁱ⁾` are distinct almost surely, so the condition `{y = y⁽ⁱ⁾}` selects exactly the index `i`. Hence `x₁ = x⁽ⁱ⁾` is **determined**.

*(Note: working with the empirical measure avoids conditioning on a measure-zero event altogether.)*

**Step 2.** With `x₁ = x⁽ⁱ⁾` fixed and `t < 1`:
```
x_t = (1-t) x₀ + t x⁽ⁱ⁾   ⟹   x₀ = (x_t - t x⁽ⁱ⁾) / (1-t)
```
No variance remains. Hence the closed form:
```
v*(x, t, y⁽ⁱ⁾) = (x⁽ⁱ⁾ - x) / (1 - t)          ......... (★)
```

**Step 3.** Integrate the ODE `dx/dt = v*`. Put `u = x - x⁽ⁱ⁾`:
```
du/dt = -u/(1-t)  ⟹  u(t) = u(0)(1-t)
⟹ x(t) = x⁽ⁱ⁾ + (1-t)(x₀ - x⁽ⁱ⁾)
⟹ x(1) = x⁽ⁱ⁾  for EVERY x₀
```
The pushforward of `π₀` is `δ_{x⁽ⁱ⁾}` → **the posterior collapses completely, variance = 0**.

**Step 4 (contrast lemma, unconditional).** Without `y`, given `(x_t = x, t)`, every candidate `i` corresponds to a valid source `x₀⁽ⁱ⁾ = (x - t x⁽ⁱ⁾)/(1-t)` with density `π₀(x₀⁽ⁱ⁾) > 0`. The posterior over `i` has **positive weight for every i**:
```
v*(x,t) = Σᵢ wᵢ(x,t) (x⁽ⁱ⁾ - x₀⁽ⁱ⁾),   wᵢ ∝ π₀(x₀⁽ⁱ⁾)
```
→ a genuine weighted average → a smooth flow, no memorization.

### 2.3 Numerically testable predictions

| ID | Prediction | How to measure |
|---|---|---|
| **P1** | The longer the training, the more the variance of the generated distribution (conditioned on `y⁽ⁱ⁾` in the training set) → 0 | Generate many samples with the same `y⁽ⁱ⁾` and different `x₀`; measure the variance against the iteration count |
| **P2** | The learned velocity network converges to the closed form (★) | Compare `v_θ(x,t,y⁽ⁱ⁾)` with `(x⁽ⁱ⁾ - x)/(1-t)` over iterations |
| **P3** | Generated samples converge to the right training point `x⁽ⁱ⁾`, not another one | Measure `‖x_gen - x⁽ⁱ⁾‖` vs `min_{j≠i} ‖x_gen - x⁽ʲ⁾‖` |
| **P4** | Collapse does **not** happen (or is much weaker) for unconditional CFM in the same setup | Train an unconditional model in parallel and compare the variance |
| **P5** | The amount of collapse depends on the spacing between the `y⁽ⁱ⁾`: the closer the `y` (large observation noise / small k), the milder the collapse | Sweep the observation noise σ_obs |
| **P6** | Collapse weakens as N grows at fixed capacity | Sweep N ∈ {50, 200, 1000, 5000} |
| **P7 (remedy)** | Adding noise/smoothing to the **conditioning variable y** restores the variance | Train with `y + h·ε`, sweep the bandwidth h |

**P1, P2 and P4 are the core.** If these three do not match → stop and report, do not continue.

---

## 3. EXP-1 — Linear-Gaussian (HIGHEST PRIORITY)

### 3.1 Why
The posterior has a **closed form** → an exact ground truth to compare against, independent of approximate metrics.

### 3.2 Model
```
x ~ N(μ_x, Σ_x)                    # prior
y = A x + ε,  ε ~ N(0, σ_obs² I)   # linear forward model
```
Analytic posterior:
```
Σ_post = (Σ_x⁻¹ + Aᵀ A / σ_obs²)⁻¹
μ_post(y) = Σ_post (Σ_x⁻¹ μ_x + Aᵀ y / σ_obs²)
```

### 3.3 Default configuration
- `d = 2` (easy to plot) and `d = 10` (to test higher dimension)
- `k = 1` and `k = d` (sweep the observation dimension)
- `A`: a fixed random matrix (fixed seed), or a simple projection
- `σ_obs ∈ {0.01, 0.1, 0.5, 1.0}` (for P5)
- `N ∈ {50, 200, 1000, 5000}` (for P6)
- Source `π₀ = N(0, I_d)`

### 3.4 Model
- MLP: 3-4 layers, width 128, SELU or SiLU activation
- Input: concat `[x_t, t_embed, y]`, with a sinusoidal time embedding
- Output: a vector field `∈ ℝ^d`
- Adam optimizer, lr 1e-3, batch 256
- **Train for a very long time**: up to 100k-200k iterations. Overtraining is the *goal*, not a bug.
- Save checkpoints at log-spaced points: 100, 300, 1k, 3k, 10k, 30k, 100k, 200k

### 3.5 Measurements (run at every checkpoint)

For each `y⁽ⁱ⁾` in the training set (take ~20 representative points):
1. Generate `M = 1000` samples by integrating the ODE from `M` different values of `x₀` (Euler or RK4, 100 steps; use `torchdiffeq` or write your own, which is simpler and good enough).
2. Compute:
   - `trace(Cov(samples))` → compare with `trace(Σ_post)` **[P1]**
   - `‖mean(samples) - μ_post(y⁽ⁱ⁾)‖`
   - `‖mean(samples) - x⁽ⁱ⁾‖` **[P3]** ← if it goes to 0, the collapse really is onto the training point
3. Measure the velocity error against the closed form (★) **[P2]**:
   - Sample random `(x, t)`, compute `‖v_θ(x,t,y⁽ⁱ⁾) - (x⁽ⁱ⁾-x)/(1-t)‖ / ‖(x⁽ⁱ⁾-x)/(1-t)‖`
   - Avoid `t` too close to 1 (use `t ∈ [0, 0.95]`) because (★) is singular at `t=1`
4. For `y` **outside** the training set (held-out): repeat 1-2 to look at generalization

### 3.6 Control baseline [P4]
Train an **unconditional** model in parallel (drop the `y` input) on the same `{x⁽ⁱ⁾}`, for the same number of iterations and with the same capacity. Measure the covariance trace of the generated samples. Prediction: it does **not** collapse to 0 like the conditional model.

### 3.7 Remedy [P7]
Train additional models with smoothed conditioning:
```
y_train = y⁽ⁱ⁾ + h · ε,  ε ~ N(0, I),  h ∈ {0, 0.01, 0.05, 0.1, 0.5}
```
Measure the covariance trace again. Prediction: larger `h` → the variance is restored, but with a bias (the mean shifts). Look for a U-shaped trade-off in `h`.

**Important:** clearly distinguish this remedy (noise on **y**) from adding noise to the **interpolant** as in 2510.18118. Also run an interpolant-noise variant (`x_t = (1-t)x₀ + t x₁ + σ√(t(1-t)) Z`) to compare the two kinds of remedy; this will be an important table in the paper.

---

## 4. EXP-2 — Gaussian Mixture

### 4.1 Goal
Test **selective memorization** when the true posterior is **multimodal**, the case where collapse does the most harm.

### 4.2 Setup
- Prior on `x`: a Gaussian mixture with 4-8 modes in `ℝ²` or `ℝ¹⁰`
- Forward model: `y = A x + ε`, with `A` chosen to **lose information** (e.g. a projection to 1 dimension) → a multimodal true posterior
- Ground-truth posterior: computed by numerical integration on a grid (d=2) or by MCMC (d=10)

### 4.3 Measurements
- **Mode coverage**: for a given `y`, how many modes of the true posterior the generated samples cover
- Sinkhorn distance / MMD between the generated samples and the true posterior (use `geomloss`)
- Track over iterations → expect mode coverage to decrease with overtraining

---

## 5. EXP-3 — Image inpainting (illustration)

### 5.1 Goal
**Qualitative illustration only**, NOT a race for quality.

### 5.2 Setup
- Dataset: CelebA or MNIST, resized to **32×32 or 64×64**
- A small subset: `N ∈ {500, 5000}` (less data makes the collapse clearer)
- Forward model: a mask covering a large region (e.g. the bottom half of the image) → `y` = the remaining part of the image
- Model: a small U-Net, conditioned by concatenating `y` along the channels
- Measure: generate many samples for the same `y` and measure the pixel-wise variance; compare with the closest training image (nearest neighbour in the training set) to detect memorization

### 5.3 Figures to produce
- Grid: the same `y`, many different `x₀` → under collapse, all samples are identical
- A comparison between an early checkpoint (not yet overtrained) and a late one
- Place the closest training image alongside to show selective memorization

---

## 6. Desired code structure

```
project/
├── README.md
├── requirements.txt
├── configs/
│   ├── exp1_linear_gaussian.yaml
│   ├── exp2_gmm.yaml
│   └── exp3_inpainting.yaml
├── src/
│   ├── models/
│   │   ├── mlp_velocity.py       # MLP velocity field + time embedding
│   │   └── unet_small.py         # for EXP-3
│   ├── flows/
│   │   ├── cfm.py                # CFM loss (conditional & unconditional)
│   │   ├── interpolants.py       # deterministic + stochastic interpolant
│   │   └── ode_solver.py         # Euler / RK4, handles the singularity near t=1
│   ├── problems/
│   │   ├── linear_gaussian.py    # forward model + analytic posterior
│   │   ├── gmm.py
│   │   └── inpainting.py
│   ├── metrics/
│   │   ├── posterior_stats.py    # trace cov, mean error, distance to the training point
│   │   ├── velocity_error.py     # comparison with the closed form (★)
│   │   └── distances.py          # MMD, Sinkhorn (geomloss)
│   └── train.py
├── scripts/
│   ├── run_exp1.sh               # includes the σ_obs, N and h sweeps
│   ├── run_exp2.sh
│   └── run_exp3.sh
├── notebooks/
│   └── analysis.ipynb            # collects the figures
└── results/
    ├── figures/
    ├── raw/                      # csv/json of the metrics per checkpoint
    └── RESULTS.md                # the final report
```

---

## 7. Important technical requirements

1. **Reproducibility:** fix the seed everywhere; log the seed in the config; save the config with every run.
2. **The singularity at t=1:** the closed form (★) blows up as `t→1`. When integrating the ODE, stop at `t = 1-ε` with `ε = 1e-3`, or use a decreasing step size. **State clearly in a code comment** that this is a deliberate treatment of the singularity, not a hack.
3. **No early stopping by default.** Overtraining is the object of study. Enable early stopping only in a separate comparison branch (to reproduce the remedy of 2603.14135).
4. **Log everything:** train loss, test loss, and every metric of Section 3.5 at every checkpoint. Save to CSV so the figures can be redrawn without retraining.
5. **Run fast first:** provide a `--smoke-test` mode that runs the whole pipeline in <2 minutes with a small N and few iterations, to check the code before the full run.
6. **No heavy libraries unless needed.** EXP-1/EXP-2 need only `torch`, `numpy`, `matplotlib`, `geomloss`, `pyyaml`.

---

## 8. Reference libraries / repositories

| Repo | Used for | Link |
|---|---|---|
| `facebookresearch/flow_matching` | Meta's official FM library: reference for the API and the standard path/interpolant implementation | https://github.com/facebookresearch/flow_matching |
| `atong01/conditional-flow-matching` (torchcfm) | A compact CFM implementation with 2D examples: **the best reference for EXP-1/2** | https://github.com/atong01/conditional-flow-matching |
| `annegnx/PnP-Flow` | Config/training pipeline structure for FM in inverse problems | https://github.com/annegnx/PnP-Flow |
| `geomloss` | Sinkhorn / MMD distance | https://www.kernel-operations.io/geomloss/ |
| `torchdiffeq` | ODE solver (optional; your own Euler/RK4 is enough) | https://github.com/rtqichen/torchdiffeq |

**Priority:** use `torchcfm` as the reference frame for the loss/interpolant, but **write your own** conditional part and measurements, because exact control is needed.

---

## 9. Background reading (no implementation needed, context only)

| arXiv ID | Title | Role |
|---|---|---|
| 2603.14135 | Solving physics-constrained inverse problems with conditional flow matching | **Source of the phenomenon**: variance collapse & selective memorization |
| 2510.18118 | Gradient Variance Reveals Failure Modes in Flow-Based Generative Models | **Source of the proof technique**: Proposition 2, Remark 2 |
| 2210.02747 | Flow Matching for Generative Modeling (Lipman et al.) | FM foundations |
| 2209.03003 | Flow Straight and Fast: Rectified Flow (Liu et al.) | RF foundations |
| 2303.08797 | Stochastic Interpolants (Albergo et al.) | A unifying flow/diffusion framework |
| 2502.09616 | Variational Rectified Flow Matching | Related: multimodal velocities get averaged |
| 2509.19903 | LIRF: velocity field collapse under data scarcity | Related work on collapse |

---

## 10. Order of work

**Stage A (mandatory first):**
1. Set up the repo, requirements and config system.
2. Implement EXP-1 with the default configuration `d=2, k=1, N=200, σ_obs=0.1`.
3. Run `--smoke-test` to verify the pipeline.
4. Full run: train to 200k iterations, collect the metrics at the checkpoints.
5. **Draw the 3 core figures:**
   - covariance trace vs iteration (with the ground-truth line `trace(Σ_post)`) **[P1]**
   - velocity error against the closed form (★) vs iteration **[P2]**
   - conditional vs unconditional comparison **[P4]**
6. **STOP AND REPORT.** If P1/P2/P4 do not match the prediction → report at once, do not continue to Stage B.

**Stage B (only if A succeeds):**
7. Sweep `σ_obs` **[P5]**, sweep `N` **[P6]**, sweep `d` and `k`.
8. Remedy experiment: noise on `y` **[P7]** + a comparison with noise on the interpolant.
9. EXP-2 (GMM, mode coverage).

**Stage C:**
10. EXP-3 (image inpainting, qualitative only).
11. Write the summary `RESULTS.md`.

---

## 11. Desired RESULTS.md format

```markdown
# Verification results

## Summary
[For each prediction P1-P7: MATCH / NO MATCH / PARTIAL, with a one-sentence explanation]

## P1 — Variance collapse
[Figure + numbers + comments]
...

## Surprises / departures from the theory
[This section is IMPORTANT: record every departure honestly]

## Details of the configurations that ran
[Table: config, seed, number of iterations, running time]
```

---

## 12. The most important point, once more

This is **theory verification**, not benchmark optimisation.

- If the variance does **not** collapse to 0 → that is an important finding; investigate why (not enough capacity? y not distinctive enough? optimisation not converged?) and report it.
- If the results match → still check carefully that it is not a bug (e.g. `y` leaking into the input in an unintended way, or a wrong ODE solver).
- **Do not edit numbers, do not pick favourable seeds.** Run several seeds (≥5) and report mean ± std.
