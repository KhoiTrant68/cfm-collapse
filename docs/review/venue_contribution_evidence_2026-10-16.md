# Contribution and venue evidence — 16 October 2026

Scope: NOT PROOF SOLVING. Read-only inspection of the manuscript and addendum, plus primary-source comparison of closest-work statements and official reviewer criteria. This report does not verify proofs. Proof novelty and priority: NOT_ASSESSED. Retrieval date for every web source below: 2026-10-16. No canonical manuscript edits were made by this audit.

Local evidence inspected: `paper/main.tex` abstract, introduction, contributions and relevant theorem references; `docs/audit/research_agent_2026-10-16/05_Lit_Grounding.md`; and `docs/audit/research_agent_2026-10-16/proof_addendum.tex`.

## Decision

Contribution gate: REVISE for the current manuscript. Existing theory and experiments do not yet establish a convincing ICLR/ICML contribution case. The addendum supplies a plausible stronger nucleus around convergence and almost-sure atomicity under label averaging and signed classifier-free guidance (CFG), conditional on correctness and a separate priority review. This is a research judgment, not an acceptance prediction.

## Inspected primary-source comparison

| Source | Specific statements inspected | Consequence for contribution |
|---|---|---|
| [Baptista et al., 2501.15785v2](https://arxiv.org/html/2501.15785v2) | Sections 6.2–6.3, Theorem 6.4: empirical conditional law restricts to indices sharing the supplied label; unique labels give one component. Off-data-label extension is not defined by that empirical conditioning alone. | Unique-label empirical collapse is known. Gaussian label smoothing supplies a particular extension and weights. |
| [Dasgupta et al., 2603.14135v3](https://arxiv.org/html/2603.14135v3) | Section 3.2, equations 38–41: interpolatory separable architecture collapses to one weighted mean. Section 3.3, equations 44–48: label cells select a training subset and sampling selects its atoms. | Current related-work table's “a point” description misses Case 2. Removing architectural restrictions matters, but conditional subset memorization is already discussed. |
| [Smola, 2605.13386v1](https://arxiv.org/html/2605.13386v1) | Sections 3.1–3.2, Propositions 1–2: empirical OT path is a KDE; exact velocity uses a spatial NW mean, with bandwidth sigma_t/t. | External-label bandwidth differs from clock-dependent spatial bandwidth. Generic kernel identity is established. |
| [Pfrommer et al., 2512.18736](https://arxiv.org/html/2512.18736) | Section 4, Theorems 2–3: conditioning smoothness yields combinations of conditional flows; regularization gives Fourier attenuation 1/(1+lambda times norm(xi)^4). These combinations generally depart from an ideal denoising path. | Close precedent for label resolution and self-guidance. The addendum's specific spectral obstruction and endpoint results are different statements; their priority is unassessed. |
| [Scarvelis et al., 2310.12395](https://arxiv.org/html/2310.12395) | Sections 4.1–4.2 and 5.3, including Proposition 5.1: spatial smoothing changes attraction toward barycenters and yields sampled barycenters. | “Only endpoint noise moves support” needs explicit restriction to the interventions analyzed in this paper. It cannot describe all regularization. |
| [Bertrand et al., 2506.03719](https://arxiv.org/html/2506.03719) | Section 2, Proposition 1/equation 6: empirical optimal velocity is a softmax combination of directions toward training samples; resulting memorization is explicitly discussed. | Separate latent-endpoint conditioning in CFM from external observed labels. Closed-form empirical velocity and memorization are background. |
| [Li et al., 2606.08554v1](https://arxiv.org/html/2606.08554v1) | “Optimal Generation and Discrete Sampling,” Proposition 1, Theorems 1–2: empirical oracle recovery and finite-step deviations around atoms; later sections treat estimation error. | Off-atom distance needs numerical controls before attributing it to learned-field error. Ordinary oracle interpolation is distinct from the addendum's averaging and signed-CFG setting. No source proof was used as a certificate for a local proof. |

Precision about the Gaussian-label NW endpoint family: these sources establish closely overlapping empirical conditional laws and construction ingredients. This bounded inspection did not locate an identical externally conditioned Gaussian-label NW endpoint theorem in these seven papers. Bayes reweighting of a fixed empirical joint law plus exact transport is nevertheless a standard construction, and the local literature audit treats the family as known. Present it as a useful exact reference from established machinery; do not claim an exact prior theorem without a direct supporting citation, or claim first discovery from this search.

## Plausible residual nucleus (proof correctness and novelty unassessed here)

- Hard conditioning under CFG: every finite source point reaches the designated atom for each finite w >= 0, with an explicit rate bound and no tie/convergence premise. This is stronger in scope than an unguided collapse observation.
- Averaging over labels: convergence for positive measurable coefficients without log-integrability, followed by atomic endpoints almost surely under an absolutely continuous source. Exceptional tie trajectories remain possible.
- Signed CFG: all trajectories converge, and endpoints are training atoms almost surely, with fixed strictly positive conditional weights, uniform unconditional weights, and finite w >= 0. Endpoint probabilities are not identified.
- Sharp spatial Lipschitz floor d/(3L): an exact optimization statement for its specified class and sampling assumptions; a supporting result whose ML significance needs a connection to measured regularity or capacity.
- Spectral obstruction: the specified continuum multiplier is not a probability characteristic function. This limits a positive-kernel mechanism interpretation; it does not establish that a trained network equals a Gaussian label mixture.

The averaging/signed-CFG results can form one coherent contribution: which conditioning interventions preserve empirical atomicity despite changing trajectories and endpoint weights. The current abstract and contributions still center the older reference law and moment-fit story. The addendum explicitly remains separate from the manuscript.

## Three decisive experimental gaps

1. Distribution-level independent validation: fit bandwidth separately, then compare full held-out laws using a prespecified distribution metric against Gaussian/Laplace/Cauchy/kNN and free baselines, with independent seeds. Mean and trace agreement do not identify a law. The existing leave-one-condition trace analysis is post hoc and has three independent problem seeds.
2. Intervention study aligned with the new theory: compare hard conditioning, positive label smoothing, averaging of fields over labels, and signed CFG over guidance strengths. Include exact-oracle and trained fields, repeated seeds, atom distances, atom frequencies and diversity. Do not conflate these interventions.
3. Numerical versus learned-field control: sweep terminal time and step size/tolerance for oracle and learned fields. Establish which off-atom spread survives numerical convergence and whether it predicts calibration or distribution quality better than free diagnostics.

## Official venue criteria

[ICLR 2027 Reviewer Guidelines](https://iclr.cc/Conferences/2027/ReviewerGuidelines), “Reviewing a submission: step-by-step”: assess supported claims, sufficient community value and new knowledge. State-of-the-art results are not required.

[ICML 2026 Reviewer Instructions](https://icml.cc/Conferences/2026/ReviewerInstructions), “Strengths and Weaknesses”: evaluate soundness, presentation, significance and originality separately. Soundness is explicitly distinct from impact; removal of restrictive theoretical assumptions can count as originality. Correct theorems alone therefore do not settle the current significance or empirical gaps.

## Verified Baptista bibliographic metadata

Primary metadata source: [arXiv abstract record, version 2](https://arxiv.org/abs/2501.15785v2), retrieved 2026-10-16.

- Exact title: Memorization and Regularization in Generative Diffusion Models.
- Authors, in source order: Ricardo Baptista; Agnimitra Dasgupta; Nikola B. Kovachki; Assad Oberai; Andrew M. Stuart.
- Year: 2025. Identifier: arXiv:2501.15785v2 [cs.LG].
- First submission: 27 January 2025. Version 2 revision: 18 March 2025.
- DOI: https://doi.org/10.48550/arXiv.2501.15785.

Suggested fields (no journal or proceedings venue inferred):

```bibtex
@misc{baptista2025memorization,
  title = {Memorization and Regularization in Generative Diffusion Models},
  author = {Baptista, Ricardo and Dasgupta, Agnimitra and Kovachki, Nikola B. and Oberai, Assad and Stuart, Andrew M.},
  year = {2025},
  eprint = {2501.15785},
  archivePrefix = {arXiv},
  primaryClass = {cs.LG},
  doi = {10.48550/arXiv.2501.15785},
  url = {https://arxiv.org/abs/2501.15785v2},
  note = {Version 2, revised 18 March 2025}
}
```
