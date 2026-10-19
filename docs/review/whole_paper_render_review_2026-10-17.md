# Full rendered-paper review — 2026-10-17

Canonical artifact: `paper/main.pdf`, 95 PDF pages. Source revision supplied by coordinator: SHA256 `A0F319683CEE5B0390D29757974B435F7E23623BEA86732A62C6B472A47B351C`.

## Scope and method

I visually inspected **every PDF page, 1–95**, linearly, using the provided page PNGs at their original 100 dpi dimensions. For efficiency I constructed horizontal pairs with Pillow without resizing either page and displayed every pair using `view_image(detail="original")`. This was not a contact-sheet-only or extracted-text review. Pair images are `tmp/whole-paper-audit-2026-10-17/render-review-pair-01.png` through `render-review-pair-95.png` (odd starts).

This review establishes rendered layout/readability coverage. It does **not** certify the mathematical correctness of the proofs, factual correctness of references, PDF metadata anonymity, or interactive hyperlink destinations. The visible title page is anonymous, with “Anonymous authors / Paper under double-blind review”; headers identify the TMLR submission. No visible author identity was noticed. Visible citations and internal references are styled in blue; no visible unresolved `??` references were noticed. Metadata and clickable link behavior require separate checks.

## Findings

Severity: P2 = fix before typeset acceptance; P3 = worthwhile clarity/layout improvement. No P0/P1 visual defect or clipped equation/table was observed.

1. **P2 — Figure labels become too small to serve their stated evidentiary purpose. PDF p62, Figure 13 (`fig:traintraj`, source around main.tex:4209).** Six trajectory panels fit in one horizontal row. Their individual covariance/atom-count annotations and legend are barely readable at ordinary page size; the caption explicitly asks the reader to use those printed quantities. Arrange as two rows of three and enlarge the annotations. Similar small-label cases are Figure 12 on p50 (`fig:interventions`, five panels), Figure 20 on p73 (dense annotations), and the inset annotations in Figure 31 on p81. Captions mitigate the problem but do not make the plotted annotations readable.

2. **P2 — Image examples are unnecessarily miniaturized. PDF pp86–87, Figures 40–41 (`fig:exp3prog`, `fig:exp3cifar`, source around main.tex:5615 and 5631).** On p86 the five MNIST grids are only 0.44 text width each, with near-microscopic headings. On p87 two CIFAR grids use roughly half width each and are vertically centered on a mostly empty float page. The page has room to show materially larger images. Figure 41 is particularly difficult to use to judge the caption's claimed near identity. Stack the two grids at larger width, crop their embedded margins, or provide a readable shared column heading.

3. **P2 — Overlapping column headings. PDF p88, Figure 42 (`fig:imagebandwidth`).** The rightmost “training image nearest the mean” heading visibly crowds/overlaps the adjacent “true image” heading. The image grid itself is readable. Shorten or wrap the last two headings in the source figure.

4. **P3 — Extreme vertical stretching. PDF p60, end of E.2 and beginning of E.3 (`An audit protocol for conditional flows`, main.tex around 4105–4127).** Large blank bands separate the opening material, “Three tests narrow this down”, E.3 heading, and its introductory sentence. The heading and introduction look disconnected. This appears to be page-bottom justification/float pressure; keep heading and intro together and allow a ragged bottom or rebalance the page.

5. **P3 — A theorem statement is interrupted by a figure. PDF pp11–12, Theorem 2.** The statement begins at the bottom of p11, then resumes on p12 only below Figure 3 and its caption. This forces readers to carry the hypotheses across a large unrelated visual block. Start the theorem on p12 or move the figure so the complete statement reads continuously. Theorem 4 is also split across pp52–53, though without an interposed float and therefore less disruptive.

6. **P3 — Dense related-work table. PDF p47, Table 5.** The full-height four-column table uses small, heavily justified text and awkward line spacing in the citation column (for example Gao & Li / Bertrand). It remains decipherable at original resolution, but is materially harder to read than the surrounding prose. Give the prose columns more room, use ragged-right cells, or split the table. No clipping was seen.

7. **P3 — Unhelpful literal equation marker. PDF p20 Proposition 2 restatement and pp25,39,41,44,49,52,64,80 and elsewhere.** The literal reference `(*)` appears repeatedly for the collapsed field, while the main Proposition 2 display on p4 has no visible matching star tag. This is a navigation problem even if the intended equation is inferable. Give the field an actual numbered label or refer directly to Proposition 2(a). Coordinator is inspecting source.

8. **P3 — Heavy forward navigation inside proof restatements. PDF pp34–36, A.24–A.25.** The restatements use unnumbered displays while proofs refer to equations (29)–(33), whose numbered versions occur only on pp51–52 in Appendix D. Those equations exist, so this is not a broken-reference finding. Make the canonical numbered destination explicit or place numbers on the local restatement to reduce back-and-forth.

## Claim wording noticed during visual reading (coordinator to adjudicate)

These are not mathematical counterexamples and are outside the visual acceptance decision:

- **PDF p86, Figure 40 caption:** “identical to one another and equal to the nearest training image” coexists with a stated final pixel variance of 0.0012. The exact equality wording exceeds what the displayed finite-resolution grids/nonzero statistic directly establish. “Visually nearly identical” would match the finite-time evidence. The same caption calls this “loss→0-paced collapse”; the displayed finite training trace alone does not establish an asymptotic mechanism.
- **PDF p87, Figure 41 caption:** one finite CIFAR run is said to “confirm” the collapse mechanism and its residual mismatch is attributed to a “harder loss landscape”. The visual evidence establishes the observed completion pattern; the mechanism/causal attribution deserves the same care used in the main-text limitations.
- **PDF p84, Figure 36 caption:** finite trained-network and nearest-atom measurements are described as directly “confirming Theorem 1's ... endpoint law”. The main text elsewhere correctly separates exact-field endpoint statements and finite-time learned-network diagnostics. Consider “consistent with” for this caption.

## Page-by-page coverage ledger

Every entry below was displayed and visually reviewed at full original 100 dpi dimensions. “Clear” means no additional material layout issue noticed, not mathematical acceptance.

| PDF page | Inspection note |
|---:|---|
| 1 | Clear; anonymous title/abstract visible. |
| 2 | Clear; Table 1 readable. |
| 3 | Clear; Figure 1 compact labels, caption readable. |
| 4 | Clear; main Proposition 2 has no visible star tag. |
| 5 | Clear. |
| 6 | Clear. |
| 7 | Clear. |
| 8 | Some lower-page whitespace; Table 2 readable. |
| 9 | Clear; Figure 2 readable. |
| 10 | Clear; Table 3 readable. |
| 11 | Theorem 2 begins near bottom. |
| 12 | Figure 3 interrupts continued Theorem 2 statement. |
| 13 | Clear; Figures 4–5 readable, compact legends. |
| 14 | Clear; Figure 6 readable. |
| 15 | Clear; conclusion, reproducibility, bibliography begins. |
| 16 | Bibliography readable; long URL lines wrap without clipping. |
| 17 | Bibliography readable. |
| 18 | Clear. |
| 19 | Clear. |
| 20 | Clear except literal (*) marker in restatement. |
| 21 | Clear. |
| 22 | Clear. |
| 23 | Clear. |
| 24 | Clear. |
| 25 | Clear except (*) cross-reference. |
| 26 | Clear. |
| 27 | Clear. |
| 28 | Clear. |
| 29 | Clear. |
| 30 | Clear. |
| 31 | Clear. |
| 32 | Clear. |
| 33 | Clear. |
| 34 | Forward equation-reference navigation noted. |
| 35 | Forward equation-reference navigation noted. |
| 36 | Forward equation-reference navigation noted. |
| 37 | Clear. |
| 38 | Clear. |
| 39 | Clear except (*) reference. |
| 40 | Clear. |
| 41 | Clear. |
| 42 | Clear. |
| 43 | Clear; Figure 7 readable. |
| 44 | Clear; Table 4 readable. |
| 45 | Clear; Figure 8 compact annotations. |
| 46 | Clear; Figures 9–10 readable, compact labels. |
| 47 | Dense small Table 5; readability improvement advised. |
| 48 | Clear. |
| 49 | Clear; Figure 11 compact annotations. |
| 50 | Figure 12 annotations too small. |
| 51 | Clear; numbered canonical equations 29–32 visible. |
| 52 | Clear; canonical equation 33 visible; Theorem 4 starts near end. |
| 53 | Clear; Theorem 4 continuation and Proposition 20. |
| 54 | Clear. |
| 55 | Clear; Table 6 readable. |
| 56 | Clear. |
| 57 | Clear. |
| 58 | Clear. |
| 59 | Clear. |
| 60 | Excessively stretched whitespace; E.3 heading/intro separated. |
| 61 | Clear; audit box readable. |
| 62 | Figure 13 very small panel annotations; Figure 14 compact. |
| 63 | Clear. |
| 64 | Clear. |
| 65 | Clear; slightly loose paragraph spacing. |
| 66 | Clear; Figure 15/Table 8 readable. |
| 67 | Clear; Table 9 readable. |
| 68 | Clear; Figure 16 compact but readable. |
| 69 | Clear; Figure 17 compact labels. |
| 70 | Clear; Tables 10–11 readable. |
| 71 | Clear; Tables 12–14 readable. |
| 72 | Clear; Figure 18/Tables 15–16 readable. |
| 73 | Figure 20 annotation size marginal; Figure 19 readable. |
| 74 | Clear; Table 17/Figure 21 readable. |
| 75 | Clear; Figures 22–23 compact but readable. |
| 76 | Clear; Figure 24 readable. |
| 77 | Clear; Figure 25 compact labels; Table 18 readable. |
| 78 | Clear; Figures 26–27 readable. |
| 79 | Clear; Figure 28 dense annotations; Table 19 readable. |
| 80 | Clear; Figure 29/Tables 20–21 readable. |
| 81 | Figure 31 inset labels tiny; Figure 30 readable. |
| 82 | Clear; Figures 32–33 readable. |
| 83 | Clear; Figures 34–35 readable; raw variable names in plot title are visually inelegant. |
| 84 | Figure 36 compact annotations; Figure 37 readable; claim wording flagged. |
| 85 | Clear; Figures 38–39 readable. |
| 86 | Figure 40 grids/headings too small; equality wording flagged. |
| 87 | Figure 41 tiny grids on mostly blank page; causal wording flagged. |
| 88 | Figure 42 rightmost column headings crowd/overlap. |
| 89 | Clear; Figure 43 image grid readable. |
| 90 | Clear; Figure 44 image grid readable. |
| 91 | Clear; Figure 45 image grid readable. |
| 92 | Clear; Figure 46 grid readable, compact headings. |
| 93 | Clear. |
| 94 | Clear; Table 22 readable; whitespace below end of appendix is acceptable. |
| 95 | Clear; final appendix text and hash wrap without clipping. |

## Acceptance

Coordinator adjudication after checking the source: finding 7 is **not a missing-marker defect**. The literal star marker is present in canonical Proposition 2(a), `paper/main.tex:300`, and repeated in its restatement at line1191. The optional suggestion to replace literal markers with a normal equation reference remains an editorial improvement. Treat page4's “no visible star tag” note as a visual observation that did not survive source verification, not an accepted factual finding. Equations29–33 in finding8 also resolve correctly to their canonical statements later in the appendix.

Full 95-page visual coverage is complete. The manuscript is generally readable, with no observed clipped equations/tables or missing-page artifacts. **Full typeset acceptance is withheld** pending the figure-readability and overlapping-header fixes above. Mathematical and bibliographic acceptance remain separate coordinator decisions.
