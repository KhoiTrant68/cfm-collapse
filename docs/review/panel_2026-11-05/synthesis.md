# Editorial Decision Package

## Calibration Resolution

`calibration_status: NOT_CALIBRATED`

Current runtime boundary: this package is not upgraded from a candidate or prose-named profile. `PROFILE_MEASURED` remains unavailable until a closed profile artifact and replay validator bind the exact target fields to the completed panel's `execution_topology_sha256`.

## Manuscript Information

- **Title**: Atomic Endpoints of Averaged and Guided Empirical Conditional Flows
- **Manuscript ID**: not provided
- **Target venue (named by the author)**: ICLR 2027
- **Submission Date**: not provided
- **Decision Date**: 2026-11-05
- **Review Round**: Round 1
- **Mode / contract**: `reviewer_full`, contract `reviewer/reviewer_full/v2` (panel_size 5)
- **Criteria binding**: `criteria_binding_unavailable`. No venue criteria brief was bound to this run. This package makes no venue-alignment claim beyond what the reviewers wrote. Binding-disclosure note: EIC, R2 (domain), R3 (perspective) and DA use the literal token `criteria_binding_unavailable`. R1 (methodology) gives the same unbound condition in prose ("No criteria binding was supplied, so I make no claim about venue fit") without the literal token. This is flagged here and was not altered. The report passed `check_phase_conformance.py`.

## Review Panel Provenance (#540/#740)

- **Typed artifact**: `docs/review/panel_2026-11-05/provenance.json` (replay-validated by the dispatching layer)
- **Artifact SHA-256** (raw bytes, recomputed at synthesis time): `d28a3270a2d8a77f4d1a4ca6f8ed9991ca8ab34ba7d258ee516f19d1bddffb4f`
- **Panel ID**: `cfm-collapse-iclr2027-2026-11-05`
- **Contract SHA-256 (bound in artifact)**: `e9712090d2469fea15a37b8e22d4e137afbcb2bf38d5789939c5df56738ef7af`
- **Normalized manifest SHA-256**: `3055c7d5504a8a7e1f51db5a22bb7b4a803e56c6d2f2d8f210da0715cc84f1b7`
- **Execution topology SHA-256**: `c259b3f71e07a5edf63a2840650cfafb0d9380f68f5533b18fdd78f82f6e2603`
- **Fresh-context scope**: `within_panel_attempt_only`. This does not compare retries or earlier rounds.

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

- **Binary independence claim**: Not computed (`independence_claim: not_computed_from_personas`). Persona or role diversity establishes only `role_separated`. The five seats are not described as independent reviewers.
- **Correlated-error disclosure**: All model-executed review seats used one model family; role separation does not remove correlated-error risk.
- **Reading note**: Every seat ran on `claude-opus-5-5` (Anthropic), each in its own fresh subagent context with no peer outputs visible. Agreement across seats is therefore agreement among five role prompts on one model family. It is not five independent confirmations. The consensus labels below count seats under the protocol. They should not be read as independent corroboration.

---

## Part 1: Editorial Decision Letter

Dear Author(s),

Thank you for submitting your manuscript, "Atomic Endpoints of Averaged and Guided Empirical Conditional Flows", for review against your stated target venue, ICLR 2027. Five role-separated review seats reviewed it: a Journal-Fit Reviewer (EIC), R1 (methodology), R2 (domain), R3 (cross-disciplinary perspective) and a Devil's Advocate (DA). Their execution provenance is reported above and is not reduced to a binary independence claim.

### Decision: Major Revision

### Sprint-contract mechanical audit (three-step protocol)

**Step 1: Role-scoped scoring matrix.** Only assessed scores from eligible roles are counted. `not_assessed` values from ineligible roles are excluded from both numerator and denominator. No seat declared a fatal block.

| Dim | Name | Priority | Eligible roles | Assessed eligible scores | n | Verdict (worst) |
|---|---|---|---|---|---|---|
| D1 | methodology_rigor | mandatory | methodology | methodology=warn | 1 | warn |
| D2 | domain_accuracy | mandatory | domain | domain=warn | 1 | warn |
| D3 | argumentative_coherence | mandatory | da, methodology | da=warn, methodology=warn | 2 | warn |
| D4 | cross_disciplinary_relevance | high | perspective | perspective=warn | 1 | warn |
| D5 | writing_and_structure | normal | eic | eic=warn | 1 | warn |
| D6 | venue_fit_and_contribution | mandatory | eic | eic=warn | 1 | warn |

Recorded triggers. D1 (R1): "numerical checks that confirm the result only qualitatively, without error bars, convergence-in-step-size evidence". D2 (R2): "image-scale interpretation stated more strongly than the measurement supports". D3 (DA): "Claims are directionally supported but overstated relative to the results". D3 (R1): "Local overreach or inconsistency that does not change the main message." D4 (R3): "a cross-field implication is stated in the discussion with hedging but no supporting evidence or explicit limitation". D5 (EIC): "The exposition is correct but hard to navigate." D6 (EIC): "The contribution is real and fits the venue but is modest or incrementally framed."

**Step 2: Failure conditions.** All six expressions parsed against the recognised vocabulary in §9. No `[EXPRESSION-UNRECOGNISED]` was raised.

| Condition | Severity | Quantifier | Expression (pattern) | Evaluation | Fired |
|---|---|---|---|---|---|
| F1 | 95 | any | any mandatory dimension has a fatal block (6) | No assessed eligible seat declared a fatal block on D1, D2, D3 or D6 | false |
| F2 | 90 | any | any mandatory dimension scores 'block' (1) | D1, D2, D3 and D6 have no block score | false |
| F3 | 70 | majority | two or more mandatory dimensions score 'warn' or worse (2) | Per-dimension majority: D1 n=1, owner warn, true. D2 n=1, owner warn, true. D3 n=2, both seats warn, true. D6 n=1, owner warn, true. That is 4 mandatory dimensions, and 4 ≥ 2 | **true** |
| F4 | 60 | any | any high-priority dimension scores 'block' (1) | D4 = warn, not block | false |
| F5 | 40 | any | any dimension scores 'warn' or worse (7) | D1 through D6 are all warn | **true** |
| F0 | 10 | all | every dimension scores 'pass' (9) | No dimension passes | false |

**Step 3: Precedence and decision.** The fired conditions are F3 (severity 70) and F5 (severity 40). The highest severity is F3, so its action (major revision) applies. The action is not softened.

dimension_verdicts: [D1=warn, D2=warn, D3=warn, D4=warn, D5=warn, D6=warn]
fired_conditions: [F3, F5]
da_critical_adjudications: []
editorial_decision=major_revision

DA CRITICAL adjudication. The DA's `#### CRITICAL` table has no rows. The DA states that "nothing here reaches a fatal or block-level break in the logic chain". The adjudication set is therefore empty and complete: no CRITICAL IDs exist, none is omitted, and no phantom ID is added. No rejection rationale is required. The decision is not `accept`, so the `[DA-CRITICAL-VS-ACCEPT]` marker does not apply. The DA's six MAJOR findings (M1 to M6) are carried into the roadmap below.

Cross-model blind decision check (#518): not run. No cross-model consent or `ARS_CROSS_MODEL` configuration was supplied to this synthesis, so the decision is single-model-family.

### Reviewer Summary

| Reviewer | Role | Recommendation | Confidence |
|---|---|---|---|
| Journal-Fit Reviewer (EIC) | ICLR Area Chair, generative-model theory | Major Revision ("My overall signal is Major Revision") | per-finding only (3 to 4) |
| Reviewer 1 | Applied mathematician, non-autonomous ODEs | Not stated as an enum. Scores D1 warn and D3 warn; "no counterexample to any formal statement as stated" | per-finding only (3 to 5) |
| Reviewer 2 | Memorisation and generalisation in diffusion and flow models | Not stated as an enum. Scores D2 warn | per-finding only (3 to 4) |
| Reviewer 3 | Nonparametric statistician, privacy and memorisation audits | Not stated as an enum. Scores D4 warn; "reframing and a few targeted additions, not for new theory" | per-finding only (3 to 4) |
| Devil's Advocate | Fixed adversarial seat | N/A, findings only | N/A, per-finding only |

Confidence values are the reviewers' self-reported scope disclosures. They were not used to weight, count or resolve anything.

### Shared strengths (recorded from the cards; not consensus labels)

- **The exact composition threshold is new and correct.** EIC S2, R1 S2 (re-derived both directions, including at the threshold), R2 S2 ("to my knowledge, no published work shows…") and R3's summary all identify the guided-label-averaging threshold w > 1/sinh²B as the paper's most novel result.
- **The formal statements hold as stated.** R1 checked the proofs line by line and found "no gap that cannot be repaired locally, and no counterexample to any formal statement as stated". R2: "The domain content I checked is correct." DA: "no theorem shown false as stated".
- **The learned-network claims are calibrated.** EIC S3, R2 S6, R3 S3 and DA all cite the abstract's statement that the learned observations "do not establish" asymptotic endpoint convergence, and they cite the Limitations section.
- **The known endpoint law is positioned correctly.** R2 S1 and R3 S1 both quote "is therefore a reference, not a new identity".

### Consensus Analysis

Consensus is counted per sub-claim over the four non-DA seats (EIC, R1, R2, R3). A seat that does not mention a sub-claim is counted as silent, not as agreeing. DA findings are tracked separately. The full sub-claim inventory is in Part 2.

#### Points of Agreement (Consensus)

**[CONSENSUS-4]**: none. No sub-claim was raised or corroborated by all four non-DA seats.

**[CONSENSUS-3]**
1. **SC-2: Standard trained networks do not reproduce the off-support basin, and the paper does not draw the consequence for practical samplers.** Raised by EIC W2 (Major): "Standard velocity CFM networks place essentially no mass at the midpoint… The paper reports this honestly but does not say what it means for the main question." Corroborated by R2 W2 (Major): "For standard trained CFM networks, the experiments point the other way: the mechanism does not appear… Report standard-CFM failure as a finding in its own right." Corroborated by R3 W1 (Major): "the networks they actually deploy do not exhibit this mechanism." **R1 (methodology) is silent.** R1 W9 concerns the causal attribution inside the ablation, which is a separate sub-claim (SC-16). DA M1 makes the same point and is not counted. Anchor: text, Section 7, "off-atom basin depends on its parametrisation, chiefly on its input, and not in every seed". Section 4.3 is also anchored: "it idealises classifier-free guidance applied to a network that resolves labels only".

**Corroborated (2/4, no conflict; below the consensus bar)**
- **SC-7a: The image experiments use one mask and N = 2000, which limits image-scale readings.** EIC W7 (Minor) and R2 W7 (Minor). R2 adds that N = 2000 sits in the known small-data memorisation regime, so the "At realistic capacity" heading overreaches.

All other sub-claims are single-reviewer findings (1/4). Each is retained and assessed against its anchored evidence. See Part 2.

#### Points of Disagreement

**Disagreement 1 (SC-6): Should the scoping disclaimer stay in the abstract?**
- **EIC W6 view (Minor)**: the abstract "ends on a disclaimer". Keep it, but move it into the introduction's experiments paragraph and end the abstract on the takeaway.
- **R2 S6 and R3 S3 view**: the abstract's statement that the observations "do not establish" asymptotic convergence is a listed strength. R2 calls it "the right caution, given Proposition C.2(a)".
- **Disagreement type**: Direction disagreement (placement).
- **Editor's Resolution**: Left to the author. The scoping statement stays visible in the abstract. The author may shorten it and end the abstract on the takeaway the EIC asks for (SC-1).
- **Resolution Rationale**: All three seats agree the disclaimer is accurate, and the EIC itself says "Keep the disclaimer". What remains is placement. Both remedies can be met at once if the scope sentence is kept and followed by a headline sentence. Obligation: `consider`.

**Disagreement 2 (SC-7b): How serious is the fact that the learned composition was tested only at d ≤ 2?**
- **EIC W7 (Minor)** and **R1 W9 (Minor)**: the narrow scope limits how far the learned findings generalise. The Limitations section already acknowledges it.
- **R3 W1 (Major parent)**: d ≤ 2 is part of why the practical meaning of the composition result is not established.
- **Disagreement type**: Severity disagreement.
- **Editor's Resolution**: Each seat's severity is kept unchanged on its own row. The roadmap item for SC-7b is `should_fix`. R3's Major concern about practical meaning is carried by SC-2, which is `must_fix`.
- **Resolution Rationale**: The seats agree on the fact, and the manuscript acknowledges it in Section 7. The severity gap comes from R3 bundling d ≤ 2 into its broader practical-relevance weakness. Resolving SC-2 answers that weakness directly.

**Disagreement 3 (SC-8b): How serious is it that the CIFAR-10 pair check is an exact-field consistency check of an analytically guaranteed reduction, presented in the abstract and introduction as confirmation?**
- **R1 W1 (Major)**: the threshold follows from Theorem 4.7 and Corollary B.9. State it as a corollary and present the computation as a consistency check.
- **R3 W1 (Major parent)**: "The CIFAR-10 pair evidence for the threshold is exact-field only."
- **R2 W4 (Minor)**: "Under these conditions the threshold is guaranteed analytically." Reword the claim and report the pair-selection rate.
- **Disagreement type**: Severity disagreement (Major vs Minor). The seats agree on substance.
- **Editor's Resolution**: `must_fix`. The three remedies are compatible and are all required: derive the result as a corollary, rescope the abstract and Section 1 wording, and report the pair-selection rate. Severities are kept unchanged per row.
- **Resolution Rationale**: Expertise first. R1 (methodology) shows that the corollary route is what actually supports the claim. R2 (domain) shows how the image-scale reading misleads. The claim appears in the abstract, so the editorial gate is `must_fix` whichever severity tag is read. The DA's M3 is not counted but reaches the same conclusion.

**Disagreement 4 (SC-14): Does Appendix C.4 rule out a solver or cutoff artefact for the off-atom U-Net samples?**
- **R1 W7 (Minor)**: no. Two refinement levels with a monotone decrease are "not evidence of convergence". The full-dataset comparison "addresses a different question".
- **R3 S5 (strength)**: the full-dataset re-measurement and the integrator refinement are the right control, ruling out "that it is a solver artefact".
- **Disagreement type**: Existence disagreement.
- **Editor's Resolution**: R1's view is upheld for the solver and cutoff part. Add a further refinement level or an adaptive solver with a stated tolerance, or soften the sentence to "not explained by the refinements tried". R3's strength stands for the separate point that the off-atom samples are not near unused dataset images. Obligation: `should_fix`.
- **Resolution Rationale**: On evidence, the manuscript (Appendix C.4, lines 2119 to 2124) reports exactly two integrator and cutoff settings (Euler with 50 steps at 1 − T = 10⁻³, and RK4 at 1 − T = 10⁻⁴). The off-atom fractions fall between them, for example from 0.298 to 0.254 at h = 6. It then concludes "therefore not a solver or cutoff artefact". On expertise, numerical convergence falls within R1's role, and R3 states "I do not assess the proofs or the training protocols".

**Disagreement 5 (SC-15): Is Theorem 5.1 a strength or close to an identity?**
- **EIC S5 (strength)**: the bound is "short and attained", and its data-prediction form gives practitioners a measurable quantity.
- **R1 W8 (Minor)**: when the scaled field tends to zero, the bound holds with equality and "carries no information beyond the endpoint itself". The contribution bullet still presents it as a mechanism by which learned fields "inherit collapse".
- **Disagreement type**: Perspective difference about framing. Neither seat disputes that the theorem is correct.
- **Editor's Resolution**: Both readings hold. R1's remedy is adopted as `should_fix`: move the Appendix C.4 caveat into Section 5, and state that the bound has content only when the scaled error is controlled independently of the endpoint, as Theorem C.3 does. This does not remove the EIC's strength.
- **Resolution Rationale**: The manuscript itself concedes in Appendix C.4: "this agreement is the identity of the theorem, not". It also states in Section 5: "The bound is attained". The disagreement is about how the result is presented, not whether it is correct. DA M5 is not counted and agrees with R1.

Arbitration note. The EIC seat ran blind to the peer reports (provenance: `peer_outputs_visible: false`), so it could not arbitrate these splits itself. The resolutions above are the synthesizer's, made only from content already on the cards and from the manuscript passages they cite. Where the EIC is a party (Disagreements 1 and 5), its card is quoted, not overruled by authority.

### Devil's Advocate findings (tracked separately from consensus)

The DA filed no CRITICAL findings. Its six MAJOR findings are listed below. Each is attached to the roadmap item that carries it.

| DA ID | DA argument (short) | Non-DA seats raising the same point | Roadmap item |
|---|---|---|---|
| M1 | The composite is motivated as an idealisation of coarse-label CFG, but the paper's own evidence (learned label averages, standard velocity CFM) does not support that bridge | R2 W1 (bridge asserted); EIC W2, R2 W2, R3 W1 (standard networks do not reproduce the basin) | REV-2, REV-20 |
| M2 | The successful networks get an oracle coordinate centred on the known tie | R2 W2 | REV-21 |
| M3 | The CIFAR-10 pair check uses a constructed configuration; the number of eligible pairs is not reported | R1 W1, R2 W4, R3 W1 | REV-11 |
| M4 | The only off-support endpoints are circumcentres of training atoms, so this is still memorisation of blends | EIC W1, W2 (significance and headline); R3 W6 (off-atom criterion does not separate blends) | REV-1 |
| M5 | The heading "inherit collapse unless scaled error persists" is close to a restatement and cannot be falsified as an empirical claim | R1 W8 | REV-18 |
| M6 | The abstract reports the synthetic agreement but omits the image-scale disagreement: slopes of 0.481 and −0.156 against 1, and 15 to 30% off-atom samples | R2 W3 (image-scale off-atom samples left unattributed); R3 W2 (16 to 25% off-atom) | REV-31 |

### Decision Rationale

The decision follows mechanically from the contract. Every dimension was scored warn by its eligible seats. These include four mandatory dimensions: D1 by R1, D2 by R2, D3 by both DA and R1, and D6 by the EIC. Condition F3, "two or more mandatory dimensions score 'warn' or worse" under a majority quantifier, therefore fires at severity 70 and sets `major_revision`. F5 (minor_revision) also fires but has lower severity. No block or fatal block was recorded, so F1 and F2 do not fire, and Reject was not available under this contract.

The cards agree on what the decision addresses. The formal core is not in question: R1 found no counterexample to any formal statement as stated, R2 found the domain content correct, and the DA found no theorem false as stated. The warns concern how far the prose carries the theorems, in four areas.

- **Practical relevance of the composition result (SC-2, CONSENSUS-3).** Standard trained networks do not reproduce the off-support basin. The networks that do receive a tie-centred input (R2 W2, DA M2), and the label-averaging bridge is asserted (R2 W1, DA M1).
- **Evidential role of the CIFAR-10 pair numerics (SC-8a, SC-8b).** They are not shown to be converged and they confirm an analytically guaranteed reduction (R1 W1, R2 W4).
- **Significance and positioning for an ICLR audience (SC-1, SC-3).** The paper lacks a headline consequence and gives a one-sentence novelty delta against Liu & Zuazua (EIC W1, W3; DA M4).
- **Local overstatements in the main text.** Proposition C.2(b) appears without its one-dimensional hypothesis, which R1 W2 shows is false in d ≥ 2. Section 4.4 claims that "sinks keep a positive fraction" although two Table 9 rows show zero. The abstract omits the image-scale disagreement (DA M6).

Minor Revision would understate this. Several items need re-analysis or new controls: solver sensitivity on all eight pairs, and a tie-agnostic input control. Others change how the central contribution is framed. Reject is not supported: no seat recorded a block, all seats credit the composition threshold as new and correct, and R3 judges that the weaknesses call "for reframing and a few targeted additions, not for new theory". Because all seats share one model family, the agreement above carries correlated-error risk and should not be read as independent confirmation.

### Blocking Issues (0 to 3, immutable source order)

| Transport ref | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---|---|---|---|---|
| R1 | No single ML headline; the conclusion restates the results without drawing implications (bears on D6) | EIC (W1); DA M4 not counted | text: Section 8 "The exact flow and its positive modifications end on training examples, guided label averaging can" | REV-1 |
| R2 | The one off-support mechanism is not realised by standard trained networks, and the paper does not draw the consequence (CONSENSUS-3) | EIC (W2), R2 (W2), R3 (W1); DA M1 not counted | text: Section 7 "off-atom basin depends on its parametrisation, chiefly on its input, and not in every seed" | REV-2 |
| R4 | CIFAR-10 composition numerics are not shown to be converged, yet are presented as confirmation (bears on D1) | R1 (W1) | text: Appendix E.3 "individual endpoints agree for at least 91% of sources up to w = 2wc but" / "only about half at w = 5wc, so we report fractions only." | REV-10 |

---

## Part 2: Revision Roadmap

### Step 1b: Weakness sub-claim inventory

Positions use the closed set raised, corroborated, not-mentioned or disputed. Every unlisted seat is not-mentioned. Severity and confidence are transported from each card's per-finding tags. The cards use "Major" and "Minor", rendered here as `major` and `minor`. The DA's tables carry the MAJOR band.

| sub_claim_id | parent_weakness | reviewer_id | position | evidence_pointer | severity | confidence |
|---|---|---|---|---|---|---|
| SC-1 | EIC W1 no ML headline | EIC | raised | text: Sec. 8 "The exact flow and its positive modifications end on training examples…" | major | 4 |
| SC-2 | EIC W2 standard nets do not realise the mechanism | EIC | raised | text: Sec. 7 "off-atom basin depends on its parametrisation…" | major | 4 |
| SC-2 | R2 W2 tie-centred input | R2 | corroborated | text: Sec. 6.2 "receives the blow-up coordinate asinh(tx/(1 − t)2) as an extra input" | major | 4 |
| SC-2 | R3 W1 practical meaning for CFG users | R3 | corroborated | text: §4.3 "it idealises classifier-free guidance applied to a network that resolves labels only" | major | 3 |
| SC-3 | EIC W3 novelty vs Liu & Zuazua | EIC | raised | text: Sec. 1 "we prove convergence of every trajectory and null non-atom basins without such a premise" | major | 3 |
| SC-4 | EIC W4 explanatory material in the appendix | EIC | raised | text: Sec. 4 "composition is where Step 2 fails (Figure 4)" | minor | 4 |
| SC-5 | EIC W5 hard-label averaging route | EIC | raised | text: Sec. 4.1 "sends every source to the midpoint. The null set in (b) cannot be removed" | minor | 4 |
| SC-6 | EIC W6 abstract ends on disclaimer | EIC | raised | text: Abstract "variance tracks the label-smoothing reference; these observations do not establish" | minor | 4 |
| SC-6 | R2 S6 calibrated abstract | R2 | disputed | text: Abstract "these observations do not establish" | — (strength) | — |
| SC-6 | R3 S3 learned evidence scoped honestly | R3 | disputed | text: Abstract "these observations do not establish" | — (strength) | — |
| SC-7a | EIC W7 narrow empirical scope (image: one mask, N = 2000) | EIC | raised | text: Sec. 7 "the learned experiments use five seeds, the learned composition d ≤ 2 and the synthetic problems" | minor | 3 |
| SC-7a | R2 W7 small-data regime | R2 | corroborated | text: Sec. 6.1 "At realistic capacity. A standard DDPM U-Net (35.75M parameters)" | minor | 3 |
| SC-7b | EIC W7 (learned composition d ≤ 2) | EIC | raised | text: Sec. 7 (as above) | minor | 3 |
| SC-7b | R1 W9 (all runs d ≤ 2) | R1 | corroborated | text: Sec. 6.2 "Of the changes the successful network makes, the input decides" | minor | 3 |
| SC-7b | R3 W1 (learned composition only d ≤ 2) | R3 | disputed (severity) | text: §4.3 (as above) | major | 3 |
| SC-7c | EIC W7 (instance and optimisation randomness confounded in image runs) | EIC | raised | text: Sec. 7 (as above) | minor | 3 |
| SC-8a | R1 W1 solver sensitivity on the first pair only | R1 | raised | text: App. E.3 "individual endpoints agree for at least 91% of sources up to w = 2wc but" | major | 4 |
| SC-8b | R1 W1 present as corollary / consistency check | R1 | raised | text: App. E.3 (as above) | major | 4 |
| SC-8b | R2 W4 exact CIFAR-10 composition confirms a reduction | R2 | disputed (severity) | text: Sec. 1 "The threshold holds unchanged on pairs of CIFAR-10 images" | minor | 4 |
| SC-8b | R3 W1 CIFAR pair evidence exact-field only | R3 | corroborated | text: §4.3 (as above) | major | 3 |
| SC-9 | R1 W2 Prop. C.2(b) stated without d = 1 | R1 | raised | text: Sec. 5 "a data-predicting one whose bounded prediction is C1 up to t = 1 ends" | minor | 5 |
| SC-10 | R1 W3 "sinks keep a positive fraction" vs zero rows | R1 | raised | text: Sec. 4.4 "put no source at z, and sinks keep a positive fraction (Table 9)." | minor | 5 |
| SC-11 | R1 W4 stated rate weaker than proved | R1 | raised | text: Sec. 4.2 "At a hard label, guidance thus weakens the guaranteed rate to (1 − t) log(1/(1 − t))" | minor | 5 |
| SC-12 | R1 W5 remark after Prop. C.2 mismatches hypothesis (b) | R1 | raised | text: App. C.2 "satisfies (b) once its output is clipped to a bounded range" | minor | 4 |
| SC-13 | R1 W6 two technical steps given as outlines | R1 | raised | text: App. B.6 / B.1 "This graph is C1 by the standard differentiability of the fixed" | minor | 4 |
| SC-14 | R1 W7 "not a solver or cutoff artefact" unsupported | R1 | raised | text: App. C.4 "remaining discrepancy is therefore not a solver or cutoff artefact." | minor | 4 |
| SC-14 | R3 S5 off-atom samples checked against full dataset | R3 | disputed | text: App. C.4 "Measured against all 50000 CIFAR-10 training images instead of the 2000" | — (strength) | — |
| SC-15 | R1 W8 Thm 5.1 close to an identity, framed as transfer | R1 | raised | text: Sec. 1 "Learned fields inherit collapse unless their scaled error persists" | minor | 4 |
| SC-15 | EIC S5 transfer bound tight and simple | EIC | disputed | text: Sec. 5 "The bound is attained: for ∆(x, t) = c/(1−t) both sides equal |c| from every x0." | — (strength) | — |
| SC-16 | R1 W9 "the input decides" runs ahead of seed-level data | R1 | raised | text: Sec. 6.2 "Of the changes the successful network makes, the input decides" | minor | 3 |
| SC-17 | R2 W1 label averaging as a model of coarse label resolution is asserted | R2 | raised | text: Sec. 1 "that resolves labels only coarsely averages the field over nearby labels" | major | 4 |
| SC-18 | R2 W2 reproducing networks receive a tie-centred input | R2 | raised | text: Sec. 6.2 "receives the blow-up coordinate asinh(tx/(1 − t)2) as an extra input" | major | 4 |
| SC-19a | R2 W3 off-atom U-Net samples unexplained; locality accounts not engaged | R2 | raised | text: App. C.4 "so it need not have the integrable global Lipschitz constant of Proposition C.2(a), and we do not" | major | 4 |
| SC-19b | R2 W3 guidance theorems silent on CFG-induced concentration of endpoint weights | R2 | raised | text: App. C.4 (as above) | major | 4 |
| SC-20 | R2 W5 missing compositional-generation and CFG-theory literature | R2 | raised | absence: Sec. 1 related work and reference list (checked Sec. 1, 4.2–4.3, 6.2, full reference list) | minor | 4 |
| SC-21 | R2 W6 memorisation references cited with narrower scope | R2 | raised | text: Sec. 1 "That the empirical minimiser memorises is well established" | minor | 4 |
| SC-22 | R3 W2 privacy implication not tied to extraction or membership | R3 | raised | text: Ethics "which is relevant when conditional models are trained on sensitive data" | minor | 4 |
| SC-23 | R3 W3 endpoint noise framed as a "remedy" | R3 | raised | text: App. D "a remedy must move the support" | minor | 4 |
| SC-24 | R3 W4 kernel reference read only at fixed N | R3 | raised | text: Prop. 3.6 "and this lower bound does not depend on h" | minor | 4 |
| SC-25 | R3 W5 endpoint-noise law is an uncited conditional KDE | R3 | raised | equation: Eq. (16), Prop. D.1 | minor | 4 |
| SC-26 | R3 W6 relative "off-atom" criterion does not separate blends | R3 | raised | dataset: CIFAR-10 on-atom criterion (App. E.2), ratio 1/9 | minor | 4 |

Dispositions over the four non-DA seats:
- **CONSENSUS-3**: SC-2 (R1 silent).
- **SPLIT**: SC-6, SC-7b, SC-8b, SC-14, SC-15. Each is arbitrated in Part 1.
- **Corroborated (2/4)**: SC-7a.
- **Single-reviewer (1/4)**: all other sub-claims.

DA MAJOR rows M1 to M6 are not counted. They are attached as co-sources in the roadmap below, except M6, which has no non-DA counterpart for the abstract-omission point and gets its own item.

Surface-form parity note: no sub-claim was down-weighted for informal wording or credited for technical phrasing. None was judged unevaluable.

### Revision Roadmap core (immutable source order; non-ranking)

`schema_version: revision-roadmap/1.0` (reviewer-owned core, rendered in prose). Order is by fixed seat order EIC, R1, R2, R3, DA, then finding ordinal, then sub-claim ordinal. Severity, obligation and cost play no part in the order. `proposed_targets[]`: `[BLOCK-MANIFEST-UNAVAILABLE]`. No block manifest was bound to this run, so no block IDs or operations are proposed, and none was invented. Author triage, display order and work order are deliberately absent. They belong to the separate author sidecar.

| Item | Source ref | Sub-claim(s) | Description | Severity | Evidence anchor | Confidence | Source | Obligation | Cost scope | Bounded consequence |
|---|---|---|---|---|---|---|---|---|---|---|
| REV-1 | EIC#1 | SC-1 | Lead with a headline and one consequence; replace the restating conclusion with a discussion of implications | major | text: Sec. 8 "The exact flow and its positive modifications end on training examples…" | 4 | EIC; DA M4 | must_fix | section: Abstract, Sec. 1 contributions, Sec. 8 | interpretive_ambiguity_remains → manuscript: Abstract/Sec. 8 |
| REV-2 | EIC#2 | SC-2 | State whether composition is a mechanism expected in practice or an existence/boundary result; draw the consequence of standard networks not reproducing it (optionally add one learned run beyond d ≤ 2) | major | text: Sec. 7 "off-atom basin depends on its parametrisation…" | 4 / 4 / 3 | EIC, R2, R3; DA M1 | must_fix | section: Sec. 4.3, 6.2, 7, 8 | claim_scope_unsupported → claim: practical relevance of Thms 4.6–4.7 |
| REV-3 | EIC#3 | SC-3 | Add an explicit comparison (setting, assumptions, conclusion) against the closest convergence results, with one example the prior criterion does not cover | major | text: Sec. 1 "we prove convergence of every trajectory and null non-atom basins without such a premise" | 3 | EIC | must_fix | section: Sec. 1 related work | evidence_gap_remains → claim: novelty of Thms 4.1, 4.5 |
| REV-4 | EIC#4 | SC-4 | Bring the two-step template figure into Sec. 4; consider moving most of Sec. 4.4 to the appendix | minor | text: Sec. 4 "composition is where Step 2 fails (Figure 4)" | 4 | EIC | should_fix | section: Sec. 4, 4.4 | reader_traceability_reduced → section: Sec. 4 |
| REV-5 | EIC#5 | SC-5 | Contrast the hard-label averaging route with the positive-bandwidth composition | minor | text: Sec. 4.1 "sends every source to the midpoint…" | 4 | EIC | should_fix | sentence: Abstract or Sec. 1 | interpretive_ambiguity_remains → claim: "composition breaks this" |
| REV-6 | EIC#6 | SC-6 | Keep the scoping statement visible; the author may shorten it and end on the takeaway | minor | text: Abstract "…these observations do not establish" | 4 | EIC (split with R2, R3) | consider | sentence: Abstract | editorial_conformance_unmet → section: Abstract |
| REV-7 | EIC#7.1 | SC-7a | Scope the image collapse result to N = 2000 and one mask; rename "At realistic capacity" or add a second mask or larger N | minor | text: Sec. 6.1 "At realistic capacity…" | 3 / 3 | EIC, R2 | should_fix | sentence: Sec. 6.1 heading (optional new_data: second mask or larger N) | claim_scope_unsupported → section: Sec. 6.1 |
| REV-8 | EIC#7.2 | SC-7b | Keep learned-composition conclusions scoped to d ≤ 2 wherever stated | minor (EIC, R1); major (R3) | text: Sec. 7 "…the learned composition d ≤ 2…" | 3 / 3 / 3 | EIC, R1, R3 (split) | should_fix | sentence: Sec. 6.2, 7 | claim_scope_unsupported → section: Sec. 6.2 |
| REV-9 | EIC#7.3 | SC-7c | Separate instance from optimisation seeds in at least one image setting, or keep the current wording | minor | text: Sec. 7 (as above) | 3 | EIC | consider | re_analysis: image experiments, Sec. 6.1 | method_reproducibility_unresolved → section: Sec. 6.1 |
| REV-10 | R1#1.1 | SC-8a | Run hand-off and tolerance sensitivity on all eight CIFAR-10 pairs at 1.1 w_c; report per-pair fractions with solver spread, or drop "every pair positive at 1.1 w_c" | major | text: App. E.3 "…only about half at w = 5wc, so we report fractions only." | 4 | R1 | must_fix | re_analysis: App. E.3 CIFAR-10 composition | evidence_gap_remains → claim: Sec. 6.2 CIFAR-10 threshold |
| REV-11 | R1#1.2 | SC-8b | State the CIFAR-10 threshold as a corollary of Thm 4.7 and Cor. B.9 with its hypotheses; present the computation as an exact-field consistency check; reword the Abstract and Sec. 1; report the pair-selection rate | major (R1, R3); minor (R2) | text: Sec. 1 "The threshold holds unchanged on pairs of CIFAR-10 images" | 4 / 4 / 3 | R1, R2, R3 (split); DA M3 | must_fix | section: Abstract, Sec. 1, Sec. 6.2, App. E.3 | claim_scope_unsupported → claim: "threshold holds on CIFAR-10" |
| REV-12 | R1#2 | SC-9 | Restore "in one dimension" for Prop. C.2(b) in Sec. 5, or add a non-recurrence hypothesis | minor | text: Sec. 5 "a data-predicting one whose bounded prediction is C1 up to t = 1 ends" | 5 | R1 | must_fix | sentence: Sec. 5 | claim_scope_unsupported → claim: Sec. 5 data-predicting endpoint statement |
| REV-13 | R1#3 | SC-10 | Qualify "sinks keep a positive fraction" (below 1/2048 for the d = 8 simplex at 1.1 and 2 w_c), or add a targeted sample near ξ = 0 | minor | text: Sec. 4.4 "…sinks keep a positive fraction (Table 9)." | 5 | R1 | should_fix | sentence: Sec. 4.4 (optional re_analysis: Table 9) | claim_scope_unsupported → table: Table 9 |
| REV-14 | R1#4 | SC-11 | State the proved sqrt-log rate and the (1 − t)^(1 − γ/2) rate | minor | text: Sec. 4.2 "…weakens the guaranteed rate to (1 − t) log(1/(1 − t))" | 5 | R1 | consider | sentence: Sec. 4.2 | reporting_requirement_unmet → section: Sec. 4.2 |
| REV-15 | R1#5 | SC-12 | Require C¹ activations and smooth squashing in the remark after Prop. C.2; say which networks meet (b) | minor | text: App. C.2 "…satisfies (b) once its output is clipped to a bounded range" | 4 | R1 | should_fix | sentence: App. C.2 remark | claim_scope_unsupported → claim: Prop. C.2(b) applicability |
| REV-16 | R1#6 | SC-13 | Give precise citations or short proofs for the C¹ Lyapunov–Perron graph (Lemma B.8) and the Carathéodory facts (Lemma B.3) | minor | text: App. B.6 "This graph is C1 by the standard differentiability of the fixed" | 4 | R1 | consider | section: App. B.1, B.6 | evidence_gap_remains → section: App. B.6 |
| REV-17 | R1#7 | SC-14 | Add a refinement level or an adaptive solver, or soften to "not explained by the refinements tried" | minor | text: App. C.4 "remaining discrepancy is therefore not a solver or cutoff artefact." | 4 | R1 (split with R3) | should_fix | sentence: App. C.4 (optional re_analysis) | claim_scope_unsupported → claim: App. C.4 solver conclusion |
| REV-18 | R1#8 | SC-15 | Move the App. C.4 identity caveat into Sec. 5; state that the bound has content only under independent control of the scaled error (cf. Thm C.3); revise the contribution bullet | minor | text: Sec. 1 "Learned fields inherit collapse unless their scaled error persists" | 4 | R1 (split with EIC); DA M5 | should_fix | section: Sec. 1 bullet, Sec. 5 | interpretive_ambiguity_remains → claim: Thm 5.1 framing |
| REV-19 | R1#9 | SC-16 | Phrase "the input decides" as necessity within the tested architectures and d ≤ 2; report per-seed outcomes in the main text | minor | text: Sec. 6.2 "Of the changes the successful network makes, the input decides" | 3 | R1 | should_fix | sentence: Sec. 6.2 | claim_scope_unsupported → claim: Sec. 6.2 attribution |
| REV-20 | R2#1 | SC-17 | Present label averaging as a hypothesis; test it (e.g. a bottlenecked label embedding compared with v_φ and the mixed-prior field) or cite evidence for it | major | text: Sec. 1 "that resolves labels only coarsely averages the field over nearby labels" | 4 | R2; DA M1 | must_fix | section: Sec. 1, 4.3 (optional new_data) | claim_scope_unsupported → claim: coarse label resolution = label averaging |
| REV-21 | R2#2 | SC-18 | State in Sec. 6.2 and the Abstract that the input is centred at the known tie; add a tie-agnostic control | major | text: Sec. 6.2 "receives the blow-up coordinate asinh(tx/(1 − t)2) as an extra input" | 4 | R2; DA M2 | must_fix | new_data: tie-agnostic input control, Sec. 6.2 / App. E.3 | claim_scope_unsupported → claim: Abstract "trained networks reproduce the off-atom basin only when…" |
| REV-22 | R2#3.1 | SC-19a | Set the U-Net off-atom fractions at h = 4–6 against locality and inductive-bias explanations (e.g. a patch-composite check) | major | text: App. C.4 "…and we do not" | 4 | R2 | must_fix | section: App. C.4, Sec. 6.1 (optional re_analysis) | evidence_gap_remains → dataset: CIFAR-10 U-Net off-atom samples |
| REV-23 | R2#3.2 | SC-19b | Say that the guidance theorems are silent on how strongly CFG induces memorisation; if possible, quantify how w changes the endpoint weights q̃ | major | text: App. C.4 (as above) | 4 | R2 | should_fix | sentence: Sec. 4.2 (optional re_analysis) | interpretive_ambiguity_remains → claim: guidance results vs CFG-induced memorisation |
| REV-24 | R2#5 | SC-20 | Add the compositional-generation, CFG-theory, memorisation-timing and replication strands to the related work | minor | absence: Sec. 1 related work and reference list | 4 | R2 | should_fix | section: Sec. 1 related work | evidence_gap_remains → section: Sec. 1 |
| REV-25 | R2#6 | SC-21 | Split the citations into memorisation by the empirical optimum and departure from it | minor | text: Sec. 1 "That the empirical minimiser memorises is well established" | 4 | R2 | should_fix | sentence: Sec. 1 | interpretive_ambiguity_remains → section: Sec. 1 |
| REV-26 | R3#2 | SC-22 | Narrow the Ethics statement; say that extraction and membership advantage are not measured | minor | text: Ethics "which is relevant when conditional models are trained on sensitive data" | 4 | R3 | should_fix | sentence: Ethics Statement | claim_scope_unsupported → section: Ethics Statement |
| REV-27 | R3#3 | SC-23 | Replace "remedy" with neutral wording; note that repeated sampling recovers the atom unless ρ is calibrated | minor | text: App. D "a remedy must move the support" | 4 | R3 | should_fix | sentence: App. D, Table 1 | interpretive_ambiguity_remains → claim: endpoint noise as remedy |
| REV-28 | R3#4 | SC-24 | Report the value of the lower bound (4) for EXP-1 and CIFAR-10; relate it to large-N Nadaraya–Watson consistency | minor | text: Prop. 3.6 "and this lower bound does not depend on h" | 4 | R3 | consider | section: Sec. 3, Prop. 3.6 | interpretive_ambiguity_remains → claim: Prop. 3.6 magnitude |
| REV-29 | R3#5 | SC-25 | Identify Eq. (16) as a conditional KDE and cite that literature | minor | equation: Eq. (16), Prop. D.1 | 4 | R3 | consider | sentence: after Prop. D.1 | reader_traceability_reduced → section: App. D |
| REV-30 | R3#6 | SC-26 | For off-atom samples, report distance to the best convex combination of the nearest training images or to x̄_h(y) | minor | dataset: CIFAR-10 on-atom criterion (App. E.2) | 4 | R3 | should_fix | re_analysis: App. E.2 / Sec. 6.1 | evidence_gap_remains → dataset: CIFAR-10 off-atom samples |
| REV-31 | DA#M6 | — | Report the image-scale disagreement in the abstract alongside the synthetic agreement: slopes of 0.481 and −0.156 against 1, and 15–30% off-atom at h = 4–6 | major | text: Abstract "on the synthetic problem their finite-cutoff"; App. C.4 "remaining discrepancy is therefore not a solver or cutoff artefact" | 4 | DA | must_fix | sentence: Abstract | claim_scope_unsupported → section: Abstract |

### Required Revisions (Must Fix)

> **Ordinal contract (#576/#670):** `R<n>` follows immutable roadmap source order filtered to `obligation_class == must_fix`. Author-selected display order and triage play no part. `R<n>` is a transport reference, not a rank.

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|---|---|---|---|---|---|---|---|---|
| R1 | REV-1 headline and implications | SC-1 | major | text: Sec. 8 "The exact flow and its positive modifications end on training examples…" | 4 — AC experience judging framing | EIC (DA M4) | must_fix | section: Abstract, Sec. 1, Sec. 8 | interpretive_ambiguity_remains → manuscript |
| R2 | REV-2 consequence of standard networks not reproducing the basin | SC-2 | major | text: Sec. 7 "off-atom basin depends on its parametrisation…" | 4 / 4 / 3 | EIC, R2, R3 (DA M1) | must_fix | section: Sec. 4.3, 6.2, 7, 8 | claim_scope_unsupported → claim |
| R3 | REV-3 novelty comparison | SC-3 | major | text: Sec. 1 "we prove convergence of every trajectory…" | 3 — did not re-read the cited theorems | EIC | must_fix | section: Sec. 1 related work | evidence_gap_remains → claim |
| R4 | REV-10 CIFAR-10 solver sensitivity | SC-8a | major | text: App. E.3 "…only about half at w = 5wc…" | 4 — stiff non-autonomous ODEs | R1 | must_fix | re_analysis: App. E.3 | evidence_gap_remains → claim |
| R5 | REV-11 CIFAR-10 threshold as corollary and rescoped claim | SC-8b | major (R1, R3); minor (R2) | text: Sec. 1 "The threshold holds unchanged on pairs of CIFAR-10 images" | 4 / 4 / 3 | R1, R2, R3 (DA M3) | must_fix | section: Abstract, Sec. 1, 6.2, App. E.3 | claim_scope_unsupported → claim |
| R6 | REV-12 restore d = 1 in Prop. C.2(b) paraphrase | SC-9 | minor | text: Sec. 5 "a data-predicting one whose bounded prediction is C1 up to t = 1 ends" | 5 — asymptotically autonomous ODEs | R1 | must_fix | sentence: Sec. 5 | claim_scope_unsupported → claim |
| R7 | REV-20 label-averaging bridge | SC-17 | major | text: Sec. 1 "that resolves labels only coarsely averages the field over nearby labels" | 4 — empirical-optimal fields | R2 (DA M1) | must_fix | section: Sec. 1, 4.3 | claim_scope_unsupported → claim |
| R8 | REV-21 tie-centred input disclosure and control | SC-18 | major | text: Sec. 6.2 "receives the blow-up coordinate…" | 4 — core expertise | R2 (DA M2) | must_fix | new_data: Sec. 6.2 / App. E.3 | claim_scope_unsupported → claim |
| R9 | REV-22 unexplained U-Net off-atom samples | SC-19a | major | text: App. C.4 "…and we do not" | 4 — image-scale memorisation | R2 | must_fix | section: App. C.4, Sec. 6.1 | evidence_gap_remains → dataset |
| R10 | REV-31 abstract omits the image-scale disagreement | — | major | text: Abstract "on the synthetic problem their finite-cutoff" | 4 — Sec. 6.1, Table 7, App. C.4 compared | DA | must_fix | sentence: Abstract | claim_scope_unsupported → section |

### Required Item Details

**R1: Give the paper an ML headline and a discussion of implications**
- **Problem**: The abstract, contribution bullets and conclusion list qualified results without stating what an ICLR reader should take away about generalisation (EIC W1). The DA's M4 adds that the only off-support endpoints are blends of training atoms.
- **Source**: EIC W1, "None of them says what an ICLR reader should take away about generalisation in practice."
- **Requirement**: Open the abstract with a two-sentence headline and one consequence. Move qualifiers into the theorem statements. Replace the conclusion with a short discussion: implications for CFG and label-noise practice, for the memorisation debate, and the open questions.
- **Acceptance criteria**: The abstract and Section 8 each state one explicit consequence for practice or for the memorisation debate, and Section 8 contains a discussion of implications rather than a restatement of results.

**R2: Draw the consequence of standard trained networks not realising the composition basin**
- **Problem**: Standard velocity CFM networks place essentially no mass at the midpoint. The paper reports this but does not say whether the composition result is a mechanism expected in practice or an existence result marking the boundary of the positive theorems (EIC W2, R2 W2, R3 W1; CONSENSUS-3).
- **Source**: EIC W2, R2 W2 ("Report standard-CFM failure as a finding in its own right"), R3 W1; DA M1.
- **Requirement**: Pick one reading and argue it in Sections 4.3, 6.2 and 8. State that standard velocity networks did not reproduce the basin. Link this to Proposition C.2, and say which deployed parametrisations, if any, meet the resolution condition. A learned run beyond d ≤ 2, for example on the CIFAR-10 pairs, is optional. If it is not run, say so.
- **Acceptance criteria**: Section 4.3 or Section 8 states explicitly whether the composition result is a practical mechanism or an existence/boundary result, and Section 6.2 states the standard-network non-reproduction as a finding.

**R3: Make the novelty delta against the closest convergence theorems explicit**
- **Problem**: The advantage of Theorems 4.1 and 4.5 over Liu & Zuazua (2025, 2026) is stated in one clause (EIC W3).
- **Source**: EIC W3, "This delta is the main originality claim for half of the paper, but it appears as a single clause".
- **Requirement**: Add a comparison table or paragraph giving, for each closest prior result, its setting, assumptions and conclusion. Give one configuration the prior criterion does not cover and the present theorems do (EIC question 3).
- **Acceptance criteria**: The related work contains a per-result comparison of setting, assumptions and conclusion, plus at least one named configuration covered here and not by the prior criterion.

**R4: Establish solver robustness of the CIFAR-10 composition fractions**
- **Problem**: Solver sensitivity was checked on the first pair only. Midpoint fractions change by up to 0.03 under a change of hand-off or tolerance, while the claim that every pair is positive at 1.1 w_c rests on fractions as low as 0.006 (R1 W1).
- **Source**: R1 W1, "the computation does not establish the specific numerical statement in Section 6.2 and the abstract … beyond numerical error."
- **Requirement**: Run the hand-off and tolerance sensitivity on all eight pairs at 1.1 w_c. Report per-pair fractions with their solver spread, or remove the claim that every pair is positive at 1.1 w_c.
- **Acceptance criteria**: Appendix E.3 reports per-pair 1.1 w_c fractions with solver spread for all eight pairs, or the "every pair positive at 1.1 w_c" claim no longer appears.

**R5: State the CIFAR-10 threshold as a corollary and rescope the claim**
- **Problem**: Under the selected-pair construction the threshold is guaranteed analytically, yet the abstract and Section 1 present the check as confirmation "on pairs of CIFAR-10 images". The pair-selection rate is not reported (R1 W1, R2 W4, R3 W1; DA M3).
- **Source**: R1 W1 ("State the CIFAR-10 threshold as a corollary of Theorem 4.7 and Corollary B.9"), R2 W4 ("Reword the abstract and Section 1… report the pair-selection rate").
- **Requirement**: Derive the CIFAR-10 pair threshold as a corollary with its hypotheses: the nearest-atom condition at z and strictly positive label weights. Call the computation an exact-field consistency check on selected, isolated pairs, in both the Abstract and Section 1. Report how many pairs were eligible out of all pairs.
- **Acceptance criteria**: A stated corollary covers the CIFAR-10 pairs, the Abstract and Section 1 describe the check as an exact-field consistency check on selected pairs, and the pair-selection rate is reported.

**R6: Restore the one-dimensional hypothesis of Proposition C.2(b) in Section 5**
- **Problem**: Section 5 states Proposition C.2(b) without "d = 1". In that generality it is false for d ≥ 2: an attracting limit cycle of g(x) − x gives an open set of non-converging initial points (R1 W2).
- **Source**: R1 W2, "In d >= 2 this fails."
- **Requirement**: Restore "in one dimension". If a d-dimensional version is wanted, add a hypothesis that excludes recurrence.
- **Acceptance criteria**: The Section 5 sentence carries the d = 1 hypothesis or an explicit non-recurrence hypothesis.

**R7: Support or reframe the label-averaging model of coarse label resolution**
- **Problem**: The introduction asserts, without citation or direct evidence, that a network resolving labels coarsely averages the field over nearby labels. The paper's own pilot (Table 8) shows that learned label averages need not follow the exact ones (R2 W1; DA M1).
- **Source**: R2 W1, "It has no citation and no direct evidence."
- **Requirement**: Present the averaging model as a hypothesis, and either test it (for example with a bottlenecked label embedding compared against v_φ and the mixed-prior field) or cite empirical evidence for this form.
- **Acceptance criteria**: Section 1 and Section 4.3 present label averaging as a hypothesis, and either a direct test or a supporting citation is added.

**R8: Disclose and control for the tie-centred input**
- **Problem**: The extra input asinh(tx/(1 − t)²) is centred at the known tie z = 0. The main text and abstract do not say that building it requires knowing z (R2 W2; DA M2).
- **Source**: R2 W2, "They do not say that building it requires knowing z".
- **Requirement**: State in Section 6.2 and the Abstract that the input is centred at the known tie. Add a tie-agnostic control, such as a 1/(1 − t)² input applied to all coordinates without centring, or a learned rescaling. Answer whether the input is tie-centred in the triangle runs too (R2 question 1).
- **Acceptance criteria**: The Abstract and Section 6.2 state that the input is tie-centred, and results for at least one tie-agnostic input control are reported.

**R9: Engage the unexplained U-Net off-atom samples**
- **Problem**: At h = 4–6, the CIFAR-10 U-Net produces 0.16–0.30 off-atom samples while the exact field produces none. The paper declines to attribute this and does not engage locality or inductive-bias accounts (R2 W3).
- **Source**: R2 W3, "The paper explicitly declines to attribute these samples."
- **Requirement**: Add a paragraph that sets the measured off-atom fractions against the locality and inductive-bias explanation, for example by checking whether the off-atom completions are patch-wise composites of training images (R2 question 3).
- **Acceptance criteria**: Appendix C.4 or Section 6.1 discusses the off-atom U-Net samples against at least one cited explanation of how trained networks depart from the empirical optimum, with a reported check or an explicit statement that it is untested.

**R10: Report the image-scale disagreement in the abstract**
- **Problem**: The abstract reports synthetic agreement with the label-smoothing reference but omits the image-scale disagreement (DA M6). That disagreement is log-log slopes of 0.481 and −0.156 against an exact value of 1, and 15–30% off-atom samples at h = 4–6 against none for the exact field.
- **Source**: DA M6, "The abstract's summary of learned-field agreement is therefore more favourable than the evidence."
- **Requirement**: Add one clause to the abstract stating that image-scale learned fields depart from the exact reference, or remove the selective synthetic-agreement summary.
- **Acceptance criteria**: The abstract either mentions the image-scale departure from the exact reference or no longer summarises learned-field agreement selectively.

### Suggested Revisions (Should Fix / Consider)

S refs follow the same immutable source order, filtered to `should_fix` and `consider`.

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source | Obligation class | Cost scope | Bounded consequence |
|---|---|---|---|---|---|---|---|---|---|
| S1 | REV-4 appendix material into Sec. 4 | SC-4 | minor | text: Sec. 4 "composition is where Step 2 fails (Figure 4)" | 4 | EIC | should_fix | section: Sec. 4 | reader_traceability_reduced → section |
| S2 | REV-5 hard-label vs composition contrast | SC-5 | minor | text: Sec. 4.1 "sends every source to the midpoint…" | 4 | EIC | should_fix | sentence: Abstract/Sec. 1 | interpretive_ambiguity_remains → claim |
| S3 | REV-6 abstract disclaimer placement | SC-6 | minor | text: Abstract "…these observations do not establish" | 4 | EIC (split) | consider | sentence: Abstract | editorial_conformance_unmet → section |
| S4 | REV-7 image scope N = 2000 / one mask | SC-7a | minor | text: Sec. 6.1 "At realistic capacity…" | 3 / 3 | EIC, R2 | should_fix | sentence: Sec. 6.1 | claim_scope_unsupported → section |
| S5 | REV-8 learned composition scoped to d ≤ 2 | SC-7b | minor (EIC, R1); major (R3) | text: Sec. 7 "…the learned composition d ≤ 2…" | 3 / 3 / 3 | EIC, R1, R3 (split) | should_fix | sentence: Sec. 6.2, 7 | claim_scope_unsupported → section |
| S6 | REV-9 instance vs optimisation seeds | SC-7c | minor | text: Sec. 7 (as above) | 3 | EIC | consider | re_analysis: Sec. 6.1 | method_reproducibility_unresolved → section |
| S7 | REV-13 sinks with zero detected fraction | SC-10 | minor | text: Sec. 4.4 "…sinks keep a positive fraction (Table 9)." | 5 | R1 | should_fix | sentence: Sec. 4.4 | claim_scope_unsupported → table |
| S8 | REV-14 sharper proved rates | SC-11 | minor | text: Sec. 4.2 "…weakens the guaranteed rate…" | 5 | R1 | consider | sentence: Sec. 4.2 | reporting_requirement_unmet → section |
| S9 | REV-15 remark hypotheses after Prop. C.2 | SC-12 | minor | text: App. C.2 "…once its output is clipped to a bounded range" | 4 | R1 | should_fix | sentence: App. C.2 | claim_scope_unsupported → claim |
| S10 | REV-16 citations or proofs for outlined steps | SC-13 | minor | text: App. B.6 "This graph is C1 by the standard differentiability of the fixed" | 4 | R1 | consider | section: App. B.1, B.6 | evidence_gap_remains → section |
| S11 | REV-17 solver-artefact conclusion in App. C.4 | SC-14 | minor | text: App. C.4 "…therefore not a solver or cutoff artefact." | 4 | R1 (split) | should_fix | sentence: App. C.4 | claim_scope_unsupported → claim |
| S12 | REV-18 framing of Thm 5.1 | SC-15 | minor | text: Sec. 1 "Learned fields inherit collapse unless their scaled error persists" | 4 | R1 (split; DA M5) | should_fix | section: Sec. 1, Sec. 5 | interpretive_ambiguity_remains → claim |
| S13 | REV-19 "the input decides" | SC-16 | minor | text: Sec. 6.2 "…the input decides" | 3 | R1 | should_fix | sentence: Sec. 6.2 | claim_scope_unsupported → claim |
| S14 | REV-23 CFG endpoint-weight concentration | SC-19b | major | text: App. C.4 "…and we do not" | 4 | R2 | should_fix | sentence: Sec. 4.2 | interpretive_ambiguity_remains → claim |
| S15 | REV-24 missing literature strands | SC-20 | minor | absence: Sec. 1 related work and reference list | 4 | R2 | should_fix | section: Sec. 1 | evidence_gap_remains → section |
| S16 | REV-25 citation scope of memorisation refs | SC-21 | minor | text: Sec. 1 "That the empirical minimiser memorises is well established" | 4 | R2 | should_fix | sentence: Sec. 1 | interpretive_ambiguity_remains → section |
| S17 | REV-26 Ethics privacy statement | SC-22 | minor | text: Ethics "…trained on sensitive data" | 4 | R3 | should_fix | sentence: Ethics | claim_scope_unsupported → section |
| S18 | REV-27 "remedy" wording for endpoint noise | SC-23 | minor | text: App. D "a remedy must move the support" | 4 | R3 | should_fix | sentence: App. D, Table 1 | interpretive_ambiguity_remains → claim |
| S19 | REV-28 magnitude of the lower bound (4); large-N view | SC-24 | minor | text: Prop. 3.6 "and this lower bound does not depend on h" | 4 | R3 | consider | section: Sec. 3 | interpretive_ambiguity_remains → claim |
| S20 | REV-29 name Eq. (16) as a conditional KDE | SC-25 | minor | equation: Eq. (16), Prop. D.1 | 4 | R3 | consider | sentence: App. D | reader_traceability_reduced → section |
| S21 | REV-30 blends vs novel off-atom samples | SC-26 | minor | dataset: CIFAR-10 on-atom criterion (App. E.2) | 4 | R3 | should_fix | re_analysis: App. E.2 | evidence_gap_remains → dataset |

Severity, confidence and evidence anchors on every row are transported from the cards. No fallback tags were needed.

### Source-Traceability Checklist

> Source order is preserved and no work order is implied. Author triage (`will_address`, `wont_address`, `not_on_point`) is collected later in a separate sidecar.

- [ ] R1 — obligation `must_fix`: headline and discussion of implications (REV-1)
- [ ] R2 — obligation `must_fix`: consequence of standard networks not reproducing the basin (REV-2)
- [ ] R3 — obligation `must_fix`: explicit novelty comparison against the closest convergence theorems (REV-3)
- [ ] S1 — obligation `should_fix`: appendix material into Section 4 (REV-4)
- [ ] S2 — obligation `should_fix`: hard-label vs composition contrast (REV-5)
- [ ] S3 — obligation `consider`: abstract disclaimer placement (REV-6)
- [ ] S4 — obligation `should_fix`: image scope N = 2000 / one mask (REV-7)
- [ ] S5 — obligation `should_fix`: learned composition scoped to d ≤ 2 (REV-8)
- [ ] S6 — obligation `consider`: instance vs optimisation seeds (REV-9)
- [ ] R4 — obligation `must_fix`: CIFAR-10 solver sensitivity on all pairs (REV-10)
- [ ] R5 — obligation `must_fix`: CIFAR-10 threshold as corollary; rescope; selection rate (REV-11)
- [ ] R6 — obligation `must_fix`: restore d = 1 in Section 5 (REV-12)
- [ ] S7 — obligation `should_fix`: sinks with zero detected fraction (REV-13)
- [ ] S8 — obligation `consider`: sharper proved rates (REV-14)
- [ ] S9 — obligation `should_fix`: remark hypotheses after Prop. C.2 (REV-15)
- [ ] S10 — obligation `consider`: citations or proofs for outlined steps (REV-16)
- [ ] S11 — obligation `should_fix`: solver-artefact conclusion in App. C.4 (REV-17)
- [ ] S12 — obligation `should_fix`: framing of Theorem 5.1 (REV-18)
- [ ] S13 — obligation `should_fix`: "the input decides" (REV-19)
- [ ] R7 — obligation `must_fix`: label-averaging bridge (REV-20)
- [ ] R8 — obligation `must_fix`: tie-centred input disclosure and control (REV-21)
- [ ] R9 — obligation `must_fix`: unexplained U-Net off-atom samples (REV-22)
- [ ] S14 — obligation `should_fix`: CFG endpoint-weight concentration (REV-23)
- [ ] S15 — obligation `should_fix`: missing literature strands (REV-24)
- [ ] S16 — obligation `should_fix`: scope of memorisation citations (REV-25)
- [ ] S17 — obligation `should_fix`: Ethics privacy statement (REV-26)
- [ ] S18 — obligation `should_fix`: "remedy" wording (REV-27)
- [ ] S19 — obligation `consider`: magnitude of the lower bound (4) (REV-28)
- [ ] S20 — obligation `consider`: conditional KDE naming (REV-29)
- [ ] S21 — obligation `should_fix`: blends vs novel off-atom samples (REV-30)
- [ ] R10 — obligation `must_fix`: image-scale disagreement in the abstract (REV-31)

### Journal-Supplied Deadline (Optional Transport)

- **Exact deadline from source letter**: `NOT PROVIDED`. No deadline, duration or work estimate is inferred.

### Response Letter Instructions

Please respond item by item using `templates/revision_response_template.md`. Include:
1. a response and revision description for each Required Revision R1–R10;
2. a response for each Suggested Revision S1–S21, adopted or with the reason for not adopting it;
3. change markup in the revised manuscript;
4. a cross-reference table of new page and paragraph locations.

Each DA MAJOR finding (M1–M6) should be acknowledged in the response under the roadmap item it is attached to.

### Closing

We encourage you to consider the reviewers' comments carefully and submit a substantially revised manuscript. The revised manuscript will undergo another round of review. The reviewers agree that the exact composition threshold is new and correctly proved, and the revision should keep that result at the centre while scoping the learned-network and image-scale claims to what the evidence shows.

---

## Part 3: Reviewer Report Summary (Appendix)

### Journal-Fit Review Report Summary (EIC)
- Recommendation: Major Revision (overall signal) | Confidence: per-finding, 3–4
- Key point: the theory is careful and falsifiable but the paper lacks an ML headline, does not draw the consequence of the mechanism's absence in standard networks, and argues the novelty delta in one sentence. D5 warn, D6 warn.

### Reviewer 1 (Methodology) Summary
- Recommendation: not stated as an enum (D1 warn, D3 warn) | Confidence: per-finding, 3–5
- Key point: the proofs check, with no counterexample to any formal statement. The one Major finding is the unconverged CIFAR-10 composition numerics. Minor findings are main-text paraphrases that overstate the results (Prop. C.2(b) without d = 1; sinks with zero detected fraction) or understate them (guidance rates). Arithmetic receipts AR1–AR4 on Table 9 are all consistent.

### Reviewer 2 (Domain) Summary
- Recommendation: not stated as an enum (D2 warn) | Confidence: per-finding, 3–4
- Key point: the domain content is correct and the composition result is new. Its bearing on real samplers is not shown: the label-averaging bridge is asserted, the reproducing networks get a tie-centred input, the U-Net off-atom samples are unexplained, and some literature is missing.

### Reviewer 3 (Perspective) Summary
- Recommendation: not stated as an enum (D4 warn; "reframing and a few targeted additions, not for new theory") | Confidence: per-finding, 3–4
- Key point: the statistical framing is unusually legible. The cross-field implications (privacy, endpoint noise as a "remedy", fixed-N kernel reading, the off-atom criterion) need narrowing or support.

### Devil's Advocate Summary
- Recommendation: N/A, findings only
- Key challenge: no unresolved Critical challenge. The DA filed no CRITICAL findings and six MAJOR ones. The strongest is that the off-support mechanism yields only blends of training atoms, and its reproduction in trained networks depends on an oracle coordinate built from the theorem (M2, M4). D3 warn.

## Attachment: Suggested-Reference Check (advisory, #1001)

Suggested-reference check (script output, not a reviewer finding; #1001)
Seats read: R2, R3 (complete).

| Seat | # | Reference | Result |
|---|---|---|---|
| R2 | 1 | Liu, N. et al. (2022) "Compositional Visual Generation with Composable Diffusion Models" | Found in an index |
| R2 | 2 | Du, Y. et al. (2023) "Reduce, Reuse, Recycle: Compositional Generation with Energy-Based Diffusion Models and MCMC" | Found in an index |
| R2 | 3 | Wu, Y. et al. (2024) "Theoretical Insights for Diffusion Guidance: A Case Study for Gaussian Mixture Models" | Found in an index |
| R2 | 4 | Bradley, A. et al. (2024) "Classifier-Free Guidance is a Predictor-Corrector" | Found in an index |
| R2 | 5 | Bonnaire, T. et al. (2025) "Why Diffusion Models Don't Memorize: The Role of Implicit Dynamical Regularization in Training" | Title not matched; no DOI or arXiv ID to check |
| R2 | 6 | Somepalli, G. et al. (2023) "Understanding and Mitigating Copying in Diffusion Models" | Found in an index |
| R2 | 7 | Wen, Y. et al. (2024) "Detecting, Explaining, and Mitigating Memorization in Diffusion Models" | Found in an index |
| R3 | 1 | Stone, C. J. (1977) "Consistent Nonparametric Regression" | Found in an index |
| R3 | 2 | Rosenblatt, M. (1969) "Conditional probability density and regression estimators" | Title not matched; no DOI or arXiv ID to check |
| R3 | 3 | Hyndman, R. J. et al. (1996) "Estimating and Visualizing Conditional Densities" | Found in an index |
| R3 | 4 | Hall, P. et al. (2004) "Cross-Validation and the Estimation of Conditional Probability Densities" | Found in an index |
| R3 | 5 | Graf, S. et al. (2000) "Foundations of Quantization for Probability Distributions" | Found in an index |
| R3 | 6 | Dwork, C. et al. (2006) "Calibrating Noise to Sensitivity in Private Data Analysis" | Found in an index |
| R3 | 7 | Shokri, R. et al. (2017) "Membership Inference Attacks Against Machine Learning Models" | Found in an index |

"Found" means an index holds a record with this DOI or arXiv ID and title, or with this title. It does not show that the work supports the recommendation, or that the authors and year are right.

## Attachment: Reviewer Claim Check (advisory, #1002)

The judge answered 35 of 35 findings from 5 reviewers: it marked 1 as contradicted, and 2 cannot be checked from the manuscript alone.

The judge marked these findings as contradicted by the manuscript. The script checked only the words of each quote: that they occur in the manuscript, or, for words the finding quotes, that they do not. The judge gave the locations, and the script did not check them. Read each quote to decide:
- Reviewer 2 � W5: Missing literature on compositional generation and theoretical analyses of CFG
  > �Kang Liu and Enrique Zuazua. Geometric asymptotics of score mixing and guidance in diffusion models.� (References; cited in Section 1, Related work)

The judge also marked Devil's Advocate � M4, Reviewer 2 � W3 as false, but its quote did not pass the check, so they are not shown as contradicted.

The author decides what to do with each row. This check does not change the decision, the consensus counts, or the Revision Roadmap. The judge is the session model; as this judge, the #1002 contrast test passed Claude Opus 5.5 and Claude Fable 5.1 (gpt-6-astra and Gemini 4 Argon passed it in part one, through other transports); other models are untested.

## Attachment: Acronym Check (advisory, #849)

### Acronym check (advisory; no reply needed)
Coverage: body (partial)
Not in this input: English abstract, Chinese abstract.
Not checked:
- Body, line 569: PLa (the initials before its parentheses do not spell it)
- Body, line 1125: ICML (the initials before its parentheses do not spell it)
- Body, line 3584: ZT (the initials before its parentheses do not spell it)
- Body, line 3586: YT (the initials before its parentheses do not spell it)
- Body, line 3637: LawU (the initials before its parentheses do not spell it)
- Body, line 3640: LawV (the initials before its parentheses do not spell it)
- Body, line 3644: LawYT (the initials before its parentheses do not spell it)
- Body, line 4520: ROS2 (the initials before its parentheses do not spell it)

| Scope | Line | Rule | Acronym | Uses |
|---|---|---|---|---|
| Body | 1 | Defined after first use | ICLR | 56 |
| Body | 3 | Not defined | AND | 5 |
| Body | 3 | Not defined | ATOMIC | 1 |
| Body | 3 | Not defined | GUIDED | 1 |
| Body | 3 | Not defined | OF | 3 |
| Body | 6 | Not defined | FLOWS | 1 |
| Body | 55 | Not defined | CIFAR | 19 |
| Body | 59 | Not defined | MLP | 8 |
| Body | 220 | Not defined | SETUP | 1 |
| Body | 261 | Not defined | EXACT | 3 |
| Body | 261 | Not defined | THE | 6 |
| Body | 277 | Not defined | ODE | 2 |
| Body | 353 | Not defined | FIELDS | 4 |
| Body | 353 | Not defined | ON | 1 |
| Body | 362 | Not defined | PN | 15 |
| Body | 402 | Not defined | ATOMS | 3 |
| Body | 402 | Not defined | FIELD | 1 |
| Body | 402 | Not defined | KEEP | 1 |
| Body | 451 | Not defined | KEEPS | 1 |
| Body | 507 | Not defined | CAN | 3 |
| Body | 507 | Not defined | LEAVE | 1 |
| Body | 507 | Not defined | TWO | 2 |
| Body | 558 | Not defined | ANY | 1 |
| Body | 558 | Not defined | IN | 2 |
| Body | 569 | Not defined | DLM | 1 |
| Body | 573 | Not defined | PL | 40 |
| Body | 592 | Not defined | PLS | 3 |
| Body | 592 | Not defined | PLz | 10 |
| Body | 616 | Not defined | FROM | 1 |
| Body | 616 | Not defined | TO | 1 |
| Body | 668 | Not defined | EXP | 25 |
| Body | 677 | Not defined | RK4 | 9 |
| Body | 725 | Not defined | MNIST | 3 |
| Body | 729 | Not defined | DDPM | 3 |
| Body | 752 | Not defined | TIES | 1 |
| Body | 776 | Not defined | CFM | 9 |
| Body | 885 | Not defined | ETHICS | 1 |
| Body | 902 | Not defined | LARGE | 1 |
| Body | 902 | Not defined | MODELS | 1 |
| Body | 902 | Not defined | USE | 1 |
| Body | 930 | Not defined | ETH | 1 |
| Body | 946 | Not defined | RL | 1 |
| Body | 980 | Not defined | USENIX | 1 |
| Body | 983 | Defined again | ICLR | 56 |
| Body | 1010 | Not defined | NY | 1 |
| Body | 1034 | Not defined | CVF | 2 |
| Body | 1034 | Not defined | IEEE | 2 |
| Body | 1041 | Defined again | ICLR | 56 |
| Body | 1066 | Defined again | ICLR | 56 |
| Body | 1073 | Not defined | PDE | 1 |
| Body | 1088 | Defined again | ICLR | 56 |
| Body | 1111 | Not defined | CADS | 1 |
| Body | 1113 | Defined again | ICLR | 56 |
| Body | 1264 | Not defined | FOR | 3 |
| Body | 1264 | Not defined | PROOFS | 3 |
| Body | 1272 | Not defined | LEMMAS | 1 |
| Body | 1272 | Not defined | THREE | 1 |
| Body | 1335 | Not defined | DTi | 1 |
| Body | 1467 | Not defined | HARD | 1 |
| Body | 1574 | Not defined | LABEL | 1 |
| Body | 1731 | Not defined | BASIC | 1 |
| Body | 1731 | Not defined | FACTS | 1 |
| Body | 1756 | Not defined | DKL | 7 |
| Body | 1897 | Not defined | STEPS | 1 |
| Body | 1974 | Not defined | BL | 1 |
| Body | 2046 | Not defined | KL | 2 |
| Body | 2100 | Not defined | CovQ | 1 |
| Body | 2246 | Not defined | RK | 1 |
| Body | 2298 | Not defined | XR | 1 |
| Body | 2809 | Not defined | PLx | 1 |
| Body | 2809 | Not defined | tPLz | 1 |
| Body | 2895 | Not defined | DA | 6 |
| Body | 3054 | Not defined | DN | 2 |
| Body | 3086 | Not defined | PLaj | 1 |
| Body | 3095 | Not defined | PLM | 2 |
| Body | 3122 | Not defined | BR0 | 5 |
| Body | 3190 | Not defined | wIL | 1 |
| Body | 3209 | Not defined | IL | 8 |
| Body | 3241 | Not defined | LOSS | 2 |
| Body | 3241 | Not defined | WHAT | 2 |
| Body | 3481 | Not defined | LR | 2 |
| Body | 3580 | Not defined | BT | 9 |
| Body | 3590 | Not defined | EZT | 1 |
| Body | 3637 | Not defined | EV | 2 |
| Body | 3644 | Not defined | EYT | 1 |
| Body | 3774 | Not defined | NOISE | 1 |
| Body | 3900 | Not defined | SiLU | 1 |
| Body | 3928 | Not defined | SGD | 3 |
| Body | 4286 | Not defined | CV | 1 |
| Body | 4313 | Not defined | DOP853 | 1 |
| Body | 4324 | Not defined | CFG | 1 |
