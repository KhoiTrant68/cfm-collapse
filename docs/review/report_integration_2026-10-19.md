# Integrating the report of 19 October 2026

Source: [archived report](archive/report_2026-10-19.md), originally `report.md` in the main checkout (SHA256
`f58c1dc785740d5936ceed8474095a5da7b0940f8151c64df0162e559099afab`). It holds a review of
`paper/main.tex`, an assessment of the stage-2 proofs, a handoff with tasks A–E, the stage-2
proofs themselves (T1–T4, T4+, T6; T5 open) and a revision plan. `paper/main.tex` remains the
canonical anonymous TMLR manuscript. The pre-integration source is
`tmp/report-integration-2026-10-19/main.before.tex` (SHA256 `5f0408eb…984d999b`).

## What changed in the paper

| Report item | Status | Where |
|---|---|---|
| T1 positive prior mixtures; `prop:filtered` as a consequence (D3) | Done | `thm:posmix`, `prop:filtered`, App. `apx:pf-posmix`, `apx:pf-filtered` |
| Negative guidance, w ∈ [−1, 0) | Done; hard labels stated as not covered | `cor:negcfg` |
| T2 BV guidance schedules, with the R(τ) patch (KL ≤ log 1/min p), w on [0,1), Carathéodory/Liouville (A1) | Done | `lem:signedconv`, `thm:schedule`, App. `apx:signedconv`, `apx:pf-schedule` |
| `prop:cfgatom`(a) convergence written out (A4) | Done: (a) is now the constant case of `thm:schedule`; the convergence step is the explicit lemma | `apx:pf-cfgatom` |
| Signed covariance identity in the w(1+w)\|μc−μu\|² form | Done | `apx:pf-schedule`, Section 4.2 |
| Growing hard-label schedules, γ < 2 (D6) | Done, as a sufficient condition | `apx:pf-cfgatom` |
| T3 counterexample and threshold w > 1/sinh²B (A2, D1) | Done and strengthened (see below) | `thm:composition`, `eq:composition-mean` |
| T3′ no-symmetry, open parameter set (A2) | Done | `prop:composition-open` |
| T4 endpoint transfer, x-prediction reading (D4) | Done, presented as an elementary consequence of `prop:survival`; no claim that it explains the 38% CIFAR figure | `thm:transfer` |
| Lemma h > 0 with ρ < D/2 and Δ = v − v_p (A3) | Done | `prop:localtransfer` |
| T6 exceptional set is a hyperplane | Done, generalised to any two atoms | `prop:hyperplane` |
| T5 endpoint weights (D5) | Left open, stated in Limitations and Conclusion | — |
| B1 duplicate "Proof of Proposition projection" title | Already fixed before this report | — |
| B2 move the `prop:filtered` proof out of the spectral-bias appendix; fix the `sec:heff` pointer | Done | `apx:pf-filtered`; App. `app:specbias` now points to Section 4.1 |
| B3 rename N(z), unify u/y′ | Done; `\nn(z)` instead of 𝒩(z), because `\N` is already the Gaussian | `math_commands.tex` |
| B4 Zador as an asymptotic statement | Main text already asymptotic; appendix values marked approximate | App. `app:deferred` |
| B5 `prop:atomicity` second moments | Done: inequality stated in [0, ∞], finite iff the posterior has a finite second moment | `prop:atomicity` |
| Góp ý 5: example satisfying risk transfer | Done: spatially constant errors (K ≡ 1) and contraction-rate errors (K = e^{2C}); the loss counterexample is in the second class with divergent ∫c | App. `app:teacher-risk` |
| C2 rewrite abstract, introduction, conclusion; gather limitations | Done | Sections 1, 7, 8 |
| C3 restructure; move h_eff out of the main text | Done: new Sections 4 (interventions) and 5 (exact → learned); `sec:heff` and `sec:independent` moved, unchanged, to the new App. `app:moment-audit`; main text now ends on page 14 (was 16) | — |
| Intervention classification table | Done | `tab:interventions` |
| D7 do not cite Peng & Ma (2026) | Not cited | — |
| Literature (E) | Added Kynkäänniemi et al. 2024 and Chidambaram et al. 2024 (both checked against the arXiv API) and Hale 1980 for Carathéodory flows | `refs.bib`, related-work table |

Claims that composition contradicts were qualified: the appendix ordering of noise
interventions, the remedies paragraph, and caption (d) of the mechanism figure. The CIFAR-10
subsection's pointer to "the next section" now points to the moved audit appendix.

The changes are split into two commits on this branch: `5d9cbb3` (theory: new results, proofs,
proof fixes, the composition experiment) and `e796124` (restructure: abstract, introduction,
limitations, conclusion, and the move of the audit to the appendix). The theory-only state was
built and passes all checks on its own (main text to page 20 before the move).

## Corrections and additions to the report

1. **Composition, not order.** Label averaging and guidance commute:
   ∫[(1+w)v*(y−u) − w v_unc]φ(du) = (1+w)v_φ − w v_unc. The paper therefore says that the
   *composition* of two atom-preserving interventions can leave the support. The report's
   phrase "thứ tự kết hợp quyết định support" (order decides support) was not used.
2. **Exact threshold.** In the symmetric two-atom case the composite mean has the closed form
   F_w(s) = 2 tanh(s)(cosh²s − w sinh²B)/(cosh 2s + cosh 2B). This gives the converse missing
   from the report: for w ≤ 1/sinh²B only x₀ = 0 reaches the midpoint (via the lower bound
   F_w(s) ≥ κ min(s³, 1), κ = 1/(cosh 2 + cosh 2B)), so the threshold is an "if and only if".
   The unstable root is cosh s_u = √w sinh B.
3. **Hyperplane through the source mean.** For two atoms c ± ν with equal weights, the
   exceptional set is {x₀ : ν·x₀ = 0}, through the origin rather than the midpoint c.

## Verification of the proofs

Each group of proofs was cut verbatim from `main.tex` into a packet with only the definitions,
statements and proofs (`tmp/report-integration-2026-10-19/` records the hashes). Four
independent verifiers per group read only the packet, used no other tool, and attacked it with
the skill's refutation taxonomy, each from a different angle (hypothesis checks, one-line-lemma
tests, proving-too-much substitutions, specification checks). The rule was 4 agreements to
confirm, 2 dissents to refute.

| Group | Results | Verdicts |
|---|---|---|
| G1 | `thm:posmix`, `prop:filtered`, `cor:negcfg` | 4 × CORRECT (high) |
| G2 | `lem:signedconv`, `thm:schedule`, `prop:cfgatom` incl. growing schedules | 4 × CORRECT (high) |
| G3 | `thm:composition`, `prop:composition-open` | 4 × CORRECT (high) |
| G4 | `prop:hyperplane` | 4 × CORRECT (high) |
| G5 | `thm:transfer`, `prop:localtransfer`, risk-transfer examples, `prop:atomicity` | 4 × CORRECT (high) |

No verifier found a hole. Their minor notes were then applied: distinct symbols for the speed
bound (V_max), the combined mean (m̄), the guided trace (Θ), the schedule bound (w̄), the
hyperplane direction (ν) and the hard-label offset (ζ); joint continuity of D_x v_Π; the
p-uniform KL bound in the positive-mixture energy; explicit Fatou chain; classical C¹
trajectories and monotone flow maps in the composition proofs; Σλ = 1 and the K = 2 parameter
space in `prop:composition-open`; the maximal-solution argument and the restart at t₀ in the
transfer proofs; scalar c in the risk-transfer examples; and the full atom set
{x¹,…,x^N} with p(dx|y) in `prop:atomicity`. One wording error ("increases" for "decreases")
was caught in self-review before the verifiers ran. The verifier runs are an additional check
on proofs taken from the user's stage-2 document; the closed form and converse in item 2 above
were added during integration and were inside the verified packets.

## Numerical check of the composition theorem

`scripts/composition_counterexample.py` (output `results/theory_composition_20261019/summary.json`)
integrates the exact two-atom composite flow with Radau (rtol 1e-11), switching to the variable
s after τ = 0.5, and stops at the first time an exact sufficient condition from the proof fixes
the limit. The midpoint basin is an interval found by bisection (relative tolerance 1e-12).

| B | w_c | w/w_c ≤ 0.9 | 1.1 | 2 | 10 | w = 1 | w = 3 |
|---|---|---|---|---|---|---|---|
| 1 | 0.7241 | 0 | 0.050 | 0.406 | 0.991 | 0.179 | 0.808 |
| 2 | 0.0760 | 0 | 0.021 | 0.182 | 0.809 | 0.891 | 0.999 |
| 3 | 0.0100 | 0 | 0.008 | 0.069 | 0.396 | 0.987 | > 0.999 |

Four asymmetric perturbations at w = 1 give basin probabilities 0.71–0.86. Numerical roots
match cosh s_u = √w sinh B. An earlier version of the script stopped on an event of a step
function and misclassified some trajectories; it now checks the forward-invariant stopping rules
at the end of fixed chunks. These are numerical evaluations, not part of any proof.

## Build and checks

- `python scripts/check_paper.py --build --build-dir tmp/report-integration-2026-10-19/build`:
  all checks pass; 110 pages; main text ends on page 14; 262 labels.
- `--baseline tmp/report-integration-2026-10-19/main.before.tex`: no reported number, citation
  key, theorem environment, figure or table lost; all 230 original labels present.
- `scripts/verify_paper_numbers.py`: 368 passed, 0 failed. `test_check_paper.py`: exit 0.
  `test_calibration.py`: passed.
- `scripts/build_workshop.py` now carries the setup, `thm:posmix`, `prop:filtered` and both
  proofs into the workshop's spectral-bias appendix; `workshop.tex` compiles to 14 pages with no
  undefined or duplicate references.
- The Bash tool collapses `\\` in heredocs; one table row was damaged that way and fixed.
  Later edits used files written directly.

## Not done

- GPU experiments E2, E3, E6, the CIFAR coverage upgrade (64 images, more masks, split seeds),
  an unbiased energy statistic with a permutation null, and a uniform solver-convergence check.
  E1 is covered only by the existing exact-field stress test; E5 (time to leave the hyperplane)
  was not run.
- The report's target of an appendix of at most 25 pages: the appendix was not cut, because
  that requires choosing which evidence to drop.
- T5 (endpoint weights), a sharp threshold for unbounded guidance, schedules that change sign,
  and the composition theorem beyond two atoms remain open and are stated as such.
- `paper/main.pdf` was not refreshed; the reviewed build is in
  `tmp/report-integration-2026-10-19/build/main.pdf`.
