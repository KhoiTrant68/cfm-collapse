# Bounded integration claim review

Verdict: PASS after verified correction of the source-comparison wording. This is local revision acceptance, not whole-paper publication readiness. No canonical file was edited.

## Frozen inputs

SHA256 of inspected `paper/main.tex`: `1b8857adb525138f189583f88c0676fb2437b2eb2e3c2cf6039e2343c9926ce3`.
SHA256 of `main.tex.before`: `c38aacedd1b31a9c11838a7c85244c76331357605e86286bb67bdff4db178cf4`.
SHA256 of `review-packet.md`: `1733f0f3c0f7cd1f6ffa62f3331fd14d1c30b6ceeddd5df8832e1e9b0cc52e8f`.
SHA256 of `summary.json`: `f033c4a10c4cbfef10234597f7186081424f27975e6433c530e3519049cb8402`.
SHA256 of `SUMMARY.md`: `0c398885316955629274147b39c22c1793abc8813966c27fbbc3ac13a18d8a36`.
SHA256 of `scripts/novelty_interventions.py`: `096a6b42e0038787525206ee453816918968dcd4bc51a590046612b2d564dc5d` (matches manuscript and all three primary result metadata records).
SHA256 of `scripts/novelty_ties_refined.py`: `b8f7aa40c756fe8b5bf308968df065e0e30697a63b0fed8aee3174777675a08e`.

Scope: added title/abstract/contributions, closest-convergence prose/table, Section 3.3 explanatory prose, Section 4.2 and final protocol appendix. Formal block equality is assigned to the root reviewer. I compared explanations with the supplied frozen proof packet, without replacing the separate proof audit. I also opened the existing null-basin review incidentally; the conclusions here about the prose follow directly from the packet and sources.

## Required correction (CLOSED)

**[P2, blocking source fidelity] Lines 130–132 and table row at line 167 reverse a theorem hypothesis into a conclusion.** The text says Liu–Zuazua give a criterion “that excludes” nonminimising critical points; the table says “criterion excludes”. Their Theorem 3.18 instead ASSUMES that the particular original trajectory's omega-limit set has no such points, and concludes convergence to a local minimizer. Remark 3.19 expressly distinguishes this hypothesis from a property proved there. The subsequent phrase “leave almost-everywhere avoidance open” is correct but does not repair the table's standalone misstatement.

Minimal correction to prose: “give an original-flow convergence criterion assuming that the omega-limit set contains no nonminimising critical point, and leave almost-everywhere avoidance open in that setting.”

Minimal table correction: “Original-flow convergence conditional on exclusion of nonminimising critical limit points”.

Primary evidence: [Theorem 3.18 and Remark 3.19](https://arxiv.org/html/2605.12231#S3.Thmtheorem3.18) (HTML theorem text and following remark, inspected directly).

## Optional precision correction

**[P3, nonblocking] Line 475: “Both proofs first use a time-dependent log-partition energy” omits the hard-label part.** Both positive-bandwidth arguments do this, but CFG part (b) directly uses the Gibbs/entropy bound and a scalar differential inequality. Minimal correction: “For positive bandwidth, both proofs first use ...”. No mathematical result changes.

## Claim classification

| Added substantive claim | Classification | Evidence / limit |
|---|---|---|
| Title and abstract: averaging and fixed finite nonnegative CFG preserve almost-sure atomic endpoints; every trajectory converges; non-atom basins are null; hard identifying CFG reaches its atom from every point | Supported relative to frozen propositions and supplied proofs | The prose retains exact fields, absolute continuity, positive bandwidth, and finite fixed nonnegative guidance. It does not imply atomicity at exceptional points. |
| Arbitrary averaging probability measure needs no moment or bounded-support condition | Supported | Finite atom bounds dominate softmax means and spatial derivatives; pointwise positive-coefficient concentration passes through bounded convergence. The packet's averaged log-partition is bounded between finite logits. |
| Common positive support and unidentified endpoint weights | Supported | Gaussian label kernel is everywhere positive; proposition only gives existence of mixture weights. |
| Field averaging differs from averaging priors/endpoint laws | Supported | Nonlinear normalization prevents commutation; paired assignments differ up to 0.3125 in supplied 40 comparison records. No identification of endpoint weights is claimed. |
| Positive covariance / signed covariance, expansion, change of variables and Fatou proof sketch | Supported with optional precision above | Packet gives exactly these positive-bandwidth mechanisms. Signed trace need not be pointwise positive, and new prose correctly specifies integration over late unit intervals. |
| Ordinary score-flow compact-support almost-everywhere convergence, Liu–Zuazua v3 Theorem 3.7 | Supported | [Primary source](https://arxiv.org/html/2511.05940v3): Theorem 3.7(i), with empirical strengthening (iii). Table correctly says convergence into support, not recovery of target weights. |
| Mixed-score criterion and open generic avoidance | Partly supported; required correction above | Hypothesis/conclusion direction must be explicit. Common finite-support intervention result is correctly distinguished from their potentially different-support setting. |
| Loss obstruction is known; Benton et al. use learned-field Lipschitz control | Supported | [Theorem 1 and Section 3](https://arxiv.org/html/2305.16860v2): W2 error bound depends on L2 error and integrated approximate-field Lipschitz constant; preceding discussion already describes arbitrarily small L2 error with large flow error. |
| Beltran-Velez et al. Appendix D supplies small-teacher-error / poor-reward examples | Supported | [Appendix D.1](https://arxiv.org/html/2606.19162): Proposition D.1 constructs Gaussian variance inflation and reward failure; later construction covers target-flow coordinates. Revision appropriately calls the local fixed singular target an illustration, not a new general obstruction. |
| 200 exact cells, 128 paired sources, seeds/dimensions/atoms/bandwidths/arms, gap and RK4 step counts | Supported | 5 seeds x 2 dimensions x 2 geometries x 2 bandwidths x 5 arms = 200 terminal cells; 600 rows across three gaps. Script and stored args agree. Near-duplicate location change is distance 0.02. |
| Exact terminal maximum cellwise q95 6.11937e-6; displacement 7.54797e-13; no assignment disagreement / outside threshold; 31.25% field/prior assignment difference | Supported by stored summary | Matches summary.json/SUMMARY.md. Prose limits these to finite-time consistency, not a null-basin or convergence proof. Roundoff recomputation maximum 1.56697e-10 matches reported 1.57e-10. |
| Symmetric zero-source midpoint and hard-label-average midpoint | Supported analytically and by protocol | Paired tanh means cancel at zero; hard identifying means average to zero, so original-time field is -x/(1-t). This is a valid demonstration that the positive-bandwidth averaging theorem cannot extend unchanged to hard fields. |
| 81 primary tie trajectories, four gaps; 84 follow-up rows, seven gaps through 1e-18, four of six adaptive failures | Supported | Primary 9 initial values x 3 bandwidths x 3 arms = 81 trajectories (324 rows). Follow-up 4 x 3 x 7 = 84 rows. Stored failure flags and tolerances agree. Max fixed refinement displacement directly checked: 0.000325231161754758. Incomplete adaptive integrations are explicitly disclosed. |
| Five learned models, radii, query/source seeds, 60 cells, float32 original-time network / double exact log-time protocol | Supported | Evaluator and stored args agree: 5 x 4 queries x 3 radii; 400/800 network steps; 768/1536 exact steps; T=.999. |
| Learned energy table, seed ranges and fresh nearest distances | Supported by stored summary | All displayed numbers round correctly. Means are seed means with queries nested. Normalization is sqrt(analytic posterior trace), exactly as implemented. |
| Learned averages do not automatically inherit exact atomicity; increasing discrepancy is descriptive, not universal over seeds | Supported and appropriately limited | Table supports increasing group means, and text explicitly notes seed variation. V-statistic is biased, has no null subtraction or equivalence threshold, and is not used to certify endpoint behavior or posterior quality. |
| Largest exact-reference cellwise mean solver displacement 6.89e-7 | Supported by direct JSON check | Maximum over 60 stored learned rows is 6.88932531634412e-7. Group network ranges round as stated. |
| All 984 primary rows and 84 follow-up rows independently recomputed | Supported as a provenance report | Primary metadata totals 600+60+324=984; summary reports checked status; refinement verification artifact exists. This review checked summaries, protocol, metadata and selected direct JSON aggregates, and did not independently recompute all raw arrays. |

No blocking mathematical reinterpretation, notation error, experimental-number discrepancy, or numerical-certification overclaim remains in the bounded added prose. The P3 wording is an optional precision improvement.

## Correction verification

Re-read canonical main.tex after the root reviewer correction. Final inspected SHA256: 580a0de0f0fd93d56edb3398cd4b00de8b50292cccf282499805ddc38a1bdde1. The prose now explicitly says the criterion assumes absence of nonminimising critical points from the omega-limit set; the table says original-flow convergence assumes no such limit points. Both correctly represent Theorem 3.18 and Remark 3.19. Required source-fidelity correction is CLOSED. The refinement verification.json was also read and confirms 84 rows, 2/6 adaptive successes and maximum available adaptive/fixed difference 4.2048663728699864e-7. No blocking issue remains for this local revision acceptance.


## Final binding and P3 closure

Verified canonical `paper/main.tex` SHA256: `6c0e59bffac4798947c7e3ff2c6e552e9a96b9fe03acf838f91e9de5018ce4d4`.
Re-read the changed proof-sketch sentence: “For positive bandwidth, both proofs first use a time-dependent log-partition energy to establish ...”. This is the requested precision correction and accurately limits the sketch to the positive-bandwidth arguments. P3 is CLOSED. All findings in this bounded claim review are closed; final verdict remains PASS for local revision acceptance only.
