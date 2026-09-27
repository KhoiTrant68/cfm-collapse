# Simulated Peer Review — "Conditional Flow Matching: Kernel Smoothing over Atoms Does Not Restore the Posterior"

- **Manuscript**: `paper/main.tex` (commit `5e5db1a`), 9 trang chính + phụ lục, tổng 70 trang PDF, 29 kết quả hình thức (proposition/theorem/corollary/lemma), 33 tài liệu tham khảo.
- **Ngày review**: 2026-09-27 — Vòng 1
- **Chế độ**: `academic-paper-reviewer` / `full` (5 reviewer + tổng hợp biên tập)
- **Venue mục tiêu**: ICLR 2027 Workshop (ví dụ DeLTa — Deep Generative Models: Theory, Principles and Efficacy); kèm hiệu chỉnh cho ICLR 2027 main track.

> **Công bố giới hạn.** Năm báo cáo dưới đây do *một* mô hình viết trong một phiên, mỗi báo cáo nhận một vai và trọng tâm khác nhau; chúng không độc lập theo nghĩa của năm con người. Điểm số có ý nghĩa **thứ tự** (bài A > bài B), không phải xác suất được nhận. Chưa chạy `calibration` mode. Reviewer chỉ đọc bản thảo — không sửa manuscript.

---

## Phase 0 — Field analysis & cấu hình reviewer

| Mục | Nhận định |
|---|---|
| Lĩnh vực chính | Machine learning — lý thuyết mô hình sinh (flow matching / stochastic interpolants) |
| Lĩnh vực phụ | Nonparametric statistics (Nadaraya–Watson, KDE), optimal transport, Bayesian inverse problems |
| Paradigm | Lý thuyết (population minimiser, closed form) + thực nghiệm kiểm chứng |
| Loại bài | Theory-with-validation / "understanding" paper |
| Độ chín | Cao về kỹ thuật (có audit script cho chứng minh), nhưng văn bản còn dấu vết nhiều vòng sửa |

| Vai | Danh tính được cấu hình | Trọng tâm |
|---|---|---|
| **EIC** | Area Chair ICLR, mảng generative models, từng review nhiều bài memorization trong diffusion | Fit, novelty, significance cho cộng đồng ICLR |
| **R1 — Methodology** | Nhà nghiên cứu empirical về diffusion/FM, quen đánh giá sample diversity, bootstrap, seed control | Thiết kế thí nghiệm, thống kê, reproducibility |
| **R2 — Domain** | Lý thuyết gia về closed-form / empirical-optimal diffusion & FM (dòng Bertrand, Gao, Kamb, Buchanan) | Tính mới toán học, định vị literature, độ chặt chứng minh |
| **R3 — Perspective** | Nhà thống kê Bayesian / scientific ML dùng CFM cho bài toán ngược vật lý | Ý nghĩa thực tiễn, uncertainty quantification, người dùng cuối |
| **Devil's Advocate** | Reviewer hoài nghi, chuyên săn "so what?" và claim quá tầm | Phản biện mạnh nhất với luận điểm trung tâm |

---

## Report 1 — EIC (Area Chair)

**Recommendation**: Main track — *Major Revision → dự kiến Reject*; Workshop — *Accept (poster)*
**Confidence**: 4/5

### Summary Assessment
Bài chứng minh rằng với tập huấn luyện cố định, nghiệm tối ưu population của conditional FM với nhãn phân biệt sụp về đúng một atom (Prop. 2), và rằng label smoothing Gaussian biến luật điểm cuối thành hỗn hợp Nadaraya–Watson trên các atom (Thm. 5), nên support vẫn nằm trên tập huấn luyện ở mọi h (Prop. 9). Từ đó bài xếp hạng bốn can thiệp (interpolant noise, CFG, label smoothing, endpoint smoothing) và đề xuất một thống kê audit (slope β) thay cho tỉ số phương sai. Thực nghiệm synthetic xác nhận rất sạch (tỉ số ≈ 1.00 ± 0.05); ở CIFAR-10 với U-Net 35.75M, collapse cứng tái lập được nhưng khớp khi h > 0 chỉ một phần (β = 0.481). Chủ đề đúng trọng tâm ICLR và bài viết trung thực hiếm thấy, nhưng đóng góp toán học lõi ngắn và gần với các kết quả closed-form đã biết, còn phần thực nghiệm quy mô lớn lại cho thấy lý thuyết *không* mô tả mạng thật. Với main track, tôi dự đoán hội đồng sẽ chia rẽ và nghiêng về reject; với workshop lý thuyết mô hình sinh, đây là bài tốt.

### Strengths
- **S1 — Thông điệp audit rõ và có giá trị.** "Variance restored ≠ posterior restored" (§1 item 3, Prop. 9) cùng quan sát rằng tỉ số aggregate vô nghĩa khi mẫu số hầu như không biến thiên (Fig. 2: 0.74 decades ở h=6) là bài học phương pháp luận dễ được cộng đồng dùng lại.
- **S2 — Phân loại can thiệp có tính thực hành** (§3.5 cuối): inert → atom-preserving → reweighting → support-moving.
- **S3 — Tính trung thực học thuật cao**: Limitations nêu thẳng rằng atomicity không chuyển sang mô hình được huấn luyện (§5), kết quả âm được báo cáo.

### Weaknesses
- **W1 — Đóng góp lõi mỏng so với chuẩn main track.** Thm. 5 là hệ quả vài dòng của Lemma mixture-coupling; Prop. 9 là hệ quả trực tiếp của Thm. 5; bài tự viết "We do not claim a new generic kernel identity" (dòng 103). *Severity: Major (main) / Minor (workshop).* *Gợi ý*: định vị lại đóng góp là *công cụ audit* + *phân loại can thiệp*, không phải là định lý.
- **W2 — Khoảng cách lý thuyết–thực tiễn được thừa nhận nhưng không được lấp.** Ở CIFAR, 38% mẫu off-atom tại h=6, β=−0.156. *Severity: Major.* *Gợi ý*: cần ít nhất một kết quả định lượng nối population và mô hình hữu hạn (ví dụ cận cho β theo phần loss chưa khử), hoặc hạ claim ở abstract.
- **W3 — Mật độ và cấu trúc.** 29 kết quả hình thức, phần chính tham chiếu phụ lục liên tục; danh sách đóng góp (§1) đọc như danh sách caveat. *Severity: Major cho presentation.*

---

## Report 2 — R1 (Methodology)

**Recommendation**: Major Revision
**Confidence**: 4/5

### Summary Assessment
Các thí nghiệm synthetic được thiết kế cẩn thận (sanity check chuẩn tắc 1.8e-15, closed-form integration, 5 seed, tách instance/optimisation ở Appendix `sec:seedsplit`). Phần CIFAR có nhiều quyết định tốt (bootstrap CI, re-measure ở M=256, ba instance mới), nhưng tôi thấy một mâu thuẫn thuật ngữ ảnh hưởng trực tiếp đến claim chính, β chỉ đo trên một instance, và lựa chọn bandwidth chưa được biện minh. Quy mô ảnh (N=2000, một cấu hình mask) còn nhỏ.

### Strengths
- **S1** — Tách đúng tham chiếu `Cov_h` khỏi `Σ_post` ở P7 và chỉ ra "h≈0.1 khôi phục hoàn hảo" là trùng hợp (dòng 600–602). Đây là một correction có giá trị thật.
- **S2** — Báo cáo quy ước (population SD, sai số tương đối √(2/(M−1)) = 8.9% ở M=256) minh bạch (dòng 2776–2787).
- **S3** — Kiểm tra rival explanations cho β (additive floor, hard floor, affine: R² 0.42/0.24/0.28 vs 0.78, dòng 2993–2996).

### Weaknesses
- **W1 — "Aggregate" và "median" bị dùng lẫn cho cùng một số.** §1 item 3 (dòng 163) viết "aggregate agreement is 1.15"; dòng 651 nói Table `tab:cifarddpm` báo cáo "the aggregate ratio". Nhưng cột trong bảng (dòng 2793) là **median** tỉ số per-condition, và tỉ số aggregate thật của seed 0 theo Table `tab:seed3` là 1.181 (h=6) và 2.255 (h=4), khác xa median 5.30. Phụ lục (dòng 3052) còn khẳng định "We report the aggregate ratio throughout". *Why it matters*: đây là con số headline của contribution 3; reviewer đối chiếu sẽ thấy ngay. *Suggestion*: thống nhất một định nghĩa, báo cả hai trong Table 2 và sửa abstract/§1. **Severity: Major** (sửa nhanh nhưng bắt buộc).
- **W2 — β chỉ từ một instance.** Table `tab:cifarddpm` và Fig. 2 là "displayed instance"; Table `tab:seed3` báo trCov và ratio cho 3 seed nhưng **không** báo β. Claim "β = 0.481 ± 0.037" chỉ mang s.e. hồi quy trong một instance, không phải biến thiên giữa instance. *Suggestion*: báo β cho cả 3 seed (dữ liệu đã có). **Severity: Major.**
- **W3 — Chọn h ∈ {4,5,6} với k=1536 không được biện minh.** Không rõ vì sao ba giá trị này, và chúng tương ứng n_eff 2.6 / 16.4 / 74.9 — tức cả dải hữu ích nằm gọn trong một khoảng rất hẹp của h. *Suggestion*: tham số hoá theo n_eff mục tiêu và giải thích cách chọn. **Severity: Minor.**
- **W4 — Quy mô và đa dạng ảnh.** Chỉ CIFAR bottom-half inpainting với N=2000 ở 60k iter; β vẫn đang tăng khi hết budget (Fig. `fig:betatraj`). Kết luận "partial" vì thế là kết luận về budget. *Suggestion*: một run dài hơn (ví dụ 200k iter) ở h=4 là thí nghiệm có giá trị nhất có thể thêm. **Severity: Major (main) / Minor (workshop).**
- **W5 — Main text chỉ báo P7 ở h = 0.05, 0.1, 0.5** (dòng 598), bỏ h=0.01 nơi tỉ số là 1.308 ± 0.376 (dòng 2895). Lý do được giải thích ở phụ lục (n_eff ≈ 3.5), nhưng main text nên nêu một câu. **Severity: Minor.**

---

## Report 3 — R2 (Domain / Theory)

**Recommendation**: Major Revision (main) — Accept (workshop)
**Confidence**: 5/5

### Summary Assessment
Các chứng minh tôi kiểm tra (Lemma change-of-variables, well-posedness, mixture coupling, Prop. 1–2, Thm. 5) đúng và được viết cẩn thận, kể cả chi tiết thường bị bỏ qua (sự tồn tại của giới hạn yếu tại t=1, tính duy nhất của nghiệm continuity equation). Vấn đề là *độ sâu*: phần lớn nội dung là hệ quả trực tiếp của closed-form empirical velocity field đã có trong literature, áp dụng cho biến điều kiện. Tôi cũng thấy literature gần đây chưa được bao quát đủ.

### Strengths
- **S1 — Chứng minh sạch, tự chứa.** Lemma `lem:wellposed` loại bỏ giả định "flow well-defined" mà nhiều bài bỏ qua; cận Grönwall `|x_t|+M ≤ (|x_0|+M)/(1−t)` gọn.
- **S2 — Tách hai nhân tố của index posterior** (spatial × label kernel, Prop. 4) và chỉ ra chỉ nhân tố nhãn tồn tại đến t=1 (Prop. `prop:factors`) — một góc nhìn hữu ích, khác biệt rõ với Smola (2026).
- **S3 — Prop. 11 (interpolant noise bất biến)** với việc sửa target đạo hàm theo đường đi (eq. `c2target`) là một điểm kỹ thuật đúng mà nhiều implementation làm sai.

### Weaknesses
- **W1 — Novelty của Thm. 5 / Prop. 9.** Endpoint law dạng hỗn hợp trên atom là hệ quả tức thời khi đã có mixture coupling; atomicity là hệ quả tức thời của endpoint law. Reviewer theory ở main track sẽ đánh giá contribution là "straightforward extension of known closed-form results (Bertrand et al. 2025; Gao et al. 2024; Scarvelis et al. 2025) to the conditional case". *Suggestion*: đưa phần *không* hiển nhiên lên trước — Prop. `prop:survival` / Cor. `cor:lossform` (sai số chỉ sống sót nếu tích luỹ cỡ (1−t)⁻¹, cận theo loss còn lại), Prop. `prop:expansion` (khai triển h²JJᵀ). **Severity: Major (main).**
- **W2 — Literature gần đây còn thiếu.** Không thấy trong `refs.bib`: *A Theoretical Analysis of Memory and Overfitting Phenomena in Stochastic Interpolation Models* (arXiv 2606.08554) và *Tracing Generated Samples to Training-Data Clusters in Flow-Matching Models* (arXiv 2608.30081). Cả hai có vẻ rất gần với Thm. 5 và phân tích n_eff. *Suggestion*: đọc, so sánh, cập nhật Table 1. **Severity: Major** (có thể thành Critical nếu có trùng lặp đáng kể).
- **W3 — Giả định (iii) nhãn phân biệt.** Tự nhiên cho bài toán ngược với nhiễu liên tục, nhưng giới hạn giá trị với class-conditional/text-conditional — những thiết lập chiếm đa số ở ICLR. Cor. `cor:repeated` xử lý nhãn lặp nhưng main text chỉ nhắc một câu. *Suggestion*: nói rõ trong §1 rằng phạm vi là "identifying conditions" (inverse problems, inpainting), không phải class labels. **Severity: Minor.**
- **W4 — Kết quả CFG (§3.5) yếu so với vị trí của nó.** "Support nằm trong affine hull" rỗng khi N > d (bài tự nói), mà N > d là trường hợp thực tế ở synthetic; ở CIFAR thì N=2000 < d=3072 nên có nội dung. Nên nói rõ trường hợp nào áp dụng thực tế. **Severity: Minor.**

---

## Report 4 — R3 (Perspective: Bayesian inverse problems / scientific ML)

**Recommendation**: Minor Revision (workshop) / Major Revision (main)
**Confidence**: 3/5

### Summary Assessment
Từ góc nhìn người dùng CFM để lấy mẫu posterior trong bài toán ngược, câu hỏi thực tế là: *khi nào dừng huấn luyện, và làm sao biết mô hình đang lấy mẫu posterior hay đang trả lại dữ liệu huấn luyện?* Bài trả lời rõ phần thứ hai (tham chiếu `Cov_h`, n_eff, tỉ lệ off-atom, β) nhưng tự thừa nhận không trả lời phần thứ nhất (§3.7: "predicts the destination, not the speed"). Đóng góp thực tiễn lớn nhất — bộ chẩn đoán — lại nằm rải rác, không được đóng gói thành một quy trình.

### Strengths
- **S1** — Chỉ ra phép so sánh với Σ_post là sai tham chiếu, và rằng thực nghiệm "early stopping hoạt động" của physicscfm2026 có cơ chế rõ ràng (dòng 579–580).
- **S2** — Adversarial pairing (hoán vị Y) là thí nghiệm có sức thuyết phục cao với người làm ứng dụng: collapse không cần quan hệ thống kê thật giữa x và y (dòng 2877–2886).
- **S3** — Kết luận endpoint smoothing "bị đánh bại bởi chiều" giống KDE (dòng 2948–2952) là cảnh báo thực tế hữu ích.

### Weaknesses
- **W1 — Không có quy trình chẩn đoán đóng gói.** *Suggestion*: một Algorithm box "Auditing a conditional flow for memorisation": tính p^(h), n_eff, `Cov_h`, β, off-atom fraction; ngưỡng khuyến nghị; chi phí tính toán O(N·M). **Severity: Major** — đây là cách rẻ nhất để tăng impact.
- **W2 — Thiếu bài toán ngược thật.** Linear-Gaussian, GMM, MNIST/CIFAR inpainting đều là proxy. Một PDE inverse problem (ví dụ Darcy, như bối cảnh của physicscfm2026) sẽ nối bài với cộng đồng động lực ban đầu. **Severity: Minor (workshop) / Major (main).**
- **W3 — Không có câu trả lời vận hành cho "khi nào dừng".** Phụ lục `app:remedies` đo early stopping (tỉ số qua 0.98 ở h=6) nhưng không biến thành khuyến nghị. *Suggestion*: dùng n_eff hoặc β trên validation conditions làm tiêu chí dừng và thử nó. **Severity: Minor.**

---

## Report 5 — Devil's Advocate

### Strongest Counter-Argument (≈250 từ)
Luận điểm trung tâm là: *label smoothing không khôi phục posterior vì luật điểm cuối vẫn là atomic.* Nhưng chính bài cho thấy điều đó **không đúng với bất kỳ mô hình nào được huấn luyện thực tế**: ở CIFAR, tỉ lệ mẫu nằm trên atom là 0.829 / 0.717 / 0.620 tại h = 4 / 5 / 6 (dòng 2811), và ở EXP-1 phương sai dừng ở 0.40 thay vì 0 sau 2×10⁵ iter. Như vậy "Kernel smoothing over atoms does not restore the posterior" — tiêu đề — là phát biểu về một đối tượng (population minimiser trên tập cố định) mà không ai triển khai, trong khi đối tượng người ta triển khai lại *rời khỏi* các atom. Hoặc sự rời khỏi đó là generalization có ích (khi đó định lý chỉ nói điều gì sẽ xảy ra nếu tối ưu hoàn hảo — một kịch bản bài không cho thấy là đạt được ở quy mô thật), hoặc đó là sai số tối ưu (khi đó β và tỉ số chỉ đo "tối ưu đã đi được bao xa", như §3.6 nói — và vậy thì bài đang đề xuất một thước đo tiến độ tối ưu, không phải một kết luận về posterior). Cả hai cách đọc đều làm yếu claim ở tiêu đề. Thêm nữa, cơ chế collapse ở h=0 (nhãn xác định mẫu ⇒ loss = 0 tại δ) là hiển nhiên với bất kỳ ai viết ra E[U | X_t, Y]; giá trị mới phải nằm ở phần *tốc độ* và *mô hình hữu hạn* — đúng phần bài tự nhận là còn thiếu.

### Issue List
| # | Mức | Chiều | Vị trí | Vấn đề |
|---|---|---|---|---|
| DA-1 | **MAJOR** | Argument | Tiêu đề, abstract, §6 | Tiêu đề khẳng định về "the posterior" trong khi kết quả chỉ đúng cho population minimiser; mạng thật rời atom (38% off-atom). Cần hạ claim hoặc đổi tiêu đề. |
| DA-2 | **MAJOR** | Evidence | dòng 163, 651 vs Table `tab:cifarddpm` | Con số headline "aggregate 1.15" thực chất là median (xem R1-W1). Có nguy cơ bị đọc là trình bày chọn lọc. |
| DA-3 | **MAJOR** | Presentation / integrity | dòng 2748, 2954, 3020, 3050, 3354, 3760 | Phụ lục chứa nhật ký sửa bài ("An earlier version of this paper reported the opposite…", "reproduced verbatim from earlier versions of the main text"), kể cả lỗi Sinkhorn đã sửa. Trong bản nộp ẩn danh, điều này (a) gây nhiễu, (b) gợi ý tồn tại phiên bản công khai trước → rủi ro double-blind nếu có bản arXiv, (c) khiến reviewer nghi ngờ các số khác. Nên chuyển các correction thành phát biểu hiện tại, bỏ lịch sử. |
| DA-4 | MINOR | Overgeneralisation | §4.1 P7 | "Strongest empirical confirmation" dựa trên d=2 nơi floor chỉ 3.5% tr Σ_post — tức atomicity gần như không quan sát được ở chính nơi bài xác nhận lý thuyết mạnh nhất. |
| DA-5 | MINOR | Cherry-picking check | dòng 598 | h=0.01 bị bỏ khỏi main text (xem R1-W5). Có lý do hợp lệ nhưng phải nói. |
| DA-6 | MINOR | Logic | §3.6 | Cor. `cor:lossform` cần L_Δ ≥ δ⁻¹ − K, bài tự nói giả định này "demanding"; prefactor fit e^{L_Δ} ≈ 25 được bỏ qua. Kết quả vì thế gần như không kiểm chứng được. |

**Không có CRITICAL issue** → quyết định không bị chặn bởi Checkpoint Rule #4, nhưng DA-1 đến DA-3 phải được xử lý.

### Ignored Alternative Explanations / Paths
- Sự rời atom ở CIFAR có thể do *inductive bias của U-Net* (tính trơn theo biến điều kiện, như Pfrommer et al. 2025 tìm thấy) chứ không chỉ do tối ưu chưa xong. Bài chưa thí nghiệm để phân biệt hai giải thích (ví dụ so sánh kiến trúc ở cùng loss).
- Chưa xét regularisation phổ biến (weight decay, EMA, dropout) như những "remedy" thực tế mà người dùng thật sự bật.

### Missing Stakeholder Perspectives
- Người dùng mô hình text-/class-conditional (đa số cộng đồng ICLR): giả định nhãn phân biệt không áp dụng.
- Người quan tâm privacy/copyright: bài nêu trong Ethics nhưng không đo trích xuất dữ liệu.

### Observations (Non-Defects)
- Mức độ tự kiểm (audit script cho từng chứng minh, `docs/audit/`) vượt chuẩn thông thường.
- Việc sửa sai công khai (Sinkhorn) là hành vi khoa học tốt — vấn đề chỉ là *nơi* đặt nó.

---

## Phase 2 — Editorial Synthesis

### Ma trận đồng thuận
| Vấn đề | EIC | R1 | R2 | R3 | DA | Mức đồng thuận |
|---|---|---|---|---|---|---|
| Novelty toán học mỏng cho main track | ✔ W1 | — | ✔ W1 | — | ✔ (lập luận chính) | **Cao** |
| Lý thuyết ↔ mô hình hữu hạn chưa nối | ✔ W2 | ✔ W4 | — | ✔ W3 | ✔ DA-1 | **Cao** |
| Median/aggregate mâu thuẫn | — | ✔ W1 | — | — | ✔ DA-2 | Trung bình, nhưng **đã xác minh trong văn bản** |
| Trình bày quá dày / nhật ký sửa bài | ✔ W3 | — | — | — | ✔ DA-3 | Trung bình |
| Thiếu literature 2026 | — | — | ✔ W2 | — | — | Một reviewer, nhưng rủi ro cao |
| Cần quy trình audit đóng gói | ✔ S1 | — | — | ✔ W1 | — | Trung bình |
| Điểm mạnh: trung thực, chứng minh sạch, thông điệp audit | ✔ | ✔ | ✔ | ✔ | ✔ (obs.) | **Cao** |

### Bất đồng và phân xử
- **R3 (Minor) vs EIC/R2 (Major) cho workshop**: Ở workshop, novelty không phải tiêu chí chặn; phân xử theo R3 — *Minor Revision* là mức phù hợp cho workshop.
- **DA cho rằng claim tiêu đề sai về mô hình thật** vs **bài coi đó là "audit target"**: phân xử — lập luận của bài hợp lệ về mặt logic, nhưng tiêu đề và abstract chưa phản ánh phạm vi; yêu cầu sửa cách diễn đạt, không yêu cầu thêm kết quả.

### Điểm theo rubric (0–100, trọng số của skill)
| Chiều (trọng số) | Main track | Workshop |
|---|---|---|
| Originality (20%) | 58 | 70 |
| Methodological rigor (25%) | 74 | 78 |
| Evidence sufficiency (25%) | 66 | 75 |
| Argument coherence (15%) | 62 | 68 |
| Writing quality (15%) | 55 | 60 |
| **Weighted** | **64.2 → Major Revision** | **71.4 → Minor Revision** |

### Hiệu chỉnh theo thang ICLR
| | Soundness (1–4) | Presentation (1–4) | Contribution (1–4) | Rating (1/3/5/6/8/10) |
|---|---|---|---|---|
| EIC | 3 | 2 | 2 | 5 |
| R1 | 3 | 2 | 2 | 5 |
| R2 | 4 | 2 | 2 | 5 |
| R3 | 3 | 2 | 3 | 6 |
| DA | 3 | 2 | 2 | 3 |
| **Trung bình main track** | 3.2 | 2.0 | 2.2 | **4.8 → borderline reject** |

Với workshop (thang thường là 1–5 hoặc accept/reject): **Accept, khả năng cao** nếu sửa các mục P0 bên dưới.

### Editorial Decision
- **ICLR 2027 main track**: *Reject in current form* (tương đương Major Revision trong hệ journal).
- **ICLR 2027 Workshop (DeLTa hoặc tương đương)**: **Minor Revision → Accept**.

---

## Revision Roadmap (ưu tiên)

### P0 — Bắt buộc trước khi nộp (ít công, rủi ro cao)
1. **Sửa median/aggregate** (R1-W1, DA-2): dòng 163, 651, 684, 3052 và Table `tab:cifarddpm`. Báo cả hai con số, gọi đúng tên.
2. **Gỡ nhật ký sửa bài khỏi phụ lục** (DA-3): dòng 2748, 2954–2965, 3020–3030, 3050–3052, 3354, 3760. Giữ nội dung đã sửa, bỏ "an earlier version…". Kiểm tra không có bản arXiv/public trùng làm lộ danh tính.
3. **Đọc và định vị arXiv 2606.08554 và 2608.30081** (R2-W2); cập nhật Table 1 / `tab:related`.
4. **Báo β cho cả 3 seed CIFAR** (R1-W2) — dữ liệu đã có.

### P1 — Nên làm (tăng impact rõ rệt)
5. **Algorithm box "Memorisation audit for conditional flows"** (R3-W1, EIC-S1).
6. **Hạ claim tiêu đề/abstract** về population minimiser (DA-1); ví dụ tiêu đề dạng khẳng định về audit.
7. **Rút gọn** còn ~5 kết quả trong main text (EIC-W3); nói rõ phạm vi "identifying conditions" (R2-W3).
8. Một câu về h=0.01 trong main text (R1-W5, DA-5).

### P2 — Cho bản main track sau (ICML/NeurIPS 2027 hoặc TMLR)
9. Run CIFAR dài hơn ở h=4 để xem β có tiến về 1 không (R1-W4).
10. Một bài toán ngược PDE thật (R3-W2).
11. Thí nghiệm tách inductive bias kiến trúc vs sai số tối ưu (DA alt. explanation).
12. Kết quả lý thuyết về collapse time hoặc cận cho β (EIC-W2, R2-W1).
