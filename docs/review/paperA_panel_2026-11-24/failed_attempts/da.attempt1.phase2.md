contract_role: da
## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "wording in the abstract or conclusion is stronger than the theorems support"

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Calibration Status
`NOT_CALIBRATED`

Seat reports always emit `NOT_CALIBRATED`; the final panel topology is not knowable at seat time.

### Criterion-Bound Judgements
| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| D3 argumentative_coherence | sprint contract D3 and the Phase 1 scoring plan (no venue criteria bound: criteria_binding_unavailable) | PARTLY_MEETS | text: Section 9 "the number of combined fields and their signs decide whether the endpoints leave the training set"; text: Abstract "We therefore present the composition as a boundary marker, not a practical mechanism." | The theorem chain from hypotheses to the stated results holds on my reading; the headline dichotomy and the practical audit message are stated more broadly than the theorems and the paper's own learned and image-scale evidence support | I checked the proofs of the positive-mixtures theorem, the fixed-guidance proposition, the guidance-schedule theorem, the two-fields corollary, the two-atom composition theorem, the perturbation proposition, the spectral theorem, the matrix-threshold corollary and the two-atom proposition at the level of argument structure, not every constant | yes: warn on a mandatory dimension; no singleton defect reaches rejection level |

### What the paper does well
The mathematical core is careful. Hypotheses are stated where they are used (strictly positive priors, constant or bounded-variation coefficients, hyperbolicity, the face condition), the template of finite kinetic energy plus volume expansion is applied uniformly, and the paper says plainly where it fails (the composite) and why. The two-atom composition theorem is self-contained and its threshold is exact; the sign rule of the two-atom proposition reduces to a short quadratic argument that I could verify. The stress test comes with a positive control that would have detected an attracting tie, which directly answers the obvious objection that a scheme biased towards atoms passes such a test trivially. The limitations section concedes most of the gaps raised below. I found no text addressed to reviewers or any other instruction-like content in the manuscript.

### Strongest Counter-Argument
The paper's organising claim is that, within the exact empirical field, the number of combined fields and their signs decide whether the sampler can leave the training set: two fields only reweight, three can blend. A sceptic would answer that this dichotomy is an artefact of one hypothesis, strictly positive priors over a common finite support, which under the paper's own Assumption (iii) (labels identify examples) exists only when Gaussian label noise with h above zero has been applied during training. Remove that hypothesis and the dichotomy collapses on the paper's own terms: averaging two hard-label fields, a positive combination of two fields, already sends every source to a circumcentre. The usual practical settings, class labels shared by many examples or text prompts whose conditional supports differ, are exactly the "mixtures with different supports" that the limitations exclude. So the boundary the paper draws is the boundary of a regime, not a law about counting fields.

The practical layer is weaker. Every conclusion is "at the exact optimum", yet the paper's own proposition on regular learned fields, part (a), shows that the standard velocity MLP has an atomless endpoint law, its CIFAR-10 U-Net does not follow the label-noise reference (slope 0.36 against 1) and leaves 17 to 28 percent of samples off the training images, and standard networks never reproduce the blend basin; only a network handed the tie location does. Blends are in any case counted as leakage, so the audit "separation" changes nothing an auditor would do: at the exact optimum every setting leaks, which the related-work section itself calls well established. What survives is a careful set of theorems about an idealised field, plus a counterexample at its boundary; the claim that this tells practitioners or auditors which knob matters is not earned by the evidence presented.

### Logic-chain validation: theorems to the practical claims
1. From the positive-mixtures theorem, the guidance-schedule theorem and the two-fields corollary to "two fields only reweight": valid under strictly positive priors. The conclusion's first sentence drops that qualifier, and Section 5.1 itself records a two-field positive combination (hard-label averaging) that leaves the atoms for every source. Section 1, practice item (iii), carries the qualifier correctly; the abstract carries it in a later sentence; the conclusion does not.
2. From the two-atom composition theorem, the spectral theorem and the two-atom proposition to "composition is the operation an audit should examine": the theorems show composition is the only studied operation (with positive priors) that changes the support of the exact law. They do not show that changing the support matters for an audit, because the new support points are circumcentres of training records, which Section 1 itself says "an audit should count as leakage". The abstract then calls composition "a boundary marker, not a practical mechanism", while the conclusion tells auditors to examine it. The two practical statements point in different directions, and neither is backed by a trained compositional sampler.
3. From the exact field to trained networks: the bridge sentence in Section 1 ("the exact field says what the objective asks the network to do") is true as a statement about the objective, but the paper's own image-scale run shows that it carries no predictive weight there, and part (a) of the regular-learned-fields proposition shows the standard parametrisation cannot reproduce atomic endpoints at all. Practice item (ii) and the broader-impact statement on predictability of the returned record rely on this bridge.
4. From "label averaging" to "a network that resolves labels coarsely": the abstract and Section 5 model coarse label resolution as a field average, but the label-bottleneck proposition (Appendix B) proves that the optimum of a coarse-label network is a prior average, not a field average. Both are atomic under positive priors, so the reweighting claim survives either way. But the motivation for guided label averaging as a model of a learner (and so for the two-atom composition theorem beyond the conjunction) is contradicted by the paper's own proposition; the alternative "network whose output is smooth in its label input" is asserted without argument.

### Overgeneralisation and cherry-picking in the numerics
- The CIFAR-10 composition check reports "up to 0.29" in the main text from the eight pairs with the largest margin; the twelve random pairs give a mean of 0.042 at 2 w_c. Both are disclosed in Appendix E, but the main-text number comes from the selected set.
- Several exact-field checks cannot fail on the threshold by construction: the CIFAR classifier admits the midpoint only above the threshold and hands off to the one-dimensional flow of the two-atom composition theorem, and the composition stopping rules are taken from the proof. The paper says so for CIFAR ("The threshold itself is not new evidence"), but the contributions list still reads "agree with the theorems". The informative content of these checks is the basin sizes, which the theorems do not give.
- The learned-blend success uses an input "centred at the known tie"; centred elsewhere it fails, and on the triangle it leaves the edge midpoints empty. This is closer to a positive control for the parametrisation than to evidence that learning can discover blends, and it is the evidence behind the abstract's "can match its exact probability".
- The d = 8 simplex places no resolvable mass at the centre at 1.1 and 2 w_c (below 1/2048), so the positive-probability conclusion of the spectral theorem is numerically visible there only at 5 w_c.

### Ignored alternative explanations
1. Trained composites leave 0.16 to 0.79 of sources away from every atom and from the centre at 2 to 10 w_c. These non-training outputs come from learned-field error, not from the exact blend basin, and they are what an auditor of a trained sampler would actually see. The paper does not characterise where they land, so the claim that the exact field identifies the audit-relevant operation is untested against this rival source of non-training samples.
2. The CIFAR-10 departure from the label-noise reference (slope 0.36) could reflect undertraining (60000 iterations, 35.75M parameters, N = 2000) rather than a departure in kind from the exact field; the paper says it does not identify why, but practice items (i) and (ii) are framed as if the exact law were the relevant reference at that scale.
3. Absence of blends in standard networks is attributed to the (1-t)^2 boundary layer. A competing explanation, finite cutoff at 1-t = 1e-5 combined with MLP capacity in d at most 2, is partly addressed (log-uniform time sampling, separate unconditional network) but not across architectures or dimensions, so "standard velocity networks miss it" generalises from small MLPs.

### Missing stakeholder perspectives
- Auditors who need per-record return probabilities rather than support membership.
- Practitioners of text-conditioned composition, where conditional supports differ and the positive-prior hypothesis does not hold.

### Unexamined premise
The paper treats support of the exact endpoint law as the invariant that matters for replication. For copyright and privacy, the operative quantity is the probability of returning a particular record. Reweighting changes that probability, so label noise does act at the exact optimum on which record is returned, while the support stays the same. The binary "atoms or not" criterion makes every knob look equally ineffective and makes composition look special. Under a per-record criterion, the ranking of interventions could differ.

### Minor issues (not decision-bearing on their own)
- Section 1, practice item (i): "Such a reduction cannot come from the knob at the exact optimum, only from the error of the learned field". This splits the effect into the knob and the learned error, but a training-time knob such as label noise also changes the learned field and its error, so the two interact. The sentence holds only if replication means support membership. Rewording would fix it.
- Use of large language models statement: "the authors' own line-by-line check of these three proofs is not yet complete" (the two-fields corollary, the two-atom proposition, the genericity remark). Contributions 2 and 4 rest on these. My reading of the three arguments found no break: the two-fields corollary reduces to the guidance-schedule theorem by the sign split, parts (a) and (b) of the two-atom proposition follow from the quadratic identity, and the genericity remark is a standard transversality argument. As submitted, though, the paper says its own authors have not finished checking the proofs behind two listed contributions. This should be resolved before submission.
- The perturbation proposition covers perturbations of priors, weights and strength but not atom geometry. In one dimension the abstract's "persists under perturbation" is correct only with this restriction, which the abstract does not state.
- Section 7 calls the CIFAR composition run "a consistency check", while the contributions list says the CIFAR pairs "agree with the theorems". The second wording reads as stronger evidence than the first.

#### CRITICAL
| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|

#### MAJOR
| # | Dimension | Issue Description | Evidence Anchor | Confidence | Field-Norm Boundary | Evidence-Crossing Rationale |
|---|-----------|-------------------|-----------------|------------|---------------------|-----------------------------|
| M1 | D3 argumentative_coherence | The headline dichotomy (two fields reweight, three can blend) holds only for strictly positive priors on a common support. Under Assumption (iii) these arise only from label noise with h above zero. The paper's own hard-label averaging, a positive combination of two fields, sends every source to a circumcentre, and disjoint-support conditions (shared class labels, distinct prompts) are excluded. The conclusion states the dichotomy without the qualifier, so it is contradicted inside the paper. The thesis needs rescoping to the positive-prior regime in the abstract, contributions and conclusion. | text: Section 9 Conclusion "Within the exact empirical field, the number of combined fields and their signs decide whether the endpoints leave the training set." | 4 — core: ODE and flow-matching theory; checked Sections 5.1 and 8 (Limitations) and Table 1 | — | — |
| M2 | D3 argumentative_coherence | The practical message on composition contradicts itself and has no support. The abstract calls composition "not a practical mechanism", while the conclusion tells auditors to examine it. Blends are circumcentres of training records, which the paper says an audit should count as leakage, so the separation changes no audit outcome: every studied setting leaks at the exact optimum. The negative practical claim rests on MLP runs in d at most 2, where blends appear only with an input centred at the known tie. | text: Section 9 "the composition of conditions is the operation an audit should examine"; Abstract "We therefore present the composition as a boundary marker, not a practical mechanism." | 4 — core: theory and the paper's own learned-composition evidence (learned-composition table, Appendix E) | — | — |
| M3 | D3 argumentative_coherence | The modelling premise that a coarse-label learner averages fields over nearby labels is contradicted by the paper's own label-bottleneck proposition (Appendix B), which shows that the optimum of a coarse-label (bottleneck) network averages priors, and guidance on it stays atomic. The alternative of a network smooth in its label input is asserted without argument. Atomicity of label averaging survives either way, but guided label averaging (the two-atom composition theorem) is then motivated only by the conjunction, not by any learner, and the abstract's description of the interventions overstates what it covers. | text: Abstract "a network that resolves labels coarsely averages the field over nearby labels"; Section 5.3 "A network that discards label information instead averages the priors" | 4 — core: theory; read the label-bottleneck proposition (Appendix B) and its proof | — | — |
| M4 | D3 argumentative_coherence | The bridge from the exact field to trained samplers fails on the paper's own evidence. At image scale the generated variance does not follow the label-noise reference (slope 0.36 against 1), 17 to 28 percent of samples are off the training images, and part (a) of the regular-learned-fields proposition shows that the standard parametrisation has no atoms at all. Practice item (ii) and the broader-impact claim that the returned record is predictable therefore have no support for any trained model the paper tests. They should be limited explicitly to the exact optimum, or backed by evidence at scale. | text: Broader impact "Under label noise the returned record is predictable from the query and the training labels"; Section 7 "so at image scale the generated variance does not follow the reference across conditions" | 4 — core: theory; the empirical comparison is read as reported, not rerun | — | — |

