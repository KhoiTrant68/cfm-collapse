# Reviewer defense — 27/10/2026

**Trạng thái paper.**
- `main` ở `0f2b21c`: bản `main.tex` của tác giả cộng 8 sửa trình bày.
- Venue: TMLR (`\usepackage{tmlr}`). TMLR chấm theo tiêu chí "claims có được bằng chứng ủng hộ không", nên
  rủi ro chính là tuyên bố vượt quá bằng chứng, không phải thiếu so sánh SOTA.
- Toán: cả 8 unit đã đạt 4/4 lượt verifier HOLDS và qua các lượt tấn công #4/#5/#18/#40
  (`docs/review/math_evaluation_2026-10-25.md`, mục 8).
- Số liệu: `scripts/verify_paper_numbers.py` cho 429/429 khớp.
- Tài liệu này không bàn tính đúng của chứng minh. Nó bàn phạm vi, bằng chứng và câu chữ.

Tài liệu này kế thừa `reviewer_defense_2026-10-20.md`. Các câu trả lời reviewer và các đoạn sửa câu chữ viết
bằng tiếng Anh để dán thẳng vào paper hoặc rebuttal.

## 0. Những gì đã thay đổi kể từ 20/10

| 20/10 | Vấn đề | Trạng thái hôm nay |
|---|---|---|
| W1 | Sai số dọc quỹ đạo học được chưa đo | **Đã đo (EXP-B), chưa vào paper** |
| W2 | Theorem 4.7 chưa có kiểm tra trên mạng thật | **Đã làm (EXP-A 1D + 2D), chưa vào paper**. Kết quả có sắc thái (mục 1, T2) |
| W3 | Composition chỉ có ở 1-D | **Đã giải quyết trong paper**: Thm `thm:spectral` và Cor `cor:spectral-threshold` cho mọi chiều, kèm số liệu exact ở d = 2, 8 |
| W4 | Ý nghĩa với người dùng | Đã thêm câu "practitioner", nhưng câu đó **tuyên bố quá mức** (mục 1, P1) |
| W5 | Quy mô nhỏ | Không đổi |
| W6 | Nhãn định danh | **Đã giải quyết**: phần class-conditional CIFAR có trong App. `app:exp4` |
| W7 | Chỉ interpolant tuyến tính | Không đổi |
| W8 | 38% off-atom ở CIFAR chưa giải thích | **Đã đo (EXP-C) trên 3 run `heff`**, chưa vào paper; con số 38% đến từ một run khác |
| W9 | Thống kê | Không đổi; đã khai báo population sd |
| W10 | Kiểm tra exact chỉ là thời gian hữu hạn | Không đổi; composition dùng tiêu chí dừng đã chứng minh |
| W11 | Thiếu tài liệu lý thuyết guidance | **Vẫn thiếu** (Q10) |
| W12 | Hai bộ ước lượng CIFAR | **Đã giải quyết**: text ghi rõ "training-time estimator; 0.458 re-measured" |
| Q6, Q7 | Ablation kiến trúc/optimiser, tách seed | **Đã có** trong App. `app:exp` |

## 1. Bảng điểm yếu hiện tại

| # | Loại | Điểm yếu | Ở đâu | Mức |
|---|---|---|---|---|
| P1 | Trình bày | **Tuyên bố vượt quá định lý ở 5 câu.** Câu "practitioner" ở intro và câu đầu Conclusion bỏ điều kiện h > 0 / prior dương ngặt, nên mâu thuẫn với Table 1 hàng 6 (lấy trung bình hai trường hard-label đưa mọi nguồn về trung điểm). "Endpoint noise is the only one … for every source" cũng mâu thuẫn với hàng 6. "endpoint prediction does not converge" phải là "does not converge to its training example". Câu tóm tắt ở intro thiếu "at an identifying label". Đây là loại lỗi reviewer TMLR bắt được chỉ bằng cách đọc intro cạnh Table 1. | Intro ¶ sau các bullet; Sec. 4.4; Conclusion | **Cao, sửa dễ** |
| T1 | Kỹ thuật | Liên hệ trường exact → mạng học được vẫn chỉ ở dạng có điều kiện trong paper. EXP-B cho thấy tiền đề quả cầu của Prop 5.2 không thỏa ở mạng nào, và K(t) = m/r tăng như (1−t)⁻². Hai định lý transfer gọi đúng tên đại lượng cần đo, nhưng không áp dụng được cho các mạng đã huấn luyện. | Sec. 5, Limitations | Cao cho tới khi thêm EXP-B |
| T2 | Kỹ thuật | **Mạng có tái hiện được composition hay không phụ thuộc cách tham số hóa.** Mạng dự đoán x theo biến blow-up s (và distill) tái hiện ngưỡng; CFM chuẩn dự đoán v thì không, vì độ dốc tại điểm hòa theo đơn vị s → 0. Reviewer có thể đọc thành "trong thực tế cơ chế này không xảy ra". | Sec. 4.3, 6.2 | Trung bình–cao |
| T3 | Kỹ thuật | Basin co lại nhanh theo số chiều. Ở d = 8, tại 5 w_c chỉ còn 0,019 (simplex) và 0,002 (box), và thấp hơn độ phân giải ở 1,1 cùng 2 w_c. Ý nghĩa ở chiều ảnh chưa rõ. | Table `tab:spectral` | Trung bình |
| T4 | Kỹ thuật | Thm transfer là sơ cấp và a posteriori: đúng với mọi đường cong và mọi điểm, và thành đẳng thức khi vế phải hội tụ. Paper đã nói điều này (Sec. 5). Proof của Prop 5.2 cho một cận tiên nghiệm mạnh hơn nhưng paper chưa phát biểu. | Sec. 5 | Trung bình |
| T5 | Kỹ thuật | Chỉ interpolant tuyến tính với nguồn Gaussian (W7). | Sec. 2 | Trung bình |
| E1 | Thí nghiệm | Quy mô: d ≤ 10; CIFAR N = 2000, một mask, 3 instance. | Sec. 6, Limitations | Trung bình |
| E2 | Thí nghiệm | Con số 38% của CIFAR h = 6 đến từ run `exp3_cifar_ddpm_h6`, không còn trọng số. Phép tách của EXP-C đo trên 3 run khác, ở đó off-atom là 0,298 ± 0,058 với cùng sampler. | Sec. 6.1 | Trung bình |
| E3 | Thí nghiệm | Thống kê: population sd với n = 3–5, không có khoảng tin cậy. | Sec. 6 | Trung bình–thấp |
| E4 | Thí nghiệm | Table `tab:learned-averages` (pilot) dùng thống kê energy có chệch, không có null. Đã có EXP-A thay thế. | Sec. 6.2 | Thấp |
| P2 | Trình bày | Thiếu tài liệu lý thuyết guidance (Q10). | Related work | Trung bình–thấp |
| E5 | Thí nghiệm | Một run ablation của EXP-A (cfm_v_sep seed 2) không chạy xong do bộ giải; phải nêu nếu dùng biến thể đó. | EXP-A | Thấp |

## 2. Các câu hỏi reviewer dự kiến (khả năng cao trước)

### Q1. Do the exact-field results say anything about trained samplers? [Rất cao]
**Lý do reviewer hỏi.** T1 và T2. Mọi định lý ở Sec. 4 là về v*.
**Trả lời được không.** Có, bằng EXP-A/B/C. Hiện mới chỉ là tài liệu nội bộ; cần đưa vào paper.
**Draft response.** "Yes, and we now measure how. (i) On EXP-1 networks, the ratio $K(t)=m/r$ of the error along the learned trajectory to the error on the teacher path grows like $(1-t)^{-2}$ (1.5 at $1-t=0.5$, $2\times10^7$ at $10^{-4}$); a loss-only bound underestimates the endpoint distance by about $100\times$. (ii) Networks that predict the endpoint in the blow-up variable reproduce the composition threshold: the midpoint occupancy matches the exact field within about $0.02$ at $w/w_c\in\{2,5,10\}$, and the tie Jacobian matches the exact eigenvalue ($-0.27$ vs $-0.268$). (iii) At CIFAR-10 $h=6$, the exact field from the same sources puts no sample off-atom, so the off-atom samples come from the learned field."

### Q2. Does guided label averaging leave the support in a trained model? [Rất cao]
**Lý do reviewer hỏi.** Đây là kết quả mới nổi bật nhất của paper.
**Trả lời được không.** Có (EXP-A), nhưng kết quả có sắc thái và phải nói thẳng.
**Draft response.** "It depends on the parametrisation, and the theory says why. The off-atom basin lives in a boundary layer of width $(1-t)^2$ around the tie (the variable $s=\beta x$). Networks that predict the endpoint as a function of $s$, trained by CFM or by distillation, reproduce the exact threshold on the line ($B\in\{1,2,3\}$) and on the triangle (recall of the exact midpoint basin $0.97$–$1.00$ for $w\ge2w_c$, at most $0.005$ midpoint mass below $w_c$). Standard velocity-parametrised CFM does not: its tie slope in $s$-units tends to $0$ (about $10^{-10}$ at $1-t=10^{-5}$) and it puts no sample at the midpoint for any $w$. The theorem identifies the mechanism; whether a learned sampler realises it is decided by whether it resolves that boundary layer."

### Q3. What is new, given that memorisation by the empirical minimiser is known? [Cao]
**Trả lời được không.** Có, từ chính text.
**Draft response.** "Memorisation of the exact minimiser is our reference, not our contribution (Related work). The contribution is the classification in Table 1: positive mixtures with strictly positive priors and nonnegative bounded-variation guidance keep every trajectory convergent with null non-atom basins, without assuming away non-minimising critical limits; their composition does not, with the explicit threshold $w_c=1/\sinh^2B$ and the matrix threshold $\lambda_{\max}(D^{-1/2}C_{\mathrm{av}}D^{-1/2})$ in any dimension (Theorem~\ref{thm:spectral}, Corollary~\ref{cor:spectral-threshold}). We are not aware of a prior threshold of this kind for guidance on the finite-support field."
**Lưu ý.** Câu cuối cần một lượt tra tài liệu có chủ đích trước khi dùng; công cụ tìm paper trong phiên đánh giá không hoạt động.

### Q4. Is the composition effect relevant beyond small dimension? [Cao]
**Lý do reviewer hỏi.** T3.
**Trả lời được không.** Một phần: về lý thuyết thì có, nhưng về số lượng, basin nhỏ ở d = 8.
**Draft response.** "Theorem~\ref{thm:spectral} and Corollary~\ref{cor:spectral-threshold} hold in any dimension, and the exact computations confirm the predicted sink/source classes in $d=2$ and $d=8$. The basin probability, however, decreases with dimension at fixed $w/w_c$ ($0.687$ for the triangle and $0.019$ for the nine-vertex simplex at $5w_c$), and we state this in Section 6.2. The theory says when an off-support endpoint exists, not that it is frequent at image scale."
**Hành động.** Thêm một câu về việc basin co lại theo số chiều vào thảo luận sau Theorem composition hoặc spectral.

### Q5. Isn't the transfer theorem trivial? [Trung bình–cao]
**Lý do reviewer hỏi.** T4.
**Trả lời được không.** Có. Paper đã tự nói đây là kết quả sơ cấp (Sec. 5).
**Draft response.** "It is elementary by design, and Section 5 says so: its use is to name the quantity that decides a learned endpoint. Proposition~\ref{prop:localtransfer} adds an a priori version near an atom: once the trajectory enters the ball, the endpoint is within $\limsup_t\sup_{|x-a|\le\rho}(1-t)|\Delta(x,t)|$ of the atom, a bound that does not depend on the trajectory. We measured both premises on trained networks (Appendix X): the trajectory premise holds for 1–11% of paths and the ball premise for none, which locates the gap in the off-trajectory error."
**Hành động.** Phát biểu cận tiên nghiệm này trong Prop 5.2 (mục 4, sửa E-9).

### Q6. Why are 38% of the CIFAR h = 6 samples off-atom? [Trung bình–cao]
**Trả lời được không.** Một phần (E2).
**Draft response.** "On three $h=6$ runs we integrated the exact kernel field from the same sources: it puts no sample off-atom at $1-t=10^{-3}$ or $10^{-4}$. The learned field with a converged solver leaves $25\%$ off-atom ($30\%$ with the 50-step Euler sampler), and only $19\%$ of samples end at the atom the exact field selects. Truncation therefore contributes nothing and discretisation about four points; the remainder is the error of the learned field. The $38\%$ quoted in the main text comes from a different run, whose weights were not kept; on these three runs the same sampler gives $0.298\pm0.058$."

### Q7. Does a small training loss guarantee the endpoint? [Trung bình]
**Trả lời được không.** Có: Prop `prop:loss-no-certificate` và EXP-B.
**Draft response.** "No. Proposition~\ref{prop:loss-no-certificate} constructs fields with vanishing hard-conditioned loss and endpoint law $\mathcal N(a,I_d)$. On trained networks, the loss-only bound at $T=1-10^{-3}$ is about $100\times$ smaller than the measured endpoint distance ($0.0065$ vs $0.64$ at $2\times10^5$ steps)."

### Q8. You say label averaging cannot create novel samples, but Table 1 says averaging hard-label fields moves every endpoint. Which is it? [Trung bình; reviewer đọc kỹ sẽ hỏi]
**Trả lời được không.** Có. Đây là lỗi câu chữ (P1), cần sửa trước khi nộp.
**Draft response.** "Both are correct with the bandwidth stated: averaging exact fields with strictly positive priors ($h>0$) keeps the atoms (Theorem~\ref{thm:posmix}, Proposition~\ref{prop:filtered}), while averaging identifying hard-label fields ($h=0$), whose priors are not positive, can send every source to a circumcentre. We corrected the introduction and conclusion, which had dropped the qualifier."

### Q9. Is h = 0 collapse trivial under identifying labels? What about class labels? [Trung bình]
**Trả lời được không.** Có, bằng App. `app:exp4` ("Class labels").
**Draft response.** "With shared labels the same analysis gives the within-class empirical law; two class-conditional CIFAR-10 runs keep $0.64$–$0.83$ ($h=0$) and $0.62$–$1.30$ ($h=0.4$) of the within-class scatter over training and both end at $0.76$ (Appendix~\ref{app:exp4}, Figure~\ref{fig:image-class})."

### Q10. How does this relate to the theory of guidance? [Trung bình]
**Trả lời được không.** Một phần.
- Hiện paper chỉ dẫn Chidambaram et al. 2024, Jain et al. 2025 và Kynkäänniemi et al. 2024.
- Ba tài liệu nên thêm, nhưng phải kiểm tra bằng `/phd-skills:factcheck` trước khi trích:
  - Bradley & Nakkiran 2024 (CFG như predictor–corrector);
  - Wu et al. 2024 (guidance trên Gaussian mixture);
  - Pavasovic, Verbeek, Biroli, Mézard 2025 (lý thuyết CFG nhiều chiều trên Gaussian mixture).

**Draft response.** "These works study guidance on continuous targets such as Gaussian mixtures. Our setting is the finite-support target that training defines, where guidance alone cannot create mass off the atoms and its composition with label averaging can."

### Q11. Are the conclusions sensitive to architecture, optimiser or seeds? [Trung bình]
**Trả lời được không.** Có, bằng Table `tab:ablation` và đoạn "Instance and training randomness".
**Draft response.** "Collapse appears for every width, depth and optimiser we tried; capacity and optimiser change its speed only (Table~\ref{tab:ablation}). Separating instance and training randomness, the instance accounts for about 78% of the variance."

### Q12. Does the analysis extend beyond the linear interpolant? [Trung bình]
**Trả lời được không.** Không; chưa chứng minh.
**Draft response.** "We state the results for the linear interpolant. The posterior over atoms keeps the same softmax form for any Gaussian path, with $\beta=\alpha_t/\sigma_t^2$, and we expect the arguments to carry over; we leave this to future work rather than claim it."

### Q13. Are the statistics adequate? [Trung bình–thấp]
**Draft response.** "Every $\pm$ is a population standard deviation over 3–5 seeds and is descriptive; seeds are fixed in advance, and per-seed values are in the released results."
**Hành động.** Với EXP-A/B/C, báo cáo khoảng giá trị theo seed thay vì chỉ ±.

## 3. Nên trình bày những thí nghiệm nào

| Ưu tiên | Thí nghiệm | Đặt ở đâu | Vì sao |
|---|---|---|---|
| 1 | **EXP-A 2D (tam giác) và 1D**: tỉ lệ chiếm tâm theo w/w_c (exact, cfm_x_s, distill_x_s, cfm_v), kèm độ dốc tại điểm hòa theo thời gian | Main, Sec. 6.2; thay Table `tab:learned-averages` | Trả lời Q1, Q2. Cho ngưỡng một bản sao trên mạng thật và giải thích vì sao CFM chuẩn bỏ lỡ nó |
| 2 | **EXP-B**: K(t) theo 1−t, khoảng cách endpoint thật so với cận chỉ dựa trên loss, tần suất các tiền đề của Prop 5.2 | Main, cuối Sec. 5 hoặc Sec. 6.1; bảng đầy đủ ở appendix | Biến các định lý transfer có điều kiện thành phép đo (Q1, Q5, Q7) |
| 3 | **EXP-C**: phép tách off-atom ở h = 4, 5, 6 | Sec. 6.1, thay câu thận trọng; bảng ở App. E.2 | Q6. Nhớ ghi chú về run khác |
| 4 | Ablation kiến trúc/optimiser, tách seed, class-conditional | Giữ ở appendix (đã có) | Q9, Q11 |
| 5 | Bảng spectral (d = 2, 8) | Giữ; thêm một câu về việc basin co lại theo chiều | Q4 |

**Kết quả âm nên giữ, viết dưới dạng phân tích:**
- CFM dự đoán v không tái hiện ngưỡng. Đây là một phát hiện về tham số hóa, không phải thất bại.
- Tiền đề quả cầu của Prop 5.2 không thỏa ở mạng nào. Điều này chỉ ra đúng chỗ còn thiếu: sai số ngoài quỹ đạo.
- Run cfm_v_sep seed 2 không chạy xong do bộ giải (nếu dùng biến thể đó).

## 4. Đề xuất sửa câu chữ

E-1 đến E-6 đã được áp dụng ở commit `f2eef6d` (27/10). E-7 đến E-10 chưa áp dụng, vì chúng cần đưa EXP-A/B/C
vào paper trước.

**E-1. Intro, đoạn sau các bullet (P1).**
> Before: "Among the interventions analysed (Table~\ref{tab:interventions}), non-training endpoints thus arise only from a support change such as endpoint noise, from averaging hard-label fields, from composing label averaging with guidance, or, for learned fields, from an error that does not vanish at the scale $(1-t)^{-1}$ up to the end of sampling. For a practitioner this says where samples off the training set can come from: not from label noise, label averaging or guidance applied separately to the field that training defines, but from their composition, from a change of the target's support, or from a learned field whose endpoint prediction does not converge."
>
> After: "Among the interventions analysed (Table~\ref{tab:interventions}), non-training endpoints of positive probability thus arise only from a support change such as endpoint noise, from averaging hard-label fields, from composing label averaging with guidance, or, for learned fields at an identifying label, from an error that does not vanish at the scale $(1-t)^{-1}$ up to the end of sampling. For a practitioner this says where samples off the training set can come from: not from label noise, from label averaging at positive bandwidth or from nonnegative guidance applied separately to the field that training defines, but from their composition, from averaging hard-label fields, from a change of the target's support, or from a learned field whose endpoint prediction does not converge to its training example."

**E-2. Intro, bullet 2.**
> Before: "on two examples the threshold is exactly $w>1/\sinh^2B$"
> After: "for two examples whose averaged priors have log-odds $\pm2B$, the threshold is exactly $w>1/\sinh^2B$"

**E-3. Sec. 4.4 ("What leaves the support").**
> Before: "Endpoint noise, $X_1=x^I+\rho\xi$, is the only one among them that leaves the atoms for every source (Proposition~\ref{prop:tgtnoise})."
> After: "Endpoint noise, $X_1=x^I+\rho\xi$, is the only one among them that leaves the atoms in every configuration: its endpoint law has a density (Proposition~\ref{prop:tgtnoise}). Averaging hard-label fields can also move every endpoint, but only in configurations such as the symmetric tie of Section~\ref{sec:posmix}."

**E-4. Conclusion, hai câu đầu.**
> Before: "The exact empirical conditional flow ends on its training examples, and so do its positive modifications: positive mixtures of prior-indexed exact fields, including label averaging and negative guidance, and nonnegative guidance with a fixed strength or a bounded schedule of bounded variation. … with an explicit threshold on two atoms that is stable under perturbation of the priors and the guidance strength."
> After: "The exact empirical conditional flow ends on its training examples, and at positive label bandwidth so do its positive modifications: positive mixtures of exact fields with strictly positive priors, including label averaging and guidance with $w\in[-1,0)$, and nonnegative guidance with a fixed strength or a bounded schedule of bounded variation. … with an explicit threshold on two atoms, above which the off-atom basin persists under perturbation of the priors, mixture weights and guidance strength."

**E-5. Table 1, hàng guidance.**
> Before: "Guidance, fixed $w\ge0$ or bounded schedule of bounded variation"
> After: "Guidance $w\ge0$, fixed or a bounded schedule of bounded variation"

**E-6. Conclusion, câu hỏi mở.**
> Before: "Open questions are when guided averaging leaves the support with many atoms in high dimension, …"
> After: "Open questions are when guided averaging leaves the support beyond hyperbolic profiles and the face condition, how large its basins are in high dimension, …"

**E-7. Limitations.**
> Before: "The transfer statements are conditional on the error along learned trajectories, which we do not infer from the loss and have not measured."
> After: "The transfer statements are conditional on the error along learned trajectories, which we do not infer from the loss. Measured on the EXP-1 networks (Appendix~X), the ratio of this error to the teacher-path error grows like $(1-t)^{-2}$, and the ball premise of Proposition~\ref{prop:localtransfer} holds for none of them."
>
> Before: "The composition theorem has no trained-network counterpart yet."
> After: "Networks that predict the endpoint in the blow-up variable reproduce the composition threshold; velocity-parametrised networks do not resolve the boundary layer at the tie and do not (Section~\ref{sec:intervention-tests})."
>
> Thêm vào danh sách các trường hợp chưa được phủ: "fixed guidance strengths below $-1$, and schedules that are not of bounded variation near $t=1$".

**E-8. Sec. 6.1, đoạn CIFAR.**
> Before: "At $h{=}6$, $38\%$ of the finite-cutoff samples are off-atom by the nearest-neighbour criterion; this combines learned-field, truncation and discretisation effects and does not identify a limiting support."
> After: "At $h{=}6$, $38\%$ of the finite-cutoff samples are off-atom by the nearest-neighbour criterion. On three further $h=6$ runs (Appendix~X), the exact kernel field integrated from the same sources puts no sample off-atom at $1-t=10^{-3}$ or $10^{-4}$, and a converged solver lowers the off-atom fraction from $0.30$ to $0.25$: the off-atom samples come from the learned field, not from truncation, and only marginally from discretisation."

**E-9. Sau Prop 5.2 (cận tiên nghiệm, T4).**
> Add: "Since $Z$ stays in the ball, the right side is at most $\limsup_{t\uparrow1}\sup_{|x-a|\le\rho}(1-t)|\Delta(x,t)|\le\rho/4$, a bound that does not depend on the trajectory."

**E-10. Sec. 6.2, "Learned label averages".** Thay pilot bằng EXP-A (ưu tiên 1 ở mục 3). Giữ pilot ở appendix nếu muốn.

## 5. Thứ tự làm, theo tác động lên review

1. **E-1 đến E-6** (P1): chỉ sửa câu chữ, nhưng chặn được câu hỏi dễ gây mất điểm nhất (Q8).
2. **Đưa EXP-A vào Sec. 6.2** cùng E-7 và E-10. Đây là thay đổi duy nhất làm tăng điều paper có thể tuyên bố.
3. **Đưa EXP-B vào cuối Sec. 5** cùng E-9.
4. **Đưa EXP-C vào Sec. 6.1 và App. E.2** cùng E-8, nhớ ghi chú về run khác.
5. Kiểm tra rồi thêm các tài liệu ở Q10.
