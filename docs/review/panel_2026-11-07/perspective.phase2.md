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
trigger: "practical implications are plausible but under-explained"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Reviewer Identity

Peer Reviewer 3, cross-disciplinary seat: a nonparametric statistician (kernel smoothing, statistical learning theory) who also audits generative models for privacy and memorisation in practice. I read the paper for its statistical meaning, its practical and privacy consequences, and its unstated assumptions. I am less at home with the ODE machinery (Liouville and Fatou arguments, Carathéodory solutions, the spectral classification in Appendix B.7), so I take those proofs as given and say nothing about their correctness.

### Calibration Status

`NOT_CALIBRATED`

### Summary Assessment

To a statistician the paper is easy to enter. The exact endpoint law at positive label bandwidth is a Nadaraya–Watson mixture over the training atoms (Theorem 3.4), and the paper says plainly that this is a reference point, not a new identity. It gives the moments a generated sample should match, and it states early that matching those moments is not the same as recovering a posterior (Proposition 3.6). Three things fit my reading of the bottleneck as label quantisation. A label bottleneck averages priors rather than fields (Proposition B.6). The one off-atom mechanism, guidance applied to a field-level label average, is explicitly presented as an existence result. And the shared-label CIFAR run checks the identifying-label assumption directly. The scope is stated more honestly than is usual in this literature.

The D4 concern is about translation, not correctness. The practical and privacy consequences that an auditor or practitioner would take from the paper are mentioned but not worked out, and some of them are framed in a way an adjacent-field reader may misread. (i) "Leaving the atoms" and "new samples" are used for endpoints that are blends of two training images, which a privacy auditor would count as leakage, not novelty. (ii) The Ethics statement says the results matter for sensitive data but does not give a usable consequence or diagnostic. (iii) The headline atomic-support statements hold at fixed N, and the paper never says how much they bite in the large-N, dense-label regime where practitioners work. (iv) The threshold 1/sinh²B and the linear law need the tie location and the averaging measure, and no practitioner knob is shown to produce that composite. (v) Endpoint noise is called a "remedy" when, statistically, it is a smoothed bootstrap, which by itself gives no privacy protection. None of these changes what the theorems license, so the score is warn, not block.

### Strengths

### S1: The Nadaraya–Watson reading and the moment-is-not-posterior warning are stated explicitly
The kernel-smoothing link is credited (Nadaraya 1964; Watson 1964; Baptista et al. 2025), and the paper derives the statistically right warning from it: the mean and covariance of the atomic mixture are computable references, and matching them does not recover a posterior. Proposition 3.6 turns this into a distributional lower bound that does not depend on h. A statistician can check this from the training set alone.
**Evidence Anchor**: text: §3 "them does not recover a posterior"

### S2: Label bottleneck formalised as prior averaging, which separates quantisation from field mixing
Proposition B.6 is the result I would have asked for. A learner that sees the label only through a cell (a quantiser) produces a field of averaged priors, not an average of fields, and guidance on it still ends on an atom almost surely. This settles the statistical question of whether coarse label resolution is itself the composite of Theorem 4.6. It is not, and the learned-network check on the triangle (Appendix E.3) supports this.
**Evidence Anchor**: text: Appendix B.6 "A label bottleneck averages priors, not fields."

### S3: Scope of the composition result stated honestly
The Conclusion and Section 4.3 both call the off-atom composition an existence result and not a mechanism expected in trained models, and they support this with Proposition C.2 and the failure of standard velocity networks. This keeps a memorisation or privacy reader from taking Theorem 4.6 as a recipe for novelty.
**Evidence Anchor**: text: §8 "the composition result is an existence result, not a mechanism we expect in standard models"

### S4: The identifying-label assumption is tested, not only stated
Assumption 1(iii) is the one hidden assumption I expected to carry the most weight. The CIFAR class-label run shows that shared labels change the endpoint law from one image to the within-class empirical law, and the trained U-Net keeps that variance. This tells practitioners with categorical labels what transfers.
**Evidence Anchor**: text: Appendix E.2 "labels therefore remove the collapse onto one image but not the restriction to training images"

### S5: Off-atom image samples checked against the full dataset
For an auditor, a sample is only "novel" if it is not near any training-set image, not just the 2000 used. The paper re-measures against all 50000 CIFAR-10 training images, which removes the most obvious confound.
**Evidence Anchor**: text: Appendix C.4 "the fractions are slightly larger, so the off-atom samples are not near other dataset images"

### Weaknesses

### W1: "New samples" is used for endpoints that are blends of training examples, which privacy readers would count as leakage
The Introduction says one composition "creates new samples", and Table 1 and Section 4.3 describe that composition as leaving the atoms. The endpoints it produces are circumcentres. On the CIFAR pairs these are pixel midpoints of two similar training images (Appendix E.3 notes they lie at 0.54–0.90 of the median nearest-neighbour distance). In privacy and memorisation auditing, such a sample counts as reconstruction of two training records, not a novel sample. The Yoon et al. ratio criterion would also flag a midpoint as off-atom even though it shows both sources. In the same way, the patch-mosaic account in Appendix C.4, which the paper leaves untested, would give off-atom samples that still copy training content locally. The mathematics is fine; the vocabulary is what will mislead adjacent-field readers. Suggested remedy: use "non-training endpoint" or "blend" instead of "new sample" throughout, and add one sentence saying that being off-atom under the finite-cutoff criterion is not evidence of non-leakage.
**Severity**: Minor
**Evidence Anchor**: text: §1 "No single intervention analysed here (Table 1) creates new samples from the field that training"
**Confidence**: 4 — privacy and memorisation auditing practice; the reading of the circumcentre as a blend comes from the paper's own Appendix E.3

### W2: The privacy consequence in the Ethics statement is not turned into anything an auditor can use
The Ethics statement says the results bear on privacy and help with auditing and extraction, and that the positive theorems matter "when conditional models are trained on sensitive data". It never says what follows. From my side, the useful reading is a negative one: at the exact optimum, label noise, label averaging, negative guidance and bounded guidance schedules are not privacy mitigations, because they only reweight the atoms. Seen from the attacker's side, the reweighting is partly computable from the training set and the query label via p^(h)(y), so the paper also shows which record a given label and guidance setting will return. Neither consequence is stated, and the paper does not connect to the formal notions an auditor would use, such as membership inference or differential privacy. A related citation (Sesmat et al. 2026) is in the bibliography but not used for this purpose. Suggested remedy: two or three sentences in the Implications paragraph or the Ethics statement, stating that these knobs are not mitigations and that only support-changing mechanisms (and, for a formal guarantee, randomisation calibrated in the DP sense) can be. I am not asking for new experiments.
**Severity**: Minor
**Evidence Anchor**: text: Ethics Statement "which is relevant when conditional models are trained on sensitive data"
**Confidence**: 4 — direct experience with training-data extraction audits; no claim about the theorems themselves

### W3: The atomic-support statements are fixed-N, and their practical bite in the large-N, dense-label regime is not discussed
Read as kernel regression, Theorem 3.4 and Proposition 3.6 are exact statements at fixed N (Corollary 3.5 says "at fixed N"). The lower bound (4) is the expected squared distance from the posterior to the nearest atom. With dense data it shrinks as N grows, and at a fixed h with k-dimensional labels the effective number of atoms n_eff grows as well. So in the regime of practitioners (large N, labels with near neighbours), "never leaves the training set" can hold exactly while the gap to the posterior is statistically negligible, and an atomic law with large n_eff can be indistinguishable in practice from a smooth one at any resolution an evaluator uses. This is the classical consistency regime of Nadaraya–Watson estimators (h → 0 with enough points in each label window). A reader from my field will ask where the paper sits relative to it. The paper reports n_eff on EXP-1 (Table 6) and the nearest-neighbour label spacing on CIFAR (Appendix E.2), so the ingredients are there. Suggested remedy: a short remark saying that the positive theorems are about support, not about distance to the posterior, and how the bound in (4) scales with N and with the label-window occupancy. Then readers will not take atomic support as a large-N failure of generalisation, and will not take it as irrelevant either.
**Severity**: Minor
**Evidence Anchor**: text: Proposition 3.6 "and this lower bound does not depend on h"
**Confidence**: 4 — kernel-regression consistency theory is my core field; I have not checked whether an appendix treats N-scaling and found none in the main text or the appendix parts I read

### W4: The threshold and linear law are not practitioner diagnostics, yet the abstract frames the setting through practitioner knobs
The abstract opens with "the knobs a practitioner turns" and then gives the exact threshold 1/sinh²B and the tie-centred coordinate. To use either as a diagnostic one needs B = u₀ℓ/h², which requires a known two-point averaging measure φ over fields and known label geometry, plus the location of the tie. The paper itself shows that the most natural practitioner mechanism, a label bottleneck, gives prior averaging and therefore not this composite (Proposition B.6). It also shows that the reproducing network fails when its input is centred away from the tie. No knob a practitioner actually turns is shown to produce the field-level average that Theorem 4.6 needs. The body is careful about this (S3), but the abstract's practitioner framing invites an overreading. Suggested remedy: say in the abstract or the Implications paragraph that the composite has no identified practical instance and that the threshold is a structural boundary, not a tuning rule for guidance strength.
**Severity**: Minor
**Evidence Anchor**: text: §6.2 "centred at the known tie z = 0 (centred elsewhere it leaves the midpoint empty, Appendix E.3)"
**Confidence**: 3 — the practical reading is mine; the facts come from the paper; I may be missing a practitioner setting that produces field averages

### W5: Endpoint noise is called a "remedy", but statistically it is a smoothed bootstrap with no privacy content of its own
Appendix D presents endpoint smoothing as the way to move the support, and Table 1 and the Introduction list it as the only intervention that removes the atoms in every configuration. Proposition D.1 shows the endpoint law is a Gaussian kernel density estimate around the weighted atoms, so sampling from it is the smoothed bootstrap. That literature (and practical privacy auditing) knows that for small ρ the samples are near-copies of training records, and that for large ρ fidelity is lost. Removing atoms is necessary for novelty in the paper's sense, but it is neither sufficient for novelty in the auditor's sense nor a privacy guarantee. Suggested remedy: either drop "remedy" or qualify it as support-level only, and mention the smoothed-bootstrap and KDE reading so statisticians see the trade-off at once.
**Severity**: Minor
**Evidence Anchor**: text: Appendix D "a remedy must move the support"
**Confidence**: 4 — smoothed-bootstrap and KDE theory and their known disclosure behaviour

### Detailed Comments

#### Assumption Audit
- **Explicit assumptions**: Assumption 1 (fixed D, linear interpolant, identifying labels) and the strictly positive common-support priors of Section 4 are stated where they are used. The identifying-label assumption is also tested (S4). The finite atom set and distinct atoms are explicit.
- **Implicit assumptions**: (a) Fixed N, with no statement about large N (W3). (b) That "off the training set" is the relevant notion of novelty, when a privacy reader would use a stricter one (W1). (c) That the averaging measure φ and the tie location are known for the composite (W4). The paper discloses (c) in the experiments but not in the framing.
- **Paradigmatic assumptions**: The analysis is at the population optimum of a fixed empirical objective, which is the standard paradigm in this literature. The paper is clear that trained networks depart from it (Theorem 5.1, Proposition C.2, Appendix C.4).

#### Cross-Disciplinary Connections
- **Parallel research**: Kernel-regression consistency (the large-N, small-h regime), smoothed bootstrap and KDE sampling, quantisation of probability measures (the bottleneck as label quantiser), and membership inference and differential privacy.
- **Borrowing opportunities**: n_eff already appears in Table 6. Reporting it on every condition, or a label-window occupancy, would give statisticians an immediate sense of how far each regime is from the consistent one.
- **Methodological borrowing**: A patch-level nearest-neighbour audit of off-atom completions, which the paper names as untested, is standard in data-replication audits (Somepalli et al. 2023, already cited) and would decide between the two accounts in Appendix C.4.

#### Practical Impact
- **Real-world application**: The most usable message for practitioners is the negative one. Label noise and guidance choose which training example the exact field returns, so these knobs are not mitigations. The paper should say so directly (W2).
- **Implementation feasibility**: The threshold diagnostic needs information practitioners lack (W4).
- **Stakeholders**: Data subjects in sensitive conditional datasets are the affected group. The paper's results are relevant to them, but this is not spelled out.

#### Broader Implications
- **Ethical dimensions**: The Ethics statement correctly names the dual use (audit and extraction). The predictability of which atom is returned for a given label, through computable weights, is a dual-use point worth one sentence.
- **Future directions**: An N-scaling of the bound in (4), and the patch-level audit of off-atom image samples.

### Questions for Authors
1. How does the expected distance to the nearest atom in (4) scale with N and with the label-window occupancy at a fixed h? Is there a regime where the atomic law and the posterior are indistinguishable at the evaluation resolution used in Section 6?
2. Is there any practical training or sampling procedure that gives the field-level label average of Theorem 4.6, as opposed to the prior-level average of Proposition B.6?
3. Would you agree to state explicitly that label noise, label averaging and bounded guidance schedules are not privacy mitigations at the exact optimum?
4. For the CIFAR midpoint samples, what is their distance to each of the two source images relative to the 1/3 ratio criterion? Would an auditor's criterion classify them as memorised?

### Minor Issues
- In the Ethics statement, "can inform both the auditing of trained models and attempts to extract data from them" could cite the extraction and membership works already in the bibliography (Carlini et al. 2023; Sesmat et al. 2026) at that point.

### Cross-Disciplinary Reading Recommendations
- Silverman and Young (1987), on the smoothed bootstrap. Relevant to W5: Proposition D.1 is a smoothed bootstrap.
- Györfi, Kohler, Krzyżak and Walk (2002), on the consistency of kernel regression estimators. Relevant to W3.
- Graf and Luschgy (2000), quantisation of probability distributions. A vocabulary for the label bottleneck of Proposition B.6.
- Shokri, Stronati, Song and Shmatikov (2017), membership inference. Relevant to W2.
- Dwork, McSherry, Nissim and Smith (2006), calibrating noise to sensitivity. The formal privacy notion that support-level smoothing does not provide (W2, W5).

~~~yaml suggested-references
- title: "The bootstrap: to smooth or not to smooth?"
  authors: ["Silverman, B. W.", "Young, G. A."]
  year: "1987"
  doi: null
  arxiv_id: null
- title: "A Distribution-Free Theory of Nonparametric Regression"
  authors: ["Györfi, L.", "Kohler, M.", "Krzyżak, A.", "Walk, H."]
  year: "2002"
  doi: null
  arxiv_id: null
- title: "Foundations of Quantization for Probability Distributions"
  authors: ["Graf, S.", "Luschgy, H."]
  year: "2000"
  doi: null
  arxiv_id: null
- title: "Membership Inference Attacks Against Machine Learning Models"
  authors: ["Shokri, R.", "Stronati, M.", "Song, C.", "Shmatikov, V."]
  year: "2017"
  doi: null
  arxiv_id: "1610.05820"
- title: "Calibrating Noise to Sensitivity in Private Data Analysis"
  authors: ["Dwork, C.", "McSherry, F.", "Nissim, K.", "Smith, A."]
  year: "2006"
  doi: null
  arxiv_id: null
~~~
