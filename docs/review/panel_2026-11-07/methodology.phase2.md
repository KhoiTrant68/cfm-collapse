contract_role: methodology

## Dimension Scores

### D1: methodology_rigor
score: warn
trigger: "numerical reporting lacks some solver, tolerance, or seed details while the conclusions still look robust"

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "Some claims are phrased more strongly than their support (for example a heuristic or numerical finding described in theorem-like language)"

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

Peer Reviewer 1 (methodology: mathematics and numerics). I read the main text, the proof appendices A to C, and the experimental appendix E. I checked the following line by line against the statements: Theorem 4.6 (closed form of Fw, the slope at the tie, the barrier argument for (a), the cubic lower bound and trapping argument for (b)), Proposition B.6 (label bottleneck), Proposition B.7, Corollary B.11 (both the two-atom and the regular-simplex thresholds), Theorem 5.1, the Θ identity in the proof of Theorem 4.5, Lemma B.2, Lemma B.3, and the energy and divergence steps of Theorem 4.1. For Lemma B.9 and Theorem B.10 I checked the structure of the argument but not every constant. I found no counterexample to any stated theorem and no invalid core step. The mathematical core holds up under a careful read. My reservations are about how a few numerical and formal results are worded, and about some gaps in the sensitivity controls. None of them reaches the core claims.

Near-threshold law (Appendix B.6). The paper labels this result correctly: "formal asymptotic law, not a theorem". I re-derived it independently. Write x = e^(−τ) y and keep only the cubic part of Fw, namely Fw(s) ≈ sech²B · s(s² − δ). The exact τ-equation x' = Fw(βx) − x then becomes a Bernoulli equation in y with no approximation in the time-dependent coefficients, because βe^(−τ) = e^τ − 1 holds exactly. In z = y^(−2) it is linear. Its capture condition is x0^(−2) > 2 sech²B ∫ g³ exp(−sech²B · δ g²) dg over (0, ∞) = 1/(sech²B · δ²), that is |x0| < δ/cosh B. So the separatrix value C* = 1 is exact for the cubic truncation, not only to leading order. All the non-autonomous corrections (the 1 + ε/t and dθ/dτ terms) cancel identically. The only error left comes from the remainder O(|s|⁵ + δ|s|³). On the relevant scale s ~ √δ that remainder is a relative O(δ) correction, which matches the reported deficit growing in proportion to δ. This also points to a short route to a theorem. Flows on the line preserve order, so it suffices to bound Fw above and below on [0, K√δ] by cubics κ±·s(s² − δ±) with κ± = sech²B(1 + O(δ)) and δ± = δ(1 + O(δ)). The barriers of Theorem 4.6(a)/(b) handle the outer region. Comparison would then give a basin half-width of (δ/cosh B)(1 + O(δ)), and hence P0 = √(2/π)(w/wc − 1)/cosh B · (1 + O(w/wc − 1)) rigorously. One note on the text I was given: it prints the constant as "2/π". The values in Table 11 (0.050, 0.021, 0.008 at 1.1 wc for B = 1, 2, 3) match √(2/π)/cosh B · 0.1 = 0.0517, 0.0212, 0.0079. The radical was therefore most likely lost in text extraction, and the authors should only confirm it in the typeset PDF.

Numerical cross-checks outside the bounded receipt procedures. I recomputed the following: wc = 1/sinh²B = 0.7241, 0.0760, 0.0100 for B = 1, 2, 3; the simplex thresholds (1 − m²)/m² = 1.160 (N = 3) and 4.802 (N = 9) at B = 2; the bottleneck threshold 3.926 at BQ = 1.2413; and the tr Γ = 1 − m²(1 + w) column of Table 10 for the triangle and the simplex. All agree with the printed values. The integer-count consistency of three Table 10 fractions is recorded under Arithmetic Receipts.

### W1: The near-threshold continuity and linearity are stated as fact in two places
**Severity**: Minor
**Evidence Anchor**: text: Appendix B.6, end of "Size of the basin just above the threshold", "The basin probability therefore vanishes continuously, and linearly, at the threshold"
**Confidence**: 4 — I re-derived the formal law; its status rests on the paper's own disclaimer one sentence earlier

Right after its disclaimer, Appendix B.6 concludes with "therefore" that P0 vanishes continuously and linearly at wc and that the endpoint law does not jump there. Section 6.2 likewise says "just above it the basin probability grows linearly (Appendix B.6)" with no qualifier. Theorem 4.6 proves P0 > 0 for w > wc and P0 = 0 for w ≤ wc. It does not prove right-continuity at wc, let alone the linear rate. Both currently rest on a formal expansion plus exact-flow computations down to δ = 3 × 10⁻⁴. The remedy is one phrase in each place ("formally and numerically"). A stronger alternative is to prove it via the cubic-comparison route sketched above, which looks short given the exact Bernoulli structure.

### W2: The CIFAR composite fractions at 5 wc and 10 wc have no sensitivity check
**Severity**: Minor
**Evidence Anchor**: text: Appendix E.3, guided label averaging on CIFAR-10, "We reran all eight pairs at w/wc ∈ {0.9, 1.1, 2}"
**Confidence**: 4 — follows directly from the protocol as described

The hand-off and tolerance reruns cover w/wc ∈ {0.9, 1.1, 2} only. On the first pair, individual endpoints at 5 wc agree with the main run for only about half the sources. Yet the text and Figure 12(b) describe a shape: a peak at 2 wc followed by a fall to means of 0.150 at 5 wc and 0.042 at 10 wc, which the paper attributes to guidance pulling sources onto the atoms. The threshold claim, which the paper correctly calls a consistency check of Theorem B.10(c), is unaffected. The large-w basin sizes are a single-setting measurement in a regime where the per-source classification is unstable. Either extend the reruns to 5 and 10 wc, or mark those points in Figure 12(b) as unchecked.

### W3: The solver-tolerance and cutoff checks for the learned composite are reported for the two-atom runs only
**Severity**: Minor
**Evidence Anchor**: text: Appendix E.3, learned guided label averaging, "in the two-atom runs the endpoint classes of the composite differ between the two tolerances for at most 1.07% of the sources"
**Confidence**: 3 — the triangle check may exist in the artifacts, but the paper does not report it

The triangle comparison in the main text (0.143 ± 0.004 against 0.133 at 2 wc) and the triangle ablations in Table 12 have no stated ROS2 tolerance agreement. The paper also says occupancy is unchanged between ϵ = 10⁻³ and 10⁻⁵ only "at B = 1". This matters because the same appendix shows how stiff these composites can be: cfm_x_a was stopped when the two tolerances disagreed on 4% and 27% of endpoints at w = 0. Reporting the tolerance disagreement and the cutoff invariance for B = 2, B = 3 and the triangle would close the gap. I expect the conclusions to survive.

### W4: Proposition C.2(b) does not predict an empty midpoint for the plain data-predicting network
**Severity**: Minor
**Evidence Anchor**: text: Section 6.2, "leaves the midpoint empty at w ≥ 5wc, as Proposition C.2(b) leads one to expect"
**Confidence**: 4 — this reading of Prop. C.2(b) follows from its statement and the remark after it

Proposition C.2(b) says that, for a bounded prediction that is C¹ up to t = 1, the off-atom mass is decided by the sign of g_w′(0) − 1. The remark after it adds that the exact field does not constrain this quantity. The proposition therefore explains why the outcome is uncontrolled, not why it should be empty. In the paper's own data, one seed at B = 1, 2 wc places 0.415 at the midpoint. The trained network is also not clipped, as the appendix concedes, so the hypotheses are not verified. Rephrasing to "is consistent with Proposition C.2(b), under which the outcome depends on the slope of the network's limit at the tie" would match what is proved.

### W5: The abstract drops a hypothesis of Proposition C.2(a)
**Severity**: Minor
**Evidence Anchor**: text: Abstract, "A learned field whose spatial Lipschitz constant is integrable up to t = 1 has no endpoint atom at all"
**Confidence**: 5 — direct comparison with the statement of Proposition C.2(a)

Proposition C.2(a) also requires |vθ(0, t)| to be integrable on [0, 1). Without that, the bounds of the proof give neither boundedness nor a well-defined endpoint map. For the MLPs in question the hypothesis is harmless, but the abstract states it as a general claim. Adding "and bounded at the origin" or "(under mild growth conditions)" would make it accurate.

### W6: The remark after the bottleneck proposition is literally false as worded
**Severity**: Minor
**Evidence Anchor**: text: Appendix B.5, remark after Proposition B.6, "is not a positive field mixture vΠ with a fixed Π"
**Confidence**: 4 — the counter-reading is immediate from the definition of vΠ in Theorem 4.1

The field v_p̄c is trivially a positive field mixture vΠ, with Π = δ_p̄c, a point mass on a strictly positive prior. That is in fact why part (b) holds. The intended statement is that v_p̄c differs from the field average ∫ v_p(h)(y) νc(dy), because the reweighting depends on (x, t). The mathematics of Proposition B.6 is correct: (a) follows from the conditional-risk decomposition and the independence of X0 from (I, Y), and (b) is right because the proof of Theorem 4.5 uses the conditional prior only through strict positivity, which I checked. Only the sentence needs fixing.

### W7: Sign slip in the first line of the Θ display in the proof of Theorem 4.5
**Severity**: Minor
**Evidence Anchor**: equation: Appendix B.5, proof of Theorem 4.5, first line of the display for Θ = (1 + w) tr Cov_qpc(a) − w tr Cov_qpu(a)
**Confidence**: 2 — this may be a text-extraction artefact

Expanding Θ with tr Cov_qp(a) = r² − |mp − z|² + ep gives r² − (1 + w)|µc|² + w|µu|² + (1 + w)epc − w·epu. The extracted text shows "− w|µu|²". The second line, obtained through the stated identity, is correct, and so is the final bound Θ ≥ r² − |µw|² − w̄·epu. Please check the typeset version.

### S1: The composition theorem is proved as stated
**Evidence Anchor**: equation: Eq. (6), closed form of Fw, and the proof of Theorem 4.6 in Appendix B.6

I verified the closed form of Fw, the slope Fw′(0) = sech²B − w tanh²B, the barrier b(t) = δε²/t with its sign computation, and the cubic lower bound Fw ≥ κ min{s³, 1} used in (b). The boundary case w = wc is included correctly in (b). The threshold is exact and the basin's (1 − t)² scale is proved, not assumed.

### S2: The formal derivation is separated from the theorem, and its constant is right
**Evidence Anchor**: text: Appendix B.6, "We have not bounded the neglected terms, so this is a formal asymptotic law, not a theorem."

The appendix states the status of the near-threshold law explicitly. Its separatrix value C* = 1 and basin |x0| < δ/cosh B agree with the exact solution of the cubic-truncated problem, which I derived independently (see above). The exact-flow ratios approaching 1 linearly in δ are what that structure predicts.

### S3: The label-bottleneck proposition is correct and small in scope
**Evidence Anchor**: text: Appendix B.5, "A label bottleneck averages priors, not fields."

Proposition B.6 isolates exactly what a coarse label code does at the optimum (it averages priors) and reuses Theorem 4.5 with the right minimal hypothesis. The cfm_x_sq experiment then tests the field-average case separately, with the threshold recomputed for BQ (3.926, which I confirmed).

### S4: Numerical failures are reported, not discarded silently
**Evidence Anchor**: text: Appendix E.3, "it gave no midpoint mass even for the positive control, and we discarded it"

The paper reports the following failures as such: the fixed-step RK4 instability, the DOP853 failures near ties, the stopped cfm_x_a runs, the unresolved large-guidance bottleneck runs, and the per-source disagreement at 5 wc on CIFAR. It also includes a distillation positive control for the solver and architecture. This is the error-control discipline the setting needs.

### S5: The spectral checks match the theory exactly where the theory is computable
**Evidence Anchor**: table: Table 10, profile class and tr Γ columns

The tr Γ entries equal 1 − m²(1 + w) for the triangle and the simplex. The sources and saddles, including the negative-trace saddles that Lemma B.3 cannot see, end with no source at z. The paper says plainly that the d = 8 sinks at 1.1 wc and 2 wc fall below the 1/2048 resolution rather than presenting them as confirmations.

### S6: The spectral classification is scoped to what is proved
**Evidence Anchor**: text: Appendix B.7, "Nonhyperbolic profiles and faces whose affine hull contains PLz remain open."

Theorem B.10(c) carries the face condition and hyperbolicity as explicit hypotheses. The main text repeats that a complete classification needs them. Lemma B.8(ii) correctly handles trajectories with unbounded ξ, which the no-escape argument in (c) requires.

### S7: One proof template carries all the positive results
**Evidence Anchor**: text: Appendix B.3, "All intervention proofs follow the same two steps"

Lemma B.2 (finite kinetic energy implies convergence to a candidate) and Lemma B.3 (Liouville plus Fatou makes basins with unbounded volume expansion null) are cleanly stated and proved. The positive theorems then differ only in an energy bound and a divergence lower bound, and both are verifiable. In Theorem 4.1 the choice of the first KL bound, so that Π may charge priors near the boundary of the simplex, is a careful touch.

## Arithmetic Receipts

### AR1
procedure_id: grim
evidence_anchor: table: Table 10, triangle row at w = 2 wc, column σ = 10^2
reported_inputs: reported fraction 0.1396; sources n = 2048; each source counted 0 or 1
assumptions: the fraction is an unweighted share of the 2048 listed sources, scale 0 to 1 per source; the rounding rule is unstated, so nearest rounding and truncation are both checked
derivation: 0.1396 × 2048 = 285.90; 285/2048 = 0.13916015625; 286/2048 = 0.1396484375; 286/2048 rounds to 0.1396 under half-up or half-even and truncates to 0.1396
derived_value_or_range: k = 286 gives 0.1396484375, which reproduces 0.1396 under every candidate rule
comparison_rule: the reported value is reachable if some integer k in [0, 2048] has k/2048 inside the rounding interval of 0.1396 at four decimals under each candidate rule
status: consistent
rounding_interval: [0.13955, 0.13965) for nearest rounding; [0.1396, 0.1397) for truncation
nearest_achievable: 285/2048 = 0.13916015625 and 286/2048 = 0.1396484375

### AR2
procedure_id: grim
evidence_anchor: table: Table 10, triangle row at w = 5 wc, column σ = 10^2
reported_inputs: reported fraction 0.6865; sources n = 2048; each source counted 0 or 1
assumptions: the fraction is an unweighted share of the 2048 listed sources, scale 0 to 1 per source; the rounding rule is unstated, so nearest rounding and truncation are both checked
derivation: 0.6865 × 2048 = 1405.95; 1405/2048 = 0.68603515625; 1406/2048 = 0.6865234375; 1406/2048 rounds to 0.6865 under half-up or half-even and truncates to 0.6865
derived_value_or_range: k = 1406 gives 0.6865234375, which reproduces 0.6865 under every candidate rule
comparison_rule: the reported value is reachable if some integer k in [0, 2048] has k/2048 inside the rounding interval of 0.6865 at four decimals under each candidate rule
status: consistent
rounding_interval: [0.68645, 0.68655) for nearest rounding; [0.6865, 0.6866) for truncation
nearest_achievable: 1405/2048 = 0.68603515625 and 1406/2048 = 0.6865234375

### AR3
procedure_id: grim
evidence_anchor: table: Table 10, box row at w = 5 (sink), column σ = 10^2
reported_inputs: reported fraction 0.0039; sources n = 512; each source counted 0 or 1
assumptions: the fraction is an unweighted share of the 512 listed sources, scale 0 to 1 per source; the rounding rule is unstated, so nearest rounding and truncation are both checked
derivation: 0.0039 × 512 = 1.9968; 1/512 = 0.001953125; 2/512 = 0.00390625; 2/512 rounds to 0.0039 under half-up or half-even and truncates to 0.0039
derived_value_or_range: k = 2 gives 0.00390625, which reproduces 0.0039 under every candidate rule
comparison_rule: the reported value is reachable if some integer k in [0, 512] has k/512 inside the rounding interval of 0.0039 at four decimals under each candidate rule
status: consistent
rounding_interval: [0.00385, 0.00395) for nearest rounding; [0.0039, 0.0040) for truncation
nearest_achievable: 1/512 = 0.001953125 and 2/512 = 0.00390625
