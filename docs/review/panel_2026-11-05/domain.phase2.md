contract_role: domain
## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: warn
trigger: "image-scale interpretation stated more strongly than the measurement supports"

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

Reviewer identity: researcher on memorisation and generalisation in diffusion and flow-matching models (closed-form and empirical-optimal denoisers, classifier-free guidance, image-scale memorisation studies). Calibration status: `NOT_CALIBRATED`. criteria_binding_unavailable, so this report makes no venue-alignment claim.

Summary. The domain content I checked is correct. The empirical conditional minimiser at an identifying label, its Nadaraya–Watson form under Gaussian label noise, and the classifier-free guidance (CFG) convention all match the standard closed-form analysis. I also re-derived the two-atom threshold myself. With averaged prior log-odds ±2B, the composite mean is the one in Eq. (6). Its slope at the tie, (1+w) sech²B − w, is negative exactly when w > 1/sinh²B. The paper is honest about what is already known. The Nadaraya–Watson endpoint is presented as a reference, not as a new result, and the abstract and limitations do not claim that trained networks behave like the exact field.

The paper adds three things that are new as far as I know:
- the composition result: guidance applied to a label-averaged field can send positive mass to a circumcentre, with an exact threshold;
- the spectral criterion in any dimension;
- the conditional transfer bound, along with the observation that small loss does not fix the endpoint.

My concerns are about how far these results bear on real samplers:
- The bridge "label averaging = coarse label resolution" is asserted, not shown.
- The only trained networks that reproduce the off-atom basin receive an input built around the known tie location.
- The off-atom samples the U-Net actually produces at h > 0 are left unexplained.
- Image-scale wording is sometimes stronger than the evidence, and some closely related literature is missing.

Taken together, the paper characterises an idealised object rigorously. It does not yet explain the off-atom or CFG-related phenomena seen in trained models.

### S1: Accurate positioning of the known endpoint law
The paper credits Baptista et al. (2025) and Dasgupta et al. (2026) for the empirical conditional law and treats the Nadaraya–Watson endpoint (Theorem 3.4) as a baseline, not a contribution. This is the correct reading of the closed-form literature, and it keeps the novelty claim confined to the intervention results.
**Evidence Anchor**: text: Section 1, Related work, "is therefore a reference, not a new identity"

### S2: A genuinely new and sharp composition result
To my knowledge, no published work shows that composing two operations, each of which keeps the endpoints on the atoms, yields a positive-probability non-training endpoint with a closed-form threshold. The two operations are positive label averaging and nonnegative CFG, and the threshold is w > 1/sinh²B. The derivation is consistent with the standard posterior-mean form of the empirical field. The result is robust to perturbing the priors and the weights (Proposition B.6, Table 10). It extends to a spectral test in any dimension (Theorem 4.7, Table 9).
**Evidence Anchor**: equation: Section 4.3, Eq. (6), slope (1 + w) sech²B − w at s = 0

### S3: Correct CFG convention and clear scope of the guidance results
The guided field is written in the standard Ho & Salimans form, and the paper says exactly why the positive-mixture theorem cannot cover w > 0. This avoids the w versus 1+w ambiguity that is common in this literature.
**Evidence Anchor**: text: Section 4.2, "For a guidance strength w the guided field is vw = (1 + w)vh⋆ − wvu⋆nc"

### S4: The loss-versus-endpoint observation is well supported and useful to the field
The learned-composition ablation shows that the velocity network has the smaller held-out loss near t = 1 yet misses the boundary layer at the tie. This gives concrete support, in a CFM setting, to the general warning (Benton et al., 2024) that regression loss alone does not control the sampler's endpoint.
**Evidence Anchor**: text: Appendix E.3, "Small loss does not decide the endpoint, as Section 5 anticipates"

### S5: The class-label CIFAR-10 control addresses a practically relevant case
The class-conditional U-Net experiment shows that a shared class label removes collapse onto one image but leaves the generated variance near the within-class scatter of the exact empirical law. This is the regime of real class-conditional models, and it is checked against the correct exact reference.
**Evidence Anchor**: text: Appendix E.2, "labels therefore remove the collapse onto one image but not the restriction to training images of the"

### S6: Calibrated abstract
The abstract says plainly that the trained-network observations do not establish asymptotic endpoint convergence. This is the right caution, given Proposition C.2(a): standard velocity MLPs cannot have atomic endpoints.
**Evidence Anchor**: text: Abstract, "these observations do not establish"

### W1: "Label averaging" as the model of coarse label resolution is asserted, not supported
**Problem**: The introduction states as fact that a network which resolves labels only coarsely averages the exact field over nearby labels. The real-sampler relevance of the headline composition result (Theorems 4.6 and 4.7) rests on this sentence. It has no citation and no direct evidence. The paper's own pilot (Appendix E.3, Table 8) reports that learned label averages need not follow the exact ones, with discrepancies that grow with the averaging radius. The positive-field-mixture form ∫ v_p Π(dp) is one possible idealisation. A network's failure to resolve labels could just as well look like the field of a mixed prior, which the paper shows is a different intervention with different atom assignments, or like a smoothing in x rather than in y.
**Why it matters**: If coarse label resolution does not act as a positive mixture of exact fields, then "guidance after label averaging" is not the object a real CFG sampler applies, and the composition mechanism loses its claimed link to practice.
**Suggestion**: Present the averaging model as a hypothesis. Test it directly: fit a network with limited label capacity, for example a bottlenecked label embedding, and compare its field with both v_φ and the mixed-prior field. Or cite empirical evidence for this form.
**Evidence Anchor**: text: Section 1, "that resolves labels only coarsely averages the field over nearby labels"
**Severity**: Major
**Confidence**: 4 — core expertise: empirical-optimal fields and conditioning in diffusion/flow models

### W2: The networks that reproduce the off-atom basin are given a tie-centred input
**Problem**: The extra input asinh(tx/(1 − t)²) is the blow-up coordinate s of the tie at z = 0. In both the two-atom and triangle configurations the tie sits at the origin, so this feature encodes where the tie is. Standard velocity CFM networks place essentially no mass at the midpoint at B ∈ {1, 2} or on the triangle. The ablation shows that the input, not the parametrisation, decides the outcome. The main text and abstract describe the input as one that "resolves the scale (1 − t)²". They do not say that building it requires knowing z, which a practical network would not know for an unknown tie among N atoms.
**Why it matters**: The evidence that trained networks can realise the composite basin is therefore evidence for networks with privileged geometric information. For standard trained CFM networks, the experiments point the other way: the mechanism does not appear. Readers in the memorisation literature will read the abstract sentence as a statement about trained networks in general.
**Suggestion**: State in Section 6.2 and the abstract that the input is centred at the known tie. Add a control with a tie-agnostic feature, for example an input at the scale 1/(1 − t)² applied to all coordinates without centring, or a learned rescaling. Report standard-CFM failure as a finding in its own right.
**Evidence Anchor**: text: Section 6.2, "receives the blow-up coordinate asinh(tx/(1 − t)2) as an extra input"
**Severity**: Major
**Confidence**: 4 — core expertise; the inference that the feature is tie-centred follows from the stated formula and the tie at z = 0

### W3: Off-atom samples and CFG-related memorisation in real models remain unexplained
**Problem**: The paper asks "which interventions … can move its endpoints off the training set". The one place where a realistic model does produce off-atom samples is the CIFAR-10 U-Net at h = 4–6. There, 0.16–0.30 of samples are off-atom after solver and cutoff refinement, while the exact field produces none, and no guidance or averaging is applied. The paper explicitly declines to attribute these samples. It also does not engage the established explanations for how trained networks leave the empirical optimum: locality and equivariance inductive biases (Kamb & Ganguli, 2025, which is cited but only as evidence of memorisation) and the training-time memorisation dynamics reported by Bonnaire et al. On the CFG side, the guidance results show that the exact field stays on atoms, but the endpoint weights are not identified. So the paper cannot say whether guidance concentrates mass on fewer training examples, which is the effect Jain et al. (2025), Somepalli et al. (2023, NeurIPS) and Wen et al. (2024) report in trained models.
**Why it matters**: The paper's contribution to understanding real samplers is mostly negative: label noise, mixtures and guidance alone do not explain off-atom samples in the exact field. The composition mechanism is not observed in standard networks (W2). As written, the work treats an idealised object and leaves the observed phenomena open.
**Suggestion**: Add a paragraph that sets the measured U-Net off-atom fractions against the locality and inductive-bias explanation, for example by checking whether off-atom completions are patch-wise composites of training images. Say explicitly that the guidance theorems are silent on the strength of CFG-induced memorisation. If possible, quantify how w changes the endpoint weights q̃ in the exact field.
**Evidence Anchor**: text: Appendix C.4, "so it need not have the integrable global Lipschitz constant of Proposition C.2(a), and we do not"
**Severity**: Major
**Confidence**: 4 — core expertise: image-scale memorisation studies

### W4: The exact CIFAR-10 composition confirms a reduction, not image-scale behaviour
**Problem**: The abstract and introduction present the CIFAR-10 composition as confirming the threshold "on pairs of CIFAR-10 images". The construction has several designed features:
- the eight pairs are selected as mutual nearest neighbours whose midpoint is far from every other image;
- h is set to |y_i − y_j|/2 so that B = 1;
- averaging uses exactly the two labels of the pair;
- each trajectory is handed off once the posteriors concentrate on the pair, and from there the flow "is exactly the one-dimensional flow" of Theorem 4.6.

Under these conditions the threshold is guaranteed analytically. The informative output is how much mass reaches the pair at all (0.06–0.96 at w = 0), not the threshold.
**Why it matters**: Readers may take "holds unchanged on CIFAR-10" as evidence about image models, when it is an exact-field consistency check in a tuned configuration.
**Suggestion**: Reword the abstract and Section 1 to say that this is an exact-field check on selected, isolated pairs, and report the pair-selection rate among all pairs.
**Evidence Anchor**: text: Section 1, "The threshold holds unchanged on pairs of CIFAR-10 images"
**Severity**: Minor
**Confidence**: 4 — core expertise; based on the Appendix E.3 protocol description

### W5: Missing literature on compositional generation and theoretical analyses of CFG
**Problem**: The central qualitative message is that composing fields can produce samples outside the support of each component. That is also the premise of compositional generation with diffusion models, where products or sums of conditional scores are used precisely to generate outside any single conditional (Liu et al., 2022; Du et al., 2023). These works are not cited. Theoretical analyses of CFG on Gaussian mixtures (Wu et al., 2024) and the predictor-corrector reading of CFG (Bradley & Nakkiran, 2024) are also missing. Chidambaram et al. (2024) is the only CFG theory cited. On memorisation timing, which bears on EXP-1's "tracks the posterior until ~10⁴ iterations, then collapses", Bonnaire et al. (2025) is directly relevant. On conditioning-driven replication in trained models, Somepalli et al. (2023, NeurIPS) and Wen et al. (2024) are relevant.
**Why it matters**: Positioning against these works would sharpen what is new: an exact threshold for the empirical field, as opposed to off-support composition in general. It would also tie the training-time collapse to known dynamics.
**Suggestion**: Add one or two sentences per strand in the related-work paragraph.
**Evidence Anchor**: absence: Section 1 related-work paragraph and reference list — expected discussion of compositional generation and theoretical CFG analyses beyond Chidambaram et al.; checked Section 1, Sections 4.2–4.3, Section 6.2 and the full reference list
**Severity**: Minor
**Confidence**: 4 — core expertise; references below are ones I am confident exist unless flagged

### W6: Some memorisation references are cited with narrower scope than their findings
**Problem**: Kadkhodaie et al. (2024) and Kamb & Ganguli (2025) are listed as showing that the empirical minimiser memorises. Their main contributions are about how trained networks generalise away from it: geometry-adaptive harmonic bases and the memorisation-to-generalisation transition with N, and locality and equivariance. Citing them only for memorisation understates the evidence that trained networks systematically depart from the exact field, which is the issue raised in W3.
**Why it matters**: A misread scope makes the gap between the exact-field theory and practice look smaller than the literature indicates.
**Suggestion**: Split the citation list: works on memorisation by the empirical optimum, and works explaining departure from it.
**Evidence Anchor**: text: Section 1, Related work, "That the empirical minimiser memorises is well established"
**Severity**: Minor
**Confidence**: 4 — familiar with both papers

### W7: "Realistic capacity" CIFAR-10 collapse sits in the known small-data memorisation regime
**Problem**: The h = 0 U-Net result uses N = 2000 images and identifying top-half labels. Kadkhodaie et al. (2024), cited in the paper, find that networks memorise at small training-set sizes and generalise only with much larger N. Collapse onto the training image here is therefore the expected outcome, not a test at realistic scale. The capacity is realistic; the data regime is not.
**Why it matters**: The heading invites the reading that hard-conditioning collapse holds for realistic image models. The data regime that would test this was not explored.
**Suggestion**: Rename the paragraph, for example "Small-data image regime", and either add a larger-N run or cite the small-N memorisation regime as the expected outcome.
**Evidence Anchor**: text: Section 6.1, "At realistic capacity. A standard DDPM U-Net (35.75M parameters)"
**Severity**: Minor
**Confidence**: 3 — core expertise; the field result is grounded in Kadkhodaie et al. (2024), but the transition N for 32×32 inpainting with identifying labels is not established

Missing key references (all are works I believe exist; venue or author details I am unsure of are flagged):
- Liu, Li, Du, Torralba, Tenenbaum, "Compositional Visual Generation with Composable Diffusion Models", ECCV 2022: composition of conditional fields beyond any single conditional.
- Du, Durkan, Strudel, Tenenbaum, Dieleman, Fergus, Sohl-Dickstein, Doucet, Grathwohl, "Reduce, Reuse, Recycle: Compositional Generation with Energy-Based Diffusion Models and MCMC", ICML 2023.
- Wu, Chen, Li, Wang, Wei, "Theoretical Insights for Diffusion Guidance: A Case Study for Gaussian Mixture Models", ICML 2024.
- Bradley, Nakkiran, "Classifier-Free Guidance is a Predictor-Corrector", arXiv 2024.
- Bonnaire, Urfin, Biroli, Mézard, "Why Diffusion Models Don't Memorize: The Role of Implicit Dynamical Regularization in Training", 2025 (I am fairly confident it appeared at NeurIPS 2025; please verify the venue).
- Somepalli, Singla, Goldblum, Geiping, Goldstein, "Understanding and Mitigating Copying in Diffusion Models", NeurIPS 2023.
- Wen, Liu, Chen, Lyu, "Detecting, Explaining, and Mitigating Memorization in Diffusion Models", ICLR 2024.
- Search lead [UNVERIFIED]: work on patch-based or local empirical denoisers as a mechanistic account of diffusion generalisation, for example by the Niedoba and Wood group (2024–2025).

~~~yaml suggested-references
- title: "Compositional Visual Generation with Composable Diffusion Models"
  authors: ["Liu, N.", "Li, S.", "Du, Y.", "Torralba, A.", "Tenenbaum, J. B."]
  year: "2022"
  doi: null
  arxiv_id: null
- title: "Reduce, Reuse, Recycle: Compositional Generation with Energy-Based Diffusion Models and MCMC"
  authors: ["Du, Y.", "Durkan, C.", "Strudel, R.", "Tenenbaum, J. B.", "Dieleman, S.", "Fergus, R.", "Sohl-Dickstein, J.", "Doucet, A.", "Grathwohl, W."]
  year: "2023"
  doi: null
  arxiv_id: null
- title: "Theoretical Insights for Diffusion Guidance: A Case Study for Gaussian Mixture Models"
  authors: ["Wu, Y.", "Chen, M.", "Li, Z.", "Wang, M.", "Wei, Y."]
  year: "2024"
  doi: null
  arxiv_id: null
- title: "Classifier-Free Guidance is a Predictor-Corrector"
  authors: ["Bradley, A.", "Nakkiran, P."]
  year: "2024"
  doi: null
  arxiv_id: null
- title: "Why Diffusion Models Don't Memorize: The Role of Implicit Dynamical Regularization in Training"
  authors: ["Bonnaire, T.", "Urfin, R.", "Biroli, G.", "Mézard, M."]
  year: "2025"
  doi: null
  arxiv_id: null
- title: "Understanding and Mitigating Copying in Diffusion Models"
  authors: ["Somepalli, G.", "Singla, V.", "Goldblum, M.", "Geiping, J.", "Goldstein, T."]
  year: "2023"
  doi: null
  arxiv_id: null
- title: "Detecting, Explaining, and Mitigating Memorization in Diffusion Models"
  authors: ["Wen, Y.", "Liu, Y.", "Chen, C.", "Lyu, L."]
  year: "2024"
  doi: null
  arxiv_id: null
~~~

Questions for authors:
1. Is asinh(tx/(1 − t)²) centred at the known tie in the triangle runs as well? What happens with a tie-agnostic rescaled input?
2. In the exact field, does increasing w ≥ 0 at h > 0 concentrate the endpoint weights q̃ on fewer atoms, as CFG-induced memorisation in trained models would suggest?
3. Are the off-atom U-Net completions at h = 4–6 patch-wise combinations of training images (the locality mechanism) or blends along the label kernel?
