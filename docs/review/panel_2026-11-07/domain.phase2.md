contract_role: domain

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: warn
trigger: "relevant closely related work is missing without affecting the central claim"

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

Reviewing as Peer Reviewer 2 (domain: memorisation and generalisation in diffusion and flow-matching models, closed-form and empirical-optimal denoisers, classifier-free guidance, locality and patch-mosaic accounts). I did not try to check the proofs line by line. My review covers positioning, how relevant the setting is to real samplers, and whether the experimental conclusions stay within the data.

Overall domain assessment. The paper studies the exact empirical conditional flow-matching field and asks which sampler-side modifications can move endpoints off the training set: label noise, averaging over labels, classifier-free guidance and guidance schedules. As far as I can judge, the paper describes the closest prior work correctly. It is unusually careful to say what is a reference and what is new: the Nadaraya–Watson endpoint law is credited to Baptista et al. and Dasgupta et al., and the Liu and Zuazua convergence results get a statement-by-statement comparison. I found no central novelty claim that is already established in the literature the paper omits, and no key prior result that is misrepresented in a way the main conclusion depends on. So D2 does not reach block. It scores warn for two reasons. First, the main-text implication for the memorisation debate is not positioned against the established inductive-bias account of off-training samples, which is cited only in an appendix. Second, several closely related lines of work on conditioning perturbation and on guidance theory are missing. Neither changes a theorem; both affect how a domain reader will take the practical message.

Relevance to real samplers. The positive results (Theorems 4.1 and 4.5, Proposition 4.3, Corollary 4.4) describe the knobs practitioners actually use, and the conclusion that they reweight training examples rather than create new ones is a clean, useful statement about the exact field. The composition result (Theorem 4.6, Theorem B.10) is framed honestly as an existence result. Every piece of in-paper evidence on whether trained networks realise the field average it needs points the other way: a label bottleneck averages priors, not fields (Proposition B.6); learned label averages do not follow the exact ones (the Appendix E.3 pilot); and standard velocity CFM networks place almost no mass at the midpoint. The basin is reproduced only by a network that is given an input centred at the known tie. The paper says all of this. My concern is the residual framing, not concealment (W5).

Experiments. The CIFAR-10 hard-conditioning collapse of a 35.75M-parameter U-Net, the exact-composite check on eight CIFAR-10 pairs with all 2000 atoms present, and the learned-composition ablations (input versus parametrisation, off-tie centring, label bottleneck) are well designed for the questions they address. The authors explicitly decline to count the CIFAR pair check as new evidence for the threshold. The main gap from my angle is the off-atom CIFAR-10 samples at h > 0. These are the closest thing in the paper to "creative" samples from a real model, yet the paper leaves their attribution open, and the main text describes the appendix analysis as more than it is (W2).

### W1: Main-text implication for the memorisation debate is not positioned against the inductive-bias account of off-training samples
**Severity**: Major
**Evidence Anchor**: text: Section 1, lines 095–096, "a sample far from the training set therefore points" and "not to the sampler"
**Confidence**: 4 — the closed-form denoiser and locality literature is my core area
In the introduction and in the conclusion's Implications paragraph, the paper says that a sample far from the training set reflects "the error of the learned field near t = 1". In the current literature, the leading explanation for why trained diffusion models produce non-training samples although the empirical optimum memorises is that the network has structured inductive biases, chiefly locality and translation equivariance, together with geometry-adaptive representations. These biases make it approximate a different, well-defined denoiser (Kamb & Ganguli, 2025; Niedoba et al., 2024; Kadkhodaie et al., 2024). In that account the departure from the empirical field is a systematic, predictable mechanism. Calling it "error" is not neutral: it implies that a more accurate learner would memorise, which is one side of an active debate. The paper cites Kamb & Ganguli and Kadkhodaie et al. only in a list headed "That the empirical minimiser memorises is well established". That list misrepresents the main thesis of both works, which is about generalisation. Niedoba et al. appear only in Appendix C.4, as one of two untested accounts. The Appendix C.4 summary of these works (patch mosaics assembled from training patches at any position) is broadly accurate, but readers of the main text will not see it. The theorems are unaffected. The fix is to reposition the implication in Section 1 and Section 8: say that Theorem 5.1 locates where any non-memorising mechanism must act (the scaled late-time field error), and that the locality accounts are candidate structured forms of that departure. Also cite Kadkhodaie et al. and Kamb & Ganguli for what they show.

### W2: Image-scale support for the late-time-error attribution is by elimination, and the main text overstates what Appendix C.4 measures
**Severity**: Major
**Evidence Anchor**: text: Section 5, lines 355–356, "Appendix C.4 measures the" and "trajectory error on EXP-1 and the off-atom CIFAR-10 samples"
**Confidence**: 4 — based on reading Section 5, Section 6.1 and Appendix C.4 together
Section 5 says that Appendix C.4 measures the trajectory error on the off-atom CIFAR-10 samples. For EXP-1, C.4 does measure the error ∆ along learned trajectories (the K = m/r ratios). For CIFAR-10 it does not measure ∆ at all. It reports off-atom fractions under two integrator settings (for example 0.158 ± 0.031 to 0.254 ± 0.047 at h = 4 to 6), notes that the exact field has none, concludes that the samples "come from the learned field, not from the sampler", and ends with "the attribution remains open" because the checkpoints were not kept. The comparison with the exact field does rule out the sampler. It does not show that these samples arise through the mechanism of Theorem 5.1: a scaled error that persists up to t = 1. In addition, Theorem 5.1 is stated at an identifying hard label, and at h = 0 the U-Net has no off-atom samples. The off-atom samples all occur at h > 0, which only the local Proposition C.1 covers, and C.1 is conditional on entering a small ball. The practitioner-facing sentence in Section 8 therefore rests, at image scale, on an elimination argument plus the EXP-1 measurement in d = 2. This is the regime my card cares most about: whether the paper explains off-atom samples in a real model. At present it does not explain them; it shows only where they do not come from. The fix is to correct the Section 5 sentence and state the image-scale limitation in the Implications paragraph. Better still, measure (1 − t)|∆| along off-atom CIFAR trajectories from retrained checkpoints, using the exact field as the teacher.

### W3: Trained-model evidence that perturbing the conditioning reduces replication is not discussed
**Severity**: Minor
**Evidence Anchor**: absence: Section 1 Related work and Section 3 discussion after Proposition 3.6 — expected discussion of empirical work reporting that randomising or noising the conditioning signal reduces training-data replication in trained text-to-image diffusion models; checked Section 1 Related work, Section 3, Section 6.1, Appendix C.4, Appendix E.2, reference list
**Confidence**: 4 — this is a standard mitigation line in the memorisation literature
Proposition 3.6 and the surrounding text state that label smoothing "never generates new samples" for the exact field. Empirical work on trained text-to-image models reports that randomising captions or adding noise to text embeddings reduces copying (Somepalli et al., 2023, "Understanding and Mitigating Copying in Diffusion Models"). Wen et al. (2024) link memorisation to the magnitude of the text-conditional guidance signal and mitigate it at inference. These findings appear to sit in tension with the exact-field result. The paper's own framework resolves the tension, because Theorem 5.1 places any such effect in the learned field. Making that link explicit would be a genuine contribution to how the community reads these mitigations, and would keep readers from thinking the paper contradicts them.

### W4: The guidance-theory literature is thin
**Severity**: Minor
**Evidence Anchor**: absence: Section 1 Related work — expected theoretical analyses of classifier-free guidance as a modified sampling dynamics and of guidance against a second model; checked Section 1 Related work, Section 4.2, Section 4.3, Appendix B.1, reference list
**Confidence**: 3 — I know these works exist and are relevant; I am less sure how much each overlaps with the convergence statements
On guidance theory the paper cites only Chidambaram et al. (2024), Liu & Zuazua (2026) and the schedule papers. Several closely related analyses are missing. Wu et al. (2024) analyse diffusion guidance for Gaussian mixtures and show that it concentrates mass and reduces diversity, a population-level counterpart to "guidance decides which atom, not whether". Bradley & Nakkiran (2024) characterise what CFG actually samples. Autoguidance (Karras et al., 2024) guides a model against a degraded version of itself rather than against an unconditional model. That is a signed combination of two different fields, the setting in which the paper's spectral criterion (Theorem B.10) and its observation that some signed combinations of more than two fields leave the atoms would be most practically relevant. None of these changes a result, but discussing them would show where the guidance results sit in current guidance theory.

### W5: The practitioner framing of the composition result exceeds the evidence that trained models implement field averaging
**Severity**: Minor
**Evidence Anchor**: text: Section 1, lines 045–046, "a hypothesis we test in one form"
**Confidence**: 4 — based on Section 4.3, Proposition B.6, the Appendix E.3 pilot and the ablations
The introduction motivates field averaging as what "a network that resolves labels only coarsely may" do, and the abstract opens with the knobs "a practitioner turns". Yet each test in the paper of whether a network averages fields comes out negative or inconclusive. A label bottleneck averages priors and keeps the atoms (Proposition B.6 and the cfm x sq runs). The learned label-average pilot does not follow the exact averages. Standard velocity CFM networks place at most 0.001 of their sources at the midpoint, and an input centred away from the tie leaves the midpoint empty. Sections 4.3 and 8 already call this an existence result. The abstract and the introduction could say just as plainly that the composition is not known to arise in any practical sampler, so that the abstract does not read as a statement about real CFG pipelines.

### W6: The practically dominant regime of shared labels is treated only in an appendix
**Severity**: Minor
**Evidence Anchor**: text: Section 2, line 141, "Labels identify"
**Confidence**: 4 — class- and text-conditioned samplers almost always share labels across training examples
Assumption 1(iii) requires identifying labels. In real conditional samplers (class labels, shared captions) many training examples share a label. Appendix E.2 handles this correctly: the exact endpoint law becomes the within-class empirical law, and the U-Net with one-hot class labels keeps 0.62 to 1.30 of the within-class scatter. This is the result most directly relevant to the memorisation debate for class-conditional models. Two sentences in Section 3 or Section 6.1 stating it would make the scope of "collapse" clear to a domain reader: collapse is onto one image only when the label identifies it, and onto the empirical class otherwise.

### S1: Faithful, statement-level comparison with the closest convergence theorems
**Evidence Anchor**: table: Appendix B.1, Table 4
The comparison with Liu & Zuazua (2025; 2026) states each theorem's field, support, combination, trajectory hypothesis and conclusion. It says explicitly that the ODEs differ and that the comparison is between analogous statements, not an implication. It also records the open almost-everywhere question (their Remark 3.19) correctly. This is the right standard for crediting prior work.

### S2: Known results are credited as references rather than claimed as new
**Evidence Anchor**: text: Section 1, line 105, "is therefore a reference, not a new identity"
The Nadaraya–Watson endpoint law is attributed to Baptista et al. (2025, Theorem 6.4) and Dasgupta et al. (2026). Conditioning augmentation is credited to Ho et al. (2022) and its annealing to Sadat et al. (2024), and kernel readings of finite-support flows are acknowledged as known. I found no overclaiming of novelty in the exact-reference section.

### S3: The composition result is scoped honestly, with ablations that isolate what a network needs
**Evidence Anchor**: text: Section 4.3, line 311, "We read the theorem as an existence"
The learned-composition experiments separate the effects of input, output parametrisation and tie-centring (Table 12, Appendix E.3). They include a distillation positive control and an off-tie centring negative control, and they report solver failures rather than discarding them. The authors tie the outcome to Proposition C.2 (no endpoint atom for integrable Lipschitz constant), which gives a domain reader a concrete explanation of why standard velocity networks miss a basin at the (1 − t)^2 scale.

### S4: Exact-field consistency check at image dimension with all atoms present
**Evidence Anchor**: text: Appendix E.3, line 2746, "The computation is a consistency check of that prediction"
Applying the exact composite to eight CIFAR-10 pairs in d = 3072 with the other 1998 atoms in the field tests whether the two-atom picture survives in high dimension. The authors correctly decline to count it as new evidence for the threshold. Checking the off-atom CIFAR samples against all 50000 training images (Appendix C.4) also rules out the reading that they are near-copies of images outside the training subset.

### S5: Shared-label CIFAR-10 runs connect the theory to class-conditional practice
**Evidence Anchor**: text: Appendix E.2, line 2422, "Shared labels therefore remove the collapse onto one image"
The class-label experiment derives the within-class empirical law as the exact reference and shows that a trained U-Net stays at the scale of the within-class scatter. This is the observation most relevant to class-conditional memorisation in practice (see W6 on its placement).

### Missing Key References
- Somepalli et al. (2023), "Understanding and Mitigating Copying in Diffusion Models", NeurIPS 2023: conditioning randomisation as a copy mitigation in trained models (W3).
- Wen et al. (2024), "Detecting, Explaining, and Mitigating Memorization in Diffusion Models", ICLR 2024: links memorisation to the text-conditional guidance signal (W3).
- Wu et al. (2024), "Theoretical Insights for Diffusion Guidance: A Case Study for Gaussian Mixture Models", ICML 2024 (W4).
- Bradley & Nakkiran (2024), "Classifier-Free Guidance is a Predictor-Corrector" (W4).
- Karras et al. (2024), "Guiding a Diffusion Model with a Bad Version of Itself", NeurIPS 2024: guidance against a second model as a signed field combination (W4).

~~~yaml suggested-references
- title: "Understanding and Mitigating Copying in Diffusion Models"
  authors: ["Somepalli, G.", "Singla, V.", "Goldblum, M.", "Geiping, J.", "Goldstein, T."]
  year: "2023"
  doi: null
  arxiv_id: null
- title: "Detecting, Explaining, and Mitigating Memorization in Diffusion Models"
  authors: ["Wen, Y."]
  year: "2024"
  doi: null
  arxiv_id: null
- title: "Theoretical Insights for Diffusion Guidance: A Case Study for Gaussian Mixture Models"
  authors: ["Wu, Y."]
  year: "2024"
  doi: null
  arxiv_id: null
- title: "Classifier-Free Guidance is a Predictor-Corrector"
  authors: ["Bradley, A.", "Nakkiran, P."]
  year: "2024"
  doi: null
  arxiv_id: null
- title: "Guiding a Diffusion Model with a Bad Version of Itself"
  authors: ["Karras, T.", "Aittala, M.", "Kynkaanniemi, T.", "Lehtinen, J.", "Aila, T.", "Laine, S."]
  year: "2024"
  doi: null
  arxiv_id: "2406.02507"
~~~

### Questions for Authors
1. Under the locality and equivariance accounts, would the off-atom CIFAR-10 completions at h > 0 count as "error" in the sense of Theorem 5.1, or as a structured departure that Theorem 5.1 only bounds?
2. Is there any trained model, beyond networks given a tie-centred input, in which you would expect guidance to act on a field average rather than a prior average?
3. Can you measure (1 − t)|∆| along a few off-atom CIFAR trajectories from retrained h > 0 checkpoints, so that the main-text attribution rests on a measurement rather than on elimination?
