contract_role: domain
## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: warn
trigger: "Learned-network experiments that support the direction of a claim but are thin in scale, seeds or datasets, with the limitation stated"

### D3: argumentative_coherence
score: not_assessed

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Reviewer Identity

Peer Reviewer 2 (domain). Researcher on memorisation and generalisation in diffusion and flow-matching models: the empirical optimum, speciation versus collapse, inductive-bias explanations, guidance theory and compositional generation. This review covers literature completeness, fair novelty claims, and whether the exact-field results say anything about trained models. I did not check proofs line by line; that is outside this seat's remit and is my declared blind spot.

### Overall Recommendation

Major Revision

### Confidence Score

4

Confidence is an uncertainty/scope disclosure only; it never changes consensus counts, severity, decision bearing, or arbitration.

### Calibration Status

`NOT_CALIBRATED`

### Criterion-Bound Judgements

| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| D2 domain_accuracy | contract.json D2; Phase 1 scoring plan | PARTLY_MEETS | S1, S4, W1, W2, W3, W4, W5 | Prior closed-form, convergence and guidance-support results are attributed precisely and novelty is stated narrowly. But the practical framing claims more about trained samplers than the learned-network evidence (d at most 2, 3 to 5 seeds, a tie-centred input) supports. The composition and guidance-theory literature is also thin. | Proof correctness not assessed (blind spot). Literature search covered arXiv, Semantic Scholar and the web only. | yes: drives the D2 warn. Every item is repairable by reframing, adding citations and a scoped learned experiment. |

criteria_binding_unavailable: no venue-alignment claim is made.

### Summary Assessment

The paper asks which sampler-side changes to the exact empirical conditional flow-matching field can move its endpoints off the training set. It proves that label noise, positive mixtures of exact fields, bounded nonnegative guidance schedules of bounded variation, and any fixed combination of two exact fields with strictly positive priors still end on training atoms almost surely. It then shows that a signed combination of three fields, such as the conjunction of compositional generation, can put positive probability on a circumcentre ("blend") of training points. The threshold is w > 1/sinh^2 B for two atoms. The paper also gives a spectral criterion in any dimension and a sign rule at two-atom ties.

From a domain standpoint, prior work is represented unusually carefully. Overlaps with Wan et al. 2025, Liu & Zuazua 2026, Baptista et al. 2025 and Azangulov et al. 2026 are acknowledged by theorem number, and the composition result appears to be new. The main weaknesses concern how far these exact-optimum statements transfer to trained models, and the paper's own framing.

The composition result is the most novel part, yet the abstract calls it a "boundary marker". Standard trained velocity networks do not reproduce it. A network matches the exact probabilities only when given a coordinate centred at a tie that is known in advance. At image scale, trained label-noise networks do not follow the exact reference (slope about 0.36 against 1). The practical claims about audits and "closer fits" therefore extrapolate beyond the evidence. Coverage of composition theory and guidance theory is also incomplete.

All of these points are repairable. I recommend major revision, mainly for reframing and literature, plus one scoped learned-network experiment.

### S1: Precise and fair attribution of the closest prior results

The paper says that its label-noise endpoint theorem follows from Wan et al. 2025, Theorem 5.3, and is not new. It credits convergence of every trajectory for two-field combinations to Liu & Zuazua 2026, Theorem 2.5, and claims only the almost-everywhere atomicity and the extensions to schedules and families of priors. It sets out the differences from Azangulov et al. 2026 (stochastic sampler, Girsanov argument), Cai et al. 2026 and Cao et al. 2026. My searches confirmed that Liu & Zuazua (arXiv 2605.12231) exists, with both titles the paper reports, and that its finite-Dirac result is conditional in version 1, as the manuscript says. This is the standard of novelty accounting a domain reviewer hopes to see.
**Evidence Anchor**: text: §1 Contributions, item 1 "This is not a new result: at a fixed query the label-noise field is the unconditional exact field of the weighted training law"

### S2: A sharp, new characterisation of when composition leaves the training set

As far as I can find, the exact threshold w_c = 1/sinh^2 B for the conjunction at a two-atom tie, the spectral criterion via the signed posterior covariance, and the "subtracted intermediate field" sign rule are new. Linear score composition has been studied for sampling fidelity (Du et al. 2023; Bradley et al. 2025), but not, to my knowledge, for where the exact empirical field ends. The sign rule gives a clean, checkable answer about negative prompts. A negative prompt against the other example never blends; a milder negative prompt for the same example can.
**Evidence Anchor**: equation: Eq. (composition-mean) and Proposition "Blending two examples needs a subtracted intermediate field", part (c), threshold w > 1/sinh^2 B

### S3: A positive control and an image-dimension exact check

The stress test is calibrated against a configuration that has an attracting tie, which closes the obvious objection that a scheme biased towards atoms would pass trivially. The exact composite is also run on CIFAR-10 pairs with all 2000 atoms present. Both are good practice for exact-field claims.
**Evidence Anchor**: text: §6 "A positive control for the stress test" "The stress test therefore sees an attracting tie when there is one"

### S4: Comparison table against the closest convergence theorems

Appendix B.1 sets the paper's results beside Liu & Zuazua 2025/2026, Wan et al. 2025 and Azangulov et al. 2026, including the change of variables that relates the flow-matching ODE to the heat-flow probability-flow ODE. This makes the incremental contribution auditable.
**Evidence Anchor**: table: Table "comparison" (Appendix B.1), columns Liu & Zuazua Thm 2.5 / Azangulov Thm 3 / This paper

### S5: Explicit statement that the theorems are about exact fields

The Limitations section states this plainly and reports the failures of learned networks, including the empty edge midpoints on the triangle.
**Evidence Anchor**: text: §7 Limitations "The theorems concern exact fields of a fixed training set and do not say that a trained network implements them."

### W1: The headline's most novel result is the one the paper itself calls a boundary marker

**Problem**: The abstract, contributions 3 and 4, Figure 1 and the conclusion lead with composition: three fields can blend training examples, and "the composition of conditions is the operation an audit should examine". The abstract then states that composition is "a boundary marker, not a practical mechanism". The learned experiments support that hedge: standard velocity CFM networks put at most 0.001 of their sources at the midpoint at every guidance strength. This leaves the reader unsure what the paper wants practitioners to take away. Is composition a real replication risk that audits must examine, or a mathematical boundary case?

There is also a domain tension the paper does not discuss. Because w_c ≈ 4e^{-2B} is exponentially small, guidance strengths used in practice (w of order 3 to 7.5) are far above w_c for any confidently identifying condition. At the exact optimum the blend would therefore not be a marginal effect. It is the learned networks that fail to show it. Either reading is defensible, but the paper asserts both.

**Why it matters**: The two-field atomicity results stand without composition. The novelty, however, sits in the composition results, and the practical recommendation to audit composition rests on a mechanism the paper's own trained models do not exhibit.

**Suggestion**: Choose one framing and make the abstract, the contribution list, the "What this means in practice" paragraph (iii) and the conclusion consistent with it. One option: lead with the reweighting results (two fields never leave the atoms, so these anti-replication knobs give no guarantee at the optimum) and present composition explicitly as the exact boundary of that theorem class. The other option: keep composition as the headline, discuss the w_c ≪ practical-w point, and say directly that the open question is whether trained compositional samplers approach the exact field near ties. Replace "boundary marker" with a defined phrase.

**Severity**: Major
**Evidence Anchor**: text: Abstract "We therefore present the composition as a boundary marker, not a practical mechanism."
**Confidence**: 4 — core expertise: guidance and compositional-generation literature; judgement on framing and claims

### W2: Practical claims about trained samplers rest on the exact optimum while the paper's own image-scale evidence departs from it

**Problem**: The "What this means in practice" paragraph says that a reduction in copying from label noise or guidance "cannot come from the knob at the exact optimum, only from the error of the learned field, and it need not survive a closer fit". Contribution 1 also offers the reference variance as a parameter-free reference for trained networks.

The paper's own CIFAR-10 results show that a 35.75M-parameter U-Net trained with label noise does not track the reference across conditions. The slope is 0.36 (95% interval [0.22, 0.51]) against 1, and 17 to 28% of samples sit off the training images at the cutoff. A substantial literature argues that trained diffusion and flow models generalise through inductive biases and training dynamics that keep them away from the empirical optimum: Kadkhodaie et al. 2024, Kamb & Ganguli 2025, Bonnaire et al. 2025 (all cited), and Vastola 2025 (not cited). In that literature, a "closer fit" to the empirical optimum is not the regime practitioners operate in. The statement that a reduction "need not survive a closer fit" is therefore true but of limited relevance. The auditing advice, that the returned record is predictable from labels, holds only for an exact-optimum model, and the trained CIFAR model is evidently not one.

**Why it matters**: D2 asks whether conclusions about the exact field are presented as statements about trained networks only when the evidence supports it. The theorems are correctly scoped. The practical paragraph and the broader-impact statement go further than the learned evidence.

**Suggestion**: Rephrase (i) and (ii) of "What this means in practice", and the broader-impact paragraph, as conditional statements about models near the empirical optimum. Cite Vastola 2025 alongside the inductive-bias works, and say explicitly that the CIFAR U-Net is not in that regime. If possible, report how the CIFAR slope and off-atom fraction change with training length or model size. That would show whether trained models approach the reference as they fit more closely, which the "closer fit" argument assumes.

**Severity**: Major
**Evidence Anchor**: text: §1 "What this means in practice" "only from the error of the learned field, and it need not survive a closer fit"
**Confidence**: 4 — core expertise: memorisation versus generalisation in trained diffusion models

### W3: The learned-composition evidence is thin and relies on a hand-supplied, tie-centred coordinate

**Problem**: Contribution 5 reports that a data-predicting network "matches the exact probability … in all but one of twenty seed-configuration pairs". This network receives asinh(tx/(1-t)^2) centred at the known tie. Centred elsewhere, it leaves the midpoint empty, and it also leaves the other blends on the triangle (edge midpoints) empty. Every learned-composition experiment uses d ≤ 2, two or three atoms, and three to five seeds. Standard CFM networks, including the log-uniform and separate-unconditional variants, give 0.000 midpoint occupancy at B=1 against an exact 0.406 at 2w_c. At B=3, velocity networks put mass at the midpoint even at w=0, an artefact of the learned field.

What the experiments show is that a network told where the tie is can reproduce one basin. They do not show what trained compositional samplers do. The paper states these limitations (§7), which is why I score warn rather than block.

**Why it matters**: The contribution title, "What a learned field needs to inherit the blend", reads as a general statement. The evidence covers one hand-engineered parametrisation in toy dimension, so the claim is fragile.

**Suggestion**: Retitle contribution 5 to what is shown: a rescaled input at the tie is sufficient in these toy runs, and standard parametrisations miss the basin. If feasible, add one learned composition experiment at moderate dimension. For example, a class-conditional model on a small subset of CIFAR-10 pairs, with the conjunction applied and the nearest-neighbour midpoint criterion already used in Appendix E, at w ≫ w_c. This would test whether trained samplers produce training-pair blends at all.

**Severity**: Major
**Evidence Anchor**: table: Table "learned-composition" (Appendix E), rows "velocity CFM" (0.000 at every w, B=1) versus "data, rescaled input" and the exact row (0.406 at 2w_c)
**Confidence**: 4 — core expertise: learned versus exact fields; experimental norms in this subfield

### W4: Coverage of composition theory is incomplete

**Problem**: The Composition paragraph of §2 cites only Liu et al. 2022 and Du et al. 2023. Two directly relevant works are missing:
- Bradley et al. 2025, "Mechanisms of Projective Composition of Diffusion Models" (ICML 2025, arXiv 2502.04549), analyses when linear score combinations provably achieve a meaningful composition and when they fail.
- Skreta et al. 2025, "The Superposition of Diffusion Models Using the Itô Density Estimator" (arXiv 2412.17762), proposes AND/OR composition operators for diffusion and flow fields.

The narrow novelty claim, that no prior work analyses where the composition ends on the exact empirical field, survives. But the paper's reading of the conjunction as a "practical" or "boundary" mechanism should engage with this literature, which already explains why summed scores do not sample the intended composition.

**Why it matters**: This is incomplete coverage of literature that bears on a central framing choice (W1), although the novelty itself is not overturned.

**Suggestion**: Add both works to §2 and to the §4.5 discussion of the conjunction. Say how the exact-field blend relates to the failure modes of projective composition that Bradley et al. identify.

**Severity**: Minor
**Evidence Anchor**: absence: §2 Related work, "Composition" paragraph — expected the theory of linear score composition (Bradley et al. 2025; Skreta et al. 2025); checked §2, §4.5 "Composing conditions", §7 Limitations, refs.bib
**Confidence**: 4 — verified both works exist (ICML proceedings page; arXiv listing)

### W5: Guidance-theory, guidance-based memorisation mitigation and replication-evidence references are missing

**Problem**: The paper's motivation is that sampler knobs are used to reduce replication, and its theorems concern guidance. The following are not cited:
- Guidance theory: Wu et al. 2024 (ICML, arXiv 2403.01639) on guidance in Gaussian mixtures, and Pavasovic et al. 2025 (arXiv 2502.07849) on the high-dimensional theory of CFG.
- Guidance-based memorisation mitigation: Chen et al. 2024, "Towards Memorization-Free Diffusion Models" (anti-memorization guidance, arXiv 2404.00922). This is exactly the kind of knob the paper says "carries no guarantee at the exact optimum".
- An oracle-velocity analysis of flow matching that explains CFG intervals by a navigation/refinement split: Liu et al. 2025, arXiv 2512.02826.
- Extraction evidence: Carlini et al. 2023, "Extracting Training Data from Diffusion Models". It is in refs.bib but never cited, although the abstract opens with the claim that models "can return exact copies of their training images".

**Why it matters**: Coverage is incomplete, but the gaps bear on secondary and motivating claims rather than the main results.

**Suggestion**: Cite Carlini et al. 2023 for the opening claim. Add the guidance-theory and mitigation works to the Guidance paragraph of §2, and say whether anti-memorization guidance falls within the two-field atomicity result (Corollary "Any two exact fields") at the exact optimum.

**Severity**: Minor
**Evidence Anchor**: absence: §1 Introduction and §2 "Guidance" paragraph — expected citations for data extraction, guidance theory and guidance-based memorisation mitigation; checked abstract, §1, §2, bibliography as cited, refs.bib
**Confidence**: 4 — verified each suggested work via arXiv or proceedings listings

### W6: Normative claim that blends are "leakage" is asserted without support

**Problem**: The paper states that circumcentres of training images are affine combinations, "which an audit should count as leakage rather than as new samples". In practice, replication audits use nearest-neighbour ratio or similarity criteria (e.g. Yoon et al. 2023, Somepalli et al. 2023, Carlini et al. 2023). Whether a pixel-average of two training images counts as replication under those criteria depends on the criterion. The paper's own Appendix E classifier, borrowed from Yoon et al., would treat an exact midpoint as non-memorised, since its two nearest neighbours are equidistant.

**Why it matters**: The audit recommendation partly depends on this classification, and the domain's own memorisation criteria give the opposite answer.

**Suggestion**: Say which replication criterion is meant, note that the standard ratio criterion would classify an exact two-image midpoint as novel, and present "leakage" as the authors' position, with a reason such as reconstructibility of both sources.

**Severity**: Minor
**Evidence Anchor**: text: §1 "What this means in practice" "which an audit should count as leakage rather than as new samples"
**Confidence**: 3 — domain knowledge of memorisation metrics; normative point

### W7: The manuscript states that the authors have not completed their own check of three core proofs

**Problem**: The "Use of large language models" statement in the submitted text says that the proofs of Corollary "Any two exact fields", Proposition "Blending two examples needs a subtracted intermediate field" and Remark "How restrictive the hypotheses …" "were first drafted with a large language model". It adds that "the authors' own line-by-line check of these three proofs is not yet complete". Two of these support contributions 2 and 4.

I make no judgement on whether the proofs are correct, since that is outside my seat. But a submitted manuscript that declares an incomplete author check of results it lists as contributions is a disclosure issue the editor should see.

**Why it matters**: Readers and reviewers rely on the authors' responsibility for the stated results. The statement as worded invites doubt about core claims, even if the proofs are correct.

**Suggestion**: Complete the check before submission and update the statement accordingly, or mark the affected results as conjectural until then.

**Severity**: Minor
**Evidence Anchor**: text: "Use of large language models" "the authors' own line-by-line check of these three proofs is not yet complete"
**Confidence**: 3 — reporting the manuscript's own statement; proof validity not assessed

### Detailed Comments

#### Literature Review
- **Coverage**: The closed-form empirical-optimum and memorisation lines are well covered: Gu et al., Biroli & Mézard, Kadkhodaie et al., Kamb & Ganguli, Bertrand et al., Biroli et al. 2024 on speciation and collapse, Aithal et al. on mode interpolation, and Pham et al. The convergence-theory comparison is excellent. Gaps are composition theory (W4), guidance theory and mitigation (W5), Vastola 2025 (W2), and Carlini et al. 2023, which is in the bib but uncited.
- **Integration quality**: The coverage is synthetic, not a list. Each nearby theorem is positioned against the paper's own statements, with version numbers.
- **Research gap argument**: Convincing for the exact field ("We are not aware of an analysis of the endpoints of this composition on the exact empirical field"). The searches I ran did not contradict it.

#### Theoretical Framework
- **Appropriateness**: Working with the exact empirical optimum is a standard and appropriate idealisation for "what the objective asks". The issue is the distance from trained models (W2).
- **Application depth**: Deep. The unified two-step template (kinetic energy, then volume expansion) organises every result.
- **Alternative frameworks**: Inductive-bias models of trained networks (local or equivariant score machines, as in Kamb & Ganguli and Niedoba et al.) could test whether composition blends survive in a model closer to trained CNNs. This could be a cheap intermediate between the exact field and trained networks.

#### Academic Argument Quality
- **Factual accuracy**: Descriptions of Biroli et al. 2024, Bertrand et al. 2025, Aithal et al. 2024, Du et al. 2023 and Liu & Zuazua 2026 agree with what I know of those works. I found no misstatement of the empirical-optimum collapse.
- **Argument logic**: See W1 (framing) and W2 (exact optimum versus trained networks).
- **Terminology precision**: "Blend" is defined as a circumcentre, which is consistent. "Negative prompting by substitution" is non-standard but defined. "Boundary marker" is undefined (W1).

#### Contribution to the Field
- **Incremental contribution**: Moderate to substantial for theory. It identifies exactly which signed combinations of exact fields can leave the atoms, with a closed-form threshold and a spectral criterion. The atomicity extensions add to Liu & Zuazua and Wan et al. incrementally but cleanly.
- **Positioning**: Careful and fair (S1, S4).
- **Overclaiming**: Limited to the practice, broader-impact and contribution-5 framing (W1 to W3, W6).

#### Missing Key References
- Bradley et al. 2025, Mechanisms of Projective Composition of Diffusion Models: when linear score composition works or fails.
- Skreta et al. 2025, The Superposition of Diffusion Models Using the Itô Density Estimator: AND/OR composition operators.
- Wu et al. 2024, Theoretical Insights for Diffusion Guidance: A Case Study for Gaussian Mixture Models: guidance theory.
- Pavasovic et al. 2025, Understanding Classifier-Free Guidance: High-Dimensional Theory and Non-Linear Generalizations (later retitled): guidance theory.
- Chen et al. 2024, Towards Memorization-Free Diffusion Models: guidance used against memorisation.
- Vastola 2025, Generalization through variance: how noise shapes inductive biases in diffusion models: why trained models leave the empirical optimum.
- Liu et al. 2025, From Navigation to Refinement: Revealing the Two-Stage Nature of Flow-based Diffusion Models through Oracle Velocity: closed-form oracle velocity and CFG intervals.
- Carlini et al. 2023, Extracting Training Data from Diffusion Models: already in refs.bib, should be cited for the opening claim.

~~~yaml suggested-references
- title: "Mechanisms of Projective Composition of Diffusion Models"
  authors: ["Bradley, A.", "Nakkiran, P.", "Berthelot, D.", "Thornton, J.", "Susskind, J. M."]
  year: "2025"
  doi: null
  arxiv_id: "2502.04549"
- title: "The Superposition of Diffusion Models Using the Itô Density Estimator"
  authors: ["Skreta, M.", "Atanackovic, L.", "Bose, A. J.", "Tong, A.", "Neklyudov, K."]
  year: "2025"
  doi: null
  arxiv_id: "2412.17762"
- title: "Theoretical Insights for Diffusion Guidance: A Case Study for Gaussian Mixture Models"
  authors: ["Wu, Y.", "Chen, M.", "Li, Z.", "Wang, M.", "Wei, Y."]
  year: "2024"
  doi: null
  arxiv_id: "2403.01639"
- title: "Understanding Classifier-Free Guidance: High-Dimensional Theory and Non-Linear Generalizations"
  authors: ["Pavasovic, K. L.", "Verbeek, J.", "Biroli, G.", "Mézard, M."]
  year: "2025"
  doi: null
  arxiv_id: "2502.07849"
- title: "Towards Memorization-Free Diffusion Models"
  authors: ["Chen, C.", "Liu, D.", "Xu, C."]
  year: "2024"
  doi: null
  arxiv_id: "2404.00922"
- title: "Generalization through variance: how noise shapes inductive biases in diffusion models"
  authors: ["Vastola, J. J."]
  year: "2025"
  doi: null
  arxiv_id: "2504.12532"
- title: "From Navigation to Refinement: Revealing the Two-Stage Nature of Flow-based Diffusion Models through Oracle Velocity"
  authors: ["Liu, H.", "Liu, J.", "Li, Y.", "Bai, L.", "Ji, Y.", "Guo, Y.", "Wan, S.", "Wen, H."]
  year: "2025"
  doi: null
  arxiv_id: "2512.02826"
- title: "Extracting Training Data from Diffusion Models"
  authors: ["Carlini, N.", "Hayes, J.", "Nasr, M.", "Jagielski, M.", "Sehwag, V.", "Tramèr, F.", "Balle, B.", "Ippolito, D.", "Wallace, E."]
  year: "2023"
  doi: null
  arxiv_id: "2301.13188"
~~~

### Questions for Authors

1. At guidance strengths used in practice (w of order 3 to 7.5) and confidently identifying conditions, w ≫ w_c. Do you then expect the exact conjunction to blend almost surely at ties? If so, why is composition a "boundary marker" rather than the main practical risk at the exact optimum?
2. Does the CIFAR-10 label-noise slope approach 1, and does the off-atom fraction shrink, with longer training or larger models? The "closer fit" argument depends on this.
3. Does anti-memorization guidance (Chen et al. 2024), written as exact fields, fall within Corollary "Any two exact fields", or does it combine three or more fields?
4. Under the Yoon et al. nearest-neighbour ratio criterion you use in Appendix E, would an exact two-image midpoint count as memorised? If not, what criterion justifies calling blends "leakage"?

### Minor Issues

- §1 opening sentence of the abstract and introduction: add a citation for exact replication (Carlini et al. 2023 is already in refs.bib).
- Table 1 row "Averaging identifying hard-label fields": "can move every endpoint to a circumcentre" holds only in symmetric configurations, as §4.1 says. The row could say so.
- I found no reviewer-directed or instruction-like text in the rendered manuscript.
