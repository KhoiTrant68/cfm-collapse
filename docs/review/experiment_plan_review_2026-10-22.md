# Nhận xét kế hoạch EXP-A / EXP-B / EXP-C — 22/10/2026

Đối chiếu với `paper/main.tex` bản đang sửa (chưa commit, trong thư mục chính) và với những gì đã
chạy trên server (`results/learned_composition_20261021/`, `results/learned_composition_2d_20261021/`).
Code `scripts/l40/` của kế hoạch chưa có trong repo nên phần dưới chỉ xét thiết kế.

## Tóm tắt

| Thí nghiệm | Tình trạng | Việc cần làm |
|---|---|---|
| EXP-A (Theorem 4.7, Cor. 4.10 trên mạng học được) | **Đã chạy**, rộng hơn kế hoạch: 1D B∈{1,2,3}, 2D tam giác, 5 biến thể × 5 seed, 16384 nguồn | Đang đánh giá lại bằng bộ giải cứng (xem mục 1.2); không cần chạy lại kế hoạch |
| EXP-B (K(t) của Theorem C.1 trên EXP-1) | Chưa chạy | Checkpoint **đã có sẵn** trên server, không cần huấn luyện |
| EXP-C (CIFAR, tách 38% off-atom) | Chưa chạy | Checkpoint **đã có sẵn** (3 seed × h∈{0,4,5,6}), không cần 7–8 giờ huấn luyện lại |

Hai điểm trong kế hoạch phải sửa trước khi chạy: (i) bộ giải RK4 bước cố định theo thời gian log không
dùng được cho trường thật sự hút về điểm hòa (mục 1.2); (ii) không cài lại torch vào môi trường server
(mục 3).

## 1. EXP-A

### 1.1. Đã có gì

- **1D:** đúng cấu hình của kế hoạch (atom và nhãn ±1, h = 1, query ±B), thêm B = 3. Có năm biến thể,
  mỗi biến thể 5 seed, 200k bước. `cfm_v` là CFM chuẩn với một mạng và dropout điều kiện. `cfm_v_sep`
  dùng hai mạng riêng như kế hoạch. Ngoài ra có lấy mẫu t nghiêng về 1, đầu vào s = tx/(1−t)², và
  control dương chưng cất từ trường exact. Các nhánh đối chứng: label average, guidance một nhãn,
  guided prior average (trường exact bằng v_unc) và conditional tại query 0.
- **2D tam giác:** nhãn e_k, query B e_k, B = 2, đúng Corollary 4.10. Ba biến thể × 5 seed. Tham chiếu
  exact tái hiện Table spectral: 0 / 0,140 / 0,677 tại 0,5 / 2 / 5·w_c, so với 0 / 0,140 / 0,687.
- **Tham chiếu exact 1D:** basin có chứng nhận và tập cắt hữu hạn {|X_{1−ε}| < δ} trên cùng nguồn,
  ε đến 10⁻⁵. Tại w = w_c điểm tách đúng ở 0, đúng Theorem 4.7(b).
- **Chẩn đoán trường:** m̂ theo s tại 13 mức t, độ dốc tại điểm hòa, sai số boundary layer, ngưỡng
  suy ra ŵ_c(t).

### 1.2. Bài học quan trọng: bộ giải

Kế hoạch dùng "RK4 theo thời gian log, 800/1600 bước" và lấy sự khớp giữa hai mức làm kiểm tra hội tụ.
Cách này không dùng được. Một trường thật sự hút về điểm hòa có hệ số co theo x là λ ≈ β|Γ|, với
β = t/(1−t)². RK4 bước cố định chỉ ổn định khi |λ·Δτ| < 2,8. Với 800 bước đến ε = 10⁻⁴ thì
Δτ ≈ 0,0115, và ở B = 1, w = 2w_c (Γ = −0,42) RK4 mất ổn định từ t ≈ 0,96. Với 1600 bước thì từ
t ≈ 0,97. Cả hai mức đều không ổn định trước mốc cắt đầu tiên, nên chúng "khớp nhau" trên một đáp
số sai.

Chính lỗi này đã xảy ra ở lần đánh giá đầu của chúng tôi, với Δτ = 0,02 và 0,005. Control dương có
Jacobian tại điểm hòa khớp exact tới 0,1% nhưng cho 0 mẫu ở midpoint. Dấu hiệu nhận biết: trường hút
càng mạnh (w lớn hơn) thì mẫu càng bị đẩy ra sớm hơn. Một hiệu ứng thật của trường không cư xử như vậy.

Hiện dùng bộ giải ROS2 thích nghi riêng cho từng nguồn (Rosenbrock bậc 2, L-ổn định), ước lượng sai
số bằng cách so một bước với hai nửa bước, Jacobian lấy bằng autograd, đổi sang biến blow-up s = βx
sau τ = 0,5. Trên trường exact nó cho đúng các basin có chứng nhận: 0,4434 / 0,1797 / 0,0488 / 0 trên
512 nguồn, ở cả hai mức sai số và mọi ε. Test hồi quy: `scripts/test_learned_composition_exact.py`.

Thêm một bẫy: embedding thời gian của `MLPVelocity` luôn tính bằng float32, nên t = 0,99 và
0,99 + 10⁻⁹ cho cùng một vector. Gần t = 1, trường học được là hàm bậc thang theo t, và mọi bộ giải
thích nghi đều bị kẹt ở các bước nhảy đó. Đã sửa để embedding giữ float64 khi đầu vào là float64.
Nhánh float32 không đổi, và không script cũ nào chạy mạng bằng float64.

### 1.3. Kết quả (bản đúng đang được tính lại cho cả 40 mô hình)

- **CFM chuẩn:** không có khối lượng ở midpoint ở bất kỳ w nào, cả 1D lẫn 2D. Kết luận này không do
  bộ giải: với Radau hay ROS2, tỷ lệ còn ở midpoint đã về 0 tại t ≈ 0,95. Lý do nằm ở trường. Sai số
  trên phân phối train nhỏ hơn 5·10⁻⁵ ở mọi t. Nhưng trong boundary layer gần điểm hòa, sai số
  khoảng 0,7 từ t ≈ 0,9. Độ dốc tại điểm hòa đổi sang dương (đẩy ra) trong khoảng t ≈ 0,85–0,95.
  Ngưỡng suy ra vượt 10·w_c.
- **Control dương:** với bộ giải đúng, tái hiện basin exact (seed 0: 0,4434 và 0,1797, trùng exact).
- **Đầu vào s, huấn luyện bằng CFM thường:** trong 2D, Jacobian tại điểm hòa khớp exact ở mọi t
  (−0,27 so với −0,268). Số occupancy cuối cùng đang được tính.

Nếu `cfm_x_s` tái hiện được ngưỡng thì câu trả lời cho RQ1 là có điều kiện: chuyển pha sống sót qua
xấp xỉ bằng mạng khi kiến trúc ngoại suy đúng theo tọa độ boundary layer. CFM chuẩn không làm được vì
không có dữ liệu ở điểm hòa khi t > 0,8.

### 1.4. Góp ý khác cho EXP-A của kế hoạch

- **Ngưỡng học được** λ_max(D̂^{-1/2}Ĉ_av D̂^{-1/2}) là dạng giới hạn β → ∞. Với trường exact nó cho
  đúng w_c ở mọi t, nên không thấy được giai đoạn chuyển tiếp. Ở t hữu hạn, điều kiện ổn định theo x
  có thêm số hạng −1/β: ŵ_c(t) = (κ̄_c − 1)/(κ_u − κ̄_c), với κ là độ dốc theo x tại điểm hòa. Với
  trường exact, đường này tăng từ âm lên 1 theo t, và lệch khỏi nó là chỗ mạng mất boundary layer.
- **Checkpoint 20k/50k/200k:** chúng tôi chỉ lưu bước cuối. Có thể thêm nếu muốn xem theo thời gian
  huấn luyện. Tuy vậy chẩn đoán cho thấy lỗi nằm ở độ phủ dữ liệu, nên huấn luyện lâu hơn khó sửa được.
- **Pilot 400 vòng** cho 0,16–0,22 ở midpoint: như kế hoạch đã nói, con số này không mang thông tin.

## 2. EXP-B

**Giá trị:** trả lời trực tiếp câu trong Limitations, "the error along learned trajectories … not
measured", và đo K(t) = m(t)/r(t) của Theorem C.1.

- **Không cần huấn luyện.** Server đã có `results/exp1/linear-gaussian-mlp-h0-seed1001…1005-200k`
  và `…-h0p1-…`, mỗi run 5 checkpoint (1k, 10k, 30k, 100k, 200k). Đây đúng là 5 problem seed ×
  {h = 0, h = 0,1} của kế hoạch, và cho phép theo dõi K(t) qua quá trình huấn luyện.
- **Chỉ báo các phép kiểm tra cận như sanity check.** Bản `main.tex` mới đã viết (dòng 681–686) rằng
  cận pathwise của Theorem 5.1 đạt dấu bằng khi v_θ bị chặn. B_T tính từ m(t) đo được chỉ là bất đẳng
  thức Minkowski, nên luôn đúng. Thông tin thật nằm ở đường K(t).
- **Dự đoán kiểm tra được:** (1−t)Δ(Z_t) → Z_1 − a, nên về cuối m(t) ≈ E|Z_1 − a|²/ε². Ở 200k bước,
  tr Cov sinh ra là 0,40 trong khi r(t) nhỏ, nên K(t) phải tăng như ε⁻². Đại lượng đáng báo là thời
  điểm K rời khỏi O(1), và thời điểm đó dịch thế nào theo số bước huấn luyện.
- **Phạm vi định lý:** Theorem C.1 chỉ cho nhãn cứng (h = 0). Với h = 0,1 thì kiểm tra tiền đề của
  Proposition 5.2. Trường kernel exact ở h = 0,1 với 200 atom rẻ, tính được ngay.
- **Bộ giải:** trường nhãn cứng có độ dốc −1/(1−t) gần atom. Kiểm tra điều kiện ổn định của bước,
  hoặc dùng bộ giải cứng ở trên, trước khi so m(t) với r(t).

## 3. EXP-C

- **Không cần huấn luyện lại.** Server có `results/exp3/exp3_cifar_heff_h{0,4,5,6}_s{0,1,2}` với
  checkpoint 2k, 5k, 10k, 20k, 30k, 40k, 60k. Config của chúng là `exp3_cifar_ddpm.yaml` giữ nguyên
  (đã kiểm tra bằng diff), chỉ thêm việc lưu trọng số. Như vậy tiết kiệm khoảng 8 giờ GPU, và có 3
  seed cho mỗi h thay vì 1.
- **Lưu ý:** con số 38% off-atom trong paper đo trên `exp3_cifar_ddpm_h6`, run không giữ trọng số.
  Cần đo lại tỷ lệ này trên `heff_h6_s*` với cùng tiêu chí d₁/d₂ < 1/3 trước khi tách nguồn gốc.
- **Tách 38%** bằng cách tích phân trường kernel exact từ cùng nguồn tới cùng mốc cắt: đây là phần
  có giá trị nhất. Trường exact ở h = 6 cũng cứng gần t = 1, nên cần float64 và bộ giải cứng hoặc
  bước đủ nhỏ, đã kiểm tra.
- **Môi trường: bỏ bước "cài torch CUDA".** Server dùng `~/clic/venv`, đã có torch 2.11 + cu128.
  Venv này thuộc dự án CLIC và chỉ được dùng ở chế độ đọc; không cài hay nâng cấp gì trong đó.
- Chia forward U-Net thành micro-batch là hợp lý. Đây chỉ là đánh giá, không chạy hai job huấn luyện
  CIFAR cùng lúc.

## 4. Thứ tự đề xuất

1. Đang chạy: đánh giá lại 40 mô hình EXP-A bằng bộ giải cứng, rồi tổng hợp và vẽ hình.
2. EXP-B trên checkpoint có sẵn: viết code vài giờ, chạy vài phút.
3. EXP-C, chỉ đánh giá, trên checkpoint có sẵn: vài giờ GPU.
4. Đưa vào paper: thay câu "The composition theorem has no trained-network counterpart yet" và câu
   "… not measured" trong Limitations bằng kết quả đo được.
