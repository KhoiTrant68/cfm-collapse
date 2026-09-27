# ICLR paper plan — conditional flow matching, effective bandwidth, audit

Status 2026-09-27. The ICLR 2027 main deadline (25 Sep 2026) has passed and the paper was not
submitted. This plans the full paper for **ICLR 2028** (deadline expected late September 2027), with
the ICLR 2027 workshop (deadline expected late January 2027) and NeurIPS 2027 (expected May 2027) as
intermediate checkpoints.

Everything below that is marked **have** exists in the repo; **need** does not yet exist.

---

## 1. The paper in one sentence

> A conditional flow trained on finite data behaves like Nadaraya–Watson regression over its training
> examples at an **effective bandwidth** that training shrinks towards the one it was given; the exact
> reference this implies makes memorisation measurable and predicts when the sampler stops being a
> posterior sampler.

This replaces the current framing ("label smoothing does not restore the posterior"), which reviewers
read as a negative result about an object nobody trains. The new framing is a positive, predictive
statement about trained models, and the population theory becomes its foundation rather than its
conclusion.

**Contribution type (to state in the introduction):** analysis of model behaviour, supported by exact
theory, delivering an evaluation method.

**Status of the central hypothesis.** Supported on CIFAR-10 at the final checkpoint only (below). The
synthetic time-course test is running. **The plan below proceeds only if the kill criteria in §7 are
passed.**

| Evidence so far (CIFAR-10, DDPM U-Net, seed 0, 48 conditions) | h = 4 | h = 5 | h = 6 |
|---|---|---|---|
| fitted h_eff (one parameter per run) | 4.80 | 5.75 | 7.05 |
| R² in log space: h_eff model (1 param) | **0.81** | **0.65** | **0.41** |
| R² in log space: power law (2 params, current paper) | 0.79 | 0.52 | 0.14 |
| R² in log space: constant multiple of reference (1 param) | −0.13 | −1.29 | −7.26 |
| bandwidth implied by the mean alone (not fitted) | 5.30 | 6.45 | 7.45 |

---

## 2. Title, TL;DR, abstract

**Title candidates**
1. *Conditional Flows Memorise at an Effective Bandwidth*
2. *Trained Conditional Flows Are Kernel Regressors over Their Training Data*
3. *An Effective-Bandwidth Account of Memorisation in Conditional Flow Matching*

**OpenReview TL;DR (≤ 250 characters)**
> Trained conditional flow-matching models act like kernel regression over their training examples at
> an effective bandwidth that shrinks with training; an exact reference makes this measurable and
> predicts loss of posterior calibration.

**Abstract skeleton (first 40 words must stand alone)**
1. Phenomenon + insight (sentence 1): conditional flows trained on finite data lose posterior calibration
   and return training examples; we show a trained model behaves as Nadaraya–Watson regression over its
   training set at an effective bandwidth h_eff.
2. Theory (sentence 2–3): at the population optimum the endpoint law is exactly the NW mixture at the
   training bandwidth; it is atomic at every bandwidth, with an h-independent Wasserstein floor.
3. Finite models (sentence 4): one scalar h_eff per model predicts the per-condition variance
   (R² up to 0.81 with one parameter vs 0.14–0.79 for a two-parameter fit) and falls with training.
4. Use (sentence 5): the reference yields an audit (h_eff, on-atom fraction, tracking slope) that
   predicts calibration loss and gives a stopping rule.
5. Scope (sentence 6): identifying conditions (inverse problems, inpainting); synthetic, CIFAR-10,
   CelebA, and a PDE inverse problem.

---

## 3. Structure and page budget (9 pages)

| § | Title | Pages | Content | Figures / tables |
|---|---|---|---|---|
| 1 | Introduction | 1.25 | Phenomenon; one-sentence insight; three contributions; what-to-verify box | **Fig. 1**: concept (population NW law → trained model at h_eff → collapse as h_eff ↓) |
| 2 | Setup | 0.5 | Fixed data, linear interpolant, label noise; one notation table | Table 1: notation |
| 3 | Exact theory | 1.75 | Collapse (Prop 1), NW endpoint law (Thm 1), reference moments, atomicity floor (Prop 2), where noise acts (Table 2) | Table 2: noise placement → endpoint law |
| 4 | Trained models have an effective bandwidth | 2.0 | Definition and estimator of h_eff; fit vs alternatives; out-of-sample check on means; h_eff over training; theory for a tractable model (T1) | **Fig. 2**: measured vs reference at h and at h_eff; **Fig. 3**: h_eff/h over training, across N and capacity |
| 5 | Auditing and stopping | 1.5 | Audit protocol (box); audit predicts calibration; stopping rule; remedies ranked by audit | **Fig. 4**: audit metrics vs calibration; Table 3: remedies |
| 6 | Related work | 0.5 | Closed-form memorisation; kernel views; conditioning augmentation; concurrent work | — |
| 7 | Limitations and conclusion | 0.5 | Scope, what is not predicted, compute | — |

**Moved to the appendix (answering predictable objections, not carrying decisive evidence):** CFG
result, loss-form corollary, asymptotic expansion and NW rates, near-duplicate labels, well-posedness
lemmas, all per-seed tables.

---

## 4. Claims → evidence map

| # | Claim | Evidence | Where | Status |
|---|---|---|---|---|
| C1 | Identifying labels give δ at the optimum | Prop. 1 + EXP-1, CIFAR h=0 (memorisation ratio 1.000, 48/48) | §3, §4 | **have** |
| C2 | Label noise gives the NW mixture; atomic; h-independent floor | Thm. 1, Prop. 2, proof checks | §3 | **have** |
| C3 | One h_eff per model predicts per-condition variance better than a 2-parameter fit | CIFAR (above); synthetic per checkpoint | §4 | CIFAR **have**; synthetic running |
| C4 | h_eff is also what explains the conditional means (out of sample) | CIFAR partial (bias ~10%); synthetic running | §4 | **need** agreement or an explanation of the gap |
| C5 | h_eff falls towards h with training | synthetic checkpoints; CIFAR checkpoints | §4 | **need** |
| C6 | h_eff/h depends on capacity and N in a predictable way | synthetic sweep over width, depth, N | §4 | **need** |
| C7 | Tractable theory for h_eff (T1) | kernel / random-features model | §4 | **need** (research risk) |
| C8 | Audit predicts calibration and extraction | EXP-1/GMM (analytic posterior): coverage, W₂; image: memorisation | §5 | **need** |
| C9 | Audit-based stopping beats loss-based stopping | synthetic + one image dataset | §5 | **need** |
| C10 | Common remedies ranked by the audit | early stopping, EMA, weight decay, CADS, endpoint noise | §5 | partial (population level) |
| C11 | Holds beyond CIFAR-10 | CelebA/FFHQ 64×64; a PDE inverse problem | §4–5 | **need** |

---

## 5. Experiments

Each run has three seeds unless noted, and each seed redraws the problem instance.

| ID | Experiment | Claims | Setting | Compute |
|---|---|---|---|---|
| E1 | h_eff per checkpoint, synthetic | C3–C5 | EXP-1, h ∈ {0, 0.01, 0.05, 0.1, 0.5}, 8 checkpoints | CPU, running (seed 0); +2 seeds |
| E2 | h_eff vs capacity and N | C6 | EXP-1 width {32…256}, depth {2,4,6}, N {50…2000} | CPU, ~2 days |
| E3 | CIFAR-10 with checkpoints kept | C3–C5, C11 | h ∈ {0,4,5,6}, 3 seeds, 120k iterations, keep all checkpoints | ~12 runs × 16 h ≈ 190 GPU-h |
| E4 | Second image dataset | C11 | CelebA 64×64 or FFHQ 64×64 inpainting, h ∈ {0, 2 values} | ~100 GPU-h |
| E5 | PDE inverse problem | C8, C11 | Darcy flow, permeability from sparse pressure; reference posterior by MCMC | ~50 GPU-h + MCMC |
| E6 | Audit vs calibration | C8 | EXP-1, GMM, E5: coverage of credible sets, W₂, extraction rate vs h_eff, β, on-atom | reuses E1/E5 |
| E7 | Stopping rule | C9 | audit on held-out conditions vs validation loss | reuses E1/E3 |
| E8 | Remedies | C10 | early stopping, EMA, weight decay, CADS annealing, endpoint noise | synthetic + E3 config, ~60 GPU-h |

**Ablations the reviewers will ask for:** ODE step count and solver (h_eff must not be an integrator
artefact); sample size M (sampling error of the trace); kernel choice in the audit (Gaussian vs the
metric the label actually lives in); grid resolution of the h_eff fit.

**Compute:** ≈ 400 GPU-hours. Kaggle alone (~30 h/week) takes ~14 weeks; plan for an additional GPU
source.

---

## 6. Theory

| ID | Result | Why | Risk |
|---|---|---|---|
| T1 | h_eff for a tractable model: e.g. a velocity field smooth in y with smoothing scale s gives a NW law at a composed bandwidth; derive how s depends on training time | Turns C3 from an observation into a prediction; answers "what is new" | High. First test the two candidate laws on data: additive, h_eff² = h² + s² (CIFAR gives s = 2.65, 2.84, 3.70, not constant) versus multiplicative, h_eff = κh (κ = 1.20, 1.15, 1.18, nearly constant) |
| T2 | Condition-dependent source distributions keep the endpoint atomic | Answers the round-2 question; completes Table 2 | Low |
| T3 | Survival identity → bound on β or on h_eff − h in terms of residual loss | Connects the optimisation view to the audit statistic | Medium |

---

## 7. Kill criteria and fallbacks

Decide after E1 and a first E3 run (target: end of October 2026).

| Outcome | Decision |
|---|---|
| h_eff fits beat alternatives on synthetic too, **and** h_eff falls with training, **and** means agree within sampling error | Proceed with this plan |
| Fits hold but h_eff does not fall with training | Reframe: h_eff as a capacity/architecture property (C6), drop C5/C9 |
| Fits hold but means disagree systematically | Report two bandwidths (variance vs mean) and investigate; weaker paper |
| Fits fail on synthetic | Drop the h_eff framing. Submit the workshop version; move the full paper to TMLR with the current framing and the round-2 fixes |

---

## 8. Writing standards (ICLR style)

- **First page carries the insight.** Abstract sentence 1 and Fig. 1 state the h_eff account; no
  background before it.
- **What to verify** box at the end of §1: Thm. 1 (proof in App. A.3, numerical check
  `proof_checks/group1`), the h_eff fit (Fig. 2, `scripts/test_heff_*.py`), the calibration result
  (Fig. 4), the supplementary package.
- **Captions are arguments.** Each caption opens with the claim the figure supports.
- **One notation table** (§2); one name for the endpoint law (see the style audit).
- **Scoped claims.** "Identifying conditions", "at the population optimum", "for the models we train".
- **No internal labels** in the main text (EXP-1, P1–P7, T1); name experiments by what they are.
- **Mandatory statements:** reproducibility, ethics (memorisation and data extraction), LLM use.
- **Anonymity:** supplementary package rebuilt with the same scan as the 2026-09-27 package.

---

## 9. Timeline

| When | Milestone |
|---|---|
| Oct 2026 | E1 complete (3 seeds), E2; E3 first run with checkpoints; **kill-criteria decision** |
| Nov 2026 | E3 remaining runs; T2; start T1 |
| Dec 2026 | E6, E7 on synthetic; draft §3–§4 |
| Jan 2027 | **Workshop submission** (short version with h_eff result); E4 starts |
| Feb–Apr 2027 | E4, E5, E8; T1 decision (in or out) |
| May 2027 | Optional **NeurIPS 2027** submission if C3–C9 are complete |
| Jun–Aug 2027 | Full draft; two rounds of simulated review; ablations |
| Sep 2027 | **ICLR 2028** abstract and paper; supplementary package |

---

## 10. Prepared answers to predictable objections

| Objection | Answer and pointer |
|---|---|
| "The population result is known / trivial" | We use it as a reference, not as the contribution; the contribution is that trained models follow it at h_eff (§4) |
| "h_eff is just another fitted parameter" | One parameter per model predicts 48 conditions and beats a two-parameter fit; validated out of sample on the means |
| "Only CIFAR-10" | CelebA/FFHQ and a PDE problem (E4, E5) |
| "Why should practitioners care?" | Audit predicts calibration loss and gives a stopping rule (§5) |
| "Class/text conditioning?" | Out of scope; shared labels reduce to per-class unconditional memorisation (appendix corollary) |
| "Integrator artefact?" | Solver and step-count ablation; h=0 reproduces the atom exactly |
