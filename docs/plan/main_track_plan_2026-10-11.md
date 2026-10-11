# From workshop to main track: what to prove and what to run (2026-10-11)

Built on the round-5 and round-6 simulated reviews
(`docs/review/simulated_review_round5_2026-10-10.md`,
`docs/review/simulated_review_round6_2026-10-11.md`) and the paper at `a1da1ae`.

## 1. Where the paper stands

**What reviewers accept.**
- The population theory is correct.
- The h_eff law reproduces in d=2: 48/48 checkpoints, 31/36 on CIFAR-10, reproducible
  across GPU runs.
- The verification apparatus is exemplary: 245 asserted numbers.

**What blocks a main-track accept** (round 6: four of five reviewers at Major, mean ICLR
reading 5.5):

1. **Novelty of the theory.** The endpoint law is a conditional transcription of known
   finite-support closed forms. The results specific to this paper are elementary:
   - Prop. `heffid` is a triangle inequality and the mean-value theorem;
   - Thm. `calib`(b) is Pinsker;
   - (c) is a Gaussian computation.

   R2: "the paper's novelty therefore rests on the empirical law".
2. **The theory does not describe the trained network.** It describes the population
   minimiser. Why a trained network sits at an effective bandwidth, why h_eff falls, and
   why it stops at 1.08h–1.34h are measured, not explained. The spectral-bias model of
   App. `specbias` reproduces the fall but not the rate, the floor or the additive
   exponent.
3. **DA's alternative.** h_eff might be optimisation progress re-expressed. At image
   scale it ranks coverage worse than the raw sample spread (0.63 against 0.98).

**Venue arithmetic.**
- The ICLR 2027 main-track deadline (25 Sep 2026) has passed.
- ICML 2027 is estimated at about 22 Jan 2027, not yet announced; verify on icml.cc.
  That leaves about 14 weeks.
- The current version fits an ICLR 2027 workshop (deadlines usually in February).
  Check the ICML dual-submission policy: non-archival workshops are normally allowed.

**Recommendation.** Make one theorem about *trained* models the paper's headline and test
its new predictions. A main-track paper needs a non-trivial result that explains the
h_eff law and predicts something not yet measured. The population results become the
reference that makes h_eff definable (round-5 arbitration). Do not add more
population-minimiser propositions: reviewers already read those as known.

---

## 2. What to prove

Ordered by how much each moves the review. Statements are drafts: assumptions and
constants to be fixed in the proof.

### T1 (headline): spectral bias in the label space is a Nadaraya–Watson smoother at a local, shrinking bandwidth

**Setting.** The paper's kernel-gradient-flow model, eq. `kgf`: the label dependence of
the conditional moments f(y) = E[φ(X) | Ỹ = y] is learned by gradient flow (or ridge) in
L²(ρ_h), with a translation-invariant kernel whose spectrum decays as a|ω|^{-ζ}. Start
with k=1, which is exactly EXP-1, and ζ = 2m (Sobolev order m). The label density ρ_h is
C² and bounded below on the evaluation set.

**Claims.** With b(t, y) := (a t ρ_h(y))^{-1/ζ}:

- **(a) Equivalent kernel.** f(y) = ∫ κ_{b(y)}(y−u) f⋆(u) du + R, with
  |R| ≤ C(b|∂ log ρ_h| + b²)‖f⋆‖_{C²}. The filter κ depends on the form of
  regularisation:
  - *Ridge form* (penalty λ): transfer 1/(1+(bω)^ζ) with b = (λ/(aρ_h))^{1/ζ}. κ is a
    positive kernel, Laplace for ζ=2.
  - *Gradient-flow form* at time t: transfer 1 − exp(−(bω)^{−ζ}) with
    b = (a t ρ_h)^{−1/ζ}. This transfer is flat at ω=0, so κ is a *signed* low-pass
    filter at scale b whose moments all vanish.
- **(b) One bandwidth to leading order.** f⋆ is the NW moment at h.
  - In the ridge form, the learned moments are those of an NW mixture over the training
    atoms with the positive kernel K_h ⋆ κ_b, up to R. Its second-moment bandwidth is
    h_eff² = h² + μ₂(κ) b².
  - In the gradient-flow form, the fitted Gaussian bandwidth of eq. `heff` is
    h_eff = Φ(h, b), increasing in b, with Φ(h, 0) = h. Positivity of the implied weights
    is not automatic and has to be shown, or bounded, along the trajectory.

  This is the statement behind "a trained network follows the mixture at one bandwidth",
  and the paper has it only empirically (median R² 0.97 in the KGF model).
- **(c) Fall and floor.**
  - Under gradient flow with no regularisation, b → 0 as t^{-1/ζ} and h_eff → h. This
    generalises Prop. `specbias`(a), currently h=0 only.
  - With weight decay λ (in the lazy regime, gradient flow on the penalised loss), the
    flow converges to the ridge form, b_∞(y) = (λ / (a ρ_h(y)))^{1/ζ}, so
    h_eff,∞² = h² + μ₂ b_∞² > h², a floor.
  - Early stopping at time t matches λ ≍ 1/t in risk, not in kernel shape.
- **(d) Locality.** The resolution scale b(y) ∝ ρ_h(y)^{-1/ζ}, so sparse label regions are
  smoothed more. In the ridge form, h_eff² − h² ∝ ρ_h(y)^{-2/ζ}.

**The technical crux.** (b) for the gradient-flow form, i.e. the positivity of the implied
weights. If it fails, the clean theorem is the ridge form, which is the weight-decay
experiment E2a. The gradient-flow form is then stated for the resolution scale b alone.

**Why it matters.**
- It turns contribution 2 from a measurement into a theorem with three new, falsifiable
  predictions: the t^{-1/ζ} rate, a floor that depends on the regulariser, and density
  dependence.
- It answers DA's alternative. h_eff becomes a predicted function of (t, λ, ρ, ζ, h),
  not of the iteration alone, and (c) and (d) vary h_eff *at fixed iteration*.
- It explains why the Laplace reference is a close second in Table `tab:families`: the
  equivalent kernel for ζ=2 is Laplace.

**Proof route.**
- Early stopping as a spectral filter, and its equivalence to ridge: Yao, Rosasco &
  Caponnetto (2007); Gerfo et al. (2008); Ali, Kolter & Tibshirani (2019).
- The equivalent kernel of penalised regression with local bandwidth ∝ (λ/ρ)^{1/(2m)}:
  Silverman (1984), *Spline smoothing: the equivalent variable kernel method*; Messer
  (1991); Nychka (1995), *Splines as local smoothers*.
- The uniform-density case is exact by Fourier analysis (Prop. `specbias`(b) already).
- The non-uniform case is the Silverman/Nychka argument with f⋆ in place of noisy
  responses. Here it is simpler: the target is known and there is no response noise.

**Risk.** The networks need not be in the lazy regime. T1 is then a theorem about a model
of the learner, and E1–E3 decide how far the networks follow it. That is still a standard,
publishable shape ("a solvable model whose predictions the networks follow"), provided at
least one of the new predictions holds.

**Already known, so not a discriminating test.** The additive exponent: the KGF model
gives p ≈ 2.2 (Laplace) against 1.3 for the networks, and the network data hardly
distinguish the two (App. `specbias`).

### T2: finite-sample calibration of the reference law, and a stopping guarantee

**Statement (draft).** For i.i.d. data with Y = g(X)+η, σ>0, and a region rule built from
the NW mixture's conditional CDF of a fixed statistic s(X), with probability ≥ 1−δ over
the training set:

|coverage − α| ≤ τ_h + C₁·L·h² + C₂·√(log(1/δ) / (N h^k ρ_min)) + 1/(2 n_eff).

Here τ_h ≤ √(k/8) h²/σ² is part (b), the second term is the NW bias for an L-Lipschitz
(in y) conditional CDF, the third is the NW variance, and the last is the discreteness of
part (d).

**Consequences.**
- An explicit calibration window [h_min(N), h_max(σ, k)].
- With T1(c), a window *in training time*. The paper locates it only empirically, and
  only with the posterior (App. `calibdetails`, stopping rules).
- In inverse problems, (x, y) pairs can be simulated from the prior and the forward
  model. A checkpoint chosen by held-out PIT error is then within O(√(log J / m)) of the
  best of J checkpoints, using m simulated pairs, and T1 says where that checkpoint is.
  This is the posterior-free use R3 asked for.

**Proof route.** Uniform rates for NW conditional distribution functions: Hall, Wolff &
Yao (1999); Einmahl & Mason (2005). Quantile coverage from CDF error is standard; the
selection bound is a hold-out argument. Moderate difficulty; the novelty is in the
combination with T1, not in the components.

### T3 (optional, after E5): a two-bandwidth law at image scale

**Conjecture.** A field with label resolution b and an error in the spatial factor ends
near ∑_i p_i^{(h_eff)}(y) N(x^i, ρ_eff² I). Its trace is tr Cov_{h_eff} + d ρ_eff², and
ρ_eff relative to the nearest-atom spacing sets the off-atom fraction.

This would join Prop. `filtered` (label resolution alone keeps the atoms) to the observed
17–38% off-atom samples. Test E5 first: if the endpoint-smoothed family does not fit
CIFAR-10 better than the Gaussian, drop T3.

### Not worth the effort for the main track
- More population-minimiser results (CFG, interpolant noise, survival refinements). Keep
  them in the appendix.
- Deeper atomicity-floor theory: the floor does not bind for trained models.
- Sharpening Prop. `heffid`: it is a tool, not a contribution.

---

## 3. Experiments (each tests a T1/T2 prediction; one factor at a time)

The baseline throughout is the paper's `heff_p7y_h{h}_seed{s}`: the EXP-1 problem (d=2,
k=1, N=200, σ_obs=0.1), the 4×128 SiLU MLP, Adam at constant lr 1e-3, no weight decay,
batch 256, 2×10⁵ iterations, checkpoints at 100…2×10⁵, seeds 0–2. These 15 runs exist, with
weights on the server and in the base checkout.

| ID | Tests | Factor | Levels | Fixed | Prediction (stated before running) | Falsified if |
|---|---|---|---|---|---|---|
| E3 | T1 assumption | empirical NTK of v_θ in the label input | init, 10⁴, 2×10⁵ iterations; 256-label grid; 64 (x,t) draws | baseline runs | eigen-decay ≈ polynomial with exponent ζ̂; kernel roughly stable after 10⁴ (lazy enough) | decay exponential (T1 predicts no fall, as for the Gaussian KGF), or kernel changes by >50% in Frobenius norm |
| E1 | T1(d) | label density at the condition | 60 conditions at label quantiles 1–99%, M=1000 | baseline checkpoints ≥10⁴ | at h=0, per-condition log h_eff falls with log ρ̂(y) at slope −1/ζ̂ (the resolution scale b); at h>0, log(h_eff² − h²) at −2/ζ̂ in the ridge form | slope 95% CI contains 0 for h=0 in ≥2 of 3 seeds |
| E2a | T1(c) | weight decay (AdamW) | 0 (baseline), 1e-4, 1e-3, 1e-2 | h∈{0, 0.05}, 3 seeds | final h_eff rises with wd as (h² + c·wd^{2/ζ̂})^{1/2} | h_eff at 2×10⁵ independent of wd (overlapping CIs at all levels) |
| E2b | T1(c), implicit regularisation | constant lr | 3e-4, 1e-3 (baseline), 3e-3 | same | larger lr → higher floor | no monotone trend |
| E2c | T1(c) | schedule | constant (baseline), cosine 1e-3 → 1e-6 | same | cosine ends closer to h than constant | cosine floor ≥ constant floor |
| E6 | DA's alternative | arm of E2 at a fixed iteration | E2 arms at 3×10⁴, 10⁵, 2×10⁵ | 100 held-out pairs per checkpoint | at fixed iteration, held-out coverage follows Thm. `calib`(d) at each arm's h_eff | coverage tracks iteration, not h_eff, across arms |
| E5 | T3 and families at image scale | reference family | Gaussian, Laplace, Cauchy, kNN, endpoint-smoothed (h, ρ) | 12 CIFAR re-runs × 7 checkpoints, per-condition traces already saved | ρ̂ > 0 at CIFAR (unlike synthetic), and ρ̂ relates to the off-atom fraction | endpoint-smoothed no better than Gaussian by leave-one-condition-out error |
| E7 | breadth (R3) | second image dataset | MNIST DDPM h_eff runs (`configs/exp3_mnist_ddpm_heff.yaml`), h∈{0, h_mid, h_hi}, 3 seeds | CIFAR protocol | the 31/36-type agreement and h_eff ↓ h replicate | no agreement between h_eff and h_mean |

E4 (the additive exponent) is dropped: it is already computed and does not discriminate
(§2, T1). The pending CIFAR h=0/h=6 re-runs, the rebuilt seed table and the multi-level
and PCA calibration (round-6 R3, S6) finish today and are not repeated here.

### Analysis plan (fixed before running)

- **E1.**
  - Per condition: fit h_mean(y_c) on the grid of eq. `heff` restricted to that condition,
    and h_var(y_c) from its trace where tr Cov_h is locally monotone.
  - ρ̂: a KDE of the training labels.
  - Regress log h_eff (h=0) and log(h_eff² − h²) (h>0) on log ρ̂: OLS per checkpoint,
    bootstrap CI over conditions,
    and a pooled fit with a run random effect.
  - Compare the slopes with −1/ζ̂ and −2/ζ̂ from E3.
- **E2.**
  - h_eff and h_mean at every checkpoint, with `scripts/test_heff_synthetic.py --glob`.
  - The floor is h_eff at 2×10⁵. Plot it against wd on log-log axes (slope against
    2/ζ̂ after subtracting h²).
  - Paired by seed against the baseline: bootstrap over seeds and conditions.
  - AdamW's decoupled decay pulls the parameters towards 0, not towards their
    initialisation, so it is not exactly the ridge penalty of T1(c). The test is
    therefore the sign of the effect and the order of the slope, not its value. A
    plain-SGD arm with L2 decay (`train.optimizer=sgd`, `train.weight_decay`) is the
    cleaner match if Adam's results are ambiguous.
- **E6.** Coverage measured as in App. `calibdetails` (`scripts/audit_calibration_v2.py`).
  Spearman of coverage against h_eff within each iteration slice, against iteration
  within each arm, and the Thm. `calib`(d) prediction R² per slice.
- **E5.** `scripts/heff_family_test.py`, fit stage, variance only (CIFAR means are not
  saved): log-space R², leave-one-condition-out error, ρ̂ with bootstrap CI, and the
  Spearman of dρ̂²/tr against the on-atom fraction.
- **Failed runs.** Rerun once with the same seed. If a run fails twice, report it and
  exclude it, never silently. NaN traces (diverged ODE) are counted, as in App. `heldout`.
- **Figures.**
  - E1: log(h_eff² − h²) against log ρ̂, one panel per h.
  - E2: the floor against wd, lr and schedule.
  - E6: coverage against h_eff, coloured by iteration.
  - E5: the family table at image scale.

---

## 4. Resources

| Item | Unit cost | Count | Total | Where |
|---|---|---|---|---|
| E2 training (MLP, 2×10⁵ it.) | ~20 min CPU at 4 threads (EXP-1: 807–1153 s) | 36 runs | ~12 CPU-h → ~2 h wall at 8 workers | server CPU, `CUDA_VISIBLE_DEVICES=` so the GPU queue is untouched |
| E2 h_eff analysis | ~1 min per run | 36 | <1 h | server CPU |
| E1 resampling | 60 cond. × M=1000 × 100 RK4 steps per checkpoint | 15 runs × 5 ckpts | <1 h | server CPU |
| E3 empirical NTK | Jacobians of a 70k-parameter MLP on 256 labels × 64 (x,t) | 15 runs × 3 ckpts | minutes | server CPU |
| E6 coverage | 100 held-out pairs per checkpoint | ~36 runs × 3 ckpts | ~1–2 h | server CPU |
| E5 references | N=2000, k=1536, 48 conditions, grid of 240 | 12 runs | <1 h | server CPU (torch only to rebuild the subset) |
| E7 MNIST DDPM | to measure (smaller than CIFAR's 2.5 h) | 9 runs | ≲ 15 GPU-h → ~8 h wall on 2 L40 | server GPU, after the current queue |
| Storage | MLP checkpoints ~1 MB; MNIST 7 checkpoints per run | — | <10 GB | server (397 GB free on the shared disk) |

Total: about 20 CPU-hours and 15 GPU-hours. Everything synthetic fits on the server CPU
alongside the running GPU queue. No API costs.

---

## 5. Execution

**Code prepared** (`a1da1ae`+; nothing launched):
- `train.weight_decay` (AdamW when >0; 0 keeps plain Adam, so existing runs are unchanged);
- the `floor` group in `scripts/run_sweeps.py` (36 runs: E2a–c);
- `--glob/--out` for `scripts/test_heff_synthetic.py`.

```bash
# on the server, after copying src/train.py, scripts/run_sweeps.py and
# scripts/test_heff_synthetic.py; CPU only, so the GPU queue keeps its speed
cd ~/cfm-collapse && source ~/clic/venv/bin/activate
export PYTHONPATH=. CFM_PYTHON_CMD=python CUDA_VISIBLE_DEVICES=
python scripts/run_sweeps.py --only floor --dry-run
tmux new-session -d -s cfm_floor \
  "python scripts/run_sweeps.py --only floor --workers 8 --threads 4 --iters 200000 2>&1 | tee logs/floor.log"
# afterwards
python scripts/test_heff_synthetic.py --glob "heff_floor_*" --out results/exp1/_heff/heff_floor.json
```

**Still to write** (small):
- `scripts/heff_local_density.py` (E1: per-condition bandwidths at label quantiles);
- `scripts/ntk_label_spectrum.py` (E3);
- a CIFAR stage for `heff_family_test.py` (E5) that reads `results/exp3/_rerun/heff_*.json`
  traces and rebuilds the references on the server.

**Order and gates.**
1. **Week 1:** E3 and E1 (existing checkpoints), and E2 launched in parallel on CPU.
   - **Gate G1.** If the label-space NTK decays exponentially or changes strongly in
     training, T1 is presented as a model of the learner. Weight the paper towards E1/E2
     as tests of it.
2. **Week 2:** E2 and E6 analysis, E5.
   - **Gate G2.** No wd/lr dependence of the floor means T1(c) is false for the networks:
     report it, and keep (a), (b) and (d).
   - **Gate G3.** No density dependence in E1 means T1(d) is false: keep the global law.
3. **Weeks 3–8:** proofs of T1 (k=1, ζ=2m first) and T2; E7 on the GPUs.
4. **Weeks 9–12:** rewrite around T1.
   - Contributions: (1) the h_eff law and T1; (2) calibration, Thm. `calib` + T2;
     (3) the audit, moved into the main text.
   - The endpoint law and atomicity compressed to about one page.
   - Interventions to the appendix.
   - ICML's main-text limit (8 pages in recent years; verify) forces this anyway.
5. **Weeks 13–14:** two internal review rounds (rounds 7–8 with this reviewer setup),
   then submit.

**Fallbacks.**
- If T1's proof slips: submit the current version to an ICLR 2027 workshop, and the
  T1 version to NeurIPS 2027 (May).
- If G1–G3 all fail: the paper is an empirical "science of DL" paper. It then needs E7
  plus a third dataset or a latent-space model to be competitive.

---

## 6. Proof notes after a pilot (2026-10-11)

`scripts/theory_t1_equivalent_kernel.py` (numpy; output in
`results/theory/t1_equivalent_kernel.json`) runs T1's learner, kernel ridge regression of
the atoms' moments started from the unconditional moments c, on the three real EXP-1
designs at h=0. It also computes the continuum equivalent kernels. T1 splits into five
lemmas of very different status.

| Lemma | Statement | Pilot | Status |
|---|---|---|---|
| L1 positivity | k=1, exponential kernel e^{-\|y-y'\|/ℓ}, ridge λ>0: the implied atom weights are ≥0 and sum to 1, at every query and every λ | min weight > 0 on all 3 designs and all λ (1e-2 to 1e-6), queries outside the data included; Gaussian kernel for contrast: 8%–370% negative mass | **provable now** (proof below); likely a k=1 phenomenon |
| L2 equivalent kernel, smoothing regime | for n_eff ≫ 1, the learned moments are NW at one bandwidth, with local scale (λ/(a p(y)))^{1/ζ} | one-bandwidth log-space R² 0.75–0.80 at n_eff≈10; density slope −0.45, −0.60, −0.63 against −0.50 | **known theory**: Silverman (1984); Sollich & Williams (NeurIPS 2004), *Using the equivalent kernel to understand Gaussian process regression*. Cite rather than claim |
| L3 collapse regime | for n_eff ≲ 4, still NW at one bandwidth | **fails in the model**: R² 0.35–0.51 at n_eff≈3.7, negative at n_eff≈2; density slope erratic | **open, and the real target**: the trained networks at h=0 still fit NW with median R² 0.82 there (Table `tab:families`), so the networks are *more* Nadaraya–Watson than the kernel model in the regime that matters |
| L4 floor | weight decay λ gives h_eff,∞ > h, scaling as λ^{1/ζ} | follows from L2 | easy given L2; E2a tests it on networks |
| L5 gradient-flow form | the early-stopped learner is a positive smoother | continuum gradient-flow filter is signed (5% negative mass at ζ=2, 11% at ζ=4); ridge kernels are positive exactly for ζ ≤ 2 (Linnik), signed for ζ=3, 4 (3%, 6%) | state for the resolution scale only, or work with weight decay (ridge form) |

**Proof of L1** (k=1, exponential kernel). The RKHS of e^{-|y-y'|/ℓ} is H¹(ℝ), with
norm ∝ ∫(ℓ²f'² + f²).

1. The minimiser of (1/N)∑(f(y^i)−z_i)² + λ‖f‖² solves a second-order equation
   (−ℓ²∂² + 1)f ∝ ∑_i c_i (z_i − f(y^i)) δ_{y^i}, with c_i > 0.
2. The weight of atom j is g_j = ∂f/∂z_j. It solves (L + V) g_j = c_j δ_{y^j}, with
   L = −ℓ²∂² + 1 and V = ∑_i c_i δ_{y^i} ≥ 0 a point potential.
3. The Green's function of L + V is positive for every nonnegative V (maximum principle;
   Feynman–Kac in 1-D, where points have positive capacity). So g_j > 0.
4. The weight left to c is 1 − ∑_j g_j. With z ≡ 1, (L+V)(1 − f₁) = 1 ≥ 0, so
   1 − f₁ ≥ 0 by the same positivity.

Hence the weights w = g + (1−∑g)/N are a probability vector. In k ≥ 2 the RKHS must have
order > k/2. Its operator is then of order ≥ 4 and has no maximum principle, so expect
signed weights there, as for the Gaussian kernel. This matters for CIFAR-10 (k=1536):
positivity, hence atomic moments, is not automatic for a kernel learner.

**What this changes in §2.**
- T1(a), (b) and (c) in the smoothing regime are known equivalent-kernel theory applied
  to the conditional moments. They make a short proposition plus L1, not a headline.
- The main-track theorem has to be about the **collapse regime** (L3), where the label
  resolution is comparable to the spacing of the training labels. That is where the
  networks still behave like a one-bandwidth NW mixture and the kernel model does not.
- Two candidate mechanisms, both testable before proving anything:
  1. **The flow re-concentrates label-filtered weights.** Prop. `filtered` and the
     halved variance at s ≫ h in App. `specbias` show this happens. A theorem for the
     endpoint weights of a label-filtered field, e.g. that they are a tempered version of
     q, would be new.
  2. **Feature learning in the label input.** The SiLU network's NTK in y is smooth, so
     its spectrum decays faster than any power. The Gaussian kernel model predicts that
     h_eff never reaches h (App. `specbias`), and the networks contradict this.
- **E3 decides between them and should run first.** Is the label-space NTK stable during
  training, and is its spectrum polynomial?

**Literature to check before claiming L1.** Positivity of first-order L-spline and
Ornstein–Uhlenbeck GP smoothers; the total positivity of the exponential kernel is
classical (Karlin, *Total Positivity*, 1968).
