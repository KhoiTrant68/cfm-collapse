# Bộ ký hiệu chung cho Paper A (theory) và Paper B (mechanism): bản chốt

Chốt ngày 2026-11-25. Mỗi chữ thay thế trong bảng đã được kiểm tra bằng regex trên `paper_theory/main.tex` và
`paper_mechanism/main.tex` (bỏ qua comment) để chắc rằng nó chưa mang nghĩa nào khác ở cùng chỗ.
Bảng này là **spec** cho mọi chỉnh sửa sau; agent nào sửa tex cũng phải theo nó.

## 1. Quy tắc

1. **Ký hiệu toàn cục** (mục 2) có cùng một nghĩa ở cả hai paper, ở cả main text lẫn appendix.
2. **Ký hiệu cục bộ** trong proof phải được khai báo ở dòng đầu proof, và không trùng với ký hiệu toàn cục.
3. **Dấu sao trên** (`v^\star`, `m^\star`) chỉ đánh dấu đối tượng của exact field. **Dấu sao dưới**
   (`\xi_\star`, `\zeta_\star`, `i_\star`, `t_\star`) đánh dấu một điểm hoặc chỉ số đặc biệt.
4. Trong phát biểu ở main text, `\delta` chỉ dùng cho Dirac. Trong proof, `\delta` được dùng làm hằng số cục bộ
   nếu đã khai báo.
5. Đặt `\varepsilon := 1-t` ở Section 3 của cả hai paper (macro `\eps` đã có sẵn) và dùng ở **mọi chỗ**.
   Hiện còn 102 lần `(1-t)` ở A và 66 lần ở B.
6. Mỗi khái niệm chỉ có một tên gọi bằng chữ (mục 4).

## 2. Ký hiệu toàn cục

| Đối tượng | Ký hiệu chốt | Ghi chú |
|---|---|---|
| Training set | `\D=\{(x^i,y^i)\}_{i=1}^N`, `d`, `k` | Chỉ dùng trong định nghĩa |
| Atom | `a_i := x^i`, tập `\mathcal A=\{a_1,\dots,a_N\}` | Dùng trong **mọi công thức** của cả hai paper. Appendix A đã dùng `a_j` (208 lần); main text đổi `x^i → a_i` (A 102, B 54). Label vẫn là `y^i` |
| Empirical law, source | `\widehat\rho_X`, `\pi_0=\N(0,I_d)` | giữ nguyên |
| Thời gian | `t`, `\varepsilon=1-t`, `\tau=-\log\varepsilon` | |
| EDM noise level | `\sigma`, `t=1/(1+\sigma)` | `\sigma` chỉ mang hai nghĩa này và `\sigma_{\rm obs}` |
| Label noise | `h`, `\omega\sim\N(0,I_k)`, `\widetilde Y=Y+h\omega` | `\omega` chỉ có nghĩa này |
| Label weight | `p_i^{(h)}(y)` (macro `\pih`) | giữ nguyên |
| Prior / tập prior dương | `p\in\Ppos` | giữ nguyên |
| Posterior weight | `q_{p,i}(x,t)`; `q^{(h)}_i := q_{p^{(h)}(y),i}` | A: `w_i^{(h)}`, `\tilde w_i`, `w_i` → `q`. B: `w_j`, `w_i(Z_t,t)` → `q` |
| Posterior mean | `m_p=\sum_i q_{p,i}a_i`; tổ hợp `\bar m`, `m_\Pi`; `m^\star:=m_{p^{(h)}(y)}` | A, proof 5.4: `\mu_c,\mu_u,\mu_w → m_c,m_u,m_w` |
| Exact field | `v_p`, `v_h^\star=v_{p^{(h)}(y)}`, `v^\star_{\rm unc}` | Khai báo quan hệ này một lần |
| Guidance | `w`, ngưỡng `w_c` | A: `w_c^{\rm spec} → w_c` (định nghĩa tổng quát lấy từ Cor 5.11) |
| Learned | `\theta` (tham số mạng), `v_\theta`, `\hat x_1`, `D_\theta`, field error `\Delta` | `\theta` chỉ có nghĩa này |
| Trajectory | exact: `x_t`; learned: `Z_t` | B dùng `x` cho EDM state, nên learned flow trajectory giữ là `Z_t` |
| Nearest atoms, candidates | `\nn(z)`, `\mathcal C\subseteq\mathcal C'` | giữ nguyên |
| Tie coordinate (1D) | `\zeta` | A: profile `s` của Thm 5.8/5.9 → `\zeta`, cùng một đối tượng với `\zeta` ở §5.5 |
| Profile (nhiều chiều) | `\xi\in L`, `M(\xi)`, `\Gamma(\xi)` | giữ nguyên |
| Swap level (B) | `s` | giữ nguyên; sau khi A bỏ `s` thì `s` chỉ còn nghĩa này |
| Relative error (B) | `\varrho_t=e_t/n_t`, `\bar\varrho`, `\varrho_{\rm crit}` | giữ nguyên; B không còn `\rho` trần nào khác ngoài `\rho=7` của EDM schedule |
| Endpoint noise (A) | bandwidth `\rho`, biến `\upsilon\sim\N(0,I_d)` | A dùng `\xi` cho biến này (dòng 1150 và App D), trùng với profile `\xi` |

## 3. Đổi tên cụ thể

| Paper | Vị trí | Cũ | Mới |
|---|---|---|---|
| A | Prop 4.3, Lemma A.2, Prop 5.2, Prop A.4 | `w_i^{(h)}`, `w_i`, `\tilde w_i` | `q^{(h)}_i`, `q_i`, `\tilde q_i` |
| A | Cor 4.5, §B | `i^\star` | `i_\star` |
| A | Thm 5.8, Prop 5.9, Fig 4, B.6 | `s`, `s_u`, `s^\star`, `F_w(s)` | `\zeta`, `\zeta_u`, `\zeta_\star`, `F_w(\zeta)` |
| A | Proof Prop 5.4(b) (cục bộ) | `\zeta=x-ta_i` | `u` |
| A | Proof Prop 5.4(a) | `\mu_c,\mu_u,\mu_w` | `m_c,m_u,m_w` |
| A | Thm 5.1 sketch | `V` | `\Theta` |
| A | Thm 5.10 sketch, B.7, E.2 | fast time `\sigma` | `\tilde\tau` (`d\tilde\tau=\beta\,d\tau`) |
| A | Proof 5.8(b) | barrier `\theta(\tau)` | `b_0(\tau)` |
| A | Threshold law (B.6), cục bộ | `\sigma`, `\theta`, `\delta=w/w_c-1` | `\psi`, `\varpi`, `g` |
| A | Thm 5.8 sketch và proof | barrier width `\delta` | `\varkappa` |
| A | B.1 | `\omega=1+w`; heat time `s`; densities `p_s,q_s,\rho_s` | `w_+`; viết thẳng `\varsigma^2/2`; `\mu^p_s,\mu^q_s,\mu^w_s` |
| A | B.7 proof | `\omega_k` | `\bar q_k` |
| A | Lemma B.2, B.4, B.7 proofs | bán kính `\rho` | `r` |
| A | App D, dòng 1150 | `X_1=x^I+\rho\xi` | `X_1=a_I+\rho\upsilon` |
| A | Ở mọi chỗ | `w_c^{\rm spec}` | `w_c` |
| B | Thm 4.1 và appendix | `\omega_t`, `\omega(y,\sigma)`, `\Omega` | `\zeta_t`, `\zeta(y,\sigma)`, `\bar\zeta` |
| B | Thm 4.1(c) | `\delta_t` | `\lambda_t` |
| B | Prop 4.3 và proof | bán kính `\rho` | `r` |
| B | Proof trap (B.1) | `\rho_R` | `c_R` |
| B | §5.4, Prop B.2 | Heun `\theta_k` | `\bar\kappa_k` |
| B | §3–4 | `w_j`, `w_i(Z_t,t)` | `q_j`, `q_i(Z_t,t)` |

### 3.1 Điều chỉnh khi áp dụng ở giai đoạn 1 (đã chấp nhận)

| Paper | Spec ghi | Thực tế dùng | Lý do |
|---|---|---|---|
| A | `\tilde w_i → \tilde q_i` | `q^\varphi_i` | Prop 5.2 đã dùng `\tilde q_i(y)` cho endpoint weight |
| A | bán kính trong proof Thm 5.1 → `r` | `r_0` | Proof đó đã dùng `r` cho một điểm của simplex |
| A | bỏ heat time `s` | `s` chỉ còn làm chỉ số của `\mu^p_s`; công thức viết `\varsigma^2/2`, `O(\sqrt s) → O(\varsigma)` | Tương đương |
| A | `\varepsilon` làm bán kính (proof Lemma B.7) | **chưa xử lý**, đụng `\eps` | Sửa ở giai đoạn 3 (W5) |
| B | `\theta=(1-r)/(2r)` (Prop B.2) | `\bar\kappa` | Chính là trọng số Heun `\bar\kappa_k` |
| B | `q` cục bộ (Prop B.1(iii)) | `\varpi` | Để `q` dành cho posterior weight |
| B | `r` | vẫn mang ba nghĩa: bán kính (Prop 4.3), `r_k` (Heun), `r(t)` (Thm A.1) | Không cùng display; xem lại ở giai đoạn 2 |
| B | — | `g` có hai nghĩa ở App A và App B; `w(t)` trong Thm A.1 | Cục bộ, khác appendix; xem lại ở giai đoạn 2 |

## 4. Thuật ngữ

| Khái niệm | Dùng | Bỏ |
|---|---|---|
| Nhiễu Gauss trên label | label noise | label smoothing (A 4 chỗ, B 1 chỗ) |
| `h=0` | hard conditioning | hard label (A 15 chỗ) |
| Điểm training | training atom (theory), training image (thí nghiệm) | training point, record, khi dùng xen kẽ trong cùng một đoạn |
| Minimiser | exact field | exact optimum, population minimiser |
| Endpoint ngoài support | blend (A); off-atom (B) | non-atom endpoint (A 17 chỗ), off-atom trong A |
