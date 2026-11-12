# Full-text prior-art check for items A–E (2026-11-11)

Scope: these five papers were checked against items A–E of the late-error / collapse paper. Short quotes are kept under 15 words. "Contains" means the passage was read in full text.

| # | Paper | What was read |
|---|---|---|
| 1 | Dodson, Gao, Wang, Wang, Wan, "Two Calm Ends and the Wild Middle", arXiv 2602.17846v1 | Full text: main body and Appendices A–E (E.1–E.9 figure captions) |
| 2 | Al-Jaff, Mehrpanah, Henter, Azizpour, Kragic, "What You Predict Shapes How You Memorize: Target-Parameterization and Memorization Dynamics in Flow Matching", ICML 2026 workshop (oral; Foundations of Deep Generative Models) | **Abstract only.** No arXiv version found. OpenReview (forum kzzlQzXldR) shows a bot-verification page to both WebFetch and its API. The ICML virtual pages (70261, 70262) carry only the abstract. |
| 3 | López Amado, Fumero, Locatello, "From Modes to Memories: Characterizing the Scale-Space Dynamics of Diffusion Models", arXiv 2609.39648v1 | Full text: main body and Appendices A–G |
| 4 | Jaziri, Mundt, Humayun, Ramesh, "Spectral Signatures of Memorization Basins in Diffusion Trajectories", arXiv 2611.01775v1 | Main body, all of Appendix A (A.1–A.5), Appendix B, and F.2. Remaining appendices C–F were grep-searched for Lipschitz/contraction/EDM/preconditioning/empirical-denoiser terms and had no hits. |
| 5 | Kwon, Fan, Lee, "Score-based Generative Modeling Secretly Minimizes the Wasserstein Distance", NeurIPS 2022, arXiv 2212.06359 | Full text with Appendices A–G |

## Item matrix

Legend: **C** = contains, **P** = partially or adjacent, **N** = no, **NA** = not accessed.

| Item | Dodson 2602.17846 | Al-Jaff ICML'26 | López Amado 2609.39648 | Jaziri 2611.01775 | Kwon 2022 |
|---|---|---|---|---|---|
| (A) Trajectory contraction/expansion bound driven by mu = lambda_max(sym d xhat/dx), threshold mu = 1 | N | NA | P | N | P |
| (B) Learned/exact risk ratio ~ (1-t)^{-2}, with floor r(1) >= d | N | NA | N | N | N |
| (C) Preconditioning gives D' -> I; memorization requires ‖dF/dx‖ ~ 1/sigma | P (weak) | NA | P (weak) | P (weak) | N |
| (D) Two clocks (selection at medium noise, landing at the end), or swap with the exact empirical denoiser | P | NA | P | N | N |
| (E) Denoiser-Jacobian eigenvalues measured along sampling trajectories of a trained model | N | NA | N | P (strong) | N |

## Evidence per paper

### 1. Dodson et al. (2602.17846)
- **A: N.** The paper has no Lipschitz, contraction or Jacobian-stability analysis of the sampling ODE. Its theorems cover something else: Thm 4.2 (posterior-weight concentration thresholds), Thm 4.8 (Gaussian shell coverage), Thm 4.9/B.6 (non-uniqueness of minimizers on disjoint shells), Thm 4.10/D.4 (pixel-sensitivity decay for circulant Gaussians) and Thm 4.11/C.4 (the large-sigma denoiser is near-linear Gaussian).
- **B: N.**
- **C: P (weak).** Appendix D (Lemma D.1) computes the Gaussian-data denoiser Jacobian Sigma(Sigma+sigma^2 I)^{-1}. It credits ref. [17] (Lukoianov et al.) with observing that it "→ I as σ → 0". This is a fact about the exact Gaussian posterior mean. The paper has no c_skip/c_out argument and no statement about how the raw network Jacobian must grow.
- **D: P.** Table 1 and App. E.6 run denoiser-swapping experiments, but the swap is **network for network** (EDM-1K and EDM-50K), not network for the exact empirical denoiser. Swapping the medium band (sigma in [0.14, 8.4]) flips memorization: 92.2% → 0% and 0% → 92.2%. Swapping the small band (sigma < 0.14) leaves memorization at 91.0% and 0.0%. The paper says memorization is "formed" at medium noise and "propagates". It does not separate *which image* from *exact landing*. EMP-1K, the empirical optimal denoiser, appears only in one-step and per-sigma MSE comparisons (Figs. 1–2, 11–16), never as a substitute inside the sampler. Section 4.2.3 also has a different emphasis: the small-noise regime of the trained EDM-1K shows near-zero per-sigma memorization, so in their account the end of sampling does not create collapse.
- **E: N.**

### 2. Al-Jaff et al. (ICML 2026 workshop)
- **Full text not accessed.** The abstract says x, eps and v prediction "memorize at different rates and to different degrees", that the ordering "persists even at matched sample quality", and that the best-FID target is not necessarily the least-memorizing one. **The abstract does not say which target memorizes most, or give the order.** It names only x, eps and v. EDM preconditioning is not mentioned in the abstract. All of A–E are unverified for this paper.
- Action: get the PDF manually (OpenReview in a browser, forum id kzzlQzXldR) before citing an ordering.

### 3. López Amado et al. (2609.39648)
- **A: P.** This is the closest result to A's threshold, but it lives in a different object. It is not the sampling ODE. It is the **fixed-sigma iterated map** x_{k+1} = D_sigma(x_k).
  - Prop. B.3 (Tweedie) gives ∇D_sigma = sigma^{-2} Cov[x0|x].
  - Prop. B.4 says the Jacobian is symmetric PSD, and a fixed point is an attractor iff Cov[x0|x*] ≺ sigma^2 I. That is iff all eigenvalues of ∇D_sigma are below 1. The appendix defines an attractor as a fixed point where "every eigenvalue of ∇M_σ(x*) has modulus less than 1".
  - Prop. B.7(b): near a training point at small sigma, ‖∇M_σ‖ ≤ eps_i R^2/sigma^2 < 1, which makes the map a contraction.
  - Thm. B.11 / Rem. (iii): the attractor disappears through a saddle-node bifurcation at sigma_c.
  - All of this is for the **exact** denoiser. The trained-network results are empirical (sigma_c and the retention coefficient kappa, App. D.2). The paper has no bound along an ODE trajectory, no time-varying sigma, and nothing about whether the sampler lands on a training point.
- **B: N.**
- **C: P (weak).** App. F writes eps-models as D_sigma(y) = y − sigma·eps_theta. The paper never argues that D' → I or that ‖dF/dx‖ must scale like 1/sigma. Prop. B.7(b) points the other way: the *exact* empirical denoiser Jacobian goes to 0 near a training point. The paper does not contrast this with what a network parametrization allows.
- **D: P.** The exact empirical denoiser is used as a reference ceiling (sigma_c^emp, kappa = sigma_c/sigma_c^emp, Table 2). It is never swapped into a sampling trajectory, and there is no two-clock statement.
- **E: N.** Trained models are probed only through orbit/escape tests. No Jacobian eigenvalues are measured, and no sampling trajectories are used. The Fig. 8 toy uses an EDM-preconditioned MLP, but only to count attractors.

### 4. Jaziri et al. (2611.01775)
- **A: N.** Appendix A has no eigenvalue-sign threshold, no Lipschitz/Grönwall bound and no contraction criterion. It contains: A.1 (basins are absorbing, a reachability argument), A.2 (the RF "curvature-equivalent" operator s·∂v/∂x − I, with identity-shift removal), A.3 (signed curvature: eigenvalues of the symmetric part of −∂eps/∂x), A.4 (stable rank, effective rank, spectral gap Delta_12) and A.5 (Tweedie posterior-covariance reading, and the isotropic ∂eps*/∂x = I/b_t near an isolated memorized example). Basins are defined operationally through bounded per-step perturbations (Def. 1), not through Jacobian stability.
- **B: N.**
- **C: P (weak).** A.2 notes that the raw RF velocity Jacobian contains a transport identity term (1/s)I "unrelated to density curvature" and subtracts it. A.5 shows that near a memorized point ∂eps*/∂x = I/b_t, which in denoiser terms means d xhat/dx → 0. The paper never draws the consequence for preconditioned networks: that F must have a Jacobian of order 1/sigma to collapse.
- **D: N.** The commitment time t* is the steepest rise of the spectral gap at intermediate DDIM steps, and the paper says trajectories become committed there. There is no split between "which image" and "exact landing", and no empirical-denoiser swap.
- **E: P (strong).** The paper computes **exact full-SVD Jacobians of a trained model along DDIM and RF sampling trajectories** (CelebA, 4,096 images; Figs. 1, 5, 8, 9; App. F.2). Singular values sigma_1..sigma_5, stable rank and effective rank are tracked step by step for memorized and non-memorized trajectories. In A.3 it also reports eigenvalues of the symmetrized eps-Jacobian, finding the spectrum is "overwhelmingly dominated by negative curvature". The differences from E: the object is ∂eps_theta/∂x (or s·∂v/∂x − I), not the data-prediction Jacobian d xhat/dx. The statistics are shape statistics (stable rank, effective rank, spectral gap), not lambda_max relative to 1. There is no EDM model and no link to a contraction threshold. Translated through Tweedie, their "negative curvature" corresponds to eigenvalues of d xhat/dx below 1/alpha_t. That is adjacent to, but not the same as, a mu < 1 measurement.

### 5. Kwon, Fan, Lee (NeurIPS 2022)
- **A: P.** Assumption (A2), Eq. (9), puts a **one-sided Lipschitz condition on the learned score** s_theta with a constant L_s(t) of either sign. Prop. 2, Eq. (28), is a differential inequality for W2(p_t, q_t), and Thm. 1, Eqs. (14)–(15), closes it with a **Grönwall integrating factor** I(t) = exp ∫ (L_f + L_s g^2). So the Grönwall machinery with a one-sided Lipschitz constant is prior art. What differs from A:
  - the bound is in W2 between distributions, under the reverse **SDE** / Fokker–Planck, not along individual ODE trajectories;
  - the constant belongs to the score, not to the denoiser, and is not written as lambda_max(sym d xhat/dx);
  - there is no threshold at 1, no contraction-to-a-training-point statement and no memorization discussion. The nearest point is Remark 4 / Fig. 4a: sigma^2 L_s(t) → −1 at large t.
- **B: N.**
- **C: N.**
- **D: N.**
- **E: N.** L_s(t) is estimated by grid search on 2-D toy data (Fig. 4a, Fig. 7). It is a global constant per t, not a Jacobian eigenvalue along trajectories of an image model.

## Verdict on novelty

- **A: novel as stated, with prior art to cite.** Kwon et al. 2022 already uses a one-sided Lipschitz constant plus a Grönwall factor, but in W2 and for the score; cite it as the technique's origin. López Amado et al. 2026 already has the "eigenvalue < 1 of the denoiser Jacobian ⇔ attractor" criterion, but for the fixed-sigma iterated map of the exact denoiser. Neither has a pathwise ODE bound in mu = lambda_max(sym D') with the mu = 1 threshold for landing on a training point. The paper should present A as connecting these two.
- **B: novel.** None of the four papers read in full has a (1-t)^{-2} risk-ratio law or the r(1) ≥ d floor.
- **C: novel.** The fact "D' → I as sigma → 0" appears only for the exact Gaussian denoiser (Dodson App. D, crediting Lukoianov et al.). The identity term in the RF velocity Jacobian is noted by Jaziri A.2. None of these turns it into the requirement ‖dF/dx‖ ~ 1/sigma under c_skip/c_out preconditioning.
- **D: the two-clock decomposition is novel. Medium-noise selection is prior art (Dodson).** Dodson's network-for-network swaps already show that the medium band decides memorization, and the paper must cite this and position against it. Note that Dodson's small-band swap leaves memorization unchanged (91%). The paper therefore needs to argue that its "landing" clock concerns exact collapse (distance to the training image), not the d1NN/d2NN < 1/3 memorization label. Swapping in the **exact empirical denoiser** inside the sampler does not appear in any paper read.
- **E: partially pre-empted by Jaziri et al.** They measure trained-model Jacobian spectra (singular values, plus symmetric-part eigenvalue signs) along sampling trajectories. Novelty remains for: (i) the data-prediction Jacobian, (ii) lambda_max against the threshold 1, (iii) EDM-preconditioned models and the c_skip/c_out decomposition. Cite Jaziri as the closest empirical prior art.
- **Al-Jaff et al.: unresolved.** Get the PDF before stating which target memorizes most.

Lead not checked: arXiv 2607.12616, "The Geometry of Memorization: Finite-Time Spectral Sensitivity as a Diagnostic for Flow Matching Models". It came up in a search and may bear on A/E.
