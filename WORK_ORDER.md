# Work Order — cfm-collapse

**Đọc `docs/THEORY.md` trước.** File này giả định bạn đã đọc nó. Mọi tham chiếu dạng
"Prop 17", "Thm 10" đều trỏ vào đó.

**Nguyên tắc bất di bất dịch:** đây là dự án kiểm chứng lý thuyết. Không sửa số liệu,
không chọn seed thuận lợi, không tinh chỉnh để ép ra kết quả mong muốn. Nếu số không
khớp lý thuyết, báo cáo trung thực — đó là thông tin, không phải lỗi.

---

## 0. Phát hiện quan trọng nhất (đọc kỹ trước khi làm bất cứ việc gì)

Theorem 10 cho một **đường tham chiếu chính xác, hữu hạn-N, không có tham số tự do**:

```
Cov_h(y) = Σ_j p_j^(h)(y) (x^j − x̄_h)(x^j − x̄_h)ᵀ,   p_j^(h)(y) ∝ K_h(y − y^j)
```

tính trực tiếp từ training set. Mình đã tính thử trên chính dữ liệu trong repo
(`p7y_h*_seed0`, tại 200k iter, trung bình trên 20 điểm điều kiện):

| h | `tr Cov_h` (Thm 10, chính xác) | đo được | `tr Σ_post` | n_eff |
|------|------|------|------|------|
| 0.01 | 0.427 | 0.472 | 1.004 | 2.2 |
| 0.05 | 0.973 | 0.800 | 1.004 | 8.2 |
| 0.1  | **1.145** | **0.812** | 1.004 | 15.4 |
| 0.5  | 1.244 | 1.218 | 1.004 | 61.9 |

`n_eff = 1/Σ_j p_j²` = số nguyên tử training thực sự có trọng số.

**Ba hệ quả bắt buộc phải phản ánh vào RESULTS.md:**

1. **Claim "khôi phục hoàn hảo tại h≈0.1" là sai.** Nó dựa trên việc so với
   `tr Σ_post = 1.004`. Nhưng mục tiêu đúng của model tại `h=0.1` là `Cov_h = 1.145`,
   và model đạt 0.812 — tức chỉ **71%** của population optimum. Không có "khôi phục
   hoàn hảo"; có một khoảng cách representation/optimisation còn lại. Việc nó *tình cờ*
   đi ngang qua `tr Σ_post` là trùng hợp, không phải thành công.

2. **Lý thuyết kernel dự đoán tốt hơn hẳn baseline.** Ở `h=0.01` (0.427 vs 0.472) và
   `h=0.5` (1.244 vs 1.218), Thm 10 khớp trong khi `Σ_post` lệch 2×. Đây là bằng chứng
   mạnh nhất trong toàn bộ dự án — mạnh hơn `rel.err` của velocity field, vì nó test
   **endpoint law**, không chỉ test trường vận tốc.

3. **Ở `h=0.5`, variance vượt `Σ_post`** (1.22 > 1.00) đúng như số hạng `h²‖J‖²_F` của
   Prop 15 dự đoán. `‖J‖²_F = 0.4031` (tính chính xác từ `A` đã lưu). Nhánh phải của
   chữ U là over-smoothing, không phải nhiễu.

Tất cả task dưới đây đều xoay quanh việc khai thác đúng phát hiện này.

---

## 1. Trạng thái hiện tại

### Đã đạt được

**Lý thuyết** (sau khi có `docs/THEORY.md` — trước đó chưa có):
- Toàn bộ population theory đã chặt, không còn giả định treo. `Lemma 3` chứng minh
  well-posedness nên Prop 5 / Thm 10 không cần "assume the flow is well defined" nữa.
- Bổ đề tương phản unconditional đã sửa đúng (Cor 6): unconditional **cũng** memorize
  toàn bộ empirical support; khác biệt nằm ở conditional variance.
- Prop 17 mới: nhiễu interpolant **không** đổi endpoint law với mọi σ — có nghiệm
  đóng `x_t = t x^i + s_t x₀`, đã verify symbolic.
- Prop 14 mới: `p_h^gen` atomic với mọi h ⇒ cận dưới `W₂` độc lập h.
- Prop 15 mới: khai triển `Cov_h = Σ + h²JJᵀ + …`, cho EXP-1 có dạng đóng.
- Prop 20/Cor 21: cận dưới representation, đại số đã kiểm.

**Thực nghiệm** (đã có trong repo, tin cậy):
- EXP-1: P1/P2/P3/P4 khớp; đối chứng unconditional rõ ràng; run mở rộng 1M iter cho
  thấy `trace(Cov)`, `vel_err`, `‖mean−x^i‖`, `loss` cùng giảm — xác nhận chúng là một
  hiện tượng.
- Pha "Bayes đúng" tới ~10⁴ iter đo được — giải thích vì sao early stopping hoạt động.
- P6 (quét N): đơn điệu rõ, 0.05 → 0.98.
- EXP-2 (GMM): mode coverage 1.00 → 0.72, MMD tăng ~40×.
- EXP-3 (MNIST): pixel-variance giảm ~100×, dist tới ảnh NN-train → 0.0005.
- `sanity_checks.py`: residual 1.8e-15, không rò rỉ `y`. Giữ nguyên, chạy trong CI.

### Chưa đạt được

| # | Vấn đề | Mức |
|---|---|---|
| G1 | Claim P7 "khôi phục hoàn hảo" sai chuẩn tham chiếu (xem §0) | **Cao** |
| G2 | Chưa có metric nào so với `Cov_h`; toàn bộ P7 so với `Σ_post` | **Cao** |
| G3 | Target stochastic interpolant sai (thiếu `γ̇(t)Z`) | **Cao** |
| G4 | Kết quả verify kernel `(†)/(‡)` chỉ có 1 file PNG, không có số trong RESULTS.md | **Cao** |
| G5 | Chưa đo `L(v_θ) − L(v_h⋆)` (Question B) | Trung bình |
| G6 | Chưa ước lượng Lipschitz ⇒ chưa tách được representation vs optimisation gap | Trung bình |
| G7 | Chưa đo Sinkhorn/MMD tới posterior **thật** cho EXP-1 (chỉ có cho EXP-2) | Trung bình |
| G8 | Sweep P5–P7 chỉ 2–3 seed, bảng không có error bar | Trung bình |
| G9 | P5 bị mô tả là "prediction failed" — sai logic (xem Part E) | Trung bình |
| G10 | §2.22 không có một trích dẫn nào | Trung bình |
| G11 | EXP-3 chỉ 1 seed, N=500, chưa quét N | Thấp |
| G12 | Run mở rộng diverge ~1M iter với lr cố định | Thấp |

---

## 2. Task

Làm **theo thứ tự**. T1–T4 là cốt lõi; đừng bắt đầu T5+ trước khi T1–T4 xong.

---

### T1 — Thêm module lý thuyết kernel + metric `Cov_h`  ⚠️ **ưu tiên cao nhất**

**File mới:** `src/metrics/kernel_theory.py`

Implement, dùng log-sum-exp toàn bộ (bandwidth nhỏ sẽ tràn số nếu không):

```python
def kernel_weights(y_q, Y, h):
    """p_j^(h)(y_q) ∝ K_h(y_q − y^j).  y_q:(k,), Y:(N,k) -> (N,)
    h == 0: point mass on argmin |y_q − y^j| (Corollary 11)."""

def kernel_moments(y_q, X, Y, h):
    """-> (x_bar, Cov, n_eff) theo Prop 13. n_eff = 1/sum(p**2)."""

def kernel_field(x, t, y_q, X, Y, h, source_std=1.0):
    """v_h*(x,t,y_q) theo Prop 8, eq (8.1).  x:(P,d), t:(P,) -> (P,d)"""

def cov_expansion(problem, h):
    """Prop 15 dạng đóng cho linear-Gaussian:
       tr Σ_post + h² ||J||_F²,  J = Σ_post Aᵀ / σ_obs².
       Trả về (predicted_trace, J_fro_sq)."""
```

**Ghép vào eval loop** (`src/train.py`, chỗ đang tính `trace_cov_mean`). Thêm cột vào
`raw/metrics.csv`:

```
trace_cov_kernel      # tr Cov_h(y^i) từ Thm 10, chính xác
n_eff                 # số nguyên tử hiệu dụng
ratio_to_kernel       # trace_cov_mean / trace_cov_kernel   <-- metric CHÍNH mới
mean_err_kernel       # ||mean(samples) − x̄_h(y^i)||
```

Giữ nguyên `trace_post`, `ratio_to_post` — nhưng **`ratio_to_kernel` mới là đại lượng
đo mức đạt tới population optimum.** `ratio_to_post` chỉ còn là đại lượng phụ.

**Acceptance:**
- Test đơn vị: `h → 0` cho `kernel_weights` hội tụ về one-hot tại nearest label (Cor 11);
  `h → ∞` hội tụ về `1/N` (Cor 12); `kernel_field(σ=0, h=0)` khớp
  `closed_form_velocity` trong `src/flows/interpolants.py` tới `1e-6`.
- Chạy lại eval trên checkpoint đã có (không cần train lại) và **tái hiện đúng bảng ở
  §0**: 0.427 / 0.973 / 1.145 / 1.244. Sai lệch >1% nghĩa là có bug.
- `cov_expansion` trả `‖J‖²_F = 0.4031` cho config mặc định `d=2,k=1,σ_obs=0.1`.

---

### T2 — Sửa target stochastic interpolant + verify Prop 17

**File:** `src/flows/interpolants.py`

Bug hiện tại: khi `sigma > 0`, `target` vẫn là `x1 - x0`. Đúng phải là (C.2):

```
γ(t)  = σ·sqrt(t(1−t))
γ̇(t) = σ(1−2t) / (2·sqrt(t(1−t)))
target = x1 − x0 + γ̇(t)·Z          # cùng Z đã dùng để tạo x_t
```

Bắt buộc dùng **cùng** `Z` cho cả `x_t` và target. `γ̇` phân kỳ ở `t→0,1` (khả tích,
bậc `|t(1−t)|^{-1/2}`); clamp `t ∈ [ε, 1−ε]`, `ε = 1e-4`, và **ghi comment rằng đây là
xử lý kỳ dị có chủ đích**. Xoá đoạn docstring biện minh "close enough for qualitative
comparison" — nó không đúng.

**File mới:** `scripts/verify_prop17.py` — kiểm nghiệm đóng, không cần mạng:

1. `s_t² = (1−t)² + σ²t(1−t)`; kiểm `c(t) = ½·d/dt log s_t²` bằng sai phân số.
2. Tích phân ODE `ẋ = x^i + c(t)(x − t x^i)` bằng RK4 từ nhiều `x₀`;
   kiểm khớp `x_t = t x^i + s_t x₀` (Prop 17b) tới `1e-6`.
3. Kiểm endpoint `x_{1−1e-3} → x^i` với `σ ∈ {0, 0.1, 0.3, 1.0}` — **bất biến theo σ**.
4. Kiểm `(1−t)|c(t)| → 1` khi `σ=0` và `→ ½` khi `σ>0` (Cor 18).

**Acceptance:** cả 4 kiểm tra pass. Chạy lại `p7i_sig{0.1,0.3}` với target đã sửa,
3 seed. **Dự đoán: variance vẫn KHÔNG được khôi phục** (Prop 17c) — nếu kết quả mới vẫn
~0.4 thì đó là *xác nhận lý thuyết*, hãy báo cáo như vậy, không phải như một thất bại.

---

### T3 — Đưa số verify kernel vào manuscript

**File:** `scripts/verify_kernel_theory.py` (đã có, mở rộng), `results/RESULTS.md`

Script hiện chỉ ghi PNG. Thêm:
- Xuất `results/exp1/_theory/raw/kernel_verification.csv` với các cột
  `h, rel_err_vs_kernel, rel_err_vs_star, tv_mixture, n_eff, seed`.
- Chạy trên **tất cả** `p7y_h*` × tất cả seed, không chỉ seed 0.
- Sửa reference `§2.X` trong docstring thành `docs/THEORY.md Prop 8 / Thm 10`.

**Acceptance:** RESULTS.md có một bảng số thật cho `(†)` và `(‡)`, không chỉ hình.
Kỳ vọng: `rel_err_vs_kernel < rel_err_vs_star` với mọi `h > 0`, và khoảng cách nới rộng
khi `h` tăng.

---

### T4 — Viết lại các claim trong RESULTS.md

**File:** `results/RESULTS.md`

1. **Mục P7** — viết lại theo §0. Bảng mới phải có cột `Cov_h` (Thm 10) bên cạnh
   `Σ_post` và giá trị đo. Bỏ chữ "khôi phục hoàn hảo". Thay bằng: model đạt 71%
   population optimum tại `h=0.1`; phần còn lại là representation/optimisation gap.

2. **Thêm caveat atomicity** (Prop 14) vào mục P7:
   > Label smoothing tái phân bố trọng số trên các điểm training, không sinh mẫu mới.
   > `p_h^gen` là atomic với mọi `h`, trong khi posterior thật liên tục — Prop 14 cho
   > cận dưới `W₂` **độc lập với h**. Khớp trace covariance là khớp mô-men bậc hai,
   > không phải khôi phục posterior. `n_eff` (bảng §0) cho thấy ngay cả `h=0.5` cũng
   > chỉ có ~62/200 nguyên tử mang trọng số.

3. **Mục P5** — bỏ nhãn "KHÔNG khớp". Dùng đúng câu chữ ở Part E:
   > Lý thuyết population không xác định sự phụ thuộc của collapse vào `σ_obs`; kết quả
   > phẳng quan sát được là một phát hiện thực nghiệm. Nó nhất quán với cơ chế
   > định-danh-qua-`y`, vốn đúng với mọi `σ_obs > 0`.

4. **Mục P6** — dùng câu chữ Part E: population optimum vẫn collapse với mọi N hữu hạn;
   việc `N=5000` không sụp cho thấy khoảng cách giữa nghiệm chính xác và regime
   representation/optimisation, **không** bác bỏ Prop 4.

5. **Mục P4** — sửa diễn giải. Unconditional **có** memorize (Cor 6);
   `trace(Cov) ≈ trace(Cov data)` chính là (6.1), không phải bằng chứng
   "không memorize".

**Acceptance:** không còn chỗ nào trong RESULTS.md gọi một đại lượng ở danh sách
"không được xác định" (Part E) là "dự đoán lý thuyết" đã "khớp" hoặc "không khớp".

---

### T5 — Đo khoảng cách tới population optimum (Question B)

**File mới:** `scripts/measure_optimality_gap.py`

Với mỗi checkpoint, ước lượng bằng Monte-Carlo trên cùng batch:

```
L(v_θ)                                  # loss thực nghiệm
L(v_h*)   = E[Var(U | X_t,t,Ỹ)]         # tính bằng kernel_field, = 0 khi h=0
gap       = L(v_θ) − L(v_h*)
```

Với `h=0` thì `L(v_h*) = 0` (Prop 4b) nên `gap = L(v_θ)` — đây chính là đại lượng đã
log sẵn. Giá trị mới nằm ở `h > 0`.

**Acceptance:** `gap ≥ 0` với mọi checkpoint (nếu âm ⇒ bug). Vẽ `gap` theo iteration
cho từng `h`, đặt cạnh `ratio_to_kernel`.

---

### T6 — Ước lượng Lipschitz, tách representation vs optimisation

**File mới:** `scripts/estimate_lipschitz.py`

Hai ước lượng, báo cáo cả hai:
- **Cận dưới (thực nghiệm):** power iteration trên `∂v_θ/∂x` tại các `(x,t)` lấy mẫu
  trên manifold, quét `t ∈ {0.5, 0.9, 0.99, 0.999}`. Báo `L(t)`, không chỉ `max_t`.
- **Cận trên (thô):** tích spectral norm các lớp tuyến tính.

So `d/(3L)` (Cor 21) với `L_trained` đã đo.

**Acceptance:** một bảng `t | L(t) | d/(3L(t)) | L_trained`. Kết quả **dự kiến** là
`d/(3L) ≪ L_trained` ⇒ kết luận: plateau chủ yếu là **optimisation gap**, không phải
representation. Đây là kết luận sạch và có giá trị — hãy báo cáo thẳng kể cả khi nó
làm Cor 21 thành không-bind. Ghi rõ trong RESULTS.md rằng Cor 21 là cận dưới, và cận
dưới không bind thì không có nghĩa là lý thuyết sai.

---

### T7 — Thêm metric khoảng cách tới posterior thật cho EXP-1

**File:** `src/metrics/distances.py` (đã có Sinkhorn/MMD cho EXP-2 — tái dùng)

EXP-1 có posterior giải tích `N(μ_post(y), Σ_post)` nên lấy mẫu ground truth trực tiếp
được. Thêm `sinkhorn_to_true_posterior` và `mmd_to_true_posterior` vào eval loop EXP-1.

**Acceptance:** báo cáo cùng với trace covariance ở mục P7. Kỳ vọng theo Prop 14:
khoảng cách này **không** về 0 tại bất kỳ `h` nào, kể cả `h` tối ưu cho trace covariance
— đây là kiểm chứng trực tiếp cho cận dưới atomicity, và là bằng chứng cho thấy
"khôi phục variance" ≠ "khôi phục posterior".

---

### T8 — Seed và error bar

**File:** `scripts/run_sweeps.py`, `scripts/analyze_sweeps.py`

Nâng lên **5 seed** cho toàn bộ P5, P6, P7y, P7i, d/k. Mọi bảng trong RESULTS.md báo
`mean ± std`. Với P5, kiểm định luôn: chênh lệch giữa các `σ_obs` có vượt biến động
giữa seed không? (Với `std ≈ 0.13` trên `mean ≈ 0.40`, nhiều khả năng là **không** —
và điều đó cần nói ra.)

**Acceptance:** không bảng nào trong RESULTS.md còn thiếu error bar.

---

### T9 — Trích dẫn

**File:** `docs/THEORY.md` §Positioning, `results/RESULTS.md`

Thêm trích dẫn thật cho dòng literature memorization: Pidstrigach (2022); Gu et al.,
*On Memorization in Diffusion Models*; Kadkhodaie et al. (2024); Biroli & Mézard;
Kamb & Ganguli. Nêu rõ đóng góp riêng là 5 điểm ở cuối `docs/THEORY.md`, **không phải**
bản thân quan sát "empirical minimizer memorizes".

---

### T10 — Tuỳ chọn, làm sau cùng

- **T10a:** chạy lại EXP-1 mở rộng với cosine lr-decay để đạt collapse sâu hơn mà không
  diverge. Đối chiếu `ratio_to_kernel` cuối cùng với 0.
- **T10b:** held-out `y`: báo cáo **median + số ca phân kỳ**, không dùng mean (mean đang
  bị chi phối bởi blow-up: 6e4 ± 1.2e5 là vô nghĩa).
- **T10c:** EXP-3 thêm seed, quét `N ∈ {500, 5000}`.
- **T10d:** thêm `n_eff` vào EXP-2/EXP-3 để nối mode coverage với lý thuyết kernel.

---

## 3. Ghi chú kỹ thuật

- **Ổn định số:** mọi tính toán kernel phải log-sum-exp. Với `h=0.01` và `k=1`, tỉ số
  `K_h` giữa các nguyên tử vượt `1e300` dễ dàng.
- **`h=0` trong `kernel_weights`:** không chia cho 0 — dùng nhánh point-mass tại nearest
  label (Cor 11).
- **Kỳ dị `t=1`:** giữ nguyên quy ước hiện có (`t_max=0.95` cho velocity error,
  dừng ODE tại `1−1e-3`). Ghi comment là xử lý có chủ đích.
- **Không train lại nếu không cần:** T1, T3, T5, T6 đều chạy được trên checkpoint đã có.
  Chỉ T2 (target mới) và T8 (thêm seed) cần train.
- **Reproducibility:** giữ nguyên quy ước fix seed + lưu `config.yaml` + `problem.json`
  mỗi run.

---

## 4. Định nghĩa "xong"

1. `docs/THEORY.md` nằm trong repo, mọi mệnh đề đều có chứng minh, không còn "assume".
2. `ratio_to_kernel` là metric chính trong mọi bảng P7; `ratio_to_post` chỉ là phụ.
3. Bảng ở §0 tái hiện được bằng code trong repo (sai số <1%).
4. Target stochastic interpolant đã sửa; `verify_prop17.py` pass; P7i chạy lại và được
   báo cáo như **xác nhận** Prop 17c.
5. Không claim nào trong RESULTS.md vi phạm quy tắc phát ngôn ở Part E.
6. Mọi bảng có `mean ± std` trên ≥5 seed.
7. Có trích dẫn cho literature memorization.
