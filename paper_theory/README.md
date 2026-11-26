# Paper A: theory (target TMLR, then the Journal-to-Conference track)

`main.tex` is the theory half of the split described in
`docs/plan/paper_split_plan_2026-11-21.md`, assembled on 2026-11-21 from
the pre-split `paper/main.tex` (removed on 2026-11-23; it is in the git history). This file is edited on its own.

Submission packages (anonymous TMLR PDF, arXiv source, code supplement) are built by
`python submit/build.py` from the repository root; see the root README. To build this paper alone with
the TMLR style (anonymous by default):

```
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

On lab09 (no LaTeX on the Windows machine), with tectonic from the conda env `cfm`:

```
ssh lab09 'cd /mnt/data/khoitm8/cfm-collapse && bash scripts/build_papers.sh paper_theory'
```

Figures are drawn on lab09 with `PYTHONPATH=.:scripts python scripts/<script>.py`; the style is
`scripts/figstyle.py` (fonts from `scripts/make_tt_fonts.py`). Words are sans, math is Computer Modern
(no STIX), and no text is below 7 pt at the printed width. Every figure the two papers include also
renders on Windows from the archived results: `python scripts/make_tt_fonts.py <dir> --heros` (TeX Gyre
Heros from MiKTeX), then run the scripts with `FIGFONTS=<dir>` and `PYTHONPATH=.;scripts`.
The figures of 2026-11-26 were drawn that way.

## Replay the CIFAR-10 midpoint figure

From the repository root or an extracted copy of `submit/supp_A.zip`, run these CPU
commands with NumPy, SciPy, Matplotlib and Pillow installed.

```bash
python -m scripts.replay_cifar_composition
python scripts/audit_cifar_handoffs.py --compare-replays results/cifar_composition_replay --sources-csv audit_sources.csv > audit.json
python scripts/make_theory_cifar_composition_figure.py
```

The first command recomputes endpoint labels for eight selected pairs, twelve random
pairs and four sensitivity settings from the archived 2,000-image handoffs. It retains
decisions made before handoff. The second compares each label, including which atom
was reached, against independent backward integrations bracketing the basin boundary.
The dated input directories retain the original classification. Corrected per-source
labels, counts and summary tables are in `results/cifar_composition_replay/`.
The figure script reads the corrected selected-pair fractions and the native RGB training
images for all eight pairs. It outputs `paper_theory/figures/fig_cifar_composition.pdf` and
`paper_theory/figures/fig_cifar_curve.json`.

## Story

With strictly positive priors on a shared finite support, label noise, label averaging and every
fixed affine combination of two exact fields end on training examples almost surely for any
absolutely continuous source. Three fields can give a blend positive probability. The conjunction of
compositional generation (Liu et al., ECCV 2022) is such a combination, and at a tie of two
examples a blend needs a subtracted field whose log-odds lie strictly between those of the fields added.

## What is in it

- Sections 2-4 of the pre-split paper: setup, the exact reference, positive mixtures, guidance and
  schedules, composition, the spectral criterion (in the main text), and what leaves the support.
- **New, Corollary `cor:twofields`** (Sec. 4.2, proof in App. B): any combination
  `c v_p + (1-c) v_q` of two exact fields with priors in Ppos, for any constant `c` and for
  schedules as in Theorem `thm:schedule`, ends on an atom almost surely. This covers negative
  prompting by substitution. The proof of `thm:schedule` uses its priors only through membership
  in Ppos.
- **New, Remark `rem:generic`** (Sec. 4.4): the face condition of `thm:spectral`(c) depends only on
  the atoms, and holds for |S| = 2 and whenever z is in the relative interior of conv S.
  Hyperbolicity holds for almost every choice of the priors, by parametric transversality
  (Guillemin and Pollack 1974).
- **New, Section 4.5 *Composing conditions***: the conjunction reading, and **Proposition
  `prop:twoatom`** (proof in App. B). At a two-atom tie, `F' = 1 - sum_k c_k m_k^2`. No profile
  attracts unless an inner prior is subtracted, and with three priors the sign pattern must be
  (+, -, +). The conjunction threshold is recovered.
- Section 5: Proposition `prop:regular`, which says what a learned field needs to reach a blend.
- Section 6: the exact-field checks, plus two new runs.
  - **Positive control** for the stress test. The centred example agrees with the exact basin
    on the original grid. Translating the centre to (0.25, 0) preserves the analytic basin and
    exposes missed midpoint endpoints with the same fixed-step RK4 scheme.
  - **Signed combinations**: a random test (3841 combinations, 0 violations), a phase diagram
    (`fig_signed_combinations.pdf`), and exact basins. The equal conjunction gives 0.406, the
    unequal one 0.742, a negative prompt against the other example 0 (both forms), and a milder
    negative prompt 0.316.
- The CIFAR-10 comparison reports corrected two-image continuations from the archived
  handoffs. The label-averaging pilot compares trained networks on one synthetic problem.
- Appendices: all proofs for the above, endpoint noise, and the numerical protocols.

## New scripts and results (all read only from `results/`; nothing retrains)

- `scripts/stress_positive_control.py` writes `results/stress_positive_control_20261125/summary.json`
  (logit and blow-up codings; the 20261121 run is kept) and, with `--translation 0.25 0`,
  `results/stress_positive_control_20261121/translated.json`. It is a NumPy transcription of the
  stress-test oracle and RK4, because torch does not load on this machine.
- `scripts/signed_combinations_check.py` writes `results/theory_signed_combinations_20261121/`.
  Run it with `uv run --no-project --with numpy --with scipy`.
- `scripts/signed_combinations_probability.py` writes `results/theory_signed_probability_20261121/`,
  the midpoint probabilities of Figure `fig:signed`(b).
- `scripts/make_signed_combinations_figure.py` writes `figures/fig_signed_combinations.pdf`.
- `scripts/theory_basin_map.py` writes `results/theory_basin_map_20261121/`: the exact endpoint
  class (centre, edge midpoint, atom) of every source on the triangle of Section 6, for 32768
  Monte Carlo sources and a 500 x 500 grid, and the check against
  `results/learned_composition_2d_20261021/exact` (same centre classes on the 4096 shared sources).
  `--faces` adds the face masses of the `tab:spectral` configurations (key `faces`), and
  `--learned-edges` the learned edge counts and off-candidate fractions on the triangle (key
  `learned_edge_counts`).
- Figure 1 is `fig_unrolled_exact.pdf`, drawn by `scripts/make_theory_hero_figure.py` from
  `results/theory_basin_map_20261121/` (no longer by `scripts/make_edm_figures.py`).

## What moved to paper B (mechanism)

Theorem `thm:transfer`, Proposition `prop:localtransfer`, `thm:risktransfer`,
`prop:loss-no-certificate`, Theorem `thm:relerr`, `prop:trap`, `prop:heun`, the EXP-1/2/3
trained-collapse results, kernel tracking, the measured transfer, and the whole EDM section.

## Decisions taken while assembling (change them if you disagree)

- Learned composition stays in paper A (Section 6).
- Kernel tracking goes to paper B.
- The LLM statement does not say that any proof came from a model. The author confirmed on
  2026-11-25 that all statements and proofs, including `cor:twofields`, `prop:twoatom` and
  `rem:generic`, are their own and checked line by line. Models served only as additional checkers.

## Revision after the memo verification (2026-11-21)

Details, sources and rejected proposals: `docs/review/changes_paperA_2026-11-21.md`.

- **Prior work.** Liu and Zuazua v2 (arXiv 2605.12231, 29 Oct 2026, Theorem 2.5) proves that every
  trajectory of a constant two-field combination converges, without a limit-set hypothesis, to an
  equilibrium that need not be an atom. The abstract, the contributions, the Technique paragraph,
  the related work, the hard-label rate remark and `apx:comparison` with `tab:comparison` now say so, and
  credit Wan et al. (ICML 2025, Thm. 5.3), Azangulov et al. (AISTATS 2026, Thm. 3) and Cao et al.
  (arXiv 2605.07220). The updated appendix derives almost-everywhere atomicity at fixed
  nonnegative guidance by combining Liu and Zuazua with Jiang and Ma's cutoff density
  formula (arXiv 2607.19725v2, Theorem 4.2). The direct trajectory argument also handles
  arbitrary probability mixtures and bounded nonnegative schedules of bounded variation
  near the endpoint. The signed three-field analysis identifies attracting ties.
- **Edge midpoints of the triangle.** They are two-atom ties that attract for w > 1.368 w_c. The
  exact conjunction ends 0.131 / 0.409 / 0.460 of the mass at the centre / edge midpoints / atoms
  at 2 w_c (32768 sources). The centre fractions reported before are unchanged; the claims that
  networks follow the exact probabilities now say "at the centre". New: `sec:conjunction` states
  the edge threshold for the regular simplex; Section 6, `tab:spectral` and
  `tab:learned-composition` report the edge mass.
- Bib metadata of `physicscfm2026`, `jain2025attraction`, `sesmat2026leaks`, `beltran2026reward`,
  `dodson2026calm`; reproducibility statement names the figure scripts.
- **Review fixes (fix-A).** Face masses of the spectral configurations, scope of the two-field
  and schedule statements, prior credit (Baptista et al. Ex. 4.4, Cai et al., Du et al.), CIFAR
  and threshold zeros marked as built into the classifiers, figures 3-5 moved next to their text
  (the composition figure is now Figure 3, the signed-combinations figure Figure 4). Details in
  `docs/review/changes_paperA_2026-11-21.md`, section 8.

## Status (2026-11-24)

- Run `python submit/build.py A_tmlr supp_A` from the repository root to rebuild the anonymous
  PDF and its code and data supplement.
- Round 3 (2026-11-23): statement fixes (two-field corollary needs strictly positive priors, "intermediate"
  instead of "less decided", the generic remark), Sontag cited for Caratheodory flows, the
  Guillemin and Pollack citation checked, citations of Wan, Baptista and Benton corrected. Reports and a
  line-by-line proof checklist: `docs/review/round3_2026-11-23/`.
- Figure 5 (`fig_signed_combinations.pdf`) is redrawn with the current theorem numbers; its script
  checks them against `main.aux` when `THEORY_AUX` is set.
- Figures redrawn from the data at print width (see the figure scripts named in the
  reproducibility statement).

## Not yet done

- (Done in fix-A) The count "at most 3 of 2048 sources within 0.05 of an edge midpoint" (Section 6)
  is now written by `scripts/theory_basin_map.py --learned-edges`.
- The fixed-guidance comparison in the current manuscript uses Liu and Zuazua v2, Theorem 2.5.
