# Gửi Khoi: kiểm tra cuối cho bài A và bài B (vòng 3)

Repo `cfm-collapse`, nhánh `paper-split-drafts`, commit `834f3bf`. A = `paper_theory/main.tex`, B = `paper_mechanism/main.tex`. "A:743" là dòng 743 của A.
Tài liệu này gộp 8 báo cáo của các tác nhân (chương trình AI kiểm bài). Mọi mục giữ lại đều đã được mở đúng dòng trong repo để đối chiếu. Mục nào chưa đối chiếu được thì ghi "chưa kiểm".

## 1. Tóm tắt (5 dòng)

1. **Toán:** hai người kiểm độc lập không thấy lỗi trong chứng minh (A: cor:twofields, prop:twoatom, rem:generic; B: thm:relerr, prop:trap, prop:heun). Lỗi nằm ở câu diễn giải: vài câu nói rộng hơn định lý, và prop:heun(e) thiếu một giả thiết.
2. **Trích dẫn:** gần như đúng hết. Số định lý của Wan (Thm 5.3) và Baptista (Thm 6.4, Ex. 4.4) đã xác nhận trong PDF, nên ghi lại số được và xoá các dòng FLAG. Có một chỗ trỏ sai: Benton "Theorem 1" ở A.
3. **Số liệu:** chạy lại bằng code viết độc lập, bảng ngưỡng của A khớp đến 3 chữ số, và mọi biến thể thử thm:relerr của B đều khớp. Tôi tính lại số 0.276 ở B:2002 từ `results/exp1`: đúng.
4. **Phải sửa trước khi nộp:** 5 mục (phần 2). Mỗi mục sửa bằng một hai câu.
5. **Việc của Khoi:** đọc kỹ khoảng 2 giờ 15 phút (phần 4). Lời khai về LLM ở A:1413-1415 và B:1103-1105 nói tác giả đã kiểm các chứng minh này. Lời khai đó chỉ đúng khi có người kiểm thật.

## 2. Phải sửa trước khi nộp

**P1. Câu "tổ hợp hai trường không rời ảnh huấn luyện" sai khi nhãn cứng.** A:743-747 và A:994-995. *2 người kiểm cùng thấy.*
- Sai gì: cor:twofields chỉ đúng khi prior dương hẳn (p, q thuộc Ppos, tức h > 0), và chỉ "hầu chắc chắn". Câu diễn giải bỏ cả hai điều kiện.
- Vì sao quan trọng: ở h = 0 câu này sai. Phản ví dụ: N = 2, p = e_1, q = e_2. Khi đó (1+w)v_{e_1} - w v_{e_2} = ((1+w)a_1 - w a_2 - x)/(1-t), nên mọi điểm xuất phát đều về (1+w)a_1 - w a_2, không phải ảnh huấn luyện. Chính A:643-645 cũng nói trung bình hai trường nhãn cứng đưa mọi điểm về trung điểm.
- Sửa A:746-747: `are combinations of two exact fields as well. With strictly positive priors (any $h>0$), none of them moves the endpoints off the training examples, except from a null set of initial points; at hard labels they can.`
- Sửa A:994-995: `rules out every combination of two fields with strictly positive priors`.
- Nguồn: proof_audit_1 §1, proof_audit_2 §3.

**P2. "Remark rem:generic shows that both are exceptional" nói quá.** A:943-944 và A:1350-1352. *2 người kiểm cùng thấy.*
- Sai gì: Remark chỉ chứng minh rằng profile không hyperbolic là hiếm (theo prior). Với điều kiện mặt (z không nằm trong bao affine của một mặt con của conv S), Remark chỉ đưa hai điều kiện đủ. Chính nó viết phần này "remains open" (A:966-967).
- Phản ví dụ: ba atom (1,0), (-1,0), (0,1) và z = 0. Điểm z nằm trên cạnh nối hai atom đầu, nên điều kiện mặt hỏng.
- Sửa A:943-944: `Remark~\ref{rem:generic} shows that nonhyperbolic profiles are exceptional in the priors, and that the face condition holds when $|S|=2$ or when $z$ lies in the relative interior of $\operatorname{conv}S$, which covers all our configurations.`
- Sửa A:1351-1352 (thay câu "The latter are exceptional ..."): `Nonhyperbolic profiles are exceptional in the priors (Remark~\ref{rem:generic}), and faces through the candidate do not occur in our configurations; neither case is shown to be harmless.`
- Nguồn: proof_audit_1 §3, proof_audit_2 §1.

**P3. prop:heun(e) dùng một bất đẳng thức chưa được giả thiết.** B:1543, B:1556-1562; chứng minh ở B:1589-1592.
- Sai gì: kết luận "on-atom" cần e(x_{K-1}, σ_{K-1}) ≤ ϱ_{K-1} n_{K-1} + γ_{K-1}. Giả thiết của (e) chỉ chặn sai số ở x_k và ở điểm dự đoán x̃_k với k ≤ K-2, không bao giờ ở x_{K-1}. Các ký hiệu ϱ_{K-1}, γ_{K-1} cũng chưa được định nghĩa. Câu "For the last step" trong (b) có cùng giả thiết ngầm.
- Vì sao quan trọng: đây là phát biểu chính thức. Lời khai LLM ở B:1103-1105 nói chứng minh này đã "verified".
- Sửa (e), trước "the output is on-atom": thêm `and $e(x_{K-1},\sigma_{K-1})\le\varrho_{K-1}n_{K-1}+\gamma_{K-1}$`. Sửa (b): `If also $e(x_{K-1},\sigma_{K-1})\le\varrho n_{K-1}+\gamma$, the last step gives ...`.
- Nguồn: proof_audit_2 §6. Người kiểm 1 không đọc B.

**P4. Trích Benton "Theorem 1" cho một ý mà định lý đó không nói.** A:1085 và A:1230.
- Sai gì: Theorem 1 của Benton là một cận trên: W2 ≤ ε·exp(∫L_t dt), với điều kiện trường học được là Lipschitz. Ý "loss nhỏ mà sai số điểm cuối vẫn lớn" nằm ở đoạn bàn về Assumption 3 trong Mục 3. Tôi đã mở PDF để xác nhận.
- Vì sao quan trọng: reviewer nào quen bài Benton sẽ thấy ngay.
- Sửa: `\citep[Section~3, discussion of Assumption~3]{benton2024error}`. Hoặc viết lại A:1084-1085 thành `small regression loss controls the endpoint only together with a Lipschitz bound on the learned field \citep[Theorem~1]{benton2024error}`. Câu ở B:347 chấp nhận được.
- Nguồn: cite_others §1.

**P5. Đoạn mô tả EXP-1 gần như chép nguyên văn giữa hai bài.** A:3225-3229 và B:1967-1971.
- Sai gì: hai câu giống nhau từng chữ (prior, quan sát, N = 200, MLP 4 lớp rộng 128, Adam). Hợp đồng chia bài (§2) cấm một đoạn xuất hiện ở cả hai bài.
- Vì sao quan trọng: công cụ dò trùng lặp sẽ bắt được. Về toán thì vô hại.
- Sửa (rút gọn bên A, giữ phần riêng của A từ "at $h\in\{0.01,\dots\}$" trở đi): `\paragraph{Linear-Gaussian problem.} We use the EXP-1 setting: $x\sim\N(0,I_2)$, one scalar observation $y=Ax+\eta$ with $\eta\sim\N(0,0.1^2)$, $N=200$ training pairs and Gaussian posterior covariance $\Sigmapost$; a 4-layer SiLU MLP of width 128 with a 64-dimensional time embedding, Adam ($10^{-3}$, batch 256, $2\times10^5$ steps).`
- Nguồn: a_vs_b §5.1.

## 3. Nên sửa

**Bài A**

| # | Dòng | Vấn đề | Sửa | Nguồn |
|---|---|---|---|---|
| A1 | A:1009-1010 | Phát biểu prop:twoatom không đòi nn(z) = {a,b}. Ở tâm hình vuông, z là trung điểm của cả hai đường chéo nhưng có 4 atom gần nhất, nên phép rút về một chiều hỏng. | `at the midpoint $z$ of two atoms $a,b$ with $\nn(z)=\{a,b\}$` | 2 người kiểm cùng thấy |
| A2 | A:1035 | "Conditions (a) and (b) are necessary, not sufficient" đảo logic: (a), (b) là điều kiện đủ để Pr = 0. | `Violating the hypotheses of (a) and (b) is necessary for a blend, not sufficient;` | 2 người kiểm cùng thấy |
| A3 | A:961-964 | "Almost every (p_1,...,p_K)" chưa cho phép giữ cố định prior vô điều kiện đều. Chứng minh thật ra chỉ cần một prior tự do. | `... so for fixed coefficients, any fixed $p_k$ ($k\ne k_0$) and almost every $p_{k_0}\in\Ppos$ with $c_{k_0}\ne0$, every profile is hyperbolic; in particular $p^{\mathrm{unc}}$ may stay uniform. Since $\mathcal C'$ is finite, this holds at every non-atom candidate at once.` | 2 người kiểm cùng thấy |
| A4 | A:964-966 | "exceptional" dễ bị đọc thành "hiếm theo w". | `exceptional in the priors (in Theorem~\ref{thm:composition} they occur only at $w=w_c$)` | 2 người kiểm cùng thấy |
| A5 | A:956-957 | η trùng với η = P_{L⊥}(x−z) ở A:2697; K chưa được định nghĩa. | Đổi thành λ_{k,a}; viết "K fields with fixed coefficients". | audit 2 |
| A6 | A:739-741, A:745 | "w as in Theorem schedule" kéo theo cả "h > 0, fix y". "unique trajectories" phải là Carathéodory. Với s(t) vượt qua 1 thì không được phủ. | `with $w:[0,1)\to[0,\bar w]$ measurable and of bounded variation on $[t_0,1)$`; `unique Carath\'eodory trajectories`; `with a constant $s$` | audit 1 + 2 |
| A7 | A:1971-1975 | Công thức Liouville được dùng cho trường chỉ đo được theo thời gian (khi w có bước nhảy). Hale Ch. I xét trường liên tục. | Trích một tài liệu về ODE Carathéodory. Người kiểm không đưa số định lý; đừng đoán. | audit 1 |
| A8 | A:255-256, A:349-350, A:202-204, A:496 | Còn FLAG, thiếu số định lý. Wan Thm 5.3 có cùng số ở PMLR v267 và arXiv v4, và phủ mọi luật rời rạc với trọng số dương. Baptista: Def. 6.2 và Thm 6.4 (v2). | `\citep[cf.][Theorem~5.3]{wan2025elucidating}`; `\citet[Definition~6.2 and Theorem~6.4]{baptista2025memorization}`; xoá FLAG | cite_wan_baptista |
| A9 | A:1869-1874 (bảng so sánh) | Cột liu2025pde/Wan: "endpoint law is the data law" và "positive reach" không đến từ liu2025pde Thm 3.7. Chính bài đó viết rằng định lý "does not assert that their sampling weights are recovered". | Ghi rõ nguồn: "compact [Thm 3.7]; positive reach with a local mass bound [Wan, Thm 5.3]". Endpoint law thuộc về Wan. | cite_others |
| A10 | A:115 | Lỗi ngữ pháp "So do every fixed combination". | `So does every fixed combination` | readability |

**Bài B**

| # | Dòng | Vấn đề | Sửa | Nguồn |
|---|---|---|---|---|
| B1 | B:494-495, B:1477-1479 | prop:trap chỉ xét trọng số đều, nhưng B:494-495 dùng nó cho mọi posterior của thm:relerr, kể cả prior label-noise. Phần EDM (đều trong lớp) vẫn đúng. | Nhân Ω với `\max_{k\ne i}p_k/p_i`, hoặc viết `for uniform or within-class weights` | audit 2 |
| B2 | B:496-497 | "(c) is the converse" quá mạnh. Giữa (b) và (c) có vùng vẫn hạ cánh: thử số với 1−ϱ = 0.6/(1+τ) cho n → 0 như τ^-0.6. | `keeps it below one where $n_t$ is large compared with $\gamma_t+\omega_t$, and (c) gives a partial converse.` | audit 2 + numeric |
| B3 | B:1495-1497 | Với N = 1, q chia cho 0. | thêm `for $N\ge2$` | audit 2 |
| B4 | B:95, B:1070; B:167, B:1066 | "explains landing" mâu thuẫn với B:864-867 ("not an independent test"). Với ϱ ≈ 0.997 (B:809), không mốc dừng hữu hạn nào tách được "hạ cánh rất chậm" khỏi "dừng trước". "never copies" dựa trên 200-500 mẫu. | `describes how landing happens and is consistent with Theorem~\ref{thm:relerr}`; `none of whose samples copied a training image in our runs` | readability + numeric |
| B5 | B:400-401, B:442-445, B:251-253 | FLAG giống A8. "equilibria of a distance potential" quá lỏng khi có guidance. | Thêm Thm 6.4 / Thm 5.3 rồi xoá FLAG; dùng `finitely many nearest-support equilibria` như A. | cite_* |
| B6 | B:561, B:1247-1248, B:1439, B:1504 | Ký hiệu bị trùng: D (khoảng cách / denoiser), m_p và q_{p,j} (ký hiệu của A), e (vectơ / sai số), h (bandwidth / γ+Ω). | g; m^⋆ và w_j^{(h)}; Y; η | a_vs_b |
| B7 | B:1232 | Trỏ tới "proof of prop:collapse(c)", nhưng B không chứng minh prop:collapse (B:1128-1130). | `as in Proposition~\ref{prop:collapse}(c) with $a+c$ in place of $x^i$` | a_vs_b |
| B8 | B:254 | Gọi A là bài về thay đổi "sampler-side" là hẹp: A còn xét label noise lúc train và label averaging. | `studies which changes of an exact conditional field, from label noise and label averaging to guidance and composition, keep its endpoints on the training set` | a_vs_b |

**Giữa hai bài**

| # | Dòng | Vấn đề | Sửa | Nguồn |
|---|---|---|---|---|
| X1 | A:463 và B:402 | Cùng là prop:collapse, nhưng B ghi "cf. Baptista" còn A trình bày như kết quả của mình. | Thêm `cf.\ \citealp[Theorem~6.4]{baptista2025memorization}` vào tiêu đề ở A | a_vs_b |
| X2 | A:1097-1101 và B:473-491 | prop:regular(b) của A (một chiều; độ dốc < 1 thì hút) là trường hợp riêng của thm:relerr của B, nhưng B không nhắc tới. | Thêm một câu ở B. Đó sẽ là lần trích companionA thứ ba (nhóm đã quyết là hai lần), nên nhóm quyết. | a_vs_b |
| X3 | A:368-369 / B:246-248; A:3219-3220 / B:1960-1962; A:1464-1466 / B:1148-1150 | Các câu gần trùng nguyên văn. | Viết lại bên B | a_vs_b |

## 4. Dòng Khoi phải tự đọc kỹ (theo thứ tự quan trọng)

| # | Dòng | Vì sao | Thời gian |
|---|---|---|---|
| 1 | A:2318-2341 | Đẳng thức Θ trong chứng minh thm:schedule. Đây là chỗ duy nhất dùng w ≥ 0, và là lý do mọi tổ hợp hai trường an toàn. | 10 phút |
| 2 | A:2264-2284 | Tích phân từng phần theo lịch w có biến phân bị chặn (lem:signedconv). Cần kiểm bước sửa w thành liên tục phải, và cận năng lượng không phụ thuộc τ'. | 10 phút |
| 3 | A:3030-3061 | Chứng minh prop:twoatom (a), (b), (c). Ngắn, nhưng toàn bộ quy tắc dấu dựa vào nó. | 15 phút |
| 4 | A:2925-2960 | thm:spectral(c): quỹ đạo không thoát ra vô cùng và profile hội tụ. Kết luận "Pr = 0" của prop:twoatom dựa vào đây. | 20 phút |
| 5 | A:947-967 | rem:generic: một chứng minh nằm trong remark và không có bản ở appendix. | 15 phút |
| 6 | B:1438-1471 | Chứng minh thm:relerr (a)-(d). | 15 phút |
| 7 | B:1501-1513, B:1566-1592 | prop:trap và prop:heun, nhất là phần (e) (xem P3). | 20 phút |
| 8 | A:1971-1980 | Phác thảo công thức Liouville cho trường Carathéodory (xem A7). | 5 phút |
| 9 | A:733-747, A:940-944, A:994-1044, A:1348-1354, B:493-497 | Các câu diễn giải định lý (P1, P2, A1-A4, B2). Nên đọc sau khi đã sửa. | 20 phút |
| 10 | A:1407-1416, B:1098-1106 | Lời khai LLM. Chỉ giữ "checked by the authors" khi đã xong các dòng 1-7. | 5 phút |

Tổng cộng khoảng 2 giờ 15 phút.

## 5. Chỗ các tác nhân bất đồng hoặc chưa kết luận được

1. **Tên gọi "less decided".** Người kiểm 1 chỉ ra rằng (a) chỉ đòi trường bị trừ có log-odds *nằm giữa* các trường cực trị, chứ không đòi nó "ít quyết đoán hơn". Phản ví dụ: B = 3, 2, 1 với hệ số (1+w)/2, −w, (1+w)/2. Trường bị trừ (B = 2) quyết đoán hơn trường B = 1, nhưng vẫn có profile hút (F'(−2) = −0.42). Người kiểm 2, bài thử số và bài đọc văn phong vẫn dùng tên này. Abstract (A:124-125) và contributions (A:232-234) đã định nghĩa đúng ("strictly between"). Tiêu đề A:1007 và các dòng A:281, 311, 1023, 1051, 1379 thì dùng tên trần, không định nghĩa. Đề xuất: giữ tên nhưng thêm định nghĩa ở A:1023, hoặc đổi thành "intermediate". Ngoài ra, tôi tự nhận thấy một điểm (chưa ai khác kiểm): với 4 trường trở lên, cụm "between those of the added fields" mạnh hơn điều (a) chứng minh, vì (a) lấy min/max trên *mọi* trường. Tôi tìm ngẫu nhiên 5889 trường hợp mà không thấy phản ví dụ, nhưng điều này chưa được chứng minh. Cách an toàn là viết giống (a).
2. **Liu-Zuazua v1, Remark 3.19 (A:1837-1838): chưa kiểm**, vì không có PDF v1. Có hai cách: đối chiếu với arXiv 2605.12231v1, hoặc bỏ "(its Remark 3.19)".
3. **Số 0.276 ở B:2002: tôi đã kiểm, đúng.** Tôi lấy `trace_cov_mean` (nhóm train) ở iter 2×10^5 trong `results/exp1/exp1_cond_seed{0-4}/raw/metrics.csv`, trừ đi giá trị ở iter 10^6 trong `exp1_ext_sched_seed{0-4}`. Hiệu theo seed là 0.292, 0.379, 0.263, 0.320, 0.127. Trung bình là 0.2761, khoảng t 95% là [0.1597, 0.3925], khớp với "0.276 [0.160, 0.393]". Tỉ số 0.389 [0.217, 0.560] cũng khớp. Số này không phải số s10, chỉ trùng giá trị. Nếu muốn tránh bị script grep báo nhầm, có thể thêm một dòng comment trong source.
4. **Bản xuất bản của Baptista.** FLAG ở A:349 đòi "published version". refs.bib trỏ arXiv v2, và các số Def. 6.2, Thm 6.4, Ex. 4.4 đã kiểm trên v2. Không tác nhân nào tìm được bản tạp chí. Trích theo v2 là đủ.
5. **Quy tắc dừng gần w_c.** Bài thử số thấy rằng nếu dừng ở một cửa sổ thời gian nhanh cố định σ (khoảng 10^4), sẽ xuất hiện blend giả ngay dưới w_c khi B lớn (B = 3: 3.4e-4 ở 0.99 w_c), vì ở đó điểm tie (điểm cách đều hai ảnh) đẩy quỹ đạo ra rất chậm. Cần σ ≥ 10^5. `scripts/theory_basin_map.py` (dùng cho fig:unrolled) dừng ở U_END = 1e4 (dòng 93). Tuy vậy, các số đã in vẫn đứng vững: tam giác ở B = 2, ở 1.1 w_c, ra 0.0009 bằng code độc lập, so với 0.0010 trong tab:spectral (A:3421). Các ô 0.9 w_c đều bằng 0. Phụ lục CIFAR (A:3594-3596) phân loại bằng nghiệm của F_w, nên không bị ảnh hưởng. Rủi ro chỉ xuất hiện nếu sau này thêm ô gần w_c với B ≥ 3. Chưa ai kiểm các script khác.
6. **Hình minh hoạ thm:relerr trong B.** Ví dụ x̂ = m* + ϱ(Z − m*) gần như đúng theo cách dựng. Một ví dụ sai số xoay 90 độ sẽ thuyết phục hơn. Đây chỉ là gợi ý.

## 6. Đã xác nhận đúng (không cần làm lại)

- **Trích dẫn:** Wan Thm 5.3 (tôi đã mở PDF; Thm 5.4 chỉ nói về tốc độ). Baptista Def. 6.2, Thm 6.4, Ex. 4.4 (v2). Mọi số Liu-Zuazua v2 mà A dùng đều có đúng nội dung (Thm 2.5, 2.5(ii), Rem 2.7, Prop 3.1, Rem 3.2, 3.6, Cor 3.7, Lemma 5.5, Sec. 7). liu2025pde Thm 3.7. Azangulov Thm 3 và Rem 4 (arXiv v2; AISTATS 2026, PMLR 300). Cao Thm 3.1. Li Thms 4-5. Pidstrigach Thm 2. Metadata bib của 9 khoá, kể cả tên NeurIPS của Pfrommer.
- **Số của A:** bảng tab:composition khớp 3 chữ số ở B = 1, 2, 3. Ngưỡng 1/sinh²B, luật gần ngưỡng, 1.368 w_c (tam giác) và 1.407 (simplex) đều khớp. fig:unrolled: 13% / 41% ở 2 w_c, cùng các mức 5 và 10 w_c. Các tổ hợp có dấu 0.742, 0.316, 0.406 khớp. cor:twofields: 85 504 điểm xuất phát, tất cả về atom.
- **Số của B:** thm:relerr khớp ở 14 biến thể (tốc độ (1−t)^{1−ϱ}, các trường hợp (c) và (d)). EXP-1: 0.276 và 0.389 (tôi kiểm).
- **Nhất quán A/B:** bốn kết quả dùng chung có cùng toán và cùng giả thiết. Các quyết định nhóm đã được áp dụng. Số s10 (0.168, 0.276) chỉ có ở A.
- **Chứng minh:** hai tác nhân đã đọc từng bước và thử phản ví dụ, không thấy lỗi. Việc này không thay được phần đọc của Khoi ở phần 4, vì lời khai LLM nói tác giả đã kiểm.

## 7. Việc của nhóm, không phải của Khoi

- **Xoá comment LaTeX trước khi đăng arXiv** (arXiv công khai source). A có comment nhắc tới bài B, các quyết định nội bộ, "Draft by the assistant" và TODO: A:4-5, A:101-103, A:255, A:349, A:1154-1155, A:1408-1410. Có thể dùng `arxiv_latex_cleaner`. B cũng có comment tương tự (B:16-22, B:400, B:442, B:1099, B:1647).
- **Lời khai LLM.** Sửa A:1413-1415 và B:1103-1105 sao cho khớp với việc đã thực sự làm. Xoá TODO ở A:1409-1410 sau khi Khoi đọc xong. Ở B, chỉ giữ chữ "verified" sau khi đã sửa P3.
- **Công khai với TMLR:** trong form nộp A, báo cho action editor biết bài B đang được review và gửi kèm bản B đã ẩn danh.
- **Mục bib companionA** (`paper_mechanism/refs.bib`:579-584) vẫn ghi "Anonymous / Companion submission". Khi A đã lên arXiv, cần ghi tác giả thật, số arXiv và `note = {arXiv preprint}`, rồi sửa comment B:16-22.
- **Số headline của B** (88%, 96%, 0.51, 2.48, 1.33, 89.6%, 95.6%) chưa được đối chiếu với `results/` trong vòng này. Cần chạy `scripts/paperB_verify_*.py`.
- Các sửa nhỏ không có trong bảng: thống nhất "label noise" thay cho "label smoothing" ở tiêu đề A:496, và tiêu chí off-atom (A:3251-3252: off-atom khi d1 > d2/3; B:676-677: off-atom khi d1 ≥ d2/3; chỉ khác ở trường hợp bằng nhau).

## 8. Cập nhật sau khi sửa (2026-11-23)

Đã sửa trên nhánh `paper-split-drafts`, cần Khoi kiểm lại cách sửa:

- **P1-P5** (commit 8e60c36): đã sửa đúng như mục 2. Riêng P3 có thêm giả thiết vào phát biểu `prop:heun` (b) và (e).
- **A1-A6, A8-A10, X1:** đã sửa theo mục 3. Tên "less decided" đổi thành "intermediate" ở mọi chỗ, kèm định nghĩa chính xác như phần (a) và ví dụ B = 3, 2, 1 (đã kiểm bằng số: F'(-2) = -0.084, -0.42, -1.68 ở w = 1.2, 2, 5 lần 1/sinh^2(1)). Ký hiệu eta trong rem:generic đổi thành lambda.
- **A7:** chưa sửa, chỉ thêm `% FLAG` vì cần một tài liệu về công thức Liouville cho trường Carathéodory; không đoán số trang/định lý.
- **B1-B5, B7, B8:** đã sửa theo mục 3. B6: D -> `\ell` trong prop:localtransfer (vì `g` đã dùng trong chứng minh đó), m_p và q_{p,j} -> m^\star và w_j^{(h)}, h -> eta trong chứng minh prop:trap. **Chưa đổi** e (vectơ Z - a) với e_t (sai số) trong thm:relerr, vì chính phát biểu dùng \hat e_t; cần Khoi quyết cách đặt tên.
- **X2:** chưa làm, cần nhóm quyết (lần trích companionA thứ ba).
- **X3 và các câu trùng khác:** đã viết lại bên B (Wan/Baptista, Liu, cách ghi ±, đoạn tổ chức phụ lục, câu reproducibility). Phần còn trùng giữa hai bài giờ chỉ là preamble LaTeX, as:standing, phương trình và bảng ký hiệu.
- **Văn phong:** abstract A mở đầu bằng chuyện mô hình copy ảnh train; abstract B định nghĩa radial ratio bằng một câu ngắn; phần mở đầu B thêm hình ảnh "chọn sân bay rồi mới hạ cánh"; B bỏ hai chỗ nói quá ("explains landing", "never copies").
