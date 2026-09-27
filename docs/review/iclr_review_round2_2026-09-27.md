# Simulated ICLR 2027 Review — Round 2

- **Submission**: *Auditing Conditional Flow Matching: Label Smoothing Is Kernel Regression over Training Atoms*
- **Version reviewed**: `paper/main.tex` at `a742398` (after the P0/P1 fixes and the cleanup pass), main text 9 pages + appendix (71 pp. total)
- **Format**: OpenReview, ICLR scale — Soundness / Presentation / Contribution on 1–4; Rating in {1, 3, 5, 6, 8, 10}; Confidence 1–5
- **Line numbers** refer to `paper/main.tex` at that commit.

> All four reviews and the meta-review are written by one model in one session, each from an assigned
> perspective. They are not independent in the way four human reviewers are, and the ratings are an
> ordinal judgement, not a prediction of the outcome. Reviews are written in English, as they would be on
> OpenReview.

---

## Reviewer vK3p — theory of flow matching / closed-form empirical optima

**Summary.**
The paper studies the population minimiser of conditional flow matching when the data law is a fixed
empirical measure and each condition identifies one training example. It shows that the minimiser sends
every source point to the identified atom (Prop. 2), that Gaussian noise on the condition turns the
endpoint law into a Nadaraya–Watson mixture over the training atoms (Thm. 5), and that this law is
atomic for every bandwidth, giving an $h$-independent $W_2$ floor (Prop. 9). It classifies interpolant,
label, guidance and endpoint noise by their effect on the endpoint law, and adds an error-survival
identity for approximate fields (Prop. `survival`). Experiments on synthetic problems and CIFAR-10
compare trained models with the exact reference moments.

**Strengths.**
1. The statements are careful and correct as far as I checked. Well-posedness on $[0,1)$ and the existence
   of the endpoint as a weak limit are proved rather than assumed (Lemma `wellposed`, the "three
   conventions" paragraph), which is better than much of the closed-form literature.
2. The factorisation of the index posterior into a spatial factor and a label factor, with only the label
   factor surviving to $t=1$ (Prop. `factors`), is a clean way to see why interpolant noise is inert
   while label noise is not. The corrected pathwise target for the stochastic interpolant (eq.
   `c2target`) is a point many implementations get wrong.
3. The survival identity $e_t=(1-t)I(t)$ is a genuinely useful lens: it says a finite model can keep
   conditional variance only through velocity error of order $(1-t)^{-1}$.

**Weaknesses.**
1. **The central results are short consequences of known facts.** Once the empirical minimiser is written
   as a posterior-weighted average over atoms (Scarvelis et al., 2025; Gao & Li, 2024; Bertrand et al.,
   2025), Thm. 5 follows from the mixture-coupling lemma in a few lines, and Prop. 9 follows from Thm. 5
   in one line. The paper says so itself ("We do not claim a new generic kernel identity", l. 103). The
   concurrent work of Li et al. (2026), now cited, already derives closed-form optimal fields for
   stochastic interpolants and shows that the endpoint is a training sample plus controlled perturbations
   under estimation error. The delta relative to that work — the conditional label factor and the
   floor — is real but narrow.
2. **The deepest result is under-sold and, as stated, weak.** Cor. `lossform` needs a Lipschitz
   hypothesis on the error that the paper itself shows forces $L_\Delta\ge\delta^{-1}-K$ (l. 533), so for
   bounded-Lipschitz networks the bound is vacuous. Yet contribution 5 (l. 174–180) states that the
   retained error "is bounded by the loss not yet removed" without this caveat. Either the contribution
   list should carry the caveat, or a version of the bound that applies to realistic networks is needed.
3. The guidance result (§3.5) is empty when $N>d$, which is the regime of the synthetic experiments;
   it has content only for CIFAR-10, where it is not tested.

**Questions.**
1. Can the survival identity be turned into a statement about $\beta$, e.g. a bound on how far $\beta$
   can be from 1 given the residual loss? That would connect the theory to the paper's own audit
   statistic and would be the most original contribution.
2. How does Thm. 5 relate to Li et al. (2026) beyond conditioning? Is there a statement there that
   specialises to Prop. 2?

**Soundness:** 3 **Presentation:** 2 **Contribution:** 2
**Rating:** 5 (marginally below the acceptance threshold) **Confidence:** 4

---

## Reviewer Rt7m — empirical diffusion / memorisation

**Summary.**
Empirical study of conditional memorisation in flow matching, measured against an exact reference.
Synthetic linear-Gaussian and GMM problems, MNIST inpainting, and a CIFAR-10 inpainting run with a
35.75M DDPM U-Net ($N=2000$, three bandwidths, three instances). The proposed audit compares measured
and reference conditional variance by an aggregate/median ratio and by an across-condition log–log slope
$\beta$.

**Strengths.**
1. The synthetic evaluation is unusually clean: the model matches the exact reference $\tr\Covh$ to
   $1.002\pm0.050$, $0.994\pm0.039$, $1.011\pm0.022$ at $h=0.05,0.1,0.5$ (Table `p7kernel`), and the paper
   correctly identifies that the apparent "restoration" of posterior variance at $h\approx0.1$ is a
   coincidence of this instance.
2. The shuffled-label control (Appendix `adv`) is a good experiment: collapse persists when $y$ carries no
   information about $x$, which isolates identification from informativeness.
3. The statistical reporting on CIFAR-10 is careful: bootstrap intervals, re-measurement at $M=256$,
   a warning against averaging per-condition ratios, rival fits for $\beta$.
4. The observation that level agreement is vacuous when the reference has little range (0.74 decades
   at $h=6$, median ratio 1.15, $\beta=-0.156$) is useful beyond this paper.

**Weaknesses.**
1. **One of the headline measurements is true by construction.** The abstract says that under hard
   conditioning "every evaluated condition selects one effective atom" (l. 70), and §4.2 reports
   $n_{\mathrm{eff}}=1.00$ at all 48 conditions (l. 643, 646). But $n_{\mathrm{eff}}$ is computed from the
   reference weights $p^{(h)}$, which at $h=0$ are a point mass by definition
   (`kernel_weights`: "h == 0: uniform over argmin"). It is not a property of the trained model. The
   measured evidence is the memorisation ratio of 1.000 and the 48/48 nearest-neighbour identification,
   which are strong; the $n_{\mathrm{eff}}$ statement should be removed or relabelled as the reference.
2. **Image-scale evidence is thin.** One dataset, one mask, $N=2000$, 60k iterations, and $\beta$ from one
   instance (stated, l. 681). $\beta$ is still rising when the budget ends (Fig. `betatraj`), so the
   central image-scale number is a snapshot of optimisation, not a property of the method. A longer run at
   $h=4$, or a second dataset, would change how this can be read.
3. **No comparison with what practitioners do.** Early stopping, EMA, weight decay, and CADS-style
   inference-time annealing (Sadat et al., 2024) are the remedies in use; the paper evaluates label,
   interpolant and endpoint noise at the population level and endpoint noise on a trained model at
   $N=50$ only. The audit's value would be clearer if it were applied to one of these.
4. **The atomicity result does not describe the trained model at scale.** 17–38% of CIFAR-10 samples
   are off-atom for $h>0$. The paper is candid about this (§5), but it means the proposition in the title
   of Section 3.2 is verified only where it is hard to distinguish from the posterior ($d=2$, floor 3.5%
   of $\tr\Sigmapost$).

**Questions.**
1. Please report $\beta$ for the other two CIFAR-10 instances if they can be regenerated.
2. For the off-atom samples at $h>0$: are they near convex combinations of the top-weighted atoms
   (interpolation) or elsewhere? This would say whether the network is smoothing the reference or
   ignoring it.
3. Why $h\in\{4,5,6\}$? The configs say bandwidths were set against the median nearest-neighbour
   distance in condition space (12.6); please state this in the paper.

**Soundness:** 3 **Presentation:** 3 **Contribution:** 2
**Rating:** 5 (marginally below the acceptance threshold) **Confidence:** 4

---

## Reviewer Wq2d — Bayesian inverse problems / uncertainty quantification

**Summary.**
For users of conditional flows as posterior samplers, the paper explains why samplers trained too long
become deterministic, shows that the common fix of noising the condition only reweights training
examples, and proposes an audit against an exact reference that can be computed from the training set.

**Strengths.**
1. It answers a question practitioners actually have ("I added conditioning noise and the variance came
   back — am I sampling the posterior?") with a clear no, and gives a computable test (Appendix
   `audit`).
2. The distinction between recovering a posterior moment and recovering the posterior is stated sharply
   and is the right one for UQ.
3. Scope is stated honestly: identifying conditions, inverse problems and inpainting (l. 149–150).

**Weaknesses.**
1. **The audit protocol is in the appendix.** It is the part a practitioner would use, and it appears in
   the main text only as a one-line pointer (l. 168). For this audience, it should be in the body with a
   worked example.
2. **No answer to "when to stop".** The paper says so (§3.7), but it also has the ingredients — $\beta$ over
   checkpoints (Fig. `betatraj`), the aggregate ratio crossing 0.98 at $h=6$ (Appendix `remedies`). A
   stopping rule evaluated on held-out conditions would make the work directly usable.
3. **No real inverse problem.** The motivating application (physics-constrained inverse problems,
   Dasgupta et al., 2026) is not evaluated. Inpainting is a reasonable proxy, but a PDE-based problem with
   a reference posterior would make the paper's claims land with its intended audience.

**Questions.**
1. Condition-dependent source distributions (e.g. [Better Source, Better Flow, arXiv 2602.05951](https://arxiv.org/html/2602.05951))
   are another place stochasticity enters. Where do they sit in the ordering of §3.5 (inert,
   atom-preserving, reweighting, support-moving)?
2. Fig. 1(c) is at "the $h^\star$ with $\tr\Covh=\tr\Sigmapost$" and the panel is labelled $h^\star=0.70$,
   while §4.1 says the crossing is near $h=0.1$. Is $h^\star$ per condition? Please say so in the caption.

**Soundness:** 3 **Presentation:** 2 **Contribution:** 3
**Rating:** 6 (marginally above the acceptance threshold) **Confidence:** 3

---

## Reviewer Hx9L — generalist, sceptical

**Summary.**
The paper argues that label smoothing in conditional flow matching cannot recover the posterior because
the population minimiser is supported on training points, and proposes to audit trained models against
that minimiser.

**Strengths.**
1. Clear, falsifiable statements with complete proofs and numerical checks.
2. Unusually honest about what fails (§5, Table `seed3`).

**Weaknesses.**
1. **"So what?"** The minimiser of an empirical-risk objective over all $L^2$ functions interpolates the
   training data; that it does so for conditional flows, with or without label noise, is expected. The
   interesting object is the trained network, and there the paper finds that the theory's key property
   (atomicity) fails (38% off-atom), and the tracking slope is 0.48 at best. The audit therefore compares
   models with a target they do not reach, and it is not shown to predict anything a practitioner cares
   about (sample quality, calibration, data extraction).
2. **Scope excludes the mainstream.** ICLR's conditional generation is mostly class- and text-conditional.
   With shared labels, Cor. `repeated` gives the within-class empirical measure, i.e. the known
   unconditional result applied per class. The new content therefore concerns identifying conditions only.
3. **Density.** 29 formal results, a 71-page PDF, and a main text that points to the appendix in nearly
   every paragraph. The contribution list is long and partly defensive (contribution 4 is titled "Two
   remedies" but one of the two is shown not to be a remedy, l. 169–171).

**Questions.**
1. Does the audit predict anything beyond itself? E.g., does a low $\beta$ or a high on-atom fraction
   predict worse posterior calibration (coverage) on held-out conditions?

**Soundness:** 3 **Presentation:** 2 **Contribution:** 1
**Rating:** 3 (reject, not good enough) **Confidence:** 4

---

## Meta-review (Area Chair)

**Scores.** Ratings 5 / 5 / 6 / 3 (mean 4.75). Soundness 3 / 3 / 3 / 3; Presentation 2 / 3 / 2 / 2;
Contribution 2 / 2 / 3 / 1.

**Consensus.** All reviewers find the mathematics correct and the reporting unusually careful and honest.
All agree the exact reference and the level-versus-slope point about auditing are useful. Three of four
find the central theorems to be short consequences of known closed-form results, with a narrow delta
over concurrent work (Li et al., 2026). All four note that the theory's defining property, atomicity,
does not hold for the trained network at image scale, so the empirical contribution rests on one
CIFAR-10 configuration with $\beta$ from one instance and still rising at the end of training.

**Disagreement.** Wq2d sees practical value for posterior-sampling users; Hx9L sees none demonstrated. The
AC agrees with Wq2d that the audit is useful in principle, and with Hx9L that the paper does not show it
predicts calibration or sample quality.

**Concrete errors to fix regardless of venue.**
- $n_{\mathrm{eff}}=1.00$ at $h=0$ is a property of the reference by construction, not a measurement
  (abstract l. 70; §4.2 l. 643, 646; Appendix l. 3066) — Rt7m W1.
- Contribution 5 omits the caveat that makes Cor. `lossform` vacuous for bounded-Lipschitz networks
  (l. 174–180 vs l. 533) — vK3p W2.
- Contribution 4 is titled "Two remedies" but lists one non-remedy (l. 169) — Hx9L W3.
- Fig. 1(c): state that $h^\star$ is per condition (0.70) versus the aggregate crossing near 0.1 — Wq2d Q2.
- State the bandwidth choice for CIFAR-10 (median nearest-neighbour distance 12.6) — Rt7m Q3.

**Recommendation.** *Reject* for the main track (below the typical acceptance bar of about 5.5–6). The
paper is a good fit for a workshop on the theory of generative models, where its clarity and honesty
are assets and the narrowness of the theoretical delta matters less.

**Compared with the first simulated round.** The median/aggregate inconsistency, the revision history in
the appendix, the uncited 2026 work and the h = 0.01 omission are resolved, and the title and abstract
are now scoped to the population optimum. The rating moves little because the remaining concerns
(novelty, scale, relevance of the atomic target to trained models) are about substance, not presentation.

---

## Workshop calibration (`paper/workshop.tex`)

The workshop version already centres the audit and drops the weakest theory (guidance, loss-form), which
answers vK3p W2/W3, Wq2d W1 and Hx9L W3 by construction. It inherits Rt7m W1 in its own text ("every
condition has $n_{\mathrm{eff}}=1.00$") and should be fixed the same way. Expected outcome at a
theory-of-generative-models workshop: **accept**, likely as a poster.
