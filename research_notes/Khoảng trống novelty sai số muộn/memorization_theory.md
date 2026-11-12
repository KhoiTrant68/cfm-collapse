# Memorization vs generalization theory in diffusion and flow matching (2023-2026)

Scope: the exact empirical optimum and its collapse onto training points, why trained networks do not reproduce it, late-sampling dynamics, which training example is returned, and how conditioning or guidance affects memorization. Search date: 2026-11-11. "Verified" means I opened the arXiv page, venue page or proceedings this session. Items marked "(not re-verified this session)" come from prior knowledge, and the report writer should check them before citing.

## Q1. Closed-form / empirical-optimum results: what do they prove?

### Takeaway
The empirical-optimum results agree on one point. With N training points, the exact minimizer of the denoising or flow-matching loss is a softmax-weighted (Nadaraya-Watson) posterior mean over training points, and its sampler returns a training point. The papers differ in what they add: when collapse happens (Biroli et al.), how large a dataset a network can still memorize (Gu et al.), and smoothed or local surrogates that generalize (Scarvelis, Kamb & Ganguli, Niedoba). None of them gives a per-example law for which training point is returned beyond "the dominant posterior atom". None studies conditional compositions (label noise, label averaging, CFG) at the exact optimum.

### Cited Findings
- **Biroli, Bonnaire, de Bortoli, Mézard, "Dynamical Regimes of Diffusion Models", Nature Communications 15, 9957 (2024), DOI 10.1038/s41467-024-54281-3; arXiv 2402.18491 (Feb 2024). Published.**
  - Statistical-physics analysis with the score assumed exact, in the joint large-N, large-d limit.
  - Three regimes along the backward process: (i) pure noise; (ii) a "speciation" transition where coarse class structure appears, likened to symmetry breaking; (iii) a "collapse" phase where trajectories are attracted to one specific training point, likened to glass condensation.
  - Speciation time is set by the top eigenvalue of the data covariance. Collapse time is governed by the entropy of the noised empirical distribution, an excess-entropy criterion. This implies a curse of dimensionality: N must be exponential in d to avoid collapse.
  - The authors state the speciation and collapse conditions hold for both deterministic (flow/ODE) and stochastic samplers.
  - [arXiv PDF](https://arxiv.org/pdf/2402.18491); [Nature Comms record (RePEc)](https://ideas.repec.org/a/nat/natcom/v15y2024i1d10.1038_s41467-024-54281-3.html)
- **Gu, Du, Pang, Li, Lin, Wang, "On Memorization in Diffusion Models", TMLR (02/2025); arXiv 2310.02664. Published.**
  - Notes that the denoising objective's closed-form optimum can only reproduce training data.
  - Defines Effective Model Memorization (EMM): the largest training-set size at which a trained model still approximates the theoretical optimum.
  - Studies how EMM depends on data distribution, model configuration and training procedure.
  - Finds that conditioning training data on uninformative random labels can significantly trigger memorization. This is directly relevant to the user's label-noise result.
  - Mostly empirical; the closed form is used as the reference point.
  - [arXiv](https://arxiv.org/html/2310.02664v2); [TMLR record](https://mlanthology.org/tmlr/2025/gu2025tmlr-memorization)
- **Scarvelis, Sáez de Ocáriz Borde, Solomon, "Closed-Form Diffusion Models", TMLR (May 2025); arXiv 2310.12395. Published.**
  - Starts from the fact that the closed-form score for a finite training set memorizes.
  - Explicitly smooths that score to get a training-free sampler that produces novel samples, with a nearest-neighbor estimator of the smoothed score.
  - Generalization here is a designed smoothing, not an explanation of trained networks.
  - [arXiv](https://arxiv.org/abs/2310.12395v3); [TMLR record](https://mlanthology.org/tmlr/2025/scarvelis2025tmlr-closedform)
- **Bertrand, Gagneux, Massias, Emonet, "On the Closed-Form of Flow Matching: Generalization Does Not Arise from Target Stochasticity", NeurIPS 2025 (oral); arXiv 2506.03719 (v1 Jun 2025, v2 Dec 2025). Published.**
  - Argues against the view that flow matching generalizes because its regression target is noisy. In high dimension the stochastic and closed-form FM losses are nearly equivalent.
  - Training on the closed-form target gives comparable or better image-generation performance.
  - Places generalization in the network's failure to approximate the exact velocity field, and reports that generalization arises mainly early along the trajectory.
  - [arXiv](https://arxiv.org/abs/2506.03719); [NeurIPS oral](https://nips.cc/virtual/2025/oral/116379)
- **Liu, Liu, Li, Bai, Ji, Guo, Wan, Wen (NYU / NYU Shanghai), "From Navigation to Refinement: Revealing the Two-Stage Nature of Flow-based Diffusion Models through Oracle Velocity", arXiv 2512.02826 (v1 2 Dec 2025, v2 17 Dec 2025, v3 10 Apr 2026). Venue NOT confirmed.**
  - The arXiv comments say "Preprint v2". My searches found no CVPR 2026 listing, so the "CVPR 2026" label needs checking against the CVPR 2026 accepted list or the v3 comments.
  - Theorem 2.1: the closed-form "oracle" marginal velocity for a Gaussian prior, a finite dataset and a linear path, u*_t(x) = A_t Σ_i γ_i(x,t) x1^(i) + B_t x, with γ_i a softmax over −‖x − α_t x1^(i)‖²/(2σ_t²) (a Nadaraya-Watson estimator).
  - The top-1 posterior weight saturates to 1 beyond t ≈ 0.1. Before that the target is a multi-sample mixture ("navigation"); after it, the nearest sample dominates ("refinement").
  - Saturation is faster at higher dimension D and slower at larger N. The trained model's own transition is around t ≈ 0.2.
  - Hybrid sampling (oracle early, then model):
    - Switching to the model at t_switch ∈ (0.2, 1] reproduces training images.
    - Switching in [0, 0.2] generalizes.
  - The authors "hypothesize that the model's generalization capability arises mainly from the navigation stage, while its memorization behavior roots from the refinement stage."
  - The oracle sampler "deterministically retrieves a random training sample". No law for which sample beyond the nearest or dominant one.
  - The model's oracle-target loss "climbs again as t → 1"; this is speculation, not tested.
  - They do NOT test the reverse swap (model early, oracle late).
  - They use the framing to explain timestep-shifted schedules, CFG intervals and latent-space choices.
  - [arXiv HTML v2](https://arxiv.org/html/2512.02826v2); [abs page](https://arxiv.org/abs/2512.02826v2)
- **Li, Hu, Lim, Li, Gao, Diao, Ding, Vazirgiannis, Boström, "A Kinetic-Energy Perspective of Flow Matching", arXiv 2602.07928 (Feb 2026). Listed as an ICML 2026 poster.**
  - The arXiv text does not state a venue, but an ICML 2026 virtual poster page exists. Treat it as ICML 2026 and confirm in the proceedings.
  - Defines Kinetic Path Energy (KPE), E = ½∫₀¹‖v_θ(x_t,t)‖²dt, a per-sample diagnostic.
    - Higher KPE goes with stronger semantics (CLIP score) on ImageNet-256 with SiT-XL/2.
    - KPE is negatively correlated with training-data density (Spearman ρ ≈ −0.65 against k-NN density on CIFAR-10).
  - Theorem 4.2: under posterior dominance, squared speed is bounded by affine functions of −log p̂_t.
  - Lemma 5.1 (informal): the empirical FM optimum has a 1/(1−t) "terminal velocity singularity". If a trajectory stays a fixed distance from all training points on [1−ε, 1) while the posterior concentrates on one atom, then ∫‖û*‖² = ∞.
  - Proposition 5.2(b): any path ending at a training point has ∫_t^1‖ẋ‖² ≥ ‖x^(i) − x(t)‖²/(1−t).
  - The memorization fraction on CelebA (1,024 training images) reaches 98% by 2M iterations while KPE keeps rising.
  - Proposes Kinetic Trajectory Shaping (KTS), a training-free inference rescaling: velocity boosted for t < 0.6 ("launch") and damped exponentially after ("soft landing").
    - CelebA-32: FID 16.68 → 14.35 and memorization fraction 37.3% → 31.2%.
    - ImageNet-256 gains are small (FID 11.70 → 11.59).
  - No Jacobian analysis, no error-propagation rate, no per-example attribution.
  - [arXiv HTML](https://arxiv.org/html/2602.07928v1); [ICML 2026 poster](https://icml.cc/virtual/2026/poster/62806)
- **Achilli, Ventura, et al., "Losing dimensions: Geometric memorization in generative diffusion", arXiv 2410.08727 (v1 Oct 2024, v2 Mar 2026). Preprint; no venue found.**
  - Data on a latent manifold: memorization removes tangent directions gradually, not all at once. Different directions are lost at different critical times and dataset sizes, depending on the variance along each direction.
  - Under some conditions, higher-variance subspaces are lost first.
  - Framed as a glassy phase transition. Gives "geometric memorization" without collapse onto a single point.
  - [arXiv HTML](https://arxiv.org/html/2410.08727v1)
- **Kamb & Ganguli, "An analytic theory of creativity in convolutional diffusion models", ICML 2025 (PMLR 267:28795-28831); arXiv 2412.20292. Published.**
  - Locality plus equivariance constraints on the optimal score give "local score" and "equivariant local score" machines.
  - After calibrating one time-dependent hyperparameter (patch size versus t), these machines quantitatively predict trained ResNet and UNet outputs.
  - Creativity arises as a "locally consistent patch mosaic" of training patches across scales and locations. The theory partially predicts self-attention UNets (median r² ≈ 0.77 on CIFAR-10).
  - [PMLR](https://proceedings.mlr.press/v267/kamb25a.html); [arXiv](https://arxiv.org/pdf/2412.20292)
- **Niedoba, Zwartsenberg, Murphy, Wood, "Towards a Mechanistic Explanation of Diffusion Model Generalization", ICML 2025 (arXiv 2411.19339; earlier at a NeurIPS 2024 workshop). Published.**
  - Patch Set Posterior Composites (PSPC) aggregate patch-level empirical denoisers across positions. PSPC denoises like trained networks, and both are closer to each other than to the optimal global denoiser.
  - Patch denoising is said to explain "a significant portion" of generalization.
  - [arXiv](https://arxiv.org/html/2411.19339v3); [ICML 2025 poster](https://icml.cc/virtual/2025/poster/45759)
- **Early Signatures of Memorization in Diffusion Models via Basin Geometry and Cyclic Denoising, arXiv 2610.11670 (Oct 2026). Preprint; authors not checked.**
  - Under the exact empirical score, a well-separated training point keeps cycling trajectories with a probability set by the cycling noise and its separation from competing points. This is a per-point retention law at the exact optimum.
  - Reports "degenerate attractors" that match no training image near τ_gen and disappear as training continues.
  - [arXiv](https://arxiv.org/html/2610.11670v1)

### Inferences
- The softmax/Nadaraya-Watson form of the CFM optimum (Liu et al. Thm 2.1; Bertrand et al.) is standard and not novel.
- The 1/(1−t) terminal blow-up of the empirical velocity is already stated informally by Li et al. (KPE, Lemma 5.1). The user's (1−t)^-2 trajectory-error-to-training-error amplification differs from it in two ways:
  - It concerns error propagation, not velocity magnitude or energy.
  - It is tied to the data-prediction Jacobian.

  The user should cite KPE and state this distinction explicitly.
- No paper here treats conditional compositions at the exact optimum: label noise, label averaging, or CFG on a label-averaged field reaching blends above a threshold. Gu et al. come closest with their empirical observation that random labels increase memorization.

### Gaps
- I could not confirm a CVPR 2026 venue for "From Navigation to Refinement". The abstract page shows only "Preprint v2", and v3 (Apr 2026) comments were not read.
- I did not re-open the Yoon et al. paper ("Diffusion probabilistic models generalize when they fail to memorize", believed to be an ICML 2023 workshop paper). Its venue and URL are unverified this session.
- The KPE appendix (the last ~76k characters) was not read, so there may be further formal results.

## Q2. Inductive-bias and early-stopping accounts: why do networks generalize? Must network error stay large near t → 1?

### Takeaway
There are five main accounts: (a) architectural inductive bias, through locality/equivariance and adaptive harmonic bases; (b) implicit dynamical regularization, an early-stopping window that grows with N; (c) smoothing or approximation error, where the network is a smoothed empirical score; (d) training-target variance; (e) a noise-level localization debate. On (e), one strand says memorization is decided at medium noise and the low-noise end is "calm" (Dodson et al.). Others put it in the late or refinement stage (Liu et al.) or say generalization is decided early (Bertrand et al.). No paper proves a theorem of the form "the network error must stay above X near t → 1 for the sample to leave the training set". The closest are informal statements and toy models.

### Cited Findings
- **Bonnaire, Urfin, Biroli, Mézard, "Why Diffusion Models Don't Memorize: The Role of Implicit Dynamical Regularization in Training", NeurIPS 2025 (oral); arXiv 2505.17638. Published.**
  - Two training timescales: τ_gen, when sample quality becomes good, which is constant in n; and τ_mem, when memorization starts, which grows linearly in training-set size n.
  - This opens an early-stopping generalization window [τ_gen, τ_mem] that widens with n.
  - Backed by U-Net experiments and an analytically tractable random-features model in the high-dimensional limit.
  - [arXiv](https://arxiv.org/abs/2505.17638v2); [NeurIPS oral](https://nips.cc/virtual/2025/oral/119373)
- **Kadkhodaie, Guth, Simoncelli, Mallat, "Generalization in diffusion models arises from geometry-adaptive harmonic representations", ICLR 2024; arXiv 2310.02557. Published (venue not re-verified this session).**
  - Two networks trained on disjoint subsets converge to nearly the same score when N is large: the transition from memorization to generalization.
  - The denoiser Jacobian is analysed as a low-rank, geometry-adaptive harmonic basis (eigenvectors and eigenvalues), and small eigenvalues act as local invariances.
  - [arXiv](https://arxiv.org/pdf/2310.02557); [NYU PDF](https://www.cns.nyu.edu/pub/lcv/kadkhodaie24a.pdf)
- **Vastola, "Generalization through variance: how noise shapes inductive biases in diffusion models", arXiv 2504.12532 (ICLR 2025 per my prior knowledge; not re-verified).**
  - The denoising-score-matching target has very high variance at low noise. The PF-ODE effectively averages over this estimator noise, which produces generalization.
  - [arXiv](https://arxiv.org/pdf/2504.12532)
  - Note that Bertrand et al. dispute this target-stochasticity route for flow matching in high dimension. [arXiv](https://arxiv.org/abs/2506.03719)
- **Kaiser & Kollmann, "Diffusion Models Memorize in Training — and Generalize in Inference" (v1 title "Beyond Sample Copying: Structural Memorization in Diffusion Models"), arXiv 2603.13419 (v2 May 2026). Preprint; no theorems.**
  - The training/validation denoising gap peaks at intermediate noise and grows with training time, model size and smaller N.
  - 2D toy model: a model error δ acts like extra noise, σ̃² = σ² + δ². It smooths the localized optimal field and suppresses the gap.
  - At inference, sampling trajectories stay "sufficiently far from the distribution of noisy training samples", which is why samples generalize.
  - No error-growth rate, no Jacobian or stability analysis, no per-example attribution.
  - [arXiv HTML v2](https://arxiv.org/html/2603.13419v2)
- **Dodson, Gao, Wang, Wang, Wan, "Two Calm Ends and the Wild Middle: A Geometric Picture of Memorization in Diffusion Models", arXiv 2602.17846 (Feb 2026). Preprint.**
  - Memorization risk is "highly non-uniform across noise levels", with a "danger zone at medium noise levels".
  - Denoiser-swap experiments on CIFAR-10:
    - Swapping the medium σ range ([0.14, 8.4]) flips memorization between 92.2% and 0%.
    - Swapping the large or small σ ranges has negligible effect.
  - Small σ is "calm" because trained networks see little training coverage there ("small noise avoids memorization due to limited training coverage"). The empirical optimal denoiser alone is nearly 100% memorizing for σ < 0.3.
  - Theory covers posterior-weight concentration (Thm 4.2) and Gaussian-shell coverage (Thm 4.8).
  - [arXiv HTML](https://arxiv.org/html/2602.17846)
- **Smoothing-score framework, arXiv 2601.19285 (2026). Preprint; authors not checked.**
  - At small noise a single centre dominates the empirical score weights, which causes collapse.
  - Argues networks fit the score but implicitly smooth its weights at small noise.
  - [arXiv HTML](https://arxiv.org/html/2601.19285v2)
- **"Manifold Generalization Provably Proceeds Memorization in Diffusion Models", arXiv 2603.23792 (2026). Preprint; authors not checked.**
  - Assumes accurate score learning at moderate-to-large noise.
  - Argues that at small noise a coarsely learned score, combined with the ODE integrator, implicitly performs an approximate projection onto the data manifold rather than onto training points.
  - [arXiv PDF](https://arxiv.org/pdf/2603.23792)
- **Position paper "Understanding diffusion models requires rethinking (again) generalization", arXiv 2605.06077 (2026).**
  - Argues error propagation through the backward process is already well understood and the open problem is the learning problem.
  - [arXiv PDF](https://arxiv.org/pdf/2605.06077)
- **Pidstrigach, "Score-based generative models detect manifolds", NeurIPS 2022 (prior knowledge; not re-verified).**
  - Shows that diffusion models learn low-dimensional structure, and that this ability drives memorization. Cited in Achilli et al. v2.
  - [Achilli v2 citing it](https://arxiv.org/html/2410.08727v2)

### Inferences
- The user's "a trained sampler leaves the training set only through late-time field error" is partly in tension with Dodson et al. Their swaps show that memorization rate is decided by the medium-noise denoiser and is almost insensitive to swapping the small-noise one.
- It is also in tension with Liu et al.: oracle up to t ≈ 0.2 then model gives memorization, which suggests the trajectory is committed by roughly t ≈ 0.2 in their schedule.
- The two views can be reconciled through how "late" is defined.
  - At the exact optimum, collapse onto a basin happens at medium noise (Biroli's collapse time).
  - The fine approach to the atom happens at t → 1.
  - A "late-time" claim should therefore be stated relative to the collapse time t_c, not as t → 1 in absolute terms.
  - It should also say whether "leaving the training set" means a different nearest neighbour (decided mid-trajectory) or a nonzero distance to the nearest atom (decided late).

  This is a concrete gap the user can fill with their Jacobian-threshold result, and a likely reviewer objection that needs a direct answer.
- None of these accounts gives a quantitative lower bound on the network's late-time error that is necessary for generalization, nor a (1−t)^-2 amplification law. The user's result appears new on this point, subject to the KPE caveat above.

### Gaps
- I did not verify author lists for arXiv 2601.19285, 2603.23792 or 2605.06077, nor whether they contain formal late-time results.
- I did not search Lukoianov et al. on locality emerging from data statistics (2025), which I believe exists but did not verify.

## Q3. Which training sample is returned; per-sample attribution; Jacobian/attractor views

### Takeaway
Per-sample theory is new and growing quickly (mostly arXiv preprints from mid to late 2026). Exact-denoiser attractor and critical-scale analyses predict retention per training point from its mass and separation. Jacobian-spectrum signatures detect memorized trajectories. Cyclic-denoising retention probabilities exist. None ties the outcome to a contraction threshold of the learned data-prediction Jacobian at eigenvalue 1 along a flow-matching trajectory. None attributes off-training samples to late-time field error per example. The nearest-neighbour ratio test (d1 < d2/3) remains the standard operational criterion.

### Cited Findings
- **López Amado, Fumero, Locatello (ISTA), "From Modes to Memories: Characterizing the Scale-Space Dynamics of Diffusion Models", arXiv 2609.39648 (30 Sep 2026). Preprint. This is the closest to the user's Jacobian idea.**
  - The exact denoiser is Gaussian mean shift: M_σ(x) = x + σ²∇log p_σ(x). Its fixed points are critical points of p_σ, and its attractors are the modes.
  - Attractors are defined through basins, not Jacobian eigenvalues.
  - Per-sample critical scale σ_c(x) = sup{σ : x retained under iteration of M_σ}. The attractor disappears at σ_c in a saddle-node bifurcation, which the authors call "a bifurcation, not a threshold".
  - Theorem 4: duplicating a training point can only increase its σ_c.
  - Theorem 5 (two atoms): σ_c ≈ d/√(2 log(1/θ)), linear in separation d and logarithmic in mass θ.
  - Corollary 7: a caption increases σ_c if and only if it raises the model's mass on that example. This is a conditioning-memorization link.
  - It iterates the denoiser at fixed σ rather than following trajectories. Flow matching is not mentioned.
  - [arXiv HTML](https://arxiv.org/html/2609.39648v1)
- **Jaziri, Mundt, Humayun, Ramesh, "Spectral Signatures of Memorization Basins in Diffusion Trajectories", arXiv 2611.01775 (1 Nov 2026). Preprint.**
  - Memorized trajectories show "the emergence of a dominant singular mode followed by a sharp spectral recovery" in the local denoiser Jacobian. In training this is seen as a rise in the relative spectral gap Δ12 around DDPM t ∈ [200, 400].
  - Basins are defined as regions no bounded-perturbation continuation can escape.
  - Per-sample detector (JER) from one low-noise query: AUROC 0.956 for DDIM and 0.870 for rectified flow on CelebA.
  - Near memorized endpoints the geometry approaches an isotropic I/b_t structure.
  - No eigenvalue-1 contraction threshold and no late-time error bound.
  - [arXiv HTML](https://arxiv.org/html/2611.01775)
- **Diffusion Model Attribution via Spectral Coupling of Denoiser Responses, arXiv 2606.28092 (2026). Preprint; not opened.**
  - Uses denoiser responses for training-data attribution.
  - [arXiv PDF](https://arxiv.org/pdf/2606.28092)
- **Cyclic Denoising Reveals Ultrastable Memories in Diffusion Models, arXiv 2606.24000 (2026). Preprint; not opened.**
  - Long-lived attractors under repeated noising and denoising reveal memorized images, including in Stable Diffusion v1.4.
  - [arXiv HTML](https://arxiv.org/html/2606.24000)
- **Local Coverage Governs Memorization in Diffusion Models, arXiv 2606.14390 (2026). Preprint; not opened.**
  - Isolated training points produce concentrated local density estimates and get memorized; dense regions support smoother generation.
  - This is a per-point prediction of which samples are memorized.
  - [arXiv HTML](https://arxiv.org/html/2606.14390)
- **Inversion-based Measure of Memorization for Diffusion Models, arXiv 2405.05846 (2024). Not opened.**
  - A per-example memorization score.
  - [arXiv PDF](https://arxiv.org/pdf/2405.05846)
- **Standard memorization criterion.**
  - A sample is memorized if d1NN < d2NN/3 (Yoon et al.; Gu et al.).
  - Used by Dodson et al. and by KPE (τ_gap = 1/3).
  - [Gu et al.](https://arxiv.org/html/2310.02664); [Dodson et al.](https://arxiv.org/html/2602.17846)

### Inferences
- The idea that "a training point is an attractor and its stability decides memorization" is now established at the exact denoiser (López Amado et al.). Jacobian-spectrum diagnostics of memorization are also established (Jaziri et al.; Kadkhodaie et al.).
- To be novel, the user's eigenvalue-1 contraction threshold should be framed around three differences:
  - It concerns the learned data-prediction Jacobian along a flow-matching ODE.
  - It gives a sharp threshold rather than an empirical spectral signature.
  - It predicts per-sample off-training outcomes rather than only detecting memorization.

  The user should cite both López Amado et al. and Jaziri et al. explicitly, since reviewers in late 2026 will know them.
- The specific question "which training example is returned, and with what probability, from the exact CFM optimum under conditioning compositions" appears open. Only two-atom and separation laws exist so far (López Amado Thm 5; the cyclic-retention paper 2610.11670).

### Gaps
- I did not open 2606.28092, 2606.24000, 2606.14390 or 2405.05846, so their exact claims and authors are unverified.
- The second halves of the López Amado and Jaziri papers (more than 100k characters each) were not read. They may contain trajectory or late-time results that narrow the user's novelty and should be checked.
- I found no theory paper on data extraction (Carlini et al. 2023-style) that predicts per-example extraction probability.

## Q4. Conditioning, guidance and memorization

### Takeaway
Guidance theory shows that CFG does not sample the tilted distribution (it acts as a predictor-corrector), and that guidance applied inside an attraction basin causes memorization, which can be mitigated by delaying guidance. Conditioning theory at the exact empirical optimum is thin. Gu et al. report empirically that random labels raise memorization. López Amado et al. show that captions raise per-example mass and critical scale. Nothing found studies label averaging, or CFG on a label-averaged field producing blends above a threshold.

### Cited Findings
- **Jain et al. (NYU and Sony AI), "Classifier-Free Guidance Inside the Attraction Basin May Cause Memorization", CVPR 2025 (pp. 12871-12879); arXiv 2411.16738. Published.**
  - Memorization comes from an attraction basin in the denoising dynamics that pulls trajectories to a memorized image. High text-conditioned noise predictions form the basin.
  - Mitigations:
    - Apply CFG only after an "ideal transition point" where the trajectory leaves the basin.
    - "Opposite guidance", to leave the basin sooner.
  - [CVF open access](https://openaccess.thecvf.com/content/CVPR2025/html/Jain_Classifier-Free_Guidance_Inside_the_Attraction_Basin_May_Cause_Memorization_CVPR_2025_paper.html); [arXiv](https://arxiv.org/html/2411.16738v1)
- **Bradley & Nakkiran, "Classifier-Free Guidance is a Predictor-Corrector", NeurIPS 2024 M3L workshop (oral); arXiv 2408.09000. Apple lists a later TMLR version, not confirmed here.**
  - CFG does not sample the gamma-powered (tilted) distribution. It is equivalent to alternating denoising with Langevin-like sharpening.
  - [arXiv](https://arxiv.org/pdf/2408.09000); [Apple research page](https://pr-mlr-shield-prod.apple.com/research/predictor-corrector); [workshop record](https://mlanthology.org/neuripsw/2024/bradley2024neuripsw-classifierfree)
- **Chidambaram et al., "What does guidance do? A fine-grained analysis in a simple setting", arXiv 2409.13074 (Sep 2024).**
  - Venue not confirmed by my search. I believe it appeared at NeurIPS 2024, but this is not verified.
  - In simple mixture settings, guidance pushes samples toward the boundary or extremes of the conditional support rather than sampling the tilted distribution.
  - [arXiv PDF](https://web3.arxiv.org/pdf/2409.13074)
- **Gu et al. (TMLR 2025):** conditioning on uninformative random labels significantly increases memorization (empirical). [arXiv](https://arxiv.org/html/2310.02664v2)
- **López Amado et al. (arXiv 2609.39648), Corollary 7:** conditioning raises an example's critical scale if and only if it raises the model's mass on that example. [arXiv HTML](https://arxiv.org/html/2609.39648v1)
- **Liu et al. (arXiv 2512.02826)** use the navigation/refinement split to motivate CFG intervals, i.e. guidance only in a limited time window. [arXiv HTML](https://arxiv.org/html/2512.02826v2)
- **Not re-verified this session (prior knowledge):**
  - Wen et al., "Detecting, Explaining, and Mitigating Memorization in Diffusion Models", ICLR 2024 (oral). Text-conditional noise-prediction magnitude flags memorized prompts.
  - Somepalli et al., "Diffusion Art or Digital Forgery?", CVPR 2023 (arXiv 2212.03860).
  - Somepalli et al., "Understanding and Mitigating Copying in Diffusion Models", NeurIPS 2023 (arXiv 2305.20086). Caption duplication and specificity drive copying.
  - Carlini et al., "Extracting Training Data from Diffusion Models", USENIX Security 2023 (arXiv 2301.13188).

### Inferences
- The user's results fill an open slot: an exact-optimum analysis of conditioning compositions showing that label noise, label averaging and CFG only reweight training atoms, plus a threshold for blends under CFG on a label-averaged field.
- Jain et al. and López Amado et al. both support the "reweighting / basin mass" reading, which the user can cite as consistent prior evidence. Neither proves the composition or threshold result.

### Gaps
- I did not re-verify the venues and URLs of Wen et al. 2024, Somepalli et al. 2023 (both papers), Carlini et al. 2023, or Chidambaram et al. 2024 in this session.
- I found no work on label averaging or label smoothing at the exact empirical optimum of conditional flow matching.
