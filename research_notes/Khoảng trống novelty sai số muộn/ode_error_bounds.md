# Error bounds for deterministic samplers (PF-ODE, flow matching ODE): assumptions, late-time behaviour, and closeness to the user's results

Scope note: these notes come from 16 tool calls (arXiv metadata searches plus full-text fetches of Benton et al., Li-Wei-Chi-Chen 2024, Huang-Huang-Lin, and Cont 2026). Statements marked "(abstract only)" were checked against the arXiv abstract but not the full text. Venue facts not seen on a fetched page are flagged.

## Q1. What do the main ODE-sampler error bounds assume and prove? Do any use one-sided Lipschitz, log-norm or contraction?

### Takeaway
Every deterministic-sampler bound found needs regularity of the learned field on top of the L2 training error. That regularity comes in one of three forms:
- a Lipschitz constant in x, possibly time-dependent and integrated (Benton et al.; Huang et al.);
- an averaged Jacobian-error assumption (Li, Wei, Chi, Chen);
- contraction from (weak or strong) log-concavity of the data (Gao & Zhu; Kremling et al.; Tang & Zhao's "contractive DPMs").

The Benton et al. form, W2 <= eps * exp(int L_t dt), is the closest template to the user's Gronwall estimate. It uses a two-sided Lipschitz constant of the learned field, not a one-sided one, and the training-law L2 error, not the error along the exact or learned path. No ML paper found uses a log-norm or one-sided Lipschitz bound on the top eigenvalue of sym(d xhat/dx) in data-prediction form, with the specific (mu-1)/(1-t) rate.

### Cited Findings
- **Benton, Deligiannidis, Doucet, "Error Bounds for Flow Matching Methods"** (arXiv 2305.16860, May 2023, v2 Feb 2024; the page says "Reviewed on OpenReview", which fits TMLR 2024, but the abstract page shows no journal reference). [arXiv](https://arxiv.org/abs/2305.16860); [HTML](https://arxiv.org/html/2305.16860v2)
  - Assumption 1: integrated L2 training error, int_0^1 E||v_theta(X_t,t) - v(X_t,t)||^2 dt <= eps^2, taken under the true interpolant law.
  - Assumption 2: unique smooth flows.
  - Assumption 3: v_theta is L_t-Lipschitz in x for each t in (0,1). This is two-sided and time-dependent; finiteness of int L_t is needed implicitly.
  - Theorem 1: W2(pi_hat_1, pi_1) <= eps * exp(int_0^1 L_t dt).
  - To get rid of the assumed Lipschitz constant, they add a data condition, "lambda-regularity" (conditioning on a noisy observation inflates the conditional covariance by at most a factor lambda).
  - Theorem 3: W2 <= C^{sqrt(lambda)} * eps * (gamma_max/gamma_min)^{2 lambda}, using an interpolant with extra noise gamma_t > 0 at the endpoints.
  - Theorem 4 adds a sqrt(d) * gamma_min term. Corollary 1 optimises gamma_min to get W2 <~ d^{2lambda/(4lambda+2)} * eps^{1/(2lambda+1)}.
  - They say L_t "explodes as t->0 or 1" when the data lack full support, and they handle it by keeping gamma_0, gamma_1 > 0, a form of endpoint smoothing or early stopping. They give no explicit 1/(1-t) rate.
- **Li, Wei, Chi, Chen, "A Sharp Convergence Theory for the Probability Flow ODEs of Diffusion Models"** (arXiv 2408.02320, Aug 2024, preprint; it supersedes 2306.09251). [arXiv](https://arxiv.org/abs/2408.02320); [HTML](https://arxiv.org/html/2408.02320v1)
  - Data assumptions: bounded data and no smoothness assumption.
  - Assumption 1: averaged L2 score error eps_score.
  - Assumption 2: averaged Jacobian error E||J_{s_t} - J_{s_t*}|| <= eps_Jacobi, with s_t of class C^1.
  - Bound: TV <= C(d log^4 T / T + sqrt(d log^4 T) * eps_score + d log^2 T * eps_Jacobi).
  - The arXiv abstract mentions only "l2-accurate" scores. The Jacobian assumption appears only in the body.
- **Chen, Chewi, Lee, Li, Lu, Salim, "The probability flow ODE is provably fast"** (arXiv 2305.11798; NeurIPS 2023, a venue I know from background but did not confirm on the page). [arXiv](https://arxiv.org/abs/2305.11798)
  - (abstract only) The polynomial-time guarantees need a corrector step based on underdamped Langevin, so the sampler is not purely deterministic.
  - (abstract only) The authors say they needed "novel techniques for studying deterministic dynamics without contractivity", and they get O(sqrt(d)) dimension dependence under smoothness of the data.
- **Huang, Huang, Lin, "Convergence Analysis of Probability Flow ODE for Score-based Generative Models"** (arXiv 2404.09730; IEEE Trans. Inf. Theory 2025, DOI 10.1109/TIT.2025.3557050). [HTML](https://arxiv.org/html/2404.09730v3)
  - Assumption 3.2: L2 score error delta.
  - Assumption 3.3: s_t is C^2 with first and second x-derivatives bounded by L_t, and the constant enters as int L_t dt. An expectation version is allowed (Remark 3.4).
  - Data: compactly supported (possibly a manifold or point masses), with early stopping at tau.
  - Bound: TV <= C d^{3/4} T^{1/4} (int L_t + T tau^{-2} D^3)^{1/2} * delta^{1/2} + initialisation error.
  - Method: characteristics, Jacobi's formula and a Gagliardo-Nirenberg inequality, which explicitly avoids the exponential Gronwall factor. There is no one-sided Lipschitz or contraction argument.
  - The tau^{-2} factor is an explicit late-time (early-stopping) blow-up.
- **Gao & Zhu, "Convergence Analysis for General Probability Flow ODEs of Diffusion Models in Wasserstein Distances"** (arXiv 2401.17958, v2 Feb 2025; the publication venue was not confirmed). [arXiv](https://arxiv.org/abs/2401.17958)
  - (abstract only) First non-asymptotic W2 analysis of general PF-ODE samplers, assuming accurate scores and smooth log-concave data.
  - (abstract only) The proof "spell[s] out explicitly the contraction rate for the continuous-time ODE" and uses synchronous coupling. This is a contraction argument, where the strong log-concavity of the data plays the role of the user's mu <= mubar < 1.
- **Kremling, Iafrate, Taheri, Lederer, "Non-asymptotic error bounds for probability flow ODEs under weak log-concavity"** (arXiv 2510.17608, Oct 2025, preprint). [arXiv](https://arxiv.org/abs/2510.17608)
  - (abstract only) W2 bounds under weak log-concavity plus a Lipschitz score, covering Gaussian mixtures and exponential-integrator discretisation. It extends the contraction route beyond strong log-concavity.
- **Tang & Zhao, "Contractive Diffusion Probabilistic Models"** (arXiv 2401.13115, v3 Oct 2024; the venue was not confirmed). [arXiv](https://arxiv.org/abs/2401.13115)
  - (abstract only) Proposes contraction of backward sampling as a design criterion and says contraction "provably narrow[s]" score-matching and discretisation errors.
  - (abstract only) Pretrained DPM weights can be reused through a transformation.
  - This is the closest conceptual match to the user's certificate when mu <= mubar < 1: contraction makes the sampler robust to field error.
- **Kwon, Fan, Lee, "Score-based Generative Modeling Secretly Minimizes the Wasserstein Distance"** (arXiv 2212.06359; NeurIPS 2022 from background, not confirmed on the page). [arXiv](https://arxiv.org/abs/2212.06359)
  - (abstract only) W2 <= sqrt(objective) times multiplicative constants plus a fixed offset, "under suitable assumptions on the model". I did not check the exact model assumptions; see Gaps.
- **Tang & Yan, "Adaptivity and Convergence of Probability Flow ODEs"** (arXiv 2501.18863, 2025). [arXiv](https://arxiv.org/abs/2501.18863)
  - (abstract only) O(k/T) TV rate in the intrinsic dimension k, "with accurate score function estimation".
- **Lions & Seeger, "Transport equations and flows with one-sided Lipschitz velocity fields"** (arXiv 2306.13288, math.AP). [arXiv](https://arxiv.org/abs/2306.13288)
  - The pure-math theory of ODE flows under one-sided Lipschitz fields: in one time direction they are compressive, in the other expansive.
  - It gives the existence, uniqueness and stability of the regular Lagrangian flow in the expansive regime.
  - It is not applied to generative models, but it is the natural mathematical reference for a one-sided (log-norm) analysis.

### Inferences
- The user's Gronwall estimate, endpoint deviation <= (error on the exact path) * exp(int (mu-1)/(1-t)), relates to the literature as follows:
  - Structurally it is a log-norm or one-sided refinement of Benton et al. Theorem 1. Benton uses exp(int L_t) with a two-sided L_t of the velocity, which is >= |1-mu|/(1-t)-type quantities. The user's form uses the one-sided quantity (mu-1)/(1-t), which can be negative.
  - The negative case gives contraction and the sharp 1/(1-mubar) constant. Benton's bound cannot produce this: it always amplifies.
  - The one-sided log-norm version of Gronwall is classical ODE theory (Dahlquist/Lozinskii log-norm), so the novelty is the application to flow matching and the identification of mu = lambda_max(sym d xhat/dx). The inequality itself is not new.
- The contraction literature on certificates and robustness (Gao & Zhu; Kremling et al.; Tang & Zhao) gets contraction from the data distribution (log-concavity) or from a modified process, not from the learned network's Jacobian in data-prediction form. The user's certificate is checkable from the network (mu <= mubar < 1) and needs no data log-concavity, and none of the papers found states it that way.
- The repelling result for mu > 1 has no direct counterpart in the bounds surveyed: upper bounds simply grow. An instability (lower-bound) result driven by the learned field's Jacobian looks new relative to these bounds, though see the memorization and attractor work in Q5.

### Gaps
- Kwon et al. 2022: I did not read the full assumptions (I recall a condition on the score model's Jacobian, possibly one-sided), so this is unverified. The full text should be checked because it may be the closest prior one-sided result.
- Chen et al. 2023: the precise score assumptions (Lipschitz score, L2 error) were not checked beyond the abstract.
- I did not check whether any 2025-2026 flow-matching-specific bound (for example Gao/Jiao et al. on CNF convergence, Fukumizu et al. on minimax flow matching, or Kunkel & Trabs on Lipschitz guarantees) uses a one-sided Lipschitz or data-prediction formulation. The single search I ran ("flow matching error bound one-sided Lipschitz") returned nothing relevant.
- Venues for Gao & Zhu, Tang & Zhao, and Benton et al. (TMLR?) were not confirmed.

## Q2. Is it known that L2 training loss alone cannot control the deterministic sampler's error? What restores control?

### Takeaway
Yes, this is well established. Explicit counterexamples or gap results appear in Lu et al. (ICML 2022, likelihood), Benton et al. (informal construction), and Li-Wei-Chi-Chen (a sawtooth score perturbation that gives TV = 1 with arbitrarily small L2 error). Control is restored by four kinds of extra conditions:
- Lipschitz or derivative bounds on the learned field (Benton; Huang et al.);
- Jacobian-error bounds (Li et al.; or Lu et al.'s higher-order score matching);
- contraction or log-concavity (Gao & Zhu; Tang & Zhao);
- a stochastic corrector (Chen et al.).

Cont (2026) adds a related twist: the sampler's stability is governed by an *unweighted* velocity error, not the density-weighted score-matching error. This is close in spirit to the user's "error on the training law vs error along the trajectory" point.

### Cited Findings
- **Li, Wei, Chi, Chen 2024**: counterexample with X_0 ~ N(0,1). [HTML](https://arxiv.org/html/2408.02320v1)
  - At one step, a sawtooth perturbation of period L is added to the score estimate.
  - As L -> 0 the score error becomes arbitrarily small, but the output Y_1 is discrete, so TV(Y_1, X_1) = 1.
  - The authors contrast this with DDPM, where L2 error suffices, and suggest Wasserstein metrics might avoid the Jacobian assumption.
- **Benton et al.** informally note that v_theta can differ from v on sets of arbitrarily small measure. That keeps the L2 error small while the flow error is large, which is their motivation for the Lipschitz Assumption 3. [HTML](https://arxiv.org/html/2305.16860v2)
- **Lu, Zheng, Bao, Chen, Li, Zhu, "Maximum Likelihood Training for Score-Based Diffusion ODEs by High-Order Denoising Score Matching"** (arXiv 2206.08265; ICML 2022 from background). [arXiv](https://arxiv.org/abs/2206.08265)
  - (abstract only) "matching the first-order score is not sufficient to maximize the likelihood of the ODE".
  - (abstract only) The ODE's NLL is bounded by first-, second- and third-order score-matching errors, and they propose high-order DSM to control them.
- **Chen et al. 2023**: the deterministic analysis needs a Langevin corrector, and the authors stress that the deterministic dynamics have no contractivity. [arXiv](https://arxiv.org/abs/2305.11798)
- **Cont, "Probability flow ODEs in score-based and reflected diffusion models"** (arXiv 2610.03846, Oct 2026; NeurIPS 2026 Workshop "AI for Stochastic Dynamics", a workshop paper). [arXiv](https://arxiv.org/abs/2610.03846)
  - (abstract only) The Fokker-Planck identity does not guarantee a well-posed flow, and reverse sampling and invertibility need two-sided divergence control.
  - (abstract only) For learned scores, sampler stability is controlled by an unweighted velocity error, "exposing a mismatch with density-weighted score matching". This motivates architectural control of Jacobians and divergence.
  - (abstract only) Under the manifold hypothesis, early stopping is justified, but "constants deteriorate near the data endpoint".
  - (abstract only) A sphere example shows the exact deterministic flow becomes singular as the noise vanishes.
- **Huang et al.**: control is restored with bounded first and second derivatives of s_t (sup-norm, or in expectation). [HTML](https://arxiv.org/html/2404.09730v3)

### Inferences
- The user's statement that training loss alone cannot certify the ODE endpoint is not new as a general principle. The novel parts are (i) the checkable, network-intrinsic certificate (mu <= mubar < 1 with the sharp constant 1/(1-mubar)) and (ii) the quantified (1-t)^-2 mismatch law. The paper should cite Li et al. 2024 and Lu et al. 2022 for the general insufficiency, and Benton et al. for the Gronwall template.
- Cont 2026 is the closest recent work to the user's training-law vs trajectory-law theme, but from its abstract it is qualitative and focused on design principles, with no (1-t)^-2 law.

### Gaps
- The full text of Cont 2026 was not read, so it is unknown whether it quantifies the weighted vs unweighted mismatch rate near the endpoint.
- I did not verify whether Albergo, Boffi & Vanden-Eijnden ("Stochastic Interpolants", arXiv 2303.08797) state that the quadratic loss controls KL for the SDE but not the ODE. I recall that they do, but it was not checked this session.

## Q3. Is the mismatch between error on the training law and error along the sampler's own trajectories ("exposure bias") quantified, especially near t -> 1?

### Takeaway
Exposure bias, meaning the input mismatch between training and sampling, is well documented empirically for diffusion models. There are training-free fixes (Epsilon Scaling, time-shift samplers) and simple analytic models of the sampling distribution. I found no result giving a rate law of the form "trajectory error / training-law error ~ (1-t)^-2", and no flow-matching-specific theoretical treatment of the endpoint.

### Cited Findings
- **Ning, Li, Su, Salah, Ertugrul, "Elucidating the Exposure Bias in Diffusion Models"** (arXiv 2308.15321; ICLR 2024 from background). [arXiv](https://arxiv.org/abs/2308.15321)
  - (abstract only) Defines exposure bias as the input mismatch between training and sampling.
  - (abstract only) Analytically models the sampling distribution and attributes the bias to per-step prediction error.
  - (abstract only) Proposes a metric and Epsilon Scaling, which scales down the network output to move trajectories back toward the field learned in training. It was tested on ADM, DDIM, EDM, LDM, DiT and PFGM++.
- **Li, Qu, Yao, Sun, Moens, "Alleviating Exposure Bias in Diffusion Models through Sampling with Shifted Time Steps"** (arXiv 2305.15583; ICLR 2024 from background). [arXiv](https://arxiv.org/abs/2305.15583)
  - (abstract only) Shows empirically and theoretically that, for a sampled state x_hat_t, another time step t_s may couple better with it. Proposes the Time-Shift Sampler.
- **Xiao, "From Euler to Dormand-Prince: ODE Solvers for Flow Matching Generative Models"** (arXiv 2605.00836, 2026, preprint and pedagogical). [arXiv](https://arxiv.org/abs/2605.00836)
  - (abstract only) Reports empirically that the Jacobian eigenvalue spectrum of a learned CFM velocity field "stiffens sharply near t=1", which is why adaptive solvers spend their steps at the end.
  - (abstract only) The gap between low- and high-order solvers widens for undertrained models.
  - This is weak but direct evidence of late-time Jacobian growth in velocity form.
- **Cont 2026**: says, at the level of the abstract, that the sampler is governed by unweighted error while training is density-weighted. [arXiv](https://arxiv.org/abs/2610.03846)

### Inferences
- The user's (1-t)^-2 law, for regular velocity networks, connects the exposure-bias literature (empirical, mostly DDPM/DDIM) with ODE error theory. I found no prior statement of it. Exposure-bias papers frame the issue through the per-step error and time shifts, not through endpoint asymptotics.

### Gaps
- I did not search the theoretical "error propagation in diffusion models" line, for example Li & van der Schaar, "On Error Propagation of Diffusion Models" (ICLR 2024, which I recall), or Daras et al., "Consistent Diffusion Models" (NeurIPS 2023), or Ning et al., "Input Perturbation Reduces Exposure Bias" (ICML 2023). These exist in my background knowledge but were not verified this session.
- I found no flow-matching-specific exposure-bias theory.

## Q4. Is there an irreducible lower bound on the flow-matching loss near t = 1, and what does it imply for time weighting?

### Takeaway
It is standard that the CFM loss equals the FM loss plus an irreducible conditional-variance term E Var(target | x_t). Whether that term vanishes or grows near the data end depends on the parameterisation:
- the posterior variance of the data endpoint goes to 0;
- the velocity target's variance behaves like (1-t)^-1 or larger in some conventions.

Recent 2025-2026 work uses the vanishing posterior variance to justify weights that diverge like (1-t)^-2. I found no paper stating the user's specific claim, that a *regular* (Lipschitz) velocity network cannot get the hard-conditioned loss below d at t -> 1. The closest is "Lipschitz singularities" (Yang et al.), which concerns the time variable near t = 0 in diffusion convention.

### Cited Findings
- **Web search synthesis**, unverified excerpts that need full-text checking:
  - One 2026 paper calls the fixed-time conditional-variance term "irreducible" and derives inverse-covariance weights that grow like (1-t)^-2 near t = 1, because the conditional covariance C_t -> 0. [arXiv 2602.05435](https://arxiv.org/pdf/2602.05435); [arXiv 2605.08344](https://arxiv.org/pdf/2605.08344)
  - Another treats the denoising phases of flow matching. [arXiv 2510.24830](https://arxiv.org/pdf/2510.24830)
  - I could not pin down from the snippets which of these specific claims each paper makes.
- **Gagneux, Martin, Gribonval, Massias, "Training Flow Matching: The Role of Weighting and Parameterization"** (arXiv 2603.06454, v3 Sep 2026; 2nd DeLTa Workshop, ICLR 2026, workshop paper). [arXiv](https://arxiv.org/abs/2603.06454)
  - An empirical study of loss weighting and of noise, clean-image and velocity parameterisations against intrinsic dimension, architecture and dataset size.
  - The abstract gives no specific t -> 1 result.
- **Yang et al., "Lipschitz Singularities in Diffusion Models"** (arXiv 2306.11251, v2 Dec 2024; ICLR 2024 from background). [arXiv](https://arxiv.org/abs/2306.11251)
  - (abstract only) Proves and observes infinite Lipschitz constants of the network with respect to time near the zero noise level.
  - (abstract only) Proposes E-TSDM and reports over 33% FID reduction for DDIM and DPM-Solver.

### Inferences
- In velocity form with the hard-conditioned target x1 - x0, the user's "loss >= d" claim reads as follows. A Lipschitz v cannot represent the singular minimiser (xhat - x)/(1-t) near the data, so at t -> 1 it essentially predicts the mean velocity, and the residual is the variance of x0, which is d for a standard Gaussian source.
- This mirrors the "Lipschitz singularity" phenomenon, but in x and at the data end, not in t. It also pushes in the opposite direction from the (1-t)^-2 ML-weighting papers: up-weighting t -> 1 is pointless or harmful for a velocity network that cannot reduce the loss there.
- I found no source that states this trade-off explicitly.

### Gaps
- The cited 2602.05435 and 2605.08344 PDFs were not opened, so authors, titles and exact claims are unverified. The report writer should not attribute specific claims to them without checking.
- I did not verify EDM (Karras et al. 2022) or EDM2 (Karras et al. 2024) loss-weighting and uncertainty-weighting discussions this session, though they are standard references for per-noise-level irreducible loss.

## Q5. Stability analysis (Lyapunov, contraction) of sampling ODEs near the data manifold or near training points

### Takeaway
There is (a) contraction-based analysis under log-concavity, (b) theory of PF-ODE convergence to training points and memorization basins for idealised denoisers, and (c) well-posedness and singularity analysis of the exact flow near the data endpoint. None uses a Jacobian-eigenvalue threshold mu = 1 of the data-prediction map as an attract-or-repel criterion along learned trajectories. That part of the user's work appears new.

### Cited Findings
- **Zeno, Manor, Ongie, Weinberger, Michaeli, Soudry, "When Diffusion Models Memorize: Inductive Biases in Probability Flow of Minimum-Norm Shallow Neural Nets"** (arXiv 2506.19031, 2025). [arXiv](https://arxiv.org/abs/2506.19031)
  - (abstract only) For min-norm shallow ReLU denoisers on orthogonal data, the probability flow converges to a training point or a sum of training points.
  - (abstract only) Early stopping by the scheduler allows convergence to more general manifold points, and memorization decreases with more samples.
- **Verma et al., "Early Signatures of Memorization in Diffusion Models via Basin Geometry and Cyclic Denoising"** (arXiv 2610.11670, Oct 2026). [arXiv](https://arxiv.org/abs/2610.11670)
  - (abstract only) Localised basins form around training samples before memorized samples appear. They measure them with score divergence and basin volume.
  - (abstract only) Under the exact empirical score, cyclic denoising started near an isolated training sample provably returns to it.
  - (abstract only) The authors report "degenerate attractors" that match no single training image.
- **Cont 2026**: a sphere example where the exact deterministic flow becomes singular as the noise vanishes, and constants deteriorate near the data endpoint. [arXiv](https://arxiv.org/abs/2610.03846)
- **Contraction under log-concavity**: Gao & Zhu (strongly log-concave), Kremling et al. (weakly log-concave), and Tang & Zhao (contractive DPMs by design). [2401.17958](https://arxiv.org/abs/2401.17958); [2510.17608](https://arxiv.org/abs/2510.17608); [2401.13115](https://arxiv.org/abs/2401.13115)
- **Lions & Seeger**: compressive and expansive one-sided Lipschitz flows, a mathematical basis for attract and repel regimes. [2306.13288](https://arxiv.org/abs/2306.13288)

### Inferences
- The user's dichotomy (mu < 1 contracts and is certified, mu > 1 repels) has natural relatives:
  - memorization basins and attractors (Verma et al.; Zeno et al.), which concern the empirical-optimal or idealised field;
  - log-concavity contraction (Gao & Zhu), which concerns the data law.
- Stating the threshold at mu = 1 for the learned data-prediction Jacobian, with a matching repelling lower bound, is not something I found in the literature.

### Gaps
- I did not verify the statistical-physics memorization and collapse work (for example Biroli, Bonnaire, de Bortoli, Mézard, "Dynamical regimes of diffusion models", which I recall appeared in Nature Communications 2024), nor associative-memory views of diffusion. These are probably relevant to the near-training-point attractor picture but were not checked this session.
- I found no Lyapunov-function analysis of the flow-matching ODE near the data manifold in the 2021-2026 ML literature, though the search budget was limited.
