# Paper A (`paper_theory/`): corrections of 2026-11-21 (editor label edit-A)

Files changed: `paper_theory/main.tex`, `paper_theory/refs.bib`, `paper_theory/README.md`,
`paper_theory/main.pdf` (recompiled on lab09). Nothing of the other session was edited
(`scripts/paperB_*.py`, `results/paperB_20261121/`, `logs_paperB/`, `docs/plan/paperB_*.md` were
only read). No figure was redrawn and no figure environment was changed. Nothing was committed.

Sources.
- "V:item eN" is edit N of that item in `docs/review/memo_verification_2026-11-21.json`. "V:item dN"
  is discrepancy N.
- "PC" is the prior-check result handed to this editor (Liu and Zuazua v2, Azangulov et al., Wan
  et al., Cao et al. read from the PDFs). Its scratch is lab09 `/mnt/data/khoitm8/tmp/prior-check/`.
- "EC" is the edge-check result handed to this editor. Its scratch is lab09
  `/mnt/data/khoitm8/tmp/edge-check/`.
- "M5.n" is Section 5 (errata) of `docs/plan/paperB_findings_2026-11-21.md`, which supersedes its
  Sections 1-3. Section 4 (E1 window swap) concerns paper B only and was not used here.
- "Recomputed" means recomputed by this editor from repo files with `uv run --no-project python`.

## 1. Liu and Zuazua v2 and the prior work it brought in (V:1.9-liu-v2, V:1.9-refute, M5.11, PC)

arXiv 2605.12231 v2 (29 Oct 2026, new title) replaces v1's conditional Theorem 3.18 and Remark 3.19
by Theorem 2.5. For two finite atomic laws and a constant weight, every trajectory converges to one
of finitely many equilibria, with no limit-set hypothesis. The limit need not be an atom (Remark
2.7). Corollary 3.7 also covers hard-label guidance at a fixed w > 0, and Lemma 5.5 gives finite
energy at a constant strength. Paper A's claim to remove the limit-set hypothesis was therefore out
of date. What remains new is listed in PC and stated in the text:
- the Lebesgue-null exceptional set for the deterministic flow: mixtures over any family of positive
  priors, guidance, two-field combinations, bottleneck fields, schedules of bounded variation;
- convergence for more than two fields;
- unbounded hard-label schedules;
- everything with three or more fields.

| Where | Change | Source |
|---|---|---|
| Abstract | "for guidance this removes the limit-set hypothesis of the known convergence result" replaced. It now says "for guidance the analogous statement was known for the stochastic sampler, and for a fixed strength every trajectory of the flow was known to converge, possibly to a point that is not a training example". The earlier sentence now reads "Positive mixtures of exact fields with strictly positive priors, and every combination of two such fields, which includes guidance with a bounded schedule of bounded variation ...". | PC A; V:1.9-liu-v2 e0; V:1.9-refute e0. Priors qualifier: PC caveat 2. "of bounded variation" is what Thm `thm:schedule` assumes. |
| Intro, first contribution bullet | Added: "for two fields with a fixed coefficient the convergence of every trajectory is due to Liu and Zuazua (2026, Theorem 2.5)". "every combination of two exact fields" becomes "... with strictly positive priors". | PC B; V:1.9-refute notes 1; PC caveat 2 |
| Technique paragraph | Credits Wan et al. Thm 5.3 for the single-field null set (through known marginals). Credits Liu and Zuazua Lemma 5.5 for finite energy at a fixed strength. Paper A's own step is now stated as the integration by parts, which extends this to schedules of bounded variation and any finite number of fields (Lemma `lem:signedconv` has K priors). | PC C; V:1.9-liu-v2 e1 |
| Table 1 (`tab:interventions`) | The row "Any two exact fields" becomes "Any two exact fields with positive priors". Before, it contradicted the hard-label-average row of the same table. "guidance w in [-1,0)" becomes "... at h > 0" (Cor `cor:negcfg` assumes h > 0). | PC caveat 2. A worked counterexample: at h = 0 and w = -0.9 on atoms +-1, the limit potential has a minimum at -0.8. |
| Related work | Replaced the v1 description (Thm 3.18, Remark 3.19, "without that hypothesis"). It now cites Wan et al. Thm 5.3 (a.e. convergence and the endpoint law for flow-matching ODEs) and v2 Thm 2.5 with Remark 2.7 and Section 7. It also cites Azangulov et al. Thm 3 (guided SDE, bounded time- and state-dependent strength, support a.s.; Girsanov, does not apply to the flow). It ends by saying what paper A adds. | PC D; V:1.9-liu-v2 e2; V:1.9-refute e1, e2 |
| Sec. 4.2, sentence after Prop `prop:cfgatom` | "guidance thus weakens the guaranteed rate to (1-t) sqrt(log 1/(1-t))" replaced. Guidance does not prevent collapse, and our bound exceeds the unguided rate 1-t only by a sqrt-log factor. For a fixed w > 0, Liu and Zuazua Thm 2.5(ii) and Cor 3.7 give O(1-t), with a constant that depends on the initial point. | PC E; V:1.9-liu-v2 e3; V:1.9-refute e3, d4 |
| App. B.1 `apx:comparison`, text | First sentence: "the closest convergence theorems for the deterministic flow and the closest support theorem for the stochastic sampler". The v1 paragraph (Thm 3.18, "needs no such hypothesis", "We do not treat two different supports") is replaced. On the common configuration the conclusions differ: v2 Thm 2.5 gives convergence to an equilibrium, Remark 2.7 shows a stuck midpoint, and Prop `prop:cfgatom`(a) adds the null set. Version 1 had left the a.e. statement open (its Remark 3.19), and this is kept as history. Two more points: schedules and Pi-mixtures go beyond a fixed weight with two laws, and different supports enter only through hard labels, where v2 Cor 3.7 also gives `prop:cfgatom`(b). Added Azangulov et al. (Girsanov, needs Brownian noise) and Cao et al. Thm 3.1 (guided DDIM ODE, every initial point, disjoint convex supports with interiors; finite data excluded). | PC F1, F2 (Cao sentence optional, kept); V:1.9-liu-v2 e4; V:1.9-refute e4, d4 |
| App. B.1, Table 5 `tab:comparison` | Now 5 columns: Liu and Zuazua 2025 Thm 3.7 together with Wan et al. Thm 5.3; Liu and Zuazua 2026 Thm 2.5 (was Thm 3.18); Azangulov et al. Thm 3; this paper. The "Hypothesis on trajectories" row is dropped; it would read "none" everywhere. Other row changes: support "two finite sets with positive weights, possibly different"; conclusion "every trajectory converges to one of finitely many equilibria ..., not always a local minimiser (Rem. 2.7); rate sqrt t when the limit has a unique nearest atom in each support" (was "almost-everywhere validity open (Rem. 3.19)"). The caption explains heat time. Cells are set ragged right (`\cmpcell`, rows end with `\tabularnewline`) to remove stretched spaces in the narrow columns. | PC G; V:1.9-liu-v2 e5-e7; V:1.9-refute e5, e6 |
| Conclusion | "every combination of two exact fields" becomes "... with strictly positive priors". | PC I; PC caveat 2 |
| `refs.bib` `liu2026geometric` | v2: new title "Convergence of Singular Dynamics Driven by Mixed Logarithmic Heat Gradients", note "Version 2, revised October 29, 2026; version 1 (May 12, 2026) was titled ...", URL `.../2605.12231v2`. Key kept. | PC H; V:1.9-liu-v2 e8 |
| `refs.bib`, new | `azangulov2026adaptive` (AISTATS 2026, PMLR 300:4087-4095, arXiv:2505.19367); `wan2025elucidating` (ICML 2025, PMLR 267:62020-62083, PMLR title, arXiv:2412.18730); `cao2026robustness` (arXiv:2605.07220 v2, 22 May 2026). Style as `kamb2024creativity`. | PC H (metadata checked on PMLR and arXiv pages there) |

## 2. Edge midpoints of the triangle (EC)

On the triangle with B = 2, each edge midpoint is a two-atom tie. The third condition has restricted
log-odds 0 and is grouped with the unconditional field, with net coefficient (1-2w)/3. The edge is
therefore the conjunction of Prop `prop:twoatom`(c) with B/2 in place of B and (2w-1)/3 in place of
w. It attracts exactly when w > (1 + 3/sinh^2(B/2))/2 = 1.586 = 1.368 w_c, and below this value its
probability is 0.

The old classifier of `learned_composition_2d.py` labelled every edge endpoint as one of that edge's
atoms. Its centre fractions are exact, so no number in paper A changes. What was wrong are the
statements implying that the rest of the mass is on atoms, and that networks "follow the exact
probabilities" on the triangle beyond the centre.

Recomputed by this editor:
- From `results/theory_basin_map_20261121/summary.json`:
  - 2 w_c: 0.1306 / 0.4095 / 0.4600 (centre / edges / atoms);
  - 5 w_c: 0.6810 / 0.2943 / 0.0247;
  - 10 w_c: 0.9503 / 0.0495 / 0.00012.
  - Standard errors are at most 0.0027, and no source is unresolved.
  - At 1.1 w_c no source ends at an edge.
  - Classes change after u = 1e3 for 0 sources at 2, 5 and 10 w_c, and for 300 at 1.1 w_c.
  - `check_exact_2d`: 1744 / 1252 / 196 of the 4096 sources end at edges at 2 / 5 / 10 w_c, with 0
    centre or atom disagreements.
  - The analytic `w_edge` is 1.5861 and `r_edge` is 1.3678.
- From the stored `final_states.npz` of `results/learned_composition_2d_20261021/{cfm_v,cfm_x_s,distill_x_s}_seed0-4`, arm L3, 1-t = 1e-5, at all seven stored strengths (0 to 10 w_c):
  - at most 3 of 2048 sources within 0.05 of an edge midpoint (cfm_v seed 3 at 2 w_c);
  - cfm_x_s and distill_x_s: 0.
- From `results/learned_composition_2d_20261021/SUMMARY.md`: on the networks' 2048 sources the
  exact centre fraction is 0.138 / 0.681 / 0.951.
- Analytic thresholds:
  - simplex N = 9, B = 2: w_e = 9/(2 tanh^2 1) - 1 = 6.758 = 1.407 w_c;
  - long edges of the rectangle and the box: B(p) = +-2 (checked against
    `spectral_criterion_check.py`, `product_config`), so 1/sinh^2 2 = 0.076;
  - bottleneck cells, B_Q = 1.241279: w_e = 3.9304 = 1.001 w_c(B_Q).

| Where | Change | Source |
|---|---|---|
| Abstract | "networks given a coordinate at that scale match the exact probabilities" becomes "... at that scale, centred at the tie, match its exact probability". The layer is now "of width (1-t)^2 around the tie". | EC (9) |
| Intro, third bullet | "... match the exact probability at the tie where the input is centred, and miss the blends at other ties" | EC (9) |
| Sec. 4.5, end of the Prop `prop:twoatom` discussion (new sentences) | The conjunction on the regular simplex also blends pairs. At an edge midpoint the other N-2 conditions have B(p) = 0, so (c) applies with B/2 and 2(1+w)/N - 1. Theorem `thm:spectral` gives positive probability for w > N/(2 tanh^2(B/2)) - 1 and 0 for smaller w. This is 1.368 w_c for the triangle. | EC (10), with the strength substitution written out (derived and checked here) |
| Sec. 6, "Learned guided label averaging" | "none on the triangle" becomes "none at the centre of the triangle"; "0.133 on the triangle" becomes "0.133 at the centre of the triangle". New sentence: the network follows the exact flow only at the tie its input is centred on. The exact composite ends a further 0.426 / 0.306 of the first 4096 shared sources at edge midpoints at 2 / 5 w_c. The standard, the rescaled-input data-predicting and the distillation networks place at most 3 of 2048 within 0.05 of an edge midpoint at 1-t = 1e-5, in any seed and at any strength. | EC (4), reworded. "on the same sources" became "of the first 4096 shared sources", because the networks use the first 2048. The gap is stated because the bound does not hold at 1-t = 1e-2 (see Rejected). |
| Sec. 6, "The spectral criterion beyond the line" (in `\moveblock{spectralexp}`) | Added: these fractions count the centre only. The edge midpoints attract for w > 1.368 w_c and have probability 0 below (Sec. 4.5). With 32768 sources the exact flow ends 0.131 / 0.409 / 0.460 at the centre / edges / atoms at 2 w_c (Fig. 1c), 0.681 / 0.294 / 0.025 at 5 w_c and 0.950 / 0.050 / 0.0001 at 10 w_c, with SE at most 0.003; at 1.1 w_c no edge mass. Also added: the simplex edges attract for w > 1.407 w_c, and the long edges of the rectangle and the box (B(p) = +-2) for w > 0.076, so also at w = 1 where xi = 0 is a saddle; their mass was not computed. | EC (1) with the derivation moved to Sec. 4.5. The OPTIONAL rectangle sentence is extended to the box and the simplex (analytic, checked here). |
| Limitations | "chiefly on its input" becomes "chiefly on an input centred at the tie ...; on the triangle such a network leaves the blends at the other ties, the edge midpoints, empty". | EC (9), reworded |
| Conclusion | "networks given a coordinate at that scale do" becomes "... do so at the tie where it is centred". | EC (9) |
| App. E.1 "Spectral criterion" | New paragraph tail on `theory_basin_map.py`. It describes the same two stages, rtol 1e-9, 32768 sources, seed 20261121, and classification at sigma = 1e4: centre if abs(xi) < 5; edge if within 0.2 and the edge profile is below 5; atom if within 0.2 and every posterior puts more than 1 - 1e-6 on it. Every source is classified, there are no class changes after 1e3 at 2, 5 and 10 w_c, and the centre fractions agree with Table 6 within sampling error. On the 4096 shared sources the centre classes coincide with `learned_composition_2d.py`, whose classifier put edge endpoints on an edge atom. | EC (3), plus the agreement check (0.1306 vs 0.1396 at 2 w_c, z = 1.2; 0.6810 vs 0.6865 at 5 w_c) |
| Table 6 `tab:spectral` caption | "Other candidates are not counted: on the triangle the edge midpoints, ..., take a further 0.41 and 0.29 of the mass at 2 and 5 w_c". | EC (2) |
| App. E.1 "Learned guided label averaging" | The exact triangle value is the fraction with abs(xi) < 5, that is, ending at the centre; edge endpoints were assigned to an edge atom, which leaves it unchanged. | EC (6) |
| App. E.1 "Which change matters" | "match the exact probabilities at the centre" | EC (7) |
| App. E.1 "Tie-centring and a label bottleneck" | "... told where the tie is, and only at that tie: the data-predicting network told the centre leaves the edge midpoints empty". The bottleneck composite is "followed at the centre (its edge midpoints, which attract for w > 1.001 w_c(B_Q), are not counted)". | EC (8); 1.001 recomputed |
| Table 8 `tab:learned-composition` caption | The exact triangle row is the centre fraction of the first 4096 sources (0.138 / 0.681 / 0.951 on the networks' 2048). The exact composite ends a further 0.426 / 0.306 / 0.048 of these 4096 at edge midpoints, which the occupancies do not count. | EC (5) |
| Figure 1 caption | Unchanged: its 13% / 41% and w > 1.37 w_c are consistent. | EC item 5 |

## 3. Bibliography metadata (V:3-bib-metadata e9-e13)

Applied to `paper_theory/refs.bib`, keys unchanged:
- `physicscfm2026`: pinned to v3 (note, URL, and a comment on the v1/v2 titles); cited at the
  `physicscfm2026` pinpoint "Section 3.3", which holds for v3.
- `jain2025attraction`: CVPR 2025 pp. 12871-12879, DOI 10.1109/CVPR52734.2025.01201.
- `sesmat2026leaks`: PMLR 306:109269-109293.
- `beltran2026reward`: NeurIPS 2026, author "Xiaofeng Zhang", note arXiv v1.
- `dodson2026calm`: `@inproceedings`, PMLR 306:25643-25694. Under `tmlr.bst` the old `@misc`
  printed no identifier.

The last three are not cited in paper A and are kept in sync with paper B. `favero2025bigger`,
`li2026kinetic`, `liu2025navigation`, `shah2025ambient`, `li2024critical` and
`kaiser2026structural` are neither in paper A's bib nor cited, so they were not added.

## 4. Reproducibility statement and ICLR branch

- The reproducibility statement now names the scripts behind every figure:
  - Fig. 1: `theory_basin_map.py`, `make_theory_hero_figure.py`;
  - Fig. 3: `signed_combinations_check.py`, `signed_combinations_probability.py`,
    `make_signed_combinations_figure.py`;
  - Fig. 4: `composition_counterexample.py`, `make_composition_figure.py`;
  - Fig. 5: `learned_composition.py`, `learned_composition_2d.py`,
    `summarize_learned_composition.py`, `make_learned_composition_figure.py`;
  - Fig. 6: the stress-test scripts and `make_intervention_validation_figure.py`;
  - Fig. 7: `cifar_composition_exact.py`, `make_theory_cifar_composition_figure.py`;
  - plus the spectral, kernel and endpoint-noise checks.
- The statement is set ragged right in a group. Justified, it had 8 underfull lines.
- "Artifacts" paragraph: added `results/theory_basin_map_20261121/`.
- ICLR-only branch of Sec. 6 "Guided label averaging": "The exact lines of Figure
  `fig:learned-composition`(a) give" becomes "The horizontal coordinates in Figure
  `fig:learned-composition` give". The new Figure 5 is a parity plot whose horizontal axis is the
  exact probability.
- Typo fixed in Sec. 4.3: `.\fi Neither` printed "B.5).Neither" because the space after `\fi` was
  eaten. It now reads `.\fi{} Neither` (both venues).
- `paper_theory/README.md`: story qualifier, the new scripts (`theory_basin_map.py`,
  `make_theory_hero_figure.py`, `signed_combinations_probability.py`), the Figure 1 provenance
  (no longer `make_edm_figures.py`), a summary of this revision, the status, and open items.

## 5. Compile (lab09, tectonic, `scripts/build_papers.sh paper_theory`)

- TMLR: rc 0, 52 pages (baseline 50), 0 overfull hboxes (baseline 0), 9 underfull (baseline 17),
  no undefined references or citations. `main.pdf` was copied back.
- ICLR variant, test only, in lab09 scratch `/mnt/data/khoitm8/tmp/edit-A/iclr/` (wrapper
  `\def\iclrversion{}\input{main}`, `paper/iclr2027_conference.sty`):
  - rc 0, 53 pages (baseline 51), 0 overfull, no undefined references.
  - The references now start on p. 14 instead of p. 13. The ICLR main text was already over a
    9-page limit before this revision.
- Pages rendered and read: TMLR 1-4, 8, 12-14, 16-18, 26-27, 48-50, 52; ICLR 10.

## 6. Rejected or not applied

- V:1.9-liu-v2 e0/e2/e4/e8 and V:1.9-refute e0/e2/e4/e8 were superseded by the PC versions of the
  same passages, which are more complete: they add Azangulov, Wan and the v1 date. V:1.9-refute e1
  (Azangulov before the `liu2025pde` sentence) went in after the Liu and Zuazua sentence instead.
- PC table G cell "deterministic flow of one score": "one field" is used, because Wan et al.
  integrate a flow-matching ODE. The caption's "rates are in heat time sigma^2/2, in which sqrt t is
  O(1-t) here" was reworded so that the two meanings of t are not confused.
- EC (4) "the sources that the exact flow sends there end at a training point, at the centre or away
  from every candidate": dropped. It is per-source scratch analysis and adds nothing beyond the
  count.
- EC's explanation of the learned centre excess (recall x paired exact + leaked edge sources):
  scratch analysis, not used.
- EC rectangle Monte Carlo (0.885 / 0.763 of the mass at long-edge midpoints, `rect_check.py`):
  scratch, not in the repo, not used. Only the analytic threshold is stated.
- EC side remark "stays at most 0.005 within 0.2 at every stored gap": not reproduced, and not
  used.
  - Within 0.2 of an edge midpoint, cfm_v reaches 60/2048 at 1-t = 1e-2 and 41/2048 at 1e-5, and
    cfm_x_s 26/2048 at 1e-5.
  - Within 0.05, distill_x_s has up to 208/2048 at 1-t = 1e-2, all gone by 1e-3.
  - The paper's count is therefore stated at 1-t = 1e-5.
- Memo M5.11's line references and "cite v2, or state v1 explicitly": v2 is cited (V:1.9-refute
  d6).
- Out of scope, not touched: the same stale v1 entry in `paper_mechanism/refs.bib` and in
  `paper/` (V:1.9-liu-v2 bib note), and the old combined `paper/main.tex`.

## 7. Open questions for the authors

- "At most 3 of 2048 within 0.05 of an edge midpoint" (Sec. 6) comes from the stored
  `final_states.npz` and has no repo script yet, although the reproducibility statement says that
  all numbers are produced by code. A script is needed before submission (EC caveat 1).
- The edge mass of `cfm_v_s`, `cfm_x`, `cfm_x_o`, `cfm_x_sq` is unknown, because no endpoints were
  stored. The text therefore names only the three networks with stored endpoints.
- Centre-only counts also undercount blends on the d = 8 simplex (edges attract above 1.407 w_c),
  the rectangle and the box (long edges at w > 0.076), and the bottleneck composite (edges above
  1.001 w_c(B_Q)). Their edge masses, and face centroids in d = 8, are not computed. Should
  `theory_basin_map.py` be extended, or is the qualitative sentence enough?
- Abstract: is the clause crediting the stochastic result and fixed-strength convergence wanted
  there, or only in the related work? PC's shorter alternative is "for a fixed guidance strength,
  every trajectory was known to converge, possibly to a point that is not a training example".
  Azangulov et al. state Thm 3 for a class with p(c) > 0, hence the word "analogous" (PC caveat 3).
- Keep or drop the optional Cao et al. sentence (App. B.1) and `cao2026robustness`.
- The convergence novelty for bounded-variation schedules is partial: v2 covers schedules constant
  near t = 1, and probably ones that settle fast in log time (PC caveat 4). The text claims only
  the general BV case and the null set.
- ICLR variant: the main text grew by about one page.
- Not checked by any verifier: `baptista2025memorization` Thm 4.3 / Ex. 4.4 (cited by v2 for
  single-score convergence with an interface endpoint), and Cai et al. (arXiv 2609.06947).

## 8. Review fixes (label fix-A)

Files changed: `paper_theory/main.tex`, `paper_theory/refs.bib`, `paper_theory/README.md`,
`paper_theory/main.pdf`, `paper_theory/figures/fig_learned_composition.pdf`,
`scripts/stress_positive_control.py`, `scripts/spectral_criterion_check.py` (optional return value
only), `scripts/theory_basin_map.py`, `scripts/make_learned_composition_figure.py`,
`results/stress_positive_control_20261121/summary.json` (new fields),
`results/theory_basin_map_20261121/summary.json` (new keys `faces` and `learned_edge_counts`; the
other keys are unchanged). Nothing of the other session was edited. Nothing was committed.
Scratch, backups of every file before the change, and the run logs: lab09
`/mnt/data/khoitm8/tmp/fix-A/`.

Sources. "Rn" is finding n (1-31, in the order handed to this editor) of the fix-A review list.
Every finding was checked against the data, the code or the cited paper before it was applied.
Duplicates and overlaps: R11 = R3 (merged wording); R6 is contained in R9 (intro, Limitations);
R7, R15 and R16 are one set of script changes; R8 and R9 both edit the Figure 5 caption; R1 and
R24 both edit the Table 6 caption; R16 and R19 concern the same Section 6 sentence.

### 8.1 Scripts and data (lab09, CPU, numpy/scipy)

| Script | Change | Result |
|---|---|---|
| `stress_positive_control.py` | Per row: `midpoint_count`, `exact_basin_count` (first coordinate inside `basin_low`/`basin_high` of `theory_composition_20261019`; empty at 0.9 w_c), `disagree`, `flagged_vs_midpoint_disagree`, `max_abs_x1/x2_at_midpoint`. Rerun (75 s). | Old fields identical. `disagree` = 0 in all 24 rows (0/201/1681/4046 sources in the basin at 0.9/1.1/2/10 w_c). The 1% criterion flags exactly the captured sources at 1e-4 and 1e-6 (0 disagreements; at 1e-2 it also flags sources still in transit). Largest abs x1 of the captured endpoints: 2.246e-17, 2.246e-19, 2.246e-21 at the gaps 1e-2, 1e-4, 1e-6; largest abs x2: 0.03701, 3.701e-4, 3.701e-6. (R7, R15) |
| `spectral_criterion_check.py` | `run(..., keep_states=False)` returns xi and tau at the checkpoints when asked. Default output unchanged; not rerun. | - |
| `theory_basin_map.py --faces` | The 14 configurations of Table 6, with the sources (seed 11; 2048, box 512) and the integration of `spectral_criterion_check.py`. Every endpoint is classified by the face whose centroid it reaches: the atoms within a factor e^50 of the largest uniform-prior weight, accepted if the centroid has exactly these nearest atoms, the trajectory is within 0.2 of it and the profile on the face span is below 5. | Every source is classified; face sizes at u = 1e4 below. No class changes after u = 1e3 at 2 and 5 w_c and for the rectangle and the box (3, 8, 19 and 158 changes at triangle 0.9, simplex 0.9, triangle 1.1 and simplex 1.1 w_c). (R1) |
| `theory_basin_map.py --learned-edges` | Stored L3 endpoints of `learned_composition_2d_20261021/{cfm_v,cfm_x_s,distill_x_s}_seed0-4`, every gap and strength. | At 1-t = 1e-5: at most 3 of 2048 within 0.05 of an edge midpoint (cfm_v seed 3, 2 w_c), 0 for cfm_x_s and distill_x_s. Farther than 0.1 from every atom and from the centre: cfm_v 0.163 +- 0.064, 0.696 +- 0.259, 0.787 +- 0.375 at 2, 5, 10 w_c; cfm_x_s 0.156 +- 0.158 at 2 w_c (equal to `SUMMARY.md`). (R16, R19) |
| `make_learned_composition_figure.py` | Headers "plain input (x,t,y): midpoint nearly empty" and "rescaled input asinh(tx/(1-t)^2): near the exact probability" ("with the" dropped: the longer header was clipped at the right edge). Regenerated on lab09. | Plotted data and the four mean deviations (0.210, 0.207, 0.049, 0.003) unchanged. (R8) |

Face masses (`faces` key; fractions of 2048 sources, box 512):

| Configuration | w | atoms | centre | other blends (face sizes: counts) |
|---|---|---|---|---|
| triangle | 1.1 / 2 / 5 w_c | 0.998 / 0.457 / 0.022 | 0.002 / 0.145 / 0.682 | 0 / 0.399 / 0.295 (edges) |
| simplex, d = 8 | 0.5 and 0.9 w_c | 1 | 0 | 0 |
| simplex | 1.1 w_c | 0.999 | 0 | 0.001 (k = 4: 1, k = 5: 1) |
| simplex | 2 w_c | 0.047 | 0 | 0.953 (k = 2..8: 349, 655, 577, 284, 77, 8, 2) |
| simplex | 5 w_c | 0 | 0.019 | 0.981 (k = 2..8: 1, 22, 122, 344, 664, 604, 252) |
| rectangle | w = 1 / 5 | 0.105 / 0 | 0 / 0.246 | 0.895 / 0.754, all at long-edge midpoints |
| box | w = 1 | 0 | 0 | 1 (faces spanned by 1/2/3/4 long axes: 3/22/154/333) |
| box | w = 5 | 0 | 1/512 | 511/512 (4 long axes plus 0/1/2/3 short: 173/234/87/17) |

The centre fractions equal Table 6 for the rectangle and the box. For the triangle and the simplex
they agree within sampling error (296 vs 286 and 1397 vs 1406 of 2048 at 2 and 5 w_c; 39 vs 38 for
the simplex at 5 w_c): `simplex()` takes an SVD basis that this LAPACK returns rotated relative to
the run behind Table 6. The negated triangle (the orientation recorded by the learned 2D runs)
gives 288 and 1388, so neither orientation reproduces Table 6 (scratch `orient_test.py`). The
masses are therefore stated in the text, not added as a Table 6 column.

Analytic checks (recomputed here). A k-face centroid of the 9-simplex has
Gamma(0) = r^2/(k-1) [1 - (1+w) k m_k^2/9] P_L with m_k = (e^B-1)/(e^B+k-1), so it attracts for
w > 9/(k m_k^2) - 1 = 1.407, 1.141, 1.031, 0.983, 0.966, 0.968, 0.980 and 1 w_c for k = 2..9
(k = 2 with N = 3 gives 1.368 w_c). With product priors on atoms of equal norm every posterior
factorises by axis, so the rectangle and box flows are per-axis one-dimensional composites with
B = 2 (long axes) and 1/2 (short axes); thresholds 1/sinh^2 2 = 0.076 and 1/sinh^2(1/2) = 3.683,
consistent with the box eigenvalues in `theory_spectral_20261020` (+0.0286 at w = 1 and -0.0141 at
w = 5 on the short axes).

### 8.2 Text (`main.tex`, `refs.bib`)

| Where | Change | Source |
|---|---|---|
| Abstract | "and every combination of two such fields, which includes guidance with a bounded schedule ..." becomes "every fixed combination of two such fields, which includes negative prompting by substitution, and guidance with a nonnegative bounded schedule of bounded variation"; "match its exact probability" becomes "can match". | R13 (Cor. `cor:twofields`: constant c, or w(t) in [0, w-bar]); R9 (cfm_v_s matches in 2 of 5 seeds at B = 2, 5 w_c; cfm_x_s seed 0 at B = 3 places 0 at 2 and 5 w_c) |
| Intro, bullet 1 | "every combination" becomes "every fixed combination" (same scope issue). The hyperplane sentence adds "already for one field (Proposition 4.3; the planar case is Example 4.4 of Baptista et al.)". | R13 (extended), R25 |
| Intro, bullet 3 | "a data-predicting network given an input that resolves this scale matches the exact probability at the tie where the input is centred in all but one of twenty seed-configuration pairs, and leaves the blends at other ties empty". | R9 (supersedes R6) |
| Consequences (i) | "bounded nonnegative guidance schedules of bounded variation"; "circumcentres of training images, that is, affine combinations of them" instead of "convex combinations". | R13, R23 |
| Consequences (iii) | "Among the operations studied here with strictly positive priors ... (averaging hard-label fields can, at a symmetric tie, Section 4.1)". | R14 |
| Related work | Liu and Zuazua v2: "nearest-support equilibria, which for a mixture are the critical points of a distance potential". New Cai, Su and Wang sentence in `\moveblock{caiflow}` (TMLR: related work; ICLR: App. B.1, after the Cao sentence). Azangulov et al.: "compactly supported data and a class of positive probability". New Du et al. sentence; "its endpoints" becomes "the endpoints of this composition". | R28, R26, R29, R31 |
| Sec. 4 proof strategy; Fig. 2 caption | "stays above a positive constant"; "stays positive, away from zero". | R17 (Lemma `lem:volume` needs the divergence integral to tend to plus infinity) |
| After Prop. `prop:hyperplane` (moveblock) | Credit to Baptista et al. Example 4.4 (VE probability-flow ODE, two points in the plane) and Liu and Zuazua v2 Remark 2.7 (one dimension), related by the change of variables of App. B.1. | R25 |
| Sec. 4.5 and App. B.8 | The two-atom coordinate sigma, sigma_star renamed zeta, zeta_star (Prop. `prop:twoatom` and its proof). Pointer for 1.368 w_c: Appendix E.1 in ICLR, Section 6 in TMLR. | R18, R24 |
| ICLR-only text of Sec. 4.4 | "except at d = 8 and w <= 2 w_c" becomes "except for the simplex in d = 8 at w <= 2 w_c". | R3 (ICLR counterpart) |
| Sec. 6, positive control | 0.992 becomes 0.991 (0.991469; Tables 7 and 8 print 0.991). "within 10^-17" becomes "within 3 x 10^-17" (2.25e-17 at the gap 1e-2). | R2; data of R7 |
| Sec. 6, guided label averaging | "sources at +-1e-9 already reach the atoms" becomes "only the source 0 reaches the midpoint (Theorem 4.8(b); the stopping rule then labels every other source an atom at its first check)". CIFAR: "whose classifier admits the midpoint only above the threshold, the exact composite ends a positive fraction of the sources there in every pair at 2 w_c, up to 0.29"; the ICLR branch likewise. | R12 (`composition_counterexample.py`: `classifier`, else-branch of `run_config`); R10 (`cifar_composition_exact.py`, `classify_1d`) |
| Sec. 6, learned | New sentence: at 1-t = 1e-5 the standard network leaves 0.16, 0.70 and 0.79 of its sources at 2, 5, 10 w_c farther than 0.1 from every atom and the centre, the data-predicting network 0.16 +- 0.16 at 2 w_c. | R19 |
| Sec. 6, spectral (moveblock) | "In d = 8 the basins of z are smaller: 0.019 for the simplex at 5 w_c and 0.002 (one of 512 sources) for the box at w = 5, and below 1/2048 for the simplex at 1.1 and 2 w_c". "we did not compute their mass" replaced by the face statement (k-face threshold; per-axis thresholds 0.076 and 3.68) and the masses: 0.953 and 0.981 of the simplex at 2 and 5 w_c (0.001 at 1.1 w_c), 0.895 and 0.754 of the rectangle at w = 1 and 5, all 512 and 511 of the 512 box sources at w = 1 and 5. | R3/R11, R1 |
| Signed-combinations figure caption | "(b) ... restricted log-odds B(p) = B, 0, -B at B = 1". | R4 (`signed_combinations_probability.py`: Bs = [B, 0, -B]) |
| Fig. 5 caption | "(for the triangle, its centre; the exact composite also ends mass at the edge midpoints, which the networks of (a) and (d), whose endpoints were stored, leave empty, Section 6)"; "and the data-predicting network in all seeds shown; at B = 3, not drawn, one of its five seeds places no source at the midpoint at 2 and 5 w_c (Table 8)". | R8 (restricted to (a) and (d)), R9 |
| Limitations | "the data-predicting network with this input leaves the blends ... empty"; "three to five seeds". | R6, R22 (four seeds for cfm_v_sep, three for cfm_x_o and cfm_x_sq) |
| Conclusion | Scope as in the abstract; "can do so at the tie where it is centred". | R13; R9 (extended) |
| Broader impact | "bounded nonnegative guidance schedules of bounded variation". | R13 |
| Reproducibility statement | Adds `composition_threshold_scaling.py` (Fig. 3(b) and the 0.01% claim: ratio_P 0.99992, 0.99995, 0.99995 at delta = 3e-4) and `learned_composition_exact.py`; `theory_basin_map.py` now also produces the blend masses and the learned edge counts. | R7 |
| Notation table | New row "sigma: fast time, d sigma = beta d tau (Appendix B.7)". | R18 |
| App. B.1 | The noise level sigma renamed varsigma. "the finite equilibrium set of their Theorem 2.5 also contains other points". Schedules: a time-varying weight can be written as a drift error in their Prop. 3.1 and Rems. 3.2 and 3.6, which then keep the convergence of every trajectory when the deviation of the weight from its limit is square integrable in log time, though possibly to another equilibrium; a schedule constant near the data end (a guidance interval) is covered by their Thm. 2.5 from its last change on. Azangulov et al.: "and any class of positive probability". `\placeblock{caiflow}`. | R18, R28, R27, R29, R26 |
| Table 5 | Azangulov support "any compact set; a class with p(c) > 0"; Liu cell "nearest-support equilibria, not always a local minimiser of the distance potential"; "rate sqrt(t_h)" in both cells; caption "the rates sqrt(t_h) are in heat time t_h = varsigma^2/2, and sqrt(t_h) = (1-t)/(sqrt2 t) is O(1-t) in our time t". | R29, R28, R18 |
| App. E.1, positive control | "the script compares"; the captured endpoints lie within 2.25e-17, 2.25e-19, 2.25e-21 along and within 0.0371, 3.71e-4, 3.71e-6 across the line of the atoms at the three gaps. | R15, R7 |
| App. E.1, spectral | Description of `--faces` and of its agreement with Table 6 (exact for the rectangle and the box, within sampling error for the triangle and the simplex because of the rotated SVD basis). | R1 |
| Table 6 caption | Adds "; on the simplex at 2 and 5 w_c and on the rectangle and the box, centroids of other faces take most of the mass" with the venue-dependent pointer. | R1, R24 |
| App. E.1, learned | Distillation control: "a positive control ... at the tie where its input is centred (on the triangle it also leaves the edge midpoints empty)". New sentence naming `theory_basin_map.py` for the learned edge counts. "except ... and of the velocity network with the rescaled input at B = 2 (0.009 +- 0.018, Table 8)". | R19, R16, R5 (cfm_v_s arm L1 at B = 2 by seed: 0, 0, 0.045, 0.002, 0) |
| App. E.1, which change matters | "reliable across seeds at B = 1, 2 and on the triangle; at B = 3 one of five seeds places no source at the midpoint at 2 and 5 w_c". | R9 |
| App. E.1, bottleneck | "follows ... at 5 and 10 w_c(B_Q), though not in every seed at 2 w_c(B_Q)"; "0.135, 0.226 and 0 against 0.179". | R20 (`bottleneck_2d_20261107/cfm_x_sq_seed*`) |
| App. E.1, CIFAR; Fig. 7 caption | New sentence: the classifier returns the midpoint only when w > w_c and abs(s) < s_u, so the zeros for w <= 0.9 w_c follow from Thm. 4.8(b) and do not test it. Caption: "zero for w <= 0.9 w_c, where the classifier excludes the midpoint (Theorem 4.8(b))". | R10 |
| Table 8 caption | "computed as for Table 7 by `learned_composition_exact.py`" (Table 7 has no 1 or 5 w_c column). | R21 |
| Artifacts paragraph | Names `results/stress_positive_control_20261121/` and the new contents of `theory_basin_map_20261121/`; set ragged right in both venues (justified, the long paths gave 5 underfull lines). | R7; layout |
| `refs.bib` | `chidambaram2024guidance` becomes `@inproceedings`, NeurIPS 37, pp. 84968-85005, DOI 10.52202/079017-2698 (the DOI resolves to the proceedings record with these pages; also ref. [11] of Liu and Zuazua v2). New `cai2026particle` (arXiv 2609.06947 v1, 7 Sep 2026) and `du2023reduce` (ICML 2023, PMLR 202:8489-8510). | R30, R26, R31 |

Literature checked here: Baptista et al. v2 Example 4.4 (arxiv.org/html/2501.15785v2: VE process,
two points symmetric about the origin in d = 2; the vertical axis is invariant and its trajectories
converge to the midpoint, off-axis initialisations converge to a data point). Cai et al. (arXiv
abstract and HTML: authors, date; guidance (1-w) v_unc + w v_c with a fixed w > 1; the conditional
law restricts the data law to D_c; Thms. 12, 13, Cor. 14 and Thm. 16 are set-attraction and
absorption statements, with no point limit). Du et al. (PMLR page; Sec. 4 on ar5iv: the summed
score is not the score of the diffused product, reverse diffusion with it generates incorrect
samples, annealed MCMC instead). Liu and Zuazua v2 Sec. 1.2, Prop. 3.1, Rems. 2.7, 3.2, 3.6 and
refs. [8], [11], [19] (lab09 `prior-check/pdf_liu/liu_v2.txt`). Azangulov et al. Sec. 3.2,
assumption (iii) p(c) > 0 and the bound -C_max log p(c) (`prior-check/pdf_az/azangulov26a.txt`).

### 8.3 Layout

The composition and learned figures printed on pp. 16 and 17, after the Limitations, seven and four
pages after their first references (Sec. 4.3 on p. 9, Sec. 6 on p. 13). The three float
environments were moved, unchanged, next to their first reference:
- the composition figure (`\moveblock{compfig}`) to the end of Sec. 4.3: now Figure 3, at the top
  of p. 10 (the ICLR build still prints it in App. E.1 through `\placeblock{compfig}`);
- the signed-combinations figure to the end of Sec. 4.5: now Figure 4, on p. 13;
- the learned figure to just after the "Learned guided label averaging" paragraph: still Figure 5,
  now on p. 15.
All references are by `\ref`, so no text changed; the composition and signed-combinations figures
swapped numbers (3 and 4). Figures 1 and 2 keep their pages, Figures 6 and 7 move one page later
with the longer appendix text, and Table 2 now prints on p. 16, with the paragraph that cites it.

### 8.4 Not applied as proposed

- R8 header "exact midpoint probability": the headers say "midpoint nearly empty" and "near the
  exact probability", because panel (c) does not reach the exact probability in every seed. The
  caption clause "which these networks leave empty" was restricted to (a) and (d): no endpoints
  were stored for (b) cfm_x and (c) cfm_v_s on the triangle, so their edge mass is unknown.
- R6 intro and Limitations wordings: superseded by the R9 intro wording, which already restricts
  the claim to the data-predicting network.
- R3 and R11 wordings: merged into one sentence.
- R7 "add the count to summarize_learned_composition_2d.py": that script imports
  `learned_composition.py`, which needs torch (absent on lab09); the count is written by
  `theory_basin_map.py --learned-edges`, as R16 proposed.
- R1 "extend theory_basin_map.py to classify by face": done, but with the integration and sources
  of `spectral_criterion_check.py` (rtol 1e-8, 2000 RK4 steps, seed 11) instead of the basin-map
  settings, so that the counts refer to the setting of Table 6. No Table 6 column was added (8.1).
- R27 wording: "enters only through their perturbation results ..., which keep ..." would
  attribute to Liu and Zuazua an application they do not state. The text says a time-varying weight
  "can be written as a drift error" there (square integrability in log time suffices because the
  score difference of two empirical laws is bounded by diam/(2 t_h)) and adds the guidance-interval
  case.
- R13 "nonnegative guidance schedules of bounded variation" (Consequences, Broader impact): "bounded"
  kept as well, since Thm. `thm:schedule` assumes w(t) in [0, w-bar] on all of [0, 1).
- R10: panel (b) of the CIFAR figure still prints "zero for w <= 0.9 w_c". It is true, and the
  caption now says why; the figure was not redrawn.

### 8.5 Compile (lab09, tectonic, `scripts/build_papers.sh paper_theory`)

- TMLR: rc 0, 53 pages (before 52), 0 overfull hboxes, 8 underfull (before 9), no undefined
  references or citations, BibTeX without warnings. `main.pdf` and `fig_learned_composition.pdf`
  copied back.
- ICLR test build (scratch `/mnt/data/khoitm8/tmp/fix-A/iclr/`, edit-A's wrapper): rc 0, 54 pages
  (edit-A: 53), 0 overfull, no undefined references; the references still start on p. 14. The
  pointers "1.368 w_c (Appendix E.1)", the Table 6 caption pointer and the Cai sentence in App. B.1
  were checked in the text.
- Pages rendered at 90 dpi and read: TMLR 1-4, 6-7, 9-18, 22, 27-28, 44-45, 48-53; Figure 5 alone
  at 200 dpi before and after.

### 8.6 Open questions for the authors

- Table 6 is not reproducible bit for bit for the triangle and the simplex on lab09, because
  `simplex()` depends on the SVD basis returned by the linear-algebra library (8.1). Fix a
  canonical vertex construction and rerun `spectral_criterion_check.py`, or record the atoms in its
  summary; a rerun would also allow a consistent "other blends" column in Table 6.
- Figure renumbering (composition now Figure 3, signed combinations Figure 4): update slides,
  rebuttal text or notes that cite the old numbers.
- The edge or face mass of the label-bottleneck composite (its edges attract above
  1.001 w_c(B_Q)), and of the networks cfm_v_s and cfm_x on the triangle, is still unknown (no
  endpoints stored).
- On the simplex at 1.1 w_c, 158 of 2048 sources change class between u = 1e3 and 1e4 (slow passage
  near weakly attracting faces); the final classes are used. A longer integration would confirm the
  0.001 blend mass there.
- The schedule sentence of App. B.1 (square-integrable deviation in log time) is this editor's
  reading of Liu and Zuazua v2 Prop. 3.1 and Rem. 3.2; confirm before submission.
- `paper_mechanism/refs.bib` still has the arXiv-only `chidambaram2024guidance` entry (paper B, not
  touched).
