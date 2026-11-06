contract_role: methodology
## Dimension Scores

### D1: methodology_rigor
score: warn
trigger: "numerical checks that confirm the result only qualitatively, without error bars, convergence-in-step-size evidence"

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "Local overreach or inconsistency that does not change the main message."

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

This is the report of Peer Reviewer 1 (Methodology). I am an applied mathematician working on non-autonomous ODEs. My review covers the rigour of the theorem statements, the two-step proof template, and whether the numerical results test the theorems or only agree with them. The calibration status of this seat report is NOT_CALIBRATED. No criteria binding was supplied, so I make no claim about venue fit.

Summary assessment. The paper studies the exact empirical conditional flow-matching field and asks which interventions can move its endpoints off the training atoms. These interventions are label smoothing, positive field mixtures, negative guidance, nonnegative guidance with a constant or bounded-variation schedule, and the composition of guidance with label averaging. A separate section asks what a learned field needs in order to inherit collapse. I checked the following proofs line by line in the rendered PDF:
- Lemmas B.1, B.2, B.3 and B.5
- Theorem 4.1, Theorem 4.5, Proposition 4.3(b) and Proposition B.4
- Theorem 4.6, including the closed form of F_w, the slope F_w'(0) = sech^2 B (1 - w sinh^2 B), both barrier computations and the cubic lower bound in part (b)
- Proposition B.6
- Theorem 4.7(a)-(c) at the level of detail given
- Corollary B.9, including the regular-simplex threshold
- Theorem 5.1 and Proposition C.1
- Both parts of Proposition C.2
- Theorem C.3, and the loss computation of Proposition C.4, d delta (1 + 3A/2 + 7A^2/6)

I found no gap that cannot be repaired locally, and no counterexample to any formal statement as stated. The paper's weaknesses are elsewhere. Some main-text paraphrases state more than the formal results do, and in one case less. Two numerical checks are presented as confirmation, but the reported data cannot fully support that role. My verdict is warn on D1 and warn on D3. The one Major finding (W1) concerns the solver sensitivity of the CIFAR-10 composition numerics. The theory already implies those results, but the paper never says so.

### S1: The two-step template is stated once and proved correctly
Lemma B.2 (finite kinetic energy and the concentration hypothesis give convergence to a candidate) and Lemma B.3 (Liouville plus Fatou on an injective C^1 flow give a null set of initial points with non-atom limits) are clean and correctly proved. The second lemma includes the Borel measurability of the exceptional set. Each intervention then verifies the same two hypotheses:
- Theorem 4.1 uses the energy W = |x|^2/2 - F + eps R^2/2. I re-derived W' = -|x'|^2 + alpha' times the integrated KL term + (eps/2)(integrated second-moment term - R^2), which is at most -|x'|^2. I also re-derived W >= 0.
- Theorem 4.5 uses the integration by parts of Lemma B.5 against a bounded-variation schedule. Its covariance-trace identity Theta = r^2 - |mu_w|^2 + w(1+w)|mu_c - mu_u|^2 + (1+w)e_c - w e_u is correct, and this is exactly where w >= 0 is used.
So the nonnegativity hypotheses in the statements are the ones the proofs use, neither stronger nor weaker.
**Evidence Anchor**: text: Appendix B.2, "All intervention proofs follow the same two steps: finite kinetic energy gives convergence, and"

### S2: The threshold of Theorem 4.6 is proved in both directions, including at the threshold
The closed form of F_w checks out, and so does the threshold w_c = 1/sinh^2 B (Table 10 values 0.7241, 0.0760 and 0.0100 at B = 1, 2, 3 all agree). Part (a) uses an explicit inward-moving barrier, delta eps^2/t. Part (b) covers the nonhyperbolic case w = w_c through the bound F_w(s) >= kappa min(s^3, 1) and a lower barrier that decays like e^{-3 tau} against an e^{-tau} decay of the trajectory, so no case is left open. Corollary B.9 recovers the same threshold from the matrix criterion. It also gives the simplex formula (1 - m^2)/m^2, which I checked against the Table 9 entries 1.160 and 4.802. I recomputed the trace column of Table 9 for the triangle and the simplex, tr Gamma = (1 - m^2) - w m^2, and it matches at every listed w (for example 0.268, -0.537, -2.148 for the triangle and 0.414, -3.311 for the simplex).
**Evidence Anchor**: text: Theorem 4.6(b), "(b) if w ≤ 1/ sinh2 B, only the initial point 0 converges to 0, and the endpoint is a training atom"

### S3: Proposition C.2 is correct and its hypotheses are shown to be needed
I checked part (a) in full: the forward and backward Gronwall bounds, bi-Lipschitz continuity of the endpoint map, surjectivity through the Cauchy sequence x_n, and absence of atoms. I checked part (b) in one dimension: the order-preserving crossing argument rules out liminf below limsup, a non-fixed limit is excluded, a repelling fixed point attracts at most one initial point because the gap D grows logarithmically, and an attracting fixed point traps an open interval. The examples after the proof show that integrability of L(t), and continuity of the derivative of x̂1 up to t = 1, cannot be dropped.
**Evidence Anchor**: text: Appendix C.2, "The hypotheses are needed. The exact field toward one atom, (a − x)/(1 − t), has L(t) = 1/(1 − t),"

### S4: Finite-time numerics are labelled as finite-time, and failures are kept
The paper does not present floating-point computations as proofs. Table 10 is said to be not verified by interval arithmetic. Table 9 is called finite-time computations that agree with the theorem. The DOP853 failures near ties are reported rather than dropped. Integrators, tolerances, hand-off rules and cutoffs are stated for every exact-field computation. Every plus-minus is declared to be a population standard deviation, and the conversion factor sqrt(5/4) of about 1.12 is correct. This is the right epistemic stance for my main concern.
**Evidence Anchor**: text: Appendix E.3, "These are finite-time computations that agree with the theorem; they do not"

### S5: Reproducibility affordances are specific
Scripts are named for each table and figure. Seeds, instance and training randomness are separated in EXP-1. I recomputed the 78 percent instance share as 0.121^2 / (0.064^2 + 0.121^2) = 0.781, and it is consistent. The learned-composition protocol states the solver (ROS2), both tolerances, the endpoint-class disagreement between tolerances (at most 1.07 percent), and a distillation positive control that tests the solver independently of learning.
**Evidence Anchor**: text: Appendix E, "Every across-seed ± is a population standard deviation (denominator n); at n = 5 the sample"

### W1: CIFAR-10 composition numerics are not shown to be converged, yet the abstract presents them as confirmation
Problem. For the eight CIFAR-10 pairs, the solver-sensitivity check was run on the first pair only. Even on that pair, changing the hand-off or the tolerance changes the midpoint fractions by up to 0.03. Individual endpoints agree for only about half the sources at 5 w_c. Meanwhile, the claim of a positive fraction in every pair at 1.1 w_c rests on fractions as low as 0.006, which is 3 of 512 sources, well inside the measured solver variability. So the computation does not establish the specific numerical statement in Section 6.2 and the abstract ("confirm the threshold, also on pairs of CIFAR-10 images") beyond numerical error.

Why it matters. Read as evidence, the computation brackets the threshold only to within [0.9, 1.1] w_c, and the positive side of the bracket is not robust. The substantive claim is nevertheless true, and for a different reason. With 1998 off-tie atoms whose posterior mass is exponentially small (Lemma B.7), the label weights restricted to the pair have log-odds plus or minus 2. Theorem 4.7(a) with Corollary B.9 then gives positive probability exactly for w > w_c, and Theorem 4.7(c) gives zero below it, since for two atoms the face condition holds trivially. The paper says only that "the threshold is the two-atom w_c with the other 1998 atoms present". It does not derive this as a corollary, so a reader takes the unconverged numerics as the support.

Suggestion. State the CIFAR-10 threshold as a corollary of Theorem 4.7 and Corollary B.9, with its hypotheses (nearest-atom condition at z, strictly positive label weights). Present the computation explicitly as a consistency check. Run the hand-off and tolerance sensitivity on all eight pairs at 1.1 w_c, and either report per-pair fractions with their solver spread or drop the claim that every pair is positive at 1.1 w_c.

**Severity**: Major
**Evidence Anchor**: text: Appendix E.3, CIFAR-10 composition paragraph, "individual endpoints agree for at least 91% of sources up to w = 2wc but" and "only about half at w = 5wc, so we report fractions only."
**Confidence**: 4 — core expertise: numerical integration of stiff non-autonomous ODEs and the stable-manifold argument behind Theorem 4.7

### W2: The main text states Proposition C.2(b) without its one-dimensional hypothesis, and in that generality it is false
Problem. Proposition C.2(b) assumes d = 1, and its proof uses the ordering of the real line (the crossing argument with sup over X_r >= c). Section 5 drops this hypothesis and asserts that a data-predicting field with a bounded prediction that is C^1 up to t = 1 ends at the fixed points of the prediction. In d >= 2 this fails. In the time tau the equation becomes asymptotically autonomous, x' = g(x) - x. Take a bounded C^1 g for which g(x) - x has an attracting limit cycle, for example (1 - |x|^2)x + Jx near the unit circle with J a rotation, modified to -x plus a bounded term at infinity. Then an open set of initial points does not converge at all.

Why it matters. This sentence is the paper's theoretical account of why data-predicting networks miss the threshold. The triangle experiment is two-dimensional. The core exact-field theory is unaffected.

Suggestion. Restore "in one dimension" in Section 5. If a d-dimensional version is wanted, add a hypothesis that excludes recurrence, for example that g - id is a gradient or that the omega-limit sets are fixed points.

**Severity**: Minor
**Evidence Anchor**: text: Section 5, "a data-predicting one whose bounded prediction is C1 up to t = 1 ends"
**Confidence**: 5 — core expertise: asymptotically autonomous ODEs and limit sets

### W3: Section 4.4 says that sinks keep a positive fraction, but two sink rows of Table 9 show zero
Problem. In Table 9, the d = 8 simplex at 1.1 w_c and 2 w_c is classified as a sink, yet 0.0000 of the 2048 sources stay in the profile. Appendix E.3 says correctly that these basins are below the sampling resolution of 1/2048. The main text, however, says without qualification that sinks keep a positive fraction.

Why it matters. Theorem 4.7(a) predicts positive probability for these rows, and the check as designed could not detect it. Those rows therefore neither confirm nor test part (a). The main text turns a non-detection into a confirmation.

Suggestion. Qualify the sentence (positive where resolvable; below 1/2048 for the d = 8 simplex at 1.1 and 2 w_c). Better, add a targeted sample near xi = 0, for example sources drawn from a small ball pulled back through the flow, so that part (a) is actually tested in d = 8.

**Severity**: Minor
**Evidence Anchor**: text: Section 4.4, "put no source at z, and sinks keep a positive fraction (Table 9)."
**Confidence**: 5 — direct comparison of the main text against Table 9

### W4: The hard-label guidance rate in the main text is weaker than the one proved
Problem. Inequality (10) gives |x_t - t a_i|^2 is at most eps^2 times [C + 2w log N log(1/eps) + O(1)]. That is, |x_t - a_i| = O((1 - t) sqrt(log(1/(1 - t)))). The main text gives the guaranteed rate as (1 - t) log(1/(1 - t)). The statement is true but loose: the proof shows more than the text says. Similarly, for the schedules w(s) bounded by W0 (1 - s)^(-gamma) the proof gives the rate (1 - t)^(1 - gamma/2), but the text states only collapse.

Suggestion. State the sqrt-log rate, and the (1 - t)^(1 - gamma/2) rate for gamma below 2.

**Severity**: Minor
**Evidence Anchor**: text: Section 4.2, "At a hard label, guidance thus weakens the guaranteed rate to (1 − t) log(1/(1 − t)) but does not"
**Confidence**: 5 — rederived from (10)

### W5: The remark after Proposition C.2 does not match hypothesis (b) to the networks it names
Problem. Part (b) requires the spatial derivative of x̂1 to be continuous on R x [t0, 1]. The remark says that an MLP with Lipschitz activations satisfies (b) once its output is clipped to a bounded range. This fails in two ways. Lipschitz activations such as ReLU do not give a C^1 map, and hard clipping destroys C^1 at the clipping boundary. Appendix E.3 also concedes that the trained network is not clipped. So the hypotheses of (b) are not checked for the networks to which (b) is applied.

Suggestion. Require C^1 activations (EXP-1 uses SiLU) and a smooth squashing such as a scaled tanh in place of clipping. State which learned-composition networks meet these conditions.

**Severity**: Minor
**Evidence Anchor**: text: Appendix C.2, "The same MLP predicting data" and "satisfies (b) once its output is clipped to a bounded range"
**Confidence**: 4 — standard regularity facts about MLPs; the activation of the learned-composition MLP is not stated

### W6: Two technical steps are given as outlines
Problem. Two steps are cited or sketched rather than proved:
- The C^1 property of the Lyapunov-Perron graph in Lemma B.8 is attributed to "the standard differentiability of the fixed point".
- The Caratheodory facts used by Lemma B.3 under the measurable schedules of Theorem 4.5 (C^1 flow maps, and Liouville's formula for fields measurable in time) are sketched as "In outline".
Both are standard and I believe them. But Lemma B.8 is non-autonomous with a forcing f(0, 0, tau) that is not zero, and it carries the codimension argument behind Theorem 4.7(b).

Suggestion. Give a precise citation for each, for example Hale, Ch. I, for the Caratheodory variational equation, and a non-autonomous invariant-manifold theorem with the uniform-continuity hypothesis stated. Alternatively, add a short proof that the fixed point of the contraction depends C^1 on (s0, eta0).

**Severity**: Minor
**Evidence Anchor**: text: Appendix B.6 and B.1, "This graph is C1 by the standard differentiability of the fixed" and "In outline, difference quotients of the flow satisfy the variational equation up to an error"
**Confidence**: 4 — core expertise: invariant manifolds of non-autonomous systems

### W7: Appendix C.4 rules out a solver artefact on evidence that does not support the conclusion
Problem. Refining the CIFAR-10 U-Net integration from 50 Euler steps at 1 - T = 1e-3 to RK4 at 1e-4 lowers every off-atom fraction (for example, 0.298 to 0.254 at h = 6). This is two refinement levels with a monotone decrease, which is not evidence of convergence. The sentence that then says the discrepancy is "therefore not a solver or cutoff artefact" follows a comparison against all 50000 images, which addresses a different question.

Suggestion. Add at least one further refinement level, or an adaptive solver with a stated tolerance. Otherwise soften the conclusion to "not explained by the refinements tried".

**Severity**: Minor
**Evidence Anchor**: text: Appendix C.4, "remaining discrepancy is therefore not a solver or cutoff artefact."
**Confidence**: 4 — numerical-analysis judgement from the reported values

### W8: Theorem 5.1 is close to an identity, and the main text frames it as a transfer result
Problem. Theorem 5.1 is variation of constants. When (1 - t) v_theta tends to 0 along the trajectory, (1 - t) Delta tends to z - a exactly, so the bound holds with equality and carries no information beyond the endpoint itself. Appendix C.4 states this frankly. The contributions bullet still presents it as a mechanism by which learned fields "inherit collapse".

Suggestion. Move the appendix caveat into Section 5. State that the bound has content only when the scaled error is controlled independently of the endpoint, as Theorem C.3 does with K(t).

**Severity**: Minor
**Evidence Anchor**: text: Section 1, "Learned fields inherit collapse unless their scaled error persists"
**Confidence**: 4 — direct reading of the proof and of Appendix C.4

### W9: The causal attribution in the learned-composition ablation runs ahead of the seed-level data
Problem. "The input decides" rests on a two-by-two ablation (output parametrisation by input) with five seeds. The input is necessary in these runs. It is not sufficient: the rescaled-input velocity network gives 0.294 +/- 0.152 at 2 w_c for B = 1 with one seed at 0, matches in only some seeds at B = 2, and fails at B = 3. All runs are at d at most 2. The Limitations section hedges this, and the abstract says "in our runs". The sentence in Section 6.2 does not.

Suggestion. Phrase the conclusion as necessity within the tested architectures and d at most 2. Report the per-seed outcomes in the main text.

**Severity**: Minor
**Evidence Anchor**: text: Section 6.2, "Of the changes the successful network makes, the input decides"
**Confidence**: 3 — methodology judgement on experimental design; no expertise claim about network training

Other checks that produced no finding.
- Theorem 4.5 states measurable, bounded, nonnegative w of bounded variation on [t0, 1), and that is exactly what Lemma B.5 and the Theta bound use.
- Theorem 3.4 defines the endpoint law as a weak limit of time marginals, and Section 4 uses the pathwise limit X_1. The two agree by dominated convergence, as the proofs state.
- "a.s." and "null" are used consistently with Lebesgue measure on initial points, transferred to any absolutely continuous source.

## Arithmetic Receipts

### AR1
procedure_id: grim
evidence_anchor: table: Table 9, row triangle d=2 w=2 wc, column sigma=10^2
reported_inputs: fraction 0.1396; sources 2048; per-source outcome binary (profile stays near the profile at fast time); reported to 4 decimals
assumptions: each source contributes 0 or 1 so the fraction is k/2048 for an integer k, as the caption licenses; rounding rule unstated but the value is not at a rounding boundary so half-up and half-even agree
derivation: 0.1396 x 2048 = 285.9; k = 286 gives 286/2048 = 0.1396484, which lies in the rounding interval
derived_value_or_range: k = 286, fraction 0.1396484
comparison_rule: some integer k with k/2048 in the half-open rounding interval of the reported 4-decimal value
rounding_interval: [0.13955, 0.13965)
nearest_achievable: 285/2048 = 0.1391602 and 286/2048 = 0.1396484
status: consistent

### AR2
procedure_id: grim
evidence_anchor: table: Table 9, row triangle d=2 w=5 wc, column sigma=10^4
reported_inputs: fraction 0.6865; sources 2048; per-source outcome binary; reported to 4 decimals
assumptions: each source contributes 0 or 1 so the fraction is k/2048 for an integer k; rounding rule unstated but the value is not at a rounding boundary
derivation: 0.6865 x 2048 = 1405.95; k = 1406 gives 1406/2048 = 0.6865234, inside the rounding interval
derived_value_or_range: k = 1406, fraction 0.6865234
comparison_rule: some integer k with k/2048 in the half-open rounding interval of the reported 4-decimal value
rounding_interval: [0.68645, 0.68655)
nearest_achievable: 1405/2048 = 0.6860352 and 1406/2048 = 0.6865234
status: consistent

### AR3
procedure_id: grim
evidence_anchor: table: Table 9, row simplex d=8 w=5 wc, column sigma=10^4
reported_inputs: fraction 0.0186; sources 2048; per-source outcome binary; reported to 4 decimals
assumptions: each source contributes 0 or 1 so the fraction is k/2048 for an integer k; rounding rule unstated but the value is not at a rounding boundary
derivation: 0.0186 x 2048 = 38.09; k = 38 gives 38/2048 = 0.0185547, inside the rounding interval
derived_value_or_range: k = 38, fraction 0.0185547
comparison_rule: some integer k with k/2048 in the half-open rounding interval of the reported 4-decimal value
rounding_interval: [0.01855, 0.01865)
nearest_achievable: 38/2048 = 0.0185547 and 39/2048 = 0.0190430
status: consistent

### AR4
procedure_id: grim
evidence_anchor: table: Table 9, row box d=8 w=5, column sigma=10^4
reported_inputs: fraction 0.0020; sources 512; per-source outcome binary; reported to 4 decimals
assumptions: each source contributes 0 or 1 so the fraction is k/512 for an integer k; rounding rule unstated but the value is not at a rounding boundary
derivation: 0.0020 x 512 = 1.024; k = 1 gives 1/512 = 0.0019531, inside the rounding interval
derived_value_or_range: k = 1, fraction 0.0019531
comparison_rule: some integer k with k/512 in the half-open rounding interval of the reported 4-decimal value
rounding_interval: [0.00195, 0.00205)
nearest_achievable: 1/512 = 0.0019531 and 2/512 = 0.0039063
status: consistent
