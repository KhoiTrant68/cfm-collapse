# Simulated review, round 3: ICLR 2027, NeurIPS, ICML

- **Submission**: *Trained Conditional Flows Memorise at an Effective Bandwidth*
- **Version reviewed**: `paper/main.tex` after PRs #18–#20 (Proposition `prop:heffid`, Theorem
  `thm:calib`, appendix `app:specbias`), main text 9 pages, 75+ pages in total.
- **Formats**: ICLR (rating in {1,3,5,6,8,10}); NeurIPS (overall 1–6: 6 strong accept, 5 accept,
  4 borderline accept, 3 borderline reject, 2 reject); ICML (overall 1–5: 5 strong accept,
  4 accept, 3 weak accept, 2 weak reject, 1 reject).

> All reviews are written by one model from assigned perspectives; they are not independent.
> Ratings are an ordinal judgement, not a prediction of the outcome.

---

## Reviewer A: theory of generative models (mathematical lens)

**Summary.** The empirical minimiser of conditional flow matching collapses onto the
identified training atom; Gaussian label noise turns its endpoint into a Nadaraya–Watson
(NW) mixture over atoms, atomic at every bandwidth. Trained networks are claimed to follow
this mixture at a fitted bandwidth $h_{\mathrm{eff}}$. New in this version: an
identifiability proposition for $h_{\mathrm{eff}}$, a calibration theorem in the
linear-Gaussian model, and a kernel-gradient-flow model of how $h_{\mathrm{eff}}$ shrinks.

**Strengths.**
1. The theorems are correct as far as I checked, and the proofs are complete and short.
   Theorem 2(b), $x^\star-\mu_h(y^\star)\sim\N(0,\Sigma_h-h^2\Gamma_h\Gamma_h^\top)$, is a
   neat way to see that a smoothed posterior over-covers. Part (c) cleanly gives the
   collapse edge of the window.
2. Every theorem comes with a numerical check, and the theory-to-measurement chain is
   quantified: theory → finite reference law $R^2=0.97$, reference law → trained network
   $0.93$, theory → network $0.90$. That chain is unusual and convincing.
3. Proposition 8 explains a puzzling earlier observation: $h_{\mathrm{eff}}$ was
   unidentified at $h=0.5$ and $h=6$. The paper turns that into $\kappa=O(h^{-3})$, with
   measured $\kappa$ ranking the bootstrap widths (Spearman 0.91).

**Weaknesses.**
1. **The mathematics is elementary.** Proposition 8 is two derivative identities and the
   mean-value theorem. Theorem 2 is Gaussian conditioning, independence of $\varepsilon$, and
   moments of a weighted sample. Proposition `specbias` is diagonalisation of a linear ODE.
   None needs a new technique. For a venue where the claim is "the central results are
   theorems", I would expect at least one result that is hard to prove. As it stands, the
   strength of the paper is the measurement framework, not the mathematics.
2. **No theorem connects trained networks to the NW family.** The hypothesis "a network is
   an NW mixture at one bandwidth" is supported by a one-parameter fit and the
   $h_{\mathrm{mean}}\approx h_{\mathrm{eff}}$ check. The calibration prediction applies
   Theorem 2 at $h_{\mathrm{eff}}$, which assumes that hypothesis. The spectral-bias
   appendix is the right direction, but it models the moments, not the flow. Its
   exponent ($p\approx2.2$) does not match the networks ($1.3$; admittedly poorly
   determined), and it explicitly does not map to iterations.
3. Proposition 8 assumes the minimiser lies in an interval $\mathcal I$ on which
   $u\cdot F'\ge\kappa$. A global identifiability statement, or a condition that
   excludes spurious minima over the whole grid, is missing. In the large-$h$ regime this
   is exactly where it matters.
4. Theorem 2 is Gaussian-only. The mixture posterior result (0.91 Spearman) is empirical.
   A version for log-concave posteriors, or at least a statement of which part survives
   (part (c) does; part (b) does not obviously), would strengthen the claim that the
   window is general.

**Questions.** (i) Can Proposition `specbias` be lifted from moments to the endpoint law,
e.g. by showing the learned field in the lazy regime is the minimiser for a filtered
label kernel? (ii) Is there a non-Gaussian analogue of Theorem 2(b)?

**ICLR:** Soundness 3, Presentation 2, Contribution 3. **Rating 5**, confidence 4.
**NeurIPS:** Quality 3, Clarity 2, Significance 2, Originality 3. **Overall 3**.
**ICML:** **Overall 2 (weak reject)**.

---

## Reviewer B: memorisation in diffusion models (empirical lens)

**Summary.** As above. I focus on whether $h_{\mathrm{eff}}$ is useful beyond the
synthetic setting.

**Strengths.**
1. The reframing is good. "Partial agreement with the reference at $h$" becomes
   "agreement at a larger bandwidth", and two disjoint statistics agree (48/48 synthetic,
   31/36 CIFAR-10 checkpoints).
2. The C8 confound from the previous round is handled. $h_{\mathrm{eff}}$ keeps Spearman
   0.90 with the iteration partialled out and 0.82 at a fixed iteration. It also repeats
   on a $d=8$ mixture posterior.
3. The paper is honest about negatives: the stopping rule is no better than one on the
   iteration count, and the on-atom fraction, not $h_{\mathrm{eff}}$, predicts extraction.

**Weaknesses.**
1. **Scale.** The calibration results are in $d\le8$ with $k=1$ labels. Image experiments
   use $N=2000$, one mask, and no calibration measurement. At image scale $h_{\mathrm{eff}}$
   fits variances no better than a two-parameter power law. The headline claim
   ("trained conditional flows memorise at an effective bandwidth") is therefore
   established where the reference is cheap and the posterior known.
2. **What does a practitioner gain?** $h_{\mathrm{eff}}$ does not beat the iteration
   count as a stopping rule, and does not predict extraction. Its value is diagnostic
   (calibration window), but the window is located with the posterior. A posterior-free use
   of $h_{\mathrm{eff}}$ at scale (e.g. predicting PIT error on CIFAR-10 inpainting, or
   comparing architectures by $h_{\mathrm{eff}}$ at matched loss) is missing.
3. Text-to-image and class-conditional settings, where memorisation matters most, are out
   of scope because labels have no natural kernel. That limits impact.

**ICLR:** Soundness 3, Presentation 2, Contribution 2. **Rating 5**, confidence 4.
**NeurIPS:** **Overall 3**. **ICML:** **Overall 2**.

---

## Reviewer C: uncertainty quantification / Bayesian inverse problems

**Summary.** The paper explains when a conditional generative sampler is calibrated:
under-coverage from collapse, over-coverage from smoothing, and a window in between set by
one number.

**Strengths.**
1. Theorem 2 is the result I would cite. It is the first clean statement I know of that
   label-noise conditioning of a generative posterior sampler over-covers in the infinite
   data limit, with the exact covariance deficit $h^2\Gamma_h\Gamma_h^\top$, and that finite
   effective sample size drives coverage to zero.
2. Figure 2 is convincing: the measured coverage of 75 checkpoints falls on the two-branch
   theoretical curve once each checkpoint is placed at its $h_{\mathrm{eff}}$.
3. The posterior-free PIT and the leave-seed-out stopping rule are good practice.

**Weaknesses.**
1. The 50% coverage is predicted much less well ($R^2=0.59$) than the 90% one ($0.90$).
   The appendix reports this, but the main text does not. The local model at small
   $n_{\mathrm{eff}}$ is sensitive to the weight distribution, which deserves a sentence.
2. Simulation-based-inference calibration methods (SBC, expected coverage tests, TARP) are
   the natural baselines for a calibration diagnostic and are not discussed.

**ICLR:** Soundness 3, Presentation 3, Contribution 3. **Rating 6**, confidence 3.
**NeurIPS:** **Overall 4**. **ICML:** **Overall 3 (weak accept)**.

---

## Reviewer D: clarity and positioning (generalist)

**Strengths.** Exceptionally careful scoping; every number is reproducible by a named
script; limitations are candid.

**Weaknesses.**
1. **Too many results for nine pages.** Collapse, NW endpoint law, atomicity floor,
   endpoint smoothing, interpolant noise, CFG, error survival, scope, three experiment
   families, $h_{\mathrm{eff}}$, an identifiability proposition, a calibration theorem.
   Each gets a paragraph, and the main story ($h_{\mathrm{eff}}$ and calibration) starts
   on page 8. A reader has to work hard to find the contribution. Sections 3.3–3.6 could
   move to the appendix, leaving room for the $h_{\mathrm{eff}}$ theory and figures.
2. The prose is dense with numbers (often 5–8 per paragraph) and parenthetical
   qualifications. The style is precise but not ICLR-typical.
3. Section 4.1 still says the residual variance at $h=0$ "is an optimisation gap", while
   Section 4.3 reinterprets it as an unfinished bandwidth. One of the two should be
   rewritten.
4. 75+ pages of appendix is a reviewing burden; consider trimming.

**ICLR:** Soundness 3, Presentation 2, Contribution 2. **Rating 5**, confidence 3.
**NeurIPS:** **Overall 3**. **ICML:** **Overall 2**.

---

## Meta-review

| Venue | Scores | Mean | Reading |
|---|---|---|---|
| ICLR 2027 main | 5 / 5 / 6 / 5 | 5.25 (round 2: 4.75) | borderline, below the usual bar (~5.5–6) |
| NeurIPS | 3 / 3 / 4 / 3 | 3.25 | borderline reject |
| ICML | 2 / 2 / 3 / 2 | 2.25 | weak reject |
| ICLR workshop | — | — | clear accept |

**What improved.** The paper now has theorems where it previously had only measurements:
identifiability explains the earlier failures, and the calibration theorem predicts measured
coverage ($R^2=0.90$). The confound concern is resolved. Reviewers agree on soundness (3/3/3/3).

**What blocks acceptance.**
1. *Depth of the mathematics* (A): every new result is elementary, and none concerns the
   trained network itself. For a "mathematical" paper at NeurIPS/ICML this is the
   decisive weakness.
2. *Scale and use* (B): calibration is shown only for $d\le8$ with known posteriors. At
   image scale, $h_{\mathrm{eff}}$ neither beats a power law nor is tied to an outcome.
3. *Focus* (D): the $h_{\mathrm{eff}}$ story starts on page 8.

**Verdict.** Not yet at the main-track bar of ICLR, NeurIPS or ICML. With a strong rebuttal
it is a borderline paper (ICLR ~25–35%, NeurIPS/ICML lower). It is a solid workshop paper now.

## What would move it over the bar (ranked by expected gain per effort)

1. **Refocus** (no new results needed, high gain): main text = Section 3.2 endpoint law →
   Section 4.3 $h_{\mathrm{eff}}$ + Proposition 8 + Theorem 2 + Figure 2 + spectral-bias
   model. Move 3.3–3.6 (endpoint smoothing, interpolant noise, CFG, survival) to the
   appendix as "interventions". Fix the §4.1/§4.3 inconsistency. This addresses D and
   makes the theorems visible to A and C.
2. **One non-elementary theorem about trained models** (high gain, high risk). The most
   promising route: in the lazy/NTK regime with a translation-invariant kernel on the
   label, prove that the learned *field* (not just the moments) is the minimiser for a
   filtered label kernel, so that the endpoint is NW at a kernel $K_h*\varphi_t$, and derive
   $h_{\mathrm{eff}}(t)$ with its rate. Proposition `specbias` is the first step.
3. **Theorem 2 beyond Gaussians** (medium gain): part (c) is distribution-free; part (b)
   could be shown for log-concave posteriors via a convex-order argument. State what holds
   in general.
4. **Image-scale calibration** (medium gain, needs GPU): posterior-free PIT on CIFAR-10
   against $h_{\mathrm{eff}}$ (the `calib_image_checkpoints.py` pipeline exists), and
   discussion of SBC/TARP.
5. Report the 50% coverage result in the main text; add a global identifiability condition
   to Proposition 8.
