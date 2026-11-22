# Bài B: kết quả phân tích mới và các chỗ cần sửa (2026-11-21)

Bản ghi nhớ này dành cho session đang viết `paper_mechanism/main.tex` (và `paper_theory/`). Session
viết bản ghi nhớ không sửa hai thư mục đó. Mọi số dưới đây đã được **tính lại độc lập** bởi một
verifier riêng (script `scripts/paperB_verify_*.py`), trừ khi ghi khác. Số dòng tham chiếu
`paper_mechanism/main.tex` bản 02:21 ngày 2026-11-21; nếu file đã đổi, tìm theo câu được trích.

> **Đính chính (2026-11-21, sau kiểm tra độc lập):** mục 5 ở cuối file liệt kê 43 lỗi đã được xác nhận, kèm câu sửa. **Mục 5 thay thế các câu tương ứng ở mục 1–3**, nhất là các đoạn LaTeX dùng E7. E7, hình của nó và các diễn giải ở 1.1, 1.2, 2.2 **chưa qua verifier độc lập**: chỉ 32 vector ảnh của sub500 s0 được kiểm khớp với `n3_strips`.

Nguồn:

| Phân tích | Kết quả | Verifier |
|---|---|---|
| Swap hai chiều, đồng hồ chọn/hạ cánh | `results/paperB_20261121/swap/` | `verify_swap/` (215/215 khớp) |
| Certificate (bất đẳng thức tích phân, Heun chain) | `results/paperB_20261121/certificate/` | `verify_certificate/` |
| Tỉ số radial, giả thiết (b), (c) | `results/paperB_20261121/radial/` | `verify_radial/` |
| Thông tin gia tăng so với khoảng cách NN | `results/paperB_20261121/incremental/` | `verify_incremental/` |
| Transfer trên CIFAR CFM (S10) | `results/paperB_20261121/transfer/` | `verify_transfer/` |
| Khoảng tin cậy (EXP-1, slope CIFAR, AUC EDM) | `results/paperB_20261121/uncertainty/` (có `tables.tex`) | `verify_uncertainty/` |
| **E7 mới:** σ collapse của exact posterior | `results/paperB_20261121/collapse_sigma/summary.json` | **chưa verify độc lập**; chỉ 32 vector ảnh của sub500 s0 khớp `n3_strips` (≤ 2.4e-4) |
| **E1 mới:** swap theo cửa sổ σ, public model | đang chạy trên CPU lab09 → `results/paperB_20261121/window_swap_public/` | chưa có |

---

## 1. Sửa bắt buộc

### 1.1 "net→exact luôn hạ cánh" là tính chất của sampler, không phải phép đo

Bước Heun cuối là một bước Euler xuống σ = 0, nên output chính là `D(x; 0.002)`. Với exact field,
đó là ảnh train gần nhất, đúng tới độ chính xác float (`heun()` trong
`scripts/n3_edm_memorization.py`). Verifier dựng một đối chứng tổng hợp: một denoiser Gaussian không
bao giờ hạ cánh (100% off-atom) trở thành 0% off-atom khi **chỉ lần gọi thứ 35/35** dùng exact field.
Vì vậy "every sample ends on a training image at every s" và "replacing the field on the last 2%
turns no memorisation into complete memorisation" đúng theo cấu trúc, không phải bằng chứng cho việc
hạ cánh được quyết định muộn. Bằng chứng thật nằm ở chiều exact→net.

Các chỗ cần sửa:
- Abstract l.76–77: "Handed the network's state at any noise level, the exact field lands every
  sample on a training image".
- Contributions l.147–148: "Network early and exact field late ends on a training image at every swap level".
- Related work l.198–200: "the public EDM model, which never copies, copies for every sample once
  the exact field replaces it on the last 2% of the time".
- Caption `fig:swap` l.584–585 và caption `tab:swap` l.613–614.
- `sec:swap` l.618–621 và l.636–637 ("The exact field lands from whatever state it is handed").

Câu thay thế cho l.618–621 (đoạn "The image is chosen early"):

```latex
With the network running down to $s$ and the exact field below, every sample ends on a training
image at every $s$. This is a property of the sampler rather than a measurement: its last step
returns the denoiser output at $\sigma=0.002$, which for the exact field is the nearest training
image, so an exact field used for the last of the $35$ denoiser evaluations alone already lands
every sample. What this direction measures is \emph{which} image is reached.
```

Abstract l.75–82, đề xuất:

```latex
On class-conditional EDM models on CIFAR-10 we separate two decisions by swapping the denoiser
mid-trajectory. Handed the network's state at $\sigma\le1$, the exact field ends on the training
image nearest to the network's own endpoint for at least $88\%$ of samples, and the network has
chosen its image within the band of noise levels where the exact posterior over the training
images collapses onto one of them. Handed the exact field's state, the public model, which never
copies, lands for half of the samples only when the swap comes at $\sigma\approx0.5$, while a model
trained on $500$ images lands from every swap level. The image is chosen early; whether it is
reached is decided late, by the contraction that the relative field error leaves.
```

### 1.2 Đoạn "Two times" (l.202–211) ghép sai cặp

Lựa chọn ảnh của bài B tương ứng với **collapse time** của Biroli et al., không phải speciation.
Việc hạ cánh không có đối ứng trong lý thuyết exact score của họ, vì ở đó hạ cánh nằm gọn trong
collapse. Ngoài ra, Biroli et al. **cũng đo t_C trên mạng đã train** (DDPM, tập nhỏ đang
memorize), nên "measured on the network's trajectory" không phải điểm khác biệt.

Con số đúng của họ (verifier đọc từ PDF): legend Fig. 5 cho t_C = 0.32, 0.63, 1.71 với
ImageNet16, ImageNet32, LSUN. Đổi ra σ là khoảng 0.95, 1.6, 5.4 theo thang pixel [0, 1] của họ.
Theo thang [−1, 1] của EDM, các giá trị này khoảng gấp đôi: 1.9, 3.2, 10.9. Đừng viết "t ≈ 0.6
cho mọi tập": 0.60 là xác suất cloning φ_C, không phải t_C.

Đề xuất thay thế (dùng E7, mục 2.2):

```latex
\paragraph{Two times.} For the exact empirical score, \citet{biroli2024dynamical} derive a
speciation time, when the class is chosen, and a later collapse time, after which the trajectory
is captured by one training point; \citet{raya2023ssb} describe such decisions as symmetry
breakings, and \citet{li2024critical} bound the windows in which features are decided under a
perfect score. Our first decision is the collapse, not the speciation: on our training sets the
exact posterior over the images of a class concentrates on one image between $\sigma=0.8$ and
$3.8$ with all $5000$ images per class (Section~\ref{sec:swap}), and the public network has chosen
half of its images by $\sigma=2.5$ and $90\%$ by $\sigma\approx0.95$. \citet{biroli2024dynamical}
also estimate the collapse time on trained networks, on small training sets where these networks
memorise. What the exact-score picture folds into the collapse, and what the swaps separate, is the
landing: a generalising network selects an image on the exact posterior's schedule and then does
not reach it.
```

Câu về Bonnaire giữ nguyên. `favero2025bigger` phải là năm **2026** (TMLR 2026, J2C Certification).

### 1.3 "The late contraction ties the baseline" (l.741–742) là phép so sổ sách

`dD` tại σ = 0.002 **bằng đúng** d1 (max |chênh| = 0), mà d1 lại là tử số của nhãn off-atom.
So sánh công bằng là ở đầu cửa sổ: tại σ = 0.585, khoảng cách NN cho AUC **0.990 [0.986, 0.994]**,
late contraction cho **0.983 [0.977, 0.988]**, hiệu cặp 0.007 [0.004, 0.010]. Thêm vào đó:
- R² của log d1: log dD(0.585) đạt 0.991 (gộp) và 0.965 (on-atom), còn C đạt 0.976 và 0.883.
- Tích phân lịch sử khoảng cách NN trên cùng cửa sổ, không dùng field error, cho tách nhóm ngang
  hoặc hơn C. Khi đã có lịch sử đó, C chỉ thêm tối đa +0.002 AUC.
- Field error (ϱ) **không bổ sung** gì so với log dD từ σ ≈ 1.9 trở xuống (|ΔAUC| ≤ 0.002).

Câu thay thế cho l.741–742:

```latex
At the end of sampling the comparison is bookkeeping, since the denoiser output at $\sigma=0.002$
is the sample itself; at the start of the late window the distance from $D_\theta$ to the nearest
training image separates the groups at least as well as the late contraction (AUC $0.990$ against
$0.983$, paired difference $[0.004,0.010]$), and it predicts $\log d_1$ better ($R^2$ $0.991$
against $0.976$).
```

Contribution l.152–158 nên đổi tên và nội dung, ví dụ:

```latex
\item \emph{What carries out landing} (Section~\ref{sec:contraction}). Along the sampler's own
  trajectories the radial ratio of Theorem~\ref{thm:relerr}(a) accounts for the change of the
  distance to the selected image (per-sample correlation at least $0.993$), and the contraction
  that the relative error leaves over $\sigma\in[0.002,0.585]$ is $1.75$ against $0.68$ for on- and
  off-atom samples of a balanced model. Which samples will land is already visible at the start of
  that window, in the distance from the denoiser output to the nearest training image (AUC $0.990$
  at $\sigma=0.585$, against $0.983$ for the late contraction), so we read Theorem~\ref{thm:relerr}
  as the mechanism of landing, not as a detector. The Heun bound certifies contraction at every
  step once the schedule has enough steps, without changing which image is reached.
```

Abstract l.80–82 ("which separates memorised from other samples, though no better than...") đã
được thay ở mục 1.1.

### 1.4 Slope CIFAR (l.507): "0.481 ± 0.037 at h=4 and −0.156 at h=6"

- Cả 48 điều kiện trong `results/exp3/_cifar_ddpm/reeval.json` đến từ **một** instance. Trong
  `results/exp3/_rerun` có ba instance, mỗi instance 48 điều kiện, và s0 là đúng instance đã công bố
  nhưng được train lại.
- h = 4: các slope train lại là 0.344, 0.316, 0.427 (trung bình 0.362, khoảng t với df = 2 là
  [0.219, 0.505]). Chỉ train lại cùng instance đã làm slope dịch 0.137, tức sai số chuẩn OLS 0.037
  đánh giá thấp độ biến thiên giữa các lần chạy. Kết luận "slope nằm xa dưới 1" vẫn vững.
- h = 6: −0.156 **không lặp lại được**. Ba lần train lại cho +0.082, +0.412, +0.598 (khoảng t
  [−0.285, 1.013]). Robust interval của chính instance đã công bố cũng chứa 0. Không nên trích −0.156.
- h = 5: sai số chuẩn OLS 0.049 so với HC3 0.142 (`tab:cifarddpm` l.1744–1746 in 0.049).

Đề xuất: báo cáo slope h = 4 dạng "0.36 (three instances, [0.22, 0.51]); 0.48 on the instance
analysed below". Với h = 6, viết là chưa xác định.

### 1.5 Transfer CIFAR (l.532–533)

- "with AUC at least 0.95 by t ≈ 0.53": h = 4 cho 0.970 [0.961, 0.978]. h = 6 cho 0.951
  [0.942, 0.959], tức chỉ ước lượng điểm đạt 0.95. Nên viết "0.97 and 0.95 at h = 4, 6 by
  t ≈ 0.53, and 0.99/0.98 by t ≈ 0.63".
- "the same network along the exact trajectory ... does not separate them": đúng ở h = 4
  (0.489–0.524). Ở h = 6 thì tách yếu nhưng phát hiện được (0.529–0.577, cluster CI > 0.5 với mọi
  t ≥ 0.71). Nên viết "separates them barely if at all (AUC at most 0.58)".
- Quy ước sd không nhất quán: S10 (l.1387–1388) dùng ddof = 1, EXP-C (l.1363–1364) dùng ddof = 0.

### 1.6 EXP-1: thay ± SD bằng khoảng t (5 seed)

`results/paperB_20261121/uncertainty/tables.tex` có bảng đề xuất. Số chính:
- 0.396 [0.220, 0.573] tại 2e5.
- 0.120 [0.046, 0.195] tại 1e6 (cosine).
- Không điều kiện: 1.926 [1.690, 2.163].
- Memorisation ratio: 0.650 [0.604, 0.696] có điều kiện, 0.389 [0.345, 0.433] không điều kiện.

Các tương phản theo cặp seed nên thêm:
- tr Cov / tr Σ_post = 0.389 [0.217, 0.560] tại 2e5.
- cosine − constant = −0.276 [−0.393, −0.160].
- Không điều kiện: tr Cov / tr X̂ = 0.997 [0.971, 1.024].

Hai lưu ý:
- Kernel ở h = 0.01: 1.308 [0.786, 1.830]. Đây là "uninformative", không phải "unstable".
- |mean − x^i| − |mean − μ_post| tại 2e5 = −0.277 [−0.568, 0.014], không có ý nghĩa thống kê; một
  trong năm seed đi ngược chiều. Tại 1e6 (cosine): −0.679 [−0.936, −0.422].

### 1.7 Giả thiết (b) của Thm relerr (l.715–716)

"reach ϱ_t ≈ 1 from σ ≈ 0.14 on, where the hypothesis of Theorem relerr(b) fails" chỉ đúng theo
nghĩa định lượng. Trên cửa sổ hữu hạn, 82.9/97.7/99.8% mẫu off-atom vẫn có ϱ < 1 ở mọi mức muộn.
Đề xuất: "where $\varrho_t$ approaches one, so that (b) certifies little contraction ($C=0.29$
against $2.55$)". Câu "consistent with, but does not verify, (c)" giữ nguyên, verifier xác nhận
đây là cách viết đúng.

### 1.8 Các câu nhỏ trong `sec:swap`

- l.641–649 ("this appears to be because little time is left rather than because the network
  contracts ... falls roughly in proportion to s"):
  - Tỉ lệ thuận chỉ đúng với s ≤ 0.2. Độ dốc log-log là 0.47 (5 → 0.5), 0.84 (0.2 → 0.02) và
    0.90 (0.1 → 0.02).
  - Network vẫn co một phần, khoảng 1.4–3 lần so với độ lệch điển hình σ√d lúc bàn giao. Con số
    này là ước lượng, vì khoảng cách lúc bàn giao không được ghi.
  - Đề xuất: "partly because little time is left: below $s=0.2$ the median distance falls roughly
    in proportion to $s$".
- Appendix (`app:relerr-exp`) ghi "100 latents per class for the subset models". Các swap run dùng
  **50 latents mỗi lớp, seed 0, n = 500**. Cần ghi rõ n của swap.
- Câu hỏi TODO ở README ("whether the 1000-image subset is class-balanced") đã có trả lời: có.
  `scripts/make_edm_cifar_subset.py` lấy `n // 10` ảnh mỗi lớp, nên subset này có 100 ảnh mỗi lớp
  (`data/edm_subsets/cifar10_sub1000_s0_indices.npy`).

### 1.9 Bài A (`paper_theory/`): Liu et al. v2 xoá Thm 3.18

`liu2026geometric` bản v2 (29/10/2026, đổi tên thành "Convergence of Singular Dynamics Driven by
Mixed Logarithmic Heat Gradients") bỏ Theorem 3.18 và Remark 3.19. Theorem 2.5 mới của v2 chứng minh
**mọi** quỹ đạo hội tụ với luật atomic hữu hạn, không cần giả thiết limit set. Điều này xoá phân biệt
mà bài A đang nêu ở l.270, l.1560–1584 và dòng "Hypothesis on trajectories" của bảng so sánh.

Phần v2 không có là phát biểu **hầu hết** điểm đầu đều kết thúc trên một atom. Remark 2.7 của v2 nói
hội tụ về equilibrium không nâng lên được thành hội tụ về local minimum cho mọi điểm đầu. Phát biểu
"almost every" này, cùng các kết quả về schedule, họ prior và signed combinations, vẫn là điểm khác
biệt của bài A.

Cần sửa: cite v2, hoặc ghi rõ v1, và viết lại phần so sánh quanh phát biểu "almost every".

---

## 2. Kết quả mới nên đưa vào

### 2.1 Đồng hồ chọn và hạ cánh, có khoảng tin cậy (`swap_clocks.json`)

Cách đọc các ký hiệu:
- `s_sel`: mức σ tại đó tỉ lệ "=L" của net→exact đạt 90%. Mốc 50% được ghi riêng.
- `s_land`: mức σ tại đó tỉ lệ off-atom của exact→net cắt 50%.
- Mọi mức đều được nội suy theo log s giữa 8 mức swap. Khoảng tin cậy là bootstrap, có điều kiện
  theo phép nội suy đó.

| model | =L 50% | s_sel (=L 90%) | s_land (50%) | ghi chú |
|---|---|---|---|---|
| public 50k | 2.48 [2.13, 2.87] | 0.95 [0.74, 1.05] | 0.51 [0.47, 0.54] | landing 10/50/90% tại s = 0.92/0.51/0.21 |
| 1000 ảnh, 0.5 Mimg | 4.74 | 0.82 [0.65, 1.02] | 1.33 [1.29, 1.37] | on-atom tại s = 1: 76.8% (public 4.4%) |
| 500 ảnh | > 5 (=L 92.8% tại s = 5) | > 5 | không có | exact→net 0/500 off-atom ở mọi s |

- **So ở cùng ngưỡng:** chọn luôn trước hạ cánh.
  - 50/50: public 2.48 so với 0.51; 1000 ảnh 4.74 so với 1.33 (P = 1.000).
  - 90/90: 1000 ảnh 0.82 so với 0.56 (P = 0.998). Ở public, tỉ số là 4.47 [3.47, 4.98].
  - Thứ tự chỉ "đảo" khi so ngưỡng 90% của chọn với ngưỡng 50% của hạ cánh. Đừng báo cáo như vậy.
- **Mức hiệu dụng** (trung bình nhân của khung bàn giao) trên public: s_sel 0.76 [0.60, 0.86] và
  s_land 0.42 [0.39, 0.45]. Khung bàn giao trên lưới 18 bước, dạng s: (mức net cuối, mức exact đầu):
  5: (5.32, 3.26); 2: (3.26, 1.92); 1: (1.09, 0.585); 0.5: (0.585, 0.296); 0.2: (0.296, 0.140);
  0.1: (0.140, 0.060); 0.05: (0.060, 0.023); 0.02: (0.023, 0.0075).
- **Model 1000 ảnh (mới).** Late field của nó hạ cánh trạng thái exact-field dễ hơn nhiều so với
  public (76.8% so với 4.4% on-atom tại s = 1), nhưng mẫu của chính nó không bao giờ hạ cánh. Vậy
  hạ cánh được quyết định bởi late field **tác động lên trạng thái của chính quỹ đạo**, không phải
  một tính chất riêng của late field. Câu chữ nên là "decided late along the trajectory". So sánh
  với model 500 ảnh chỉ mang tính gợi ý, vì hai model khác nhau cả thời gian train (0.5 so với
  10 Mimg).
- **Model 500 ảnh.** Trong 323 mẫu mà net và exact chọn ảnh khác nhau, exact→net tại s = 5 kết thúc
  trên ảnh của exact 92.9% [89.5, 95.2], trên ảnh của chính net 3.1% [1.7, 5.6], và 0/323 off-atom.
  Late field memorize co về ảnh gần trạng thái nhất, không về ảnh nó đã chọn.
- **Lưu ý khi đọc =L của public:** endpoint learned gần như cách đều hai ảnh gần nhất (median d1/d2
  là 0.977). "=L" vì thế đo việc trạng thái cố định *basin của exact field*, không phải việc network
  tiến về một ảnh.

### 2.2 E7 mới: lựa chọn của network bám theo collapse của exact posterior

Tại điểm x = y + σε, với y là một ảnh **test** cùng lớp, exact posterior trên n_c ảnh train của lớp
là w_j ∝ exp(−|x − y_j|²/2σ²). Thống kê lấy trung bình theo lớp, ε cố định cho mỗi điểm. Subset được
sinh lại đúng như `make_edm_cifar_subset.py` (cân bằng lớp) và đã kiểm khớp với vector ảnh trong
`n3_strips` (sai số ≤ 2.4e-4). Script: `scripts/paperB_collapse_sigma.py` (numpy, 137 s trên CPU).

| ảnh/lớp | σ: median max w = 0.5 | σ: 90% điểm có max w ≥ 0.5 | σ: 90% điểm có max w ≥ 0.9 | retrieval: median w(ảnh của mình) = 0.5 | NN test→train (median) |
|---|---|---|---|---|---|
| 50 (sub500 s0 / s1) | 7.52 / 7.41 | 3.82 / 3.77 | 1.44 / 1.38 | 8.89 / 8.45 | 24.0 / 24.1 |
| 100 (sub1000) | 6.39 | 3.30 | 1.22 | 7.89 | 23.0 |
| 200 (sub2000) | 5.67 | 2.88 | 1.10 | 7.09 | 22.4 |
| 5000 (toàn bộ) | 3.82 | 1.99 | 0.78 | 5.14 | 19.4 |

Cách đọc:
- **Public:** network chọn 50% ảnh tại σ = 2.48 và 90% tại 0.95. Cả hai nằm trong dải collapse
  [0.78, 3.82] của exact posterior với 5000 ảnh mỗi lớp.
- **1000 ảnh:** network chọn ở 4.74 và 0.82, so với dải [1.22, 6.39]. Mốc 50% nằm trong dải, mốc
  90% hơi muộn hơn.
- **500 ảnh, đang memorize:** model chọn sớm hơn nữa (σ > 5). Điều đó khớp với đường *retrieval*
  (posterior tại một ảnh *train* đã thêm nhiễu tập trung vào chính ảnh đó tại σ ≈ 8.9), đúng như kỳ
  vọng ở một sampler mà trạng thái luôn ở gần ảnh train cộng nhiễu.
- **Tập càng lớn thì collapse càng muộn** (σ nhỏ hơn): mốc median giảm từ 7.5 (50 ảnh mỗi lớp) xuống
  3.8 (5000 ảnh mỗi lớp).

Như vậy quyết định thứ nhất chính là collapse của Biroli et al., đo trực tiếp trên dữ liệu, và
network đi theo nó. Quyết định thứ hai (hạ cánh) thì exact-score theory không có.

Đoạn đề xuất cho `sec:swap`, đặt sau "The image is chosen early":

```latex
\paragraph{The choice follows the exact posterior.} For a point $x=y+\sigma\varepsilon$ with $y$
a CIFAR-10 test image of class $c$, the exact posterior over the training images of the class,
$w_j\propto\exp(-|x-y_j|^2/2\sigma^2)$, concentrates on one image as $\sigma$ decreases. With all
$5000$ images per class, the median largest weight passes $1/2$ at $\sigma=3.8$, and the largest
weight is at least $1/2$ for $90\%$ of points from $\sigma=2.0$ and at least $0.9$ from $\sigma=0.78$.
The public network's choice, $50\%$ of samples at $\sigma=2.5$ and $90\%$ at $\sigma=0.95$, falls in
this band. With $100$ images per class the band moves up to $[1.2,6.4]$, and the $1000$-image
network chooses at $4.7$ and $0.82$. The memorising $500$-image model chooses earlier still, near
the level ($\sigma\approx8.9$) where the posterior at a noised \emph{training} image concentrates on
that image, as expected of a sampler whose states stay near noised training images. The first
decision is the collapse of \citet{biroli2024dynamical}, measured on our training sets; the network
follows it, and Section~\ref{sec:contraction} turns to the second.
```

Hình: `results/paperB_20261121/collapse_sigma/fig_collapse_vs_choice.pdf` (rộng FULL_W, ba panel,
theo `figstyle`). Script: `scripts/make_collapse_choice_figure.py`, vẽ trên lab09 với
`PYTHONPATH=.:scripts`. Chép sang `paper_mechanism/figures/` nếu dùng. Caption gợi ý:

```latex
\caption{The network chooses its image where the exact posterior collapses, and lands much later
(EDM on CIFAR-10; sampling runs left to right). Blue: the exact posterior over the training images
of a class at a noised test image, share of points whose largest weight is at least $1/2$ (solid)
or $0.9$ (dashed), and at a noised training image, share whose weight on that image is at least
$1/2$ (dotted), for the training set of each model. Vermillion: share of net$\to$exact endpoints on
the network's own image ($=$L). Black: share of exact$\to$net endpoints on a training image. Swap
values at the eight hand-over levels, $500$ latents per model, Wilson $95\%$ intervals. (a)~Public
model; (b)~$1000$ images, trained for $0.5$\,Mimg; (c)~$500$ images.}
```

### 2.3 Tính dự đoán được: hạ cánh đã thấy rõ từ σ ≈ 1

Trên model 2000 ảnh, AUC của dD là 0.909 (σ = 3.26), 0.962 (1.92), 0.988 (1.09) và 0.990 (0.585).
R² của log d1 theo log dD(σ) là 0.671, 0.852, 0.959 và 0.991 tại cùng các mức đó. Đọc theo nghĩa dự
đoán, việc mẫu nào sẽ hạ cánh đã thấy được gần σ ≈ 1. Điều này không mâu thuẫn với can thiệp swap,
nhưng nên viết "landing is predictable by the start of the late window and carried out by the late
contraction" thay cho "decided only late".

### 2.4 Radial và certificate (tuỳ chọn, cho appendix)

**Radial.**
- Bất đẳng thức rad ≤ ϱ + ω/n: 0 vi phạm trong 240000 cặp (mẫu, mức).
- Co rút thực tế log(n(0.585)/n(0.002)) tương quan 0.993/0.997/1.000 với tích phân hình thang của
  (1 − rad).
- Off-atom có rad ≥ 0.95 ở mọi mức từ σ = 0.060 trở xuống: 93% và 89% (hai model 500 ảnh); không mẫu
  on-atom nào như vậy.
- Error trỏ dọc x − y với off-atom (median rad/ϱ là 0.62–0.99), và gần như vuông góc với on-atom
  (0.22–0.60).
- Cảnh báo: phân tách `q1 + r1` không thoả identity ở 0.06 ≤ σ ≤ 1.92 (4 nút cầu phương). Không dùng
  bảng `Q_SUMMARY.md` ở các mức đó.

**Certificate tích phân** (Cor certificate trong bản nháp ở scratchpad; `paper_mechanism` hiện
không có).
- Bất đẳng thức log(n0/n1) ≥ C_ϱ − Ω: 1/3000 vi phạm ở 18 bước (thiếu 0.28%), 0 ở 36 và 64 bước,
  0 trên public.
- Slack trung vị 0.32–0.37 nats, chủ yếu đến từ góc giữa error và hướng tới ảnh.
- Đây là phép kiểm bất đẳng thức, **không** phải bộ certify hay bộ phát hiện: luật "B_K < d2/3" chứa
  d1 (vì err(0.002) = d1).

**Heun chain** (Prop heun(b), chặt chẽ cho sampler rời rạc).
- Certify hạ cánh (B_K < d2/3) ở 0/499, 0/956 và 2/959 mẫu on-atom ở 18 bước; 946/960 (98.5%) ở
  36 bước; 952/961 (99.1%) ở 64 bước; 0 vi phạm.
- Lưu ý: bound này cũng dùng ϱ đo dọc toàn bộ quỹ đạo.

### 2.5 Transfer: luật cảnh báo sớm (tuỳ chọn)

Tại t ≈ 0.63, ngưỡng Youden chọn out-of-sample (leave-one-seed-out) cho:
- h = 4: TPR 0.930, FPR 0.046.
- h = 6: TPR 0.953, FPR 0.100.

Kết quả này tốt ngang luật endpoint "d1 > 4", vốn chỉ là sổ sách. Ngưỡng ở t ≈ 0.53 thì phụ thuộc
băng thông (4.03 so với 5.36).

### 2.6 AUC = 1.000 trên các model 500 ảnh

Đây là tách hoàn toàn: khoảng [1.0, 1.0] bị suy biến. Cận dưới một phía 95% không phụ thuộc phân
phối là khoảng 0.92–0.93. Baseline NN cũng tách hoàn toàn trên cả hai model.

---

## 3. Tài liệu tham khảo

**Sửa hoặc thêm vào `paper_mechanism/refs.bib`:**

```bibtex
@inproceedings{shah2025ambient,
  title     = {Does Generation Require Memorization? Creative Diffusion Models using Ambient Diffusion},
  author    = {Shah, Kulin and Kalavasis, Alkis and Klivans, Adam R. and Daras, Giannis},
  booktitle = {Proceedings of the 42nd International Conference on Machine Learning},
  series    = {Proceedings of Machine Learning Research},
  volume    = {267},
  pages     = {54143--54166},
  year      = {2025}
}
@inproceedings{li2024critical,
  title     = {Critical windows: non-asymptotic theory for feature emergence in diffusion models},
  author    = {Li, Marvin and Chen, Sitan},
  booktitle = {Proceedings of the 41st International Conference on Machine Learning},
  series    = {Proceedings of Machine Learning Research},
  volume    = {235},
  pages     = {27474--27498},
  year      = {2024}
}
@misc{kaiser2026structural,
  title         = {Beyond Sample Copying: Structural Memorization in Diffusion Models},
  author        = {Kaiser, Tim and Kollmann, Markus},
  year          = {2026},
  eprint        = {2603.13419},
  archivePrefix = {arXiv},
  note          = {Version 3}
}
```

**Sửa metadata:**
- `favero2025bigger`: năm 2026, TMLR (J2C Certification). Có thể đổi key thành `favero2026bigger`.
- `jain2025attraction`: CVPR 2025, pp. 12871–12879, DOI 10.1109/CVPR52734.2025.01201.
- `li2026kinetic`: ICML 2026. arXiv ghi là Spotlight; trang ICML ghi poster và viết tiêu đề có gạch
  nối "Kinetic-Energy".
- `beltran2026reward`: NeurIPS 2026 (poster).
- `dodson2026calm`: ICML 2026, PMLR 306:25643–25694.
- `sesmat2026leaks`: PMLR 306:109269–109293.
- `physicscfm2026`: ghim v3, vì v1 có tiêu đề và danh sách tác giả khác. Câu ở intro "return training
  examples" nên viết mềm đi: bài đó chỉ cho thấy phương sai co lại, không có thí nghiệm nào cho thấy
  mẫu sao chép ảnh train.

**Cách định vị (đã được kiểm lại; các chỗ extractor viết sai đã sửa):**
- **Bertrand et al.** (TODO l.197 đã giải quyết).
  - Họ nói rõ generalisation xuất hiện sớm. Trong hybrid sampler của họ (closed-form trước, learned
    sau τ), output thôi mới lạ khi τ ≥ 0.3, tức σ ≲ 2.3 theo đơn vị EDM. Với τ ≥ 0.4 (σ ≈ 1.5), output
    gần như chính mẫu u*. Quyết định nằm khoảng τ ≈ 0.2–0.4 (σ ≈ 4 tới 1.5).
  - Họ cũng nói thất bại muộn không giải thích hết generalisation.
  - Chỉ số LPIPS của họ không tách được chọn và hạ cánh. Đóng góp của bài B là tách hai việc này.
- **Li et al. 2026 (kinetic).**
  - Soft landing chỉ ở t ≥ 0.6 (σ ≲ 0.67) giảm tỉ lệ copy từ 37.3% xuống 30.2% (19.4% với β0 = 0.02,
    nhưng FID tệ đi). Riêng early boost thì không đổi tỉ lệ copy.
  - Đây là bằng chứng can thiệp độc lập cho việc hạ cánh muộn.
- **Shah et al. 2025.**
  - Họ chỉ train phần nhiễu cao trên dữ liệu nhiễu; σ chuyển tối ưu nằm trong [0.4, 4], trùng dải
    chọn ảnh của bài B.
  - Quan hệ là "nuances", không phải "conflicts".
- **Kim et al. (NeurIPS 2026, v2).**
  - Với CFG, prompt bị memorize chốt ảnh ngay ở bước đầu, khớp việc model memorize chọn sớm hơn.
  - Điều kiện ở bước cuối của họ dành cho dự đoán Bayes-optimal, nên **không** tương đương điều kiện
    hạ cánh.
  - Trích theo câu chữ của v2.
- **Raya & Ambrogioni.**
  - Hỗ trợ nửa "chọn".
  - Các symmetry breaking theo từng datum ở Sec. 4.2 được đo trên score của mạng đã train, và xảy ra
    muộn hơn critical time. Chỉ Li & Chen là phân tích với perfect score.
- **Jain et al.** Chỉ kịch bản 3/4 là ảnh bị nhân bản. Không viết "landing is automatic there".
- **Kaiser & Kollmann (v3).**
  - Denoiser overfit mạnh nhất ở nhiễu trung bình (σ ≈ 1.67 trên ImageNet-64) nhưng họ không đo việc
    sao chép.
  - Không có tiêu chí "error so với mật độ" trong bài.

---

## 4. Thí nghiệm đang chạy và bước tiếp theo

**E1** (`scripts/paperB_window_swap.py`, đã chạy thử trên CPU):
- Đang chạy trên CPU lab09, GPU bị ẩn hoàn toàn. Cấu hình: public model, 50 latents mỗi lớp,
  18 lần chạy cho mỗi mẫu (learned, exact và 16 cửa sổ).
- Log ở `logs_paperB/window_swap_public.log`. Khi xong, chạy
  `python -m scripts.paperB_window_swap --summarize results/paperB_20261121/window_swap_public`.
- Dự đoán đăng ký trước P1.1–P1.2 nằm trong `docs/plan/paperB_gpu_experiments_2026-11-21.md`.
- Lưu ý cho P1.1: dữ liệu swap cũ đã cho k = d1/σ_lo = 21–30 với σ_lo ≤ 0.2, nhưng 13 và 9 tại
  0.5 và 1. Nếu đọc P1.1 trên toàn bộ dải thì nó sẽ không đạt.

**Kết quả E1 (xong, 4490 s CPU, n = 500, cùng latents với swap cũ).** Bảng đầy đủ ở
`results/paperB_20261121/window_swap_public/WINDOW_ANALYSIS.md` (script
`scripts/paperB_window_analysis.py`). E1 dùng đúng latents của swap cũ (seed 0, 50 mỗi lớp), nên
các cửa sổ (lo, ∞) tái lập chính xác số swap cũ (0.606, 1.374, 2.569, 4.219, 6.455, 9.208; off-atom
0.492 và 0.956). Đây là phép kiểm cài đặt, không phải lần lặp độc lập.

- **P1.1:** đạt với σ_lo ≤ 0.2 (k = 30.3, 27.5, 25.7, 21.1), không đạt tại 0.5 và 1 (k = 12.9, 9.2).
  d1 đơn điệu theo σ_lo. Tỉ lệ thuận chỉ đúng ở σ_lo ≤ 0.2.
- **P1.2: bị bác bỏ** với ngưỡng hi = 0.5. Median d1 của (lo, 0.5] lớn hơn rõ rệt so với hi ≥ 2:
  tỉ số 0.69 [0.68, 0.70] tại lo = 0.05 và 0.60 [0.58, 0.61] tại lo = 0.1. Từ hi ≥ 2 trở lên, d1 gần
  như chỉ phụ thuộc lo: 1.33, 1.33, 1.37 cho (0.05, 2], (0.05, 5], (0.05, ∞); 2.48 so với 2.57 cho
  (0.1, 2] và (0.1, ∞).
- **Ảnh nào được chọn do hi quyết định.** "=L" của cửa sổ (lo, hi] bằng đúng "=L" của net→exact tại
  hi (0.956 tại 0.5, 0.896 tại 1, 0.560 tại 2, 0.306 tại 5). Exact field nhận trạng thái ở hi và giữ
  ảnh mà trạng thái đó đã chọn.
- **Hạ cánh do lo quyết định, kèm phần thừa khi hi thấp.** (0.1, 0.5] có 21.4% off-atom
  [18.0, 25.2], so với 0.2% của (0.1, ∞).
- **Cách đọc:** khi được giao trạng thái của network ở σ ≤ 1, exact field co trong cửa sổ, nhưng chưa
  kéo được trạng thái về độ lệch điển hình của chính nó. Phải bắt đầu từ σ ≳ 2 thì độ lệch lúc trả lại
  network mới chỉ còn phụ thuộc lo. Nói cách khác, độ lệch lúc bàn giao không quên quá khứ theo kiểu
  ϱ = 0 trên một cửa sổ ngắn.

**Cần GPU** (chờ GPU 6 rảnh):
- E1 trên sub500 và sub2000. Checkpoint các model subset đang ở server khác, chưa có trên lab09.
- Swap cho model 2000 ảnh (chưa có dữ liệu swap nào).
- Ghi khoảng cách lúc bàn giao để kiểm tra trực tiếp câu "network giữ độ lệch".

---

## 5. Đính chính sau kiểm tra độc lập (thay thế mục 1–3 khi mâu thuẫn)

Nguồn: workflow `verify-paperB-memo` (run wf_c355699a-595). Năm checker kiểm độc lập, sau đó một judge kiểm lại từng báo lỗi. Kết quả: 43 lỗi được xác nhận, 5 báo lỗi bị loại. Các số chép từ sáu phân tích đã verify hầu hết đều đúng. Lỗi tập trung ở phần E7 và cách diễn giải nó.

**Li et al. (kinetic), Table 4, arXiv v2, CelebA, checkpoint 30K bước:**

| điều kiện | FID | copy |
|---|---|---|
| baseline | 16.68 | 37.34% |
| chỉ soft landing, β0 = 0.01 | 35.04 | 30.17% |
| chỉ soft landing, β0 = 0.02 | 86.56 | 19.36% |
| chỉ early boost, α0 = 0.01 / 0.02 | 11.30 / 11.27 | 37.44% / 36.78% |
| cả hai, 0.01 / 0.01 | 14.35 | 31.22% |

### 5.1 [NGHIÊM TRỌNG] mục 1.1 (abstract đề xuất) (cũng có trong tin đã gửi)

Câu gốc: and the network has chosen its image within the band of noise levels where the exact posterior over the training images collapses onto one of them

Vấn đề: States as a general result what E7 supports for the public model only, and only at nominal swap levels. The 1000-image model reaches 90% =L at s=0.82 [0.65,1.02], below the lower edge 1.22 of its band [1.22,6.39]. The 500-image model is censored above s=5. The public 90% point is 0.76 [0.60,0.86] on the effective hand-over level, below the edge 0.78. E7 also measures the posterior at noised test images of one class, not along trajectories, and E7 was not independently verified.

Bằng chứng: swap_clocks.json models.sub1000.clocks.s_sel.nominal 0.8156 (lo 0.653, hi 1.022); models.public.clocks.s_sel.effective 0.764 (0.602, 0.858); models.sub500.clocks.s_sel status reached_at_max_s; collapse_sigma/summary.json sub1000_s0 sigma_c_frac_maxw_ge_0.9_reaches_0.9=1.219, sigma_c_median_maxw_0.5=6.389; full50k 0.784 / 3.821; paperB_collapse_sigma.py docstring: x = t + sigma*eps, t a TEST image.

Sửa: Thay vế đó trong abstract bằng (hoặc bỏ hẳn khỏi abstract):
```latex
..., and on the public model the image is chosen in the range of noise levels where the exact posterior over the training images of a class, evaluated at noised test images, concentrates on one image.
```
Ghi chú: E7 chưa được verifier tính lại. Model 1000 ảnh chọn 90% ở s = 0.82, dưới dải [1.22, 6.39] của nó; mốc 90% của public là 0.76 theo mức hiệu dụng, dưới mép 0.78. Không đưa vào abstract như kết quả chung.

### 5.2 [NGHIÊM TRỌNG] mục 2.2 (đoạn LaTeX và bullet '500 ảnh, đang memorize')

Câu gốc: The memorising $500$-image model chooses earlier still, near the level ($\sigma\approx8.9$) where the posterior at a noised \emph{training} image concentrates on that image

Vấn đề: The 500-image choice level is not measured: =L is already 92.8% at s=5, the largest swap level, so both the 50% and 90% points are only known to be above 5. Nothing places it near 8.9. And 8.9 is where the class-averaged median own weight reaches 1/2, where only 49% of points have own weight at least 1/2, so 'concentrates' overstates the statistic. The data support a same-sigma comparison: at sigma=5, =L 0.928 [0.902,0.948], retrieval share (own weight >= 1/2) 0.936, fresh-point share (max w >= 1/2) 0.789.

Bằng chứng: swap_clocks.json models.sub500.clocks.s_sel and s_sel50 status reached_at_max_s (share_reached_at_max_s 0.9925 and 1.0); summary.json sub500_s0 sigma_retrieval_own_median_0.5=8.894; log-sigma interpolation of subsets.sub500_s0.train: frac_own_ge_0.5 = 0.936 at sigma 5 and 0.49 at 8.9; fresh frac_maxw_ge_0.5 = 0.789 at 5.

Sửa: Bullet: "**500 ảnh, đang memorize:** model đã chọn 92.8% [90.2, 94.8] ảnh ngay tại s = 5, mức swap lớn nhất, nên chỉ biết mốc chọn > 5 (không có swap trên 5). Tại σ = 5, posterior tại một ảnh *train* thêm nhiễu đặt trọng số ≥ 1/2 lên chính ảnh đó cho 93.6% điểm, còn chỉ 78.9% điểm test thêm nhiễu có max w ≥ 0.5. Không thể nói model chọn 'gần σ ≈ 8.9'." LaTeX:
```latex
The memorising $500$-image model has chosen $93\%$ of its images already at $s=5$, the largest swap level we ran; at $\sigma=5$ the posterior at a noised \emph{training} image puts weight at least $1/2$ on that image for $94\%$ of points, against $79\%$ of noised test points with a largest weight of at least $1/2$, as expected of a sampler whose states stay near noised training images.
```

### 5.3 [lớn] mục 2.2 (Cách đọc 'Public' và LaTeX 'falls in this band'); 1.2 LaTeX (cũng có trong tin đã gửi)

Câu gốc: The public network's choice, $50\%$ of samples at $\sigma=2.5$ and $90\%$ at $\sigma=0.95$, falls in this band.

Vấn đề: 2.48 and 0.95 are interpolated nominal swap levels s, written as posterior noise levels sigma. Memo 2.1 itself gives effective levels; there the 90% point is 0.76 [0.60,0.86], just below the band edge 0.78, so 'in the band' depends on the convention. The same nominal-as-sigma wording is in the 1.2 block ('half of its images by $\sigma=2.5$ and $90\%$ by $\sigma\approx0.95$').

Bằng chứng: swap_clocks.json models.public.clocks.s_sel nominal 0.955 [0.741,1.045], effective 0.764 [0.602,0.858]; s_sel50 nominal 2.483, effective 2.822; summary.json full50k sigma_c_frac_maxw_ge_0.9_reaches_0.9=0.784; swap digest: report both conventions.

Sửa: Bullet: "**Public:** network chọn 50% tại s danh nghĩa 2.48 và 90% tại 0.95 (mức hiệu dụng 2.82 và 0.76 [0.60, 0.86]). Mốc 50% nằm trong dải [0.78, 3.82]; mốc 90% nằm sát mép dưới, trong hay ngoài tuỳ quy ước mức bàn giao." LaTeX 2.2:
```latex
The public network's choice, $50\%$ of samples at the swap level $s=2.5$ and $90\%$ at $s=0.95$, falls in or at the lower edge of this band (with each swap level replaced by the geometric mean of its hand-over step, the $90\%$ point is $0.76$).
```
Trong 1.2 thay "by $\sigma=2.5$ and $90\%$ by $\sigma\approx0.95$" bằng "by a swap at $s=2.5$ and $90\%$ by $s\approx0.95$ (nominal swap levels; $2.8$ and $0.76$ at the geometric mean of the hand-over step)".

### 5.4 [lớn] mục 2.2 (kết luận và câu LaTeX cuối) (cũng có trong tin đã gửi)

Câu gốc: The first decision is the collapse of \citet{biroli2024dynamical}, measured on our training sets; the network follows it

Vấn đề: An identity E7 does not establish. Biroli et al. define t_C through the excess entropy (largest time where f_e(t)=0) and estimate it with cloned trajectories; E7 measures posterior max-weight crossings at noised test images, a band spanning a factor of about 5. 'The network follows it' rests on one model inside the band at nominal levels, one whose 90% point lies below its band, and one censored model. The Vietnamese sentence ('quyết định thứ nhất chính là collapse ... network đi theo nó') says the same.

Bằng chứng: pdf_biroli/biroli_text.txt l.18-19 and l.80 (excess entropy, t_C as the largest time with f_e=0), l.141 (Fig. 5 cloning); summary.json full50k 0.784-3.821; swap_clocks.json sub1000 s_sel 0.816 < 1.219.

Sửa: Memo: "Như vậy quyết định thứ nhất xảy ra ở vùng exact posterior tập trung lên một ảnh, một phiên bản đo được của collapse của Biroli et al. (họ định nghĩa t_C qua excess entropy); lựa chọn của network rơi vào hoặc sát vùng đó trên public, muộn hơn vùng đó ở mốc 90% trên model 1000 ảnh." LaTeX:
```latex
This concentration is an operational counterpart of the collapse of \citet{biroli2024dynamical}, measured on our training sets; the network's choice falls at or near it.
```

### 5.5 [lớn] mục 1.2 (đoạn LaTeX 'Two times') (cũng có trong tin đã gửi)

Câu gốc: Our first decision is the collapse, not the speciation: ... a generalising network selects an image on the exact posterior's schedule and then does not reach it.

Vấn đề: Generalises from the public model. The 1000-image model's 90% choice (0.82) lies below its band [1.22,6.39], and the public 90% point is inside only at nominal levels. The two band endpoints are also different statistics (3.8 = class-averaged median max weight 1/2; 0.78 = 90% of points with max weight >= 0.9), measured at noised test images, and 'on our training sets ... with all 5000 images per class' names a single set.

Bằng chứng: swap_clocks.json sub1000 s_sel nominal 0.816; public s_sel effective 0.764; summary.json full50k sigma_c_median_maxw_0.5=3.821, sigma_c_frac_maxw_ge_0.9_reaches_0.9=0.784; sub1000_s0 1.219 / 6.389.

Sửa: ```latex
... Our first decision corresponds to the collapse rather than to the speciation: with all $5000$ training images per class, the exact posterior over the images of the class, evaluated at noised test images, puts weight above $1/2$ on one image for half of the points from $\sigma\approx3.8$ and weight above $0.9$ for $90\%$ of them from $\sigma\approx0.8$, and the public network has chosen half of its images by a swap at $s=2.5$ and $90\%$ by $s\approx0.95$ (Section~\ref{sec:swap}); on the $1000$-image model the last $10\%$ of choices come later than its band. \citet{biroli2024dynamical} also estimate the collapse time on trained networks, on small training sets where these networks memorise. What the exact-score picture folds into the collapse, and what the swaps separate, is the landing: the public network, which generalises, selects an image at about the time the exact posterior concentrates and then does not reach it.
```

### 5.6 [lớn] mục 1.1 (danh sách 'Các chỗ cần sửa') (cũng có trong tin đã gửi)

Câu gốc: - `sec:swap` l.618–621 và l.636–637 ("The exact field lands from whatever state it is handed").

Vấn đề: The list of places repeating the structural fact as a finding is incomplete. The Conclusion (l.820-822) and the Broader impact statement (l.839-841) both present 'the exact field on the last noise levels turns a non-copying model into a copying one' as a result. If only the listed lines are fixed, the false framing stays in the paper.

Bằng chứng: snapshot l.820-822 'and the exact field run on the last $2\%$ of the time turns a model that never copies into one that always does'; l.839-841 'and that an exact field substituted on the last noise levels turns a model that does not copy into one that does'; l.1451-1452 median d1 of net->exact below 1e-5.

Sửa: Thêm vào danh sách:
- Conclusion l.820–822: bỏ vế "and the exact field run on the last $2\%$ of the time turns a model that never copies into one that always does", hoặc thay bằng bằng chứng exact→net ("handed the exact field's state, the public model lands for half of the samples only when the swap comes at $s\approx0.5$").
- Broader impact l.839–841: bỏ vế "and that an exact field substituted on the last noise levels turns a model that does not copy into one that does" (đúng theo cấu trúc sampler, không phải phát hiện).
- Appendix l.1451–1452: ghi rằng median $d_1<10^{-5}$ của net→exact là hệ quả của bước cuối $D(x;0.002)$.

### 5.7 [lớn] mục thiếu (sec:swap 'Reading' l.657–660 và l.636)

Câu gốc: Câu chữ nên là "decided late along the trajectory".

Vấn đề: Memo 2.1 draws the right conclusion from the 1000-image model but gives no line and no replacement. Snapshot l.659-660 says that, handed the same exact state, 'the memorising network lands and the two others do not', and l.636 'Landing is a property of the field that runs last'. The 1000-image model's late field lands exact states for 76.8% at s=1 and 92.6% at s=0.5, so both sentences are false for that model.

Bằng chứng: snapshot l.636, l.659-660; swap_clocks.json sub1000 exact2net off 97.4/88.2/23.2/7.4% at s=5/2/1/0.5; s_land 1.33 [1.29,1.37].

Sửa: Thêm vào 1.8: "- l.636 ('Landing is a property of the field that runs last') và l.659–660 ('the two others do not') sai với model 1000 ảnh: late field của nó đưa trạng thái exact về atom cho 76.8% mẫu tại s = 1. Thay l.657–660 bằng:"
```latex
Whether the endpoint is that image is decided below $\sigma\approx1$, by the late field acting on the trajectory's own state: handed the exact state, the memorising network lands from every swap level, the public network leaves the image unless the swap is late, and the $1000$-image network lands most exact states from $s\le1$ although its own samples never land.
```

### 5.8 [lớn] mục 2.2 (caption hình E7) (cũng có trong tin đã gửi)

Câu gốc: \caption{The network chooses its image where the exact posterior collapses, and lands much later

Vấn đề: The opening sentence covers all three panels but holds only for panel (a). In panel (c), the 500-image model, exact->net ends on a training image for 100% of samples at every s. In panel (b), the 1000-image model's 90% choice (0.82) is outside its band, and its matched 90/90 gap is only 0.82 against 0.56.

Bằng chứng: swap_clocks.json models.sub500.curves.e2n_on all 1.0 (exact->net off 0/500 at every s); sub1000 s_sel 0.816 vs s_land90 0.560; public ratio sel90/land90 4.47 [3.47,4.98].

Sửa: ```latex
\caption{Choice and landing against the concentration of the exact posterior (EDM on CIFAR-10; sampling runs left to right). On the public model the network chooses its image where the exact posterior concentrates and lands much later; the $1000$-image model makes its last choices later than its band, and the memorising $500$-image model lands from every swap level. ...
```
Kèm ghi chú: hình và caption chưa được kiểm độc lập.

### 5.9 [lớn] mục Mở đầu (l.4–5), bảng nguồn (l.18) và 2.2 (cũng có trong tin đã gửi)

Câu gốc: | **E7 mới:** σ collapse của exact posterior | `results/paperB_20261121/collapse_sigma/summary.json` | kiểm khớp subset (sai số ≤ 2.4e-4) |

Vấn đề: The memo says every number was independently recomputed unless stated otherwise, and the Verifier column for E7 reads as verification. E7, its figure and the readings built on it (1.1, 1.2, 2.2) were not independently verified. The subset check covers only 32 nearest-image vectors of sub500 seed 0, plus a trivial check against the full set; sub500 s1, sub1000 and sub2000 were never checked against saved data.

Bằng chứng: paperB_collapse_sigma.py l.124-125: verify_against_strips only for idx500 and arange(50000); summary.json checks {sub500_s0_vs_strips_maxerr n 32, public_vs_strips_maxerr n 32}; results/n3_strips_20261118 holds only public.npz and sub500.npz.

Sửa: Cột Verifier của dòng E7: "chưa verify độc lập; chỉ kiểm 32 vector ảnh của sub500 s0 khớp `n3_strips` (≤ 2.4e-4); sub500 s1, sub1000, sub2000 chưa kiểm". Đầu mục 2.2 thêm: "**Chưa verify.** Số E7, hình và các diễn giải ở 1.1, 1.2, 2.2 do session viết bản ghi nhớ tự tính và tự đọc, không qua verifier riêng." Ở đoạn protocol 2.2 thay "đã kiểm khớp với vector ảnh trong `n3_strips`" bằng "riêng subset 500 ảnh seed 0 đã kiểm với 32 vector ảnh gần nhất lưu trong `n3_strips` (sai số ≤ 2.4e-4)".

### 5.10 [lớn] mục 2.2 (bullet '1000 ảnh' và câu LaTeX 'the band moves up to')

Câu gốc: With $100$ images per class the band moves up to $[1.2,6.4]$, and the $1000$-image network chooses at $4.7$ and $0.82$.

Vấn đề: The juxtaposition reads as both points lying in the band, but 0.82 is below the lower edge 1.22 by a factor 1.49 (0.66 on effective levels). The Vietnamese 'hơi muộn hơn' understates this. The 50% point 4.74 has an open bootstrap interval [3.63, inf), since =L is 0.492 at s=5.

Bằng chứng: summary.json sub1000_s0 sigma_c_frac_maxw_ge_0.9_reaches_0.9=1.219, sigma_c_median_maxw_0.5=6.389; swap_clocks.json sub1000 s_sel nominal 0.816 (effective 0.659), s_sel50 nominal 4.745 lo 3.628 hi inf.

Sửa: Bullet: "**1000 ảnh:** network đạt 50% tại s = 4.74 [3.63, > 5], trong dải [1.22, 6.39]; nhưng 90% chỉ đạt tại 0.82 [0.65, 1.02] (0.66 theo mức hiệu dụng), muộn hơn mép dưới của dải khoảng 1.5 lần. Model này mới train 0.5 Mimg." LaTeX:
```latex
With $100$ images per class the band moves up to $[1.2,6.4]$; the $1000$-image network, trained for $0.5$\,Mimg only, reaches $50\%$ at $s=4.7$, inside it, but $90\%$ only at $s=0.82$, below it.
```

### 5.11 [lớn] mục 1.9

Câu gốc: Điều này xoá phân biệt mà bài A đang nêu ở l.270, l.1560–1584 và dòng "Hypothesis on trajectories" của bảng so sánh.

Vấn đề: Incomplete. Paper A's abstract l.107 claims 'for guidance this removes the limit-set hypothesis of the known convergence result', which v2 Theorem 2.5 already does. The l.270 passage runs to l.273 (Remark 3.19); the table row is l.1589, outside 1560-1584, and the 'Conclusion' row l.1590 cites Rem. 3.19, which v2 no longer has.

Bằng chứng: paper_theory/main.tex l.107; l.270-273 'Theorem~3.18 ... their Remark~3.19'; l.1584 header Thm.~3.18; l.1589 'Hypothesis on trajectories & none & limit set contains no non-minimising critical point & none'; l.1590 '(Rem.~3.19)'.

Sửa: Điều này xoá phân biệt mà bài A đang nêu ở abstract l.107 ("removes the limit-set hypothesis of the known convergence result"), l.270–273 (Theorem 3.18, Remark 3.19), l.1560–1578, và bảng so sánh l.1584–1590 (tiêu đề cột Thm. 3.18 ở l.1584, dòng "Hypothesis on trajectories" ở l.1589, dòng "Conclusion" trích Rem. 3.19 ở l.1590).

### 5.12 [nhỏ] mục 1.3

Câu gốc: Tích phân lịch sử khoảng cách NN trên cùng cửa sổ, không dùng field error, cho tách nhóm ngang hoặc hơn C.

Vấn đề: The verifier rejected 'as much or more'. C's gain exceeds the history's in 8 of 24 window x sigma cells, including the window from 1.92 at sigma 0.14 (0.0043 vs 0.0036); the largest excess is 0.00085 AUC. Only 'comparable' is supported.

Bằng chứng: incremental.json models.sub2000.incremental: C* vs Hist* dauc, 8/24 cells with C > Hist, max excess 0.000846 (recomputed); wf_digest/incremental.md DISAGREE line.

Sửa: Tích phân lịch sử khoảng cách NN trên cùng cửa sổ, không dùng field error, cho tách nhóm cùng cỡ với C: trong 24 ô cửa sổ × σ, C nhỉnh hơn ở 8 ô, chênh nhiều nhất 0.0009 AUC. Khi đã có lịch sử đó, C chỉ thêm tối đa +0.002 AUC.

### 5.13 [nhỏ] mục 1.3 (câu thay thế cho l.741–742)

Câu gốc: Câu thay thế cho l.741–742:

Vấn đề: l.741 starts with the end of the radial-ratio sentence and l.742 ends with 'These', so replacing whole lines deletes text. The kept next sentence ('These conclusions do not change for off-atom thresholds 0.2 and 0.5') would then cover the new dD(0.585) vs C comparison, which was not rerun at those thresholds. The replacement also drops 'on the balanced model' and the level 0.585 that all its numbers refer to.

Bằng chứng: snapshot l.741-743; CERTIFICATE_TABLES.md l.189 'sub2000: AUC dD(0.585) 0.990 [0.986, 0.994], AUC -C 0.983 ...'; incremental caveat: thresholds 0.2/0.5 not rerun.

Sửa: Thay đúng câu "The late contraction ties the baseline on the balanced model ($0.983$ against $0.985$, difference $[-0.004,0.000]$)." (cuối l.741 đến giữa l.742) bằng:
```latex
At the end of sampling that comparison is bookkeeping, since the denoiser output at $\sigma=0.002$ is the sample itself. On the balanced model, at the start of the late window ($\sigma=0.585$), the distance from $D_\theta$ to the nearest training image separates the groups at least as well as the late contraction (AUC $0.990$ against $0.983$, paired difference $[0.004,0.010]$), and it predicts $\log d_1$ better ($R^2$ $0.991$ against $0.976$).
```
Câu tiếp "These conclusions do not change for off-atom thresholds 0.2 and 0.5" chỉ áp dụng cho các so sánh cũ; so sánh dD(0.585) với C chưa chạy lại ở ngưỡng 0.2/0.5.

### 5.14 [nhỏ] mục 1.1 (chỉ dẫn vị trí thay thế)

Câu gốc: Abstract l.75–82, đề xuất:

Vấn đề: l.75 begins with 'the Heun sampler.', the end of the sentence from l.74; replacing l.75-82 with a block starting 'On class-conditional' cuts that sentence. Likewise l.618 holds \paragraph{The image is chosen early.} and l.621 ends with 'The image reached is the one nearest to the', so replacing l.618-621 with the proposed block deletes the heading and breaks the next sentence.

Bằng chứng: snapshot l.74-75 '... with a discrete version for' / 'the Heun sampler. On class-conditional EDM models ...'; l.618 and l.621.

Sửa: "Abstract, từ 'On class-conditional EDM models' (giữa l.75) đến hết l.82, đề xuất:" và "Giữ \paragraph{The image is chosen early.}; thay hai câu 'With the network running down to $s$ ... into complete memorisation.' (l.618–621) bằng đoạn sau." Ở 2.2: "đặt thành đoạn mới ngay sau đoạn 'The image is chosen early', trước \paragraph{Whether it is reached is decided late.}".

### 5.15 [nhỏ] mục 1.4 (slope h = 6) và thiếu l.522, l.1746

Câu gốc: Với h = 6, viết là chưa xác định.

Vấn đề: Only l.507 is named; the same -0.156 is in the fig:kernel-tracking caption (l.522, '-0.16 at h=6') and tab:cifarddpm (l.1746). 'Undetermined' holds for the df=2 t-interval [-0.285,1.013], but tables.tex, which the memo recommends, reports the pooled slope 0.434 [0.062,0.755], which excludes 0 and 1; text and table would disagree unless the interval is named.

Bằng chứng: snapshot l.522, l.1746; uncertainty/tables.tex l.39; wf_digest/uncertainty.md l.157 (minor: name the interval; with 3 clusters only t(df=2) is credible; all re-trained slopes positive).

Sửa: Thêm vào 1.4: "- Sửa cả caption `fig:kernel-tracking` l.522 và dòng h = 6 của `tab:cifarddpm` l.1746. - Với h = 6: ba slope train lại đều dương (0.08, 0.41, 0.60); khoảng t (df = 2) [−0.285, 1.013] chứa cả 0 và 1, nên viết 'chưa xác định, theo khoảng t trên 3 instance'. Cột pooled 0.434 [0.062, 0.755] trong `tables.tex` là bootstrap trên 3 cụm, quá hẹp; nếu dùng bảng đó thì ghi rõ khoảng nào được dùng trong text."

### 5.16 [nhỏ] mục 1.4 (đề xuất)

Câu gốc: "0.36 (three instances, [0.22, 0.51]); 0.48 on the instance analysed below"

Vấn đề: 0.48 is the original single training run in results/exp3/_cifar_ddpm/reeval.json (tab:cifarddpm). The networks analysed later (appendix l.1380ff) are the re-trained _rerun runs, on which the same seed-0 instance gives 0.344. The wording attaches 0.48 to the wrong network.

Bằng chứng: cifar_slopes.json per_h.4.published_single_instance.slope=0.4807; per_h.4.rerun_instances.s0.slope=0.3438 (same_reference_as_published=true); snapshot l.1380-1383.

Sửa: Đề xuất: "0.36 (three trained instances, $95\%$ $t$-interval $[0.22, 0.51]$); an earlier training run of the seed-0 instance gave $0.48$ (Table~\ref{tab:cifarddpm})".

### 5.17 [nhỏ] mục 1.5 và thiếu appendix app:measured-transfer

Câu gốc: Nên viết "separates them barely if at all (AUC at most 0.58)".

Vấn đề: Only l.532-533 is fixed. Appendix l.1406-1408 repeats 'does not separate the groups' with 0.53-0.58 at h=6 (cluster CI excludes 0.5 at all late t). l.1397-1398 claims m* is a posterior mean over many images at t≈0.53, which could not be checked (weights not saved). l.1410-1412 calls the endpoint rule (final scaled error = d1) a 'monitoring rule'. Also the ddof item does not say which value to change: l.1580 declares population SD, so l.1387-1388 breaks the convention.

Bằng chứng: snapshot l.1397-1398, 1406-1412, 1580; transfer_summary.json headline_auc.h6.late_exact_path_ci_excludes_0.5_at_all_late_t=true; transfer digest caveats (posterior weights not saved; e_final is d1); S10 0.1675 sd 0.0100 / 0.2765 sd 0.0061 with ddof=0.

Sửa: Thêm vào 1.5: "- Appendix l.1406: sửa như l.533, 'separates the groups only weakly: from $t\approx0.71$ on, the AUC of that error is $0.49$--$0.52$ at $h=4$ and $0.53$--$0.58$ at $h=6$'. - l.1397–1398: bỏ 'where $m^*$ is a posterior mean over many training images rather than the nearest one' (trọng số posterior không được lưu, chưa kiểm được). - l.1410: thay 'As a monitoring rule' bằng 'As an endpoint rule (the final scaled error is $d_1$)'. - ddof: l.1580 tuyên bố mọi ± là SD tổng thể, nên sửa l.1387–1388 thành $0.168\pm0.010$ và $0.276\pm0.006$."

### 5.18 [nhỏ] mục 1.6

Câu gốc: cosine − constant = −0.276 [−0.393, −0.160].

Vấn đề: The contrast is tr Cov at 1e6 iterations (cosine) minus tr Cov at 2e5 (constant lr), so it changes both schedule and iteration count; the label invites reading it as the schedule effect alone.

Bằng chứng: uncertainty/exp1_uncertainty.csv l.61 'cond tr Cov at 1e6 (cosine) - at 2e5 (constant lr)', -0.276105, t_lo -0.392541, t_hi -0.15967.

Sửa: tr Cov tại 1e6 (cosine) − tr Cov tại 2e5 (constant lr) = −0.276 [−0.393, −0.160] (khác cả lịch learning rate lẫn số vòng lặp).

### 5.19 [nhỏ] mục 1.7

Câu gốc: Trên cửa sổ hữu hạn, 82.9/97.7/99.8% mẫu off-atom vẫn có ϱ < 1 ở mọi mức muộn.

Vấn đề: Models and window are not named (first 500-image, second 500-image, 2000-image; sigma in [0.002,0.585]); the public model (97.5%) is also in the paper sentence. The proposed '$C=0.29$ against $2.55$' uses a symbol defined only in the appendix (l.1543) and is for the first 500-image model, off-atom first.

Bằng chứng: radial_numbers.json b_hypothesis.sigma0.002_rhobar1.0_off: sub500 0.8293, sub500s1 0.9773, sub2000 0.9980, public 0.975; snapshot l.725-728, l.1543.

Sửa: Trên cửa sổ σ ∈ [0.002, 0.585], tỉ lệ mẫu off-atom có ϱ < 1 ở mọi mức là 82.9% (model 500 ảnh thứ nhất), 97.7% (500 ảnh thứ hai), 99.8% (2000 ảnh); model public 97.5%. Đề xuất: "where $\varrho_t$ approaches one, so that (b) certifies little contraction (on the $500$-image model the integral below is $0.29$ for off-atom against $2.55$ for on-atom samples)".

### 5.20 [nhỏ] mục 1.8

Câu gốc: Tỉ lệ thuận chỉ đúng với s ≤ 0.2. Độ dốc log-log là 0.47 (5 → 0.5), 0.84 (0.2 → 0.02) và 0.90 (0.1 → 0.02).

Vấn đề: Slopes are for the public model only; the paper sentence also covers the 1000-image model (0.44/0.76/0.84). The proposed replacement also leaves l.646-647 'a relative error near one that neither contracts nor expands', which the memo's own 1.4-3x partial contraction contradicts.

Bằng chứng: swap_levels.csv / snapshot l.1448-1450: public 18.85, 6.46, 4.22, 2.57, 0.61; sub1000 14.49, 5.25, 3.95, 2.63, 0.68 -> 0.441/0.764/0.840; snapshot l.646-647.

Sửa: Tỉ lệ thuận chỉ gần đúng với s ≤ 0.2. Độ dốc log-log trên model public là 0.47 (5 → 0.5), 0.84 (0.2 → 0.02), 0.90 (0.1 → 0.02); trên model 1000 ảnh là 0.44, 0.76, 0.84. Thêm: "- l.646–647: thay 'a relative error near one that neither contracts nor expands' bằng 'a relative error near one that contracts only weakly (by an estimated factor of about $1.4$--$3$; the hand-over distance was not recorded)'."

### 5.21 [nhỏ] mục 1.8

Câu gốc: Appendix (`app:relerr-exp`) ghi "100 latents per class for the subset models". Các swap run dùng **50 latents mỗi lớp, seed 0, n = 500**. Cần ghi rõ n của swap.

Vấn đề: No line number, and paper B already gives the swap n at l.566 ('500 samples (50 per class)') and l.1439 ('50 latents per class with seed 0'). Only the general sentence at l.1430-1431 needs qualifying.

Bằng chứng: snapshot l.566, l.1430-1431, l.1439; swap_run.json of the three swap runs: n_per_class 50, seed 0.

Sửa: Appendix l.1430–1431 ghi "each run uses 100 latents per class for the subset models"; câu này không đúng cho swap (50 latents mỗi lớp, seed 0, n = 500, đã ghi ở l.566 và l.1439). Sửa thành "... for the subset models outside the swap experiments".

### 5.22 [nhỏ] mục 2.4 (Heun chain)

Câu gốc: Certify hạ cánh (B_K < d2/3) ở 0/499, 0/956 và 2/959 mẫu on-atom ở 18 bước; 946/960 (98.5%) ở 36 bước; 952/961 (99.1%) ở 64 bước; 0 vi phạm.

Vấn đề: Models are not named: at 18 steps 0/499 is the 2000-image model, 0/956 the second and 2/959 the first 500-image model; 36/64-step counts exist only for the first 500-image model. They are also a different quantity from tab:edm-steps' '99.5% certified at every step' (c_k<1), which is correct and must not be 'corrected'.

Bằng chứng: wf_digest/certificate.md l.115-116 (endpoint_certificate.sub500_s{18,36,64}, anchor_certificate.{sub2000,sub500s1}); snapshot l.761, l.1502-1503 (99.5%).

Sửa: Certify hạ cánh (B_K < d2/3), ở 18 bước: 0/499 (model 2000 ảnh), 0/956 (500 ảnh thứ hai), 2/959 (500 ảnh thứ nhất). Chỉ trên model 500 ảnh thứ nhất: 946/960 (98.5%) ở 36 bước và 952/961 (99.1%) ở 64 bước. 0 vi phạm. Đây là đại lượng khác với "99.5% certified at every step" của `tab:edm-steps` (c_k < 1 ở mọi bước); con số đó đúng, giữ nguyên.

### 5.23 [nhỏ] mục 2.4 (Radial)

Câu gốc: Error trỏ dọc x − y với off-atom (median rad/ϱ là 0.62–0.99), và gần như vuông góc với on-atom (0.22–0.60).

Vấn đề: Medians are for the first 500-image model at sigma 0.585 to 0.060, unnamed. A ratio of 0.60 (about 53 degrees) is not 'nearly perpendicular'. The cosine reading assumes omega=0, which fails for some off-atom samples (9 of 41 at 0.585).

Bằng chứng: wf_digest/paperB_radial.md l.86 and l.152.

Sửa: Trên model 500 ảnh thứ nhất, từ σ = 0.585 đến 0.060, median rad/ϱ là 0.62 → 0.99 với off-atom (error gần như dọc x − y) và 0.22 → 0.60 với on-atom (lệch xa hướng đó, gần vuông góc ở đầu cửa sổ). Cách đọc cosin giả định ω = 0, không đúng với một phần mẫu off-atom (9/41 tại σ = 0.585).

### 5.24 [nhỏ] mục 2.4 (Radial)

Câu gốc: Off-atom có rad ≥ 0.95 ở mọi mức từ σ = 0.060 trở xuống: 93% và 89% (hai model 500 ảnh); không mẫu on-atom nào như vậy.

Vấn đề: Omits the 2000-image model, where only 33.7% of off-atom samples stall from 0.060 (88.0% from 0.023); without it the pattern reads as universal.

Bằng chứng: wf_digest/paperB_radial.md l.106 and l.141.

Sửa: Off-atom có rad ≥ 0.95 ở mọi mức từ σ = 0.060 trở xuống: 93% (38/41) và 89% (39/44) trên hai model 500 ảnh, 33.7% trên model 2000 ảnh (88.0% từ σ = 0.023); không mẫu on-atom nào trên cả ba model.

### 5.25 [nhỏ] mục 2.3

Câu gốc: R² của log d1 theo log dD(σ) là 0.671, 0.852, 0.959 và 0.991 tại cùng các mức đó.

Vấn đề: These are pooled in-sample R^2 values, inflated by the on/off split; within on-atom samples they are 0.338, 0.554, 0.851, 0.965.

Bằng chứng: wf_digest/certificate.md H8.

Sửa: R² (gộp on- và off-atom, OLS trong mẫu) của log d1 theo log dD(σ) là 0.671, 0.852, 0.959 và 0.991 tại cùng các mức đó; chỉ trong nhóm on-atom là 0.338, 0.554, 0.851 và 0.965.

### 5.26 [nhỏ] mục 2.5

Câu gốc: Kết quả này tốt ngang luật endpoint "d1 > 4", vốn chỉ là sổ sách.

Vấn đề: Omits the verifier's caveats: e(t) needs the exact posterior mean m*, so it is an audit rule, not an online monitor; it was not compared with the NN baseline; and transferred across bandwidths at t≈0.63 the threshold miscalibrates (h4->h6 FPR 0.145 against 0.083 in sample).

Bằng chứng: transfer/TRANSFER_SUMMARY.md l.158 (in_sample_h6 youden FPR 0.083) and l.163 (h4_to_h6 youden FPR 0.145 [0.099, 0.160]); transfer digest methodology.

Sửa: Thêm: "Lưu ý: luật này cần m* (tổng trên tập train ở mỗi bước), nên là luật kiểm toán, không phải monitor trực tuyến; chưa so với baseline khoảng cách NN; ngưỡng chuyển từ h = 4 sang h = 6 tại t ≈ 0.63 cho FPR 0.145 [0.099, 0.160] so với 0.083 trong mẫu."

### 5.27 [nhỏ] mục thiếu (l.725–726)

Câu gốc: (none)

Vấn đề: Snapshot l.725-726 says 'What Theorem relerr(b) and (c) use is the contraction that the relative error leaves, ∫(1-ϱ_t)'. Hypothesis (c) is on the radial ratio (δ_t), as l.718 and the theorem state; its discrete analogue is ∫(1-rad)^+.

Bằng chứng: snapshot l.395-397 (thm:relerr(c) in terms of the radial term and δ_t), l.718; wf_digest/paperB_radial.md H5.

Sửa: Thêm mục: "- l.725–726: đổi 'What Theorem~\ref{thm:relerr}(b) and (c) use is' thành 'What Theorem~\ref{thm:relerr}(b) uses is' (giả thiết (c) dùng tỉ số radial)."

### 5.28 [nhỏ] mục thiếu (caption fig:edm-clocks l.682–684)

Câu gốc: (none)

Vấn đề: The caption says relative error and radial ratio are 'both anchored without endpoint information'; at sigma=0.002 the predictive anchor equals the endpoint's nearest image for every sample (dD(0.002)=d1), and the late contraction in the same panel uses the endpoint anchor. A reader can take the whole panel as endpoint-free.

Bằng chứng: wf_digest/incremental.md DISAGREE (anc_17 == nn1 for 100%); certificate.md H9 (C computed with err/n1); snapshot l.682-684.

Sửa: Thêm mục: "- Caption `fig:edm-clocks` l.682–684: thay 'both anchored without endpoint information' bằng 'anchored at the nearest training image of $D_\theta$ at the same level (at $\sigma=0.002$ this is the endpoint's)', và thêm sau late contraction 'anchored at the endpoint's nearest image'."

### 5.29 [nhỏ] mục 3 (Li et al. 2026 kinetic)

Câu gốc: giảm tỉ lệ copy từ 37.3% xuống 30.2% (19.4% với β0 = 0.02,
    nhưng FID tệ đi). Riêng early boost thì không đổi tỉ lệ copy.

Vấn đề: Numbers are right, but the parenthesis attaches the FID cost only to β0=0.02; FID roughly doubles already at β0=0.01 (16.68 to 35.04). The bullet also omits the combined KTS row (31.2%, FID 14.35), which is the '37.3% to 31.2%' of the paper's Introduction, and the scope (CelebA, 30K-step checkpoint).

Bằng chứng: arXiv 2602.07928v2 (29 May 2026) HTML, Table 4 (CelebA, 30K-step checkpoint): baseline 16.68/37.34; β0=0.01 35.04/30.17; β0=0.02 86.56/19.36; α0=0.01 11.30/37.44; α0=0.02 11.27/36.78; α0=β0=0.01 14.35/31.22; Introduction: 'from 37.3% to 31.2%'.

Sửa:   - Soft landing chỉ ở t ≥ 0.6 (σ ≲ 0.67) giảm tỉ lệ copy từ 37.3% (FID 16.7) xuống 30.2% với β0 = 0.01 (FID 35.0) và 19.4% với β0 = 0.02 (FID 86.6): FID tệ đi ở cả hai mức. Riêng early boost thì tỉ lệ copy không đổi (37.4% và 36.8%, FID 11.3). Cả hai cùng lúc (α0 = β0 = 0.01) cho 31.2% (FID 14.4); đó là con số "37.3% → 31.2%" trong phần Introduction của họ (Table 4, arXiv v2, CelebA, checkpoint 30K bước).

### 5.30 [nhỏ] mục 3 (Sửa metadata, physicscfm2026)

Câu gốc: Câu ở intro "return training examples" nên viết mềm đi

Vấn đề: No such sentence exists in paper B (which never cites physicscfm2026) or paper A (cites it only at l.252 for Section 3.3). The sentence is paper/main.tex l.143, the old combined paper. Paper B's l.838 'return training examples' is about paper B itself and must not be softened.

Bằng chứng: grep: physicscfm absent from snapshot main.tex; paper_theory/main.tex:252; paper/main.tex:143.

Sửa: - `physicscfm2026`: ghim v3, vì v1 có tiêu đề và danh sách tác giả khác. Bài B hiện không trích key này; bài A trích ở paper_theory/main.tex l.252. Câu "return training examples \citep{physicscfm2026}" chỉ có ở `paper/main.tex` l.143 (bản gộp cũ); nếu đưa lại vào bài nào thì viết mềm: bài đó chỉ cho thấy phương sai co lại. Không sửa câu Broader impact l.838 của bài B.

### 5.31 [nhỏ] mục 3 (Shah et al. 2025)

Câu gốc: σ chuyển tối ưu nằm trong [0.4, 4], trùng dải
    chọn ảnh của bài B.

Vấn đề: [0.4,4] is the range of Pareto-optimal switch levels on FFHQ-300, not one optimum, and it brackets rather than coincides with paper B's selection band; it also reaches into the landing range (σ ≲ 0.6).

Bằng chứng: wf_digest/lit0.md l.58 ('brackets sigma~1-2') and l.61.

Sửa:   - Họ chỉ train phần nhiễu cao trên dữ liệu nhiễu; trên FFHQ-300 các σ chuyển cho trade-off Pareto-tối ưu nằm trong [0.4, 4]. Dải này chứa dải chọn ảnh σ ≈ 1–2 của bài B (và chạm đầu trên của dải hạ cánh σ ≲ 0.6).

### 5.32 [nhỏ] mục 1.3 (contribution đề xuất)

Câu gốc: the contraction that the relative error leaves over $\sigma\in[0.002,0.585]$ is $1.75$ against $0.68$

Vấn đề: 1.75 and 0.68 are group medians, not the contraction of the groups.

Bằng chứng: snapshot l.727-728 '(medians, ...)'; incremental.json models.sub2000.reference.

Sửa: ```latex
the contraction that the relative error leaves over $\sigma\in[0.002,0.585]$ has median $1.75$ against $0.68$ for on- and off-atom samples of a balanced model
```

### 5.33 [nhỏ] mục 2.2 (LaTeX, ký hiệu)

Câu gốc: For a point $x=y+\sigma\varepsilon$ with $y$ a CIFAR-10 test image of class $c$, the exact posterior over the training images of the class, $w_j\propto\exp(-|x-y_j|^2/2\sigma^2)$

Vấn đề: Paper B writes training atoms as x^j (m^\star=\sum_j w_j x^j) and uses y^i for labels; here y is a test image and y_j training images.

Bằng chứng: snapshot l.255, l.315, l.380.

Sửa: ```latex
For a point $x=x_{\rm test}+\sigma\varepsilon$ with $x_{\rm test}$ a CIFAR-10 test image of class $c$, the exact posterior over the training images $x^j$ of the class, $w_j\propto\exp(-|x-x^j|^2/2\sigma^2)$, ...
```

### 5.34 [vặt] mục 2.2 (LaTeX, mệnh đề cuối)

Câu gốc: and Section~\ref{sec:contraction} turns to the second.

Vấn đề: The paragraph is placed inside sec:swap directly before \paragraph{Whether it is reached is decided late.}, which treats landing; pointing to sec:contraction skips it.

Bằng chứng: snapshot l.618, l.636, l.671.

Sửa: "...; the next paragraph turns to the second."

### 5.35 [vặt] mục 2.2 (caption)

Câu gốc: Swap values at the eight hand-over levels

Vấn đề: The figure plots swap shares at the nominal swap levels s, not at hand-over brackets or effective levels.

Bằng chứng: scripts/make_collapse_choice_figure.py: s = [L['s'] for L in lv]; ax.errorbar(s, eqL, ...).

Sửa: "Swap values at the eight swap levels $s$, $500$ latents per model, Wilson $95\%$ intervals."

### 5.36 [vặt] mục 2.2 (LaTeX)

Câu gốc: the median largest weight passes $1/2$ at $\sigma=3.8$

Vấn đề: The value is the class average of per-class medians (pool() averages over classes before the crossing), not the median over all points.

Bằng chứng: scripts/paperB_collapse_sigma.py l.148-158 (pool, crossing on maxw_median).

Sửa: "the largest weight, median over the points of a class and averaged over classes, passes $1/2$ at $\sigma=3.8$"

### 5.37 [vặt] mục 2.1 (so ở cùng ngưỡng)

Câu gốc: Thứ tự chỉ "đảo" khi so ngưỡng 90% của chọn với ngưỡng 50% của hạ cánh.

Vấn đề: The inversion happens only on the 1000-image model (0.82 < 1.33); on the public model 0.95 > 0.51.

Bằng chứng: verify_swap_report.txt l.30 (public P(s_sel90 > s_land50) 1.000), l.52 (sub1000 0.000).

Sửa: Thứ tự chỉ "đảo" trên model 1000 ảnh, khi so ngưỡng 90% của chọn (0.82) với ngưỡng 50% của hạ cánh (1.33). Đừng báo cáo như vậy.

### 5.38 [vặt] mục 2.4 (Certificate)

Câu gốc: Slack trung vị 0.32–0.37 nats

Vấn đề: These are on-atom medians (0.320 / 0.368 / 0.346), not stated.

Bằng chứng: wf_digest/certificate.md l.103.

Sửa: Slack trung vị (on-atom) 0.32–0.37 nats

### 5.39 [vặt] mục 1.8

Câu gốc: Câu hỏi TODO ở README ("whether the 1000-image subset is class-balanced") đã có trả lời: có.

Vấn đề: The same TODO is a comment in paper B (l.1436-1437), which is where it must be resolved; and the indices file is not in the local repo, so 'có' is inferred from the generator script and file name.

Bằng chứng: snapshot l.1436-1437; paper_mechanism/README.md l.101-102; data/edm_subsets absent locally; make_edm_cifar_subset.py takes n // 10 per class.

Sửa: Câu hỏi TODO ở README (l.101–102) và comment trong main.tex (l.1436–1437) đã có trả lời: có, suy từ `scripts/make_edm_cifar_subset.py` (lấy `n // 10` ảnh mỗi lớp) và đường dẫn `data/edm_subsets/cifar10_sub1000_s0_indices.npy` trong swap_run.json; file indices không có trong repo local nên chưa kiểm trực tiếp.

### 5.40 [vặt] mục 1.1 (câu thay thế l.618–621)

Câu gốc: so an exact field used for the last of the $35$ denoiser evaluations alone already lands

Vấn đề: Paper B never states that the 18-step Heun sampler makes 35 denoiser evaluations, and the statement is shown only in the verifier's synthetic control, not on the EDM models.

Bằng chứng: heun() in n3_edm_memorization.py; verify_swap_report.txt l.125-126; snapshot l.1440 mentions only the 18-step sampler.

Sửa: ```latex
so an exact field used only for the last of the $35$ denoiser evaluations of the $18$-step sampler would already land every sample.
```

### 5.41 [vặt] mục 3 (Raya & Ambrogioni)

Câu gốc: Chỉ Li & Chen là phân tích với perfect score.

Vấn đề: Read literally it says Raya and Ambrogioni do no exact-score analysis; their Sec. 3 (two-point model) does. The lit1 check meant only that Sec. 4.2 is not exact-score.

Bằng chứng: wf_digest/lit1.md l.157.

Sửa: Phần lý thuyết Sec. 3 của họ (mô hình hai điểm) dùng score chính xác; Li & Chen thì toàn bộ là phân tích với perfect score.

### 5.42 [vặt] mục 3 (Jain et al.)

Câu gốc: Chỉ kịch bản 3/4 là ảnh bị nhân bản.

Vấn đề: '3/4' can be read as 'three of four', the opposite of the intended meaning.

Bằng chứng: wf_digest/lit1.md l.158.

Sửa: - **Jain et al.** Trong 4 kịch bản, chỉ kịch bản thứ 3 là ảnh bị nhân bản. Không viết "landing is automatic there".

### 5.43 [vặt] mục 3 (favero2025bigger)

Câu gốc: Có thể đổi key thành `favero2026bigger`.

Vấn đề: The key is cited at snapshot l.229; renaming only in refs.bib breaks the citation.

Bằng chứng: snapshot l.229 '\citet{favero2025bigger}'.

Sửa: Có thể đổi key thành `favero2026bigger`, nhưng khi đó phải đổi cả \citet ở main.tex l.229.
