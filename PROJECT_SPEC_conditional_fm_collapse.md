# PROJECT SPEC — Posterior Variance Collapse in Conditional Flow Matching

> **Đọc kỹ toàn bộ file này trước khi viết code.**
> Đây là một dự án **nghiên cứu lý thuyết**, không phải dự án kỹ thuật SOTA.
> Mục tiêu của code là **kiểm chứng số học một định lý**, không phải đạt điểm benchmark cao.
> Nếu kết quả số **không khớp** với dự đoán lý thuyết, đó là thông tin quan trọng — hãy báo cáo trung thực, KHÔNG tinh chỉnh để ép ra kết quả mong muốn.

---

## 0. TL;DR cho agent

Bạn sẽ implement 3 thí nghiệm tăng dần độ phức tạp để kiểm chứng một định lý về **posterior variance collapse** trong conditional flow matching (CFM):

1. **EXP-1 (Linear-Gaussian)** — hậu nghiệm có dạng đóng → kiểm chứng chính xác. **Ưu tiên cao nhất.**
2. **EXP-2 (Gaussian Mixture)** — kiểm tra mode collapse / selective memorization.
3. **EXP-3 (Image inpainting nhỏ)** — minh hoạ định tính.

Toàn bộ chạy được trên 1 GPU 24GB. EXP-1 và EXP-2 chạy được cả trên CPU.

**Deliverable chính:** một báo cáo `RESULTS.md` với các biểu đồ chứng minh (hoặc bác bỏ) dự đoán lý thuyết ở Mục 2.

---

## 1. Bối cảnh nghiên cứu

### 1.1 Vấn đề

Conditional flow matching được dùng rộng rãi để giải Bayesian inverse problems: học velocity field `v(x_t, t, y)` transport từ source distribution về **hậu nghiệm** `p(x | y)`.

Bài arXiv 2603.14135 ("Solving physics-constrained inverse problems with conditional flow matching") quan sát thực nghiệm rằng khi train lâu (overtraining), phân phối sinh ra bị:
- **variance collapse** — phương sai hậu nghiệm bị đánh giá thấp nghiêm trọng;
- **selective memorization** — mẫu sinh ra tụ quanh các training point có observation tương tự.

Họ chỉ đưa ra "a simplified theoretical analysis" và khắc phục bằng **early stopping** (heuristic).

Bài arXiv 2510.18118 ("Gradient Variance Reveals Failure Modes in Flow-Based Generative Models") chứng minh cho trường hợp **unconditional**: với deterministic interpolant, tồn tại vector field đạt loss = 0 bằng cách memorize cặp ghép training (Proposition 2). Họ cũng lập luận rằng CFM chuẩn **không** memorize vì `x₀` được resample độc lập mỗi epoch → phá vỡ song ánh `(x_t, t) ↦ (x₀, x₁)`.

### 1.2 Giả thuyết trung tâm của dự án này

> **Trong trường hợp conditional, cơ chế bảo vệ "resample x₀" bị vô hiệu hoá, vì biến điều kiện `y` đóng vai trò chỉ số định danh training sample.**

Đây là điểm mới: conditioning làm injectivity **mạnh hơn**, chứ không yếu đi.

---

## 2. Lý thuyết cần kiểm chứng

### 2.1 Thiết lập

- Phân phối chung `ρ(x, y)` trên `ℝ^d × ℝ^k`.
- Training set `{(x⁽ⁱ⁾, y⁽ⁱ⁾)}_{i=1}^N` i.i.d. từ `ρ`.
- Source `π₀` (ví dụ `N(0, I)`), **resample độc lập mỗi lần**.
- Interpolant tuyến tính (deterministic, không nhiễu):
  ```
  x_t = (1 - t) x₀ + t x₁,   t ~ U(0,1)
  ```
- Loss:
  ```
  L(v) = E_{t, x₀~π₀, (x₁,y)~ρ̂}  || (x₁ - x₀) - v(x_t, t, y) ||²
  ```
  với `ρ̂` là empirical measure.

### 2.2 Định lý (Conditional Minimizer Collapses)

Minimizer trong lớp hàm đo được bất kỳ là `v*(x, t, y) = E[x₁ - x₀ | x_t = x, t, y]`.

**Bước 1.** Dưới `ρ̂`, biến `y` là **rời rạc** với các nguyên tử tại `y⁽ⁱ⁾`. Nếu marginal `ρ_Y` là atomless thì các `y⁽ⁱ⁾` phân biệt h.c.c., nên điều kiện `{y = y⁽ⁱ⁾}` chọn ra đúng chỉ số `i`. Do đó `x₁ = x⁽ⁱ⁾` **xác định**.

*(Ghi chú: làm việc trên empirical measure giúp tránh hoàn toàn vấn đề điều kiện hoá trên sự kiện đo-không.)*

**Bước 2.** Với `x₁ = x⁽ⁱ⁾` cố định và `t < 1`:
```
x_t = (1-t) x₀ + t x⁽ⁱ⁾   ⟹   x₀ = (x_t - t x⁽ⁱ⁾) / (1-t)
```
Không còn phương sai. Suy ra dạng đóng:
```
v*(x, t, y⁽ⁱ⁾) = (x⁽ⁱ⁾ - x) / (1 - t)          ......... (★)
```

**Bước 3.** Tích phân ODE `dx/dt = v*`. Đặt `u = x - x⁽ⁱ⁾`:
```
du/dt = -u/(1-t)  ⟹  u(t) = u(0)(1-t)
⟹ x(t) = x⁽ⁱ⁾ + (1-t)(x₀ - x⁽ⁱ⁾)
⟹ x(1) = x⁽ⁱ⁾  với MỌI x₀
```
Pushforward của `π₀` là `δ_{x⁽ⁱ⁾}` → **hậu nghiệm sụp đổ hoàn toàn, phương sai = 0**.

**Bước 4 (bổ đề tương phản, unconditional).** Không có `y`, cho `(x_t = x, t)`, mỗi ứng viên `i` đều tương ứng một source hợp lệ `x₀⁽ⁱ⁾ = (x - t x⁽ⁱ⁾)/(1-t)` với mật độ `π₀(x₀⁽ⁱ⁾) > 0`. Hậu nghiệm trên `i` có trọng số **dương với mọi i**:
```
v*(x,t) = Σᵢ wᵢ(x,t) (x⁽ⁱ⁾ - x₀⁽ⁱ⁾),   wᵢ ∝ π₀(x₀⁽ⁱ⁾)
```
→ trung bình có trọng số thực sự → flow trơn, không memorize.

### 2.3 Dự đoán có thể kiểm chứng bằng số

| ID | Dự đoán | Cách đo |
|---|---|---|
| **P1** | Khi train càng lâu, phương sai của phân phối sinh ra (điều kiện trên `y⁽ⁱ⁾` trong training set) → 0 | Sinh nhiều mẫu với cùng `y⁽ⁱ⁾`, khác `x₀`; đo variance theo số iteration |
| **P2** | Velocity network học được hội tụ về dạng đóng (★) | So sánh `v_θ(x,t,y⁽ⁱ⁾)` với `(x⁽ⁱ⁾ - x)/(1-t)` theo iteration |
| **P3** | Mẫu sinh ra hội tụ về đúng training point `x⁽ⁱ⁾` tương ứng, không phải điểm khác | Đo `‖x_gen - x⁽ⁱ⁾‖` vs `min_{j≠i} ‖x_gen - x⁽ʲ⁾‖` |
| **P4** | Sụp đổ **không** xảy ra (hoặc yếu hơn nhiều) ở unconditional CFM cùng setup | Train song song 1 model unconditional, so sánh variance |
| **P5** | Mức sụp đổ phụ thuộc khoảng cách giữa các `y⁽ⁱ⁾`: `y` càng gần nhau (nhiễu quan sát lớn / k nhỏ) → sụp đổ càng nhẹ | Quét mức nhiễu quan sát σ_obs |
| **P6** | Sụp đổ yếu đi khi N tăng với capacity cố định | Quét N ∈ {50, 200, 1000, 5000} |
| **P7 (remedy)** | Thêm nhiễu/smoothing vào **biến điều kiện y** khôi phục được phương sai | Train với `y + h·ε`, quét bandwidth h |

**P1, P2, P4 là cốt lõi.** Nếu ba cái này không khớp → dừng lại và báo cáo, đừng chạy tiếp.

---

## 3. EXP-1 — Linear-Gaussian (ƯU TIÊN CAO NHẤT)

### 3.1 Vì sao
Hậu nghiệm có **dạng đóng** → có ground truth chính xác để so sánh, không phụ thuộc metric xấp xỉ.

### 3.2 Mô hình
```
x ~ N(μ_x, Σ_x)                    # prior
y = A x + ε,  ε ~ N(0, σ_obs² I)   # forward model tuyến tính
```
Hậu nghiệm giải tích:
```
Σ_post = (Σ_x⁻¹ + Aᵀ A / σ_obs²)⁻¹
μ_post(y) = Σ_post (Σ_x⁻¹ μ_x + Aᵀ y / σ_obs²)
```

### 3.3 Cấu hình mặc định
- `d = 2` (dễ vẽ) và `d = 10` (kiểm tra chiều cao hơn)
- `k = 1` và `k = d` (quét theo chiều observation)
- `A`: ma trận ngẫu nhiên cố định (fix seed), hoặc projection đơn giản
- `σ_obs ∈ {0.01, 0.1, 0.5, 1.0}` (cho P5)
- `N ∈ {50, 200, 1000, 5000}` (cho P6)
- Source `π₀ = N(0, I_d)`

### 3.4 Model
- MLP: 3–4 layer, width 128, activation SELU hoặc SiLU
- Input: concat `[x_t, t_embed, y]` — dùng sinusoidal time embedding
- Output: vector field `∈ ℝ^d`
- Optimizer Adam, lr 1e-3, batch 256
- **Train rất lâu**: tới 100k–200k iterations. Overtraining là *mục đích*, không phải lỗi.
- Lưu checkpoint ở các mốc log-spaced: 100, 300, 1k, 3k, 10k, 30k, 100k, 200k

### 3.5 Đo đạc (chạy tại mỗi checkpoint)

Với mỗi `y⁽ⁱ⁾` trong training set (lấy ~20 điểm đại diện):
1. Sinh `M = 1000` mẫu bằng cách integrate ODE từ `M` giá trị `x₀` khác nhau (Euler hoặc RK4, 100 steps; dùng `torchdiffeq` hoặc tự viết — tự viết đơn giản hơn và đủ dùng).
2. Tính:
   - `trace(Cov(samples))` → so với `trace(Σ_post)` **[P1]**
   - `‖mean(samples) - μ_post(y⁽ⁱ⁾)‖`
   - `‖mean(samples) - x⁽ⁱ⁾‖` **[P3]** ← nếu tiến về 0 thì đúng là collapse về training point
3. Đo sai số velocity so với dạng đóng (★) **[P2]**:
   - Sample ngẫu nhiên `(x, t)`, tính `‖v_θ(x,t,y⁽ⁱ⁾) - (x⁽ⁱ⁾-x)/(1-t)‖ / ‖(x⁽ⁱ⁾-x)/(1-t)‖`
   - Tránh `t` quá gần 1 (dùng `t ∈ [0, 0.95]`) vì (★) kỳ dị tại `t=1`
4. Với `y` **ngoài** training set (held-out): lặp lại 1–2 để xem generalization

### 3.6 Baseline đối chứng [P4]
Train song song một model **unconditional** (bỏ input `y`) trên cùng `{x⁽ⁱ⁾}`, cùng số iteration, cùng capacity. Đo trace covariance của mẫu sinh ra. Dự đoán: **không** sụp về 0 như conditional.

### 3.7 Remedy [P7]
Train thêm các model với conditioning được làm trơn:
```
y_train = y⁽ⁱ⁾ + h · ε,  ε ~ N(0, I),  h ∈ {0, 0.01, 0.05, 0.1, 0.5}
```
Đo lại trace covariance. Dự đoán: `h` lớn hơn → phương sai được khôi phục, nhưng có bias (mean lệch). Cần tìm được trade-off dạng chữ U theo `h`.

**Lưu ý quan trọng:** phải phân biệt rõ remedy này (nhiễu trên **y**) với việc thêm nhiễu vào **interpolant** như 2510.18118. Nên chạy thêm một biến thể interpolant-noise (`x_t = (1-t)x₀ + t x₁ + σ√(t(1-t)) Z`) để so sánh hai loại remedy — đây sẽ là một bảng quan trọng trong paper.

---

## 4. EXP-2 — Gaussian Mixture

### 4.1 Mục tiêu
Kiểm tra **selective memorization** khi hậu nghiệm thật là **đa phương thức** — trường hợp mà collapse gây hại nhất.

### 4.2 Thiết lập
- Prior `x`: hỗn hợp Gaussian 4–8 mode trong `ℝ²` hoặc `ℝ¹⁰`
- Forward model: `y = A x + ε`, chọn `A` sao cho **mất thông tin** (ví dụ chiếu xuống 1 chiều) → hậu nghiệm thật đa phương thức
- Ground truth hậu nghiệm: tính bằng numerical integration trên lưới (d=2) hoặc MCMC (d=10)

### 4.3 Đo đạc
- **Mode coverage**: với `y` cho trước, mẫu sinh ra phủ được bao nhiêu mode của hậu nghiệm thật
- Sinkhorn distance / MMD giữa mẫu sinh và hậu nghiệm thật (dùng `geomloss`)
- Theo dõi theo số iteration → kỳ vọng thấy mode coverage giảm dần khi overtrain

---

## 5. EXP-3 — Image inpainting (minh hoạ)

### 5.1 Mục tiêu
Chỉ để **minh hoạ định tính**, KHÔNG chạy đua chất lượng.

### 5.2 Thiết lập
- Dataset: CelebA hoặc MNIST, resize **32×32 hoặc 64×64**
- Subset nhỏ: `N ∈ {500, 5000}` (dữ liệu ít làm collapse rõ hơn)
- Forward model: mask che vùng lớn (ví dụ nửa dưới ảnh) → `y` = phần ảnh còn lại
- Model: U-Net nhỏ, conditioning bằng concat `y` theo channel
- Đo: sinh nhiều mẫu cho cùng `y`, đo pixel-wise variance; so sánh với ảnh training gần nhất (nearest neighbour trong training set) để phát hiện memorization

### 5.3 Hình cần xuất
- Grid: cùng một `y`, nhiều `x₀` khác nhau → nếu collapse, tất cả mẫu giống hệt nhau
- So sánh giữa checkpoint sớm (chưa overtrain) và checkpoint muộn
- Đặt cạnh ảnh training gần nhất để cho thấy selective memorization

---

## 6. Cấu trúc code mong muốn

```
project/
├── README.md
├── requirements.txt
├── configs/
│   ├── exp1_linear_gaussian.yaml
│   ├── exp2_gmm.yaml
│   └── exp3_inpainting.yaml
├── src/
│   ├── models/
│   │   ├── mlp_velocity.py       # MLP velocity field + time embedding
│   │   └── unet_small.py         # cho EXP-3
│   ├── flows/
│   │   ├── cfm.py                # loss CFM (conditional & unconditional)
│   │   ├── interpolants.py       # deterministic + stochastic interpolant
│   │   └── ode_solver.py         # Euler / RK4, xử lý kỳ dị gần t=1
│   ├── problems/
│   │   ├── linear_gaussian.py    # forward model + hậu nghiệm giải tích
│   │   ├── gmm.py
│   │   └── inpainting.py
│   ├── metrics/
│   │   ├── posterior_stats.py    # trace cov, mean error, distance tới training point
│   │   ├── velocity_error.py     # so sánh với dạng đóng (★)
│   │   └── distances.py          # MMD, Sinkhorn (geomloss)
│   └── train.py
├── scripts/
│   ├── run_exp1.sh               # bao gồm cả quét σ_obs, N, h
│   ├── run_exp2.sh
│   └── run_exp3.sh
├── notebooks/
│   └── analysis.ipynb            # tổng hợp biểu đồ
└── results/
    ├── figures/
    ├── raw/                      # csv/json các metric theo checkpoint
    └── RESULTS.md                # báo cáo cuối
```

---

## 7. Yêu cầu kỹ thuật quan trọng

1. **Reproducibility:** fix seed ở mọi chỗ; log seed vào config; lưu config kèm mỗi run.
2. **Kỳ dị tại t=1:** dạng đóng (★) nổ khi `t→1`. Khi integrate ODE, dừng tại `t = 1-ε` với `ε = 1e-3`, hoặc dùng step size giảm dần. **Ghi rõ trong code comment** rằng đây là xử lý kỳ dị có chủ đích, không phải hack.
3. **Không early-stopping mặc định.** Overtraining là đối tượng nghiên cứu. Chỉ bật early stopping trong nhánh so sánh riêng (để tái hiện remedy của 2603.14135).
4. **Log đầy đủ:** train loss, test loss, và tất cả metric ở Mục 3.5 tại mọi checkpoint. Lưu ra CSV để vẽ lại được mà không phải train lại.
5. **Chạy nhanh trước:** làm một chế độ `--smoke-test` chạy toàn bộ pipeline trong <2 phút với N nhỏ và ít iteration, để verify code đúng trước khi chạy full.
6. **Không dùng thư viện nặng nếu không cần.** EXP-1/EXP-2 chỉ cần `torch`, `numpy`, `matplotlib`, `geomloss`, `pyyaml`.

---

## 8. Thư viện / repo tham khảo

| Repo | Dùng để | Link |
|---|---|---|
| `facebookresearch/flow_matching` | Thư viện FM chính thức của Meta — tham khảo API và cách implement path/interpolant chuẩn | https://github.com/facebookresearch/flow_matching |
| `atong01/conditional-flow-matching` (torchcfm) | Implementation CFM gọn nhẹ, có sẵn ví dụ 2D — **nguồn tham khảo tốt nhất cho EXP-1/2** | https://github.com/atong01/conditional-flow-matching |
| `annegnx/PnP-Flow` | Cấu trúc config/training pipeline cho FM trong inverse problems | https://github.com/annegnx/PnP-Flow |
| `geomloss` | Sinkhorn / MMD distance | https://www.kernel-operations.io/geomloss/ |
| `torchdiffeq` | ODE solver (tuỳ chọn — tự viết Euler/RK4 cũng đủ) | https://github.com/rtqichen/torchdiffeq |

**Ưu tiên:** dùng `torchcfm` làm khung tham chiếu cho loss/interpolant, nhưng **tự viết** phần conditional + phần đo đạc, vì cần kiểm soát chính xác.

---

## 9. Bài đọc nền (không cần implement, chỉ để hiểu bối cảnh)

| arXiv ID | Tiêu đề | Vai trò |
|---|---|---|
| 2603.14135 | Solving physics-constrained inverse problems with conditional flow matching | **Nguồn hiện tượng** — variance collapse & selective memorization |
| 2510.18118 | Gradient Variance Reveals Failure Modes in Flow-Based Generative Models | **Nguồn kỹ thuật chứng minh** — Proposition 2, Remark 2 |
| 2210.02747 | Flow Matching for Generative Modeling (Lipman et al.) | Nền tảng FM |
| 2209.03003 | Flow Straight and Fast: Rectified Flow (Liu et al.) | Nền tảng RF |
| 2303.08797 | Stochastic Interpolants (Albergo et al.) | Khung hợp nhất flow/diffusion |
| 2502.09616 | Variational Rectified Flow Matching | Liên quan: velocity đa phương thức bị trung bình hoá |
| 2509.19903 | LIRF — velocity field collapse dưới khan hiếm dữ liệu | Related work về collapse |

---

## 10. Thứ tự thực hiện

**Giai đoạn A (bắt buộc trước tiên):**
1. Setup repo, requirements, config system.
2. Implement EXP-1 với cấu hình mặc định `d=2, k=1, N=200, σ_obs=0.1`.
3. Chạy `--smoke-test` verify pipeline.
4. Chạy full: train tới 200k iter, thu metric tại các checkpoint.
5. **Vẽ 3 biểu đồ cốt lõi:**
   - trace covariance vs iteration (kèm đường ground truth `trace(Σ_post)`) **[P1]**
   - velocity error so với dạng đóng (★) vs iteration **[P2]**
   - so sánh conditional vs unconditional **[P4]**
6. **DỪNG LẠI VÀ BÁO CÁO.** Nếu P1/P2/P4 không khớp dự đoán → báo cáo ngay, không chạy tiếp giai đoạn B.

**Giai đoạn B (chỉ khi A thành công):**
7. Quét `σ_obs` **[P5]**, quét `N` **[P6]**, quét `d` và `k`.
8. Thí nghiệm remedy: nhiễu trên `y` **[P7]** + so sánh với nhiễu trên interpolant.
9. EXP-2 (GMM, mode coverage).

**Giai đoạn C:**
10. EXP-3 (image inpainting, chỉ định tính).
11. Viết `RESULTS.md` tổng hợp.

---

## 11. Định dạng RESULTS.md mong muốn

```markdown
# Kết quả kiểm chứng

## Tóm tắt
[Mỗi dự đoán P1–P7: KHỚP / KHÔNG KHỚP / MỘT PHẦN, kèm 1 câu giải thích]

## P1 — Variance collapse
[Biểu đồ + số liệu + nhận xét]
...

## Những điều bất ngờ / không khớp lý thuyết
[Phần này QUAN TRỌNG — ghi trung thực mọi sai lệch]

## Chi tiết cấu hình đã chạy
[Bảng: config, seed, số iteration, thời gian chạy]
```

---

## 12. Nhắc lại điều quan trọng nhất

Đây là **kiểm chứng lý thuyết**, không phải tối ưu benchmark.

- Nếu phương sai **không** sụp về 0 → đó là phát hiện quan trọng, hãy điều tra tại sao (capacity không đủ? y chưa đủ phân biệt? optimization chưa hội tụ?) và báo cáo.
- Nếu kết quả khớp → cũng cần kiểm tra kỹ rằng không phải do bug (ví dụ: `y` bị leak vào input theo cách không mong muốn, hoặc ODE solver sai).
- **Không sửa số liệu, không chọn lọc seed thuận lợi.** Chạy nhiều seed (≥5) và báo cáo mean ± std.
