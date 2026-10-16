# Atomicity proof audit and manuscript integration — 17 October 2026

Scope: execute the accepted proof review, novelty revision, and integration of the completed intervention experiments. This is a bounded revision, not a whole-paper publication audit or an ICLR submission conversion. The canonical source is `paper/main.tex`.

## Mathematical review

The frozen input source SHA256 is `c38aacedd1b31a9c11838a7c85244c76331357605e86286bb67bdff4db178cf4`; the full proof packet SHA256 is `1733f0f3c0f7cd1f6ffa62f3331fd14d1c30b6ceeddd5df8832e1e9b0cc52e8f`. Snapshots and reviews are retained in `tmp/atomicity-integration-2026-10-16/`.

Three independent fresh-context reviewers examined the exact statements and proofs, not author summaries:

| Reviewer | Scope | Finding |
|---|---|---|
| `audit_label_average` | Positive label averaging, arbitrary averaging measure | HOLDS; no substantive gap found |
| `audit_signed_guidance` | Signed CFG covariance, convergence, hard-label endpoint | HOLDS; no substantive gap found |
| `audit_null_basins` | Both proofs, geometry and measure-zero basins | HOLDS; no substantive gap found |

Checks included differentiation under arbitrary label averaging, concentration without uniform label-prior ratios, finite candidate sets inside affine hulls, residence-time arguments supplementing finite energy, covariance positivity on a compact simplex, finite-time diffeomorphisms, and the change-of-variables/Fatou argument.

For signed guidance, the reviewers checked the covariance identity and the control of its negative term over complete late unit intervals. Jacobian divergence along integer times suffices for Fatou; arbitrary partial intervals need not have positive signed covariance. Hard-label guidance uses the correctly signed Gibbs/entropy inequality and gives convergence from every finite source point.

No repair to a formal statement or proof was required. This is independent reasoning review, not formal verification. All 78 theorem/proposition/lemma/corollary/assumption/proof blocks are preserved verbatim as a multiset after newline normalization; only the two proposition statements moved. Macros are unchanged. The two results now appear in Section 3.3 as Propositions 6 and 7, with their original complete proofs in Appendices E.2 and A.23.

## Contribution and literature revision

Title, abstract, contributions, closest-work table, interpretation, and conclusion now emphasize convergence and almost-sure atomicity after positive label averaging and fixed finite nonnegative CFG on a common finite support. Endpoint probabilities remain unidentified. No priority or acceptance claim is made.

The fixed-target small-loss example is presented as a specialization illustrating a known obstruction. The risk-transfer theorem is a sufficient coupling/variation-of-constants certificate; the text no longer says every loss certificate must assume risk transfer directly.

Primary sources checked:

- [Liu and Zuazua, A PDE Perspective on Generative Diffusion Models, v3](https://arxiv.org/html/2511.05940v3): Theorem 3.7, ordinary-flow almost-everywhere support recovery. Bibliography records the October 7, 2026 revision rather than attributing the checked version to the original 2025 submission alone.
- [Liu and Zuazua, Geometric Asymptotics of Score Mixing and Guidance, v1](https://arxiv.org/html/2605.12231): Theorem 3.18 assumes the omega-limit set excludes nonminimising critical points; Remark 3.19 leaves the corresponding almost-everywhere avoidance unresolved. A final independent review caught ambiguous wording that could sound like the theorem proved that exclusion. Both prose and table now explicitly say it is assumed.
- [Benton, Deligiannidis and Doucet, Error Bounds for Flow Matching Methods](https://arxiv.org/html/2305.16860v2): learned-field regularity in endpoint bounds, and the regression-error obstruction.
- [Beltran-Velez et al., The Reward Was in Your Data All Along](https://arxiv.org/html/2606.19162): Appendix D, small teacher-error/generated-reward counterexamples. The paper does not claim that this exactly subsumes our singular-target Wasserstein construction.

The independent post-integration review and its exact source binding are saved in `tmp/atomicity-integration-2026-10-16/review-integration-claims.md`. Its required source correction and optional positive-bandwidth qualification are closed, with PASS at final source SHA256 `6c0e59bffac4798947c7e3ff2c6e552e9a96b9fe03acf838f91e9de5018ce4d4`.

## Experiment integration

Section 4.2, Table 2, Figure 2, and Appendix G integrate the already completed server experiments. No new training was launched during this revision.

- Exact stress test: five geometry seeds, 200 paired cells, dimensions 2/8, random/near-duplicate geometry, positive averages, prior averages, and CFG. Largest cellwise q95 nearest-atom distance at gap 1e-6 is 6.11937e-6; largest mean coarse/fine displacement is 7.54797e-13. No observed threshold violations or assignment changes under refinement. These are finite-time checks, not support proofs.
- Tie controls: exact symmetric zero source remains a non-atom exceptional trajectory; the hard-label average is explicitly outside the positive-bandwidth theorem. Four of six adaptive follow-ups failed; failures and partial outputs remain visible. No certified adaptive convergence is claimed for them.
- Learned averages: reuse five existing h=0.1 checkpoints, with paired sources and exact averaged-field references. Wider averaging increases mean discrepancy, not every seed's discrepancy. The biased energy V-statistic is not null-corrected or an equivalence test; no posterior-quality improvement is inferred.

984 primary metric rows and 84 refinement rows were previously recomputed from raw arrays. Provenance, scripts, and limitations are retained in [the experiment report](novelty_experiment_results_2026-10-16.md) and the results directory. Primary and posthoc refinement remain separate.

## Acceptance and remaining scope

- Existing numerical validation: 359 checks passed, zero failed.
- Formal block preservation, unique labels, resolved internal references, bibliography keys, source/build equality and clean LaTeX reference checks: `tmp/atomicity-integration-2026-10-16/verification.json`.
- Isolated pdflatex/BibTeX build; no undefined citations/references, overfull boxes, or oversized floats. Existing hyperref warnings strip math delimiters from two older appendix bookmarks; existing underfull boxes concern spacing, not clipped content.
- Editor visually checked changed pages and neighbours: 1–3, 5–9, 12–17, 46–47, 51, 93–94. Later local corrections were re-rendered at the affected pages. This is not a visual review of every page of the 94-page paper.
- Current PDF uses TMLR style; main content extends into page 14. ICLR template conversion, substantial compression, and a full final publication audit remain a separate revision. No claim that the paper now meets ICLR acceptance standards follows from these checks.

Final source and PDF hashes are recorded in the verification JSON. The canonical deliverable is `paper/main.pdf`, SHA256 `fd3544ad19be3ad3240fdb5a06fbc79150da0cd12517c462834ec185e241bbff`.

## Subsequent remote integration for commit/push

The audit and hashes above bind the pre-merge manuscript committed as `26d812a`.
Before pushing, origin/main had three additional commits through `0c83cce`.
Their updates were merged while preserving the audited abstract, contribution
framing, mathematical statements/proofs and diagnostic limitations. The remote
changes bring two existing bandwidth figures into the main text and use the
rank-based image coverage numbers in that text. The exact finite-sample rank
reference is qualified by tie-free scores or randomized ties. The assertion
checking an older abstract phrase now checks the same coverage range at its
current location in the body.

After conflict resolution, all formal blocks still match the frozen mathematical
surface. The expanded numerical suite passes 368 checks, and
`scripts/test_calibration.py` passes. The merged PDF compiles to 95 pages, with
main content through page 15; no undefined references/citations, overfull boxes
or oversized floats are reported. This supersedes the earlier 94-page output
and its PDF hash; the earlier independent mathematical/prose audit remains
bound to its named source revision rather than being relabelled as a full audit
of the merge.
