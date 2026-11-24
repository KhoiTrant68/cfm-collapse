# Revision response: paper A (2026-11-25)

This file answers the roadmap in `editorial_decision.md` and two further points from an outside critique of an earlier review. Every change is in `paper_theory/main.tex` (and `refs.bib`) unless stated otherwise. The TMLR build compiles to 59 pages with no undefined references and no overfull boxes. `submit/build.py A_tmlr` passes, including its leak scan.

## Required revisions

| Item | Status | What changed |
|---|---|---|
| R1 positivity qualifier; h = 0 | Done | The abstract, introduction, contribution 3, conclusion, Limitations and broader-impact statement now restrict the counting rule to strictly positive priors. §5.1 proves in one line, from Prop. collapse(a), that a fixed average of hard-label fields sends every source to the weighted average of the atoms in every geometry. The wrong §5.6 remark ("only in configurations such as the symmetric tie") and the Table 1 row are corrected. The hard-label conjunction is stated as not analysed; the paper makes no claim about it. |
| R2 composition framing; scope to the exact optimum | Done | "Boundary marker, not a practical mechanism" is gone. The practice paragraph now opens by saying that every statement concerns the exact optimum and that the trained networks are not at it. Item (iii) says that practical guidance strengths exceed w_c and that it is open whether trained samplers blend. The conclusion's "operation an audit should examine" is replaced by a conditional statement, and an audit of a trained sampler is said to need its own measurement. |
| R3 positive control | Done | `scripts/stress_positive_control.py` now runs both field codings. Output: `results/stress_positive_control_20261125/`; the 2026-11-21 run is kept. The logit coding reproduces the exact basins (0.049, 0.410, 0.988) only through rounding: captured trajectories reach \|x_1\| ≈ 1e-17, while the step is about 27× past RK4's stability bound at w = 2 w_c. The blow-up coding ejects them: 0 at every strength, except 0.049 at 1.1 w_c, 512 steps, gap 1e-2, and the 1 % criterion flags nothing. §6 (retitled "The stress test cannot see an attracting tie"), contribution 6, Limitations and the artifacts list now say that the stress test does not detect attracting ties, and that every number with an attracting tie comes from the stiff integrator with proof-derived stopping rules. |
| R4 LLM statement | Done | The author confirmed that they wrote and checked every proof line by line. The statement says so (separate commit). |
| R5 leakage criterion | Text done; analysis not done | Practice item (iii) says that single-record criteria ((ℓ2, δ)-extraction, the nearest-neighbour ratio test used in §6) classify a two-image midpoint as new. It also gives the reconstruction argument 2z − x^i. **Not done:** counting how many of the off-atom CIFAR-10 samples (0.168, 0.276) lie near a pairwise training midpoint. This needs the stored s10 endpoints. |
| R6 threat model | Done | Item (ii) and the broader-impact statement name the required knowledge (training labels, h, query), say who typically holds it (the model owner), and say that the ranking does not transfer to the trained image networks. Under guidance no ranking follows. |
| R7 learned-field contribution | Text done; experiment not done | Contribution 5 is retitled "A diagnostic for learned fields". It states the toy scale (d ≤ 2, three to five seeds), that the tie location is supplied, and that this "shows that the basin is learnable when its location is known, not that trained samplers find it". The abstract says "centred at a tie given in advance". **Not done:** a learned conjunction at moderate dimension. |

## Suggested revisions

| Item | Status | What changed |
|---|---|---|
| S1 restructure the introduction | Not done | Kept the six-item contribution list; the framing changes are under R2 and R7. |
| S2 literature | Done | Added and cited: Bradley et al. 2025, Skreta et al. 2025, Miglior et al. 2026 (CompFlow, ICML 2026 CompLearn workshop, cited by title only; its PDF could not be read), Wu et al. 2024, Chen et al. 2024 (anti-memorisation guidance, placed under Cor. twofields), Vastola 2025, Duan et al. 2023, Matsumoto et al. 2023 and Dockhorn et al. 2023. The previously uncited Carlini et al. 2023, Somepalli et al. 2023 ("Diffusion Art") and Sesmat et al. 2026 are now cited. A new related-work paragraph, "Replication, membership and privacy", covers them. Pavasovic et al. 2025 was not added (its identifier was not found) and neither was Liu et al. 2025 (oracle velocity). |
| S3 w_c notation | Done | The notation table defines w_c as the threshold of the configuration at hand (1/sinh²B for two atoms, w_c^spec for the simplex and the triangle). The Figure 2 caption states w_c = w_c^spec = 1.160. |
| S4 spectral qualifiers in the abstract | Done | "at hyperbolic profiles, which are generic in the priors", also in contribution 3. |
| S5 Prop. regular(b) | Done | The statement is made for states at t_0, with a linear-growth condition on [0, t_0] that transfers it to initial points at t = 0. The proof adds the homeomorphism step. |
| S6 CIFAR departure | Unchanged | The departure is still reported as unexplained, and is now restated beside the practice claims. |
| S7 "closer fit" | Done | Labelled "a hypothesis the exact field suggests; we do not test it". |
| S8 endpoint noise and DP | Done | ρ/√M averaging over repeated queries; guarantees come from private training (Dockhorn et al.). |
| S9 dual use | Done | The broader-impact statement covers guidance as a possible extraction amplifier and composition thresholds as indicating which pairs blend. |
| S10 delta over Liu et al. in the main text | Not done | The comparison table remains in Appendix B.1. |
| S11 §6 density; random pairs | Partly done | The main text now gives the CIFAR composition means: 0.186 over the eight selected pairs and 0.042 over the twelve random ones. The paragraph restructuring and table moves were not done. |
| S12 shorter abstract | Not done | The abstract grew slightly because of the R1 and R2 qualifiers. |
| S13 small fixes | Done | Figure panels are cited as (a)/(b). The "All proofs are in the appendices" sentence names the exception. The abstract presents field averaging as a sampler operation (the bottleneck proposition gives prior averaging). |

## Points from the outside critique

| Point | Status | What changed |
|---|---|---|
| "Exactly when w > w_c" for CIFAR (appendix) | Done | Now states Pr = 0 for w < w_c (the only profile is hyperbolic with F′ > 0) and Pr > 0 for w > w_c. The value w = w_c is not covered for the full 2000-atom field, and no run uses it. §6 says the same. |
| "Reproducing the exact threshold requires an unbounded derivative" (§5) | Done | The smooth counterexample ḡ = 2 tanh x, g_u = (2 + 1/w_c) tanh x, with g_w′(0) = 2 − w/w_c, is given in the text. The unbounded-derivative requirement is now stated only for following the exact flow on the shrinking layer \|x\| ≲ (1−t)². |
| Learned image composition, a robustness theorem for learned fields | Not done | These would be new experiments or theorems, outside this revision. |

The panel reports and the decision letter are unchanged: they record the version that was reviewed.
