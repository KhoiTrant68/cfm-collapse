# Proof audit 1 (round 3): cor:twofields, prop:twoatom, rem:generic

Repo: cfm-collapse, branch paper-split-drafts, commit 834f3bf, file paper_theory/main.tex.
All line numbers refer to that file. Nothing in the repo was edited.

Notation used below. A "prior" p is a probability vector on the N atoms a_1..a_N (distinct).
P_pos is the set of priors with all entries positive. v_p is the exact field of the coupling
I ~ p (eq. prior-field, line 552-558). In the time tau = -log(1-t) every field reads
dx/dtau = mbar - x. beta = t/(1-t)^2. For a non-atom candidate z, S = nn(z) is its set of
nearest atoms and r = dist(z, atoms).

What I read: setup and as:standing (398-428), Prop projection/collapse/kernel-field and
Lemma mixture-coupling (447-489, 1611-1637), Lemma wellposed (1554-1609), notation and
Lemma basic (1886-1980), Lemmas conv and volume (1982-2067), Thm posmix proof (2070-2154),
Lemma signedconv (2230-2299), Thm schedule proof (2301-2368), Cor twofields proof
(2370-2382), Prop bottleneck (2390-2422), Prop cfgatom proof (2435-2498), Section spectral
(859-967), Lemma offtie, Lemma LP and Thm spectral proof (2682-2961), Prop twoatom and its
proof (994-1043, 3005-3062).

I also ran a numerical check of Prop twoatom (random B-values and coefficients; script at
scratchpad/agents/round3/twoatom_check.py). Results are reported under Prop twoatom.

---------------------------------------------------------------------------------------------

## 1. Corollary cor:twofields (statement 735-741, proof 2370-2382)

Verdict: sound. The issues are about scope sentences in the main text, not about the proof.

How the proof works. For 0 <= c <= 1 the field is a positive mixture, so Thm posmix applies.
For c > 1 or c < 0 it is rewritten as (1+w) v_p - w v_q (or with p, q swapped) with a constant
w > 0. Both rewrites are correct: for c < 0, (1-c) v_q + c v_p = (1+w) v_q - w v_p with w = -c.
The schedule case is Thm schedule with p, q in place of p^(h)(y), p^unc.

I checked every step of the chain Lemma signedconv -> Lemma conv -> Thm schedule ->
Lemma volume, with the two priors arbitrary in P_pos:

- Well-posedness (2243-2247): D_x v_c is bounded on R^d x [0,T] for T < 1, so Caratheodory
  solutions exist and are unique. Correct.
- Energy (2249-2284): the chain rule for h_k = H_{p_k}(x, t, alpha), the bound
  |r_k| <= R^2 eps/2 + log(1/p_min) |alpha'|, and the integrability of |alpha'| (alpha
  decreases to 0) are correct. The integration by parts against the BV coefficient is correct
  because h_k is continuous. The bound |h_k| <= XR + R^2/2 uses only boundedness of the
  trajectory. Correct. This is the only place where p_min > 0 is needed.
- Concentration hypothesis of Lemma conv (2286-2298): correct, the signed weights sum to one
  and the off-tie weights vanish by Lemma basic(c).
- Lemma conv (1989-2026): the omega-limit / passage argument is correct; C' is finite by
  Lemma basic(d), which I checked.
- Theta identity (2320-2341): tr Cov = r^2 - |m_p - z|^2 + e_p with e_p >= 0 is correct because
  all atoms of S are at distance r. The algebraic identity
  (1+w)|u|^2 - w|v|^2 = |(1+w)u - wv|^2 - w(1+w)|u-v|^2 is correct (I expanded it). With
  w(t) in [0, wbar] the bound Theta >= r^2 - |mu_w|^2 - wbar e_{p_u} holds pointwise in time.
- Divergence estimate (2343-2366): the ratio bound beta(n+1)/beta(n) <= C_beta and the
  per-interval bound (1/2) r^2 beta(n) are correct; the sum diverges.
- Lemma volume (2028-2067): Liouville + Fatou argument is correct, given Liouville's formula
  for Caratheodory fields (see issue 4).

Counterexample attempts that failed (as they should): N = 2, d = 1, every pair of B-values
with any real c; equilateral triangle at its circumcentre (at a profile mu_w = 0, so
tr Gamma >= r^2 > 0 and the basin is null). I found no configuration with p, q in P_pos where
a non-atom candidate keeps positive mass.

Issues

1. main.tex:743-747. Step: "Guidance towards one condition with another as the base, and
   negative prompting ... are combinations of two exact fields as well, so none of them moves
   the endpoints off the training examples." Why it may fail: the corollary needs p, q in
   P_pos. At hard labels (h = 0) the priors are e_i, not in P_pos, and the claim is false.
   Counterexample: N = 2, c = 2, p = e_1, q = e_2. The field is ((2a_1 - a_2) - x)/(1-t), whose
   solution is x_t = (1-t) x_0 + t (2a_1 - a_2). Every source ends at 2a_1 - a_2, which is not
   an atom. Severity: presentation (the formal statement is correct; the gloss overreaches).
   Fix: add "with strictly positive priors, for instance at any h > 0" and "almost surely".

2. main.tex:994-995. Step: "Corollary~\ref{cor:twofields} rules out every combination of two."
   Same scope problem as issue 1 (hard-label fields are excluded). Severity: presentation.
   Fix: "every combination of two fields with strictly positive priors".

3. main.tex:739-740 and 743-746. Step: the schedule part covers only (1+w(t)) v_p - w(t) v_q
   with w(t) >= 0. A time-varying coefficient c(t) that moves between [0,1] and (1, inf), for
   example a negative-prompt scale s(t) that crosses 1, is not covered: Lemma signedconv still
   gives convergence to C', but the volume step of Thm schedule uses w(1+w) >= 0 and fails for
   w(t) in (-1, 0). The text at 743-746 does not say whether s is constant. Severity:
   presentation. Fix: say "constant s, or s(t) = 1 + w(t) with w as in Theorem schedule".

4. main.tex:1971-1980 (used through Lemma volume). Step: Liouville's formula and C^1 flow maps
   for fields that are only measurable in time (needed when w is BV, not continuous). The
   paragraph gives an outline and cites Hale Ch. I. The result is standard, but the cited
   chapter treats continuous fields. Severity: gap (minor, standard). Fix: cite a
   Caratheodory reference for differentiability of the flow (e.g. Hale Ch. I, Sec. 3 if it
   covers it, or a control-theory text on Caratheodory ODEs; I did not verify a theorem
   number). A BV schedule can have countably many jumps, so "continuous in time" cannot be
   assumed; a reference is the clean fix.

5. main.tex:735-741. Step: "unique trajectories" for the schedule part means Caratheodory
   trajectories (as in Thm schedule, line 721). Severity: presentation. Fix: say
   "unique Caratheodory trajectories" for the second sentence.

Statement match: \cortwofields* restates the main-text statement verbatim (restatable).

---------------------------------------------------------------------------------------------

## 2. Proposition prop:twoatom (statement 1007-1021, proof 3005-3062)

Verdict: sound, conditional on Thm spectral (c). I checked the parts of Thm spectral that it
uses and found no error. There are presentation issues in the statement and a real inaccuracy
in the prose gloss "less decided".

Reduction (3010-3028). With nu = (a-b)/2 and zeta = <xi, nu>, the tilted two-point law gives
E[a] = z + nu tanh(zeta + B_k), so M - z = nu F(zeta) and Gamma = F'(zeta) nu nu^T. Correct.
Grouping equal B_k changes neither F nor Gamma. Correct. The face condition holds for |S| = 2.
Correct. F tends to +1 and -1 at +inf and -inf (coefficients sum to one), so its zeros lie in a
compact set; this agrees with the finiteness proved in Thm spectral (c).

(a) (3036-3044). The quadratic trick is correct: with q(x) = (x - m_-)(x - m_+), the two
linear constraints give sum c_k q(m_k) = V + m_- m_+, and nonnegative inner coefficients give
V <= -m_- m_+ < 1. I re-derived it independently. Correct.

(b) (3046-3056). I checked each inequality: c_1 m_1 = |c_2| m_2 + |c_3| m_3 <= (c_1 - 1) m_2
< (c_1 - 1) m_1 gives m_1 < 0; then V = |c_2| m_2 (m_1 - m_2) + |c_3| m_3 (m_1 - m_3) < 0.
Correct. A shorter proof: use q(x) = (x - m_2)(x - m_3), which is >= 0 at m_1, so c_1 <= 0
gives V <= -m_2 m_3 < 1; symmetric for c_3 <= 0.

(c) (3058-3061). The closed form F_w = 2 tanh s (cosh^2 s - w sinh^2 B)/(cosh 2s + cosh 2B) is
correct (I expanded it). Zeros: s = 0 always; s = +-s_u with cosh^2 s_u = w sinh^2 B when
w > 1/sinh^2 B, and these are simple zeros with F' > 0. F_w'(0) = (1+w) sech^2 B - w < 0 iff
w > 1/sinh^2 B. At w = 1/sinh^2 B the only profile is 0 with F' = 0 (nonhyperbolic), which
does not count as "F' < 0". So "exactly when" is correct.

Use of Thm spectral. "F' > 0 at every profile" makes every profile hyperbolic with a positive
eigenvalue; part (c) then says every trajectory converging to z converges in profile to one of
finitely many profiles, and part (b) makes each profile basin null. I read the proofs of
Lemma offtie, Lemma LP and Thm spectral (a)-(c). The no-escape argument (potential Psi with
dPsi/dsigma >= |G|^2/2 outside a ball, Psi = O(|xi|) = o(sigma)) and the convergence of the
profile (integral of |G|^2 finite, G uniformly continuous) are correct as far as I can tell.

Numerical check (my script): random B-values and coefficients summing to one, K = 2..5 groups;
no profile with F' < 0 was found whenever the hypothesis of (a), or of (b) with K = 3, held.
(c): F' at the profiles is negative only above w_c. See section 4 for the run's output.

Issues

1. main.tex:1010 (statement) vs 997 (prose). Step: "at the midpoint z of a tie of two atoms".
   The proof needs nn(z) = {a, b} exactly (|S| = 2). If a third atom is at the same distance
   (e.g. the centre of a square, which is the midpoint of both diagonals), S has four points,
   the one-dimensional reduction is wrong, and the proposition says nothing. The prose at 997
   states nn(z) = {a,b} but the proposition does not. Severity: presentation. Fix: put
   "with nn(z) = {a, b}" in the statement.

2. main.tex:1015. Step: "With three distinct values B(p_1) > B(p_2) > B(p_3)". It must mean
   exactly three groups after grouping; the proof uses only three m_k. Severity: presentation.
   Fix: "If, after grouping, there are exactly three values ...".

3. main.tex:1013-1014, 1016. Step: "Pr(X_1 = z) = 0". The law is not named. Thm spectral gives
   a Lebesgue-null basin, so it holds under pi_0 and every absolutely continuous source.
   Severity: presentation. Fix: "under pi_0 (indeed under every absolutely continuous source)".

4. main.tex:1007 (title), 1023-1024. Step: "Blending two examples needs a subtracted, less
   decided field" and "a subtracted field that is less decided between them than the fields it
   is subtracted from". What (a) proves is that the subtracted field must have B strictly
   between the extreme B-values, not that it is less decided (|B| smaller). Counterexample to the
   gloss: B-values 3, 2, 1 (every field favours a), coefficients (1+w)/2, -w, (1+w)/2 with
   w > 1/sinh^2(1). Shifting zeta by -2 maps this to the conjunction with B = 1, so
   zeta_* = -2 is a profile with F' < 0 and the midpoint has positive probability by Thm
   spectral (a). Here the subtracted field (B = 2) is MORE decided than the B = 1 field it is
   subtracted from. Severity: presentation (the proposition is right; the title and the sentence
   misdescribe it). Fix: say "a subtracted field whose log-odds lie strictly between those of
   added fields" (an "intermediate" field), and keep "less decided" only for the symmetric
   case B, 0, -B.

5. main.tex:1035-1036. Step: "Conditions (a) and (b) are necessary, not sufficient". Read
   literally, (a) and (b) are sufficient conditions for Pr = 0; what is necessary for a blend is
   that their hypotheses FAIL. Severity: presentation. Fix: "The sign patterns excluded by (a)
   and (b) are necessary for a blend, not sufficient".

6. main.tex:1038-1041 (consequence, not the proposition itself). Step: "probability 0 for
   smaller w" on the simplex edge midpoints. Correct for w strictly below the threshold
   N/(2 tanh^2(B/2)) - 1 (one profile, F' > 0, or (a) when 2(1+w)/N - 1 < 0). At the threshold
   itself the profile is nonhyperbolic and nothing is proved; the text says "smaller", so it is
   fine. I checked the threshold algebra and the value 1.368 w_c for N = 3, B = 2. No issue,
   noted only because it relies on (c) and on nn(edge midpoint) = {a,b}, which holds for a
   regular simplex.

Statement match: \proptwoatom* restates the main-text statement verbatim (restatable).

---------------------------------------------------------------------------------------------

## 3. Remark rem:generic (947-967; no appendix proof)

Verdict: sound with a fixable gap. The mathematics of the remark is correct. The sentence that
introduces it (943-944) claims more than the remark shows.

Checked steps.
- P_L S = P_L z + (S - z) is a translate of S, since a - z is in L for a in S. Correct. So the
  face condition of Thm spectral (c) is the same as "z is in the affine hull of no proper face
  of conv S". Correct.
- |S| = 2: z is the midpoint, the proper faces are the two endpoints (and the empty face).
  Correct.
- z in the relative interior of conv S: every proper face of a polytope is exposed, hence lies
  in a supporting hyperplane of conv S inside aff S, which misses the relative interior.
  Correct. (All points of S lie on a sphere around z, so all are vertices of conv S.)
- The experiment configurations (triangle, regular simplex, rectangle, box with z the centre;
  edge midpoints; face centroids of the simplex and box, lines 1260-1292) all have z in the
  relative interior of conv S or |S| = 2. Correct.
- Derivative dG/d eta_{k,a} = c_k pi_k(xi)(a) (a - E_{pi_k} a). Correct.
- Spanning: the vectors pi(a)(a - mu), a in S, sum to zero and have positive weights, so the
  span of those with a != a_0 equals span{a - mu : a in S} = span of differences of S = L
  (z in aff S). Correct. Some c_k != 0 because the c_k sum to one.
- Parametric transversality (G smooth, D_eta G onto L, parameter space R^{K(|S|-1)} without
  boundary): for almost every eta, 0 is a regular value of G(.; eta), i.e. every profile is
  hyperbolic. Correct.
- The log-ratio map (P_pos)^K -> R^{K(|S|-1)} is a submersion, and preimages of null sets
  under a submersion are null. Correct.

Issues

1. main.tex:943-944. Step: "Nonhyperbolic profiles and faces whose affine hull contains P_L z
   are not covered; Remark~\ref{rem:generic} shows that both are exceptional." The remark shows
   hyperbolicity is generic in the priors. It does NOT show that the face condition fails only
   exceptionally; it only gives sufficient conditions (|S| = 2, or z in the relative interior).
   The face condition can fail: atoms (1,0), (-1,0), (0,1) in R^2 with z = 0 (a right
   triangle) have nn(z) = S, z in aff S, and z on the edge between (1,0) and (-1,0). Failure
   needs the circumcentre of S to equal the circumcentre of a proper subset, which is a
   non-generic condition on atom positions, but this is not proved. Severity: gap
   (overclaim in prose). Fix: either write "the remark shows the first is exceptional in the
   priors and the second does not occur in our configurations", or add a one-line argument that
   for atoms in general position (no circumcentre of a subset of size >= 2 lies in the affine
   hull of a smaller subset with the same circumcentre) the face condition holds, and state it as
   genericity in the atom positions.

2. main.tex:954-964. Step: "Hyperbolicity is generic in the priors ... for almost every choice
   of (p_1,...,p_K) in (P_pos)^K". In every application one prior is FIXED: guidance uses the
   uniform unconditional prior. A statement "almost every K-tuple" does not by itself give
   "almost every choice of the conditional priors with p^unc uniform": the slice at a fixed p^unc
   is a null set of the product and could be entirely bad. The argument in fact proves the
   stronger statement, because it only needs one k with c_k != 0 to vary ("For any k with
   c_k != 0 these vectors span L"). Severity: presentation (fixable by restating). Fix: state
   "for any fixed priors p_k, k != k_0, and almost every p_{k_0} in P_pos, where c_{k_0} != 0,
   every profile is hyperbolic"; this covers guidance with a uniform unconditional prior.

3. main.tex:954-966. Step: the genericity statement is for one fixed candidate z (S and L
   depend on z). Pr(X_1 = z) for all non-atom candidates at once needs a union over z.
   C' is finite (Lemma basic(d)), so the union of null sets is null. Severity: presentation.
   Fix: add "since C' is finite, the same holds at every non-atom candidate simultaneously".

4. main.tex:964-966. Step: "Nonhyperbolic profiles, such as the threshold w = w_c of
   Theorem~\ref{thm:composition}, are therefore exceptional". Exceptional in the priors, at
   fixed coefficients. Thm composition's priors are a special symmetric family (p^(h)(+-u0) and
   uniform), and inside that family nonhyperbolicity happens at w = w_c, a single value of w.
   Nothing wrong, but the reader may read "exceptional" as "exceptional in w". Severity:
   presentation. Fix: "exceptional in the priors (and, in Theorem composition, occur only at
   w = w_c)".

5. main.tex:947-967. The remark has no appendix proof and no \proofin; it is effectively a
   proposition with proof inside a remark. Severity: presentation. Fix: either promote it to a
   lemma with the proof in the appendix next to Thm spectral, or keep it a remark but cite
   Guillemin-Pollack with the exact theorem name ("Transversality Theorem", Ch. 2, Sec. 3).

---------------------------------------------------------------------------------------------

## 4. Numerical check output

Script: scratchpad/agents/round3/twoatom_check.py (grid zeta in [-40, 40], step 2e-4).

- 20000 random trials (2 to 5 groups, B ~ N(0, 9), coefficients ~ N(0, 9) then normalised to
  sum one): 0 profiles with F' < 0 when the hypothesis of (a) holds; 0 when K = 3 and the
  hypothesis of (b) holds.
- (c), B = 0.5, 1, 2 and w/w_c = 0.5, 1, 1.01, 3: min F' at the profiles is positive at 0.5,
  zero (up to 1e-16) at 1, and negative at 1.01 and 3. Matches "exactly when w > 1/sinh^2 B".
- Gloss counterexample (section 2, issue 4): B = 3, 2, 1 with coefficients (1+w)/2, -w,
  (1+w)/2 and w = 2/sinh^2(1): F(-2) = 0 and F'(-2) = -0.42 < 0, a sink profile although the
  subtracted field is not the least decided one.

The grid check is a sanity check, not a proof; profiles closer than the grid step would be
missed.

---------------------------------------------------------------------------------------------

## Lines a human must read carefully (for Khoi)

- 2320-2341: the Theta identity in Thm schedule; it is the only place where w >= 0 is used,
  and it is what makes every two-field combination safe.
- 2266-2284: integration by parts against a BV schedule in Lemma signedconv; check the
  right-continuous modification and that the energy bound does not depend on tau'.
- 1971-1980: Liouville's formula for Caratheodory (time-measurable) fields is asserted in
  outline; confirm a reference that covers measurable time dependence.
- 743-747 and 994-995: the prose extends Cor twofields to all two-field recipes; it is false at
  hard labels (counterexample in section 1, issue 1).
- 1007-1024: Prop twoatom title and gloss say "less decided"; the proof shows "strictly between".
  Counterexample B = 3, 2, 1 in section 2, issue 4.
- 3036-3056: the quadratic and sign arguments of Prop twoatom (a), (b); short and correct, but
  they carry the whole sign-pattern claim.
- 2925-2960: the no-escape and profile-convergence argument of Thm spectral (c), on which
  Prop twoatom's "Pr(X_1 = z) = 0" rests.
- 943-944 vs 947-967: the claim that faces through z are "exceptional" is not shown by the
  remark (right-triangle example in section 3, issue 1).
- 954-964: genericity is stated jointly in all priors; applications fix the unconditional
  prior. The proof supports the stronger per-prior statement; the text should say so.
