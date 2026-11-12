# Parametrization, loss weighting, late-time drift and memorization in diffusion / flow models

Verification legend: [V] = content checked this session on the primary page (arXiv HTML, proceedings, or conference page). [K] = standard reference cited from prior knowledge; the arXiv ID/venue is well known but its content was NOT re-fetched this session. The report writer should treat [K] items as needing a quick check before they go into a paper.

## Q1. Do papers compare memorization across x0-, epsilon-, v-prediction or EDM preconditioning? What do they find?

### Takeaway
Until 2026 almost no paper varied the prediction target as a memorization factor. The main memorization studies hold the parametrization fixed (EDM preconditioning) and vary data, capacity, architecture, time embedding and training length. The one direct study is an ICML 2026 flow-matching paper, Al-Jaff et al. It reports that x-, epsilon- and v-targets memorize at different rates, with an ordering that holds even at matched FID. Its public abstract does not say which target memorizes most. Parametrization is known to change sample quality sharply: Li & He 2025 show that x-prediction works and epsilon/v-prediction fail on high-dimensional pixel patches. No paper found links memorization to the eigenvalues of the data-prediction Jacobian relative to 1.

### Cited Findings
- [V] Al-Jaff, Mehrpanah, Henter, Azizpour, Kragic, "What You Predict Shapes How You Memorize: Target-Parameterization and Memorization Dynamics in Flow Matching", ICML 2026 (published; no arXiv ID found). They compare clean-data x, noise epsilon and velocity v targets, sweeping training-set size and model capacity with architecture, optimizer, training budget, sampler and evaluation held fixed. The metrics are FID, nearest-neighbour memorization, and memorization at the best-FID checkpoint. Findings: the three targets "memorize at different rates and to different degrees". The ordering holds across sizes and capacities and persists at matched sample quality. "The prediction target that is best for sample quality is not necessarily the one that memorizes least." The target also shapes *when* memorization emerges during training, a connection the authors say no prior work established. The public abstract does not say which target memorizes most, and the OpenReview page (forum kzzlQzXldR) was behind a browser check — [ICML 2026 page](https://icml.cc/virtual/2026/70261); [OpenReview](https://openreview.net/forum?id=kzzlQzXldR)
- [V] Gu, Du, Pang, Li, Lin, Wang, "On Memorization in Diffusion Models" (arXiv 2310.02664; TMLR 2025). Experiments use EDM (Karras et al. 2022) with DDPM++ by default. The prediction target and loss weighting are NOT varied: the appendix shows score, epsilon and denoiser optima are equivalent, and lambda(t) appears only in derivations. Factors that do matter, measured by Effective Model Memorization (EMM):
  - Random Fourier time embedding (NCSN++) "significantly" reduces memorization compared with positional embedding (DDPM++). The same trend holds on FFHQ.
  - Skip connections: with full skips, NCSN++ memorizes about 45% and DDPM++ over 90% (1k images). Higher-resolution skips matter most.
  - Width raises EMM monotonically (about 4x from width 128 to 320). Depth is non-monotonic.
  - Weight decay of at least 5e-2 sharply cuts memorization (13.79% at 5e-2, 1.33% at 1e-1).
  - EMA rate has little effect.
  - Class labels, even random ones, increase memorization.

  — [arXiv HTML](https://arxiv.org/html/2310.02664v2); [TMLR listing](https://mlanthology.org/tmlr/2025/gu2025tmlr-memorization)
- [V] Li & He, "Back to Basics: Let Denoising Generative Models Denoise" (arXiv 2511.13720, Nov 2025, v2 Jan 2026; preprint). The paper argues for x-prediction because clean data lies on a low-dimensional manifold and noise does not. With the same v-loss on high-dimensional pixel patches, JiT-B/16 reaches FID 8.62 with x-prediction, versus 372.38 with epsilon-prediction and 96.53 with v-prediction. This is about quality, not memorization; the numbers come via search snippets of the paper — [arXiv](https://arxiv.org/abs/2511.13720)
- [V] Dodson, Gao, Wang, Wang, Wan, "Two Calm Ends and the Wild Middle: A Geometric Picture of Memorization in Diffusion Models" (arXiv 2602.17846, Feb 2026; preprint). It uses standard EDM and does not study parametrization or weighting. EDM trained on 1k CIFAR-10 images shows 92.2% trajectory-level memorization; trained on 50k it shows 0%. Per-noise-level memorization of the 1k model peaks at about 26% for sigma in [1.1, 5.3] and is near 0 at very small sigma, whereas the empirical optimal denoiser is about 100% memorizing for sigma < 0.3. Denoiser swapping: replacing the 1k model's denoiser with the 50k one only on sigma in [0.14, 8.4] drops memorization from 92.2% to 0%, and the reverse swap raises it from 0% to 92.2%. Swapping only sigma < 0.14 or sigma > 8.4 has little effect. Shells around training points become disjoint below about sigma 0.2 on CIFAR-10. There, many global minimizers of the loss exist (informal Thm 4.9), so behaviour depends on inductive bias. Removing training on sigma in [1, 5] cuts memorization on a 2k-image car subset from 78.8% to 0.7%, and FID improves from 3.72 to 2.35 — [arXiv HTML](https://arxiv.org/html/2602.17846v1)
- [V] Bonnaire, Urfin, Biroli, Mézard, "Why Diffusion Models Don't Memorize: The Role of Implicit Dynamical Regularization in Training" (arXiv 2505.17638; NeurIPS 2025 oral). There are two training timescales: one at which quality appears, which stays roughly fixed, and a later memorization time that grows with dataset size. Evidence comes from U-Nets plus a random-features theory. Parametrization is not the studied axis — [arXiv](https://arxiv.org/abs/2505.17638v2); [NeurIPS](https://neurips.cc/virtual/2025/poster/119372)
- [V] Flow-matching analyses with the optimal velocity:
  - "How Do Flow Matching Models Memorize and Generalize in Sample Data Subspaces?" (arXiv 2410.23594, preprint): under the optimal velocity field, generated samples memorize training points, and generalization comes from a suboptimal velocity — [arXiv](https://arxiv.org/pdf/2410.23594)
  - Bertrand et al., "On the Closed-Form of Flow Matching: Generalization Does Not Arise from Target Stochasticity" (arXiv 2506.03719, preprint): generalization emerges when a limited-capacity network fails to approximate the exact velocity field — [arXiv](https://arxiv.org/html/2506.03719)
  - "The Generation Phases of Flow Matching: a Denoising Perspective" (arXiv 2510.24830) builds denoisers with different parametrizations and weightings and reports that they affect distinct temporal phases of generation (search snippet only; not fetched) — [arXiv](https://arxiv.org/html/2510.24830v1)
  - "From Navigation to Refinement" (arXiv 2512.02826) reports that the late refinement stage increasingly memorizes fine-grained details (snippet only) — [arXiv](https://arxiv.org/abs/2512.02826)
- [K] Reference works on parametrization and weighting (not memorization studies):
  - Karras, Aittala, Aila, Laine, "Elucidating the Design Space of Diffusion-Based Generative Models" (EDM), NeurIPS 2022. Defines c_skip, c_out, c_in, c_noise with c_skip = sigma_data^2/(sigma^2 + sigma_data^2) -> 1 as sigma -> 0, and loss weight lambda(sigma) = 1/c_out^2 — [arXiv 2206.00364](https://arxiv.org/abs/2206.00364)
  - Karras et al., "Analyzing and Improving the Training Dynamics of Diffusion Models" (EDM2), CVPR 2024. Magnitude-preserving layers, post-hoc EMA, learned per-sigma uncertainty weighting — [arXiv 2312.02696](https://arxiv.org/abs/2312.02696)
  - Salimans & Ho, "Progressive Distillation", ICLR 2022. Introduces v-prediction because epsilon-prediction breaks at low SNR in distillation — [arXiv 2202.00512](https://arxiv.org/abs/2202.00512)
  - Kingma & Gao, "Understanding Diffusion Objectives as the ELBO with Simple Data Augmentation", NeurIPS 2023. All objectives are weighted ELBOs over noise levels; parametrization equals a reweighting — [arXiv 2303.00848](https://arxiv.org/abs/2303.00848)
  - Lin, Liu, Li, Yang, "Common Diffusion Noise Schedules and Sample Steps are Flawed", WACV 2024. Zero terminal SNR needs v-prediction. This concerns the high-noise end, not t -> 1 — [arXiv 2305.08891](https://arxiv.org/abs/2305.08891)
  - Hang et al., "Min-SNR Weighting", ICCV 2023. Down-weights low-noise steps — [arXiv 2303.09556](https://arxiv.org/pdf/2303.09556)

### Inferences
- Before the 2026 Al-Jaff et al. paper, parametrization was treated as a quality and stability knob, not a memorization factor. A Jacobian-spectrum (mu vs 1) mechanism explaining *why* targets differ would be new, and could explain their ordering if their paper does not already. The user should obtain and read the full paper; it is the closest prior work.
- Gu et al.'s time-embedding effect (Fourier features memorize less than positional embeddings) is the nearest published evidence that how t enters the network changes memorization. It is consistent with, but not explained by, the user's asinh(t x/(1-t)^2) ablation. Gu et al. give no mechanism.
- Dodson et al.'s finding that very low sigma is "safe" in per-level memorization, with many minimizers there, fits a picture where the late-time outcome is set by inductive bias: borderline contraction near mu ≈ 1, as in c_skip -> 1 or velocity with a smooth embedding. Their swap experiment shows that late-sigma denoisers do not decide collapse in EDM. This is a potential tension with any claim that the late-time Jacobian alone decides collapse. Under EDM preconditioning the late-time map is near-identity, so it carries rather than creates the memorized state, which supports the user's "borderline mu -> 1" reading.

### Gaps
- Al-Jaff et al.'s ordering (which target memorizes most), datasets and numbers could not be read: OpenReview was blocked and no arXiv version was found.
- No paper found compares memorization under EDM preconditioning vs plain x0/epsilon/v at fixed architecture, or varies the loss weighting while measuring memorization (Min-SNR, EDM's 1/c_out^2, uniform). Dodson et al.'s "gap" training (dropping sigma in [1, 5]) is the only weighting-like intervention found.

## Q2. Singular behaviour of score/velocity Lipschitz constants as t -> 1 (sigma -> 0), and measured Jacobians/Lipschitz constants of trained networks there

### Takeaway
Yang et al. (ICLR 2024 oral) show that epsilon- and v-prediction networks have a Lipschitz constant *in time t* that blows up near the data end, and they measure it on trained networks (log-scale plots up to about 1e3). They do not study the Jacobian in x. Measurements of the x-Jacobian of trained denoisers exist mainly as eigen-analyses (Kadkhodaie et al. ICLR 2024) and, most recently, as a finite-time flow-map spectral diagnostic for flow matching (Wang 2026 preprint), which ties late-time contraction under data scarcity to memorization. No paper found compares the top eigenvalue of the symmetric part of the data-prediction Jacobian with 1, or links that comparison to collapse onto training points.

### Cited Findings
- [V] Yang, Feng, Zhang, Shen, Zhu, Huang, Zhang, Liu, Zhao, Zhou, Cheng, "Lipschitz Singularities in Diffusion Models", ICLR 2024 (oral):
  - The singularity is with respect to the time variable t near t = 0 (the data end in their convention), not the input x. The theory assumes the score is smooth in x, so the blow-up comes from schedules with dalpha/dt = 0 at t = 0 (linear, quadratic, cosine).
  - The main analysis covers epsilon-prediction. v-prediction "has a similar singularity problem" (App. C.2, Fig. A5). x0-prediction is not analysed.
  - Measured Lipschitz constants are plotted on a log axis spanning about 10 to 1000 near zero; no exact table is given.
  - The fix, E-TSDM, shares the time condition within sub-intervals near zero. It reduces FID of DDIM and DPM-Solver by over 33%, and EDM CIFAR-10 FID goes from 1.904 to 1.797 (no Lipschitz measurement for EDM).

  — [ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/hash/3aff334b139550ffffed3f4e2498d43b-Abstract-Conference.html); [full text](https://object.cloud.sdsc.edu/v1/AUTH_da4962d3368042ac8337e2dfdd3e7bf3/ml-papers-txt/ICLR/2024/lipschitz_singularities_in_diffusion_models__65aefd09.txt)
- [V] Kadkhodaie, Guth, Simoncelli, Mallat, "Generalization in diffusion models arises from geometry-adaptive harmonic representations", ICLR 2024 (oral):
  - Two denoisers trained on disjoint subsets learn nearly the same score once N is about 1e5.
  - Bias-free denoisers are locally linear. The eigendecomposition of the denoiser Jacobian gives an adaptive basis, and the eigenvalues set how much of each component is kept. MSE trades off Jacobian rank (sum of eigenvalues) against residual error.

  This is the main published measurement of trained-denoiser Jacobian spectra across noise levels, but it is not tied to a threshold at 1 or to collapse — [arXiv](https://arxiv.org/abs/2310.02557v1); [ICLR](https://dev.iclr.cc/virtual/2024/oral/19783)
- [V] Shuchan Wang, "The Geometry of Memorization: Finite-Time Spectral Sensitivity as a Diagnostic for Flow Matching Models" (arXiv 2607.12616, Jul 2026; preprint, single author):
  - Defines FTSS g(t) as the RMS singular value of the flow-map state-transition matrix Phi(1, t), built from the spatial Jacobian of the velocity field and estimated by forward finite differences.
  - Reports g(t) > 1 early (expansion) and g(t) < 1 late, t -> 1 (contraction toward targets). Under data scarcity there is a "spectral collapse" at this late-stage bottleneck, attributed to rank collapse.
  - The ratio M = g_min / g_min^full rises with N and reaches about 1 for N >= 1000 (MNIST, CIFAR-10/100, Imagenette).
  - No AUC or threshold is reported, the method needs a full-data reference model, and only the velocity parametrization is used.

  This is the closest prior work to "late-time contraction decides memorization", measured on trained networks — [arXiv HTML](https://arxiv.org/html/2607.12616)
- [V] Ning et al. (see Q3) report that epsilon-prediction loss near t = 0 is "larger than other timesteps by several orders of magnitude", which is evidence of poor low-noise epsilon fits — [arXiv HTML](https://arxiv.org/html/2308.15321v6)
- [K] Theory of the score blow-up as sigma -> 0 (not re-fetched):
  - Pidstrigach, "Score-Based Generative Models Detect Manifolds", NeurIPS 2022 — [arXiv 2206.00667](https://arxiv.org/abs/2206.00667)
  - Stanczuk et al., "Diffusion Models Encode the Intrinsic Dimension of Data Manifolds", ICML 2024. Uses the score Jacobian spectrum at small t to estimate local dimension — [arXiv 2212.12611](https://arxiv.org/abs/2212.12611)
  - Wang & Vastola, "The Unreasonable Effectiveness of Gaussian Score Approximation..." / Wang et al., "Understanding Generalizability of Diffusion Models Requires Rethinking the Hidden Gaussian Structure", NeurIPS 2024. Trained denoisers are close to linear (Gaussian) denoisers in the generalization regime — [arXiv 2410.24060](https://arxiv.org/abs/2410.24060)

### Inferences
- In data-prediction form, an x-Jacobian of the denoiser near identity at sigma -> 0 (EDM c_skip -> 1; velocity nets) is the network-side counterpart of the score's 1/sigma^2 singularity. Yang et al. address only t-Lipschitzness, Kadkhodaie only spectra without a threshold, and Wang 2026 only the integrated flow map. The specific "top eigenvalue of the symmetric part of the denoiser Jacobian vs 1" criterion, with a parametrization-dependent limit, appears not to be published.
- Wang 2026 is concurrent and close in spirit: late contraction plus data scarcity leads to memorization. Distinctions to stress:
  - local denoiser-Jacobian eigenvalue vs integrated flow-map singular values;
  - an explicit threshold at 1 and its parametrization dependence;
  - a per-sample rather than per-model diagnostic;
  - no full-data reference model needed.

### Gaps
- No measurement found of the trained denoiser's x-Jacobian (or Lipschitz constant in x) specifically as sigma -> 0 compared across parametrizations.
- No analysis of Lipschitz singularities for x0-prediction or EDM preconditioning was found; Yang et al. explicitly skip x0.

## Q3. Exposure bias and late-time error accumulation; per-sample links to novelty or near-copies

### Takeaway
Exposure bias is well documented. Ning et al. (ICLR 2024) find the train/sample variance mismatch grows toward the end of sampling and fix it with a scalar epsilon rescaling. Li et al. 2023 fix it by shifting time steps. These works are dataset-level and do not discuss memorization. No paper found ties per-sample accumulated trajectory error to whether a sample is novel or a near-copy. The closest per-sample late-trajectory signal is Aithal et al. (NeurIPS 2024), who use variance over the last sampling steps to flag hallucinations rather than copies.

### Cited Findings
- [V] Ning, Li, Sangineto, Porrello, Calderara, Cucchiara, "Elucidating the Exposure Bias in Diffusion Models", ICLR 2024:
  - Metric: delta_t = (sqrt(beta'_t) - sqrt(beta_bar_t))^2, comparing the sampling-time variance of x_t with the training variance. "The closer to t=1 (the end of sampling), the larger the variance error of multi-step sampling."
  - The norm of epsilon predicted on sampled states exceeds the norm on ground-truth x_t, and the ratio Delta N(t) is used as the accumulated-error measure.
  - Epsilon Scaling divides epsilon by lambda_t; in practice lambda is constant. It corrects magnitude, not direction.
  - On EDM, epsilon is extracted from the denoiser. Gains are larger with Euler than with Heun.
  - There is no per-sample or memorization analysis. ADM-ES reaches CIFAR-10 FID 2.17 (100 steps).

  — [arXiv HTML](https://arxiv.org/html/2308.15321v6); [ICLR](https://iclr.cc/virtual/2024/poster/17461)
- [V] Li, Qu, Sun, Moens, "Alleviating Exposure Bias in Diffusion Models through Sampling with Shifted Time Steps" (arXiv 2305.15583; ICLR 2024 per our knowledge [K] — venue not re-checked). At each step it picks a time step better matched to the current state's variance; training-free, used with DDIM/DDPM — [arXiv](https://arxiv.org/abs/2305.15583v1)
- [V] Tsonis et al., "Mitigating Exposure Bias in Discriminator Guided Diffusion Models" (arXiv 2311.11164). Combines discriminator guidance with Epsilon Scaling, giving CIFAR-10 FID 1.73 — [arXiv](https://arxiv.org/pdf/2311.11164)
- [V] Aithal, Maini, Lipton, Kolter, "Understanding Hallucinations in Diffusion Models through Mode Interpolation", NeurIPS 2024. Models interpolate between nearby modes, which the authors attribute to a too-smooth learned score near discontinuities. High variance of the trajectory in the final few backward steps flags hallucinations, and a simple variance metric removes over 95% of them while retaining most in-support samples — [NeurIPS](https://proceedings.neurips.cc/paper_files/paper/2024/hash/f29369d192b13184b65c6d2515474d78-Abstract.html); [arXiv](https://arxiv.org/abs/2406.09358)
- [V] Dodson et al. 2026 (Q1): memorization formed at medium sigma propagates along the inference trajectory into small sigma, shown via denoiser swaps — [arXiv HTML](https://arxiv.org/html/2602.17846v1)

### Inferences
- Exposure-bias literature and memorization literature are disconnected. A per-sample analysis showing that late-time trajectory error (or its contraction) separates near-copies from novel samples would be a new bridge. Aithal et al. is the natural baseline for "late-trajectory variance as a per-sample signal", but it targets hallucination, the opposite failure from copying.
- Ning et al.'s observation that error grows toward the end of sampling, together with Lipschitz singularities near the data end, is consistent with the user's 1/(1-t) contraction framing. Neither paper uses a contraction or eigenvalue argument.

### Gaps
- No study found that measures exposure bias per sample and correlates it with nearest-neighbour distance to training data.
- No study found that tests whether exposure-bias fixes (Epsilon Scaling, time shift) change memorization rates.

## Q4. Trajectory-error or denoiser-error measurements as memorization detectors at inference, and simple baselines

### Takeaway
Inference-time memorization detection is dominated by text-conditional signals for Stable Diffusion: the norm of the conditional minus unconditional noise prediction (Wen et al., ICLR 2024), refined for the low-noise regime by an anisotropy/cosine term (Asthana & Belagiannis, ICLR 2026). For unconditional models, membership-inference work localizes leakage at intermediate interpolation times, not at the data end. A spectral flow-map diagnostic (Wang 2026) is per-model. Standard memorization labels use nearest-neighbour distance ratios. No paper found uses the denoiser Jacobian eigenvalue as a per-sample copy detector for unconditional models.

### Cited Findings
- [V] Wen, Liu, Chen, Lyu, "Detecting, Explaining, and Mitigating Memorization in Diffusion Models", ICLR 2024 (oral). The detection metric is the magnitude of the text-conditional noise prediction, ||eps(x_t, c) - eps(x_t, empty)||, averaged over steps. Memorized prompts have larger magnitudes. It also supports token attribution and mitigation (prompt-embedding perturbation, data filtering) — [ICLR proceedings PDF](https://proceedings.iclr.cc/paper_files/paper/2024/file/993760d9b1d63a385611c7c9ef8f3ecb-Paper-Conference.pdf); [mlanthology](https://mlanthology.org/iclr/2024/wen2024iclr-detecting)
- [V] Asthana & Belagiannis, "Detecting and Mitigating Memorization in Diffusion Models through Anisotropy of the Log-Probability", ICLR 2026 (arXiv 2601.20642). Norm-based detectors assume an isotropic log-probability, which holds at high and medium noise and fails at low noise, where it is anisotropic. Their metric combines the guidance-vector norm at high noise with the cosine between the guidance vector and the unconditional score at low noise. It is denoising-free (pure-noise input, two forward passes), beats prior denoising-free detectors on SD v1.4/v2, and is at least about 5x faster than the previous best — [arXiv](https://arxiv.org/abs/2601.20642); [ICLR slides](https://iclr.cc/media/iclr-2026/Slides/10010388.pdf)
- [V] Sesmat, Meseguer-Brocal, Peeters, "Where Rectified Flows Leak: Characterising Membership Signals Along the Interpolation Path" (arXiv 2606.07271, Jun 2026; preprint):
  - Uses a velocity-parametrized rectified flow. The train/test reconstruction gap vanishes at both ends and peaks at intermediate lambda, with closed form lambda* = sigma0^2/(sigma0^2 + sigma1^2) under isotropic Gaussian assumptions. Predicted 0.52 vs observed 0.5–0.6 on MAESTRO; predicted 0.45 vs observed 0.6–0.7 on CelebA (prediction fails).
  - MIA AUC on MAESTRO: naive single-lambda 0.67, SecMI 0.72, PIA 0.83, their lambda-resolved MLP 0.91.

  — [arXiv HTML](https://arxiv.org/html/2606.07271v1)
- [V] Wang 2026 FTSS (Q2): per-model spectral-collapse ratio; needs a full-data reference; no AUC reported — [arXiv HTML](https://arxiv.org/html/2607.12616)
- [V] Dodson et al. 2026 and Gu et al. 2023 label memorization with nearest-neighbour distance criteria; Gu et al. use the ratio of distances to the first and second nearest training neighbours (the standard "1/3 ratio" test, [K] for the exact threshold) — [Gu et al.](https://arxiv.org/html/2310.02664v2); [Dodson et al.](https://arxiv.org/html/2602.17846v1)

### Inferences
- Simple baselines the user should report against:
  - nearest-neighbour distance (or ratio) of the predicted x0 at an intermediate or late step;
  - the Wen-style norm of the network output (for unconditional models, an epsilon-norm or denoiser-residual norm);
  - Aithal-style late-trajectory variance.

  Membership-inference results suggest that the strongest train/test signals sit at intermediate times, so a late-time Jacobian detector should be compared against intermediate-time baselines. Asthana & Belagiannis's point that low-noise geometry is anisotropic supports using a Jacobian-spectrum (direction-aware) statistic rather than a norm at low noise. That is partial prior support for, and a nearby competitor to, a mu-based detector.

### Gaps
- No published AUCs found for per-sample copy detection in unconditional CIFAR-10/EDM models using denoiser-error or Jacobian statistics; the Wen and Asthana detectors need text conditioning.
- Did not find 2025–2026 detectors explicitly based on x0-prediction drift across late steps; such work may exist but did not surface in searches.
