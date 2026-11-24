# Editorial Decision Package

## Calibration Resolution

`calibration_status: NOT_CALIBRATED`

The current runtime has no closed profile artifact and no replay validator, so this package stays uncalibrated. No candidate profile or profile named in prose upgrades it.

## Mechanical Synthesis (sprint contract `reviewer/reviewer_full/v2`)

Role-scoped scoring matrix (assessed eligible seats only):

| Dimension | Priority | Eligible seats | Assessed scores | Worst |
|---|---|---|---|---|
| D1 methodology_rigor | mandatory | methodology | methodology=warn | warn |
| D2 domain_accuracy | mandatory | domain | domain=warn | warn |
| D3 argumentative_coherence | mandatory | da, methodology | da=block (repairable), methodology=warn | block |
| D4 cross_disciplinary_relevance | high | perspective | perspective=warn | warn |
| D5 writing_and_structure | normal | eic | eic=warn | warn |
| D6 venue_fit_and_contribution | mandatory | eic | eic=warn | warn |

Failure conditions:

- F1 (any mandatory dimension has a fatal block): not fired. No seat declared a fatal block.
- F2 (any mandatory dimension scores 'block', quantifier any): fired. D3 has da=block.
- F3 (two or more mandatory dimensions score 'warn' or worse, quantifier majority): fired. D1, D2 and D6 each have n=1 at warn or worse; D3 has n=2 with both seats at warn or worse.
- F4 (any high-priority dimension scores 'block'): not fired. D4 is at warn.
- F5 (any dimension scores 'warn' or worse): fired.
- F0 (every dimension scores 'pass'): not fired.

Precedence: F2 (severity 90) is the highest-severity fired condition, and its action is major_revision.

dimension_verdicts: [D1=warn, D2=warn, D3=block, D4=warn, D5=warn, D6=warn]
fired_conditions: [F2, F3, F5]
da_critical_adjudications: []
editorial_decision=major_revision

The Devil's Advocate CRITICAL table is empty, so no DA-CRITICAL adjudication is required.

## Part 1: Editorial Decision Letter

Dear Authors,

Thank you for submitting "Which Interventions Keep a Conditional Flow on Its Training Set?". Five role-separated review seats assessed it: a Journal-Fit Reviewer, a methodology reviewer (proofs and numerics), a domain reviewer, a privacy and auditing reviewer, and a Devil's Advocate. All five are model personas run in separate invocation contexts of one model family. The execution provenance section below reports this; persona separation is not a claim of independent errors. No target venue was confirmed (`criteria_binding_unavailable`), so this letter makes no claim about fit to any named venue.

### Decision: Major Revision

### Consensus Analysis

#### Points of Agreement (Consensus)

- **[5 of 5 seats] The h > 0 mathematics is sound and well positioned; the composition block is the new content.** EIC S3, R1 S1–S6, R2 S1–S2, R3 (takes the theorems as stated) and DA ("Checks that held") agree. R1 worked through the two-step template, the bounded-variation integration by parts, Theorem composition at w = w_c, and the Lyapunov–Perron argument of Theorem spectral, and found no false statement and no unrepairable gap. Every seat that looked found the prior-work accounting unusually candid (EIC S1–S2, R2 S1, S4).
- **[4 seats: EIC, R2, R3, DA] The practical message about composition is inconsistent, and the practice claims go beyond the trained-model evidence.** The abstract calls composition "a boundary marker, not a practical mechanism", while the conclusion tells auditors that composition is "the operation an audit should examine" (EIC W1, R2 W1, R3 W1, DA M2). The paper's own trained networks argue against transfer: the CIFAR-10 label-noise slope is 0.36 against 1, 17–28% of samples are off the training images, standard CFM networks never reach the blend, and reproducing it needs an input centred at a tie known in advance (R2 W2–W3, R3 W1/W3, EIC W3/W10, DA M2).
- **[4 seats: EIC, R1, R2, DA] The printed LLM-use statement says the authors have not finished their own check of three proofs that support listed contributions** (Corollary twofields, Proposition twoatom, Remark generic). EIC rates this Major as a readiness issue. R1, R2 and DA rate it Minor. R1 independently verified all three proofs as correct, and DA checked two of them step by step.
- **[2 seats: R2, R3] Calling blends "leakage" lacks a criterion, and the paper's own memorisation test classifies an exact two-image midpoint as not memorised** (the Yoon et al. ratio test of Appendix E) (R2 W6 Minor, R3 W2 Major).
- **[2 seats: R2, R3] The privacy, extraction and composition-theory literature is under-cited.** Carlini et al. (2023) is in refs.bib but never cited, even though the abstract's opening sentence relies on it (R2 W4–W5, R3 W4).

#### Points of Disagreement

- **The §5.6 remark and Table 1 row on averaging hard-label fields.** R2 (Minor Issues) reads the Table 1 row as true only in symmetric configurations, which matches the remark in §5.6. DA M1 argues that the remark itself is wrong. By Proposition collapse(a), the hard-label field at y^i is (x^i − x)/(1 − t), so a fixed average λ v_1 + (1 − λ) v_2 equals (z − x)/(1 − t) with z = λ x^1 + (1 − λ) x^2. Every source therefore ends at z in every geometry, and z is a circumcentre only when the weights are equal.
  - **Editor's resolution: DA's reading stands.** The calculation follows in one line from a stated proposition. It means the headline counting rule ("two fields reweight, three can blend") holds only for strictly positive priors (h > 0). The abstract, introduction and conclusion state it without that qualifier, and the §5.6 remark must be corrected.
- **The positive control for the stress test.** EIC S6 and R2 S3 count the positive control as a strength. R1 W1 reports that it passes because of a floating-point effect: the captured endpoints sit at the double-precision resolution floor of the logits (about 2e-17). When R1 rewrote the field in the algebraically identical s-coordinate and ran the same RK4 with the same steps and gaps, the midpoint fraction dropped to 0 at every w/w_c. The fixed-step scheme runs about 25 times past RK4's stability bound in the last steps, and Appendix E.2 concedes this elsewhere.
  - **Editor's resolution: R1's finding stands.** EIC and R2 took the paragraph's claim as written, while R1 transcribed the script and reproduced the reported fractions before showing that they depend on rounding. As an orchestration check, which adds no reviewer finding, the dispatching session reran `scripts/stress_positive_control.py`'s oracle and RK4 (4,096 sources, 256 steps per segment, B = 1). The original coding gives midpoint fractions of 0.049, 0.410 and 0.988 at w/w_c = 1.1, 2 and 10, with captured |x_1| ≤ 3e-21. The algebraically identical s-coordinate coding, with the same scheme, gives 0 at every strength and every gap. The theorems are unaffected; what is at stake is the empirical claim in contribution 6 and in Limitations.
- **How much the composition result matters at the exact optimum.** EIC W1 treats composition as an existence result with limited reach into trained samplers. R2 (W1, Q1) and DA (strongest counter-argument) argue the opposite way: practical guidance strengths satisfy w ≫ w_c ≈ 4e^{-2B}, and at h = 0 averaging blends generically. At the exact optimum, then, blending is not marginal, and the only open question is whether trained samplers approximate the exact field near ties.
  - **Editor's resolution: not an arbitration but a framing obligation.** The seats agree on the facts and differ on which reading the paper should adopt. The paper currently asserts both readings. It must choose one and state the other as the open question (R2 in roadmap item R2).

### Decision Rationale

The decision is mechanical. The Devil's Advocate scored D3 (argumentative coherence) a repairable block, because informal claims strictly exceed their formal counterparts, and that fires F2 (Major Revision). F3 fires independently, since four mandatory dimensions sit at warn or worse. No seat declared a fatal block, and the DA raised no CRITICAL issue.

The reports explain why the revision is substantial although the mathematics holds. Every seat that examined the proofs found them correct, and the closest-prior-work accounting is exemplary. The problems lie between the theorems and what the paper tells readers to do:

- The counting rule, "the number and signs of combined fields decide", is stated without the positivity qualifier that its proofs need. A one-line consequence of Proposition collapse contradicts the unqualified version, and a remark in §5.6 understates this.
- The practical paragraph, the conclusion and the broader-impact statement give advice to auditors and practitioners that the paper's own trained networks do not support. The paper also gives two incompatible readings of composition: a boundary marker, and the operation audits should examine.
- Blends are called leakage under a criterion the paper never states and its own measurement tool contradicts.
- The positive control, offered as evidence that the numerical stress test can see an attracting tie, may pass only through floating-point resolution loss.
- The printed statement that the authors have not finished checking three proofs is a readiness issue for any venue, whether or not the proofs are correct (R1 found them correct).

Almost all of this can be repaired by rewriting and rescoping. The two exceptions are a rerun of the positive control and, optionally, small analyses on networks the authors already have: nearest-midpoint counts among off-atom CIFAR samples, and replication against training length. No new theorem is required.

### Blocking Issues (0–3, immutable source order)

| Transport ref | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---------------|----------------|--------------------|-----------------|------------------------|
| R1 | The headline counting rule and the audit separation hold only for strictly positive priors (h > 0). The §5.6 remark and the Table 1 row misstate the h = 0 case. | DA | text: Section 5.6 "Averaging hard-label fields can also move every endpoint, but only in configurations such as the" | REV-1 |
| R2 | Composition is framed both as a boundary marker and as the operation an audit should examine, and the practice claims extrapolate past the trained-model evidence. | EIC, R2, R3, DA | text: Conclusion "the composition of conditions is the operation an audit should examine" | REV-2 |
| R3 | The stress-test positive control appears to pass through floating-point resolution loss, not because the scheme resolves an attracting tie. | R1 | text: Section 6, paragraph "A positive control for the stress test" "The stress test therefore sees an attracting tie when there is one" | REV-3 |

---

## Part 2: Revision Roadmap

The `Sub-Claim(s)` column uses the working sub-claim ids below. The machine-readable `revision-roadmap/1.0` JSON core and its block manifest were not generated in this run, so this table is the roadmap of record.

### Required Revisions (Must Fix)

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|---|---|---|---|---|---|---|---|---|
| R1 | Add the strict-positivity (h > 0) qualifier to the thesis sentences of the abstract, introduction and conclusion, and to the practice and broader-impact statements. Correct the §5.6 remark and the Table 1 row: the endpoint of a fixed average of hard-label fields is the weighted average of the atoms in every geometry, and a circumcentre only for equal weights. State what the conjunction does at h = 0. | SC-1 | major | text: Section 5.6 "Averaging hard-label fields can also move every endpoint, but only in configurations such as the" | 4 — direct calculation from Proposition collapse(a) | DA | must_fix | section: Abstract, §1, §5.6, Table 1, §9 | blocks_acceptance: D3 |
| R2 | Choose one framing of composition (an exact-optimum risk that trained samplers have not been shown to realise, or a boundary of the two-field theorem class), and make the abstract, contribution list, practice paragraph (i)–(iii), conclusion and broader-impact statement consistent with it. Address the point that w ≫ w_c at practical guidance strengths. Scope every auditor or practitioner statement explicitly to the exact optimum, and place the trained-model departures (CIFAR slope 0.36, off-atom fractions, missing blend basin) next to those statements, not only in Limitations. Replace "boundary marker" with a defined phrase. | SC-2, SC-3 | major | text: Conclusion "the composition of conditions is the operation an audit should examine" | 4 — four seats, argument analysis of the paper's own evidence | EIC, R2, R3, DA | must_fix | section: Abstract, §1 practice paragraph, §9, Broader impact | blocks_acceptance: D3 |
| R3 | Rerun the positive control with the stiff integrator and proof-derived stopping rules, or the same RK4 with the field coded in the s-coordinate. Alternatively, report the mechanism of capture (completed before the step size becomes unstable, then floating-point symmetrisation) and the stiffness range in which the conclusion holds. Reconcile the paragraph and Limitations with Appendix E.2's statement that fixed-step RK4 ejects trajectories held by an attracting tie. | SC-4 | major | text: Section 6, paragraph "A positive control for the stress test" "The stress test therefore sees an attracting tie when there is one" | 4 — reproduced numerically by R1 with the authors' oracle and RK4 transcribed | R1 | must_fix | re_analysis: stress_positive_control.py, §6, §8 Limitations | blocks_acceptance: D1 |
| R4 | Complete the authors' own line-by-line check of Corollary twofields, Proposition twoatom and Remark generic, and update the LLM-use statement. Until then, put the caveat next to the three results. If any part cannot be confirmed, downgrade it explicitly. | SC-5 | major | text: Use of large language models "the authors' own line-by-line check of these three proofs is not yet complete" | 5 — reports the manuscript's own statement; R1 independently found the three proofs correct | EIC, R1, R2 | must_fix | sentence: Use of large language models | blocks_acceptance: D6 |
| R5 | State an operational leakage criterion that covers blends, for example reconstruction of a record from a blend given side information on the other k − 1 records (2z − x^i for k = 2), or weaken the wording. Note that the Yoon et al. ratio test used in Appendix E classifies an exact two-image midpoint as not memorised. Report how many of the off-atom CIFAR-10 samples (0.168, 0.276) lie near a pairwise training midpoint. | SC-6 | major | text: §1 What this means in practice "which an audit should count as leakage rather than as new samples" | 4 — core expertise: extraction and replication definitions | R3, R2 | must_fix | section: §1 practice paragraph (i), Appendix E CIFAR protocol | blocks_acceptance: D4 |
| R6 | Give the predictability claim a knowledge model: who holds the training labels, h and query access, and what the ranking adds over a membership-inference or extraction attack with the same knowledge. Restrict the claim to the exact optimum and place the CIFAR non-tracking result next to it. | SC-7 | major | text: §1 What this means in practice "so an auditor can rank, for any label, the records an exact-optimum model returns" | 4 — core expertise: threat modelling | R3 | must_fix | section: §1 practice paragraph (ii), Broader impact | blocks_acceptance: D4 |
| R7 | Retitle and reframe contribution 5 to what is shown: in d ≤ 2 runs, a rescaled input centred at a tie known in advance is sufficient to reproduce that one basin, standard parametrisations miss it, and every learned network leaves the edge-midpoint blends empty. Optionally, add one learned conjunction experiment at moderate dimension (for example class-conditional CIFAR-10 pairs at w ≫ w_c). | SC-8 | major | table: Table "learned-composition" (Appendix E), rows "velocity CFM" (0.000 at every w, B=1) versus "data, rescaled input" and the exact row (0.406 at 2w_c) | 4 — core expertise: learned versus exact fields | R2, EIC | must_fix | section: §1 contribution 5, §6, §7 | blocks_acceptance: D2 |

### Suggested Revisions (Should Fix)

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|---|---|---|---|---|---|---|---|---|
| S1 | Restructure the introduction around the composition and sign-rule results as the main contribution, with the two-field results as their contrast class. Compress the label-noise reference into the setup. | SC-9 | major | text: Abstract "We therefore present the composition as a boundary marker, not a practical mechanism." | 4 — positioning judgement | EIC | should_fix | section: §1 | improves_dimension: D6 |
| S2 | Cite the composition-theory work (Bradley et al. 2025; Skreta et al. 2025), guidance theory (Wu et al. 2024; Pavasovic et al. 2025), guidance-based mitigation (Chen et al. 2024), Vastola 2025, Liu et al. 2025 (oracle velocity), and Carlini et al. 2023 for the opening claim. Add a short "Relation to privacy and extraction" paragraph citing the uncited refs.bib entries (Somepalli et al. 2023 "Diffusion Art or Digital Forgery?", Sesmat et al. 2026) and membership-inference work. | SC-10 | minor | absence: §2 Related work, "Composition" paragraph — expected the theory of linear score composition (Bradley et al. 2025; Skreta et al. 2025); checked §2, §4.5 "Composing conditions", §7 Limitations, refs.bib | 4 — verified existence (see Suggested-Reference Check) | R2, R3 | should_fix | section: §2 | improves_dimension: D2 |
| S3 | Use one symbol for the threshold: define w_c^spec once, or define w_c locally in every caption (Figure 2, §4.5, §6, Tables 6 and 8 use a value other than 1/sinh^2 B). | SC-11 | minor | table: Table 9 (notation), row "w, w_c=1/sinh^2 B; threshold of Theorem composition" against the triangle and simplex rows of Table 6 and the caption of Figure 2 | 5 — direct reading and recomputation | R1 | should_fix | sentence: notation table and captions | improves_dimension: D3 |
| S4 | Add the hyperbolicity (generic) and face-condition qualifiers to the abstract's statement of the spectral criterion. | SC-12 | minor | text: Abstract "in any dimension the eigenvalue signs of a signed posterior covariance decide it" | 4 — comparison with Theorem spectral | R1 | should_fix | sentence: Abstract | improves_dimension: D3 |
| S5 | State Proposition regular(b) for states at t_0, or add a linear-growth assumption on [0, t_0]. | SC-13 | minor | text: Proposition regular(b) "is the limit of at most one initial point" | 4 — statement against proof | R1 | should_fix | sentence: Proposition regular | improves_dimension: D1 |
| S6 | Either diagnose the CIFAR-10 departure from the label-noise reference (cutoff, capacity, effective number of atoms) or present it as a clearly scoped negative observation. Optionally, report the slope and off-atom fraction against training length, which would test "need not survive a closer fit". | SC-14 | minor | table: Table tab:cifar-kernel, row $h=4$ — three-draw slope mean $0.36$ with $95\%$ interval $[0.22,0.51]$ against the exact-field value $1$ | 4 — reading of reported numbers | EIC, R2, R3 | should_fix | section: §6, Appendix E | improves_dimension: D2 |
| S7 | Label "it need not survive a closer fit" as a hypothesis suggested by the exact field, or test it on the existing checkpoints. | SC-15 | minor | text: §1 What this means in practice "only from the error of the learned field, and it need not survive a closer fit" | 3 — inference judgement | R3 | should_fix | sentence: §1 practice paragraph (i) | improves_dimension: D4 |
| S8 | Add that repeated sampling averages endpoint noise away (error of order ρ/√M), and that DP guarantees for these models come from private training (Dockhorn et al. 2023), not from output noise. | SC-16 | minor | text: Broader impact statement "a formal guarantee requires randomisation calibrated in the sense of differential privacy, which we do not analyse" | 4 — core expertise | R3 | should_fix | sentence: Broader impact, §1 (i) | improves_dimension: D4 |
| S9 | Discuss the dual-use reading: guidance concentrates the exact endpoint law on fewer records (a plausible extraction amplifier), and the composition thresholds indicate which prompt pairs blend. | SC-17 | minor | text: Broader impact statement "which helps auditors and, equally, an adversary who knows the labels" | 4 — core expertise | R3 | consider | sentence: Broader impact | improves_dimension: D4 |
| S10 | Move the precise delta over Liu et al. (2026), a condensed comparison table, into §2. | SC-18 | minor | text: §1 Contributions item 2 "we add that the initial points ending off the atoms form a null set" | 4 — main text against Appendix B.1 | EIC | should_fix | section: §2 | improves_dimension: D6 |
| S11 | Shorten the §6 paragraphs: lead each with its claim and the theorem it checks, move seed-level detail to Appendix E, and bring the spectral table and a reduced learned-composition table into the main text. In the main text, give the random-pair CIFAR composition mean (0.042 at 2 w_c) next to the selected-pair maximum (0.29). | SC-19 | minor | text: §7 "These fractions count the centre only, and on the triangle the centre is not the only blend" | 4 — editorial judgement; DA prose on selected versus random pairs | EIC, DA | should_fix | section: §6 | improves_dimension: D5 |
| S12 | Shorten the abstract to about 200 words, keeping the question, the two-versus-three dichotomy (with its qualifier), the threshold and the framing. | SC-20 | minor | text: Abstract "a blend requires subtracting an intermediate field: one whose prior log-odds between the two examples lie strictly between the smallest" | 4 — editorial judgement | EIC | consider | section: Abstract | improves_dimension: D5 |
| S13 | Small fixes: cite intervention-validation figure panels as (a) and (b); amend "All proofs are in the appendices" (Remark generic is proved in §5); merge the three-sentence §5.6; say what the "Learned label averages" energy statistic is meant to show; present field averaging in the abstract as one modelling choice (the bottleneck proposition gives prior averaging). | SC-21 | minor | text: §1 Organisation "All proofs are in the appendices." | 5 — direct reading | EIC, DA | consider | sentence: §1, §5.6, §6, Abstract | improves_dimension: D5 |

### Source-Traceability Checklist

Items are in source order, which is not a suggested work order.

- [ ] R1, obligation `must_fix`: positivity qualifier; correct §5.6 and the Table 1 hard-label row; state h = 0 behaviour of the conjunction.
- [ ] R2, obligation `must_fix`: one framing of composition; scope practice, conclusion and broader-impact statements to the exact optimum.
- [ ] R3, obligation `must_fix`: rerun or re-explain the positive control.
- [ ] R4, obligation `must_fix`: finish the authors' check of three proofs; update the LLM-use statement.
- [ ] R5, obligation `must_fix`: leakage criterion for blends; midpoint count in the CIFAR off-atom samples.
- [ ] R6, obligation `must_fix`: knowledge model for the predictability claim.
- [ ] R7, obligation `must_fix`: reframe contribution 5; optional moderate-dimension learned conjunction.
- [ ] S1, obligation `should_fix`: restructure the introduction around composition.
- [ ] S2, obligation `should_fix`: literature additions.
- [ ] S3, obligation `should_fix`: w_c notation.
- [ ] S4, obligation `should_fix`: spectral qualifiers in the abstract.
- [ ] S5, obligation `should_fix`: Proposition regular(b).
- [ ] S6, obligation `should_fix`: CIFAR departure.
- [ ] S7, obligation `should_fix`: "closer fit" as hypothesis or test.
- [ ] S8, obligation `should_fix`: endpoint noise and DP.
- [ ] S9, obligation `consider`: dual use.
- [ ] S10, obligation `should_fix`: delta over Liu et al. in the main text.
- [ ] S11, obligation `should_fix`: §6 density; random-pair figure.
- [ ] S12, obligation `consider`: shorter abstract.
- [ ] S13, obligation `consider`: small fixes.

### Response Letter Template

Respond to every item above, R1 to R7 and S1 to S13, in the Reviewer comment, Author response, Change made (with location) format of `templates/revision_response_template.md`.

---

## Part 3: Reviewer Report Summary (Appendix)

### Journal-Fit Review Report Summary
- Recommendation: Major Revision | Confidence: 4
- Key point: the composition block carries the paper's originality but is framed as non-practical, and the authors' own proof check is declared incomplete. The prior-work accounting and navigation aids are strong.

### Reviewer 1 (Methodology) Summary
- Recommendation: from D1 and D3 at warn, minor-to-major | Confidence: 4
- Key point: every proof checked, including the three flagged ones, is correct, and the passages to the limit t → 1 hold. The stress-test positive control appears to pass through floating-point resolution loss (Major).

### Reviewer 2 (Domain) Summary
- Recommendation: Major Revision | Confidence: 4
- Key point: the composition threshold and sign rule are new and fairly positioned. The practical framing overreaches the learned evidence, the learned-composition result relies on a tie-centred oracle input, and composition-theory and guidance literature are missing.

### Reviewer 3 (Perspective) Summary
- Recommendation: Major Revision | Confidence: 4
- Key point: the advice to auditors points away from where the paper's own trained models produce off-atom outputs. "Leakage" and "predictability" need a criterion and a threat model.

### Devil's Advocate Summary
- Recommendation: N/A, findings only
- Key challenge: no Critical challenge. The strongest counter-argument is that the counting rule is a property of strictly positive priors, not of field counting, since at h = 0 two averaged hard-label fields blend in every geometry. On the "so what?" test, the h > 0 negative results are worth publishing; the unqualified rule and the audit separation are not, as written.

## Execution Provenance and Panel Notes

- Five seats, each run as a two-call sprint (a paper-content-blind Phase 1, then a paper-visible Phase 2) in separate subagent contexts. Peer outputs were withheld until each seat committed. All seats ran on the same model family and provider, so correlated errors cannot be ruled out. Persona separation is not evidence of independent error processes.
- The first Devil's Advocate attempt failed the Phase 2 conformance gate (`[DA-TABLE-PARSE]`: a criterion table outside the two issue tables carried typed anchors). Per protocol it was marked unusable and not retried. A fresh DA seat, with a new context, a new Phase 1 and a new Phase 2, replaced it. The failed attempt is kept in `failed_attempts/` and was not shown to any seat or used in this synthesis.
- The methodology seat and the replacement DA seat were interrupted by a usage limit during Phase 2 and resumed in the same context after the reset. Neither had seen another seat's output.
- All five Phase 1 plans and Phase 2 reports passed `check_phase_conformance.py`. The methodology seat filed a `no_recomputable_statistics` attestation. Its body recomputes the CIFAR-10 t-interval ([0.218, 0.509] against the reported [0.22, 0.51]), which is not a bounded-procedure statistic.
- No text in the manuscript was aimed at reviewers (all seats).

## Attachment: Suggested-Reference Check (advisory, #1001)

Suggested-reference check (script output, not a reviewer finding; #1001)
Seats read: R2, R3 (complete).

| Seat | # | Reference | Result |
|---|---|---|---|
| R2 | 1 | Bradley, A. et al. (2025) "Mechanisms of Projective Composition of Diffusion Models" arXiv:2502.04549 | Found in an index |
| R2 | 2 | Skreta, M. et al. (2025) "The Superposition of Diffusion Models Using the Itô Density Estimator" arXiv:2412.17762 | Found in an index |
| R2 | 3 | Wu, Y. et al. (2024) "Theoretical Insights for Diffusion Guidance: A Case Study for Gaussian Mixture Models" arXiv:2403.01639 | Found in an index |
| R2 | 4 | Pavasovic, K. L. et al. (2025) "Understanding Classifier-Free Guidance: High-Dimensional Theory and Non-Linear Generalizations" arXiv:2502.07849 | DOI or arXiv ID not found, and no title match |
| R2 | 5 | Chen, C. et al. (2024) "Towards Memorization-Free Diffusion Models" arXiv:2404.00922 | Found in an index |
| R2 | 6 | Vastola, J. J. (2025) "Generalization through variance: how noise shapes inductive biases in diffusion models" arXiv:2504.12532 | Found in an index |
| R2 | 7 | Liu, H. et al. (2025) "From Navigation to Refinement: Revealing the Two-Stage Nature of Flow-based Diffusion Models through Oracle Velocity" arXiv:2512.02826 | Found in an index |
| R2 | 8 | Carlini, N. et al. (2023) "Extracting Training Data from Diffusion Models" arXiv:2301.13188 | Found in an index |
| R3 | 1 | Carlini, N. et al. (2023) "Extracting Training Data from Diffusion Models" arXiv:2301.13188 | Found in an index |
| R3 | 2 | Somepalli, G. et al. (2023) "Diffusion Art or Digital Forgery? Investigating Data Replication in Diffusion Models" arXiv:2212.03860 | Found in an index |
| R3 | 3 | Duan, J. et al. (2023) "Are Diffusion Models Vulnerable to Membership Inference Attacks?" arXiv:2302.01316 | Found in an index |
| R3 | 4 | Matsumoto, T. et al. (2023) "Membership Inference Attacks against Diffusion Models" arXiv:2302.03262 | Found in an index |
| R3 | 5 | Sesmat, T. et al. (2026) "Where Flow Matching Leaks: Characterising Membership Signals Along the Interpolation Path" arXiv:2606.07271 | Found in an index |
| R3 | 6 | Dockhorn, T. et al. (2023) "Differentially Private Diffusion Models" arXiv:2210.09929 | Found in an index |

"Found" means an index holds a record with this DOI or arXiv ID and title, or with this title. It does not show that the work supports the recommendation, or that the authors and year are right.

## Attachment: Reviewer Claim Check (advisory, #1002)

The judge answered 31 of 31 findings from 5 reviewers: it marked 3 as contradicted, and 0 cannot be checked from the manuscript alone.

The judge marked these findings as contradicted by the manuscript. The script checked only the words of each quote: that they occur in the manuscript, or, for words the finding quotes, that they do not. The judge gave the locations, and the script did not check them. Read each quote to decide:
- Journal-Fit Reviewer · W6: The numbers that §7 discusses live in appendix tables
  > “\\caption{Learned versus exact label averages across five problem seeds. Energy is normalised by the square root of the analytic posterior trace; conditions and samples are nested within seeds” (Section 7 (Numerical evidence), Table tab:learned-averages, printed in place in the TMLR build via moveblock{learnedtab})
- Reviewer 3 · W4: The privacy and extraction literature is not engaged where the paper makes privacy claims
  The claim quotes words that the manuscript does not contain: “extraction-relevant”
- Reviewer 1 · W1: The stress-test positive control passes because of floating-point resolution loss, not because the fixed-step scheme resolves an attracting tie
  > “fractions $0$, $0.049$, $0.410$ and $0.988$, against basin probabilities $0$, $0.050$, $0.406$ and $0.991$ under $\\pi\_0$” (Section 7, paragraph "A positive control for the stress test")

The author decides what to do with each row. This check does not change the decision, the consensus counts, or the Revision Roadmap. The judge is the session model; as this judge, the #1002 contrast test passed Claude Opus 5.5 and Claude Fable 5.1 (gpt-6-astra and Gemini 4 Argon passed it in part one, through other transports); other models are untested.

## Attachment: Acronym Check (advisory, #849)

### Acronym check (advisory; no reply needed)
Not checked: the input is not a Markdown or plain-text file.
