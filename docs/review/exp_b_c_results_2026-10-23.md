# Kết quả EXP-B và EXP-C — 23/10/2026

Cả hai chạy trên checkpoint có sẵn trên server, không huấn luyện lại. Code:
`scripts/exp_b_transfer_exp1.py`, `scripts/exp_c_cifar_transfer.py`. Kết quả thô:
`results/exp_b_transfer_20261022/`, `results/exp_c_cifar_transfer_20261022/`.

## EXP-B — sai số dọc quỹ đạo học được so với sai số trên luật teacher (EXP-1)

**Thiết lập.**
- **Mạng:** các run `linear-gaussian-mlp-{h0,h0p1}-seed1001…1005-200k`, mỗi run 5 checkpoint (1k, 10k, 30k, 100k, 200k).
- **Điều kiện và nguồn:** 20 điều kiện train như `src/train.py`; 1000 nguồn Gaussian dùng chung cho mọi điều kiện.
- **Hai quỹ đạo từ cùng X₀:** Y_t là luồng exact (h = 0: t a + (1−t) X₀; h = 0,1: luồng kernel exact); Z_t là luồng của mạng.
- **Đại lượng đo:** r(t) = E|Δ(Y_t)|², m(t) = E|Δ(Z_t)|², K = m/r, với Δ = v_θ − v*.
- **Bộ giải:** ROS2 thích nghi riêng cho từng nguồn, float64.

**Kết quả** (median theo 20 điều kiện, rồi trung bình ± sd theo 5 seed; bảng đầy đủ trong `SUMMARY.md`,
hình `fig_exp_b.pdf`):

| | 1−t = 0,5 | 0,1 | 10⁻² | 10⁻³ | 10⁻⁴ |
|---|---|---|---|---|---|
| K(t), h = 0, 200k bước | 1,5 | 127 | 3,1·10³ | 2,1·10⁵ | 2,0·10⁷ |
| K(t), h = 0,1, 200k bước | 1,0 | 1,3 | 25 | 2,1·10³ | 2,0·10⁵ |

1. **K(t) ≈ 1 lúc đầu, rồi tăng như (1−t)⁻².** Đúng như dự đoán từ trường hợp dấu bằng của
   Theorem 5.1: (1−t)Δ(Z_t) → Z_1 − a ≠ 0, nên m(t) ≈ ‖Z_1 − a‖²/(1−t)². Huấn luyện thêm chỉ giảm
   K theo một hằng số (h = 0: từ 8·10⁵ ở 1k bước xuống 2·10⁵ ở 200k bước, tại 1−t = 10⁻³). Ở h = 0,1,
   K nhỏ hơn khoảng 100 lần nhưng có cùng bậc tăng.
2. **Cận chỉ dựa trên loss sai khoảng 100 lần** (h = 0, T = 1 − 10⁻³). ‖Z_T − Y_T‖ đo được là
   1,37 → 0,64 (từ 1k đến 200k bước). B_T với K ≡ 1 chỉ là 0,010 → 0,0065. Đây là thước đo trực tiếp
   cho hiện tượng mà Proposition `prop:loss-no-certificate` nêu dưới dạng tồn tại: loss nhỏ không
   chứng nhận được endpoint. B_T tính bằng m(t) đo được thì khớp ‖Z_T − Y_T‖ tới ba chữ số. Điều này
   là tự động (Minkowski), chỉ là kiểm tra nhất quán.
3. **Ở h = 0,1, B_T không chặn được gì** (0,066 so với ‖Z_T − Y_T‖ = 0,18). Lý do: trường teacher
   không tuyến tính nên đẳng thức của Theorem C.1 không còn. Theorem C.1 chỉ áp dụng cho nhãn cứng,
   đúng như phát biểu của nó.
4. **Proposition 5.2 (h = 0,1):**
   - Tiền đề trên quỹ đạo (|Z_{t₀} − a| < ρ/4 và (1−t)|Δ(Z_t)| ≤ ρ/4 với t ≥ t₀, ρ = 0,4·D) đúng cho
     1–11% số quỹ đạo, tăng theo số bước huấn luyện. Với các quỹ đạo đó, kết luận |Z_t − a| < ρ
     đúng 100%.
   - Tiền đề trên cả quả cầu, tức tiền đề thật của mệnh đề, **không bao giờ** thỏa. Đã tách hai
     điều kiện trên 60 cặp (điều kiện, atom) của seed 1001 ở 200k bước, t₀ ∈ {0,999; 0,9999}. Trường
     exact luôn đã tập trung (điều kiện t* đúng). Nhưng sai số của mạng vượt ρ/4 ở đâu đó trên mọi
     quả cầu. Vậy mệnh đề không chứng nhận được mạng huấn luyện thật. Thứ thiếu là kiểm soát sai số
     ngoài quỹ đạo, đúng chỗ mà phần Limitations nói là "conditional".

**Gợi ý cho paper.** Có thể thay câu "… which we do not infer from the loss and have not measured"
trong Limitations bằng kết quả đo được. Tỉ số K(t) = m/r giữa sai số dọc quỹ đạo học được và sai số
trên luật teacher tăng như (1−t)⁻² trên mọi checkpoint. Tại T = 1 − 10⁻³, cận dựa trên loss nhỏ hơn
khoảng cách endpoint thật khoảng 100 lần. Tiền đề quả cầu của Proposition 5.2 không thỏa ở mạng nào,
vì sai số ngoài quỹ đạo.

## EXP-C — nguồn gốc mẫu off-atom ở CIFAR-10

**Thiết lập.**
- **Mạng:** U-Net 35,75M tham số của EXP-3 (`exp3_cifar_heff_h{0,4,5,6}_s{0,1,2}`), checkpoint 60000.
- **Mẫu:** 48 điều kiện, mỗi điều kiện 16 nguồn chung.
- **Ba luồng từ cùng nguồn:**
  - (A) Euler 50 bước tới T = 1 − 10⁻³, bộ lấy mẫu của paper.
  - (B) Mạng học được, RK4 trong τ = −log(1−t), kiểm tra lại ở bước 2Δτ.
  - (C) Trường kernel exact, float64, RK4 với Δτ = 0,005. Hệ số ổn định lớn nhất β·tr Cov·Δτ = 0,455 < 2,8.
- **Tiêu chí on-atom:** d₁/d₂ < 1/3, tính trên 2000 ảnh train của run và trên toàn bộ 50k ảnh CIFAR-10.

**Kết quả** (tỉ lệ off-atom trên 2000 ảnh train | trên 50k ảnh, mean ± sd theo 3 seed; bảng đầy đủ trong
`results/exp_c_cifar_transfer_20261022/SUMMARY.md`):

| h | Euler 50, 10⁻³ | học RK4, 10⁻³ | học RK4, 10⁻⁴ | exact, 10⁻³ và 10⁻⁴ | cùng atom với exact |
|---|---|---|---|---|---|
| 0 | 0,000 \| 0,000 | 0,000 \| 0,000 | 0,000 \| 0,000 | 0 \| 0 | 1,000 |
| 4 | 0,173 \| 0,207 | 0,158 \| 0,189 | 0,158 \| 0,187 | 0 \| 0 | 0,516 ± 0,076 |
| 5 | 0,246 \| 0,289 | 0,211 \| 0,264 | 0,212 \| 0,265 | 0 \| 0 | 0,325 ± 0,055 |
| 6 | 0,298 \| 0,349 | 0,254 \| 0,307 | 0,254 \| 0,305 | 0 \| 0 | 0,191 ± 0,047 |

1. **Không phải do cắt cụt (truncation).** Trường exact đặt mọi mẫu lên atom ngay tại T = 1 − 10⁻³.
   Mạng học được cho cùng một tỉ lệ off-atom ở 10⁻³ và 10⁻⁴.
2. **Rời rạc hóa chỉ đóng góp một phần nhỏ.** Euler 50 bước so với RK4 hội tụ chênh khoảng 0,02–0,04
   (h = 6: 0,298 so với 0,254). RK4 ở Δτ và 2Δτ cho cùng atom gần nhất với ít nhất 96,5% mẫu.
3. **Phần còn lại là sai số của trường học được.** Ở h = 6, khoảng 25% mẫu là off-atom, trong khi trường
   exact cho 0%. Chỉ 19% mẫu kết thúc ở cùng atom mà trường exact chọn; con số này giảm khi h tăng
   (h = 4: 52%). K(t) = m/r tại 1−t ≈ 10⁻³ là 724 ở h = 0 và 5·10³–7,5·10³ ở h > 0, tức là sai số dọc
   quỹ đạo học được lớn hơn nhiều so với trên quỹ đạo teacher, như EXP-B.
4. **Đối chiếu với paper** (sửa ngày 26/10; bản trước ghi nhầm rằng paper dùng tiêu chí 50k).
   - Paper tính on-atom trên 2000 ảnh train của run (`scripts/reeval_exp3_cifar_ddpm.py`, `problem.X`),
     với M = 256 nguồn cho mỗi điều kiện.
   - Vậy đại lượng so sánh đúng là cột Euler 50 theo 2000 ảnh:

     | h | paper | EXP-C (Euler 50, 2000 ảnh) |
     |---|---|---|
     | 4 | 0,171 | 0,173 ± 0,029 |
     | 5 | 0,283 | 0,246 ± 0,040 |
     | 6 | 0,380 | 0,298 ± 0,058 |

   - Ở h = 6, con số của paper cao hơn khoảng 1,4 sd. Có hai khác biệt có thể giải thích: paper đo trên
     run `exp3_cifar_ddpm_h6`, run này không còn giữ trọng số; EXP-C dùng 3 run `heff` khác và chỉ 16 nguồn
     cho mỗi điều kiện.
   - Phép tách ở trên (exact cho 0%, phần lớn do sai số của mạng) áp dụng cho các run `heff`. Con số 38%
     của paper chưa được đo lại trực tiếp.

**Gợi ý cho paper.** Câu ở `sec:p7` "this combines learned-field, truncation and discretisation effects and
does not identify a limiting support" có thể thay bằng phép tách vừa đo. Trường exact không có mẫu off-atom
nào ở cả hai mốc cắt. Thay Euler bằng RK4 hội tụ chỉ giảm tỉ lệ off-atom khoảng 4 điểm phần trăm. Vậy phần
lớn mẫu off-atom ở h = 6 đến từ sai số của mạng. Khi viết vào paper, cần nói rõ phép tách này đo trên ba
run `heff`, còn con số 38% đến từ một run khác (xem mục 4). Đây là đúng tình huống mà Theorem `thm:transfer` mô tả:
sai số tỉ lệ (1−t)|Δ| không triệt tiêu.
