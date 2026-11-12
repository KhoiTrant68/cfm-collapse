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
trigger: "The exposition is correct but hard to navigate."

### D6: venue_fit_and_contribution
score: warn
trigger: "The contribution is real and fits the venue but is modest or incrementally framed."

## Review Body

Reviewer identity: ICLR Area Chair, generative-model theory (diffusion and flow matching), with session-chair experience on memorisation and generalisation. criteria_binding_unavailable: no author-confirmed venue criteria brief was bound to this run, so I judge fit against general expectations for an ICLR main-track theory-plus-experiments paper. I make no claim that this card matches any official ICLR 2027 criteria.

Summary. The paper asks which common interventions on the exact empirical conditional flow-matching field can move its endpoints off the training set. It proves that label smoothing, positive field mixtures (which include label averaging and negative guidance), and nonnegative guidance with a fixed strength or a bounded-variation schedule all end on training atoms for almost every source. It then proves that composing guidance with label averaging can produce a non-training endpoint with positive probability, with an exact threshold w > 1/sinh^2 B for two atoms and a spectral criterion in any dimension. A conditional transfer theorem bounds a learned endpoint's distance from its atom by the limiting scaled field error. Experiments run from small MLPs to a 35.75M-parameter CIFAR-10 U-Net. The paper fits ICLR's scope, and the theory is stated carefully and in a falsifiable form. My concerns are editorial and strategic. The ML takeaway is weak and spread across many qualified statements. The one off-support mechanism is not reproduced by standard networks. The novelty of the positive results relative to the closest convergence results is argued in a single sentence. As it stands I place the paper in the borderline band for ICLR, below the acceptance line on presentation and significance more than on correctness. A focused rewrite of the abstract, introduction and conclusion, plus a sharper positioning paragraph, could move it to a competitive weak accept. My overall signal is Major Revision.

### S1: A clear question answered in a single summary table
The paper reduces its contribution to one question: which interventions keep the exact endpoint law atomic. Table 1 then gives the answer for each intervention with a pointer to the result that proves it. An ICLR reader can see the whole picture at a glance.
**Evidence Anchor**: table: Table 1 — endpoint support per intervention (hard conditioning, label noise, positive mixtures, guidance, guidance after label averaging, endpoint noise) with result pointers

### S2: An exact and robust threshold for the composition mechanism
The composition result is exact rather than asymptotic. The slope of F_w at the tie gives the threshold in closed form. The paper states that the threshold is stable under perturbation of the priors, the mixture weights and the guidance strength, and it checks the threshold with exact fields on pairs of CIFAR-10 images. This is the most novel piece of the paper.
**Evidence Anchor**: equation: Eq. (6) — F_w(s) and the tie slope F_w'(0) = (1 + w) sech^2 B − w, which turns negative exactly when w > 1/sinh^2 B

### S3: Calibrated claims and an explicit limitations section
The paper repeatedly separates what is proved for exact fields from what is observed in trained networks. It does not claim that trained networks implement the theorems. Reviewers will value this honesty.
**Evidence Anchor**: text: Section 7 "The theorems concern exact fields of a fixed training set and do not say that a trained network"

### S4: Experiments designed so they could fail
The exact-field checks use a prespecified failure threshold. The learned experiments report seeds and population standard deviations. This follows good practice for theory-validation experiments.
**Evidence Anchor**: text: Section 6.2 "exceeds the prespecified threshold of 1% of the minimum atom separation."

### S5: A transfer bound that is tight and simple
Theorem 5.1 is short and attained, and its data-prediction form gives practitioners a quantity they can measure: the late-time endpoint-prediction error.
**Evidence Anchor**: text: Section 5 "The bound is attained: for ∆(x, t) = c/(1−t) both sides equal |c| from every x0."

### S6: Main text within 9 pages, with an organised appendix
The main text fits in 9 pages. The appendix opens with a notation table, a proof roadmap and a dependency figure, and each result is restated before its proof. This makes checking much easier.
**Evidence Anchor**: text: Section 1 "which open with a notation table and a proof roadmap (Tables 2 and 3)."

### W1: No single ML headline; the paper reads as a chain of qualified theorems
Problem: The abstract, the contribution bullets and the one-sentence conclusion all list results with their qualifiers ("almost every initial point", "bounded nonnegative schedule of bounded variation", "null set that can be a hyperplane"). None of them says what an ICLR reader should take away about generalisation in practice. The conclusion restates the results and has no discussion of implications.
Why it matters: ACs and reviewers decide quickly from the abstract and introduction. Without a stated consequence, such as "the standard sampler-side knobs cannot by themselves explain novel samples, so generalisation must come from the learned error at late times", the paper will be read as technically solid but of narrow interest.
Suggestion: Lead the abstract with a two-sentence headline and a single consequence. Move most qualifiers into the theorem statements. Replace the conclusion with a short discussion that covers what the results imply for practitioners using CFG and label noise, what they imply for the memorisation and generalisation debate, and which open questions remain.
**Severity**: Major
**Evidence Anchor**: text: Section 8 "The exact flow and its positive modifications end on training examples, guided label averaging can"
**Confidence**: 4 — core AC experience judging ICLR framing and significance

### W2: The one off-support mechanism is not realised by standard trained networks, and the paper does not draw the consequence
Problem: The positive-probability non-training endpoint from guided label averaging appears in learned networks only when they receive an engineered blow-up input. Standard velocity CFM networks place essentially no mass at the midpoint, and the paper itself says reproduction is not robust across seeds. The paper reports this honestly but does not say what it means for the main question.
Why it matters: For ICLR readers the practical answer to "can interventions move endpoints off the training set" then seems to be "not in standard models". That either weakens the significance of Theorems 4.6 and 4.7 or, read the other way, is itself the headline. The paper needs to choose one and argue it.
Suggestion: State explicitly whether the composition result is a mechanism expected in practice or an existence result that marks the boundary of the positive theorems. If it is the latter, frame the learned-network finding as evidence that standard parametrisations smooth away the (1 − t)^2-scale tie, and link this to Proposition C.2. If feasible, add one learned composition run beyond d ≤ 2, for example on the CIFAR-10 pairs where the exact threshold is already verified. Otherwise state this as an open question.
**Severity**: Major
**Evidence Anchor**: text: Section 7 "off-atom basin depends on its parametrisation, chiefly on its input, and not in every seed"
**Confidence**: 4 — core expertise in guidance and memorisation of learned diffusion and flow models

### W3: The novelty of the positive results against the closest convergence theorems rests on one sentence
Problem: Theorems 4.1 and 4.5 extend the known memorisation of the empirical minimiser to mixtures and guidance. Their stated advantage over Liu & Zuazua (2025, 2026) is that they prove convergence of every trajectory and null non-atom basins without a no-critical-limit-point premise. This delta is the main originality claim for half of the paper, but it appears as a single clause inside a dense related-work paragraph, with no explicit comparison of assumptions and conclusions.
Why it matters: Reviewers who know the closed-form and memorisation literature (Bertrand et al., Baptista et al., Liu & Zuazua, Chidambaram et al.) are likely to see the positive half as incremental unless the paper shows precisely what is new.
Suggestion: Add a compact comparison table, or a dedicated paragraph, giving for each closest prior result its setting (score vs CFM, mixture type, guidance), its assumptions, and its conclusion (every trajectory vs a.e., null basin, threshold). Give one example that the prior criterion does not cover and the present theorems do.
**Severity**: Major
**Evidence Anchor**: text: Section 1 "we prove convergence of every trajectory and null non-atom basins without such a premise"
**Confidence**: 3 — familiar with the area, but I did not re-read the cited Liu & Zuazua theorems

### W4: Key explanatory material sits in the appendix while the main text depends on it
Problem: The main text depends on appendix objects to make its argument. These include the proof-template figure (Figure 4), the trajectory illustration (Figure 5, cited in the introduction), the threshold plot (Figure 11), the spectral checks (Table 9), and the basin values (Tables 10 and 11). Section 4.4 is compressed to the point that its matrix threshold and numerical support can only be followed in Appendix B.6 and E.3.
Why it matters: An ICLR reader cannot follow the composition story from the 9 pages alone. This is the main reason I score D5 as warn.
Suggestion: Bring Figure 4 (the two-step template, with the point where composition fails Step 2) into Section 4, compressing Figure 1 if space requires. Consider moving most of Section 4.4 to the appendix, leaving a one-paragraph statement of Theorem 4.7, so that Sections 4.3 and 6.2 have room to breathe.
**Severity**: Minor
**Evidence Anchor**: text: Section 4 "composition is where Step 2 fails (Figure 4)"
**Confidence**: 4 — direct reading of the main text and appendix layout

### W5: The headline "composition breaks this" sits uneasily with the simpler hard-label averaging route
Problem: The abstract presents composition as what breaks atomicity. Table 1 and Section 4.1, however, note that averaging two identifying hard-label fields already sends every source to the midpoint. The reader is not told in the introduction why the positive-bandwidth composition is the interesting case, for example because it gives an open basin under strictly positive priors and is stable under perturbation, while the hard-label case is degenerate.
Why it matters: A reviewer skimming the paper may conclude that the composition result is unnecessary, which undercuts the headline.
Suggestion: Add one sentence to the abstract or introduction contrasting the two routes and saying why the composition result is the one relevant to practical samplers.
**Severity**: Minor
**Evidence Anchor**: text: Section 4.1 "sends every source to the midpoint. The null set in (b) cannot be removed"
**Confidence**: 4 — follows from the paper's own Table 1 and Section 4.1

### W6: The abstract ends on a disclaimer
Problem: The abstract is long and ends by stating what the experiments do not establish. That is accurate but weak as an OpenReview snippet. It also mixes the model size and finite-cutoff details into the main message.
Why it matters: The abstract is the first, and often the only, thing bidders read.
Suggestion: Keep the disclaimer, but move it into the experiments paragraph of the introduction. End the abstract on the takeaway from W1.
**Severity**: Minor
**Evidence Anchor**: text: Abstract "variance tracks the label-smoothing reference; these observations do not establish"
**Confidence**: 4 — standard ICLR presentation practice

### W7: The empirical scope behind the learned-model claims is narrow
Problem: The learned composition experiments use d ≤ 2. The synthetic problems use d ≤ 10. The image experiments use one mask and N = 2000, with instance and optimisation randomness confounded. The limitations section acknowledges all of this.
Why it matters: The paper does not overclaim, but the narrow scope limits how far ICLR readers will generalise the learned-network findings.
Suggestion: If compute allows, add a second mask or dataset size for the CIFAR-10 collapse result, and separate instance from optimisation seeds in at least one setting. Otherwise keep the current wording.
**Severity**: Minor
**Evidence Anchor**: text: Section 7 "the learned experiments use five seeds, the learned composition d ≤ 2 and the synthetic problems"
**Confidence**: 3 — general standards for empirical validation at ICLR; I did not inspect the experiment protocols in detail

Questions for the authors. (1) What practical recommendation follows from the results for practitioners who combine condition dropout, label noise and CFG? (2) Is there a regime of learned parametrisation (for example EDM-style preconditioning) in which the tie scale (1 − t)^2 would be resolved without the hand-added input? (3) Precisely which configuration of Theorem 4.1 or 4.5 falls outside Liu & Zuazua (2026, Theorem 3.18)?
