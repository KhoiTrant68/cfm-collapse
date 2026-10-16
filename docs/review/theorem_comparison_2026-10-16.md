# Bounded closest-work comparison — 16 October 2026

**Superseded in scope by [the deeper novelty audit](novelty_audit_2026-10-16.md).**
That audit adds Benton, the two Liu–Zuazua papers, and explicit prior no-certificate
constructions. Its assessment lowers the standalone novelty of the loss/certificate
part and isolates the intervention/exceptional-basin statements as the main candidate.

This comparison supports a narrower contribution statement. It does not establish priority across the literature or predict acceptance. The canonical mathematical statements are unchanged by this revision.

| Primary source and checked location | Established scope | Boundary of this manuscript's contribution |
|---|---|---|
| [Baptista et al., Theorem 6.4 and discussion](https://arxiv.org/html/2501.15785v2#S6.SS3) | The empirical conditional score uses the training subset with the supplied label. Its value off the empirical label support is unspecified. The discussion of the dynamical result includes Voronoi boundary limits and leaves the measure of their basins open. | Conditional memorisation is prior work. The manuscript analyzes label-field averages and its specified signed guidance, proving convergence and almost-sure atomicity with exceptional basins treated. Fresh-label hard-conditioned errors concern a learned extension. |
| [Dasgupta et al., Sections 3.2–3.3, equations 40–48](https://arxiv.org/html/2603.14135v3) | An interpolatory separable architecture gives point collapse to a weighted training-point average. Indicator-cell conditioning selects subsets and gives mixture dynamics. | It is inaccurate to describe this work as covering only a single-point architecture. The manuscript distinguishes its unrestricted label-noised reference from these architectural cases; generic conditional collapse is not the novelty. |
| [Pfrommer et al., Theorems 2–3](https://arxiv.org/html/2512.18736) | Minimum label-curvature interpolation gives cubic combinations in the discrete-label setting. A uniform-conditioning/Hessian-penalty result gives a Fourier convolution. | The positive probability averages in Proposition `prop:filtered` need not include those combinations. No claim that every smoothness regularizer preserves atoms is justified. The signed theorem covers one specified CFG combination, rather than arbitrary signed interpolation. |
| [Li et al., Proposition 1 and Theorems 1–3](https://arxiv.org/html/2606.08554) | Closed-form empirical velocities, continuous oracle recovery and discretized endpoint-distance bounds under terminal/margin assumptions. | Ordinary oracle memorisation and finite-time Gaussian clouds are established. Label averaging and signed guidance change the field; ordinary marginal recovery does not supply their endpoint probabilities. The manuscript does not identify these probabilities. |
| [Jain et al., Sections 4–5](https://arxiv.org/html/2411.16738v2) | Empirical attraction-basin observations motivate delaying guidance and opposite guidance for learned text-to-image diffusion. | “Guidance can memorize” is already known. The defensible mathematical distinction is an almost-sure endpoint result for exact finite-support fields with fixed finite nonnegative guidance strength. It does not contradict mitigation through learned fields or changing guidance schedules. |

The source comparisons above are deliberately limited. Searches included memorisation with classifier-free guidance, convergence/Voronoi dynamics, and small-loss endpoint counterexamples. Search absence is not a proof of novelty. A broader stability-literature comparison is still needed before claiming the loss counterexample or risk-transfer theorem is the first result of its kind.

## Contribution that the revised text can defend

1. Convergence and almost-sure atomicity for the stated positive label averages and signed CFG fields, including exceptional trajectories, with hard-label all-source convergence in its identifying-label setting.
2. An explicit small-teacher-loss family with nonvanishing endpoint variance, together with a finite-time sufficient certificate under a separate risk-transfer assumption. No uniform regularity claim is added to the counterexample.
3. Independent empirical tests that delimit a moment-based reference: paired new problem seeds, full-law discrepancy, an adaptive-solver check of the extreme extrapolation condition, and a small paired image coverage/solver pilot.

The NW identity, memorisation itself, guidance-related memorisation, and moment-fit agreement should serve as reference material or context rather than carry the novelty claim. The manuscript now adopts that ordering. Its mathematical proofs were preserved, not re-verified from first principles in this editorial pass.
