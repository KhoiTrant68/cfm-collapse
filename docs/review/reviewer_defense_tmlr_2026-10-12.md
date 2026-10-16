# Reviewer defense: TMLR submission (2026-10-12)

- **Manuscript**: `paper/main.tex` at `0fe1e9f`. Compiled: 84 pages; the main text ends on
  p. 9, references on pp. 9–11, appendix on pp. 12–84. Line numbers below refer to
  `main.tex` at this commit.
- **Venue**: TMLR. Reviewers are asked two questions: are the claims supported by
  accurate, convincing and clear evidence, and would some of TMLR's audience be
  interested? Novelty and significance are not acceptance criteria. So the weaknesses
  that matter most are mismatches between claim and evidence; "the theory is elementary"
  matters only if the paper claims more than it delivers.
- **Process**: authors answer reviews and upload revisions during a discussion period of
  about two weeks. A revised PDF with a diff convinces more than a promise, so text fixes
  should be made before submission, and only CPU-scale analyses promised during
  discussion.
- **Relation to round 6** (`simulated_review_round6_2026-10-11.md`): checked item by item
  below. Most required items are done; this document is about what remains and what round
  6 did not catch.

---

## 0. Round-6 items: status at `0fe1e9f`

| Round 6 | Item | Status |
|---|---|---|
| R1 | Report image-scale calibration | **Done** (L658–665, App. `app:calibdetails`) |
| R2 | Conclusion, contribution 2, title to the abstract's scope | **Partly**: conclusion and contribution 2 rewritten; title unchanged; "no coverage labels" survives in four places (see T1) |
| R3 | Seed table from the M=256 re-evaluation | **Done** (`3d4d6fd`) |
| R4 | Family control with a non-atomic, y-dependent competitor, split by h | **Done** (Table `tab:families`, both panels) |
| R5 | Qualify the floor argument | **Done** (L413–416: intrinsic d, the trained model leaves the atoms) |
| R6 | Audit box: h_eff step, M and C | **Done** (L3537–3543) |
| S1 | Run-level error and noise ceiling for R² | **Done** (L622–623) |
| S3 | Which results cover σ=0 | **Done** (L714–717) |
| S4 | Notation | **Partly**: ζ for the spectral exponent, h⋆ per condition in Fig. 1; κ still overloaded (P7) |
| S5 | h_true ∈ 𝓗 in Prop. `heffid` | **Done** |
| S6 | CIFAR h=0 and h=6 | **Done** (App. `app:heffends`) |
| S7 | Deduplicate the appendix | **Open** (P4) |
| S2 | Swap contributions 1 and 2 | Open; optional |

---

## 1. Weakness table

Severity is for TMLR: **High** = a reviewer can say a headline claim is not supported;
**Medium** = a reviewer will ask for a change; **Low** = polish.

### Technical

| # | Weakness | Where | Severity | Fix |
|---|---|---|---|---|
| T1 | **The label-free coverage prediction needs the analytic posterior.** The local model of Thm. `calib`(d) plugs in μ_h, Σ_h and V_h from part (c), i.e. the prior, A and σ (`scripts/theory_t3_coverage.py`: `V_of`, `coverage_local_model` read `p.Sigma_x`, `p.A`, `p.Sigma_post`). Anyone who knows these can simulate (x*, y*) and measure the model's coverage directly, so "needs no coverage labels" overstates what a practitioner gains. The "exact finite reference law" variant (R²=0.93) uses the held-out x* themselves. | abstract L70–72; contribution 2 L170–173; L619–631; conclusion L732–733; App. L3286–3289 | **High** | text (Edits A–E) |
| T2 | **"Agree within 95% intervals" is an overlap test**, and overlap is weak: kNN weights pass it at 48/48 and Laplace at 45/48 (Table `tab:families`). The paper says so (L544–546), but the abstract leads with 48/48. Existing data answer it (§6): the intervals are narrow relative to the range of h_eff. | abstract L62–64; L579–581 | Medium | text + numbers in §6 (Edit I) |
| T3 | **At image scale the reference uses Euclidean pixel distance between observed halves.** That metric is a choice the paper does not test. A mis-specified metric would explain the three image-scale shortfalls together: h_eff fits no better than a power law, 31/36 rather than 48/48, and h=0 not described by one bandwidth. | L646–657; App. `app:heffends` | Medium | new analysis (CPU for the variance fit on saved traces) |
| T4 | **h=4–6 on pixels in [−1, 1] looks as if it destroys the condition**: \|hε\| ≈ h√k ≈ 157 at h=4. The weights depend only on differences \|ỹ−yⁱ\|²−\|ỹ−yʲ\|², in which h²\|ε\|² cancels, and n_eff = 2.6/16.4/74.9 of 2000 shows the label still selects few atoms. The paper never says this. | L507–513; Table `tab:cifarddpm` | Medium | one sentence (Edit H) |
| T5 | **Contribution 4 lists consequences of known facts as a contribution.** Interpolant noise is inert because any valid interpolant has γ(1)=0 (the paper's own Remark `rem:notsampler`); endpoint noise turns the atoms into a Gaussian KDE. A memorisation theorist will say so. | L184–187; Sec. 3.3 | Low–Medium | text (Edit N) |
| T6 | **No mechanism for the gap above h or for off-atom samples**, and the spectral-bias model gets a main-text figure (Fig. `t2`) although App. `specbias` (L3484–3490) shows training is not lazy, so that model does not describe these networks. | L669–704 | Low–Medium | move Fig. `t2` to the appendix (§3) |

### Presentation

| # | Weakness | Where | Severity | Fix |
|---|---|---|---|---|
| P1 | **The title is broader than the evidence.** At CIFAR h=0, the way conditional models are usually trained, no single bandwidth fits; at h=6 the two estimates agree at 8/18. The abstract scopes it; the title does not. | L43–44 | **High** | Edit G |
| P2 | **An abstract number is not in the main text.** The abstract's "0.77–0.87 against 0.91" (rank test, 12 runs) appears only in App. L3342. Sec. 4.3 gives "0.72–0.81 … calibrated 0.87" (quantile-interval test, 6 runs). A reader checking the abstract against the body will find two protocols and two references. "Near nominal" for 0.77 against 0.91 will also be challenged. | abstract L73–74; L658–665; App. L3317–3349 | Medium | Edits B, F, J |
| P3 | **The core evidence figures are in the appendix.** Figs. `heffsyn` and `heffcifar` (L3133–3154) carry contribution 2; the main text has the figures for Thm. `calib` and for the spectral model instead. | — | Medium | §3 |
| P4 | **The 72-page appendix repeats material.** On-atom fractions 1.000/0.829/0.717/0.620 appear three times (L2558–2579, L2582–2591, L3640–3650). Adversarial pairing appears twice (App. `app:exp4` paragraph and App. `app:adv`, L4012–4038). The paragraph on why inpainting was chosen (L2548–2555) sits under the EXP-1 table in a subsection titled "Scope: what is and is not predicted" (L2522). | Apps. C–E | Medium | Edit K |
| P5 | **The abstract carries about fifteen numbers.** It reads as a results table. | L55–76 | Low–Medium | optional trim |
| P6 | **Dangling pointer.** The early-stopping numbers at h=6 (0.98 at 8k, 1.18 at 60k) cite App. `app:deferred`, which does not contain them; they appear nowhere else in the paper. | L2949–2951 | Low | Edit L |
| P7 | **Overloaded symbols.** κ is the identifiability constant (Prop. `heffid`), the regular conditional law in Thm. `labelmix` (L2103, L2134, L2139) and κ_j in the proof of Prop. `cfgatom` (L1730); η is the observation noise and the near-duplicate bound (L1655, L2471). | — | Low | Edit O |
| P8 | **Missing related work for an SBI/UQ reviewer**: simulation-based calibration, overconfidence of neural posterior estimators, TARP for joint coverage, and flow-matching posterior estimation. The marginal-versus-joint point of Sec. 4.3 is known there. | refs.bib; L83–125; L658–665 | Medium if such a reviewer is assigned | Edit M |

### Experimental

| # | Weakness | Where | Severity | Fix |
|---|---|---|---|---|
| E1 | One image dataset, one mask, N=2000, pixel space; no image-scale result in the regime where models generalise. E7 (MNIST DDPM h_eff, 9 runs) is pending. | L721–722 | Medium | add E7 when ready |
| E2 | At CIFAR h=0 the atomic family cannot describe "atom plus a small spread", and the endpoint-smoothed family (atoms + ρ), which can, is fitted only on the synthetic runs. | App. L3166–3178 | Medium | CPU fit on saved traces (planned E5) |
| E3 | CIFAR instance and optimisation randomness are confounded (3 instances per h). The architecture ablation has 2 seeds and measures tr Cov, not h_eff. | L520–521; Table `tab:ablation` | Low–Medium | text; answered in part by reruns (Q12) |
| E4 | No comparison with practitioner remedies at matched sample quality. | App. L2952–2953 | Low (claims are diagnostic) | text, already present |

---

## 2. Anticipated questions, most likely first

### Q1. "The coverage prediction 'needs no coverage labels', but it uses μ_h, Σ_h and V_h. What is its use?"
- **The question.** "Theorem 2(d) predicts held-out coverage from h_eff with R²=0.90 and 'no coverage labels'. The local model uses μ_h and Σ_h from part (c), which require the Gaussian prior, A and σ. Anyone who knows these can simulate pairs and measure coverage directly. In what setting is the prediction useful?"
- **Why they'd ask.** Abstract L70–72, contribution 2 L170–173, conclusion L733. Any statistician who reads `theory_t3_coverage.py`, or just Thm. `calib`(c), sees it.
- **Answerable.** Yes. It needs a concession and a rewording, not new data.
- **Draft response.** "Correct: the local model takes (μ_h, Σ_h) from Theorem 2(c), so it uses the known posterior family; it fits nothing to coverage and takes nothing from the trained model beyond h_eff. We present it as evidence that the bandwidth accounts for the coverage (Theorem 2(d) at h_eff explains 90% of its variance, against a binomial ceiling of 97%), not as a tool for unknown posteriors. Where pairs can be simulated, coverage should be measured directly, and as a predictor h_eff adds little to free quantities (ΔR² = +0.04, [−0.04, 0.22]). We have reworded the abstract, contribution 2, Sec. 4.3 and the conclusion accordingly."

### Q2. "The abstract's per-pixel coverage is 0.77–0.87 against 0.91; Sec. 4.3 says 0.72–0.81 against 0.87. Which is it?"
- **Why they'd ask.** Abstract L73–74 against L658–661. The abstract's numbers appear only in App. L3342.
- **Answerable.** Yes: two protocols, both in the appendix.
- **Draft response.** "Both. Sec. 4.3 reports the 5–95% quantile interval of M=64 draws on six runs, whose calibrated reference at M=64 is 0.873. The abstract reports the rank of the true image among the draws on all twelve runs, whose reference is exactly 0.908. The revision puts the rank-based numbers in Sec. 4.3, beside the abstract's, and moves the quantile-interval trajectory to Appendix E.1."

### Q3. "The title says trained conditional flows memorise at an effective bandwidth. At CIFAR h=0 no bandwidth fits, and at h=6 the estimates agree at 8/18."
- **Why they'd ask.** Title L43–44 against L650–655 and App. L3166–3178. Round 6 raised it too (EIC W1, DA-7).
- **Answerable.** Yes, as a text change.
- **Draft response.** "We agree the title should name the scope. The law holds at all 48 identified synthetic checkpoints, including h=0, and at 31/36 CIFAR checkpoints at h ∈ {4,5}. It fails where Proposition 6 predicts no identification (h=6, κ=0.13) and under hard conditioning at image scale, where the model is the atom plus a small spread (Q10). The new title is '…' [see Edit G]."

### Q4. "Interval overlap is a weak test, and kNN passes it at 48/48. How wide are the intervals?"
- **Why they'd ask.** L544–546 concedes overlap does not single out the kernel; the abstract still leads with 48/48.
- **Answerable.** Yes, from `results/exp1/_heff/heff_synthetic.json` (computed for this document, §6).
- **Draft response.** "The intervals are narrow relative to what they distinguish. Across the 48 checkpoints, the 95% interval of h_eff spans a median factor of 1.47 (upper/lower; IQR 1.32–1.75) and that of h_mean 1.67, while h_eff itself ranges over a factor of about 66. Under the stricter test that each point estimate lies inside the other's interval, the counts are 38/48 and 36/48, and the median ratio is 0.97 (5–95%: 0.74–1.59). Overlap shows that one scale explains both statistics at each checkpoint. What selects the Gaussian kernel is fit quality: it fits the variances best at 36/48, and its variance-fitted scale predicts the means best at 41/48 (Table 4)."

### Q5. "What is technically new in Section 3?"
- **The question.** "Proposition 1 is the standard L² projection. Collapse follows because the label determines the index. Theorem 1 is the conditional analogue of known closed forms for the empirical flow (Gao et al., Bertrand et al., Scarvelis et al.). Interpolant noise is inert because γ(1)=0. Endpoint noise gives a KDE."
- **Why they'd ask.** Contributions 1 and 4 (L151–160, L184–187) list these results; round 6 R2 called them elementary.
- **Answerable.** Yes.
- **Draft response.** "We claim no new kernel identity (Sec. 1). What the paper supplies is the label factor's endpoint law at h>0, a mixture over atoms where the separable analysis of Dasgupta et al. gives a single point; the h-independent floor, a statement about the whole family; when the bandwidth is identified (Prop. 6); what a bandwidth implies for calibration under any prior (Thm. 2(b), (d)) and at finite N (Thm. 3); and that label resolution alone cannot move the atoms (Prop. 7). The interpolant and endpoint results are stated so that the interventions can be compared on one footing; we now say in contribution 4 that they follow from γ(1)=0 and from Gaussian smoothing of the atoms. The empirical law and the audit are the main contribution."

### Q6. "On CIFAR, label noise of standard deviation 4–6 per pixel, on images in [−1, 1], should destroy the condition."
- **Why they'd ask.** L508–513; the pixel scale is not stated.
- **Answerable.** Yes.
- **Draft response.** "h is per coordinate, so \|hε\| ≈ h√k is large, but the index posterior depends only on \|ỹ−yⁱ\|² − \|ỹ−yʲ\|² = \|yᵏ−yⁱ\|² − \|yᵏ−yʲ\|² + 2hε·(yʲ−yⁱ), in which the common h²\|ε\|² cancels. What matters is the separation of the observed halves relative to h. At the 48 evaluation conditions the reference keeps n_eff = 2.6, 16.4 and 74.9 of 2000 atoms at h = 4, 5, 6 (Table 5). We added this sentence to Sec. 4.2." (Add the reason these three values were chosen, if there was one beyond spanning n_eff.)

### Q7. "At image scale the sample spread ranks coverage at 0.98 against 0.63 for h_eff, and in low dimension h_eff adds ΔR²=+0.04. Why compute h_eff?"
- **Why they'd ask.** L629–631, L656–662. Practitioners want a coverage predictor.
- **Answerable.** Yes; the paper already concedes it.
- **Draft response.** "To predict coverage, use the spread, and the paper says so (Sec. 4.3; App. E.1). h_eff answers a different question: where a checkpoint sits relative to its training set. It is one number that explains the generated means and variances across conditions together, which the spread cannot, and it is what makes the level and slope of the audit interpretable: a partial slope β is agreement with the reference at a larger bandwidth (β rises to 0.66 as h_eff/h falls to 1.13). We present it as a descriptor, not a calibration predictor, at image scale."

### Q8. "That marginal calibration hides joint under-coverage is known in simulation-based inference. Why not use TARP or SBC, and why is flow-matching posterior estimation not discussed?"
- **Why they'd ask.** L662–665 and App. L3335–3363 present the joint-versus-marginal gap as a finding. An SBI reviewer knows Talts et al. 2018, Hermans et al. (overconfident NPE), Lemos et al. 2023 (TARP) and FMPE.
- **Answerable.** Partly: citations and positioning yes; TARP numbers would need regenerated samples (GPU).
- **Draft response.** "We agree, and now cite this literature. Our joint test is an SBC-style rank statistic on a Mahalanobis depth in the top principal components, with an exact finite-M reference (0.908). Our addition is not that marginal coverage can mislead, but how the gap arises here: a per-direction shortfall in spread of s ≈ 0.7–0.9 that compounds over directions and predicts the 8-component joint coverage with R² = 0.81 (App. E.1). [If GPU time allows: TARP on the same checkpoints gives …]"

### Q9. "One dataset, one mask, N=2000, pixel space. Does the law hold elsewhere, and in the regime where models generalise?"
- **Why they'd ask.** Always asked; Limitations L721–722 concedes it.
- **Answerable.** Partly now; fully once E7 (MNIST DDPM h_eff, launched 2026-10-12) is in.
- **Draft response.** "The synthetic evidence spans three posterior families (linear-Gaussian, a bimodal mixture, an eight-mode mixture in d=8). At image scale we have the 12 CIFAR runs, an N-sweep on MNIST inpainting (App. E.14), and class-conditional CIFAR, where collapse is onto the class (Fig. 45). [E7: on MNIST the two bandwidths agree at …/…]. The regime where models generalise is outside the paper: there the reference law is still defined, and the on-atom fraction measures how far a model has left it."

### Q10. "At CIFAR h=0 the means sit on the atom but the variance needs h≈3.6. Isn't the trained model 'atom plus spread', and why isn't the endpoint-smoothed family fitted at image scale?"
- **Why they'd ask.** App. L3166–3178 reports exactly this, and Table 6 fits the endpoint-smoothed family only on synthetic runs.
- **Answerable.** Partly now; fully after a CPU fit on the saved traces.
- **Draft response.** "Yes. The residual trace at h=0 is 0.41–0.50, summed over the 3072 coordinates of the generated image on the [−1, 1] scale. Spread evenly, that is about 0.012 per coordinate, roughly 1.5 grey levels of 255, while the generated mean identifies the training image at 48/48. An atomic family can reach that trace only by mixing neighbouring atoms, hence h_eff ≈ 3.6 with h_mean at the grid floor. The endpoint-smoothed family fits it with s ≈ 0 and dρ² ≈ tr Cov. [Fit on the saved traces: ρ̂ = …, leave-one-condition-out error against the Gaussian …]."
- **Note.** The arithmetic assumes the variance is spread evenly over coordinates; check `scripts/heff_cifar_checkpoints.py` L123 before quoting it.

### Q11. "Why a Gaussian kernel in pixel space? Networks smooth in a learned metric."
- **Why they'd ask.** T3.
- **Answerable.** No; it needs a new analysis.
- **What to run.** Recompute the reference with distances in a fixed feature space of the observed halves (PCA-whitened pixels, or a pretrained encoder) and refit h_eff on the saved per-condition traces (CPU). h_mean needs regenerated means from the archived checkpoints (GPU).
- **Draft response.** "The Gaussian pixel-space kernel is the one the training noise induces, so it is the reference at the optimum. Whether the network's own smoothing is better described in another metric is a fair question: with [metric] the variance fit at image scale [improves / does not improve] (App. …)."

### Q12. "Instance and optimisation randomness are confounded, with three instances per bandwidth. Is 31/36 robust?"
- **Why they'd ask.** L520–521, L721–722.
- **Answerable.** Yes.
- **Draft response.** "Two independent retrainings of all six h ∈ {4,5} runs, on different GPUs, give the same 31/36 agreement and the same endpoints, 1.13–1.34h, and reproduce h_eff to a few percent (4.79, 4.80, 4.93 at h=4, seed 0; App. E.1). On the synthetic problem the instance carries 78% of the variance (App. E.13)."

### Q13. "Theorem 2(b) is vacuous for noiseless inpainting and at k=1536."
- **Answerable.** Yes, already in Limitations (L714–717).
- **Draft response.** "Yes: (b) needs σ>0 and is informative only for h²√k ≪ σ². For noiseless inpainting the endpoint law, part (d) and the audit apply, and (b) does not; Sec. 5 says so."

### Q14. "No comparison with early stopping, EMA, condition dropout or CFG at matched sample quality."
- **Answerable.** Partly (App. `app:remedies`).
- **Draft response.** "The paper's claims are diagnostic. Four of the five remedies are settled analytically (App. D.4), early stopping is measured, and EMA is not analysed. We do not claim a comparison at matched sample quality."

---

## 3. Evidence to show where: main text versus appendix

Ranked by how directly each item supports a claim the abstract makes.

| Evidence | Supports | Impact | Unique | Now | Recommend |
|---|---|---|---|---|---|
| h_eff vs h_mean and the fall to h, synthetic (Fig. `heffsyn`, 48 checkpoints) | contribution 2, the claim itself | highest | yes | appendix figure | **move to the main text** |
| CIFAR h_eff with its two ends (Fig. `heffcifar`; h=0, h=6) | contribution 2 at scale, and where it stops | high | yes | appendix figure | **move to the main text**, merged with the above as one two-panel figure |
| Reference-family control (Table `tab:families`) | the "Nadaraya–Watson" wording; atoms versus ρ | high (answers the alternative-smoother objection) | yes | appendix; main-text sentences L543–551 | keep as is |
| Identifiability, κ by bandwidth | explains the failures at h=0.5 and h=6 before a reviewer finds them | medium–high | yes | main | keep |
| Image-scale calibration: rank test, joint regions, spread vs h_eff | contribution 3's limit | high | yes | main paragraph | keep; one protocol in the main text (Edit J) |
| Thm. `calib` with Fig. `t3` | calibration | medium after rewording | yes | main | keep, reworded (T1) |
| ΔR² of h_eff over free quantities | candour about predictive value | medium | yes | main sentence | keep |
| Floor tests: AdamW, learning rate, cosine (App. L3491–3496) | the gap above h is not a regularisation artefact | medium | yes | appendix | add one main-text sentence |
| Kernel-gradient-flow model and Fig. `t2` | where the bandwidth comes from | low (training is not lazy) | partly | main figure | **move the figure to the appendix**; keep Prop. `filtered` in the main text |
| Collapse checks (memorisation ratio, held-out labels, permutation; Table `exp1`) | Prop. `collapse` | low (expected) | no | main paragraph | keep the paragraph short |
| Architecture and optimiser ablation (tr Cov only) | collapse speed | low | no | appendix | appendix; say h_eff was not measured there |
| Atomicity floor and endpoint smoothing (Tables `floor`, `tgt`) | contributions 1 and 4 | low–medium | no | appendix | appendix |
| Seed split; GPU reproducibility | robustness (Q12) | medium in rebuttal | yes | appendix | appendix; cite in responses |

The two figure moves leave the main-text length roughly unchanged (one figure in, one out).
The main text ends on p. 9, well under TMLR's 12-page threshold for the standard review
timeline.

**Cheap analyses that answer open questions**

| Analysis | Answers | Cost |
|---|---|---|
| Interval widths and point-in-interval counts | Q4 | done here (§6); add a script line |
| Endpoint-smoothed and kNN/Laplace families on the saved CIFAR traces | Q10, E2 | CPU, under an hour (planned E5) |
| Feature-space metric for the CIFAR reference, variance fit | Q11 | CPU for the fit; minutes of GPU for the features |
| E7 MNIST h_eff | Q9 | running |
| TARP on regenerated CIFAR samples | Q8 | GPU; optional |

---

## 4. Negative results, and how they are framed

The paper already reports its negatives well: atomicity not inherited at image scale; no
fit advantage over a power law there; h_eff does not predict image-scale coverage; ΔR² ≈ 0
over free quantities; endpoint smoothing defeated by dimension; Thm. `labelmix` vacuous at
N ≤ 10⁴; training not lazy; no density-adaptive bandwidth. Under TMLR's criteria this
candour is an asset. Two framing suggestions:

- **State each as a finding with a reason**, as Prop. `filtered` already does for off-atom
  samples ("needs an error in the spatial dependence of the field"). The image-scale
  coverage result reads best as: "h_eff tracks training progress, which falls
  monotonically; coverage recovers after 20k, which a monotone quantity cannot follow."
  That is in App. L3327–3330 but not in the main text.
- **Keep T1 from turning a negative into an apparent positive.** "No coverage labels" is
  where the paper currently undersells a negative (ΔR² ≈ 0) by presenting the
  analytic-posterior prediction as a label-free tool. Fixing T1 is the single most
  important edit.

---

## 5. Suggested text edits

Each edit gives the current text and a replacement in the paper's style. All are text
only, except Edit I, which uses the numbers in §6.

**Edit A: abstract, L70–72 (T1).**
- Now: "In low dimension this turns $h_{\mathrm{eff}}$ into a prediction of held-out coverage that needs no coverage labels ($R^2=0.90$ at $d{=}2$); given such labels, it adds little to free quantities."
- Replace: "In low dimension, where the posterior is known, this turns $h_{\mathrm{eff}}$ into a prediction of held-out coverage with nothing fitted to coverage ($R^2=0.90$ at $d{=}2$); as a predictor it adds little to free quantities."

**Edit B: abstract, L73–74 (P2).**
- Now: "per-pixel coverage near nominal ($0.77$--$0.87$ against $0.91$) hides joint regions that cover $0.47$--$0.78$."
- Replace: "per-pixel coverage of $0.77$--$0.87$ (calibrated: $0.91$) hides joint regions that cover $0.47$--$0.78$."

**Edit C: contribution 2, L170–173 (T1).**
- Now: "with the kernel weights at $h_{\mathrm{eff}}$ the theorem predicts the held-out coverage of 75 trained $d{=}2$ checkpoints with $R^2=0.90$ and no coverage labels, though a regression on free quantities fitted to such labels does as well."
- Replace: "with the kernel weights at $h_{\mathrm{eff}}$ and the known posterior, the theorem predicts the held-out coverage of 75 trained $d{=}2$ checkpoints with $R^2=0.90$, fitting nothing to coverage, though a regression on free quantities fitted to coverage does as well."

**Edit D: Sec. 4.3, L619–621 and L629–631 (T1).**
- L619: after "as draws of $\N(\mu_h,\Sigma_h)$ with the actual weights," insert "with $(\mu_h,\Sigma_h)$ from (c), that is, from the known prior and forward model,".
- L629–631, now: "Given the free quantities it adds no reliable information ($\Delta R^2=+0.04$, $[-0.04,0.22]$); its use is a prediction that needs no coverage labels (Appendix~\ref{app:calibdetails})."
- Replace: "Given the free quantities it adds no reliable information ($\Delta R^2=+0.04$, $[-0.04,0.22]$): through (d) it accounts for coverage, and where pairs can be simulated, coverage is better measured directly (Appendix~\ref{app:calibdetails})."
- Make the matching change in App. L3286–3289 ("What it adds is that …").

**Edit E: conclusion, L732–735 (T1, P2).**
- Now: "That bandwidth places a checkpoint relative to its training set, and in low dimension it predicts calibration without coverage labels. … per-pixel coverage near nominal can hide joint regions that cover far less."
- Replace: "That bandwidth places a checkpoint relative to its training set, and in low dimension, where the posterior is known, it accounts for calibration through Theorem~\ref{thm:calib}. … per-pixel coverage can hide joint regions that cover far less."

**Edit F: contribution 3, L182–183 (P2).**
- Drop "near nominal": "…where the sample spread ranks coverage better and per-pixel coverage hides joint regions that cover far less".

**Edit G: title, L43–44 (P1).** Two options:
1. `Trained Conditional Flows Memorise at an Effective Bandwidth:\\ Exact in Low Dimension, in Moments at Image Scale` (round 6's suggestion; long, but keeps the current title as its head).
2. `An Effective Bandwidth for Memorising Conditional Flows` (names the measurement rather than asserting a universal law).

Recommendation: option 2. It is short, true at every scale the paper measures, and leaves the abstract to give the scope.

**Edit H: Sec. 4.2, after L513 (T4).** Insert:
> Pixels lie in $[-1,1]$ and $h$ is the per-coordinate standard deviation of the label
> noise, so $|h\varepsilon|\approx h\sqrt k$ is large. The index posterior, however,
> depends on $|\widetilde Y-y^i|^2-|\widetilde Y-y^j|^2$, in which the common
> $h^2|\varepsilon|^2$ cancels, and at $h=4,5,6$ the reference keeps
> $n_{\mathrm{eff}}=2.6$, $16.4$ and $74.9$ of the $2000$ atoms (Table~\ref{tab:cifarddpm}).

**Edit I: Sec. 4.3, L579–581 (T2).** After "(log correlation $0.97$, median ratio $1.03$)" insert:
> ; the intervals span a median factor of $1.47$ and $1.67$, against a factor of about
> $66$ over which $h_{\mathrm{eff}}$ ranges, and each point estimate lies inside the
> other's interval at 38/48 and 36/48

Add the computation to `scripts/test_heff_synthetic.py` (or a small script) so the numbers are reproducible.

**Edit J: Sec. 4.3, L658–665 (P2).** Use one protocol in the main text, the rank test, which matches the abstract:
> On a second training of the same runs, we rank the true bottom half among $M{=}64$ draws
> (exact reference $0.908$ at the 90\% level). At 60k, per-pixel coverage is
> $0.77$--$0.87$ for $h>0$ and $0.06$--$0.08$ at $h{=}0$, while a joint region in the top 8
> or 32 principal components covers $0.59$--$0.78$ and $0.47$--$0.77$. A larger per-pixel
> spread goes with a smaller gap (Spearman $|\rho|=0.85$--$0.93$, against $0.49$--$0.65$
> for $h_{\mathrm{eff}}$); in the top 8 components the joint gap is a per-direction
> shortfall in spread compounding over the directions ($R^2=0.81$,
> Appendix~\ref{app:calibdetails}).

The quantile-interval trajectory (0.91–0.95 → 0.67–0.78 → 0.72–0.81; Spearman 0.98 against 0.63) moves to App. E.1, where it already is. The h=0 value of 0.06–0.08 is a strong result that is not in the main text now.

**Edit K: appendix cleanup (P4).**
- Delete the two on-atom paragraphs at L2558–2591; L3640–3650 and Sec. 4.2 carry the numbers.
- Move the inpainting-design paragraph (L2548–2555) into App. `app:exp4`, next to the CIFAR setup.
- Retitle the subsection holding Table `tab:exp1` (L2522), or move the table to App. `app:exp4`.
- Keep adversarial pairing in App. `app:adv` only; cut the duplicate paragraph in App. `app:exp4`.
- If the LaTeX source goes into the supplementary, also strip the internal comments (`% ---- 5.4 problem-specification justification (C8) ----` and similar).

**Edit L: L2951 (P6).** Point "(Appendix~\ref{app:deferred})" at the table or figure that holds the h=6 early-stopping trajectory, or add that trajectory to Table `tab:seed3` / Fig. `betatraj` and cite it there.

**Edit M: related work (P8).** All four confirmed on arXiv for this document. Check the venues with `/phd-skills:factcheck` before adding them to `refs.bib`.
- Talts, Betancourt, Simpson, Vehtari, Gelman, "Validating Bayesian Inference Algorithms with Simulation-Based Calibration", arXiv:1804.06788.
- Hermans, Delaunoy, Rozet, Wehenkel, Begy, Louppe, "A Trust Crisis in Simulation-Based Inference? Your Posterior Approximations Can Be Unfaithful", arXiv:2110.06581 (TMLR 2022: verify).
- Lemos, Coogan, Hezaveh, Perreault-Levasseur, "Sampling-Based Accuracy Testing of Posterior Estimators for General Inference" (TARP), arXiv:2302.03026 (ICML 2023: verify).
- Dax, Wildberger, Buchholz, Green, Macke, Schölkopf, "Flow Matching for Scalable Simulation-Based Inference", arXiv:2305.17161 (NeurIPS 2023; verify the author order in the proceedings).

A sentence for Sec. 4.3, before the joint-region result:
> Overconfident posterior samplers are documented in simulation-based inference
> \citep{hermans2022trust}, where calibration is tested by ranks \citep{talts2018sbc} and,
> for joint regions, by TARP \citep{lemos2023tarp}; conditional flow matching is used
> there as a posterior estimator \citep{dax2023fmpe}.

**Edit N: contribution 4, L184–187 (T5).**
- Now: "Interpolant noise leaves the population endpoint unchanged at any noise level (Propositions~\ref{prop:prop17} and~\ref{prop:factors}),"
- Replace: "Interpolant noise leaves the population endpoint unchanged at any noise level, as it must for any interpolant with $\gamma(1)=0$ (Propositions~\ref{prop:prop17} and~\ref{prop:factors}),"

**Edit O: notation (P7).** Rename the regular conditional law of Thm. `labelmix` (L2103–2139) to $Q(y,\cdot)$, and the near-duplicate bound $\eta$ (L1655, L2471) to $\epsilon_C$ or similar.

**Edit P: one main-text sentence on the floor tests (§3).** At the end of the "Synthetic" paragraph of Sec. 4.3 (after L587):
> Neither weight decay ($10^{-4}$--$10^{-2}$), a smaller learning rate nor a cosine schedule
> moves the final $h_{\mathrm{eff}}$ outside $0.86$--$1.22$ times its baseline
> (Appendix~\ref{app:specbias}), so the gap above $h$ is not set by explicit
> regularisation or the step size.

---

## 6. Numbers computed for this document

From `results/exp1/_heff/heff_synthetic.json`, restricted to the 48 checkpoints of
Sec. 4.3 (h ≤ 0.1, iteration ≥ 10⁴):

| Quantity | Value |
|---|---|
| intervals overlapping | 48/48 (matches the paper) |
| h_eff 95% interval, upper/lower | median 1.47, IQR 1.32–1.75, max 2.79 |
| h_mean 95% interval, upper/lower | median 1.67, IQR 1.41–2.00, max 3.86 |
| median interval ratio by h (h_eff / h_mean) | h=0: 1.67/1.81; 0.01: 1.61/1.78; 0.05: 1.40/1.74; 0.1: 1.32/1.39 |
| h_mean point estimate inside the h_eff interval | 38/48 |
| h_eff point estimate inside the h_mean interval | 36/48 |
| h_eff / h_mean | median 0.969 (paper: h_mean/h_eff = 1.03), 5–95% range 0.74–1.59 |
| range of h_eff over the 48 checkpoints | 0.0037–0.246, a factor of about 66 |

From the code: the CIFAR trace is `sf.var(dim=0, unbiased=True).sum()`
(`scripts/heff_cifar_checkpoints.py` L123), summed over the generated image. At h=0,
0.41–0.50 over 3072 coordinates is about 0.012 per coordinate if spread evenly
(1.5 grey levels of 255 on the [−1, 1] scale); over the 1536 hidden coordinates it would be
about 0.017 (2.2 levels).

From `scripts/theory_t3_coverage.py`: `coverage_local_model` uses `V_of(p, h)`, built from
`p.Sigma_post`, `p.A`, `p.Sigma_x` and `p.sigma_obs`; the reference-law prediction
(`ref_cov_*`) uses the held-out `Xt[j]`.
