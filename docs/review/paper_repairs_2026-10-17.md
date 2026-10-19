# Repairs after the whole-paper audit — 17 October 2026

The user authorized repairing the findings in `whole_paper_audit_2026-10-17.md`.
`paper/main.tex` remains the sole canonical manuscript, in anonymous TMLR style.
The pre-repair source is preserved at `tmp/paper-repair-2026-10-17/main.before.tex`
(SHA256 `a0f319683cee5b0390d29757974b435f7e23623bea86732a62c6b472a47b351c`).
No experiment results were changed or new training runs launched.

## Mathematical contracts and their consumers

| Finding | Implemented repair |
|---|---|
| M01–M02 | State the fixed-dimension quantization asymptotic with a finite `(2+eta)` moment and nonzero absolutely continuous part. Retain empirical slopes and exponent-factor values, removing finite-N error-ratio and empirical-Theta conclusions. |
| M03 | Replace the false necessary bandwidth condition by a sufficient condition for separation from the displayed generic stochastic error. Covariance expansion unchanged. |
| M04 | Distinguish a fixed finite table failing on fresh draws from a measurable table fitted to an entire countable stream. Remove the inferred SGD convergence/generalization claim, including its summary. |
| M05 | Distinguish deviation from the teacher trajectory from actual sampler spread. Restore `delta sqrt(d)` in the prose and stop treating the empirical loss–spread fit as a theorem or estimate of the error Lipschitz constant. |
| M06 | Restrict h=0 CFG to observed identifying labels; require nonempty C, h>0 and nonnegative epsilon for near-duplicate bounds; treat rho=0 separately in the endpoint-noise proof; define the loss counterexample at every observed label. Correct the null-slice convention. |
| M07 | Replace an endpoint-value condition by `gamma(t)->0`, and qualify general exact-flow conclusions by regularity and marginal-transport uniqueness. |

All original theorem/proposition/lemma/corollary/assumption/remark counts and all
230 labels are preserved. Of 38 proof environments, only two change: the rho=0
branch and the label-explicit loss counterexample. The two principal intervention
atomicity proofs are unchanged. Exact old/new text for the initial contracts is
recorded in `tmp/paper-repair-2026-10-17/math_contract_changes.json`; subsequent
consumer edits are in the Git diff and adjacent change records.

## Experimental claims and source attribution

- E01–E02: replace learned endpoint-law/atomicity conclusions from moments or
  assignments by the actual finite-cutoff observations, consistently in prose and
  captions. Do not use hard-label solver success to rule out errors for another field.
- E03: disclose the unweighted experimental objective and time clipping, and
  distinguish it from the time-weighted theoretical interpolant-noise objective.
- E04/R02/R04: distinguish fixed Gaussian training-label/embedding noise from
  general caption interventions and inference-time annealing.
- E05: describe the 78% share as a quadrature summary of two slices; remove the
  claimed general decomposition and absence of interactions.
- E06: restrict the sweep comparison to its reference families; remove SGD
  convergence claims for arbitrary architectures.
- E07: retain `sqrt(S_epsilon)` rather than W2 for Sinkhorn values. Describe null
  discrepancy as a reference score, not a paired-difference resolution threshold.
  Replace causal conclusions from rank correlation by association.
- E08: report 31/36 checkpoint agreements and visual similarity rather than exact
  equality of finite generated samples.
- R01/R05/R06: clarify Smola's coordinate-dependent bandwidth; correct the
  gradient-variance attribution; distinguish large kernel eigenvalues from generic
  Fourier low frequencies.
- R07/R08: cite the original Nadaraya–Watson entries and use the published Sesmat title.

## Build tooling and layout

The checker now records hashes of paper inputs and build products, accepts a
separate build directory, rejects stale/missing provenance, and checks a page cap
only when explicitly requested. ICLR validation rejects the current TMLR style.
Four regression tests cover changed sources, changed products, missing provenance,
explicit page caps and oversized floats. `paper/README.md` now describes the canonical workflow;
obsolete ICLR page-count and bibliography-count assertions were removed.

The six trajectory panels and five intervention panels are reflowed in TeX from
unchanged image data. Shared legends omitted by the crops are described in captions.
MNIST grids use two continued-float pages and larger panels; CIFAR grids are stacked
at larger width. Figure42 is regenerated from stored grids with wrapped headers.
The variability-slice plot is regenerated with readable stacked panels and a
descriptive title; the four inset-bearing collapse panels are enlarged in two rows.
The calibration theorem now fits continuously on one page; ragged-bottom layout
avoids the previous forced vertical stretching.

## Verification and limits

- Numerical verifier: 368 passed, zero failed; calibration checks passed.
- Checker regression suite: four tests passed. Expected rejected-cache cases
  print `FAIL` inside the successful unit-test run.
- Isolated full pdflatex/BibTeX build: no undefined references/citations or overfull
  hboxes; all labelled figures and tables referenced. Build hashes and page count
  are recorded in the accompanying verification JSON.
- Editor inspected the reflowed intervention/trajectory figures, complete
  calibration theorem, enlarged image grids and wrapped headers in rendered pages.
  This is an affected-page review, not a fresh independent inspection of every
  page of the revised PDF.

Two independent reviewers completed bounded re-reviews of the actual patched source,
SHA256 `72f7d6ed220e930e9f63e40650710c3b81f53c7494d44365a154ab32a32ce29b`.
The mathematical reviewer accepted all nine reviewed repair packets and checked
consumers after a final correction to the interpolant caption. The empirical-claim
reviewer accepted the held-out, trace, null-reference, image-caption, interpolant
and figure-generator repairs. Their first passes found remaining overstatements;
these were corrected and independently re-read before the final verdicts.
These verdicts apply to the bounded repairs, not every assertion in the paper or
the rendered PDF. The original whole-paper audit and frozen ledger retain their
original hashes; their statuses are not silently transferred to the new manuscript.
An additional image-caption correction was independently accepted at final source
SHA256 `23ac6122ec15529d07df69a97666f443038b8915eb89bac29739c84c6b60dcd0`.
The only other source change after the mathematical verdict was reducing the
training-grid width from 0.9 to 0.86 textwidth to fit its expanded caption.

Exact Yoon threshold and Blohm–Garg theorem-level comparisons remain unresolved
where full text was inaccessible. Full independent linear reading of the revised
manuscript remains pending. No venue conversion, submission, commit or push is performed.
