# Kế hoạch tách thành 2 bài (2026-11-21)

Nguồn hiện tại là `paper/main.tex`. Lý do tách và các mốc thời gian nằm trong `docs/review/acceptance_strategy_2026-11-20.md`.

Nguyên tắc chung:
- Mỗi bài có một thông điệp riêng.
- Bài B dẫn chiếu bài A (bản arXiv) cho mọi kết quả về exact field, và không chứng minh lại các kết quả đó.
- Không có định lý nào xuất hiện như một đóng góp ở cả hai bài. Làm vậy để tránh bị coi là thin slicing hoặc dual submission.

---

## Bài A: lý thuyết, nhắm TMLR (rồi J2C để được trình bày tại NeurIPS 2027 hoặc ICLR 2028)

**Thông điệp.** Can thiệp nào ở phía sampler giữ được endpoint của exact conditional field trên training set, và tổ hợp nào phá vỡ điều đó.

**Tiêu đề nháp.** *Which Sampler Interventions Keep a Conditional Flow on Its Training Set?*

| Thành phần | Lấy từ `main.tex` |
|---|---|
| Setup, exact reference | Sec. 2–3: Prop projection, collapse, kernel-field; Thm endpoint; Cor zerobw; Prop atomicity |
| Đóng góp 1: atomicity | Template hai bước (Lemma conv, Lemma volume); Thm posmix; Prop filtered, hyperplane; Prop cfgatom; Cor negcfg; **Lemma signedconv**; Thm schedule |
| Đóng góp 2: composition | Thm composition; Prop composition-open; định luật gần ngưỡng (App. threshold-scaling) |
| Đóng góp 3: tiêu chí phổ | Thm spectral, Cor spectral-threshold. **Đưa lên main text** |
| Giới hạn học được | Prop regular, Prop bottleneck, Prop tgtnoise |
| So sánh với các bài trước | App. comparison với Liu et al. **Đưa phần chính lên main text** |
| Kiểm chứng số | Stress test exact-field, near-tie, Table composition, Table spectral, cặp ảnh CIFAR, learned composition (asinh) |
| Hình | `fig_unrolled` (chỉ (a)–(c), cần tách hình), `fig_composition`, `fig_learned_composition`, `fig_cifar_composition`, `fig_intervention_validation`, proof template, `fig_flow_portrait` (c, d) |

**Việc mới cho bài A** (ước tính vài tuần, chủ yếu là viết và tính toán rẻ):
1. Positive control cho stress test: cho composite với w = 2w_c chạy qua cùng pipeline RK4 (R1 W4).
2. Nối tiêu chí phổ với các tổ hợp có dấu dùng trong thực tế: negative prompt, compositional/multi-prompt CFG, autoguidance. Chạy exact field với từ 3 field trở lên, gồm cả trường hợp bài đã nói là "fails for some signed combinations".
3. Remark về tính generic của giả thiết Thm spectral(c) (R1 W7).
4. Tách Lemma lp đã viết lại (Lipschitz) ra thành phát biểu đầy đủ; phần này đã sửa.
5. Viết lại Related Work: Bertrand, Biroli, Bonnaire, Kim et al., Jain et al., Bradley & Nakkiran, Pham et al., Aithal et al.
6. Abstract khoảng 150–200 từ, gồm 3 đóng góp.

**Bỏ khỏi bài A:** Thm transfer, Thm relerr, Prop trap, Prop heun, toàn bộ phần EDM, EXP-1/CIFAR collapse của trained net, kernel tracking. Những phần này chuyển sang bài B.

---

## Bài B: cơ chế, nhắm NeurIPS 2027 (loại "General")

**Thông điệp.** Sampler đã train chọn ảnh sớm, còn việc có landing lên ảnh đó hay không được quyết định muộn, bởi độ co tương đối (late relative contraction) của learned field.

**Tiêu đề nháp.** *Trained Samplers Choose Early and Land Late*

| Thành phần | Lấy từ `main.tex` |
|---|---|
| Nền | Prop collapse, kernel-field, Thm endpoint: phát biểu lại ngắn gọn, cite bài A |
| Lý thuyết | Thm transfer, Prop localtransfer, Prop loss-no-certificate, Thm risktransfer, **Thm relerr**, Prop trap, **Prop heun** |
| Thực nghiệm đã có | EXP-1 collapse, CIFAR DDPM collapse, kernel tracking, measured transfer (App. C), toàn bộ Sec. EDM |
| Hình | `fig_intuition`, `fig_landscape`, `fig_unrolled` ((d), (e)), `fig_edm_clocks`, `fig_heun`, `fig_exp1_collapse`, `fig_cifar_collapse`, `fig_kernel_tracking` |

**Việc mới cho bài B** (nhiều tháng, phần lớn là GPU), sắp theo mức ưu tiên:
1. Swap exact→net trên mọi model. Dữ liệu đã có trong `results/n3_followup_*`.
2. Can thiệp vào cửa sổ σ do ϱ chỉ ra, và **dự đoán trước** tỉ lệ memorization.
3. Lưới N ∈ {500, 1k, 2k, 5k} × 3 seed, tách subset seed khỏi training seed, thêm một model có augmentation. So sánh với Bonnaire et al.
4. CFG trên model thật: train EDM với class dropout, quét w, thử guidance interval và delayed guidance.
5. Giá trị gia tăng so với baseline NN: logistic regression, ΔAUC, LRT.
6. Một bước tăng quy mô: CIFAR-10 đầy đủ hoặc ImageNet-64, có một model train bằng CFM loss.
7. Định vị so với Bertrand (generalization "sớm"), Biroli (speciation/collapse) và Kinetic-FM ("late soft landing").

---

## Thứ tự làm

1. **Bài A trước.** Tạo `paper_theory/` từ `main.tex`: cắt các phần thuộc bài B, đưa spectral theorem và phần so sánh Liu lên main text, làm các việc mới 1–6. Đăng arXiv rồi nộp TMLR.
2. **Bài B song song.** Tạo `paper_mechanism/`, chạy thí nghiệm theo thứ tự 1 → 5, viết khi có kết quả. Nộp NeurIPS 2027 (khoảng tháng 5/2027; cần kiểm tra khi CFP ra).
3. `paper/main.tex` giữ nguyên làm bản gốc tham chiếu, không nộp bản này.

## Những điểm cần tác giả quyết định
- Bài A có giữ learned composition (network nhận asinh input) không? Phần này cho thấy lý thuyết là kiểm chứng được; mình nghiêng về giữ.
- Kernel tracking (label smoothing so với tr Cov_h trên trained net) để ở bài B hay bài A? Mình nghiêng về bài B, vì đây là phép so sánh learned với exact.
- Đăng arXiv bài A trước khi nộp bài B có ảnh hưởng gì đến tính ẩn danh của bài B không? Theo các quy định đã tra, NeurIPS và ICLR cho phép preprint, nhưng bài B phải cite bài A như một bài của người khác.

---

## Tình trạng (cập nhật 2026-11-21)

Bài A đã dựng xong trong `paper_theory/` (chi tiết ở `paper_theory/README.md`). Các việc mới:

1. Positive control cho stress test: **xong**. Không có source nào trong 4096 bị phân loại sai so với basin chính xác.
2. Tổ hợp có dấu với từ 3 field trở lên: **xong**.
   - Cor. twofields: mọi tổ hợp của 2 field đều atomic.
   - Prop. twoatom: điều kiện cần cho blend tại tie hai atom.
   - Phase diagram, cùng xác suất basin chính xác cho conjunction và negative prompt.
3. Remark về tính generic cho Thm spectral(c): **xong** (Remark rem:generic).
4. Lemma lp dạng Lipschitz: **xong**, đã có trong bài A.
5. Related Work: **xong**, 10 trích dẫn mới đã xác minh, cộng Guillemin & Pollack.
6. Abstract: đã viết lại theo câu chuyện "hai field không blend, ba field có thể". Bản hiện tại dài khoảng 230 từ, dài hơn mức 150–200 từ của kế hoạch.

Còn lại: compile, xem PDF, và tác giả tự kiểm tra ba kết quả mới (do mô hình soạn).
