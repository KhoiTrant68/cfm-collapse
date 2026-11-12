contract_role: eic

## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: warn
trigger: "frequent but non-essential appendix dependence"

### D6: venue_fit_and_contribution
score: warn
trigger: "significance for practical samplers is argued thinly"

## Review Body

Editorial summary. The submission studies where the exact empirical conditional flow-matching field and its sampler-side modifications send their endpoints. It proves that positive field mixtures (including label averaging and negative guidance) and nonnegative guidance with a fixed strength or a bounded, bounded-variation schedule end on a training atom for almost every initial point; that guidance applied to a label-averaged field can instead converge to a circumcentre of training atoms with positive probability, with an exact two-atom threshold w > 1/sinh^2 B and a spectral criterion in general dimension; and that a learned field at an identifying label ends within the limiting scaled field error of its atom. Experiments check the exact statements numerically, show finite-time collapse in trained networks up to a 35.75M-parameter U-Net, and show that only networks given the rescaled input asinh(tx/(1-t)^2) reproduce the off-atom basin.

From the Area Chair angle, the work fits ICLR: memorisation in diffusion and flow models, classifier-free guidance and label conditioning are live topics for this audience, and the paper is careful, honest about scope, and states its results precisely. The main text stays within nine pages and is organised so that Table 1 gives the full picture before any proof. The theory is not mine to verify step by step (that is the methodology seat's work), and I rely on the domain seat for whether prior memorisation results are described faithfully.

My two concerns are editorial rather than technical. First, the result that distinguishes this paper from the established "the empirical minimiser memorises" literature is the composition basin, and the paper itself argues that this basin is not expected in standard trained models and appears only with an input centred at the known tie. An ICLR reader will ask what they should do differently; the paper's answer (off-training samples point to late-time field error) is useful but is established only at an identifying label and is in visible tension with the image-scale results at positive bandwidth. Second, the main text leans on the appendix for the general-dimension statement, most of the supporting figures and tables, and the definitions needed to read Section 4.4. Neither concern reaches a block: the contribution is real and clearly delimited, and the main text is followable on its own for the two-atom headline.

### W1: The distinctive headline has no demonstrated route to practical samplers
**Severity**: Major
**Evidence Anchor**: text: §4.3 after Theorem 4.6 "not as a mechanism expected in standard trained models"
**Confidence**: 4 — area-chair judgement of ICLR significance in the memorisation and guidance literature

The positive theorems of Sections 4.1 and 4.2 refine a picture that the community already holds (the exact empirical field returns training examples), so the paper's novelty for the ICLR audience rests mostly on the composition result of Section 4.3 and its spectral extension. The authors frame that result, candidly, as an existence result: the basin lives at scale (1-t)^2 near the tie, Proposition C.2 rules out endpoint atoms for velocity networks with integrable Lipschitz constant, standard velocity CFM networks place at most 0.001 of sources at the midpoint, and the Conclusion adds that a label bottleneck does not even produce the averaged field. The successful network is given an input centred at the known tie, which a practitioner would not have. The paper therefore leaves the reader with an object whose practical relevance it argues against. To strengthen the case, the authors should state in the Introduction what a practitioner or a memorisation auditor can test or change because of this result (for example, whether the threshold or the boundary-layer scale predicts anything measurable in a standard model, or whether the asinh input is a design recommendation or only a probe), or else re-centre the headline on the positive and transfer results and present the composition as a boundary marker. The honesty of the current framing is a strength; the gap is that significance is asserted through scope limits rather than shown through a consequence.

### W2: The practical takeaway is stated more generally than the transfer theorem covers
**Severity**: Minor
**Evidence Anchor**: text: §1 closing paragraph "a sample far from the training set therefore points to the error of the learned field" and §6.1 "38% of the finite-cutoff samples are off-atom by the nearest-neighbour criterion"
**Confidence**: 3 — reading of the stated scope of Theorem 5.1 against the reported experiments

The abstract correctly qualifies the takeaway with "at an identifying label", but the Introduction and the Implications paragraph state it for standard models in general. Theorem 5.1 is a hard-conditioning statement, and Proposition C.1 at positive bandwidth requires the trajectory to enter a small ball, which the paper does not assert for trained networks. The image-scale result that a reader will find most interesting, 38% off-atom samples at h = 6 with a log-log slope of 0.481 or -0.156 against the reference, is at positive bandwidth and is explicitly not attributed to any single cause. The paper should restrict the practical sentence to the setting the theorem covers, or say directly that the off-atom CIFAR-10 samples are not yet explained by the transfer bound.

### W3: Statement-level comparison with Liu and Zuazua leaves the equivalence question open
**Severity**: Minor
**Evidence Anchor**: text: Appendix B.1 "so the comparison is between the analogous statements, not a claim that one implies the other"
**Confidence**: 3 — familiarity with Gaussian-path reparametrisations between score and flow-matching ODEs, not a verified derivation

The new comparison in Appendix B.1 and Table 4 is a clear improvement and states the configuration that separates the results (fixed w > 0 on one finite support, where Liu and Zuazua need a hypothesis on the limit set and leave almost-everywhere validity open in their Remark 3.19). For an empirical measure, the heat-flow probability-flow ODE and the linear-interpolant flow-matching field are commonly related by a change of scale and time. If that holds here, Proposition 4.3 directly settles the case of their open remark for one common support, which would sharpen the novelty claim; if it fails, saying why would forestall the obvious reviewer question. Either way, one sentence in B.1, and a pointer from the Related Work paragraph, would make the delta exact rather than analogical.

### W4: Section 4.4 cannot be read without the appendix
**Severity**: Minor
**Evidence Anchor**: absence: main text §4.4 — expected a definition of the signed posterior covariance Γ, of a hyperbolic profile and of the face condition; checked §1 contributions, §2 Setup and Notation, Table 1 and its caption, §4 proof strategy, §4.4
**Confidence**: 4 — direct reading of the main text

Section 4.4 is promoted to the abstract ("a signed posterior covariance decides the general case") and to the contribution list, but its objects (the profile, Γ, the face condition, the trace test) are defined only in Appendix B.7. A reader of the nine pages cannot state the criterion. A two- or three-line definition of Γ at the profile, with the two-atom specialisation Γ = F'_w(0), would make the general claim checkable from the main text.

### W5: Most supporting evidence sits in appendix figures and tables
**Severity**: Minor
**Evidence Anchor**: text: §4 proof strategy "composition is where Step 2 fails (Figure 4)"
**Confidence**: 4 — count of main-text cross-references against the figures and tables present in pages 1–9

The main text contains Table 1 and Figures 1 and 2; it cites Figures 4, 5, 6, 7, 8, 10 and 11 and Tables 5, 6, 8, 10, 11 and 12, all in the appendix, often for the numbers that support the sentence in which they appear (for example the perturbed basin probabilities, the CIFAR-10 midpoint fractions, the near-tie failures and the image-scale slopes). Each individual jump is non-essential, but together they make Section 6 hard to evaluate on its own. Moving the image-scale off-atom numbers (Table 8 or Figure 6) into the main text, at the cost of compressing Section 4.4 or Section 6.1, would help.

### W6: Two dense passages obscure rather than state the result
**Severity**: Minor
**Evidence Anchor**: text: §4.4 last sentence "sources and saddles, including those the trace test misses, put no source at z"
**Confidence**: 3 — readability judgement; the extraction may have lost formatting

The closing sentence of Section 4.4 uses "source" in two senses (a profile type and an initial point) and its exception clause about d = 8 and w at most 2w_c is hard to parse. The abstract has a similar problem: it packs the threshold, its stability, the spectral case, the (1-t)^2 layer, the integrable-Lipschitz statement, the asinh input, the transfer bound and the CIFAR-10 and U-Net results into one paragraph, which will read poorly as an OpenReview snippet. Shortening the abstract to the three claims of the contribution list and rewording the Section 4.4 sentence would cost nothing technically.

### S1: Table 1 states the whole result map up front
**Evidence Anchor**: table: Table 1, Support of the exact endpoint law

Table 1 lists each intervention, its endpoint support and the result that proves it, including the negative cases, before any technical development. This is the right editorial device for a theorem-heavy ICLR paper.

### S2: Scope and limits are stated honestly, including the negative experimental findings
**Evidence Anchor**: text: §7 Limitations "whether a network reproduces the off-atom basin depends on its parametrisation, chiefly on its input, and not in every seed"

The Limitations and Conclusion state what is not covered (different supports, sign-changing schedules, nonhyperbolic profiles, unidentified endpoint weights) and report that standard networks do not reproduce the basin. The paper does not oversell its existence result.

### S3: A falsifiable prediction from the theory is tested and confirmed
**Evidence Anchor**: figure: Figure 2, learned versus exact guided label averaging

The boundary-layer analysis predicts that only a field resolving the (1-t)^2 scale reproduces the basin; Figure 2 shows that networks with the rescaled input track the exact probabilities (0.401 against 0.406 at B = 1, 2w_c) while standard CFM does not, with a control centred elsewhere. This is the kind of checkable link between theory and learned samplers that ICLR readers value.

### S4: Statement-level positioning against the closest convergence theorems
**Evidence Anchor**: table: Table 4, closest convergence theorems and the positive results of Section 4

Table 4 compares field, support, combination, hypotheses and conclusion with Liu and Zuazua (2025; 2026) side by side, and the text concedes the case the paper does not treat (two different supports). This answers the most likely novelty objection at the level of statements.

### S5: Reproducibility and proof navigation
**Evidence Anchor**: text: Reproducibility Statement "All numbers are produced by code in the supplementary material"

The paper names the script behind each family of results, and the appendix opens with a notation table, a proof roadmap and a dependency figure, with each main-text result restated before its proof.
