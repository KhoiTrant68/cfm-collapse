# Reviewer defense — 16 October 2026

**Revision status:** The assessment below records the draft before the accepted
revision. The canonical manuscript now has a theory-focused title and abstract,
the five-new-seed validation, a clarified fresh-label domain, and Appendix F with
targeted solver results. The synthetic outlier persists under DOP853; the three
selected CIFAR classifications persist under refined Euler and RK4. The bounded
comparison is in [theorem_comparison_2026-10-16.md](theorem_comparison_2026-10-16.md).
These changes address presentation and missing evidence; they do not turn the
historical simulated recommendation into an acceptance or novelty certificate.

## Assessment and scope

**My simulated recommendation for the current manuscript: leaning reject, with a
credible path to revision.** This is an editorial/research judgment, not an actual
review, acceptance probability, or independent proof certificate. The strongest
case is a theory paper about which exact empirical conditioning interventions
preserve atomicity and what teacher loss cannot certify. The title and prominent
effective-bandwidth narrative still pull attention toward a weaker empirical claim.

The abstract and conclusion already distinguish exact fields from trained models,
and explicitly say that moment agreement does not identify a distribution. That is
a strength. The new held-out results do **not** refute a universal full-law claim
that the current abstract actually makes; the issue is consistency of emphasis,
scope, significance, and incorporation of the new evidence.

The [ICLR 2027 reviewer guide](https://iclr.cc/Conferences/2027/ReviewerGuidelines)
asks whether claims are supported and the paper contributes valuable new knowledge;
it explicitly does not require state-of-the-art results. Consequently, adding a
leaderboard or a new method is not a mandatory repair for this analysis paper.

Sources inspected: canonical `paper/main.tex` (title, abstract, introduction,
contributions, conclusion, intervention/certification statements and relevant
experimental appendices); `paper/refs.bib`; existing literature and theory audits;
`results/independent_seeds_20261016/SUMMARY.md` and `summary.json`;
`results/intervention_cifar_pilot_20261016/SUMMARY.md`; existing measurement audit.
This review did not re-prove all mathematical results or certify theorem priority.
The three recently supplied OpenReview PDFs were not fully accessible; they are
not being silently counted as inspected related work.

## 1. Vulnerabilities ranked by decision impact

| Priority | Category | Vulnerability | Existing evidence / required repair |
|---|---|---|---|
| P0 | Originality | Empirical memorization, conditional expectation and generic kernel identities are established. The specific priority of the convergence/atomicity results remains unverified. | Compare exact statements and assumptions against closest work; separate known reference machinery from the proposed new theorem delta. More training cannot settle priority. |
| P0 | Contribution/presentation | “Trained Conditional Flows Memorise at an Effective Bandwidth” suggests a more general organizing principle than the new evidence establishes. The theoretical contribution and descriptive audit compete for the main story. | Recenter title and contributions on atomicity/certification; retain bandwidth as an explicitly limited diagnostic. |
| P0 | Empirical scope | The five new problem seeds show residual held-out distribution discrepancy. Gaussian wins the fitted-family comparison at h=.1, not at h=0. | Include the new per-seed law comparison. Preserve the distinction between training-label moments and held-out-label laws. |
| P0 | Numerical validity | One synthetic condition fails the practical solver screen. CIFAR joint coverage remains solver-sensitive at 400 steps. | Keep the failures visible. Either resolve selected cases with a higher-accuracy control or state that numerical/learned-field attribution remains unresolved. |
| P1 | Significance | The bandwidth diagnostic does not yet show reliable predictive value beyond free spread/loss/iteration diagnostics. | Existing audit reports incremental R²=.03885 with interval [-.036,.216]. Present the limitation; do not sell a superior calibration predictor. |
| P1 | Statistical validity | Checkpoints and conditions are nested; the independent synthetic units are five new problem seeds. CIFAR has only eight distinct test images in the latest pilot. | Report all seeds and paired inputs, with counts at the correct level. Do not turn 640 conditions or thousands of pixels into independent model replicates. |
| P1 | Measurement | New randomized-tie ranks are valid under the specified exchangeability contract; old deterministic midranks do not have the same tied null. Joint scores depend on chosen PCA dimension/ridge. | Document metric version, tie handling, finite-M reference and training-only PCA. Do not merge old/new tables as if identical. |
| P1 | Theory-to-network transfer | Exact-field atomicity does not imply trained-network endpoint atomicity. A finite-time nearest-neighbor distance does not certify exact membership. | Use separate oracle and network panels; state finite terminal time and numerical limits beside each result. |
| P1 | Theory usefulness | The risk-transfer assumption is restrictive and is not certified by observed teacher loss or empirical error ratios. | Present a conditional theorem plus a counterexample, not an operational global certificate for the trained models. |
| P2 | Packaging | The canonical source still uses TMLR style; the previously built PDF was 89 pages with a long appendix. New experiments have not been integrated. | Prepare the correct venue version and a coherent main-paper path. Do not equate number of propositions/experiments with significance. |

Already handled correctly: the manuscript qualifies the Lipschitz floor as a result
for a specified function class, not an explanation of the measured optimization
plateau; restricts its endpoint-noise comparison to the interventions analyzed;
and acknowledges limited image-level calibration utility. Do not manufacture new
reviewer objections by ignoring these existing caveats.

## 2. Ten anticipated reviewer questions

Rank is qualitative likelihood/decision impact, not a numerical probability.
Draft replies below state only supportable facts. They must not be pasted into a
rebuttal with “we revised” claims until those revisions actually exist.

### Q1 — What is new beyond known empirical memorization? [Very high]

**Reviewer:** “The endpoint of the exact empirical flow is known to memorize.
Which theorem adds a materially new result?”

**Trigger:** Bayes/NW identities and single-label collapse dominate the early
contribution list; several close sources already treat empirical conditional laws.

**Answerable:** **Partly.** We can identify a specific statement delta from the
paper, but have not completed a priority audit for that delta.

**Draft response:** “The empirical conditional reference is background machinery.
The proposed extension concerns convergence and almost-sure atomicity under label
averaging and fixed nonnegative CFG, including signed guided coefficients and
exceptional tie trajectories. We must distinguish this statement from the nearest
prior theorems before asserting originality.”

**To close:** a statement/assumption/conclusion comparison with Baptista,
Dasgupta, Pfrommer and the nearest empirical-flow dynamics results. Existing
sources: `docs/review/venue_contribution_evidence_2026-10-16.md` and
`docs/audit/research_agent_2026-10-16/05_Lit_Grounding.md`. Those audits are bounded,
not a priority certificate. Keep “first” claims out pending that comparison.

### Q2 — Does a scalar bandwidth identify the trained law? [Very high]

**Reviewer:** “Matching a mean and a trace does not identify a distribution. Is
effective bandwidth a law or a descriptive fit?”

**Trigger:** title and contribution 3; the current abstract already gives the
correct qualification, but new distribution-level evidence is absent from it.

**Answerable:** **Yes, for the limited interpretation.** Five new seeds, both
h arms, 64 held-out conditions/run, M512; 640 primary and 640 same-moment-control
energies were independently recomputed.

**Draft response:** “It is a descriptive moment fit. At checkpoint 200k, the
median across five seed-level mean excess energies is .4301 at h=0 and .008118 at
h=.1. Gaussian is closest among the four protocol-fitted references on all five
smoothed-label seeds and none of the hard-label seeds; these findings do not
establish equality of held-out laws.”

**To close:** integrate `results/independent_seeds_20261016/SUMMARY.md`; label the
metric as distance to a fitted reference, not distance to the true posterior.

### Q3 — Why test h=0 on labels absent from the empirical support? [Very high]

**Reviewer:** “Your collapse theorem is at training labels. Does the new held-out
failure test a different claim?”

**Trigger:** new condition 50 in seed 1004 is outside the training-label range.

**Answerable:** **Yes.** This is an essential scope distinction.

**Draft response:** “Yes. The h=0 empirical conditional law is specified at the
training labels; the new experiment probes the learned model’s extension to fresh
labels. Its failure limits a general effective-bandwidth interpretation outside
the fitted conditions and does not contradict the hard-conditioning theorem at
identifying training labels.”

**Evidence:** outlier query y=1.61918; training-label range [-1.17355,1.18362].
Do not reframe this as a theorem counterexample or retrospectively exclude it.

### Q4 — Are the deviations numerical artifacts? [Very high]

**Reviewer:** “Your ODE becomes singular near the endpoint. Why attribute spread
or off-atom samples to model error?”

**Trigger:** finite terminal time, low-step original image sampling and failed
synthetic/CIFAR numerical controls.

**Answerable:** **Partly.** 639/640 new synthetic conditions pass the frozen
practical screen, not a rigorous solver certificate. One condition is unresolved.

**Draft response:** “We pair source draws across RK4 resolutions and retain the
one unresolved synthetic condition in the main statistics. For CIFAR, 200-to-400
Euler RMS is .0139–.0233 in the h=4 runs and joint coverage is still sensitive to
resolution. We therefore do not attribute all image-level deviations to learned
spatial error or treat 400 steps as the exact endpoint.”

**To close:** a bounded higher-accuracy check on synthetic seed1004/condition50
and the most sensitive CIFAR model/images; predefine stopping criteria. This is
more informative than another broad training sweep. Keep any terminal-time
change separate from solver refinement.

### Q5 — Are the sample counts and intervals overstated? [High]

**Reviewer:** “Are 48 checkpoints or 640 conditions independent replications?
Were conditions used to select bandwidth reused for validation?”

**Trigger:** headline 48/48 and 31/36 counts, bootstrap intervals and repeated
measurements from the same problem instances.

**Answerable:** **Yes, with explicit limitations.**

**Draft response:** “The new comparison has five independent problem seeds,
paired across h, with 20 training conditions for fitting and 64 fresh conditions
for evaluation. Conditions are nested within seeds; the old checkpoint counts
are descriptive counts, not independent replicates. The 16-pair null q95 envelope
is diagnostic and is not reported as a multiplicity-corrected rejection test.”

**To close:** show seed-level values and unmodified means beside medians. A
clustered interval requires clear unit definitions; with five clusters, avoid
strong population-wide significance claims. Broader testing is needed only if
such claims remain central.

### Q6 — What does the audit add beyond sample spread? [High]

**Reviewer:** “Why use an effective-bandwidth audit when free diagnostics predict
calibration as well or better?”

**Trigger:** the local-model R²=.90 may be read as diagnostic superiority.

**Answerable:** **Yes for a limitation; no for a superiority claim.**

**Draft response:** “We do not establish incremental predictive superiority.
The saved audit gives incremental R²=.03885 with an interval spanning zero.
The contribution of the reference is an interpretation relative to the finite
training set and a way to expose moment-versus-law differences, rather than a
better standalone calibration predictor.”

**Evidence:** `20_Reality_Gate.md`, C5, and the manuscript’s own caveat in
contribution 3. A new out-of-sample baseline comparison is needed only if the
paper continues to claim practical predictive advantage.

### Q7 — Is the loss counterexample an unrealistic boundary-layer construction? [High]

**Reviewer:** “The construction puts large expansion in a thin late-time layer.
Does it say anything about bounded-regularity neural models?”

**Trigger:** spatial Lipschitz constants grow along the counterexample family.

**Answerable:** **Yes for the theorem’s stated class; not for universal neural
realizability or a common Lipschitz cap.**

**Draft response:** “Each constructed field has a finite spatial Lipschitz
constant, but the family has no shared cap. The counterexample rules out an
endpoint certificate based solely on teacher loss over that stated class; it
does not claim every architecture realizes the construction. The matched-loss
illustration compares exact fields with different regularity, not a neural
single-factor ablation.”

**Evidence:** `prop:loss-no-certificate`; matched loss/d=.0113784 gives endpoint
variance/d=1 for the amplifying field versus .000157695 for the selected
Lipschitz attainer. Keep the sharp floor and time-dependent-cap discussion as
complementary scope, not a demonstrated optimization mechanism.

### Q8 — Is the risk-transfer assumption circular or untestable? [High]

**Reviewer:** “You assume learned-path error is controlled by teacher error. Is
this already the hard part of certification?”

**Trigger:** assumption m(t)≤K(t)r(t); uniform density domination can fail even
between closely related Gaussian laws.

**Answerable:** **Partly.** The theorem is explicitly conditional. A usable global
K for trained networks is not established.

**Draft response:** “The transfer condition is an additional assumption, not a
consequence of training loss. The theorem states what a finite-time certificate
would require; our empirical ratios do not certify a global K. At t=.999 the
hard-label learned-path/teacher-error ratios range from 2.58e5 to 6.07e5 on the
five new seeds, illustrating why teacher-path error alone is insufficient.”

**To close:** either keep this as a conditional positive result, or derive an
independently checkable sufficient condition before advertising an operational
certificate. Do not turn sampled ratios into a uniform bound.

### Q9 — Does the image calibration experiment establish posterior recovery? [High]

**Reviewer:** “Pixel coverage improves with label noise, but are correlations,
finite-sample references and numerical errors controlled?”

**Trigger:** pixel versus joint coverage, only eight distinct new test images,
PCA/ridge choices, and mixing metric versions.

**Answerable:** **Partly.** The improved marginal behavior is supported; posterior
recovery is not.

**Draft response:** “The new pilot uses randomized tie ranks, training-only PCA
and identical test images/source draws across models and solver resolutions.
At 400 steps pixel coverage is .0728–.0830 for h=0 and .7709–.7983 for h=4,
against the M32 central-rank reference .87879. Joint32 coverage for h=4 varies
from .375 to .875 across seeds, and remains solver-sensitive; these results do
not certify posterior recovery.”

**To close:** expand the number of independent test images after resolving the
targeted numerical cases if a broad image-calibration claim is retained. Treat
PCA/ridge as part of the score definition. Pooled calibration over images does
not prove calibration at every fixed condition.

### Q10 — Do the new intervention results transfer to trained networks? [Medium–high]

**Reviewer:** “The oracle theorem is exact, but the experiments use a finite
neural approximation. Which causal claims are actually tested?”

**Trigger:** oracle label averaging/CFG panels could be mistaken for interventions
on trained CIFAR networks.

**Answerable:** **Partly.** The new oracle arms are directly verified, not neural
guarantees. The old paper already has a small trained endpoint-noise comparison.

**Draft response:** “The oracle study isolates hard conditioning, positive-label
noise, averaging three fields and fixed CFG under shared geometry and sources.
It illustrates exact-field endpoint behavior. The trained CIFAR experiment
compares existing h=0 and h=4 models; it does not establish the exact-field CFG
or averaging conclusion for arbitrary learned networks.”

In particular, atomicity under averaging/CFG does not identify their endpoint
probabilities. Do not substitute the original label-noise NW weights for those
intervened endpoint weights without a separate result.

**Evidence:** 35 ODE arms across five geometry seeds, mean atom distance ≤4.60e-6
at epsilon1e-6; target-noise controls retain .178–.199. Existing `app:tgt` tests
endpoint noise at N50,h=.1 on two seeds and reports improvements in that setting.
Do not state that trained endpoint interventions have never been tested, or
generalize the two-seed low-dimensional result to image-scale recovery.

## 3. Which results belong in the main paper?

| Placement/rank | Evidence | Why it earns space | Qualification |
|---|---|---|---|
| Main 1 | Atomicity/convergence statement plus shared-source oracle intervention panel | Directly illustrates the proposed theorem delta and distinguishes trajectory changes from support changes. | Not proof by simulation; finite w≥0 and specified coefficient/source assumptions. |
| Main 2 | Exact matched-teacher-loss fields and conditional risk-transfer statement | Shows a concrete limitation and a positive theorem in one coherent chain. | Different regularity across fields; no general neural-realizability claim. |
| Main 3 | Five new seed pairs, held-out full-law comparison, all means and medians | Tests the stronger bandwidth interpretation with a falsifier. | Separate training-label reference results from learned extrapolation. Retain failed row. |
| Main 4 | Paired CIFAR solver/calibration panel | Explains why variance increase, pixel coverage and posterior recovery differ. | Eight images is a pilot; joint uncertainty and convergence are unresolved. |
| Main limitation | Free-diagnostic baseline result | Prevents an unsupported claim of utility and answers an obvious reviewer question. | No reliable incremental prediction advantage demonstrated. |
| Appendix | Sharp Lipschitz floor, covariance asymptotics, older architecture/LR/N sweeps, all raw rows | Supports scope and reproducibility without fragmenting the main story. | No need to rerun already adequate checks merely to increase experiment count. |

## 4. Suggested text edits — drafts, not applied

### Title and contribution order

Suggested title: **Empirical Conditional Flows: Atomicity and the Limits of Loss
Certification**. This is a proposal, not a priority assertion. Order contributions
as (1) specified intervention/atomicity results, (2) failure and conditional repair
of loss certification, (3) empirical scope of moment-based diagnostics. Treat the
Bayes/NW reference as the common setup rather than the headline discovery.

### Abstract replacement draft

> We study endpoint behavior and loss certification for empirical conditional
> flow matching. For specified exact fields, label averaging and fixed
> nonnegative classifier-free guidance preserve atomic endpoints almost surely;
> convergence is proved without excluding tie trajectories in advance. An
> explicit affine-field family shows that vanishing teacher loss alone need not
> force endpoint collapse, while an additional risk-transfer assumption yields a
> finite-time Wasserstein certificate. Experiments separate these exact-field
> statements from trained-model behavior. Across five new problem instances,
> moment-fitted Gaussian references are closer to models trained with label noise
> than to hard-conditioned models, but do not establish equality of held-out
> laws. Paired image experiments reveal substantial differences between marginal
> calibration, joint calibration and numerical stability. Effective bandwidth is
> therefore used as a descriptive moment diagnostic, with its limits reported.

### Replace contribution 3’s heading and opening

Location: the introduction’s item beginning “Trained models sit at an effective
bandwidth, in low dimension” (around `paper/main.tex:171`). Suggested text:

> **Moment diagnostics and their distributional limits.** We fit a bandwidth
> from conditional variance and compare its mean predictions within the measured
> training-label regimes. A separate evaluation on five new problem instances
> fits bandwidth on 20 training conditions and tests 64 fresh conditions using
> 512 samples each. The fitted Gaussian reference is closer under positive label
> noise, but the held-out discrepancies and a numerically unresolved outlier
> preclude interpreting moment agreement as identification of the generated law.

Do not discard the old 48/48 result. State its selection rule, three underlying
problem seeds and moment-only target alongside the new generalization test.

### Add a label-domain paragraph to Methods

> Under hard conditioning, the empirical conditional law is specified at the
> observed training labels. Its extension to a new label is not identified by
> that empirical objective. Our new-label experiment evaluates the trained
> network’s extension and a moment-fitted reference, rather than testing the
> identifying-label collapse theorem. Positive Gaussian label noise supplies a
> particular full-support conditioning model.

### Add an empirical limitations paragraph

> We retain all five new problem instances, including one held-out condition
> outside its training-label range for which two source trajectories become
> extremely large and the practical solver screen fails. Image-level joint
> coverage also remains sensitive to Euler resolution. Consequently, neither
> finite-time off-atom distance nor improved marginal coverage is interpreted as
> an endpoint-law or posterior-recovery certificate. The null-envelope counts
> are descriptive, and conditions or pixels are not treated as independent
> problem replicates.

### Tighten the related-work comparison

Use columns for the exact setting, coefficient signs, assumptions on convergence,
tie treatment and conclusion. A generic collection of checkmarks is not sufficient
to establish novelty. State that empirical conditional collapse and spatial NW
representations are known. The strongest candidate difference is the specified
convergence/atomicity result, pending a direct priority check.

## 5. Work with the greatest expected review impact

1. **Before more broad experiments:** complete the theorem-level closest-work
   comparison and rewrite the main story around the surviving delta. This is
   required for the originality argument; another ten-run grid cannot replace it.
2. **Targeted numerical closure:** one problematic synthetic condition and the
   most sensitive image case(s), with paired source, fixed terminal time and a
   higher-accuracy reference. If unresolved, retain the limitation instead of
   promoting an unsupported attribution.
3. **Conditional expansion:** increase independent CIFAR test images only if
   joint-calibration/image-generalization claims remain a main contribution.
   Benchmark first; retain training/test separation and metric version.
4. **Use completed evidence:** integrate the new tables and failure case into the
   paper, then re-audit abstract, introduction and conclusion for consistency.

No new experiment, manuscript edit, deployment or external message was performed
in this reviewer-defense pass. A polished rebuttal cannot substitute for missing
priority evidence, an unresolved numerical comparison, or an unsupported claim.
