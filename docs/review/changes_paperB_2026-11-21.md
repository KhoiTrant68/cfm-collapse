# Paper B (`paper_mechanism/`): corrections of 2026-11-21 (editor label edit-B)

Files changed: `paper_mechanism/main.tex`, `paper_mechanism/refs.bib`, `paper_mechanism/README.md`,
`paper_mechanism/figures/fig_teaser.pdf` (redrawn), `paper_mechanism/figures/fig_posterior_choice.pdf`
(new; a copy of `results/paperB_20261121/collapse_sigma/fig_collapse_vs_choice.pdf`),
`scripts/make_paperB_figures_v2.py` (teaser only), `paper_mechanism/main.pdf` (recompiled).
Nothing of the other session was edited (`scripts/paperB_*.py`, `results/paperB_20261121/`,
`logs_paperB/`, `docs/plan/paperB_*.md` were only read). Nothing was committed.

Sources. "V:item" = `docs/review/memo_verification_2026-11-21.json`, item and edit/discrepancy
number; "M5.n" = Section 5 (errata) of `docs/plan/paperB_findings_2026-11-21.md`, which supersedes
its Sections 1-3; "M4" = its Section 4 (E1). "Recomputed" = recomputed by this editor from the
per-sample files with `uv run --no-project python` (numpy), in addition to the verifiers.

## 1. Net-to-exact landing is structural (V:1.1-structural-landing, V:1.1-refute; M5.6, M5.7, M5.14, M5.40)

The last Heun step is an Euler step to sigma = 0, so the output is D(x; 0.002), which for the exact
field is the nearest training image of the class. Recomputed: net-to-exact is off-atom for 0/500 at
every s on all three models, largest d1 7.07e-6 (public) and 1.51e-6 (1000- and 500-image).

| Where | Change |
|---|---|
| Abstract | "Handed the network's state at any noise level, the exact field lands every sample ..." replaced by "Handed the network's state at sigma <= 1, the exact field ends on the training image nearest to the network's own endpoint in at least 88% of samples" (V:1.1-structural-landing e0). Added the measured landing clock: "on the public model, half of the samples land only for a swap at sigma ~ 0.5" (s_land = 0.51 [0.47, 0.54], `swap_clocks.json`). |
| Intro, "Two decisions" | "Which training image a trajectory heads for" replaced by the basin reading ("which training image the exact field would reach from a trajectory's state") (V e1). |
| Contribution 3 | Net-to-exact "ends on a training image by construction ...; what it measures is which image" (V e2); novelty sentence rewritten (Section 8 below). |
| Related work, Bertrand paragraph | Removed "copies for every sample once the exact field replaces it on the last 2%"; TODO resolved (V:3-positioning e1). |
| Related work, Hybrid samplers | Rewritten with exact-to-net evidence (95.6% off at s = 1, half landed at s = 0.5) instead of the net-to-exact inference (V:3-positioning e3, V:1.1 e4). |
| `fig:swap`, `tab:swap` captions | "by construction"; every (not only the median) net-to-exact endpoint is within 1e-5 (V e5, e6). |
| Sec. 5.3 "The image is chosen early" | The "last 2% turns no memorisation into complete memorisation" sentence replaced by the explanation (Euler step, double precision, tie exception, "would" for the last of the 35 evaluations) (V e7, V:1.1-refute e5, M5.40). Added the basin reading of =L (median learned d1/d2 0.977 and 0.949; 379/431 = 87.9% vs 11/431 = 2.6% at s = 1) (V e8, recomputed) and the clock (=L 50% at 2.48 [2.13, 2.87], 90% at 0.95 [0.74, 1.05]). |
| Sec. 5.3 "Whether it is reached is decided late" | "Landing is a property of the field that runs last. The exact field lands from whatever state ..." replaced (V e9; M5.7). |
| Sec. 5.3 "Reading" | False clause "handed the same exact state, the memorising network lands and the two others do not" replaced: at s = 2 the 500-, 1000-image and public models land 100%, 12%, 0%; at s = 1 the 1000-image model lands 77% (public 4%) although it lands none of its own samples (V e10; M5.7; recomputed: 0.118, 0.768, 0.044). |
| Sec. 5.4 "Not a better detector", last sentence | "the exact-to-net swaps ..., which change only the field below the switch, are what tie landing to the late field causally" (V e11). |
| Planned experiment (i) | Window must hand the state back to the network; first run on the public model reported (V e12). |
| Conclusion | "the exact field run on the last 2% ... turns a model that never copies into one that always does" replaced by the basin statement (>= 88% at sigma ~ 1) and exact-to-net evidence (96% off at sigma = 1) (V e13). |
| Broader impact | Removed the "exact field substituted on the last noise levels turns a model that does not copy into one that does" clause (V e14; M5.6). |
| Appendix D, Swap protocol | Largest d1 7.1e-6; why it holds (off-atom only if the two smallest squared distances differ by at most 2 sigma^2 ln 3 = 8.8e-6, V:1.1-refute (3)); net-to-exact off-atom fraction carries no information, =L does (V e15). Clock interpolation and bootstrap stated (`paperB_swap.py`, 4000 resamples). |

## 2. "Two times" and E7 (V:1.2-two-times-biroli; M5.1-M5.5, M5.8, M5.9, M5.10, M5.33-M5.36)

- "Two times" rewritten: Biroli et al. define speciation (commitment to a class) and collapse (into
  the attractor of one training point, then reached); they also measure both times on trained
  networks (collapse on DDPM U-Nets with 200 or 2000 images). Our first decision corresponds to the
  collapse, not the speciation. Raya and Ambrogioni narrowed to the first transition (V:1.2 d7),
  Li and Chen (`li2024critical`) added.
- E7 claim limited to the public model (M5.1, M5.5): "on the public model it is made in the range of
  noise levels where the exact posterior ..., evaluated at noised test images, concentrates on one
  image". No E7 claim in the abstract (task item 2, M5.1).
- Decision: E7 goes to Appendix D ("Choice and the exact posterior"), not to Sec. 5.3: it holds only
  for the public model at nominal swap levels, and the main text is already long. The paragraph
  follows V:1.2 e1 with the M5 corrections: nominal vs effective levels (2.8 and 0.76, M5.3), the
  1000-image 90% point 0.82 [0.65, 1.02] below its range [1.2, 6.4] (M5.10), the 500-image model only
  compared at sigma = 5 (93% vs 94% retrieval vs 79% fresh, M5.2), x^j notation (M5.33), "operational
  counterpart" of Biroli's collapse (M5.4; Biroli evaluate an excess entropy at noised training
  points, V:1.2 d3), protocol (81 levels, one draw per test image, 200 training points per class,
  class averages, log-sigma interpolation; V:1.2 e4, checked in `paperB_collapse_sigma.py`).
- Figure `fig:posterior` (`figures/fig_posterior_choice.pdf`, copy) with the caption of M5.8 and
  "swap levels s, drawn at sigma = s" (M5.35).
- Numbers checked in `collapse_sigma/summary.json` (3.821/1.991/0.784; 6.389/3.296/1.219;
  7.520/3.818/1.441; shares at sigma = 1, 0.5: 0.845, 0.956 for >= 0.9; sub1000 at 2/1/0.5: 0.747,
  0.933, 0.982; sub500 at 5: 0.789 fresh, 0.936 retrieval) and `swap_clocks.json`. E7 itself was
  recomputed independently by the V:1.2 verifier (answers M5.9).

## 3. Bookkeeping AUC and contribution 4 (V:1.3-bookkeeping-auc; M5.12, M5.13, M5.32)

- dD at sigma = 0.002 equals d1 for every sample (recomputed: max |dD17 - d1| = 0 on all three
  trained models), so "ties the baseline (0.983 against 0.985)" compared C with d1 itself.
- "Not a better detector": replaced by the bookkeeping explanation (Prop. heun(a)), the comparison at
  sigma = 0.585 (0.990 against 0.983, paired difference [0.004, 0.010]), R^2 of log d1 (0.991 vs
  0.976 pooled, 0.965 vs 0.883 on-atom), earlier AUCs (0.909, 0.962, 0.988 at sigma = 3.26, 1.92,
  1.09) (V e0; source `certificate/CERTIFICATE_TABLES.md` l.189 and Section 4, `incremental.json`).
  The threshold sentence is kept, placed after the AUC comparison (V:1.3 summary (7), d8).
- Added the incremental result (cross-validated logistic regression, balanced model: relative error
  adds |dAUC| <= 0.002 from sigma <= 1.9; late contraction <= 0.002; `incremental.json`, recomputed
  from it) and removed planned experiment (iv), which is done (V:1.3 d10).
- Contribution 4 retitled "The late contraction carries out landing", with "median 1.75 against
  0.68" (M5.32), "endpoint's nearest training image" (V:1.3 d5), AUC 0.990 vs 0.983, "not as a
  detector" (V e1). The radial correlation is not quoted in the bullet; the body states it as an
  identity check (V:1.3 d4): "Part (a) is an identity of the flow, and the sampler follows it ...
  correlation at least 0.993 ..., at least 0.97 within the on-atom samples of the 500-image models,
  ... falls short ... by a median of 0.02 to 0.04" (V e2; recomputed from `radial/late_*.npz`:
  0.9933/0.9966/0.99997/0.99999; on-atom 0.973/0.986; medians -0.024 to -0.043).
- Abstract last sentence, Conclusion, Implications ("does not detect memorisation better", not
  "cheaper"), Appendix D "Second seed" paragraph, `tab:edm-models` (new column "baseline, sigma =
  0.585": 1.000/1.000/0.990, recomputed 0.99995/1.0/0.99024; caption says the 0.002 column is
  bookkeeping), subsection title and `fig:landing` caption ("carries out landing"; "0.983 with either
  anchor") (V e3-e9).

## 4. CIFAR slope (V:1.4-cifar-slope; M5.15, M5.16)

- Sec. 5.1: h = 4 slope 0.36, 95% t-interval [0.22, 0.51] over the three retrained instances, 0.48
  in the original run on the first instance; h = 6 not determined (retrained 0.08, 0.41, 0.60;
  original -0.16; reference spans 0.74-1.89 decades); "38%" attributed to the original run
  (V e0). Consistent with the existing `fig:collapse` caption (slopes 0.32, 0.34, 0.43; h = 6 not
  determined).
- `tab:cifarddpm` rebuilt (HC3 s.e. 0.039/0.142/0.108, OLS in the caption; retrained slopes and mean
  with t-interval; CV column dropped) (V e2). Appendix E.2: only the first instance was re-measured
  at M = 256; slopes of all three from the retrained networks; on-atom fractions are the first
  instance's (V e3, e4). All values checked in `uncertainty/cifar_slopes.json`.

## 5. Other numbers (V:1.5-1.8-misc; M5.17-M5.21, M5.27, M5.39)

- Transfer, Sec. 5.1: "AUC 0.97 and 0.95 at h = 4 and 6 by t ~ 0.53 and 0.99 and 0.98 by t ~ 0.63,
  while the same network along the exact trajectory ... separates them weakly if at all (AUC at most
  0.58 from t ~ 0.63 on)" (V e4, with the time range of V d0). Appendix C: cluster intervals 0.970
  [0.961, 0.978], 0.951 [0.942, 0.959] (V e9); unverifiable "m* is a posterior mean over many
  training images" removed (M5.17); exact-path sentence rewritten (every interval contains 0.5 at
  h = 4, above 0.5 at h = 6; early AUCs 0.77/0.61 vs 0.76/0.59) (V e10); "monitoring rule" -> endpoint
  rule on d1 (M5.17); 0.168 +- 0.010 and 0.276 +- 0.006 (population SD, the stated convention)
  (V e8). Checked in `transfer/TRANSFER_SUMMARY.md`, `auc_vs_t.csv`.
- EXP-1: t-intervals (df = 4) in Sec. 5.1, `tab:exp1`, `tab:p7kernel`; the crossing of the two
  distances "between 1e5 and 2e5" with paired differences -0.28 [-0.57, 0.01] (one seed not
  crossed) and -0.68 [-0.94, -0.42]; paired contrasts in the `tab:exp1` caption, the cosine contrast
  labelled as a change of both schedule and length (M5.18); h = 0.01 "uninformative" (per seed 0.92
  to 1.96); Setup and Appendix E conventions (bracket = t-interval, half-width 1.39 population SD;
  +- = population SD) (V e0-e3, e14-e19). Checked in `uncertainty/stdout.txt` and `tables.tex`.
- Hypothesis (b) (Sec. 5.4): no longer "fails"; 34/41 off-atom and 195/200 public samples keep
  rho < 1 at every level of [0.002, 0.585]; "(b) uses" instead of "(b) and (c) use" (V e7; M5.19,
  M5.27; checked in `radial/radial_numbers.json`).
- Sec. 5.3 small claims: proportionality only from s = 0.1 to 0.02 (slopes 0.90 public, 0.84
  1000-image, 0.47 from 5 to 0.5), "partly because little time is left", weak contraction by a factor
  of about 1.4 to 3 (estimate; hand-over distance not recorded), "close to the boundary case" (V e6;
  M5.20; checked in `verify_swap/verify_swap_report.txt`). Matched-threshold clocks added (public 50%:
  2.48 vs 0.51, 90%: 0.95 vs 0.21; 1000-image 4.74 vs 1.33, 0.82 vs 0.56).
- n of the swaps: Appendix D now says "unless stated otherwise ... the swap runs use 50 per class on
  every model" (V e11; M5.21). 1000-image subset class-balanced (100 per class) in Sec. 5.2 and
  Appendix D; TODO removed (V e5, e12; M5.39; inferred from `make_edm_cifar_subset.py` and the swap
  data, the indices file is not in the repo).
- Rounding in the swap protocol: 6.45, 10.73, 3.94 (V e13; `swap_summary.json` 6.4545, 10.7348,
  3.9447).

## 6. Teaser (`fig:intuition`, `fig_teaser.pdf`)

- Old: "landing decided" at sigma = 0.14 from the public model's median rho passing 0.9, "image
  chosen" at s = 1, and rho curves. New: both clocks from the swaps, same threshold: choice =
  share of net-to-exact endpoints on the network's own image (=L), landing = share of exact-to-net
  endpoints on a training image; public model thick, 500-image model thin; dotted lines where the
  public curves pass 1/2, interpolated in log s (s = 2.48 and 0.51; the script asserts agreement with
  `swap_clocks.json` s_sel50 and s_land). The rho curves are dropped (they are in Figure 5).
- `scripts/make_paperB_figures_v2.py`: `fig_teaser` bottom panel and docstrings only; redrawn on
  lab09 (`PYTHONPATH=.:scripts python scripts/make_paperB_figures_v2.py teaser`) and inspected at
  130 and 300 dpi. Caption rewritten to state both definitions and the 500-image values (93% chosen
  at s = 5, lands from every level).

## 7. E1 window swaps (M4; `results/paperB_20261121/window_swap_public/`)

- New paragraph "A window of exact field" in Sec. 5.3, new Appendix D paragraph "Window swaps" and
  Table `tab:window` (all 18 runs). Reported: P1.1 holds for sigma_lo <= 0.2 (k = 30.3, 27.5, 25.7,
  21.1) but not at 0.5 and 1 (12.9, 9.2), and these windows reproduce the exact-to-net runs; P1.2
  refuted ((0.1, 0.5] 4.16 vs (0.1, 2] 2.48, ratio 0.60 [0.58, 0.61]); (0.1, 0.5] leaves 21.4%
  [18.0, 25.2] off-atom vs 0.2% for (0.1, inf); the chosen image is set by sigma_hi (=L 0.956, 0.896,
  0.560, 0.306 equal to net-to-exact at hi; same image for >= 99.6% of samples); from sigma_hi >= 2
  the final d1 depends on sigma_lo alone (1.33, 1.33, 1.37).
- Every number recomputed from `window_per_sample.npz` (shares, Wilson intervals, medians, k, ratios).
  The windows (lo, inf) and (0, hi] reproduce the old swap runs sample by sample (same nearest images,
  same off-atom flags, medians within 5e-4). Note: `WINDOW_ANALYSIS.md` labels the old runs "other
  latents"; the labels, learned nearest images and d1 agree, so they are the same latents (as M4 says).

## 8. Bibliography and positioning (V:3-bib-metadata paper-B keys, V:3-positioning; M5.29-M5.31, M5.41-M5.43)

- Contribution 3 novelty: earlier hybrids ran the exact field first (Bertrand et al., Liu et al.) or
  exchanged two trained networks (Dodson et al.); we add network first / exact field late and record
  which image apart from whether it lands (V:3-positioning e0, d2). README's overlap note updated.
- Related work: Hybrid samplers (Bertrand tau >= 0.3 / 0.4; Liu; Dodson [0.14, 8.4], 92.2% <-> 0%);
  Late landing (Li et al. Table 4: damping alone 37.3% -> 30.2% at FID 16.7 -> 35.0, early boost alone
  36.8-37.4%, both 31.2% at FID 14.4; M5.29; no sigma conversion, V:3-positioning d5); Favero et al.
  finding corrected (V d9); new paragraph "Where memorisation arises" (Kaiser and Kollmann: gap
  largest at intermediate noise, overfitting rather than copying; Dodson sigma in [1, 5] excluded:
  78.8% -> 0.7%; Shah et al. Pareto switch levels [0.4, 4] on FFHQ-300, M5.31; Kim et al. under
  Bayes-optimal predictions; Jain et al. "reduces", not "avoids"). Dodson TODO in Sec. 5.3 resolved
  (V e5). Implications: interventions can act at either stage (V e6). exact-to-net attributed to
  Bertrand et al. and Liu et al. in Sec. 5.3 (V e7).
- `refs.bib`: added `shah2025ambient` (PMLR 267, "Adam Klivans", braced {C}reative),
  `li2024critical` (PMLR 235), `kaiser2026structural` (@article with version in note/url, since
  tmlr.bst ignores eprint); updated `biroli2024dynamical` (pages 9957), `sesmat2026leaks` (PMLR 306),
  `jain2025attraction` (CVPR pages, DOI), `beltran2026reward` (NeurIPS 2026, "Xiaofeng Zhang"),
  `dodson2026calm` (@inproceedings, PMLR 306), `liu2025navigation` (CVPR 2026 Findings, pp.
  2649-2658; prints "Liu et al. (2026)"), `li2026kinetic` (PMLR 306, no hyphen), `favero2025bigger`
  (year 2026, key kept), `kim2025how` (v2), `physicscfm2026` (pinned to v3; not cited in paper B).
- physicscfm2026 "return training examples": no such sentence in paper B (M5.30, V:3-bib d5); the
  Broader-impact sentence of paper B is about paper B and is unchanged.

## 9. Reproducibility statement and README

- Names `make_paperB_figures_v2.py` (Figures 1, 2, 3, 5, 8), `make_swap_figure.py` (Figure 4),
  `make_collapse_choice_figure.py` (Figure 6), `make_paperB_figures.py` (other appendix figures),
  `paperB_window_swap.py` and `paperB_window_analysis.py` (E1), `paperB_collapse_sigma.py` (E7), and
  `paperB_swap.py`, `paperB_uncertainty.py`, `paperB_transfer.py`, `paperB_radial.py`,
  `paperB_certificate.py`, `paperB_incremental.py`.
- README: story (basin reading), contents, numbers and their files, "Done (third pass)", "Not yet
  done" updated.

## Not applied (and why)

- V:1.4 e1 (caption of `fig:kernel-tracking`): that figure is no longer in paper B; `fig:collapse`
  (c) already shows the retrained slopes and calls h = 6 undetermined.
- V:1.2 e1 as a Sec. 5.3 paragraph: moved to Appendix D (decision above); Sec. 5.3 keeps no E7
  paragraph, related work points to the appendix.
- Memo 1.1 proposed abstract (E7 band, general): rejected (M5.1, task item 2).
- Memo 2.2 LaTeX and caption: replaced by the corrected versions (M5.2-M5.5, M5.8, M5.10, M5.33-36).
- Memo 1.5 "AUC at most 0.58" without a time range, and memo 1.8 "below s = 0.2": false as worded
  (V:1.5-1.8 d0, d8); used "from t ~ 0.63 on" and "from s = 0.1 to 0.02".
- Radial correlation in contribution 4 (V:1.3 e1): kept out of the bullet, stated in the body as an
  identity check (V:1.3 d4).
- `li2026kinetic` hyphenated title (memo 3): PMLR and arXiv have no hyphen (V:3-bib d0).
- @misc `kaiser2026structural` and "Proceedings of the 41st/42nd ICML" booktitles (V:3-positioning
  bib): house style and tmlr.bst fields used instead (V:3-bib d2, d3).
- Renaming `favero2025bigger` (M5.43): key kept.
- Paper A bibliography edits of V:3-bib (e9-e13) and items 1.9: outside this editor's files.
- Li et al. "boosting the velocity before t = 0.6": the boost interval was not verified; written as
  "an early boost".
- Memo 2.4-2.6 (certificate, Heun chain, early-warning rule, AUC = 1.000 bounds): not added; not
  required by the items.

## Compile

tectonic on lab09 (`bash scripts/build_papers.sh paper_mechanism`): rc 0, 34 pages (29 before), no
undefined references or citations, no overfull boxes; two underfull lines in the reproducibility
statement (long file names). The main text now ends on p. 15 (p. 12 before). Pages 1-4, 8-15, 26-28,
31, 32 and 34 were rendered at 100 dpi and checked.

---

# Second pass: review findings (editor label fix-B, 2026-11-21)

Files changed: `paper_mechanism/main.tex`, `paper_mechanism/refs.bib`, `paper_mechanism/README.md`,
`paper_mechanism/figures/fig_swap.pdf` and `fig_teaser.pdf` (redrawn on lab09; `fig_swap.json`
unchanged), `scripts/make_swap_figure.py` and `scripts/make_paperB_figures_v2.py` (one label each),
new `scripts/threshold_auc_r2.py` and `results/threshold_auc_r2_20261121/` (`threshold_auc_r2.json`,
`run.log`), `paper_mechanism/main.pdf` (recompiled). Nothing of the other session was edited; nothing
was committed. "R1".."R34" number the 34 review findings in the order received. Each was checked
against the data, code or source before it was applied.

## Deduplication

R16 = R2 (off-atom thresholds sentence; R2's fuller wording used); R7 = R3 (window prediction P1.1;
merged); R29 = R17 (three arXiv entries; R29's entries used); R12 and R6 overlap R5 in the abstract,
contribution 3/4, Conclusion and Implications (merged into one wording per passage).

## Applied

| Finding | Where | Change | Checked against |
|---|---|---|---|
| R1 | Sec. 5.3 "Whether it is reached" | "factor of about 1.4 to 3" (two baselines mixed) -> "about 2 to 3, or about 1.4 to 2.2 if the exact field is credited with its half of the mixed Heun step at the hand-over"; the assumption now says "the state at the last level sigma of the exact field" | `verify_swap_report.txt` (3.01/2.42/2.10 vs Heun-aware 2.15/1.67/1.39); recomputed sigma_hi*sqrt(3072)/median d1 |
| R2+R16 | Sec. 5.4 "Not a better detector" | "These conclusions do not change for thresholds 0.2 and 0.5" -> AUC 0.987 vs 0.974, paired [0.008, 0.018] at 0.2; tie 0.990 vs 0.990, [-0.003, 0.003] at 0.5; on-atom R^2 0.903 vs 0.716 and 0.975 vs 0.934. Script named in the reproducibility statement | new `scripts/threshold_auc_r2.py` (the verifier's `check_auc_r2.py` with repo paths, plus R^2 by threshold), run on lab09; its output equals the verifier's `out.json` in all 1491 shared values |
| R3+R7 | Sec. 5.3 "A window of exact field"; Sec. 6 (i); App. D "Window swaps" | "registered" -> "written down"; P1.1 "restated the exact->net runs above, which the windows (lo, inf) repeat on the same latents and reproduce sample by sample, so it is not an independent test; ... so by its own criterion it fails"; P1.2 "the only new test"; (i) "refuted the one prediction that did not restate earlier runs"; App. D "(the first restates the exact->net runs of Table 1)" | recomputed: `window_per_sample.npz` vs `n3_followup_20261111/swap_public/swap_per_sample.npz`, 500/500 same image and off-atom flag at all six lo, medians within 5e-4; k = 30.3, 27.5, 25.7, 21.1, 12.9, 9.2; registration and its criterion in `docs/plan/paperB_gpu_experiments_2026-11-21.md` |
| R4 | `fig:swap` caption, panel (b) | caption: "Shaded: the swap levels s >= 1, over which the image is chosen, and s <= 0.2, from which at least 93% of the public model's samples land"; band label "image reached" -> "landed" | `make_swap_figure.py` (bands 6.25-1 and 0.2-0.016); landing 0.930 at s = 0.2 (`tab:swap`) |
| R5 | Intro; Related work (2 places); Sec. 5.3 heading and paragraph; Implications (2); Broader impact; teaser | "decided late" wording replaced: "stays open until late and depends on how strongly the learned field still contracts toward it from the state the trajectory has reached"; "stays open after the image is chosen"; "...where the contraction ... carries out landing from the state it is handed"; heading "Whether it is reached stays open until late."; new sentence on the 19 samples the 500-image model leaves off-atom (all land under exact->net at every s, even 5); Implications "A trained network's sample ends off the training set only if its late field fails to contract onto the image from the state it is handed, and the regression loss does not control that failure", "where landing is carried out"; Broader impact rewritten; teaser labels "image chosen"/"landing decided" -> "half chosen"/"half landed" | window table (0.1, 0.5]: 21.4% off vs (0.1, inf): 0.2%; `verify_swap_report.txt` "exact2net off-atom among the 19 learned off-atom samples, summed over all 8 s: 0" |
| R6 | Abstract; contribution 4; Conclusion; Implications; Limitations | prediction of landing placed at sigma ~ 1 "where the image is chosen" (AUC 0.988 at sigma = 1.09 and 0.990 at 0.585 on the 2000-image model); Limitations: the swaps leave out the 2000-image model | `CERTIFICATE_TABLES.md` and the threshold script (AUC of dD at 1.088: 0.9876) |
| R8 | Sec. 5.2; `tab:edm-rho` caption | added: the measurements apply Theorem relerr with Z = x and 1 - t = sigma/80, so n = abs(x - a), part (a) is sigma dn/dsigma = n - <e, D - a> and the contraction is int (1 - rho) dlog(1/sigma); caption "n_t = abs(x - a)" | `n3_directional_q.py` (n1 = abs(x - y1)); the change of variables checked by hand (both Z = tx and Z = x give the theorem's ODE; only Z = x gives the measured n and measure) |
| R9 | App. D "Choice and the exact posterior"; Related work "Two times"; `fig:posterior` caption | "at or near it" -> "at or near the concentration at noised test images, and later than that at noised training images, where the weight on the image is at least 1/2 for half of the points at sigma = 5.1 and for 90% at sigma = 3.4"; "in the range" -> "at or near the range"; caption "at noised test images" | `collapse_sigma/summary.json` full50k: sigma_retrieval_own_median_0.5 = 5.14; frac_own_ge_0.5 crosses 0.9 at 3.40 (recomputed, log-sigma interpolation) |
| R10 | Sec. 5.1; App. C (2 paragraphs) | 48/48 "in this run and in networks retrained on each of three independently redrawn instances"; EXP-C "reintegrates 60000-iteration checkpoints of networks retrained with the configuration of Section 5.1, whose original weights were not kept"; S10 "We retrained these networks once more" | `exp_c_cifar_transfer.py` docstring; `exp3/_cifar_ddpm/reeval.json` (original first instance, 48 conditions, nn_correct 1.0); `exp3/_rerun/seed_table.json` (retrained h = 0 seeds 0-2, 1.0); S10 vs EXP-C off-atom shares differ for the same run names |
| R11 | Sec. 4; Conclusion | "is decided by a weaker quantity" -> "is controlled by"; "landing is decided by the error relative to the distance" -> "a trajectory lands when its error stays a fixed fraction below its distance to the example" | Theorem relerr (b) is sufficient; remark after its proof |
| R12 | Abstract; contribution 3 | "ends off the training set unless the swap comes late" -> landing of half (contribution: half and 90%) of the samples needs a later swap level than the choice of the same share: public 0.5 vs 2.5; 1000-image 1.3 vs 4.7 | `swap_clocks.json` / `verify_swap_report.txt` matched thresholds (public 2.48/0.51, 0.95/0.21; 1000-image 4.74/1.33, 0.82/0.56) |
| R13 | Sec. 6 | "The following are in progress; apart from the first run of (i), they are not reported here." | |
| R14 | Related work "Late landing" | "the swaps measure where" -> "indicate where" | hand-over distance not recorded |
| R15 | Contribution 4 | "Theorem relerr(a) is an identity of the flow, which the sampler's trajectories follow up to discretisation"; "With 36 or 64 steps the Heun bound certifies contraction at every step for 99.5% of the on-atom samples of the 500-image model" | `tab:edm-steps` |
| R17+R29 | `refs.bib` | `verma2026early`, `lopezamado2026modes`, `jaziri2026spectral`: @misc with eprint -> @article with journal "arXiv preprint arXiv:...", same authors and titles; now print their identifiers | compiled reference list |
| R18 | Contribution 3 | "(Section 5.3, new)" -> "(Section 5.3)" | |
| R19 | App. D "Worst-direction contraction" | "... does, though at the last steps partly by bookkeeping (Section 5.4)" | Sec. 5.4 |
| R20 | `fig:intuition` caption | "which copies (bottom)" -> "(middle)" | rendered figure: public pair, 500-image pair, clocks |
| R21 | App. C | "what decides an off-atom endpoint" -> "what marks" | AUCs only |
| R22 | Sec. 5.3 "Reading" | "the swap levels over which exact->net goes from almost no to almost all samples on-atom, s = 2 to 0.1 on the public model and s = 5 to 0.2 on the 1000-image model, indicate ..." | `tab:swap` (public 0% at s = 2, 99.8% at 0.1; 1000-image 2.6% at 5, 99.0% at 0.2) |
| R23 | App. E.2 "Class labels" | "...remove the collapse onto one image; whether the completions stay on training images of the class is not measured here." | no nearest-image test in that run |
| R24 | `fig:collapse` caption | "follows it at h = 0.05, 0.1 and 0.5; at h = 0.01 the seeds disagree (ratio 0.92 to 1.96)" | `tab:p7kernel` |
| R25 | Conclusion | "the sampler-side knobs studied in the companion paper" -> "label noise, label averaging and guidance with a bounded schedule, studied in the companion paper"; next sentence "A trained sampler that uses them leaves ..." | `paper_theory/main.tex` abstract: the conjunction of compositional generation blends with positive probability |
| R26 | Related work, first paragraph; `refs.bib` | added Liu and Zuazua: liu2025pde Theorem 3.7 (v3, a.e. trajectory of the exact score ends on a training example) and liu2026geometric **Theorem 2.5 of version 2** (every trajectory of a two-score mixture or guidance with a constant weight converges to one of finitely many equilibria of a distance potential, which need not be a training example); the companion shows a null exceptional set for guidance. `liu2026geometric` bib entry updated to v2 (title, note, URL) | arXiv abs v2 (29 Oct 2026) and HTML of 2511.05940v3 checked; V:1.9-liu-v2 and V:1.9-refute; `paper_theory/main.tex` l.286 already cites v2 Thm 2.5 |
| R27 | Related work "Error bounds" | added Li, Lin and Yu, Theorems 4-5 (upper bound in terms of the training loss under a bounded density of the iterates w.r.t. the interpolant law, which implies the risk-transfer condition with K equal to the bound; lower bound on the mean-square deviation from the selected example under non-cancellation) and Pidstrigach, Theorem 2 (bounded score difference: still only training examples) | arXiv HTML 2606.08554v1 (Thm 4 bound is B_det + sqrt(Gamma A_h L_train / eta)); Pidstrigach PDF text, Theorem 2 |
| R28 | `refs.bib` `companionA` | title "Which Interventions Keep a Conditional Flow on Its Training Set?" | `paper_theory/main.tex` title |
| R30 | Related work "Hybrid samplers" | "a switch after t = 0.2 of their latent-space schedule (t = 0 at the prior) reproduces the layout of a training sample and an earlier one gives novel outputs" | arXiv HTML 2512.02826v3 Sec. 4.2 (t_switch in (0.2, 1.0] vs [0.0, 0.2]; t = 0 prior) |
| R31 | Related work "Hybrid samplers"; `refs.bib` | Cheng et al. (clipped empirical denoiser early, public network after, privacy loss of sampling) and Briq et al. (closed-form velocity at learned states, cluster attribution, no hybrid); new entry `cheng2026privacy` | arXiv abs 2610.27710 (Cheng, Kim, Park; v3 23 Oct 2026) and HTML 2608.30081v2 |
| R32 | Open questions | "a smoothed empirical score (Scarvelis et al.; Chen)" added | arXiv 2502.19499 (ICLR 2026) abstract |
| R33 | `refs.bib` `niedoba2024mechanistic` | @inproceedings ICML, PMLR 267, pp. 46389-46411, 2025 (key kept) | proceedings.mlr.press/v267/niedoba25a.html |
| R34 | `refs.bib` `somepalli2023diffusion` | "{I}nvestigating" | |

Also: `README.md` story line ("stays open until late") and two "Not yet done" items (hand-over factor;
threshold check now under `results/`).

## Applied with changes, or not applied

- R26: the finding asked to keep `liu2026geometric` pinned to v1 and cite v1's Theorem 3.18 ("converges
  to a local minimiser if the limit set contains no non-minimising critical point; the companion
  removes this hypothesis"). Not done that way: v2 (29 Oct 2026) replaces Theorem 3.18 by Theorem 2.5,
  which already proves convergence of every trajectory (to an equilibrium that need not be a
  minimiser, Remark 2.7), so citing the withdrawn theorem and claiming the companion removes its
  hypothesis would misstate the current literature (V:1.9-refute d5). Cited v2 Theorem 2.5, as paper A
  now does, and stated the companion's distinct claim (null exceptional set).
- R12: "lands only from later swap levels than those at which the same share of its images is chosen"
  holds at 50% and 90% but not for every share: at the top shares landing comes first (public: 99.8%
  land from s = 0.1, 99.8% chosen only at 0.05; 1000-image: 99.0% land at s = 0.2, 98.2% chosen
  there). Restricted to half (abstract) and half and 90% (contribution 3).
- R5 (5): "not by its late field" dropped; the sentence says the same late field lands these samples
  from the exact field's state, so the failure is set by the state reached above sigma = 5.
  R5 (4): the heading itself was changed (the finding's first option), since the new 19-sample
  sentence in the same paragraph contradicts "decided late". R5 (9): "half landed" instead of
  "half land", parallel to "half chosen".
- R3/R7: R7's wording ("written down", "by its own criterion it fails") combined with R3's ("repeat on
  the same latents", "the only new test").
- R31: placed after "These works record how close the output ends to a training image", so that
  sentence still covers only Bertrand, Liu and Dodson; "on a subsample" not used (the abstract
  describes subsampling as one accounting variant, not the hybrid itself).
- R8: optional n = abs(x - a) added to `tab:edm-rho` only (the `fig:landing` caption refers to it).
- R16's alternative wording ("except that at 0.5 the two AUCs tie") superseded by R2's fuller one.

## Layout

- The additions to Section 2 pushed `fig:collapse` to the top of p. 9, and the `\FloatBarrier` before
  Section 5.2 then left half of p. 9 empty. The figure block was moved to the start of Section 5.1
  (text unchanged); it now sits at the top of p. 8 with its text.
- Tables 7-9 of Appendix D had drifted into Appendix E (pre-existing). Added `\FloatBarrier` before
  Appendix E: they now form p. 31 directly after Appendix D, and Table 13 shares p. 35 with
  Figure 10 instead of standing alone.

## Compile

tectonic on lab09 (`bash scripts/build_papers.sh paper_mechanism`): rc 0, 35 pages (34 before), no
undefined references or citations (no "??" in the text), no overfull boxes; one underfull line in
the reproducibility statement (long file names). All 35 pages were rendered at 90 dpi; pages 1-16
and 26-35 (every figure page and every changed page) were looked at. Figures 1-5 sit on or next to
the pages of their text (pp. 2, 7, 8, 10 and 13; Table 1 on p. 11); the redrawn labels are not
clipped.

## Open for the authors

- Paper A's `refs.bib` still pins `liu2026geometric` to v1 (title and note) while paper A's text
  cites "Theorem 2.5, version 2"; paper A's editor should update that entry (not in fix-B's files).
- The abstract's "where the image is chosen" for the 2000-image model rests on the swaps of the
  other models; the 2000-image model was not swapped (stated in Limitations).
- The swap levels in the abstract (sigma ~ 0.5 and 2.5) are nominal; the effective hand-over levels
  are 0.42 and 2.8 (App. D gives the effective choice levels).
- Heading "Whether it is reached stays open until late." replaces "... is decided late."; revert if
  the original heading is preferred together with an opening qualifier.
