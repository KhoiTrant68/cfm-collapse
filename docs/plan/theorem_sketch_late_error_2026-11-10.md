# Phác thảo: định lý về sai số muộn dọc quỹ đạo learned — 10/11/2026

**Trạng thái: bản phác thảo để tác giả xem.** Các chứng minh dưới đây là ý tưởng và lập luận ngắn,
chưa qua quy trình kiểm chứng của dự án (solver độc lập, verifier đối kháng). Tác giả viết lại và
kiểm chứng trước khi đưa vào bài. Đã kiểm tra số: bất đẳng thức của Bổ đề 1 trên ví dụ 2D, và dự
đoán của Mệnh đề 4 trên dữ liệu EXP-B sẵn có.

## 1. Vì sao cần

Theo panel 2 và đánh giá ngày 9/11, hai điểm yếu nặng nhất là:

- **W1:** Theorem `transfer` chặn khoảng cách endpoint bằng chính sai số tại endpoint (DA M3), nên
  không dự đoán được gì từ loss. Theorem `risktransfer` thì *giả sử* tỉ số $K=m/r$, không suy ra.
- **W2:** ở positive bandwidth chỉ có bản cục bộ (Prop. `localtransfer`).

S10 cho một quan sát chưa có lý thuyết: cùng một network, đo dọc quỹ đạo exact thì sai số về
$0.006$, còn đo dọc quỹ đạo của chính nó thì giữ quanh $6$. EXP-B cho $K(t)\approx(1-t)^{-2}$, cũng
chưa được giải thích.

Ý tưởng chung: viết field ở dạng *data prediction* $v=(\hat x-x)/\varepsilon$ với
$\varepsilon=1-t$. Khi đó exact flow co với tốc độ đúng bằng $1/\varepsilon$, nên ngưỡng tự nhiên
là **chuẩn logarit của Jacobian của $\hat x$ so với 1**.

## 2. Ký hiệu

- $\varepsilon_t=1-t$. Exact data prediction $m^*(x,t)=\sum_i w_i^{(h)}(x,t,y)\,x^i$ (ở $h=0$ và
  label identifying thì $m^*\equiv a$). Exact field $v^*=(m^*-x)/\varepsilon$.
- Learned field $v_\theta=(\hat x_\theta-x)/\varepsilon$, với $\hat x_\theta(\cdot,t)$ thuộc lớp
  $C^1$ theo $x$. Sai số theo scale của bài: $(1-t)|\Delta|=|\hat x_\theta-m^*|$.
- Từ cùng $X_0$: $Y$ là exact flow, $Z$ là learned flow, $D_t=Z_t-Y_t$.
- $e_Y(t)=|\hat x_\theta(Y_t,t)-m^*(Y_t,t)|$: sai số của network **trên quỹ đạo exact** (đại lượng
  `e_exact` của S10). Ở $h=0$, $Y_t=ta+\varepsilon_tX_0$ có đúng phân phối training tại label đó,
  nên $\E e_Y(t)^2=\varepsilon_t^2\,r(t)$, với $r$ là training-law error của Theorem `risktransfer`.
- Chuẩn logarit (one-sided Lipschitz) trên đoạn thẳng nối $Y_t$ và $Z_t$:
  $\mu(t)=\sup_{s\in[0,1]}\lambda_{\max}\big(\operatorname{sym}\partial_x\hat x_\theta(Y_t+sD_t,t)\big)$.

## 3. Bổ đề 1 (ước lượng co) — mọi $h\ge0$

**Phát biểu.** Với $t_0\le t<1$,
$$
|D_t|\le|D_{t_0}|\,e^{-\int_{t_0}^t\frac{1-\mu}{\varepsilon}}
+\int_{t_0}^t\frac{e_Y(s)}{\varepsilon_s}\,e^{-\int_s^t\frac{1-\mu}{\varepsilon}}\,ds .
$$

**Ý chứng minh.**
$\dot D=\big[\hat x_\theta(Z)-\hat x_\theta(Y)-D+(\hat x_\theta(Y)-m^*(Y))\big]/\varepsilon$.
Viết $\hat x_\theta(Z)-\hat x_\theta(Y)=\bar J D$ với $\bar J=\int_0^1\partial_x\hat x_\theta(Y+sD)\,ds$,
thì $\langle D,\bar JD\rangle\le\mu|D|^2$. Do đó đạo hàm Dini trên thỏa
$D^+|D|\le\big((\mu-1)|D|+e_Y\big)/\varepsilon$, rồi áp dụng bổ đề so sánh. Lập luận chỉ dùng
$\dot Y=(m^*(Y)-Y)/\varepsilon$, nên đúng cho mọi $h$.

**Kiểm tra số** (`contraction_check.py` trong scratchpad, $d=2$, 6 atom, $h>0$, bốn kiểu nhiễu):
khi tính $\mu$ chính xác trên đoạn, bất đẳng thức đúng tại mọi bước
($\max(|D|-\text{bound})\approx-4\cdot10^{-5}$). Nếu Y và Z kết thúc cùng atom thì bound rất sát
($0.3354$ so với $0.3361$). Nếu kết thúc **khác atom** thì bound lên tới $10^5$–$10^{36}$, nghĩa là
vô dụng (xem Nhận xét 5).

## 4. Hệ quả 2 (chứng thực từ training loss) — label identifying, $h=0$

**Phát biểu.** Giả sử có $\bar\mu<1$ sao cho
$\sup_x\lambda_{\max}(\operatorname{sym}\partial_x\hat x_\theta(x,t))\le\bar\mu$ với mọi
$t\in[t_1,1)$, và $\E|Z_{t_1}|^2<\infty$. Điều kiện sau đúng chẳng hạn khi
$|\hat x_\theta(x,t)|\le M(1+|x|)$ trên $[0,t_1]$, theo Gronwall. Giả thiết này **bắt buộc**:
verifier đã dựng được phản ví dụ khi thiếu nó. Ví dụ, một field $C^1$ trước $t_1$ biến $X_0$ thành
$X_0e^{X_0^2}$, có phương sai vô hạn. Khi đó
$$
\limsup_{t\uparrow1}\|Z_t-a\|_{L^2}\ \le\ \frac{1}{1-\bar\mu}\,\limsup_{t\uparrow1}\varepsilon_t\sqrt{r(t)} .
$$
Hằng số $1/(1-\bar\mu)$ là chặt: với $\hat x_\theta(x)=a+\bar\mu(x-a)+c$, mọi quỹ đạo hội tụ tới
$a+c/(1-\bar\mu)$, trong khi $e_Y\to|c|$.

**Ý chứng minh.** *Bước 1 ($Z_t\in L^2$ với mọi $t\ge t_1$):* so sánh $Z$ với quỹ đạo learned
$Z^0$ xuất phát từ $0$. Áp dụng Bổ đề 1 cho hai nghiệm của cùng field learned: số hạng nguồn bằng
0, nên $|Z_t-Z^0_t|\le|Z_{t_1}-Z^0_{t_1}|$. Bước này thay cho một phép chia trường hợp từng có lỗ
hổng: trường hợp $E(t_1)=\infty$ nhưng $E(t_2)<\infty$. *Bước 2:* áp dụng Bổ đề 1 với
$\mu\le\bar\mu$ và bất đẳng thức Minkowski. Đặt
$E=\sup_{s\ge t_1}\|e_Y(s)\|_{L^2}$. Số hạng tích phân bị chặn bởi
$E\,\varepsilon_t^{1-\bar\mu}\int_{t_1}^t\varepsilon_s^{\bar\mu-2}ds\le E/(1-\bar\mu)$, còn số hạng
đầu tắt như $(\varepsilon_t/\varepsilon_{t_1})^{1-\bar\mu}$. Cuối cùng dùng $Y_t\to a$. Ở $h=0$ thì
$m^*\equiv a$, nên đoạn nối $Y_t$ và $Z_t$ không bao giờ đi qua vùng tie.

**Ý nghĩa.** Kết quả này trả lời trực tiếp W1. Nếu data prediction của network co ($\bar\mu<1$),
thì training loss ở thời điểm muộn, đo theo scale $\varepsilon\sqrt r$, chặn được khoảng cách
endpoint mà không cần đo gì dọc quỹ đạo learned. Ngưỡng là $\bar\mu=1$, không phải độ lớn của loss.

## 5. Mệnh đề 3 (ngưỡng là sắc) — tổng quát hóa Prop. `regular`(b) lên $d$ chiều

**Phát biểu.** Giả sử có lân cận lồi $U$ của $z$ và $t_2<1$ sao cho
$\lambda_{\min}(\operatorname{sym}\partial_x\hat x_\theta)\ge1+\kappa$ trên $U\times[t_2,1)$, với
$\kappa>0$. Khi đó có nhiều nhất một điểm ban đầu có quỹ đạo hội tụ tới $z$.

**Ý chứng minh.** Giống phần "repelling" trong chứng minh của Prop. `regular`(b): với hai quỹ đạo
cùng nằm trong $U$, $\frac{d}{dt}|D|^2\ge2\kappa|D|^2/\varepsilon$, nên
$|D|\gtrsim\varepsilon^{-\kappa}\to\infty$, mâu thuẫn.

Hệ quả 2 và Mệnh đề 3 cùng cho thấy: $\mu<1$ thì endpoint bị kéo về training example; $\mu>1$ thì
endpoint bị đẩy ra; $\mu=1$ là trường hợp biên.

## 6. Mệnh đề 4 (vì sao $K\asymp(1-t)^{-2}$) — velocity network chính quy, $h=0$

**Phát biểu.** Giả sử $v_\theta$ liên tục trên $\R^d\times[0,1]$ và thỏa giả thiết của Prop.
`regular`(a), cùng điều kiện bị chặn đủ để dùng hội tụ trội. Khi đó
$$
(1-t)^2K(t)\ \longrightarrow\ \frac{\E|Z_1-a|^2}{|v_\theta(a,1)-a|^2+d}\ \in\ \Big(0,\ \tfrac{\E|Z_1-a|^2}{d}\Big].
$$

**Ý chứng minh.**
- Mẫu số: teacher trên training law là $f(Y_t,t)=a-X_0$, ngẫu nhiên, trong khi
  $v_\theta(Y_t,t)\to v_\theta(a,1)$ là hằng số. Vì vậy
  $r(t)\to|v_\theta(a,1)-a|^2+\E|X_0|^2\ \ge\ d$.
- Tử số: $\varepsilon_t\Delta(Z_t)=\varepsilon_tv_\theta(Z_t)-(a-Z_t)\to Z_1-a$, nên
  $\varepsilon^2m\to\E|Z_1-a|^2$. Đại lượng này dương vì Prop. `regular`(a) cho $Z_1$ không có atom.

**Ý nghĩa.** Với một velocity network chính quy, training loss tại $t\to1$ không thể nhỏ hơn $d$:
không network nào khớp được target ngẫu nhiên tại $t=1$. Ngoài ra $\hat x_\theta=x+\varepsilon
v_\theta$ có Jacobian dần về $I$, tức $\mu\to1$, đúng trường hợp biên. Đây là cơ chế tổng quát đằng
sau Prop. `loss-no-certificate`.

**Đối chiếu với EXP-B** ($d=2$, $h=0$; K là trung vị theo điều kiện rồi trung bình theo seed, còn
$\|Z_T-a\|$ là RMS, nên chỉ so được gần đúng):

| checkpoint | dự đoán (cận trên) $\|Z_T-a\|^2/d$ | đo $(1-t)^2K$ tại $10^{-3}$ | tại $10^{-4}$ |
|---|---|---|---|
| 1000 | 0.94 | 0.84 | 0.84 |
| 10000 | 0.90 | 0.81 | 0.81 |
| 30000 | 0.82 | 0.74 | 0.73 |
| 100000 | 0.37 | 0.38 | 0.36 |
| 200000 | 0.20 | 0.21 | 0.20 |

Như vậy $(1-t)^2K$ ổn định ở hai thập phân cuối và nằm ở cận trên hoặc ngay dưới đó, tức
$v_\theta(a,1)\approx a$. Điều này giải thích các số mũ cục bộ 1.8 và 2.0 đã báo trong App. C.4.

## 7. Nhận xét 5 — positive bandwidth và hiện tượng đổi atom

Bổ đề 1 vẫn đúng ở $h>0$. Nhưng exact data prediction có Jacobian
$\partial_xm^*=\beta_t\operatorname{Cov}(\text{posterior})$ với $\beta_t=t/\varepsilon_t^2$. Đại
lượng này rất lớn ở thời điểm trung gian khi quỹ đạo đi gần một tie (chính là $\beta\operatorname{tr}\operatorname{Cov}$
trong `exp_c_cifar_transfer.py`). Network xấp xỉ $m^*$ nên thừa hưởng $\mu\gg1$ ở đó. Hệ quả:

- Một sai số nhỏ khi đi qua gần tie có thể đổi atom mà quỹ đạo chọn. Bound khi đó vô dụng; ví dụ
  2D cho đúng điều này, bound $10^5$–$10^{36}$ khi Y và Z kết thúc khác atom.
- Điều này khớp với S10: AUC đã cao từ $t\approx0.5$, và learned cùng exact chỉ ra cùng ảnh ở
  23–67% mẫu on-atom.
- Sau khi đã vào basin của một atom, $\partial_xm^*\to0$. Quỹ đạo kết thúc on-atom hay off-atom
  tùy vào việc $\mu$ của network ở cuối nhỏ hơn 1 hay xấp xỉ 1.

**Vấn đề mở** (đây mới là thứ làm W2 thành toàn cục): chặn xác suất đổi basin theo training error
và hình học tie, rồi ghép với Hệ quả 2 trong từng basin.

## 8. Dự đoán kiểm được trên server

Tính $\mu$ dọc quỹ đạo learned bằng power iteration trên JVP của phần đối xứng của Jacobian
denoiser, chỉ vài chục lần forward mỗi điểm. Đo trên N3/EDM hoặc checkpoint S10 nếu còn.

1. Mẫu on-atom có $\mu<1$ ở cuối; mẫu off-atom có $\mu\approx1$.
2. Với EDM: $D=c_{\rm skip}x+c_{\rm out}F$ và $c_{\rm skip}\to1$ khi $\sigma\to0$, nên $\mu\to1$
   theo cấu trúc. Model public generalise, nên không mẫu nào on-atom (đã thấy ở N3 bước 1). Model
   train trên tập nhỏ, nếu copy, phải có $\mu<1$ ở $\sigma$ trung bình.
3. Thời điểm đổi atom trùng với lúc $\mu\gg1$, tức lúc đi gần tie.

## 8b. Kết quả kiểm chứng đối kháng (11/11/2026, skill math-olympiad)

Mỗi verifier là một agent mới. Nó chỉ thấy phát biểu và chứng minh đã làm sạch, không thấy lập
luận của người viết hay phiếu của verifier khác. Ngưỡng: 4 phiếu CORRECT để xác nhận, 2 lỗ hổng để
bác. Các agent dùng nhiều kiểu tấn công: tổng quát, pattern #40 (bước một dòng), "chứng minh quá
nhiều", và kiểm tra liên tiếp.

| Mệnh đề | Kết quả | Ghi chú |
|---|---|---|
| Bổ đề 1 | 4/4 CORRECT | Không cần đạo hàm Dini: $|D|$ Lipschitz địa phương, bất đẳng thức đúng h.k.n. là đủ |
| Hệ quả 2, bản đầu | 3/3 tìm ra lỗ hổng | Thiếu giả thiết $\E|Z_{t_1}|^2<\infty$; có phản ví dụ |
| Hệ quả 2, bản 2 | 3/3 tìm ra lỗ hổng nhỏ | Phép chia trường hợp thiếu một trường hợp; claim vẫn đúng |
| Hệ quả 2, bản 3 (hiện tại) | 4/4 CORRECT | Ghi rõ "sắc" cần $c\neq0$ |
| Mệnh đề 3 | 4/4 CORRECT | Nên đổi tên nghiệm thứ hai (đang trùng ký hiệu $Z'$ với đạo hàm) |
| Mệnh đề 4 | 4/4 CORRECT | Giả thiết $|v(0,t)|$ khả tích là thừa khi đã có tăng trưởng tuyến tính; hội tụ $Z_t\to Z_1$ là tự động |

Verifier chỉ kiểm tra **tính đúng**, không đánh giá novelty hay mức độ phù hợp với network thật.
Tác giả vẫn cần tự kiểm lại trước khi đưa vào bài.

## 9. Đóng góp và rủi ro novelty

- **Thêm vào bài:** một chứng thực từ training loss (trả lời W1), một ngưỡng sắc $\mu=1$ (tổng quát
  hóa Prop. `regular`(b)), và một kết quả định lượng giải thích EXP-B ($K\asymp(1-t)^{-2}$ với hằng
  số tính được). Quan sát của S10 có một cơ chế. Positive bandwidth vẫn chưa toàn cục (W2 còn mở
  một nửa).
- **Rủi ro:** ước lượng kiểu Grönwall / one-sided Lipschitz cho ODE sampler đã có (Benton et al.
  2024, đã có trong `refs.bib`). Phần mới phải nằm ở ba điểm: ngưỡng ở dạng data prediction đúng
  bằng 1; vật cản $r(1)\ge d$; và hằng số của $K$. Cần đối chiếu với công trình về Jacobian của
  denoiser đang generalise (ví dụ Kadkhodaie et al. 2024; cần kiểm tra trích dẫn trước khi dùng).
- **Việc tiếp:** tác giả kiểm lại Bổ đề 1 (bổ đề so sánh với đạo hàm Dini), Hệ quả 2 và Mệnh đề 4
  (điều kiện hội tụ trội). Sau đó chạy dự đoán 1–2 trên server.
