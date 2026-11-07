contract_role: da
## Dimension Scores

### D1: methodology_rigor
score: not_assessed

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "an equivocation between closely related notions"

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

Strongest counter-argument. The paper's thesis has two halves: (i) within the exact empirical field at positive bandwidth, the practitioner knobs (label noise, coarse label resolution, classifier-free guidance) reweight but never leave the training atoms, and exactly one composition (guidance on a label-averaged field) does; (ii) therefore, in standard trained models, a sample far from the training set reflects late-time learned-field error rather than the sampler. A hostile reader can argue that the first half is mathematically sound but practically narrow, and that the second half is close to definitional. On (i): the single composition that leaves the atoms requires a field average over labels, and the paper's own Proposition B.6 shows that the natural model of coarse label resolution, a label bottleneck, averages priors instead and keeps the atoms; the learned label-averaging pilot also shows networks need not follow exact field averages. So the composition result is attached to a knob ("coarse label resolution") that the paper itself shows does not produce the required object. The authors say this in the Conclusion ("existence result, not a mechanism we expect in standard models"), but the abstract opens by framing all three as "the knobs a practitioner turns", which invites the reading that guided label averaging is a practical route to novelty. On (ii): Theorem 5.1 is an exact variation-of-constants identity plus a lim sup; Appendix C.4 concedes that the measured certificate agreement "is the identity of the theorem". Any departure of a learned flow from the exact flow is, by construction, a learned-field error, so the dichotomy "learned-field error, not the sampler" carries little empirical content beyond the observation that the exact field has no off-atom endpoints. The theorem is also scoped to an identifying label (h = 0), while the off-atom image samples it is used to interpret occur at h in {4, 5, 6}, where only the local Proposition C.1 applies.

Logic chain: "collapse". The abstract and Section 6.1 say trained networks "collapse in finite time as the hard-conditioning theory predicts". The theory's collapse is an endpoint atom (Proposition 3.2). Proposition C.2(a), however, shows that a velocity MLP with a smooth time embedding has an absolutely continuous endpoint law with no atom, and the appendix itself says collapse "can only be approached at a finite cutoff". The EXP-1 evidence is a conditional variance falling to 0.120 at a cutoff of 1 - t = 10^-3, not zero. The experiments thus show that training drives the network toward the exact minimiser at a finite cutoff, which follows from the L2 projection, not that the network inherits the theorem's endpoint atom. "Collapse" is used for both the exact endpoint atom and small variance at a finite cutoff without marking the switch. This is the main equivocation behind the D3 warn.

Logic chain: framing sentence versus Table 1. Line 90 states that no single intervention in Table 1 creates new samples, yet Table 1 lists averaging of identifying hard-label fields (every endpoint can move to a circumcentre) and endpoint noise (a density) as single interventions that leave the atoms, and the next sentence lists them as exceptions. The abstract is correctly scoped to positive bandwidth, so this is a local repair (Minor), but it is the sentence a reader takes as the paper's summary.

Scope of "exactly one composition". Read as compositions of the three named knobs at h > 0 (averaging, guidance, and their combination, with label noise always present), the claim is defensible: averaging alone and guidance alone keep the atoms, and their combination can leave. Read more broadly it is not supported: the Limitations say composites other than guided label averaging are not covered, and Section 1 notes that signed combinations of more than two fields can fail. I treat this as an exposition issue (Minor), not a defect in the theorem.

Cherry-picking in the CIFAR-10 composition check. The abstract says exact computations "confirm the threshold, also on isolated pairs of CIFAR-10 images". The eight pairs are the largest-margin ones among 81 mutual-nearest-neighbour pairs; the bandwidth is set per pair so that B = 1; and the averaging measure sits on the pair's own two labels. The appendix states the threshold "is not new evidence", since Theorem B.10(c) and Corollary B.11 already decide it once the face condition holds. The computation is a valid consistency check and measures basin sizes (mean midpoint fraction 0.186 at 2wc), but the abstract presents a selected, theorem-implied check as independent image-scale confirmation.

Learned reproduction depends on oracle information. The learned basin appears only with the input asinh(tx/(1 - t)^2) centred at the known tie; centred elsewhere (cfm_x_o) the midpoint stays empty, and the appendix concludes the composition "is learned only by a network told where the tie is". The velocity network with the input fails in some seeds (one of five at B = 1 and 2wc; three of five at B = 2 and 5wc; all at B = 3). The data-predicting plain-input network leaves the midpoint empty, as Proposition C.2(b) predicts, although C.2(b) assumes a clipped bounded prediction and the trained network is not clipped. The abstract does say "centred at the known tie", so I keep this Minor; it limits "networks ... do" to an oracle-assisted positive control in d <= 2.

Alternative explanations not ruled out. For the image-scale h > 0 off-atom samples (0.158 to 0.254 after refinement), the paper names patch-mosaic composition (Kamb and Ganguli; Niedoba et al.) and non-integrable Lipschitz behaviour as accounts, but tests neither, because the checkpoints were not kept. The log-log variance slope of 0.481 at h = 4 against the exact value 1 shows that at image scale the label-smoothing reference does not describe the trained model. This limits how far the "learned fields inherit collapse" message extends past hard conditioning; the abstract states the departure, so the issue is caveat placement rather than concealment.

Other local gaps (Minor). The stability claim in the abstract excludes perturbation of the atom geometry (stated in Section 4.3 but not in the abstract sentence). In Table 10 at d = 8 and w <= 2wc, sink fractions fall below the 1/2048 resolution, so the spectral criterion's "positive fraction" is unconfirmed numerically there. All exact composite probabilities are floating-point computations without interval arithmetic, which the paper discloses.

Overall: the theorems in Sections 3 and 4 appear internally consistent and carefully scoped in their formal statements, and the paper is candid in its Limitations and Conclusion. The coherence problems lie in the bridge from exact fields to practice: the meaning of "collapse", the practical status of the field-averaging knob, and the near-definitional transfer claim. Each is repairable by rewriting and rescoping, with no new theory needed, so D3 is warn rather than block, and no single defect reaches rejection level.

#### CRITICAL

| # | Issue | Evidence Anchor | Confidence | Remedy |
|---|---|---|---|---|

#### MAJOR

| # | Issue | Evidence Anchor | Confidence | Remedy |
|---|---|---|---|---|
| M1 | "Collapse" equivocates between the exact endpoint atom of Proposition 3.2 and small conditional variance at a finite cutoff. Proposition C.2(a) rules out endpoint atoms for standard velocity networks, so the experiments cannot show collapse "as the theory predicts" in the theorem's sense. | text: Abstract l.30 "collapse in finite time as the hard-conditioning theory"; App. C.2 "endpoint law has no atom anywhere, and collapse can only be approached at a finite cutoff." | 4 (direct reading of the abstract, Prop. 3.2, Prop. C.2(a) and Sec. 6.1) | Define finite-cutoff collapse separately from the endpoint atom, and restate the experimental claim as convergence toward the exact minimiser at a cutoff. |
| M2 | The one off-atom composition depends on a field average over labels, but the paper's own Proposition B.6 shows that a label bottleneck (the concrete coarse-resolution learner) averages priors and keeps the atoms. Framing "coarse label resolution" as a practitioner knob that yields the composite therefore overstates the practical reach of Theorem 4.6. | text: Abstract l.11 "Label noise, coarse label resolution and classifier-free guidance are the knobs a"; Conclusion "label bottleneck does not even produce the averaged field" | 4 (internal comparison of abstract framing with Prop. B.6 and the label-averaging pilot) | In the abstract and introduction, state that field-level label averaging is a modelling hypothesis that a bottleneck does not realise, and move the existence-result caveat into the abstract. |
| M3 | The transfer claim that off-training samples reflect late-time field error "rather than the sampler" is close to definitional. Theorem 5.1 is an identity plus a lim sup, which App. C.4 concedes, and it holds only at an identifying label, yet it is used to interpret h greater than 0 image samples. | text: Abstract l.27 "so in standard models a sample far from the training set reflects that"; App. C.4 "this agreement is the identity of the theorem" | 4 (reading of Thm. 5.1, Prop. C.1 scope and App. C.4) | Restrict the inference to identifying labels, or state what observation could falsify the field-versus-sampler attribution at h greater than 0. |
| M4 | The CIFAR-10 composition check is presented as confirming the threshold, but it uses the 8 largest-margin pairs out of 81, a bandwidth tuned per pair to B = 1 and an averaging measure on the pair's own labels, and the appendix concedes the threshold is not new evidence. | text: App. E.3 "these eight are the ones with the largest margin"; Abstract l.28 "Exact computations confirm the threshold," | 3 (selection protocol read from App. E.3; impact on the reader's inference is a judgement) | Describe it in the abstract as a consistency check of Theorem B.10(c) on selected pairs, and report midpoint fractions over all 81 mutual-nearest-neighbour pairs or a random subset. |
