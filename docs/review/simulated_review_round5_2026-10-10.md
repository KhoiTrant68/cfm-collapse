# Simulated review, round 5: full five-reviewer panel (ICLR 2027)

- **Manuscript**: *Trained Conditional Flows Memorise at an Effective Bandwidth*,
  `paper/main.tex` at `45659d1` (after PR #25). Line numbers below refer to that file.
- **Mode**: `academic-paper-reviewer` full mode, sprint contract `reviewer/reviewer_full/v1`
  (panel of 5: EIC, three peer reviewers, Devil's Advocate).
- **Supplementary evidence**: the code-against-paper audit of the same day
  (`docs/review/paper_verification_2026-10-10.md`) was admitted as supplementary-code
  inspection, at the author's request. Every point that depends on it is tagged **[audit]**.

> **Disclosure.** All five reviewers were written inline by one model in a session that had
> already read the paper and audited it against the code. The protocol's paper-blind Phase 1
> and the reviewers' mutual independence are therefore **simulated, not enforced**. The
> Phase 1 scoring plans below are generic, written before the scores, but not by a context
> that had never seen the paper. Treat scores as ordinal. They are not a calibrated
> prediction of ICLR outcomes.

---

## Phase 0 summary (field analysis)

| Dimension | Result |
|---|---|
| Primary discipline | ML: theory of memorisation in flow-matching and diffusion models |
| Secondary | nonparametric statistics; Bayesian inverse problems and UQ; ODE flows and measure theory |
| Paradigm / method | theory with quantitative validation (synthetic d≤10 and CIFAR-10 DDPM) |
| Tier / maturity | Q1-equivalent (ICLR main track); pre-submission |

Panel: EIC (ICLR Senior Area Chair, generative models). R1 (methodology: simulation-based
inference and calibration statistician). R2 (domain: theorist of memorisation in score-based
and flow models). R3 (perspective: scientific-ML practitioner in imaging inverse problems).
DA (Devil's Advocate).

---

## Phase 1 commitments (contract paraphrase and scoring plans)

The contract has five dimensions. D1 methodology rigour, D2 domain accuracy and D3
argumentative coherence are *mandatory*; D4 cross-disciplinary relevance is *high*; D5
writing and structure is *normal*. The decision follows four failure conditions, highest
severity first:

| Condition | Rule | Decision |
|---|---|---|
| F1 | any mandatory dimension scores `block` (any reviewer) | reject or major revision |
| F2 | ≥4 of 5 reviewers each score ≥2 mandatory dimensions `warn` or worse | major revision |
| F3 | any reviewer scores D4 `block` | major revision |
| F0 | every reviewer scores every mandatory dimension `pass` | accept |

All five reviewers committed, from metadata only, to the following shared triggers. Each
added role-specific signals.

| Dim | `what_to_look_for` | `what_triggers_block` | `what_triggers_warn` |
|---|---|---|---|
| D1 | the stated protocol against the executed one; estimator choice; seeds/n; uncertainty convention; reproducibility | a **headline** claim rests on a protocol or estimator that contradicts the stated one in a way that changes the conclusion, or uncertainty is uninterpretable for a headline claim | secondary results use a protocol or estimator that differs from the stated one; mixed or unstated uncertainty conventions; small n not acknowledged |
| D2 | novelty against named prior work; correctness of cited results; theory-to-data statements | a core novelty claim is false, or a core theorem is wrong | novelty overstated relative to known results; quantitative theory-to-data statements that do not hold; outdated or incomplete citations |
| D3 | abstract/title claims against the scope of the evidence; internal consistency | the central conclusion does not follow from the evidence | headline or summary claims generalise beyond the tested regime; internal contradictions in secondary claims |
| D4 | usability by adjacent fields (UQ, inverse problems); applicability of the guarantees to the advertised scope | the advertised scope is contradicted by the method's own requirements | guarantees or tools do not cover part of the advertised scope; practical guidance missing |
| D5 | density, organisation, notation, venue fit | the main text cannot be followed without the appendix | heavy appendix dependence, redundancy, notation clashes |

Role-specific additions:
- **EIC**: contribution focus.
- **R1**: estimator independence and the effective number of independent units.
- **R2**: proof rigour and citation currency.
- **R3**: whether a practitioner can run the audit without ground truth.
- **DA**: untested alternative explanations; whether any measured regime shows the core
  caveat biting.

`[CONTRACT-ACKNOWLEDGED]` ×5

---

# Phase 2 — Reviewer reports

---

## Report 1 — EIC (ICLR 2027 Senior Area Chair, generative models)

**Recommendation:** Major Revision · **Confidence:** 4

### Summary assessment
The paper characterises the population minimiser of conditional flow matching on a fixed
training set. Hard conditioning collapses each label onto its example. Gaussian label noise
turns the endpoint into a Nadaraya–Watson (NW) mixture over training atoms. The paper then
claims that trained networks follow that mixture at a single *effective* bandwidth h_eff,
which training shrinks towards h, and that h_eff predicts held-out coverage.

The writing is unusually careful about what is proved versus measured. It also comes with a
reproducibility apparatus I rarely see at ICLR. The weakness is focus and reach. The theory
core is admitted to be a conditional transcription of known closed forms (L106–107). The
genuinely new object, the h_eff law and its calibration consequence, is established in d=2,
and partially at one image setting. Yet the title, abstract and conclusion speak of "trained
conditional flows" in general. Several main-text CIFAR numbers also do not use the protocol
the text states **[audit]**. All of this is fixable. As submitted it reads as a borderline
paper.

### Strengths
- **S1. An honest theory/measurement boundary.** Sec. 5 (L666–674) separates what is proved
  from what is measured. Negative findings are reported in the body rather than buried: 38%
  off-atom at h=6, h_eff no better than a power law at image scale (L620–621).
- **S2. A new, checkable empirical law.** h_eff agrees with the mean-implied h_mean at 48/48
  synthetic and 31/36 CIFAR checkpoints (L549–560, L613–621). These counts reproduce exactly
  from `results/` **[audit]**.
- **S3. An actionable audit protocol** (App. `app:audit`, L3138–3176). It reports level,
  range, slope and h_eff together, and the "0.74 decades / median ratio 1.15 / β=−0.156"
  example makes the point that level agreement can certify nothing.

### Weaknesses
**W1. Contribution diffusion (Major).**
- *Problem.* Four contributions (L146–177) and roughly 25 numbered results compete for nine
  pages. The paper's own statement that it does not claim a new kernel identity (L106–107)
  undercuts contribution 1 as written.
- *Why it matters.* ICLR reviewers will score novelty on contribution 1 and miss contribution 2.
- *Suggestion.* Lead with the h_eff law, Prop. `prop:heffid` and Thm. `thm:calib`. Present
  the endpoint law as the reference that makes h_eff definable.

**W2. Headline claims exceed the tested regime (Major).**
- *Problem.* The abstract (L55–57) and conclusion (L682–683: "its memorisation and its
  calibration are set by one number read off a checkpoint") generalise from:
  - calibration evidence in d=2 (75 checkpoints) and an eight-mode d=8 mixture, with no
    image-scale calibration result; this was the round-4 blocker 1, still open;
  - an image setting where the support is not NW (17–38% off-atom, L2407) and where h_eff
    has no fit advantage over a power law.
- *Suggestion.* Scope the title and abstract, e.g. "…in low dimension, and in their first
  two moments at image scale". Alternatively, run the pending CIFAR calibration.

**W3. Main-text CIFAR numbers use an unstated protocol (Major) [audit].**
- *Problem.*
  - Sec. 4.2 says "evaluating 48 conditions at M=256" (L495).
  - The h=0 trajectory (179.1→0.431, L500–501) and the three-instance range (0.409–0.467,
    L503) come from the in-training evaluator (8 conditions, M=16).
  - Appendix C.3 asserts the opposite: "every reported value is re-measured" (L3214–3216).
- *Suggestion.* Re-evaluate, or label the numbers and remove the assertion.

**W4. Density and organisation (Minor).**
- *Problem.*
  - The body is saturated with numbers and appendix pointers.
  - App. D contains near-duplicate paragraphs (L2404–2425 and L2428–2437).
  - A CIFAR "problem-specification" paragraph sits under "Scope: what is and is not
    predicted", after the EXP-1 table (L2394–2401).
- *Suggestion.* Deduplicate and re-file; cut about a third of the main-text numbers.

### Questions for the authors
1. If you could keep only one empirical claim in the abstract, is it 48/48, 31/36, or R²=0.90?
   The answer should determine the title.
2. Is there any image-scale coverage or PIT result, positive or negative, that you can report?

### Dimension scores (rubric, 0–100)
| Originality | Rigour | Evidence | Coherence | Writing | Weighted |
|---|---|---|---|---|---|
| 68 Adequate | 58 Weak | 70 Adequate | 64 Adequate | 60 Adequate | **64.2 → Major** |

### Contract scores
| Dimension | Score | Basis |
|---|---|---|
| D1 | warn | W3 |
| D2 | pass | |
| D3 | warn | W2 |
| D4 | pass | |
| D5 | warn | W4 |

Failure conditions on my own scores: F1 no, F2 **yes**, F3 no, F0 no. **Editorial decision:
major_revision.**

---

## Report 2 — Peer Reviewer 1 (Methodology: calibration and simulation-based inference)

**Recommendation:** Major Revision · **Confidence:** 4

### Summary assessment
The empirical programme has three parts: synthetic EXP-1/2 (d≤10, 2–5 seeds), an h_eff
estimation procedure (log-trace least squares over a grid, bootstrap over conditions), and a
CIFAR-10 DDPM sweep (three instances per bandwidth). Its strengths are rare: released
per-run outputs, scripts that assert the paper's numbers, explicit uncertainty conventions,
and a seed/instance decomposition (App. `sec:seedsplit`).

Inspecting the supplementary code, however, shows that the executed protocol departs from
the stated one in several places. The paper also violates its own estimator rule. Its
uncertainty conventions are not the ones it declares. None of this overturns the 48/48 or
31/36 counts, which reproduce. But the CIFAR reproducibility analysis, one convergence
narrative, and several "within noise" statements need redoing.

### Strengths
- **S1. Traceability.** All but about 20 of roughly 370 numbers checked match their source
  files to the printed precision **[audit]**.
- **S2. An instance/run variance split** (Table `tab:seedsplit`). Instance variation carries
  78% of the variance and the decomposition is consistent (0.143 vs 0.1375). This is
  exemplary.
- **S3. Exposure controls.** These cut the apparent N-dependence from 20.2× to 2.28×
  (EXP-1) and from 14.9× to 2.3× (EXP-3), turning a confound into a finding.

### Weaknesses
**W1. CIFAR protocol mismatch (Major) [audit].**
- *Problem.*
  - Table `tab:seed3` and its prose (L3453–3493) are built from `raw/metrics.csv`, the
    in-training evaluator with `n_conditions: 8, M: 16` (`configs/exp3_cifar_ddpm.yaml`).
  - On seed 0, where both protocols exist, the aggregate ratio differs by 4.7%, 15% and 1.7%
    at h=4, 5, 6 (h=5: 1.245 log vs 1.461 re-evaluated).
  - The interpreted instance spreads are 23–30%. The "1.245 and 1.248 coincidence" argument
    (L3462–3464) does not survive re-evaluation.
  - The design is also misdescribed: the mask is the fixed bottom half for every seed
    (`src/problems/inpainting.py:70–72`). Seeds vary only the training subset and the
    training randomness, not "the mask" (L497, L3454).
- *Suggestion.* Run `scripts/reeval_exp3_cifar_ddpm.py --M 256 --n-conditions 48` on all
  nine runs and rebuild Table `tab:seed3`. Fix the design description.

**W2. The paper violates its own estimator rule (Major) [audit].**
- *Problem.*
  - The audit box says "Never average per-condition ratios" (L3161–3162).
  - Table `tab:gaph01` reports exactly that estimator (`ratio_to_kernel_mean`,
    `src/train.py:117`): 1.649 → 1.004. The recommended aggregate reads 1.045 → 0.996, i.e.
    ≈1 from iteration 100.
  - "The covariance reaches the kernel optimum early" (L4232) is therefore an estimator
    statement.
  - "Ratio-to-kernel" denotes three different estimators across Tables 4, 5 and 13. Table
    5's footnote calls a per-seed aggregate a "per-condition ratio".
- *Suggestion.* Use one named estimator per quantity. Report the aggregate and the median
  everywhere.

**W3. Uncertainty reporting (Major) [audit].**
- *Problem.*
  - App. C.3 declares that every ± is a population SD (L3209–3213). The ablation table
    prints 2-seed *sample* SDs, and the N-sweep script uses `ddof=1`.
  - n=2 seeds cannot support "within seed noise" (Table `tab:ablation`).
  - The P5 caption's "range smaller than the between-seed std at each point" is false at
    3 of 4 points.
  - "Within 3% per seed" (Table `tab:tgt`) reaches 5.9%.
- *Suggestion.* Use one convention. Report CIs or bootstrap intervals for comparisons. Drop
  inferential language where n=2.

**W4. h_mean is weaker evidence than "out-of-sample check" implies (Major).**
- *Problem.*
  - L527–529 calls h_mean≈h_eff "an out-of-sample check that the model is an NW mixture at
    all".
  - Both estimates are computed from the same samples, on the same grid, against nested
    moments of the same reference family. Agreement shows the mean and the variance are
    consistent *within* that family. It does not show the family is right.
  - The bootstrap is over only 20 (synthetic) or 48 (CIFAR) conditions.
- *Suggestion.* Add a competing family: a kNN-weight or Laplace-kernel smoother at fitted
  scale, or a variance-tempered Bayes posterior (which cannot reproduce per-condition
  variation in the linear-Gaussian case). Report fit quality and h_mean agreement under each.

**W5. Non-independent units in the calibration fit (Minor).**
- *Problem.* R²=0.90 and the Spearman values are computed over 75 checkpoints nested in 15
  runs and 3 seeds (L592–598). Neighbouring checkpoints of one run are not independent.
- *Suggestion.* Report leave-one-run-out or leave-one-seed-out prediction error. The heff-law
  file already does this for its RMSE.

### Questions for the authors
1. Are the nine CIFAR checkpoints at 60k still available for re-evaluation at M=256?
2. Under a kNN-weight family, does h_mean still match the variance-fitted scale at 48/48?

### Detailed comments
- **Methods.**
  - The h_eff estimator matches Eq. (6) exactly in code (squared log-trace loss, unsquared
    mean norms, log grid, percentile bootstrap).
  - The atomicity floor F is a Monte Carlo estimate over 800 posterior draws, not "closed
    form, free of any estimator" (Table `tab:floor` caption) **[audit]**.
  - The √(2/(M−1)) sampling-error figure (L3214) is the rank-one worst case.
- **Results.** The Table 10 caption says OT levels are resolved "by 1.8 to 2.3×". The d=10,
  N=50 row gives 2.98×, and two d=2 gains exceed the stated floor **[audit]**.

### Minor issues
Iteration Spearman −0.4147 is printed as −0.42. The EXP-2 MMD is 0.239, not "~0.25".

### Dimension scores
| Originality | Rigour | Evidence | Coherence | Writing | Weighted |
|---|---|---|---|---|---|
| 70 Adequate | 52 Weak | 62 Adequate | 60 Adequate | 64 Adequate | **61.1 → Major** |

### Contract scores
| Dimension | Score | Basis |
|---|---|---|
| D1 | warn | W1–W3 |
| D2 | pass | |
| D3 | warn | W4 and the abstract |
| D4 | pass | |
| D5 | warn | estimator naming |

D1 is not `block`: the headline counts (48/48, 31/36, R² 0.90) reproduce and use the stated
estimators.

Failure conditions: F2 **yes**. **Editorial decision: major_revision.**

---

## Report 3 — Peer Reviewer 2 (Domain: memorisation theory for score and flow models)

**Recommendation:** Major Revision · **Confidence:** 4

### Summary assessment
The theory is correct where I checked it:
- Prop. `prop:collapse`, Thm. `thm:endpoint`, Prop. `prop:moments` (including the
  non-monotone example);
- the TV/Pinsker bound in Thm. `thm:calib`(b);
- Cor. `cor:floor`;
- the survival identity and its closed forms;
- the large-h limit in Prop. `prop:heffid`.

The proofs are careful about weak limits and the open interval [0,1). They are also
elementary. Read as a theory paper, the finite-support endpoint results are a short step
from known unconditional closed forms (Gao & Li 2024, Thm 4.6; Bertrand et al. 2025;
Scarvelis et al. 2025). The paper partly concedes this (L106–107). The new content is the
label factor as a modelling choice with an h-indexed reference, the identifiability and
calibration results built on it, and the empirical h_eff law.

Two theory-to-data statements do not hold as written **[audit]**. The literature section
also has gaps, including the classifier-free guidance paper itself.

### Strengths
- **S1. Rigour on conventions.** The three-conventions paragraph (L2593–2612) and the narrowed
  Lemma `lem:wellposed` avoid the usual hand-waving about t=1.
- **S2. Prop. `prop:survival`(c–d).** It exhibits fields that attain the bound and occupy
  every case of the converse. This turns a bound into a genuine trichotomy.
- **S3. A careful distinction from Smola (2026).** That work reads the spatial factor; this
  paper reads the label factor, whose bandwidth survives to t=1 (L102–107; Table `tab:related`).

### Weaknesses
**W1. Novelty is overstated (Major).**
- *Problem.*
  - Contribution 1 (L147–156) is presented as "an exact reference". Theorem `thm:endpoint`
    is the unconditional closed form applied to the joint (x, noisy label) with a factorised index
    posterior.
  - Prop. `prop:atomicity` (support inside the atoms, plus a W₂ bound by nearest-atom
    distance) follows in two lines.
- *Suggestion.* Re-label these as the reference construction. State explicitly which
  statements have no unconditional analogue: the h-indexed family, Prop. `prop:heffid`, Thm.
  `thm:calib`, Prop. `prop:filtered`.

**W2. Theory-to-data statements that do not hold (Major) [audit].**
- *Problem.*
  - The Table `tab:dagger` caption says the h=0.5 overshoot (1.29) "match[es] the
    +h²‖J‖²_F term (‖J‖²_F=0.4031, exact)".
  - 0.4031 is seed 0's value; across seeds ‖J‖² runs from 0.38 to 4.46.
  - Even for seed 0, 1.004+0.25·0.403=1.10 against a measured 1.286. The overshoot is
    tracked by the finite-N Cov_h (1.28), not by the asymptotic term.
- *Suggestion.* Rewrite the caption. The finite-N reference is the paper's own better
  explanation.

**W3. The calibration bound degrades with label dimension (Major).**
- *Problem.*
  - τ_h ≤ √(k/8) h²/σ² (L573–576) grows with √k.
  - At k=1536 the bound is informative only when h ≪ 0.3σ (since √(1536/8)≈13.9). It is
    vacuous when σ=0, which is the noiseless-inpainting case.
  - The abstract nonetheless lists inpainting in scope (L75–76).
- *Suggestion.* State the k-dependence in the abstract or the theorem discussion, and
  restrict the calibration claims to σ>0 with h²√k ≪ σ².

**W4. Missing and outdated literature (Minor).**
- *Problem.*
  - Props. `prop:cfg` and `prop:cfgatom` analyse classifier-free guidance, but the
    classifier-free guidance paper (Ho & Salimans) is not in `refs.bib`.
  - Several entries cite preprints that have since been published: Buchanan et al. (NeurIPS
    2025), Biroli et al. (Nat. Commun. 2024), Albergo et al. (JMLR 2025), Pfrommer et al.
    (NeurIPS 2025, listed as "Pfrommer and others").
  - Kamb & Ganguli is an ICML 2025 paper but is entered as an arXiv `@article`.
- *Suggestion.* Update the entries; add the CFG reference.

**W5. Notation clashes and one mis-described result (Minor).**
- *Problem.*
  - h⋆ means three things: the NW rate-optimal bandwidth (L1451), the true bandwidth in
    Prop. `prop:heffid` (L538), and the variance-matching bandwidth (L187, L4343).
  - β is both the across-condition slope and the spectral exponent (L619–631, L3061).
  - κ is reused (L540, L1615).
  - "At h=6, β never leaves zero" (L3437) is inaccurate: β is −0.20±0.06 at 60k (M=96) and
    −0.156±0.058 at M=256.
- *Suggestion.* Rename the symbols; say "stays at or below zero".

### Questions for the authors
1. Which statement in Sec. 3 has no unconditional counterpart in Gao & Li or Bertrand et al.?
2. Can Thm. `thm:calib`(b) be sharpened in k for structured noise, e.g. a bound in terms of
   the effective label dimension?

### Dimension scores
| Originality | Rigour | Evidence | Coherence | Writing | Lit. integration | Weighted |
|---|---|---|---|---|---|---|
| 58 Weak | 72 Adequate | 68 Adequate | 60 Adequate | 58 Weak | 64 | **64.3 → Major** |

### Contract scores
| Dimension | Score | Basis |
|---|---|---|
| D1 | pass | |
| D2 | warn | W1, W2, W4 |
| D3 | warn | W3, and the title against the evidence |
| D4 | pass | |
| D5 | warn | W5 |

Failure conditions: F2 **yes**. **Editorial decision: major_revision.**

---

## Report 4 — Peer Reviewer 3 (Perspective: imaging inverse problems practitioner)

**Recommendation:** Major Revision · **Confidence:** 3

### Summary assessment
From the practitioner's side, the most useful product here is the audit protocol. It needs
only the training set and samples, and it would catch the "variance looks right"
false certificate that I have seen in imaging UQ papers. The calibration story is less
usable than the abstract suggests:
- Locating the calibrated window used the true posterior (L3025).
- The ground-truth-free stopping rule is "no better than the same rule on the iteration
  count" (L3027–3028).
- The prior-free guarantee needs observation noise, which inpainting does not have.

The scope is also narrow for the headline: one mask, N=2000, a pixel-space DDPM, and no
latent or text-conditioned model.

### Strengths
- **S1. The audit is cheap and ground-truth-free** (L3142–3143: O(CN(k+d))).
- **S2. Recognisable false certificates.** The h=6 example (median ratio 1.15 with no slope)
  and "tr Cov≈tr Σ_post certifies nothing" are exactly what reviewers of imaging UQ papers
  should be told.
- **S3. A diagnosis practitioners can use.** Prop. `prop:filtered`'s corollary is that
  off-atom samples require spatial-field error. It turns the CIFAR observation into a
  diagnosis.

### Weaknesses
**W1. No practical use demonstrated for the calibration result (Major).**
- *Problem.* The R²=0.90 coverage prediction needs the analytic posterior (μ_h, Σ_h) and the
  kernel weights (L590–593). The transferred-h_eff stopping rule does not beat stopping by
  iteration (L3027).
- *Suggestion.* Either show a posterior-free decision that h_eff improves (choice of h, of
  checkpoint, or flagging collapsed conditions), or present the result as explanatory.

**W2. The guarantee does not cover the advertised inpainting scope (Major).**
- *Problem.* Thm. `thm:calib` requires Y=g(X)+η with σ>0 (L567). The paper's image task
  observes the top half without noise. The abstract scope says "inverse problems and
  inpainting" (L75–76).
- *Suggestion.* Say which parts of the theory apply to noiseless conditioning. The endpoint
  law and the audit do; part (b) does not.

**W3. A narrow image setting for a general title (Minor).**
- *Problem.* One mask (L673), N=2000, a pixel DDPM, 6 runs at two bandwidths for h_eff.
  Text-like labels with no natural kernel are excluded.
- *Suggestion.* Add one more image condition type (another mask or a class-plus-mask setting),
  or narrow the title.

**W4. Missing practitioner guidance (Minor).**
- *Problem.* There is no recommendation for M, the number of conditions, or how to pick h.
  The paper's own M=16 numbers needed re-measurement **[audit]**.
- *Suggestion.* Add a short "using the audit" box with the minimum M and C, and a rule for h.

### Questions for the authors
1. What would you tell an imaging practitioner to do differently after measuring h_eff?
2. Does the audit run unchanged in a latent-space model, where atoms live in latent space?

### Dimension scores
| Originality | Rigour | Evidence | Coherence | Writing | Significance | Weighted |
|---|---|---|---|---|---|---|
| 66 Adequate | 62 Adequate | 62 Adequate | 60 Adequate | 62 Adequate | 66 | **62.5 → Major** |

### Contract scores
| Dimension | Score | Basis |
|---|---|---|
| D1 | warn | W4 and the protocol mismatch |
| D2 | pass | |
| D3 | warn | W2 |
| D4 | warn | W1, W2 |
| D5 | warn | density for non-specialists |

D4 is `warn`, not `block`: the endpoint law and the audit do cover the advertised scope.

Failure conditions: F2 **yes**; F3 no. **Editorial decision: major_revision.**

---

## Report 5 — Devil's Advocate

### Strongest counter-argument
Take the paper at its word: the population theory is a conditional transcription of known
finite-support closed forms. That leaves the empirical claim that a trained network *is* a
Nadaraya–Watson mixture at one bandwidth. The evidence for "Nadaraya–Watson" specifically,
rather than "some local average over nearby training atoms at some scale", is thin.

The paper's own kernel-gradient-flow model shows that learners with Laplace or Matérn
kernels also produce an NW-at-one-bandwidth fit with median R² 0.97 (L3085–3088). The fit is
generic to local smoothing. The "out-of-sample" check h_mean≈h_eff compares two moments of
the same nested family, so it cannot distinguish NW from any other scale-indexed local
smoother. No competing family is fitted.

At image scale, the one regime where the distinction matters, the NW reading fails in
support: 17–38% of samples are off-atom, which no mixture of atoms can produce. There,
h_eff fits no better than an unrestricted power law (L620–621). Three of the quantitative
CIFAR statements rest on an 8-condition, M=16 estimator **[audit]**.

The calibration consequence is real in d=2 and d=8. However, it needs the analytic
posterior to evaluate, and its ground-truth-free use does not beat counting iterations.
Finally, the atomicity caveat, framed as central ("variance restored is not posterior
restored"), binds in no regime the paper measures. At d=2 the floor is 3.5% of tr Σ_post; at
d=3072 the trained network does not inherit atomicity.

What survives is a careful, well-instrumented study showing that trained conditional flows
interpolate between calibrated and collapsed along a one-parameter path whose first two
moments track a finite-sample local smoother. That is worth publishing. It is narrower than
the title.

### Issue list

**CRITICAL.** None. No finding meets the foundation-collapse, logic-break,
data-contradiction or stronger-counter-narrative bar. The alternative in DA-1 is not shown to
fit *better*; it is untested.

**MAJOR**

| # | Dimension | Issue | Location |
|---|---|---|---|
| DA-1 | Alternative paths | No competing scale-indexed smoother is fitted, so "NW at one bandwidth" is not distinguished from generic local averaging. The Laplace/Matérn KGF result shows the fit is not specific. | L520–529, L3085–3088 |
| DA-2 | Overgeneralisation | The abstract's NW claim (L55–57) is contradicted at image scale in support (17–38% off-atom, L2407) and unsupported in fit quality (L620–621). | Abstract, Sec. 4.3 |
| DA-3 | "So what?" | The atomicity caveat binds in no measured regime: negligible at d=2 (F=3.5%), and not inherited at d=3072. Yet it is framed as the central caveat (L156, L391–395). | Sec. 3.2, App. D |
| DA-4 | Logic chain | "From h_eff alone this predicts the held-out coverage" (L71–72) relies on the analytic posterior and the training weights. The usable rule does not beat the iteration baseline (L3027). | Abstract, L590–599 |

**MINOR**

| # | Dimension | Issue | Location |
|---|---|---|---|
| DA-5 | Alternative explanations | "h_eff falls towards h" may simply be optimisation progress re-expressed. The fall tracks iteration closely (12/12 runs fall between 1e4 and 1e5). | L556 |
| DA-6 | Cherry-picking (checked, not found) | Negative results are reported in the body. I found no selective reporting. | — |
| DA-7 | Confirmation bias | The unexplained additive exponent p≈1.3 against 2.2–2.8 is reported but not used to qualify the "single bandwidth" claim. | L648–649 |

### Ignored alternative explanations
1. A kNN-weight or Laplace-kernel smoother at fitted scale. It would explain the
   per-condition variation equally well if the fit is generic.
2. A two-stage reading: an early calibrated phase followed by a collapse paced by the loss.
   The collapse is explained by Cor. `cor:lossform`'s √L scaling without invoking a
   bandwidth.

### Missing stakeholder perspectives
- Practitioners without ground-truth posteriors (cf. R3).
- Data owners: the attribution claim in the Ethics statement assumes the population
  minimiser, which trained image models do not reach in support.

### Observations (non-defects)
- The per-condition variation of the trained variance does track the finite-N reference
  (log-space R² 0.86). A posterior-tempering family with condition-independent variance
  cannot do this. That is genuine evidence for *local* averaging over atoms, and the authors
  should say so explicitly.
- The verification apparatus (scripts that assert the paper's numbers) is a model for the field.

### Contract scores
| Dimension | Score |
|---|---|
| D1 | warn |
| D2 | warn |
| D3 | warn |
| D4 | pass |
| D5 | pass |

Failure conditions: F2 **yes**. **Editorial decision: major_revision.**

---

# Phase 2 — Editorial synthesis

## Sprint-contract arithmetic (binding)

**Step 1 — Scoring matrix** (columns: EIC, R1, R2, R3, DA)

| Dim | Priority | EIC | R1 | R2 | R3 | DA |
|---|---|---|---|---|---|---|
| D1 methodology_rigor | mandatory | warn | warn | pass | warn | warn |
| D2 domain_accuracy | mandatory | pass | pass | warn | pass | warn |
| D3 argumentative_coherence | mandatory | warn | warn | warn | warn | warn |
| D4 cross_disciplinary_relevance | high | pass | pass | pass | warn | pass |
| D5 writing_and_structure | normal | warn | warn | warn | warn | pass |

**Step 2 — Failure conditions** (N=5)

| Condition | Severity | Evaluation | Fired? |
|---|---|---|---|
| F1 | 90 | no mandatory `block` from any reviewer | **no** |
| F2 | 70 | reviewers with ≥2 mandatory warn-or-worse: EIC (D1, D3), R1 (D1, D3), R2 (D2, D3), R3 (D1, D3), DA (D1, D2, D3) = 5. Threshold under `majority` for N=5 is ⌈5/2⌉+1 = 4 | **yes** |
| F3 | 60 | no D4 `block` | **no** |
| F0 | 10 | not every mandatory dimension passes | **no** |

**Step 3 — Precedence.** F2 is the only fired condition. **editorial_decision = major_revision.**

D3 is `warn` for all five reviewers: the scope of the headline claims is the unanimous concern.

## Weakness sub-claim inventory (Step 1b; the denominator is the 4 non-DA reviewers)

| SC | Sub-claim | EIC | R1 | R2 | R3 | Disposition |
|---|---|---|---|---|---|---|
| SC-1 | Title, abstract and conclusion generalise beyond the tested regime | raised (W2) | corroborated (D3) | corroborated (D3) | corroborated (W3) | **CONSENSUS-4** |
| SC-2 | CIFAR main-text and Table `tab:seed3` numbers use the in-training estimator, not the stated protocol | raised (W3) | raised (W1) | not-mentioned | corroborated (W4) | **CONSENSUS-3** |
| SC-3 | Calibration evidence is low-dimensional only; no image-scale result | raised (W2) | not-mentioned | not-mentioned | raised (W1) | corroborated (2) |
| SC-4 | Thm. `thm:calib`(b) does not cover noiseless or high-k conditioning | not-mentioned | not-mentioned | raised (W3) | raised (W2) | corroborated (2) |
| SC-5 | Novelty of the population theory relative to known closed forms | raised (W1, as Major for *framing*) | not-mentioned | raised (W1, Major for *novelty*) | disputed: the audit, not the theory, is the contribution; restructuring should promote the audit | **SPLIT** |
| SC-6 | Estimator inconsistency (mean-of-ratios against the own rule; "ratio-to-kernel" overloaded) | not-mentioned | raised (W2) | not-mentioned | corroborated (W4) | corroborated (2) |
| SC-7 | Uncertainty conventions and small-n inference | not-mentioned | raised (W3) | not-mentioned | not-mentioned | single (R1, conf. 4) |
| SC-8 | h_mean is not an independent test; competing family needed | not-mentioned | raised (W4) | not-mentioned | not-mentioned | single (R1); DA-1 concurs separately |
| SC-9 | Non-independent checkpoints in the calibration R² | not-mentioned | raised (W5) | not-mentioned | not-mentioned | single (R1) |
| SC-10 | Mask misdescribed (the instances do not vary the mask) | not-mentioned | raised (W1) | not-mentioned | corroborated (W3: "one mask") | corroborated (2) |
| SC-11 | ‖J‖² caption and "F in closed form" do not hold | not-mentioned | corroborated (detailed comments) | raised (W2) | not-mentioned | corroborated (2) |
| SC-12 | Missing CFG reference; outdated citations | not-mentioned | not-mentioned | raised (W4) | not-mentioned | single (R2) |
| SC-13 | Notation clashes; "β never leaves zero" | not-mentioned | not-mentioned | raised (W5) | not-mentioned | single (R2) |
| SC-14 | Density, duplicated and misplaced appendix text | raised (W4) | not-mentioned | not-mentioned | corroborated (D5) | corroborated (2) |
| SC-15 | Missing practitioner guidance (M, C, choice of h) | not-mentioned | not-mentioned | not-mentioned | raised (W4) | single (R3) |

**DA-CRITICAL:** none. The four DA-MAJOR items go to Required Revisions. DA-1 is
corroborated by R1's SC-8.

## Points of disagreement

**SPLIT — SC-5: what the body should foreground.**
- *EIC:* the theory core is not new. Foreground the h_eff law, identifiability and
  calibration.
- *R2:* agrees the theory is not new, and rates it as a novelty defect.
- *R3:* disputes the remedy. For practitioners the audit protocol is the most valuable
  contribution, and it should move into the main text.
- *Type:* direction disagreement (incompatible restructuring).
- *EIC arbitration:* promote **both** the h_eff law and a one-paragraph version of the audit
  into the main text. Demote the endpoint law to "the reference that makes h_eff definable".
  Space comes from moving the interventions paragraph (Sec. 3.3) and two-thirds of Sec. 4.1's
  numbers to the appendix.
- *Rationale:* R3's point is substantive. The audit is the part of the paper with
  ground-truth-free use (R3 S1). Both R2 and the EIC agree that the novelty argument must
  rest on the h_eff results rather than on Thm. `thm:endpoint`.

No other sub-claim is disputed.

## Editorial Decision

### Decision: **Major Revision**

| Reviewer | Recommendation | Confidence | Rubric (weighted) | ICLR-scale reading* |
|---|---|---|---|---|
| EIC (SAC) | Major | 4 | 64.2 | 5 |
| R1 (methodology) | Major | 4 | 61.1 | 5 |
| R2 (domain) | Major | 4 | 64.3 | 5 |
| R3 (practice) | Major | 3 | 62.5 | 6 |
| DA | — (no CRITICAL) | — | — | — |

\*An informal translation to the ICLR 1–10 scale. The four-reviewer mean is about 5.25,
borderline reject as submitted. Round 4 read 6/5/6/6; the drop comes from the audit findings.
With Required Revisions R1–R5 done, the panel expects 6/6/5–6/6.

### Decision rationale
- **The contract fixes the decision.** F2 fires: all five reviewers score at least two
  mandatory dimensions `warn`. No reviewer scores `block`. No DA finding is CRITICAL.
- **The unanimous concern is scope (SC-1).** The paper's evidence supports "trained
  conditional flows follow a finite-sample local smoother at an effective scale, exactly in
  low dimension and in two moments at image scale". The title and abstract claim more.
- **The strongest methodological concern (SC-2, CONSENSUS-3) is mechanical.** The CIFAR
  reproducibility analysis must be re-measured at the stated protocol, or relabelled. One
  argument in it (h=5) does not survive.
- **Why not Minor.** SC-1 and SC-2 change what the paper claims. SC-8/DA-1 asks for a new
  control experiment.
- **Why not Reject.** The headline counts reproduce exactly. The theory is correct. The
  verification apparatus is unusually strong (R1 S1, DA observations). Every required item
  has a concrete, bounded fix.

## Required revisions (must fix)

| # | Item | Sub-claims | Source | Severity | Section | Effort |
|---|---|---|---|---|---|---|
| R1 | Re-scope the title, abstract and conclusion to the tested regime; state that the calibration evidence is d≤8 | SC-1, SC-3 | EIC W2, DA-2, DA-4 | Major | Abstract, Sec. 1, Sec. 6 | 1 day |
| R2 | Re-evaluate the nine CIFAR runs at 48 conditions / M=256, or relabel Table `tab:seed3` and the 179.1→0.431 numbers; delete "every reported value is re-measured"; fix the mask description | SC-2, SC-10 | R1 W1, EIC W3 | Major | Sec. 4.2, App. C.3 | 1–2 days GPU, or 2 h text |
| R3 | Add a competing scale-indexed smoother (kNN or Laplace weights) to the h_eff analysis, and report fit quality and h_mean agreement under it | SC-8 | R1 W4, DA-1 | Major | Sec. 4.3, App. C | 2–3 days |
| R4 | Restrict Thm. `thm:calib`(b)'s advertised scope (σ>0, h²√k≪σ²); say which results cover noiseless inpainting | SC-4 | R2 W3, R3 W2 | Major | Sec. 4.3, abstract | 0.5 day |
| R5 | Restructure per the SC-5 arbitration: h_eff law + audit paragraph in front; endpoint law as the reference | SC-5 | EIC W1, R2 W1, R3 | Major | Secs. 1, 3, 4 | 2 days |
| R6 | Fix the estimator inconsistency: one named ratio per quantity, aggregate in Table `tab:gaph01`, correct Table 5's footnote | SC-6 | R1 W2 | Major | App. C | 0.5 day |
| R7 | Fix the theory-to-data statements: the ‖J‖² caption, "F in closed form", Table 10's ranges and resolution claim | SC-11 | R2 W2, R1 | Major | App. B/C | 0.5 day |

## Suggested revisions (should fix)

| # | Item | Sub-claims | Source | Priority |
|---|---|---|---|---|
| S1 | One std convention (or labelled exceptions); CIs for comparisons; remove "within noise" language at n=2; fix the P5, Table `tab:tgt` and held-out wording | SC-7 | R1 W3 | P2 |
| S2 | Leave-one-run-out error for the calibration R² | SC-9 | R1 W5 | P2 |
| S3 | Add the CFG reference; update the five bib entries | SC-12 | R2 W4 | P2 |
| S4 | Rename h⋆, β, κ; "β stays at or below zero" | SC-13 | R2 W5 | P2 |
| S5 | A "using the audit" box: minimum M and C, and a rule for h | SC-15 | R3 W4 | P2 |
| S6 | Show one posterior-free decision h_eff improves, or present calibration as explanatory | SC-3 | R3 W1, DA-4 | P2 |
| S7 | Address DA-3: say where the atomicity floor would bind for a trained model, or demote it from "central caveat" | — | DA-3 | P2 |
| S8 | Deduplicate App. D (L2404–2437); re-file the misplaced CIFAR paragraph (L2394–2401); trim main-text numbers | SC-14 | EIC W4 | P3 |
| S9 | Low-precision items from the audit (−0.42→−0.41, MMD 0.24, 1e-3, 0.003, 12%, 4.4×, five checkpoints, `proof_checks/`) | — | R1 minor | P3 |

## Revision roadmap

**Priority 1 — structural (about 1 week, plus GPU time for R2)**
- [ ] R2: CIFAR re-evaluation or relabel; mask wording
- [ ] R3: competing-smoother control
- [ ] R5 + R1: restructure, then re-scope the title and abstract
- [ ] R4: calibration-theorem scope

**Priority 2 — content (2–3 days)**
- [ ] R6, R7
- [ ] S1–S7

**Priority 3 — text (1 day)**
- [ ] S8, S9

The text-only items (R1, R4, R6, R7, S1, S3, S4, S8, S9) are covered by the proposed session
"Apply paper-verification fixes to main.tex". R2's re-evaluation and R3 need GPU or torch
runs, which are blocked on this machine.

## Closing
We encourage a substantially revised manuscript. The measured law is interesting and well
supported in its regime, and the verification apparatus is exemplary. The revision should
make the claims match that regime, and close the protocol gaps that the authors' own scripts
make visible.
