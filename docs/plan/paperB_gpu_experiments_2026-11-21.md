# Bài B: kế hoạch thí nghiệm GPU, có dự đoán đăng ký trước (2026-11-21)

## Vì sao cần tài liệu này

Máy này không có GPU (`nvidia-smi` không tồn tại) và torch không load được. Vì vậy mọi thí nghiệm cần train model hoặc chạy denoiser EDM phải làm trên server, như các lần chạy `n3_*` trước đây trên `nexai-sv20` (A30).

Tài liệu này ghi **trước khi chạy**:
- protocol của từng thí nghiệm;
- dự đoán của lý thuyết;
- tiêu chí để biết dự đoán sai.

Mục đích là để thí nghiệm có thể falsify được, chứ không chỉ mô tả lại sau khi đã có số liệu. Đây cũng là điều mà các reviewer mô phỏng (R2 W1–W3, W5–W6; DA) yêu cầu.

## Quy ước chung

- Model là EDM class-conditional trên CIFAR-10 (VP, DDPM++), batch 128, không augmentation trừ khi ghi rõ. Mặc định train 10 Mimg, lấy EMA snapshot.
- Sampler mặc định là Heun deterministic 18 bước, ρ = 7, σ ∈ [0.002, 80].
- Exact field là posterior mean của lớp, tính trên ảnh train của lớp đó, ở double precision.
- Nhãn off-atom: d1/d2 ≥ 1/3 (d1, d2 là khoảng cách tới ảnh train gần nhất và gần nhì cùng lớp). Báo cáo thêm với ngưỡng 0.2 và 0.5.
- Mỗi model dùng 100 latent mỗi lớp (1000 mẫu). Seed latent cố định để các điều kiện được so sánh theo cặp.
- Script có sẵn: `scripts/n3_edm_memorization.py`, `scripts/n3_swap.py` (`--swap-sigmas`), `scripts/n3_directional_q.py` (`--forward-only` cho các đại lượng T1/T3), `scripts/n3_robustness.py`.
- CI: bootstrap phân tầng 1000 lần, paired cho các hiệu số. Seed huấn luyện là đơn vị thống kê khi so sánh giữa các model.

---

## E1. Swap theo cửa sổ: tách hai đồng hồ

**Câu hỏi.** Landing có thật sự chỉ do field ở cuối quyết định không? Và field ở cuối "giữ" độ lệch tại lúc bàn giao theo quy luật nào?

**Protocol.** Mở rộng `n3_swap.py` để exact field được dùng trên một cửa sổ [σ_lo, σ_hi], còn network dùng ở ngoài cửa sổ. Các cửa sổ:
- [0, σ_hi] với σ_hi ∈ {0.02, 0.05, 0.1, 0.2, 0.5, 1}: đây chính là net→exact đã có.
- [σ_lo, ∞) với σ_lo trong cùng tập giá trị: đây là exact→net đã có.
- Các cửa sổ giữa [σ_lo, σ_hi] với σ_lo < σ_hi, ví dụ [0.05, 0.5], [0.1, 1], [0.5, 2].

Chạy trên public model, sub500 seed 0 và sub2000.

**Dự đoán (đăng ký trước):**
- **P1.1.** Với exact→net trên public model, median d1 tỉ lệ với σ_lo, với hệ số k = d1/σ_lo ≈ 27 (dữ liệu cũ cho 26, 27 và 30 tại σ_lo = 0.1, 0.05 và 0.02). Tiêu chí sai: k ngoài [20, 35], hoặc d1 không đơn điệu theo σ_lo.
- **P1.2.** Với cửa sổ giữa [σ_lo, σ_hi] trên public model, độ lệch cuối chỉ phụ thuộc vào σ_lo (lúc bàn giao lại cho network), không phụ thuộc σ_hi, miễn là σ_hi ≥ 0.5. Lý do là trong cửa sổ exact field co gần như hoàn toàn (ϱ = 0, nên C_window = log(σ_hi/σ_lo)), còn network sau đó giữ độ lệch. Tiêu chí sai: median d1 thay đổi quá 20% khi σ_hi đổi từ 0.5 sang 2 với cùng σ_lo.
- **P1.3.** Trên sub500 (memorize), network tự landing. Vì vậy mọi cửa sổ đều cho tỉ lệ off-atom ≤ 5%, như mô hình gốc.

## E2. Lịch Heun thô: dự đoán thay đổi outcome

**Câu hỏi.** Prop. heun có dự đoán được outcome, chứ không chỉ việc certificate đúng hay sai không? (R2 W2, R1 W3.)

**Protocol.** Trên sub500 seed 0 và sub2000, với cùng latent, chạy các lịch:
- K ∈ {6, 8, 10, 12, 18} bước với ρ = 7;
- K = 18 với ρ_schedule = 3, để vài bước cuối có r_k < 3 − 2√2 ≈ 0.172, tức vùng overshoot của Prop. heun(d).

Ghi lại theo từng mẫu: c_k, ϱ tại x_k và tại predictor, và outcome.

**Dự đoán:**
- **P2.1 (certificate).** Tỉ lệ mẫu on-atom có c_k < 1 ở mọi bước được dự đoán *trước khi chạy*. Cách tính: nội suy ϱ(σ) theo log σ từ run 18 bước của chính mẫu đó, rồi tính c_k theo lịch mới. Tiêu chí sai: tỉ lệ đo được lệch khỏi dự đoán quá 5 điểm phần trăm.
- **P2.2 (outcome, khám phá có kiểm soát).** Lý thuyết không dự đoán outcome tuyệt đối. Nó dự đoán *thứ tự*: những mẫu có biên contraction thấp nhất ở run 18 bước (C late nhỏ nhất, hoặc min_k(ϱ_crit − ϱ_k) nhỏ nhất) là những mẫu đổi on→off trước khi lịch thô đi. Tiêu chí sai: AUC của C late (18 bước) để dự đoán mẫu đổi trạng thái < 0.7, xét trên các lịch có ít nhất 10 mẫu đổi.
- **P2.3.** Với ρ_schedule = 3 (r_k < 0.172), overshoot xảy ra với một tỉ lệ dương các bước. Dự đoán: hướng của x_{k+1} − a ngược với x_k − a ở ít nhất 1% số bước cuối của các mẫu on-atom.

## E3. Lưới N × seed tách bạch, cộng một model có augmentation

**Câu hỏi.** Hai đồng hồ thay đổi thế nào theo kích thước tập train và thời gian train? Có khớp với kết quả τ_mem ∝ n của Bonnaire et al. (NeurIPS 2025) không? (R2 W6, DA.)

**Protocol.**
- N ∈ {500, 1000, 2000, 5000}, mỗi lớp N/10 ảnh.
- Tại N = 2000: thiết kế 2 × 2 giữa subset seed và training seed. Với các N khác: 3 seed, trong đó subset seed và training seed khác nhau.
- Lưu checkpoint EMA mỗi 1 Mimg, tới 10 Mimg (20 Mimg với N = 5000).
- Thêm một model N = 2000 có augmentation mặc định của EDM.
- Mỗi checkpoint: đo tỉ lệ off-atom. Mỗi checkpoint cuối: đo swap (E1, hai chiều) và các đại lượng của `n3_directional_q.py`.

**Dự đoán:**
- **P3.1 (selection không phụ thuộc N).** σ_sel (σ lớn nhất mà net→exact cho cùng ảnh ≥ 90%) nằm trong [0.5, 2] với mọi N và mọi thời điểm train. Tiêu chí sai: ngoài khoảng đó với một model bất kỳ, có CI.
- **P3.2 (thời gian memorize).** Thời điểm tỉ lệ on-atom vượt 50% tăng xấp xỉ tuyến tính theo N, với hệ số mũ log-log trong [0.7, 1.3], như Bonnaire et al. Tiêu chí sai: hệ số mũ ngoài khoảng.
- **P3.3 (landing).** Ở mọi model, late contraction C tách on/off với AUC ≥ 0.95, xét các model có lớp thiểu số ≥ 10%.
- **P3.4.** Model có augmentation có tỉ lệ off-atom cao hơn model không augmentation cùng N và seed. Đây là nhiễu đã biết; mục đích là đo độ lớn, không phải kiểm định giả thuyết.

## E4. CFG trên model thật: guidance tác động lên đồng hồ nào?

**Câu hỏi.** Guidance là một nửa tiêu đề của bài lý thuyết (A), nhưng chưa có thí nghiệm nào trên model ảnh thật (R2 W5). Câu chuyện "chọn sớm, landing muộn" dự đoán rằng guidance tác động khác nhau tùy cửa sổ σ mà nó được áp dụng.

**Protocol.**
- Train N = 2000 với class dropout p = 0.1, 3 seed.
- Sample với w ∈ {0, 0.5, 1, 2, 4}.
- Thêm: guidance chỉ trong cửa sổ σ > 1 (trước khi chọn ảnh xong), và chỉ trong cửa sổ σ < 0.6 (giai đoạn landing).
- Thêm cửa sổ của Kynkäänniemi et al.

**Dự đoán:**
- **P4.1.** Ở exact optimum, mọi w cho endpoint atomic. Đây là kết quả lý thuyết của bài A (Cor. twofields) và được dùng làm kiểm tra cài đặt.
- **P4.2.** Tỉ lệ on-atom tăng theo w (cùng hướng với Jain et al., CVPR 2025). Tiêu chí sai: không tăng đơn điệu, hoặc hiệu số giữa w = 4 và w = 0 có CI chứa 0.
- **P4.3 (tách đồng hồ).** Guidance chỉ ở σ > 1 làm thay đổi *ảnh được chọn* (tỉ lệ cùng ảnh với w = 0 giảm) nhiều hơn tỉ lệ on-atom. Guidance chỉ ở σ < 0.6 làm thay đổi *tỉ lệ on-atom* nhiều hơn ảnh được chọn. Tiêu chí sai: thứ tự hai hiệu ứng ngược lại ở hai trong ba seed.
- **P4.4.** Thay đổi tỉ lệ on-atom theo w đi qua late contraction: ΔC giữa hai mức w dự đoán việc một mẫu đổi trạng thái với AUC ≥ 0.75.

## E5. Mở rộng quy mô và một model train bằng CFM

**Protocol.**
- Train một model rectified-flow / CFM (U-Net cùng cỡ, velocity loss) trên CIFAR-10 sub2000 và CIFAR-10 đầy đủ.
- Chạy ImageNet-64 class-conditional (EDM hoặc EDM2 public checkpoint). Exact field tính theo lớp, khoảng 1300 ảnh mỗi lớp nên khả thi.
- Đo hai đồng hồ (E1) và late contraction.

**Dự đoán:**
- **P5.1.** Cấu trúc hai đồng hồ giữ nguyên: σ_sel ở noise trung bình, và net→exact tại σ ≤ 0.1 cho tỉ lệ on-atom ≥ 99%.
- **P5.2.** Với model CFM, tỉ lệ off-atom ở public-scale ≥ 95%.

## E6. Swap net→net' trên cùng một subset

**Câu hỏi.** Việc landing do field cuối quyết định là tính chất của network nói chung, hay của một model cụ thể? (R2 W3.)

**Protocol.** Dùng hai model cùng subset (từ thiết kế 2 × 2 của E3): một checkpoint sớm (chưa memorize) và một checkpoint muộn (memorize). Chạy model sớm ở σ > s và model muộn ở σ ≤ s, và chiều ngược lại.

**Dự đoán.**
- **P6.1.** Với s ≤ 0.6, tỉ lệ on-atom gần với tỉ lệ của model dùng ở *cuối*, sai khác ≤ 10 điểm phần trăm.
- **P6.2.** Với s ≥ 2, tỉ lệ on-atom gần với tỉ lệ của model dùng ở *đầu*.

## E7. Speciation và collapse time (CPU, cần dữ liệu CIFAR)

**Protocol.** Trên đúng các subset 500, 1000, 2000 và trên CIFAR đầy đủ:
- Tính σ mà tại đó posterior chính xác trên ảnh train, cho một điểm nhiễu x = y + σε, có trọng số lớn nhất vượt 1/2 (collapse theo Biroli et al. 2024, đo trực tiếp).
- Tính speciation time từ phổ covariance của lớp.
- So sánh với σ_sel đo được.

**Dự đoán.**
- **P7.1.** σ_sel đo được trên network nằm trong khoảng một bậc độ lớn so với collapse σ của exact posterior trên cùng subset.
- **P7.2.** Model public chọn ảnh ở σ nhỏ hơn model subset, vì collapse σ giảm khi N tăng.

## Ước lượng tài nguyên (thô)

- Train EDM CIFAR 10 Mimg: khoảng 2–3 ngày A100 mỗi model.
- E3 cần khoảng 16 model, E4 thêm 3, E5 thêm 2–3, tổng cộng khoảng 50–70 ngày A100.
- Sampling, exact field và các đại lượng `n3_directional_q` mất vài giờ mỗi model.
- Nếu cần cắt giảm, ưu tiên theo thứ tự: E1 và E2 (không cần train) → E4 tại N = 2000 → E3 rút gọn (N ∈ {500, 2000}, 2 × 2) → E6 → E5.
