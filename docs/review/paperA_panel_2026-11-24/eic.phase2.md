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
trigger: "The manuscript can be followed but is costly to read."

### D6: venue_fit_and_contribution
score: warn
trigger: "The contribution is real but under-argued or modest."

## Review Body

### Reviewer Identity
Action editor for ML theory of diffusion and flow models, field-general. No venue is confirmed and no criteria binding was supplied, so fit is judged only against a general ML-theory readership, not against any named venue. I reviewed the TMLR build (the `\else` branches of `\ificlr`, with moved blocks printed in place). By configuration I did not check proofs line by line. Where I discuss proofs, I discuss their stated status, not their correctness.

### Overall Recommendation
Major Revision. This is a preliminary signal for the synthesizer, not an editorial decision.

### Confidence Score
4. I am confident about framing, positioning and structure. I am less confident about whether the prior-work comparisons are exhaustive: a quick literature search found no earlier analysis of composition endpoints on the exact empirical field, but that search was not systematic.

### Calibration Status
`NOT_CALIBRATED`

### Criterion-Bound Judgements
| Dimension / criterion | Criterion source | Judgement | Evidence anchors | Rationale | Uncertainty or scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| D5 writing_and_structure | contract D5; Phase 1 scoring plan | PARTLY_MEETS | text: §7 "These fractions count the centre only"; absence: §7 main-text tables | Navigation aids are strong (overview figure, Table 1, notation table, proof-roadmap table, restated results). However, §7 is dense, and its key numerical tables sit in Appendix E. Every headline result is stated in the main text, and I found no broken cross-reference, so the block trigger does not apply. | Judged on the LaTeX source; I did not inspect a compiled PDF for page count or float placement | yes: sets D5 at warn |
| D6 venue_fit_and_contribution | contract D6; Phase 1 scoring plan; configuration card | PARTLY_MEETS | text: Abstract "boundary marker, not a practical mechanism"; text: Use of LLMs disclosure | The composition results (Theorem 5.8, Theorem 5.10, Proposition 5.13) are original and well positioned. The label-noise result is declared not new. The guidance results are honest but incremental extensions of Liu et al. (2026). By the authors' own disclosure, the proofs of three statements, one of them a headline proposition, have not yet been checked line by line by the authors. | Novelty search was quick and not systematic; proof correctness not assessed (blind spot) | yes: sets D6 at warn, not block. The prior-work comparison exists, and the proved-versus-numerical status is clearly marked throughout. |

### Summary Assessment
The paper asks which modifications of the exact conditional flow-matching field can move its endpoints off the training set. The answer is organised by how many exact fields are combined and with which signs. Label noise is only a reweighting, and the paper presents it as a reference, not a new result. Positive mixtures, guidance with a fixed strength or with a schedule of bounded variation, and any combination of two fields with strictly positive priors end on atoms from almost every initial point. Guidance applied to an average of conditional fields, which is exactly the conjunction of compositional generation, reaches circumcentres of training points with positive probability. The two-atom threshold is the exact value $1/\sinh^2B$. A spectral criterion classifies the endpoints in any dimension, and at a two-atom tie a blend requires a subtracted intermediate field. The numerics are explicitly labelled as consistency checks, and they include a positive control and CIFAR-10 pairs in $d=3072$.

The theory is unusually well positioned. Each statement names the closest prior theorem (Wan et al. 2025 Thm 5.3, Liu et al. 2026 Thm 2.5, Azangulov et al. 2026 Thm 3, Baptista et al. 2025), and an appendix table compares them. On my configured focus question, the composition results carry the novelty. The label-noise part adds nothing new on its own, and the guidance part adds a null-set statement and an extension to schedules and prior averages. These are real but modest gains, and they are needed mainly as the contrast class for the composition story. The paper itself calls the composition a "boundary marker, not a practical mechanism". That honest framing also limits its significance for a general readership. The most pressing editorial issue is readiness: the printed LLM-use statement says the authors have not finished their own check of three proofs, including Proposition 5.13.

### Strengths

### S1: Candid positioning of each result against the closest prior theorem
The label-noise result is explicitly disclaimed as a consequence of Wan et al. (2025) Thm 5.3. The guidance results state precisely what Liu et al. (2026) already give (every trajectory converges) and what is added (the non-atom initial points form a null set; the extension to schedules and to prior averages). An editor rarely sees a delta this transparent.
**Evidence Anchor**: text: §1 Contributions item 1 "This is not a new result"

### S2: An explicit comparison table of hypotheses and conclusions
Table tab:comparison sets the dynamics, support, combination class and conclusion against Liu et al. 2025/2026, Wan et al. 2025 and Azangulov et al. 2026. The accompanying text gives the change of variables that makes the deterministic flows comparable. This is exactly the delta table my scoring plan looked for.
**Evidence Anchor**: table: Table tab:comparison (Appendix B.1), columns "Combination" and "Conclusion"

### S3: An original, sharp composition result with a closed form, a general criterion and a sign rule
The two-atom threshold is exact and explicit. The profile function $F_w$ has a closed form that makes the mechanism visible: averaging lowers the slope at the tie to $\operatorname{sech}^2B$. The result generalises to a spectral classification (Theorem 5.10) and to a sign rule for signed combinations at a tie (Proposition 5.13). Together they give the paper a memorable takeaway, "two fields reweight, three can blend", that I did not find anticipated in prior work.
**Evidence Anchor**: equation: Eq. (eq:composition-mean), $F_w(s)$ and the factor $\cosh^2s-w\sinh^2B$

### S4: Navigation aids that make a long manuscript tractable
The paper provides a one-figure overview, a support table for all interventions (Table 1), a one-paragraph proof template with a schematic, a notation table, and a proof-roadmap table naming each result's proof location and ingredients. Every main-text result is restated with its number before its proof.
**Evidence Anchor**: table: Table tab:roadmap (proof roadmap, appendix front matter)

### S5: Proved and numerical claims are kept visibly apart
Section 7 opens by saying the exact-field computations do not prove the theorems. The near-threshold law is labelled "a formal asymptotic law, not a theorem". Tables carry caveats about interval arithmetic. The CIFAR-10 classifier's zero fractions are explicitly said not to test Theorem 5.8(b).
**Evidence Anchor**: text: §7 opening "they do not prove them"

### S6: A positive control for the numerical stress test
The authors anticipated the obvious objection that an atom-biased integrator would pass the stress test. They ran the same scheme on a configuration with an attracting tie and showed that it recovers the exact basin.
**Evidence Anchor**: text: §7 "The stress test therefore sees an attracting tie when there is one"

### Weaknesses

### W1: Significance rests on the composition results, which the paper itself presents as non-practical
**Problem**: My configured focus question was whether the label-noise and guidance results add enough on their own. They largely do not. Label noise is explicitly not new. The guidance results add, relative to Liu et al. (2026), a null-set statement and extensions to bounded-variation schedules and prior averages. These gains are honest but modest technical extensions of a known template (finite kinetic energy, then Liouville volume expansion). The original content is the composition block: Theorem 5.8, Proposition 5.9, Theorem 5.10, Corollary 5.11 and Proposition 5.13. The abstract, practice paragraph and conclusion all frame that block as a "boundary marker". Standard trained velocity networks do not reproduce it (§7), and the threshold is set at the scale $(1-t)^2$ around a tie. For a general ML-theory readership, the paper therefore offers a clean existence-and-criterion result about exact fields with limited reach into trained samplers.
**Evidence Anchor**: text: Abstract "We therefore present the composition as a boundary marker, not a practical mechanism."
**Why it matters**: As written, the six-item contribution list gives roughly equal weight to the label-noise reference, the two-field results and the learned-field proposition. A reader cannot tell quickly that the composition block is the paper's main new content, nor why an exact-field-only result matters.
**Suggestion**: Restructure the introduction around the composition and sign-rule results as the main contribution, with the two-field results as the necessary contrast class. Compress the label-noise reference into the setup. In the main text, add a short argument for why an exact-optimum phenomenon matters even when trained networks miss it, for example as an audit or upper-bound statement, or as a statement about what closer fits converge to.
**Severity**: Major
**Confidence**: 4 — core expertise: positioning of diffusion/flow theory results

### W2: The authors' own verification of three proofs, including a headline proposition, is declared incomplete
**Problem**: The printed "Use of large language models" section says that the statements and proofs of Corollary 5.7, Proposition 5.13 and Remark 5.12 were first drafted with a large language model. It also says that they have been checked by model-based audits and numerical tests, but that the authors' own line-by-line check is not complete. Proposition 5.13 is contribution item 4, the sign rule, and appears in the abstract and conclusion. Corollary 5.7 underwrites the abstract's claim about every fixed combination of two fields.
**Evidence Anchor**: text: Use of large language models "the authors' own line-by-line check of these three proofs is not yet complete"
**Why it matters**: An editor cannot send out, or accept, a theory paper whose authors state that they have not yet verified the proofs of headline results. This is a readiness issue independent of whether the proofs are correct, which I did not assess. The disclosure itself is appropriate and to the authors' credit.
**Suggestion**: Complete the authors' check of all three proofs before submission and update the statement to say so. If any part cannot be confirmed, downgrade it explicitly, for example to a conjecture supported by numerics, and adjust the abstract and Table 1 to match.
**Severity**: Major
**Confidence**: 5 — the finding reports the manuscript's own statement; no proof checking was involved

### W3: The label-noise reference is validated only in $d=2$ and fails, unexplained, at image scale
**Problem**: Contribution items 1 and 6 present the label-noise variance $\tr\Covh$ as a parameter-free reference for trained networks. It matches on a two-dimensional linear-Gaussian problem. On CIFAR-10, however, the across-condition slope is far from the exact-field value of 1, and the authors do not identify why. The label-noise block therefore adds neither new theory nor a working empirical reference at scale.
**Evidence Anchor**: table: Table tab:cifar-kernel, row $h=4$ — three-draw slope mean $0.36$ with $95\%$ interval $[0.22,0.51]$ against the exact-field value $1$
**Why it matters**: The block occupies main-text space and two appendix tables. It dilutes the takeaway (W1) without strengthening the central claim.
**Suggestion**: Either diagnose the CIFAR-10 departure (for example, an analysis of finite cutoff, network capacity or effective number of atoms), or demote the image-scale comparison to a clearly scoped negative observation and shorten it.
**Severity**: Minor
**Confidence**: 4 — reading of reported numbers; adjacent to the methodology seat's remit

### W4: The gain over Liu et al. (2026) is stated precisely only in the appendix
**Problem**: The main text states the delta over Liu et al. (2026) in one clause of contribution item 2 and in a Related Work paragraph. The full comparison, including what a time-varying weight already gives through their perturbation results and that a guidance interval is covered by their Thm 2.5, appears only in Appendix B.1. A reader judging the size of the guidance contribution must go to the appendix.
**Evidence Anchor**: text: §1 Contributions item 2 "we add that the initial points ending off the atoms form a null set"
**Why it matters**: The guidance results are the contribution whose standalone weight is most open to question. The paragraph that makes their delta precise is therefore editorially important.
**Suggestion**: Move a condensed version of Table tab:comparison, or its last row and the "Combination" row, into Section 2. Also state in the main text which schedule classes were already covered by Liu et al. (2026).
**Severity**: Minor
**Confidence**: 4 — direct comparison of main text with Appendix B.1

### W5: Section 7 is dense and mixes results with protocol-level detail
**Problem**: Several §7 paragraphs run 20 to 35 lines and carry dozens of numbers, solver settings and seed-level exceptions. Examples are "The spectral criterion beyond the line", "Learned guided label averaging" and "The label-noise reference in trained networks". The reader has to extract the claim each paragraph supports.
**Evidence Anchor**: text: §7 "These fractions count the centre only, and on the triangle the centre is not the only blend"
**Why it matters**: This is the main reason the manuscript is costly to read (D5 warn). The theory sections are comparatively well signposted.
**Suggestion**: Open each §7 paragraph with a one-sentence claim and the theorem it checks. Move seed-level exceptions, tolerance comparisons and secondary configurations to Appendix E. Consider a single summary table of "theorem, check, outcome".
**Severity**: Minor
**Confidence**: 4 — editorial judgement of readability

### W6: The numbers that §7 discusses live in appendix tables
**Problem**: §7 discusses at length the composition probabilities, the spectral-criterion fractions and the learned-composition occupancies. The tables holding them (tab:composition, tab:spectral and tab:learned-composition) and the diagnostic figure for the stress test (fig:intervention-validation) are all in Appendix E. In the main text, §7 is supported only by the figures fig:unrolled, fig:composition, fig:signed and fig:learned-composition.
**Evidence Anchor**: absence: §7 main text — expected the tables carrying the composition, spectral-criterion and learned-composition numbers that §7 discusses; checked §7 body, all table and figure floats of §§1–8, Appendix E
**Why it matters**: With no page limit confirmed, keeping these tables in the appendix only adds cross-referencing cost.
**Suggestion**: Bring the spectral table (tab:spectral) and a reduced learned-composition table (for example, $B=1,2$ and the triangle at $2$ and $5\,w_c$) into §7.
**Severity**: Minor
**Confidence**: 3 — float placement judged from source, not from a compiled PDF

### W7: Panel references do not match the figure's panel labels
**Problem**: §7 cites the intervention-validation figure by "left" and "middle". The figure's caption labels its panels (a), (b) and (c).
**Evidence Anchor**: figure: Figure fig:intervention-validation (Appendix E), caption panels (a)–(c) against the "left" and "middle" citations in §7 "Exact fields"
**Why it matters**: This is a small navigation cost, but it signals that the text was not updated after the figure was relabelled.
**Suggestion**: Cite the panels as (a) and (b).
**Severity**: Minor
**Confidence**: 5 — direct reading

### W8: "All proofs are in the appendices" is not quite true
**Problem**: The Organisation paragraph says that all proofs are in the appendices. However, Remark 5.12 (rem:generic) carries its full transversality proof in the spectral subsection of §5, and the roadmap table records that location. Corollary 5.5 (negative guidance) is proved within its statement.
**Evidence Anchor**: text: §1 Organisation "All proofs are in the appendices."
**Why it matters**: This is minor, but Remark 5.12 is one of the three statements whose verification is pending (W2). Its proof should be easy to locate.
**Suggestion**: Either move the argument of Remark 5.12 to Appendix B with a pointer, or amend the sentence.
**Severity**: Minor
**Confidence**: 5 — direct reading

### W9: The abstract is long and technical for a field-general readership
**Problem**: The abstract runs to roughly 330 words. It defines a "tie" and an "intermediate field" inline, gives the threshold, the eigenvalue criterion and the $(1-t)^2$ layer, and adds a learned-network result, so a reader has to parse several technical clauses.
**Evidence Anchor**: text: Abstract "a blend requires subtracting an intermediate field: one whose prior log-odds between the two examples lie strictly between the smallest"
**Why it matters**: The abstract is the first thing a general reader sees, and as written the main message, "two fields reweight, three can blend", is hard to pick out.
**Suggestion**: Cut to about 200 words. Keep the question, the two-versus-three dichotomy, the explicit threshold, and the boundary-marker framing. Move the tie definition and the sign rule to the introduction.
**Severity**: Minor
**Confidence**: 4 — editorial judgement

### W10: The learned-field contribution is narrow
**Problem**: Contribution item 5 ("what a learned field needs to inherit the blend") rests on two things. The first is Prop 6.1, whose part (a) is a general Grönwall consequence and whose part (b) is one-dimensional. The second is a set of experiments in $d\le2$ in which the successful network receives a coordinate centred at a tie whose location is known in advance. Centred elsewhere, the network leaves the midpoint empty, and even the tie-centred network leaves the other ties (the edge midpoints) empty.
**Evidence Anchor**: text: §7 "centred at the known tie"
**Why it matters**: Listing this as a contribution overstates what a reader learns about trained samplers. It works better as a diagnostic showing that the exact basin is resolvable in principle.
**Suggestion**: Reframe item 5 as a diagnostic in the introduction, and state in the contribution list that the oracle tie location is required.
**Severity**: Minor
**Confidence**: 4 — reading of §6, §7 and Appendix E.2

### Detailed Comments

#### Journal Fit
The topic is squarely within ML theory of diffusion and flow models: the memorisation of exact empirical optima, guidance, and compositional generation. A general ML-theory readership would find the composition dichotomy interesting. The length (main text plus roughly 30 pages of appendix) suits a journal-style venue without a page limit. I make no claim about fit to any named venue.

#### Originality
The composition block is original as far as I can tell, and the authors' own claim that it is unanalysed for the exact empirical field matches my quick search. The guidance results are incremental over Liu et al. (2026), mainly through the null-set statement and the bounded-variation schedules. The label-noise result is a declared corollary of Wan et al. (2025). The originality is therefore real but concentrated in one block (W1, W4).

#### Significance
The paper makes a clean conceptual point with a sharp threshold, but its practical significance is limited by the paper's own findings: the blend lives at the scale $(1-t)^2$, and standard networks do not resolve it. The audit-oriented reading in "What this means in practice" is the best case for significance and deserves more prominence.

#### Structural Coherence
Title, abstract, introduction and conclusion are consistent. I found no over-promising: claims about trained networks are hedged throughout. The main costs are the dense numerical section and the appendix placement of key tables (W5, W6). I found no text addressed to reviewers and no instruction-like content in the manuscript.

#### Title & Abstract
The title is accurate and phrased as the paper's question. The abstract is accurate but overlong (W9).

#### Conclusion
The conclusion answers the stated question and lists its open problems honestly.

### Questions for Authors
1. Will the authors' own check of Corollary 5.7, Proposition 5.13 and Remark 5.12 be complete before submission, and will the disclosure be updated accordingly?
2. Which result do you regard as the paper's main contribution, and why does it matter for practitioners or auditors given that trained velocity networks miss the blend basin?
3. Can the CIFAR-10 departure from the label-noise reference be attributed to any identifiable cause (finite cutoff, capacity, effective number of atoms)?
4. Beyond the oracle tie-centred input, is there any architecture-agnostic condition under which a learned field would inherit the composition threshold?

### Minor Issues
- §5.6 "What leaves the support" is a three-sentence subsection. Consider merging it into the end of §5.5 or into the Table 1 discussion.
- In §7, the paragraph "Learned label averages" and Table tab:learned-averages report a biased energy statistic with no null or threshold. Say in one clause what conclusion the reader should draw.
