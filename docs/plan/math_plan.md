# Mathematical plan: theorems behind the effective bandwidth

Goal: an ICLR / NeurIPS paper whose central claims are theorems, with experiments as
checks of their predictions. Status 2026-10-02: the population theory (collapse,
Nadaraya-Watson endpoint law, atomicity) is proved; the effective bandwidth h_eff and
the calibration window are empirical. This plan adds the missing theory.

GPU work on Kaggle is paused (long run, MNIST): it widens the experiments but does not
supply theorems. Everything below runs on CPU from data already in the repository.

---

## Notation

Training set (x^i, y^i), i = 1..N. Label distances D_i(y) = |y - y^i|^2. Kernel weights
p_i(h; y) = exp(-D_i / 2h^2) / Z. Weighted moments: E_p, Cov_p. Reference mean
xbar_h(y) = E_p[x], reference covariance Cov_h(y), trace T_h(y) = tr Cov_h(y),
n_eff(h; y) = 1 / sum_i p_i^2. For conditions y_1..y_C: F(h) = (log T_h(y_c))_c and
G(h) = (xbar_h(y_c))_c.

---

## T1. Identifiability and stability of the effective bandwidth

**T1.a Derivative identities (exact).**
  d/dh log p_i = (D_i - Dbar) / h^3, Dbar = E_p[D]
  d/dh xbar_h  = Cov_p(x, D) / h^3
  d/dh T_h     = Cov_p(|x - xbar_h|^2, D) / h^3
The reference variance grows with h exactly when, under the kernel weights, atoms far
in label space are far from the weighted mean in data space.

**T1.b Stability of the least-squares estimator (exact).** If the measured log traces
are F(h*) + e and hhat minimises |log T - F(h)| over an interval I containing h*, and
some unit vector u has u . F'(h) >= kappa > 0 on I, then |hhat - h*| <= 2|e| / kappa.
Same for the mean-based estimator with G. Hence the two estimators can disagree by at
most 2|e|/kappa_F + 2|e'|/kappa_G if the model is a Nadaraya-Watson mixture at one
bandwidth: a disagreement beyond that bound falsifies the single-bandwidth account.

**T1.c Large-bandwidth degeneracy (asymptotic).** As h -> infinity,
d/dh T_h = c_inf(y) / h^3 + O(h^-5) with c_inf(y) = Cov_unif(|x - xbar|^2, D(y)), so
kappa(h) = O(h^-3) and the error of hhat grows like h^3: h_eff is identified only
where the reference still varies. In log space small h is well identified.

**Checks (scripts/theory_t1_check.py).** Finite differences against T1.a on EXP-1 and
CIFAR-10 training sets; kappa(h) on both; predicted interval width 2*sd(e)*sqrt(C)/kappa
against the bootstrap interval widths already measured (heff_synthetic.json, CIFAR
JSONs); explain the poor identification at h = 0.5 (synthetic) and h = 6 (CIFAR-10).

---

## T3. Calibration of the reference law as a function of bandwidth (linear-Gaussian)

Prior x ~ N(0, s^2 I_d), y = A x + eta, eta ~ N(0, sigma^2 I_k).

**T3.a Infinite-data reference law (exact).** For fixed h and N -> infinity, the
Nadaraya-Watson mixture at bandwidth h converges weakly to the posterior of x given a
label observed with noise variance sigma^2 + h^2:
  mu_h(y) = Sigma_h A^T y / (sigma^2 + h^2),  Sigma_h = (I/s^2 + A^T A/(sigma^2+h^2))^-1.

**T3.b Calibration of the smoothed posterior (exact).** For (x*, y*) from the model,
x* - mu_h(y*) ~ N(0, V_h) with V_h = Sigma_post + B_h Cov(y) B_h^T, where
B_h = Sigma_post A^T / sigma^2 - Sigma_h A^T / (sigma^2 + h^2) and
Cov(y) = s^2 A A^T + sigma^2 I. The coverage of the level-alpha Mahalanobis region of
N(mu_h, Sigma_h) is P[z^T Sigma_h^-1 z <= q_alpha], z ~ N(0, V_h): a generalised
chi-square determined by the eigenvalues of Sigma_h^-1/2 V_h Sigma_h^-1/2. It equals
alpha at h = 0 and exceeds alpha for h > 0 (over-coverage branch).

**T3.c Finite effective sample (exact identity + model).** For weights w with
sum w = 1 and atoms drawn i.i.d. from a law with mean m and covariance S:
E[weighted covariance] = (1 - sum w^2) S = (1 - 1/n_eff) S and
Cov(weighted mean) = S / n_eff. Under the local model (atoms near y are draws of the
smoothed posterior), coverage(h, n_eff) = P[z^T ((1 - 1/n_eff) Sigma_h)^-1 z <= q_alpha],
z ~ N(0, V_h + Sigma_h / n_eff). It tends to 0 as n_eff -> 1 (collapse branch) and to
T3.b as n_eff -> infinity.

**T3.d Prediction for trained models.** Plug the trained model's h_eff and the n_eff it
implies at the held-out conditions into T3.c; compare with the measured held-out
coverage at the 75 synthetic checkpoints (audit_calibration_v2.json). Also compute the
exact coverage of the finite-N reference law at h_eff (sampling the mixture) as the
intermediate between theory and model.

**Checks (scripts/theory_t3_coverage.py).** Closed form vs Monte Carlo of the
smoothed posterior; T3.c identity by simulation; predicted vs measured coverage
(R^2, MAE, Spearman), figure.

---

## T2 (stretch). Where h_eff comes from

A model whose dependence on the label is resolved only to a scale s gives
h_eff^2 = h^2 + s^2 exactly when the extra smoothing is Gaussian noise on the label;
the data fit p ~ 1.35 instead of 2. Attempt only after T1 and T3: a toy gradient-flow
model (Gaussian random features in y) to see whether spectral bias yields a decreasing
s(t). Drop if it does not match the synthetic s(t) within a factor.

---

## Writing

- Main text: T1.a-b as one proposition with a corollary (T1.c) in section 4.3;
  T3 as a theorem in section 4.3 with the predicted-versus-measured coverage figure.
  To stay at nine pages, move fig_heff_synthetic panel (b) or the survival paragraph
  to the appendix if needed.
- Appendix: full proofs; numerical checks listed next to each proof.
- Workshop version: T3 statement and figure.
- Every number checked by script; check_paper and verify_paper_numbers must pass.

## Order of work

1. T1.a identities + finite-difference check.
2. T1.b-c stability bound, kappa(h) curves, comparison with bootstrap widths.
3. T3.a-c closed forms + simulation checks.
4. T3.d prediction of measured coverage.
5. Write theorems and proofs; figures; compile; commit; PR; merge.
6. T2 if time remains.
