# Proof audit 2 (round 3)

Repo: cfm-collapse, branch paper-split-drafts, commit 834f3bf. Read-only audit.
Paper A = paper_theory/main.tex. Paper B = paper_mechanism/main.tex.
Numerical checks: `audit2_checks.py` in this folder (run with `python3 -I`).

Method. For each target I listed the facts the conclusion needs, traced each to the line that proves it,
and tried small counterexamples (N=2 or 3, d=1 or 2, sign patterns of coefficients, Heun ratios near the
cutoffs). Main-text and appendix statements are `restatable` copies, so they agree verbatim for all six
targets.

---

## Paper A

### 1. Remark rem:generic (A:947-967)

**Verdict: sound, with presentation fixes. The text that cites it claims more than it proves.**

What the remark needs, and where each fact comes from:
- P_L S is a translate of S. Since a-z lies in L for a in S, P_L a = P_L z + (a-z). Checked; correct.
- The face condition holds when |S|=2. z is then the midpoint, and the proper faces are the endpoints. Correct.
- The face condition holds when z is in the relative interior of conv S. The affine hull of a proper face lies in
  a supporting hyperplane (inside aff S), and that hyperplane misses the relative interior. Correct.
- The derivative of G with respect to eta_{k,a} is c_k pi_k(xi)(a)(a - E_{pi_k}[a]). Checked; correct.
  These vectors lie in L. With the a_0 vector they sum to zero. Dividing by pi_k(a)>0 gives every a - mu,
  so their span contains all differences of points of S. That span is L because z is in aff S. Correct.
- G is jointly smooth (analytic), so parametric transversality applies: for almost every eta, 0 is a regular
  value of G(.;eta), that is, Gamma is invertible at every profile. Correct.
- The log-ratio map from the open simplex to the restricted log-ratios is a submersion. So the preimage of a
  null set is null. Correct.

Counterexample attempts. A right triangle (z on the hypotenuse) breaks the face condition. The remark does not
claim otherwise. An obtuse triangle (z outside conv S) still satisfies the face condition. That case is not
mentioned but does no harm. All test configurations (triangle, 9-simplex, rectangle, box centres; edge
midpoints; face centroids) have z in the relative interior of conv S or |S|=2. So "covers every configuration
of Section intervention-tests" (A:953-954) holds.

Issues:
1. A:944 ("Remark~\ref{rem:generic} shows that both are exceptional") and A:1351-1352 ("The latter are
   exceptional"). **Gap (overclaim).** The remark proves that nonhyperbolic profiles are exceptional in the
   priors. For faces through P_L z it proves only two sufficient conditions. It does not show that such faces
   are exceptional. The remark itself says that case "remains open" (A:966-967).
   Fix: say "Remark shows that nonhyperbolic profiles are exceptional, and that the face condition holds when
   |S|=2 or z lies in the relative interior of conv S". Optionally add one sentence: a face through z forces z
   to be the circumcentre of a proper sub-face as well. That is a non-generic condition on the atom positions,
   not on the priors.
2. A:955-964. **Presentation.** Genericity is over the whole tuple (p_1,...,p_K) in (Ppos)^K. The families
   the paper studies are a null set of that space: the uniform unconditional prior and the symmetric conditional
   priors. The proof needs only one free prior with c_k != 0, because the vectors of a single such k already
   span L. Fix: state "for almost every choice of any one prior p_k with c_k != 0, the others fixed". Then the
   uniform unconditional prior can stay fixed.
3. A:966 ("such as the threshold w=w_c ... are therefore exceptional"). **Presentation.** The remark proves
   genericity in the priors at fixed coefficients. It does not prove genericity in w at fixed priors. For
   dim L >= 2 the w-derivative M_av - M_u alone does not span L. So the argument does not give it. Fix: say
   "exceptional in the priors".
4. A:956-957. **Presentation (notation).** eta clashes with eta = P_{L^perp}(x-z) in Appendix A:2700.
   K (the number of fields) is used but never named. The remark also needs c_k fixed. Fix: rename the
   log-ratios (e.g. lambda_{k,a}), define K, and say "coefficients fixed".

### 2. Proposition prop:twoatom (A:1007-1021; proof A:3005-3062)

**Verdict: sound. Statement-level presentation fixes only.**

Backward chain. "Pr(X_1=z)=0" needs Theorem thm:spectral(c). That needs: (i) the face condition, which holds
for a segment (A:3030-3032); (ii) every profile hyperbolic, which follows from F'>0; (iii) every trajectory
converges, by Lemma lem:signedconv. The reduction M - z = nu F(zeta) and Gamma = F'(zeta) nu nu^T is correct.
The log-odds are 2(B_k + zeta) because <xi, a-b> = 2 zeta.
- (a) Correct. sum c_k q(m_k) = V + m_- m_+, using sum c_k = 1 and sum c_k m_k = 0. The extreme terms vanish
  whatever the sign of their coefficients. With interior c_k >= 0, V <= -m_- m_+ < 1. I also checked the
  degenerate one-value case (F' = 1) and coefficients of 0.
- (b) Correct. In the case c_2 < 0, c_3 <= 0 the chain gives m_1 < 0. Then V = |c_2| m_2(m_1-m_2) +
  |c_3| m_3(m_1-m_3) < 0. The term with c_2 is strict because c_2 < 0. The case c_1 <= 0 follows by symmetry.
- (c) Correct for every real w, not just w >= 0. F_w'(0) = sech^2 B - w tanh^2 B. The other zeros are
  +/- s_u with upward crossings.
- Numerics: 1643 random combinations (2-5 priors, B in [-4,4], Gaussian coefficients) satisfy the hypotheses
  of (a) or (b). None has a profile with F' <= 0. The triangle edge threshold ratio is 1.36781, matching
  "1.368 w_c" (A:1043, A:1276). The 9-simplex edge ratio is 1.4075, matching "1.407".
- Negative-prompt reading (A:1027-1031): coefficients (s, 1-s+s_neg, -s_neg) at B_pos > 0 > B_neg. The
  subtracted field is extreme, so (b) applies with c_3 <= 0. Correct.

Issues:
1. A:1010-1011. **Presentation.** The statement says "the midpoint z of a tie of two atoms". It does not
   require nn(z) = {a,b}. The preceding paragraph does (A:997-998). Counterexample if this is read loosely:
   take the square with corners (+/-1,+/-1). The midpoint of a diagonal is 0, but nn(0) has four atoms, so the
   one-variable reduction does not apply. Fix: write "with nn(z)={a,b}" in the statement.
2. A:1013-1014. **Presentation.** "min_k B(p_k)" and "max_k B(p_k)" should be taken after grouping, over the
   priors with nonzero coefficient. As written the statement stays true, because a zero-coefficient prior adds
   q(m_k) * 0. But it is stricter than needed.
3. A:1035. **Presentation.** "Conditions (a) and (b) are necessary, not sufficient" inverts the logic. The
   proposition gives sufficient conditions for Pr=0. Their negations are necessary for a blend. Fix: "Violating
   the hypotheses of (a) and (b) is necessary for a blend, not sufficient".
4. A:1036-1044 (the simplex edge reading). Correct: w' = 2(1+w)/N - 1, and B/2 per edge. Note that "probability
   0 for smaller w" excludes equality, which is the nonhyperbolic case. The wording is fine.

### 3. Corollary cor:twofields (A:735-741; proof A:2370-2383)

**Verdict: the corollary is sound. The sentence that glosses it in the main text is wrong as stated.**

Backward chain. For c in [0,1], Theorem thm:posmix with Pi = c delta_p + (1-c) delta_q gives convergence to
C, a subset of C'. For c > 1 or c < 0, the field is (1+w)v_{p'} - w v_{q'} with constant w > 0. Theorem
thm:schedule uses its priors only through membership in Ppos. I checked this line by line:
- In Lemma lem:signedconv, p_min > 0 bounds the KL term.
- The identity (1+w)|u|^2 - w|v|^2 = |(1+w)u - wv|^2 - w(1+w)|u-v|^2 is checked.
- e_p >= 0, and e_p -> 0 by Lemma lem:basic(c).
- The integration by parts against a BV schedule is correct.
- The bounds on unit intervals with C_beta are correct.
No step uses p_unc being uniform. Correct.

Issues:
1. A:743-747. **Gap (wrong as stated).** "Guidance towards one condition with another as the base, and negative
   prompting ... are combinations of two exact fields as well, so none of them moves the endpoints off the
   training examples." This needs strictly positive priors, that is h > 0. It is false for hard-label exact
   fields. Counterexample: N=2, h=0, p=e_1, q=e_2. Then (1+w)v_{e_1} - w v_{e_2} = ((1+w)a_1 - w a_2 - x)/eps.
   It sends every source to (1+w)a_1 - w a_2, which is not an atom when w > 0. With c=1/2 it sends every source
   to the midpoint, as the paper itself notes at A:643-645. In addition, "none moves" ignores the null
   exceptional set. Fix: "combinations of two exact fields with strictly positive priors (h>0) as well, so each
   ends on a training example almost surely".
2. A:740-741. **Presentation.** "w as in Theorem thm:schedule" imports "h>0, fix y", which does not apply here.
   Fix: "with w:[0,1)->[0, w_bar] measurable and of bounded variation on [t_0,1)".

---

## Paper B

Standing assumptions (B:386-390): fixed data, linear interpolant, distinct labels. The three targets use only
the bound |m* - a| <= (1-w_i) delta_i (B:1426-1430). That bound holds for any probability weights.

### 4. Theorem thm:relerr (B:473-490; proof B:1436-1471)

**Verdict: sound. Fixable presentation gaps in the surrounding text.**

Checked:
- (a) The radial identity and a.e. inequality. At zeros of n, n is at a minimum, so n' = 0 wherever it exists.
- (b) The substitution u = eps^{-nu} n, the integrated bound, and the kappa/nu tail.
- (c) Gronwall applied with delta^+. The sup-T argument.
- (d) The N=1 linear field. At rho=1 the hypothesis of (b) holds with gamma=0 and omega=0, yet Z stays put.
- Rates. For x_hat = a + rho_t(Z-a) with N=1: n_t = n_{t1} exp(-int (1-rho)/eps). This lands iff
  int (1-rho_s)/(1-s) ds = infinity. Example: 1-rho = 1/log(1/eps) lands, and is covered by neither (b) nor (c).
  1-rho = 0.6 eps^{1/2} does not land, which is (c). So (b) and (c) leave a gap between them. The theorem does
  not claim to cover it.

Issues:
1. B:496-497. **Presentation.** "A relative error below one keeps it [the radial ratio] below one" holds only
   where n >> gamma + omega. The radial ratio is at most rho_bar + (gamma+omega)/n, which can exceed 1 when n is
   small. "(c) is the converse" is too strong. (c) is a partial converse, and the intermediate regime above
   (radial ratio -> 1 with a non-integrable gap) lands. Fix: "(c) gives a partial converse".
2. B:494-495. **Gap (citation scope).** "omega_t -> 0 ... holds on a ball around a at late times (Proposition
   prop:trap)". prop:trap is stated for weights proportional to exp(-|x-x^j|^2/2 sigma^2), that is a uniform
   prior (B:1478). Theorem thm:relerr allows label-noise posteriors with priors p^{(h)}(y). With a prior, part
   (i) of the trapping bound needs the factor max_k p_k/p_i. The class posterior of Section edm (B:1729) is
   uniform within a class, so the EDM use is fine. Fix: either add the prior ratio to Omega, or restrict the
   sentence to uniform or within-class weights.

### 5. Proposition prop:trap (B:1480-1498; proof B:1500-1516)

**Verdict: sound for uniform-prior (and within-class) posteriors. Fixable scope gap.**

Checked:
- (i) w_k <= w_k/w_i <= exp((R^2-(g-R)^2)/2sigma^2). Also rho_R <= 1/3 when R <= g/4.
- (ii) The EDM radial identity sigma dn/dsigma = n - <e_hat, D-a>. The barrier at the largest sigma with
  n >= R: there n = R > 0, so n is differentiable, and the strict inequality gamma + Omega < nu R gives the
  contradiction. The integrated bound from d(n s^{-nu})/ds >= -h s^{-nu-1}.
- (iii) Omega <= (N-1) delta_i q^2 < (N-1) delta_i q = (1-rho_bar)R/2. The bound q <= 1/8 uses delta_i >= g.
  The constant is loose by a square, but the claim is correct.
- I checked the EDM-to-CFM correspondence t = 1/(1+sigma), Z = t x. dZ/dt = (D - Z)/(1-t). Correct.

Issues:
1. B:1477-1479. **Gap (scope).** Only uniform priors are covered (see issue 4.2). Fix: Omega ->
   (max_{k!=i} p_k/p_i) Omega, or state the restriction.
2. B:1496-1497. **Presentation.** For N=1, q divides by zero. Omega is identically 0 then. Fix: "for N >= 2".

### 6. Proposition prop:heun (B:1530-1563; proof B:1565-1593)

**Verdict: sound, with one fixable missing hypothesis in (e).**

Checked:
- (a) The coefficients r, kappa, theta. Their sum is 1. The last Euler step gives x_K = D_{K-1}.
- (b) Both bounds, term by term.
- (c) c = r + (|kappa| + theta r)rho + theta(1-r)rho^2. For r<1/2, |kappa| + theta r = theta(1-r).
  rho_crit gives c = 1 exactly (numerics: r=0.1 gives rho_crit=0.1872, c=1.0000).
- (d) c* matches a brute-force supremum over u in the d=2 disc to 5 digits (r in {0.1,0.3,0.5,0.8},
  rho in {0.2,0.6,0.95}). c* = c for r >= 1/2 and c* < c for r < 1/2. The overshoot discriminant
  (1-r)^2(r^2-6r+1) is checked, and both roots lie in (0,1) because the quadratic equals 2r at rho=1. A
  numerical sweep finds p<0 only for r < 0.1710, against 3-2 sqrt2 = 0.1716.
  d >= 2 is needed because sqrt(affine in s) is concave, so the maximum can be interior.
- (e) The induction. rho R + gamma + Omega <= R gives n_tilde <= R, so Omega bounds omega at the predictor.
  Then c R + b <= R.

Issues:
1. B:1560-1562 and B:1592-1593. **Gap (missing hypothesis).** The on-atom conclusion uses
   n_K <= rho_{K-1} n_{K-1} + gamma_{K-1} + omega. That bound needs e(x_{K-1}, sigma_{K-1}) <= rho_{K-1}
   n_{K-1} + gamma_{K-1}. Nothing assumes it: the hypotheses of (b) for k <= K-2 bound e at x_k and at the
   predictor x_tilde_k, never at x_{K-1}. rho_{K-1} and gamma_{K-1} are not even defined. (b)'s "for the last
   step" clause has the same implicit hypothesis. Fix: add "and e(x_{K-1},sigma_{K-1}) <= rho_{K-1} n_{K-1} +
   gamma_{K-1}".
2. B:1529 and B:1537-1547. **Presentation.** (b) and (c) are about the upper bound c, not the true one-step
   factor. (d) shows c* < c for r < 1/2, so "c<1 iff rho<rho_crit" is a statement about the certificate, not
   about contraction. The main text (B:981-987) reads it this way ("looseness of the bound"), which is
   consistent. One clause in the statement would avoid misreading.
3. (e) inherits the uniform-prior restriction of prop:trap(i). That is fine for EDM classes.

---

## Lines a human must read carefully

- A:743-747. Says two-field combinations never leave the atoms. This is false for hard-label (h=0) fields.
  Counterexample: (1+w)v_{e_1} - w v_{e_2} sends every source to (1+w)a_1 - w a_2. Needs "strictly positive
  priors".
- A:944 and A:1351-1352. Cite rem:generic for "both are exceptional". The remark proves this only for
  hyperbolicity, not for the face condition.
- A:955-966. Check that "generic in the priors" is meant in the full prior tuple at fixed coefficients. It is
  not genericity in w, and one free prior suffices.
- A:1007-1021. The statement of prop:twoatom should require nn(z)={a,b}. The proof is correct, and random tests
  found no counterexample.
- B:1556-1562. Heun (e) uses a relative-error bound at x_{K-1} that is never assumed.
- B:494-497 and B:1477-1479. The trapping ball assumes uniform weights, but Theorem relerr is advertised at any
  label and bandwidth. Also "(c) is the converse" is too strong: there is a landing regime between (b) and (c).
- B:1494-1497. The constant in prop:trap(iii) is correct but loose (q^2 vs q). It is undefined for N=1.
