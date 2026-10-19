# Canonical manuscript

`main.tex` is the full anonymous TMLR manuscript. `math_commands.tex` defines
shared notation, `refs.bib` is the bibliography, and `figures/` contains the
scientific figures. Older ICLR styles and workshop sources are historical.

Preserve the distinction between exact empirical-reference endpoints and
trained samplers evaluated at finite cutoffs. Moment agreement alone does not
identify a distribution or prove learned atomicity.

## Build and check

From the repository root, with Python, pdflatex and BibTeX on PATH:

```powershell
python scripts/check_paper.py --build --build-dir tmp/paper-build
python scripts/check_paper.py --build-dir tmp/paper-build
python scripts/verify_paper_numbers.py
python scripts/test_calibration.py
python scripts/test_check_paper.py
```

The wrapper records hashes of inputs and build products. Validation rejects
stale auxiliary files, changed inputs, and changed outputs. TMLR validation
imposes no page cap. `--venue iclr` explicitly checks the nine-page main-text
gate and rejects TMLR style; it neither converts the paper nor certifies every
conference requirement. `--page-limit N` supplies an explicit cap.

Inspect the regenerated PDF after edits. Compilation and numerical checks do
not certify mathematics or layout. Copy the reviewed PDF to `paper/main.pdf`;
build records stay in the chosen build directory.

## Provenance

Artifacts are under `results/`; the manuscript records protocols and limits.
Some older checkpoints were not retained: those figures and tables use saved
outputs rather than a fresh derivation from weights.

Figure scripts include `make_paper_figures.py`, `make_flow_portraits.py`, and
`make_image_bandwidth_figure.py`. The last reuses stored grids without training
or new sampling. Preserve data and numerical annotations when changing layout.

Dated `docs/review/whole_paper_*_2026-10-17.*` files describe the frozen audit.
The subsequent repair report records changes and checks. Obtain page and
bibliography counts from the current build rather than hardcoding them here.
