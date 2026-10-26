# Đánh giá tính đúng đắn và đóng góp của `paper/main.tex` (bản cập nhật) — 25/10/2026

**Phạm vi.**
- **Toán:** mọi kết quả có chứng minh trong Sections 3–5 và các Appendix chứng minh.
- **Thí nghiệm:** các thí nghiệm có trong paper, cùng bốn thí nghiệm bổ sung chạy trên server: EXP-A 1D, EXP-A 2D, EXP-B, EXP-C.

Các chứng minh là của tác giả. Các lượt verifier dưới đây chỉ là kiểm tra thêm, không thay thế việc tác giả
đã tự kiểm chứng.

## Kết luận ngắn

1. **Đúng đắn: không tìm thấy lỗi toán học nào.**
   - 24 lượt verifier độc lập (8 unit × 3 lượt) và 5 lượt tấn công có mục tiêu đều trả về CORRECT.
   - Có 8 lỗi trình bày, mỗi lỗi sửa trong một dòng. Không lỗi nào làm đổi một kết luận (mục 3).
2. **Đóng góp:**
   - Hai kết quả mạnh nhất: Theorem `thm:composition`, với ngưỡng dạng đóng w_c = 1/sinh²B, và
     Theorem `thm:spectral`, với ngưỡng ma trận λ_max(D^{-1/2} C_av D^{-1/2}).
   - Các kết quả "can thiệp dương không rời tập train" vững, nhưng dùng kỹ thuật chuẩn.
   - Phần transfer là sơ cấp, và paper tự nói vậy.
   - Mắt xích yếu nhất là liên hệ với mạng huấn luyện thật: trong paper hiện tại, phần này chỉ ở dạng có
     điều kiện.
3. **Thí nghiệm:** ba thí nghiệm bổ sung lấp đúng ba khoảng trống mà mục Limitations tự nêu:
   - EXP-A: có mạng học được tái hiện ngưỡng composition, nhưng chỉ khi tham số hóa đúng lớp biên.
   - EXP-B: đã đo sai số dọc quỹ đạo học được.
   - EXP-C: mẫu off-atom ở CIFAR-10 đến từ sai số của mạng, không đến từ cắt cụt hay rời rạc hóa.

## 1. Cách kiểm tra

- **Chia unit:** paper được cắt thành 8 unit, mỗi unit gồm định nghĩa, phát biểu và chứng minh đầy đủ.
  Danh sách unit:
  - U1: nền tảng, Section 3.
  - U2: các bước chung, Lemma basic/conv/volume.
  - U3: positive mixtures.
  - U4: guidance.
  - U5: composition.
  - U6: spectral.
  - U7: transfer.
  - U8: risk transfer.
- **Verifier:** mỗi verifier chỉ đọc một file unit, không có công cụ nào khác, và không thấy kết quả của
  verifier khác. Nó phải chọn bước khó nhất và tự dựng lại bước đó.
- **Tấn công có mục tiêu**, theo các pattern của skill math-olympiad:
  - #40: tổng quát hóa mỗi bước ngắn thành một bổ đề rồi thử phá bằng trường hợp 2×2. Chạy trên U4, U5, U6.
  - #5: liệt kê từng giả thiết của mọi kết quả được gọi và kiểm tra lại từ đầu. Chạy trên U3, U6.
- **Giới hạn của cách kiểm tra:**
  - Verifier là các instance LLM cùng họ mô hình, nên có thể có điểm mù chung. Đây không phải chứng minh
    hình thức.
  - Giao thức của skill gợi ý 5 lượt cho mỗi unit; ở đây chạy 3 lượt cộng các lượt tấn công.
  - Các kết quả chuẩn được trích dẫn (Hale Ch. I, AGS Ch. 8) chỉ được kiểm ở mức "áp dụng đúng giả thiết",
    không chứng minh lại.

## 2. Kết quả kiểm tra toán

| Unit | Kết quả | 3 lượt | Tấn công | Tin cậy |
|---|---|---|---|---|
| U1 | Lemma change of variables, well-posedness, mixture coupling; Prop L² projection, collapse, unconditional, kernel field, atomicity; Thm endpoint; Cor bandwidth | 3/3 CORRECT | — | cao |
| U2 | Lemma basic (a)–(d), conv, volume; đoạn "Solutions" | 3/3 CORRECT | — | cao; "Solutions": trung bình (dẫn Hale cho luồng C¹ với trường Carathéodory) |
| U3 | Thm posmix; Prop filtered, hyperplane | 3/3 CORRECT | #5: CORRECT | cao |
| U4 | Lemma signedconv; Thm schedule; Prop cfgatom | 3/3 CORRECT | #40: CORRECT | cao |
| U5 | Thm composition; Prop composition-open | 3/3 CORRECT | #40: CORRECT | cao |
| U6 | Lemma offtie, LP; Thm spectral; Cor spectral | 3/3 CORRECT | #40: CORRECT; #5: CORRECT | cao, riêng Lemma LP trung bình–cao (xem lỗi 2) |
| U7 | Thm transfer; Prop localtransfer | 3/3 CORRECT | — | cao |
| U8 | Thm risktransfer; Prop loss-no-certificate | 3/3 CORRECT | — | cao |

**Các bước khó nhất được dựng lại độc lập:**
- Bất đẳng thức F_w(s) ≥ κ min{s³, 1} tại đúng ngưỡng w sinh²B = 1, cùng barrier dưới θ = (κβ³)^{-1/2}.
- Barrier di động b = c ± ε²/t khi c± có dấu bất kỳ (Prop composition-open).
- Đẳng thức (1+w)|u|² − w|v|² = |(1+w)u − wv|² − w(1+w)|u−v|², dùng để chặn divergence dưới guidance.
- Tích phân từng phần với hệ số BV dạng right-continuous (Lemma signedconv).
- Lập luận "no escape" bằng thế Ψ cùng bổ đề Barbalat (Thm spectral (c)).
- Phép tính C_av của regular simplex, kiểm chéo: ở N = 2 công thức trùng với 1/sinh²(B/2).
- Phép tính loss 1/2 + 3A/2 + 7A²/6 trong Prop loss-no-certificate. B_T đạt đẳng thức trên chính phản ví dụ
  đó.

**Đối chiếu số với kết quả exact độc lập** (các script của tôi, chọn nguồn khác với paper):
- Table `tab:composition` cho B = 1, w/w_c = 2 ghi 0,406. Tôi được 0,40590, có unit test.
- Table `tab:spectral` cho tam giác ở 1,1 / 2 / 5 w_c ghi 0,0010 / 0,1396 / 0,6865. Tôi được
  0,002 / 0,138 / 0,681 trên 2048 nguồn của tôi. Chênh lệch nằm trong sai số lấy mẫu (sd ≈ 0,008–0,010).

## 3. Lỗi trình bày cần sửa

Không lỗi nào làm đổi kết luận. Số dòng dưới đây là của `paper/main.tex` trước khi sửa.

**Đã sửa ngày 25/10.**
- Cả 8 mục đã được sửa trong `paper/main.tex` của worktree. Patch chỉ chứa các sửa này, so với bản của
  tác giả: `docs/review/main_tex_fixes_2026-10-25.patch`.
- Nhiễu nhãn được đổi tên thành ω. ξ đã dùng cho nhiễu endpoint trong Prop `prop:tgtnoise`; ω chỉ còn
  xuất hiện trong cụm "ω-limit" và trọng số cục bộ ω_k của Lemma `lem:offtie`.
- Bản sau khi sửa biên dịch ra 46 trang, giống bản gốc: không lỗi, không overfull box.
- Cảnh báo `\eqref{eq:pf:transfer-t0}` undefined mà tôi ghi trước đây hóa ra không phải lỗi của paper
  (đính chính ngày 27/10).
  - Nguyên nhân: tôi biên dịch với `-output-directory`, và pdflatex đọc một file `paper/main.aux` cũ (ngày
    20/10, không nằm trong git) không có label mới này.
  - Bản build sạch của thư mục `paper/` cho "(13) with Δ̃ in place of Δ", không còn "??" nào, 46 trang.

1. **Dòng 2040, phát biểu Lemma `lem:offtie`.** Câu "the logit difference is ⟨ξ, a_i − a_{i'}⟩" thiếu
   số hạng log(p_i/p_{i'}). Chứng minh ở dòng 2064 có số hạng này, và kết luận "posterior trên S là π(ξ)"
   vẫn đúng. Cả 3 lượt U6 đều bắt được.
2. **Dòng 2122–2125, phát biểu Lemma `lem:lp`.**
   - Phát biểu nói "ε-ball", nhưng chiều ngược lại của chứng minh chỉ đúng cho ε/2-ball (dòng 2162). Lỗi này
     đã có trong audit 21/10 và vẫn chưa sửa.
   - "form a C¹ graph" nói hơi quá. Chứng minh cho thấy tập hội tụ *nằm trong* đồ thị, và dữ liệu nhỏ *trên*
     đồ thị thì hội tụ.
   - Part (a) của Theorem dùng ý "khi n₊ = 0 mọi dữ liệu nhỏ đều hội tụ". Ý này có trong chứng minh nhưng
     không có trong phát biểu, nên nên đưa vào phát biểu.
3. **Dòng 2220.** "being isolated (each is hyperbolic) they are finitely many": một tập bị chặn gồm các điểm
   cô lập chưa chắc hữu hạn, ví dụ {1/n}. Cần thêm rằng tập profile là tập đóng, vì nó là tập không điểm của
   G liên tục.
4. **Dòng 2412, Theorem `thm:risktransfer`.** Cần ghi K ≥ 0. Nếu không, tại nơi r = 0 hàm K có thể âm, và
   cận có trọng số ∫K/(ε²w) có thể sai. Thay K bằng max(K, 0) không đổi giả thiết lẫn B_T.
5. **Dòng 1198.** `\eps` được định nghĩa là `\varepsilon` (`math_commands.tex:17`) và dùng cho 1−t. Nhưng
   ở dòng này Ỹ = y^i + h`\eps` lại là nhiễu nhãn ε ~ N(0, I_k). Nên đổi ký hiệu của nhiễu nhãn.
6. **Dòng 262–263.** "since (X_t, t, Ỹ) has a positive density" sai khi h = 0, vì lúc đó Ỹ = Y rời rạc.
   Nên viết "for h > 0", vì tại h = 0 paper dùng trường collapse tường minh.
7. **Dòng 1079, Lemma `lem:wellposed` (c).** "The backward flow exists … by the growth bound of (b)", nhưng
   (b) chỉ phát biểu chiều xuôi. Chỉ cần thêm một mệnh đề: cùng lập luận Grönwall chạy ngược cho
   g(s) ≤ g(T)(1−s)/(1−T).
8. **Ký hiệu nhỏ.**
   - β(T) trong cận Lipschitz nhận đối số là t, trong khi ở nơi khác β là hàm của τ.
   - Trong Thm schedule, lý do đặt η_n ≤ r²/4 (để r² − η_n ≥ 0 trước khi chặn ∫β bằng β(n)) không được
     nói ra.
   - Cor `cor:spectral-threshold` ngầm cần các prior có điều kiện thuộc P_pos.

## 4. Đóng góp

| Nhóm kết quả | Mới | Độ sâu kỹ thuật | Nhận xét |
|---|---|---|---|
| Section 3: collapse, endpoint law dưới label smoothing, atomicity | thấp | thấp | Paper tự nói đây là reference, không phải đồng nhất thức mới (Baptista 2025; physicscfm2026). Sàn W₂ trong Prop atomicity là một nhận xét định lượng nhỏ nhưng có ích. |
| Positive mixtures (Thm posmix, Prop filtered, Prop hyperplane) | trung bình | trung bình | Mọi quỹ đạo hội tụ và gần như chắc chắn rơi vào atom, với Π Borel bất kỳ trên P_pos, không cần giả thiết "không có điểm tới hạn không cực tiểu" như Liu 2026. Kỹ thuật (năng lượng Lyapunov, Liouville, Fatou) là chuẩn nhưng ghép cẩn thận, kể cả với prior gần biên simplex. Prop hyperplane cho thấy tập ngoại lệ null nhưng không rỗng. |
| Guidance (Lemma signedconv, Thm schedule, Prop cfgatom) | trung bình | trung bình–cao | Hệ số có dấu nên không có hàm Lyapunov. Xử lý bằng tích phân từng phần với hệ số BV và đẳng thức trace của covariance có guidance. Ở nhãn cứng: mọi quỹ đạo về x^i, không có tập ngoại lệ, và có tốc độ. |
| **Composition** (Thm composition, Prop composition-open) | **cao** | trung bình | Ngưỡng dạng đóng w_c = 1/sinh²B, sắc tại đúng ngưỡng (bậc ba), và ổn định dưới nhiễu. Kết quả cho thấy lớp can thiệp dương không đóng dưới phép hợp. Tìm kiếm tài liệu (xem cuối mục) không thấy kết quả tương tự. |
| **Spectral** (Thm spectral, Cor spectral) | **cao** | **cao** | Tọa độ blow-up, Lyapunov–Perron với tốc độ β không bị chặn, thế Ψ và điều kiện mặt. Ngưỡng ma trận tổng quát hóa sạch cả hai trường hợp đóng. Giới hạn: chỉ profile hyperbolic, cần điều kiện mặt, và không xác định trọng số endpoint. |
| Transfer (Thm transfer, Prop localtransfer) | thấp | thấp | Biến thiên hằng số và Grönwall. Giá trị nằm ở cách đọc: endpoint học được bị điều khiển bởi lim sup (1−t)\|Δ\|. |
| Risk transfer, loss-no-certificate (App. C) | thấp–trung bình | thấp | Chuyên biệt hóa Benton 2024 và Beltran 2026 (App. D) cho mục tiêu suy biến. Phản ví dụ affine gọn và đạt đẳng thức. |

**Cảnh báo về tầm ảnh hưởng thực tế của kết quả composition.**
- Các endpoint mới chỉ là một tập hữu hạn tâm đường tròn ngoại tiếp (circumcentre), không phải một miền
  liên tục.
- Khi số chiều tăng, basin nhỏ đi rất nhanh. Ở d = 8, tại 5 w_c chỉ còn 0,019 (simplex) và 0,002 (box), và
  ở 1,1 cùng 2 w_c thì thấp hơn độ phân giải.
- Reviewer có thể hỏi điều này có ý nghĩa gì ở chiều ảnh. Paper đã viết thận trọng ("non-training point"),
  nhưng nên nói thẳng về sự co lại theo chiều.

**Tìm kiếm tài liệu.**
- Không thấy công trình nào trước đó đưa ra ngưỡng off-support cho guidance tác động lên trường empirical
  đã lấy trung bình nhãn.
- Công trình gần nhất là lý thuyết CFG trên Gaussian mixture
  ([Pavasovic et al.](https://www.researchgate.net/publication/388955450_Understanding_Classifier-Free_Guidance_High-Dimensional_Theory_and_Non-Linear_Generalizations)).
  Đó là mô hình của phân phối dữ liệu, không phải trường của tập train hữu hạn.
- Các công trình về closed-form score chỉ xác nhận ghi nhớ:
  [Closed-Form Diffusion Models](https://arxiv.org/pdf/2310.12395),
  [On Memorization in Diffusion Models](https://arxiv.org/html/2310.02664v2).
- Công cụ tìm paper (paper-search MCP) trả về rỗng trong phiên này. Vì vậy nên tra thêm một lượt có chủ
  đích (arXiv 2025–2026, từ khóa "guidance" + "empirical score" + "memorization") trước khi nộp.

## 5. Thí nghiệm

### 5.1 Thí nghiệm có trong paper

- Các con số đối chiếu được đều khớp (mục 2).
- Cách diễn đạt đã đúng mức:
  - Các phép tính exact được gọi là "finite-time computations … do not prove it".
  - Pilot learned-averages được ghi rõ là thống kê có chệch, không có null.
- **Appendix chi tiết thí nghiệm (rà ngày 26/10, `app:expdetails`): không có lỗi cần sửa.**
  - Đã kiểm bằng tay `tr Γ` của tam giác và simplex ở mọi mức w, w_c = 1,160 và 4,802, cùng hai phương
    trình tích phân (ṡ = βF + (1 + ε/t)s, vì 1 + ε/t = 1/t; và 1/(tβ) = ε²/t²).
  - Số ô (200 = 5 seed × 2 chiều × 2 bộ atom × 2 giá trị h × 5 arm) đúng. Toàn bộ Table composition khớp
    kết quả exact độc lập.
  - Tiêu chí on-atom (d₁² ≤ d₂²/9 trên ảnh train của run) khớp với code. Các đường dẫn artifacts và script
    được nhắc tới đều có trong repo.
  - Chưa kiểm: số liệu EXP-2/EXP-3, bảng ablation và các số của rectangle/box. `scripts/verify_paper_numbers.py`
    chưa chạy lại vì máy local không có Python và server đang lỗi host key.
- Ba câu tự giới hạn của paper nay đã có số đo để thay:
  - (a) "The composition theorem has no trained-network counterpart yet" → EXP-A.
  - (b) "error along learned trajectories, which we … have not measured" → EXP-B.
  - (c) "combines learned-field, truncation and discretisation effects" ở CIFAR-10 → EXP-C.

### 5.2 EXP-A 2D: tam giác, B = 2, w_c = 1,1596

Thiết lập: 5 seed cho mỗi biến thể. Bộ giải ROS2 L-stable chạy riêng cho từng nguồn, mạng chạy ở float64.
Đánh giá trên 2048 nguồn. Chi tiết trong `results/learned_composition_2d_20261021/SUMMARY.md`.

Tỉ lệ chiếm tâm của composite L3 (|x| < 0,05, ε = 10⁻⁵):

| w/w_c | exact | cfm_v (dự đoán v) | cfm_x_s (dự đoán x theo s) | distill_x_s |
|---|---|---|---|---|
| 0 … 0,9 | 0 | 0 | 0 | ≤ 0,005 |
| 1,1 | 0,002 | 0 | 0,001 | 0,007 |
| 2 | 0,133 | 0 | 0,143 ± 0,004 | 0,140 ± 0,004 |
| 5 | 0,673 | 0 | 0,692 ± 0,023 | 0,699 ± 0,037 |
| 10 | 0,952 | 0 | 0,962 ± 0,005 | 0,961 ± 0,012 |

**Các biến thể theo s (cfm_x_s, distill_x_s) tái hiện ngưỡng.**
- Basin tâm của trường exact được tìm lại với recall 0,97–1,00 khi w ≥ 2 w_c.
- Jacobian tại điểm hòa, tính theo đơn vị s, khớp trị riêng exact:
  - Ở w = 2 w_c: −0,27 so với exact −0,268.
  - Ở w = 0,5 w_c: +0,136 so với exact +0,134.

**CFM chuẩn tham số hóa theo v (cfm_v) không tái hiện ngưỡng.**
- Không có mẫu nào ở tâm, với mọi w.
- Độ dốc tại điểm hòa theo đơn vị s tiến về 0 (≈ 10⁻¹⁰ ở 1−t = 10⁻⁵). Sai số lớp biên ≈ 0,58, nghĩa là mạng
  không phân giải được lớp biên bề rộng (1−t)².
- Khi w ≥ 2 w_c, 16–79% mẫu kết thúc ở xa mọi atom lẫn tâm.

**Ý nghĩa.** Định lý mô tả đúng cơ chế, nhưng một mạng chỉ kế thừa cơ chế đó khi tham số hóa của nó phân
giải được lớp biên. Đây là phát hiện mới, đáng có một đoạn riêng trong paper.

### 5.3 EXP-A 1D: hai atom ±1, B ∈ {1, 2, 3}

Thiết lập: cùng bộ giải và cùng 2048 nguồn như 2D. Chi tiết trong `results/learned_composition_20261021/SUMMARY.md`.

Tỉ lệ chiếm tâm của composite L3 ở ε = 10⁻⁵ (mean ± sd theo seed):

| B | w/w_c | exact | cfm_v | cfm_x_s | distill_x_s |
|---|---|---|---|---|---|
| 1 | 1,1 | 0,050 | 0 | 0,054 ± 0,004 | 0,049 |
| 1 | 2 | 0,406 | 0 | 0,401 ± 0,006 | 0,407 |
| 1 | 10 | 0,991 | 0 | 0,991 | 0,991 |
| 2 | 2 | 0,182 | 0,000 | 0,177 ± 0,007 | 0,179 |
| 2 | 5 | 0,532 | 0,000 | 0,530 ± 0,004 | 0,535 |
| 3 | 2 | 0,069 | 0,049 ± 0,088 | 0,056 ± 0,030 | 0,066 |
| 3 | 10 | 0,396 | 0,056 ± 0,104 | 0,378 ± 0,009 | 0,395 |

**Kết quả giống 2D.** Các biến thể theo s tái hiện đường cong exact ở cả ba B: không có khối lượng ở tâm
khi w < w_c, và khớp tới khoảng 0,01 khi w > w_c. Ngoại lệ nhỏ là cfm_x_s ở B = 3, w = 5 w_c
(0,167 ± 0,084 so với 0,221).

**Các biến thể theo v không có cơ chế ngưỡng.** Ngoài cfm_v còn hai biến thể khác: cfm_v_tis (5 seed) và
cfm_v_sep (4 seed).
- Ở B = 1 và B = 2 chúng không đặt mẫu nào ở tâm.
- Ở B = 3 có một ít khối lượng ở tâm, nhưng nó không phụ thuộc w: nó có cả trong đối chứng w = 0
  (L1: 0,048 ± 0,083, trong khi exact là 0). Đó là mẫu bị kẹt, không phải hiệu ứng composition.
- Độ dốc tại điểm hòa theo đơn vị s tiến về 0, và E_BL ≈ 0,67 khi 1−t ≤ 0,1. Hai số này cho cùng chẩn đoán
  như ở 2D.

**Một lỗi bộ giải đã được báo cáo.** cfm_v_sep seed 2 không chạy xong arm B = 1, r = 10. Lần đầu nó dừng
vì W = I − γhJ suy biến. Sau khi sửa để bước suy biến bị từ chối, bước của một nguồn lại co lại mãi, nên
run được dừng sau 5 giờ. Run này bị loại khỏi bảng (cfm_v_sep còn 4 seed), và bộ tổng hợp giờ chỉ đọc các
run đã đánh giá bằng ROS2.

### 5.4 EXP-B và EXP-C

Chi tiết trong `docs/review/exp_b_c_results_2026-10-23.md`.

**EXP-B (EXP-1, h = 0):**
- K(t) = m/r tăng như (1−t)⁻². Ở 200k bước: 1,5 tại 1−t = 0,5 và 2·10⁷ tại 1−t = 10⁻⁴.
- Cận chỉ dựa trên loss nhỏ hơn ‖Z_T − Y_T‖ thật khoảng 100 lần.
- Tiền đề quả cầu của Prop `prop:localtransfer` không thỏa ở mạng nào. Tiền đề trên quỹ đạo thỏa cho 1–11%
  quỹ đạo, và khi thỏa thì kết luận đúng 100%.

**EXP-C (CIFAR-10, h = 6):**
- 25% mẫu off-atom với RK4 hội tụ, và 30% với Euler 50 bước.
- Trường exact cho 0% ở cả 1−t = 10⁻³ và 10⁻⁴.
- Chỉ 19% mẫu kết thúc ở cùng atom mà trường exact chọn.
- Vậy cắt cụt đóng góp khoảng 0, rời rạc hóa khoảng 4 điểm phần trăm, còn lại là sai số của mạng.

## 6. Đề xuất cho paper, theo thứ tự ưu tiên

1. Sửa 8 lỗi trình bày ở mục 3. Mỗi lỗi chỉ cần một dòng.
2. Thay câu "no trained-network counterpart" bằng EXP-A, và nói rõ sắc thái: dự đoán x theo s tái hiện
   ngưỡng, còn dự đoán v thì không. Câu này trả lời trước câu hỏi "định lý có liên quan tới mạng thật không".
3. Thay "have not measured" trong Limitations bằng EXP-B: K(t) ~ (1−t)⁻², cận theo loss thiếu khoảng 100 lần,
   tiền đề quả cầu không thỏa.
4. Thay câu thận trọng về CIFAR-10 ở `sec:p7` bằng phép tách của EXP-C. Cần nói rõ phép tách đo trên ba
   run `heff`, còn con số 38% đến từ run `exp3_cifar_ddpm_h6` (không còn trọng số). Trên các run `heff`,
   tỉ lệ off-atom với Euler 50 bước là 0,298 ± 0,058.
5. Nói thẳng về việc basin co lại theo số chiều (d = 8) trong phần thảo luận của Theorem composition.
6. Tra thêm tài liệu về tính mới của kết quả composition (mục 4).

## 7. Mức tin cậy

- **Đúng đắn toán học:** cao cho U1, U3, U4, U5, U7, U8. Trung bình–cao cho U6, vì:
  - tính C¹ của đồ thị Lyapunov–Perron dựa vào kết quả chuẩn về khả vi của điểm bất động (để có null chỉ
    cần Lipschitz, và Lipschitz đã được chứng minh);
  - đoạn "Solutions" dẫn Hale cho trường Carathéodory, trong khi mọi trường cụ thể trong paper đều liên tục
    theo thời gian.
- **Thí nghiệm bổ sung:** cao cho chiều và độ lớn của hiệu ứng.
  - Bộ giải đã được đối chứng: trường exact cho 0,4434 / 0,1797 / 0,0488 / 0; distill khớp exact.
  - Số seed nhỏ (3–5), nên các khoảng ± chỉ là mô tả.
- **Tính mới:** trung bình. Lý do là công cụ tìm tài liệu bị hạn chế trong phiên này.

## 8. Lượt kiểm tra bổ sung (26–27/10) trên bản đã sửa

Các unit được dựng lại từ `paper/main.tex` sau 8 sửa ở mục 3, và có thêm unit U9. U9 đặt các tuyên bố của
abstract, intro, Table 1, Section 4.4, Limitations và Conclusion cạnh 22 phát biểu hình thức.

**Lượt 4: cả 8 unit đều CORRECT.** Mỗi unit giờ có 4 lượt HOLDS và 0 lượt bác, tức đạt ngưỡng xác nhận
4-HOLDS của skill. Lượt 5 không cần chạy.

| Unit | 4 lượt | Tấn công đã chạy (tất cả CORRECT) |
|---|---|---|
| U1 | 4/4 | #5 |
| U2 | 4/4 | #5 |
| U3 | 4/4 | #5, #40 |
| U4 | 4/4 | #5, #40 |
| U5 | 4/4 | #5, #40, #4 (thử với hỗn hợp dương, w = 0 và đúng ngưỡng: lập luận dừng đúng ở bước cần F′(s*) < 0) |
| U6 | 4/4 | #5, #40 |
| U7 | 4/4 | #40, #18 |
| U8 | 4/4 | #40 |

**Điểm mới từ các lượt tấn công** (không điểm nào là lỗi toán):
- **#18 trên Thm transfer.** Bất đẳng thức đúng với mọi đường cong liên tục tuyệt đối và mọi điểm a, và
  thành đẳng thức khi vế phải hội tụ. Paper đã tự nói điều này (main.tex:677–686), chỉ là unit không chứa
  đoạn đó.
  - Gợi ý đáng làm: chứng minh của Prop localtransfer thực ra cho một cận tiên nghiệm,
    limsup|Z_t − a| ≤ limsup_{t↑1} sup_{|x−a|≤ρ} (1−t)|Δ(x,t)| ≤ ρ/4. Cận này không phụ thuộc quỹ đạo, nên
    hữu ích hơn dạng hiện tại.
- **#5 trên U1 và U4.**
  - Lớp nghiệm của phương trình liên tục chưa được định nghĩa hình thức.
  - "BV trên [t₀, 1)" phải hiểu là tổng biến phân hữu hạn trên cả khoảng.
  - Hale Ch. I chỉ chứng minh luồng C¹ cho trường liên tục theo t. Trường hợp Carathéodory dựa vào phác
    thảo trong paper; phác thảo đó đúng.
- **#40 trên U7.** Câu "áp dụng Theorem từ t₀" nên nói rõ rằng phương trình không đổi dạng khi dời gốc
  thời gian. Giả thiết khả tích của Δ là thừa.

**U9, đối chiếu tuyên bố với định lý: có tuyên bố vượt quá điều được chứng minh.** Mọi điểm dưới đây đều
sửa được bằng câu chữ; abstract đã có đủ điều kiện. Tôi đã tự đối chiếu từng điểm với main.tex:
1. **Câu "practitioner" ở intro (dòng 142–146):** "not from label noise, label averaging or guidance applied
   separately to the field that training defines". Câu này mâu thuẫn với dòng 140, Table 1 hàng 6 và dòng
   430–431: lấy trung bình hai trường hard-label (h = 0) đưa mọi nguồn về trung điểm. Cần thêm "at positive
   label bandwidth".
2. **Cũng câu đó:** "a learned field whose endpoint prediction does not converge" phải là "does not converge
   to its training example". Một dự đoán hội tụ về điểm b khác atom cũng cho endpoint ngoài tập train.
3. **Kết luận (dòng 896–898):** "positive mixtures of prior-indexed exact fields, including label averaging
   and negative guidance" thiếu "with strictly positive priors (h > 0)". Thêm nữa, "negative guidance" chỉ
   được chứng minh cho w ∈ [−1, 0).
4. **Section 4.4 (dòng 642–643):** "Endpoint noise … is the only one among them that leaves the atoms for
   every source" mâu thuẫn với Table 1 hàng 6. Thêm nữa, Prop tgtnoise chỉ cho kết luận hầu chắc chắn theo
   π₀. Nên viết: "the only one that leaves the atoms in every configuration: its endpoint law has a density".
5. **Câu tóm tắt ở intro (dòng 139–142):** "for learned fields, from an error that does not vanish at the
   scale (1−t)⁻¹" chỉ đúng ở nhãn định danh. Ở h > 0, agent dựng được phản ví dụ:
   Δ = −2 tanh(s)/(1−t) cho sai số tỉ lệ dọc quỹ đạo → 0, nhưng một tập mở các nguồn hội tụ về trung điểm.
   Cần thêm "at an identifying label".
6. **Lỗi nhỏ.**
   - Ở intro, B chưa được định nghĩa ("on two examples the threshold is exactly w > 1/sinh²B").
   - Kết luận ghi "threshold … stable under perturbation", trong khi cái được chứng minh ổn định là basin
     ngoài atom.
   - Limitations có thể thêm các trường hợp chưa được phủ: w cố định < −1, và lịch guidance không BV.
   - Câu hỏi mở "many atoms in high dimension" trong kết luận nói thấp hơn Theorem spectral; nên viết
     "beyond hyperbolic profiles and the face condition".

**Một điểm U9 nêu sai:** agent cho rằng Table 1 không có cơ sở cho lịch guidance ở h = 0. Nhận xét ở
main.tex:501–503, kèm appendix "Time-dependent guidance at a hard label" (đã được U4 kiểm 4 lượt), phủ mọi
lịch đo được, bị chặn địa phương và không âm với w = O((1−t)^{−γ}), γ < 2. Vì vậy mọi lịch bị chặn đều
được phủ. Chỉ nên viết rõ "w ≥ 0" cho cả hai trường hợp trong hàng đó.

**Số liệu:** `scripts/verify_paper_numbers.py`, chạy bằng `.venv` của repo, cho 429/429 số khớp với bản đã sửa.

**Kết luận cập nhật:** phần toán được xác nhận ở ngưỡng 4-HOLDS cho cả 8 unit. Phần cần sửa trước khi nộp
không nằm ở chứng minh, mà ở 5–6 câu tóm tắt trong intro, Section 4.4 và Conclusion đã bỏ mất các điều kiện
h > 0, prior dương ngặt và nhãn định danh.
