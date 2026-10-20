# Đánh giá paper và kế hoạch nộp ICLR / ICML / NeurIPS / TMLR — 20/10/2026

Bản được đánh giá: `main` tại `222d129` (sau PR #31, thêm Theorem 4.9). Build lại từ nguồn: **37 trang**,
main text kết thúc ở **trang 13** (khuôn TMLR), tài liệu tham khảo trang 14–16, appendix trang 17–37.
Số hiệu theorem/figure dưới đây lấy từ bản build này.

Các chứng minh là của tác giả; các lượt verifier chỉ là kiểm tra thêm. Tài liệu này không đặt lại câu hỏi
về tính đúng của chứng minh. Nó đánh giá phạm vi, mức liên quan, bằng chứng và cách trình bày.

Kế thừa: `reviewer_defense_2026-10-20.md`. Các mục ở đó đã xử lý xong: abstract, câu dành cho người làm
thực tế, estimator CIFAR, ablation kiến trúc, tách seed, nhãn lớp, và Theorem 4.9 cho trường hợp $d\ge2$.
Tài liệu này bắt đầu từ những gì còn mở.

---

## 0. Tóm tắt

| Venue | Nếu nộp ngay hôm nay | Sau kế hoạch | Yếu tố quyết định |
|---|---|---|---|
| **TMLR** | Nhiều khả năng *minor revision* | Accept khá chắc | Một số câu nói quá; thống kê; Theorem 5.1 chưa được đo |
| **ICML / NeurIPS / ICLR** | Borderline reject (ước lượng chủ quan 4–5/10) | Borderline đến weak accept (5–6/10) | Phải có **bằng chứng trên mạng đã huấn luyện cho phần lý thuyết mới** |

**Chẩn đoán chính.** Phần mới của paper (Section 4: positive mixtures, guidance, composition,
spectral) chỉ được kiểm chứng trên *exact field*. Các thí nghiệm trên mạng đã huấn luyện (Section 6.1)
lại kiểm chứng phần *đã biết* (hard-conditioning collapse, tham chiếu Nadaraya–Watson). Với TMLR, đây
là một giới hạn đã được nêu rõ. Với hội nghị, đây là lý do bị reject: "rigorous but of limited significance".

**Ba quan sát mới, đều rẻ để khai thác:**

1. **Ranh giới là dominance, không phải số prior.** Tổ hợp $\sum_kc_kv_{p_k}$ (với
   $\sum_kc_k=1$) giữ atom với mọi dữ liệu nếu hệ số lồi, hoặc nếu có một hệ số trội:
   $c_j\ge\sum_{k\ne j}|c_k|+\gamma$. Ngược lại, mọi $c$ không trội và có hệ số âm đều rời atom với
   một số dữ liệu trong $\mathbb R^2$. Đây là T1 ở Mục 9, đã qua vote. Ví dụ: CFG với nhiều negative
   prompt có ba prior trở lên nhưng vẫn giữ atom. Đây là thông điệp gọn mà hội nghị cần.
2. **Dấu vân tay circumcentre.** Theory dự đoán điểm off-support là *circumcentre* của các ảnh huấn
   luyện, trong trường hợp hai atom là trung điểm, tức là ảnh "blend". Đây là một chữ ký kiểm tra được
   trên mạng đã huấn luyện. Nó cũng phân biệt được các cơ chế có thể sinh ra 38% mẫu off-atom ở CIFAR
   $h=6$: composition hoặc signed averaging thì cho blend, còn lỗi trường bất kỳ thì cho điểm tuỳ ý
   (E-A2).
3. **Chiều tie, không phải chiều ambient.** Bảng 9 cho thấy basin ở $d=8$ rất nhỏ (simplex: 0 ở
   $2w_c$, 0.019 ở $5w_c$), và reviewer sẽ kết luận "hiệu ứng biến mất ở chiều cao". Nhưng trong
   Theorem 4.9, chỉ các hướng tie bị ép ở thang $1/\beta$; phần pháp tuyến chỉ cần nằm trong một bán
   kính cố định. Với $N=2$, basin là một slab và hiển nhiên không phụ thuộc $d$; với $N>2$ đây mới
   chỉ là giả thuyết. Simplex và box là những trường hợp $\dim L=d$, tức trường hợp xấu nhất. Cần một
   thí nghiệm scaling để kiểm tra (E-A1).

**Lộ trình đề xuất.**
- Củng cố từ nay đến 1/12, rồi qua **Gate G1**.
- Nộp **ICML 2027** (khoảng cuối tháng 1, ngày chưa chính thức).
- Nếu bị reject: nộp **NeurIPS 2027** (khoảng giữa tháng 5), rồi đến **ICLR 2028** hoặc **TMLR**.
- Nếu G1 thất bại (không có cầu nối sang mạng đã huấn luyện): nộp **TMLR** ngay tháng 12 và xin
  **J2C certification** để trình bày ở ICML hoặc NeurIPS qua Journal-to-Conference track.

---

## 1. Điểm mạnh

| # | Điểm mạnh | Bằng chứng |
|---|---|---|
| S1 | Phân loại rõ, có kết quả bất ngờ: hai can thiệp đều giữ atom, nhưng ghép lại thì có thể rời khỏi atom, với ngưỡng chính xác dạng "khi và chỉ khi" $w>1/\sinh^2B$ | Table 1, Thm 4.7, Prop 4.8 |
| S2 | Kỹ thuật không tầm thường: một template hai bước (động năng hữu hạn kéo theo hội tụ; nở thể tích kéo theo basin null), bỏ được giả thiết "không có điểm tới hạn không cực tiểu" của Liu–Zuazua; Theorem 4.9 dùng Lyapunov–Perron | Fig 2, Lemma B.2–B.3, Thm 4.9 |
| S3 | Trình bày toán theo chuẩn hội nghị: restatable, bảng ký hiệu, roadmap, đồ thị phụ thuộc | App. đầu, Tables 3–4, Fig 8 |
| S4 | Trung thực và tái lập được: limitations đầy đủ, 429 con số được kiểm tự động, báo cáo cả lỗi solver | Sec 7, `verify_paper_numbers.py` |
| S5 | Collapse trên mạng đã huấn luyện ở hai quy mô (MLP và U-Net 35.75M), kèm ablation kiến trúc, tách seed và nhãn lớp | Fig 3–4, Tables 5–8, Fig 10 |

## 2. Điểm yếu

Mức độ: **C** = critical, **H** = high, **M** = medium, **L** = low. Cột đầu dành cho ICML/NeurIPS/ICLR, cột sau cho TMLR.

| # | Loại | Điểm yếu | Ở đâu | Hội nghị | TMLR |
|---|---|---|---|---|---|
| W1 | Bằng chứng | Phần lý thuyết mới (Sec 4) chỉ được kiểm trên exact field. Bằng chứng trên mạng đã huấn luyện chỉ phủ phần đã biết (Sec 3). Thí nghiệm duy nhất trên mạng liên quan đến Sec 4 là pilot learned averages (Table 2), và đó là kết quả âm/mô tả. Composition không có đối ứng trên mạng (dòng 877–878) | Sec 6 | **C** | M |
| W2 | Mô hình hoá | Câu "a network that resolves labels only coarsely averages the field over nearby labels" (dòng 112) không có căn cứ. Phân tích nội bộ trước đây (`main_track_plan_2026-10-11.md` §6, Lemma L1) cho thấy trọng số ngầm của learner kernel chỉ dương khi $k=1$ với kernel mũ. Kernel Gaussian/Matérn cho trọng số **có dấu** ngay từ $k=1,N=2$. Learner thực tế nhiều khả năng là *signed* mixture: Thm 4.1 không áp dụng, còn Thm 4.9 thì áp dụng | Intro, Sec 4.1 | H | M |
| W3 | Ý nghĩa | Điểm off-support là circumcentre (blend của các ảnh huấn luyện), và endpoint law vẫn có support hữu hạn. Đoạn "for a practitioner…" (dòng 139–142) có thể bị đọc là giải thích tính sáng tạo hay khả năng generalization. Reviewer đến từ văn liệu memorization/creativity sẽ chất vấn điểm này | Intro | H | M |
| W4 | Ý nghĩa | Basin của composition ở $d=8$ nhỏ (Table 9), và chưa có phân tích vì sao. Reviewer sẽ suy ra "vô nghĩa ở chiều ảnh" | Sec 6.2, Table 9 | H | L |
| W5 | Phạm vi | Chỉ xét interpolant tuyến tính với nguồn Gaussian. CFG trong thực tế chủ yếu dùng với diffusion VP/EDM. Việc mở rộng mới chỉ là "expected", chưa chứng minh | Sec 2 | H | M |
| W6 | Kỹ thuật | Theorem 5.1 là kết quả sơ cấp (tác giả tự nói ở dòng 664), Prop 5.2 có điều kiện, và đại lượng $(1-t)\lvert\Delta\rvert$ chưa bao giờ được đo, dù ở EXP-1 exact field được biết chính xác | Sec 5 | M | M |
| W7 | Related work | Thiếu văn liệu về guidance (predictor–corrector, GMM, CFG chiều cao) và về **mode interpolation / hallucination** của diffusion. Văn liệu sau gần trực tiếp với "circumcentre = blend" (danh sách cần kiểm ở Q11) | Related work | M–H | M |
| W8 | Trình bày | Abstract mở bằng câu hỏi kỹ thuật, chưa có động cơ. Figure 1 minh hoạ hard collapse (phần đã biết), không phải kết quả headline. Sec 3 dùng khoảng 1.5 trang cho phần đã biết. Main text 13 trang, trong khi cần 8 trang (ICML) hoặc 9 trang (NeurIPS/ICLR) | Toàn bài | H | L–M |
| W9 | Thống kê | Dùng population SD với $n=5$ (ablation $n=2$), không có khoảng tin cậy. Table 2 dùng energy V-statistic có bias, không có null hay ngưỡng tương đương | Sec 6, Table 2, Table 7 | M | M |
| W10 | Kỹ thuật | Thm 4.9 cần tính hyperbolic và điều kiện face. Cor 4.10 chỉ áp dụng cho cấu hình đối xứng (common equilibrium). Tính generic chưa được bàn | Sec 4.4 | L–M | L |
| W11 | Thực nghiệm | Quy mô nhỏ: dữ liệu tổng hợp $d\le10$, CIFAR $N=2000$, một mask, ba instance | Sec 6 | M | L |

### Điểm mô phỏng (ước lượng chủ quan theo thang ICLR/NeurIPS)

| Tiêu chí | Hiện tại | Sau kế hoạch (nếu E-A2 dương tính và T1–T3 vào paper) |
|---|---|---|
| Soundness | 3–4/4 | 4/4 |
| Presentation | 2–3/4 | 3/4 |
| Contribution | 2/4 | 3/4 |
| Overall | 4–5 | 5–6 |

---

## 3. Câu hỏi reviewer dự kiến (xếp theo xác suất)

### Q1. Lý thuyết exact field nói gì về sampler đã huấn luyện? [rất cao]
**Lý do reviewer hỏi.** W1. Mọi định lý ở Sec 4 đều nói về $v^\star$, và chính Table 2 cho thấy tính atomic không tự truyền sang mạng.
**Trả lời được không.** Một phần (Thm 5.1, Fig 3–5). Phần còn lại cần E-A2 và E-B.
**Bản nháp trả lời.**
> The exact field is the population minimiser that training targets. Theorem 5.1 states what a trained network must do to inherit its endpoint: the implied endpoint prediction must converge. We now measure this quantity along learned trajectories (Section 6.x): on EXP-1 the endpoint distance matches the late-time prediction error within …, and guided label averages of trained networks place their off-atom samples at circumcentres of training examples, as Theorem 4.7 predicts.

Chỉ dùng câu cuối khi đã có kết quả E-A2.

### Q2. Composition có xảy ra trong mô hình đã huấn luyện không? [rất cao]
**Lý do reviewer hỏi.** Đây là claim gây ngạc nhiên nhất, nhưng mới chỉ được kiểm trên exact field.
**Trả lời được không.** Không, cần E-A2.
**Bản nháp trả lời (nếu kết quả khớp).**
> We added a trained-network test: classifier-free guidance on a CIFAR-10 U-Net trained with label dropout, queried between training conditions. Off-atom samples increase with $w$, and X% of them are closer to the midpoint of their two nearest training images than to either image (Figure …).

### Q3. Điểm off-support chỉ là blend, vậy đây có phải generalization không? [cao]
**Lý do reviewer hỏi.** W3.
**Trả lời được không.** Có, đây là vấn đề cách viết.
**Bản nháp trả lời.**
> No. The new endpoints are circumcentres of training examples (for two examples, their midpoint), and the endpoint law remains finitely supported. The result says that composing two atom-preserving interventions can produce blends of training examples, which are neither training data nor new samples from the data distribution. This is closer to the mode-interpolation artefacts reported for trained diffusion models than to generalisation, and it has a privacy reading: a blend reveals both of its training examples.

Câu về mode interpolation chỉ dùng sau khi đã kiểm tài liệu (Q11).

### Q4. Ở chiều cao basin có biến mất không (Table 9: $d=8$ gần 0)? [cao]
**Lý do reviewer hỏi.** W4.
**Trả lời được không.** Một phần, theo lý thuyết. Cần E-A1 để có số liệu.
**Bản nháp trả lời.**
> In Theorem 4.9 only the tie directions $L$ are squeezed at the scale $1/\beta$; the normal component needs only to lie within a fixed radius. The simplex and box of Table 9 are the least favourable case, $\dim L=d$. Our new computation (Figure …) measures the basin probability against $d$ at fixed tie dimension.

Chỉ dùng câu cuối khi E-A1 xác nhận.

### Q5. Label averaging dương có phải mô hình đúng của learner không? [cao]
**Lý do reviewer hỏi.** W2.
**Trả lời được không.** Một phần.
**Bản nháp trả lời.**
> It is a model, and we have weakened the wording. Label smoothers with signed equivalent kernels give signed combinations of prior fields. Theorem … (dominance) decides these: a signed smoother keeps the atoms when its central weight outweighs the rest in absolute value, and otherwise can create off-atom endpoints even without guidance.

Chỉ dùng sau khi tác giả đã kiểm T1.

### Q6. Có gì mới, khi memorization của empirical minimiser đã được biết? [rất cao ở hội nghị]
**Trả lời được không.** Có.
**Bản nháp trả lời.**
> The endpoint law of Section 3 is a reference, as stated in Related work. The contribution is the classification of interventions (Table 1): convex and dominant combinations, including guidance with any bounded schedule of bounded variation, keep every trajectory convergent with a null non-atom basin, without the non-degeneracy premise of Liu & Zuazua (2026, Remark 3.19). Composition can leave, with an exact threshold, and a spectral criterion decides it in any dimension.

### Q7. Kết quả có mở rộng ra ngoài interpolant tuyến tính (VP/EDM) không? [cao ở hội nghị]
**Trả lời được không.** Có, với T2 (Mục 9), cho các sampler tất định.
**Bản nháp trả lời.**
> Yes, for deterministic samplers. In $y=x/\alpha_t$ and $\lambda=\log(\alpha_t/\sigma_t)$, every Gaussian path gives the same equation $dy/d\lambda=\bar m-y$ (Theorem …; the reduction is the empirical-target case of the schedule invariance noted by Karras et al., 2022). For paths that start from pure noise the endpoint map is that of the linear path, so all endpoint statements transfer, with schedules read in log-SNR. Samplers that start at a finite noise level (EDM, discrete DDPM) keep the almost-sure and positive-probability statements but not the exact endpoint weights. Stochastic samplers are not covered (Conjecture …).

### Q8. Vì sao 38% mẫu CIFAR ở $h=6$ là off-atom? [trung bình–cao]
**Trả lời được không.** Một phần. Cần E-A2 (kiểm circumcentre) và E-B (đo lỗi dự đoán endpoint).
**Bản nháp trả lời.**
> The exact law is atomic. The measured samples come from a learned field at $t=1-10^{-3}$. Theorem 5.1 names the quantity that decides the limit. Measuring it along these trajectories gives …, and only Y% of the off-atom samples lie near circumcentres, so the dominant cause is [field error / label averaging].

### Q9. Theorem 5.1 là sơ cấp; nó đóng góp gì? [trung bình]
**Trả lời được không.** Có, và sẽ mạnh hơn khi có E-B.
**Bản nháp trả lời.**
> Its value is the reading: the endpoint is controlled by the late-time endpoint-prediction error, not by the training loss (Proposition C.2 shows that small loss does not suffice). We now use it as a measurement (Figure …): the bound is attained on EXP-1 to within …

### Q10. Thống kê có đủ không? [trung bình]
**Trả lời được không.** Một phần, cần E-D.
**Bản nháp trả lời.**
> We now report sample standard deviations and 95% t-intervals across seeds, and replace the biased energy statistic of Table 2 with an unbiased estimator and a permutation null.

### Q11. Liên hệ với lý thuyết guidance và mode interpolation? [trung bình]
**Trả lời được không.** Có, sau khi đã kiểm tài liệu. **Kiểm từng mục bằng `/phd-skills:factcheck` trước khi cite.** Danh sách dưới đây nhớ từ trí nhớ và chưa có trong `refs.bib`:
- Aithal, Maini, Lipton, Kolter (NeurIPS 2024), *Understanding Hallucinations in Diffusion Models through Mode Interpolation*. Gần nhất với W3.
- Bradley & Nakkiran (2024), *Classifier-Free Guidance is a Predictor-Corrector*.
- Wu et al. (2024), *Theoretical insights for diffusion guidance: a case study for Gaussian mixture models*.
- Pavasovic, Verbeek, Biroli, Mézard (2025), *Understanding classifier-free guidance: high-dimensional theory and non-linear generalizations*.

**Bản nháp trả lời.**
> These works study guidance on continuous targets. We study the finite-support target that training defines, where guidance alone cannot create mass off the atoms, but guided label averaging creates blends. This is an exact-field counterpart of mode interpolation.

### Q12. Hyperbolicity và điều kiện face có generic không? [thấp–trung bình]
**Trả lời được không.** Một phần.
**Bản nháp trả lời.**
> Parts (a) and (b) of Theorem 4.9 need only hyperbolicity of the profile in question. Part (c) adds the face condition, and Table 9 includes saddles with negative trace, where the trace test is silent. Nonhyperbolic profiles remain open and are listed as such.

Chỉ nói "hyperbolicity là generic" nếu có chứng minh.

---

## 4. Thí nghiệm và lý thuyết đề xuất (theo thứ tự tác động)

### Thí nghiệm

| Ưu tiên | ID | Thí nghiệm | Trả lời | Chi phí | Vị trí |
|---|---|---|---|---|---|
| 1 | **E-A2** | **Composition trên mạng đã huấn luyện, kiểm chữ ký circumcentre.** (i) EXP-1: các mạng $h=0.1$ seed 1001–1005 (đã có) cộng mạng unconditional cùng problem seed (kiểm xem có chưa; nếu chưa, khoảng 20 phút CPU mỗi mạng); field $(1+w)\,\overline{v_\theta}(\cdot,y\pm r)-wv_\theta^{\mathrm{unc}}$; truy vấn ở giữa hai nhãn huấn luyện. (ii) CIFAR: một U-Net huấn luyện với **label dropout** ($p=0.1$), giống thiết lập CFG thật, ở $h\in\{4,6\}$ (ở $h=0$ tham chiếu exact không xác định tại nhãn giữ lại; $h=0$ chỉ dùng làm đối chứng tại nhãn huấn luyện); CFG $w\in\{0,1,3,7\}$. **Metric**: tỉ lệ off-atom, và với mỗi mẫu off-atom, tỉ số khoảng cách tới circumcentre của $k$ ảnh gần nhất ($k=2,3$, lấy giá trị nhỏ nhất) so với khoảng cách tới ảnh gần nhất. Figure: mẫu, hai ảnh huấn luyện gần nhất, và trung bình pixel của chúng | Q1, Q2, Q8; W1 | EXP-1: CPU, vài giờ. CIFAR: khoảng 2.5 GPU-giờ mỗi run × 2 | Main |
| 2 | **E-A1** | **Composition exact ở quy mô lớn.** (i) Atom ngẫu nhiên, $N\in\{12,200,2000\}$, $d\in\{2,8,64,512,3072\}$. (ii) Dữ liệu CIFAR thật ($N=2000$, $x$ là nửa dưới với $d=1536$, nhãn là nửa trên với $k=1536$), $h\in\{4,6\}$, $\varphi$ gồm $K=8$ offset Gaussian, $w\in\{0,1,3,7\}$, truy vấn ở nhãn huấn luyện và ở nhãn giữ lại. Đo tỉ lệ kết thúc ở circumcentre, tách theo $\dim L$. Dùng lại log-time và logsumexp từ `spectral_criterion_check.py` | Q4; W4 | GPU vài phút hoặc CPU khoảng 1 giờ | Main |
| 3 | **E-B** | **Đo Theorem 5.1.** Trên EXP-1 $h=0$, các checkpoint $10^4$, $10^5$, $2\times10^5$, $10^6$: tính $\hat x_1(Z_t,t)=Z_t+(1-t)v_\theta(Z_t,t)$ dọc quỹ đạo, vẽ $\lvert\hat x_1-x^i\rvert$ theo $t$ và so với $\lvert Z_1-x^i\rvert$. Lặp lại trên CIFAR $h=0$ và $h=6$ nếu checkpoint còn | Q8, Q9; W6 | CPU, dưới 1 giờ (EXP-1) | Main (EXP-1), App (CIFAR) |
| 4 | **E-D** | Vệ sinh thống kê: sample SD và khoảng $t$ 95%; Table 2 dùng U-statistic không bias cộng permutation null; ablation tăng lên 5 seed | Q10; W9 | CPU, vài giờ | Main + App |
| 5 | E-C | (Tuỳ chọn; kiểm Hệ quả của T1 cho signed smoothing) Learner kernel ridge với kernel Gaussian trong không gian nhãn: tính tổ hợp prior có dấu mà nó ngầm định, rồi kiểm sink off-atom bằng phương pháp số của Thm 4.9, không dùng guidance | Q5; W2 | CPU | App |

**Pre-registration (ghi trước khi chạy):**
- **E-A2.** Dự đoán: tỉ lệ off-atom tăng theo $w$, và đa số mẫu off-atom ở gần circumcentre hơn là gần atom. Bị bác bỏ nếu mẫu off-atom không gần circumcentre ($k=2$ hoặc $3$) hơn gần ảnh gần nhất ở mọi $w\le7$. Khi đó báo cáo thẳng: "trained guidance does not show the exact mechanism".
- **E-A1.** Dự đoán: với $\dim L=1$, xác suất basin gần như không đổi theo $d$; với $\dim L=d$, nó giảm. Bị bác bỏ nếu cả hai trường hợp đều giảm theo $d$.
- **E-B.** Dự đoán: $\lvert Z_1-x^i\rvert\approx\lvert\hat x_1-x^i\rvert$ tại thời điểm lưới cuối.

**Lưu ý server dùng chung.** Chạy trên CPU khi được (`CUDA_VISIBLE_DEVICES=`). Các run GPU chỉ khởi chạy rồi đọc kết quả khi xong, không theo dõi liên tục. Kiểm kê checkpoint CIFAR ($h=4,6$, `intervention_cifar_pilot`) và mạng unconditional EXP-1 trước khi lên lịch.

### Lý thuyết (chứng minh do tác giả viết; verifier chỉ là kiểm tra thêm)

| Ưu tiên | ID | Nội dung | Vì sao | Chi phí ước lượng |
|---|---|---|---|---|
| 1 | ~~T-B~~ → **T1** | Thay bằng định lý dominance (Mục 9), đã qua vote. Tổ hợp hai prior là trường hợp riêng 1-dominant | — | Xong (bản nháp) |
| 2 | ~~T-A~~ → **T2** | Thay bằng định lý bất biến theo schedule (Mục 9), đã qua vote. Mọi đường Gaussian quy về cùng một phương trình | — | Xong (bản nháp) |
| 3 | ~~T-C~~ | Hệ quả của T1: label smoothing với kernel có dấu là một tổ hợp có dấu, nên giữ atom nếu trọng số trung tâm trội, và có thể rời atom nếu không trội | — | Xong (hệ quả) |
| — | ~~T-D~~ | Không theo đuổi: chứng minh scaling của basin theo $\dim L$ cho cấu hình tổng quát. Để thực nghiệm E-A1 trả lời | — | — |

---

## 5. Đề xuất sửa văn bản (tiếng Anh, dán được)

**TE1. Abstract, bản hội nghị** (dùng T1–T3 sau khi tác giả đã kiểm):
> Classifier-free guidance, label noise and coarse label resolution are routinely applied to conditional flow-matching and diffusion models, but it is unclear which of them can move samples off the training set when the model fits its objective exactly. We answer with one criterion on the coefficients of the combined exact field. If the coefficients are convex, or one coefficient outweighs all others in absolute value, every trajectory ends on a training example for almost every initial point; this covers label noise, label averaging, guidance with any bounded schedule of bounded variation, and guidance with several negative prompts. Every non-dominant combination with a negative coefficient converges, for some data in dimension two or more, to a circumcentre of training examples with positive probability: a blend, not a new sample. Guidance applied to a label-averaged field is the simplest case, with the exact threshold $1/\sinh^2B$ on two examples. The statements hold for every Gaussian noise schedule that starts from pure noise, and the off-support endpoints persist under learned errors whose scaled size stays below a fixed threshold. [One sentence of E-A1/E-A2 results.]

**TE2. Dòng 112** (W2):
> Before: "a network that resolves labels only coarsely averages the field over nearby labels"
> After: "a network that resolves labels only coarsely can be modelled as an average of the field over nearby labels, with positive or, for kernel-type learners, signed weights"

**TE3. Dòng 139–142** (W3):
> After "…from a learned field whose endpoint prediction does not converge.", add: "The new endpoints are circumcentres of training examples, such as the midpoint of two of them: blends, not samples from the data distribution."

**TE4. Sau Prop 4.8 hoặc trong phần Limitations** (W4, thêm sau khi có E-A1):
> "The basin of Theorem 4.9 is a neighbourhood in the tie coordinates only, so its size depends on the number of tied atoms rather than on $d$; Table 9 shows the full-dimensional ties, the least favourable case."

**TE5. Sec 4.3, trước Theorem 4.7:**
> "The configuration is a query halfway between two training labels, the situation of a held-out condition, where the averaged priors favour different atoms."

**TE6. Figure 1** (W8): thay hình minh hoạ hard collapse bằng hình bốn panel:
- (a) guidance riêng: atom;
- (b) label averaging riêng: atom;
- (c) ghép hai can thiệp: basin ở trung điểm, kèm $F_w$;
- (d) mẫu CIFAR dạng blend từ E-A2.

Hình hiện tại chuyển xuống Sec 6.1 hoặc appendix.

**TE7. Tiêu đề** (tuỳ chọn, cho hội nghị): *When Do Guided and Averaged Flows Leave the Training Set?*. Với T1: *A Dominance Criterion for Atomic Endpoints of Guided and Averaged Conditional Flows*.

---

## 6. Kế hoạch theo venue

### 6.1 Thông tin venue (kiểm lại trên trang chính thức trước khi nộp)

| Venue | Hạn nộp | Giới hạn | Yêu cầu riêng | Nguồn |
|---|---|---|---|---|
| ICLR 2027 | **Đã qua** (25/9/2026) | 9 trang | — | iclr.cc |
| Workshop ICLR 2027 | Thường vào tháng 2/2027 (non-archival) | Thường 4–9 trang | Kiểm chính sách dual submission của ICML với workshop non-archival | — |
| **ICML 2027** | Khoảng 22–28/1/2027 (tracker không chính thức, CFP chưa ra) | 8 trang (theo ICML 2026) | Impact statement (theo các năm trước) | trackers |
| **NeurIPS 2027** | Khoảng 14/5 (abstract) và 21/5/2027 (ước lượng) | 9 trang (theo năm trước) | Paper checklist bắt buộc | trackers |
| **ICLR 2028** | Khoảng cuối tháng 9/2027 | 9 trang | Review công khai trên OpenReview; kiểm quy định reciprocal reviewing và công bố dùng LLM | — |
| **TMLR** | Liên tục | Không giới hạn cứng; trên 12 trang main thì không áp thời hạn review 2 tuần | Template TMLR; không nộp song song; tiêu chí là claims và evidence cộng với việc có độc giả quan tâm | jmlr.org/tmlr |
| J2C track | Theo từng hội nghị | — | Bài TMLR cần **J2C, Featured hoặc Outstanding certification** | icml.cc, neurips.cc, iclr.cc |

### 6.2 Lộ trình A (đề xuất): hội nghị trước, TMLR làm lưới an toàn

| Giai đoạn | Thời gian | Việc | Đầu ra |
|---|---|---|---|
| P0 | 21/10 – 3/11 | TE2, TE3, TE5; E-D; factcheck Q11; E-B trên EXP-1; phần tổng hợp của E-A1; kiểm kê checkpoint trên server; **tác giả kiểm T1–T3** (`docs/theory/new_theorems_2026-10-20.tex`) | Commit sửa văn bản; Fig E-B; số liệu E-A1 tổng hợp |
| P1 | 4/11 – 1/12 | E-A1 trên CIFAR thật; E-A2 trên EXP-1 rồi CIFAR (huấn luyện U-Net label dropout); E-T4 (thử nghiệm SDE); đưa T1–T3 vào paper | Kết quả E-A1/E-A2/E-T4; Sec 4 viết lại quanh T1 |
| **G1** | **1/12** | Quyết định (xem dưới) | — |
| P2 | 2/12 – 5/1 | Viết lại theo khuôn ICML 8 trang (cấu trúc ở 6.4); Figure 1 mới; abstract TE1; một vòng review nội bộ (`/ars-reviewer`); verifier kiểm thêm các kết quả mới | Bản ICML |
| P3 | 6/1 – hạn nộp | Đánh bóng; đăng ký abstract; impact statement; code ẩn danh; tuyên bố dùng AI (`/ars-disclosure`) | Nộp ICML |
| P4 | Cuối 3/2027 | Rebuttal ICML (dùng Mục 3 làm khung) | — |
| P5 | Khoảng đầu 5/2027 | Nếu reject: sửa theo review, thêm 1 trang và checklist, nộp NeurIPS (khoảng 2 tuần sau quyết định ICML; bản 9 trang nên chuẩn bị sẵn từ tháng 4) | Nộp NeurIPS |
| P6 | Khoảng cuối 9/2027 | Nếu NeurIPS reject: nộp ICLR 2028 (dùng `iclr-writing-style`) hoặc TMLR | — |

**Gate G1 (1/12):**
- **E-A2 dương tính** (có chữ ký circumcentre trên mạng), hoặc **E-A1 cho thấy khối lượng off-atom đáng kể ở quy mô ảnh**: đi tiếp lộ trình A.
- **Cả hai âm tính**: bản hội nghị thiếu cầu nối. Chuyển sang lộ trình B, đưa kết quả âm vào paper như phân tích ("exact composition is a property of the target that trained guidance does not reproduce").
- **Tác giả tìm thấy lỗ hổng trong T1–T3**: định lý nào hỏng thì bỏ khỏi headline; lộ trình A vẫn đứng được với các kết quả còn lại.

### 6.3 Lộ trình B (an toàn): TMLR rồi J2C

1. P0 cộng E-B cộng E-D (khoảng 3 tuần). Cắt main text còn tối đa 12 trang: chuyển Fig 7 và Table 2 xuống appendix, gộp Prop 3.1 và Cor 3.5 vào phần văn.
2. Nộp TMLR vào giữa tháng 11/2026 (hoặc tháng 12 nếu đến từ G1). Quyết định có thể vào khoảng Q1/2027. TMLR không đảm bảo thời hạn này.
3. Khi accept, xin J2C certification, rồi gửi yêu cầu trình bày ở ICML hoặc NeurIPS 2027 qua Journal-to-Conference track.
4. Hạn chế: không được nộp ICML trong lúc đang review ở TMLR, và certification không chắc chắn được cấp.

**Vì sao đề xuất A.** Về độ chặt chẽ, phần lý thuyết đã đạt chuẩn hội nghị. Phần còn thiếu là một cầu nối sang mạng đã huấn luyện, chủ yếu là việc CPU/GPU trong khoảng 6 tuần. TMLR vẫn luôn mở, và bản đã củng cố cũng làm tăng khả năng được nhận ở TMLR. Chi phí của A là thời gian: nếu cả ICML và NeurIPS đều reject thì đến tháng 9/2027 mới nộp TMLR. Nếu ưu tiên của bạn là có công bố trong Q1/2027, hãy chọn B.

### 6.4 Cấu trúc 8 trang cho ICML (từ đó lên 9 trang cho NeurIPS/ICLR)

| Trang | Nội dung | Từ bản hiện tại |
|---|---|---|
| 1–1.5 | Abstract TE1, Intro, **Figure 1 mới** (TE6), danh sách đóng góp, Table 1 (rút gọn) | Sec 1 |
| 1.5–2.25 | Setup và tham chiếu exact: Prop 3.2 và Thm 3.4 gộp trong 0.75 trang; Prop 3.1, Cor 3.5, Prop 3.6 viết thành văn | Sec 2–3 |
| 2.25–5.5 | Đoạn proof strategy cộng Fig 2 (thu nhỏ); **T1 (dominance) làm định lý chính**, Thm 4.6 thành hệ quả, giữ Thm 4.1 cho mixture tổng quát; Thm 4.7 cộng Fig 6 làm ví dụ không trội; Thm 4.9 cộng Cor 4.10; một câu về T2 | Sec 4 |
| 5.5–6.25 | Thm 5.1 cộng E-B (một hình) | Sec 5 |
| 6.25–7.5 | E-A1 và E-A2 (hình chính); hard collapse trên EXP-1/CIFAR gói trong một đoạn và một hình nhỏ | Sec 6 |
| 7.5–8 | Related work rút gọn (bản đầy đủ đưa vào appendix); Limitations | Sec 1, 7 |

**Chuyển xuống appendix:** Prop 4.2, Prop 4.3 (giữ một câu), Cor 4.5, Prop 5.2, Fig 3/4/5/7, Table 2, Prop 4.8 (giữ một câu và tham chiếu).
**NeurIPS** (+1 trang): đưa lại Fig 5 (kernel tracking) và Related work đầy đủ hơn; thêm checklist.
**ICLR:** abstract phải đọc được như một snippet trên OpenReview, và nên có đoạn hướng dẫn reviewer "what to verify".

---

## 7. Không nên làm

- **Không** đưa lại audit $h_{\mathrm{eff}}$, calibration hay mô hình spectral-bias. Các gate G1–G3 của kế hoạch ngày 11/10 đều đã kích hoạt, và đưa chúng lại sẽ mở lại các phản biện cũ.
- **Không** thêm proposition về population minimiser mà không gắn với can thiệp. Reviewer đã đọc phần đó là kiến thức đã biết.
- **Không** claim ánh xạ endpoint trùng với đường tuyến tính cho sampler bắt đầu ở mức nhiễu hữu hạn (EDM, DDPM rời rạc; Q7), "hyperbolicity là generic" (Q12) hay "composition giải thích 38%" (Q8) trước khi có chứng minh hoặc số liệu.
- **Không** cite các tài liệu ở Q11 khi chưa factcheck.
- **Không** nộp TMLR song song với ICML.

## 8. Nguồn về venue (tra ngày 20/10/2026)

- ICLR 2027 Author Guidelines: https://iclr.cc/Conferences/2027/AuthorGuidelines
- ICLR 2027 Call for Papers: https://iclr.cc/Conferences/2027/CallForPapers
- ICML 2026 Author Instructions (giới hạn 8 trang): https://icml.cc/Conferences/2026/AuthorInstructions
- Ngày ICML 2027 (ước lượng, không chính thức): https://www.opencurious.com/ai-conference-deadlines/icml-2027, https://trybibby.com/conference-deadlines/icml-2027
- Ngày NeurIPS 2027 (ước lượng, không chính thức): https://www.opencurious.com/ai-conference-deadlines/neurips-2027
- Hướng dẫn tác giả TMLR: https://jmlr.org/tmlr/author-guide.html; hướng dẫn reviewer TMLR (ngưỡng 12 trang): https://www.jmlr.org/tmlr/reviewer-guide.html
- Journal-to-Conference track: https://icml.cc/public/JournalToConference, https://neurips.cc/public/JournalToConference, https://iclr.cc/public/JournalToConference

## 9. Lý thuyết bổ sung (21/10/2026)

Các chứng minh nằm trong `docs/theory/new_theorems_2026-10-20.tex` (7 trang, biên dịch được). Chúng được soạn trong session này:
- Với mỗi định lý, 2–3 solver độc lập viết chứng minh đầy đủ, chỉ bằng suy luận, không chạy code.
- Bản chứng minh đã làm sạch được đưa cho các verifier với context mới. Các verifier tấn công theo nhiều góc: adversarial tổng quát, bóc tách bổ đề một dòng, kiểm đặc tả và giả thiết, và lượt kiểm tuần tự.
- Ngưỡng: 4 phiếu đồng ý thì xác nhận, 2 phiếu phản đối thì bác bỏ.

**Đây là bản nháp: tác giả cần tự kiểm từng dòng trước khi đưa vào `main.tex`.**

| ID | Định lý | Mới ở đâu | Ứng dụng | Vote |
|---|---|---|---|---|
| **T1** | **Dominance.** (A) Nếu tại mọi $t$ hệ số $c(t)$ là lồi hoặc $\gamma$-trội ($c_j\ge\sum_{k\ne j}\lvert c_k\rvert+\gamma$), với schedule BV bị chặn, thì endpoint là atom a.s. với mọi dữ liệu và mọi prior dương. (B) Với $d\ge2$, mọi $c$ hằng, không trội và có hệ số âm đều rời atom với một số dữ liệu: có xác suất dương kết thúc ở một circumcentre. | Bao gồm Thm 4.6 và trường hợp hữu hạn của Thm 4.1, và giải thích Thm 4.7 như một ví dụ không trội. Thm 4.1 vẫn giữ cho mixture tổng quát, vì Prop 4.2 cần nó. Phủ được schedule guidance đổi dấu, vốn đang ghi là open trong Limitations. Với hữu hạn field trong $d\ge2$, có điều kiện cần và đủ, chỉ trừ biên. | CFG với mọi schedule BV bị chặn; nhiều negative prompt; guidance ngược một field đã trung bình hoá (đều giữ atom). Guided label averaging giữ atom nếu $\lambda_{\max}>(1+2w)/(2(1+w))$. Phép AND của composable diffusion giữ atom nếu tổng các trọng số còn lại $<\frac12$. Khi không trội, T1(B) chỉ cho ví dụ rời atom với prior tự do; với prior có cấu trúc (trọng số nhãn, prior unconditional uniform) thì chỉ có Thm 4.7 cho trường hợp $\lambda=(\frac12,\frac12)$. | CORRECT 4/4 (3 solver độc lập đều ra lời giải đầy đủ) |
| **T2** | **Bất biến theo schedule.** Mọi đường Gaussian $\alpha_tX_1+\sigma_tX_0$, viết theo $y=x/\alpha_t$ và $\lambda=\log(\alpha_t/\sigma_t)$, đều cho cùng phương trình $dy/d\lambda=\bar m-y$. Với các đường bắt đầu từ nhiễu thuần ($\alpha_0=0$), ánh xạ endpoint trùng với của đường tuyến tính: $x(t)=(\alpha_t+\sigma_t)\,x_{\rm lin}(\alpha_t/(\alpha_t+\sigma_t))$. | Cơ chế đã biết (Karras et al. 2022). Phần mới là mọi kết quả endpoint của paper, kể cả guided và averaged, đều chuyển sang được. | Trả lời Q7/W5: với rectified flow và VP chạy tới $\alpha=0$, mọi kết quả chuyển sang. Với EDM ($\sigma_{\max}$ hữu hạn) và DDPM rời rạc ($\alpha_T>0$), chỉ các phát biểu "atom a.s." và "xác suất dương" chuyển sang; trọng số endpoint chính xác thì không. Guidance cộng trên $\varepsilon$, score hay $x$ với tổng hệ số bằng 1 đều cho cùng một field. | CORRECT 4/4 |
| **T3** | **Off-support sink bền với lỗi học.** Tại một sink $\Gamma(\xi^\star)\prec0$ của Thm 4.9, mọi field $v+\Delta$ với $(1-t)\lvert\Delta\rvert\le\eta_0$ trên một vùng ống kết thúc trong khoảng $\limsup(1-t)\lvert P_{L^\perp}\Delta\rvert$ quanh $z$, với xác suất dương. Theo hướng tie, sai số bị nén theo hệ số $1/\beta$. | Cầu nối đầu tiên từ composition sang mạng đã huấn luyện. Sai số endpoint nhỏ hơn ở atom (chỉ còn theo hướng pháp tuyến), nhưng cỡ lỗi cho phép $\eta_0$ co lại theo khe phổ $\lambda$, nên tiến về 0 gần ngưỡng $w_c$. | Dự đoán blend vẫn sống sót trong CFG đã huấn luyện, nếu lỗi dự đoán endpoint nhỏ. Được kiểm bởi E-A2 cùng E-B. | CORRECT 4/4 |
| T4 | **Giả thuyết:** sampler ngẫu nhiên có churn không tắt dần theo log-SNR sẽ xoá các endpoint off-support. | Có heuristic, chưa có chứng minh. | Nếu đúng: blend là đặc trưng riêng của ODE sampler. | Chưa chứng minh |

**Chưa vote (chỉ một solver đưa ra; cần kiểm trước khi dùng):**
- Hằng số biến phân $\kappa(c)=B/(1-B)$ khi $B\le\frac12$, và $=1+C-(A-B)_+^2/C$ khi $B\ge\frac12$.
- Trong $d=1$ tiêu chí thay đổi: $c=(\tfrac7{20},\tfrac7{20},\tfrac7{20},-\tfrac1{20})$ không trội nhưng vẫn giữ atom trên đường thẳng. Mọi $c$ không trội có tối đa hai hệ số dương thì rời atom ngay với hai atom.

**Biên còn mở:** $\max_kc_k=\lVert c\rVert_1/2$, schedule có biên dominance tiến về 0, và schedule không bị chặn.

**Thí nghiệm mới:**
- **E-T4** (CPU, vài phút): chạy Euler–Maruyama trên exact field của Thm 4.7 ($B=2$, $w=5w_c$), churn $\zeta\in\{0,0.1,0.5,1\}$, gap $10^{-2}$ đến $10^{-6}$. Dự đoán: khối lượng ở trung điểm về 0 khi gap giảm, với mọi $\zeta>0$.
- **E-A1 bổ sung:** chạy một cặp hệ số trội và không trội có cùng $\lVert c\rVert_1$ trên cùng dữ liệu, để minh hoạ T1.

**Vị trí trong paper:**
- T1 thành định lý chính của Sec 4. Thm 4.6 thành hệ quả. Thm 4.1 vẫn giữ cho mixture tổng quát, vì Prop 4.2 cần nó. Thm 4.7 là ví dụ không trội tường minh.
- T2 là một mệnh đề ngắn ở Sec 2, chứng minh trong appendix.
- T3 đặt ở Sec 5, cạnh Thm 5.1.
- T4 đặt trong Limitations, kèm kết quả E-T4.
