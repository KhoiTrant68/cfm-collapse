# Simulated ICLR/ICML/NeurIPS review — 2026-11-20

Bài: *Atomic Endpoints of Averaged and Guided Empirical Conditional Flows* (`paper/main.tex`, bản ICLR qua `paper/main_iclr.tex`).

Hội đồng gồm 5 ghế chạy độc lập, không ghế nào thấy báo cáo của ghế khác: AC/Journal-fit, R1 (chứng minh), R2 (diffusion/EDM), R3 (privacy/thống kê) và Devil's Advocate. Cả 5 ghế dùng cùng một họ model (không có cross-model). Vì vậy các điểm trùng nhau giữa các ghế có thể do lỗi tương quan, không nên coi là xác nhận độc lập. Quy trình rút gọn so với giao thức sprint-contract của skill: mỗi ghế đọc paper một lần rồi viết báo cáo, không có pha cam kết tiêu chí trước khi đọc paper.

Các điểm đánh dấu **[đã kiểm]** là những gì người tổng hợp tự đối chiếu lại với source hoặc `results/`.

---

## 1. Điểm số

| Ghế | Soundness | Presentation | Contribution | Rating | Confidence |
|---|---|---|---|---|---|
| AC / Journal-fit | 3 | 2 | 2 | **5** | 4 |
| R1 – chứng minh | 3 | 2 | 2 | **6** | 4 |
| R2 – diffusion/EDM | 2 | 2 | 2 | **5** | 4 |
| R3 – privacy/thống kê | 3 | 2 | 3 | **6** | 3 |
| Devil's Advocate | 3 | 2 | 2 | (5) | 4 |

Trung bình 4 ghế thường là **5.5**. Ở ICLR, mức này là borderline, thường nghiêng về reject.

## 2. Quyết định tổng hợp (meta-review)

**Khuyến nghị: Major revision.** Với ICLR 2027 ở trạng thái hiện tại, kết quả dự kiến là borderline reject.

Cả 5 ghế đồng ý về ba điểm:

- **Toán đúng.** R1 kiểm tra từng dòng khoảng 20 chứng minh và không tìm thấy lỗi nào sai thực sự. Các phần khó được xử lý cẩn thận: Θ chỉ dương theo trung bình, năng lượng với hệ số có dấu BV, và trường hợp không hyperbolic w=w_c.
- **Bài trung thực về giới hạn.** Ghế nào cũng ghi nhận điểm này.
- **Bài thiếu trọng tâm cho một hội nghị 9 trang.**

Kết quả mới nhất về toán (composition/spectral) thì chính tác giả gọi là "boundary marker", không phải cơ chế thực tế. Kết quả gần thực tế nhất (transfer, relerr, Heun) thì sơ cấp, và bằng chứng EDM cho nó có thành phần gần tautology ở σ nhỏ. Ba trong bốn ghế (AC, R2, DA) cho rằng bản TMLR hợp hơn, nếu không tái cấu trúc quanh một luận điểm.

### Đồng thuận (≥3 ghế, đã kiểm)

1. **Abstract sai số liệu (AC, R2, R3, DA).** Dòng 116–117 viết "models that memorise 4 and 50%". Model 500 ảnh thực ra có 4.1% off-atom, tức memorise khoảng 96% **[đã kiểm, dòng 1248]**.
2. **Disclosure LLM mâu thuẫn với comment trong source (cả 5 ghế).** Dòng 1445 viết "The authors wrote and verified all proofs". Comment ở dòng 899–900, 1440–1442 và 3373 ghi rằng bản nháp chứng minh của Thm relerr, Prop trap và Prop heun đến từ model **[đã kiểm]**. AC xếp mức Critical vì rủi ro integrity nếu source lộ ra (arXiv hoặc supplementary).
3. **Claim thực tiễn (i) "the knobs are not privacy mitigations" bị chính dữ liệu của bài phản bác (DA CRITICAL; AC, R2, R3 Major).** Trên U-Net CIFAR đã train, off-atom tăng theo h: 0.173/0.246/0.298 (Euler) và 0.158/0.212/0.254 (RK4) tại h=4,5,6, còn h=0 là 0 **[đã kiểm, dòng 3317–3320]**. Somepalli et al. 2023b có trong `refs.bib` nhưng không được cite **[đã kiểm]**.
4. **Phần tách on/off-atom trên EDM gần tautological ở σ nhỏ (AC, R2, R3, DA; R1 nêu khía cạnh logic).**
   - n_t neo vào ảnh gần nhất của endpoint, nhãn off-atom cũng định nghĩa bằng endpoint, và x_K = D_{K−1}.
   - Model 500 ảnh bị ceiling: mọi đặc trưng, kể cả baseline, đạt AUC ≈ 1.
   - Model 2000 ảnh (1 seed) là model duy nhất cho thông tin, và ở đó late contraction hòa baseline (0.983 so với 0.985).
5. **"Heun bound never violated" là sanity check, không phải kiểm định (R1, R2, DA).** Với ϱ đo trên chính quỹ đạo, bất đẳng thức đúng theo định nghĩa (bất đẳng thức tam giác). Dự đoán theo số bước là phép tính đại số trên r_k ≥ 1/2 và outcome không đổi. Nên đổi "predicts" thành "certifies".
6. **Narrative phân tán và abstract quá dài (cả 5).** Abstract khoảng 400 từ, có khoảng 20 statement. Bản ICLR đẩy spectral criterion và nhiều kết quả ra appendix, nhưng intro vẫn liệt kê chúng là contribution.
7. **Thiếu trích dẫn trực tiếp.** `biroli2024dynamical` (speciation/collapse time, chính là "two clocks") và `somepalli2023copying` có trong bib nhưng không cite **[đã kiểm]**. Cũng thiếu Wen et al. ICLR 2024, Raya & Ambrogioni 2023, Bonnaire et al. 2025, Aithal et al. 2024 (mode interpolation, gần với circumcentre).
8. **Submission hygiene.** Còn `% TODO` ở dòng 2846 về trích dẫn C¹ cho Lemma lp **[đã kiểm]**, `% DRAFT`, `% CHECK`, đường dẫn `docs/plan/...` và placeholder `\openreview` XXXX. AC lưu ý rủi ro dual submission: README ghi "TMLR submission", và còn có bản workshop.

### Bất đồng và cách phân xử

| Vấn đề | Ý kiến | Phân xử |
|---|---|---|
| Prop heun là "falsifiable prediction" | AC, R3 coi là điểm mạnh. R1, R2, DA coi là tautology hoặc dự đoán về độ lỏng của bound. | Theo phía phê bình. R1 đã kiểm chứng minh và xác nhận phần (b) đúng cho mọi D khi ϱ được đo a posteriori. Chỉ "outcome không đổi theo số bước" là nội dung thực nghiệm. |
| Contribution 2 hay 3 | R3 chấm 3 (framing "which vs whether" có ích cho privacy). Các ghế khác chấm 2. | Giữ 2 cho ICLR. Framing có giá trị, nhưng phần mới về kỹ thuật hẹp: Lemma signedconv, composition, spectral. |
| Soundness 2 hay 3 | R2 chấm 2 (thiết kế thí nghiệm). R1 chấm 3 (chứng minh đúng). | Toán là 3. Phần EDM có các vấn đề W1–W3 của R2. Gộp lại khoảng 2.5. |
| Swap net→exact là bằng chứng | AC, R3, DA khen. R2 cho rằng nửa đầu suy trực tiếp từ lý thuyết. | Cả hai đều đúng một phần. Kết quả "0%→100%" là hệ quả của Thm posmix. Phần có thông tin là ảnh nào được chọn. R2 chỉ ra chiều exact→net có trong `results/n3_followup_20261111/SWAP_SUMMARY.md` mà không có trong bài **[đã kiểm: file tồn tại với cột exact->net]**. |

### Devil's Advocate CRITICAL: phân xử

- **Claim (i) mâu thuẫn dữ liệu:** **VALIDATED.** AC, R2 và R3 xác nhận độc lập, và số liệu đã kiểm. Đây là điểm chặn: phải sửa trước khi nộp.
- Các mục MAJOR còn lại của DA (novelty, composition, tautology, Heun, augmentation confound) đều có ít nhất một ghế khác xác nhận. Confound augmentation đã kiểm: subset models "without augmentation" ở dòng 1241 và 3553.

### Điểm mạnh được công nhận

- Template hai bước (Lemma conv và Lemma volume, Liouville + Fatou) sạch và dùng lại được. Thm schedule xử lý đúng việc |μ_w|² chỉ nhỏ trong L².
- Lemma signedconv giải quyết được trường hợp mà Remark 3.19 của Liu et al. để ngỏ.
- Thm composition cho ngưỡng chính xác 1/sinh²B, kể cả trường hợp không hyperbolic. Phần số khớp đến 0.01%.
- Thm spectral (c) có lập luận "không thoát ra vô cực" đẹp.
- Tự phê bình hiếm thấy. Bài báo cáo cả failure và kết quả âm.
- Reproducibility tốt. R2 đã đối chiếu nhiều con số với `results/` và thấy khớp.

---

## 3. Lộ trình sửa (ưu tiên)

### Mức 0: bắt buộc, rẻ (làm trước mọi thứ)
1. Sửa abstract: "memorise 96% and 50%", hoặc "with 4% and 50% off-atom samples". Rà lại mọi con số trong abstract so với các bảng.
2. Viết lại đoạn "Use of large language models" cho khớp quy trình thật, ở cả hai bản. Đây là quyết định của tác giả, nhưng câu hiện tại mâu thuẫn với ghi chú của chính tác giả.
3. Xoá mọi comment nội bộ trước khi nộp hoặc lên arXiv (ví dụ dùng `arxiv_latex_cleaner`). Kiểm tra trạng thái nộp TMLR và workshop.
4. Scope lại claim (i) và (iii) cùng Ethics:
   - "Ở exact optimum không đổi support; ở trained model mọi tác dụng đến từ learned-field error và không có guarantee." Nêu luôn số liệu off-atom tăng theo h.
   - (iii) thành "explains landing; for detection use NN distance".
   - Thêm một đoạn threat model ngắn (R3 W3).
5. Đổi "predicts" thành "certifies" cho Heun. Đổi "non-landing regime of Thm relerr(c)" thành "consistent with failure of the hypothesis of (b)" (R1 W2).
6. Cite `somepalli2023copying`, `biroli2024dynamical`, `graf2000quantization`, và thảo luận quan hệ "two clocks" với speciation/collapse time.
7. Compile bản ICLR và đếm số trang main text. Bỏ khỏi danh sách contribution trong intro những kết quả không nằm trong main text.

### Mức 1: phân tích lại trên dữ liệu có sẵn
8. Đo giá trị gia tăng của late contraction C so với d̂ (D_θ → NN): hồi quy logistic, ΔAUC, LRT trên model 2000 ảnh (R2 W1).
9. Dùng predictive anchor ở mọi σ. Tính lại C chỉ trên σ ≥ ~0.06 (R3 W5).
10. Đưa kết quả swap exact→net vào main text (R2 W3). Nó cho thấy trực tiếp và mạnh hơn rằng landing được quyết định muộn: off-atom 95.6% khi giao ở s=1 nhưng 0.2% ở s=0.1.
11. Báo cáo median của radial ratio theo σ (R1 W2).
12. Thêm positive control cho stress test: composite w=2w_c phải cho lại P₀≈0.406 (R1 W4).
13. Thay population std bằng mean ± 95% CI. Tách CI Monte Carlo khỏi biến thiên giữa các seed. Dùng s.e. cluster-robust cho slope (R3 W6).
14. Lemma lp: thay claim C¹ bằng Lipschitz (đủ cho Thm spectral(b)) và thêm trích dẫn, ví dụ Coppel 1978 hoặc Barreira–Valls (R1 W1).

### Mức 2: thí nghiệm mới (nếu muốn nhắm ICLR)
15. Train EDM sub500/sub2000 với class dropout. Quét CFG w, guidance interval và delayed guidance, rồi đo off-atom và ϱ_t (R2 W5). Đây là thí nghiệm mà title đòi hỏi.
16. Lưới N × seed, tách subset seed khỏi training seed, thêm một model có augmentation (R2 W6, DA).
17. Kiểm tra claim (ii) trên các top-half held-out: so tần suất trả về với p_i^(h)(y) (R2 W7).
18. Một Heun schedule thô (r_k < 3−2√2) trong đó lý thuyết dự đoán outcome thay đổi, rồi đo precision/recall (R2 W2).
19. (Tuỳ chọn) MIA TPR@1% FPR theo h (R3 W4).

### Quyết định chiến lược
Chọn một trục:
- **(A)** Bài lý thuyết về guidance và mixture dynamics. Đưa spectral criterion và phần so sánh Liu et al. vào main text, rút gọn EDM, nộp **TMLR**. Theo AC thì bản hiện tại đã gần sẵn sàng.
- **(B)** Bài "selection early, landing late". Làm các mục 8–10 và 15–16, giữ atomicity làm nền, chuyển composition xuống appendix, nộp **ICLR**.

---

## Phụ lục: 5 báo cáo gốc

Năm báo cáo đầy đủ được nối ở dưới, theo thứ tự AC, R1, R2, R3, DA.


---

### Review — Area Chair / Journal-Fit seat

**Paper:** "Atomic Endpoints of Averaged and Guided Empirical Conditional Flows" (ICLR 2027, bản build `main_iclr.tex` từ `main.tex`)

Tôi đã đọc kỹ toàn bộ main text (dòng 1–1457) và đọc lướt các appendix liên quan đến claim chính (App. comparison với Liu & Zuazua, measured-transfer dòng 3294–3370, relerr/trap/Heun dòng 3372–3547, EDM experiments). Tôi không kiểm tra chi tiết từng chứng minh (đã có reviewer khác làm), nhưng có ghi lại những chỗ đáng ngờ mà tôi thấy.

---

## Summary

Bài báo nghiên cứu **population minimiser** của conditional flow matching trên một tập huấn luyện hữu hạn cố định (exact empirical field), rồi hỏi: các can thiệp phía sampler/learner có thể tự chúng đẩy endpoint ra khỏi tập huấn luyện hay không. Các can thiệp được xét là Gaussian label noise (bandwidth $h$), trung bình field theo label (label averaging), classifier-free guidance (hằng số, âm, hoặc schedule có biến phân bị chặn) và tổ hợp của chúng. Các kết quả chính:

1. **Exact reference (Sec. 3):** khi $h=0$, field sụp về một atom (Prop. 3.2). Khi $h>0$, endpoint law là phân phối Nadaraya–Watson $\sum_i p_i^{(h)}(y)\delta_{x^i}$ (Thm. 3.4), kèm một sàn $W_2$ (Prop. 3.6). Tác giả tự thừa nhận phần này là "a reference, not a new identity" (dòng 304–307).
2. **Interventions (Sec. 4):** positive field mixtures (Thm. 4.1), guidance với $w\ge0$ cố định (Prop. 4.3), negative guidance (Cor. 4.4) và bounded-variation schedules (Thm. 4.5) đều cho endpoint là training atom với hầu hết initial point, và mọi trajectory đều hội tụ. Chứng minh dùng chung một template hai bước: kinetic energy hữu hạn, rồi Liouville/divergence $\beta\Theta-d$.
3. **Composition (Sec. 4.3–4.4):** guidance áp lên field đã label-averaged có thể tạo một atom tại circumcentre (một blend của các training points) với xác suất dương. Với hai atom, ngưỡng là đúng $w>1/\sinh^2B$ (Thm. 4.6), ổn định dưới nhiễu (Prop. 4.7), và có một spectral criterion tổng quát (Thm. 4.8, trong bản ICLR nằm ở appendix). Tác giả nói rõ đây là "boundary marker, not a practical mechanism".
4. **Transfer (Sec. 5):** một bound pathwise sơ cấp: endpoint của learned field nằm trong $\limsup(1-t)|\Delta|$ (Thm. 5.1), cùng một điều kiện landing theo relative error $\varrho<1$ (Thm. 5.2) và một phiên bản rời rạc cho Heun (Prop. heun, appendix).
5. **Experiments (Sec. 6):** finite-cutoff collapse trên MLP 2D và DDPM U-Net CIFAR-10 inpainting; kiểm tra số học của ngưỡng composition; learned composition chỉ tái tạo được basin khi network được cho thêm input $\operatorname{asinh}(tx/(1-t)^2)$ tại đúng điểm tie đã biết; và trên EDM CIFAR-10 class-conditional (subset 500/2000 ảnh cùng public model), relative error/late contraction tách sample on-atom và off-atom, nhưng không tốt hơn baseline khoảng cách tới nearest training image.

---

## Strengths

1. **Template chứng minh thống nhất, có kỹ thuật thật sự.** Đoạn "Proof strategy" (dòng 509–519) quy mọi kết quả atomicity về hai bước (finite kinetic energy ⇒ hội tụ về candidate set $\mathcal C/\mathcal C'$; divergence $\beta\Theta-d$ ⇒ basin null). Thm. 4.5 (schedule BV) và Prop. 4.3(a) bỏ được giả thiết "limit set contains no non-minimising critical point" của Liu & Zuazua (dòng 313–325, App. `apx:comparison`). Nếu đúng, đây là đóng góp kỹ thuật cụ thể và có thể kiểm chứng, vượt qua kết quả đã biết về guidance.
2. **Phản ví dụ composition sắc nét và được trình bày trung thực.** Thm. 4.6 cho ngưỡng dạng đóng $w_c=1/\sinh^2B$ với cơ chế dễ hiểu: slope $F_w'(0)=(1+w)\operatorname{sech}^2B-w$ (dòng 698–721). Prop. 4.7 cho thấy hiện tượng không phụ thuộc vào tính đối xứng, và Thm. 4.8/Cor. 4.9 nâng lên thành tiêu chí ma trận. Phần số học (Fig. composition, Table composition, kiểm tra trên các cặp ảnh CIFAR, dòng 1117–1137) khớp với lý thuyết đến $0.01\%$ gần ngưỡng.
3. **Tự phê bình hiếm thấy.** Bài nói rõ các giới hạn của chính mình. Composition là "boundary marker" (dòng 186–189, 1394–1397). Transfer bound "is not a separate test of the endpoint" vì là một đồng nhất thức (dòng 892–897, 3310–3311). Field error "no better than the distance to the nearest training image" (dòng 1319–1328, và ngay trong abstract). Hai lần refine solver được báo cáo là "do not establish convergence" (dòng 3323). Các near-tie integrations thất bại cũng được báo cáo (dòng 1111–1115). Đây là chuẩn mực tốt.
4. **Thí nghiệm "two clocks" trên EDM có thông tin.** Chạy network tới $\sigma=s$ rồi chuyển sang exact field (dòng 1253–1262): image được chọn khi $\sigma\approx1$ (99.6% trùng khớp trên subset model, 90% trên public model ở $s=1$). Riêng việc thay field trên 2% thời gian cuối đã biến public model từ 0% thành 100% memorisation. Đây là một cách tách *selection* khỏi *landing* gọn và dễ tái lập.
5. **Prop. heun cho một dự đoán định lượng về số bước sampler, và dự đoán này được kiểm tra.** Theo Prop. heun, với $r_k<1/2$ thì $\varrho_{\rm crit}<1$. Bài dự đoán rằng tăng lên 36/64 bước sẽ làm certificate thoả mãn ở mọi bước mà không đổi outcome, và điều này được xác nhận (dòng 1330–1345, Table edm-steps). Đây là một liên kết lý thuyết–thực nghiệm sạch, dù tầm ảnh hưởng hẹp.
6. **Reproducibility.** Có script cụ thể cho từng con số (dòng 1407–1421), có `verify_paper_numbers.py`, và các con số trong comment được trỏ tới thư mục `results/` (dòng 1233–1235).

---

## Weaknesses

### W1 — [Critical] Câu khai báo việc dùng LLM mâu thuẫn với chính các comment trong source; nguy cơ vi phạm policy

- **Ở đâu.** Dòng 1443–1447 (chỉ có trong bản ICLR) viết: *"The authors wrote and verified all proofs; the model-based checks supplemented this verification…"*. Trong khi đó, comment ở dòng 899–900 và 3373–3374 ghi "Theorem thm:relerr and Propositions prop:trap, prop:heun: drafted with model assistance", còn dòng 1440–1442 ghi "the first drafts of the proofs of thm:relerr, prop:trap and prop:heun came from model-based solver runs before the authors verified them; decide whether this paragraph should say so".
- **Vì sao quan trọng.** Thm. 5.2 và Prop. heun là xương sống của phần EDM và của hai câu trong abstract. Policy LLM của ICLR (từ 2026) yêu cầu disclosure trung thực. Một câu khẳng định "the authors wrote … all proofs" trái với hồ sơ nội bộ là rủi ro integrity, không chỉ là chuyện văn phong. Nếu source được nộp lên arXiv hoặc kèm supplementary, các comment này sẽ lộ ra.
- **Cách sửa.** Viết lại đoạn disclosure cho đúng sự thật, ví dụ: "the first drafts of the proofs of Theorem 5.2, Proposition E.1 and E.2 were generated with LLM assistance; the authors checked and rewrote them". Thêm câu tương tự vào bản TMLR. Xoá mọi comment nội bộ trước khi nộp.

### W2 — [Major] Lỗi sự thật trong abstract: đảo ngược tỷ lệ memorisation

- **Ở đâu.** Abstract dòng 116–117 viết "models that memorise $4$ and $50\%$ of their samples". Nhưng Sec. 6.4 dòng 1247–1250 lại viết "41 of 1000 samples (4.1%) are off-atom", tức model 500 ảnh memorise khoảng **96%**, còn model 2000 ảnh có 50.1% off-atom.
- **Vì sao quan trọng.** Đây là câu định lượng duy nhất của abstract về phần EDM, và nó sai theo hướng làm người đọc hiểu nhầm regime đang được thử nghiệm.
- **Cách sửa.** Viết lại thành "models with 4% and 50% off-atom samples" (hoặc "that memorise 96% and 50%"). Tiện thể rà lại toàn bộ abstract so với các bảng số.

### W3 — [Major] Novelty/significance so với hiểu biết sẵn có rằng empirical minimiser memorises

- **Ở đâu.** Sec. 3 (dòng 386–481) gần như hoàn toàn là kiến thức đã biết; tác giả tự thừa nhận ở dòng 293–307 (Gu et al., Biroli & Mézard, Bertrand et al., Baptista et al. Thm. 6.4, physicscfm2026, Smola 2026 "Support-conditioned FM is kernel smoothing"). Phần mới thực sự là: (a) atomicity hầu-chắc-chắn cho positive mixtures, guidance và schedule (Sec. 4.1–4.2); (b) phản ví dụ composition cùng spectral criterion (Sec. 4.3–4.4); (c) relative-error landing (Thm. 5.2). Mức độ mới của từng phần như sau:
  - (a) Kết quả "guidance của exact empirical field vẫn kết thúc trên atom" là điều cộng đồng đã kỳ vọng. Đóng góp nằm ở việc bỏ một giả thiết kỹ thuật của Liu & Zuazua (2026), một cải tiến dành cho người làm dynamical systems hơn là cho khán giả ICLR rộng.
  - (b) Đây là phần mới nhất về mặt toán, nhưng chính tác giả tuyên bố nó không phải cơ chế thực tế. Không có model nào được huấn luyện mà lại average field theo label (dòng 124–126). Basin nằm ở thang $(1-t)^2$, và chỉ network được "mớm" toạ độ blow-up tại điểm tie *đã biết* mới tái tạo được nó (dòng 1146–1156).
  - (c) Thm. 5.1 được tác giả gọi là "elementary; its use is the reading" (dòng 888). Thm. 5.2 là một bất đẳng thức Grönwall trên chuẩn bán kính (chứng minh dòng 3392–3422 dài khoảng 30 dòng). Cả hai đều đúng, nhưng chiều sâu kỹ thuật không cao.
- **Vì sao quan trọng.** Kết quả mới nhất thì bị chính tác giả tuyên bố là không áp dụng cho thực tế, còn kết quả liên quan tới thực tế thì sơ cấp. Với một top venue, AC sẽ hỏi: người làm diffusion/FM thay đổi điều gì sau khi đọc bài này?
- **Cách sửa.** Chọn một luận điểm trung tâm. Hoặc (i) định vị bài là một bài lý thuyết dynamical systems về guidance/mixtures (Sec. 4 cùng spectral criterion), với phần so sánh Liu & Zuazua đưa vào main text; hoặc (ii) định vị là "selection-early/landing-late" cho sampler thực, khi đó Sec. 6.4 cần mạnh hơn, chẳng hạn một can thiệp dựa trên late contraction có làm giảm memorisation hay không. Hiện tại bài cố làm cả hai.

### W4 — [Major] Narrative phân tán; tiêu đề không phản ánh nội dung

- **Ở đâu.** Abstract (dòng 101–130, khoảng 400 từ kể cả markup) liệt kê lần lượt: label noise → mixtures → guidance → schedule → transfer → relative error → EDM two clocks → Heun → detector comparison → composition → spectral → learned composition → CIFAR pair check → MLP/U-Net finite cutoff. Main text (bản TMLR) có 20 restatable/corollary, khoảng 10.4k từ. Tiêu đề chỉ nói về "averaged and guided" trong khi gần nửa bài (Sec. 5, Sec. 6.4) là về learned field và EDM.
- **Vì sao quan trọng.** Reviewer ICLR sẽ không nắm được thông điệp mang về. Ba "đường dây" (exact-field atomicity, composition counterexample, learned-field landing trên EDM) đủ chất liệu cho hai bài.
- **Cách sửa.** Cắt abstract xuống ≤200 từ với 3 claim. Cân nhắc tách bài: (A) atomicity và composition cho exact field (phù hợp TMLR hoặc một venue lý thuyết); (B) relative-error landing cùng EDM two clocks và Heun. Nếu giữ một bài, đổi tiêu đề cho khớp với claim trung tâm.

### W5 — [Major] Phần "What this means in practice" mạnh hơn bằng chứng

- **Ở đâu.** Dòng 226–256.
  - (i) "The knobs are not privacy mitigations": kết luận chỉ đúng *at the exact optimum*. Nhưng chính bài cho thấy U-Net CIFAR với $h=6$ có 28–38% sample off-atom (dòng 1079–1081, 3341–3342), và public EDM model có 0% memorisation. Công trình thực nghiệm dùng caption/conditioning noise để giảm copying (Somepalli et al. 2023, "Understanding and mitigating copying", **đã có trong refs.bib dưới key `somepalli2023copying` nhưng không được cite**) nói về trained model, không phải exact field. Câu (i) vì vậy dễ bị đọc như phản bác những công trình đó, trong khi thực ra không mâu thuẫn.
  - (iii) "Monitor late-time field error, not the loss": nhưng Sec. 6.4 (dòng 1319–1328) cho thấy nó không tốt hơn khoảng cách $D_\theta$→nearest training image, và đòi hỏi exact field, tức một tổng trên toàn bộ tập huấn luyện ở mỗi bước. Một khuyến nghị thực hành mà baseline đơn giản hơn làm tốt ngang thì không nên đứng thành một bullet riêng.
- **Cách sửa.** Đổi (i) thành "at the exact optimum these knobs do not change the support; any mitigation they provide in trained models must come from the learned-field error", cite Somepalli 2023b, Wen et al. 2024 và các công trình khác. Gộp (iii) với kết quả âm tính của Sec. 6.4, hoặc bỏ đi.

### W6 — [Major] Phần EDM có yếu tố gần tautology; cách anchoring và tiêu chí off-atom cần được tách bạch

- **Ở đâu.** Table edm-rho (dòng 1278–1301) dùng $n_t$ là "distance to the endpoint's nearest training image", tức là dùng thông tin endpoint. Nhãn off-atom cũng được định nghĩa bằng endpoint (tỷ lệ 1/3). Khi đó $\varrho_t\approx1$ cuối quỹ đạo gần như đồng nghĩa với "không co về ảnh đó". Tác giả có nói anchoring theo nearest image của $D_\theta$ "gives the same AUC", nhưng chỉ trong caption và appendix. Late contraction trên model 2000 ảnh có AUC 0.983 so với baseline 0.985 (dòng 1325–1326). Tác giả cũng tự nhận định Thm. 5.2 "the mechanism of landing, not a cheaper test", tức đây chủ yếu là một mô tả lại hiện tượng. Ngoài ra, câu "replacing the field on the last 2% … turns no memorisation into complete memorisation" (dòng 1255–1257) là hệ quả trực tiếp của Thm. 4.1/Prop. 3.2 (exact field luôn kết thúc trên atom), nên không phải bằng chứng thực nghiệm độc lập.
- **Vì sao quan trọng.** Đây là phần duy nhất chạm tới model quy mô thực, và nó đang được dùng để biện minh cho significance.
- **Cách sửa.** Đưa anchoring không dùng endpoint lên làm phân tích chính trong main text. Báo cáo một kết quả *can thiệp*, ví dụ: chỉ cần chỉnh field ở các mức $\sigma$ mà $\varrho$ cho biết thì có đổi outcome không. Hoặc báo cáo một dự đoán out-of-sample, ví dụ $\varrho$ ở $\sigma\approx0.585$ dự đoán off-atom trên model 2000 ảnh tốt hơn $D_\theta$-NN. Nói rõ "selection early" liên hệ thế nào với speciation time của Biroli et al. 2024 (W9).

### W7 — [Major] Fit với giới hạn 9 trang ICLR: phần main text phụ thuộc nặng vào appendix

- **Ở đâu.** Bản ICLR chuyển ra appendix: Thm. 4.8 spectral (cả định nghĩa $M,\Gamma$), Prop. 4.7, Prop. hyperplane, Prop. localtransfer, Prop. regular, Prop. bottleneck, Prop. heun, mọi proof sketch, Fig. portrait/cifar/kernel/composition, phần spectral experiment và learned-label-average pilot (dòng 1683–4236, các `\placeblock`). Tuy vậy, intro vẫn tham chiếu tới tất cả các kết quả này như contribution (dòng 165–189). Limitations của bản ICLR trỏ tới "label-averaging pilot of Appendix…" (dòng 1354). Tôi không compile được, nhưng main text bản ICLR vẫn còn khoảng 5 figure, 2 table, khoảng 14 formal statement và một abstract khoảng 400 từ. Tôi khó tin nó vừa 9 trang mà không có thủ thuật về khoảng cách.
- **Vì sao quan trọng.** Reviewer ICLR đánh giá dựa trên main text. Spectral criterion, một contribution được nêu trong intro, lại không có statement trong main text. Phần "ICLR" của Sec. 4.4 (dòng 774–785) là một đoạn văn dày đặc tham chiếu chéo mà người đọc không thể hiểu nếu không mở appendix.
- **Cách sửa.** Compile và báo cáo số trang. Bỏ khỏi danh sách contribution trong intro những gì không nằm trong main text, hoặc nêu chúng như "further results". Cân nhắc TMLR, nơi không có giới hạn trang và bản TMLR đã sẵn sàng.

### W8 — [Minor→Major tùy venue] Submission hygiene và rủi ro dual submission

- Còn sót các comment `% DRAFT` (dòng 1423), `% CHECK` (1439–1442), `% TODO` (2846–2848: thiếu trích dẫn cho tính $C^1$ của Lyapunov–Perron fixed point, một lỗ hổng *trích dẫn* trong chứng minh Thm. 4.8), cùng các đường dẫn nội bộ `docs/plan/...` và ngày tháng (899–900, 1233–1235, 3373–3374). Nếu source được nộp lên arXiv thì sẽ lộ ra.
- Dòng 5 ghi "TMLR submission", README gọi `main.tex` là "full anonymous TMLR manuscript", và còn có `workshop.tex` "ICLR 2027 workshop version" (tiêu đề "Trained Conditional Flows Memorise…"). Tác giả cần chắc chắn rằng bài không đồng thời đang được review ở TMLR (vi phạm dual-submission policy), và rằng bản workshop là non-archival, nộp sau quyết định của main conference, theo đúng policy ICLR 2027.
- `\openreview` vẫn là placeholder `XXXX` (dòng 95). Vô hại nhưng nên dọn.
- Supplementary code: cần kiểm tra để không lộ tên tài khoản hay đường dẫn máy trong script và output (tôi không thấy trong `main.tex`).
- **Cách sửa.** Dùng một bước build strip comment (ví dụ `arxiv_latex_cleaner`) và kiểm tra trạng thái nộp ở các venue khác.

### W9 — [Minor] Thiếu trích dẫn trực tiếp liên quan dù đã có trong refs.bib

`biroli2024dynamical` ("Dynamical Regimes of Diffusion Models") và `somepalli2023copying` có trong `refs.bib` nhưng **không được cite ở đâu** trong `main.tex`. Cả hai liên quan trực tiếp: Biroli et al. 2024 về speciation time và collapse time, tương ứng với "image chosen early / reached late" (Sec. 6.4); Somepalli 2023b về conditioning noise như một biện pháp mitigation (abstract dòng 102–104 và (i)). Xem thêm mục Missing references.

### W10 — [Minor] Độ rõ ràng cho khán giả ICLR

- Câu văn rất dài và dày mệnh đề. Ví dụ dòng 108–113 của abstract, và dòng 191–209 của intro (các khối `\ificlr`/`\else` khiến luồng đọc của bản ICLR khác bản TMLR).
- Ký hiệu chồng chéo: $w$ vừa là guidance strength vừa là posterior weight $w_i$/$w_j$ (dòng 904, 913). $\rho$ vừa là endpoint noise vừa là bán kính (dòng 270, 953). $B$ vừa là log-odds vừa là certificate $B_T$ (dòng 3307).
- "EXP-1/2/3" xuất hiện trong intro (dòng 168) trước khi được định nghĩa (dòng 1010).
- Fig. 1 (dòng 211–224) là hình mở đầu, nhưng dựa vào EDM và $\varrho$, những khái niệm chỉ có ở Sec. 5–6, trong khi trọng tâm của tiêu đề là averaging/guidance.

### W11 — [Minor] Một số điểm đáng ngờ về tính chặt (để reviewer proof xem kỹ)

- Thm. 5.2(b) yêu cầu $\omega_t\to0$, tức $w_i(Z_t,t)\to1$. Điều này gần như giả định trajectory đã ở gần $a$. Prop. trap xử lý được trong EDM coordinates, nhưng main text nên nói rõ rằng (b) chỉ là non-circular khi đi kèm Prop. trap.
- Thm. 4.8(c) phụ thuộc vào một bước $C^1$ chưa có trích dẫn (TODO dòng 2846).
- Prop. 4.3 nói "unique trajectory … from every finite initial point" cho exact guided field với $w\ge0$. Tôi không thấy chỗ nào lỗi, nhưng cần kiểm tra rằng Lemma wellposed phủ được trường hợp hệ số âm.
- Dòng 1255 dùng "the public model, which never memorises" dựa trên 1000 sample và ngưỡng 1/3. Nên nói "no sample in 1000 met the criterion".

---

## Questions for authors

1. Đoạn disclosure LLM (dòng 1443–1447) có phản ánh đúng việc các bản nháp đầu tiên của chứng minh Thm. 5.2, Prop. trap và Prop. heun được tạo bởi model không? Các anh/chị có định sửa không?
2. Abstract nói "models that memorise 4 and 50%", còn Sec. 6.4 nói 4.1% off-atom. Con số nào đúng?
3. Ngoài việc bỏ giả thiết của Liu & Zuazua (2026), phần nào của Sec. 4.1–4.2 là mới về kỹ thuật? Template Liouville/divergence đã từng được dùng cho score flows chưa?
4. Có ví dụ *thực tế* nào (sampler, ensembling theo label, hay network có label embedding mượt) mà field gần với guided label averaging đủ để basin ở thang $(1-t)^2$ có ý nghĩa không? Nếu không, vì sao composition nên là một contribution của main text thay vì một remark?
5. Trên model 2000 ảnh, nếu dùng $\varrho$ hoặc late contraction tính *trước* $\sigma=0.585$ (không dùng thông tin endpoint) thì AUC là bao nhiêu? Nó có vượt baseline $D_\theta$-NN ở $\sigma$ đó không?
6. "Image chosen at $\sigma\approx1$" khác hay trùng với speciation time của Biroli et al. (2024) trên CIFAR-10?
7. Thí nghiệm swap (network → exact field) có thể làm chiều ngược lại không (exact field → network ở cuối), để kiểm tra rằng *chỉ* late field quyết định landing?
8. Bài có đang được review ở TMLR, hoặc bản workshop có archival không?
9. Bản ICLR compile ra bao nhiêu trang main text?

---

## Missing references

Đã có trong `refs.bib` nhưng không được cite trong `main.tex` (chắc chắn tồn tại):
- Somepalli, G., Singla, V., Goldblum, M., Geiping, J., Goldstein, T. *Understanding and Mitigating Copying in Diffusion Models.* NeurIPS 2023. Liên quan trực tiếp tới việc dùng conditioning noise để giảm replication.
- Biroli, G., Bonnaire, T., de Bortoli, V., Mézard, M. *Dynamical Regimes of Diffusion Models.* Nature Communications 2024. Speciation và collapse time, tương ứng với hai "clocks".

Chắc chắn tồn tại, nên cite:
- Wen, Y., Liu, Y., Chen, C., Lyu, L. *Detecting, Explaining, and Mitigating Memorization in Diffusion Models.* ICLR 2024. Dùng độ lớn text-conditional guidance để phát hiện memorisation, liên quan tới (iii) và guidance.
- Raya, G., Ambrogioni, L. *Spontaneous Symmetry Breaking in Generative Diffusion Models.* NeurIPS 2023. Thời điểm "quyết định" trong sampling và điểm tie đối xứng.
- Ambrogioni, L. *In Search of Dispersed Memories: Generative Diffusion Models Are Associative Memory Networks* (arXiv 2023 / Entropy 2024). Cách nhìn attractor/basin.
- Zhang, H., Zhou, J., Lu, Y., Guo, M., Wang, P., Shen, L., Qu, Q. *The Emergence of Reproducibility and Generalizability in Diffusion Models.* ICML 2024.
- Yi, M., Sun, J., Li, Z. *On the Generalization of Diffusion Model* (arXiv 2305.14712, 2023). Empirical optimum memorises.
- Wu, Y., Chen, M., Li, Z., Wang, M., Wei, Y. *Theoretical Insights for Diffusion Guidance: A Case Study for Gaussian Mixture Models.* ICML 2024.
- Bradley, A., Nakkiran, P. *Classifier-Free Guidance is a Predictor-Corrector* (arXiv 2024).
- Karras, T. et al. *Guiding a Diffusion Model with a Bad Version of Itself.* NeurIPS 2024. Autoguidance, liên quan tới guidance và field error.
- Dockhorn, T., Cao, T., Vahdat, A., Kreis, K. *Differentially Private Diffusion Models.* TMLR 2023. Liên quan đến câu về DP ở dòng 232.
- Li, X., Dai, Y., Qu, Q. *Understanding Generalizability of Diffusion Models Requires Rethinking the Hidden Gaussian Structure.* NeurIPS 2024.
- Wang, B., Vastola, J. *The Unreasonable Effectiveness of Gaussian Score Approximation for Diffusion Models and its Applications.* TMLR 2024.

Cần kiểm tra:
- Bonnaire, T., Urfin, R., Biroli, G., Mézard, M. *Why Diffusion Models Don't Memorize: The Role of Implicit Dynamical Regularization in Training* (2025) — cần kiểm tra venue.
- Achilli, B., Ventura, E., Silvestri, G., et al. *Losing Dimensions: Geometric Memorization in Generative Diffusion* (2024) — cần kiểm tra.
- Ross, B. et al. *A Geometric Framework for Understanding Memorization in Generative Models* (ICLR 2025) — cần kiểm tra.

Ghi chú: nhiều trích dẫn năm 2026 (`sesmat2026leaks`, `physicscfm2026`, `li2026memory`, `smola2026support`, `liu2026geometric`, `beltran2026reward`, `dodson2026calm`, `lopezamado2026modes` arXiv 2609.39648, `jaziri2026spectral` 2611.01775, `verma2026early` 2610.11670) nằm ngoài khả năng xác minh của tôi. Đề nghị chạy kiểm tra DBLP/arXiv cho tất cả, đặc biệt là các key được dùng để định vị novelty (Liu & Zuazua 2026 và Smola 2026).

---

## Scores

- **Soundness: 3/4.** Các statement được phát biểu cẩn thận, kèm giả thiết rõ ràng và tự giới hạn. Phần số học khớp với lý thuyết. Trừ điểm vì một chứng minh còn TODO trích dẫn (Thm. 4.8), Thm. 5.2(b) cần Prop. trap mới thực sự non-circular, và phân tích EDM chính dùng anchoring có thông tin endpoint.
- **Presentation: 2/4.** Văn phong dày đặc, abstract khoảng 400 từ có một lỗi định lượng, narrative có 6 mạch, bản ICLR phụ thuộc nặng vào appendix, và ký hiệu chồng chéo.
- **Contribution: 2/4.** Kết quả mới nhất (composition/spectral) bị chính tác giả xếp là không thực tế. Các kết quả có liên quan thực tế (transfer, relerr) thì sơ cấp. Phần atomicity dưới guidance là một bước tăng có thật nhưng hẹp so với Liu & Zuazua và với kiến thức "empirical minimiser memorises".
- **Overall Rating: 5 (marginally below the acceptance threshold).** Bài trung thực, kỹ lưỡng và đúng về kỹ thuật, nhưng là một tập hợp các kết quả đúng hơn là một contribution có trọng tâm cho ICLR. Bản TMLR hiện có hợp hơn với tiêu chí "correct and of interest" của TMLR.
- **Confidence: 4/5.** Tôi quen thuộc với tài liệu về memorisation và guidance, nhưng không kiểm tra chi tiết từng chứng minh.

---

## Điều gì sẽ nâng điểm của tôi

Trước hết, sửa W1 (disclosure LLM trung thực) và W2 (lỗi abstract); đây là điều kiện tiên quyết, không phải điểm cộng. Sau đó tôi sẽ nâng lên 6 nếu bài chọn một luận điểm trung tâm và thể hiện nó trong 9 trang. Ví dụ "selection early, landing late, decided by relative contraction", được củng cố bởi: (a) một thí nghiệm *can thiệp*, trong đó chỉnh late field hoặc lịch bước theo $\varrho$ thay đổi được tỷ lệ memorisation trên model thật; (b) một phân tích không dùng thông tin endpoint, cho thấy late contraction đo *trước* landing có thông tin vượt baseline $D_\theta$-NN, hoặc chỉ ra rõ vì sao điều đó không thể xảy ra; và (c) liên hệ rõ với speciation/collapse time của Biroli et al. (2024). Khi đó các kết quả atomicity dưới guidance/mixtures sẽ là phần nền đã được rút gọn, còn composition/spectral nằm ở appendix như một "boundary result". Ngược lại, nếu tác giả muốn bài là một bài lý thuyết về guidance dynamics, tôi cần thấy spectral criterion được phát biểu đầy đủ trong main text, so sánh chi tiết với Liu & Zuazua ở main text, và bỏ phần EDM. Với cách tiếp cận đó, tôi khuyên nộp TMLR, nơi bài hiện tại gần như đã sẵn sàng.

---

### Reviewer 1 (Methodology / Proofs): "Atomic Endpoints of Averaged and Guided Empirical Conditional Flows"

## Summary

Bài báo nghiên cứu flow của trường vận tốc tối ưu chính xác (exact population minimiser) của conditional flow matching trên một tập huấn luyện hữu hạn cố định, rồi hỏi các can thiệp phía sampler có đưa endpoint ra khỏi các atom huấn luyện hay không. Các can thiệp được xét là label noise ($h>0$), trung bình trường theo nhãn, classifier-free guidance (cố định hoặc theo schedule), và tổ hợp của chúng. Các kết quả chính:

1. Endpoint law với label smoothing là Nadaraya–Watson trên các atom (Thm endpoint, l.443–450). Tác giả tự nói đây là một tham chiếu, không phải đồng nhất thức mới.
2. Template hai bước (l.509–519, App. l.1975–2060). Bước 1: động năng hữu hạn kéo theo hội tụ về một tập ứng viên hữu hạn $\mathcal C\subseteq\mathcal C'$ (Lemma conv). Bước 2: $\operatorname{div}=\beta\Theta-d$, nên khi $\int\operatorname{div}\to+\infty$ thì tập điểm đầu có giới hạn không phải atom là null, theo Liouville + Fatou (Lemma volume).
3. Template này được áp dụng cho positive field mixtures (Thm posmix), guidance $w\ge0$ cố định hoặc schedule BV bị chặn (Prop cfgatom, Thm schedule; dùng Lemma signedconv, lấy tích phân từng phần theo biến phân của hệ số), và guidance tại hard label với tốc độ $(1-t)\sqrt{\log}$.
4. Một phản ví dụ: guided label averaging trên hai atom có basin mở tại trung điểm khi và chỉ khi $w>1/\sinh^2B$ (Thm composition), kết luận này ổn định dưới nhiễu (Prop composition-open). Bài cũng đưa ra phân loại phổ trong mọi chiều qua blow-up $\xi=\beta P_L(x-tz)$ và đồ thị Lyapunov–Perron (Thm spectral, Cor spectral-threshold).
5. Phần chuyển sang trường học được: Thm transfer (variation of constants), Thm relerr (sai số tương đối so với khoảng cách), Prop trap, Prop heun (bước Heun là tổ hợp affine, có thể ngoại suy khi $r<1/2$), Prop regular.
6. Thí nghiệm gồm: tính toán exact-field (stress test, composition bằng bisection có stopping rule lấy từ chứng minh, kiểm tra phổ); trường học được trên toy và CIFAR-10; mô hình EDM trên CIFAR-10.

Nhìn chung, phần chứng minh mà tôi kiểm tra là đúng, và nhiều chỗ được viết cẩn thận hơn mức thường gặp ở một bài ML. Các vấn đề chính nằm ở mấy chỗ: (i) đóng góp toán học, so với các công cụ chuẩn, ở mức vừa phải; (ii) một vài bước kỹ thuật cốt lõi, đặc biệt là Lemma lp, được viết dưới dạng phác thảo và thiếu trích dẫn; (iii) một số diễn giải thực nghiệm vượt quá những gì định lý cho phép, và vài "kiểm chứng số" theo thiết kế không thể thất bại.

## Strengths

1. **Template hai bước sạch và tái sử dụng được** (Lemma conv l.1982–2019; Lemma volume l.2021–2060).
   - Lemma conv loại trừ được dao động giữa hữu hạn ứng viên một cách đúng đắn. Lập luận dùng hai ý: $\omega$-limit set liên thông và $\mathcal C'$ hữu hạn. Phần đánh giá tốc độ bị chặn dưới trên compact rời $\mathcal C'$ được làm chặt chẽ qua lập luận "passage" (l.2010–2015).
   - Lemma volume chỉ cần $J_n\to\infty$ theo từng điểm trên $E$, cộng với tính bị chặn đều của $\Phi_n(K_0)$. Với giả thiết đó, Fatou cho $\operatorname{Leb}(E)=0$ mà không cần $\Theta$ bị chặn dưới đều theo thời gian.
2. **Xử lý trường hợp "$\Theta$ chỉ dương theo trung bình"** một cách đúng kỹ thuật.
   - Thm posmix (l.2133–2145) dùng tập "good times" có độ đo $\ge1/2$ trên mỗi $[n-1,n]$, rút ra bằng Chebyshev từ động năng hữu hạn.
   - Thm schedule (l.2336–2359) dùng đồng nhất thức $(1+w)|u|^2-w|v|^2=|(1+w)u-wv|^2-w(1+w)|u-v|^2$ để tách $\Theta=r^2-|\mu_w|^2+w(1+w)|\mu_c-\mu_u|^2+o(1)$. Số hạng $|\mu_w|^2$ chỉ nhỏ trong $L^2$ trên từng khoảng đơn vị. Bài xử lý đúng điều này bằng tỉ số $\beta(n+1)/\beta(n)\le C_\beta$. Đây chính là chỗ mà một chứng minh cẩu thả sẽ ngầm giả định $\Theta\ge c>0$ theo từng điểm.
3. **Lemma signedconv** (l.2223–2292). Mẹo lấy tích phân từng phần log-partition $h_k$ theo $dc_k$ (BV, right-continuous modification), cùng cận KL thứ hai $\log(1/p_{\min})$, cho năng lượng hữu hạn với hệ số có dấu. Mẹo này gọn và đúng. Đó cũng là phần thực sự mới so với Lyapunov đơn điệu của Thm posmix.
4. **Thm composition** (l.2489–2576) là một counterexample tường minh, chặt và xử lý được cả trường hợp không hyperbolic $w=w_c$. Phần (b) dùng cận $F_w\ge\kappa\min\{s^3,1\}$ và barrier dưới $\theta(\tau)=(\kappa\beta^3)^{-1/2}$. Trong khi đó, phân loại phổ (l.821–822) phải loại trường hợp này ra.
5. **Thm spectral (c)** (l.2879–2938). Thế năng $\Psi$ (log-sum-exp có dấu) có $\nabla\Psi=G$, kết hợp với điều kiện mặt (face condition) để chặn $|G|$ ở vô cực, rồi lập luận excursion + $\Psi=o(\sigma)$. Đây là một lập luận "không thoát ra vô cực" đẹp. Việc dùng Barbalat để có $G(\xi)\to0$ là đúng.
6. **Trung thực về giới hạn.**
   - Thm composition được đọc như một "boundary marker" (l.723, l.186).
   - Định luật $P_0\sim\sqrt{2/\pi}(w/w_c-1)/\cosh B$ được dán nhãn rõ là formal (l.2602).
   - Bảng composition ghi "not verified by interval arithmetic" (l.4031).
   - Các lần chạy DOP853 thất bại cũng được báo cáo (l.3955–3957).
7. **So sánh với Liu et al.** qua phép đổi biến $y=x/t$, $\sigma=(1-t)/t$ (l.1840–1858). Tôi đã kiểm tra lại: $dy/d\sigma=-(m-y)/\sigma=-\sigma\nabla\log p_\sigma$, đúng. Phép đổi biến này đặt kết quả về guidance (không cần giả thiết về limit set) vào đúng ngữ cảnh của Remark 3.19 trong liu2026geometric.

## Weaknesses

### W1 (Major, rigor/presentation): Lemma lp (Lyapunov–Perron) chỉ là phác thảo, và claim $C^1$ không có trích dẫn
- **Ở đâu:** l.2786–2849. Comment LaTeX ở l.2846–2848 tự thừa nhận là thiếu trích dẫn.
- **Vấn đề:**
  - Hằng số co "$C\delta\max\{a^{-1},1\}$", "after shrinking $\delta$" và cận "fixed point có cỡ $\le C(|s_0|+|\eta_0|+\delta\varepsilon)$" đều không được tính ra. Hằng số $C$ đến từ $D\chi$ của cutoff (l.2823) và dùng chung cho mọi $T'\ge T$, nhưng tính đều này không được kiểm.
  - Claim "graph $C^1$" (l.2843) viện dẫn "standard differentiability" mà không có nguồn.
  - Hệ là non-autonomous, với tốc độ $\beta(\tau)\to\infty$ trên $L$ và tốc độ $1$ trên $L^\perp$. Trong thời gian nhanh $\sigma$, hướng $\eta$ trở thành gần-center (tốc độ $1/\beta\to0$). Vì vậy độc giả cần thấy rõ rằng dichotomy được lấy trong thời gian $\tau$: phần stable có exponent $\min\{1,a\beta\}$, phần unstable có exponent $a\beta$. Bài không nói rõ điều này.
- **Tại sao quan trọng:** Lemma lp là lõi của Thm spectral (a)(b).
- **Fix cụ thể:**
  - Cho (b) chỉ cần đồ thị **Lipschitz**, và đồ thị Lipschitz codim $\ge1$ là null. Tính Lipschitz suy ra trực tiếp từ uniform contraction theo $(s_0,\eta_0)$. Nên bỏ claim $C^1$, hoặc chuyển nó thành remark có trích dẫn (ví dụ stable manifold theorem cho hệ có exponential dichotomy: Coppel 1978; Barreira–Valls 2008; hoặc Palmer).
  - Nên viết tường minh hằng số co và chứng minh rằng tập "stay in the $\varepsilon/2$-ball and tend to 0" trùng với tập điểm bất động.

### W2 (Major, interpretation): diễn giải $\varrho_t\approx1$ là "non-landing regime of Thm relerr(c)" là sai về logic
- **Ở đâu:** l.1305–1306; cũng l.217–222 (Fig. 1), l.288 (Fig. unrolled (e)).
- **Vấn đề:**
  - Thm relerr(c) đòi hỏi **radial ratio** $\langle\hat e_t,\hat x_1-a\rangle/n_t\ge1-\delta_t$, với $\int\delta_t^+/(1-t)\,dt<\infty$.
  - Relative error $\varrho_t=e_t/n_t\approx1$ chỉ cho biết giả thiết của (b) thất bại. Radial ratio bị chặn trên bởi $\varrho_t+\omega_t/n_t$, nhưng $\varrho\approx1$ không kéo theo radial ratio $\approx1$, vì hướng của sai số có thể tùy ý.
  - Ngoài ra, giả thiết tích phân được của (c) là một mệnh đề tiệm cận $t\uparrow1$. Nó không thể kiểm trên lưới 18 bước kết thúc ở $\sigma=0.002$. Đại lượng "late contraction" $C=\int_{0.002}^{0.585}(1-\varrho)\,d\log(1/\sigma)$ (l.3650) luôn hữu hạn.
- **Tại sao quan trọng:** abstract (l.115–117) và intro (l.174–176) trình bày các phép đo EDM như minh họa cơ chế của Thm relerr.
- **Fix:**
  - Báo cáo trực tiếp radial ratio (bảng ở l.3638 đã có AUC của radial ratio, nhưng không có median theo $\sigma$).
  - Diễn đạt lại thành: "consistent with the failure of the hypothesis of (b)", không phải "the regime of (c)".
  - Nói rõ rằng $C$ là một proxy hữu hạn cho đại lượng tiệm cận.

### W3 (Major, methodology): "Heun bound never violated" là một kiểm tra hiển nhiên theo cấu trúc (tautological)
- **Ở đâu:** l.1337, l.3574–3598 (Table edm-heun, "No step of any of the 1500 trajectories violates the bound"), l.3671.
- **Vấn đề:** $\varrho_k$ được định nghĩa là giá trị lớn hơn trong hai relative error *đo được* tại $x_k$ và $\tilde x_k$, với $\gamma=0$ và $\omega$ lấy từ posterior chính xác (l.3575–3576). Khi đó giả thiết của Prop heun(b) đúng theo định nghĩa. Kết luận $n_{k+1}\le c_kn_k+b_k$ chỉ là hệ quả của bất đẳng thức tam giác (chứng minh l.3524–3527). Vì vậy "0 violations" chỉ kiểm tra code, không kiểm tra lý thuyết hay mô hình. Tương tự, "dự đoán" rằng thêm bước sẽ làm $c_k<1$ đến từ Prop heun(c): $r\ge1/2\Rightarrow c<1$ với mọi $\varrho<1$. Đó là một sự kiện toán học về schedule, không phải về mạng.
- **Fix:**
  - Trình bày phần này như một sanity check.
  - Tách rõ phần nội dung thực nghiệm thật sự: tỉ lệ off-atom và ảnh đạt được không đổi theo số bước, và tỉ lệ mẫu có $\varrho_k<\varrho_{\rm crit}(r_k)$.
  - Một kiểm tra có thể thất bại thì phải dùng $\varrho$ đo *trước* bước, chẳng hạn chỉ tại $x_k$ và dùng cận cho $\tilde x_k$ suy từ mô hình, rồi so với $n_{k+1}$ thực tế.

### W4 (Major, methodology): stress test exact-field không có positive control và dùng scheme có thể "đẩy" quỹ đạo khỏi các tie hút
- **Ở đâu:** l.1104–1110, l.3943–3949 (fixed-step log-time RK4, 256/512 bước mỗi đoạn, gap tới $10^{-6}$). So sánh với l.4064–4067, nơi tác giả tự ghi nhận rằng RK4 bước cố định mất ổn định khi $\beta|F'|\Delta\tau>2.8$ và "ejects the trajectories an attracting tie holds".
- **Vấn đề:**
  - Gần một ứng viên không phải atom, Jacobian trong thời gian $\tau$ là $\beta\Gamma-I$ với $\beta\sim\varepsilon^{-2}\sim10^{12}$. RK4 bước cố định với $\Delta\tau\approx0.02$ không ổn định ở đó.
  - Kết quả là stress test, theo cấu trúc, thiên về kết luận "kết thúc trên atom", tức đúng giả thuyết đang được kiểm. Các arm của nó (single field, guidance, label average, prior average) không gồm composite. Do đó không có bằng chứng rằng pipeline phát hiện được một endpoint off-atom khi nó tồn tại.
  - Tác giả có nói "finite-time consistency checks, not a numerical proof" (l.1110–1111), nhưng con số "$6.11937\times10^{-6}$" vẫn được trình bày như một xác nhận định lượng.
- **Fix:** chạy cùng pipeline trên composite với $w=2w_c$ làm positive control. Pipeline phải tìm lại được $P_0\approx0.406$ ở $B=1$. Nếu không, phải chuyển sang integrator implicit hoặc integrator trong biến blow-up $s$ hay $\xi$ (như đã làm cho Table composition và Table spectral).

### W5 (Major, contribution): phần lớn kết quả dùng công cụ chuẩn; phần mới là tương đối hẹp
- **Phần đã biết hoặc gần biết:**
  - Hội tụ a.e. về atom cho flow empirical một prior (liu2025pde Thm 3.7, qua chính phép đổi biến của bài).
  - Kỹ thuật Liouville + Fatou cho basin null, vốn là phiên bản thể tích của các lập luận "avoid saddles a.e.".
  - Thm transfer: tác giả tự nói "elementary" (l.888).
  - Thm relerr (a)–(d): (a) là đạo hàm của chuẩn, (b) là Grönwall với hệ số $\nu=1-\bar\varrho$, (c) là Grönwall ngược, (d) là ví dụ tuyến tính một atom.
  - Prop trap và Prop heun: tính toán một bước.
- **Phần thực sự mới:**
  - Lemma signedconv cho hệ số có dấu và BV, từ đó trả lời trường hợp guidance $\lambda>1$ cùng support mà Remark 3.19 của liu2026geometric để ngỏ.
  - Counterexample composition với ngưỡng chính xác.
  - Phân loại phổ.
- **Tại sao quan trọng:** đóng góp ở mức "solid but incremental", trong khi bài đang dàn trải trên rất nhiều mệnh đề.
- **Fix:** nêu rõ trong intro rằng đóng góp kỹ thuật chính là Lemma signedconv, Thm composition và Thm spectral; chuyển Thm transfer, Thm relerr, Prop trap và Prop heun thành "observations/tools".

### W6 (Minor–Major, statement strength): giả thiết của Thm relerr(b) đặt lên chính quỹ đạo
- **Ở đâu:** l.918–919, $\omega_t=(1-w_i(Z_t,t))\max_k|x^k-a|\to0$.
- **Vấn đề:** điều kiện $\omega_t\to0$ đòi posterior tại $Z_t$ tập trung về $a$, tức về thực chất quỹ đạo nằm trong một compact của phần trong ô Voronoi của $a$ ở thời gian muộn. Đây là một giả thiết a posteriori. Prop trap (l.3435–3453) là phiên bản cục bộ không vòng, nên mới là phát biểu có thể dùng.
- **Fix:** phát biểu (b) dưới dạng cục bộ như Prop trap. Hoặc nêu rõ ở l.928–930 rằng (b) là một mệnh đề điều kiện theo quỹ đạo.

### W7 (Minor): Thm spectral (c) có giả thiết mạnh và chưa có nhận xét về tính generic
- **Ở đâu:** l.795–798.
- **Vấn đề:** cả "every profile hyperbolic" và face condition đều không được chỉ ra là generic, chẳng hạn dưới nhiễu của $(c_k,p_k)$. Chiều (a) và (b) là cho từng profile, nên không ảnh hưởng.
- **Fix:** thêm một remark về tính generic (Sard / transversality theo tham số $p_k$), hoặc nói rõ là còn mở.

### W8 (Minor): trích dẫn cho tính khả vi của flow Carathéodory và công thức Liouville
- **Ở đâu:** l.1964–1971. Bài trích "[Hale, Ch. I]" cho một outline.
- **Vấn đề:** với trường chỉ đo được theo thời gian (Thm schedule), cần một định lý cụ thể về khả vi theo điều kiện đầu, với $D_xf$ Carathéodory và bị chặn khả tích địa phương.
- **Fix:** trích một định lý chính xác, ví dụ Hale 1980 Thm I.3.3 hoặc Bressan–Piccoli, Thm 2.3.2.

### W9 (Minor): kiểm tra phổ số học dùng tiêu chí dừng heuristic, không lấy từ chứng minh
- **Ở đâu:** l.3975–3980, Table spectral.
- **Vấn đề:**
  - Tiêu chí "$|\xi|<5$ tại $\sigma=10^4$" khác với Table composition, nơi stopping rule là forward-invariant (tôi đã kiểm: với $\dot s=\beta F(s)+(1+\varepsilon/t)s$, các rule ở l.3962–3966 đúng là bất biến tiến, vì $\beta$ tăng và $1+\varepsilon/t$ giảm).
  - Ở $d=8$, các sink $1.1w_c$ và $2w_c$ có basin dưới độ phân giải. Vì vậy phần (a) chỉ được "xác nhận" ở 5/8 dòng sink.
  - Box $5w_c$ đổi từ $0.0039$ sang $0.0020$ giữa $\sigma=10^2$ và $10^4$.
- **Fix:** dùng tiêu chí bất biến tiến cho sink. Chẳng hạn, nếu $\Gamma\prec0$, một quả cầu nhỏ quanh $\xi_\star$ trong metric thích hợp là bất biến khi $|\mathcal R|$ nhỏ, mà $|\mathcal R|=(1/(t\beta))|\xi|$ là tường minh khi $S=A$.

### W10 (Minor, presentation)
- Bài dài 4258 dòng, và các phát biểu bị di chuyển qua lại bằng `\moveblock` / `\ificlr`. Các sketch nằm ở main text trong một phiên bản và ở appendix trong phiên bản kia. Điều này làm việc đối chiếu khó.
- Source có comment nội bộ (l.899–900, l.1233–1235, l.2846–2848) trỏ tới tài liệu và đường dẫn nội bộ, và một TODO. Phải gỡ trước khi nộp supplementary để giữ ẩn danh và tính hoàn chỉnh.
- Prop trap (iii) (l.3466–3467): thực ra $\Omega\le(N-1)\delta_iq^2<(N-1)\delta_iq$, và định nghĩa $q$ cần $N\ge2$.
- Lemma volume (l.2021) được phát biểu cho "every trajectory whose limit is not an atom". Nhưng l.818 dùng nó cho một tập con, cụ thể là basin của một profile có $\operatorname{tr}\Gamma>0$. Lập luận Fatou vẫn đúng cho mọi Borel $E$ mà trên đó $J_n\to\infty$, nhưng nên phát biểu lemma ở dạng đó.

## Proofs I checked in detail (line-by-line)

| Kết quả | Dòng | Verdict |
|---|---|---|
| Lemma basic (a)–(d) | 1894–1962 | **Correct.** $D_xm_p=\beta\operatorname{Cov}$, $\partial_\alpha H=-D_{KL}$, cả hai cận KL, và concentration đều kiểm lại được. |
| Lemma conv | 1982–2019 | **Correct.** Ý "no oscillation" được giải quyết qua tính liên thông của $\Omega$ và $\mathcal C'$ hữu hạn. Lập luận passage đúng. |
| Lemma volume | 2021–2060 | **Correct.** Borel-measurability qua giới hạn từng điểm của $\Phi_n$; $\Phi_n(K_0)$ bị chặn đều; Fatou. Một gap nhỏ về trích dẫn khả vi flow Carathéodory (W8). |
| Thm posmix | 2073–2147 | **Correct.** Tôi đã tính lại $\dot W=-|\dot x|^2+\dot\alpha\int D_{KL}+\tfrac\varepsilon2(\int\sum q|a|^2-R^2)$ và $W\ge0$. Tính liên tục của $V$ trên simplex đóng và $V=0$ chỉ tại các đỉnh đúng, vì $Q_p(r)$ cùng support với $r$. |
| Prop hyperplane | 2175–2218 | **Correct** ($\dot\zeta=A_0\tanh(\beta\zeta)-\zeta$, barrier). |
| Lemma signedconv | 2232–2292 | **Correct.** Tích phân từng phần Lebesgue–Stieltjes với $h_k$ liên tục và $c_k$ BV right-continuous là hợp lệ. Cận $\int|r_k|\le\tfrac12R^2\varepsilon(\tau_0)+\log(1/p_{\min})\alpha(\tau_0)$ đúng. |
| Thm schedule | 2303–2361 | **Correct.** Đồng nhất thức bình phương đúng (tôi đã khai triển). Xử lý $|\mu_w|^2$ chỉ nhỏ trong $L^2$ là chặt. |
| Prop cfgatom (b), kể cả schedule $O((1-t)^{-\gamma})$ | 2420–2477 | **Correct.** Bất đẳng thức Gibbs $2t\zeta\cdot(a_i-m)\le2\varepsilon^2\log N$ và $\tfrac{d}{dt}(Y/\varepsilon^2)\le2w\log N/(t(1-t))$ đều kiểm lại được. |
| Thm composition (a)(b) | 2489–2576 | **Correct.** Dạng đóng của $F_w$, đạo hàm barrier $v-b'=\varepsilon^{-1}[-\gamma+\delta(\varepsilon^2/t+\varepsilon^3/t^2)]$, $F_w\ge\kappa\min\{s^3,1\}$, và barrier dưới $\theta$ đều đúng. |
| Prop composition-open | 2614–2656 | **Correct** (barrier hai phía, IFT). |
| Lemma offtie | 2707–2784 | **Correct.** Phân tích logit và các cận $O(e^{-c\beta})$ đúng. |
| Lemma lp | 2786–2849 | **Correct with gap** (W1). Cấu trúc LP đúng và dichotomy hợp lệ trong thời gian $\tau$, nhưng hằng số và claim $C^1$ chưa được chứng minh hay trích dẫn. Tính Lipschitz là đủ cho (b). |
| Thm spectral (a)(b)(c) | 2854–2939 | **(a)(b): correct modulo W1. (c): correct.** Tôi đã kiểm lại phương trình $\xi$: $d\xi/d\tau=\xi/t+\beta P_L(\bar m-z)$, dùng $\dot\beta=\beta(1+t)/t$. Các bước face condition, $\Psi$, excursion và Barbalat đều đúng. Đóng góp $\int|\mathcal R|^2d\sigma<\infty$ đúng. |
| Cor spectral-threshold, kể cả simplex | 2942–2981 | **Correct.** $C_{av}=(1-m^2)/(N-1)I$, $C_u=I/(N-1)$; khi $N=2$ thì trùng với $1/\sinh^2B$, sau khi đổi $B\to2B$. |
| Thm transfer | 2992–3027 | **Correct** (elementary). |
| Prop localtransfer | 3035–3077 | **Correct.** |
| Prop regular (a)(b) | 3092–3153 | **Correct.** |
| Thm relerr (a)–(d) | 3392–3422 | **Correct.** Riêng (b) có giả thiết nằm trên quỹ đạo (W6). |
| Prop trap | 3455–3468 | **Correct.** Có một lỗi trình bày nhỏ ở (iii) (W10). |
| Prop heun (a)–(e) | 3520–3547 | **Correct.** Tôi đã kiểm $\kappa,\theta$, $c(1)=1$ khi $r\ge1/2$, $\varrho_{\rm crit}$, biệt thức $(1-r)^2(r^2-6r+1)$, và các nghiệm thuộc $(0,1)$. |
| Stopping rules của Table composition | 3960–3969 | **Correct** (bất biến tiến). |

Tôi không kiểm chi tiết: Thm endpoint và Cor zerobw (chỉ đọc lướt Lemma wellposed, Lemma mixture-coupling, đều ổn); Thm risktransfer; Prop loss-no-certificate; Prop tgtnoise; Prop bottleneck (đọc lướt, ổn).

Tôi không tìm thấy lỗi toán học thực sự (incorrect) nào. Các vấn đề là gap trình bày hoặc trích dẫn (W1, W8), độ mạnh phát biểu (W6, W7), và diễn giải thực nghiệm (W2–W4, W9).

## Questions for authors

1. **Lemma lp:** các bạn có thể (i) viết tường minh hằng số co và (ii) xác nhận rằng chỉ cần đồ thị Lipschitz cho Thm spectral(b) không? Nếu muốn giữ $C^1$, xin cho trích dẫn chính xác (định lý stable manifold cho hệ có exponential dichotomy với exponent không bị chặn $a\beta(\tau)$).
2. **Thm relerr(c) trên EDM:** median của radial ratio theo $\sigma$ (không phải AUC) cho các mẫu off-atom là bao nhiêu? Nó có thực sự $\ge1-\delta_t$ với $\delta_t$ giảm đủ nhanh hay không?
3. **Stress test (W4):** pipeline RK4 log-time có tìm lại được $P_0\approx0.406$ ($B=1$, $w=2w_c$) trên composite không? Nếu không, kết quả "$6.1\times10^{-6}$" còn mang thông tin gì về Step 2?
4. **Thm spectral(c):** điều kiện "mọi profile hyperbolic" có generic theo $(p_k,c_k)$ không? Có ví dụ nào với profile không hyperbolic mà basin có độ đo dương không, tương tự trường hợp $w=w_c$ trong 1D (ở đó basin là null)?
5. **Thm schedule:** giả thiết BV có thực sự cần không? Một $w(t)\in[0,\bar w]$ dao động với biến phân vô hạn gần $t=1$ có thể phá Step 1 không? Một counterexample, hoặc một nhận xét rằng giả thiết BV chỉ là kỹ thuật, sẽ làm rõ độ sắc của định lý.
6. **Prop cfgatom(b)** với schedule $\gamma<2$: điều kiện được nói là "sufficient, not sharp". Có ví dụ nào với $\gamma\ge2$ mà quỹ đạo không collapse không?
7. **So sánh với liu2026geometric:** sau phép đổi biến, Thm 3.18 của họ với $\lambda>1$ và cùng support có trùng chính xác với Prop cfgatom(a) không? Nếu trùng, đóng góp ở đây có phải chính xác là việc bỏ giả thiết về limit set, cộng với kết luận a.e., không?

## Scores

- **Soundness: 3 (good).** Mọi chứng minh tôi kiểm đều đúng, và một số chỗ khó (Step 2 với $\Theta$ chỉ dương theo trung bình; năng lượng với hệ số có dấu BV; trường hợp không hyperbolic $w=w_c$) được xử lý cẩn thận. Bài chưa đạt 4 vì ba lý do: lemma LP chỉ là phác thảo và thiếu trích dẫn; một số diễn giải thực nghiệm vượt quá định lý (W2); và vài kiểm chứng số không thể thất bại theo thiết kế (W3, W4).
- **Presentation: 2 (fair).** Văn bản chính xác, nhưng bài quá dài và quá nhiều mệnh đề. Cơ chế `moveblock`/`ificlr` làm khó đối chiếu, và các sketch bị nén. Bảng roadmap và notation có giúp ích.
- **Contribution: 2 (fair).** Các phần thực sự mới là Lemma signedconv, counterexample composition với ngưỡng chính xác và phân loại phổ. Phần còn lại là ứng dụng chuẩn của Lyapunov/Liouville/Grönwall, hoặc là các nhận xét elementary mà tác giả tự thừa nhận.
- **Overall Rating: 6 (marginally above acceptance threshold).** Về mặt toán học, đây là một bài đúng và cẩn thận, trả lời một câu hỏi rõ ràng (can thiệp nào có thể rời khỏi support) với một ranh giới sắc (composition, $w_c=1/\sinh^2B$). Nhưng mức mới về kỹ thuật là vừa phải, và phần nối với mô hình thực (EDM, Heun) mang tính diễn giải nhiều hơn là kiểm chứng định lý.
- **Confidence: 4.** Tôi đã kiểm khoảng 20 chứng minh từng dòng. Tôi chưa kiểm phần risk-transfer và tgtnoise, và chưa chạy code.

## What would move my score up

1. Viết đầy đủ Lemma lp (hằng số co, tập decaying bằng tập điểm bất động) và thay claim $C^1$ bằng Lipschitz kèm trích dẫn (W1). Đây là điều kiện đủ để tôi nâng Soundness lên 4.
2. Sửa diễn giải EDM: báo cáo radial ratio theo $\sigma$, và bỏ cụm "non-landing regime of (c)" trừ khi có bằng chứng về giả thiết của (c) (W2). Trình bày "Heun bound never violated" như một sanity check (W3).
3. Thêm positive control (composite $w>w_c$) cho stress-test pipeline, hoặc chuyển sang integrator ổn định trong biến blow-up (W4). Dùng tiêu chí dừng bất biến tiến cho Table spectral (W9).
4. Viết lại phần đóng góp, tập trung vào Lemma signedconv, Thm composition và Thm spectral, kèm một so sánh định lượng với liu2026geometric Thm 3.18 / Rem 3.19 sau phép đổi biến (W5). Với 1–3 cộng thêm một remark về tính generic của giả thiết (c), tôi sẽ cân nhắc nâng điểm lên 8.

---

### Reviewer 2: Atomic Endpoints of Averaged and Guided Empirical Conditional Flows

*Góc nhìn: chuyên gia về memorization trong diffusion/flow matching (thực nghiệm trên EDM, Stable Diffusion). Báo cáo tập trung vào thiết kế thí nghiệm và việc các thí nghiệm có đỡ được claim hay không. Phần chứng minh chỉ được xem xét khi nó quyết định cách đọc thí nghiệm.*

## Summary

Bài báo xét exact empirical minimiser của conditional flow matching (CFM) trên một tập huấn luyện cố định, rồi hỏi liệu các "knob" phía sampler có đưa được endpoint ra khỏi tập huấn luyện hay không. Các knob gồm label noise (bandwidth h), label averaging, negative guidance, CFG với strength cố định hoặc theo schedule có bounded variation. Kết luận lý thuyết: các knob này chỉ reweight các training atom (Thm. endpoint, posmix, schedule; Table 1). Ngoại lệ duy nhất là composition "guidance áp lên label-averaged field", với threshold w > 1/sinh²B (Thm. composition, spectral). Với learned field, Thm. transfer (identifying label) và Thm. relerr (relative error ϱ < 1 thì landing) đặt nguyên nhân của off-atom samples vào field error ở cuối quá trình sampling. Prop. heun là phiên bản rời rạc cho Heun sampler.

Phần thực nghiệm gồm:
- EXP-1: linear-Gaussian d=2, N=200, 5 seed. Có thêm EXP-2/3.
- DDPM U-Net 35.75M cho CIFAR-10 inpainting, N=2000, 3 instance, h ∈ {0,4,5,6}.
- Label-smoothing tracking: slope 0.48 / −0.16.
- Learned guided label averaging trong d ≤ 2, kèm input asinh(tx/(1−t)²).
- Section 6.3, ba EDM model tự train (500/500/2000 ảnh CIFAR-10 class-balanced) cùng public EDM. Ba kết quả chính:
  - Swap sang exact field ở cuối cho thấy "image is chosen early, reached late".
  - Late contraction ∫(1−ϱ) d log(1/σ) tách on/off-atom, nhưng không tốt hơn baseline "khoảng cách từ D_θ tới ảnh train gần nhất".
  - Prop. heun "dự đoán" rằng 36/64 bước làm certificate đúng.

## Strengths

1. **Tách bạch exact field và learned field rõ ràng, với các phát biểu trung thực về giới hạn.** Abstract (dòng 118–119) và Section 6.3 (dòng 1319–1328) tự nói rằng "as a detector of memorisation, the error is no better than the distance to the nearest training image". Phụ lục C.4 (dòng 3346–3349) tự chỉ ra rằng final scaled error "are bookkeeping, not evidence". Mức tự phê bình này hiếm gặp và đáng ghi nhận.
2. **Thí nghiệm swap denoiser (dòng 1253–1262, Fig. edm-clocks(a)) có thiết kế hay.** Chạy network tới σ = s rồi chuyển sang exact field là một intervention có kiểm soát. Nó tách được "selection" (network chọn ảnh quanh σ ≈ 1–2) khỏi "landing". Tôi đã đối chiếu với `results/n3_followup_sub500_20261111/SWAP_SUMMARY.md`: các số 92.8/98.2/99.6% (sub500) và 31/56/90/99/100% (public, file `n3_followup_20261111`) khớp với bài.
3. **Có baseline mạnh và có bootstrap CI.** So sánh với baseline nearest-training-image distance d̂ đi kèm 95% stratified bootstrap CI cho chênh lệch có paired resampling (Table edm-anchor, `results/n3_robust_20261117/ROBUSTNESS.md`). Đây là chuẩn mực mà nhiều paper memorization không đạt.
4. **Có kiểm tra độ nhạy theo threshold off-atom 0.2/0.33/0.5** (dòng 3624–3626). Tôi đã kiểm tra trong ROBUSTNESS.md: số off-atom là 46/41/39, và dấu của mọi chênh lệch không đổi.
5. **Loại trừ solver error cho off-atom CIFAR samples một cách cẩn thận** (App. C.4, dòng 3313–3324): Euler-50 sang RK4 với cutoff 1e-3 sang 1e-4, exact field không có off-atom sample nào, và đo lại với cả 50k ảnh CIFAR.
6. **Báo cáo kết quả âm và failure.** Có 4/6 lần integration near-tie thất bại (dòng 1111–1115). Off-tie network bị bỏ (dòng 4097–4108). Variant `cfm_x_a` bị dừng. Slope −0.156 ở h=6 vẫn được báo cáo.
7. **Phần learned composition có ablation tách được yếu tố quyết định** (dòng 4079–4095): input, parametrisation (velocity hay data) và tie-centring, mỗi cấu hình 5 seed.

## Weaknesses

### W1 [Critical]: Việc on/off-atom "tách nhau" ở σ thấp gần như tautological, nên claim "separates memorised from other samples" trong abstract không mang thông tin về mechanism

- **Vấn đề.** Theo Prop. heun(a) (dòng 3489), output của sampler là x_K = D_{K−1}, tức chính denoiser output ở bước cuối. Nhãn off-atom được định nghĩa qua d₁/d₂ của x_K. Ở σ nhỏ, m* tiến về ảnh train gần nhất, nên e_t = |D − m*| ≈ |D − a| ≈ d₁ chính là tử số của tiêu chí nhãn. File `results/n3_edm_sub2000_20261117/N3_SUMMARY.md` ghi rõ "final error vs d1, max relative deviation: 0.0000".
- **ϱ_t → 1 là tính chất generic.** Với bất kỳ denoiser nào có D(x,σ) → x khi σ → 0 và x không trùng ảnh train, ta có e → |x − a| = n, do đó ϱ → 1. Vì vậy, việc "off-atom samples reach ϱ ≈ 1 from σ ≈ 0.14" (dòng 1304–1306) chỉ là hệ quả của việc sample không nằm trên ảnh train. Nó không phải bằng chứng độc lập cho "the non-landing regime of Theorem relerr(c)".
- **Hệ quả cho AUC.** Late contraction C lấy tích phân trên σ ∈ [0.002, 0.585], tức đúng vùng mà anchor-agreement ≈ 1.000 và AUC của mọi đặc trưng (kể cả baseline) ≈ 1.000 trên model 500 ảnh (ROBUSTNESS.md: tại σ ≤ 1.92 cả e, nn, ρ đều có AUC 0.999–1.000). Trên model 500 ảnh có ceiling effect, nên model này không phân biệt được phương pháp nào. Chỉ model 2000 ảnh (một seed duy nhất) mới có thông tin, và ở đó C hòa với baseline (0.983 so với 0.985).
- **Kiểm chứng của tôi về anchor.** "Predictive anchor gives the same AUC at every σ" (Table edm-rho caption, Table edm-anchor) cũng ít thông tin: ở σ = 19.4 anchor chỉ trùng 49.6% mà AUC vẫn giống hệt đến ba chữ số (0.519/0.519). Lý do là ở σ lớn n_t ≈ |x| ≫ khoảng cách giữa các ảnh, nên ϱ gần như không phụ thuộc anchor. Ở σ nhỏ thì anchor trùng 100%.
- **Tại sao quan trọng.** Abstract và Introduction (dòng 116–118, 174–176) trình bày việc tách nhóm như bằng chứng thực nghiệm cho Thm. relerr. Thực tế, ở vùng có tách biệt rõ, đại lượng đo được gần như là nhãn. Ở vùng dự báo thật sự (σ ≥ 3), ϱ kém hơn baseline (AUC 0.52–0.88 so với 0.69–0.96).
- **Đề xuất sửa.**
  - (a) Chỉ báo cáo AUC trên các σ mà ở đó off-atom label chưa được xác định bởi đặc trưng. Ví dụ, so với một "oracle" là off-atom label của ảnh D_θ(x_σ) chiếu tới endpoint, hoặc báo cáo AUC có điều kiện trên d̂.
  - (b) Báo cáo incremental value: hồi quy logistic off-atom ~ d̂ + C, rồi kiểm tra C có thêm thông tin sau khi đã có d̂ hay không (ΔAUC, likelihood ratio test).
  - (c) Sửa abstract: thay "separates memorised from other samples" bằng câu nói rõ đây là consistency check gần với định nghĩa nhãn.

### W2 [Major]: Kết quả "never violated" của Heun bound là kiểm tra số học, không phải kiểm định; "predicts when more steps make the guarantee hold" bị diễn đạt quá mức

- **Vấn đề.** Prop. heun bắt đầu bằng "Let D be any function" (dòng 3485). Phần (b) là một bất đẳng thức đúng cho mọi D khi ϱ, γ, ω được đo trên chính quỹ đạo. Việc "Along all 1500 trajectories the bound is never violated" (dòng 1337, Table edm-heun) vì thế chỉ kiểm tra cài đặt, không kiểm tra lý thuyết. Ngoài ra, vì ϱ_k được đo a posteriori ở cả x_k lẫn x̃_k, certificate cũng không có tính dự báo.
- **Dự đoán thật sự quá yếu.** "Dự đoán" theo số bước có hai phần. Phần thứ nhất: với 36/64 bước, mọi r_k ≥ 1/2 thì c_k < 1. Đây là số học trên schedule cộng với giả thiết ϱ < 1. Phần thứ hai: off-atom fraction không đổi (4.1 → 4.0 → 3.9%). Điều này đã được biết từ việc 18-step Heun (35 NFE) gần hội tụ cho EDM CIFAR-10 (FID bão hòa, Karras et al. 2022). Không có kịch bản nào mà lý thuyết dự đoán một thay đổi quan sát được rồi thay đổi đó xảy ra.
- **Tại sao quan trọng.** Abstract (dòng 117–118) và Conclusion (dòng 1393–1394, "which also tells how many sampler steps the guarantee needs") đọc như một dự đoán có thể falsify được về hành vi sampler.
- **Đề xuất sửa.** Thiết kế một thí nghiệm mà Prop. heun dự đoán outcome thay đổi:
  - Dùng schedule thô (ví dụ 8–10 bước, hoặc ρ_schedule = 3 thay vì 7, sao cho r_k < 3 − 2√2 ≈ 0.17 ở các bước cuối, tức vùng overshoot của Prop. heun(d)).
  - Dự đoán trước sample nào sẽ chuyển từ on sang off-atom dựa trên ϱ đo ở schedule 18 bước, rồi kiểm tra precision/recall.
  - Hoặc so sánh Euler và Heun cùng NFE.
  - Đồng thời đổi chữ "predicts" thành "certifies".

### W3 [Major]: Thí nghiệm "exact field replacement" (swap) diễn giải nửa đầu bị tautological; nửa thông tin nhất lại không được báo cáo trong bài

- **Vấn đề.** "Replacing the field on the last 2% of the time turns no memorisation into complete memorisation" (dòng 1255–1257) suy ra trực tiếp từ lý thuyết: exact field từ bất kỳ trạng thái nào cũng kết thúc trên một atom (Prop. collapse/uncond với class prior). Đây là tính chất của exact field, không nói gì về network. Phần thông tin là "=L" (ảnh nào được chọn), cũng là điều đã được đặt tên trong literature: speciation/collapse time (Biroli et al. 2024), symmetry breaking (Raya & Ambrogioni 2023), phase transition (Sclocchi et al. 2025). Các công trình này không được thảo luận (xem Missing references).
- **Kết quả bị bỏ ngoài bài.** File `results/n3_followup_20261111/SWAP_SUMMARY.md` có chiều ngược lại "exact→net": exact field cho σ > s, network cho σ ≤ s.
  - Public model: off-atom 95.6% tại s = 1, nhưng chỉ 0.2% tại s = 0.1.
  - d₁ giảm gần tuyến tính theo s (2.57/1.37/0.61 tại s = 0.1/0.05/0.02). Network gần như "giữ nguyên" độ lệch tại thời điểm giao (μ ≈ 1).
  - Đây là bằng chứng trực tiếp và mạnh hơn cho luận điểm "landing decided late by the learned field", và nó định lượng được thang σ mà network bắt đầu không co. Kết quả này không xuất hiện trong bài.
- **Lưu ý thêm.** Swap dùng 500 sample, còn mọi kết quả khác dùng 1000. Phiên bản public dùng 500 sample, trong khi App. C.5 ghi "50 or 20 per class for the public model".
- **Đề xuất sửa.** Đưa thí nghiệm exact→net vào main text với cả ba model. Thêm một swap "net→net' " giữa hai network khác seed: tiếp quản quỹ đạo của model 500-ảnh-seed-0 bằng model seed-1 ở σ = s. Thí nghiệm này tách được việc "late field decides landing" là tính chất của network nói chung hay của model cụ thể.

### W4 [Major]: Mâu thuẫn giữa practical message "(i) The knobs are not privacy mitigations" và dữ liệu của chính bài báo

- **Vấn đề.** Dòng 227–233 và Ethics statement khẳng định label noise, label averaging, guidance "are not privacy mitigations". Nhưng trên U-Net CIFAR-10 trained (App. exp4, dòng 3870), on-atom fraction giảm đơn điệu theo h: 1.000, 0.829, 0.717, 0.620 tại h = 0, 4, 5, 6. Off-atom tăng từ 0.17 lên 0.30 (App. C.4). Như vậy, với model mà practitioner thực sự có, label noise *có* giảm replication, thông qua learned-field error mà bài báo coi là "nguồn duy nhất". Đây cũng là kết quả thực nghiệm của Somepalli et al. 2023b (caption randomization, Gaussian noise trên text embedding). Bài này có trong `refs.bib` (key `somepalli2023copying`) nhưng **không được trích dẫn** trong main.tex.
- **Tại sao quan trọng.** Đọc theo nghĩa practitioner, (i) gây hiểu lầm. Phát biểu chỉ đúng tại exact optimum, trạng thái mà model quy mô thực tế không đạt (chính bài cũng nói vậy ở (iv)). Một practitioner đọc abstract sẽ kết luận "đừng dùng conditioning augmentation chống memorization", trái với bằng chứng thực nghiệm, kể cả của bài này.
- **Đề xuất sửa.** Viết lại (i) thành: "at the exact optimum ... ; in trained networks these knobs change the off-atom fraction only through learned-field error, which we measure in App. C.4". Bổ sung một bảng "knob → off-atom fraction" trên EDM sub500 với h ∈ {0, 0.1, 0.4} (label noise trên one-hot), label dropout và CFG (xem W5). Đây là thí nghiệm practitioner thực sự cần.

### W5 [Major]: Không có thí nghiệm CFG/guidance schedule nào trên model ảnh thật, dù guidance là một nửa của title và lý thuyết

- **Vấn đề.** Các Thm. cfgatom, schedule, composition chỉ được kiểm tra trên exact field (d ≤ 8, N = 12) và learned field trong d ≤ 2. Phần CIFAR-10 composition (dòng 1132–1137) dùng *exact* composite. Model EDM CIFAR-10 công khai không train với label dropout, nên không có CFG. Các knob trong literature mitigation thực tế đều là guidance trên text-to-image: negative/delayed guidance (Jain et al. 2025), Anti-Memorization Guidance (Chen et al. CVPR 2024), prompt-embedding perturbation (Wen et al. ICLR 2024), cross-attention reweighting (Ren et al. ECCV 2024). Bài không có thí nghiệm nào trên latent diffusion, text-conditioning hay Stable Diffusion.
- **Đề xuất sửa (khả thi, chi phí thấp).**
  - Train lại EDM sub500/sub2000 với class dropout 0.1, mất khoảng chi phí của một model đã có.
  - Sample với w ∈ {−0.5, 0, 1, 3, 7}, guidance interval (Kynkäänniemi 2024) và "delayed guidance" kiểu Jain 2025.
  - Báo cáo off-atom fraction, image identity so với w = 0, và ϱ_t.
  - Lý thuyết đưa ra dự đoán falsifiable: tại exact field mọi w đều atomic. Câu hỏi là với learned field, guidance có làm ϱ_t cuối tăng hay giảm.
  - Nếu có tài nguyên, thêm một kiểm tra nhỏ trên SD-1.x với bộ prompt memorized của Webster 2023 / Wen 2024. Chỉ cần đo ϱ (không cần exact field) thông qua proxy là khoảng cách tới ảnh train đã biết.

### W6 [Major]: Kích thước mẫu và confound ở phần EDM

- **Số model.** Kết luận chính dựa trên 3 model tự train: 2 ở N = 500 (đều memorize khoảng 96%, có ceiling effect) và 1 ở N = 2000 (model duy nhất cân bằng on/off, nơi mọi so sánh có thông tin, nhưng chỉ một seed). Phát biểu "the second gives the same conclusions" chỉ về model 500 ảnh, vốn có ceiling.
- **Confound giữa instance và optimisation.** Seed 0/1 đổi cả subset lẫn training seed (App. C.5, dòng 3554–3556). Bài thừa nhận điều tương tự cho CIFAR inpainting (dòng 1367–1368) và EXP-1 (dòng 1013), nhưng không tách được.
- **Confound giữa public và subset model.** Public model được train *với* augmentation (EDM mặc định augment_p = 0.12), trên khoảng 200 Mimg, với N = 50000. Subset model *không* augmentation, 10 Mimg. Augmentation là một yếu tố memorization đã được biết rõ, vậy mà Fig. intuition so sánh trực tiếp hai model này.
- **Ít positive.** Có 41 off-atom/1000 sample, nên các CI cho AUC ở σ cao khá rộng (ví dụ [0.428, 0.608]).
- **Public model** chỉ có 200 sample cho phần ϱ (Q_SUMMARY: n = 200) và 500 cho swap.
- **Đề xuất sửa.**
  - Một lưới N ∈ {500, 1000, 2000, 5000} × 3 seed, có thiết kế tách subset seed khỏi training seed (2×2 factorial ở ít nhất một N).
  - Thêm một model 2000 ảnh *có* augmentation.
  - Báo cáo AUC/ΔAUC so với baseline cho từng ô.
  - Cách làm này cũng cho phép kiểm tra trực tiếp quan hệ giữa off-atom fraction và N mà Gu et al. 2023 và Bonnaire et al. 2025 mô tả.

### W7 [Major]: CIFAR-10 inpainting ở h = 0 là một bài toán lookup; claim "predictable record" (ii) chưa được kiểm tra ở image scale

- **Vấn đề.** Label là top-half của chính ảnh train (k = 1536). Ở h = 0 với training condition, việc "generated mean identifies the correct training image at 48/48 conditions" (dòng 1038–1039) gần như hiển nhiên, vì nearest neighbour trong không gian label đã xác định ảnh. Không có held-out condition (test-set top halves), trong khi EXP-1 có 8 held-out condition.
- **Claim (ii) chưa được kiểm tra.** Claim (ii) (dòng 234–240) nói auditor có thể xếp hạng record theo p_i^(h)(y). Thí nghiệm duy nhất là trùng ảnh per-source (23–67%), nhưng lý thuyết dự đoán *phân phối* trên các ảnh, không dự đoán per-source.
- **Đề xuất sửa.**
  - Với CIFAR-10 test top-halves (y không thuộc tập train) ở h = 4, 5, 6, sample M = 256 cho mỗi condition và đếm tần suất từng ảnh train được trả về.
  - So sánh với p_i^(h)(y) bằng total variation hoặc top-k overlap, và rank correlation (Spearman) giữa tần suất thực nghiệm và p_i^(h).
  - Đây là test trực tiếp của Thm. endpoint trên learned model và là kết quả có giá trị nhất cho auditor.

### W8 [Major]: Kernel tracking ở image scale thực chất bác bỏ reference; cần được trình bày như vậy

- **Vấn đề.** Table cifarddpm cho thấy:
  - h = 4: slope 0.481 (R² 0.785), median ratio 5.30 [2.24, 7.45].
  - h = 6: slope −0.156 (R² 0.135), trên dải reference chỉ 0.74 decade.
  - Exact field dự đoán slope 1 và ratio 1.
  - Ở h = 6, R² 0.135 trên dải 0.74 decade nghĩa là test thiếu power. Vì vậy "−0.16" không nên được đặt ngang với "0.48" như hai "regime" (Fig. kernel-tracking, dòng 1076–1082).
- **Số liệu thống kê.** Chỉ có 3 instance, độ lệch chuẩn là "population SD" (ddof = 0, dòng 1014) với 5 seed (EXP-1). Với n = 3 hoặc 5, ddof = 0 làm thu hẹp sai số khoảng 10–20%.
- **Đề xuất sửa.** Báo cáo sample SD hoặc t-interval. Chọn bandwidth sao cho dải reference đủ rộng, ví dụ chọn condition theo tầng của n_eff. Ghi rõ trong abstract rằng ở image scale reference sai theo hệ số khoảng 5 ở h = 4.

### W9 [Minor–Major]: Learned guided label averaging: input asinh đặt tâm tại tie đã biết là một oracle feature, không phải test về khả năng học

- Network chỉ tái tạo basin khi được cho tọa độ asinh(tx/(1−t)²) đặt tâm tại z = 0 đã biết (dòng 1146–1148). Đặt tâm lệch (0.3, 0.2) thì midpoint rỗng (dòng 4100–4104). Một input mỗi vertex thì không đánh giá được (dòng 4105–4108).
- Đây là test về *representability* với một oracle feature, không phải bằng chứng rằng "the distinction can be tested" (dòng 1400) trong model thực tế. Bài đã gọi composition là "boundary marker", điều này hợp lý. Tuy vậy, tôi đề nghị:
  - (a) Đổi ngôn từ thành "an oracle coordinate at the known tie".
  - (b) Thêm một baseline: network có Fourier features / time-embedding dạng log(1−t) chuẩn (như EDM c_noise = ¼ log σ), không biết vị trí tie. Đây là parametrisation practitioner thực sự dùng. Nếu nó cũng thất bại thì kết luận "standard networks do not reproduce it" mới mạnh.
  - (c) Thử ít nhất d = 8 hoặc d = 16, vì learned composition hiện chỉ có d ≤ 2.

### W10 [Minor]: Tiêu chí off-atom trong pixel-space ℓ2

Tỉ lệ 1/3 (Yoon et al. 2023; Carlini et al. 2023 dùng biến thể tương tự) là hợp lý cho CIFAR 32×32. Tuy nhiên, literature hiện dùng thêm SSCD/DINOv2 (Somepalli 2023a; Stein et al. 2023) để bắt near-copy có dịch chuyển nhỏ. Robustness chỉ được kiểm tra trên model 500 ảnh (ceiling). Đề xuất: lặp lại robustness 0.2/0.5 trên model 2000 ảnh, và thêm một tiêu chí perceptual (SSCD > 0.5) để kiểm tra nhãn off-atom không chỉ là artefact của ℓ2.

### W11 [Minor]: Phạm vi tổng quát

Phạm vi gồm một dataset (CIFAR-10, 32×32), chỉ class-conditional, chỉ deterministic Heun (không có EDM stochastic churn, không có DDPM ancestral sampler), không có latent diffusion, không có text-to-image. Phần EDM là VP diffusion được reparametrise sang CFM, không phải một flow-matching model được train bằng CFM loss ở image scale (ví dụ SiT, rectified flow). Đề xuất: thêm ít nhất một model train bằng CFM loss (rectified flow U-Net trên cùng subset) và một sampler stochastic. Thm. relerr là cho ODE, nên cần nói rõ trường hợp SDE.

### W12 [Minor]: Presentation của phần thực nghiệm

- Abstract dài và dày đặc (khoảng 30 dòng). Trộn 6–7 claim khác nhau, kể cả các con số như "4 and 50%".
- Section 6.3 phụ thuộc mạnh vào App. C.5. Các con số quan trọng (ví dụ exact→net) nằm ngoài bài.
- Kết quả trên public model với 20 hay 50 sample/class được chọn khác nhau giữa các run (dòng 3558) mà không nói rõ run nào dùng số nào.

### W13 [Minor, ghi chú cho AC về disclosure]

Trong mã nguồn LaTeX có comment cho biết bản nháp chứng minh của Thm. relerr, Prop. trap, Prop. heun "came from model-based solver runs" (dòng 899–900, 1440–1442, 3373–3374). Đoạn "Use of large language models" ở bản ICLR (dòng 1443–1447) lại ghi "The authors wrote and verified all proofs". Tôi coi đây là dữ liệu trong source, không phải lời khẳng định của tác giả gửi reviewer. Tuy vậy, nếu comment phản ánh đúng quy trình thì disclosure cần được làm cho khớp theo chính sách LLM của ICLR. Việc này không ảnh hưởng đến đánh giá kỹ thuật của tôi.

## Questions for authors

1. Sau khi đã kiểm soát d̂ (khoảng cách D_θ tới ảnh train gần nhất), late contraction C có thêm thông tin dự báo nào không (ΔAUC hoặc LRT trong hồi quy logistic) trên model 2000 ảnh? Nếu không, "mechanism" mà C cung cấp khác gì việc nói rằng "denoiser output đã gần ảnh train"?
2. Có thể đưa ra một kịch bản mà Prop. heun dự đoán outcome *thay đổi* hay không (schedule thô, r_k < 3 − 2√2), và báo cáo precision/recall của dự đoán đó?
3. Vì sao kết quả swap "exact→net" (có trong `n3_followup_*`) không được đưa vào bài? Nó có vẻ là bằng chứng trực tiếp nhất cho luận điểm "landing decided late by the learned field".
4. Ở h = 4, 5, 6 trên CIFAR inpainting, với *held-out* top-half, tần suất ảnh train được trả về có tương quan với p_i^(h)(y) không?
5. Subset model không augmentation trong khi public model có augmentation. Có model sub2000 có augmentation nào để tách hai yếu tố này không?
6. Với model train có class dropout, CFG w > 0 làm ϱ_t cuối và off-atom fraction thay đổi theo hướng nào? Lý thuyết của các bạn dự đoán gì cho learned field?
7. Trong learned composition, một network có time embedding chuẩn theo log(1−t) (không biết vị trí tie) có tái tạo basin không?
8. App. C.5 ghi "50 or 20 per class for the public model". Run nào dùng số nào, và số liệu ở Table edm-rho cho public model dựa trên bao nhiêu sample?
9. "Selection by σ ≈ 1" có khác gì về bản chất so với speciation time của Biroli et al. 2024? Có thể so sánh σ selection đo được với công thức speciation time tính từ phổ covariance của subset không?

## Missing references

Tôi tự tin về các tài liệu sau (đều liên quan trực tiếp):

- **Somepalli, Singla, Goldblum, Geiping, Goldstein. "Understanding and Mitigating Copying in Diffusion Models", NeurIPS 2023.** Đã có trong `refs.bib` (`somepalli2023copying`) nhưng không được cite. Đây là bằng chứng thực nghiệm trung tâm rằng label/caption noise giảm copying (liên quan W4).
- **Biroli, Bonnaire, de Bortoli, Mézard. "Dynamical Regimes of Diffusion Models", Nature Communications 2024.** Đã có trong `refs.bib` (`biroli2024dynamical`) nhưng không được cite. Speciation/collapse time liên quan trực tiếp đến "image chosen early, reached late".
- **Wen, Liu, Chen, Lyu. "Detecting, Explaining, and Mitigating Memorization in Diffusion Models", ICLR 2024.** Detector dựa trên magnitude của text-conditional prediction và mitigation qua prompt embedding.
- **Chen, Liu, Xu. "Towards Memorization-Free Diffusion Models", CVPR 2024** (Anti-Memorization Guidance). Một mitigation dựa trên guidance, trực tiếp liên quan đến Thm. cfgatom/schedule.
- **Ren et al. "Unveiling and Mitigating Memorization in Text-to-Image Diffusion Models through Cross Attention", ECCV 2024.**
- **Hintersdorf et al. "Finding NeMo: Localizing Neurons Responsible for Memorization in Diffusion Models", NeurIPS 2024.**
- **Daras et al. "Ambient Diffusion: Learning Clean Distributions from Corrupted Data", NeurIPS 2023.** Một mitigation thay đổi training data, cùng tinh thần "support change" của Prop. tgtnoise.
- **Aithal, Maini, Lipton, Kolter. "Understanding Hallucinations in Diffusion Models through Mode Interpolation", NeurIPS 2024.** Rất gần với "blends/circumcentres" của Thm. composition.
- **Raya & Ambrogioni. "Spontaneous Symmetry Breaking in Generative Diffusion Models", NeurIPS 2023.**
- **Sclocchi, Favero, Wyart. "A phase transition in diffusion models reveals the hierarchical nature of data", PNAS 2025.**
- **Zhang, Zhou, Wang, Qu et al. "The Emergence of Reproducibility and Generalizability in Diffusion Models", ICML 2024.**
- **Li, Dai, Qu. "Understanding Generalizability of Diffusion Models Requires Rethinking the Hidden Gaussian Structure", NeurIPS 2024.**
- **Wang & Vastola. "The Unreasonable Effectiveness of Gaussian Score Approximation for Diffusion Models and its Applications", TMLR 2024.**
- **Bonnaire, Urfin, Biroli, Mézard. "Why Diffusion Models Don't Memorize: The Role of Implicit Dynamical Regularization in Training", NeurIPS 2025.** Thời điểm memorization tỉ lệ với N; liên quan trực tiếp đến EXP-1 (collapse sau khoảng 10⁴ iteration) và EDM theo N.
- **Dockhorn, Cao, Vahdat, Kreis. "Differentially Private Diffusion Models", TMLR 2023.** Bài nhắc đến DP ở (i) nhưng chỉ cite Dwork & Roth.
- **Stein et al. "Exposing flaws of generative model evaluation metrics and their unfair treatment of diffusion models", NeurIPS 2023.** Liên quan đến metric memorization/novelty (W10).

Cần kiểm tra:
- Ross et al. "A Geometric Framework for Understanding Memorization in Generative Models", ICLR 2025.
- Vastola. "Generalization through variance: how noise shapes inductive biases in diffusion models", ICLR 2025.
- Webster. "A Reproducible Extraction of Training Images from Diffusion Models", arXiv 2023.
- Chen et al. "Exploring Local Memorization in Diffusion Models via Bright Ending Attention", ICLR 2025.
- Achilli et al. "Losing dimensions: Geometric memorization in generative diffusion", 2024.
- Pham et al. "Memorization to Generalization: Emergence of Diffusion Models from Associative Memory", 2025.
- Lukoianov et al. "Locality in Image Diffusion Models Emerges from Data Statistics", 2025.
- Wang et al. "Replication in Visual Diffusion Models: A Survey and Outlook", 2024.

Một số cite năm 2026 trong related work (dodson2026calm, lopezamado2026modes, jaziri2026spectral, verma2026early, li2026memory, physicscfm2026) là arXiv mới. Tôi không xác minh được nội dung, nên ở đây chỉ ghi nhận chúng mà không đánh giá.

## Scores

- **Soundness: 2/4.** Lý thuyết (trong phạm vi tôi đã kiểm tra: Thm. relerr, Prop. trap, Prop. heun ở App. D) có vẻ đúng và được phát biểu cẩn thận. Phần thực nghiệm image-scale lại có vấn đề về thiết kế:
  - Tách nhóm ở σ thấp gần như tautological (W1).
  - "Bound never violated" là identity (W2).
  - Swap có nửa tautological (W3).
  - Kích thước mẫu và confound (W6).
  - Claim (ii) chưa được kiểm tra (W7).
- **Presentation: 2/4.** Viết chính xác và trung thực về giới hạn. Nhưng mật độ rất cao: abstract quá tải, nhiều kết quả quan trọng nằm trong appendix hoặc chỉ có trong artefact. Giọng điệu ở abstract và các mục "What this means in practice" mạnh hơn bằng chứng.
- **Contribution: 2/4.** Cộng đồng memorization đã ngầm hiểu kết luận "các knob phía sampler chỉ reweight atom tại exact optimum" (closed-form/empirical-optimal-denoiser literature). Giá trị mới nằm ở chứng minh a.s. cho guidance/schedule và ở composition threshold, nhưng chính composition lại được tác giả gọi là "boundary marker" không xuất hiện trong model thực. Phần thực nghiệm EDM không cho thấy giá trị vượt baseline đơn giản d̂.
- **Overall Rating: 5 (marginally below the acceptance threshold).** Bài có lõi lý thuyết sạch và tự phê bình trung thực. Tuy nhiên, các claim thực nghiệm trong abstract ("separates memorised from other samples", "predicts when more steps make the guarantee hold") đang được calibrate quá tay so với bằng chứng. Thông điệp practical (i) mâu thuẫn với dữ liệu của chính bài (W4). Bài cũng thiếu thí nghiệm nào về guidance trên model ảnh thật, dù guidance là trọng tâm của title. Nếu W1–W5 được xử lý, tôi sẵn sàng nâng lên 6.
- **Confidence: 4/5.** Tôi quen với setup EDM/CIFAR memorization và đã đối chiếu một số số liệu với artefact (`n3_robust_20261117/ROBUSTNESS.md`, `n3_edm_sub2000_20261117/N3_SUMMARY.md`, `n3_followup_*/SWAP_SUMMARY.md`, `n3_rho_20261117/Q_SUMMARY.md`). Tôi không kiểm tra hết các chứng minh trong App. B (spectral classification).

## What would move my score up

1. **(Đủ để lên 6)** Báo cáo incremental value của C/ϱ so với d̂ (W1). Thay "predicts" bằng "certifies" và thêm một thí nghiệm schedule thô mà Prop. heun dự đoán outcome thay đổi (W2). Đưa kết quả exact→net vào main text (W3). Viết lại practical message (i) cho khớp với on-atom fraction 1.00 → 0.62 theo h của chính bài (W4).
2. **(Lên 6 vững chắc, có thể 8)** Thêm một thí nghiệm CFG/guidance-interval/negative guidance trên EDM được train với class dropout ở N ∈ {500, 2000}, báo cáo off-atom fraction và ϱ_t (W5). Mở rộng lên ít nhất 3 seed × 3 giá trị N có tách subset seed khỏi training seed, cộng một model có augmentation (W6).
3. Kiểm tra claim (ii) trên held-out top-halves: tần suất trả về so với p_i^(h)(y) (W7).
4. Bổ sung related work 2023–2025 về mitigation (Somepalli 2023b, Wen 2024, Chen 2024 AMG, Ren 2024, Daras 2023) và dynamical regimes (Biroli 2024, Raya & Ambrogioni 2023, Sclocchi 2025, Bonnaire 2025, Aithal 2024). Định vị rõ đóng góp so với các công trình này.

---

### Review — Reviewer 3 (góc nhìn privacy + nonparametric statistics)

**Paper:** Atomic Endpoints of Averaged and Guided Empirical Conditional Flows

---

## Summary

Bài báo nghiên cứu population minimiser của conditional flow-matching objective trên một training set cố định (exact empirical field) và hỏi: các "knob" phía sampler/learner — Gaussian label noise (bandwidth h), label averaging, classifier-free guidance (hằng hoặc schedule bị chặn, bounded variation), negative guidance — có đưa endpoint ra khỏi tập training atoms hay không. Kết quả chính:

1. Với h>0, endpoint law là Nadaraya–Watson mixture `Σ_i p_i^(h)(y) δ_{x^i}` (Thm. 3.3), kèm một W2 floor không phụ thuộc h (Prop. 3.5, eq. w2floor).
2. Positive field mixtures (bao gồm label averaging, guidance w∈[-1,0)) và guidance w≥0 hằng hoặc theo schedule BV đều kết thúc trên một atom với hầu hết initial point (Thm. 4.1, Prop. 4.4, Thm. 4.6), qua một proof template chung (kinetic energy + volume expansion).
3. Composition "guidance sau label averaging" có thể tạo endpoint tại circumcentre (blend) với xác suất dương; ngưỡng chính xác `w > 1/sinh²B` cho hai atom (Thm. 4.7), tổng quát hoá bằng spectral criterion (Thm. 4.9).
4. Cho learned field: Thm. 5.1 (transfer, identifying label) chặn khoảng cách endpoint bởi `limsup (1-t)|Δ|`; Thm. 5.2 (relative error ϱ<1 ⇒ landing, ở mọi label), có phiên bản rời rạc cho Heun sampler (Prop. heun).
5. Thực nghiệm: EXP-1 (d=2), CIFAR-10 inpainting với U-Net 35.75M, và ba EDM class-conditional model trên subset CIFAR-10 (500/500/2000 ảnh) + public model; tác giả cho thấy ảnh được "chọn" sớm (σ≈1), còn landing được quyết định muộn bởi late contraction `∫(1-ϱ_t) d log(1/σ)`, và thừa nhận rằng như một detector, field error không tốt hơn khoảng cách từ D_θ tới training image gần nhất.

Đoạn "What this means in practice" (l.226–256) và Ethics statement (l.1426–1436) rút ra bốn hệ quả thực tiễn: (i) knobs không phải privacy mitigation, (ii) record nào được trả về là predictable, (iii) monitor late-time field error thay vì loss, (iv) phát biểu chỉ về support ở N cố định.

Đánh giá tổng quát từ góc độ của tôi: phần lý thuyết về exact field cẩn thận và trung thực về phạm vi; nhưng phần diễn giải privacy dựa trên một khái niệm leakage theo *support* ("có nằm trên training atom hay không") vốn yếu hơn nhiều so với các khái niệm chuẩn trong privacy (DP, membership inference, extraction theo khoảng cách), threat model không được nêu, và phần lớn nền tảng nonparametric (kernel conditional density estimation, smoothed bootstrap, quantization) chỉ được credit một phần. Phần thống kê thực nghiệm nhìn chung trung thực nhưng có vài lựa chọn (population std ở n=5, AUC có thành phần tautological, ngưỡng chọn post hoc) cần chỉnh.

---

## Strengths

**S1. Phân tách rõ "which" vs "whether".** Thông điệp trung tâm — label noise/guidance quyết định *training example nào* được trả về chứ không phải *có trả về hay không* (abstract l.104–105; Table 1, l.258–276) — là một framing hữu ích cho cộng đồng privacy, nơi nhiều người vẫn ngầm coi conditioning augmentation hay negative guidance là "giảm memorisation" (Jain et al. 2025, được cite l.153). Bảng 1 là một bản tóm tắt gọn, dễ dùng cho auditor.

**S2. Endpoint law dạng đóng ở h>0 (Thm. 3.3, l.443–450).** Việc `p_i^(h)(y)` chỉ phụ thuộc vào labels (l.437–438) là một quan sát có giá trị thực tiễn trực tiếp: ở exact optimum, xác suất trả về record i được tính chỉ từ label set và h. Tác giả không overclaim tính mới: l.304–307 nói rõ đây là "a reference, not a new identity", credit Nadaraya (1964)/Watson (1964) (l.425) và Baptista et al.

**S3. Trung thực về giới hạn và negative results.** Hiếm thấy một bài tự viết rằng đại lượng lý thuyết của mình "no better than the distance to the nearest training image" như một detector (abstract l.118–119; §6.4 l.1319–1328), rằng giá trị cuối của scaled error là "bookkeeping, not evidence" (App. measured-transfer l.3346–3349), và rằng certificate B_T trùng với RMS distance là "the identity of the theorem, not an independent prediction" (l.3310–3311). Composition được trình bày là "boundary marker, not a practical mechanism" (l.123–126, l.1394–1397). Đây là chuẩn mực tốt.

**S4. Phân biệt exact optimum vs trained model trong claim (ii).** l.237–240 tự giới hạn: trên U-Net retrained, learned và exact field chỉ trả về cùng một ảnh cho 23–67% on-atom samples. Đây là cách scope đúng.

**S5. Kết quả "selection sớm, landing muộn" trên EDM (§6.4, l.1253–1262; Fig. edm-clocks).** Thí nghiệm swap (chạy network tới σ=s rồi exact field) cho thấy thay field ở 2% thời gian cuối biến public model từ 0% thành 100% memorisation. Với một privacy researcher, đây là bằng chứng cơ chế rất cụ thể rằng "không copy" của model lớn nằm ở late-time field error, và nó gắn với kết quả của Dodson et al. về medium-noise band.

**S6. Dự đoán kiểm chứng được cho Heun sampler (l.1330–1345, Tab. edm-steps).** Prop. heun đưa ra dự đoán trước (thêm bước làm r_k ≥ 1/2 thì certificate giữ mà outcome không đổi) và dữ liệu xác nhận (0% → 99.5% certified, off-atom 4.1/4.0/3.9%). Đây là kiểu falsifiable prediction ít gặp trong mảng này.

**S7. Báo cáo uncertainty có nỗ lực:** stratified bootstrap 1000 resamples, paired cho differences (l.3621–3622); kiểm tra robustness với ngưỡng off-atom 0.2/0.5 (l.3625–3626); ghi chú rõ energy statistic "has no null subtraction or equivalence threshold" và "descriptive values, not hypothesis tests" (l.1210, l.1227–1228); ghi rõ population std (l.3749–3750).

---

## Weaknesses

### W1 [Major] — Khái niệm "leakage" dựa trên support không phải là một khái niệm privacy; claim (i) và giải pháp endpoint noise bị diễn giải quá mức

- **What/where:** l.227–233 và Ethics l.1428–1436: "Changing the support needs a mechanism such as endpoint noise"; App. noise l.3687: "a remedy must move the support". Toàn bộ phân loại "on-atom/off-atom" dùng tiêu chí tỉ số khoảng cách 1/3 (l.1246–1247, l.3868–3870).
- **Why it matters:** Trong privacy, việc output có *đúng bằng* một training record hay không không phải là tiêu chí. Endpoint noise ρ>0 cho output `x^I + ρξ` (Prop. tgtnoise, eq. tgtendpoint) — đó chính là một Gaussian mechanism áp lên *một* record được chọn. Với ρ nhỏ so với khoảng cách giữa các atoms, một adversary biết candidate set nhận dạng nguồn gần như chắc chắn (MAP theo khoảng cách); với ρ√d lớn (d=3072), tiêu chí 1/3 sẽ gắn nhãn "off-atom" trong khi sample vẫn là record cộng nhiễu isotropic — tức support-based audit sẽ báo sai "không leak". Ngược lại, để đạt (ε,δ)-DP cho cơ chế "release một record + Gaussian", ρ phải tỉ lệ với đường kính dữ liệu (sensitivity khi thay một record là toàn bộ record), khiến sample gần như vô dụng; đây là bài học đã biết của "one posterior sample" mechanisms (Wang, Fienberg & Smola 2015; Dimitrakakis et al. 2014). Câu "carries no formal privacy guarantee unless calibrated" (l.232–233) là đúng nhưng quá mỏng — nó vẫn ngầm gợi ý endpoint noise là hướng "remedy" (l.3687).
- **Fix:** (a) Thêm một định nghĩa/threat model tường minh: leakage ở đây = "output trùng/ hội tụ về training record"; nói rõ đây là điều kiện *đủ* để leak chứ không phải điều kiện cần. (b) Sửa l.3687 và l.231: endpoint noise thay đổi support nhưng *không* tự nó giảm identifiability; với ρ nhỏ, record nguồn vẫn khôi phục được. (c) Một đoạn ngắn: tính toán đơn giản cho thấy ρ cần cho DP của mechanism `x^I+ρξ` (ít nhất cho Gaussian mechanism ở sensitivity = diam), để người đọc thấy khoảng cách giữa "smoothed bootstrap" và DP. (d) Liên hệ với DP training (DP-SGD, Abadi et al. 2016; Dockhorn et al. 2023; Ghalebikesabi et al. 2023) như lối duy nhất có guarantee — câu hỏi tự nhiên của privacy reader là "vậy DP-SGD ở exact-optimum-view thì sao?" (DP-SGD không hội tụ về exact field, nên toàn bộ bài thuộc vùng "learned-field error" — đáng nói ra).

### W2 [Major] — Claim (i) "the knobs are not privacy mitigations" mâu thuẫn một phần với chính dữ liệu của tác giả trên trained models; cần scope lại

- **What/where:** l.227–230, Conclusion l.1385–1388 ("none of them protects training data"), Ethics l.1429–1432. Nhưng App. measured-transfer l.3317–3320, 3341–3342: trên U-Net CIFAR-10 trained, off-atom fraction *tăng theo h*: 0.158/0.212/0.254 (h=4,5,6) so với 0 ở h=0; §6.1 l.1079–1080: 38% off-atom ở h=6.
- **Why it matters:** Đối với người thực hành, câu hỏi là trained model, không phải exact optimum. Dữ liệu của chính bài cho thấy label noise *có* làm giảm exact copying ở trained networks (qua learned-field error tăng theo h), dù không có guarantee. Cụm "none of them protects training data" (l.1387–1388) sẽ bị trích dẫn ngoài ngữ cảnh như "label noise vô dụng cho privacy" — đó là overclaim. Đồng thời, Somepalli et al. 2023b ("Understanding and mitigating copying in diffusion models", có trong refs.bib dưới key `somepalli2023copying` nhưng *không được cite* trong main.tex) báo cáo thực nghiệm rằng ngẫu nhiên hoá/ thêm nhiễu vào text conditioning giảm copying — tức chính "knob" label noise. Bài cần đối thoại trực tiếp với kết quả này.
- **Fix:** Viết lại claim (i) thành hai mệnh đề: (a) ở exact optimum, các knob này không thay đổi support — vậy mọi tác dụng quan sát được ở trained models đến từ approximation error, không có guarantee và có thể biến mất khi model fit tốt hơn (dữ liệu EXP-1: collapse tăng theo số iteration, l.1021–1024); (b) report rõ rằng trên CIFAR-10 off-atom fraction tăng theo h. Cite và thảo luận Somepalli et al. 2023b và Wen et al. 2024 (ICLR; detection/mitigation qua magnitude của text-conditional prediction, liên quan trực tiếp tới guidance).

### W3 [Major] — Threat model và hướng dual-use không được làm rõ; claim (ii) có ý nghĩa tấn công rõ hơn tác giả nói

- **What/where:** l.234–240 (claim ii), Ethics l.1432–1433.
- **Why it matters:** Từ l.437–438, `p_i^(h)(y)` chỉ phụ thuộc vào *labels* và h, không vào x^i. Vì vậy một adversary chỉ cần biết label set (thường là public metadata, captions, hay — trong thí nghiệm inpainting — *nửa trên của chính ảnh training*, k=1536, l.1034–1036 và l.3858–3861) là có thể chọn query y để tối đa xác suất trả về một record cụ thể: đó là targeted extraction/reconstruction attack với side information. Thiết lập inpainting với identifying label thực chất là "biết một phần record → khôi phục phần còn lại", một threat model kinh điển (attribute inference/reconstruction). Ethics statement chỉ nói "helps auditors and, equally, anyone attempting extraction" mà không phân tích ai có quyền truy cập gì (query access tới sampler? biết labels? biết h?), cũng không bàn mitigations (giới hạn query, không công bố labels, DP).
- **Fix:** Thêm một đoạn "Threat model" ngắn: (1) auditor có training set (cần cho Thm. 5.2, l.1371); (2) adversary có black-box sampler + labels; (3) adversary có partial record (inpainting). Với mỗi loại, nói kết quả nào áp dụng. Ethics statement cần nêu rõ rằng việc tính được `p^(h)` chỉ từ labels làm tăng rủi ro targeted extraction, và rằng thiết lập conditioning trên record-derived signals (inpainting, super-resolution) là trường hợp rủi ro cao nhất. Lưu ý thêm: ethics statement chỉ tồn tại trong ICLR build (`\ificlr`, l.1425) và có comment "DRAFT ... the authors must check both statements" (l.1423–1424) — cần hoàn thiện.

### W4 [Major] — Claim (iii) "Monitor late-time field error, not the loss" chưa actionable cho auditor; cần định vị lại so với baselines chuẩn

- **What/where:** l.241–252; Conclusion l.1390; nhưng §6.4 l.1319–1328 và Tab. edm-anchor cho thấy nearest-neighbour distance của D_θ bằng hoặc tốt hơn ở hầu hết σ; l.251–252 thừa nhận cần exact field (tổng trên training set mỗi bước).
- **Why it matters:** Một auditor có training set đã có công cụ rẻ hơn và chuẩn hơn: nearest-neighbour distance của output (Carlini et al. 2023; Somepalli et al. 2023a; Yoon et al. 2023, đều đã cite). Kết quả của chính bài cho thấy late-time field error không thêm detection power. Do đó tiêu đề "Monitor late-time field error, not the loss" gợi ý một khuyến nghị vận hành mà dữ liệu không ủng hộ; giá trị thực là *giải thích* (mechanism of landing), không phải *giám sát*. Ngoài ra, so sánh với regression loss là đối thủ yếu: không ai trong cộng đồng privacy dùng training loss làm audit memorisation; baseline đúng là MIA (loss-based, LiRA, SecMI) và extraction rate.
- **Fix:** Đổi tên/claim (iii) thành "late-time field error explains landing; for detection use nearest-neighbour distance". Nếu muốn giữ khía cạnh audit, cần ít nhất một so sánh với membership inference trên cùng models (ví dụ loss-threshold hoặc SecMI/Duan et al. 2023) và báo cáo **TPR tại FPR thấp** (1%, 0.1%) theo Carlini et al. 2022 ("Membership inference attacks from first principles"), không chỉ AUC.

### W5 [Major] — Các thống kê "separation" có thành phần tautological và ngưỡng chọn post hoc

- **What/where:**
  - Tab. edm-rho (l.1294–1296): `ϱ_t = e_t/n_t` với n_t = khoảng cách tới *nearest training image của endpoint*; nhãn off-atom cũng định nghĩa bằng endpoint. Tác giả kiểm tra predictive anchor nhưng Tab. edm-anchor chỉ hiển thị σ ≥ 3.26 (l.3633), trong khi caption Tab. edm-rho nói "gives the same AUC at every σ" (l.1297–1299).
  - Late contraction C tích phân tới σ=0.002 (l.1310, l.3650), tức gồm các mức noise nơi ϱ_t gần như là hàm của endpoint distance; AUC=1.000 (500-image) vì vậy một phần là bookkeeping, cùng logic mà tác giả đã thừa nhận ở l.3346–3349.
  - "a final scaled error above 4 flags 94% and 95% ... and 7% and 12%" (l.3365–3366): ngưỡng 4 dường như chọn trên cùng dữ liệu, không có held-out calibration.
  - AUC tại nhiều σ, nhiều threshold, nhiều model; khoảng tin cậy chỉ được nêu cho các σ được chọn (ví dụ σ=8.4, l.1321) — vấn đề multiple comparisons/selective reporting.
- **Why it matters:** Kết luận "the late contraction separates memorised from other samples" (abstract l.115–117) sẽ yếu đi nếu separation chủ yếu đến từ các mức σ cuối gần như định nghĩa nhãn.
- **Fix:** (a) Báo cáo C chỉ trên σ ∈ [σ_min, 0.585] với σ_min đủ lớn (ví dụ ≥0.06, trước khi ϱ của mọi nhóm ~1) và với predictive anchor; (b) hiển thị predictive anchor cho *tất cả* σ của Tab. edm-rho; (c) chọn ngưỡng 4 trên một model/seed và đánh giá trên model khác (đã có model seed 1); (d) báo cáo bootstrap interval cho toàn bộ hàng AUC hoặc dùng simultaneous bands.

### W6 [Major] — Uncertainty quantification chưa phản ánh đơn vị lấy mẫu đúng

- **What/where:** l.1013–1014, l.3749–3750 (population std, n=5); l.1311 (AUC 0.983, interval [0.977, 0.988]) từ một trained model; l.1367–1368 ("instance and optimisation randomness confounded"); Tab. cifarddpm (slope s.e. 0.037, l.3917–3919); Tab. learned-averages (l.1215–1231).
- **Why it matters:**
  - Population std (denominator n) ở n=5 làm hẹp spread ~12% so với sample std, và std không phải là uncertainty của mean. Với n=5, t-interval 95% cho mean có hệ số ~2.78·s/√5. Ví dụ "0.396±0.127" (l.1023) không cho người đọc biết mean được xác định chính xác tới đâu.
  - Bootstrap intervals ở §6.4 resample *latents* của một model cố định, nên chỉ phản ánh Monte Carlo uncertainty của sampler, không phản ánh training variability (chỉ có 2 seeds ở 500 ảnh, 1 ở 2000 ảnh). Câu "the second gives the same conclusions" với n=2 không phải là bằng chứng thống kê.
  - Slope log–log (Tab. cifarddpm) là OLS trên 48 conditions có biến độc lập là reference và biến phụ thuộc là measured variance ước lượng với M=256; không rõ 48 conditions là từ 1 hay 3 instance (pooled?), s.e. OLS bỏ qua clustering theo instance và không xử lý errors-in-variables (tr Σ_h tính từ training set là chính xác, nhưng log của variance ước lượng có bias ở n_eff nhỏ, đặc biệt h=4 với n_eff=2.6).
  - Energy statistic không có null (tác giả đã thừa nhận) — nhưng một permutation null hoặc so sánh với energy giữa hai lần sample từ *cùng* exact field (Monte Carlo floor) là rẻ và nên làm.
- **Fix:** Báo cáo mean ± 95% CI (t hoặc bootstrap theo seed) thay vì population std; tách rõ "Monte Carlo CI conditional on model" và "across-training-seed variability"; nêu số instance trong regression và dùng cluster-robust s.e. hoặc mixed-effects (condition nested in instance/seed); thêm Monte Carlo floor cho energy statistic (energy giữa hai tập sample độc lập của exact field với cùng M). Bỏ false precision như "6.11937×10^{-6}" (l.1107).

### W7 [Major, presentation/correctness] — Abstract nêu sai tỉ lệ memorisation

- **What/where:** Abstract l.116–117: "on models that memorise 4 and 50% of their samples". Nhưng §6.4 l.1247–1249: model 500 ảnh có 41/1000 = 4.1% *off-atom*, tức memorise ~96%; model 2000 ảnh có 50.1% off-atom.
- **Why it matters:** Người đọc chỉ đọc abstract sẽ hiểu ngược hoàn toàn mức memorisation của model 500 ảnh — đây chính là con số mà privacy reader quan tâm nhất.
- **Fix:** "on models that memorise 96% and 50% of their samples" hoặc "with 4% and 50% off-atom samples".

### W8 [Major] — Credit nền tảng nonparametric chưa đầy đủ

- **What/where:** l.231–232 ("Gaussian kernel density estimate ... smoothed bootstrap") không có citation; eq. w2floor và câu "typically like N^{-2/d}" (l.253–256, l.478–481) không có citation; n_eff = 1/Σp² (l.1075) không có citation; Σ_h (l.458–461) không liên hệ với ước lượng conditional covariance.
- **Why it matters:** Đối với một reader từ nonparametric statistics, các object sau đã là kinh điển:
  - Endpoint law có endpoint noise, `Σ_i p_i^(h)(y) N(x^i, ρ² I)` (eq. tgtendpoint), *chính xác* là kernel conditional density estimator với bandwidth ρ trên x và h trên y (Rosenblatt 1969; Hyndman, Bashtannyk & Grunwald 1996; Fan, Yao & Tong 1996). Ở ρ=0 nó suy biến thành "weighted empirical" — Thm. 3.3. Đây là cách đọc ngắn gọn nhất của Section 3 và nên được nói ra.
  - Sampling từ đó là smoothed bootstrap (Efron 1979; Silverman & Young 1987).
  - `Σ_h` là Nadaraya–Watson (local-constant) estimator của conditional covariance; việc "matching tr Σ_h to tr Σ_post" (Fig. mechanism, h*=0.70) chính là chọn bandwidth bằng moment matching, và bias O(h²) + variance ~1/n_eff là tradeoff đã biết (Fan & Yao 1998 cho conditional variance).
  - W2 floor `∫ dist(x, {x^i})² p(dx|y)` là quantization/nearest-neighbour error; tốc độ N^{-2/d} cần điều kiện (density dương, intrinsic dimension; d≥... ) và là kết quả trong Graf & Luschgy (2000) — **có trong refs.bib (`graf2000quantization`) nhưng không được cite**; tương tự `tsybakov2009nonparametric`, `gyorfi2002distribution` có trong refs.bib nhưng không được cite. Biau & Devroye (2015) cho nearest-neighbour distance rates.
  - n_eff = 1/Σp_i² là Kish effective sample size (Kish 1965).
- **Fix:** Thêm một đoạn "statistical reading" ở cuối §3 với các citation trên, và nêu điều kiện cho N^{-2/d} (posterior có density dương trên một tập d-chiều; thay d bằng intrinsic dimension nếu posterior nằm trên manifold; và lưu ý rằng atoms được lấy từ marginal, không phải từ posterior, nên hằng số phụ thuộc vào mass của marginal quanh posterior — với σ_obs nhỏ, số atoms "hữu dụng" ~ N·P(posterior region)).

### W9 [Minor] — Tiêu chí off-atom và "class-conditional retains training images" chưa được kiểm chứng đầy đủ

- **What/where:** l.3880–3884: "Shared labels therefore remove the collapse onto one image but not the restriction to training images of the class" — nhưng chỉ có trace covariance được đo (Fig. image-class), không có tỉ lệ on-atom cho run class-conditional.
- **Fix:** Báo cáo on-atom fraction (cùng tiêu chí 1/3) cho run class-conditional, hoặc làm mềm câu.

### W10 [Minor] — "Blends as leakage" cần một tiêu chí đo được

- **What/where:** l.229–230, Ethics l.1431–1432.
- **Why:** Đồng ý rằng convex combination của hai training images là leakage. Nhưng tiêu chí off-atom 1/3 của bài *sẽ phân loại midpoint của hai ảnh là off-atom* (khoảng cách tới hai ảnh bằng nhau, tỉ số = 1). Tức chính audit protocol của bài sẽ không bắt được loại leakage mà bài nói auditor phải đếm.
- **Fix:** Đề xuất (và dùng trong CIFAR composition check, App. cifar-composition) một tiêu chí "blend detection", ví dụ khoảng cách tới affine hull/convex hull của k nearest training images, hoặc tiêu chí kiểu Carlini et al. 2023 trên patches.

### W11 [Minor] — Data attribution và tính ổn định của "which record"

- Thm. 3.3 là một công thức attribution đóng ở exact optimum; nhưng l.3367–3369 cho thấy trên trained U-Net chỉ 23–28% trùng ở h=6. Bài nên liên hệ với data attribution cho diffusion (Georgiev et al. 2023; Zheng et al. 2024) — các phương pháp đó là cách thực tế để "rank records" cho trained model, và so sánh `p^(h)` với một attribution baseline sẽ cho biết claim (ii) hữu dụng tới đâu.

### W12 [Minor] — Disclosure về LLM cần nhất quán với source

- Trong source (không hiển thị ở PDF) có các comment: l.899–900 và l.3373–3374 ghi Thm. relerr, Prop. trap, Prop. heun "drafted with model assistance", và l.1440–1442 ghi "the first drafts of the proofs ... came from model-based solver runs before the authors verified them; decide whether this paragraph should say so". Trong khi đoạn disclosure in ra (l.1445–1446) viết "The authors wrote and verified all proofs". Tôi không coi đây là vấn đề về tính đúng của chứng minh, nhưng đề nghị AC/ tác giả làm cho disclosure khớp với quy trình thực tế theo chính sách ICLR 2027. (Ghi chú: tôi chỉ thấy điều này vì supplementary chứa LaTeX source.)

### W13 [Minor] — Accessibility cho reader không chuyên

- Abstract dài ~30 dòng với nhiều qualifier lồng nhau (l.101–131); một reader ML/privacy khó trích ra 3 thông điệp chính. Các thuật ngữ "atom", "identifying label", "circumcentre", "profile", "hyperbolic" xuất hiện trước khi có giải thích trực quan. Fig. 1 (intuition, l.211–224) và đoạn "What this means in practice" là rất tốt — nên đưa chúng lên sớm hơn và rút abstract còn ~12 dòng.
- Bản ICLR (`\ificlr`) bỏ đi nhiều câu giải thích có trong bản TMLR (ví dụ l.477–481, l.193–196, l.888) — chính những câu này giúp non-specialist. Đề nghị giữ các câu interpretive và chuyển chi tiết kỹ thuật sang appendix thay vì ngược lại.
- Inpainting "label" = nửa trên ảnh (k=1536) chỉ được nói ở §6.1/App.; nên nói sớm vì nó thay đổi hoàn toàn cách đọc privacy của "identifying label".

---

## Questions for authors

1. Theo các anh/chị, threat model nào là đích của claim (i)–(iii)? Auditor có training set, adversary black-box biết labels, hay adversary có partial record? Kết quả nào áp dụng cho mỗi loại?
2. Off-atom fraction trên CIFAR-10 trained U-Net tăng theo h (0.158→0.254). Làm sao dung hoà điều này với "none of them protects training data" (l.1387–1388)? Có nên nói "không có guarantee" thay vì "không bảo vệ"?
3. Với endpoint noise ρ, nếu một adversary biết candidate set, xác suất nhận dạng đúng nguồn I từ một sample `x^I+ρξ` là bao nhiêu trên CIFAR-10 subset (một hàm của ρ)? Một đường cong như vậy sẽ minh hoạ trực tiếp khoảng cách giữa "support change" và privacy.
4. Late contraction C: AUC còn bao nhiêu nếu bỏ các mức σ < 0.06 (hoặc chỉ dùng predictive anchor ở mọi σ)? Predictive anchor có thực sự cho AUC giống hệt ở σ ≤ 1.92 không (Tab. edm-anchor chỉ hiển thị σ ≥ 3.26)?
5. Ngưỡng "final scaled error above 4" (l.3365) được chọn thế nào? Có held-out evaluation không?
6. Trong Tab. cifarddpm, 48 conditions thuộc một instance hay pooled qua ba instance? s.e. của slope có tính clustering không?
7. Có thử đo membership inference (ví dụ loss-threshold hoặc SecMI) trên các model EXP-1/CIFAR ở các h khác nhau không? Theo lý thuyết của bài, MIA advantage ở trained model nên phụ thuộc h thế nào?
8. Câu "typically like N^{-2/d}" (l.255, l.480): d ở đây là ambient dimension hay intrinsic dimension của posterior? Với posterior hẹp (σ_obs=0.1) và atoms lấy từ marginal, hằng số có phụ thuộc vào P(atom gần posterior) không?
9. Midpoint/blend ở Thm. 4.7 sẽ bị tiêu chí off-atom 1/3 xếp là off-atom. Anh/chị đề xuất auditor phát hiện blends bằng tiêu chí nào?

---

## Missing references

Chắc chắn liên quan:
- **Somepalli et al. 2023b**, "Understanding and Mitigating Copying in Diffusion Models", NeurIPS 2023 — *đã có trong refs.bib (`somepalli2023copying`) nhưng không được cite*; trực tiếp về conditioning randomisation như mitigation.
- **Wen et al. 2024**, "Detecting, Explaining, and Mitigating Memorization in Diffusion Models", ICLR 2024 — detection/mitigation dựa trên text-conditional prediction magnitude (liên quan guidance).
- **Carlini et al. 2022**, "Membership Inference Attacks From First Principles", IEEE S&P 2022 — chuẩn báo cáo TPR@low FPR.
- **Duan et al. 2023**, "Are Diffusion Models Vulnerable to Membership Inference Attacks?", ICML 2023.
- **Abadi et al. 2016**, "Deep Learning with Differential Privacy", CCS 2016.
- **Dockhorn, Cao, Vahdat, Kreis 2023**, "Differentially Private Diffusion Models", TMLR.
- **Ghalebikesabi et al. 2023**, "Differentially Private Diffusion Models Generate Useful Synthetic Images", arXiv 2023.
- **Wang, Fienberg, Smola 2015**, "Privacy for Free: Posterior Sampling and Stochastic Gradient Monte Carlo", ICML 2015 — privacy của "release one sample" mechanisms.
- **Rosenblatt 1969**, "Conditional probability density and regression estimators" (Multivariate Analysis II); **Hyndman, Bashtannyk & Grunwald 1996**, "Estimating and visualizing conditional densities", JCGS — kernel conditional density estimator (eq. tgtendpoint).
- **Silverman & Young 1987**, "The bootstrap: to smooth or not to smooth?", Biometrika — smoothed bootstrap.
- **Graf & Luschgy 2000**, *Foundations of Quantization for Probability Distributions* — *có trong refs.bib nhưng không cite*; cho W2 floor / N^{-2/d}.
- **Kish 1965**, *Survey Sampling* — effective sample size.
- **Georgiev et al. 2023**, "The Journey, Not the Destination: How Data Guides Diffusion Models"; **Zheng et al. 2024**, "Intriguing Properties of Data Attribution on Diffusion Models", ICLR 2024.

Cần kiểm tra:
- Fan, Yao & Tong 1996 (Biometrika) về conditional density estimation; Fan & Yao 1998 (Biometrika) về conditional variance estimation — cần kiểm tra chi tiết trích dẫn.
- Dimitrakakis et al. 2014 ("Robust and private Bayesian inference", ALT) — cần kiểm tra.
- Biau & Devroye 2015, *Lectures on the Nearest Neighbor Method* — cho nearest-neighbour distance rates; cần kiểm tra chương cụ thể.
- Chen et al. 2024, "Towards Memorization-Free Diffusion Models" (anti-memorization guidance, CVPR 2024) — cần kiểm tra, liên quan "negative guidance" như mitigation.
- Tsybakov (2009) và Györfi et al. (2002) có trong refs.bib nhưng không cite — có lẽ tác giả định dùng cho NW; nên cite hoặc xoá.

---

## Scores

- **Soundness: 3 / 4.** Lý thuyết về exact field có cấu trúc chặt chẽ (proof template thống nhất, ví dụ hyperplane cho thấy exceptional set không bỏ được, threshold chính xác, phần chứng minh trong appendix chi tiết; tôi không kiểm tra từng dòng các chứng minh Lyapunov–Perron vì ngoài chuyên môn). Trừ điểm vì: phần thống kê thực nghiệm có thành phần tautological trong C/ϱ ở σ nhỏ, uncertainty chưa phản ánh training variability, và abstract mô tả sai tỉ lệ memorisation.
- **Presentation: 2 / 4.** Fig. 1, Table 1, "What this means in practice" rất tốt; nhưng abstract quá dày đặc và chứa lỗi số liệu, nhiều nội dung giải thích bị cắt trong bản ICLR, threat model không được nêu, ethics statement còn là draft.
- **Contribution: 3 / 4.** Đặc trưng hoá đầy đủ các knob trên exact field + phân biệt "which vs whether" + kết quả selection-early/landing-late trên EDM là đóng góp có giá trị cho cả cộng đồng generative modelling và privacy. Tuy nhiên, với privacy, giá trị thực tiễn bị giới hạn: kết quả là về exact optimum, khái niệm leakage là support-based, và đại lượng đề xuất không vượt NN-distance baseline.
- **Overall Rating: 6 (marginally above acceptance threshold).** Lý do: đóng góp lý thuyết rõ ràng, chính xác về phạm vi và trung thực về giới hạn ở hầu hết chỗ; thí nghiệm EDM có dự đoán falsifiable. Không cao hơn vì các claim thực tiễn về privacy (đặc biệt (i) và (iii)) cần được scope lại, thiếu threat model và liên hệ DP/MIA/extraction literature, và phần thống kê cần chỉnh. Không thấp hơn vì những vấn đề này chủ yếu sửa được bằng viết lại và một số phân tích bổ sung rẻ.
- **Confidence: 3 / 5.** Tôi tự tin về phần privacy và nonparametric statistics; ít tự tin hơn về các chứng minh dynamical-systems (spectral classification, Lyapunov–Perron) mà tôi không kiểm tra chi tiết.

---

## What would move my score up

1. Viết lại claim (i)/(iii) và Ethics với threat model tường minh; scope (i) thành "không có guarantee ở exact optimum; tác dụng ở trained models đến từ approximation error", có dẫn số liệu off-atom tăng theo h và thảo luận Somepalli et al. 2023b / Wen et al. 2024. (→ 8 nếu kèm 2–3.)
2. Một phân tích nhỏ về endpoint noise từ góc độ identifiability: tỉ lệ nhận dạng đúng nguồn I theo ρ, và ρ cần cho Gaussian-mechanism DP, để làm rõ khoảng cách "support change ≠ privacy".
3. Bổ sung thống kê: C và ϱ chỉ trên σ không chứa thông tin endpoint (predictive anchor ở mọi σ), held-out cho ngưỡng 4, mean ± CI thay vì population std, cluster-robust s.e. cho slope, Monte Carlo floor cho energy statistic.
4. Một thí nghiệm membership inference (TPR@1% FPR) theo h trên EXP-1 hoặc CIFAR subset, để nối lý thuyết với metric chuẩn của privacy.
5. Sửa lỗi abstract (4% vs 96%), thêm đoạn "statistical reading" với credit cho kernel conditional density estimation, smoothed bootstrap, quantization, Kish n_eff; và làm disclosure LLM khớp với quy trình thực tế.

---

### Devil's Advocate Review — "Atomic Endpoints of Averaged and Guided Empirical Conditional Flows"

## 1. Strongest Counter-Argument (200-300 words)

Thông điệp cốt lõi của bài, "exact empirical minimiser memorises, và các biến đổi sampler-side của nó (label noise, label averaging, CFG, guidance schedule) vẫn memorise", gần như là hệ quả trực tiếp của một sự thật đã biết: mọi field có dạng `dot x = (m̄ - x)/(1-t)` với `m̄` là convex combination của posterior means trên một finite support thì hội tụ về các atoms. Phần khó thật sự về kỹ thuật (bỏ được giả thiết limit-set của Liu et al. 2026, có kết luận a.e.) có giá trị, nhưng nhỏ và hẹp. Kết quả "positive" duy nhất (guided label averaging tạo ra blend) lại nói về một construction mà chính tác giả thừa nhận là không ai dùng ("we know of no trained model that averages its field over labels", l.124). Basin của nó nằm trong boundary layer cỡ `(1-t)^2`, và chỉ tái tạo được khi network được cho sẵn input `asinh(tx/(1-t)^2)` đặt đúng tại vị trí tie đã biết. Đó là một construction được dựng để thành công.

Phần cầu nối sang mô hình thực tế (Theorem transfer, Theorem relerr) gần như là tautology. Tác giả tự viết rằng bound "holds with equality" và các đo đạc cuối trajectory chỉ là "bookkeeping, not evidence" (l.895-897, l.3346-3349). Ở EDM, `ϱ_t = e_t/n_t` với `n_t` neo vào ảnh gần nhất của endpoint, nên `ϱ→1` cho off-atom samples gần như đúng theo định nghĩa. Bản thân tác giả cũng kết luận field error không tốt hơn nearest-neighbour distance khi dùng làm detector (l.1319). "Prediction" cho Heun sampler (thêm steps thì certificate đúng) chỉ là một nhận xét đại số về `r_k ≥ 1/2`, và outcome không đổi. Đó là dự đoán về độ chặt của chính cái bound, không phải về sampler. Ngoài ra, chính dữ liệu CIFAR của bài (off-atom fraction tăng theo h: 0.17→0.30) mâu thuẫn với khuyến nghị thực tiễn "the knobs are not privacy mitigations". Cuối cùng, bài bị quá tải với khoảng 20 kết quả, các hedge chồng lên nhau và một abstract 30 dòng, nên người đọc ICLR khó rút ra một takeaway hành động được.

## 2. Issue List

**[CRITICAL] Significance / logic chain: khuyến nghị thực tiễn bị chính dữ liệu của bài phản bác**
- Vị trí: l.227-233 ("The knobs are not privacy mitigations"), l.1385-1388 (Implications), Ethics statement l.1429-1432; đối chiếu App. measured-transfer l.3317-3320, l.3341-3342, Sec. p7 l.1079-1081.
- Lập luận: Khẳng định chỉ đúng *at the exact optimum*, tức là đúng nơi không ai kỳ vọng mitigation có tác dụng. Mitigation trong thực tế (Somepalli et al. 2023, conditioning augmentation) có tác dụng chính vì network *không* đạt exact optimum. Dữ liệu của bài cho thấy label noise trên network đã train *làm tăng* off-atom fraction theo h (0.173 → 0.246 → 0.298 tại h=4,5,6; h=0 bằng 0) và làm giảm tỷ lệ trùng ảnh với exact field (55-67% → 23-28%). Đây là bằng chứng ngược chiều với cách đọc "(i)" cho trained models. Đoạn (i) có nhắc "at the exact optimum" nhưng framing của abstract, Introduction và Ethics vẫn đẩy về kết luận thực tiễn.
- Cách giải quyết: Viết lại (i) thành "label noise không thay đổi support của exact optimum; trên trained networks chúng tôi quan sát ngược lại: off-atom fraction tăng theo h". Nếu muốn giữ claim privacy thì cần một thí nghiệm extraction/replication trên trained models có và không có label noise/guidance.

**[MAJOR] Novelty: thông điệp chính gần như trivial so với prior work**
- Vị trí: Sec. 3-4 (Prop. collapse, Thm. endpoint, Thm. posmix, Prop. cfgatom, Thm. schedule); Related work l.293-330.
- Lập luận: Collapse at h=0 và Nadaraya-Watson endpoint law đã được tác giả tự nhận là "a reference, not a new identity" (l.306-307). Atomicity dưới positive mixture hay guidance là điều trực giác hiển nhiên (`m̄` là combination của posterior means trên finite support). Phần mới là bỏ được giả thiết limit-set của Liu et al. 2026 Thm 3.18 và kết luận a.e. Đây là đóng góp kỹ thuật thật nhưng biên (incremental) cho ICLR, nhất là khi bài tự thừa nhận hai ODE tương đương qua change of variables (App. l.1841-1851).
- Cách giải quyết: Tách rõ "đã biết / folklore" và "mới chặt chẽ". Định vị đóng góp chính là bổ đề Step 2 (volume expansion qua Liouville + Fatou, xử lý được signed combination) và chứng minh nó có ích ngoài bài này.

**[MAJOR] Significance: kết quả positive duy nhất là về một construction không ai dùng**
- Vị trí: Thm. composition (l.683-696), Thm. spectral, Prop. composition-open; l.120-126, l.186-189, l.1394-1397; learned composition l.1139-1157.
- Lập luận: Tác giả thừa nhận không có trained model nào average field over labels. Prop. bottleneck cho thấy label bottleneck average *priors* chứ không phải fields, nên guidance trên đó vẫn atomic. Basin chỉ tồn tại ở scale `(1-t)^2`. Network chỉ tái tạo được khi nhận input `asinh(tx/(1-t)^2)` *centred at the known tie* (đặt chỗ khác thì midpoint trống, l.1148). Như vậy thí nghiệm learned composition là một engineered sanity check, không phải bằng chứng về hiện tượng. "Boundary marker" là một cách đóng khung hợp lý, nhưng khi đó Thm. spectral, Cor. spectral-threshold, Prop. composition-open, các thí nghiệm CIFAR pairs và d=8 đều phục vụ cho một ranh giới không có hệ quả thực tiễn.
- Cách giải quyết: Hoặc chỉ ra một pipeline thực tế tương đương (ví dụ ensemble of label queries, multi-prompt averaging với CFG, compositional guidance kiểu Liu et al. 2022 "Compositional Visual Generation") và kiểm tra trên đó, hoặc rút composition xuống thành một remark/appendix để phần chính tập trung.

**[MAJOR] Soundness/Significance: Theorem transfer và relerr gần tautological; bằng chứng EDM mang tính circular**
- Vị trí: Thm. transfer (l.868-897; "The argument is elementary; its use is the reading", l.888); Thm. relerr (l.908-926); App. l.3307-3311, l.3346-3349; Table edm-rho (l.1294-1297).
- Lập luận:
  (a) Thm. transfer là variation-of-constants trên một ODE tuyến tính. Bản thân tác giả chỉ ra rằng nếu `v_θ` bounded thì `(1-t)Δ → z - a`, nên bound là đẳng thức. Đo `(1-t)|Δ|` cuối trajectory tức là đo khoảng cách endpoint đến atom.
  (b) Ở EDM, `n_t` là khoảng cách đến *endpoint's* nearest training image. Ở σ nhỏ, `m* ≈ a`, nên `e_t ≈ |D_θ - a|`, còn `Z` hội tụ về `D_θ`. Do đó `ϱ_t = e_t/n_t → 1` cho mọi sample không hội tụ về `a`, tức là đúng theo định nghĩa off-atom. Late contraction `∫(1-ϱ) d log(1/σ)` là một tích phân của đại lượng gần như được định nghĩa bởi outcome. Predictive anchor (App. Table edm-anchor) chỉ được báo cáo ở σ ≥ 3.26, trong khi phần "late contraction decides landing" dùng σ ∈ [0.002, 0.585] với anchor là endpoint.
  (c) Thm. relerr(b) là Gronwall chuẩn; (c) là converse Gronwall; (d) là ví dụ tuyến tính. Đây là các bất đẳng thức cơ bản, không phải insight mới.
- Cách giải quyết: Báo cáo toàn bộ Table edm-rho và late contraction với predictive anchor (nearest image của `D_θ` tại σ đầu cửa sổ, ví dụ σ=0.585), không dùng thông tin endpoint. Nêu rõ trong main text rằng hai theorem là pathwise stability identities, không phải predictive results.

**[MAJOR] Evidence: đóng góp thực nghiệm EDM không vượt baseline đơn giản**
- Vị trí: l.1319-1328; App. Table edm-anchor; abstract l.118-119.
- Lập luận: Chính tác giả kết luận field error "no better than the distance to the nearest training image" làm detector. Absolute error còn *tệ hơn* baseline ở σ ∈ [3.3, 19.4]. Radial ratio chỉ hơn ở σ rất cao, nơi cả hai đều yếu (AUC 0.6-0.8). Late contraction chỉ ngang baseline trên model 2000 ảnh. Đại lượng lại cần exact field (tổng trên toàn training set mỗi step), nên không ai triển khai được ngoài auditor. Vì vậy EDM section là "mechanism description" mà không có predictive gain. Câu "explains landing" khó kiểm chứng (falsify) vì đại lượng gần như được định nghĩa từ outcome (xem issue trên).
- Cách giải quyết: Đưa ra một prediction có thể sai mà baseline NN-distance không đưa ra được, ví dụ can thiệp (intervention) giảm `ϱ_t` chỉ trong cửa sổ muộn và cho thấy off-atom fraction thay đổi như dự đoán. Swap experiment (l.1255-1262) là bước đúng hướng; cần mở rộng thành định lượng.

**[MAJOR] Novelty: "image chosen early, landing decided late" thiếu đối chiếu với prior work trực tiếp**
- Vị trí: l.1253-1262, Fig. edm-clocks ("Two clocks"), l.1390-1393; Related work l.296-302.
- Lập luận: Biroli, Bonnaire, de Bortoli & Mézard (2024, "Dynamical regimes of diffusion models") đã mô tả đúng hai thang thời gian: speciation time (chọn class/mode sớm) và collapse time (bị hút vào một training point muộn) cho empirical score. Entry `biroli2024dynamical` có trong refs.bib nhưng **không được cite** trong main.tex. Các công trình về critical windows / symmetry breaking (ví dụ Raya & Ambrogioni 2023; Sclocchi et al. 2024/2025; Li & Chen 2024) cũng mô tả hiện tượng "quyết định sớm". Dodson et al. được cite nhưng chỉ để xác nhận. Ngoài ra, trên CIFAR với 50-200 ảnh/class, posterior empirical ở σ≈1 đã gần delta do khoảng cách giữa ảnh trong d=3072 lớn. Vì vậy "swap từ σ=s đến nearest image" phần lớn phản ánh hình học dữ liệu chứ không phải hành vi network.
- Cách giải quyết: Cite và so sánh định lượng với collapse time `t_C` của Biroli et al. (dự đoán σ tại đó exact posterior tập trung, so với σ selection đo được). Báo cáo posterior entropy của exact field tại σ = 5, 2, 1 để phân biệt "network chọn" với "hình học buộc chọn".

**[MAJOR] Evidence/Overgeneralization: phạm vi thực nghiệm hẹp**
- Vị trí: Limitations l.1364-1372; Sec. 6.
- Lập luận: Một dataset ảnh (CIFAR-10), một mask inpainting, N=2000. EDM chỉ có 3 trained models (2 seeds × 500 ảnh, 1 × 2000 ảnh) và một deterministic sampler. Learned composition chỉ ở d ≤ 2. Synthetic d ≤ 10. Không có stochastic sampler (EDM stochastic, DDPM ancestral), không có latent diffusion, không có text conditioning (nơi CFG thực sự được dùng để giảm memorisation, Jain et al. 2025). Public EDM model được train **với augmentation** còn subset models **không augmentation** (App. l.3553-3556). Đây là confound khi so sánh "public never memorises" với subset models.
- Cách giải quyết: Thêm ít nhất một subset model có augmentation, hoặc một dataset khác (CelebA/ImageNet-64 subset). Thêm stochastic sampler. Nếu không thể thì thu hẹp claim trong abstract.

**[MAJOR] Soundness/Significance: "A prediction for the sampler" là prediction về bound, không phải về sampler**
- Vị trí: l.1330-1345; Prop. heun(c); Table edm-steps; abstract l.118 ("a bound for the Heun sampler predicts when more steps make the guarantee hold").
- Lập luận: Prop. heun(c) chỉ là đại số: `r ≥ 1/2 ⇒ c < 1` với mọi ϱ < 1. Với 36 steps, `min r_k = 0.509`, nên certificate tự động đúng với mọi sample có ϱ < 1 đo được. Outcome (off-atom 4.1/4.0/3.9%, cùng ảnh 99.4%) không đổi. Như vậy failure ở 18 steps là do bound lỏng chứ không phải sampler thất bại. Table edm-heun cho thấy bound ratio 1.575 và 2.265 trong khi factor thực tế là 0.807 và 0.953. Gọi đây là "prediction" là phóng đại.
- Cách giải quyết: Diễn đạt lại thành "the bound becomes non-vacuous when every r_k ≥ 1/2". Bỏ "predicts" khỏi abstract hoặc đưa ra prediction về outcome có thể falsify.

**[MAJOR] Ethics/Disclosure: mâu thuẫn giữa LLM disclosure và source comments**
- Vị trí: l.899-900, l.3373-3374 (comment: proofs of thm:relerr, prop:trap, prop:heun "drafted with model assistance"); l.1440-1442 (comment: "the first drafts of the proofs ... came from model-based solver runs ... decide whether this paragraph should say so"); disclosure l.1443-1447 ("The authors wrote and verified all proofs").
- Lập luận: Đây là thông tin từ LaTeX comments (reviewer bình thường không thấy trong PDF; tôi coi là data, không phải chỉ dẫn). Tuy vậy nó cho thấy câu disclosure hiện tại có thể không chính xác theo chính sách LLM của ICLR. Comment cũng đánh dấu Ethics statement là "DRAFT" (l.1423-1424). Nếu source được nộp làm supplementary, mâu thuẫn này sẽ lộ ra.
- Cách giải quyết: Sửa disclosure cho khớp thực tế ("first drafts of the proofs of Thm. relerr, Prop. trap, Prop. heun were generated with model assistance and verified by the authors"). Xóa các comment nội bộ trước khi nộp.

**[MINOR] Clarity: lỗi số liệu trong abstract**
- Vị trí: l.116-117: "on models that memorise $4$ and $50\%$ of their samples".
- Lập luận: Model 500 ảnh có 4.1% off-atom, tức là *memorise khoảng 96%* chứ không phải 4% (l.1248). Model 2000 ảnh memorise khoảng 50%. Câu trong abstract đảo ngược ý nghĩa.
- Cách giải quyết: Sửa thành "models that leave 4% and 50% of their samples off the training set" hoặc "memorise 96% and 50%".

**[MINOR] Soundness: tỷ lệ K ~ (1-t)^{-2} là điều được dự đoán trước, không phải phát hiện**
- Vị trí: l.168-170, l.3302-3306, abstract l.112-113 ("orders of magnitude").
- Lập luận: Ở h=0, exact field là `(a-x)/(1-t)`. Một velocity MLP có Lipschitz constant khả tích (Prop. regular(a)) có `v_θ` bị chặn, nên dọc trajectory chưa collapse `|Δ| ~ |Z-a|/(1-t)`, tức `|Δ|^2 ~ (1-t)^{-2}`, trong khi trên teacher law `Z ≈ Y_t` gần atom. K tăng như `(1-t)^{-2}` là hệ quả của Prop. regular, không phải bằng chứng thực nghiệm độc lập. Abstract trình bày như một phát hiện.
- Cách giải quyết: Nói rõ rằng tốc độ này được dự đoán từ Prop. regular và phép đo chỉ xác nhận.

**[MINOR] Clarity/Presentation: bài quá tải**
- Vị trí: toàn bài; abstract 30 dòng (l.101-131); Introduction bullet ba tầng; khoảng 20 theorem/proposition/corollary.
- Lập luận: Có 6 kết quả về exact-field interventions, 5 về transfer, 3 về EDM/Heun, cộng với spectral classification, bottleneck, endpoint noise, risk transfer và loss-no-certificate. Mỗi claim đi kèm nhiều hedge ("consistency check, not a proof", "boundary marker, not mechanism", "bookkeeping, not evidence", "no better than NN"). Người đọc ICLR khó xác định đóng góp chính. Hai phiên bản ICLR/TMLR được ghép bằng `\ificlr`/`\moveblock` khiến nội dung main text ICLR bị dồn vào appendix (ví dụ Thm. spectral chỉ còn một đoạn tóm tắt).
- Cách giải quyết: Chọn một trục: hoặc (A) theory of exact-field interventions (posmix + schedule + composition + spectral), hoặc (B) relative-error landing mechanism trên EDM. Đưa trục kia vào follow-up. Rút abstract xuống khoảng 200 từ.

**[MINOR] Clarity: phép đo "off-atom" phụ thuộc ngưỡng 1/3 và chỉ tính trong class**
- Vị trí: l.1246-1247, l.3315-3316.
- Lập luận: Criterion là tỉ lệ khoảng cách nearest/second-nearest trong pixel space, chỉ tính trong class. Bài có kiểm tra robustness ngưỡng 0.2/0.5 (tốt). Tuy nhiên pixel L2 không phản ánh "copy" theo nghĩa privacy (SSCD, Somepalli et al.), và near-duplicate (ảnh dịch/lật) có thể bị tính là off-atom.
- Cách giải quyết: Bổ sung một metric perceptual/SSCD hoặc ít nhất là kiểm tra flip/shift.

**[MINOR] Evidence: thống kê**
- Vị trí: Table learned-averages (l.1214-1230, "no null subtraction or equivalence threshold"); EXP-1 seed spread (CV 30-45% ở 2×10^5); CIFAR 3 seeds.
- Lập luận: Nhiều kết quả là descriptive với 3-5 seeds và không có CI. Pilot learned label averages không có test nên không hỗ trợ kết luận nào.
- Cách giải quyết: Bỏ pilot hoặc thêm null baseline. Báo cáo CI cho các tỷ lệ chính.

## 3. Ignored alternative explanations / paths

1. **Off-atom EDM samples là do underfitting/capacity/EMA, không phải "late field error" như một cơ chế riêng.** Mô hình 2000 ảnh với 10 Mimg có thể chưa hội tụ. Phase transition memorisation theo N đã biết (Gu et al. 2023; Yoon et al. 2023; Kadkhodaie et al. 2024). Late error có thể chỉ là triệu chứng của generalisation do inductive bias, và theorem chỉ mô tả lại triệu chứng đó.
2. **Augmentation confound:** public model train với augmentation, subset models không. "Public model never memorises" có thể do augmentation và dataset size, không nói gì về cơ chế landing.
3. **Hình học dữ liệu thay vì network selection:** "image chosen by σ≈1" có thể chủ yếu do exact posterior trên vài trăm ảnh đã tập trung ở σ≈1 (cần đo entropy posterior). Khi đó "selection" là thuộc tính của dữ liệu, không phải network.
4. **Patch-mosaic / locality** (Kamb & Ganguli; Niedoba et al.): tác giả nêu nhưng không kiểm tra (l.3332-3333). Đây là giải thích cạnh tranh trực tiếp cho off-atom samples và kiểm tra khá rẻ.
5. **Stochastic samplers:** noise injection (EDM S_churn, ancestral) thay đổi cơ chế landing. Thm. relerr là cho ODE. Không rõ kết luận có giữ không.
6. **Hướng khác cho composition:** compositional/multi-prompt CFG (sum of conditional scores với nhiều prompt) trong text-to-image *là* một dạng signed combination of fields thực sự được dùng. Đây là chỗ composition result có thể có ý nghĩa thực tiễn nhưng bài không khai thác.
7. **Label noise thực sự giảm memorisation trên trained nets** (dữ liệu của chính bài). Giải thích thay thế: label noise làm target khó fit hơn, nên network ở xa exact optimum hơn. Đây là regularisation effect mà theory exact-field không thấy được.

## 4. Missing stakeholder perspectives

- **Privacy/DP auditors:** bài nói về "leakage" và "audit" nhưng không có membership inference hay extraction experiment, không có threat model. Exact field cần toàn bộ training set, nên auditor nào cũng đã có dữ liệu.
- **Practitioners text-to-image / latent diffusion:** CFG, negative prompts, guidance interval được dùng chủ yếu ở đó. Label ở đó không identifying, không Gaussian-noised, và model chạy trong latent space. Không có thí nghiệm nào ở setting này.
- **Theory community về sampling error (Benton et al., Chen et al.):** cần hiểu quan hệ giữa relerr và các KL/TV bounds hiện có. Bài chỉ nhắc qua.
- **Practitioners về sampler design:** kết luận Heun (r_k ≥ 1/2) không đưa ra khuyến nghị nào thay đổi outcome.
- **Statistical physics community** (Biroli, Mézard, Bonnaire): framing "two clocks" trùng với speciation/collapse time nhưng không được đối chiếu.

## 5. Observations (non-defects): những điểm tôi không bác bỏ được

- **Độ chặt chẽ toán học cao và trung thực.** Theorem posmix và Prop. cfgatom loại bỏ được giả thiết limit-set của Liu et al. 2026 Thm 3.18 và đạt kết luận *every trajectory converges + a.e. atom* cho guidance w>0 cố định. Đây là một cải tiến kỹ thuật thật, có bảng so sánh rõ ràng (App. Table comparison).
- **Proof template hai bước** (kinetic energy → convergence; divergence `βΘ - d` + Liouville/Fatou → null basin) thống nhất và tái sử dụng được. Prop. hyperplane cho thấy null set không thể bỏ được.
- **Threshold đóng `w > 1/sinh^2 B`** là kết quả sắc nét, đã được kiểm tra số (basin grows linearly với hệ số `sqrt(2/π)/cosh B` khớp đến 0.01%). Spectral classification có phần (a)/(b) rõ ràng, phân biệt được saddle mà trace test bỏ sót.
- **Tác giả tự phê bình rất mạnh:** thừa nhận transfer bound là identity, báo cáo field error không tốt hơn NN baseline, báo cáo near-tie integration failures, tách "consistency check" khỏi "proof". Đây là văn hóa báo cáo đáng khen, hiếm thấy.
- **Swap experiment** (network đến σ=s rồi exact field) là một thiết kế can thiệp sạch và cho thấy hiệu ứng đáng chú ý: thay field ở 2% thời gian cuối biến public model từ 0% thành 100% memorisation.
- **Prop. loss-no-certificate** là counterexample gọn, minh họa đúng khoảng trống giữa regression loss và endpoint.
- Reproducibility tốt: scripts được liệt kê theo từng con số.

## 6. Scores (nếu là regular reviewer)

- **Soundness:** 3 (proofs có vẻ đúng; một số claim thực nghiệm mang tính circular hoặc bị phóng đại, và abstract có lỗi số)
- **Presentation:** 2 (quá tải, hedge chồng chất, abstract dài, cấu trúc hai phiên bản)
- **Contribution:** 2 (kỹ thuật chặt chẽ nhưng message chính gần trivial; kết quả positive nói về construction không ai dùng; EDM không vượt baseline)
- **Rating:** 5 (marginally below acceptance threshold)
- **Confidence:** 4
