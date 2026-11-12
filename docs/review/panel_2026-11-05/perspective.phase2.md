contract_role: perspective
## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: warn
trigger: "a cross-field implication is stated in the discussion with hedging but no supporting evidence or explicit limitation"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Reviewer Identity and Calibration
Peer Reviewer 3 (cross-disciplinary): a nonparametric statistician (kernel smoothing, statistical learning theory) who also works on privacy and memorisation audits of deployed generative models. I am less familiar with ODE well-posedness arguments and flow-matching training practice, so I do not assess the proofs or the training protocols. Calibration status: `NOT_CALIBRATED`. No review-target criteria binding was supplied (`criteria_binding_unavailable`), so I make no venue-alignment claim.

### Summary Assessment
The paper characterises the endpoint law of the exact empirical conditional flow-matching field under label smoothing, positive field mixtures (label averaging, negative guidance), nonnegative classifier-free guidance (fixed or bounded-variation schedules) and their composition. The first three keep the endpoints on the training atoms almost surely; guidance applied to a label-averaged field can create a circumcentre atom with positive probability above an explicit threshold w > 1/sinh^2 B, with a spectral criterion in higher dimension. A conditional transfer bound ties a learned endpoint to the limiting scaled field error, and experiments range from a 2-D linear-Gaussian problem to a 35.75M-parameter CIFAR-10 U-Net.

From a statistician's seat, the paper is unusually legible: the exact field is correctly identified as a Nadaraya–Watson regression over atoms and is credited as a reference rather than claimed as new, the moment-versus-posterior distinction is made formally (a Wasserstein lower bound), memorisation is measured with a stated nearest-neighbour criterion, and the abstract and Limitations scope the learned-network evidence carefully. The weaknesses are in the adjacent-field implications rather than in the core statements: the practical meaning of the composition result for CFG users is not yet established by trained standard networks; the privacy reading in the Ethics statement and the "remedy" framing of endpoint noise use support as a proxy for leakage, which privacy auditing would not accept; and the fixed-N reading of the kernel reference omits the large-N and bandwidth-selection view that a statistical reader will bring. These call for reframing and a few targeted additions, not for new theory, hence warn on D4.

### S1: The kernel identity is placed correctly in the statistical literature
The paper names the exact positive-bandwidth field as a Nadaraya–Watson regression over the atoms, cites Nadaraya and Watson, and explicitly declines novelty for the identity, positioning it alongside prior kernel readings of finite-support flows. An adjacent reader can immediately map p_i^(h)(y) to Nadaraya–Watson weights and Corollary 3.5 to the familiar oversmoothing and undersmoothing limits.
**Evidence Anchor**: text: §1 Related work "is therefore a reference, not a new identity"

### S2: Moment matching is formally separated from posterior recovery
Proposition 3.6 gives an h-independent W2 lower bound whenever the posterior puts no mass on the atoms, and Table 5 and Figure 5(c) then show the practical trap: the generated trace can equal tr Covh, or even tr Σpost at h⋆ = 0.70, while the law stays atomic. This is precisely the "matching moments is not matching the law" caution that variance-based evaluations of conditional generators need, and it is stated as a theorem rather than as a slogan.
**Evidence Anchor**: equation: Eq. (4), Proposition 3.6 — W2 lower bound by the expected squared distance to the nearest atom, independent of h

### S3: Learned-network evidence is scoped honestly in the abstract and Limitations
The abstract states that the trained-network observations do not establish asymptotic endpoint convergence, and Section 7 lists that the theorems do not say a trained network implements the exact fields, that the composition basin depends on parametrisation, and that image experiments use one mask and N = 2000. I did not find a place where the main text overstates the learned evidence.
**Evidence Anchor**: text: Abstract "these observations do not establish"

### S4: The identifying-label assumption is probed with shared labels
Appendix E.2 drops Assumption 1(iii) by conditioning on the CIFAR-10 class, derives that the exact endpoint law becomes the within-class empirical law, and shows that the trained U-Net keeps 0.62–1.30 of the within-class scatter rather than collapsing. This directly answers the practical question of what changes when labels are shared: collapse onto one image disappears, restriction to training images of the class does not.
**Evidence Anchor**: dataset: CIFAR-10 class-label runs (Appendix E.2, Figure 9) — within-class scatter 717 retained at h = 0 and h = 0.4

### S5: Off-atom samples are checked against the full dataset
For the off-atom CIFAR-10 samples the authors re-measure nearest-neighbour distances against all 50000 training images, not only the 2000 used, and refine the integrator and cutoff. This is the right control from an audit standpoint: it rules out that "off-atom" merely means "near another unused dataset image" and that it is a solver artefact.
**Evidence Anchor**: text: Appendix C.4 "Measured against all 50000 CIFAR-10 training images instead of the 2000"

### W1: Practical meaning of the composition result for CFG users is not established
**Problem**: Section 4.3 motivates the composite field as an idealisation of classifier-free guidance applied to a network that resolves labels coarsely, the setting a practitioner would recognise. But in Section 6.2 a standard velocity CFM network with condition dropout places at most 0.001 of sources at the midpoint at every guidance strength; the off-atom basin appears only with the hand-added input asinh(tx/(1 − t)^2), and the learned composition is tested only at d ≤ 2. The CIFAR-10 pair evidence for the threshold is exact-field only.
**Why it matters**: A CFG user or a memorisation auditor reading the abstract learns that composition "can" create non-training endpoints, while the evidence says that the networks they actually deploy do not exhibit this mechanism. Without a statement of which practical architectures are expected to resolve the (1 − t)^2 scale (for example data-prediction or preconditioned parametrisations used in practice), the composition result reads as a property of the idealisation rather than of guided samplers.
**Suggestion**: State in Section 4.3 and the conclusion that standard velocity networks did not reproduce the basin, and say which deployed parametrisations (if any) satisfy the resolution condition of Proposition C.2. One trained, image-scale composite run with a common parametrisation (for example an EDM-style preconditioned denoiser on the CIFAR-10 pairs) would turn the idealisation into a testable claim about practice; if that is out of scope, say so.
**Severity**: Major
**Evidence Anchor**: text: §4.3 "it idealises classifier-free guidance applied to a network that resolves labels only"
**Confidence**: 3 — adjacent field: memorisation audits; less familiar with flow-matching parametrisation practice

### W2: The privacy implication in the Ethics statement is not tied to an extraction or membership notion
**Problem**: The Ethics statement says that label noise, positive mixtures and nonnegative guidance do not move the exact field's endpoints off the training set, and that this is relevant for models trained on sensitive data. The statement concerns support of the exact endpoint law; privacy auditing reasons about extraction success under a distance threshold or about membership-inference advantage, and about trained models. The paper's own trained h > 0 networks place 16–25% of CIFAR-10 samples off-atom (Appendix C.4), so the exact-field atomicity does not translate directly into a statement about what a trained model leaks.
**Why it matters**: A reader from privacy could take the sentence as evidence about trained-model leakage in either direction. The useful, defensible message is narrower and negative: label smoothing, label averaging and bounded guidance are not privacy mechanisms at the population level, because the target they approximate is still atomic.
**Suggestion**: Rephrase the Ethics paragraph to state that narrower message and to say explicitly that the paper measures neither extraction rates nor membership advantage in trained models. Citing the extraction definition of Carlini et al. (2023), which the paper already references, and contrasting it with the relative nearest-neighbour criterion used here would make the boundary clear.
**Severity**: Minor
**Evidence Anchor**: text: Ethics Statement "which is relevant when conditional models are trained on sensitive data"
**Confidence**: 4 — core expertise: privacy and memorisation audits

### W3: Endpoint noise is framed as a remedy, but moving the support is not a privacy criterion
**Problem**: Appendix D introduces endpoint noise with the sentence that a remedy must move the support, and Table 1 singles it out as the only intervention that leaves the atoms in every configuration. At an identifying label the resulting law is N(x_i, ρ^2 I_d); averaging M samples at that label recovers x_i to accuracy of order ρ/√M, and the mean of (16) is the Nadaraya–Watson mean x̄_h(y) regardless of ρ.
**Why it matters**: A practitioner reading "remedy" may conclude that output noise addresses memorisation. Absolute continuity of the endpoint law is compatible with essentially complete reconstruction of training examples by repeated querying; the privacy-relevant quantity is a calibrated noise-to-sensitivity ratio, as in differential privacy, not the presence of a density.
**Suggestion**: Replace "remedy" with neutral wording (for example "an intervention that changes the support") and add one sentence noting that, at an identifying label, repeated sampling recovers the atom, so endpoint noise is not a privacy mechanism unless ρ is calibrated in the sense of differential privacy.
**Severity**: Minor
**Evidence Anchor**: text: Appendix D "a remedy must move the support"
**Confidence**: 4 — core expertise: privacy mechanisms and memorisation

### W4: The kernel reference is read only at fixed N; the large-N and bandwidth-selection view is missing
**Problem**: Corollary 3.5 gives the h → 0 and h → ∞ limits at fixed N, and Proposition 3.6 emphasises that the W2 lower bound does not depend on h. The lower bound is the expected squared distance from a posterior draw to its nearest training atom, a quantisation error that shrinks as N grows (for a density, at a rate of order N^(-2/d)); with h = h_N → 0 at a suitable rate, the Nadaraya–Watson-weighted empirical law is the classical consistent estimator of the conditional law. The paper discusses neither regime, nor how h would be chosen, although h is the central smoothing parameter.
**Why it matters**: A statistician will read "matching moments is not matching the posterior" as a fixed-sample statement whose size is the quantisation gap, which can be negligible for dense low-dimensional data (EXP-1, d = 2, N = 200) and large for CIFAR-10 at d = 3072. Without the magnitude, an adjacent reader cannot tell whether the gap is practically material, and the bias–variance trade-off visible in Table 5 (instability at n_eff ≈ 3.5 at h = 0.01, oversmoothing at h = 0.5) is left uninterpreted.
**Suggestion**: Report the numerical value of the right-hand side of (4) for EXP-1 and for the CIFAR-10 conditions, add two sentences relating the fixed-N statement to Nadaraya–Watson consistency as N → ∞ with h_N → 0, and note that n_eff plays the role of the effective local sample size in bandwidth selection.
**Severity**: Minor
**Evidence Anchor**: text: Proposition 3.6 "and this lower bound does not depend on h"
**Confidence**: 4 — core expertise: kernel smoothing and nonparametric consistency

### W5: The endpoint-noise law is a classical conditional kernel density estimator, uncited
**Problem**: Equation (16) is Σ_i p_i^(h)(y) N(x_i, ρ^2 I_d): a conditional kernel density estimator with label bandwidth h and response bandwidth ρ (Rosenblatt; Hyndman, Bashtannyk and Grunwald). The paper derives it without naming it.
**Why it matters**: Naming the estimator imports a body of results on joint selection of (h, ρ) by cross-validation and on its bias and variance, which would let the authors and readers reason about when endpoint noise trades fidelity for generalisation instead of treating ρ as a free knob.
**Suggestion**: Add one sentence after Proposition D.1 identifying (16) as the conditional KDE and citing the conditional-density-estimation literature.
**Severity**: Minor
**Evidence Anchor**: equation: Eq. (16), Proposition D.1 — endpoint law as a Nadaraya–Watson-weighted Gaussian mixture with bandwidth ρ
**Confidence**: 4 — core expertise: kernel density estimation

### W6: "Off-atom" is a relative criterion that does not distinguish novel samples from blends of training images
**Problem**: The CIFAR-10 on-atom criterion is a relative nearest-neighbour ratio (squared distance at most 1/9 of the second nearest), following Yoon et al. A sample midway between two training images, such as the circumcentre endpoints of Section 4.3, is "off-atom" under this rule, yet from a privacy standpoint it is a deterministic function of training images.
**Why it matters**: The Section 6.1 statement that 38% of h = 6 samples are off-atom can be read by adjacent readers as generalisation. The paper is careful to say it does not identify a limiting support, but it does not say that off-atom samples may still be close to a convex combination of a few training images.
**Suggestion**: Report, for the off-atom samples, the distance to the best convex combination of the two or three nearest training images (or the Nadaraya–Watson mean x̄_h(y)), which separates blends from genuinely new completions at negligible cost.
**Severity**: Minor
**Evidence Anchor**: dataset: CIFAR-10 on-atom criterion (Appendix E.2) — relative squared-distance ratio of 1/9 to the second-nearest training image
**Confidence**: 4 — core expertise: memorisation measurement

### Assumption Audit
- Explicit assumptions: fixed training set, linear interpolant, identifying labels (Assumption 1). These are stated where used, and the shared-label case is examined (S4). The linear-interpolant assumption is not stress-tested; I defer to the domain seat on whether the results extend to variance-preserving paths.
- Implicit assumptions: that support of the endpoint law is the relevant notion of memorisation (W2, W3), and that the fixed-N regime is the practically relevant one (W4). For conditional inpainting the identifying-label assumption is realistic, since observed halves are almost surely distinct; this makes the h = 0 theory directly relevant to practice, which the paper could say.
- Paradigmatic assumptions: the population-minimiser reference. The paper is explicit that it is a reference, not a model of trained networks.

### Cross-Disciplinary Reading Recommendations
- Stone (1977), consistency of nonparametric regression estimators including kernel weights: frames the large-N regime of the Nadaraya–Watson reference (W4).
- Rosenblatt (1969) and Hyndman, Bashtannyk and Grunwald (1996): conditional kernel density estimation, the classical name for (16) (W5).
- Hall, Racine and Li (2004): cross-validated bandwidth selection for conditional densities, relevant to choosing (h, ρ) (W5).
- Graf and Luschgy (2000): quantisation error rates, which give the size of the h-independent lower bound in (4) (W4).
- Dwork, McSherry, Nissim and Smith (2006): calibrated output noise, the right comparison for endpoint noise as a privacy mechanism (W3).
- Shokri, Stronati, Song and Shmatikov (2017): membership inference, the complementary audit notion to extraction (W2).

~~~yaml suggested-references
- title: "Consistent Nonparametric Regression"
  authors: ["Stone, C. J."]
  year: "1977"
  doi: null
  arxiv_id: null
- title: "Conditional probability density and regression estimators"
  authors: ["Rosenblatt, M."]
  year: "1969"
  doi: null
  arxiv_id: null
- title: "Estimating and Visualizing Conditional Densities"
  authors: ["Hyndman, R. J.", "Bashtannyk, D. M.", "Grunwald, G. K."]
  year: "1996"
  doi: null
  arxiv_id: null
- title: "Cross-Validation and the Estimation of Conditional Probability Densities"
  authors: ["Hall, P.", "Racine, J.", "Li, Q."]
  year: "2004"
  doi: null
  arxiv_id: null
- title: "Foundations of Quantization for Probability Distributions"
  authors: ["Graf, S.", "Luschgy, H."]
  year: "2000"
  doi: null
  arxiv_id: null
- title: "Calibrating Noise to Sensitivity in Private Data Analysis"
  authors: ["Dwork, C.", "McSherry, F.", "Nissim, K.", "Smith, A."]
  year: "2006"
  doi: null
  arxiv_id: null
- title: "Membership Inference Attacks Against Machine Learning Models"
  authors: ["Shokri, R.", "Stronati, M.", "Song, C.", "Shmatikov, V."]
  year: "2017"
  doi: null
  arxiv_id: null
~~~

### Questions for Authors
1. Which parametrisations used in deployed guided samplers (for example preconditioned denoisers) would satisfy the resolution condition under which a trained network reproduces the off-atom basin, and do you expect the composition effect to appear in them?
2. What is the numerical value of the lower bound in (4) on EXP-1 and on the CIFAR-10 conditions, and how would you expect it to scale with N?
3. In the CIFAR-10 hard-conditioning runs, does the iteration at which completions coincide with the training image (about 8000 at N = 2000) grow with N? This is the testable consequence most relevant to practitioners training on larger sets.
4. Are the off-atom CIFAR-10 samples at h = 4–6 close to the Nadaraya–Watson mean x̄_h(y) or to convex combinations of a few training images?

### Minor Issues
- The Ethics statement could point to Section 7 for the scope of the trained-network evidence.
- Table 1 could note that "a.s." is with respect to the source law, not the training sample, for readers who default to the sampling-distribution reading.
