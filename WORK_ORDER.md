# Work Order — cfm-collapse

**Read `docs/THEORY.md` first.** This file assumes you have read it. Every reference of
the form "Prop 17", "Thm 10" points there.

**Non-negotiable rule:** this is a theory-verification project. Do not edit numbers, do
not pick favourable seeds, do not tune to force the desired result. If a number does not
match the theory, report it honestly: that is information, not a bug.

> **Status (2026-10-11).** T1-T9 are done; see `results/RESULTS.md` for what each task
> produced. This file is kept as the record of what was asked. Some of the numbers it
> quotes were later revised: in particular, the §0 table below was computed before the
> kernel module existed, and the values measured with `src/metrics/kernel_theory.py`
> (RESULTS.md, P7 section) replace it.

---

## 0. The most important finding (read carefully before doing anything)

Theorem 10 gives an **exact, finite-N reference with no free parameters**:

```
Cov_h(y) = Σ_j p_j^(h)(y) (x^j − x̄_h)(x^j − x̄_h)ᵀ,   p_j^(h)(y) ∝ K_h(y − y^j)
```

computed directly from the training set. I computed it on the data already in the repo
(`p7y_h*_seed0`, at 200k iterations, averaged over 20 conditioning points):

| h | `tr Cov_h` (Thm 10, exact) | measured | `tr Σ_post` | n_eff |
|------|------|------|------|------|
| 0.01 | 0.427 | 0.472 | 1.004 | 2.2 |
| 0.05 | 0.973 | 0.800 | 1.004 | 8.2 |
| 0.1  | **1.145** | **0.812** | 1.004 | 15.4 |
| 0.5  | 1.244 | 1.218 | 1.004 | 61.9 |

`n_eff = 1/Σ_j p_j²` = the number of training atoms that actually carry weight.

**Three consequences that must be reflected in RESULTS.md:**

1. **The claim "perfect restoration at h≈0.1" is wrong.** It rests on comparing with
   `tr Σ_post = 1.004`. But the right target for the model at `h=0.1` is
   `Cov_h = 1.145`, and the model reaches 0.812, i.e. only **71%** of the population
   optimum. There is no "perfect restoration"; a representation/optimisation gap
   remains. That it *happens* to cross `tr Σ_post` is a coincidence, not a success.

2. **The kernel theory predicts far better than the baseline.** At `h=0.01`
   (0.427 vs 0.472) and `h=0.5` (1.244 vs 1.218), Thm 10 matches while `Σ_post` is off
   by 2×. This is the strongest evidence in the whole project, stronger than the
   `rel.err` of the velocity field, because it tests the **endpoint law**, not only the
   velocity field.

3. **At `h=0.5` the variance exceeds `Σ_post`** (1.22 > 1.00), exactly as the
   `h²‖J‖²_F` term of Prop 15 predicts. `‖J‖²_F = 0.4031` (computed exactly from the
   saved `A`). The right branch of the U is over-smoothing, not noise.

Every task below is about exploiting this finding correctly.

---

## 1. Current state

### Achieved

**Theory** (since `docs/THEORY.md` exists; it did not before):
- The whole population theory is tight, with no dangling assumptions. `Lemma 3` proves
  well-posedness, so Prop 5 / Thm 10 no longer need "assume the flow is well defined".
- The unconditional contrast lemma is corrected (Cor 6): the unconditional model
  **also** memorises the whole empirical support; the difference lies in the
  conditional variance.
- New Prop 17: interpolant noise does **not** change the endpoint law for any σ; it has
  the closed-form solution `x_t = t x^i + s_t x₀`, verified symbolically.
- New Prop 14: `p_h^gen` is atomic for every h ⇒ a `W₂` lower bound independent of h.
- New Prop 15: the expansion `Cov_h = Σ + h²JJᵀ + …`, in closed form for EXP-1.
- Prop 20/Cor 21: a representation lower bound, with the algebra checked.

**Experiments** (already in the repo, reliable):
- EXP-1: P1/P2/P3/P4 match; the unconditional control is clear; the extended 1M-iteration
  run shows `trace(Cov)`, `vel_err`, `‖mean−x^i‖` and `loss` falling together,
  confirming that they are one phenomenon.
- The "correct Bayes" phase up to ~10⁴ iterations is measurable, which explains why
  early stopping works.
- P6 (N sweep): clearly monotone, 0.05 → 0.98.
- EXP-2 (GMM): mode coverage 1.00 → 0.72, MMD grows ~40×.
- EXP-3 (MNIST): pixel variance falls ~100×, distance to the nearest training image →
  0.0005.
- `sanity_checks.py`: residual 1.8e-15, no `y` leak. Keep it as is, run it in CI.

### Not yet achieved

| # | Problem | Severity |
|---|---|---|
| G1 | The P7 claim "perfect restoration" uses the wrong reference (see §0) | **High** |
| G2 | No metric compares with `Cov_h`; all of P7 compares with `Σ_post` | **High** |
| G3 | The stochastic-interpolant target is wrong (missing `γ̇(t)Z`) | **High** |
| G4 | The kernel verification results `(†)/(‡)` exist only as one PNG, with no numbers in RESULTS.md | **High** |
| G5 | `L(v_θ) − L(v_h⋆)` not yet measured (Question B) | Medium |
| G6 | No Lipschitz estimate yet ⇒ the representation and optimisation gaps cannot be separated | Medium |
| G7 | No Sinkhorn/MMD to the **true** posterior for EXP-1 yet (only for EXP-2) | Medium |
| G8 | The P5-P7 sweeps have only 2-3 seeds, and the tables have no error bars | Medium |
| G9 | P5 is described as "prediction failed", which is a logical error (see Part E) | Medium |
| G10 | §2.22 has no citation at all | Medium |
| G11 | EXP-3 has only 1 seed, N=500, no N sweep yet | Low |
| G12 | The extended run diverges near 1M iterations with a fixed LR | Low |

---

## 2. Tasks

Work **in order**. T1-T4 are the core; do not start T5+ before T1-T4 are done.

---

### T1 — Add the kernel theory module + the `Cov_h` metric  ⚠️ **highest priority**

**New file:** `src/metrics/kernel_theory.py`

Implement, using log-sum-exp throughout (small bandwidths overflow otherwise):

```python
def kernel_weights(y_q, Y, h):
    """p_j^(h)(y_q) ∝ K_h(y_q − y^j).  y_q:(k,), Y:(N,k) -> (N,)
    h == 0: point mass on argmin |y_q − y^j| (Corollary 11)."""

def kernel_moments(y_q, X, Y, h):
    """-> (x_bar, Cov, n_eff) per Prop 13. n_eff = 1/sum(p**2)."""

def kernel_field(x, t, y_q, X, Y, h, source_std=1.0):
    """v_h*(x,t,y_q) per Prop 8, eq (8.1).  x:(P,d), t:(P,) -> (P,d)"""

def cov_expansion(problem, h):
    """Prop 15 in closed form for the linear-Gaussian problem:
       tr Σ_post + h² ||J||_F²,  J = Σ_post Aᵀ / σ_obs².
       Returns (predicted_trace, J_fro_sq)."""
```

**Wire it into the eval loop** (`src/train.py`, where `trace_cov_mean` is computed). Add
columns to `raw/metrics.csv`:

```
trace_cov_kernel      # tr Cov_h(y^i) from Thm 10, exact
n_eff                 # effective number of atoms
ratio_to_kernel       # trace_cov_mean / trace_cov_kernel   <-- the new MAIN metric
mean_err_kernel       # ||mean(samples) − x̄_h(y^i)||
```

Keep `trace_post` and `ratio_to_post`, but **`ratio_to_kernel` is now the quantity that
measures how close the model gets to the population optimum.** `ratio_to_post` becomes a
secondary quantity.

**Acceptance:**
- Unit tests: as `h → 0`, `kernel_weights` converges to one-hot at the nearest label
  (Cor 11); as `h → ∞` it converges to `1/N` (Cor 12); `kernel_field(σ=0, h=0)` matches
  `closed_form_velocity` in `src/flows/interpolants.py` to `1e-6`.
- Re-run the eval on the existing checkpoints (no retraining needed) and **reproduce the
  table in §0 exactly**: 0.427 / 0.973 / 1.145 / 1.244. A deviation above 1% means a bug.
- `cov_expansion` returns `‖J‖²_F = 0.4031` for the default config `d=2,k=1,σ_obs=0.1`.

---

### T2 — Fix the stochastic-interpolant target + verify Prop 17

**File:** `src/flows/interpolants.py`

Current bug: when `sigma > 0`, `target` is still `x1 - x0`. It should be (C.2):

```
γ(t)  = σ·sqrt(t(1−t))
γ̇(t) = σ(1−2t) / (2·sqrt(t(1−t)))
target = x1 − x0 + γ̇(t)·Z          # the same Z used to build x_t
```

The **same** `Z` must be used for both `x_t` and the target. `γ̇` diverges as `t→0,1`
(integrably, of order `|t(1−t)|^{-1/2}`); clamp `t ∈ [ε, 1−ε]`, `ε = 1e-4`, and **add a
comment saying this is a deliberate treatment of the singularity**. Delete the docstring
passage justifying it as "close enough for qualitative comparison": it is not true.

**New file:** `scripts/verify_prop17.py`, closed-form checks, no network needed:

1. `s_t² = (1−t)² + σ²t(1−t)`; check `c(t) = ½·d/dt log s_t²` by finite differences.
2. Integrate the ODE `ẋ = x^i + c(t)(x − t x^i)` with RK4 from many `x₀`; check it
   matches `x_t = t x^i + s_t x₀` (Prop 17b) to `1e-6`.
3. Check the endpoint `x_{1−1e-3} → x^i` for `σ ∈ {0, 0.1, 0.3, 1.0}`: **invariant in
   σ**.
4. Check `(1−t)|c(t)| → 1` when `σ=0` and `→ ½` when `σ>0` (Cor 18).

**Acceptance:** all 4 checks pass. Re-run `p7i_sig{0.1,0.3}` with the corrected target,
3 seeds. **Prediction: the variance is still NOT restored** (Prop 17c). If the new
result is still ~0.4, that is a *confirmation of the theory*; report it as such, not as
a failure.

---

### T3 — Put the kernel verification numbers in the manuscript

**Files:** `scripts/verify_kernel_theory.py` (exists, extend it), `results/RESULTS.md`

The script currently writes only a PNG. Add:
- Write `results/exp1/_theory/raw/kernel_verification.csv` with the columns
  `h, rel_err_vs_kernel, rel_err_vs_star, tv_mixture, n_eff, seed`.
- Run it on **all** `p7y_h*` × all seeds, not only seed 0.
- Change the `§2.X` reference in the docstring to `docs/THEORY.md Prop 8 / Thm 10`.

**Acceptance:** RESULTS.md has a table of real numbers for `(†)` and `(‡)`, not only a
figure. Expected: `rel_err_vs_kernel < rel_err_vs_star` for every `h > 0`, with the gap
widening as `h` grows.

---

### T4 — Rewrite the claims in RESULTS.md

**File:** `results/RESULTS.md`

1. **P7 section**: rewrite according to §0. The new table must have a `Cov_h` (Thm 10)
   column next to `Σ_post` and the measured value. Drop the words "perfect
   restoration". Replace them with: the model reaches 71% of the population optimum at
   `h=0.1`; the rest is a representation/optimisation gap.

2. **Add the atomicity caveat** (Prop 14) to the P7 section:
   > Label smoothing redistributes weight over the training points; it does not generate
   > new samples. `p_h^gen` is atomic for every `h`, while the true posterior is
   > continuous: Prop 14 gives a `W₂` lower bound **independent of h**. Matching the
   > covariance trace matches a second moment, not the posterior. `n_eff` (the §0 table)
   > shows that even at `h=0.5` only ~62/200 atoms carry weight.

3. **P5 section**: drop the label "does NOT match". Use the exact wording of Part E:
   > The population theory does not determine how the collapse depends on `σ_obs`; the
   > flat result observed is an empirical finding. It is consistent with the
   > identification-through-`y` mechanism, which holds for every `σ_obs > 0`.

4. **P6 section**: use the Part E wording: the population optimum still collapses for
   every finite N; that `N=5000` does not collapse shows the gap between the exact
   solution and the representation/optimisation regime, and does **not** refute Prop 4.

5. **P4 section**: fix the interpretation. The unconditional model **does** memorise
   (Cor 6); `trace(Cov) ≈ trace(Cov data)` is exactly (6.1), not evidence of "no
   memorisation".

**Acceptance:** nothing in RESULTS.md calls a quantity on the "not determined" list
(Part E) a "theoretical prediction" that "matched" or "did not match".

---

### T5 — Measure the distance to the population optimum (Question B)

**New file:** `scripts/measure_optimality_gap.py`

For each checkpoint, estimate by Monte Carlo on the same batch:

```
L(v_θ)                                  # the empirical loss
L(v_h*)   = E[Var(U | X_t,t,Ỹ)]         # computed with kernel_field, = 0 when h=0
gap       = L(v_θ) − L(v_h*)
```

At `h=0`, `L(v_h*) = 0` (Prop 4b), so `gap = L(v_θ)`, the quantity already logged. The
new values are at `h > 0`.

**Acceptance:** `gap ≥ 0` at every checkpoint (negative ⇒ bug). Plot `gap` against
iteration for each `h`, next to `ratio_to_kernel`.

---

### T6 — Estimate the Lipschitz constant, separate representation from optimisation

**New file:** `scripts/estimate_lipschitz.py`

Two estimates, report both:
- **Lower bound (empirical):** power iteration on `∂v_θ/∂x` at `(x,t)` sampled on the
  manifold, sweeping `t ∈ {0.5, 0.9, 0.99, 0.999}`. Report `L(t)`, not only `max_t`.
- **Upper bound (crude):** the product of the spectral norms of the linear layers.

Compare `d/(3L)` (Cor 21) with the measured `L_trained`.

**Acceptance:** a table `t | L(t) | d/(3L(t)) | L_trained`. The **expected** result is
`d/(3L) ≪ L_trained` ⇒ conclusion: the plateau is mainly an **optimisation gap**, not a
representation gap. This is a clean and valuable conclusion; report it plainly even if it
makes Cor 21 non-binding. State clearly in RESULTS.md that Cor 21 is a lower bound, and
that a non-binding lower bound does not mean the theory is wrong.

---

### T7 — Add a distance-to-the-true-posterior metric for EXP-1

**File:** `src/metrics/distances.py` (already has Sinkhorn/MMD for EXP-2; reuse it)

EXP-1 has the analytic posterior `N(μ_post(y), Σ_post)`, so ground-truth samples can be
drawn directly. Add `sinkhorn_to_true_posterior` and `mmd_to_true_posterior` to the
EXP-1 eval loop.

**Acceptance:** report them with the covariance trace in the P7 section. Expected from
Prop 14: this distance does **not** go to 0 at any `h`, including the `h` that is
optimal for the covariance trace. This is a direct check of the atomicity lower bound,
and evidence that "restoring the variance" ≠ "restoring the posterior".

---

### T8 — Seeds and error bars

**Files:** `scripts/run_sweeps.py`, `scripts/analyze_sweeps.py`

Raise every P5, P6, P7y, P7i and d/k sweep to **5 seeds**. Every table in RESULTS.md
reports `mean ± std`. For P5, also test: does the difference between `σ_obs` values
exceed the seed-to-seed variation? (With `std ≈ 0.13` on `mean ≈ 0.40`, most likely
**not**, and that needs to be said.)

**Acceptance:** no table in RESULTS.md lacks error bars.

---

### T9 — Citations

**Files:** `docs/THEORY.md` §Positioning, `results/RESULTS.md`

Add real citations for the memorisation literature: Pidstrigach (2022); Gu et al., *On
Memorization in Diffusion Models*; Kadkhodaie et al. (2024); Biroli & Mézard; Kamb &
Ganguli. State clearly that the original contribution is the 5 points at the end of
`docs/THEORY.md`, **not** the observation "the empirical minimiser memorises" itself.

---

### T10 — Optional, do last

- **T10a:** re-run the extended EXP-1 with cosine LR decay to reach a deeper collapse
  without diverging. Compare the final `ratio_to_kernel` with 0.
- **T10b:** held-out `y`: report the **median + the number of diverging cases**, not the
  mean (the mean is dominated by blow-ups: 6e4 ± 1.2e5 is meaningless).
- **T10c:** EXP-3: more seeds, sweep `N ∈ {500, 5000}`.
- **T10d:** add `n_eff` to EXP-2/EXP-3 to connect mode coverage with the kernel theory.

---

## 3. Technical notes

- **Numerical stability:** every kernel computation must use log-sum-exp. With `h=0.01`
  and `k=1`, the ratio of `K_h` between atoms easily exceeds `1e300`.
- **`h=0` in `kernel_weights`:** do not divide by 0; use the point-mass branch at the
  nearest label (Cor 11).
- **The `t=1` singularity:** keep the existing convention (`t_max=0.95` for the velocity
  error, stop the ODE at `1−1e-3`). Comment that it is deliberate.
- **Do not retrain unless needed:** T1, T3, T5 and T6 all run on the existing
  checkpoints. Only T2 (the new target) and T8 (more seeds) need training.
- **Reproducibility:** keep the convention of fixing the seed + saving `config.yaml` +
  `problem.json` for every run.

---

## 4. Definition of "done"

1. `docs/THEORY.md` is in the repo, every statement has a proof, no "assume" remains.
2. `ratio_to_kernel` is the main metric in every P7 table; `ratio_to_post` is secondary.
3. The §0 table is reproducible with code in the repo (error <1%).
4. The stochastic-interpolant target is fixed; `verify_prop17.py` passes; P7i is re-run
   and reported as a **confirmation** of Prop 17c.
5. No claim in RESULTS.md violates the wording rule of Part E.
6. Every table has `mean ± std` over ≥5 seeds.
7. The memorisation literature is cited.
