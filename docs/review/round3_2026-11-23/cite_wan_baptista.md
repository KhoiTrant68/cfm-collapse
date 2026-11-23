# Citation check: Wan et al. (2025) and Baptista et al. (2025)

Repo: cfm-collapse, branch paper-split-drafts, commit 834f3bf. Read only; nothing edited.
Paper A = paper_theory/main.tex. Paper B = paper_mechanism/main.tex.
Sources read with pdftotext:
- Wan et al., ICML 2025, PMLR v267 (the version in refs.bib).
- Wan et al., arXiv 2412.18730v4 (3 June 2025).
- Baptista et al., arXiv 2501.15785v2 (18 March 2025). This is the version refs.bib cites.

## 1. Wan et al.: which theorem?

Terms first.
- "Endpoint law": the probability law of where the flow ends at t = 1 when the start point is drawn from the Gaussian source.
- "Atomic law": a law that puts all its mass on finitely many points ("atoms"), e.g. sum_i a_i delta_{x_i}.
- "Almost every": all start points except a set of volume zero.

Numbering is the same in PMLR v267 and arXiv v4:
Assumption 5.2, Theorem 5.3, Theorem 5.4. No renumbering.

Theorem 5.3 (PMLR p. 7; arXiv v4 p. 11–12), verbatim:
"For p satisfying Assumption 5.2, we have
1. Psi_1(x) := lim_{t->1} Psi_t(x) exists for x in R^d a.e.
2. Psi_1 is a measurable map and (Psi_1)_# p_prior = p."
Item 1 says almost every trajectory converges. Item 2 says the endpoint law is the data law p.

Assumptions of Theorem 5.3:
- Assumption 5.2: p has a finite second moment; the support of p has positive reach;
  and a local mass bound p(B_r(x)) >= C_R r^k.
- Right after Assumption 5.2 the paper says: "Any discrete distribution satisfies the assumptions with k = 0."
- Standing setup (Section 2.1): the prior p_prior is the standard Gaussian N(0, I);
  the path is N(alpha_t x, beta_t^2 I) with smooth schedules. Linear alpha_t = t, beta_t = 1 - t is named as a case.
  This matches our setup: pi_0 = N(0, I_d) and the linear interpolant.

Theorem 5.4 is NOT the right one. It only gives convergence RATES
("When p is supported on a submanifold or a discrete set, we have the following convergence results").
Its discrete case, p = sum_i a_i delta_{x_i}, gives |Psi_1(x) - Psi_t(x)| = O(sigma_t).
It says nothing about the endpoint law. It does show the authors treat general weights a_i.

Non-uniform weights: yes, covered.
Theorem 5.3 holds for "any discrete distribution", with any positive weights.
So it covers p = sum_i p_i^{(h)}(y) delta_{x^i}. With h > 0 every p_i^{(h)}(y) > 0.

Fair for thm:endpoint? Yes.
At a fixed query y, the label-noise field is the exact flow-matching field of that weighted atomic law
(A says this; it is Bayes' rule with prior p_i^{(h)}(y), and it matches Wan's posterior formula, Section 2.1, eq. (3)).
Theorem 5.3(2) applied to that law gives eq. (endpoint) directly.
Theorem 5.3(1) even gives more: almost every trajectory converges.
A also has its own short proof (coupling + continuity equation), so "cf." is the right tone.
Recommended: "cf. Wan et al., 2025, Theorem 5.3 (with Assumption 5.2)".

A's related-work sentence (line 368–369) is accurate:
"prove for flow-matching ODEs, finite data included, that almost every trajectory converges and that the endpoint law is the data law."
Theorem 5.3 items 1 and 2 say exactly this. Finite data is included via "Any discrete distribution ... k = 0".
One small precision you may add: the source is the standard Gaussian.

## 2. Baptista et al.: what each number says

Theorem 6.4 (arXiv v2, Section 6.3, p. 39), verbatim start:
"Let y^j be an element of the marginal data set {y^n}. Then, the score function that minimizes the empirical loss function (6.6) ... has the form
s^N(x, y^j, t) := (1/|I_j|) sum_{n in I_j} ..."
and it ends: "For y outside the marginal data set, the optimal s^N(x, y, t) is undefined."
- I_j is the set of training examples that share the label y^j (Definition 6.2).
- Definition 6.2 sets the empirical conditional law to "a sum of equally weighted Dirac masses" on I_j.
- Setting: diffusion score matching (VE / VP processes), not flow matching. It is about the minimiser (the field), not the endpoint.
- The endpoint for conditional sampling is only stated informally after the theorem ("will also exhibit the memorization behavior shown in Section 4"). It is not a theorem.
- Their main convergence result (Theorem 4.3) only says limit points are data points or on Voronoi-cell boundaries.
  That almost every start point reaches a data point is a conjecture there (Section 4.2 and Section 7).

Example 4.4 (arXiv v2, p. 14), summary:
Variance-exploding reverse ODE, N = 2 points in d = 2, placed symmetrically (x^1 = -x^2 on the horizontal axis).
A start point on the vertical axis stays on it and goes to the origin, "This is not a data point".
That start points off the axis reach a data point is shown only numerically (Figure 3), not proved.

## 3. Table

| Location | What our paper claims | What the source says | Verdict | Suggested citation text |
|---|---|---|---|---|
| A:204 (contributions item 1) | label-noise endpoint law is not new; "the endpoint result of Wan et al. applies" | Wan Thm 5.3(2): "(Psi_1)_# p_prior = p", any discrete p | correct, no number | `the endpoint result of \citet[Theorem~5.3]{wan2025elucidating} applies` |
| A:220 (contributions item 2) | the hyperplane exceptional set; "the planar case is Example 4.4 of Baptista" | Baptista Ex. 4.4: VE ODE, N=2, d=2, symmetric points; on-axis start goes to origin, "not a data point" | correct (number confirmed) | keep; optionally `the planar symmetric case is Example~4.4 of \citealp{baptista2025memorization}` |
| A:255–256 (Technique; FLAG) | for one field, the null set "follows from the known marginals of the flow (cf. Wan)" | Wan Thm 5.3: Psi_1 exists a.e. and pushes the Gaussian prior to p | correct; number is 5.3, not 5.4 | `the flow \citep[cf.][Theorem~5.3]{wan2025elucidating}`; delete the FLAG |
| A:349–350 (Related work; FLAG) | Baptista "identify the empirical conditional law on the subset sharing a label" | Def. 6.2 (equal Diracs on I_j) and Thm 6.4 (optimal score at y^j is the average over I_j) | correct; 6.4 confirmed in v2 | `\citet[Definition~6.2 and Theorem~6.4]{baptista2025memorization} identify ...`; delete the FLAG |
| A:368–369 (Related work) | Wan prove, finite data included, a.e. convergence and endpoint law = data law | Wan Thm 5.3 items 1–2; "Any discrete distribution satisfies the assumptions with k = 0" | correct | `\citet[Theorem~5.3]{wan2025elucidating} prove for flow-matching ODEs from a Gaussian source, finite data included, ...` |
| A:420 (Setup) | at h = 0 the objective constrains the field only at observed labels | Thm 6.4: "For y outside the marginal data set, the optimal s^N(x, y, t) is undefined." | correct | `\citep[cf.][Theorem~6.4]{baptista2025memorization}` |
| A:496 (thm:endpoint) | endpoint law = sum_i p_i^{(h)}(y) delta_{x^i}; cf. Wan | Wan Thm 5.3(2) for the discrete law with weights p_i^{(h)}(y) > 0 | correct; covers non-uniform weights | `[Endpoint law under label smoothing; cf.\ \citealp[Theorem~5.3]{wan2025elucidating}]` |
| A:657 (after prop:hyperplane) | Baptista give this example for the VE probability-flow ODE with two points in the plane | Ex. 4.4, as above | correct | keep. Optional honest addition: "their off-axis convergence is numerical" |
| A:1829, A:1869 (comparison and table) | Wan integrate the FM ODE itself; support "compact, or of positive reach with a local mass bound; both include finite sets" | Assumption 5.2 (positive reach, local mass bound); Wan work with the FM ODE | correct | optional: `\citet[Thm.~5.3]{wan2025elucidating}` in the table header |
| B:108 (intro) | flow of the exact field ends on the training examples (list incl. Wan) | Wan Thm 5.3 with discrete p | correct | keep |
| B:246–249 (Related work) | same sentence as A:368 for Wan; same as A:350 for Baptista | as above | correct | same text as for A:368 and A:350 |
| B:400–402 (prop:collapse; FLAG) | exact field at hard conditioning is (x^i - x)/(1-t), cf. Baptista | Thm 6.4 with |I_j| = 1: the optimal score is that of one Gaussian centred on x^i (diffusion form) | correct for part (a) as "cf."; parts (b)–(d) are elementary and ours | `cf.\ \citealp[Theorem~6.4]{baptista2025memorization}`; delete the FLAG |
| B:411–412 | without the label the exact flow ends on the full empirical law | Wan Thm 5.3(2), uniform discrete p | correct | `(cf.\ \citealp[Theorem~5.3]{wan2025elucidating})` |
| B:429 | Bayes' rule written in the posterior-mean form used by Wan | Wan Sect. 2.1 eq. (3) and Sect. 3.1: field via posterior p(dx_1 / X_t = x), denoiser | correct | keep |
| B:431, B:439–445 (thm:endpoint; FLAG) | as A:496; "compare the endpoint results of Wan for FM ODEs with finite data" | Wan Thm 5.3 (not 5.4; 5.4 is rates only) | correct | `cf.\ \citealp[Theorem~5.3]{wan2025elucidating}`; delete the FLAG |
| B:2100–2101 (class labels) | class-conditional law is the empirical law of the class (Baptista); its endpoint law is that law (Wan) | Def. 6.2 / Thm 6.4 give the uniform law on I_j; Wan Thm 5.3 gives the endpoint | correct; the split of credit is right | `(cf.\ \citealp[Theorem~6.4]{baptista2025memorization})` and `(cf.\ \citealp[Theorem~5.3]{wan2025elucidating})` |

Things I could not settle:
- The A FLAG at 349 asks for the "published version" of Baptista et al. Both refs.bib files cite arXiv v2, and I checked v2. I have no journal version, so I cannot confirm its numbering.
- I did not verify Wan's proof, only the statement and its assumptions.

## 4. Short summary for a newcomer (Vietnamese)

- Wan et al. chung minh mot dinh ly (Dinh ly 5.3, cung so trong ban ICML va ban arXiv v4).
  No noi: neu bat dau tu nhieu Gauss va chay dong chay flow matching chinh xac, thi gan nhu moi quy dao deu hoi tu,
  va diem cuoi co dung phan phoi cua du lieu.
- Dinh ly nay dung cho moi phan phoi roi rac, ke ca khi cac diem co trong so khac nhau.
  Vi vay no ap dung truc tiep cho dinh ly thm:endpoint (trong so lay tu nhieu nhan).
- Dinh ly 5.4 chi noi ve toc do hoi tu, nen khong phai so can trich.
- Cau trong phan Related work cua A ve Wan et al. la dung.
- Baptista et al., Dinh ly 6.4 (ban arXiv v2): truong toi uu tai mot nhan da thay chi dung cac anh mang nhan do,
  va khong xac dinh tai nhan chua thay. Cach trich cua chung ta dung, nhung day la mo hinh khuech tan, khong phai flow matching.
- Vi du 4.4 cua Baptista: hai diem du lieu doi xung trong mat phang; diem bat dau tren duong trung truc di ve trung diem, khong phai diem du lieu.
  Cach trich trong A dung.
- Viec can lam: thay "cf." bang "cf. Theorem 5.3" cho Wan, them "Theorem 6.4" cho Baptista, va xoa cac dong FLAG.
