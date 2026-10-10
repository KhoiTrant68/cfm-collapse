# Paper verification — `paper/main.tex` against code and results (2026-10-10)

Scope: the conference paper `paper/main.tex` (all 4,703 lines, main text and appendices), the
code under `src/` and `scripts/`, the saved outputs under `results/`, and `paper/refs.bib`.
`paper/workshop.tex` was checked only for numbers absent from `main.tex` (none) and for the
wording problems below (it carries none of them).

How it was checked:

- `scripts/verify_paper_numbers.py` passes **116/116**. It covers the CIFAR DDPM section, P6
  exposure, the seed split, OT resolution, the atomicity-floor slopes and the survival closed
  forms. Note that it checks numbers hard-coded in the script against the files; it does not
  read them out of `main.tex`.
- `docs/review/paper_verification_2026-10-10_checks.py` (new) adds **215** checks on what that
  script does not cover: Table 1, the schedule run, memorisation, held-out, adversarial,
  ablation, the velocity-field table, gap-to-optimum, optimality gap, P5/P7, endpoint
  smoothing, EXP-2, the EXP-3 N-sweep, collapse time, T1/T3, CIFAR extras and class labels.
  Result: **199 OK, 16 flagged**; every flag is discussed below.
- Additional checks done by hand: synthetic and CIFAR h_eff (48/48, 31/36, 1.08h,
  1.13–1.34h, 9/15, 12/12, R² 0.86/0.79/0.66), calibration Spearman values, κ, T2 slopes,
  p-exponents, collapse time, per-seed ||J||², the estimator code, and the loss variants.
- **Could not recompute anything that needs torch.** Torch DLLs are blocked on this machine by
  a Windows Application Control policy, so numbers that exist only as script stdout or inside
  figures are listed as untraceable (§1.4), not as wrong.

## Summary

**35 issues: 4 high, 16 medium, 15 low.** About 370 numerical checks were run; all but about
20 match their source to the printed precision. The theory checked out wherever it was checked
(the TV/Pinsker bound, the non-monotone example, the Lipschitz floor integral, the survival
closed forms, the bandwidth-identity derivatives).

The four high-priority items:

1. **The CIFAR seed-reproducibility analysis uses the in-training evaluator** (8 conditions at
   M=16), not the stated 48 conditions at M=256. On the same instance the two protocols differ
   by up to 15% in the aggregate ratio, which is the size of the spreads the paper interprets.
2. **"Each instance redraws the mask" is false.** The mask is the fixed bottom half for every
   seed.
3. **The h=0.5 overshoot is attributed to the h²‖J‖² term, but the numbers don't match.** The
   paper uses seed 0's ‖J‖² against the 5-seed mean variance, and even for seed 0 the term
   explains less than half of the overshoot.
4. **"Every ± is a population std" is false** for the ablation table and the N-sweep.

---

## 1. Numerical audit

### 1.1 Verified (abridged; full list from the two checkers)

| Paper claim | Location | Source | Source value | Match |
|---|---|---|---|---|
| 48/48 checkpoints agree; log-corr 0.97; median ratio 1.03 | abstract, L552–554 | `results/exp1/_heff/heff_synthetic.json` (h≤0.1, iter≥1e4) | 48/48, 0.973, 1.032 | ✓ |
| 31/36 CIFAR checkpoints; 4 of 5 misses at h=5, 5k–10k | abstract, L615–616 | `results/exp3/_heff/*.json` | 31/36; misses h5 s0@5k, s0@10k, s1@5k, s2@5k, h4 s2@20k | ✓ |
| h_eff ends at 1.08h (synthetic, h≥0.05); 1.13–1.34h (CIFAR) | abstract, L557, L617 | same | 1.078; 1.131–1.337 | ✓ |
| monotone 5/6; still falling in 4, flat in 2; β reaches 0.66 at 1.13h | L617–620 | same | ✓ (h5_s0 non-monotone; h4_s2, h5_s0 flat; 0.659) | ✓ |
| h=0: 0.011±0.006 at 2e5; h=0.5: 9/15 intervals overlap; 12/12 runs fall 1e4→1e5 | L556–560 | `heff_synthetic.json` | 0.0115±0.0064 (pop.); 9/15 (iter≥3000); 12/12 | ✓ |
| fit R² 0.86 vs 0.79 vs 0.66 | L2992–2994 | same, 48-checkpoint set | 0.860, 0.792, 0.658 | ✓ |
| R²=0.90 (90%), MAE 0.051, Spearman 0.89; ref 0.93; agree 0.97; n_eff-only 0.61; 50%: 0.59/0.68 | L72, L593, L3017–3023 | `results/theory/t3_coverage.json` t3d | 0.900, 0.0515, 0.888, 0.932, 0.967, 0.609, 0.593, 0.683 | ✓ |
| Spearman h_eff 0.92, loss 0.85, raw var 0.76, β 0.34; partial 0.90, 0.69 (loss 0.42), fixed-iter 0.82; GMM 0.91/0.91/0.90, PIT −0.67 | L596–598, L3002–3009 | `results/exp{1,2}/_heff/audit_v2_analysis.json` | all match | ✓ |
| κ = 17.1, 3.8, 0.38, 0.13; Spearman 0.91; median κ 1.4 vs 5–33 | L547, L1939–1941 | `results/theory/t1_check.json` | 17.14, 3.80, 0.376, 0.125; 0.911; 1.36; 5.28–32.8 | ✓ |
| T2 slopes −0.40/−0.29/−0.05; 6/6, 5/6, 0/6; R² 0.97/0.95; p 2.2/2.8/2.8; RMSE 0.352 vs 0.366 | L631, L3087–3130 | `t2_summary.json`, `t2_filtered.json`, `_heff_law.json` | all match | ✓ |
| Table 1 (all 50 cells), tr Σ_post 1.018±0.016, tr X̂ 1.931±0.162 | L2371–2392 | `exp1_cond_seed[0-4]`, `exp1_uncond_seed[0-4]`, `exp1_ext_sched_seed*` | all match (pop. std) | ✓ |
| Schedule: 0.128 vs 0.162 at 7e5; 0.115 at 1e6; range 0.035–0.186; 4/5 improve; 0.955 | L3286–3292, L3309 | `exp1_ext_sched_seed*`, `exp1_cond_seed0_ext` | all match | ✓ |
| memorisation 0.650±0.033 vs 0.389±0.032, baseline ≈0.11 | L444–446, L3303 | `_analysis_memratio/summary.json`, `*_mr` runs | 0.650±0.033, 0.389±0.032, 0.114/0.114 | ✓ |
| Held-out table, medians 0.43 vs 0.42, 0.12→0.87, 6.0e4 | L3816–3830, L3317–3322 | `exp1_cond_seed*` heldout rows | all match | ✓ |
| Adversarial 0.625±0.108; 0.84±0.13→1.437±0.176; 1.35±0.10→0.559±0.104; crossing 1e4–3e4 | L3326–3332, L3648–3658 | `exp1_adv_shuffle_seed*` | all match (crossing at the 3e4 checkpoint) | ✓ |
| Table 5 (P7 kernel) and velocity-field table (12 cells) | L4387–4408, L4484–4503 | `p7_kernel_summary.csv`, `kernel_verification.csv` | all match | ✓ |
| Gap h=0.1 table (except the ratio row, §2.2), n_eff 25.1 (13.7–43.9), per-seed 0.019–0.026, 2.85 | L4250–4272 | `exp1_ext_sched_h01_seed*` | all match | ✓ |
| Optimality gap 1.14→0.22→0.102; L* 0→1.88; last gap 0.09–0.44; monotone | L4141–4150 | `optimality_gap.csv` | ✓ | ✓ |
| Lipschitz 7.1→65.7; d/(3L)≈0.010; ~50× below 0.48 | L4157–4158 | `lipschitz.csv` | 7.08, 65.66, 0.0102, 47× | ✓ |
| Posterior distance MMD 0.256→0.012, OT 1.34→0.119, floor 0.00073 / 0.075, 0.345 vs 0.333, n_eff ≤66 | L4178–4193, L4216 | `posterior_distance_exp1.csv`, `posterior_reference_scales.csv` | all match (but see L6) | ✓ |
| Endpoint smoothing table (20 cells), 1.49×, 1.29× | L3773–3797 | `target_noise_trained.csv` (+ per-seed values) | means match | ✓ |
| P5/P6/(d,k) sweeps | L3842–3892 | `_sweeps/summary.json` | all match | ✓ |
| EXP-3 N-sweep A/B/C, slopes +0.90/−0.29, spreads 14.9×/2.3× | L4026–4088 | `exp3/_n_sweep/summary.json` | all match | ✓ |
| CIFAR Table 4 incl. bootstrap CIs and SEs; β trajectory; 20.4 mean vs 5.30 median; seed-2 n_eff 2.10 | L3222–3240, L3426–3427, L3487 | `stats.json`, `beta_trajectory.json`, `reeval.json` | all match | ✓ |
| Class labels 717/719, 0.64–0.83, 0.62–1.30, 0.76, loss 0.22→0.06 | L4683–4688 | `exp3_cifar_class_h0{,p4}` | all match | ✓ |
| collapse time 0.86–0.97 (d=2), 0.06 (d=3072); initial n_eff 4, 18, 81 | L2494, L3680 | `collapse_time.json` | 0.859–0.974; 0.057–0.065; 4.43, 17.6, 81.0 | ✓ |
| floor slopes −0.612/−0.379/−0.249, d=2 −0.846, drift 1.05/1.52 | L2629–2632 | `atom_floor_scaling.csv` | ✓ | ✓ |
| 0.071 and 0.9975 (N^{-1/d}); 1.0e-3·σ^{2/(1−σ²)} spread 0.01/0.07; √(2/255)=8.9%, √(2/15)=36% | L397, L3415, L3215 | arithmetic | ✓ | ✓ |

### 1.2 Numbers that do not match their source

| # | Paper claim | Location | Source | Source value | Severity |
|---|---|---|---|---|---|
| N1 | Table 6 and "179.1→0.431, factor 415", "0.409–0.467", presented after "evaluating 48 conditions at M=256" | L495–503, L3508–3537 | `configs/exp3_cifar_ddpm.yaml` `eval: n_conditions 8, M 16`; `raw/metrics.csv` | training-log estimator (8 cond, M=16) | **HIGH** (§2.1) |
| N2 | "1.29 … matching the +h²‖J‖²_F term (‖J‖²_F=0.4031)" | L4499–4501 | `exp1_cond_seed*/problem.json`, `p7_kernel.csv` | ‖J‖² = 0.40, 1.89, 4.46, 1.44, 0.38 by seed; Σ_post+h²·0.4031 = 1.12; 5-seed expansion 1.446; seed-0 expansion 1.105 vs measured 1.286 | **HIGH** |
| N3 | Ablation ± (0.058, 0.058, 0.079, 0.156, 0.127, 0.193) under "population std throughout" | L3209–3213, L3613–3620 | `ablation_*_seed[01]` | pop. std 0.041, 0.041, 0.056, 0.110, 0.090, 0.136 (the printed values are the √2-larger sample std) | **HIGH** |
| N4 | "levels resolved … by 1.8 to 2.3× in higher dimension" | L3741–3742 | Table 10 row d=10, N=50 | 12.72/4.27 = 2.98× | MEDIUM |
| N5 | "OT gains … below resolution at every row" | L3743–3745 | Table 10's own cells | d=2, N=50: 0.76−0.76/1.04 ≈ 0.029 > floor 0.019; d=2, N=200: ≈0.015 vs 0.014 | MEDIUM |
| N6 | "matches tr Cov_h + dρ² to within 3% in both arms … per seed as well as on average" | L3391, L3766–3768, L3791 | Table 11 | arm means 0.2% and 3.1%; per seed up to 5.9% (seed 1, ρ=0.3: 0.587 vs 0.624) | MEDIUM |
| N7 | "range ~0.14 is smaller than the between-seed std at each point (0.11–0.24)" | L3885–3888 | `_sweeps/summary.json` | range 0.143; ratio std 0.108, 0.125, 0.122, 0.154 (trace std 0.108, 0.127, …); false at 3 of 4 points | MEDIUM |
| N8 | "2–4× closer to the kernel field … at every h" | L3354, L4496 | `kernel_verification.csv` | 1.88× (h=0.01) to 4.81× (h=0.5) | MEDIUM |
| N9 | "four of five seeds … held-out tr Cov within a factor of ~2 of training" | L3804–3805 | Table 12 | seed 4: 3.5× (0.564 vs 0.162); seed 1: 2.6× | MEDIUM |
| N10 | Table 13 caption "tr Σ_post = 1.004" for "median over 5 seeds" | L4262 | `exp1_ext_sched_h01_seed*` | 5-seed median 1.015; 1.004 is seed 0 | LOW |
| N11 | iteration Spearman "−0.42" | L3004 | `audit_v2_analysis.json` | −0.4147 → −0.41 | LOW |
| N12 | EXP-2 "MMD grows to ~0.25" | L479 | `exp2/_analysis/summary.json` | 0.239 | LOW |
| N13 | "(d) identities to 10⁻³"; "mean error ≤0.017", "covariance error ≤0.7%" | L2006–2009 | `t3_coverage.json` | Var-mean identity off by 1.9e-3; 0.0174; 0.74% | LOW |
| N14 | "every endpoint is an atom (distance ≤0.003)" | L3121 | `t2_filtered.json` | max 0.0032 | LOW |
| N15 | "√(5/4)≈1.12 … widen each interval by about 11%" | L3213 | arithmetic | 11.8% → "about 12%" | LOW |
| N16 | "the prediction itself stops 4.6× above the sampling floor in W₂" | L4190–4191 | `posterior_reference_scales.csv` | prediction 0.333/0.075 = 4.4×; 4.6× is the *measured* curve (in MMD the 14× quoted *is* the prediction) | LOW |
| N17 | "integrated through six checkpoints of one run" | L3189 | `scripts/make_flow_portraits.py:327` | five (100, 1k, 10k, 30k, 200k); caption's (a–e) agrees with five | LOW |

### 1.3 Stale values elsewhere in the repo

- `results/RESULTS.md` (Table "Scaling") still carries the **pre-Sinkhorn-fix** OT columns
  (3.33, 16.75, 60.41 …, gains 1.17–1.57×). The paper's Table 10 OT columns (0.08 … 12.72)
  exist in no saved file.

### 1.4 Untraceable to a saved output (not necessarily wrong)

| Claim | Location | Status |
|---|---|---|
| MNIST three-seed 0.137±0.021 → (1.17±0.12)×10⁻³, NN (0.77±0.26)×10⁻³ | L482–484, L4598 | only in `RESULTS.md`; `exp3_mnist_seed1/2` have figures but no raw metrics |
| small-U-Net CIFAR 0.142 → 0.0087; NN distance 0.0040 | L485, L4614 | only in `RESULTS.md` |
| Ablation table (whole table) | L3607–3633 | no generating script; computed by hand in `RESULTS.md` |
| Table 10 OT columns and gains; floor F per row | L3725–3730 | `atomicity_scaling.py` prints to stdout only; not rerun (torch blocked) |
| 96% of paths on the atom; trace 1.19→…→0.13 and 72→3 atoms; factorisation n_eff 29.1/5.5; portrait ratios 1.24/1.09/1.12; expansion-figure 2.5%/7.7%/−0.48/6%/n_eff≈37; survival 1.9–27×, prefactor 23.9→26.0; CFG identity to six decimals | Figs 1, 15, 17, 18, 20, App C | computed inside figure/verify scripts; no saved output |
| 35.75M parameters | L65, L494 | not logged anywhere; consistent with the standard DDPM CIFAR U-Net (35.7M) |

---

## 2. Code–paper mismatches

### 2.1 HIGH — CIFAR evaluation protocol (Table 6, §4.2 h=0 paragraph)

- §4.2 states "evaluating 48 conditions at M=256 samples each" (L495). App C.3 states the M=16
  training log has 36% per-condition error, "which is why every reported value is re-measured
  from checkpoints" (L3214–3216).
- But the h=0 headline (179.1 → 0.431, factor 415; three instances 0.409–0.467) and **all of
  Table 6** (raw traces, aggregate ratios, n_eff ranges, spreads) come from `raw/metrics.csv`.
  That is the in-training evaluator, with `n_conditions: 8, M: 16`.
- On the one instance where both exist (seed 0), the two protocols disagree:

  | h | training log (8 cond, M=16) | re-eval (48 cond, M=256) | gap |
  |---|---|---|---|
  | 4 | 2.255 | 2.154 | 4.7% |
  | 5 | **1.245** | **1.461** | **15%** |
  | 6 | 1.181 | 1.202 | 1.7% |

- That gap is the same size as the instance spreads Table 6 interprets (23–30%). It also undoes
  the L3462–3464 argument that h=5 seeds "land on 1.245 and 1.248, and only the third at 1.654
  shows that agreement to be a coincidence": re-measured, seed 0 is 1.461.
- **Fix:** re-evaluate the nine seed runs with `scripts/reeval_exp3_cifar_ddpm.py --M 256
  --n-conditions 48` and rebuild Table 6 and its prose from that. If the checkpoints are gone,
  label Table 6 and the h=0 numbers as training-log estimates (8 conditions, M=16), use 0.458 in
  §4.2, and drop the "1.245/1.248" argument. Also delete "every reported value is re-measured".

### 2.2 MEDIUM — the paper's own estimator rule is broken by Table 13

- The audit box says "Never average per-condition ratios" (L3161–3162).
- Table 13's tr Cov/tr Cov_h row (1.649 → 1.004) is the seed-median of `ratio_to_kernel_mean`.
  That column is the **mean of per-condition ratios** (`src/train.py:117`).
- The aggregate ratio the paper recommends reads 1.045, 1.036, 0.991, 0.990, 0.996 at the same
  iterations, i.e. ≈1 from iteration 100. The reason is that Σ_post ≈ Cov_h at h=0.1, so an
  early calibrated sampler already matches.
- "The covariance reaches the kernel optimum early … 1.65 → 1.00 by 10⁵" (L4232) is therefore
  a statement about the estimator. The seed-4 outlier (2.85) is the pathology the rule warns
  about.
- **Fix:** report the aggregate (and the median per-condition ratio) and reword. If the intent
  is per-condition tracking, say that and cite β instead.

### 2.3 MEDIUM — Table 5 footnote mislabels its own estimator

- L4403–4406 and L3343–3345 attribute 1.308±0.376 at h=0.01 to "the per-condition ratio".
- In `scripts/analyze_p7_kernel.py:89`, each seed's value is already a ratio of mean traces
  (tm/tk), and 1.308 is the mean of those over seeds. The instability is across seeds: seed 0
  has n_eff = 1.0 at h=0.01 (`kernel_verification.csv`).
- **Fix:** "the per-seed ratio is unstable because one seed's reference is near-degenerate;
  pooling the traces across seeds gives 0.673/0.583 = 1.15."

### 2.4 MEDIUM — "F … computed in closed form and so free of any estimator"

- Table 10's caption (L3733–3734), L3710 ("compute the floor … exactly") and L3365 ("directly
  computable") say F is exact.
- `scripts/atomicity_scaling.py:72` computes F as a Monte Carlo mean over 800 posterior draws
  at 6 conditions.
- **Fix:** "estimated by Monte Carlo over 800 posterior draws (no generative-model estimator
  involved)".

### 2.5 HIGH — the mask

- L496–498 ("three independently redrawn instances, which vary the mask, training subset, and
  training randomness") and L3453–3455 ("each redrawing the mask") are wrong.
- `src/problems/inpainting.py:70–72` fixes `mask[:, :16, :] = 1` for `bottom_half`. The seed
  changes only the `randperm` training subset and the training randomness.
- This also contradicts Limitations L673 ("one mask").
- **Fix:** "vary the training subset and the training randomness (the mask is the bottom half
  throughout)".

### 2.6 Verified matches

- h_eff and h_mean estimators match Eq. (6): squared log-trace loss; sum of unsquared mean
  norms; log grid; percentile bootstrap over conditions (`scripts/test_heff_synthetic.py:104–121`).
- The on-atom test is d₁² ≤ d₂²/9 (`src/metrics/memorization.py`).
- Label noise y + hε and endpoint noise x¹ + ρξ are redrawn per batch (`src/flows/cfm.py:71–82`).
- The interpolant uses γ = σ√(t(1−t)) with the pathwise target and the same Z
  (`src/flows/interpolants.py:68–72`).
- The EXP-1 setup (d=2, k=1, N=200, σ=0.1, width 128, depth 4, Adam 1e-3, batch 256, RK4,
  100 steps, ε=1e-3, M=1000, 20 + 8 conditions) matches `configs/exp1_linear_gaussian.yaml`.
- The CIFAR training settings (N=2000, batch 128, 60k iterations, bottom half) match
  `configs/exp3_cifar_ddpm.yaml`.

---

## 3. Formula and claim checks

- **Theorem `thm:calib`(b)** is correct. Pinsker gives TV² ≤ (k/4)(log(1+u) − u/(1+u)) ≤ ku²/8.
- **Proposition `prop:moments`** is correct: p = (0.531, 0.469, 2×10⁻⁶) and tr Cov = 24.90 at
  h=2; 200/9 = 22.22 as h → ∞.
- **Corollary `cor:floor`** (the ∫(1−Ls)² = 1/(3L) integral), **`prop:survival`(a,c)** (the
  ∫(1−s)⁻² and closed forms) and **`prop:nwrate`** (c₁ = ¼μ₂²|b|²; leading LG bias
  −h²BΣ_Y⁻¹y = (h²/2)b) are all correct.
- The **mis-specified interpolant endpoint x^i + σ^{2/(1−σ²)}X₀** is correct (integrating
  −u/(1−(1−σ²)t) from 0 to 1).
- **β at h=6 "never leaves zero" / "stays at zero" (L3437, L3502–3504) — MEDIUM.**
  `beta_trajectory.json` gives −0.362±0.133 at 20k and −0.202±0.062 at 60k (M=96), and Table 4
  gives −0.156±0.058 at M=256: 2.7–3.3 SE below zero. The audit box itself says "the slope has
  the wrong sign". Fix: "stays at or below zero, with no positive tracking".
- **√(2/(M−1)) as "the" relative error of a trace estimate (L3214) — LOW.** It is exact only
  for a rank-one covariance. For a d=3072 image covariance it is an upper bound.
- **Lemma `lem:nonintersect`(a) proof — LOW.** It ends "A union bound over pairs finishes (a)",
  but (a) is stated for a fixed pair, so the step is not needed.

---

## 4. Terminology consistency

| Term | Meanings | Locations | Severity |
|---|---|---|---|
| h^⋆ | (i) NW MSE-optimal rate N^{−1/(k+4)}; (ii) the true bandwidth in the identifiability bound; (iii) the bandwidth with tr Cov_h = tr Σ_post (=0.703 for one condition, while the text says Σ_post ≈ Cov_h at h≈0.1 on average) | L1451; L538–541; L187, L2516, L4343 | MEDIUM |
| β | across-condition slope **and** kernel-spectrum exponent \|ω\|^{−β}, in adjacent sentences | L619–631, L3061 | MEDIUM |
| "ratio-to-kernel" | mean of per-condition ratios (EXP-1 log, Table 13); per-seed aggregate averaged over seeds (Table 5); median per-condition (CIFAR Table 4); aggregate (CIFAR Table 6) | §2.2–2.3 | MEDIUM (folded into §2.2/2.3) |
| κ | identifiability slope (`prop:heffid`) and exp(ε²/2h²) (`prop:nearduplicate`) | L540, L1615 | LOW |
| σ, M | σ: interpolant noise and label-noise scale in Thm `thm:calib`. M: samples per condition, max\|x^i\| (Lemma `lem:wellposed`), Σ_h^{−1/2}Γ_h (proof of `thm:calib`), Buchanan's capacity | various | LOW |

---

## 5. Citation issues

Authors, titles and venues were checked against arXiv, conference pages and MLAnthology.
All four 2026 preprints exist with the stated authors and IDs: `physicscfm2026` (2603.14135),
`smola2026support` (2605.13386), `li2026memory` (2606.08554) and `briq2026tracing`
(2608.30081). The claims attributed to them match their abstracts.

| Key | Issue | Fix | Severity |
|---|---|---|---|
| `pfrommer2025conditional` | author list "Pfrommer, Daniel and others"; preprint only | Pfrommer, Dou, Scarvelis, Simchowitz, Jadbabaie, "Is Your Diffusion Model Actually Denoising?", NeurIPS 2025 (arXiv 2512.18736 is titled "…Conditional…") | MEDIUM |
| `buchanan2025edge` | cited as arXiv preprint | NeurIPS 2025 | MEDIUM |
| `biroli2024dynamical` | cited as arXiv preprint | Nature Communications 15 (2024), doi:10.1038/s41467-024-54281-3 | MEDIUM |
| `albergo2023stochastic` | cited as arXiv preprint | JMLR 26(209):1–80 (2025) | MEDIUM |
| `kamb2024creativity` | `@article` arXiv with `note = ICML 2025` | `@inproceedings`, ICML 2025, PMLR 267:28795–28831 | LOW |
| `gradvar2025`, `bertrand2025closed`, `chen2026scoresmoothing`, `gu2023memorization` (TMLR 2025), `scarvelis2025closedform` (TMLR 2025), `yoon2023memorization` (ICML 2023 SPIGM workshop), `gao2024flow` (arXiv only) | verified | optional: add arXiv IDs (gradvar: 2510.18118) | — |
| `yoon2023memorization` | the "1/3 of the second-nearest distance" criterion attributed to it, "as used by Buchanan et al. at their default" | not confirmed from abstracts; check the definition section of both papers | LOW |

Other references (classics and textbooks; ICLR/NeurIPS/CVPR/USENIX 2022–2024 entries) were
checked against known venues with no discrepancy, but were not looked up individually.

---

## 6. Suggested text fixes

1. L496–498: "…on three independently redrawn instances, which vary the training subset and
   the training randomness together (the mask is the bottom half throughout)". Same at
   L3453–3455.
2. L500–503: either quote the M=256 re-evaluation (0.458) or add "(training-time estimator, 8
   conditions at M=16)". At L3214–3216, delete "which is why every reported value is re-measured
   from checkpoints" unless Table 6 is regenerated.
3. Table 6 caption: add the estimator. At L3461–3464, drop the 1.245/1.248 coincidence argument
   unless re-evaluated.
4. L4499–4501: "At h=0.5 the generated variance 1.29 overshoots Σ_post = 1.02 and tracks the
   finite-N reference tr Cov_h = 1.28 (Theorem `thm:endpoint`); the N→∞ term h²‖J‖²_F
   (0.38–4.46 across seeds) accounts for part of it."
5. L3209–3211: "Every across-seed ± is a population standard deviation except Tables
   `tab:ablation` and `tab:nsweep3`…". Better: recompute the ablation with ddof=0 (0.041,
   0.041, 0.056, 0.110, 0.090, 0.136) and the N-sweep with ddof=0.
6. Table 10 caption: "F … estimated by Monte Carlo (800 posterior draws per condition)"; "by
   1.8 to 3.0× in higher dimension". Reconsider "below resolution at every row" for d=2,
   N∈{50, 200}, or show the absolute gains.
7. L4232 and Table 13: report the aggregate ratio (≈1.04 → 1.00) alongside, and say what the
   mean-of-ratios row is for.
8. L4403–4406: replace "per-condition ratio" with "per-seed ratio" (§2.3).
9. L3437, L3502–3504: "β stays at or below zero (−0.20±0.06 at 60k)".
10. L3391, L3791: "to within 3.1% on average (6% for one seed)". At L3766–3768, drop "per seed
    as well as on average".
11. L3885–3888: "comparable to the between-seed std (0.11–0.15 in ratio units)".
12. L3354 and L4496: "1.9–4.8×".
13. L3804–3805: "within a factor of ~3.5".
14. Low items N10–N17 as listed in §1.2.
15. (LOW) L203: `proof_checks/` does not exist in the repo (the material is in `docs/audit/`); point
    to the directory the supplement will actually contain.

## Reproduce

```bash
uv run python scripts/verify_paper_numbers.py
uv run python docs/review/paper_verification_2026-10-10_checks.py
```
