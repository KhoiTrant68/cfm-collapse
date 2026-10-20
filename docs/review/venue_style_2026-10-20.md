# Venue-style presentation — 20 October 2026

Request: present the paper the way ICLR, ICML and NeurIPS papers usually do, with particular care
for how the mathematical proofs are presented. No statement and no proof body changed.

## Theorem apparatus

- Results are numbered by section on one shared counter (Theorem 4.1, Proposition 4.2,
  Lemma B.2), so a number tells the reader where to look.
- The 15 main-text results with appendix proofs are `restatable` (`thmtools`, `thm-restate`).
  Each one is restated with its original number and title immediately before its proof, so the
  appendix can be read without paging back. The pointer "[Proof: Appendix X]" appears only in the
  main text (`\proofpointerfalse` after `\appendix`).
- Hyperref anchors for restatements carry their own prefix, so there are no duplicate
  destinations.

## Main text

- Section 4 opens with a **Proof strategy** paragraph: the two-step template (finite kinetic
  energy gives convergence; volume expansion gives null non-atom basins), stated once, with the
  remark that composition is where the second step fails.
- The informal paragraphs after Theorem 4.1, Proposition 4.4 and Theorem 4.7 are now **Proof
  sketch** blocks that say which step of the template each argument checks. Remarks that are not
  part of a sketch (the weaker guided rate, the exponentially small threshold) stay outside.
- The summary of interventions (Table 1) moved to the introduction, next to the contributions.
- The composition table is replaced in Section 6 by Figure 2: (a) the composite mean `F_w`
  below, at and above the threshold, and (b) the basin probability against `w/w_c` for
  `B = 1, 2, 3`. The table moved to Appendix E.3. The figure is produced by
  `scripts/make_composition_figure.py` from `results/theory_composition_20261019/summary.json`.

## Appendix

- **Organization of the appendix** (unnumbered, so the appendix letters are unchanged), with a
  notation table (Table 3) and a proof roadmap (Table 4) listing where each result is proved and
  what it uses.
- **Proof overview** paragraphs before the longer proofs: Theorem 4.1, Theorem 4.6, Theorem 4.7
  and Proposition 5.2. Each overview names the steps of the proof that follows.

## Checks

- All 26 proof bodies are byte-identical to commit `0caf18e`. The check compares the text between
  each `\begin{proof}` and `\end{proof}`.
- `check_paper.py --build`: all checks pass. The main text ends on page 10, and the PDF has 28
  pages (the appendix runs to page 28).
- `verify_paper_numbers.py`: 370 passed, 0 failed.
- `test_check_paper.py` (4 tests) and `test_calibration.py` pass. `workshop.tex` compiles to 14
  pages with no undefined references.
