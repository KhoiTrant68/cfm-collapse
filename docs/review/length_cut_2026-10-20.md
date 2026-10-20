# Cutting the paper to length — 20 October 2026

Request: main text at most 12 pages, appendix at most 25 pages, unnecessary material removed,
proofs written clearly. The pre-cut source is the state of commit `15010bf`; everything removed
remains in Git history.

## Result

| | Before | After |
|---|---|---|
| Main text (to the end of the conclusion) | 14 pages | 10 pages |
| Appendix | pp. 17–110 (about 94 pages) | pp. 12–24 (13 pages) |
| Total PDF | 110 pages | 24 pages |
| `main.tex` | 6494 lines | about 1680 lines |

## What was kept

- All results of the current story: Sections 3–5 and their proofs, the composition experiment,
  the exact-field stress and tie tests, the learned-averaging pilot, hard-conditioning collapse on
  EXP-1 and the CIFAR-10 U-Net, and the EXP-1 label-smoothing comparison.
- Supporting statements needed by the main text: Proposition `prop:uncond`, endpoint noise
  (`prop:tgtnoise`), the risk-transfer certificate and the loss counterexample.
- Experimental details for everything the main text reports (Appendix E).

## What was removed

- The effective-bandwidth audit and its independent evaluation, the calibration theorem and
  finite-sample coverage bound, the spectral-bias model, and the reference-family control. The
  workshop version keeps this material; its source is now frozen (`workshop_src.tex`), because the
  blocks it used to cut from `main.tex` no longer exist there.
- The random-design `N → ∞` results, near-duplicate labels, finite-sample memorisation and
  non-representability, the representation floor, error survival and the loss form, interpolant
  noise, the affine-hull guidance proposition, and the related-work table.
- About 40 pages of additional experiments and supporting figures (sweeps, seed split, N-sweep,
  adversarial pairing, survival measurements, architecture sensitivity, independent validation,
  solver diagnosis).
- Corollaries folded into the text: the conditional/unconditional distinction, the exact moments,
  and the two bandwidth limits (now one corollary).

## How the proofs were rewritten

Appendix B now opens with one lemma of basic facts and two general lemmas used by every
intervention proof: convergence from finite kinetic energy (`lem:conv`) and null non-atom basins
from volume expansion (`lem:volume`). Each proof is split into named steps (well-posedness,
energy, convergence, volume expansion), so the shared arguments appear once. The Section 3 proofs
are shortened to their content, without restated statements.

## Verification

Each group of rewritten proofs went verbatim to four fresh verifiers that saw only the
definitions, statements and proofs, with no other tools. The groups were: Section 3 and endpoint
noise; positive mixtures with the two general lemmas; guidance; composition; and transfer with the
certificates. All five groups were confirmed 4 of 4 with no hole found; results are in `length_cut_verification_2026-10-20.json`. Minor notes were
applied afterwards: the continuous-version convention for the minimiser, the integral form of the
Grönwall step, narrow continuity of the marginals, and the squared distance bound.

## Checks

- `check_paper.py --build`: all checks pass; main text ends on page 10.
- `verify_paper_numbers.py`: 370 passed. Three text-presence checks for cut h_eff and coverage
  prose were removed (their values are still checked against the result files), and the sanity
  list now names the image-scale numbers the main text quotes.
- `test_check_paper.py` and `test_calibration.py` pass; `workshop.tex` compiles to 14 pages with
  no undefined references.
