# Independent whole-paper source audit — 17 October 2026

Read-only review of `paper/main.tex`, SHA256 `A0F319683CEE5B0390D29757974B435F7E23623BEA86732A62C6B472A47B351C`, and `paper/refs.bib`. No manuscript or bibliography edits. Line references below refer to this hash. I independently extracted 40 distinct cited keys from 45 bibliography entries and browsed primary sources afresh; no earlier audit verdict was used.

## Findings requiring repair

### R01 — P2: Smola's bandwidth is misreported

**Locations:** main.tex:106–110 and 3095–3100. **Evidence:** [Smola, §2 and Propositions 1–2](https://arxiv.org/html/2605.13386), especially equations (4)–(5), uses query `x/t`, fixed support points, and bandwidth `sigma_t/t`. With zero terminal noise this is `(1-t)/t`. The manuscript states `1-t` without explaining that its spatial kernel is instead centered at the moving points `t x^i` in the original coordinates.

**Smallest repair:** state both coordinate conventions: “the spatial posterior factor is a kernel on the moving centers `t x^i` with scale `1-t`; Smola expresses it on the fixed atoms at query `x/t`, with bandwidth `(1-t)/t`.” Preserve the substantive spatial-versus-label distinction. Do not attribute the `1-t` convention directly to Smola.

### R02 — P2: CADS comparison identifies two different interventions

**Location:** main.tex:3118–3121. **Evidence:** [CADS abstract and sampling method](https://arxiv.org/html/2310.17347) specify scheduled Gaussian perturbation of the condition **during inference**, using a pretrained model. The endpoint theorem here concerns the exact minimizer after a fixed training-label corruption. No argument establishes their equivalence.

**Smallest repair:** replace “that the restored variance is an exact … mixture” with “for fixed Gaussian label noise in the training objective, we identify an exact … mixture; the time-dependent inference intervention of CADS is outside this theorem.” The introduction at 112–115 already describes the practical method accurately.

### R03 — P2: Zador's asymptotic factor is presented like a finite-sample floor magnitude

**Locations:** main.tex:420–425, 3167–3170, 3186–3188. **Evidence:** [Graf–Luschgy book record](https://link.springer.com/book/10.1007/BFb0103945) verifies metadata, but subscription content prevented direct inspection of its Theorem 6.2. [Graf–Luschgy–Pagès, §1 and equation (2.3)](https://numdam.org/item/10.1051/ps:2007044.pdf), by the quantization authors, explicitly gives the `r+eta` moment condition and a distribution-dependent asymptotic constant. For `r=2`, the Gaussian example satisfies this condition. The bare factors `0.071` and `0.9975` are not numerical lower bounds for the error. Arbitrary “intrinsic dimension” replacement also needs extra support-regularity assumptions.

**Smallest repair:** specify the moment hypothesis, label those numbers “exponent factors only,” and restrict the quoted theorem to a nonzero absolutely continuous part in the stated Euclidean dimension. Keep the fixed-atom-versus-optimal-quantizer direction, which is correct. Retain image intrinsic dimension only as a conditional heuristic.

### R04 — P2: General caption randomisation is equated with Gaussian label smoothing

**Location:** main.tex:3114–3117. **Evidence:** [Somepalli et al., §7](https://arxiv.org/html/2305.20086) treats multiple captions, Gaussian embedding noise, caption replacement, token changes, repetition, and random numbers, with both training and inference interventions. Only the fixed Gaussian training-embedding-noise special case has the precise additive-noise form considered here.

**Smallest repair:** say “Gaussian perturbation of a fixed text embedding during training is a special case of our label-noise construction; the other caption interventions are related motivations.” Avoid claiming the theorem identifies endpoints of arbitrary caption randomisation.

### R05 — P2: Gradient-variance source does not establish conditional calibration collapse

**Locations:** main.tex:83–85; compare 2654–2657, 2700–2704, 2893–2900, 4654. **Evidence:** [Reu et al., §4.1 Proposition 2 and §4.3 Tables 2–3](https://arxiv.org/html/2510.18118) concerns fixed deterministic source–target pairings, ReFlow, and unconditional CelebA experiments. “Conditional flow matching” there is the CFM training construction, not an external observation-conditioned posterior. Its claim about injected interpolant noise is also different from resampling the source every epoch; the latter has a direct argument in this manuscript but was not located in the source.

**Smallest repair:** cite `physicscfm2026` alone for the introductory conditional posterior claim. At 2654–2657 describe Reu's stochasticity/noise mechanism precisely rather than naming its remedy “resample-x0.” Keep Proposition 2 as the antecedent for finite-pair zero-loss interpolation. At 2700–2704 say “adapts a finite-batch representability argument and adds an exact non-representability observation”; 2893–2900 already makes that distinction much better.

### R06 — P2: Generic fixed-kernel dynamics need not learn Fourier low frequencies first

**Location:** main.tex:3853–3855. **Evidence:** [Jacot et al.](https://proceedings.neurips.cc/paper/2018/hash/5a4be1fa34e62bb8a6ec6b91d2462f5a-Abstract.html) supplies NTK gradient dynamics; [Rahaman et al.](https://proceedings.mlr.press/v97/rahaman19a.html) investigates neural-network spectral bias and the effect of data geometry. Neither says an arbitrary fixed positive-definite kernel has eigenvalues ordered by Fourier frequency. The displayed dynamics learns large-eigenvalue modes first. A Fourier interpretation requires a suitable translation-invariant design/kernel and frequency-ordered spectrum.

**Smallest repair:** write “learns modes with larger kernel eigenvalues first; we investigate a spectral-bias model motivated by Rahaman et al.” State the additional spectral hypothesis exactly where Fourier resolution is inferred.

### R07 — P3: Classical NW references exist in BibTeX but are never cited

**Locations:** main.tex:148, 342, 1766–1807. `nadaraya1964estimating`, `watson1964smooth`, `tsybakov2009nonparametric`, and `gyorfi2002distribution` are unused. The first two primary metadata records are [Nadaraya/SIAM](https://epubs.siam.org/doi/10.1137/1109020) and [Watson/JSTOR](https://www.jstor.org/stable/25049340). The manuscript proves its own rate assertion, so this is provenance/reader guidance rather than an unproved imported theorem.

**Smallest repair:** cite the original NW papers at the first estimator definition and a precisely checked rate reference if desired; do not add an unchecked chapter citation merely to make the bibliography appear complete.

### R08 — P3: Published Sesmat title differs from the preprint title

**Location:** refs.bib, `sesmat2026leaks`. [The ICML2026/PMLR record](https://proceedings.mlr.press/v306/sesmat26a.html) has “Characterising **the** Membership Signals Along the Interpolation Path,” whereas the entry uses the arXiv title without “the.” The authors/year are correct. **Smallest repair:** when citing the published version, use its exact title and optionally PMLR306:109269–109293; alternatively identify the entry consistently as the preprint.

## Important checks that passed, and their limits

- **Conditional antecedent:** [Baptista v2, Theorem 6.4 and its following paragraph](https://arxiv.org/html/2501.15785v2), lines 782–789 of the web rendering, explicitly restricts the conditional score to observations in the marginal dataset and discusses singleton-label memorisation and undefined off-support behaviour. This supports main.tex:100–103 and 247. The displayed score formula in the source appears to have sign/normalization peculiarities; the manuscript does not import that formula, so this is not a manuscript defect.
- **Architecture comparison:** [Physics CFM, §3.2 equations (32)–(41), §3.3](https://arxiv.org/html/2603.14135) supports the partition-of-unity collapse to a barycenter and the cell-conditioned training-subset mechanism at 85–86, 102–104, 3101–3109. These are explicitly architecture-restricted, as the manuscript says.
- **Closest convergence results:** [PDE v3, Theorem 3.7(i)–(iii)](https://arxiv.org/html/2511.05940v3) supports 128–129 and table166: compact support, almost-everywhere support convergence, empirical rate. [Geometric v1, Theorem 3.18 and Remark 3.19](https://arxiv.org/html/2605.12231v1) supports 130–137 and table167. Its §7.4 proves convergence for **autonomous limiting inclusions** (Theorem 3.16); it does not remove the original-flow premise in Theorem 3.18. No stronger priority claim should be inferred from that section.
- **Scheduled CFG boundary:** [Analytic Distribution of CFG, Theorem 4.3](https://arxiv.org/html/2607.19725), inspected although not cited, assumes positive smooth densities on a finite interval with `t0>0`, a unique C1 flow, normalizable product, and finite path integrals. It does not directly prove singular zero-noise atomic endpoint behaviour. The current manuscript's explicit exclusions of arbitrary schedules are appropriate; adding this reference would improve context but is not a demonstrated priority defect.
- **Label-Hessian regularisation:** [Pfrommer et al., Theorems 2–3 and Appendix A.4](https://arxiv.org/html/2512.18736) has cubic-spline combinations for finite scalar labels and the Fourier multiplier `1/(1+lambda|xi|^4)` for uniform conditioning. The manuscript correctly avoids treating every such combination as a positive average. The NeurIPS title differs from the arXiv title; the BibTeX note explicitly records this.
- **Risk versus endpoints:** [Benton v2, Theorem 1, Assumptions 1–3 and §3](https://arxiv.org/html/2305.16860v2) makes the learned-field Lipschitz integral explicit. [Beltran-Velez et al., Proposition 3.1 and Appendix D.1](https://arxiv.org/html/2606.19162v1) contains small-training-error/poor-reward examples. Intro140–147 correctly presents these as antecedents, not as guarantees for the manuscript's singular empirical setting.
- **Flow/continuity proof inputs:** [Hartman, Ch.II §1 Theorem 1.1 excerpt](https://epubs.siam.org/doi/10.1137/1.9780898719222) verifies the cited local existence/uniqueness input at1095. [AGS publisher](https://link.springer.com/book/10.1007/978-3-7643-8722-8) confirms the 2008 second edition. The accessible [2005 full text, Proposition 8.1.8, printed p.175](https://www2.stat.duke.edu/~sayan/ambrosio.pdf) verifies the representation mechanism, with its integrability and local regularity conditions. Exact second-edition text was unavailable. The manuscript's compact backward-test argument at1116–1133 is self-contained and avoids relying on a global moment hypothesis for arbitrary initial probabilities. A pinpoint reference would improve discoverability.
- **NW/target-noise/calibration:** Proposition nwrate (1766–1807), label/target-noise convolution identities, and calibration proof (2384 onward) are internally derived rather than justified solely by a named external theorem. Do not count the unused statistical books as verified proof inputs. I reviewed citation dependency/provenance here, not all of these internal proofs or experimental numbers.
- **Li limitation:** [Li et al., Theorem1 and deterministic proof, Appendix B](https://arxiv.org/html/2606.08554) explicitly claims oracle training-sample recovery. Its proof turns a softmax limit into one-hot without dealing with ties. The manuscript only cites the stated result as a scope comparison (119,3126–3131), and does not use it to prove intervention convergence. Do not import its proof as a replacement for the manuscript's own null-basin arguments.

## Complete coverage table (40 cited keys)

`metadata_verified` means the cited title/authors and stated publication identity were checked against a primary record; `partial` means only title/authors/preprint identity, not all venue/year fields, were independently confirmed. `claim_verified` is deliberately separate: `limited` means the broad motivation is supported but a theorem-level/full point-of-use audit is not complete. `fulltext_unavailable` records actual access failures; `not inspected` is not an access failure. URLs link to evidence, not secondary summaries. All rows were inspected for manuscript point of use.

| # | Key; main.tex lines | metadata_verified | claim_verified | Full text / evidence location |
|---|---|---|---|---|
| 01 | albergo2023building;78,273 | yes | yes, quadratic field regression background | [arXiv2209.15571](https://arxiv.org/abs/2209.15571), abstract and ICLR2023 comment; theorem input not imported |
| 02 | albergo2023stochastic;78 | yes | yes, flow/diffusion framework background | [JMLR26(209):1–80,2025](https://www.jmlr.org/beta/papers/v26/23-1605.html), publisher abstract; full theorem audit not needed for this use |
| 03 | ambrosio2008gradient;1122,1133 | yes | partial, mechanism verified in earlier edition | [2008 publisher](https://link.springer.com/book/10.1007/978-3-7643-8722-8), [2005 Prop8.1.8 p175](https://www2.stat.duke.edu/~sayan/ambrosio.pdf); exact 2008 fulltext_unavailable |
| 04 | baptista2025memorization;100,165,247,3137 | yes, v2 date/authors | yes | [v2 §6.3 Thm6.4, paragraph following](https://arxiv.org/html/2501.15785v2) |
| 05 | beltran2026reward;142 | yes, v1 header/authors | yes | [v1 Prop3.1; AppD.1](https://arxiv.org/html/2606.19162v1) |
| 06 | benton2024error;140,3514 | partial, preprint identity; TMLR venue not separately checked | yes, with source hypotheses | [v2 Thm1, Assumptions1–3, §3](https://arxiv.org/html/2305.16860v2) |
| 07 | bertrand2025closed;97,3086 | partial, title/authors/year; venue not separately checked | yes | [v2 §2 eq3,§3.2](https://arxiv.org/html/2506.03719), exact minimizer and learned-field deviation |
| 08 | biroli2023diffusion;97 | partial, arXiv title/authors; JSTAT pages not separately checked | limited, empirical/theoretical memorisation motivation | [arXiv2306.03518 abstract](https://arxiv.org/abs/2306.03518); full theorem text not inspected |
| 09 | biroli2024dynamical;3037 | partial, arXiv identity; Nature DOI endpoint fetch failed | yes, analogy to collapse time only | [arXiv2402.18491](https://arxiv.org/html/2402.18491), dynamical-regime discussion; Nature fulltext_unavailable via attempted endpoint |
| 10 | buchanan2025edge;97,153,2955,3122,4304 | yes | yes for capacity crossover; criterion attribution limited by Yoon access | [NeurIPS2025 record](https://papers.nips.cc/paper_files/paper/2025/hash/8a6a3f289e3e2654509ccfdd631e592e-Abstract-Conference.html), [arXiv full text](https://arxiv.org/html/2508.17689), §3 and experiments |
| 11 | carlini2023extracting;82 | yes | yes, observed extraction | [USENIX2023 publisher](https://www.usenix.org/conference/usenixsecurity23/presentation/carlini), abstract and BibTeX; full PDF not inspected |
| 12 | chen2026scoresmoothing;99,3083 | yes, arXiv author and official ICLR2026 PDF indexed | yes, restricted analytical/empirical score-smoothing evidence | [arXivv4 §§3–5](https://arxiv.org/html/2502.19499), [official indexed ICLR PDF](https://openreview.net/pdf/3f8ed4354cc5754741317526324e6acdb2fabc6f.pdf) |
| 13 | gao2024flow;97,3086 | yes, preprint identity | yes, exact-field memorisation background | [arXiv2410.23594](https://arxiv.org/html/2410.23594), closed-form field and sample-subspace discussion |
| 14 | gradvar2025;85,2656,2700,2894,4654 | partial, arXiv title/authors; conference independently supported by author CV but not proceedings inspected | partial; R05 | [arXiv2510.18118 §4.1 Prop2,§4.3](https://arxiv.org/html/2510.18118) |
| 15 | graf2000quantization;421,3167 | yes | partial; lower-bound direction passes, asymptotic application needs R03 | [publisher](https://link.springer.com/book/10.1007/BFb0103945); book theorem fulltext_unavailable; [authors' paper §1,eq2.3](https://numdam.org/item/10.1051/ps:2007044.pdf) |
| 16 | gu2023memorization;97,333,3110 | partial, preprint identity and TMLR linked review; year not separately established from venue record | yes | [v2 §6 and AppsC.3,D.3](https://arxiv.org/html/2310.02664), random external labels |
| 17 | hartman2002ode;1095 | yes | yes, local theorem; continuation proved in manuscript | [SIAM ChII §1 Thm1.1 excerpt](https://epubs.siam.org/doi/10.1137/1.9780898719222) |
| 18 | ho2022cascaded;113,3118 | yes | yes for conditioning augmentation; R02 for transfer to endpoint theorem | [JMLR23(47):1–33](https://jmlr.org/papers/v23/21-0635.html), abstract; full PDF not inspected |
| 19 | ho2022classifier;492,2662 | partial, arXiv identity; 2021 workshop record not directly inspected | yes, score combination background | [arXiv2207.12598](https://arxiv.org/abs/2207.12598), abstract; 2022 arXiv versus2021 workshop is not itself an error |
| 20 | jacot2018neural;3854 | yes | yes for NTK dynamics; R06 for generic Fourier claim | [NeurIPS2018 publisher](https://proceedings.neurips.cc/paper/2018/hash/5a4be1fa34e62bb8a6ec6b91d2462f5a-Abstract.html) |
| 21 | jain2025attraction;122 | partial, title/authors/arXiv; CVPR venue not independently fetched | yes, empirical timing/attraction-basin context | [v2 method and experiments](https://arxiv.org/html/2411.16738v2) |
| 22 | kadkhodaie2024generalization;97 | yes, official ICLR2024 PDF and arXiv | limited, primarily generalisation/inductive-bias work rather than a new empirical-minimizer theorem | [arXivv3 §2.2](https://arxiv.org/html/2310.02557), [official proceedings](https://proceedings.iclr.cc/paper_files/paper/2024/file/cbaf319a4712385b5ba8a414808b5713-Paper-Conference.pdf) |
| 23 | kamb2024creativity;97 | yes, all PMLR volume/pages/year | limited, creativity/memorisation context, not load-bearing | [PMLR267:28795–28831](https://proceedings.mlr.press/v267/kamb25a.html), [arXiv full text](https://arxiv.org/html/2412.20292) |
| 24 | li2026memory;97,119,3126 | yes, preprint identity | yes as statement-of-source comparison; source proof tie limitation noted above | [Thm1, AppB deterministic/stochastic proofs](https://arxiv.org/html/2606.08554) |
| 25 | lipman2023flow;78,273 | partial, title/authors/preprint; ICLR venue not separately fetched | yes, field regression background | [arXiv2210.02747](https://arxiv.org/abs/2210.02747); abstract; full theorem text not inspected |
| 26 | liu2023rectified;78,273 | partial, title/authors/preprint; ICLR venue not separately fetched | yes, straight-path transport background | [arXiv2209.03003](https://arxiv.org/abs/2209.03003), abstract; full theorem text not inspected |
| 27 | liu2025pde;128,166 | yes, v3 title/authors/version | yes | [v3 Thm3.7(i)–(iii),§3.2](https://arxiv.org/html/2511.05940v3) |
| 28 | liu2026geometric;130,167 | yes, v1 title/authors/version | yes | [Thm3.18,Rem3.19;§7.4 limited to autonomous inclusions](https://arxiv.org/html/2605.12231v1) |
| 29 | pfrommer2025conditional;114,3091 | yes, NeurIPS short title/arXiv long title explicitly disambiguated | yes | [arXiv Thms2–3,AppA.4](https://arxiv.org/html/2512.18736), [official short-title PDF indexed](https://openreview.net/pdf/4b80b588562513f63972d53033df9a2d205d5514.pdf) |
| 30 | physicscfm2026;85,102,524,3101 | yes, preprint identity | yes | [§§3.2–3.3,eq32–41, early stopping discussion](https://arxiv.org/html/2603.14135) |
| 31 | pidstrigach2022manifolds;97 | partial, title/author/preprint; NeurIPS venue not separately fetched | limited, support/manifold memorisation conditions | [arXiv2206.01018](https://arxiv.org/abs/2206.01018), abstract; full theorem text not inspected |
| 32 | rahaman2019spectral;3855 | yes, PMLR author list/year | partial; R06 | [PMLR97:5301–5310](https://proceedings.mlr.press/v97/rahaman19a.html), abstract and indexed official PDF |
| 33 | sadat2024cads;113,3118 | partial, title/authors/preprint; ICLR venue not separately fetched | yes for practical annealing; R02 for exact-law equivalence | [arXiv2310.17347](https://arxiv.org/html/2310.17347), inference algorithm |
| 34 | scarvelis2025closedform;99,3079 | partial, title/authors/preprint; TMLR venue not separately fetched | yes for empirical kernel denoiser and memorisation; avoid conflating its smoothed model with empirical unsmoothed limit | [arXiv2310.12395](https://arxiv.org/html/2310.12395), empirical denoiser and smoothing construction |
| 35 | sesmat2026leaks;82 | partial, title/authors/preprint; ICML venue not independently fetched | yes, membership evidence; does not by itself prove endpoint copying | [v3 abstract,§§3–4,7](https://arxiv.org/html/2606.07271) |
| 36 | smola2026support;106,3022,3095 | yes, preprint identity | partial; R01 | [§2,Props1–2,eq4–5](https://arxiv.org/html/2605.13386) |
| 37 | somepalli2023copying;332,3114 | partial, title/authors/preprint; NeurIPS pages not independently fetched | yes for conditioning/replication contrast; R04 for claimed equivalence | [§§5.3,7](https://arxiv.org/html/2305.20086) |
| 38 | somepalli2023diffusion;82 | partial, title/authors/preprint; CVPR HTML returned403 | yes, observed replication background | [arXiv2212.03860 abstract](https://arxiv.org/abs/2212.03860); publisher fulltext_unavailable on attempted endpoint |
| 39 | tong2024improving;80 | yes, title/authors and TMLR comment/year | yes, generalized CFM regression background | [arXiv2302.00482](https://arxiv.org/abs/2302.00482), abstract; full theorem text not inspected |
| 40 | yoon2023memorization;529,2954,4149,4304 | partial, official indexed title/authors/workshop evidence | not fully verified: exact squared nearest/second-nearest threshold and default attribution remain open | [official indexed PDF](https://openreview.net/pdf/2c153b8c682414c640edfbecc86524332e91c826.pdf); direct fetch produced browser verification challenge: fulltext_unavailable; no challenge bypass attempted |

## Access and scope ledger

The audit covers all 40 cited entries, but **does not certify every bibliography field or every claim**. The table explicitly leaves partial metadata and restricted claim verification open. This is a source-integrity review, not a proof audit of all results or a replication of the experiment archive.

### Supplemental metadata checks after the table draft

These primary checks close the corresponding venue/year reservations in the table, without upgrading claim verification:

- Rows06,08,09: [Oxford author's repository](https://ora.ox.ac.uk/objects/uuid%3A8132c98e-616f-42d6-b522-8bb8f0b41d6b) confirms Benton TMLR2024; [Biroli–Mézard arXiv journal reference](https://arxiv.org/abs/2306.03518) confirms JSTAT2023 article093402; [Biroli et al. arXiv journal reference](https://arxiv.org/abs/2402.18491) confirms Nature Communications15(2024), DOI as cited.
- Rows07,14: [NeurIPS2025 Bertrand record](https://proceedings.nips.cc/paper_files/paper/2025/hash/0ca819b3e8126e19a008c38cd0c371ea-Abstract-Conference.html) confirms venue; [official indexed Reu PDF](https://openreview.net/pdf/261221c8a4e906cb4273bf201ba92342c62bc50e.pdf) explicitly identifies NeurIPS2025.
- Rows21,25,26,31,33: [CVPR2025 Jain record](https://openaccess.thecvf.com/content/CVPR2025/html/Jain_Classifier-Free_Guidance_Inside_the_Attraction_Basin_May_Cause_Memorization_CVPR_2025_paper.html), [official indexed Lipman ICLR2023 PDF](https://openreview.net/pdf?id=PqvMRDCJT9t), [Xingchao Liu's official OpenReview listing](https://openreview.net/search?content=authors&group=all&sort=cdate%3Adesc&source=forum&term=~Xingchao_Liu1), [NeurIPS2022 Pidstrigach record](https://proceedings.neurips.cc/paper_files/paper/2022/hash/e8fb575e3ede31f9b8c05d53514eb7c6-Abstract-Conference.html), and [ICLR2024 CADS record](https://proceedings.iclr.cc/paper_files/paper/2024/hash/6769bfdeb7313ded45714aabf759adfe-Abstract-Conference.html) confirm the listed venues/years.
- Rows34,35,37: [Scarvelis author's publication page](https://cscarv.github.io/publication/cfdm) explicitly confirms TMLR2025; [PMLR306 Sesmat record](https://proceedings.mlr.press/v306/sesmat26a.html) confirms ICML2026 but reveals R08; [NeurIPS2023 Somepalli record](https://proceedings.neurips.cc/paper_files/paper/2023/hash/9521b6e7f33e039e7d92e23f5e37bbf4-Abstract-Conference.html) confirms venue/year (page range remains unchecked).
- Gu's linked OpenReview forum returned a browser challenge. Its venue-year verification remains partial; no bypass was attempted.

Five uncited entries are `nadaraya1964estimating`, `watson1964smooth`, `tsybakov2009nonparametric`, `gyorfi2002distribution`, and `briq2026tracing`. Their non-use was verified by extraction, not inferred from the bibliography size. Primary title/author metadata for the last was located at [arXiv2608.30081](https://arxiv.org/abs/2608.30081); no manuscript claim currently rests on it.

The requested Blohm–Garg/OpenReview candidate `ADLiUSC7Qm` is not in the cited40. Opening [its forum](https://openreview.net/forum?id=ADLiUSC7Qm) produced the OpenReview browser verification challenge. I did not bypass it and cannot certify its theorem-level overlap. Treat this novelty-comparison check as unresolved rather than absence of prior art. The same access limitation affected the direct Yoon PDF fetch; indexed snippets are not a substitute for its exact metric definition.

**Recommended integration order:** repair R01–R06 without altering theorem contracts, add R07 attribution if appropriate, then close the Yoon exact-threshold and Blohm–Garg full-text checks. The closest three convergence comparisons have primary-source evidence and should remain narrowly stated as in the present introduction.
