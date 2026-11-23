# A vs B consistency check (round 3)

Repo: `cfm-collapse`, branch `paper-split-drafts`, commit `834f3bf`.
A = `paper_theory/main.tex` (3718 lines). B = `paper_mechanism/main.tex` (2124 lines). Reference = `paper/main.tex`.
Read-only check. Nothing was edited or committed.

Line numbers are `file:line` in the current files.

## 0. Group decisions: are they applied consistently?

| Decision | Status | Where |
|---|---|---|
| Papers are split | Applied | both |
| s10 numbers 0.168 / 0.276 only in A; B qualitative | Applied | A:1147-1149, A:3247-3252; B:1645-1648 says "close to the ones above" |
| thm:endpoint is "cf. Wan et al.", not a contribution, in both | Applied | A:196, A:202-204 ("This is not a new result"); B:364-365, B:431 |
| Composition = "boundary marker, not a practical mechanism" | Applied | A:128, A:308 |
| A to arXiv first; B cites companionA twice | Applied in text (B:254, B:579). **But the bib entry does not match** (see 2.4) | B refs.bib:579-584 |
| B title | Applied | B:63 |
| Landing colour blue | Applied | B:183 (teaser "Landing (blue)") |

## 1. Shared results: same math, same hypotheses?

The mathematical content is the same in A, B and `paper/main.tex` for all four shared items. The drift is in attribution and in the surrounding text.

| # | Item | A | B | Issue | Severity | Fix |
|---|---|---|---|---|---|---|
| 1.1 | as:standing | A:423-428 | B:386-391 | Identical, letter for letter. Allowed by the brief. | none | none |
| 1.2 | prop:collapse, math | A:463-472 | B:402-410 | Same (a)-(d), same hypotheses (h=0, training label y^i). B rewords (c) and (d). | none | none |
| 1.3 | prop:collapse, attribution | A:463 "Exact conditional collapse; h=0", no citation, own proof | B:402 "Exact field at hard conditioning; cf. Baptista et al." | B says the result is known (Baptista). A states it as its own result with a proof and does not cite Baptista there. A reader of both sees two different claims of origin. | should fix | Add "cf. Baptista et al. (2025)" (or "standard") to A's title at A:463, or drop the cf. in B. Same wording in both. |
| 1.4 | prop:collapse used in a B proof | B:1232 "by the computation in the proof of Proposition prop:collapse(c)" | - | B does not prove prop:collapse (B:1130, B:1190 say the background is proved in cited works). The pointer goes to a proof that is not in B. | should fix | Replace with "solving this linear ODE, as in Proposition prop:collapse(c)", or give the one-line solution. |
| 1.5 | prop:kernel-field | A:480-489 "Kernel-weighted population minimiser" | B:418-427 "Exact field under label noise" | Same equation and hypotheses (h>0, t<1). Names differ. | cosmetic | Fine if intentional (contract asks B to use its own words). |
| 1.6 | thm:endpoint | A:496-503 "Endpoint law under label smoothing; cf. Wan" | B:431-438 "Exact endpoint law under label noise; cf. Wan" | Same statement. B defines p_i^{(h)} inline; A defines it at A:491. Same "cf.", no theorem number in either. | cosmetic | Use "label noise" in A's title too (A uses both "label smoothing" and "label noise" for the same thing). |
| 1.7 | Endpoint law definition | A:417-418 "a weak limit as t->1" | B:383-384 "the law at t=1 of the minimiser's flow" | B drops "weak limit". The field is not defined at t=1, so B is less precise. | cosmetic | Add "(the weak limit as t->1)" in B:384. |
| 1.8 | prop:regular (A) cited by B | A:1090-1104 (a) | B:576-579 | B's paraphrase (integrable Lipschitz constant and integrable abs v(0,t) give a bi-Lipschitz flow map, no atoms) matches A(a). | none | none |
| 1.9 | Stale FLAG comments in B | - | B:400-401 "(6.4 in paper A)", B:442-443 "Paper A cites Wan et al. Theorem 5.3" | A no longer prints these numbers (A:255, A:349 are FLAGs too). Comments only, not printed. | cosmetic | Update the two B comments to "A also omits the number". |

## 2. Novelty claims and how each paper describes the other

| # | A | B | Issue | Severity | Fix |
|---|---|---|---|---|---|
| 2.1 | A:1097-1101, prop:regular(b): in d=1, a bounded data prediction ends on fixed points of its limit g; a fixed point with g'<1 attracts an open interval, one with g'>1 at most one point | B:193-197, B:473-491, thm:relerr (headline) | Same mechanism, different generality. In A(b), slope g'<1 = contraction toward the point = landing; g'>1 = no landing. B's thm:relerr(b)/(c) is the per-trajectory, any-d version with error measured against the exact posterior mean, and B's own example (B:1464-1467, x_hat = a + rho (z-a)) is the linear case of A(b). B never mentions A(b). A reviewer who reads both can say part of B's headline is in companionA. | should fix | One sentence in B after thm:relerr or in Related work: "In one dimension, companionA (Proposition regular(b)) shows that a bounded data prediction ends on the fixed points of its limit, attracting when the slope is below one; Theorem relerr is the per-trajectory version in any dimension, with the error measured against the exact posterior mean." This also uses companionA a third time; the group must allow that (decision said "twice"). Alternative: say it without citing, e.g. "the one-dimensional case reduces to a slope condition". |
| 2.2 | A:1084-1085, A:1226-1230: "small regression loss does not control where that difference sends the endpoint (Benton)"; experiment "lossrisk" | B:201-206, prop:loss-no-certificate (B:1365-1372) | Same message. A cites Benton and gives an experiment; B proves a construction. No conflict, no double claim (A does not claim it as new). | none | none |
| 2.3 | A has no sentence about B | B:254-256 "Companion work studies which **sampler-side** changes of an exact conditional field keep its endpoints on the training set" | A also covers training-side and learner-side changes: label noise in training (A:107, A:179) and label averaging by a coarse network (A:108, A:542). "Sampler-side" is too narrow. | should fix | B:254: "studies which changes of an exact conditional field, from label noise and label averaging to guidance and composition, keep its endpoints on the training set". |
| 2.4 | - | B refs.bib:579-584: `author = {Anonymous}`, `note = {Companion submission}` | Group decision: A is a public arXiv preprint when B is submitted. The entry still says "Companion submission". B's header comment B:18-19 also says "cited as an anonymous work". | should fix | When A is posted: real authors, arXiv id, `note = {arXiv preprint}`; cite it in the third person (NeurIPS rule for public own work). Update B:18-19. |
| 2.5 | A does not mention B anywhere | - | TMLR requires disclosure of closely related work under review elsewhere. Text cannot cite B yet (B is double-blind). | should fix (process) | Tell the TMLR action editor in the submission form that a companion paper on learned fields is under review, and upload an anonymised copy of B as supplementary for the editor. |
| 2.6 | A:375-388 and A:1869 (comparison table) | B:243-256 | Both describe Wan, Liu (2025, 2026), Baptista the same way in substance. | none | none (see 5.2 for wording) |
| 2.7 | - | B:214 "to our knowledge, the direction with the network first has not been run before" | A does not touch swaps. No conflict between A and B. | none | none |

## 3. Numbers

| # | A | B | Issue | Severity | Fix |
|---|---|---|---|---|---|
| 3.1 | A:1147-1149 0.168 / 0.276 (s10) | B:1640-1648 | **No s10 off-atom fractions in B.** B says "close to the ones above" (B:1645). Confirmed. | none | none |
| 3.2 | - | B:1991 `0.168 [0.095, 0.241]` | This is EXP-1 "velocity rel. error vs (star)" at 10^6, also in paper/main.tex:3801 (0.168 +- 0.052; half-width 0.073 = 1.39 x 0.052, consistent). Not s10. Coincidence. | none | none |
| 3.3 | - | B:2002 `0.276 [0.160, 0.393]` in tab:exp1 caption | EXP-1: cosine run at 10^6 minus constant-rate run at 2x10^5 (0.396 - 0.120 = 0.276). Not s10, but it sits in the hard-conditioning appendix, exactly where contract §5 says "no 0.276". It is new relative to paper/main.tex, so its interval is not checked by me. A grep-based checker will flag it. | cosmetic | Verify the interval against `results/exp1`. Optionally write the ratio instead, or add "(not the h=6 fraction of the companion)" only in a source comment. |
| 3.4 | A:1147 s10 h=4/h=6 at RK4, 1-t=1e-4: 0.168, 0.276 (sample SD 0.012, 0.008) | B:1621-1623 first retrain, same integrator and cutoff: 0.158 +- 0.031, 0.254 +- 0.047 (population SD) | Two retrains, same configuration, two sets of numbers. Not a contradiction: B says the s10 values are "close to" its own. A reader of both papers can still wonder which is "the" value. | cosmetic | In B:1645 keep "close to"; in A:1147 "In a further retraining" is fine. No change needed unless the group wants A to say "one of two retrainings". |
| 3.5 | A:1149, A:3250-3252: s10 SDs are **sample** SDs (0.012, 0.008; population 0.010, 0.006) | paper/main.tex:3363 "0.168+-0.012", under that paper's "every +- is a population SD" rule | A corrects the label of paper/main.tex. Contract §5 agrees (sample SD 0.008). Consistent between A and contract; paper/main.tex is the outlier. | none | none |
| 3.6 | A:3262-3265 tr Sigma_post = 1.018 | B:623, B:2000, B:2034 tr Sigma_post = 1.018 | Same reference value of the same EXP-1 problem. A setup constant, not a result. | none | none |
| 3.7 | Setup numbers: d=2, N=200, sigma_obs=0.1, 4-layer width-128 MLP, 35.75M U-Net, N=2000, 60000 it., h in {4,5,6} | same | Consistent across A, B and paper/main.tex. | none | none |
| 3.8 | - | B headline numbers 88%, 96%, 0.51, 2.48, 1.33, 89.6%, 95.6% | Not in paper/main.tex (the swap is new). Internally consistent with tab:swap (B:737-746): 0.880 at s=1 on the 1000-image model; 0.896 / 1.000 on the public model; 0.956 off at s=1; 4.1% off-atom -> 96% copies. Not checked against `results/` here. | none | Run `paperB_verify_*` in the number check. |
| 3.9 | A:1162, A:1217, A:1304 (0.406 etc.) | - | A-only. No overlap with B. | none | none |

## 4. Notation and terminology

### 4a. Across the two papers

| # | Symbol | A | B | Severity | Fix |
|---|---|---|---|---|---|
| 4.1 | rho | endpoint noise std (A:283, A:1073); local radius in proofs (A:2016, A:2140) | trapping radius in prop:localtransfer (B:561-565); EDM schedule exponent rho=7 (B:1695); rho_R = R/(g-R) (B:1478) | cosmetic | B: see 4.8. A keeps rho for endpoint noise. |
| 4.2 | varrho (relative error) | not used | B throughout | none | none |
| 4.3 | sigma | fast time d sigma = beta d tau (A:909, A:1491); sigma_obs | EDM noise level; sigma_obs | cosmetic | Fine; papers are read separately. |
| 4.4 | s | blow-up coordinate (A:1186, A:2609) | swap level (B:137, B:1172) | cosmetic | Fine. |
| 4.5 | Omega | a set (A:2016) | off-atom bound (B:1479) | cosmetic | Fine. |
| 4.6 | Posterior mean | m_p, bar m, q_{p,j} | m^star, w_j | cosmetic | Fine, but see 4.12 (B borrows A's m_p inside one proof). |
| 4.7 | w | guidance strength w, w_c; weights w_i^{(h)} | weights w_i, w_j; a weight function w in thm:risktransfer (B:1316) | cosmetic | Fine. B never uses w for guidance. |
| 4.8 | "label smoothing" vs "label noise" | both terms (A:496, A:516 "smoothing"; A:199 "noise") | "label noise" (B:376); "label smoothing" once (B:1971) | cosmetic | Pick "label noise" in both theorem titles. |
| 4.9 | off-atom criterion | A:3248-3249 on-atom iff d1 <= d2/3 (cites Yoon) | B:676-678, B:1710 off-atom iff d1/d2 >= 1/3 | cosmetic | Equality case differs. Use the same inequality in both, e.g. "off-atom iff d1 >= d2/3". |
| 4.10 | t vs sigma | flow time t only | t for theory, sigma for EDM, t = 1/(1+sigma), Z = tx; B says the EDM measurement uses prop:trap, not relerr coordinates (B:668-674, B:1006-1007) | none | Honest and consistent. |

### 4b. Inside B (one symbol, two meanings)

| # | Where | Clash | Severity | Fix |
|---|---|---|---|---|
| 4.11 | B:561 `D = min_{j!=i} abs(x^j - a)` vs denoiser D, D_theta, D_k (B:1476, B:1522) | D = distance and D = denoiser | should fix | Use g in prop:localtransfer, as in app:relerr (B:1425 defines the same quantity as g). |
| 4.12 | B:1247-1248 proof of prop:localtransfer uses m_p, q_{p,j} | A's notation, not defined in B; B elsewhere writes m^star and w_j | should fix | Write m^star and w_j^{(h)}. |
| 4.13 | B:1439 "e = Z - a" in the proof of thm:relerr | e_t is the scalar error in the statement (B:477) | should fix | Rename the vector to u or Y (B:1205 already uses Y_t = Z_t - a). |
| 4.14 | B:1504 "h = gamma + Omega" in proof of prop:trap | h is the label bandwidth | should fix | Rename to eta (thm:relerr proof uses eta = gamma + omega, B:1439). |
| 4.15 | B:1425 delta_i = max_k abs(x^k - a); B:485 delta_t in thm:relerr(c); B:1375 delta in prop:loss-no-certificate | three deltas | cosmetic | Rename delta_i (e.g. Lambda_i or diam_i). |
| 4.16 | B:376 omega ~ N(0, I_k) label noise vs omega_t (B:478), omega(y,sigma) (B:1527) | omega twice | cosmetic | Rename omega_t (e.g. beta_t or "off-atom term" o_t). |
| 4.17 | B:972, B:1531 Heun weight theta_k vs network parameters theta in D_theta | theta twice in one formula region | cosmetic | Rename Heun weight (e.g. lambda_k). |
| 4.18 | B:1643, B:1653 `m^*`, `\hat m` | elsewhere `m^\star`, `\hat x_1` | cosmetic | Use `m^\star` and `\hat x_1`. |

## 5. Text reuse (beyond as:standing and equations)

Measured with 8-grams per paragraph and 6-grams per sentence (scripts in this folder: `ngram.py`, `sent.py`). Total shared 8-grams: 334 of 27280 (A) and 17783 (B). Low overall. The near-verbatim pieces are:

| # | A | B | What | Severity | Fix |
|---|---|---|---|---|---|
| 5.1 | A:3225-3233 | B:1967-1973 | EXP-1 protocol: "The prior is x~N(0,I_2), the observation is y=Ax+eta with a random 1x2 matrix A and eta~N(0,0.1^2), and N=200 training pairs are drawn; ... The velocity network is a 4-layer, width-128 MLP with SiLU activations and a 64-dimensional time embedding, trained with Adam (learning rate 10^-3, batch 256) for 2x10^5 iterations". Two sentences, about 70% of 6-grams shared. | blocker (contract §2: no paragraph in both) | Rewrite one side. Easiest: A gives a short version and says "the linear-Gaussian problem and network of [standard setup]: d=2, k=1, N=200, sigma_obs=0.1, 4-layer width-128 SiLU MLP, Adam 1e-3, batch 256, 2x10^5 steps" as a table row. |
| 5.2 | A:368-369 | B:246-247 | "Wan et al. prove for flow-matching ODEs, finite data included, that almost every trajectory converges and that the endpoint law is the data law." | should fix | Reword B: "Wan et al. show that the flow-matching ODE, also for finite data, converges for almost every start and has the data law as its endpoint law." |
| 5.3 | A:370-373 | B:251-253 | Liu et al. (2026) sentence, close wording **and content drift**: A says the limits are "nearest-support equilibria, which for a mixture are the critical points of a distance potential". B says "equilibria of a distance potential" for mixture and guidance alike. B is less precise. | should fix | B: "converges to one of finitely many equilibria (for a mixture, critical points of a distance potential), which need not be a training example." |
| 5.4 | A:3218-3219 | B:1960-1962 | "Every across-seed +- is a population standard deviation (denominator n); at n=5 the sample standard deviation is larger by sqrt(5/4) ~ 1.12." Identical. | cosmetic | Reword one. |
| 5.5 | A:1464-1466 | B:1148-1150 | Appendix organisation boilerplate: "Each main-text result is restated, with its original number, immediately before its proof. Table notation collects the notation and Table roadmap shows where each result is proved and what it uses." Identical. | cosmetic | Reword one. |
| 5.6 | A:1468-1496 | B:1152-1177 | Notation tables share the first six rows. | cosmetic | Acceptable for notation; leave. |
| 5.7 | A:1404-1405, A:1444 | B:1095-1096, B:1128 | Broader impact / reproducibility boilerplate ("All experiments use synthetic data and the public CIFAR-10 dataset; no personal or human-subject data are involved"; "Every assumption is stated where it is used"). | cosmetic | Reword one. |
| 5.8 | A:172-176 | B:103-108 | Opening sentence of the introduction: same citation list, close wording ("Flow matching and stochastic-interpolant models ... regress / learn a velocity field by regression on a path from noise to data"). Below the 6-gram threshold but visible. | cosmetic | Start B with its own question (copies vs new images) instead. |
| 5.9 | A:480-494 vs B:418-429 | | kernel-field equation block | none | Equation; allowed. |

Process item linked to reuse: A's LaTeX source contains comments that name paper B and internal decisions: A:4-5, A:101-103, A:1154-1155 ("paper B describes it only qualitatively"), A:1408 ("Draft by the assistant"), A:1409 (TODO), A:255, A:349 (FLAG). arXiv publishes the source. **Severity: blocker before the arXiv upload.** Fix: run `arxiv_latex_cleaner` (or strip `%` comments) on A before posting.

## 6. Contract section 5 (take / not take)

| Item | Status | Evidence |
|---|---|---|
| Take: no shared text, figures, numbers | Mostly holds. Exceptions: 5.1-5.5 (text), 3.6-3.7 (setup constants, acceptable). Figures: B has no kernel-tracking panel (B:608-617 caption covers EXP-1 h=0 and CIFAR h=0 only); A has its own `fig_kernel_tracking` (A:3270). | see section 5 |
| Take: thm:relerr headline; transfer demoted to lemma | Holds | B:79, B:124, B:473; B:526-527 "Lemma" |
| Take: late contraction and "bound never violated" only descriptive / code check | Holds | B:219-220, B:864-867, B:977-979 |
| Take: kernel tracking to A; B self-contained | Holds | A:1131-1153, A:3222-3305; B:2008-2009, B:2121-2122 (removal notes); B cites companionA only twice |
| Take: fix F3 ("We test Theorem relerr") by wording | Holds | no "We test" in B; B:668-674 says the EDM quantities are those of prop:trap |
| Not take: A headline to AND / class label | Holds | A:101-103 |
| Not take: open B with exact->net | Holds | B abstract opens with the landing condition; exact->net is used to tell memorising from non-memorising models (B:786-793) |
| Not take: "fix n2 NaN" | Holds | no n2 / NaN in B |
| Not take: 0.276 in B hard-conditioning | Holds for the s10 value. A coincidental 0.276 (EXP-1 cosine difference) is now in B:2002 | see 3.3 |
| Not take: new inference or training | Holds | B:1020-1046 lists them as planned; A has no new runs listed |

## 7. Summary table of fixes by severity

Blockers (2):
1. EXP-1 protocol paragraph near-verbatim in both (A:3225-3233, B:1967-1973). Rewrite one side.
2. Strip LaTeX comments from A before the arXiv upload (they name paper B, the decisions, "Draft by the assistant", TODO).

Should fix (12): 1.3, 1.4, 2.1, 2.3, 2.4, 2.5, 4.11, 4.12, 4.13, 4.14, 5.2, 5.3.

Cosmetic: 1.5-1.7, 1.9, 3.3, 3.4, 4.1, 4.3-4.9, 4.15-4.18, 5.4-5.8.

## 8. Tóm tắt (tiếng Việt, cho người mới)

- Bốn kết quả dùng chung (as:standing, prop:collapse, prop:kernel-field, thm:endpoint) có cùng nội dung toán ở A, B và bản gốc. Không có giả thiết nào bị đổi.
- Các quyết định của nhóm đã được áp đúng. B không có số s10 (0.168, 0.276). Cả hai bài đều ghi thm:endpoint là hệ quả của Wan et al. A gọi composition là "boundary marker". B có tiêu đề mới và trích companionA đúng hai lần.
- Có hai lỗi chặn (blocker). Thứ nhất: đoạn mô tả thí nghiệm EXP-1 gần như chép nguyên văn ở cả hai bài; hợp đồng cấm điều này. Thứ hai: mã nguồn LaTeX của A có comment nhắc tới bài B, "Draft by the assistant" và TODO; arXiv công khai mã nguồn, nên phải xoá comment trước khi đăng.
- Về nguồn gốc kết quả: B ghi prop:collapse là "cf. Baptista", còn A trình bày như kết quả của mình mà không trích. Cần ghi giống nhau ở hai bài.
- Về tính mới: prop:regular(b) của A (một chiều, độ dốc nhỏ hơn 1 thì hút) là trường hợp riêng của cơ chế trong thm:relerr của B. B nên nói một câu về điều này, để reviewer không cho rằng B giấu phần đã có ở A.
- B mô tả A là bài về thay đổi "phía sampler". Mô tả này hẹp quá, vì A còn xét label noise lúc train và label averaging. Nên sửa câu ở B:254.
- Mục bib `companionA` vẫn ghi "Anonymous, Companion submission". Theo quyết định, A sẽ lên arXiv trước, nên cần ghi tên tác giả thật và số arXiv.
- Một số câu trong phần related work gần giống nhau (câu về Wan, câu về Liu 2026). Câu về Liu ở B còn kém chính xác hơn A. Nên viết lại câu ở B.
- Trong B có vài ký hiệu bị dùng cho hai nghĩa: D (khoảng cách và denoiser), e (vector và sai số), h (bandwidth và γ+Ω), θ (tham số mạng và trọng số Heun). Nên đổi tên trong chứng minh.
- Số 0.276 vẫn xuất hiện ở B:2002, nhưng đó là số khác (hiệu hai lần chạy EXP-1), không phải số s10. Chỉ cần kiểm lại khoảng tin cậy với `results/exp1`.
- A nên báo cho action editor TMLR biết có bài B đang được review, kèm bản ẩn danh.
