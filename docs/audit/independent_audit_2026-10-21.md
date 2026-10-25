# Kiểm toán độc lập Theorem 4.7, Proposition 4.8, Theorem 4.9, Corollary 4.10 — 21/10/2026

Bản được kiểm toán: `paper/main.tex` tại `f3beed4`. Các chứng minh là của tác giả; tài liệu này là
một lượt kiểm tra **thêm**: mỗi bước được suy lại từ định nghĩa, không chép lại lập luận của paper,
rồi đối chiếu. Script `scripts/audit_composition_spectral.py` kiểm tra lại đại số bằng sympy và các
đẳng thức hình học bằng số (kết quả: `results/learned_composition_20261021/audit_checks.json`).
Script chỉ dùng để bắt lỗi hệ số và dấu; không mục nào được gắn PASS chỉ dựa trên số.

Quy ước trạng thái: **PASS** = có một phép suy luận độc lập đi tới cùng kết luận từ đúng giả thiết
đã nêu; **PASS (sửa chữ)** = như PASS, kèm một lỗi trình bày không ảnh hưởng kết luận;
**NEEDS ASSUMPTION** = cần thêm giả thiết; **FAIL** = có phản ví dụ hoặc một bước sai.

## Proof ledger

| Proof ID | Claim | Giả thiết | Bước đã kiểm | Trạng thái |
|---|---|---|---|---|
| P47-01 | $w_c=1/\sinh^2B$ là ngưỡng chính xác | $B>0$ | Đạo hàm $F_w'(0)$; dạng đóng; luật tổng phương sai | **PASS** |
| P47-02 | Basin mở của midpoint khi $w>w_c$ | $w\sinh^2B>1$ | Barrier di động; tương đương trong toạ độ $s$ | **PASS** |
| P47-03 | Basin null khi $w\le w_c$, kể cả $w=w_c$ | $w\sinh^2B\le1$ | Barrier dưới; bất đẳng thức $\kappa\min\{s^3,1\}$ | **PASS** (có chứng minh ngắn hơn, xem dưới) |
| P48-01 | Nghiệm ổn định $F(s^\star)=0$, $F'(s^\star)<0$ cho basin mở | $\lambda_k>0$, $\sum\lambda_k=1$ | Hai barrier; homeomorphism thời gian $t_1$ | **PASS** |
| P48-02 | Tập tham số mở | IFT tại $\vartheta_0$ | $\partial_sF_{\vartheta_0}(0)<0$ | **PASS** |
| P49-01 | $\Gamma(\xi_\star)\prec0\Rightarrow$ basin có phần trong | hyperbolic | Đổi biến blow-up; Lemma offtie; Lemma LP với $n_+=0$ | **PASS (sửa chữ)** |
| P49-02 | Có eigenvalue dương $\Rightarrow$ basin null | hyperbolic | Đồ thị LP codim $n_+$; hợp đếm được; kéo ngược | **PASS (sửa chữ)** |
| P49-03 | Phân loại đầy đủ | mọi profile hyperbolic; điều kiện face | Không thoát ra vô cực; tập $\omega$-giới hạn | **PASS** |
| C410-01 | Ngưỡng ma trận | $D\succ0$ trên $L$; điểm cân bằng chung | Congruence; dạng đóng 2 atom và simplex | **PASS** |
| T41 | Theorem 4.1 (positive mixtures) | $\Pi$ trên $\Ppos$ | Năng lượng $W$; $V(r)>0$ ngoài đỉnh; Lemma volume | **PASS** |
| T46 | Theorem 4.6 (schedule BV) | $w\in[0,\bar w]$, BV | Lemma signedconv; đẳng thức vết có guidance | **PASS** |
| T51 | Theorem 5.1 (transfer) | $\Delta$ khả tích | Đẳng thức $Y_t/(1-t)$; giới hạn trên đạt được | **PASS** |
| P52 | Proposition 5.2 (local transfer) | $\rho<D/2$ | Bẫy trong bóng; $T_{\max}=1$ | **PASS** |

Không có mục nào FAIL hay NEEDS ASSUMPTION. Hai lỗi trình bày (P49-01/02) và một chứng minh ngắn hơn
(P47-03) được ghi ở dưới; cả ba đều tuỳ chọn.

---

## Audit 1 — Theorem 4.7

**Trường.** Atom $\pm1$, nhãn $\pm\ell$. Tại query $y'$, log-odds của atom $1$ là
$\log K_h(y'-\ell)/K_h(y'+\ell)=[(y'+\ell)^2-(y'-\ell)^2]/(2h^2)=2y'\ell/h^2$, nên $y'=\pm u_0$ cho
log-odds $\pm2B$. Với prior log-odds $2b$, log-odds hậu nghiệm là $2b+[(x+t)^2-(x-t)^2]/(2\eps^2)=2(b+s)$,
$s=tx/\eps^2$; trung bình hậu nghiệm $\tanh(s+b)$. Vận tốc $v_p=(m_p-x)/\eps$ và các hệ số
$(\tfrac{1+w}2,\tfrac{1+w}2,-w)$ cộng lại bằng 1, nên $v_{\varphi,w}=(F_w(s)-x)/\eps$ đúng như (5). (A1)

**P47-01, hai cách.**
(i) Trực tiếp: $\tanh(s+B)+\tanh(s-B)=2\sinh2s/(\cosh2s+\cosh2B)$ và $\tanh s=\sinh2s/(\cosh2s+1)$; quy
đồng, tử số là $\sinh2s\,[2\cosh^2s-2w\sinh^2B]$, cho dạng đóng của paper (A1). Do đó
$F_w'(0)=(1-w\sinh^2B)/\cosh^2B=\operatorname{sech}^2B-w\tanh^2B=(1+w)\operatorname{sech}^2B-w$,
bằng 0 khi và chỉ khi $w=1/\sinh^2B$ (A2), và trên $s>0$ dấu của $F_w$ là dấu của
$\cosh^2s-w\sinh^2B$ (A3).
(ii) Luật tổng phương sai: tại $s=0$, prior trung bình là uniform, có phương sai $C_{\mathrm u}=1$;
mỗi thành phần có phương sai $\operatorname{sech}^2B$ và trung bình $\pm\tanh B$. Nên
$C_{\mathrm{av}}=C_{\mathrm u}-\operatorname{Var}(\text{means})=1-\tanh^2B$ và
$\Gamma_w(0)=(1+w)C_{\mathrm{av}}-wC_{\mathrm u}=1-(1+w)\tanh^2B$ (A7). Cách này giải thích câu
"averaging adds $-(1+w)$ times the variance of the component means" ở dòng 531 và cho cùng ngưỡng.

**P47-02.** Suy lại trong toạ độ $s$: từ $d\beta/d\tau=\beta(1+t)/t$ và $dx/d\tau=F_w(s)-x$,
$$\frac{ds}{d\tau}=\beta F_w(s)+\frac st .$$
Với $0<\delta<s_u$ và $\gamma=-F_w(\delta)>0$: tại $s=\delta$, $ds/d\tau=-\beta\gamma+\delta/t<0$ khi
$\beta\gamma>\delta/t$; đối xứng tại $s=-\delta$. Vậy $[-\delta,\delta]$ bất biến tiến từ thời điểm đó,
và $x=s/\beta\to0$. Điều kiện $\beta\gamma>\delta/t$ trùng với điều kiện ngoặc vuông âm của paper:
nhân ngoặc với $\beta$, dùng $\beta\eps^2/t=1$ và $\beta\eps^3/t^2=\eps/t$, được
$-\beta\gamma+\delta(1+\eps/t)=-\beta\gamma+\delta/t$ (sympy xác nhận đạo hàm barrier, A4). Kéo
ngược bằng flow map thời gian $t_1$ (homeomorphism tăng của $\R$) cho một khoảng mở chứa 0. PASS.

**P47-03.** Các bước của paper đúng: $\cosh^2s-w\sinh^2B\ge\sinh^2s$; bất đẳng thức
$F_w\ge\kappa\min\{s^3,1\}$ được kiểm trên lưới $B\in[0.05,6]$, $w\in\{0,w_c/2,w_c\}$, $s\in[10^{-4},60]$
với 60 chữ số: tỉ số nhỏ nhất là $2.00>1$ (A5); $2\tanh1\sinh^21=2.104>1$ (A6). Lập luận bẫy với
$\theta(\tau)=(\kappa\beta^3)^{-1/2}$ đúng từng bước.

*Ghi chú số học.* Ở float64, cùng kiểm tra A5 cho tỉ số $-0.69$: tại $w=w_c$ số hạng tuyến tính triệt
tiêu và $F_w\sim\kappa s^3$ nhỏ hơn sai số làm tròn của $\tanh(s+B)+\tanh(s-B)$. Đây không phải phản ví
dụ, nhưng là lý do mọi phép tính số gần ngưỡng phải dùng dạng đóng hoặc độ chính xác cao.

*Chứng minh ngắn hơn (tuỳ chọn).* Chỉ cần $F_w\ge0$ trên $[0,\infty)$, tức $w\le w_c$. Với $x_0>0$,
$x>0$ mãi mãi (0 là một quỹ đạo), $\dot x=F_w-x\ge-x$ nên $x(\tau)\ge x_0e^{-\tau}$, và
$\beta=e^{2\tau}-e^\tau$ cho $s=\beta x\ge x_0(e^\tau-1)\to\infty$. Khi đó $F_w(s(\tau))\to1$ và
$x(\tau)=e^{-(\tau-\tau_1)}x(\tau_1)+\int_{\tau_1}^\tau e^{-(\tau-\sigma)}F_w(s(\sigma))\,d\sigma\to1$.
Không cần cận bậc ba, không cần $\theta(\tau)$, và cũng không cần Lemma signedconv cho phần (b). Cùng
lập luận rút gọn Step 3 của Proposition 4.3 ($\dot\zeta\ge-\zeta$ nên $\beta\zeta\to\infty$).
Ở phần (a) cũng có thể tránh Lemma signedconv: nếu $s$ vượt $s_u$ thì $ds/d\tau>0$ mãi, nên $s\to\infty$
và $x\to1$; nếu không, $|s|\le s_u$ mãi và $x=s/\beta\to0$.

## Proposition 4.8

Các barrier $b_\pm=c_\pm\eps^2/t$ thoả $v(b_\pm,t)-b_\pm'=\eps^{-1}[F(c_\pm)+c_\pm(\eps^2/t+\eps^3/t^2)]$
với mọi dấu của $c_\pm$ (A4 với $F(c)$ tổng quát). Ngoặc vuông tiến tới $F(c_\pm)$, có dấu ngược nhau,
nên dải giữa hai barrier bất biến tiến từ $t_1$. IFT tại $\vartheta_0=(\tfrac12,B,-B,0,w)$ dùng
$\partial_sF_{\vartheta_0}(0)=\operatorname{sech}^2B-w\tanh^2B<0$, đúng với A2. PASS.

## Audit 2 — Theorem 4.9

**Bước A — đổi biến.** Từ $\xi=\beta P_L(x-tz)$, $d\beta/d\tau=\beta(1+t)/t$, $dt/d\tau=\eps$:
$$\frac{d\xi}{d\tau}=\frac{\xi}t+\beta P_L(\bar m-z),\qquad
\frac{d\xi}{d\sigma}=\frac{\eps^2}{t^2}\xi+P_L(\bar m-M(\xi))+G(\xi),$$
vì $1/(t\beta)=\eps^2/t^2$ và $M(\xi)-z\in L$. Phương trình chuẩn $d\eta/d\tau=-\eta+P_{L^\perp}(\bar m-z)$.
Cả hai khớp phương trình `eq:pf:spec:blowup` của paper; kiểm bằng số trên một cấu hình ngẫu nhiên $d=4$, $\dim L=2$, ba atom bị
tie, ba atom ngoài, ba prior với hệ số có dấu: sai số tương đối $4\times10^{-16}$ (B1, B2). Logit của
Lemma offtie: $8\times10^{-16}$ (B3). $\Gamma=D_LM=\sum_kc_k\Cov_{\pi_k}(P_La)$ và $\nabla_L\Psi=G$
khớp sai phân hữu hạn (B6, B7).

*Lỗi chữ 1 (dòng 1754).* Paper viết $x-z=\beta^{-1}\xi+\eps P_{L^\perp}z-\eps P_Lz+\eta$. Từ
$x=tz+\beta^{-1}\xi+\eps P_{L^\perp}z+\eta$ ta có
$$x-z=\beta^{-1}\xi-\eps P_Lz+\eta ,$$
không có số hạng $+\eps P_{L^\perp}z$ (B4 đúng tới $2\times10^{-16}$; dạng in trong paper sai tới $1.18$,
B5). Kết luận không đổi: cả hai vế tiến về 0, nên "basin = các điểm có $(y,\eta)\to0$" vẫn đúng.

**Bước B — giả thiết của Lemma LP.** Với $f=N+\mathcal R(\xi_\star+\cdot)$, $g=\mathcal E(\xi_\star+\cdot)$:
$|DN|$ nhỏ gần 0; $D_y\mathcal R$ gồm $\eps^2/t^2\to0$ và phần off-tie $O(e^{-c\beta})$; $D_\eta\mathcal R$
và $D_\eta\mathcal E$ là $O(\beta e^{-c\beta})$ vì logit off-tie phụ thuộc $\eta$ qua
$\beta\langle\eta,a_j-a_i\rangle$, còn logit trong $S$ không phụ thuộc $\eta$ (vì $a_i-a_{i'}\in L$).
Hệ số $\beta$ trước $f$ đã nằm trong nhân $\int e^{-a\int\beta}\beta\,ds\le a^{-1}$, nên hằng số co
$\le C\delta\max\{a^{-1},1\}$ không phụ thuộc thời điểm bắt đầu $T'$. Cutoff: $|D(\chi f)|\le C\varepsilon^{-1}
\sup|f|+|Df|\le C\delta$. Ánh xạ LP giữ lớp hàm bị chặn tiến về 0. Đúng.

*Lỗi chữ 2 (Lemma LP).* Phát biểu nói về các trạng thái "trong $\varepsilon$-ball" ở lại trong đó, nhưng
chứng minh chỉ đặc trưng nghiệm ở lại trong $\varepsilon/2$-ball (nơi cutoff bằng 1). Sửa: đổi tên
$\varepsilon/2$ thành $\varepsilon$ trong phát biểu. Không ảnh hưởng (a), (b): mọi quỹ đạo hội tụ cuối
cùng nằm trong bóng nhỏ hơn bất kỳ.

**Bước C — codimension và kéo ngược.** Fixed point cho $y_u(T')=\Psi_{T'}(y_s(T'),\eta(T'))$, đồ thị
trên $L^s\times\R^n$, codim $=\dim L^u=n_+$. (a) $n_+=0$: mọi $(y,\eta)$ nhỏ tại $T$ hội tụ; ảnh ngược
qua ánh xạ affine $x\mapsto(\xi,\eta)$ (song ánh ở thời gian cố định) và flow map (diffeomorphism
$C^1$) là tập mở khác rỗng. (b) $n_+\ge1$: basin nằm trong hợp đếm được (theo $T'$ nguyên) các đồ thị
codim dương, nên null; diffeomorphism $C^1$ giữ tập null. Ghi chú độ bền: (b) chỉ cần đồ thị
Lipschitz, điều có ngay từ tính co với hằng số Lipschitz đều; tính $C^1$ không cần cho kết luận null.

**Bước D — phần (c).** $P_La_j$ khác nhau và affine-span $P_Lz+L$, nên mọi $v\in L$ đơn vị không hằng
trên $\{b_j\}$ và $F(v)$ là face thật sự. Khi $\xi_n/|\xi_n|\to v$, trọng số ngoài $F(v)$ tiến về 0
với tốc độ $e^{-c|\xi_n|}$; tổ hợp affine (hệ số có dấu, tổng 1) các điểm gần $\operatorname{conv}F(v)$
có điểm tụ trong $\operatorname{aff}F(v)$. Lập luận compact cho $\liminf|G|\ge2\delta_0$. Thế năng $\Psi$
Lipschitz, $\nabla_L\Psi=G$; mỗi chuyến ra ngoài $B_{R_0}$ rồi quay lại kéo dài tối đa
$(\max\Psi-\min\Psi)/c_0$; nếu $\xi$ không bị chặn thì nó ở ngoài từ một lúc, khi đó
$\Psi\ge c_0\sigma-O(1)$, mâu thuẫn với $|\Psi|\le C(1+|\xi|)=o(\sigma)$. Sau đó
$\int|\mathcal R|^2d\sigma=\int O(\beta^{-2})\beta\,d\tau<\infty$, $\int|G|^2d\sigma<\infty$,
Barbalat cho $G\to0$, và tập $\omega$-giới hạn liên thông nằm trong tập hữu hạn các profile. Đúng.

## Corollary 4.10

$\Gamma_w=(1+w)C_{\mathrm{av}}-wC_{\mathrm u}=C_{\mathrm{av}}-wD$; congruence bởi $D^{-1/2}$ cho
$\Gamma_w\prec0\iff w>\lambda_{\max}(D^{-1/2}C_{\mathrm{av}}D^{-1/2})$. Hai atom: $\operatorname{sech}^2B/
\tanh^2B=1/\sinh^2B$ (C2). Simplex đều, $N=2,\dots,9$, $B\in\{0.3,1,2,4\}$: ngưỡng tính bằng ma trận khớp
$(1-m^2)/m^2$ và trung bình các thành phần bằng 0, sai số $2\times10^{-13}$ (C1). Với $N=2$ công thức
cho $1/\sinh^2(B/2)$, nhất quán với Theorem 4.7 vì prior $e^{B\,\mathbb 1\{j=k\}}$ có log-odds $B$ chứ
không phải $2B$. Lưu ý phạm vi: corollary là điều kiện **đủ**; với $w<w_c^{\mathrm{spec}}$ profile
$\xi_\star$ có basin null nhưng profile khác vẫn có thể là sink. Paper không nói ngược lại.

## Các mục P1

- **Theorem 4.1.** $\dot W=-|\dot x|^2+\dot\alpha\int D_{\mathrm{KL}}+\tfrac\eps2(\int\sum q|a|^2-R^2)\le
  -|\dot x|^2$ và $W\ge\min_j\{\tfrac12|x-a_j|^2+\tfrac\eps2(R^2-|a_j|^2)\}\ge0$: suy lại được. $V(r)=0$
  đúng tại đỉnh vì $Q_p(r)$ cùng support với $r$; thời điểm "tốt" chiếm ít nhất nửa mỗi đoạn. PASS.
- **Theorem 4.6.** Đẳng thức $|(1+w)u-wv|^2=(1+w)|u|^2-w|v|^2+w(1+w)|u-v|^2$ (A8);
  $\Theta\ge r^2-|\mu_w|^2-\bar we_{p_u}$; $\int_n^{n+1}\beta\Theta\ge\tfrac12r^2\beta(n)$. Năng lượng
  của Lemma signedconv: tích phân từng phần với $c_k$ BV, $|r_k|\le\tfrac12R^2\eps+\log(1/p_{\min})|\dot\alpha|$. PASS.
- **Theorem 5.1, Proposition 5.2.** $\tfrac d{dt}\tfrac{Y_t}{1-t}=\tfrac{\Delta}{1-t}$; cận
  $(1-t)\int_{t_0}^t(1-s)^{-2}ds\le1$; $|Z_t-a|<3\rho/4$ trước lần thoát đầu tiên. PASS.

## Audit 3 — trường hợp biên

| Trường hợp | Kết luận |
|---|---|
| Prior gần một đỉnh simplex | Theorem 4.1 dùng cận KL thứ nhất, không phụ thuộc $\min_jp_j$, nên $\Pi$ được phép tích tụ gần biên. Lemma signedconv và Theorem 4.9 cần hữu hạn prior cố định trong $\Ppos$; hằng số $\log(1/p_{\min})$ nổ khi $p_{\min}\to0$, và nhãn cứng ($p=e_i$) được xử lý riêng ở Prop. 4.4(b). Đã nêu trong giả thiết. |
| Tập tie bằng toàn bộ tập train | Không có atom ngoài $S$: $\mathcal E=0$, $\mathcal R=\eps^2\xi/t^2$, Lemma offtie tầm thường. Đây chính là các cấu hình của Section 6.2. |
| Eigenvalue bằng 0 / profile không hyperbolic | Bị loại khỏi Theorem 4.9 và nêu là câu hỏi mở (dòng 623, Limitations). Trong 1D, $w=w_c$ được Theorem 4.7(b) xử lý riêng. |
| Ứng viên gần biên Voronoi | Ứng viên là tie **chính xác**; near-tie không phải ứng viên, và Lemma conv đưa giới hạn về $\mathcal C'$. Hệ quả thực tế là quá độ dài (Section 6.2, hình giữa), không phải lỗ hổng. |
| Nguồn nằm trên stable manifold | Thuộc đồ thị LP, hội tụ về $z$, là tập null khi $n_+\ge1$; nhất quán với (b). |
| Guidance tiến tới ngưỡng | Corollary 4.10 dùng bất đẳng thức chặt; tại đẳng thức $\Gamma_w$ suy biến nên ngoài phạm vi. |
| Điều kiện face không thoả | Ví dụ: bốn atom trên một đường tròn quanh $z$ trong $\R^2$, hai atom đối tâm và hai atom còn lại cùng một phía. Đường kính là một cạnh của bao lồi và $z$ nằm trên affine hull của nó, nên profile có thể thoát theo pháp tuyến của cạnh đó. Theorem 4.9(c) không áp dụng; paper đã nêu là mở. |

## Đề xuất sửa (tuỳ chọn, không thay đổi kết luận)

1. Dòng 1754: thay $\beta^{-1}\xi+\eps P_{L^\perp}z-\eps P_Lz+\eta$ bằng $\beta^{-1}\xi-\eps P_Lz+\eta$.
2. Lemma LP: thống nhất $\varepsilon$ và $\varepsilon/2$ giữa phát biểu và chứng minh.
3. Theorem 4.7(b), Step 4: có thể thay bằng chứng minh ba dòng ở trên ($s\ge x_0(e^\tau-1)$). Tiết kiệm
   khoảng 20 dòng appendix và bỏ hằng số $\kappa$.
