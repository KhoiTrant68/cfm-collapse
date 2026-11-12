# Editorial Decision Package

## Calibration Resolution

`calibration_status: NOT_CALIBRATED`

Runtime boundary: this package is not upgraded from any candidate or prose-named profile. `PROFILE_MEASURED` is unavailable; no closed profile artifact or replay validator binds this panel's execution topology.

## Run Conditions

- **Contract**: `reviewer/reviewer_full/v2` (mode `reviewer_full`, panel_size 5), `P/contract.json`.
- **Criteria binding**: this is an explicitly unbound run. All five seats (EIC, methodology, domain, perspective, DA) disclose `criteria_binding_unavailable` in their contract-acknowledgement cards (`eic.phase1.md`, `methodology.phase1.md`, `domain.phase1.md`, `perspective.phase1.md`, `da.phase1.md`). No #684 binding marker set exists, so the criteria-aware pre-check does not apply. **No venue-alignment claim is made.** The author's target venue is ICLR 2027 main track; the D6 judgement below is the EIC seat's opinion under the generic contract wording, not an assessment against bound ICLR 2027 criteria.
- **Cards used**: the five Phase 2 cards `eic.phase2.md`, `methodology.phase2.md`, `domain.phase2.md`, `perspective.phase2.md`, `da.phase2.md`. All five passed `check_phase_conformance.py` (as reported by the dispatching layer). No seat was dropped; the panel is not shrunk.
- **Manuscript use**: `manuscript.md` was consulted only to confirm that quoted evidence anchors exist. Every anchor cited in this package was found in the manuscript text (several span a line break in the extraction). No finding in this package originates with the editor.
- **Cross-model decision check (#518)**: not run; no cross-model check was requested for this dispatch.

## Review Panel Provenance (#540/#740)

- **Typed artifact**: `P/provenance.json` (`review-panel-provenance/1.0`), built from `P/provenance_input.json` and replay-validated with `review_panel_provenance.py validate` (PASS, as reported by the dispatching layer).
- **Artifact SHA-256**: `c89dbdf25cd8d075cd5aa750c2387d775306a0e72c1f8397ad9e597fdc1ab4fa` (raw bytes of `provenance.json`)
- **Panel ID**: `cfm-collapse-iclr2027-2026-11-07`
- **Contract SHA-256**: `e9712090d2469fea15a37b8e22d4e137afbcb2bf38d5789939c5df56738ef7af`
- **Normalized manifest SHA-256**: `c7d64cadf46200d38226429fc600f7ae621a3e1559efd051d87ca764431860a4`
- **Execution topology SHA-256**: `c259b3f71e07a5edf63a2840650cfafb0d9380f68f5533b18fdd78f82f6e2603`
- **Fresh-context scope**: `within_panel_attempt_only` (does not compare retries or prior rounds).

| Seat | Role ID | Actor type | Context ID | Peer outputs visible | Model family | Provider | Human reviewer ID |
|---|---|---|---|---|---|---|---|
| EIC | eic | model | phase2-eic-fresh-subagent | false | claude-opus-5-5 | anthropic | null |
| R1 | methodology | model | phase2-methodology-fresh-subagent | false | claude-opus-5-5 | anthropic | null |
| R2 | domain | model | phase2-domain-fresh-subagent | false | claude-opus-5-5 | anthropic | null |
| R3 | perspective | model | phase2-perspective-fresh-subagent | false | claude-opus-5-5 | anthropic | null |
| DA | da | model | phase2-da-fresh-subagent | false | claude-opus-5-5 | anthropic | null |

| Provenance axis | Status (`true` / `false` / `unknown`) |
|---|---|
| Role-separated | true |
| Within-panel invocation-context separation | true |
| Blind to peer outputs | true |
| Model-family distinct | false |
| Provider distinct | false |
| Human-reviewer distinct | false |

- **Binary independence claim**: not computed (artifact `independence_claim: not_computed_from_personas`). Persona and role diversity establish only `role_separated`. Persona separation is not independence, so this panel is not relabelled as independent.
- **Correlated-error disclosure** (artifact: `required: true`, reason `same_model_family`): "All model-executed review seats used one model family; role separation does not remove correlated-error risk." In this panel, all five seats ran on claude-opus-5-5 (Anthropic), each in a fresh subagent context without visibility of peer outputs. Read cross-seat corroboration in this letter with that limit in mind.

---

## Mechanical Synthesis (v3.6.2 Sprint Contract Protocol)

### Step 1: Role-scoped scoring matrix

Only assessed scores from eligible roles count; `not_assessed` entries from ineligible roles are excluded from numerator and denominator. No seat declared a fatal block.

| Dim | Name | Priority | Eligible roles | Assessed eligible scores | Audit verdict |
|---|---|---|---|---|---|
| D1 | methodology_rigor | mandatory | methodology | methodology = warn | warn |
| D2 | domain_accuracy | mandatory | domain | domain = warn | warn |
| D3 | argumentative_coherence | mandatory | da, methodology | da = warn; methodology = warn | warn |
| D4 | cross_disciplinary_relevance | high | perspective | perspective = warn | warn |
| D5 | writing_and_structure | normal | eic | eic = warn | warn |
| D6 | venue_fit_and_contribution | mandatory | eic | eic = warn | warn |

Every dimension has at least one assessed eligible seat; no `[DIMENSION-UNASSESSED]` abort.

Seat triggers (transported verbatim): D1 methodology "numerical reporting lacks some solver, tolerance, or seed details while the conclusions still look robust"; D2 domain "relevant closely related work is missing without affecting the central claim"; D3 da "an equivocation between closely related notions"; D3 methodology "Some claims are phrased more strongly than their support (for example a heuristic or numerical finding described in theorem-like language)"; D4 perspective "practical implications are plausible but under-explained"; D5 eic "frequent but non-essential appendix dependence"; D6 eic "significance for practical samplers is argued thinly".

### Step 2: Failure-condition evaluation

All six expressions parse within the closed vocabulary.

| Condition | Severity | Quantifier | Expression | Evaluation | Fired |
|---|---|---|---|---|---|
| F1 | 95 | any | any mandatory dimension has a fatal block | No seat declared a fatal block on D1, D2, D3 or D6 | false |
| F2 | 90 | any | any mandatory dimension scores 'block' | D1, D2, D3, D6 are all warn; no block | false |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse | Per dimension under `majority`: D1 (n=1, owner seat warn) true; D2 (n=1, owner seat warn) true; D3 (n=2, both seats required: da warn, methodology warn) true; D6 (n=1, owner seat warn) true. Four mandatory dimensions true, which is two or more | true |
| F4 | 60 | any | any high-priority dimension scores 'block' | D4 is warn | false |
| F5 | 40 | any | any dimension scores 'warn' or worse | D1 to D6 all warn | true |
| F0 | 10 | all | every dimension scores 'pass' | No dimension passes | false |

### Step 3: Precedence and audit lines

Fired: F3 (severity 70, action major_revision) and F5 (severity 40, action minor_revision). Highest severity is F3. The DA card's CRITICAL table is empty, so there are no DA CRITICAL IDs to adjudicate.

dimension_verdicts: [D1=warn, D2=warn, D3=warn, D4=warn, D5=warn, D6=warn]
fired_conditions: [F3, F5]
da_critical_adjudications: []
editorial_decision=major_revision

The F3 action is applied as stated and not softened. No `[DA-CRITICAL-VS-ACCEPT]` marker applies (the decision is not accept and there are no DA CRITICAL items).

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting "Atomic Endpoints of Averaged and Guided Empirical Conditional Flows", which you intend for the ICLR 2027 main track. The manuscript was reviewed by five role-separated review seats: a Journal-Fit Reviewer (EIC), three peer reviewers (methodology, domain, cross-disciplinary), and a Devil's Advocate. All five seats ran on the same model family in separate contexts. Their provenance is reported above and is not a claim of independent review. This run was not bound to ICLR 2027 review criteria, so nothing below asserts alignment with that venue's standards.

### Decision: Major Revision

The decision follows mechanically from the review contract. Four mandatory dimensions (methodology rigour, domain accuracy, argumentative coherence, venue fit and contribution) each received a warn from their eligible seats, which fires condition F3. No seat found a block or a fatal flaw. The methodology seat checked the core proofs line by line and reports "no counterexample to any stated theorem and no invalid core step". The revision this decision asks for is mostly rescoping, repositioning and added reporting, not new theory.

### Reviewer Summary

The cards are sprint-contract score cards. None states an overall Accept/Minor/Major/Reject recommendation, so the dimension scores are reported instead.

| Seat | Role | Assessed dimensions | Weaknesses (severity) | Report-level scope disclosure |
|---|---|---|---|---|
| EIC | Journal-Fit Reviewer (Area Chair angle) | D5 warn, D6 warn | 1 Major, 5 Minor | Defers proof checking to R1 and literature fidelity to R2 |
| R1 | Methodology: mathematics and numerics | D1 warn, D3 warn | 7 Minor | Checked Thm 4.6, Prop B.6, B.7, Cor B.11, Thm 5.1 and Lemmas B.2/B.3 line by line; Lemma B.9 and Thm B.10 structure only |
| R2 | Domain: memorisation, closed-form denoisers, CFG | D2 warn | 2 Major, 4 Minor | Did not check proofs line by line |
| R3 | Cross-disciplinary: nonparametric statistics, privacy auditing | D4 warn | 5 Minor | Takes the ODE machinery as given |
| DA | Devil's Advocate | D3 warn | 0 Critical, 4 Major, several Minor (body text) | N/A, per-finding only |

### Consensus Analysis

Consensus is counted per sub-claim over the four non-DA seats (EIC, R1, R2, R3); silence is not agreement. The full sub-claim inventory is in Part 3.

#### Points of Agreement (Consensus)

- **[CONSENSUS-4]**: none.
- **[CONSENSUS-3]**: none.

No sub-claim reached the consensus bar. This reflects the seats' disjoint assignments (R1 assessed only D1/D3, R2 only D2, R3 only D4, EIC only D5/D6) as much as any substantive disagreement. Every other weakness is a single-reviewer finding, assessed against its anchored evidence, not discounted for lack of corroboration.

Shared strengths, stated independently by several seats:
- **Honest scoping of the composition result as an existence result**: EIC S2, R2 S3, R3 S3, and the DA overall assessment.
- **Statement-level comparison with Liu and Zuazua (Appendix B.1, Table 4)**: EIC S4 and R2 S1.
- **Numerical failures reported, not discarded**: R1 S4 and R2 S3.
- **Label-bottleneck proposition (B.6) correct and well placed**: R1 S3 and R3 S2.
- **Shared-label CIFAR-10 run tests Assumption 1(iii)**: R2 S5 and R3 S4.
- **Core theorems sound**: R1 S1, S5, S6, S7. The DA also says that "the theorems in Sections 3 and 4 appear internally consistent".

#### Points of Disagreement

**Disagreement 1 (SC-1): practical significance and framing of the composition result**
- **EIC view (W1, Major)**: the result that sets the paper apart from "the empirical minimiser memorises" has no demonstrated route to practical samplers. The paper asserts its significance through scope limits rather than showing a consequence. The authors should either state what a practitioner or auditor can test or change, or re-centre the headline on the positive and transfer results.
- **R2 view (W5, Minor)** and **R3 view (W4, Minor)**: the same facts (Prop B.6, the learned label-average pilot, at most 0.001 midpoint mass for standard velocity CFM, the tie-centred input) make the abstract's practitioner framing an overreading. The abstract and Introduction should say that the composite has no identified practical instance and that the threshold is a structural boundary, not a tuning rule.
- **R1**: silent.
- **DA (M2, Major)**, outside the count, makes the same point and anchors it to the abstract's "knobs a practitioner turns" sentence.
- **Disagreement type**: severity disagreement. All three seats agree the problem exists and propose compatible remedies.
- **Editor's Resolution**: required revision (must_fix). The shared minimum is to rescope the abstract and Introduction so that the composition's existence status and lack of a known practical instance appear where the practitioner framing appears, and either (a) name a testable consequence or (b) present the composition as a boundary marker (EIC's two options).
- **Resolution Rationale**: on evidence, all three seats cite the same in-paper facts and none disputes them. On expertise, significance for the venue is the EIC seat's assigned dimension (D6), while R2 and R3 judged the framing from D2 and D4. The editor does not re-rate severity. Each row keeps its transported severity, and the Major versus Minor split is recorded as **unresolved on severity, resolved on action**. It does not bear on the decision, which F3 fixes regardless of this item's severity.

**Disagreement 2 (SC-2a): scope of the practical takeaway from Theorem 5.1**
- **EIC view (W2, Minor)**: the Introduction and Implications state "a sample far from the training set therefore points to the error of the learned field" more generally than Theorem 5.1, which is a hard-conditioning, identifying-label statement. The 38% off-atom CIFAR-10 samples at h = 6 are at positive bandwidth and not attributed to any cause. The fix is to restrict the sentence, or to say the off-atom CIFAR samples are not yet explained by the transfer bound.
- **R2 view (W2, Major)**: same scope problem. In addition, the image-scale support is "by elimination" (the sampler is ruled out, the mechanism of Theorem 5.1 is not shown), and Section 5 overstates what Appendix C.4 measures (sub-claim SC-2b below). R2 proposes the same restriction and, as a stronger option, measuring (1 − t)|Δ| along off-atom CIFAR trajectories from retrained checkpoints.
- **R1, R3**: silent.
- **DA (M3, Major)**, outside the count: the transfer claim is close to definitional (Appendix C.4: "this agreement is the identity of the theorem") and holds only at an identifying label. The DA asks the authors to restrict the inference or state what observation could falsify the field-versus-sampler attribution at h > 0.
- **Disagreement type**: severity disagreement, with compatible remedies.
- **Editor's Resolution**: must_fix for the shared remedy: restrict the practical sentence in Section 1 and Section 8 to the setting Theorem 5.1 covers, and say explicitly that the off-atom CIFAR-10 samples at h > 0 are not explained by the transfer bound. The DA's falsifiability request is folded into this item's acceptance criterion. R2's retrained-checkpoint measurement is a separate `consider` item (S-series), because R2 offers it as "better still", not as the minimum.
- **Resolution Rationale**: on evidence, the EIC, R2 and DA readings of Theorem 5.1's scope agree and all anchors are verified. Severity is left as transported and recorded as unresolved, with no directional prior.

No existence or direction disagreements were found. No seat argues that a raised weakness is not a real problem.

### Devil's Advocate Findings

The DA card's CRITICAL table is empty, so the adjudication list is `[]` and nothing is VALIDATED, REJECTED or UNRESOLVED. The four DA MAJOR findings are handled visibly:

| DA item | DA argument | Corroboration by non-DA seats | Editorial assessment | Required author response |
|---|---|---|---|---|
| M1 | "Collapse" equivocates between the exact endpoint atom (Prop 3.2) and small conditional variance at a finite cutoff. Prop C.2(a) rules out endpoint atoms for standard velocity networks. | None directly. R1 W5 concerns the hypotheses of Prop C.2(a) but not this equivocation. | Both anchors are verified in the manuscript (abstract "collapse in finite time as the hard-conditioning theory"; App C.2 "collapse can only be approached at a finite cutoff"). It is the DA owner's stated D3 warn trigger. | must_fix (Required R8) |
| M2 | The composite needs a field average that the paper's own Prop B.6 says a bottleneck does not produce, so the practitioner-knob framing overstates Theorem 4.6. | EIC W1, R2 W5, R3 W4 | Merged into SC-1 (Disagreement 1) | must_fix (Required R1) |
| M3 | The transfer claim is near-definitional and scoped to identifying labels, yet it is used for h > 0 image samples. | EIC W2, R2 W2 | Merged into SC-2a (Disagreement 2) | must_fix (Required R2) |
| M4 | The abstract presents the CIFAR-10 pair computation as confirming the threshold, but it uses the 8 largest-margin pairs of 81, B = 1 tuned per pair, and the appendix concedes it is not new evidence. | Partial. R1 W2 questions the large-w fractions on the same pairs. R2 S4 and R1 W2 both note that the appendix correctly calls it a consistency check; the problem is the abstract wording. | Anchors verified ("these eight are the ones with the largest margin"; "Exact computations confirm the threshold"). | must_fix (Required R9) |

The DA's Minor items (the line-90 sentence versus Table 1, the scope of "exactly one composition", the abstract stability claim, the d = 8 resolution and the floating-point caveat) appear as Suggested Revisions.

### Decision Rationale

Under the sprint contract the decision is arithmetic. Four mandatory dimensions score warn from every eligible seat: D1 (methodology), D2 (domain), D3 (DA and methodology together) and D6 (EIC). Condition F3 ("two or more mandatory dimensions score 'warn' or worse", majority quantifier) fires at severity 70 and outranks F5 (severity 40). The decision is therefore Major Revision. A more lenient outcome is not available: Minor Revision would require F3 not to fire, and the contract forbids softening a fired action. A stricter one is not warranted either: no seat recorded a block or a fatal block, so F1 and F2 do not fire.

The cards agree on the substance behind this result. The mathematical core is not in question. R1 verified Theorem 4.6, Proposition B.6, Corollary B.11 and Theorem 5.1, re-derived the near-threshold law (finding C* = 1 exact for the cubic truncation), and found no invalid core step. The DA concurs that the Section 3 and 4 theorems are internally consistent. The warns concern the bridge from the exact field to practice and how it is presented:
- the composition result is framed through practitioner knobs that the paper's own evidence says do not produce the composite (SC-1, DA M2);
- the late-time-error takeaway is stated beyond the identifying-label scope of Theorem 5.1 and is supported at image scale only by elimination (SC-2a, SC-2b, DA M3);
- "collapse" is used for two different objects (DA M1);
- the main text does not engage the inductive-bias account of off-training samples and mischaracterises two cited works (SC-3);
- a formal law is stated as fact (SC-8), and some numerical sensitivity checks are missing (SC-9, SC-10).

Most of these are text and positioning repairs. A few need added numerical reporting. None needs new theory. The two SPLITs are severity disagreements with compatible remedies, and resolving them either way would not change the decision. Because this was an unbound, same-family panel, the result should not be read as a prediction of the ICLR 2027 outcome.

### Blocking Issues (immutable source order)

The three Major-severity issues raised by more than one seat. All nine Required Revisions remain required. This table only selects the multi-seat Major items.

| Transport ref | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| R1 | Composition result framed as practical without demonstrated route; abstract practitioner framing overreads it | EIC (W1), R2 (W5), R3 (W4), DA (M2) | `text: §4.3 after Theorem 4.6 "not as a mechanism expected in standard trained models"` | REV-1 |
| R2 | Practical takeaway from Theorem 5.1 stated beyond its identifying-label scope; h > 0 image samples unexplained | EIC (W2), R2 (W2), DA (M3) | `text: §1 closing paragraph "a sample far from the training set therefore points to the error of the learned field"` | REV-2 |
| R6 | "Error" framing not positioned against the inductive-bias account; cited works mischaracterised | R2 (W1) | `text: Section 1, lines 095–096, "a sample far from the training set therefore points" and "not to the sampler"` | REV-6 |

Note: R6 is a single-seat Major finding, included because it is the D2 owner's principal driver. The other two are multi-seat.

### Closing

We encourage you to consider the reviewers' comments carefully and to submit a substantially revised manuscript. The revised manuscript will go through another round of review. Please answer every Required and Suggested item using `templates/revision_response_template.md`, and mark all changes in the revised manuscript.

---

## Part 2: Revision Roadmap

`schema_version: revision-roadmap/1.0` (reviewer-owned core). Items follow immutable source order: card order EIC, R1, R2, R3, DA; within each card, the order of findings; merged items sit at their first source. `R<n>` and `S<n>` are transport references, not ranks. Severity and confidence are transported from the cards. Obligation class is the editorial gate: must_fix applies to Major findings and to the stated warn-trigger drivers of the mandatory dimensions, should_fix to the other substantive findings, and consider to optional or extraction-conditional items. `proposed_targets[]` block ids are **not emitted**, because no bound block manifest exists for this run. The dispatching layer must supply one before the machine artifact is finalised. No author triage, work order or deadline is included.

### Required Revisions (Must Fix)

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|---|---|---|---|---|---|---|---|---|
| R1 | Rescope the composition result's practical framing (abstract, §1); state existence status and lack of a known practical instance; either name a testable consequence or present it as a boundary marker | SC-1 | Major (EIC); Minor (R2, R3); Major (DA M2) | `text: §4.3 after Theorem 4.6 "not as a mechanism expected in standard trained models"`; `text: Section 1, lines 045–046, "a hypothesis we test in one form"`; `text: §6.2 "centred at the known tie z = 0 ..."` | EIC 4; R2 4; R3 3; DA 4 | EIC, R2, R3, DA | must_fix | section: Abstract, §1, §8 Implications | claim_scope_unsupported: abstract/§1 composition framing |
| R2 | Restrict the Theorem 5.1 takeaway to identifying labels; say that off-atom CIFAR samples at h > 0 are not explained by the transfer bound; state what would falsify the attribution at h > 0 | SC-2a | Minor (EIC); Major (R2); Major (DA M3) | `text: §1 closing paragraph "a sample far from the training set therefore points to the error of the learned field"`; `text: Abstract l.27 "so in standard models a sample far from the training set reflects that"` | EIC 3; R2 4; DA 4 | EIC, R2, DA | must_fix | sentence: §1 closing paragraph, §8 Implications | claim_scope_unsupported: §1/§8 practical takeaway |
| R3 | Qualify near-threshold continuity and linearity as formal and numerical in App B.6 and §6.2, or prove them (R1 sketches a cubic-comparison route) | SC-8 | Minor | `text: Appendix B.6 "The basin probability therefore vanishes continuously, and linearly, at the threshold"` | 4 — re-derived the formal law | R1 | must_fix | sentence: App B.6, §6.2 | claim_scope_unsupported: App B.6 / §6.2 near-threshold statement |
| R4 | Extend hand-off and tolerance reruns of the CIFAR composite to 5 wc and 10 wc, or mark those points in Fig 12(b) as unchecked | SC-9 | Minor | `text: Appendix E.3 "We reran all eight pairs at w/wc ∈ {0.9, 1.1, 2}"` | 4 — follows from the stated protocol | R1 | must_fix | re_analysis: App E.3, Fig 12(b) | method_reproducibility_unresolved: CIFAR composite at 5 wc, 10 wc |
| R5 | Report ROS2 tolerance disagreement and cutoff invariance for the learned composite at B = 2, B = 3 and on the triangle (main-text 0.143 ± 0.004; Table 12) | SC-10 | Minor | `text: Appendix E.3 "in the two-atom runs the endpoint classes of the composite differ between the two tolerances for at most 1.07% of the sources"` | 3 — the check may exist in artifacts but is unreported | R1 | must_fix | re_analysis: App E.3, Table 12 | reporting_requirement_unmet: learned-composite tolerance checks |
| R6 | Reposition the "error of the learned field" implication against the inductive-bias/locality account (Kamb & Ganguli; Niedoba et al.; Kadkhodaie et al.); stop listing Kamb & Ganguli and Kadkhodaie et al. under "the empirical minimiser memorises" | SC-3 | Major | `text: Section 1, lines 095–096, "a sample far from the training set therefore points" and "not to the sampler"` | 4 — core area of the seat | R2 | must_fix | section: §1 Related work, §1 closing, §8 | claim_scope_unsupported: §1/§8 interpretation of off-training samples |
| R7 | Correct the §5 sentence saying App C.4 measures trajectory error on the off-atom CIFAR-10 samples (C.4 measures Δ only on EXP-1) and state the image-scale limitation in Implications | SC-2b | Major | `text: Section 5, lines 355–356, "Appendix C.4 measures the" ... "trajectory error on EXP-1 and the off-atom CIFAR-10 samples"` | 4 | R2 | must_fix | sentence: §5, §8 Implications | evidence_gap_remains: image-scale attribution of off-atom samples |
| R8 | Separate "finite-cutoff collapse" from the theorem's endpoint atom; restate the experimental claim as convergence toward the exact minimiser at a cutoff | DA-M1 | Major | `text: Abstract l.30 "collapse in finite time as the hard-conditioning theory"`; `text: App C.2 "endpoint law has no atom anywhere, and collapse can only be approached at a finite cutoff."` | 4 | DA | must_fix | section: Abstract, §6.1, App C.2 | interpretive_ambiguity_remains: meaning of "collapse" |
| R9 | Describe the CIFAR-10 pair computation in the abstract as a consistency check of Thm B.10(c) on selected pairs; report midpoint fractions over all 81 mutual-nearest-neighbour pairs or a random subset | DA-M4 | Major | `text: App E.3 "these eight are the ones with the largest margin"`; `text: Abstract l.28 "Exact computations confirm the threshold,"` | 3 | DA | must_fix | re_analysis: Abstract, App E.3 | claim_scope_unsupported: abstract CIFAR threshold claim |

### Required Item Details

**R1: Practical framing of the composition result**
- **Problem**: The abstract opens with "the knobs a practitioner turns", but every in-paper test of field averaging by a network is negative or needs a tie-centred input. The paper's significance for the venue is asserted through scope limits rather than shown.
- **Source**: EIC W1 ("significance is asserted through scope limits rather than shown through a consequence"); R2 W5; R3 W4; DA M2.
- **Requirement**: In the abstract and §1, state that field-level label averaging is a modelling hypothesis with no identified practical instance (a bottleneck averages priors, Prop B.6), and that the threshold is a structural boundary. Then either state what a practitioner or auditor can test or change because of the result, or re-centre the headline on the positive and transfer results.
- **Acceptance criteria**: The abstract and §1 carry the existence-result caveat next to the practitioner framing, and the paper either names one testable consequence or explicitly presents the composition as a boundary marker.

**R2: Scope of the Theorem 5.1 takeaway**
- **Problem**: The practical sentence in §1 and §8 generalises Theorem 5.1, which is stated at an identifying hard label, to standard models and to h > 0 image samples. Only Prop C.1 (conditional on entering a small ball) covers h > 0.
- **Source**: EIC W2; R2 W2; DA M3.
- **Requirement**: Restrict the sentence to the setting Theorem 5.1 covers. State that the off-atom CIFAR-10 samples at h > 0 are not explained by the transfer bound. State what observation could falsify the field-versus-sampler attribution at h > 0.
- **Acceptance criteria**: No main-text sentence attributes h > 0 off-atom samples to the mechanism of Theorem 5.1 without qualification, and a falsifiable observation is named.

**R3: Status of the near-threshold law**
- **Problem**: App B.6 and §6.2 state right-continuity and linearity of P0 at wc as fact. Theorem 4.6 does not prove them; the paper itself calls the law formal.
- **Source**: R1 W1.
- **Requirement**: Add "formally and numerically" in both places, or prove the law by the cubic-comparison route R1 outlines.
- **Acceptance criteria**: Both statements are qualified as formal and numerical, or a proof of P0 = √(2/π)(w/wc − 1)/cosh B · (1 + O(w/wc − 1)) is given.

**R4: Sensitivity of CIFAR composite fractions at large w**
- **Problem**: The reruns cover w/wc ∈ {0.9, 1.1, 2} only. On the first pair, endpoints at 5 wc agree with the main run for only about half the sources, yet Fig 12(b) describes a peak-then-fall shape.
- **Source**: R1 W2.
- **Requirement**: Extend the reruns to 5 wc and 10 wc, or mark those points as unchecked.
- **Acceptance criteria**: Fig 12(b) and the text either report rerun agreement at 5 wc and 10 wc or flag those points as unchecked.

**R5: Tolerance and cutoff checks for the learned composite beyond two atoms**
- **Problem**: Tolerance agreement and ϵ-invariance are reported only for the two-atom runs and B = 1. The triangle comparison and the Table 12 ablations have none, in a regime the appendix shows to be stiff.
- **Source**: R1 W3.
- **Requirement**: Report the ROS2 tolerance disagreement and cutoff invariance for B = 2, B = 3 and the triangle.
- **Acceptance criteria**: App E.3 states the tolerance disagreement fraction and cutoff invariance for B = 2, B = 3 and the triangle runs.

**R6: Positioning against the inductive-bias account**
- **Problem**: Calling off-training samples "error" takes one side of an active debate. Kamb & Ganguli and Kadkhodaie et al. are cited only under "That the empirical minimiser memorises is well established", which misstates their main thesis. Niedoba et al. appear only in App C.4.
- **Source**: R2 W1.
- **Requirement**: Reposition §1 and §8: Theorem 5.1 locates where any non-memorising mechanism must act, and the locality accounts are candidate structured forms of that departure. Cite the three works for what they show.
- **Acceptance criteria**: The main text names the inductive-bias/locality account as a candidate structured departure covered by Theorem 5.1, and no citation of those works supports a claim of memorisation.

**R7: What Appendix C.4 measures**
- **Problem**: §5 says App C.4 measures trajectory error on the off-atom CIFAR-10 samples. C.4 measures Δ only on EXP-1. For CIFAR it reports off-atom fractions and concludes "the attribution remains open".
- **Source**: R2 W2.
- **Requirement**: Correct the §5 sentence and state the image-scale limitation in the Implications paragraph.
- **Acceptance criteria**: The §5 sentence matches what C.4 reports, and the Implications paragraph states that image-scale attribution rests on elimination.

**R8: Two meanings of "collapse"**
- **Problem**: "Collapse" denotes both the endpoint atom of Prop 3.2 and small conditional variance at a finite cutoff. Prop C.2(a) excludes the former for standard velocity networks.
- **Source**: DA M1.
- **Requirement**: Define finite-cutoff collapse separately and restate the experimental claim in the abstract and §6.1 accordingly.
- **Acceptance criteria**: Every use of "collapse" for trained networks is either the finite-cutoff notion, defined once, or explicitly the endpoint atom.

**R9: CIFAR-10 pair computation in the abstract**
- **Problem**: The abstract says exact computations "confirm the threshold" on CIFAR-10 pairs. The pairs are the 8 largest-margin of 81, B is tuned to 1 per pair, and the appendix says the result is not new evidence.
- **Source**: DA M4.
- **Requirement**: Call it a consistency check of Thm B.10(c) on selected pairs, and report fractions over all 81 pairs or a random subset.
- **Acceptance criteria**: The abstract wording matches the appendix's consistency-check framing, and the selection protocol and an unselected or all-pairs result are reported.

### Suggested Revisions (Should Fix / Consider)

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|---|---|---|---|---|---|---|---|---|
| S1 | Add one sentence in App B.1 (and a pointer from Related Work) on whether the heat-flow PF-ODE and the linear-interpolant field are related by reparametrisation for an empirical measure | SC-4 | Minor | `text: Appendix B.1 "so the comparison is between the analogous statements, not a claim that one implies the other"` | 3 | EIC | should_fix | sentence: App B.1, §1 Related work | interpretive_ambiguity_remains: novelty delta vs Liu & Zuazua |
| S2 | Define Γ, the hyperbolic profile and the face condition in §4.4 (two-atom case Γ = F′_w(0)) | SC-5 | Minor | `absence: main text §4.4 — expected a definition of Γ, a hyperbolic profile and the face condition` | 4 | EIC | should_fix | section: §4.4 | reader_traceability_reduced: §4.4 |
| S3 | Move image-scale off-atom numbers (Table 8 or Fig 6) into the main text | SC-6 | Minor | `text: §4 proof strategy "composition is where Step 2 fails (Figure 4)"` | 4 | EIC | should_fix | section: §6 | reader_traceability_reduced: §6 |
| S4 | Reword the last sentence of §4.4 ("source" used in two senses) and shorten the abstract to the contribution-list claims | SC-7 | Minor | `text: §4.4 last sentence "sources and saddles, including those the trace test misses, put no source at z"` | 3 | EIC | should_fix | sentence: §4.4, Abstract | editorial_conformance_unmet: abstract and §4.4 |
| S5 | Confirm the constant √(2/π) in the typeset B.6 (the extraction shows "2/π"; Table 11 matches √(2/π)) | SC-15 | not tagged; R1 review body note [SEVERITY-SOURCE: letter-fallback] Minor | `table: Table 11 (0.050, 0.021, 0.008 at 1.1 wc)` | [CONFIDENCE-SOURCE: report-level] not stated | R1 | consider | sentence: App B.6 | interpretive_ambiguity_remains: B.6 constant |
| S6 | Rephrase §6.2 to "is consistent with Proposition C.2(b)", not "leads one to expect" | SC-11 | Minor | `text: Section 6.2 "leaves the midpoint empty at w ≥ 5wc, as Proposition C.2(b) leads one to expect"` | 4 | R1 (DA body concurs) | should_fix | sentence: §6.2 | claim_scope_unsupported: §6.2 Prop C.2(b) reading |
| S7 | Add the missing hypothesis of Prop C.2(a) to the abstract (|vθ(0,t)| integrable, or "under mild growth conditions") | SC-12 | Minor | `text: Abstract "A learned field whose spatial Lipschitz constant is integrable up to t = 1 has no endpoint atom at all"` | 5 | R1 | should_fix | sentence: Abstract | claim_scope_unsupported: abstract Prop C.2(a) |
| S8 | Fix the remark after Prop B.6: v_p̄c is a vΠ with Π = δ_p̄c; the intended contrast is with the field average | SC-13 | Minor | `text: Appendix B.5 remark after Prop B.6 "is not a positive field mixture vΠ with a fixed Π"` | 4 | R1 | should_fix | sentence: App B.5 | interpretive_ambiguity_remains: remark after Prop B.6 |
| S9 | Check the sign of w|µu|² in the first line of the Θ display (proof of Thm 4.5) in the typeset version | SC-14 | Minor | `equation: Appendix B.5, proof of Theorem 4.5, first line of the Θ display` | 2 — may be an extraction artefact | R1 | consider | sentence: App B.5 | editorial_conformance_unmet: Θ display |
| S10 | Optional: measure (1 − t)|Δ| along off-atom CIFAR trajectories from retrained h > 0 checkpoints, using the exact field as teacher | SC-2c | Major (parent R2 W2) | `text: Section 5, lines 355–356` | 4 | R2 | consider | new_data: App C.4 | evidence_gap_remains: image-scale attribution |
| S11 | Discuss trained-model evidence that perturbing conditioning reduces replication (Somepalli et al. 2023; Wen et al. 2024), and link it to Theorem 5.1 | SC-16 | Minor | `absence: Section 1 Related work and Section 3 after Prop 3.6` | 4 | R2 | should_fix | section: §1 Related work, §3 | evidence_gap_remains: conditioning-perturbation literature |
| S12 | Expand guidance-theory related work (Wu et al. 2024; Bradley & Nakkiran 2024; Karras et al. 2024 autoguidance) | SC-17 | Minor | `absence: Section 1 Related work — theoretical analyses of CFG` | 3 | R2 | should_fix | section: §1 Related work | evidence_gap_remains: guidance-theory literature |
| S13 | State the shared-label result (within-class empirical law; App E.2) in two sentences in §3 or §6.1 | SC-18 | Minor | `text: Section 2, line 141, "Labels identify"` | 4 | R2 | should_fix | sentence: §3 or §6.1 | reader_traceability_reduced: shared-label scope |
| S14 | Replace "new samples" with "non-training endpoint" or "blend" for circumcentre endpoints; state that off-atom is not evidence of non-leakage | SC-19 | Minor | `text: §1 "No single intervention analysed here (Table 1) creates new samples from the field that training"` | 4 | R3 | should_fix | sentence: §1, §4.3, Table 1 | interpretive_ambiguity_remains: "new samples" vocabulary |
| S15 | Turn the Ethics privacy remark into a usable consequence: these knobs are not privacy mitigations at the exact optimum; connect to membership inference and DP | SC-20 | Minor | `text: Ethics Statement "which is relevant when conditional models are trained on sensitive data"` | 4 | R3 | should_fix | sentence: Ethics, §8 Implications | interpretive_ambiguity_remains: privacy consequence |
| S16 | Add a remark on how bound (4) scales with N and label-window occupancy (support vs. distance to posterior) | SC-21 | Minor | `text: Proposition 3.6 "and this lower bound does not depend on h"` | 4 | R3 | should_fix | section: §3 | interpretive_ambiguity_remains: large-N regime |
| S17 | Qualify endpoint noise as a support-level "remedy" only; note the smoothed-bootstrap and KDE reading | SC-22 | Minor | `text: Appendix D "a remedy must move the support"` | 4 | R3 | should_fix | sentence: App D, Table 1, §1 | claim_scope_unsupported: endpoint-noise remedy |
| S18 | Reconcile the line-90 sentence ("No single intervention ... creates new samples") with the Table 1 exceptions | DA-5 | Minor (DA body) | `text: §1 line 090 "No single intervention analysed here (Table 1) creates new samples"` | [CONFIDENCE-SOURCE: report-level] not stated | DA | should_fix | sentence: §1 | interpretive_ambiguity_remains: §1 summary sentence |
| S19 | Scope "exactly one composition" to compositions of the three named knobs at h > 0 | DA-6 | Minor (DA body) | `text: Limitations, composites other than guided label averaging not covered` | [CONFIDENCE-SOURCE: report-level] not stated | DA | should_fix | sentence: Abstract, §1 | claim_scope_unsupported: "exactly one composition" |
| S20 | State in the abstract's stability sentence that atom-geometry perturbation is excluded | DA-7 | Minor (DA body) | `text: §4.3 "not of the atom geometry (Proposition B.7 in Appendix B.6)"` | [CONFIDENCE-SOURCE: report-level] not stated | DA | should_fix | sentence: Abstract | claim_scope_unsupported: abstract stability claim |
| S21 | Note in the main text that d = 8 sink fractions at w ≤ 2 wc fall below the 1/2048 resolution, and that composite probabilities lack interval arithmetic | DA-8 | Minor (DA body) | `table: Table 10, d = 8 rows` | [CONFIDENCE-SOURCE: report-level] not stated | DA | consider | sentence: §4.4 or §6.2 | reporting_requirement_unmet: numerical resolution caveat |

### Source-Traceability Checklist

Source order is preserved; this is not a work order. Author triage (`will_address` / `wont_address` / `not_on_point`) is collected later in a separate sidecar.

- [ ] R1 — obligation `must_fix`: rescope the practical framing of the composition result (SC-1)
- [ ] R2 — obligation `must_fix`: restrict the Theorem 5.1 takeaway to identifying labels; name a falsifier (SC-2a)
- [ ] R3 — obligation `must_fix`: qualify or prove the near-threshold law (SC-8)
- [ ] R4 — obligation `must_fix`: sensitivity reruns at 5 wc and 10 wc, or mark them unchecked (SC-9)
- [ ] R5 — obligation `must_fix`: report tolerance and cutoff checks for B = 2, B = 3 and the triangle (SC-10)
- [ ] R6 — obligation `must_fix`: position against the inductive-bias account; fix the citation list (SC-3)
- [ ] R7 — obligation `must_fix`: correct the §5 description of App C.4 (SC-2b)
- [ ] R8 — obligation `must_fix`: separate finite-cutoff collapse from the endpoint atom (DA-M1)
- [ ] R9 — obligation `must_fix`: reword the abstract CIFAR claim; report all or random pairs (DA-M4)
- [ ] S1 — obligation `should_fix`: Liu & Zuazua equivalence sentence (SC-4)
- [ ] S2 — obligation `should_fix`: define Γ and the face condition in §4.4 (SC-5)
- [ ] S3 — obligation `should_fix`: move image-scale evidence into the main text (SC-6)
- [ ] S4 — obligation `should_fix`: shorten the abstract; reword the §4.4 closing sentence (SC-7)
- [ ] S5 — obligation `consider`: confirm √(2/π) in B.6 (SC-15)
- [ ] S6 — obligation `should_fix`: reword the §6.2 Prop C.2(b) sentence (SC-11)
- [ ] S7 — obligation `should_fix`: add the Prop C.2(a) hypothesis to the abstract (SC-12)
- [ ] S8 — obligation `should_fix`: fix the remark after Prop B.6 (SC-13)
- [ ] S9 — obligation `consider`: check the Θ display sign (SC-14)
- [ ] S10 — obligation `consider`: retrained-checkpoint Δ measurement (SC-2c)
- [ ] S11 — obligation `should_fix`: conditioning-perturbation literature (SC-16)
- [ ] S12 — obligation `should_fix`: guidance-theory literature (SC-17)
- [ ] S13 — obligation `should_fix`: shared-label result in the main text (SC-18)
- [ ] S14 — obligation `should_fix`: "new samples" vocabulary (SC-19)
- [ ] S15 — obligation `should_fix`: privacy consequence in Ethics (SC-20)
- [ ] S16 — obligation `should_fix`: large-N remark (SC-21)
- [ ] S17 — obligation `should_fix`: qualify the endpoint-noise remedy (SC-22)
- [ ] S18 — obligation `should_fix`: line-90 sentence vs Table 1 (DA-5)
- [ ] S19 — obligation `should_fix`: scope of "exactly one composition" (DA-6)
- [ ] S20 — obligation `should_fix`: abstract stability caveat (DA-7)
- [ ] S21 — obligation `consider`: d = 8 resolution and interval-arithmetic caveat (DA-8)

### Response Letter Template

Respond to every R and S item using `templates/revision_response_template.md`, giving each item's disposition, the change made, and its new location.

### Journal-Supplied Deadline

- **Exact deadline from source letter**: `NOT PROVIDED`

---

## Part 3: Sub-Claim Inventory (Step 1b) and Reviewer Summaries

### Weakness sub-claim inventory (non-DA seats; DA shown for traceability, outside the count)

| sub_claim_id | parent_weakness | reviewer_id | position | evidence_pointer | severity | confidence |
|---|---|---|---|---|---|---|
| SC-1 | Composition result: practical significance and framing | EIC | raised | EIC W1 | major | 4 |
| SC-1 | same | R2 | disputed (severity: Minor) | R2 W5 | minor | 4 |
| SC-1 | same | R3 | disputed (severity: Minor) | R3 W4 | minor | 3 |
| SC-1 | same | R1 | not-mentioned | — | — | — |
| SC-1 | same | DA | raised (outside count) | DA M2 | major | 4 |
| SC-2a | Theorem 5.1 takeaway beyond identifying-label scope | EIC | raised | EIC W2 | minor | 3 |
| SC-2a | same | R2 | disputed (severity: Major) | R2 W2 | major | 4 |
| SC-2a | same | R1, R3 | not-mentioned | — | — | — |
| SC-2a | same | DA | raised (outside count) | DA M3 | major | 4 |
| SC-2b | §5 misstates what App C.4 measures | R2 | raised | R2 W2 | major | 4 |
| SC-2c | Measure Δ on off-atom CIFAR trajectories (optional) | R2 | raised | R2 W2, Q3 | major | 4 |
| SC-3 | Inductive-bias positioning; citations mischaracterised | R2 | raised | R2 W1 | major | 4 |
| SC-4 | Liu & Zuazua equivalence left open | EIC | raised | EIC W3 | minor | 3 |
| SC-5 | §4.4 unreadable without appendix | EIC | raised | EIC W4 | minor | 4 |
| SC-6 | Supporting evidence in appendix | EIC | raised | EIC W5 | minor | 4 |
| SC-7 | Dense passages (§4.4, abstract) | EIC | raised | EIC W6 | minor | 3 |
| SC-8 | Near-threshold law stated as fact | R1 | raised | R1 W1 | minor | 4 |
| SC-9 | CIFAR fractions at 5 wc and 10 wc unchecked | R1 | raised | R1 W2 | minor | 4 |
| SC-10 | Tolerance and cutoff checks only for two-atom runs | R1 | raised | R1 W3 | minor | 3 |
| SC-11 | Prop C.2(b) does not predict an empty midpoint | R1 | raised | R1 W4 | minor | 4 |
| SC-12 | Abstract drops a hypothesis of Prop C.2(a) | R1 | raised | R1 W5 | minor | 5 |
| SC-13 | Remark after Prop B.6 literally false | R1 | raised | R1 W6 | minor | 4 |
| SC-14 | Θ display sign slip | R1 | raised | R1 W7 | minor | 2 |
| SC-15 | √(2/π) constant in extraction | R1 | raised | R1 review body | minor [SEVERITY-SOURCE: letter-fallback] | [CONFIDENCE-SOURCE: report-level] not stated |
| SC-16 | Conditioning-perturbation literature missing | R2 | raised | R2 W3 | minor | 4 |
| SC-17 | Guidance-theory literature thin | R2 | raised | R2 W4 | minor | 3 |
| SC-18 | Shared-label regime only in appendix | R2 | raised | R2 W6 | minor | 4 |
| SC-19 | "New samples" vocabulary for blends | R3 | raised | R3 W1 | minor | 4 |
| SC-20 | Ethics privacy consequence not usable | R3 | raised | R3 W2 | minor | 4 |
| SC-21 | Fixed-N, large-N regime not discussed | R3 | raised | R3 W3 | minor | 4 |
| SC-22 | Endpoint-noise "remedy" is a smoothed bootstrap | R3 | raised | R3 W5 | minor | 4 |

Dispositions:
- SC-1 is a SPLIT (agree 1, conflict 2, silent 1).
- SC-2a is a SPLIT (agree 1, conflict 1, silent 2).
- All others are single-reviewer findings (agree 1, conflict 0, silent 3). None is promoted to consensus.

The `disputed` positions on SC-1 and SC-2a record severity divergence only. No seat denies that either problem exists.

Surface-form parity check: no sub-claim was down-rated for informal wording or credited for technical phrasing. Each is weighed against its verified anchor. R1's two extraction-conditional items (SC-14, SC-15) are kept as `consider` because the seat itself attributes them to possible extraction artefacts, not because of their wording.

### Journal-Fit Review (EIC) Summary
- Scores: D5 warn, D6 warn | Confidence per finding 3–4
- Key point: the work fits the venue's topics and is carefully scoped, but its distinctive composition headline lacks a demonstrated practical consequence, and the main text leans heavily on the appendix.

### Reviewer 1 (Methodology) Summary
- Scores: D1 warn, D3 warn | Confidence per finding 2–5
- Key point: the mathematical core holds after a line-by-line check. The reservations are the wording of a formal law and two gaps in sensitivity reporting. All three arithmetic receipts (Table 10 fractions) are consistent.

### Reviewer 2 (Domain) Summary
- Scores: D2 warn | Confidence per finding 3–4
- Key point: prior work is represented faithfully. The off-training "error" implication ignores the inductive-bias account, the image-scale attribution rests on elimination, and conditioning-perturbation and guidance-theory work is missing.

### Reviewer 3 (Perspective) Summary
- Scores: D4 warn | Confidence per finding 3–4
- Key point: the paper is statistically clear (Nadaraya–Watson reading, prior-averaging bottleneck). Its privacy and practical consequences are under-explained, and "new samples" and "remedy" will mislead auditors.

### Devil's Advocate Summary
- Recommendation: N/A, findings only. D3 warn.
- Key challenge: no unresolved CRITICAL challenge. The strongest MAJOR is the equivocation on "collapse" between the exact endpoint atom and finite-cutoff variance (M1). The other three concern the bridge from exact fields to practice.

## Attachment: Suggested-Reference Check (advisory, #1001)

Suggested-reference check (script output, not a reviewer finding; #1001)
Seats read: R2, R3 (complete).

| Seat | # | Reference | Result |
|---|---|---|---|
| R2 | 1 | Somepalli, G. et al. (2023) "Understanding and Mitigating Copying in Diffusion Models" | Found in an index |
| R2 | 2 | Wen, Y. (2024) "Detecting, Explaining, and Mitigating Memorization in Diffusion Models" | Found in an index |
| R2 | 3 | Wu, Y. (2024) "Theoretical Insights for Diffusion Guidance: A Case Study for Gaussian Mixture Models" | Found in an index |
| R2 | 4 | Bradley, A. et al. (2024) "Classifier-Free Guidance is a Predictor-Corrector" | Found in an index |
| R2 | 5 | Karras, T. et al. (2024) "Guiding a Diffusion Model with a Bad Version of Itself" arXiv:2406.02507 | Found in an index |
| R3 | 1 | Silverman, B. W. et al. (1987) "The bootstrap: to smooth or not to smooth?" | Found in an index |
| R3 | 2 | Gy�rfi, L. et al. (2002) "A Distribution-Free Theory of Nonparametric Regression" | Found in an index |
| R3 | 3 | Graf, S. et al. (2000) "Foundations of Quantization for Probability Distributions" | Found in an index |
| R3 | 4 | Shokri, R. et al. (2017) "Membership Inference Attacks Against Machine Learning Models" arXiv:1610.05820 | Found in an index |
| R3 | 5 | Dwork, C. et al. (2006) "Calibrating Noise to Sensitivity in Private Data Analysis" | Found in an index |

"Found" means an index holds a record with this DOI or arXiv ID and title, or with this title. It does not show that the work supports the recommendation, or that the authors and year are right.

## Attachment: Reviewer Claim Check (advisory, #1002)

The judge answered 28 of 28 findings from 5 reviewers: it marked 0 as contradicted, and 2 cannot be checked from the manuscript alone.

The judge also marked Reviewer 2 � W1 as false, but its quote did not pass the check, so they are not shown as contradicted.

The author decides what to do with each row. This check does not change the decision, the consensus counts, or the Revision Roadmap. The judge is the session model; as this judge, the #1002 contrast test passed Claude Opus 5.5 and Claude Fable 5.1 (gpt-6-astra and Gemini 4 Argon passed it in part one, through other transports); other models are untested.

## Attachment: Acronym Check (advisory, #849)

### Acronym check (advisory; no reply needed)
Coverage: body (partial)
Not in this input: English abstract, Chinese abstract.
Not checked:
- Body, line 1118: ICML (the initials before its parentheses do not spell it)
- Body, line 2933: PLa (the initials before its parentheses do not spell it)
- Body, line 3731: ZT (the initials before its parentheses do not spell it)
- Body, line 3735: YT (the initials before its parentheses do not spell it)
- Body, line 3794: LawU (the initials before its parentheses do not spell it)
- Body, line 3798: LawV (the initials before its parentheses do not spell it)
- Body, line 3799: LawYT (the initials before its parentheses do not spell it)
- Body, line 4580: ROS2 (the initials before its parentheses do not spell it)
- Body, line 4646: BQ (the initials before its parentheses do not spell it)

| Scope | Line | Rule | Acronym | Uses |
|---|---|---|---|---|
| Body | 1 | Defined after first use | ICLR | 59 |
| Body | 3 | Not defined | AND | 5 |
| Body | 3 | Not defined | ATOMIC | 1 |
| Body | 3 | Not defined | GUIDED | 1 |
| Body | 3 | Not defined | OF | 3 |
| Body | 6 | Not defined | FLOWS | 1 |
| Body | 60 | Not defined | CIFAR | 17 |
| Body | 60 | Not defined | MLP | 8 |
| Body | 227 | Not defined | SETUP | 1 |
| Body | 267 | Not defined | EXACT | 3 |
| Body | 267 | Not defined | THE | 7 |
| Body | 284 | Not defined | ODE | 5 |
| Body | 364 | Not defined | FIELDS | 4 |
| Body | 364 | Not defined | ON | 1 |
| Body | 374 | Not defined | PN | 18 |
| Body | 412 | Not defined | ATOMS | 3 |
| Body | 412 | Not defined | FIELD | 1 |
| Body | 412 | Not defined | KEEP | 1 |
| Body | 464 | Not defined | KEEPS | 1 |
| Body | 512 | Not defined | CAN | 3 |
| Body | 512 | Not defined | LEAVE | 1 |
| Body | 512 | Not defined | TWO | 2 |
| Body | 563 | Not defined | ANY | 1 |
| Body | 563 | Not defined | IN | 2 |
| Body | 566 | Not defined | PL | 40 |
| Body | 580 | Not defined | FROM | 1 |
| Body | 580 | Not defined | TO | 2 |
| Body | 632 | Not defined | EXP | 25 |
| Body | 643 | Not defined | RK4 | 9 |
| Body | 656 | Not defined | MNIST | 3 |
| Body | 664 | Not defined | DDPM | 3 |
| Body | 720 | Not defined | TIES | 1 |
| Body | 871 | Not defined | ETHICS | 1 |
| Body | 888 | Not defined | LARGE | 1 |
| Body | 888 | Not defined | MODELS | 1 |
| Body | 888 | Not defined | USE | 1 |
| Body | 916 | Not defined | ETH | 1 |
| Body | 932 | Not defined | RL | 1 |
| Body | 966 | Not defined | USENIX | 1 |
| Body | 969 | Defined again | ICLR | 59 |
| Body | 996 | Not defined | NY | 1 |
| Body | 1020 | Not defined | CVF | 2 |
| Body | 1020 | Not defined | IEEE | 2 |
| Body | 1027 | Defined again | ICLR | 59 |
| Body | 1052 | Defined again | ICLR | 59 |
| Body | 1059 | Not defined | PDE | 1 |
| Body | 1075 | Defined again | ICLR | 59 |
| Body | 1104 | Not defined | CADS | 1 |
| Body | 1106 | Defined again | ICLR | 59 |
| Body | 1258 | Not defined | FOR | 3 |
| Body | 1258 | Not defined | PROOFS | 3 |
| Body | 1315 | Not defined | LEMMAS | 1 |
| Body | 1315 | Not defined | THREE | 1 |
| Body | 1330 | Not defined | DTi | 1 |
| Body | 1472 | Not defined | HARD | 1 |
| Body | 1576 | Not defined | LABEL | 1 |
| Body | 1805 | Not defined | BASIC | 1 |
| Body | 1805 | Not defined | FACTS | 1 |
| Body | 1830 | Not defined | DKL | 7 |
| Body | 1934 | Not defined | STEPS | 1 |
| Body | 2047 | Not defined | BL | 1 |
| Body | 2115 | Not defined | KL | 2 |
| Body | 2164 | Not defined | CovQ | 1 |
| Body | 2302 | Not defined | RK | 1 |
| Body | 2362 | Not defined | XR | 1 |
| Body | 2933 | Not defined | DLM | 1 |
| Body | 2959 | Not defined | PLx | 1 |
| Body | 2959 | Not defined | tPLz | 1 |
| Body | 2961 | Not defined | PLz | 9 |
| Body | 3038 | Not defined | DA | 6 |
| Body | 3175 | Not defined | PLS | 2 |
| Body | 3200 | Not defined | DN | 2 |
| Body | 3227 | Not defined | PLaj | 1 |
| Body | 3239 | Not defined | PLM | 2 |
| Body | 3269 | Not defined | BR0 | 5 |
| Body | 3332 | Not defined | wIL | 1 |
| Body | 3353 | Not defined | IL | 8 |
| Body | 3387 | Not defined | LOSS | 2 |
| Body | 3387 | Not defined | WHAT | 2 |
| Body | 3585 | Defined again | CFM | 9 |
| Body | 3625 | Not defined | LR | 2 |
| Body | 3727 | Not defined | BT | 9 |
| Body | 3737 | Not defined | EZT | 1 |
| Body | 3794 | Not defined | EV | 2 |
| Body | 3799 | Not defined | EYT | 1 |
| Body | 3929 | Not defined | NOISE | 1 |
| Body | 4024 | Not defined | SiLU | 1 |
| Body | 4050 | Not defined | SGD | 3 |
| Body | 4276 | Not defined | CV | 1 |
| Body | 4304 | Not defined | DOP853 | 1 |
| Body | 4409 | Not defined | CFG | 1 |
