# Manuscript draft

Draft paper auto-assembled from `docs/THEORY.md` (theory, Section 3 + Appendix) and
`results/RESULTS.md` (experiments, Section 4). Every number is reproducible from the
repository code; see the Reproducibility paragraph in the paper.

## Files

- `main.tex` — full manuscript (English, LaTeX).
- `refs.bib` — 7 references (5 memorisation-literature citations from THEORY.md + the
  two phenomenon/technique sources).
- `figures/` — the 6 PNGs referenced by `main.tex`, copied from `results/`.

## Compile

Needs a LaTeX toolchain (TeX Live / MiKTeX). It was **not** compiled in-repo — only the
source is provided.

```bash
cd paper
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

## Status / TODO before submission

- **Theory** is complete and proof-carrying (load-bearing results inline, two auxiliary
  lemmas in the appendix). Proposition/Theorem numbers are LaTeX-auto and do **not**
  match the `THEORY.md` numbering; the descriptive names do.
- **Experiments** cover P1–P7, the interpolant-noise contrast, the three
  checkpoint-only checks (optimality gap / Lipschitz / posterior distance), EXP-2 (GMM)
  and EXP-3 (MNIST). All 5-seed where the sweep supports it.
- **Author/affiliation** are placeholders.
- **Weakest empirical point** (state honestly, or strengthen): EXP-3 is a single seed at
  N=500, no N-sweep.
- To add more figures, copy from `results/` — the available extras and their source
  paths:

  | suggested name | source |
  |---|---|
  | `fig_p2_velocity.png` | `results/exp1/_analysis/figures/P2_velocity_error.png` |
  | `fig_p3_meanshift.png` | `results/exp1/_analysis/figures/P3_collapse_to_train_point.png` |
  | `fig_collapse2d.png` | `results/exp1/_analysis_seed0/figures/collapse_2d_700k.png` |
  | `fig_p5_sigma.png` | `results/exp1/_sweeps/figures/P5_sigma_obs.png` |
  | `fig_p6_n.png` | `results/exp1/_sweeps/figures/P6_N.png` |
  | `fig_p7_ynoise.png` | `results/exp1/_sweeps/figures/P7_y_noise.png` |
  | `fig_exp2_2d.png` | `results/exp2/_analysis/figures/gmm_collapse_2d.png` |
  | `fig_exp3_grid200.png` | `results/exp3/exp3_mnist_seed0/figures/grid_it200.png` |
  | `fig_exp3_grid15k.png` | `results/exp3/exp3_mnist_seed0/figures/grid_it15000.png` |
