# Review trình bày: Paper A (TMLR) và Paper B

Ngày 2026-11-25. Đọc từ `submit/pdf/A_tmlr.pdf` (62 trang) và `submit/pdf/B_neurips.pdf` (37 trang), build cùng ngày.
Phạm vi: trình bày, ký hiệu, figure, cấu trúc chứng minh. Bản review này **không** đánh giá tính đúng của các
chứng minh và không chạy panel 5 reviewer của ARS. Đây là góc nhìn của một reviewer duy nhất, theo yêu cầu.
Bộ ký hiệu đề xuất nằm ở [docs/notation/shared_notation.md](../../notation/shared_notation.md).

---

## 0. Ấn tượng chung (giọng reviewer)

> Đây là paper thứ 11 tôi đọc hôm nay. Đến trang 4 của Paper A, tôi đã gặp 6 contribution, mỗi cái 6 dòng; một
> đoạn "Technique" tóm tắt chứng minh; và một đoạn "What this means in practice" dài 35 dòng, nhồi bốn ý (i)–(iv)
> vào một khối chữ. Đến trang 8, cùng cái proof template đó được kể lại lần thứ hai, trang 9 có thêm flowchart,
> trang 27 có Table 4, Appendix B.3 kể lần thứ tư. Tôi hiểu template rồi. Cái tôi chưa hiểu là **kết quả nào
> mới thật sự quan trọng**, vì Section 4–5 có 20 statement được đánh số (Proposition, Corollary, Theorem,
> Remark), và cứ hai statement lại có một statement chỉ là trường hợp đặc biệt của statement khác.
>
> Trang 11–21 là chỗ tôi bắt đầu đọc lướt. Section 7 là báo cáo thí nghiệm viết bằng văn xuôi: "0.401±0.006
> against 0.406 at B=1 and w=2w_c, and 0.143±0.004 against 0.133...". Một đoạn có 15 con số mà không có câu kết
> luận nào ở đầu. Tôi phải tự làm cái bảng mà lẽ ra tác giả phải làm. Đoạn "The stress test cannot see an
> attracting tie" dài gần một trang để nói rằng RK4 hỏng ở gần điểm tie. Chuyện đó thuộc về appendix.
>
> Ký hiệu thì mỗi chỗ một kiểu: `w` vừa là guidance vừa là posterior weight, `\omega` có ba nghĩa, `s` có bốn
> nghĩa, `\sigma` là noise level ở Paper B nhưng lại là fast time ở Appendix B.7 của Paper A. Main text viết
> `x^i`, appendix chuyển sang `a_j`. Hai paper được nộp như "companion" mà Paper B gọi posterior mean là `m^\star`,
> còn Paper A gọi là `m_p`, `\bar m`, `m_\Pi`, `\mu_c`.
>
> Phần toán có thể đúng. Nhưng nếu tôi phải tự xây lại bảng ký hiệu thì tôi sẽ không kiểm proof. Tôi sẽ viết
> "hard to follow" rồi chấm Major Revision.

Các mục dưới đây là danh sách việc cần làm, xếp theo thứ tự nên làm.

---

## 1. Layout, font, ký hiệu

### 1.1 Font (cả hai paper)

**Bằng chứng.** `pdffonts` của A cho thấy ba họ font cùng lúc: thân bài và math dùng Latin Modern; figure
matplotlib dùng Nimbus Sans TT; ký tự nào Nimbus không có thì rơi xuống **STIXGeneral** (do
`mathtext.fallback: stixsans` trong `scripts/figstyle.py:104-107`). Hệ quả thấy được ngay khi đọc:

- Math trong figure là sans italic (Fig 4 trục y: `s = tx/(1-t)^2`, Fig 4(b) `P_0 ≃ √(2/π)…`; Fig 6 trục x),
  còn math ở caption và thân bài là serif. Cùng một biểu thức nhưng trông như hai ký hiệu khác nhau.
- Các glyph `√`, `≈`, `↓`, `≤` lấy từ STIX lại có nét khác Nimbus ngay trong cùng một nhãn.
- TikZ (Fig 1 và Fig 3 của A, Fig 1 của B) dùng chữ sans nhưng math là LM serif. Còn matplotlib thì cả chữ lẫn
  math đều là sans. Hai loại figure đặt cạnh nhau nhìn như của hai nhóm khác nhau.

**Sửa.** Chọn một trong hai cách, áp cho **mọi** figure:
1. (khuyến nghị) Chữ trong figure dùng sans, **math dùng Computer Modern/LM**: `mathtext.fontset = "cm"` và bỏ
   fallback stixsans. Như vậy math trong figure khớp với thân bài. Trong TikZ, giữ math mặc định (LM).
2. Hoặc dùng `text.usetex=True` với `lmodern`, để toàn bộ figure dùng LM.

Kèm theo đó: chữ nhỏ nhất trong figure sau khi scale không dưới 7pt. Hiện các nhãn ở thanh % của Fig 2 (A),
hàng chữ "fields at the tie" của Fig 5(a) (A) và trục của Fig 6(b) (B) chỉ khoảng 5pt.

### 1.2 Ký hiệu

Xem [shared_notation.md](../../notation/shared_notation.md). Các xung đột nặng nhất:

| Ký hiệu | Số nghĩa | Ví dụ gây nhầm cho reviewer |
|---|---|---|
| `w` | 2 | Prop 4.3 (A) `w_i^{(h)}` ngay trước Section 5, nơi `w` là guidance |
| `\omega` | 3 | label noise (§3) và `\omega=1+w` (B.1, A); `\omega_t` (B, Thm 4.1) |
| `s` | 4 | profile (A, Thm 5.8), heat time (A, B.1), swap level (B), biến tích phân |
| `\sigma` | 3 | EDM noise (B), fast time (A, B.7), `\sigma_{\rm obs}` |
| `\delta` | 4 | Dirac, barrier, `w/w_c-1`, `\delta_t` |
| `\theta` | 3 | tham số mạng `v_\theta`, barrier `\theta(\tau)` (proof 5.8), hệ số Heun `\theta_k` |
| atom | 2 | `x^i` (main text) và `a_j` (appendix B) |
| posterior mean | 6 | `m_p, \bar m, m_\Pi, \mu_c, M(\xi)` (A); `m^\star` (B) |

Còn hai việc nữa:
- `\varepsilon = 1-t` chỉ được định nghĩa ở Appendix B.2, nhưng main text đầy `(1-t)^2` và `tx/(1-t)^2`. Đưa
  định nghĩa lên Section 3 sẽ làm gọn hàng chục công thức.
- Table 3 (bảng notation) nằm ở trang 26, sau references. Hãy chuyển một bảng ngắn khoảng 12 dòng vào cuối
  Section 3, và giữ bảng đầy đủ ở appendix.

### 1.3 Lỗi layout nhỏ

- B: header vẫn là "Under review as submission to TMLR" dù đích nộp là NeurIPS. Ghi chú trong build đã nói rõ
  lý do, nhưng nhớ đổi khi có `neurips_2027.sty`.
- A, trang 7: phát biểu Prop 4.1 bị ngắt dòng ngay giữa `\E[U \mid X_t, t, \widetilde Y]`. Biểu thức này phải
  đưa ra display.
- A, trang 13: tiêu đề "Remark 5.12" in nghiêng, nhưng nội dung là một chứng minh transversality hoàn chỉnh
  (xem mục 4).
- Hai paper mô tả việc dùng LLM theo cách khác nhau: A ghi "all statements and proofs are the authors' own",
  còn B (trang 17) ghi rằng bản nháp đầu của proof Thm 4.1, Prop B.1, B.2 "came from model-based solver runs".
  Hai submission của cùng một nhóm mà nói khác nhau thì reviewer sẽ để ý. Hãy kiểm tra câu nào đúng với thực
  tế rồi viết cho thống nhất.

---

## 2. Văn bản: quá dài, thiếu kết luận

### 2.1 Quy tắc áp dụng cho mọi đoạn

1. **Câu đầu tiên là kết luận** (claim), các câu sau là bằng chứng. Hiện nhiều đoạn làm ngược lại hoặc không
   có kết luận.
2. Đoạn nào có từ 4 con số trở lên thì chuyển số vào **bảng**. Văn bản chỉ giữ con số quan trọng nhất kèm so
   sánh ("learned ≈ exact: 0.40 vs 0.41").
3. Đoạn dài quá 12 dòng thì cắt ra, hoặc chuyển thành list.
4. Mỗi section kết thúc bằng một câu "Takeaway".

### 2.2 Paper A, trang 1–5 (phần mở đầu)

| Vị trí | Vấn đề | Sửa |
|---|---|---|
| Abstract (21 câu) | Gần như liệt kê toàn bộ kết quả, có cả công thức `w>1/\sinh^2B`, `(1-t)^2` | Viết lại còn khoảng 150 từ: câu hỏi → 3 kết quả (two fields keep, three fields blend, sign rule) → ý nghĩa với learned samplers |
| Contributions (trang 3, 6 mục × ~6 dòng) | Đọc như một bản tóm tắt thứ hai của paper | Gộp còn 4 mục, mỗi mục ≤ 2 dòng, cuối mỗi mục trỏ tới theorem |
| "Technique" (trang 4) | Lặp lại proof template | Xóa; một câu trỏ tới §5 là đủ |
| "What this means in practice" (trang 4–5, ~35 dòng) | Bốn ý (i)–(iv) chạy liền trong một khối chữ | Thành list 4 bullet, mỗi bullet có một câu in đậm kết luận và 2 dòng giải thích |

### 2.3 Paper A, trang 11–21

| Trang | Đoạn | Vấn đề | Sửa |
|---|---|---|---|
| 12 | Sau Prop 5.9 (14 dòng) | Giải thích vì sao "generalised family" và chuyển tiếp sang §5.4 | Giữ 3 dòng; phần "atoms stay at {−1,1}" đưa vào phát biểu |
| 13–14 | Remark 5.12 (~25 dòng) | Là một chứng minh (submersion, parametric transversality) nằm trong main text | Chuyển vào Appendix B.7; main text chỉ giữ một câu: "Nonhyperbolic profiles are non-generic in the priors (App. B.7)" |
| 14 | "Which combinations blend two examples" | Định nghĩa `B(p)` và `F(\zeta)` bằng văn xuôi | Đưa vào display có đánh số, giới thiệu bằng một câu |
| 15 | Sau Prop 5.13 (~20 dòng) | Diễn giải luật dấu bằng lời: "intermediate is not the same as less decided…" | Thay bằng một **bảng luật dấu** (recipe → dấu của field trung gian → blend có thể xảy ra không?). Figure 5(a) đã gần như là bảng đó; văn bản giữ ≤ 4 dòng |
| 15 | §5.6 "What leaves the support" | Lặp lại Table 1 | Xóa section này |
| 16 | Sau Prop 6.1 (~14 dòng) | Ví dụ `H(x)=\tanh x+2\tanh^3x` dày đặc | Chuyển ví dụ vào Appendix C; giữ một câu kết luận "matching requires Lipschitz ≳ (1−t)^{-2}" |
| 17 | "Exact fields" | 10 con số, không có câu claim | Một câu claim, các con số đưa vào bảng ở appendix |
| 17–18 | "The stress test cannot see an attracting tie" (~25 dòng) | Câu chuyện về lỗi số của RK4; đó là chi tiết phương pháp | Chuyển sang Appendix E.2. Main text giữ: "Fixed-step RK4 does not detect attracting ties; every reported basin uses a stiff solver with proof-based stopping (Alg. X)" |
| 18 | "Guided label averaging" | Cách tính và các con số trộn vào nhau | Phần cách tính → **Algorithm** (pseudocode, mục 4.4); phần kết quả → một câu kèm Fig 4(b) |
| 18 | "Learned guided label averaging" (~25 dòng) | Khoảng 20 con số | **Bảng** gồm các cột: config × {exact, std CFM, data-pred, data-pred + asinh input}; văn bản chỉ còn 3 câu kết luận |
| 18–19 | "The spectral criterion beyond the line" | Khoảng 25 con số | Bảng rút gọn của Table 8 đưa vào main text; văn bản: "the classification agrees in all 4 configurations" |
| 19 | "Signed combinations" | Số liệu đã có trong Fig 5 | Giữ ≤ 4 dòng |
| 20 | Table 2 và "Learned label averages" | Kết quả yếu, có chú thích "not hypothesis tests" | Chuyển cả hai sang appendix |
| 20 | Limitations: một đoạn duy nhất, các tiêu đề in nghiêng nằm ngay trong dòng | Rất khó tìm ý | List theo nhóm (Theory scope, Numerics, Learned networks), mỗi ý 1–2 dòng |

Ước tính: phần trang 11–21 giảm được khoảng 3 trang. Main text từ 21 trang xuống còn khoảng 15–16 trang mà
không mất kết quả nào.

### 2.4 Paper B

Paper B dễ đọc hơn A (có Fig 1–3 để dẫn dắt), nhưng mắc cùng một bệnh ở Section 5:

| Trang | Đoạn | Sửa |
|---|---|---|
| 2–4 | Contributions (5 bullet dài, bullet 2 có công thức) | Mỗi bullet ≤ 2 dòng |
| 4–6 | Related work (2,5 trang) | Rút còn khoảng 1,5 trang; "Late landing" và "Where memorisation arises" có thể gộp làm một |
| 12–13 | "The reverse swap…", "A window of exact field" (~45 dòng số) | Một bảng window-swap (σ_lo, σ_hi, d₁ median, off-atom %) cùng 3 câu kết luận. Câu "Two predictions were written down before the run" nên in đậm: đây là điểm mạnh, đừng để nó chìm |
| 15 | "Not a better detector" (~25 dòng, khoảng 20 AUC) | Bảng AUC: feature × σ × model. Văn bản: "Relative error is not a better detector than nearest-image distance (Table X)" |
| 15–16 | "A certificate for the sampler" | Đưa phần Heun step vào display có đánh số |
| 10–11 | Đoạn đầu §5.2 (định nghĩa n, e, ϱ, tiêu chí on-/off-atom) | Đưa vào một khung "Measurement protocol" hoặc Algorithm |

---

## 3. Figure

### 3.1 Phân tích hai figure mẫu trong `D:\AwesomeCV\reference`

- **figure sample 1** (inpainting, A/B/C): một figure ý tưởng (conceptual) duy nhất. Hình học được vẽ một lần
  (các vùng density, vùng thỏa constraint); ba phương pháp được phân biệt bằng **màu kèm nhãn (A)(B)(C)**; có ✓/✗
  cho hai tiêu chí; legend nằm dưới. Người đọc hiểu đóng góp chính trong khoảng 5 giây mà không cần đọc công thức.
- **figure sample 2** (steer / projection / optimization / ours): **cùng một khung hình học** (ν₀ bên trái, ν_T
  bên phải, mặt H=0) được lặp lại ở 4 panel; mỗi panel chỉ khác ở mũi tên can thiệp. Phương pháp của tác giả đặt
  cuối cùng và có viền nổi bật. Đây là dạng so sánh các can thiệp: đúng loại câu hỏi mà Paper A đặt ra.
- **mathematic sample 1/2**: câu dẫn ngắn ("Set", "Substituting … yields", "Consequently,"), display canh theo
  dấu `=`, mỗi display một mục đích, có đánh số ở bên phải, và chừa khoảng trống dọc rộng rãi.

### 3.2 Đề xuất cho Paper A

| # | Figure | Kiểu (theo mẫu) | Thay hoặc bổ sung | Nội dung |
|---|---|---|---|---|
| A-F1 | **Figure mở đầu theo kiểu sample 2** | 5 panel, cùng một khung hình học | Thay Fig 1 hiện tại (sơ đồ hộp có số theorem, đọc như mục lục) | Cùng một hình: nguồn Gauss bên trái, 3 atom bên phải. (a) exact field → atom; (b) label noise → atom, mũi tên dày mỏng tùy trọng số; (c) guidance w ≥ 0 → atom; (d) tổ hợp bất kỳ của hai field → atom; (e) conjunction ba field → **midpoint** (ngôi sao màu cam). Mỗi panel có ✓ "on training set" hoặc ✗. Panel (e) có viền nổi bật. Kéo theo Fig 2(a–c) vì cùng hình học |
| A-F2 | **Cơ chế ở điểm tie** | Kiểu sample 1, conceptual | Bổ sung trong §5.3 | Hai atom ±1 và midpoint 0. Vẽ ba trường thành phần (v₊, v₋, v_unc) dạng mũi tên 1D trên trục, cùng trường tổng hợp: với w < w_c thì mũi tên rời khỏi 0, với w > w_c thì mũi tên hướng về 0. Câu "subtract an intermediate field" trở thành một hình |
| A-F3 | **Phân loại phổ** | 3 panel schematic | Bổ sung trong §5.4 | Không gian tie span L và hướng pháp tuyến. (a) Γ ≺ 0: sink, có basin mở (vùng tô màu); (b) Γ có một trị riêng dương: saddle, basin là một đường (codim 1); (c) source: basin chỉ là một điểm. Thay cho mấy dòng văn trong proof sketch của Thm 5.10 |
| A-F4 | **Proof template** | Xem mục 5 | Xóa Fig 3 | Thay bằng một khung implication và bảng (mục 5) |
| A-F5 | **Learned vs exact** | Giữ Fig 6 | Chỉ sửa caption | Fig 6 tốt. Mở caption bằng một câu kết luận: "Only the rescaled input recovers the exact basin" |

### 3.3 Đề xuất cho Paper B

| # | Figure | Nội dung |
|---|---|---|
| B-F1 | **Hình học của landing condition** (bổ sung ngay trước Thm 4.1) | Vẽ atom a, state Z_t, exact mean m⋆, prediction x̂₁; các đoạn n_t = \|Z_t − a\|, e_t = \|x̂₁ − m⋆\|; hình chiếu xuyên tâm ⟨ê_t, x̂₁ − a⟩. Có hai trường hợp: ϱ < 1 (prediction kéo về a) và ϱ → 1 (không kéo). Theorem 4.1 hiện có 4 đại lượng chỉ được định nghĩa bằng chữ, và hình này giải quyết chuyện đó |
| B-F2 | **Gộp Fig 2 (dưới) và Fig 5(b)** | Hai hình cùng vẽ đường cong "choice/landing" theo s. Giữ một hình (Fig 5b), Fig 2 chỉ giữ phần các ô ảnh |
| B-F3 | **Swap protocol** | Fig 1 (phải) đã có. Nên thêm Algorithm (mục 4.4) thay vì một hình nữa |

### 3.4 Về scivisagent

Môi trường này **không có** tool hay plugin tên `scivisagent`. Mình đã tìm cả trong skill lẫn catalog plugin.
Có hai thứ gần nhất đang có sẵn: skill `scientific-figure-making` (matplotlib, theo house style) và
`opentikz:using-opentikz` (template TikZ). Mỗi figure A-F1…A-F3 và B-F1 ở trên có thể làm thành một task riêng
bằng TikZ (khuyến nghị cho schematic, vì chúng dùng font LM khớp thân bài) hoặc bằng matplotlib theo mục 1.1.
Nếu bạn có scivisagent ở nơi khác, hãy chỉ đường dẫn, mình sẽ dùng.

---

## 4. Chứng minh và trình bày toán

### 4.1 Quá nhiều tầng statement

Main text của A có **20 statement được đánh số** (Prop 4.1, 4.2, 4.3, Thm 4.4, Cor 4.5, Prop 4.6, Thm 5.1,
Prop 5.2, 5.3, 5.4, Cor 5.5, Thm 5.6, Cor 5.7, Thm 5.8, Prop 5.9, Thm 5.10, Cor 5.11, Rem 5.12, Prop 5.13,
Prop 6.1). Ngoài ra appendix còn khoảng 10 lemma. Nhiều statement chỉ là trường hợp đặc biệt của statement
khác, hoặc chỉ là ví dụ.

Đề xuất gộp (chỉ tái cấu trúc, không đổi nội dung toán):

| Mới | Gộp từ | Lý do |
|---|---|---|
| **Fact 4.1** (Exact field), các phần (a)(b)(c) | Prop 4.1, 4.2, 4.3 | Là kết quả đã biết (Baptista, Lipman); gọi "Fact" kèm trích dẫn, không đặt ngang hàng với đóng góp mới |
| **Theorem 4.2** (Label-noise endpoint law), các phần (a) law, (b) các giới hạn theo h, (c) W₂ floor | Thm 4.4, Cor 4.5, Prop 4.6 | Cùng một đối tượng |
| **Theorem 5.1** (Positive mixtures keep the atoms) | Thm 5.1, Prop 5.2, Cor 5.5 | Label averaging và negative guidance là các trường hợp riêng của Π; nêu chúng trong một câu "In particular…" |
| **Example 5.2** | Prop 5.3 | Đây là ví dụ cho thấy exceptional set có thể là một hyperplane |
| **Theorem 5.3** (Any two fields keep the atoms) | Prop 5.4, Thm 5.6, Cor 5.7 | Cor 5.7 là phát biểu tổng quát nhất; hai cái kia là trường hợp riêng. Phần h = 0 của Prop 5.4(b) giữ làm phần (b) |
| **Theorem 5.4** (Three fields can blend), các phần (a) ngưỡng, (b) ổn định khi nhiễu | Thm 5.8, Prop 5.9 | |
| **Theorem 5.5** (Spectral criterion), kèm phần ngưỡng ma trận | Thm 5.10, Cor 5.11 | Remark 5.12 chuyển hẳn vào appendix |
| **Proposition 5.6** (Sign rule) | Prop 5.13 | |
| **Proposition 6.1** | giữ nguyên | |

Kết quả: từ 20 xuống còn **8** (1 Fact, 5 Theorem, 1 Example, 2 Proposition). Reviewer nhìn vào là thấy ngay
đâu là đóng góp.

Paper B chỉ có khoảng 7 statement, ổn. Tuy vậy Lemma 4.2 và Prop 4.3 nên gộp thành Theorem 4.2 với hai phần
(h = 0 và h > 0).

### 4.2 Appendix: mỗi theorem một proof liền mạch

- Chỉ giữ **2 lemma dùng chung** (B.2 convergence, B.3 volume expansion), vì chúng được dùng ≥ 4 lần. Các lemma
  chỉ dùng một lần thì đưa thẳng vào proof dưới dạng "Step k".
- Mỗi proof dùng khung cố định: **Setup** (khai báo biến cục bộ) → **Step 1…n** (mỗi step có tiêu đề là claim
  của step đó) → **Conclusion**. Không còn những đoạn "For (a), let…, fix…, put…, so that…" kéo dài 10 dòng.
- Bỏ "Proof sketch" ở main text khi proof đầy đủ đã có ở appendix và sketch dài hơn 6 dòng (Thm 5.10). Sketch
  ngắn (Thm 5.1) thì giữ.

### 4.3 Ví dụ viết lại (proof Thm 5.8(a), trang 43 của A)

Hiện tại là một đoạn văn xuôi khoảng 12 dòng, với 7 biến được định nghĩa nằm xen trong câu. Bản viết lại theo
quy tắc của bạn (nội dung toán giữ nguyên):

```latex
\paragraph{Step 1 (a barrier that moves inward faster than the flow).}
Let $w\sinh^2 B>1$. Fix
\begin{equation}\label{eq:barrier-setup}
  \cosh s_u=\sqrt{w}\,\sinh B,\qquad
  \delta_0\in(0,s_u),\qquad
  \gamma:=-F_w(\delta_0)>0,\qquad
  b(t):=\delta_0\,\varepsilon^2/t .
\end{equation}
Then $s=\delta_0$ on $x=b(t)$, and
\begin{align}
  v_{\varphi,w}\big(b(t),t\big)-b'(t)
  &=\frac{F_w(\delta_0)-b(t)}{\varepsilon}
    +\delta_0\Big(\frac{2\varepsilon}{t}+\frac{\varepsilon^2}{t^2}\Big)\notag\\
  &=\frac1\varepsilon\Big[-\gamma+\delta_0\Big(\frac{\varepsilon^2}{t}+\frac{\varepsilon^3}{t^2}\Big)\Big]
  \;<\;0 \qquad \forall\, t\in[t_1,1). \label{eq:barrier-sign}
\end{align}

\paragraph{Step 2 (trapping).} By \eqref{eq:barrier-sign} and oddness of $F_w$,
\begin{equation}
  |x(t_1)|<b(t_1)\;\Longrightarrow\;|x(t)|<b(t)\quad\forall\,t\in[t_1,1)
  \;\Longrightarrow\; x(t)\to0 .
\end{equation}
(First crossing at $t_2$ would need $(x-b)'(t_2)\ge0$, contradicting \eqref{eq:barrier-sign}.)

\paragraph{Step 3 (positive mass).} $U:=\Phi_{t_1}^{-1}\big((-b(t_1),b(t_1))\big)$ is an open interval
containing $0$, so $P_0\ge\pi_0(U)>0$.
```

(Ở đây `\delta` đã đổi thành `\delta_0` cho đúng quy tắc "`\delta` chỉ dùng cho Dirac"; tên cuối cùng lấy theo
bảng ký hiệu.)

### 4.4 Pseudocode cho phần thủ tục

Các phần đang được mô tả bằng văn xuôi mà nên viết thành `algorithm`:

| Paper | Thủ tục | Hiện ở |
|---|---|---|
| A | Stiff integration với stopping rule lấy từ proof, cùng bisection tìm basin | §7 "Guided label averaging", App E.2 |
| A | Phân loại endpoint theo candidate hoặc centroid | §7 "spectral criterion", App E.2 |
| B | Hybrid Heun sampler với swap level s (net→exact, exact→net, window) | §5.3, Fig 1 phải |
| B | Đo n_t, e_t, ϱ_t và late contraction C dọc trajectory | §5.2, §5.4 |
| B | Heun certificate c_k(ϱ) | §5.4 "A certificate" |

### 4.5 Checklist toán, áp cho từng trang

- [ ] Mọi biểu thức có phân số lồng nhau, tổng, hoặc dài hơn khoảng 1/3 dòng thì đưa ra display.
  Ví dụ: Prop 4.1 và Prop 5.2 (A); Thm 4.1(a)(c) (B).
- [ ] Phát biểu theorem tách thành các khối **Assumption / Setting / Conclusion**. Ví dụ: Thm 5.10 hiện trộn
  định nghĩa basin vào câu giả thiết.
- [ ] Các công thức quan trọng được đánh số và tham chiếu bằng số, không chép lại. Ví dụ: `F_w(s)` xuất hiện
  lại ở Fig 4, §5.3 và B.6; `\sinh^2` xuất hiện 43 lần trong `main.tex` của A, phần lớn là để viết lại `w_c=1/\sinh^2B`; `(1-t)^2` xuất
  hiện 28 lần.
- [ ] Câu dẫn ngắn: "Set", "Then", "Hence", "By (k)". Tránh dạng "With s = …, the averaged posterior means are
  … and the unconditional one is …, so in the time τ the composite flow is …".
- [ ] Mỗi câu chứa ≤ 2 biểu thức inline.
- [ ] Dùng `\forall`, `\Rightarrow` cho giả thiết và kết luận khi nó gọn hơn lời. Ví dụ Prop 5.13(b):
  `c_2\ge0 \wedge (c_1\le0 \vee c_3\le0) \Rightarrow F'>0`.

---

## 5. Proof strategy: giữ, bỏ, hay chuyển thành pseudocode?

**Hiện trạng.** Cùng một template hai bước đang được kể **bốn lần**: "Technique" (trang 4), "Proof strategy"
cùng Figure 3 (trang 8–9), Table 4 (trang 27), và Appendix B.3.

**Đánh giá.**
- Nội dung đáng giữ: đây là xương sống chung của 5 kết quả, và nó giải thích vì sao composition là chỗ thất bại.
  Reviewer cần biết điều đó **trước khi** đọc Section 5.
- Figure 3 không đáng giữ. Flowchart với các ô "z an atom?" và "Θ > 0 near z?" chiếm khoảng 1/3 trang nhưng chỉ
  vẽ lại hai implication. Hình thoi và các nhánh yes/no không thêm thông tin gì ngoài hai câu.
- Pseudocode (`algorithm`) **không phải** hình thức phù hợp. Proof không phải là thủ tục, và viết
  `if … then … else` cho một lập luận logic sẽ làm reviewer lý thuyết khó chịu.

**Khuyến nghị.** Thay "Technique", đoạn "Proof strategy" và Figure 3 bằng **một khung duy nhất** ở đầu Section 5:

```latex
\begin{framed}
\textbf{Template.} For a field $\dot x=\bar m-x$ in log-time $\tau$, with candidate set $\mathcal C'$
and combined posterior covariance trace $\Theta$:
\begin{align*}
 &\text{(S1)}\quad \textstyle\int^\infty|\dot x|^2\,d\tau<\infty
   \;\Longrightarrow\; x(\tau)\to z\in\mathcal C' \hfill\text{(Lemma B.2)}\\
 &\text{(S2)}\quad z\notin\mathcal X,\ \liminf\Theta>0
   \;\Longrightarrow\; \textstyle\int\operatorname{div}f\to\infty
   \;\Longrightarrow\; \operatorname{Leb}\{x_0: x\to z\}=0 \hfill\text{(Lemma B.3)}\\
 &\text{(S1)}\wedge\text{(S2)} \;\Longrightarrow\; X_1\in\mathcal X \ \text{a.s.}
\end{align*}
\end{framed}
```

Ngay sau khung là **một bảng 5 dòng** nói rõ "các can thiệp chỉ khác ở cách kiểm S1/S2":

| Kết quả | S1 kiểm bằng | S2 kiểm bằng | Kết luận |
|---|---|---|---|
| Thm 5.1 (mixtures) | log-partition energy | Θ = averaged trace > 0 | atom a.s. |
| Thm 5.3 (two fields) | integration by parts theo w | Θ ≥ r² − \|m_w\|² − … | atom a.s. |
| Thm 5.4 (conjunction) | Lemma B.4 | **Θ < 0** tại tie khi w > w_c | blend có xác suất > 0 |
| Thm 5.5 (spectral) | Lemma B.4 | dấu các trị riêng của Γ | open / null basin |

Giữ Table 4 ở appendix làm roadmap cho reviewer muốn kiểm proof. Appendix B.3 giữ nguyên vì đó là chỗ chứa
lemma. Tổng cộng tiết kiệm được khoảng 2/3 trang, và template chỉ còn xuất hiện một lần ở main text.

Paper B không có proof template. Đoạn "What the statements do and do not say" (trang 9) là cách làm tốt, nên
giữ.

---

## 6. Thứ tự làm đề xuất

1. Chốt bảng ký hiệu (`shared_notation.md`), rồi thêm macro vào `math_commands.tex` của cả hai paper.
2. Sửa font figure (`scripts/figstyle.py`) và vẽ lại tất cả figure. Việc này chạy một lần trên lab09.
3. Gộp statement theo mục 4.1 và viết lại cấu trúc proof ở appendix của A. Phần này tốn công nhất; mọi proof là
   của tác giả, nên tác giả cần xác nhận từng thay đổi cấu trúc.
4. Cắt văn bản trang 11–21 của A và Section 5 của B (mục 2). Số liệu chuyển vào bảng.
5. Thay proof strategy bằng khung và bảng (mục 5); thêm các Algorithm (mục 4.4).
6. Vẽ các figure mới A-F1…A-F3 và B-F1.
7. Build lại, kiểm leak scan, so số trang.
