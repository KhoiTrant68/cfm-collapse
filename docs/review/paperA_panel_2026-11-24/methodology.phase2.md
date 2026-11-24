contract_role: methodology
## Dimension Scores

### D1: methodology_rigor
score: warn
trigger: "a result the authors themselves mark as unchecked is cited downstream with a caveat"

### D2: domain_accuracy
score: not_assessed

### D3: argumentative_coherence
score: warn
trigger: "inconsistent use of a defined term across sections"

### D4: cross_disciplinary_relevance
score: not_assessed

### D5: writing_and_structure
score: not_assessed

### D6: venue_fit_and_contribution
score: not_assessed

## Review Body

### Reviewer identity and scope

Peer Reviewer 1 (methodology). Applied mathematician working on non-autonomous ODEs, singular perturbation and invariant-manifold theory. I reviewed the TMLR build of the manuscript (the `\else` branches) and read all of it, including every appendix proof. I did not review LaTeX comments. I checked the main identities and thresholds with small NumPy/SciPy scripts, and I read `scripts/stress_positive_control.py` to check the positive-control protocol against the text. Calibration status: `NOT_CALIBRATED`. Overall confidence: 4.

### Summary assessment

This is a proof-based paper, and its proofs are strong. I worked through the two-step template line by line: Lemma conv (finite kinetic energy gives convergence to a finite candidate set) and Lemma volume (Liouville's formula plus Fatou's lemma gives null non-atom basins). I did the same for its instances: Theorem posmix, Lemma signedconv with Theorem schedule, Theorem composition (including the threshold w = w_c), Theorem spectral (the blow-up, Lemma offtie, Lemma lp and part (c)), and Proposition regular. I found no false statement and no unrepairable gap.

The paper passes to the limit t -> 1 correctly throughout:
- Kinetic-energy bounds are uniform in time.
- In Theorem posmix, the divergence integrals are bounded below on sets of good times.
- In Theorem schedule, the integration by parts against a right-continuous version of the bounded-variation schedule is valid.
- In the composition and spectral proofs, the barrier and Lyapunov–Perron arguments carry explicit rates.

I also checked independently the three results that the LLM-use statement says the authors have not yet checked line by line: Corollary twofields, Proposition twoatom and Remark generic. All three are correct.

The weak points are elsewhere. The main one concerns the evidential value of the stress-test positive control (W1). The others are presentation and scope issues. The D1 and D3 warns rest on the disclosed unchecked status of three results that the headline claims use (W2) and on the overloaded threshold symbol w_c (W3).

### Strengths

### S1: The two-step template is sound and is applied without hidden uniformity gaps
Evidence Anchor: equation: Appendix B.3, Lemma conv and Lemma volume (eq. pf:divinfinity)

Each step checks out:
- Lemma conv: the speed lower bound away from candidates and the crossing-energy argument are complete.
- Lemma volume: it applies Fatou correctly to the injective C^1 flow maps.
- Theorem posmix, Step 2: Chebyshev's inequality yields good times of measure at least one half in each unit interval. Together with the compactness of K_delta in the closed simplex (V vanishes only at vertices because every prior is strictly positive), this gives the required growth of beta times V.
- Theorem schedule: the estimate int_n^{n+1} beta Theta >= beta(n) r^2/2 uses the ratio bound beta(n+1)/beta(n) <= C_beta correctly.

### S2: Bounded-variation schedules are handled by a correct integration by parts
Evidence Anchor: text: Appendix B.5, Lemma signedconv "changing each $c_k$ on the countable set of its discontinuities there makes it right-continuous"

The remainder terms r_k are integrable because both eps and alpha decrease to zero. h_k is bounded by H-bar on the trajectory. The Stieltjes term costs only H-bar times Var c_k. So the kinetic energy is finite for any bounded schedule of bounded variation, and constant guidance needs no special treatment.

### S3: The threshold w = w_c of Theorem composition is treated separately and correctly
Evidence Anchor: equation: Appendix B.6, proof of Theorem composition (b), F_w(s) >= kappa min{s^3, 1}

At w <= 1/sinh^2 B the linearisation degenerates. The proof replaces it with a cubic lower bound and the moving barrier theta = (kappa beta^3)^(-1/2), which decays faster than e^(-tau). I checked every inequality, including 2 tanh(1) sinh^2(1) > 1. The closed form of F_w and its slope (1+w) sech^2 B - w also check out numerically for B in {0.5, 1, 2, 3}.

### S4: The spectral classification is a careful fast–slow and invariant-manifold argument
Evidence Anchor: equation: Appendix B.7, eq. pf:spec:blowup and Lemma lp

Each step checks out:
- I re-derived the blow-up equations: dxi/dsigma = (eps^2/t^2) xi + P_L(m-bar - z).
- In Lemma offtie(i), the off-tie mass is O(e^{-c beta}) on a compact set in xi with |eta| <= rho, and its derivatives in (xi, eta) are O(beta^2 e^{-c beta}). This is exactly what Lemma lp needs.
- Lemma lp handles the time-dependent rate beta(tau) through the kernel bounds int beta e^{-a int beta} <= 1/a.
- The codimension of the decaying set equals n_+, and the Lipschitz graph is null.
- Part (c) rules out escape to infinity using the potential Psi, which grows at rate at least c_0 outside a ball, combined with xi = o(sigma).

### S5: Numerical computations of the composite use stopping rules that follow from the proof
Evidence Anchor: text: Appendix E.2, Guided label averaging "Every $0.25$ units of $\tau$ it checks two stopping rules, each forward invariant"

The barrier rule beta min{F(s*-delta), -F(s*+delta)} > (1+eps/t)(|s*|+delta) makes the interval around a sink forward-invariant under ds/dtau = beta F + (1+eps/t)s, because beta increases and eps/t decreases. The outer-root rule is also justified by the proof. The basin probabilities are consistent with the formal law near the threshold: at w = 1.1 w_c with B = 1 the formula gives 0.0517, against 0.050 computed.

### S6: The three flagged results are correct (independent check)
Evidence Anchor: text: Appendix B.8, proof of Proposition twoatom "With $q(x)=(x-m_-)(x-m_+)$, the two linear constraints give"

**Corollary twofields.** The reduction to Theorem schedule for c > 1 and c < 0 is correct, and the Theta identity of that proof uses only membership of both priors in P_N^+.

**Proposition twoatom.** I re-derived the parts:
- (a) follows from sum_k c_k q(m_k) = V + m_- m_+.
- (b) holds: if c_2 < 0 and c_3 <= 0, then m_1 < 0 and V < 0. I also re-derived (b) by a second route, using the quadratic (m - m_2)(m - m_3).
- (c) matches F_w.

In 4000 random signed combinations of two to five priors, 252 had a sink profile. None of them violated (a) or (b), and the identity F' = 1 - sum c_k m_k^2 held at every profile. The B = 3, 2, 1 example with a sink exists (for instance c = (4.66, -9.54, 5.89)). The negative-prompt example (0.91, -4, 4.09) has a sink profile, as the text says. The edge thresholds 1.368 w_c (triangle) and 1.407 w_c (nine-simplex) and the face range 0.97–1.14 w_c reproduce.

**Remark generic.** The partial derivatives with respect to the restricted log-odds of one prior with c_k != 0 span L. This makes G a submersion, and the parametric transversality theorem applies as stated.

### Weaknesses

### W1: The stress-test positive control passes because of floating-point resolution loss, not because the fixed-step scheme resolves an attracting tie
**Severity**: Major
**Evidence Anchor**: text: Section 6, paragraph "A positive control for the stress test" "The stress test therefore sees an attracting tie when there is one"
**Confidence**: 4 — reproduced numerically with the authors' oracle and RK4 transcribed

**Problem.** The positive control runs the stress test's fixed-step log-time RK4 (256 steps per segment) on the guided two-atom composite. In the last steps of the first segment (gap 1e-2), the stiffness beta |F'(0)| Delta-tau is about 75 at w = 2 w_c. That is far beyond RK4's stability bound of about 2.8, which the paper itself states in Appendix E.2 when it discards fixed-step RK4 for the learned composites.

**My test.** I transcribed the script's `oracle` and `rk4` and ran them on the first coordinate. They reproduce the reported midpoint fractions (0.049, 0.417, 0.987 at w/w_c = 1.1, 2, 10). The captured endpoints sit at |x_1| of about 2e-17, 2e-19 and 2e-21 at the three gaps, matching the printed 2.25e-17, 2.25e-19 and 2.25e-21. This is the floor below which the logits -|x - t a|^2 / (2 eps^2) can no longer resolve x_1 in double precision. Below that floor the computed field is exactly symmetric, and the state then decays like e^(-tau).

I then replaced the oracle with an algebraically identical one written in s = t x / eps^2, which computes (1+w)/2 [tanh(s+B) + tanh(s-B)] - w tanh s. With the same RK4, steps and gaps, the midpoint fraction is 0 at every w/w_c (0/4096 at 1.1, 2 and 10): the scheme ejects every captured trajectory.

**Why it matters.** What the control actually shows is that this particular implementation, through rounding, freezes trajectories that the true flow captured before the step size became unstable. It does not show that the stress-test scheme can detect attracting non-atom candidates. Detection depends on how the field is coded, and on whether capture is complete before beta |F'| Delta-tau exceeds the stability bound. The text claims a scheme property, and Limitations repeats it: "a positive control shows that the fixed-step scheme of the stress test detects an attracting tie". As stated, that claim is not supported.

The theorems themselves are unaffected, because they are proved. What is weakened is the empirical claim in contribution 6.

**Suggestion.** Choose one of three fixes:
1. Rerun the stress-test arms with the stiff integrator and the proof-derived stopping rules already used for the composite (Radau plus barrier checks), and use that as the control.
2. Report the mechanism honestly: capture before instability plus floating-point symmetrisation. Then state for which stiffness the conclusion holds.
3. At minimum, reconcile this paragraph with the Appendix E.2 statement that fixed-step RK4 "ejects the trajectories an attracting tie holds".

### W2: Headline claims rest on three results the authors say they have not yet checked themselves
**Severity**: Minor
**Evidence Anchor**: text: Use of large language models "the authors' own line-by-line check of these three proofs is not yet complete"
**Confidence**: 4 — I verified the three proofs and found them correct

**Problem.** Corollary twofields supports an abstract sentence ("every fixed combination of two such fields"). Proposition twoatom supports the abstract's sign rule and contribution 4. Remark generic supports the claim of hyperbolicity for almost every choice of priors. The caveat appears only in the LLM-use statement, not next to these results.

**Assessment.** My independent check (S6) found all three correct, so the decision impact is small.

**Suggestion.** Before final submission, finish the authors' own line-by-line check and update the statement. Until then, place the caveat next to the three results.

### W3: The threshold symbol w_c carries three different values
**Severity**: Minor
**Evidence Anchor**: table: Table 9 (notation), row "w, w_c=1/sinh^2 B; threshold of Theorem composition" against the triangle and simplex rows of Table 6 and the caption of Figure 2
**Confidence**: 5 — direct reading and recomputation

**Problem.** The notation table fixes w_c = 1/sinh^2 B. But:
- Figure 2 (the triangle at B = 2), Section 4.5 ("1.368 w_c"), Section 6 and Tables 6 and 8 use w_c = (1-m^2)/m^2 = 1.160 for the triangle and 4.802 for the simplex.
- Appendix E.2 uses w_c(B_Q).

A reader who uses the notation table on Figure 2 would take w = 2 w_c to mean 0.152 instead of 2.32. That misreads the figure by a factor of about 15.

**Suggestion.** Define w_c^spec once and use it consistently, or define w_c locally in every caption.

### W4: The abstract states the spectral criterion without its hypotheses
**Severity**: Minor
**Evidence Anchor**: text: Abstract "in any dimension the eigenvalue signs of a signed posterior covariance decide it"
**Confidence**: 4 — direct comparison with the statement of Theorem spectral

**Problem.** Theorem spectral(c) decides Pr(X_1 = z) > 0 only when every profile is hyperbolic and the face condition holds. The nonhyperbolic and degenerate-face cases remain open, as Limitations says. The abstract drops both qualifiers.

**Suggestion.** Add "at hyperbolic profiles (generic in the priors)" or an equivalent qualifier.

### W5: Proposition regular(b) speaks of initial points but controls the flow only from t_0
**Severity**: Minor
**Evidence Anchor**: text: Proposition regular(b) "is the limit of at most one initial point"
**Confidence**: 4 — reading of the statement against its proof

**Problem.** In (b), v_theta is only continuous and locally Lipschitz on [0, t_0). Solutions from time 0 may blow up before t_0, and the proof sidesteps this by redefining v_theta(x, t) = v_theta(x, t_0) for t < t_0. So "initial points" effectively means states at t_0. The "nonempty open interval" conclusion at time 0 needs the flow from 0 to t_0 to be defined on all of R, or at least to reach the preimage interval.

**Suggestion.** Either state (b) for states at t_0, or add a linear-growth assumption on [0, t_0], which the MLPs in question satisfy.

### Detailed comments

**Limits as t -> 1.** Every theorem that claims an endpoint law obtains it from convergence of every trajectory plus dominated convergence, and not from finite-time marginals. The one formal (unproved) passage to the limit is the near-threshold law in Appendix B.6, and it is clearly labelled as formal.

**Finite time versus limit in the numerics.** The text consistently calls exact-field computations finite-time checks. Learned occupancies are measured at a cutoff and interpreted through Proposition regular(a), whose bounded-Lipschitz networks have atomless endpoint laws. That framing is appropriate.

**Statistical reporting.** This is not a hypothesis-testing paper. The CIFAR-10 slope interval reproduces: from 0.34, 0.32 and 0.43, the t(2) 95% interval is [0.218, 0.509], against the reported [0.22, 0.51]. Population standard deviations are declared. None of the bounded recompute procedures applies.

### Questions for authors

1. Does the stress test's `novelty_interventions.py` oracle compute logits from |x - t a|^2 / eps^2, as the transcription does? If so, would a non-atom sink in those arms be detected at all if capture were not complete before the step size became unstable?
2. In Remark generic, should "almost every" be read as Lebesgue measure on P_N^+ for each fixed choice of the other priors and the coefficients?

## Arithmetic Receipts

no_recomputable_statistics: checked every reported test statistic, mean, SD, df and N in Sections 3 and 6 and Appendix E (variance ratios, OLS and HC3 slopes, t-interval, occupancy fractions); none is a test statistic with df and p, a discrete-scale mean or SD, or a df-to-N claim, so p_from_test_statistic, grim, grimmer and n_from_df do not apply
