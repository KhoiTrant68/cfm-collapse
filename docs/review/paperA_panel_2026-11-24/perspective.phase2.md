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
trigger: "only partly bridged by experiments"

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Reviewer Identity

Peer Reviewer 3 (perspective seat). I work on privacy and training-data extraction for generative models: membership inference, extraction attacks, and differential privacy. I read the paper as a privacy auditor would. My question is whether the practical guidance it gives to practitioners and auditors follows from results that are proved for the exact empirical optimum. I did not check the proofs. Mathematical details are outside my competence, and I take the theorems as stated. I reviewed the TMLR build: the `\else` branches of `\ificlr`, without LaTeX comments.

### Overall Recommendation

Major Revision, from this seat only. The mathematical core is not in question here. The changes I ask for are mostly rewrites of the practice paragraph in §1 ("What this means in practice"), the conclusion and the broader-impact statement, plus one small added analysis (W2). They are listed below.

### Confidence Score

4. I am confident on the privacy and auditing side. I relied on the authors for every theorem.

### Calibration Status

`NOT_CALIBRATED`

### Criterion-Bound Judgements

| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| D4 cross_disciplinary_relevance | Sprint contract D4 with my Phase 1 scoring plan (criteria_binding_unavailable) | PARTLY_MEETS | text: §1 "which an audit should count as leakage rather than as new samples"; text: §8 "the composition of conditions is the operation an audit should examine" | The guidance says it holds at the exact optimum, and the limitations are stated frankly. But the guidance to auditors runs against the paper's own learned-network and CIFAR-10 evidence. Blends are called leakage with no criterion. The paper does not engage the privacy literature. | I did not check whether the theorems are correct. | yes: this is the basis for the D4 warn |

### Summary Assessment

The paper asks which sampler interventions can move the endpoints of the exact empirical conditional flow-matching field off the training set. These interventions are label noise, label averaging, guidance and its schedules, negative prompts, and the conjunction used in compositional generation. The paper opens by saying this matters for copyright and privacy, and it closes with advice for auditors.

From a privacy standpoint, three of its messages are useful and well put. First, these knobs give no guarantee against replication at the optimum. Second, endpoint noise moves the support without hiding the source. Third, composition is presented as a "boundary marker". Each is stated with care.

The step from "what happens at the exact optimum" to "what an auditor should do" is weaker than the wording suggests, for four reasons:
- The conclusion tells auditors to examine composition, but the paper's own trained networks do not produce the blend. Its trained CIFAR-10 networks leave a sizeable fraction of samples off the training images for reasons the theory does not cover.
- Blends are declared leakage without a criterion. The nearest-neighbour criterion the paper itself uses to measure memorisation classifies a two-image midpoint as not memorised.
- The claim that the returned record is predictable has no threat model, and the paper's own image-scale experiment shows trained networks do not follow the reference that makes it predictable.
- The privacy literature, including works already present in the bibliography file, is not cited where the paper makes privacy claims.

These problems are fixable mostly by rewriting.

### S1: Composition is framed honestly as a boundary marker
The abstract and §1(iii) say plainly that the blend mechanism is an existence result at the edge of the theory, not a demonstrated route to leakage in deployed models. This keeps privacy readers from over-reading Theorem 3.
**Evidence Anchor**: text: Abstract "We therefore present the composition as a boundary marker, not a practical mechanism."

### S2: Correct statement of what endpoint noise does not give
The paper says explicitly that changing the support is not the same as hiding the source, because the nearest atom of a lightly noised sample recovers the record. This is the distinction the privacy community most often has to explain to generative-modelling papers.
**Evidence Anchor**: text: App. Endpoint noise "it does not by itself hide the source record, since for small noise the nearest atom of a sample recovers it"

### S3: The scope of the composition results is stated frankly
The Limitations section says that trained text-conditioned compositional samplers are not tested. That is the setting in which an auditor would actually meet composition.
**Evidence Anchor**: text: §7 Limitations "Trained compositional samplers on images, where the conditions are text prompts rather than labels, are not tested."

### S4: A negative image-scale result is reported rather than hidden
The CIFAR-10 label-noise experiment fails to follow the exact reference across conditions, and the paper says so with intervals over three training-set draws.
**Evidence Anchor**: text: §6 "so at image scale the generated variance does not follow the reference across conditions"

### S5: A concrete picture of what a blend is
Panel (d) of the triangle figure (`fig:unrolled`) shows two CIFAR-10 training images and their midpoint. An auditor can see what "blend" means at image scale.
**Evidence Anchor**: figure: Figure 2 (`fig:unrolled`), panel (d), the CIFAR-10 pair and its midpoint

### W1: The audit recommendation points away from where the paper's own evidence locates off-atom outputs
**Problem**: The conclusion tells auditors that composition is "the operation an audit should examine". The paper's own evidence on trained networks points elsewhere:
- Standard velocity networks place at most 0.001 of their sources at the blend (§6).
- Every learned network leaves the edge-midpoint blends of the triangle empty.
- The trained CIFAR-10 networks with label noise, without any composition, leave 0.168 (h=4) and 0.276 (h=6) of their samples off the training images at the cutoff.
- The standard network leaves 0.16 to 0.79 of its sources far from every atom and every blend.

So in this paper's trained models, off-atom outputs come from learned-field error, which the theory does not describe. They do not come from the composition mechanism. The practitioner sentence in §1(i) has the same gap in reverse. It says any reduction in copying from a knob comes "only from the error of the learned field". That is a claim about trained models, and the paper does not test it (see W7).
**Evidence Anchor**: text: §8 Conclusion "the composition of conditions is the operation an audit should examine"
**Why it matters**: An auditor reading the conclusion would put effort on compositional prompts. The paper's own results suggest that, for trained models, composition is the least likely of the studied settings to produce blends. They also suggest that label-noised and guided samplers already produce non-copies whose relation to training records is uncharacterised.
**Suggestion**: Make the conclusion conditional, along the lines of "at the exact optimum, composition is the only studied operation that can produce blends; in our trained networks it does not, unless the network resolves the (1−t)² layer". Add one sentence to the guidance for auditors saying that the off-atom fractions of trained models (§6) are not explained by the theory and need their own extraction or nearest-neighbour test. Move the boundary-marker caveat from the abstract into the conclusion's practice sentence, so the two cannot be read apart.
**Severity**: Major
**Confidence**: 4 — core expertise: extraction audits of trained generative models

### W2: Blends are declared leakage without a criterion, and the paper's own memorisation criterion counts them as novel
**Problem**: §1(i) says circumcentres of training images are leakage "rather than new samples". No operational criterion supports this. The paper's own memorisation measure is the nearest-neighbour ratio test of Yoon et al. (Appendix, CIFAR-10 protocol): a sample counts as memorised only if its nearest training image is at most 1/3 as far as the second nearest. That test classifies the midpoint of two training images as off-atom, that is, as not memorised, because the ratio is exactly 1. The standard extraction definition of Carlini et al. (2023), (ℓ2, δ)-closeness to a single record, would usually not flag it either. The paper's prescriptive definition and its measurement instrument therefore disagree, and the paper does not say so. There is also a dilution question. A circumcentre of k atoms (the simplex face centroids of §6, up to nine images) carries less of each record as k grows. A single "count as leakage" rule cannot cover all k.
**Evidence Anchor**: text: §1 What this means in practice "which an audit should count as leakage rather than as new samples"
**Why it matters**: To a privacy reader, "leakage" means an adversary learns something specific about a record. The paper never shows that a blend lets anyone learn a record. A strong argument for the claim exists and is missing. If an adversary already holds one image of a two-atom tie, the midpoint z gives the other image exactly as 2z − x^i. More generally, a blend together with side information is a linear constraint on the records it averages. Without this kind of argument, the claim reads as a definitional choice, and it contradicts the paper's own measurement tool.
**Suggestion**: Either (a) state a leakage criterion that covers blends, for example reconstruction of a record from a blend given side information on the other k−1 records, or a perceptual-similarity threshold of the kind used by Somepalli et al. (2023), and note that the ratio test of §6 cannot detect two-atom blends; or (b) weaken the wording to "an audit using single-record nearest-neighbour criteria will miss these; whether they constitute leakage depends on the adversary's side information". In either case, re-examine the 0.168 and 0.276 CIFAR-10 off-atom fractions. Report how many of those samples lie near a pairwise midpoint, so the reader knows whether the ratio test is hiding blends there.
**Severity**: Major
**Confidence**: 4 — core expertise: definitions of extraction and replication in the privacy literature

### W3: "The returned record is predictable" has no threat model, and the paper's own image-scale evidence does not support it for trained models
**Problem**: §1(ii) says an auditor can rank, for any label, the records an exact-optimum model returns. This ranking requires the full set of training labels, the bandwidth h and the exact field. The paper does not say who has these. In the paper's own image experiment (CIFAR-10 inpainting) the label is the top half of the image, so "knowing the labels" means already holding half of every training record. The broader-impact statement then says the same predictability helps "an adversary who knows the labels", again with no statement of what that adversary gains beyond what it already knows. Finally, the trained U-Nets do not follow the label-noise reference across conditions: the log–log slopes are 0.34, 0.32 and 0.43 against 1, and the median ratio is 5.30 at h=4. On images, then, the ranking would not predict what a trained model returns.
**Evidence Anchor**: text: §1 What this means in practice "so an auditor can rank, for any label, the records an exact-optimum model returns"
**Why it matters**: Auditors and adversaries differ mainly in their knowledge and their access. A predictability claim with no stated knowledge model cannot be turned into an audit procedure or a risk assessment. Here the image-scale evidence also argues against transfer to trained models.
**Suggestion**: State the knowledge assumed: the training labels, h, and query access. Say what the ranking adds over a membership-inference or extraction attack with the same knowledge. Restrict the claim explicitly to the exact optimum, and add "our CIFAR-10 networks do not follow this reference (§6)" next to it, not only in Limitations. If the authors want the claim to be usable, an auditor-facing experiment would help: on the d=2 problem where networks do match the reference, does the top-ranked record by p_i^(h)(y) coincide with the nearest training record of trained-model samples?
**Severity**: Major
**Confidence**: 4 — core expertise: threat modelling for membership inference and extraction

### W4: The privacy and extraction literature is not engaged where the paper makes privacy claims
**Problem**: The abstract opens with copyright and privacy, and the paper uses "replication", "copying", "leakage", "memorisation" and "extraction-relevant" auditing language. The only privacy-side works cited are Somepalli et al.'s copying-mitigation paper, Wen et al. (2024), Yoon et al. (as a criterion) and Dwork & Roth (2014). The bibliography file contains Carlini et al. (2023), "Extracting Training Data from Diffusion Models", Somepalli et al. (CVPR 2023), "Diffusion Art or Digital Forgery?", and Sesmat et al. (2026) on membership signals in flow matching, but none of them is cited in the text, so none appears in the reference list. No membership-inference work on diffusion or flow models is cited.
**Evidence Anchor**: absence: §1 and §2 Related work — expected citation of and positioning against the training-data-extraction, replication-detection and membership-inference literature for diffusion/flow models; checked abstract, §1 (including "What this means in practice"), §2, §7, §8, broader-impact statement, and refs.bib (entries `carlini2023extracting`, `somepalli2023diffusion`, `sesmat2026leaks` present but uncited)
**Why it matters**: Privacy readers will judge the "leakage" and "audit" language against these works. Carlini et al. give the operational extraction definition that W2 needs. Somepalli et al. give the replication-detection practice an auditor would use. Membership-inference work is the standard audit tool, and the paper's predictability claim (W3) should be compared with it.
**Suggestion**: Add a short "Relation to privacy and extraction" paragraph in §2. Cite the three uncited entries and at least one membership-inference work on diffusion models (e.g., Duan et al., 2023; Matsumoto et al., 2023). Define "replication" and "leakage" operationally once, in §3 or §1.
**Severity**: Minor
**Confidence**: 5 — core expertise: this literature; bibliography checked directly

### W5: The endpoint-noise and differential-privacy remark omits the point that matters most to a privacy reader
**Problem**: The broader-impact statement and §1(i) say that endpoint noise carries no formal guarantee "unless its randomisation is calibrated in the sense of differential privacy", which the paper does not analyse. That is correct but incomplete in a way that could mislead. The endpoint law of Proposition `prop:tgtnoise` is a mixture of Gaussians centred on the training records. Every sample is an independent noisy copy of one record. An adversary who draws M samples for a query can cluster them and average, which recovers x^i to error of order ρ/√M. No fixed ρ therefore protects against an unbounded query budget, and protection against a single sample would need ρ on the order of the data diameter, which destroys utility. Formal guarantees for diffusion-type models attach to the training algorithm (for example DP-SGD in Dockhorn et al., 2023), not to output-side noise on an exact empirical field. The current wording suggests that DP is one calibration step away from this mechanism.
**Evidence Anchor**: text: Broader impact statement "a formal guarantee requires randomisation calibrated in the sense of differential privacy, which we do not analyse"
**Why it matters**: Practitioners might read endpoint noise as a privacy knob. The paper's own law shows that repeated sampling defeats it.
**Suggestion**: Add two sentences: (1) repeated samples average the noise out, so endpoint noise gives no protection against an adversary with many queries; (2) DP guarantees for these models come from private training (cite Dockhorn et al., 2023), not from noise on the endpoint of the exact field.
**Severity**: Minor
**Confidence**: 4 — core expertise: differential privacy for generative models

### W6: The broader-impact statement does not discuss what the results offer an adversary beyond label-based prediction
**Problem**: The broader-impact statement mentions adversaries only in one clause, about predictability under label noise. It does not discuss the dual-use reading of the paper's other results. Guidance at a fixed strength keeps the support on the training atoms and, in Figure 2(b), concentrates almost all the mass on one record. Proposition `prop:cfgatom`(b) shows that at a hard label guidance collapses every source onto the record. To an extraction adversary, these results suggest raising guidance as an amplifier. The paper's composition thresholds also tell an adversary which prompt combinations would elicit blends of chosen record pairs.
**Evidence Anchor**: text: Broader impact statement "which helps auditors and, equally, an adversary who knows the labels"
**Why it matters**: A broader-impact statement in this area is expected to weigh what the results enable for extraction, not only what they deny to mitigation.
**Suggestion**: Add a sentence noting that, at the exact optimum, increasing guidance concentrates the endpoint law on fewer records, so high guidance is a plausible extraction amplifier. Note that this agrees with empirical reports linking guidance to memorisation (`jain2025attraction`, `kim2025how`, already cited). Say whether the authors see any misuse risk in the composition thresholds.
**Severity**: Minor
**Confidence**: 4 — core expertise: extraction attacks on diffusion models

### W7: The practitioner prediction "it need not survive a closer fit" is testable but untested
**Problem**: §1(i) says any reduction in copying that a knob gives in a trained model comes from learned-field error and need not survive a closer fit. For practitioners this is the most actionable sentence in the paper: it predicts that copying mitigations weaken as models are trained longer or made larger. The paper has trained networks at several iteration counts (200k steps on the d=2 problem, and CIFAR-10 retrainings), but it does not measure replication against training length or capacity, with and without the knob.
**Evidence Anchor**: text: §1 What this means in practice "only from the error of the learned field, and it need not survive a closer fit"
**Why it matters**: An untested prediction in the practice paragraph will be quoted as a finding.
**Suggestion**: Either label the sentence explicitly as a hypothesis the exact field suggests, or add a small check. On the d=2 problem, report the nearest-training-point fraction with and without label noise across checkpoints. On CIFAR-10, report it across the existing retrainings.
**Severity**: Minor
**Confidence**: 3 — adjacent: I can judge the inference but not how costly the experiment is in this codebase

### Detailed Comments

#### Assumption Audit
- **Explicit assumptions**: The exact empirical optimum, a fixed training set, identifying labels, and strictly positive priors. The paper states these well. My concern is not the assumptions themselves but that the practice sentences sometimes drop the "at the exact optimum" qualifier (W1, W3).
- **Implicit assumptions**: (a) That "returns a training record" and "leaks a training record" are the same question. Privacy separates replication from the question of what an adversary can learn (W2, W5). (b) That an auditor has white-box knowledge of the training labels and the bandwidth (W3). (c) That nearest-neighbour ratio tests detect replication. They miss multi-record blends (W2).
- **Paradigmatic assumptions**: Support of the endpoint law is used as the measure of privacy-relevant behaviour. Privacy work instead measures distinguishability (membership) or recoverability (extraction). Support is necessary for extraction but is neither the same thing nor sufficient.

#### Cross-Disciplinary Connections
- **Parallel research**: Extraction attacks and replication detection on diffusion models (Carlini et al., 2023; Somepalli et al., 2023). Membership inference on diffusion models (Duan et al., 2023; Matsumoto et al., 2023) and on flow matching (Sesmat et al., 2026). Differentially private diffusion models (Dockhorn et al., 2023).
- **Borrowing opportunities**: The (ℓ2, δ) extraction definition and its relaxations would give the blend-as-leakage claim operational content. Reconstruction from linear constraints with side information (the 2z − x^i argument) is the natural privacy reading of circumcentres.
- **Methodological borrowing**: A small extraction-style audit on the d=2 and CIFAR-10 networks would directly link the exact-optimum statements to trained models (W3, W7): generate many samples per label and count samples within δ of a record or of a pairwise midpoint.

#### Practical Impact
- **Real-world application**: The clearest practical value is negative. Label noise, label averaging, guidance schedules and negative prompts are not privacy mechanisms at the optimum. This is useful and correctly stated.
- **Implementation feasibility**: The "rank records by p_i^(h)(y)" audit needs the training labels and h. That may be realistic for an internal auditor, but not for an external one (W3).
- **Stakeholders**: Data subjects whose images form the circumcentres. Their exposure depends on the side information of others, which the paper does not discuss.

#### Broader Implications
- **Ethical dimensions**: The broader-impact statement is specific, not generic, which is good. It is incomplete on adversaries (W6) and on what endpoint noise does not give (W5).
- **Social impact**: No personal data are used; CIFAR-10 is public.
- **Future directions**: Extending the composition analysis to text-conditioned samplers with an extraction-style audit. Characterising the trained-model off-atom samples of §6 in privacy terms.

### Cross-Disciplinary Reading Recommendations
- Carlini et al. (2023), Extracting Training Data from Diffusion Models. Gives the operational extraction definition needed for W2. It is already in refs.bib.
- Somepalli et al. (2023), Diffusion Art or Digital Forgery? Investigating Data Replication in Diffusion Models. Replication detection by similarity search. Already in refs.bib.
- Duan et al. (2023), Are Diffusion Models Vulnerable to Membership Inference Attacks? Membership inference for diffusion models, the standard audit tool.
- Matsumoto et al. (2023), Membership Inference Attacks against Diffusion Models. Shows the vulnerability depends on the time step, which relates to the time-scale analysis here.
- Sesmat et al. (2026), Where Flow Matching Leaks: Characterising Membership Signals Along the Interpolation Path. Membership signals specific to flow matching. Already in refs.bib.
- Dockhorn et al. (2023), Differentially Private Diffusion Models. Where formal guarantees for these models actually come from (W5).

~~~yaml suggested-references
- title: "Extracting Training Data from Diffusion Models"
  authors: ["Carlini, N.", "Hayes, J.", "Nasr, M.", "Jagielski, M.", "Sehwag, V.", "Tramèr, F.", "Balle, B.", "Ippolito, D.", "Wallace, E."]
  year: "2023"
  doi: null
  arxiv_id: "2301.13188"
- title: "Diffusion Art or Digital Forgery? Investigating Data Replication in Diffusion Models"
  authors: ["Somepalli, G.", "Singla, V.", "Goldblum, M.", "Geiping, J.", "Goldstein, T."]
  year: "2023"
  doi: null
  arxiv_id: "2212.03860"
- title: "Are Diffusion Models Vulnerable to Membership Inference Attacks?"
  authors: ["Duan, J.", "Kong, F.", "Wang, S.", "Shi, X.", "Xu, K."]
  year: "2023"
  doi: null
  arxiv_id: "2302.01316"
- title: "Membership Inference Attacks against Diffusion Models"
  authors: ["Matsumoto, T.", "Miura, T.", "Yanai, N."]
  year: "2023"
  doi: null
  arxiv_id: "2302.03262"
- title: "Where Flow Matching Leaks: Characterising Membership Signals Along the Interpolation Path"
  authors: ["Sesmat, T.", "Meseguer-Brocal, G.", "Peeters, G."]
  year: "2026"
  doi: null
  arxiv_id: "2606.07271"
- title: "Differentially Private Diffusion Models"
  authors: ["Dockhorn, T.", "Cao, T.", "Vahdat, A.", "Kreis, K."]
  year: "2023"
  doi: null
  arxiv_id: "2210.09929"
~~~

### Questions for Authors
1. Under what adversary knowledge does a circumcentre of k training images reveal a record? Is k=2 with one known image (z gives x^j = 2z − x^i) the case you have in mind?
2. Of the CIFAR-10 trained-network samples the ratio test classifies as off-atom (0.168 and 0.276), how many lie near a pairwise midpoint of training images?
3. Who is assumed to know the training labels and h in the predictability claim, and what does the ranking give beyond a standard membership-inference or extraction attack with the same knowledge?
4. Given that standard trained networks do not reach the blend, what concrete audit procedure would you recommend for compositional prompts in deployed samplers?
5. Do you expect higher guidance to raise extraction rates in trained models, as the exact-optimum concentration in Figure 2(b) suggests?

### Minor Issues
- "Replication", "copying", "memorisation" and "leakage" are used interchangeably across §1, §2 and the broader-impact statement. A single definition would help privacy readers.
- In §1(ii), "Under guidance the support is the same but the weights have no closed form" also limits the auditor ranking under guidance. Say so explicitly there.
