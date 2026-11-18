# Chuẩn bị phản biện — 17/11/2026

**Căn cứ:**
- `paper/main.tex`: abstract, phần giới thiệu, ý (iii) "monitor late-time field error".
- `paper/drafts/sec_edm_draft.tex`.
- `docs/plan/next_venue_plan_2026-11-09.md`.
- `docs/plan/theory_extensions_2026-11-11.md`, gồm E, R, T1, T2, T3 và các bảng đo.
- `results/n3_*` (sub500, q, ϱ, T3, ablation số bước).

**Venue:** ICLR 2027 đã bỏ, đang nhắm venue tiếp theo. Mặc định coi đó là một hội nghị ML top (ICML/NeurIPS 2027).

**Đánh giá chung:**
- **Điểm mạnh:**
  - Phần toán chặt.
  - Các định lý mới (T1–T3) áp dụng cho denoiser bất kỳ và nhãn lớp, nên lấp được khoảng cách giữa lý thuyết identifying-label và thí nghiệm EDM.
  - Có một dự đoán được xác nhận trước (ablation số bước).
- **Ba rủi ro lớn nhất:**
  1. Baseline ảnh gần nhất ngang hoặc hơn tín hiệu của paper.
  2. Tiêu chí landing dùng ảnh được chọn *từ endpoint*, nên dễ bị đọc là vòng tròn.
  3. Quy mô thực nghiệm mới chỉ là CIFAR-10, một seed, 41 mẫu off-atom.

## 0. Cập nhật sau khi đo (17/11, `results/n3_robust_20261117/ROBUSTNESS.md`, `results/n3_anchor_20261117`)

Bootstrap phân tầng (B = 1000) trên sub500 (1.000 mẫu, 41 off-atom). Hiệu AUC được tính theo cặp, trên cùng một lần lấy mẫu lại.

- **W2 (vòng tròn) đã được trả lời.**
  - ϱ neo tại σ_k, tức ảnh gần nhất của D(x_k) và không dùng thông tin endpoint, cho AUC trùng với ϱ neo theo endpoint ở mọi σ (0,884 [0,843, 0,917] ở σ = 8,4; 0,974 ở σ = 5,3; 1,000 từ σ ≤ 1,09).
  - Ảnh neo tại σ_k trùng ảnh của endpoint ở 50% mẫu on-atom tại σ = 19,4, 90% tại σ = 8,4, 97% tại σ = 5,3, và ≥ 99,4% từ σ ≤ 3,3.
  - Vậy các bảng AUC không phụ thuộc vào việc chọn neo từ endpoint.
- **W1 (baseline) đã được định lượng.**
  - e_learned (|D − m*|) thua nn_hat có ý nghĩa ở σ 3,3–19,4. Ví dụ ở σ = 8,4, hiệu là −0,074 [−0,099, −0,049]. Từ σ ≤ 1,9 thì ngang nhau.
  - Ngược lại, tỉ số xuyên tâm radA (neo tại σ_k) **thắng** nn_hat ở σ = 19,4: 0,796 so với 0,689, hiệu +0,106 [0,056, 0,159]. Kết quả này đúng với cả ba ngưỡng.
  - Ở σ = 12,9 thì ngang (+0,017 [−0,009, 0,043]). Ở σ 5,3–8,4 radA thua nhẹ (khoảng −0,01).
  - Kết luận: chỉ có một lợi thế sớm và khiêm tốn. Không đủ để bán như một detector, nhưng đủ để nói rằng đại lượng theo hướng (T1) mang thông tin mà khoảng cách thuần không có ở σ lớn.
- **W9 (ngưỡng) đã được trả lời.** Với ngưỡng 0,2, 1/3 và 0,5, số mẫu off-atom là 46, 41, 39. Mọi AUC và mọi kết luận về dấu của hiệu giữ nguyên.

## 1. Bảng điểm yếu

| # | Loại | Điểm yếu | Mức | Trạng thái / cách xử lý |
|---|---|---|---|---|
| W1 | Thực nghiệm | nn_hat (khoảng cách tới ảnh train gần nhất) dự đoán memorization tốt bằng hoặc hơn e_learned ở mọi t (0,959 so với 0,885 ở t = 0,11; cùng 1,000 từ t = 0,34). Ý (iii) "monitor late-time field error" của abstract không đứng vững như một detector. | **Cao** | Đổi framing: sai số theo field là *cơ chế* (vì sao hạ cánh), không phải detector. Báo baseline trung thực. |
| W2 | Kỹ thuật | ϱ và rad₁ đo so với y₁ = ảnh gần nhất *của endpoint*. Reviewer sẽ nói "AUC 1,000 vì nhãn on/off cũng tính từ endpoint". | **Cao** | Cần biến thể dự báo: neo vào ảnh gần nhất của D(x,σ) tại σ ≈ 1–2, chỉ dùng thông tin đến thời điểm đó. Chưa chạy, rẻ (forward-only). |
| W3 | Trình bày | T1(a) là một đồng nhất thức (phép chiếu xuyên tâm của ODE), nên "rad₁ dự đoán đúng Δlog n (−2,01 so với −2,01)" là hiển nhiên, không phải bằng chứng. | Trung bình–cao | Trình bày như một phân rã (nhóm nào đóng góp mức co nào), không gọi là "dự đoán". Phần có nội dung là ϱ < 1 (T1(b)) và chứng chỉ T3. |
| W4 | Thực nghiệm | Một dataset (CIFAR-10 32×32), một seed sub500, 41 mẫu off-atom. Model public không có mẫu on-atom nào. | **Cao** | Đang chạy: sub2000 (chế độ trung gian) và sub500 seed 1. Còn thiếu: bootstrap CI cho AUC và một dataset thứ hai (ví dụ CelebA-64 hoặc AFHQ-64 với tập con nhỏ). |
| W5 | Trình bày | Paper đang là hai paper: (A) can thiệp lên exact field (nhiễu nhãn, guidance, composition) và (B) sai số muộn của field đã học trên EDM. main.tex dài 3.717 dòng, bản ICLR vượt 9 trang (N6). | Cao | Chọn một câu chuyện chính. Đề xuất: (A) là nền, (B) là phần thực nghiệm chính, composition vào phụ lục (xem mục 4). |
| W6 | Trình bày | `sec_edm_draft.tex` đã lỗi thời. Đoạn "Why a trained EDM network does not land" mâu thuẫn với sub500 (95,9% hạ cánh). Các số μ dựa trên model public, và μ không tách on/off ở cuối (AUC ≈ 0,5). | Cao | Viết lại mục EDM quanh T1 và T3 (mục 4). Giữ μ làm kết quả âm có giải thích. |
| W7 | Novelty | T3 dựa trên bất đẳng thức tam giác cho dạng affine của bước Heun. Reviewer lý thuyết có thể gọi là "straightforward". Ngưỡng μ = 1 gần với attractor criterion của López-Amado 2026; vùng chọn ảnh ở σ trung bình gần Dodson 2026. | Trung bình | Nhấn vào thứ chưa ai có: chứng chỉ theo từng quỹ đạo kiểm được trên dữ liệu, hằng số sắc nét c*, dự đoán số bước được xác nhận. Viết rõ phần related work. |
| W8 | Kỹ thuật | Chứng chỉ T3 thất bại ở 3 bước cuối của lịch EDM mặc định 18 bước. ϱ → 0,99 ở cuối, nên dữ liệu chỉ ủng hộ hạ cánh tới tiêu chí d₁/d₂ < 1/3, không phải hạ cánh chính xác. | Trung bình | Đã có câu trả lời: ablation 36/64 bước cho chứng chỉ phủ mọi bước với 99,5% mẫu. Nói rõ giới hạn "hạ cánh tới tiêu chí". |
| W9 | Kỹ thuật | Ngưỡng off-atom d₁/d₂ ≥ 1/3 do mình chọn. Chưa có độ nhạy theo ngưỡng, chưa có metric kiểu SSCD. | Trung bình | Thêm độ nhạy theo ngưỡng (0,2 / 1/3 / 0,5) từ dữ liệu sẵn có. Rẻ. |
| W10 | Kỹ thuật | ϱ cần exact field, tức một tổng trên toàn bộ tập train ở mỗi bước. Không dùng được khi deploy. | Thấp–trung bình | Đã nói ở ý (iii) ("suits audits"). Giữ nguyên. |
| W11 | Trình bày | Placeholder và TODO: OpenReview `XXXX`, `% CHECK` ở mục khai báo LLM, bib TODO trong bản nháp EDM (dodson2026, lopezamado2026, kwon2022score, jaziri2026), nhãn tham chiếu TODO. | Trung bình | Chạy citation check trước khi nộp (N5, N7). |
| W12 | Kỹ thuật | Chứng minh E, R, T1, T2, T3 mới qua kiểm chứng đối kháng, tác giả chưa kiểm. | Trung bình | Tác giả kiểm tra trước khi đưa vào bản nộp. |
| W13 | Thực nghiệm | Chưa có so sánh với cách giảm memorization trong thực tế (ví dụ guidance interval, giảm memorization lúc sampling kiểu Wen et al. 2024) dưới góc nhìn ϱ. | Thấp–trung bình | Tùy chọn. Có thể bỏ qua nếu paper tập trung vào cơ chế. |

## 2. Mười câu hỏi reviewer dễ hỏi nhất

**Q1. Tín hiệu của các anh có tốt hơn khoảng cách tới ảnh train gần nhất không?** (W1)
- *Vì sao hỏi:* đây là baseline rẻ nhất, và abstract đang bán ý "monitor late-time field error".
- *Trả lời bằng dữ liệu sẵn có:* được, với một câu trả lời trung thực. Không tốt hơn (nn_hat ≥ e_learned ở mọi t, `N3_SUMMARY`).
- *Nháp:* "We do not claim a better detector. At late times the field error and the nearest-image distance coincide up to an exponentially small term (Lemma R), so no detector built on them can beat the nearest-image baseline there. Our claim is mechanistic: Theorem T1 shows that landing on a training image happens if and only if the relative field error stays below one, and the swap experiment shows that replacing only the late field changes memorization from 0% to 100%."

**Q2. ϱ được tính so với ảnh gần nhất của endpoint. Phải chăng đây là vòng tròn?** (W2)
- *Vì sao hỏi:* nhãn on/off cũng tính từ endpoint.
- *Trả lời bằng dữ liệu sẵn có:* chỉ một phần. T1 là phát biểu với *mọi* ảnh i cố định, nên phần lý thuyết không vòng tròn. Nhưng các AUC trong bảng thì có. Cần chạy biến thể dự báo: neo vào ảnh gần nhất của D(x,σ) tại σ ≈ 1–2.
- *Nháp (sau khi chạy):* "Anchoring at the nearest image of the denoiser output at σ = σ₀, using no information after σ₀, gives AUC … at σ₀ = …; the anchor agrees with the endpoint image for …% of on-atom samples."

**Q3. Đồng nhất thức xuyên tâm "dự đoán đúng" Δlog n. Chẳng phải đó chỉ là ODE sao?** (W3)
- *Trả lời bằng dữ liệu sẵn có:* được. Thừa nhận đó là đồng nhất thức. Phần thực nghiệm có nội dung là ϱ < 1 với 100% mẫu on-atom ở mọi bước, trong khi mẫu off-atom có ϱ → 1 từ σ ≈ 0,14; cộng với kiểm chứng chặn T3 không bị vượt trên 1.500 quỹ đạo.

**Q4. Chỉ CIFAR-10, một seed, 41 mẫu off-atom. Kết quả có tổng quát được không?** (W4)
- *Trả lời bằng dữ liệu sẵn có:* một phần. sub2000 và sub500 seed 1 đang chạy, khoảng 1 ngày. Còn cần bootstrap CI và một dataset thứ hai.

**Q5. Các định lý chính cần identifying label. Thí nghiệm EDM dùng nhãn lớp. Lý thuyết nào thực sự áp dụng?** (W5, W6)
- *Trả lời bằng dữ liệu sẵn có:* được. T1–T3 áp dụng cho denoiser D bất kỳ, trọng số hậu nghiệm bất kỳ (gồm nhãn lớp) và mọi ảnh i, không cần identifying label. Đây là cầu nối mà Prop. localtransfer chưa làm được. Cần viết rõ điều này trong bài.

**Q6. Vì sao μ (giá trị riêng lớn nhất của Jacobian) không tách được on/off ở cuối, trong khi lý thuyết dựa vào Jacobian?** (W6)
- *Trả lời bằng dữ liệu sẵn có:* được (`MU_SUMMARY`, Prop. E). μ đo hướng xấu nhất, còn việc hạ cánh phụ thuộc vào độ co *theo hướng tới ảnh* (độ dốc cát tuyến q, Prop. E), hướng mà μ không thấy. Đây là một kết quả âm có giải thích: nó cho thấy cần đại lượng theo hướng.

**Q7. T3 có gì mới ngoài bất đẳng thức tam giác?** (W7)
- *Trả lời bằng dữ liệu sẵn có:* được.
  1. Dạng affine của Heun có trọng số âm khi r < 1/2, nên bước cuối có thể vượt qua ảnh (p < 0 với r < 3 − 2√2).
  2. Hằng số sắc nét c* cho thấy chặn theo chuẩn bị lỏng đúng khi r < 1/2.
  3. Một dự đoán định lượng được xác nhận: từ 36 bước trở lên, chứng chỉ phủ mọi bước với 99,5% mẫu, trong khi memorization và ảnh được chọn giữ nguyên 99,3–99,4%.

**Q8. Ngưỡng 1/3 có tùy tiện không? Kết quả có nhạy với ngưỡng không?** (W9)
- *Trả lời bằng dữ liệu sẵn có:* được, tính lại từ `per_sample.npz` với các ngưỡng 0,2 và 0,5. Chưa làm, mất vài phút.

**Q9. Network chỉ chọn trùng ảnh với exact field 35,8%. Vậy exact field có ý nghĩa gì với một model thật?** (Prop. T, swap)
- *Trả lời bằng dữ liệu sẵn có:* được. Exact field là thước đo cho *việc hạ cánh*, không phải cho *việc chọn ảnh nào*. Swap net→exact cho thấy ảnh do network chọn sớm: tới σ = 5 đã trùng 92,8%, và hai đồng hồ "chọn ảnh" và "hạ cánh" tách nhau.

**Q10. Kết quả này giúp gì cho người thực hành giảm memorization?**
- *Trả lời bằng dữ liệu sẵn có:* một phần.
  - Các núm sampling (nhiễu nhãn, guidance) chỉ đổi trọng số giữa các ảnh train (phần A).
  - Việc hạ cánh do field ở cuối quyết định, nên can thiệp phải tác động vào field muộn hoặc vào lịch bước.
  - T3 cho thấy lịch bước thô ở cuối làm yếu đảm bảo co.
  - Chưa có thí nghiệm can thiệp thực sự làm *giảm* memorization theo hướng này. Nếu có thời gian, đây là thí nghiệm có giá trị nhất cho reviewer thực hành, ví dụ làm mềm field ở σ < 0,1 rồi đo memorization và FID.

Câu hỏi phụ có thể gặp: chi phí tính exact field (W10); vì sao dùng Heun mà không dùng sampler ngẫu nhiên (T3 chỉ áp dụng cho sampler tất định); quan hệ với Gu et al. 2023 và Kadkhodaie et al. 2024.

## 3. Tập ablation đề xuất

| Thứ tự | Ablation | Chứng minh điều gì | Đặt ở đâu | Có sẵn? |
|---|---|---|---|---|
| 1 | **Swap field** (net→exact, exact→net theo s) | Claim lõi: việc hạ cánh do field muộn quyết định; thay field trên 2% thời gian cuối đưa memorization từ 0% lên 100% | Bài chính | Có (public, sub1000, sub500) |
| 2 | **ϱ và rad₁ theo σ, on/off, cạnh baseline nn_hat** | T1 trên dữ liệu: on-atom có ϱ < 1 ở mọi bước, off-atom và public có ϱ → 1. Đặt cạnh baseline để trả lời trước Q1 | Bài chính | Có, nhưng thiếu biến thể dự báo (Q2) |
| 3 | **Số bước Heun 18/36/64** | Dự đoán T3 được xác nhận; memorization không đổi | Bài chính (bảng nhỏ) | Có |
| 4 | **Thang N** (sub500, sub2000, public 50k) | Tín hiệu đi từ "memorize gần hết" tới "không memorize"; trả lời Q4 | Bài chính | sub2000 đang train |
| 5 | **Seed thứ hai** (sub500 s1) | Độ biến thiên | Phụ lục | Đang train |
| 6 | **μ không tách được ở cuối** (kết quả âm) | Vì sao cần đại lượng theo hướng (Prop. E) | Phụ lục, một câu ở bài chính | Có |
| 7 | **Chặn T3 không bị vượt** (1.500 quỹ đạo × 17 bước) và phần sửa sai số cầu phương của q | Kiểm tra độ đúng | Phụ lục | Có |
| 8 | Độ nhạy theo ngưỡng off-atom, bootstrap CI | Độ vững | Phụ lục | Chưa, rẻ |

Thứ tự trình bày: 1 → 2 → 3 → 4. Swap cho thấy *cái gì* quyết định, ϱ cho thấy *đại lượng nào*, số bước cho thấy *lý thuyết dự đoán đúng*, thang N cho thấy *tổng quát*.

**Kết quả âm nên giữ, viết như phân tích:**
- μ không tách on/off ở cuối.
- e_learned không vượt nn_hat.
- q cầu phương 4 điểm bị thổi phồng ở σ 0,1–1.
- Chứng chỉ theo chuẩn thất bại ở các bước r < 1/2.

## 4. Đề xuất sửa văn bản

**(a) Abstract, câu về ý (iii).** Hiện tại abstract nói sai số theo field "is what moves a learned sampler off the training set", và phần thực hành nói "monitor late-time field error… separates… with AUC at least 0.95". Sửa theo hướng:
> "…whether a learned sampler lands on a training image is decided late: along EDM trajectories a sample lands exactly when its field error stays below its distance to the image (relative error < 1), a criterion we prove for any denoiser and verify on every step of every trajectory. As a detector, the field error is no better than the distance to the nearest training image, with which it coincides late."

**(b) Mục EDM: viết lại `sec_edm_draft.tex`.**
- Bỏ đoạn "Why a trained EDM network does not land". Nó đúng cho model public nhưng sai cho sub500, và các số μ trong đó là của sub1000 hoặc public.
- Cấu trúc mới:
  1. Swap: hai đồng hồ "chọn ảnh" và "hạ cánh".
  2. Định lý T1 (sai số tương đối) với bảng ϱ.
  3. Định lý T3 (sampler Heun) với bảng số bước.
  4. μ là kết quả âm, kèm Prop. E.
  5. Thang N.

**(c) Phần giới thiệu, gạch đầu dòng thứ hai** ("Learned fields leave only through late-time error"):
- Thêm một câu: T1–T3 không cần identifying label và áp dụng cho sampler rời rạc thực tế. Đây là chỗ trả lời Q5.

**(d) Limitations:** nêu rõ bốn điểm:
- Dữ liệu chỉ ủng hộ hạ cánh tới tiêu chí d₁/d₂ < 1/3, chưa phải hạ cánh chính xác (ϱ → 0,99).
- ϱ cần exact field.
- Một dataset.
- Sampler tất định.

**(e) Related work:** viết rõ ranh giới với López-Amado 2026 (attractor criterion tại σ cố định, so với chứng chỉ theo quỹ đạo của paper), Dodson 2026 (memorization ở σ trung bình, so với hai đồng hồ) và Jaziri 2026 (phổ Jacobian, so với độ co theo hướng). Chạy citation check cho 4 khóa bib TODO.

## 5. Việc nên làm trước khi nộp, theo thứ tự lợi ích / chi phí

1. Biến thể ϱ dự báo, neo tại σ₀ (Q2). Forward-only, vài phút GPU. **Quan trọng nhất.**
2. Bootstrap CI cho AUC và độ nhạy theo ngưỡng (Q4, Q8). Chạy local từ npz sẵn có.
3. Chờ sub2000 và sub500 seed 1 (đang chạy), rồi chạy lại bộ đo ϱ và T3 trên chúng.
4. Viết lại mục EDM và abstract theo mục 4. Tác giả kiểm tra E, R, T1–T3.
5. Tùy chọn, giá trị cao cho reviewer thực hành: một can thiệp vào field muộn để giảm memorization (Q10).
6. Tùy chọn: một dataset thứ hai.
