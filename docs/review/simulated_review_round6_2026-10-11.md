# Simulated review, round 6: full five-reviewer panel (ICLR 2027)

- **Manuscript**: *Trained Conditional Flows Memorise at an Effective Bandwidth*,
  `paper/main.tex` at `7e88fd9` (the paper itself last changed in `79a7528`). Line numbers
  below refer to that file.
- **Mode**: `academic-paper-reviewer` full mode, sprint contract `reviewer/reviewer_full/v1`
  (panel of 5: EIC, three peer reviewers, Devil's Advocate), same panel as round 5.
- **Supplementary evidence**: files committed to the repository that the paper does not yet
  use, chiefly the CIFAR-10 re-runs of 2026-10-11 (`results/exp3/_rerun/`). Every point
  that depends on them is tagged **[supp]**. Findings from the round-5 audit that the
  revision has fixed are not repeated.

> **Disclosure.** All five reviewers were written inline by one model, in the session that
> also wrote most of the revisions under review and ran the supplementary experiments. The
> protocol's paper-blind Phase 1 and the reviewers' mutual independence are therefore
> **simulated, not enforced**, and the panel has an author's knowledge of what the
> supplementary files contain. Treat scores as ordinal. They are not a calibrated
> prediction of ICLR outcomes.

---

## Phase 0 summary (field analysis)

| Dimension | Result |
|---|---|
| Primary discipline | ML: theory of memorisation in flow-matching and diffusion models |
| Secondary | nonparametric statistics; Bayesian inverse problems and UQ; ODE flows and measure theory |
| Paradigm / method | theory with quantitative validation (synthetic d≤10 and CIFAR-10 DDPM) |
| Tier / maturity | Q1-equivalent (ICLR main track); pre-submission, second revision |

Panel, unchanged from round 5: EIC (ICLR Senior Area Chair, generative models). R1
(methodology: simulation-based inference and calibration statistician). R2 (domain:
theorist of memorisation in score-based and flow models). R3 (perspective: scientific-ML
practitioner in imaging inverse problems). DA (Devil's Advocate).

---

## Phase 1 commitments

The contract, its five dimensions (D1 methodology rigour, D2 domain accuracy, D3
argumentative coherence: mandatory; D4 cross-disciplinary relevance: high; D5 writing and
structure: normal), the failure conditions F0–F3 and the shared `block`/`warn` triggers are
those of round 5, restated there in full. Role-specific additions:

- **EIC**: whether the revision changed what the paper claims, not only how it says it.
- **R1**: whether each control can, in principle, reject the hypothesis it is used for.
- **R2**: theory-to-data statements, notation.
- **R3**: whether a practitioner gains anything over a free baseline.
- **DA**: results in the supplementary material that cut against the thesis.

`[CONTRACT-ACKNOWLEDGED]` ×5

---

# Phase 2 — Reviewer reports

---

## Report 1 — EIC (ICLR 2027 Senior Area Chair, generative models)

**Recommendation:** Major Revision (close to Minor) · **Confidence:** 4

### Summary assessment
The revision is substantial and mostly well judged.
- The abstract is now scoped: low dimension for the Nadaraya–Watson (NW) description, "the
  first two moments but not the support" at image scale, and d≤8 for calibration (L55–59,
  L74–76).
- A competing-family control answers round 5's main methodological request (Table
  `tab:families`).
- Every CIFAR number now says which estimator produced it (L504–509, L3267–3284).
- The theory-to-data statements the audit flagged are corrected (the ‖J‖² caption, F as a
  Monte Carlo estimate, the OT resolution ranges).

What remains is less about the evidence than about the paper's *summary* of it. The title,
the contribution list and the conclusion still speak of trained conditional flows in
general. The conclusion says one number sets "memorisation and calibration" (L689–690),
which the paper's own appendix contradicts for memorisation (L3088–3089). And the
repository now holds an image-scale calibration result that the paper does not report and
that does not favour h_eff **[supp]**.

### Strengths
- **S1. The scoping of the abstract is honest and specific.** "At image scale this holds for
  the first two moments but not for the support" (L58–59) is exactly the right sentence.
- **S2. The competing-family control was done properly** (L3006–3053). It uses paired
  per-checkpoint comparisons and a bootstrap interval on the margin, and the paper concedes
  in the main text that interval agreement "does not single out the Gaussian kernel"
  (L532–534).
- **S3. Estimator labelling is now explicit.** The main text names the training-time
  estimator wherever it is used (L505–508). App. C.3 lists what was re-measured and what
  was not, with the size of the difference (L3276–3282).

### Weaknesses
**W1. The summary claims outrun the scoped abstract (Major).**
- *Problem.*
  - The conclusion (L687–690): "so its memorisation and its calibration are set by one
    number read off a checkpoint". App. `app:calibdetails` says the on-atom fraction, not
    h_eff, predicts extraction (0.95), and that h_eff predicts collapse "far better than
    the PIT error (−0.28)" (L3086–3089).
  - Contribution 2 (L161–172) still reads "A trained network follows that mixture at one
    bandwidth", and quotes R²=0.90 for "75 trained checkpoints" without saying they are
    d=2.
  - The title is unchanged.
- *Why it matters.* An area chair reads the abstract, the contribution list and the
  conclusion. Two of the three still make the unscoped claim.
- *Suggestion.* Bring contribution 2 and the conclusion to the abstract's scope. Consider a
  title that names what is measured, e.g. "…Memorise at an Effective Bandwidth: Exact in Low
  Dimension, in Moments at Image Scale".

**W2. The structure is as in round 5 (Major for presentation).**
- *Problem.*
  - Round 5's arbitration was to put the h_eff law and a paragraph of the audit in front,
    with the endpoint law as the reference that makes h_eff definable. The order of
    Secs. 1–4 and contribution 1 ("An exact reference", L151–160) are unchanged.
  - Contribution 3 says the audit "reports level, range, slope and h_eff together"
    (L175–176). The audit box (L3203–3234) has no h_eff step.
- *Suggestion.* At minimum, add h_eff and h_mean as a step of the audit box. The
  restructuring can be lighter than round 5 proposed: swap contributions 1 and 2, and move
  the interventions paragraph (Sec. 3.3) to the appendix.

**W3. A relevant result exists but is not reported (Major) [supp].**
- *Problem.*
  - `results/exp3/_rerun/calib_image_summary.json` measures held-out coverage at 42
    checkpoints of the six CIFAR-10 re-runs.
  - There, h_eff ranks 90% coverage with Spearman 0.63 against 0.98 for the raw generated
    pixel standard deviation (0.59 against 0.97 given the iteration).
  - The paper's only image-scale statement about calibration is the abstract's scoping.
- *Why it matters.* Round 5 asked for "any image-scale coverage or PIT result, positive or
  negative". The result is negative. A reader of the repository will find it, so the paper
  should say it first.
- *Suggestion.* Report it in Sec. 4.3 or Limitations, and in App. `app:calibdetails`.

### Questions for the authors
1. With the image-scale result in hand, which claim about calibration do you want the
   conclusion to make?
2. Will h_eff at CIFAR h=0 and h=6 (the regime where β<0) be in the next version?

### Dimension scores (rubric, 0–100)
| Originality | Rigour | Evidence | Coherence | Writing | Weighted |
|---|---|---|---|---|---|
| 68 Adequate | 66 Adequate | 70 Adequate | 62 Adequate | 62 Adequate | **66.2 → Major** |

### Contract scores
| Dimension | Score | Basis |
|---|---|---|
| D1 | warn | W3 |
| D2 | pass | |
| D3 | warn | W1 |
| D4 | pass | |
| D5 | warn | W2 |

Failure conditions on my own scores: F2 **yes**. **Editorial decision: major_revision.**

---

## Report 2 — Peer Reviewer 1 (Methodology: calibration and simulation-based inference)

**Recommendation:** Major Revision · **Confidence:** 4

### Summary assessment
The round-5 methodology items were handled with care:
- the CIFAR estimator labels;
- one standard-deviation convention with labelled exceptions;
- the aggregate ratio in Table `tab:gaph01`;
- the competing-family control.

The new control is the main thing to review. It is well executed but cannot test what it is
presented as testing: its only non-atomic competitor fails by construction. Two older items
remain open: the CIFAR seed table is still on the training-time estimator, now with
re-evaluated data available **[supp]**; and the calibration R² still has no leave-one-run-out
error.

### Strengths
- **S1. Paired comparison with an interval on the margin** (L3043–3047). Gaussian beats
  Laplace at 36/48 checkpoints and in 9/12 runs, with median log-RMSE difference 0.020,
  95% CI [0.011, 0.024]. That is the right way to compare families.
- **S2. A conceded limit stated in the body.** "Their agreement alone does not single out
  the Gaussian kernel" (L532–534) answers round 5's objection that h_mean≈h_eff was not an
  independent test.
- **S3. The uncertainty convention is declared once and its exceptions labelled**
  (L3267–3272).

### Weaknesses
**W1. The family control cannot reject a non-atomic reference (Major).**
- *Problem.*
  - The only non-atomic family is "the linear-Gaussian posterior with observation noise s,
    whose covariance does not depend on y" (L3015–3017).
  - A reference whose trace is the same at every condition predicts a constant log-trace.
    Its log-space R² against per-condition variances is therefore ≤0 by construction.
    "R²=−0.12" (L3030, L3048) restates this; it is not a test result.
  - The Gaussian's advantage over Laplace is small (0.020 log-RMSE). At h>0, the Gaussian is
    the kernel of the training label noise, so Theorem `thm:endpoint` already predicts it
    at the optimum. The interesting case is h=0, where any smoothing is the network's own,
    and the table does not split by h.
  - The control is synthetic only. CIFAR-10, where the support is not atomic (17–38%
    off-atom), is not tested.
- *Suggestion.*
  - Add a non-atomic competitor whose variance depends on y. The paper already has one: the
    endpoint-smoothed law of Prop. `prop:tgtnoise`, with trace tr Cov_s + dρ², nests the
    Gaussian at ρ=0. If ρ̂≈0, the moments are consistent with atoms; if not, they are not.
  - Report Table `tab:families` by h.
  - Run the five families on the CIFAR checkpoints: the reference costs O(CN(k+d)).

**W2. The CIFAR seed table uses an estimator the repository has since superseded (Major)
[supp].**
- *Problem.*
  - Table `tab:seed3` and its reading (L3519–3544) use 8 conditions at M=16.
  - `results/exp3/_rerun/seed_table.json` re-evaluates three fresh runs per bandwidth at
    48 conditions and M=256. It gives aggregate-ratio spreads of 9.6% against 26.5% for
    the raw trace at h=4, and 16.9% against 3.3% at h=5. The table prints 23.4% against
    41.4%, and 29.6% against 22.9%.
  - The training-time numbers of the same runs are 9.7–15.3% off the re-evaluation at
    four of six run-bandwidth pairs (the other two: +1.8% and −4.1%).
  - The qualitative reading survives (the ratio is the more stable statistic only at h=4).
    Every number in it changes.
- *Suggestion.* Rebuild Table `tab:seed3` and the h=0 sentence of Sec. 4.2 from the
  re-evaluation once the h=0 and h=6 re-runs finish. Then drop the M=16 caveats in App. C.3.

**W3. The calibration R² still lacks a run-level error (Minor; round-5 W5).**
- *Problem.*
  - R²=0.90 is over 75 checkpoints nested in 15 runs (L597–600), and no leave-one-run-out
    error is reported.
  - Each checkpoint's coverage comes from 100 held-out pairs (L3056), so its binomial
    standard error is about 0.03 at 0.9. The R² ceiling implied by that noise is not
    stated.
- *Suggestion.* Report leave-one-run-out (or leave-one-seed-out) error and the noise
  ceiling.

**W4. A finite-M reference is needed when the image result is added (Minor) [supp].**
- *Problem.* The image-scale script (`scripts/calib_image_checkpoints.py`) takes the 5–95%
  quantile interval of M=64 draws. A perfectly calibrated sampler covers a fresh draw with
  that interval only about 87% of the time at M=64. The 0.93→0.76 trajectory therefore
  starts *above* its reference, not near 0.90.
- *Suggestion.* Use rank-based coverage, whose reference is exact at finite M, or print
  the M=64 reference next to the measurements.

### Detailed comments
- **L552–554.** "The bound holds at all 75 synthetic checkpoints": h⋆ is unknown for a
  trained network, so say what was checked. L1945 suggests the bound was compared with
  bootstrap widths.
- **L3000–3004.** The six CIFAR re-runs reproduce the published h_eff (4.79 against 4.80).
  A third run of seed 0 at h=4 **[supp]** gives 4.93. The GPU non-determinism of
  App. `app:exp4` applies here too; one sentence would do.

### Dimension scores
| Originality | Rigour | Evidence | Coherence | Writing | Weighted |
|---|---|---|---|---|---|
| 70 Adequate | 62 Adequate | 64 Adequate | 62 Adequate | 66 Adequate | **64.7 → Major** |

### Contract scores
| Dimension | Score | Basis |
|---|---|---|
| D1 | warn | W2, W3 |
| D2 | pass | |
| D3 | warn | W1 (the R²=−0.12 inference) |
| D4 | pass | |
| D5 | pass | |

Failure conditions: F2 **yes**. **Editorial decision: major_revision.**

---

## Report 3 — Peer Reviewer 2 (Domain: memorisation theory for score and flow models)

**Recommendation:** Major Revision · **Confidence:** 4

### Summary assessment
I re-checked the results the revision leans on, and they are correct:
- Theorem `thm:calib`: (a) by the strong law; (b) by Pinsker with the stated constant;
- (c) the covariance identity Σ_h = Cov(X−μ_h(Y)) + h²Γ_hΓ_hᵀ and the χ² domination;
- (d) the weighted-moment identities;
- Prop. `prop:heffid`: the derivative identities and the stability bound;
- Prop. `prop:filtered`(b): a sound argument via the diverging integral.

These results are elementary: a triangle inequality with the mean-value theorem, Pinsker,
and an exact Gaussian computation. The paper's novelty therefore rests on the empirical
law, as round 5 concluded. The citation fixes are done: the classifier-free guidance
reference was added and the five preprints were updated.

My remaining concerns are one theory-to-data argument that has become more prominent, the
scope of Theorem `thm:calib`(b), and notation.

### Strengths
- **S1. Theorem `thm:calib` is stated with the right generality.** Part (b) is genuinely
  prior-free, and the simulation check against exact highest-density regions of non-Gaussian
  posteriors (L2017–2023) is the right test.
- **S2. Prop. `prop:filtered` is a clean negative result.** Label resolution alone cannot
  move the atoms, which turns the 38% off-atom observation into a statement about the
  spatial field.
- **S3. The literature is now current** (`refs.bib`: NeurIPS/ICML/JMLR versions, CFG).

### Weaknesses
**W1. The "atomicity dominates at image dimension" argument uses the wrong dimension and the
wrong object (Major).**
- *Problem.*
  - L400–405 and App. D (L2624–2656) argue that the floor is "dominant in exactly the
    regime where diversity is wanted", from the rate factor N^{-1/d}=0.9975 at
    (d,N)=(3072,2000).
  - The scaling measurement behind it uses a standard Gaussian target in ambient dimension
    d≤8 (L2635–2638). The rate that governs nearest-atom distances is the *intrinsic*
    dimension of the posterior's support. The conditional law of the bottom half of a
    CIFAR image is not a full-rank Gaussian in R^3072.
  - A rate factor without its constant does not give the floor's size relative to the
    posterior scale.
  - The argument applies to the population minimiser. The paper's own trained image model
    leaves the atoms (L515–516: 38% off-atom), so in the one regime where the floor would
    be large, the object it bounds is not the deployed one.
- *Suggestion.* Either measure F for CIFAR conditions directly (nearest-training-image
  distances of held-out bottom halves, against the trained model's spread), or restrict
  the claim to "large for a full-rank posterior in high ambient dimension" and drop
  "dominant".

**W2. Theorem `thm:calib`(b) and the advertised scope (Minor; round-5 W3, partly fixed).**
- *Problem.*
  - The abstract now carries the √k and σ dependence (L71–72), which is good. It also still
    lists inpainting in scope (L79–80).
  - Part (b) is vacuous at σ=0, which is the noiseless inpainting of Sec. 4.2. At k=1536 it
    is informative only for h ≲ 0.27σ.
  - Neither point is in the main text. Limitations says only "(b) only bounds the deviation"
    (L677).
- *Suggestion.* One sentence in Limitations: which results cover noiseless conditioning
  (the endpoint law, the audit, part (d)) and which do not (part (b)).

**W3. Notation clashes persist (Minor; round-5 W5).**
- *Problem.*
  - h⋆ means three things: the variance-matching bandwidth (Fig. 1, L190; 0.703 at one
    condition, L4423), the true bandwidth (Prop. `prop:heffid`, L545–548), and the NW
    rate-optimal bandwidth (L1459).
  - β is both the across-condition slope (L626) and the spectral exponent (L636), ten lines
    apart.
  - κ is both the identifiability constant (L547) and the near-duplicate ratio bound
    (L2328).
  - Fig. 1's h⋆≈0.70 sits beside Sec. 4.1's "Σ_post ≈ Cov_h at h=0.1" (L466–467). The
    first is per-condition, the second averaged; tr Cov_h is non-monotone in h
    (Prop. `prop:moments`). Readers will see a contradiction.
- *Suggestion.* Rename the symbols, e.g. h_var for the variance-matching bandwidth and
  γ for the spectral exponent. Give the value of h⋆ in Fig. 1's caption and say it is
  per-condition.

**W4. Prop. `prop:heffid` leaves an assumption in the proof (Minor).**
- *Problem.* The stability claim needs h⋆∈𝓗 (or a grid-misfit term). The proof says so
  (L1929–1930); the statement (L544–549) does not.
- *Suggestion.* Move it into the statement.

### Questions for the authors
1. What is the nearest-training-image distance of a held-out CIFAR bottom half, relative to
   the trained model's per-pixel spread at h=4?
2. Is there a version of Theorem `thm:calib`(b) for σ=0 with h>0, e.g. a bound in terms of
   the label noise's effect on the region rule?

### Dimension scores
| Originality | Rigour | Evidence | Coherence | Writing | Lit. integration | Weighted |
|---|---|---|---|---|---|---|
| 60 Adequate | 74 Adequate | 68 Adequate | 62 Adequate | 60 Adequate | 72 | **65.8 → Major** |

### Contract scores
| Dimension | Score | Basis |
|---|---|---|
| D1 | pass | |
| D2 | warn | W1 |
| D3 | warn | W2, and W1's "dominant" |
| D4 | pass | |
| D5 | warn | W3 |

Failure conditions: F2 **yes**. **Editorial decision: major_revision.**

---

## Report 4 — Peer Reviewer 3 (Perspective: imaging inverse problems practitioner)

**Recommendation:** Major Revision · **Confidence:** 3

### Summary assessment
The audit remains the most useful thing in the paper for me, and the revision made the
paper more honest about what it does not do (the stopping-rule result, the estimator
labels). Two things still keep it from being usable as a tool.
- The audit box has none of the guidance a practitioner needs: how many samples, how many
  conditions, how to pick h.
- At image scale, the repository shows that the proposed statistic predicts coverage worse
  than a free baseline **[supp]**.

### Strengths
- **S1. The family result is useful in practice** (L3048–3051). The across-condition
  variation of the generated variance is a property of the finite atoms, so any reference
  for a trained conditional flow must be built from the training set.
- **S2. The stopping-rule result is reported straight** (L3083–3086): transferring h_eff
  across seeds is no better than stopping by iteration count.
- **S3. The audit needs no ground truth** (L3200–3201).

### Weaknesses
**W1. At image scale, a free baseline beats h_eff for the decision a practitioner makes
(Major) [supp].**
- *Problem.*
  - In `calib_image_summary.json`, the generated pixel standard deviation, which needs
    neither the training set nor a reference, ranks held-out 90% coverage with Spearman
    0.98.
  - h_eff does so with 0.63, and h_eff/h with 0.36.
  - Extraction tracks the iteration (0.98), not h_eff.
- *Why it matters.* Contribution 2 and the conclusion present h_eff as what sets
  calibration. A practitioner at image scale would do better with the sample spread.
- *Suggestion.* Report this. Say what h_eff adds at image scale: it describes where the
  model sits relative to the training set (the mean and the variance level together),
  rather than predicting coverage.

**W2. The audit box is not yet a procedure (Minor; round-5 W4).**
- *Problem.*
  - No minimum M or C. The paper's own M=16 estimator was off by up to 15% (L3280–3281).
  - No rule for choosing h, and no h_eff step (cf. EIC W2).
- *Suggestion.*
  - Add three lines: M≥128 for the trace, given the √(2/(M−1)) worst case; C≥48 for the
    slope; h_eff and h_mean with bootstrap intervals.
  - Add the reading "if h_eff/h ≫ 1, the model is under-trained relative to its label
    noise".

**W3. Scope (Minor; unchanged).**
- *Problem.* One mask, N=2000, pixel space, no latent model (L679–681).
- *Suggestion.* Acknowledged in Limitations; nothing more is needed for a first paper.

### Questions for the authors
1. Given W1, what should a practitioner compute first: h_eff or the sample spread?
2. Does the audit run unchanged on a latent-space model?

### Dimension scores
| Originality | Rigour | Evidence | Coherence | Writing | Significance | Weighted |
|---|---|---|---|---|---|---|
| 66 Adequate | 66 Adequate | 62 Adequate | 62 Adequate | 62 Adequate | 64 | **63.8 → Major** |

### Contract scores
| Dimension | Score | Basis |
|---|---|---|
| D1 | pass | |
| D2 | pass | |
| D3 | warn | W1 against contribution 2 and the conclusion |
| D4 | warn | W1, W2 |
| D5 | warn | the audit box |

D4 is `warn`, not `block`: the audit and the endpoint law still cover the advertised scope.

Failure conditions: F2 no (one mandatory warn); F3 no. **Editorial decision on my own
scores: minor_revision.**

---

## Report 5 — Devil's Advocate

### Strongest counter-argument
The revised paper makes one central claim: a trained conditional flow sits at an effective
bandwidth h_eff, and that number sets its memorisation and its calibration (L687–690). Take
the three parts in turn.

*"Sits at an effective bandwidth."* In d=2 this is well supported for the first two
moments. Is it specifically Nadaraya–Watson? The revision's own control shows that interval
agreement cannot tell. Fit quality separates Gaussian from Laplace weights by 0.02
log-RMSE, at bandwidths where the Gaussian is the kernel the network was trained with.
The only non-atomic competitor has a condition-independent variance, so it fails by
construction. What is established is local averaging over the training atoms at one scale.
That is a real finding, but a weaker one than "Nadaraya–Watson".

*"Sets its memorisation."* The paper's appendix says the on-atom fraction, not h_eff,
predicts extraction (L3088–3089). The supplementary image runs agree: extraction tracks the
iteration at 0.98 **[supp]**.

*"Sets its calibration."* In d=2 and d=8, h_eff ranks coverage well. At image scale, where
calibration is the practical question, the supplementary runs show h_eff ranking coverage
at 0.63 against 0.98 for the raw sample spread **[supp]**. The paper does not report this.

Meanwhile the paper argues that the atomicity floor is "dominant" at image dimension
(L2653–2656), while its trained image model leaves the atoms. What survives is a careful,
reproducible description of where trained flows sit relative to their training set, exact
in low dimension. The conclusion claims a predictive law, and at image scale the data
contradict it.

### Issue list

**CRITICAL.** None. The conclusion sentence that the data contradict is a summary
statement. The scoped abstract does not make it, and the fix is a rewording plus reporting a
result that exists. No foundational claim of Sec. 3 or of the d=2 evidence is overturned.

**MAJOR**

| # | Dimension | Issue | Location |
|---|---|---|---|
| DA-1 | Overgeneralisation / logic | "Memorisation and calibration are set by one number" contradicts the paper's appendix (extraction ← on-atom fraction) and the image-scale coverage result **[supp]**. | L687–690 vs L3088–3089 |
| DA-2 | Reporting completeness | An image-scale calibration result that cuts against the thesis is in the repository but not in the paper. Probably timing rather than intent, but it must be reported before submission. | `results/exp3/_rerun/calib_image_summary.json` |
| DA-3 | Alternative explanations | "NW" is weakly identified against other local smoothers. The only non-atomic competitor cannot vary with y. At h>0, the Gaussian preference is predicted by the training objective. | L532–536, Table `tab:families` |
| DA-4 | Logic chain | The floor is "dominant at image dimension" (ambient-d extrapolation), while the trained image model does not inherit atomicity. The argument bounds an object the paper shows is not reached. | L400–405, L2624–2656 vs L515–516 |

**MINOR**

| # | Dimension | Issue | Location |
|---|---|---|---|
| DA-5 | Alternative explanations | At image scale, h_eff's association with coverage barely survives conditioning on the iteration (0.59), while the sample spread keeps 0.97 **[supp]**. | — |
| DA-6 | Cherry-picking (checked) | Main-text negatives are reported (38% off-atom; no fit advantage over a power law at image scale). DA-2 is the only omission found. | L515–516, L627–628 |
| DA-7 | Overgeneralisation | The title is unchanged and unscoped. | L40–41 |

### Ignored alternative explanations
1. **The sample spread as the whole story at image scale.** If the generated spread alone
   predicts coverage, h_eff may be a re-parametrisation of the spread with the training set
   attached.
2. **An endpoint-smoothed (non-atomic, y-dependent) reference.** It would test atomicity
   in the moments, and the paper has it already (Prop. `prop:tgtnoise`).

### Missing stakeholder perspectives
- Practitioners at image scale, who need a coverage predictor (cf. R3 W1).
- Data owners: extraction is predicted by the on-atom fraction and the iteration, which is
  the actionable privacy result, and the main text does not say it.

### Observations (non-defects)
- The revision fixed every round-5 theory-to-data statement I flagged.
- The estimator labelling (L505–508) is now a model of how to report mixed protocols.

### Contract scores
| Dimension | Score |
|---|---|
| D1 | warn (DA-2) |
| D2 | warn (DA-4) |
| D3 | warn (DA-1, DA-3) |
| D4 | pass |
| D5 | pass |

Failure conditions: F2 **yes**. **Editorial decision: major_revision.**

---

# Phase 2 — Editorial synthesis

## Sprint-contract arithmetic (binding)

**Step 1 — Scoring matrix** (columns: EIC, R1, R2, R3, DA)

| Dim | Priority | EIC | R1 | R2 | R3 | DA |
|---|---|---|---|---|---|---|
| D1 methodology_rigor | mandatory | warn | warn | pass | pass | warn |
| D2 domain_accuracy | mandatory | pass | pass | warn | pass | warn |
| D3 argumentative_coherence | mandatory | warn | warn | warn | warn | warn |
| D4 cross_disciplinary_relevance | high | pass | pass | pass | warn | pass |
| D5 writing_and_structure | normal | warn | pass | warn | warn | pass |

**Step 2 — Failure conditions** (N=5)

| Condition | Severity | Evaluation | Fired? |
|---|---|---|---|
| F1 | 90 | no mandatory `block` from any reviewer | **no** |
| F2 | 70 | reviewers with ≥2 mandatory warn-or-worse: EIC (D1, D3), R1 (D1, D3), R2 (D2, D3), DA (D1, D2, D3) = 4; R3 has one (D3). Threshold under `majority` for N=5 is 4 | **yes** (at the threshold) |
| F3 | 60 | no D4 `block` | **no** |
| F0 | 10 | not every mandatory dimension passes | **no** |

**Step 3 — Precedence.** F2 is the only fired condition. **editorial_decision = major_revision.**

D3 is `warn` for all five reviewers again. Round 5's concern about the abstract has moved
to the conclusion and the contribution list.

## Weakness sub-claim inventory (Step 1b; the denominator is the 4 non-DA reviewers)

| SC | Sub-claim | EIC | R1 | R2 | R3 | Disposition |
|---|---|---|---|---|---|---|
| SC-1 | Conclusion, contribution 2 and the title exceed the scoped abstract | raised (W1) | not-mentioned | corroborated (D3) | corroborated (W1) | **CONSENSUS-3** |
| SC-2 | The image-scale calibration result in the repository is unreported, and it does not favour h_eff **[supp]** | raised (W3) | corroborated (W4) | not-mentioned | raised (W1) | **CONSENSUS-3** |
| SC-3 | The family control cannot reject non-atomic references; no split by h; synthetic only | not-mentioned | raised (W1) | not-mentioned | not-mentioned | single (R1); DA-3 concurs |
| SC-4 | Table `tab:seed3` and the h=0 numbers should be rebuilt from the M=256 re-evaluation **[supp]** | not-mentioned | raised (W2) | not-mentioned | not-mentioned | single (R1, conf. 4) |
| SC-5 | The atomicity "dominant at image dimension" argument (ambient d; minimiser not reached) | not-mentioned | not-mentioned | raised (W1) | not-mentioned | single (R2); DA-4 concurs |
| SC-6 | Audit box: no h_eff step (contradicting contribution 3), no M/C/h guidance | raised (W2) | not-mentioned | not-mentioned | raised (W2) | corroborated (2) |
| SC-7 | Structure unchanged from round 5 | raised (W2) | not-mentioned | not-mentioned | not-mentioned | single (EIC) |
| SC-8 | Thm. `thm:calib`(b) scope at σ=0 and k=1536 not stated in the main text | not-mentioned | not-mentioned | raised (W2) | not-mentioned | single (R2) |
| SC-9 | Notation (h⋆, β, κ); Fig. 1 h⋆ against Sec. 4.1 | not-mentioned | not-mentioned | raised (W3) | not-mentioned | single (R2) |
| SC-10 | Calibration R² without run-level error | not-mentioned | raised (W3) | not-mentioned | not-mentioned | single (R1) |
| SC-11 | Prop. `prop:heffid`: h⋆∈𝓗 in the statement; what "the bound holds" checked | not-mentioned | corroborated (detailed comments) | raised (W4) | not-mentioned | corroborated (2) |

**DA-CRITICAL:** none. DA-1 corroborates SC-1, DA-2 corroborates SC-2, DA-3 corroborates
SC-3, and DA-4 corroborates SC-5.

## Points of disagreement

**R3 (minor_revision) against the others (major_revision).**
- *R3:* the remaining issues are reporting and wording.
- *EIC, R1, R2, DA:* SC-2 and SC-1 together change what the paper may claim about
  calibration. SC-3 asks for a control whose outcome is not known.
- *Type:* severity disagreement.
- *EIC arbitration:* major_revision, as the contract requires. The revision is, however,
  closer to minor than round 5's: of the six required items below, four are text or
  integration of results that already exist, and the two experimental ones (R4, and the
  pending CIFAR h=0/h=6 runs behind R3) are bounded.

**What h_eff is for, at image scale.**
- *R3 and DA:* at image scale, h_eff is a descriptor, not a predictor.
- *EIC:* it is the quantity that makes the level/slope audit interpretable.
- These are compatible. The paper should say both.

## Status of the round-5 roadmap

| Round 5 | Item | Status in this version |
|---|---|---|
| R1 | Re-scope title, abstract, conclusion | **Partly**: abstract done; conclusion, contribution 2 and title open (SC-1) |
| R2 | CIFAR re-evaluation or relabel; mask wording | **Done by relabelling**; re-evaluation now exists in the repository **[supp]** but is not used (SC-4) |
| R3 | Competing smoother | **Done** (Table `tab:families`); design limits in SC-3 |
| R4 | Thm. `thm:calib`(b) scope | **Partly**: √k and σ in the abstract; σ=0 not stated (SC-8) |
| R5 | Restructure (h_eff and audit forward) | **Open** (SC-7) |
| R6 | Estimator inconsistency | **Done** |
| R7 | Theory-to-data statements (‖J‖², F, Table 10) | **Done** |
| S1 | Std conventions; n=2 language | **Done** |
| S2 | Leave-one-run-out R² | **Open** (SC-10) |
| S3 | CFG reference; bib | **Done** |
| S4 | Rename h⋆, β, κ | **Open** (SC-9) |
| S5 | "Using the audit" guidance | **Open** (SC-6) |
| S6 | Posterior-free use, or explanatory framing | **Open**; sharpened by SC-2 |
| S7 | Atomicity framing (DA-3) | **Open**, and the floor argument has grown (SC-5) |
| S8 | Deduplicate App. D; re-file the misplaced paragraph | **Partly**: App. `app:exp4` still repeats Sec. 4.1 nearly verbatim (L3333–3347 and L3400–3411 against L438–447 and L458–467); Table `tab:exp1` sits under "Scope: what is and is not predicted" (L2377) |
| S9 | Low-precision items | **Done** |

## Editorial Decision

### Decision: **Major Revision**

| Reviewer | Recommendation | Confidence | Rubric (weighted) | ICLR-scale reading* |
|---|---|---|---|---|
| EIC (SAC) | Major (close to Minor) | 4 | 66.2 | 6 |
| R1 (methodology) | Major | 4 | 64.7 | 5 |
| R2 (domain) | Major | 4 | 65.8 | 5 |
| R3 (practice) | Minor | 3 | 63.8 | 6 |
| DA | — (no CRITICAL) | — | — | — |

\*An informal translation to the ICLR 1–10 scale. The four-reviewer mean is 5.5, up from
5.25 in round 5: borderline, leaning accept if the required items below are done.

### Decision rationale
- **The contract fixes the decision.** F2 fires at the threshold: four reviewers score at
  least two mandatory dimensions `warn`. Nobody scores `block`, and no DA finding is
  CRITICAL.
- **The unanimous concern is again coherence (D3), now in the summary claims.** The
  abstract is right. The conclusion and contribution 2 claim a predictive law that the
  appendix and the supplementary image result do not support.
- **Why not Minor.** SC-2 requires reporting a negative image-scale result and adjusting
  claims to it. SC-3 asks for a control whose outcome could change the "Nadaraya–Watson"
  wording.
- **Why not Reject.** Every round-5 correctness item is fixed. The d=2 law is well
  supported and reproduces. Every required item has a bounded fix, most of them textual.

## Required revisions (must fix)

| # | Item | Sub-claims | Source | Severity | Section | Effort |
|---|---|---|---|---|---|---|
| R1 | Report the image-scale held-out calibration **[supp]** (coverage, PIT, extraction against h_eff, sample spread and iteration), with a finite-M reference for coverage at M=64, or rank-based coverage | SC-2 | EIC W3, R3 W1, R1 W4, DA-2 | Major | Sec. 4.3, Limitations, App. `app:calibdetails` | 1 day |
| R2 | Bring the conclusion, contribution 2 and (optionally) the title to the abstract's scope; reconcile "memorisation … set by one number" with the extraction result | SC-1 | EIC W1, DA-1, DA-7 | Major | Sec. 1, Sec. 6 | 0.5 day |
| R3 | Rebuild Table `tab:seed3` and the Sec. 4.2 h=0 numbers from the 48-condition, M=256 re-evaluation, once the h=0/h=6 re-runs finish **[supp]** | SC-4 | R1 W2 | Major | Sec. 4.2, App. `app:exp4` | 0.5 day after the runs |
| R4 | Strengthen the family control: a y-dependent non-atomic competitor (endpoint-smoothed, tr Cov + dρ²); results split by h; say that a constant-covariance reference has R²≤0 by construction; ideally the CIFAR checkpoints too | SC-3 | R1 W1, DA-3 | Major | Sec. 4.3, App. `app:families` | 1–2 days |
| R5 | Qualify the floor argument: intrinsic against ambient dimension, and the minimiser against the trained model; or measure F on CIFAR conditions; drop "dominant" | SC-5 | R2 W1, DA-4 | Major | Sec. 3.2, App. D | 0.5–1 day |
| R6 | Make the audit box match contribution 3: an h_eff/h_mean step, minimum M and C, how to read h_eff/h | SC-6 | EIC W2, R3 W2 | Major | App. `app:audit` | 2 h |

## Suggested revisions (should fix)

| # | Item | Sub-claims | Source | Priority |
|---|---|---|---|---|
| S1 | Leave-one-run-out error and the binomial noise ceiling for the calibration R² | SC-10 | R1 W3 | P2 |
| S2 | Light restructuring: swap contributions 1 and 2; move Sec. 3.3 to the appendix | SC-7 | EIC W2 | P2 |
| S3 | State in Limitations which results cover σ=0 conditioning | SC-8 | R2 W2 | P2 |
| S4 | Rename h⋆, β, κ; give Fig. 1's h⋆ and say it is per-condition | SC-9 | R2 W3 | P2 |
| S5 | Prop. `prop:heffid`: h⋆∈𝓗 in the statement; say what "the bound holds at all 75" checked | SC-11 | R2 W4, R1 | P3 |
| S6 | h_eff at CIFAR h=0 and h=6 once the re-runs finish | — | EIC Q2 | P2 |
| S7 | Deduplicate App. `app:exp4` (L3333–3411) and re-title the subsection holding Table `tab:exp1` | — | round-5 S8 | P3 |
| S8 | One sentence on GPU non-determinism of h_eff across re-runs (4.79/4.80/4.93) | — | R1 detailed | P3 |

## Revision roadmap

**Priority 1 — results that already exist (2 days)**
- [ ] R1: image-scale calibration in the paper
- [ ] R3: seed table from the re-evaluation (after the h=0/h=6 runs)
- [ ] R2, R6: conclusion, contribution 2, audit box

**Priority 2 — one new control and one argument (2–3 days)**
- [ ] R4: family control with an endpoint-smoothed competitor, split by h
- [ ] R5: the floor argument
- [ ] S1, S6

**Priority 3 — text (1 day)**
- [ ] S2–S5, S7, S8

R4's endpoint-smoothed family and the split by h are numpy-only on the saved synthetic
samples (`scripts/heff_family_test.py`). R1 and R3 need the server runs that are in
progress.

## Closing
The revision did what round 5 asked where it was asked for evidence, and did it well. What
is left is to let the paper's summary say what its evidence says. In low dimension, a
trained conditional flow sits at an effective bandwidth over its training atoms. At image
scale it does so in its first two moments, and there h_eff describes the model rather than
predicting its coverage. That paper is publishable.
