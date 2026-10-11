# Simulated Peer Review — "Conditional Flow Matching: Kernel Smoothing over Atoms Does Not Restore the Posterior"

- **Manuscript**: `paper/main.tex` (commit `5e5db1a`), 9 main pages + appendix, 70 PDF pages in total, 29 formal results (proposition/theorem/corollary/lemma), 33 references.
- **Review date**: 2026-09-27, Round 1
- **Mode**: `academic-paper-reviewer` / `full` (5 reviewers + editorial synthesis)
- **Target venue**: ICLR 2027 Workshop (e.g. DeLTa, Deep Generative Models: Theory, Principles and Efficacy); with a calibration for the ICLR 2027 main track.

> **Limits of this review.** The five reports below were written by *one* model in one session, each report taking a different role and focus; they are not independent in the sense that five humans would be. The scores are meaningful as an **ordering** (paper A > paper B), not as acceptance probabilities. `calibration` mode was not run. The reviewers only read the manuscript; they did not edit it.

---

## Phase 0 — Field analysis & reviewer configuration

| Item | Assessment |
|---|---|
| Primary field | Machine learning: theory of generative models (flow matching / stochastic interpolants) |
| Secondary fields | Nonparametric statistics (Nadaraya–Watson, KDE), optimal transport, Bayesian inverse problems |
| Paradigm | Theory (population minimiser, closed form) + experimental verification |
| Paper type | Theory-with-validation / "understanding" paper |
| Maturity | Technically high (an audit script for the proofs), but the text still shows traces of many revision rounds |

| Role | Configured identity | Focus |
|---|---|---|
| **EIC** | ICLR Area Chair, generative models, has reviewed many memorisation-in-diffusion papers | Fit, novelty, significance for the ICLR community |
| **R1 — Methodology** | Empirical diffusion/FM researcher, used to evaluating sample diversity, bootstrap, seed control | Experimental design, statistics, reproducibility |
| **R2 — Domain** | Theorist of closed-form / empirical-optimal diffusion & FM (the Bertrand, Gao, Kamb, Buchanan line) | Mathematical novelty, positioning in the literature, rigour of the proofs |
| **R3 — Perspective** | Bayesian statistician / scientific-ML practitioner using CFM for physical inverse problems | Practical significance, uncertainty quantification, end users |
| **Devil's Advocate** | A sceptical reviewer who hunts "so what?" and overreaching claims | The strongest rebuttal of the central thesis |

---

## Report 1 — EIC (Area Chair)

**Recommendation**: Main track: *Major Revision → likely Reject*; Workshop: *Accept (poster)*
**Confidence**: 4/5

### Summary Assessment
The paper proves that, for a fixed training set, the population-optimal conditional FM with distinct labels collapses onto exactly one atom (Prop. 2), and that Gaussian label smoothing turns the endpoint law into a Nadaraya–Watson mixture over the atoms (Thm. 5), so the support stays on the training set for every h (Prop. 9). From this the paper ranks four interventions (interpolant noise, CFG, label smoothing, endpoint smoothing) and proposes an audit statistic (the slope β) in place of the variance ratio. The synthetic experiments confirm it very cleanly (ratio ≈ 1.00 ± 0.05); on CIFAR-10 with a 35.75M U-Net, the hard collapse is reproduced but the agreement at h > 0 is only partial (β = 0.481). The topic is squarely on target for ICLR and the writing is unusually honest, but the core mathematical contribution is short and close to known closed-form results, while the large-scale experiments show that the theory does *not* describe the real network. For the main track I expect a split committee leaning towards reject; for a workshop on the theory of generative models this is a good paper.

### Strengths
- **S1 — A clear and valuable audit message.** "Variance restored ≠ posterior restored" (§1 item 3, Prop. 9), together with the observation that the aggregate ratio is meaningless when the denominator barely varies (Fig. 2: 0.74 decades at h=6), is a methodological lesson the community can easily reuse.
- **S2 — A practical classification of interventions** (end of §3.5): inert → atom-preserving → reweighting → support-moving.
- **S3 — High academic honesty**: the Limitations state plainly that atomicity does not carry over to trained models (§5), and negative results are reported.

### Weaknesses
- **W1 — The core contribution is thin by main-track standards.** Thm. 5 is a few-line consequence of the mixture-coupling Lemma; Prop. 9 is a direct consequence of Thm. 5; the paper itself writes "We do not claim a new generic kernel identity" (line 103). *Severity: Major (main) / Minor (workshop).* *Suggestion*: reposition the contribution as an *audit tool* + an *intervention classification*, not as a theorem.
- **W2 — The theory-practice gap is acknowledged but not bridged.** On CIFAR, 38% of samples are off-atom at h=6, β=−0.156. *Severity: Major.* *Suggestion*: at least one quantitative result linking the population and the finite model is needed (e.g. a bound on β in terms of the unremoved part of the loss), or the claim in the abstract should be lowered.
- **W3 — Density and structure.** 29 formal results, the main text constantly refers to the appendix; the contribution list (§1) reads like a list of caveats. *Severity: Major for presentation.*

---

## Report 2 — R1 (Methodology)

**Recommendation**: Major Revision
**Confidence**: 4/5

### Summary Assessment
The synthetic experiments are carefully designed (a canonical sanity check at 1.8e-15, closed-form integration, 5 seeds, the instance/optimisation split in Appendix `sec:seedsplit`). The CIFAR part makes many good decisions (bootstrap CIs, re-measurement at M=256, three new instances), but I see a terminology conflict that directly affects the main claim, β is measured on only one instance, and the choice of bandwidths is not justified. The image scale (N=2000, one mask configuration) is still small.

### Strengths
- **S1** — Correctly separates the `Cov_h` reference from `Σ_post` in P7 and shows that "h≈0.1 restores perfectly" is a coincidence (lines 600–602). This is a correction of real value.
- **S2** — The reporting conventions (population SD, relative error √(2/(M−1)) = 8.9% at M=256) are transparent (lines 2776–2787).
- **S3** — Checks rival explanations for β (additive floor, hard floor, affine: R² 0.42/0.24/0.28 vs 0.78, lines 2993–2996).

### Weaknesses
- **W1 — "Aggregate" and "median" are used interchangeably for the same number.** §1 item 3 (line 163) says "aggregate agreement is 1.15"; line 651 says Table `tab:cifarddpm` reports "the aggregate ratio". But the column in the table (line 2793) is the **median** of the per-condition ratios, and the real aggregate ratio of seed 0 in Table `tab:seed3` is 1.181 (h=6) and 2.255 (h=4), far from the median 5.30. The appendix (line 3052) even states "We report the aggregate ratio throughout". *Why it matters*: this is the headline number of contribution 3; a reviewer who cross-checks will see it at once. *Suggestion*: settle on one definition, report both in Table 2 and fix the abstract/§1. **Severity: Major** (quick to fix but mandatory).
- **W2 — β comes from a single instance.** Table `tab:cifarddpm` and Fig. 2 are the "displayed instance"; Table `tab:seed3` reports trCov and the ratio for 3 seeds but **not** β. The claim "β = 0.481 ± 0.037" carries only the regression s.e. within one instance, not the between-instance variation. *Suggestion*: report β for all 3 seeds (the data exist). **Severity: Major.**
- **W3 — The choice h ∈ {4,5,6} with k=1536 is not justified.** It is unclear why these three values, and they correspond to n_eff 2.6 / 16.4 / 74.9, i.e. the whole useful range sits in a very narrow interval of h. *Suggestion*: parametrise by a target n_eff and explain the choice. **Severity: Minor.**
- **W4 — Image scale and diversity.** Only CIFAR bottom-half inpainting with N=2000 at 60k iterations; β is still rising when the budget runs out (Fig. `fig:betatraj`). The "partial" conclusion is therefore a conclusion about the budget. *Suggestion*: a longer run (e.g. 200k iterations) at h=4 is the most valuable experiment that could be added. **Severity: Major (main) / Minor (workshop).**
- **W5 — The main text reports P7 only at h = 0.05, 0.1, 0.5** (line 598), dropping h=0.01 where the ratio is 1.308 ± 0.376 (line 2895). The reason is explained in the appendix (n_eff ≈ 3.5), but the main text should say so in one sentence. **Severity: Minor.**

---

## Report 3 — R2 (Domain / Theory)

**Recommendation**: Major Revision (main) — Accept (workshop)
**Confidence**: 5/5

### Summary Assessment
The proofs I checked (the change-of-variables Lemma, well-posedness, mixture coupling, Props. 1–2, Thm. 5) are correct and carefully written, including details that are often skipped (the existence of the weak limit at t=1, the uniqueness of the continuity-equation solution). The problem is *depth*: most of the content is a direct consequence of the closed-form empirical velocity field already in the literature, applied to a conditioning variable. I also find the recent literature insufficiently covered.

### Strengths
- **S1 — Clean, self-contained proofs.** Lemma `lem:wellposed` removes the "flow is well defined" assumption many papers skip; the Grönwall bound `|x_t|+M ≤ (|x_0|+M)/(1−t)` is neat.
- **S2 — Separates the two factors of the index posterior** (spatial × label kernel, Prop. 4) and shows that only the label factor survives to t=1 (Prop. `prop:factors`), a useful angle clearly distinct from Smola (2026).
- **S3 — Prop. 11 (interpolant noise is inert)**, with the corrected path-derivative target (eq. `c2target`), is a correct technical point that many implementations get wrong.

### Weaknesses
- **W1 — Novelty of Thm. 5 / Prop. 9.** The mixture-over-atoms endpoint law is an immediate consequence once mixture coupling is available; atomicity is an immediate consequence of the endpoint law. A main-track theory reviewer will rate the contribution as a "straightforward extension of known closed-form results (Bertrand et al. 2025; Gao et al. 2024; Scarvelis et al. 2025) to the conditional case". *Suggestion*: lead with the *non*-obvious parts: Prop. `prop:survival` / Cor. `cor:lossform` (an error survives only if it accumulates at order (1−t)⁻¹, bounded by the remaining loss), Prop. `prop:expansion` (the h²JJᵀ expansion). **Severity: Major (main).**
- **W2 — Recent literature is missing.** Not found in `refs.bib`: *A Theoretical Analysis of Memory and Overfitting Phenomena in Stochastic Interpolation Models* (arXiv 2606.08554) and *Tracing Generated Samples to Training-Data Clusters in Flow-Matching Models* (arXiv 2608.30081). Both appear very close to Thm. 5 and the n_eff analysis. *Suggestion*: read them, compare, update Table 1. **Severity: Major** (could become Critical if there is substantial overlap).
- **W3 — Assumption (iii), distinct labels.** Natural for inverse problems with continuous noise, but it limits the value for class-conditional/text-conditional settings, which are the majority at ICLR. Cor. `cor:repeated` handles repeated labels but the main text mentions it in only one sentence. *Suggestion*: state clearly in §1 that the scope is "identifying conditions" (inverse problems, inpainting), not class labels. **Severity: Minor.**
- **W4 — The CFG result (§3.5) is weak for its position.** "The support lies in the affine hull" is vacuous when N > d (the paper says so itself), and N > d is the practical case in the synthetic experiments; on CIFAR, N=2000 < d=3072, so it has content. The paper should say which case applies in practice. **Severity: Minor.**

---

## Report 4 — R3 (Perspective: Bayesian inverse problems / scientific ML)

**Recommendation**: Minor Revision (workshop) / Major Revision (main)
**Confidence**: 3/5

### Summary Assessment
From the point of view of someone using CFM to sample posteriors in inverse problems, the practical questions are: *when to stop training, and how to tell whether the model is sampling the posterior or handing back the training data?* The paper answers the second clearly (the `Cov_h` reference, n_eff, the off-atom fraction, β) but admits it does not answer the first (§3.7: "predicts the destination, not the speed"). The largest practical contribution, the diagnostic toolkit, is scattered and not packaged as a procedure.

### Strengths
- **S1** — Shows that comparing with Σ_post is the wrong reference, and that the "early stopping works" experiment of physicscfm2026 has a clear mechanism (lines 579–580).
- **S2** — Adversarial pairing (permuting Y) is a highly convincing experiment for practitioners: collapse does not need a real statistical relation between x and y (lines 2877–2886).
- **S3** — The conclusion that endpoint smoothing is "defeated by dimension", like KDE (lines 2948–2952), is a useful practical warning.

### Weaknesses
- **W1 — No packaged diagnostic procedure.** *Suggestion*: an Algorithm box "Auditing a conditional flow for memorisation": compute p^(h), n_eff, `Cov_h`, β, the off-atom fraction; recommended thresholds; the O(N·M) computational cost. **Severity: Major**, as this is the cheapest way to increase impact.
- **W2 — No real inverse problem.** Linear-Gaussian, GMM and MNIST/CIFAR inpainting are all proxies. A PDE inverse problem (e.g. Darcy, the setting of physicscfm2026) would connect the paper with the community that motivated it. **Severity: Minor (workshop) / Major (main).**
- **W3 — No operational answer to "when to stop".** Appendix `app:remedies` measures early stopping (the ratio crosses 0.98 at h=6) but does not turn it into a recommendation. *Suggestion*: use n_eff or β on validation conditions as a stopping criterion and test it. **Severity: Minor.**

---

## Report 5 — Devil's Advocate

### Strongest Counter-Argument (≈250 words)
The central thesis is: *label smoothing does not restore the posterior because the endpoint law remains atomic.* But the paper itself shows that this is **not true of any model actually trained**: on CIFAR, the fraction of samples on an atom is 0.829 / 0.717 / 0.620 at h = 4 / 5 / 6 (line 2811), and in EXP-1 the variance stops at 0.40 instead of 0 after 2×10⁵ iterations. So "Kernel smoothing over atoms does not restore the posterior", the title, is a statement about an object (the population minimiser on a fixed set) that nobody deploys, while the object people do deploy *leaves* the atoms. Either that departure is useful generalisation (and then the theorem only says what would happen under perfect optimisation, a scenario the paper does not show to be reachable at real scale), or it is optimisation error (and then β and the ratio only measure "how far optimisation has got", as §3.6 says, so the paper is proposing a measure of optimisation progress, not a conclusion about the posterior). Both readings weaken the claim in the title. Moreover, the collapse mechanism at h=0 (the label identifies the sample ⇒ loss = 0 at δ) is obvious to anyone who writes down E[U | X_t, Y]; the new value must lie in the *speed* and the *finite model*, exactly the parts the paper admits are missing.

### Issue List
| # | Level | Dimension | Location | Problem |
|---|---|---|---|---|
| DA-1 | **MAJOR** | Argument | Title, abstract, §6 | The title makes a claim about "the posterior" while the result holds only for the population minimiser; the real network leaves the atoms (38% off-atom). Lower the claim or change the title. |
| DA-2 | **MAJOR** | Evidence | lines 163, 651 vs Table `tab:cifarddpm` | The headline number "aggregate 1.15" is in fact a median (see R1-W1). It risks being read as selective presentation. |
| DA-3 | **MAJOR** | Presentation / integrity | lines 2748, 2954, 3020, 3050, 3354, 3760 | The appendix contains a revision log ("An earlier version of this paper reported the opposite…", "reproduced verbatim from earlier versions of the main text"), including the corrected Sinkhorn error. In an anonymous submission this (a) adds noise, (b) suggests an earlier public version exists → a double-blind risk if there is an arXiv version, (c) makes reviewers doubt the other numbers. Turn the corrections into present-tense statements and drop the history. |
| DA-4 | MINOR | Overgeneralisation | §4.1 P7 | "Strongest empirical confirmation" rests on d=2, where the floor is only 3.5% of tr Σ_post, i.e. atomicity is almost unobservable exactly where the paper confirms the theory most strongly. |
| DA-5 | MINOR | Cherry-picking check | line 598 | h=0.01 is dropped from the main text (see R1-W5). There is a valid reason, but it must be stated. |
| DA-6 | MINOR | Logic | §3.6 | Cor. `cor:lossform` needs L_Δ ≥ δ⁻¹ − K, an assumption the paper itself calls "demanding"; the fitted prefactor e^{L_Δ} ≈ 25 is ignored. The result is therefore almost untestable. |

**No CRITICAL issue** → the decision is not blocked by Checkpoint Rule #4, but DA-1 to DA-3 must be addressed.

### Ignored Alternative Explanations / Paths
- The departure from the atoms on CIFAR may come from the *inductive bias of the U-Net* (smoothness in the conditioning variable, as Pfrommer et al. 2025 found), not only from unfinished optimisation. The paper has no experiment that separates the two explanations (e.g. comparing architectures at equal loss).
- Common regularisation (weight decay, EMA, dropout) is not considered among the "remedies" that real users actually turn on.

### Missing Stakeholder Perspectives
- Users of text-/class-conditional models (the majority of the ICLR community): the distinct-label assumption does not apply.
- Those concerned with privacy/copyright: the paper raises it in the Ethics section but does not measure data extraction.

### Observations (Non-Defects)
- The level of self-checking (an audit script for every proof, `docs/audit/`) exceeds the usual standard.
- Publicly correcting an error (Sinkhorn) is good scientific practice; the only issue is *where* it is placed.

---

## Phase 2 — Editorial Synthesis

### Consensus matrix
| Issue | EIC | R1 | R2 | R3 | DA | Consensus |
|---|---|---|---|---|---|---|
| Mathematical novelty thin for the main track | ✔ W1 | — | ✔ W1 | — | ✔ (main argument) | **High** |
| Theory ↔ finite model not connected | ✔ W2 | ✔ W4 | — | ✔ W3 | ✔ DA-1 | **High** |
| Median/aggregate conflict | — | ✔ W1 | — | — | ✔ DA-2 | Medium, but **verified in the text** |
| Presentation too dense / revision log | ✔ W3 | — | — | — | ✔ DA-3 | Medium |
| Missing 2026 literature | — | — | ✔ W2 | — | — | One reviewer, but high risk |
| Needs a packaged audit procedure | ✔ S1 | — | — | ✔ W1 | — | Medium |
| Strengths: honesty, clean proofs, audit message | ✔ | ✔ | ✔ | ✔ | ✔ (obs.) | **High** |

### Disagreements and arbitration
- **R3 (Minor) vs EIC/R2 (Major) for the workshop**: at a workshop, novelty is not a blocking criterion; arbitrated in favour of R3, *Minor Revision* is the appropriate level for the workshop.
- **The DA argues the title claim is wrong about real models** vs **the paper treats it as the "audit target"**: arbitration: the paper's argument is logically valid, but the title and abstract do not yet reflect its scope; a change of wording is required, not additional results.

### Rubric scores (0–100, skill weights)
| Dimension (weight) | Main track | Workshop |
|---|---|---|
| Originality (20%) | 58 | 70 |
| Methodological rigor (25%) | 74 | 78 |
| Evidence sufficiency (25%) | 66 | 75 |
| Argument coherence (15%) | 62 | 68 |
| Writing quality (15%) | 55 | 60 |
| **Weighted** | **64.2 → Major Revision** | **71.4 → Minor Revision** |

### Calibration to the ICLR scale
| | Soundness (1–4) | Presentation (1–4) | Contribution (1–4) | Rating (1/3/5/6/8/10) |
|---|---|---|---|---|
| EIC | 3 | 2 | 2 | 5 |
| R1 | 3 | 2 | 2 | 5 |
| R2 | 4 | 2 | 2 | 5 |
| R3 | 3 | 2 | 3 | 6 |
| DA | 3 | 2 | 2 | 3 |
| **Main-track mean** | 3.2 | 2.0 | 2.2 | **4.8 → borderline reject** |

For the workshop (usually a 1–5 or accept/reject scale): **Accept, likely**, if the P0 items below are fixed.

### Editorial Decision
- **ICLR 2027 main track**: *Reject in current form* (equivalent to Major Revision in a journal system).
- **ICLR 2027 Workshop (DeLTa or equivalent)**: **Minor Revision → Accept**.

---

## Revision Roadmap (prioritised)

### P0 — Mandatory before submission (little work, high risk)
1. **Fix median/aggregate** (R1-W1, DA-2): lines 163, 651, 684, 3052 and Table `tab:cifarddpm`. Report both numbers and name them correctly.
2. **Remove the revision log from the appendix** (DA-3): lines 2748, 2954–2965, 3020–3030, 3050–3052, 3354, 3760. Keep the corrected content, drop "an earlier version…". Check that no matching arXiv/public version reveals the authors.
3. **Read and position arXiv 2606.08554 and 2608.30081** (R2-W2); update Table 1 / `tab:related`.
4. **Report β for all 3 CIFAR seeds** (R1-W2); the data exist.

### P1 — Should do (clearly increases impact)
5. **An Algorithm box "Memorisation audit for conditional flows"** (R3-W1, EIC-S1).
6. **Lower the title/abstract claim** to the population minimiser (DA-1); e.g. a title that makes a claim about the audit.
7. **Cut down** to ~5 results in the main text (EIC-W3); state the scope "identifying conditions" clearly (R2-W3).
8. One sentence about h=0.01 in the main text (R1-W5, DA-5).

### P2 — For a later main-track version (ICML/NeurIPS 2027 or TMLR)
9. A longer CIFAR run at h=4 to see whether β approaches 1 (R1-W4).
10. A real PDE inverse problem (R3-W2).
11. An experiment separating architectural inductive bias from optimisation error (DA alternative explanation).
12. A theoretical result on the collapse time or a bound on β (EIC-W2, R2-W1).
