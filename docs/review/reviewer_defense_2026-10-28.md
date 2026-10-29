# Reviewer defense — 28 October 2026

> **Post-merge status (29 October 2026):** this is a historical review of the pre-merge working copy. Main now includes `a25bbfe` and its experiment artifacts and wording fixes; individual findings below are not an outstanding-task checklist. Consult the worktree reuse assessment for the remaining experimental gaps. The older `report.md` is preserved at [archive/report_2026-10-19.md](archive/report_2026-10-19.md); it is historical material, not a new proof certification.

> **Update after inspecting `.claude/worktrees`:** the absence of learned-composition, EXP-B and EXP-C evidence below applies to the main manuscript, not the whole workspace. The reviewer-defense worktree contains those experiments. See `worktree_reuse_assessment_2026-10-28.md` and its independent saved-state check before planning new experiments. In particular, do not rerun the composition pilot from scratch or describe it as nonexistent; its remaining gap is attribution between parametrization, loss weighting and the rescaled input feature.

Scope: the working copy of `paper/main.tex` on HEAD `f3beed4`, including pre-existing uncommitted edits. Target: TMLR, as specified in the manuscript preamble and `paper/README.md`. This report leaves the manuscript and result files unchanged. Source locations below refer to this working copy; LaTeX labels are the stable identifiers.

This is a claims-and-evidence review, not a fresh proof certification or an exhaustive literature search. Historical verifier reports are supporting records, not independent verification performed in this review. Suggested responses describe existing evidence unless explicitly marked as proposals.

**Assessment.** The paper now has a defensible theoretical story: positive field mixtures and guidance individually retain training support; their composition can create a non-training endpoint; the signed covariance spectrum distinguishes attracting and null profile basins. The main remaining empirical gap is whether trained guided averages reproduce that mechanism. For a theory submission this is a limitation, not automatically a missing prerequisite: the theorems can support claims about exact fields without a trained-network counterpart.

TMLR evaluates support for claims and clear communication to an interested audience; a state-of-the-art benchmark is not itself required. Prioritize precise scope and numerical interpretation over adding an unrelated performance comparison. See the [official acceptance criteria](https://jmlr.org/tmlr/acceptance-criteria.html).

## 1. Weakness table

Severity denotes likely review impact, not a finding that a theorem is false.

| ID | Category | Concern and evidence | Severity | Best response |
|---|---|---|---|---|
| W1 | Experimental | No trained guided-averaging test. `tab:learned-averages` tests averaging alone; the central composition result is checked on exact fields. | High for practical claims; medium for exact theory | Keep the claim explicitly theoretical; add a matched learned composition pilot if feasible. |
| W2 | Technical | Transfer conditions are not independently measured. The manuscript correctly explains that scaled error can equal endpoint error for bounded learned velocities, making their empirical correlation uninformative (`sec:transfer`, lines 673–685). | High if used as an explanation of learned behavior | Present the theorem as a conditional stability statement, not an empirical mechanism already established. |
| W3 | Presentation | Introduction says a learned endpoint prediction “does not converge” (lines 143–145). Convergence to the wrong point also permits a non-training endpoint. | Medium | Say “does not converge to the identified training atom”; qualify separate-intervention claims by their hypotheses. |
| W4 | Presentation | Conclusion lists when guided averaging leaves support in high dimension as open (lines 905–907), although `thm:spectral` already supplies a criterion under explicit conditions. | Medium | Restrict the open question to cases outside hyperbolicity/face assumptions and quantitative basin sizes. |
| W5 | Experimental | High-dimensional tests use cospherical atoms, all tied at zero. They do not exercise the off-tie remainder or perturb atom geometry. `prop:composition-open` perturbs priors/weights/guidance, with atoms fixed. | Medium | State what each robustness result covers; add an exact-field test with extra farther atoms. |
| W6 | Statistical | “Below the sampling resolution of 1/2048” (line 830) is a detection statement, not an upper confidence bound. Zero hits does not imply zero basin probability. | Medium | Report counts and a one-sided binomial bound for the finite-time event; separate it from asymptotic support. |
| W7 | Statistical | Five seed means, two-seed architecture variants, biased energy V-statistics, and nested queries limit uncertainty claims. Existing text is mostly appropriately descriptive. | Medium | Preserve per-seed values and ranges; use paired seed-level changes for any comparative inference. |
| W8 | Statistical | “Instance accounts for about 78% of the combined variance” (line 2693) uses two one-factor sweeps sharing one run, without a crossed design or interaction estimate. | Medium | Call it a descriptive ratio of the two observed sweep variances, or omit the percentage. |
| W9 | Technical | Strictly positive priors on common support and a Gaussian linear path are substantive restrictions. Hard-label averaging is an explicit counterexample to removing positivity. | Medium | Keep assumptions close to claims; do not infer diffusion-schedule or different-support generality. |
| W10 | Experimental | The 38% off-atom CIFAR result at h=6 mixes learning, terminal cutoff, solver error and the nearest-neighbor rule. It has no established causal explanation. | Medium | Keep it as an observed finite-cutoff discrepancy; a fixed-checkpoint cutoff/solver factorial is the next diagnostic. |
| W11 | Presentation | Novelty could be mistaken for empirical memorization or general guidance geometry, both previously studied. Current related work makes the relevant distinction. | Medium | Emphasize convergence plus null non-atom basins on common finite support, and the composite/spectral results. |
| W12 | Experimental | Four adaptive near-tie solver failures and finite-time profile classification constrain numerical claims. Forward-invariant stopping rules for the scalar composition calculation are stronger evidence than a terminal-distance threshold, but use floating-point arithmetic. | Low–medium | Retain failures and distinguish these two numerical protocols. |
| W13 | Experimental | Image evidence uses N=2000, one inpainting mask, three instances; class-label controls have one seed. | Low–medium | Frame it as a controlled image experiment; do not claim universality across applications. |

**Already addressed since the older defense:** the spectral theorem and tests go beyond two atoms/one dimension; architecture/optimizer controls, class labels, and EXP-1 instance/training sweeps are now in the appendix; the abstract distinguishes finite-time collapse from learned asymptotic convergence. Do not propose restoring these results again. `report.md` describes older manuscript content and is not a current inventory.

## 2. Anticipated reviewer questions, ranked by likelihood

Likelihoods are qualitative judgments, not estimated probabilities.

### Q1 — Very high: “What do the exact-field results establish about trained generators?”

**Motivation:** W1–W2; the learned averaging pilot itself departs from its exact reference.

**Answerable:** Partly. `thm:transfer` and `prop:localtransfer` give conditional statements; `fig:exp1-collapse`, `fig:cifar-collapse`, and `tab:p7kernel` give finite-cutoff observations. There is no measured asymptotic error certificate.

**Draft response:** “Our classification concerns exact empirical fields. The learned experiments document finite-cutoff collapse and reference tracking, while the transfer statements specify additional trajectory-error conditions needed to inherit an endpoint conclusion. We do not establish those conditions for the trained networks.”

### Q2 — Very high: “Does the composition mechanism occur in a trained network?”

**Motivation:** The most surprising result could otherwise appear disconnected from the learned experiments.

**Answerable:** No for the learned mechanism. `thm:composition`, `prop:composition-open`, `fig:composition` and `tab:composition` support the exact result; `tab:learned-averages` is averaging without guidance.

**Current response:** “The positive-probability composition result is proved and numerically checked for exact fields. Our trained averaging pilot does not test guided averaging, so it cannot establish that learned networks reproduce the threshold.”

**New work needed:** Matched conditional and unconditional networks trained on the same two-atom instance, then the four arms in ablation A1 below. Do not insert a positive learned result into a rebuttal before observing it.

### Q3 — High: “Why is this more than a two-point construction?”

**Motivation:** W5 and the scalar threshold in the abstract.

**Answerable:** Yes within stated assumptions. `thm:spectral`, `cor:spectral-threshold`, `tab:spectral`; `results/theory_spectral_20261020/summary.json` includes a triangle, nine-vertex simplex, rectangle and 256-vertex box.

**Draft response:** “The scalar construction gives the explicit threshold. The spectral theorem treats hyperbolic profiles in arbitrary dimension: negative definiteness gives an open basin, whereas a positive eigenvalue gives a null profile basin. Completeness requires the additional face condition; the current numerical tests use cospherical configurations.”

### Q4 — High: “What does the matrix criterion add over the covariance trace test?”

**Motivation:** A reviewer may see an unnecessarily elaborate reformulation.

**Answerable:** Yes. `thm:spectral` and `tab:spectral`; rectangle and box at w=1 have trace approximately −0.572 but are saddles.

**Draft response:** “A negative trace can coexist with a positive eigenvalue, so it does not imply attraction. The rectangle and box give this case: their profile basin is null by the spectral theorem despite negative trace. The matrix criterion resolves precisely this ambiguity.”

### Q5 — High: “Isn’t the transfer bound tautological near a bounded learned field?”

**Motivation:** W2; `(1−t)Δ=(1−t)vθ+Zt−a`.

**Answerable:** Yes as a limitation, not as an empirical validation. `sec:transfer`, immediately after `thm:transfer`; `prop:loss-no-certificate` explains why training loss alone is insufficient.

**Draft response:** “If the learned velocity remains bounded and its trajectory converges, the scaled error tends to the endpoint displacement, as the manuscript explicitly notes. The bound is informative when error is controlled independently, for example uniformly in a trapping neighborhood. We do not interpret a correlation of measured scaled error and endpoint displacement as independent evidence.”

### Q6 — High: “Do zero hits above the high-dimensional threshold refute positive basin probability?”

**Motivation:** Zero sampled hits at 1.1wc and 2wc for the eight-dimensional simplex.

**Answerable:** Partly. `tab:spectral` and its raw summary establish zero observed hits, not zero probability. The theorem establishes an open basin under its hypotheses; its Gaussian mass need not be large.

**Draft response:** “The theorem guarantees positivity, without a lower bound on Gaussian mass. Zero hits among 2048 independent Gaussian draws has an exact one-sided 95% binomial upper bound of approximately 0.00146 for the event measured by the numerical protocol. This bound does not account for finite-time or classification error and is not an upper bound on the asymptotic basin without additional justification.”

### Q7 — High: “Identifying labels make hard collapse immediate. What happens for shared labels?”

**Motivation:** W9; class labels do not identify an example.

**Answerable:** Yes. `app:exp4`, paragraph “Class labels,” and `fig:image-class`.

**Draft response:** “At a shared hard label the exact reference is the empirical law on examples carrying that label, rather than a single atom. Our class-conditional CIFAR control retains within-class variance; both reported runs end near 0.76 of the within-class scatter. That second-moment observation does not establish the learned endpoint law or learned atomicity.”

### Q8 — High: “What is new relative to score-mixing convergence results?”

**Motivation:** W11; close theoretical predecessors already study mixed guidance and Voronoi geometry.

**Answerable:** Yes for a narrow comparison, not an exhaustive priority claim. The related-work paragraph cites Liu–Zuazua, Theorem 3.18 and Remark 3.19; checked against the [version-1 primary source](https://arxiv.org/html/2605.12231v1).

**Draft response:** “Their original-flow convergence criterion assumes exclusion of non-minimizing critical limit points. On a common finite support, our positive-mixture and guidance results establish convergence and null non-atom basins without that trajectory premise. Our support and path restrictions differ, so we do not claim to subsume their broader framework.”

### Q9 — Medium–high: “Could the claimed endpoints be a solver or terminal-time artifact?”

**Motivation:** W12; singular terminal dynamics and failed near-tie integrations.

**Answerable:** Partly. `sec:intervention-tests` reports unchanged assignments under doubled resolution in 200 stress-test cells; `app:intervention-protocol` describes forward-invariant scalar stopping criteria and four retained adaptive failures. High-dimensional bounded-profile fractions are finite-time diagnostics.

**Draft response:** “The stress tests are consistency checks with resolution refinement. For the scalar composition probabilities, the proof supplies sufficient invariant conditions for assigning the limit, evaluated numerically with bisection. Those are floating-point computations, not interval-arithmetic certificates, and we retain the unresolved adaptive near-tie failures.”

### Q10 — Medium–high: “What explains the 38% off-atom CIFAR samples at h=6?”

**Motivation:** W10; apparent conflict with the exact support theorem.

**Answerable:** No for causal attribution; yes for compatibility. `sec:p7`, `tab:cifarddpm`, and `sec:limitations` explicitly distinguish the finite learned sampler from the exact limit.

**Draft response:** “This is a finite-cutoff observation under a nearest-neighbor criterion, while the atomicity theorem concerns the exact field at the terminal limit. We have not isolated learning, cutoff and discretization contributions. The observation therefore neither refutes the theorem nor identifies which of those mechanisms dominates.”

### Q11 — Medium: “Are averaging effects statistically reliable across independent runs?”

**Motivation:** W7; a fresh-query energy range of 0.001758–0.544995 at the widest radius.

**Answerable:** Descriptively, yes; a population-level significance/equivalence claim, no. `tab:learned-averages` and `results/novelty_interventions_20261016/learned_seed_aggregates.csv` contain five-seed means and ranges.

**Draft response:** “Fresh-query mean normalized energy rises from 0.007227 at radius zero to 0.143176 at radius 1.5, with substantial seed heterogeneity. These are biased finite-sample descriptive statistics, not a test of equality or equivalence. Conditions and generated samples are nested within each of the five independent problem seeds.”

### Q12 — Medium: “Are instance and optimization effects really separated?”

**Motivation:** W8 and the 78% attribution sentence.

**Answerable:** Partly. `tab:ablation` and the following EXP-1 paragraph report two ten-run one-factor sweeps: 0.338±0.064 for training randomness and 0.404±0.121 for instance randomness.

**Draft response:** “The two sweeps isolate each source of randomness around fixed settings and show larger variation across the tested instances. They are not a crossed variance-component design, and do not estimate instance–training interactions. CIFAR still confounds the two sources.”

### Q13 — Medium: “Do the conclusions cover standard diffusion schedules, changing supports, or arbitrary guidance schedules?”

**Motivation:** W9; practical CFG is used more broadly than this model.

**Answerable:** No for those general extensions. Yes for the theorem's actual scope: `thm:posmix`, `thm:schedule`, `sec:limitations`.

**Draft response:** “The results are stated for the Gaussian linear path and common finite support. Positive-bandwidth mixtures require strictly positive priors; the schedule theorem covers bounded nonnegative guidance of bounded variation near the endpoint. We do not assert the same classification outside these hypotheses.”

### Q14 — Medium: “Does leaving the training set improve posterior sampling or generation quality?”

**Motivation:** A midpoint attractor may be interpreted as a proposed generalization method.

**Answerable:** No quality improvement is established. `thm:composition` shows mass at a non-training circumcentre; `prop:atomicity` and `fig:mechanism` separate moment matching from distributional recovery.

**Draft response:** “Off-training-set support is the property classified, not a quality metric. The composite example creates an additional atom at a circumcentre, which need not be a valid or likely posterior sample. We make no posterior-quality or benchmark-performance claim for that intervention.”

## 3. Recommended ablation subset

For this theory paper, rank by how directly a comparison discriminates the proposed mechanism. Metric magnitudes below come from saved results; they are not newly executed experiments. New studies have no known effect size.

| Priority | Study and status | Observed magnitude / unique role | Placement and cost |
|---|---|---|---|
| A1 | **New:** matched learned and exact four-arm comparison: single conditional field, label average, guidance alone, guided average | The only comparison that tests whether the headline composition mechanism survives learning. Effect unknown. | Main if informative; requires matching conditional/unconditional checkpoints, otherwise new training. |
| A2 | **Exists:** scalar exact threshold sweep at B=1,2,3 | At B=2, midpoint mass is 0 below threshold, ≈0.021 at 1.1wc, 0.182 at 2wc, 0.809 at 10wc. Directly supports the core transition. | Main figure, detailed table in appendix; no new training. |
| A3 | **Exists:** rectangle/box negative-trace saddle versus sink | Rectangle: zero observed hits at w=1 versus 0.2461 at w=5; box: zero versus 1/512 at the last checkpoint. Distinguishes spectrum from trace. | Promote one compact comparison into the main text; rest in appendix. |
| A4 | **Exists:** unequal priors, weights and guidance in scalar exact composition | Reported midpoint masses 0.71–0.86. Addresses symmetry in parameter space, with geometry fixed. | Appendix plus one main-text sentence; no new training. |
| A5 | **Exists:** hard identifying labels versus class labels, with architecture and seed sweeps as controls | Hard EXP-1 variance 0.396±0.127; class runs end near 0.76 of class scatter. Supports the identification distinction, not distributional equality. | Appendix; retain current controls without expanding every sweep. |
| A6 | **New:** add farther, non-tied atoms around a configuration with a verified attracting profile | Exercises the off-tie remainder absent from the present cospherical tests. Effect unknown; choose geometry and parameters by the theorem before sampling. | Appendix exact-field check, no training; higher value than another symmetric configuration. |
| A7 | **New:** fixed learned checkpoint, paired sources, multiple cutoffs and independently refined solvers at CIFAR h=6 | Can distinguish some cutoff/discretization sensitivity from persistent learned discrepancy. It cannot alone certify the limiting endpoint law. | Appendix diagnostic; checkpoint availability and inference cost must be checked first. |

**Concrete A1 protocol:** start with the actual two-atom setting for which B and wc are defined. Use the same atoms, labels, source draws, terminal cutoffs and solver-refinement checks across all four arms, with w/wc below and above 1. Do not assign that scalar wc to a generic twelve-atom network. Evaluate whether samples approach the predicted midpoint as the cutoff advances, separately from merely exceeding a nearest-atom distance threshold. Report conditional/unconditional field errors, per-training-seed results, and the exact composite reference. A learned unconditional field must use the same training instance; do not pair networks from different problem seeds.

Existing experiments do not form an additive method with independently beneficial components. The four arms above test an interaction between interventions, rather than a sequence of performance improvements.

**Minimal selection without new training:** A2 in the main text, a compact A3 contrast, A4/A5 in the appendix. A1 improves empirical relevance but is not required to keep an explicitly exact-field claim. Do not revive the removed effective-bandwidth material solely to make the experimental section larger.

## 4. Negative and unresolved results to retain

- **Learned averaging:** increasing radius raises mean discrepancy but not on every seed. Show ranges and finite-time nearest-atom distances; describe a mismatch with the exact reference, without calling it a failure of the theorem.
- **High-dimensional zero hits:** retain them alongside the positive theorem; they expose unknown basin size and sampling limits.
- **Near-tie solver failures:** retain all four; separate unresolved trajectories from assigned outcomes.
- **CIFAR h=6:** retain the off-atom fraction and limited reference dynamic range. A narrow dynamic range weakens slope estimation, but does not by itself explain the negative slope or prove consistency with slope one.
- **Architecture control:** width 256 has lower training loss (0.460 versus 0.586) but similar variance at the measured budget. This illustrates why loss is not an endpoint certificate; it does not prove the optimization mechanism.

## 5. Suggested text edits — not applied

### E1. Introduction, practitioner paragraph (around lines 140–145)

Replace the sentence beginning “For a practitioner…” with:

> “Within the stated common-support and positivity assumptions, label noise, label averaging and guidance applied separately preserve the exact field's training support. Their composition can instead create a non-training attractor. For a learned field at an identifying label, the corresponding collapse guarantee requires its scaled trajectory error to vanish, equivalently that its endpoint prediction approach the identified training atom.”

This fixes convergence to the wrong point and avoids silently extending the positive-bandwidth result to hard-label averages.

### E2. Conclusion, open questions (around lines 905–907)

> “Open questions include the classification of nonhyperbolic profiles and configurations outside the face condition, quantitative bounds on basin probability in high dimension, the endpoint weights of averaged fields, and the source of off-atom samples in trained image samplers.”

This preserves the actual unresolved cases without overlooking `thm:spectral`.

### E3. EXP-1 seed paragraph (around lines 2691–2694)

> “The observed sweep variance is larger when varying the instance than when varying the training seed (population standard deviations 0.121 and 0.064, respectively). These one-factor sweeps do not estimate interactions between instance and training randomness.”

If retaining 78%, specify that it is `0.121²/(0.121²+0.064²)` for these two sweeps, rather than a population variance attribution.

### E4. Spectral experiment, zero-hit interpretation (around lines 828–831)

> “For the eight-dimensional simplex at 1.1wc and 2wc, none of 2048 sampled sources met the bounded-profile criterion at the last checkpoint. Zero hits gives an approximate one-sided 95% binomial upper bound of 0.00146 for that numerical event; finite-time classification uncertainty is separate. The theorem asserts a positive basin under its hypotheses without bounding its Gaussian probability.”

### E5. Class-label paragraph, closing sentence (around line 2736)

> “Shared labels remove the exact collapse onto one example: the reference endpoint law remains supported on training examples within the class. The learned variance measurements do not establish that support restriction for the trained sampler.”

This prevents a theoretical support statement from being inferred from a variance measurement.

### E6. Reproducibility opening (around line 910)

> “Reported numbers are linked to analysis code and saved experimental outputs in the supplementary material. Some older checkpoints were not retained; those results can be checked against saved outputs but cannot all be regenerated from weights.”

This matches `paper/README.md`; do not claim complete rerun reproducibility from retained weights unless checkpoint availability is verified.

## 6. Review evidence and validation limits

Read: current main text, theorem statements, experimental appendix, `paper/README.md`, the historical defense, spectral verification record, scalar/spectral JSON summaries, and learned-averaging aggregate CSV. No figure-layout audit or full proof re-verification was performed. No training or new sampling was run.

Validation: `scripts/verify_paper_numbers.py` completed with **429 checks passed, 0 failed**, using the bundled Python runtime after the PATH Python alias could not start. The checker validates its covered numbers and manuscript strings against saved results; it does not certify proofs, complete numerical coverage, or full reproduction from checkpoints.

External checks were limited to the official TMLR criteria and the closely related Liu–Zuazua version-1 theorem/remark. Neither constitutes a comprehensive literature or bibliography audit.
