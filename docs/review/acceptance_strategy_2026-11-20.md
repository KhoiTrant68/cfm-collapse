# Chiến lược để được accept tại ICLR / ICML / NeurIPS (2026-11-20)

Tài liệu này là kết quả deep-research ở chế độ `quick`, tổng hợp từ ba nguồn:
- hai luồng tìm kiếm web: quy định của từng venue, và các bài đã được accept trong cùng mảng;
- bản review mô phỏng `docs/review/simulated_review_iclr_2026-11-20.md`;
- việc đối chiếu `paper/main.tex` và `paper/refs.bib`.

Mọi fact về venue đều có URL ở mục 6. Những gì chưa xác minh được đánh dấu UNVERIFIED.

---

## 1. Lịch thực tế: ICLR 2027 đã đóng

| Venue | Deadline | Giới hạn trang | Ghi chú |
|---|---|---|---|
| ICLR 2027 | Đã đóng (full paper 25/09/2026). Decision 16/12/2026 | 9 (10 khi camera-ready) | Nếu bài *đã nộp*, lúc này không được nộp song song ở nơi khác |
| **ICML 2027** | Abstract 14/01/2027, full paper **22/01/2027** | **8** trang | Review hai vòng: AC có thể reject ngay ở vòng 1. Bắt buộc có reciprocal reviewer. Bắt buộc AI Disclosure Statement |
| **NeurIPS 2027** | Chưa công bố (UNVERIFIED). Theo NeurIPS 2026, có thể khoảng đầu tháng 5/2027 | 9 trang | Từ 2026 tác giả chọn **contribution type**. Loại **Theory** "shouldn't be penalized for lacking experiments" |
| **TMLR** | Nộp liên tục | Không giới hạn | Tiêu chí: claim có bằng chứng và có người quan tâm. Significance và novelty *không* là lý do reject |
| TMLR → **J2C** | Hạn J2C cho ICLR 2027 là 18/12/2026 (không kịp). NeurIPS 2027 và ICML 2027 sẽ có hạn J2C riêng | — | Cần có chứng nhận J2C/Featured/Outstanding. Mỗi hội nghị tối đa 150 bài. Paper được trình bày tại ICLR/NeurIPS/ICML |

Tỉ lệ accept: ICLR 2026 27.4%, ICML 2026 26.6%, NeurIPS 2025 24.5%. ICLR 2027 có tin là trên 60k submission (UNVERIFIED).

---

## 2. Bài được accept hay award trong mảng này có gì?

Các bài được đối chiếu đều đã xác minh qua arXiv hoặc trang venue:
- Kadkhodaie et al.: ICLR 2024, Outstanding Paper.
- Bonnaire et al.: NeurIPS 2025, **Best Paper**.
- Kamb & Ganguli: ICML 2025, oral.
- Bertrand et al.: NeurIPS 2025, oral.
- Wen et al.: ICLR 2024, oral.

Chúng có chung năm đặc điểm:

1. **Một cơ chế duy nhất cộng một dự đoán định lượng, đo được trên mạng đã train.** Ví dụ: τ_mem ∝ n; r² ≈ 0.9 khi dự đoán từng ảnh; hai model train trên hai nửa dữ liệu rời nhau học ra cùng một score.
2. **Giải thích vì sao model *đã train* không memorize**, thay vì nhắc lại rằng exact optimum memorize. Điều sau giờ được coi là kiến thức chung: Biroli 2024, Gao & Li 2024, Scarvelis, Bertrand 2025.
3. **Nếu có claim thực tiễn thì thí nghiệm vượt quy mô CIFAR-subset**: SD/SDXL, ImageNet-512.
4. **Một thông điệp, thường kèm một lợi ích thực tế**: quy tắc early stopping, guidance interval, một metric phát hiện memorization.
5. **Phân tích exact-score kiểu vật lý chỉ được award khi gắn với hành vi của mạng thật.** Biroli 2024 (chỉ có exact score) được đăng ở Nature Communications, không phải ở một venue ML.

**Đối chiếu với bài hiện tại.** Bài làm tốt (5) ở phần lý thuyết. Bài yếu ở (1), (3) và (4): phần EDM không có dự đoán nào vượt được baseline nearest-neighbour, và thông điệp bị chia thành 6 mạch.

---

## 3. Bản đồ rủi ro novelty (phải xử lý trong Related Work)

| Bài (đã xác minh) | Trùng với claim nào | Đã cite? | Việc cần làm |
|---|---|---|---|
| Bertrand et al., NeurIPS 2025 oral, "On the Closed-Form of Flow Matching" | Exact FM chỉ tái tạo điểm train; generalization đến từ lỗi fit; **xảy ra sớm** trên quỹ đạo | Có (`bertrand2025closed`) | **Đối thoại trực tiếp.** Bài này nói *sớm*, bài của bạn nói *muộn*. Phần EDM thực ra dung hòa được hai ý: chọn ảnh sớm, landing muộn. Hãy biến điểm này thành selling point |
| Bonnaire et al., NeurIPS 2025 **Best Paper** | Memorization phụ thuộc thang thời gian train và n | **Chưa** | Cite. Liên hệ với collapse ở EXP-1 sau khoảng 10⁴ iteration |
| Biroli et al., Nat. Comm. 2024 | Speciation sớm, collapse muộn (exact score) | Vừa thêm | Định vị rõ: họ phân tích exact score, bạn đo trên quỹ đạo của mạng |
| Gao & Li, arXiv 2024 | Exact FM field memorize | Có | — |
| Gu et al., TMLR 2025 | EMM trên EDM CIFAR-10; random label kích hoạt memorization | Có (`gu2023memorization`) | Thảo luận khía cạnh conditioning |
| Jain et al., CVPR 2025 | CFG trong attraction basin; delayed/negative guidance | Có | Nói rõ: bài của bạn là phiên bản exact-field chặt chẽ cho kết quả thực nghiệm của họ |
| Kim et al., arXiv 2509.25705 (comment ghi NeurIPS 2026) | Lý thuyết CFG khuếch đại memorization | **Chưa** | Kiểm tra kỹ rồi cite. Rủi ro trùng cao nhất ở phần guidance |
| Li et al., arXiv 2602.07928 (comment ghi ICML 2026 Spotlight), "Kinetic Energy Perspective of FM" | Closed-form FM; "late-time soft landing" | **Chưa** | Đọc và cite. Trùng trực tiếp với ý "late-time" |
| Shah et al. 2025; Favero et al. (TMLR); Wu et al. 2025 | Memorization quyết định ở noise thấp | **Chưa** | Cite. Đây là bằng chứng *ủng hộ* bạn |
| Kaiser & Kollmann, arXiv 2026 | Khoảng cách train/val xuất hiện ở noise **trung bình** | **Chưa** | Phản chứng tiềm năng; cần trả lời |
| Bradley & Nakkiran, TMLR 2025 | CFG với exact denoiser có hiệu ứng regularize | **Chưa** | Có thể bị đọc là mâu thuẫn với "guidance vẫn trên atom". Cần giải thích (khác setting) |
| Pham et al. 2025; Aithal et al., NeurIPS 2024 | Basin, spurious attractor; mode interpolation (blend) | **Chưa** | Liên hệ với basin circumcentre |
| Wen et al. ICLR 2024; Chen et al. CVPR 2024 (AMG); Raya & Ambrogioni 2023; Sclocchi et al. PNAS 2025; Li & Chen ICML 2024 | Detect/mitigate; critical windows | Phần lớn **chưa** | Cite |

**Novelty có thể bảo vệ được.** Luồng tìm kiếm không thấy định lý nào đã công bố về:
- exact **conditional** FM field dưới label noise, label averaging, hoặc CFG schedule có bounded variation;
- ngưỡng dạng w > 1/sinh²B cho basin tại điểm blend;
- tiêu chí phổ (spectral) cho tổ hợp có dấu.

Đây là phần mới thật sự. R1 cũng đã xác nhận các chứng minh tương ứng là đúng.

**Phần dễ bị tấn công nhất** là claim "chỉ rời training set qua late-time error". Nó bị kẹp giữa Bertrand (sớm), Biroli, Shah/Favero và Kinetic-FM.

---

## 4. Hai con đường (chọn một, hoặc tách bài)

### Đường T: bài lý thuyết
Đích: **NeurIPS 2027, contribution type Theory**, hoặc **TMLR rồi J2C**.

- **Thông điệp.** "Sampler-side interventions on the exact conditional field: what keeps and what breaks atomic endpoints". Đóng góp chính gồm:
  - Lemma signedconv, giải quyết trường hợp mà Remark 3.19 của Liu et al. để ngỏ;
  - atomicity dưới guidance và schedule;
  - ngưỡng composition;
  - tiêu chí phổ trong mọi chiều.
- **Nâng significance.** Nối tiêu chí phổ với các tổ hợp có dấu được dùng thật trong thực tế: negative prompt, compositional/multi-prompt CFG (Composable Diffusion, Liu et al. ECCV 2022), autoguidance. Bài đã nêu rằng kết quả "fails for some signed combinations of more than two fields". Đó chính là câu hỏi mà practitioner có.
- **Cần làm:**
  - Đưa spectral theorem và phần so sánh với Liu et al. lên main text.
  - Rút phần EDM còn khoảng 1 trang, hoặc chuyển sang appendix.
  - Thêm positive control cho stress test.
  - Remark về tính generic của giả thiết trong Thm spectral(c).
  - Ba lần chạy exact-field cho compositional CFG với 3 field trở lên (chi phí rẻ).
- **Ưu điểm:** NeurIPS ghi rõ bài lý thuyết không bị phạt vì thiếu thí nghiệm, và tiêu chí chính là tính đúng. Theo R1, các chứng minh đã đúng. TMLR coi bản hiện tại gần như sẵn sàng.
- **Rủi ro:** reviewer vẫn có thể hỏi "so what?". Phần nối với compositional CFG là để trả lời câu hỏi đó.

### Đường E: bài về cơ chế
Đích: **ICML 2027 (22/01, 8 trang)** hoặc **NeurIPS 2027, contribution type General**.

- **Thông điệp.** "Trained samplers select early and land late: late-time relative contraction decides replication". Phải định vị cùng lúc so với Bertrand (sớm) và Biroli (exact score).
- **Bắt buộc có dự đoán định lượng falsifiable trên mạng thật**, đúng điều mà các bài award đều có:
  1. Swap exact→net trên mọi model. Kết quả đã có trong `results/n3_followup_*`: giao ở s=1 thì off-atom 95.6%, giao ở s=0.1 thì 0.2%. Từ đó dự đoán *σ tại đó model bắt đầu không co*.
  2. Can thiệp: chỉ thay field trong cửa sổ σ mà ϱ chỉ ra, rồi dự đoán tỉ lệ memorization *trước khi chạy*.
  3. Lưới N ∈ {500, 1k, 2k, 5k} × 3 seed, tách subset seed khỏi training seed, thêm một model có augmentation. So τ_mem với Bonnaire.
  4. CFG thật: train EDM với class dropout, quét w, guidance interval và delayed guidance. Đây là thí nghiệm mà title đòi hỏi.
  5. Giá trị gia tăng so với NN baseline (logistic, ΔAUC). Nếu không có thì không được gọi C là detector.
  6. Ít nhất một bước quy mô: ImageNet-64 hoặc CIFAR-10 đầy đủ, với model train bằng CFM loss.
- **Ưu điểm:** nếu (1)–(3) cho kết quả sạch thì đây là kiểu bài mà ICLR/NeurIPS thường chọn.
- **Rủi ro:** khối lượng tính toán lớn. 8 trang ICML trong 2 tháng là rất chật.

### Khuyến nghị
1. **Hỏi trước tiên:** bài đã nộp ICLR 2027 chưa? Nếu đã nộp thì đang trong giai đoạn AC thảo luận (đến 16/12). Không được nộp song song ở venue khác. Các sửa đổi đang làm chỉ dùng được cho camera-ready hoặc lần nộp sau.
2. Nếu chưa nộp ở đâu, cách có xác suất cao nhất là **tách bài**:
   - Phần lý thuyết (Đường T) nộp **TMLR** ngay, nhắm chứng nhận J2C/Featured để được trình bày tại NeurIPS 2027 hoặc ICLR 2028.
   - Phần cơ chế (Đường E) phát triển thành bài cho **NeurIPS 2027**.
   - Lưu ý: hai bài phải khác nhau đáng kể, tránh thin slicing (NeurIPS cấm).
3. **Không khuyên nộp ICML 2027 với bài hiện tại.** Giới hạn 8 trang kết hợp vòng desk reject của AC rất bất lợi cho một bài có khoảng 20 statement và 6 mạch.

---

## 5. Điều kiện bắt buộc ở mọi venue (không làm thì có thể bị desk reject)

- **Khai báo LLM.** ICLR 2027 *bắt buộc* khai báo việc dùng LLM để "formulating mathematical claims", nên bản nháp chứng minh do model tạo thuộc diện phải khai. Câu hiện tại trong `main.tex` đã được sửa theo hướng đó; tác giả cần xác nhận. ICML 2027 cũng bắt buộc AI Disclosure Statement.
- **Trích dẫn ảo bị desk reject** (đã có tiền lệ ở ICLR 2026). Cần kiểm tra mọi key năm 2026 trong `refs.bib` qua DBLP/arXiv, ví dụ `liu2026geometric`, `smola2026support`, `dodson2026calm`, `lopezamado2026modes`, `jaziri2026spectral`, `verma2026early`, `physicscfm2026`, `sesmat2026leaks`, `li2026memory`, `beltran2026reward`. Gợi ý dùng `labrat:paper-check`.
- **Reciprocal reviewer.** ICLR, ICML và NeurIPS đều yêu cầu một tác giả đủ điều kiện đăng ký review.
- **NeurIPS checklist.** Error bars phải nói rõ là std hay std-error và tính thế nào. Bài hiện dùng population std với n=5, nên đổi sang CI. Bắt buộc có proof sketch trong main text cho các kết quả có chứng minh ở appendix.
- **Giới hạn trang.** Vượt là desk reject. ICLR: 9 trang. ICML: 8 trang.
- **Dual submission.** Nộp song song TMLR và hội nghị bị coi là vi phạm (suy luận từ quy định; các trang không nêu tên TMLR). Workshop non-archival thì được phép.

---

## 6. Nguồn

**Venue**
- ICLR 2027 Dates: https://www.iclr.cc/Conferences/2027/Dates
- ICLR 2027 Call for Papers: https://iclr.cc/Conferences/2027/CallForPapers
- ICLR 2027 Author Guidelines: https://iclr.cc/Conferences/2027/AuthorGuidelines
- ICLR 2027 AI Policy for Authors: https://iclr.cc/Conferences/2027/AIPolicyForAuthors
- ICLR 2027 Reviewer Guidelines: https://iclr.cc/Conferences/2027/ReviewerGuidelines
- Nhìn lại ICLR 2026: https://blog.iclr.cc/2026/03/31/a-retrospective-on-the
- ICML 2027 Call for Papers: https://icml.cc/Conferences/2027/CallForPapers
- ICML 2027 Reciprocal Reviewing and Submission Quotas: https://icml.cc/Conferences/2027/ReciprocalReviewingAndSubmissionQuotas
- ICML 2026 Reviewer Instructions: https://icml.cc/Conferences/2026/ReviewerInstructions
- NeurIPS 2026 Dates: https://neurips.cc/Conferences/2026/Dates
- NeurIPS 2026 Main Track Handbook: https://neurips.cc/Conferences/2026/MainTrackHandbook
- NeurIPS 2026 Reviewer Guidelines: https://neurips.cc/Conferences/2026/ReviewerGuidelines
- NeurIPS Paper Checklist: https://neurips.cc/public/guides/PaperChecklist
- NeurIPS 2025, nhìn lại quy trình review: https://blog.neurips.cc/2025/09/30/reflections-on-the-2025-review-process-from-the-program-committee-chairs/
- NeurIPS 2026 Journal Track: https://blog.neurips.cc/2026/10/15/announcing-the-neurips-2026-journal-track/
- TMLR Acceptance Criteria: https://jmlr.org/tmlr/acceptance-criteria.html
- TMLR Reviewer Guide: https://jmlr.org/tmlr/reviewer-guide.html
- TMLR Editorial Policies: https://jmlr.org/tmlr/editorial-policies.html
- Journal-to-Conference track: https://neurips.cc/public/JournalToConference

**Bài liên quan**
- Kadkhodaie et al.: https://arxiv.org/abs/2310.02557
- Kamb & Ganguli: https://arxiv.org/abs/2412.20292
- Bonnaire et al.: https://arxiv.org/abs/2505.17638 (best paper: https://blog.neurips.cc/2025/11/26/announcing-the-neurips-2025-best-paper-awards/)
- Biroli et al.: https://arxiv.org/abs/2402.18491
- Bertrand et al.: https://arxiv.org/abs/2506.03719
- Wen et al.: https://arxiv.org/abs/2407.21720
- Gu et al.: https://arxiv.org/abs/2310.02664
- Jain et al.: https://arxiv.org/abs/2411.16738
- Kim et al.: https://arxiv.org/abs/2509.25705
- Kinetic-energy FM: https://arxiv.org/abs/2602.07928
- Shah et al.: https://arxiv.org/abs/2502.21278
- Favero et al.: https://arxiv.org/abs/2505.16959
- Wu et al.: https://arxiv.org/abs/2502.03435
- Kaiser & Kollmann: https://arxiv.org/abs/2603.13419
- Bradley & Nakkiran: https://arxiv.org/abs/2408.09000
- Pham et al.: https://arxiv.org/abs/2505.21777
- Aithal et al.: https://arxiv.org/abs/2406.09358
- Chen et al. (AMG): https://arxiv.org/abs/2404.00922
- Raya & Ambrogioni: https://arxiv.org/abs/2305.19693
- Sclocchi et al.: https://arxiv.org/abs/2402.16991
- Li & Chen: https://arxiv.org/abs/2403.01633

**Giới hạn của bản này.** Venue của Kim et al. và Kinetic-FM chỉ lấy từ trường comment trên arXiv. Thang điểm review của ICLR 2027 và mọi thông tin về NeurIPS 2027 chưa xác minh được. Composable Diffusion (Liu et al. ECCV 2022) là trích dẫn từ trí nhớ, cần kiểm tra trước khi cite.
