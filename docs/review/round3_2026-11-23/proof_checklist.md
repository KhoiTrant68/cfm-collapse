# Checklist kiểm tra 3 chứng minh của paper A

Phần "Use of large language models" của paper A ghi rằng ba kết quả dưới đây do mô hình
soạn trước rồi tác giả kiểm tra lại. Checklist này để hai người làm đúng việc đó, từng bước,
trước khi nộp. Số dòng là của `paper_theory/main.tex` ngày 2026-11-23.

Cách dùng: đọc dòng "Ý chính" để biết chứng minh muốn làm gì, rồi đi qua từng ô. Mỗi ô là một
bước tự kiểm được bằng giấy bút. Ô "Mình đã thử" ghi điều mình (trợ lý) đã kiểm và thấy đúng;
nó chỉ giúp đi nhanh hơn, không thay được việc hai người tự kiểm. Chỗ nào thấy sai hoặc thiếu,
ghi ngay bên cạnh ô.

Thời gian dự kiến: cor:twofields 45 phút (phần lớn là đọc lại các bổ đề nó dựa vào),
prop:twoatom 30 phút, rem:generic 30 phút.

---

## 1. Corollary cor:twofields (Any two exact fields)

Phát biểu: dòng 734. Chứng minh: dòng 2393.

**Ý chính.** Mọi tổ hợp của hai trường chính xác, `c v_p + (1-c) v_q`, đều chỉ là một trong
hai trường hợp đã chứng minh: hỗn hợp dương (Theorem thm:posmix) hoặc guidance có lịch
(Theorem thm:schedule) với hai prior bất kỳ thay cho prior có điều kiện và prior không điều kiện.
Rủi ro duy nhất là câu "proof applies verbatim": nếu chứng minh của thm:schedule lén dùng một
tính chất riêng của `p^unc` (ví dụ đều), thì hệ quả này sai.

**Bước 1. Chia trường hợp theo c** (dòng 2395-2398)
- [ ] `0 <= c <= 1`: trường là `v_Pi` với `Pi = c delta_p + (1-c) delta_q`, một độ đo xác suất
      trên `Ppos`. Đúng giả thiết của thm:posmix (dòng 599)? Kể cả khi `c = 0` hoặc `c = 1`.
- [ ] thm:posmix cho hội tụ về `C`, còn hệ quả nói `C'`. Kiểm `C` là tập con của `C'`
      (Lemma lem:basic(d), dòng 1917).
- [ ] `c > 1`: `c v_p + (1-c) v_q = (1+w) v_p - w v_q` với `w = c - 1 > 0`. Khai triển lại.
- [ ] `c < 0`: `c v_p + (1-c) v_q = (1+w) v_q - w v_p` với `w = -c > 0`. Khai triển lại.
- [ ] Trường hợp lịch `w(t)`: giả thiết của hệ quả (`w` đo được, giá trị trong `[0, wbar]`,
      biến phân bị chặn trên `[t0, 1)`) khớp với giả thiết của thm:schedule (dòng 717).

Mình đã thử: cả bốn khai triển đúng. Một điểm rất nhỏ: hệ quả viết "for some `t0 < 1`", còn
thm:schedule viết `t0 in (0,1)`. Nếu biến phân bị chặn trên `[t0, 1)` thì cũng bị chặn trên mọi
đoạn con, nên không ảnh hưởng gì. Có thể sửa cho khớp chữ.

**Bước 2. Câu "verbatim": chứng minh thm:schedule dùng hai prior ở đâu** (dòng 2323-2390)

Đi qua chứng minh thm:schedule, đánh dấu mọi chỗ xuất hiện `p_c` hoặc `p_u`, và kiểm rằng
mỗi chỗ chỉ cần prior nằm trong `Ppos` (mọi khối lượng dương):
- [ ] Lemma lem:signedconv (dòng 2253) với `K = 2`, `c = (1+w, -w)`: chỉ cần
      `p_min = min p_{k,j} > 0` (dùng trong cận KL của lem:basic(b)).
- [ ] Đẳng thức `tr Cov = r^2 - |m_p - z|^2 + e_p` với `e_p >= 0`: đúng cho mọi prior,
      vì chỉ dùng việc các nguyên tử trong `S` cách `z` đúng bằng `r`.
- [ ] `e_p -> 0` dọc quỹ đạo: lem:basic(c), cần `p_i > 0` (xem phương trình eq:pf:int:conc,
      dòng 1971-1975, có thương `p_j / p_i`).
- [ ] Đẳng thức `(1+w)|u|^2 - w|v|^2 = |(1+w)u - wv|^2 - w(1+w)|u - v|^2`: đại số thuần túy,
      khai triển hai vế.
- [ ] Cận dưới `Theta >= r^2 - |mu_w|^2 - wbar e_{p_u}`: chỉ dùng `w >= 0`, `w <= wbar`,
      `e_{p_c} >= 0`. Không dùng gì riêng của `p_u`.
- [ ] Phần tích phân `beta Theta` trên từng đoạn `[n, n+1]` (dòng 2365-2388): không có prior nào.

Mình đã thử: không tìm thấy chỗ nào dùng `p_u` đều hay dùng quan hệ giữa `p_c` và `p_u`. Câu
"verbatim" đứng vững. Câu dòng 732 ("Nothing in these results depends on the unconditional field
being unconditional") nói cùng ý.

**Bước 3. Nền giải tích** (đoạn "Solutions", dòng 1986; Lemma lem:volume, dòng 2051)
- [ ] Với `w(t)` chỉ đo được, quỹ đạo là nghiệm Carathéodory. Đoạn "Solutions" vừa được viết lại
      để dẫn Sontag (1998) thay cho Hale (mục A7). Kiểm rằng trường của thm:schedule có dạng
      `f(x,t) = f~(pi(t), x)` với `pi(t) = (t, c(t))`, `f~` và `D_x f~` liên tục.
- [ ] lem:volume dùng công thức Liouville `J = exp int div f` dọc dòng chảy. Với `w` đo được,
      công thức này đến từ Sontag, Lemma C.4.1(f), áp dụng cho `A(t) = D_x f` dọc một quỹ đạo.
      Kiểm `D_x f` bị chặn địa phương: lem:signedconv đã cho cận
      `||D_x v_c|| <= (cbar beta_T R^2 + 1)/(1-T)` trên `R^d x [0, T]`.

Số trang Sontag đã đối chiếu với bản PDF của tác giả: Definition 2.6.1 (tr. 43), Theorem 1
(tr. 57), Remark 2.8.1 (tr. 62), Theorem 54 (tr. 476), Proposition C.3.6 (tr. 481),
Lemma C.4.1(f) (tr. 488). Ghi chú cùng nội dung nằm trong `paper_theory/refs.bib`.

---

## 2. Proposition prop:twoatom (Blending two examples needs a subtracted intermediate field)

Phát biểu: dòng 1015. Chứng minh: dòng 3030.

**Ý chính.** Ở trung điểm `z` của hai nguyên tử `a, b`, mọi thứ thu về một hàm một biến
`F(zeta) = sum_k c_k tanh(zeta + B_k)`. Điểm `z` nhận xác suất dương chỉ khi `F` có một nghiệm
với `F' < 0`. Phần (a) và (b) chỉ ra khi nào điều đó không thể xảy ra, phần (c) tính trường hợp
phép hội (conjunction).

**Bước 1. Thu gọn về một chiều** (dòng 3032-3050)
- [ ] Với `nu = (a-b)/2`, prior `p_k` bị nghiêng bởi `e^{<xi, .>}` cho `a` log-odds
      `2(B_k + zeta)` so với `b`. Dùng `a - b = 2 nu` và `<xi, nu> = zeta`.
- [ ] Trung bình của luật hai điểm: `b + P(a)(a - b) = z + nu tanh(zeta + B_k)`, với
      `P(a) = (1 + tanh)/2`.
- [ ] `Gamma = D_L M = F'(zeta) nu nu^T`: đạo hàm của `nu F(<xi, nu>)` theo `xi`.
- [ ] Gộp các prior có cùng `B_k` (cộng hệ số) không đổi `F` và `Gamma`.
- [ ] Điều kiện mặt (face condition) của thm:spectral(c) đúng: mặt thật sự của một đoạn thẳng là
      hai đầu mút, còn `P_L z` là trung điểm.
- [ ] Phụ thuộc ngầm: kết luận "`Pr(X_1 = z) = 0`" đến từ thm:spectral(c) (chứng minh từ dòng
      2704; phần (c) ở khoảng dòng 2923-2990). Chứng minh đó không nằm trong ba cái cần kiểm,
      nhưng nên đọc lướt phần (c) để chắc nó cho đúng điều được dùng ở đây.

**Bước 2. Đẳng thức** (dòng 3052-3056)
- [ ] `F'(zeta) = sum c_k (1 - m_k^2) = 1 - V` dùng `sum c_k = 1`.
- [ ] Tại một profile, `sum c_k m_k = 0`.

**Bước 3. Phần (a)** (dòng 3058-3066)
- [ ] Vì `tanh` tăng, `m_-` và `m_+` thuộc về prior có `B` nhỏ nhất và lớn nhất. Sau khi gộp, các
      `B_k` khác nhau, nên mọi `m_k` khác nằm *chặt* giữa.
- [ ] `sum c_k q(m_k) = V + m_- m_+`, với `q(x) = (x - m_-)(x - m_+)`: khai triển và dùng hai ràng
      buộc tuyến tính.
- [ ] `q(m_pm) = 0`, nên hệ số của hai prior ngoài cùng (dấu bất kỳ) không đóng góp; các hệ số
      bên trong không âm và `q < 0` ở giữa, nên tổng `<= 0`.
- [ ] `V <= -m_- m_+ <= |m_-||m_+| < 1`, nên `F' > 0`.
- [ ] Trường hợp suy biến: chỉ có một giá trị `B`. Khi đó `F = tanh(zeta + B)`, `F' > 0`.

**Bước 4. Phần (b)** (dòng 3068-3078)
- [ ] `c_2 >= 0` thì quay về (a).
- [ ] `c_2 < 0, c_3 <= 0`: `c_1 = 1 - c_2 - c_3 > 1` và `m_3 < m_2 < m_1`.
- [ ] Chuỗi `c_1 m_1 = |c_2| m_2 + |c_3| m_3 <= (|c_2| + |c_3|) m_2 = (c_1 - 1) m_2 < (c_1 - 1) m_1`.
      Bước `<=` dùng `m_3 < m_2`; bước `<` dùng `c_1 - 1 > 0` và `m_2 < m_1`. Suy ra `m_1 < 0`.
- [ ] `V = |c_2| m_2 (m_1 - m_2) + |c_3| m_3 (m_1 - m_3) < 0`: thay `c_1 m_1^2 = m_1(|c_2| m_2 + |c_3| m_3)`.
      Số hạng đầu âm chặt vì `|c_2| > 0`, `m_2 < 0`, `m_1 > m_2`.
- [ ] Trường hợp `c_1 <= 0` theo đối xứng đổi `a` và `b` (đảo dấu `zeta` và mọi `B_k`).
- [ ] `c_1 <= 0` và `c_3 <= 0` cùng lúc với `c_2 < 0` không thể có (tổng phải bằng 1).

**Bước 5. Phần (c)** (dòng 3080-3083)
- [ ] `F = F_w` của eq:composition-mean (dòng 783). Hệ số: `(1+w)/2 + (1+w)/2 - w = 1`.
- [ ] Nghiệm: `0`, và `+-s_u` với `cosh s_u = sqrt(w) sinh B` khi `w > 1/sinh^2 B`.
- [ ] Tại `+-s_u`, `F_w' > 0`: nhân tử `cosh^2 s - w sinh^2 B` đổi dấu từ âm sang dương khi `|s|`
      tăng qua `s_u`, và `tanh s_u != 0`, nên đạo hàm khác 0 và dương.
- [ ] `F_w'(0) = (1+w) sech^2 B - w < 0` đúng khi `w > 1/sinh^2 B`.

Mình đã thử: cả năm bước đúng, không thấy lỗi.

---

## 3. Remark rem:generic (How restrictive the hypotheses of Theorem thm:spectral(c) are)

Phát biểu và lập luận nằm ngay trong remark, dòng 951-974. Không có phần chứng minh riêng.

**Ý chính.** Hai giả thiết của thm:spectral(c) hiếm khi bị vi phạm. Điều kiện mặt chỉ phụ
thuộc vào hình học của các nguyên tử và đúng trong mọi cấu hình của paper. Tính hyperbolic
đúng với hầu hết mọi prior, nhờ định lý hoành tham số (parametric transversality).

**Bước 1. Điều kiện mặt** (dòng 952-957)
- [ ] `P_L S = P_L z + (S - z)` vì `a - z` nằm trong `L` với mọi `a` trong `S`.
- [ ] Điều kiện tương đương: `z` không nằm trong bao affine của mặt thật sự nào của `conv S`.
- [ ] `|S| = 2`: mặt thật sự là hai đầu mút, `z` là trung điểm, không phải nguyên tử.
- [ ] `z` ở phần trong tương đối của `conv S`: bao affine của một mặt thật sự nằm trong một siêu
      phẳng tựa của `conv S` (trong `aff S`), nên không chứa điểm trong tương đối.
- [ ] "Đúng với mọi cấu hình của Section sec:intervention-tests": đối chiếu với các cấu hình trong
      Table tab:spectral (tam giác, simplex, hình chữ nhật, khối lập phương) và xác định `|S|`
      hoặc vị trí của `z` cho từng cái.

**Bước 2. Đạo hàm theo prior** (dòng 958-961)
- [ ] Tham số hóa bằng log-ratio `lambda_{k,a} = log(p_k(a)/p_k(a_0))`. `M` chỉ phụ thuộc vào
      prior qua `lambda` (vì `pi_k` chỉ dùng prior thu hẹp trên `S`, đã chuẩn hóa).
- [ ] `dE[a]/d lambda_{k,a} = pi_k(a)(a - E[a])`: đạo hàm của trung bình theo log-trọng số.
      Nhân thêm `c_k` vì `M = sum c_k E_{pi_k}[a]`.

**Bước 3. Các vectơ đạo hàm sinh ra L** (dòng 962-964)
- [ ] Tổng `sum_{a in S} pi(a)(a - E[a]) = 0`, nên vectơ ứng với `a_0` là tổ hợp của các vectơ còn
      lại, và span của các vectơ `a != a_0` bằng span của tất cả.
- [ ] Vì mọi `pi(a) > 0`, span đó bằng span của `{a - E[a]}`, chứa mọi hiệu `a - a'`.
- [ ] Span của các hiệu bằng `L`: dùng `z` thuộc `aff S`, nên `a - z` là tổ hợp affine của các hiệu.
- [ ] Các vectơ nằm trong `L`: `E[a]` thuộc `conv S`, là tập con của `aff S = z + L`.

**Bước 4. Định lý hoành và chuyển về prior** (dòng 964-970)
- [ ] `G(xi; lambda)` trơn và là submersion trên `L x R^{K(|S|-1)}`, đúng giả thiết của định lý
      hoành tham số. Kết luận: với hầu hết mọi `lambda`, 0 là giá trị chính quy của `G(.; lambda)`,
      tức `Gamma` khả nghịch ở mọi profile.
- [ ] Trích dẫn \citep[Ch.~2, §3]{guillemin1974differential}: mình **chưa** đối chiếu với sách.
      Cần mở Guillemin và Pollack để chắc định lý hoành nằm ở Chương 2, mục 3, và phát biểu
      có dạng "for almost every s".
- [ ] Chỉ biến thiên khối `lambda_{k0}` của một prior có `c_{k0} != 0` cũng đã là submersion
      (cùng lập luận Bước 3 với một `k`).
- [ ] Ánh xạ log-ratio từ `Ppos` lên khối đó là submersion, và tạo ảnh ngược của một tập độ đo 0
      qua submersion có độ đo 0. Vì vậy với hầu hết mọi `p_{k0}`, mọi profile hyperbolic, còn
      `p^unc` có thể giữ đều.
- [ ] `C'` hữu hạn (lem:basic(d)), nên hợp hữu hạn các tập độ đo 0 vẫn có độ đo 0.
- [ ] Câu "in Theorem thm:composition they occur only at `w = w_c`": profile là `0` và `+-s_u`;
      `F'(+-s_u) > 0` (xem prop:twoatom, Bước 5), nên chỉ `0` có thể không hyperbolic, và chỉ khi
      `w = w_c`.

Mình đã thử: Bước 1 đến Bước 4 đúng, trừ trích dẫn Guillemin và Pollack chưa kiểm với sách.

---

## Sau khi kiểm xong

- Nếu cả ba đều ổn: xóa dòng TODO phía trên phần "Use of large language models" (dòng 1424 của
  `paper_theory/main.tex`). `submit/build.py` sẽ hết báo ghi chú đó.
- Nếu có chỗ sai hoặc thiếu: ghi vào ô tương ứng ở đây, báo lại để sửa trong `paper_theory/`,
  rồi chạy lại `python submit/build.py`.
