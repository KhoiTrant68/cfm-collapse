# Paper B: mechanism (target NeurIPS 2027, main track, "General")

`main.tex` is the mechanism half of the split described in
`docs/plan/paper_split_plan_2026-11-21.md`, assembled on 2026-11-21 from `paper/main.tex`.
`paper/main.tex` stays the reference source and is not submitted; from now on this file is
edited on its own.

Draft title: *Trained Samplers Choose Early and Land Late*.

The NeurIPS 2027 style file is not out yet, so the draft is built on the same TMLR setup as
`paper_theory/` (anonymous by default; the ICLR `\moveblock`/`\placeblock` machinery is dropped).
When the CFP is out: swap in the NeurIPS style, add the paper checklist, and cut the main text
(through the Conclusion) to 9 pages. The comment at the top of `main.tex` says the same.

```
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

On lab09 (no LaTeX on the Windows machine): `ssh lab09 'cd /mnt/data/khoitm8/cfm-collapse && bash
scripts/build_papers.sh paper_mechanism'`.

## Story

By medium noise the state of a trained sampler fixes which training image the exact field would
reach from it (the choice), and whether the sample lands on that image stays open until late and
depends on the late field acting on the state it is handed; the contraction that the relative field error leaves
carries out the landing. Paper A
(`paper_theory/`) is cited as an anonymous companion submission (`companionA` in `refs.bib`) for
every exact-field result; nothing from it is re-proved here.

## What is in it

- Sec. 1 Introduction with a contributions list; Figure 1 (`fig:intuition`) is `fig_teaser.pdf`
  ("one latent, two clocks": the network's and the exact field's guesses along one trajectory of
  the public and the 500-image EDM model; below, the two swap clocks, choice = net-to-exact =L and
  landing = exact-to-net on-atom share, public model thick and 500-image model thin, with dotted
  lines where the public curves pass 1/2: s = 2.48 and s = 0.51).
- Sec. 2 Related work: Bertrand et al. (failure to fit the closed form at t ~ 0.15 and near 1;
  hybrid sampler), Biroli et al. (speciation and collapse; our choice corresponds to the collapse),
  Raya and Ambrogioni, Li and Chen (critical windows), Bonnaire et al., hybrid samplers (Bertrand
  et al., Liu et al., Dodson et al.), late landing (Li et al. kinetic, with their Table 4 numbers;
  Favero et al.), where memorisation arises (Dodson et al., Kaiser and Kollmann, Lopez-Amado et al.,
  Jaziri et al., Verma et al., Wen et al., Pham et al., Shah et al., Kim et al., Jain et al.), error
  bounds (Benton et al., Beltran et al.).
- Sec. 3 Background: setup, Assumption, and Prop. `prop:collapse`, Prop. `prop:kernel-field`,
  Thm. `thm:endpoint`, restated without proof and attributed to the companion paper.
- Sec. 4 From exact to learned fields: Thm. `thm:transfer`, Prop. `prop:localtransfer`,
  Thm. `thm:relerr`, `fig_mechanism.pdf` (1-D flows for the exact field and two learned fields,
  their relative errors and distances to the training point; it replaces the former
  `fig_unrolled_learned.pdf` and `fig_landscape.pdf`); pointers to Prop. `prop:loss-no-certificate`,
  Thm. `thm:risktransfer`, Prop. `prop:trap`, Prop. `prop:heun` (stated and proved in the appendix).
- Sec. 5 Experiments:
  - 5.1 Collapse in trained networks: EXP-1, CIFAR-10 DDPM inpainting, kernel tracking, and a
    one-paragraph summary of the measured transfer; one figure, `fig_collapse.pdf`, with the other
    panels in the appendix (`fig_collapse_details.pdf`).
  - 5.2 Landing in EDM image models: the models and the off-atom criterion.
  - **5.3 Choose early, land late: swapping the field mid-trajectory (new)**, from
    `results/n3_followup_20261111/SWAP_SUMMARY.md` (public and 1000-image models) and
    `results/n3_followup_sub500_20261111/SWAP_SUMMARY.md` (first 500-image model), with the
    clocks and intervals of `results/paperB_20261121/swap/swap_clocks.json`. Table
    `tab:swap` has all three models; Figure `fig:swap` (`figures/fig_swap.pdf`) shows the images
    reached by net-to-exact and the choice and landing curves. Net-to-exact landing is stated as
    structural (the last Heun step returns D(x; 0.002)); landing evidence is exact-to-net. The
    paragraph "A window of exact field" reports E1
    (`results/paperB_20261121/window_swap_public/`; Table `tab:window` in Appendix D).
  - 5.4 The late contraction carries out landing: relative error table, late contraction, the
    radial identity check, the detector comparison (baseline at sigma = 0.585, not at 0.002, which
    is bookkeeping) and the Heun certificate (`fig_landing.pdf`; `fig_heun.pdf` is in the
    appendix). The main-text figures other than `fig_swap.pdf` are drawn by
    `scripts/make_paperB_figures_v2.py`.
- Sec. 6 Limitations and planned experiments: the round-2 GPU experiments (sigma-window
  intervention predicting memorisation, N grid x seeds with augmentation, guidance on real
  models, nearest-neighbour baselines, scale-up) are listed as in progress.
- Sec. 7 Conclusion; broader impact, LLM use and reproducibility statements adapted from
  `paper/main.tex`.
- Appendices: A proofs of transfer, local transfer, risk transfer and the loss counterexample;
  B relative error, trapping, Heun (proofs); C measured transfer; D EDM experiments (swap protocol
  and why net-to-exact always lands, the exact posterior against the choice (E7,
  `figures/fig_posterior_choice.pdf`, a copy of
  `results/paperB_20261121/collapse_sigma/fig_collapse_vs_choice.pdf` drawn by
  `scripts/make_collapse_choice_figure.py`), the window swaps (`tab:window`), Heun bound, predictive
  anchor, the three trained models); E experimental details (synthetic problems with t-intervals,
  CIFAR-10 with the retrained slopes).

## New text (not in `paper/main.tex`)

- Abstract (about 200 words), introduction, related work, Section 5.3, limitations and planned
  experiments, conclusion, the swap protocol paragraph in Appendix D.
- The proof of `prop:localtransfer` no longer cites Lemma `lem:mixture-coupling` or
  `eq:pf:int:conc` of paper A; the two facts it used are written out from
  Proposition `prop:kernel-field`.
- Sentences that used Prop. `prop:regular` and Prop. `prop:uncond` of paper A now cite the
  companion paper instead.

## Numbers to double-check

All swap numbers are copied from the `SWAP_SUMMARY.md` files and `swap_summary.json`
(net-to-exact median distance below 1e-5 on all three models). Derived numbers in the text:
re-selection from s = 5 of 58% / 22% / 5% is 1 - (=E) for exact-to-net at s = 5; "93% by
sigma = 5" is =L 0.928 of the 500-image model; "at least 88%" is the smallest =L at s = 1
(1000-image model, 0.880); "about 96%" of samples memorised by the 500-image model is 1 - 0.041.

Added on 2026-11-21 (third pass), each checked against the file named, and recomputed from the
per-sample files where possible (see `docs/review/changes_paperB_2026-11-21.md`):
- Swap clocks (public: =L 50% at s = 2.48 [2.13, 2.87], 90% at 0.95 [0.74, 1.05]; landing 50% at
  0.51 [0.47, 0.54], 90% at 0.21; 1000-image: 4.74, 0.82 [0.65, 1.02], 1.33 [1.29, 1.37], 0.56;
  effective levels 2.82 and 0.76): `results/paperB_20261121/swap/swap_clocks.json`,
  `verify_swap/verify_swap_report.txt`. Largest net-to-exact d1 7.07e-6; 379/431 and 11/431 at
  s = 1; median learned d1/d2 0.977 / 0.949: the `swap_per_sample.npz` files.
- E1 window swaps: `results/paperB_20261121/window_swap_public/` (recomputed from
  `window_per_sample.npz`; the windows (lo, inf) and (0, hi] reproduce the old swap runs sample by
  sample).
- E7 posterior crossings (3.82 / 1.99 / 0.78; 6.39 / 3.30 / 1.22; 7.52 / 3.82 / 1.44; at sigma = 5:
  0.789 and 0.936): `results/paperB_20261121/collapse_sigma/summary.json`.
- EXP-1 t-intervals and EDM AUC intervals: `results/paperB_20261121/uncertainty/` (`stdout.txt`,
  `tables.tex`, `edm_auc.json`; `scripts/paperB_uncertainty.py`). The CIFAR slopes and the
  tab:p7kernel intervals moved to paper A: `results/kernel_tracking_20261121/uncertainty/`
  (`scripts/kernel_tracking_uncertainty.py`). Transfer AUCs: `transfer/TRANSFER_SUMMARY.md`,
  `auc_vs_t.csv`. Radial identity (correlation >= 0.993) and 34/41, 195/200: `radial/`. Baseline at
  sigma = 0.585 (0.990 [0.986, 0.994], paired difference [0.004, 0.010], R^2 0.991 / 0.976 /
  0.965 / 0.883): `certificate/CERTIFICATE_TABLES.md`. Incremental logistic regression (<= 0.002):
  `incremental/incremental.json`.

## Done on 2026-11-21 (second pass)

- Compiles with tectonic on lab09 (29 pages, no undefined references or citations).
- `figures/fig_swap.pdf` by `scripts/make_swap_figure.py`: (a) the training images reached by
  net-to-exact at each switch level for three latents of the public model (CIFAR-10 images read
  from the python batches; the stored indices are within-class indices in torchvision order),
  (b) choice and landing curves for the public and 1000-image models.
- Citations resolved from the arXiv pages: Liu et al. 2025 "From Navigation to Refinement"
  (`liu2025navigation`), Li et al. 2026 "A Kinetic Energy Perspective of Flow Matching"
  (`li2026kinetic`), Favero et al. "Bigger Isn't Always Memorizing" (`favero2025bigger`). The
  unidentified "Shah et al." was dropped (identified and added in the third pass, `shah2025ambient`).
- **Overlap to keep in mind:** the hybrid samplers of Bertrand et al. (closed form first, pixel
  space, CIFAR-10 and CelebA) and Liu et al. (oracle velocity first, latent ImageNet) are our
  exact-to-net direction, and Dodson et al. exchange two trained EDM networks over wide sigma
  ranges in both directions. Related work and the contribution list say so; our new parts are the
  separation of the choice from the landing (net-to-exact with the exact posterior, recording which
  image apart from whether it lands, in both directions at one swept level) and the
  relative-error landing theory.

## Done on 2026-11-21 (third pass: corrections after the memo verification)

Source: `docs/review/memo_verification_2026-11-21.json` and Section 5 of
`docs/plan/paperB_findings_2026-11-21.md`; full list in `docs/review/changes_paperB_2026-11-21.md`.
- Net-to-exact landing is no longer presented as evidence anywhere (abstract, contributions,
  related work, captions, Sec. 5.3, conclusion, broader impact, appendix); the Reading paragraph no
  longer says that the 1000-image model's late field does not land exact states.
- "Two times" rewritten (our choice corresponds to Biroli et al.'s collapse; they also measure on
  trained networks); E7 is in Appendix D with Figure `fig:posterior`, and is claimed only for the
  public model.
- The "ties the baseline 0.983 vs 0.985" comparison is replaced by the baseline at sigma = 0.585;
  contribution bullet 4 and the title of Sec. 5.4 now say "carries out landing".
- CIFAR slopes (h = 4: 0.36 [0.22, 0.51] over three retrained instances; h = 6 not determined),
  EXP-1 t-intervals, transfer AUC intervals, hypothesis (b) wording, the sd convention, swap
  rounding (6.45, 10.73, 3.94), class-balanced 1000-image subset.
- Figure 1 redrawn with the swap clocks (`make_paperB_figures_v2.py teaser`).
- E1 window swaps added (Sec. 5.3 paragraph, Table `tab:window`); planned experiment (i) updated,
  (iv) removed (the baseline comparison is reported in Sec. 5.4).
- Bibliography: Shah et al. 2025, Li and Chen 2024, Kaiser and Kollmann 2026 added; venue fields of
  Li et al. (PMLR 306), Liu et al. (CVPR 2026 Findings), Favero et al. (TMLR 2026), Dodson et al.,
  Sesmat et al., Jain et al., Beltran et al., Biroli et al. updated; physicscfm2026 pinned to v3
  (not cited in paper B; the "return training examples" sentence is only in `paper/main.tex`).
- Compiles with tectonic on lab09: 34 pages, no undefined references or citations, no overfull
  boxes.

## Not yet done

- The LLM statement is the one of `paper/main.tex`; confirm it (this draft was restructured with
  model assistance).
- Page count against the 9-page limit once the NeurIPS style exists (the main text, through the
  Conclusion, is about 15 TMLR pages).
- GPU experiments still open: E1 window swaps on the 500- and 2000-image models (planned
  experiment (i)), swaps of the 2000-image model, recording the hand-over distance (the factors
  "about 2 to 3, or 1.4 to 2.2" in Sec. 5.3 are estimates that assume it), and the other round-2
  items of Sec. 6.
- The threshold check (0.2, 0.5) of the balanced-model comparison at sigma = 0.585 is now in
  `results/threshold_auc_r2_20261121/threshold_auc_r2.json` (`scripts/threshold_auc_r2.py`, the
  verifier's check moved into the repository, with the R^2 by threshold added).
- Figure `fig_posterior_choice.pdf` is a copy of the other session's figure; if
  `scripts/make_collapse_choice_figure.py` is rerun, copy it again.
