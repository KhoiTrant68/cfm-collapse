# Reviewer defense — 20 October 2026

Paper state: `main` at `9748b9c` (after PRs 27–29). The story is now "which interventions on
the exact empirical conditional field leave the training set". The previous defense
(`reviewer_defense_2026-10-16.md`) targeted the effective-bandwidth audit, which has since
been removed. This document starts again from the current text.

Target venue: the preamble is TMLR (`\usepackage{tmlr}`). TMLR reviews claims and evidence
rather than novelty or impact. The main risk is a claim the evidence does not support, not a
missing state-of-the-art comparison. The ICLR notes below apply only if the paper goes back to
a 9-page conference format. The main text currently ends on page 12.

Proofs: all proofs are the authors' and have been checked by independent verifier runs
(`length_cut_verification_2026-10-20.json`). This document does not question their correctness.
It questions scope, relevance and evidence.

## 1. Weakness table

| # | Category | Weakness | Where | Severity |
|---|---|---|---|---|
| W1 | Technical | All atomicity results concern **exact** fields. A trained network is linked to them only conditionally (Theorem 5.1, Proposition 5.2), and the scaled error $(1-t)\lvert\Delta\rvert$ along learned trajectories is never measured. | Sec. 5, Limitations | High |
| W2 | Experimental | The headline new result, Theorem 4.7, has **no trained-network test**. Guided label averaging is checked only on the exact field (Figure 6, Table 8). | Sec. 4.3, 6.2 | High |
| W3 | Technical | Theorem 4.7 covers $d=k=1$ and two atoms. The many-atom, high-dimensional case is listed as open, so a reviewer may call the composition result a toy. | Sec. 4.3, Limitations | Medium–high |
| W4 | Presentation | Significance: that the empirical minimiser memorises is well known (Related work cites ~10 papers). A reader may not see what a practitioner learns. | Intro, Related work | Medium–high |
| W5 | Experimental | Small scale. Synthetic $d\le10$; CIFAR-10 uses $N=2000$, one mask and 3 instances; instance and optimisation randomness are confounded. The abstract says "collapse at scale". | Abstract, Sec. 6, Limitations | Medium |
| W6 | Technical | Assumption (iii), identifying labels, makes $h=0$ collapse almost immediate. Real class labels are shared. | Assumption 2.1 | Medium |
| W7 | Technical | Only the linear interpolant with a Gaussian source. No statement for variance-preserving or score diffusion, where CFG is usually used. | Sec. 2 | Medium |
| W8 | Experimental | The CIFAR $h=6$ off-atom samples (38%) are left unexplained. The transfer theorem names the measurement that would explain them, but it was not done. | Sec. 6.1 | Medium |
| W9 | Experimental | Statistics: population standard deviations with $n=5$ (or 3), no intervals; the learned-averaging table is "descriptive, not hypothesis tests". | Sec. 6, Table 2 | Medium |
| W10 | Experimental | Exact-field checks are finite-time. Four of six adaptive near-tie integrations fail. | Sec. 6.2 | Low–medium |
| W11 | Presentation | Possible missing guidance-theory references (to verify before citing; see Q10). | Related work | Low–medium |
| W12 | Presentation | Figure 4(a) uses the training-time estimator (8 conditions, $M=16$), while the text elsewhere quotes re-measured values ($0.458$ at $M=256$). Both are stated, but a reader can mix them up. | Sec. 6.1, App. E.2 | Low |

## 2. Anticipated questions (most likely first)

### Q1. Do the exact-field results say anything about trained samplers? [Very high]
**Motivation.** W1 and W2. Every theorem in Section 4 is about $v^\star$, and the learned-averaging pilot (Table 2) itself shows that exact atomicity does not transfer automatically.
**Answerable.** Partly.
- Theorem 5.1 and Proposition 5.2 give the exact condition: a learned endpoint stays within $\limsup(1-t)\lvert\Delta\rvert$ of the atom.
- Figures 3–4 show trained networks reaching the hard-conditioning endpoint.
- Figure 5 shows trained networks tracking the kernel reference for $h\ge0.05$.
- Not answerable without new work: whether trained guided or averaged samplers stay atomic.

**Draft response.** "The exact field is the population minimiser that training targets, and it is the reference against which the learned field is measured. Theorem 5.1 states precisely what a trained network must do to inherit the exact behaviour: its implied endpoint prediction must converge. Figures 3–5 show trained MLPs and a 35.75M-parameter U-Net reaching the predicted hard-conditioning endpoint and the kernel reference. We do not claim that trained guided samplers are atomic. Table 2 shows that learned label averages can depart from the exact ones, and we state this as a limitation."

### Q2. Does guided label averaging leave the support in a trained model? [Very high]
**Motivation.** W2. It is the paper's most surprising claim, and it is checked only on the exact field.
**Answerable.** No; this needs a new experiment.
- The five $h=0.1$ EXP-1 networks used for Table 2 already provide learned label averages.
- Adding $-w\,v^{\mathrm{unc}}_\theta$ needs an unconditional network for each problem seed. The `exp1_uncond_seed*` runs exist for seeds 0–4. Whether unconditional runs exist for problem seeds 1001–1005 has not been checked.

**Proposed experiment (CPU, existing pipeline).**
- Two-atom and twelve-atom instances; learned $(1+w)\bar v_\theta-wv^{\mathrm{unc}}_\theta$ at $w/w_c\in\{0.5,2,10\}$.
- Report the fraction of 128 paired sources whose nearest-atom distance at $T=0.999$ exceeds $1\%$ of the atom separation, next to the exact field's.

**Draft response, if the result agrees.** "We added a trained-network test (Appendix E): the learned composite reproduces the threshold within …"

### Q3. What is new, given that empirical-minimiser memorisation is known? [Very high for ICLR, medium for TMLR]
**Motivation.** W4.
**Answerable.** Yes, from the text. Related work already says that the Nadaraya–Watson law is a reference, not a new identity.
**Draft response.** "The new content is not memorisation of the exact minimiser. It is the classification of interventions in Table 1. Positive prior mixtures and nonnegative guidance, including bounded schedules of bounded variation, provably keep every trajectory convergent with a null non-atom basin, with no assumption excluding non-minimising critical limits (cf. Liu & Zuazua 2026). Their composition provably does not, with an exact threshold (Theorem 4.7) that is stable under perturbation (Proposition 4.8). The common proof template (Figure 2) makes clear why the second step fails only for the composite."

### Q4. Is Theorem 4.7 a one-dimensional curiosity? [High]
**Motivation.** W3.
**Answerable.** Partly.
- Proposition 4.8 gives an open set of parameters.
- The mechanism does not depend on dimension: averaging subtracts $(1+w)$ times the variance of the component means from the covariance trace (Sec. 4.3).
- Not answerable: a theorem for $N>2$ or $d>1$.

**Cheap evidence.** Run `composition_counterexample.py` in $d=2,8$ with $N$ atoms on a regular simplex, using the same certified stopping rules for the radial coordinate when the configuration is symmetric. This is not done yet.

**Draft response.** "In general dimension the obstruction is the sign of the combined covariance trace $\Theta$ at a circumcentre (Figure 2, Step 2). The one-dimensional case is where the threshold is explicit. Proposition 4.8 shows that the effect is not tied to the symmetric configuration. We have added exact-field computations for … atoms in $d=…$ (Appendix E.3)." Only use this last sentence once the computation is run.

### Q5. Is $h=0$ collapse trivial under identifying labels, and what happens with class labels? [High]
**Motivation.** W6.
**Answerable.** Yes, with data that is cut from the current paper.
- `results/exp3/exp3_cifar_class_h0`, `..._h0p4` contain class-conditional CIFAR runs, about 200 images per class, with `fig_image_class.png` already drawn. Shared labels give $p^{(0)}$ uniform within a class, so the endpoint law is the within-class empirical law (Theorem 3.4 with $p$ uniform on the class).
- The identifying-label case matches captions and continuous measurements (inpainting).

**Draft response.** "Assumption (iii) models conditioning signals that are almost surely distinct, such as observations in inverse problems or near-unique captions. With shared labels the same analysis gives the empirical law of the label's class. Appendix E shows the class-conditional CIFAR-10 runs, whose generated variance matches the within-class scatter."

**Action.** Restore the class-conditional result (one paragraph and `fig_image_class.png`) to Appendix E.

### Q6. Are the conclusions sensitive to architecture, optimiser, $N$ or $\sigma_{\mathrm{obs}}$? [High]
**Motivation.** W5. A single architecture is used (MLP 128×4, Adam).
**Answerable.** Yes, with data that is cut from the current paper.
- Architecture/optimiser ablation, `results/exp1/ablation_*`, two seeds each. $\mathrm{tr}\,\mathrm{Cov}$ at $2\times10^5$: width 32: 0.657; width 64: 0.526; width 256: 0.403; depth 2: 0.860; depth 6: 0.407; SGD: 0.711. The baseline is 0.396.
- $N$ sweep (`p6_N*`, `p6exp_N*`), $\sigma_{\mathrm{obs}}$ sweep (`p5_sobs*`) and $d/k$ sweep (`dk_*`).

**Draft response.** "Collapse appears for every architecture and optimiser; capacity and optimiser change only its speed (Appendix E, Table …). This is consistent with Proposition 3.2, which constrains the minimiser, not the model."

**Action.** Restore the ablation table to Appendix E. Use the population SDs recorded in RESULTS.md: 0.041, 0.041, 0.056, 0.110, 0.090 and 0.136, in the order of the six configurations.

### Q7. Are instance and training randomness confounded? [Medium–high]
**Motivation.** The Limitations section says so explicitly.
**Answerable.** Yes. `results/exp1/seedsplit_inst_s0–9` and `seedsplit_train_s0–9` vary each source separately, and `scripts/analyze_exp1_seed_split.py` and `make_seed_split_figure.py` exist.
**Action.** Rerun the analysis, report both variance components in Appendix E, and remove "confounded" from Limitations for EXP-1. CIFAR stays confounded.

### Q8. Why are 38% of the CIFAR $h=6$ samples off-atom? Does this contradict Proposition 3.6? [Medium–high]
**Motivation.** W8.
**Answerable.** Partly.
- Proposition 3.6 concerns the exact limit.
- At a finite cutoff with a learned field, Theorem 5.1 bounds the distance by the scaled error.
- `results/intervention_cifar_pilot_20261016` has the solver pilot. The $h=0$ hidden-mean MSE is unchanged from 50 to 400 Euler steps, so the solver is not the cause at $h=0$.
- `scripts/verify_error_survival.py` checks when an error of order $(1-t)^{-a}$ survives.

**Missing.** $(1-t)\lvert\Delta\rvert$, or equivalently $\lvert\hat x_1-x^{i}\rvert$, along trained CIFAR trajectories at $h=6$. This is cheap if the checkpoints exist. The pilot reports "six exact DDPM checkpoints", so they did exist on 16 October; confirm they are still kept.

**Draft response.** "The exact endpoint law is atomic; the measured samples are at $t=1-10^{-3}$ from a learned field. Theorem 5.1 identifies the quantity that decides the limit, the endpoint prediction error. Measuring it along the $h=6$ trajectories shows …"

### Q9. Are the statistics adequate? [Medium]
**Motivation.** W9.
**Answerable.** Partly.
- Seeds are fixed in advance; population SDs are declared (App. E).
- Table 7 has bootstrap intervals for the CIFAR median ratios.

**Action.** Give 95% $t$-intervals (or seed ranges) for the EXP-1 headline numbers in Table 5. Say in Sec. 6 that 5 seeds gives an interval of about ±1.24 SD, so the quoted ± is not a confidence interval.

### Q10. How does this relate to the theory of guidance? [Medium]
**Motivation.** W11. The paper cites Chidambaram et al. 2024, Jain et al. 2025, Kynkäänniemi et al. 2024 and Liu 2026. A guidance-theory reviewer may expect more.
**Candidates to verify with `/phd-skills:factcheck` before citing.**
- Bradley & Nakkiran (2024), "Classifier-Free Guidance is a Predictor-Corrector".
- Wu et al. (2024), "Theoretical insights for diffusion guidance: a case study for Gaussian mixture models".

Both are recalled from memory and are not in `refs.bib`. Do not add them without checking.

**Draft response.** "These works study guidance on continuous targets (Gaussian mixtures, predictor-corrector views). Our setting is the finite-support target that training actually defines, where guidance cannot create mass off the atoms unless it is composed with averaging."

### Q11. Does the result extend beyond the linear interpolant? [Medium]
**Motivation.** W7.
**Answerable.** No; it is not proved.
- The Nadaraya–Watson structure uses only Bayes' rule over a finite atom set and a Gaussian path. A general $(\alpha_t,\sigma_t)$ path would change $\beta$ and the time change.
- This needs a check of Lemmas B.2 and B.3 under a general schedule. **Do not claim it in the rebuttal without the proof.**

**Draft response.** "We state the results for the linear interpolant. The posterior over atoms has the same form for any Gaussian path, and we expect the argument to carry over with $\beta=\alpha_t/\sigma_t^2$. We leave this to future work rather than claim it."

### Q12. Are the exact-field checks reliable given the solver failures? [Low–medium]
**Motivation.** W10.
**Answerable.** Yes.
- Atom assignments are unchanged when the resolution doubles.
- The composition computation uses certified, forward-invariant stopping rules (App. E.3), so its basin probabilities are not finite-time estimates.
- The reported failures are adaptive integrations at a tie, which the theory classifies as a null set.

**Draft response.** Point to App. E.3 and Figure 6.

## 3. Recommended ablation subset

| Priority | Experiment | Status | Placement | Why |
|---|---|---|---|---|
| 1 | Trained guided label averaging (Q2) | **new, CPU-cheap** | Main, Sec. 6.2 | Turns the paper's main new claim from exact-only into exact plus learned; answers W1/W2 at once. |
| 2 | Scaled endpoint error along CIFAR $h=6$ trajectories (Q8) | new, needs checkpoints | Main or App. E.2 | Applies Theorem 5.1 to the one result the paper cannot yet explain. |
| 3 | Architecture/optimiser ablation (Q6) | **exists** | App. E.1 | Shows collapse is not tied to one model. |
| 4 | Seed split, instance vs training (Q7) | **exists** | App. E.1 | Removes a limitation stated in the paper. |
| 5 | Class-conditional CIFAR (Q5) | **exists** | App. E.2 | Answers the identifying-label objection with data. |
| 6 | Composition in $d\ge2$, $N\ge3$ exact (Q4) | new, cheap | App. E.3 | Evidence beyond the 1-D theorem; label it numerical. |
| 7 | $N$ and $\sigma_{\mathrm{obs}}$ sweeps | exists | App. E.1, one table | Low priority; supports "the speed varies, the endpoint does not". |

Leave out: the effective-bandwidth audit, the coverage theorem and the spectral-bias model. They were removed for focus, and bringing them back reopens the 16 October questions (Q2, Q6 there).

**Negative results worth keeping, framed as analysis.**
- Table 2: learned label averages deviate from exact ones as $r$ grows. Frame it as "exact atomicity is a property of the target, not automatically of the learner".
- The four failed adaptive near-tie integrations: they show where finite-precision checks stop being informative.
- CIFAR $h=6$: the reference spans only 0.74 decades, so a slope of $-0.16$ is uninformative, not contradictory. The text already says this; keep it.

## 4. Suggested text edits (drafts; not applied)

**Abstract, last sentence.** "at scale" overstates $N=2000$ and one mask.
> Before: "Exact-field computations confirm the threshold, and experiments up to a 35.75M-parameter CIFAR-10 U-Net show hard-conditioning collapse at scale."
> After: "Exact-field computations confirm the threshold, and trained networks, from MLPs to a 35.75M-parameter CIFAR-10 U-Net, reach the hard-conditioning endpoint and track the label-smoothing reference."

**Introduction, after the contribution list.** Add one sentence on what a practitioner takes away (W4):
> "For a practitioner the classification says where novelty can come from. It cannot come from label noise, label averaging or guidance applied separately to the field training defines, and it can come from their composition, from endpoint noise, or from a learned field whose endpoint prediction does not converge."

**Limitations.** Replace "with instance and optimisation randomness confounded" by the seed-split result once restored. Add: "Theorem 4.7 has no trained-network counterpart yet" until Q2 is run. It is better that the paper says this than that a reviewer finds it.

**Section 6.1, CIFAR paragraph.** Make the estimator explicit in the text, not only in the caption: "(training-time estimator; $0.458$ when re-measured at $M=256$, Appendix E.2)".

**Section 4.3, after Proposition 4.8.** One sentence on why the 1-D theorem is the general mechanism, pointing to Figure 2: the sign of $\Theta$ at a circumcentre. This pre-empts Q4.

## 5. Order of work by expected review impact

1. Q2 trained composition pilot. This is the only item that changes what the paper can claim.
2. Restore three existing appendix results (Q5, Q6, Q7). These need no new compute.
3. Abstract, Introduction and Limitations edits above.
4. Q8 CIFAR error measurement, if the checkpoints are still available.
5. Verify the Q10 references, then add them.
