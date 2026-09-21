# Proof audit, 22 September 2026

Four independent read-throughs of every result in `paper/main.tex` (foundations and endpoint law;
atomicity, remedies, guidance; survival and loss; asymptotics and body/appendix consistency), each with
its own numerical checks in `group1/` to `group4/`. Verdicts are the reviewers' own, kept here with what
was done about them. Nothing below claims a formal proof check; it records what was read and computed.

Legend: **fixed** = wording or proof text changed in the paper; **open** = stated in the paper as not proved.

| Result | Verdict | What was found | Status |
|---|---|---|---|
| Lemma cov, mixture coupling | correct | none | none needed |
| Lemma wellposed | minor gap | uniqueness step used time-dependent test functions without saying the weak form extends | fixed (K1) |
| Prop. projection, collapse, uncond., moments; Cor. repeated, distinction, zerobw, infbw | correct / minor | "for every x" means the continuous version; convention text was wrong about which slice fixes it | fixed (K1) |
| Prop. kernel-field | minor gap | conditional independence of X_t and the noisy label was implicit | fixed (K1) |
| Thm. endpoint | minor gap | p_h^gen was never defined; body claimed local Lipschitz gives existence of the limit | fixed (K1, K3) |
| Prop. atomicity | minor gap | h = 0 only at y = y^i; posterior need not be absolutely continuous (CIFAR inpainting is not), only atom-free; Zador is asymptotic | fixed (K3) |
| Prop. tgtnoise | minor gap | well-posedness of a field of a different form; h > 0 | fixed (K4) |
| Prop. interpolant noise, Cor. irreducible error | serious (side claim) | gamma-dot squared is not integrable at t = 0, so the pathwise loss is +infinity; the mis-specified target X_1 - X_0 does not end at the atom (it ends at x^i + sigma^(2/(1-sigma^2)) X_0), which the appendix and a table caption had claimed | fixed (K3, K4) |
| Prop. factors | correct, scope | proved for h = 0 | fixed (K4) |
| Prop. guidance (affine hull) | minor gap | "endpoint law" presupposes existence; tightness argument added | fixed (K4) |
| Prop. guidance atoms | minor gap | pathwise, needs convergence and a unique nearest atom; limit lies in the affine hull of the nearest atoms, not the convex hull, when w > 0 | fixed (K3, K4) |
| Prop. near duplicates | minor gap | sufficiency only, "exactly when" removed; n_eff defined | fixed (K3, K4) |
| Prop. Lipschitz bound, Cor. floor | correct | bound is attained | none needed |
| Prop. survival | correct; minor gap | fourth case not exhaustive; fields realising a >= 1/2 have infinite loss | fixed (K1) |
| Cor. loss form | correct algebra; serious (interpretation) | hypothesis forces L_Delta >= 1/delta - K for a network with Lip <= K, so the corollary says nothing for such networks; the sentence "consistent with measured Lipschitz constants" was unsupported | fixed (K1); EXP-1 slope now called an empirical scaling |
| Lemma nonintersect, Prop. memorise, Remark norepr | correct / minor | time law of the memorisation proposition unspecified | fixed (K1) |
| Prop. expansion | minor gaps | delta method, O not Theta, identifiability needs N h^(k+4) -> infinity, homoscedasticity wording | fixed (K3) |
| Prop. NW rates | correct, minor | design points need a bounded-below label density; Gaussian kernel to be stated | fixed (K3, K5) |

## Numerical checks (all in this folder)

- group1: closed-form field against brute-force conditional expectation (1-D exact quadrature, higher
  dimension by importance sampling, a few percent); ODE endpoints against the mixture weights on 4 atoms
  (deviation within 1.7 standard errors at h = 0.3, 1, 3); moments example (0, 24.90, 22.22).
- group2: endpoint smoothing and interpolant noise fields against Monte Carlo (within 0.003 to 0.01); the
  interpolant-noise flow x_t = t x^i + s_t x_0 to six digits; the mis-specified-target endpoint to five;
  guidance orthogonal-component identity to 1e-11; W_2 floor on a 2-D example.
- group3: survival identity to 7.5e-10 relative; the four cases; the loss-form bound on finite-loss
  examples; the d/(3L) floor by constrained least squares (attained).
- group4: expansion coefficient at N = 4e6; scaling of the spread with (N h^k)^(-1/2) (fitted -0.492);
  quoted rate numbers.

## Not checked

- Experiments were not rerun: the CIFAR slope 0.481, EXP-1 slope 0.485, the 415-fold reduction, the 38%
  off-atom share and the 1.9 to 27 tightness range are taken from the result files.
- Existence of the guided-flow endpoint law in general, and pathwise convergence of guided trajectories,
  are stated as unproved.
- The heuristic collapse-time scaling t_c/(1-t_c) = 2 sqrt(log N / d) in the collapse-time figure is a
  Gaussian-fluctuation argument, not a result.
