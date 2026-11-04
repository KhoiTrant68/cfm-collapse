# Reviewer defense cho bản ICLR — 4/11/2026

Phạm vi: bản ICLR build từ `paper/main_iclr.tex` (cùng nguồn `paper/main.tex`, nhánh `\ificlr`),
working copy chưa commit ngày 4/11/2026. Đây là đánh giá claim–evidence từ góc nhìn reviewer,
không phải kiểm chứng lại chứng minh và không phải khảo sát tài liệu đầy đủ. Không chạy huấn luyện
hay lấy mẫu mới. Bản trước: [reviewer_defense_2026-10-28.md](reviewer_defense_2026-10-28.md)
(nhắm TMLR); các mục ở đây chỉ ghi điều mới hoặc điều đổi mức độ khi chuyển sang ICLR.

## Kết luận ngắn

**Chưa đủ để kỳ vọng accept ở ICLR main track với bản hiện tại.** Lý thuyết chặt, phạm vi được
khoanh rõ, và số liệu kiểm được (429/429 kiểm tra). Nhưng reviewer ICLR sẽ hỏi trước hết "kết quả
này nói gì về mô hình đã huấn luyện", và bản hiện tại trả lời yếu hơn mức dữ liệu đang có cho phép:

1. Kết quả mạnh nhất về mô hình đã huấn luyện, **learned composition 1D/2D**
   (`results/learned_composition_20261021/`, `results/learned_composition_2d_20261021/`), **chưa
   có trong bài**. Phần Limitations còn ghi ngược lại: "The composition theorem has no
   trained-network counterpart yet" (`main.tex:975–976`), và trường sai số dọc quỹ đạo "have not
   measured" (`main.tex:971–972`), trong khi EXP-B đã đo.
2. Kết quả ngoài tập train (headline) dựng trên cấu hình hai atom và các cấu hình đồng cầu
   (cospherical). Ý nghĩa thực tiễn của threshold $1/\sinh^2B$ với sampler thật chưa được nối.
3. Phần thực nghiệm nhỏ (d ≤ 10; CIFAR N=2000, một mask, ba instance), không có benchmark chuẩn.
   Với một bài lý thuyết thì chấp nhận được, nhưng reviewer ICLR thường đòi nhiều hơn.
4. Bài nén rất chặt (8,999 trang): 9 định lý/mệnh đề trong phần chính, mọi chứng minh ở phụ lục,
   hình mở đầu đã chuyển xuống phụ lục. Dễ đọc là một rủi ro thật trên OpenReview.

Ước lượng định tính (không phải xác suất): bản hiện tại nằm quanh **borderline reject**; đưa
learned composition vào và sửa Limitations có thể kéo lên **borderline**. Khả năng accept còn
phụ thuộc vào reviewer có quan tâm lý thuyết memorisation hay không, điều không kiểm soát được.

Lưu ý lịch: hạn ICLR 2027 (25/9/2026) đã qua (`docs/plan/iclr_paper_plan.md`). Mục tiêu thực tế là
ICLR 2028, NeurIPS 2027 hoặc workshop ICLR 2027; cần style file và call for papers của venue đó.

## 1. Bảng điểm yếu

Mức độ là tác động dự kiến lên review, không phải nhận định rằng một định lý sai.

| ID | Loại | Điểm yếu và bằng chứng | Mức độ (ICLR) | Cách xử lý |
|---|---|---|---|---|
| V1 | Thực nghiệm | Learned composition đã chạy nhưng không có trong bài; Limitations nói chưa có. | **Rất cao** | Đưa vào §6 (xem E1, E2). |
| V2 | Thực nghiệm | Ở learned composition, CFM velocity chuẩn (`cfm_v`) **không** tái hiện attractor: occupancy 0.000 ± 0.000 tại B=1, w=2w_c (exact 0.406). Chỉ biến thể data prediction + feature rescale (`cfm_x_s`) tái hiện (0.401 ± 0.006). | Cao | Báo cả hai; đây là phát hiện, không phải điểm cần giấu. Ablation tách nguyên nhân đang thiếu (V3). |
| V3 | Thực nghiệm | `cfm_x_s` đổi đồng thời output (velocity → data), loss weighting và thêm input `asinh(tx/(1-t)^2)`. Hàng đợi ablation `cfm_v_s`, `cfm_x` (29/10) chưa có kết quả trong `results/`. | Cao | Lấy kết quả từ server nếu đã chạy xong; nếu chưa, ghi rõ là confound. |
| V4 | Kỹ thuật | Kết quả off-support (Thm 4.6) là cấu hình hai atom; tiêu chí phổ (Thm 4.8) chỉ được thử trên atom đồng cầu, không có phần dư off-tie. | Trung bình–cao | Giữ phạm vi; thêm một cấu hình exact có atom xa không tie (A6 của bản 28/10). |
| V5 | Trình bày | Ý nghĩa thực tiễn: reviewer sẽ hỏi composition có xảy ra trong sampler thật (label dropout + CFG) không. Bài chưa nói phép tổ hợp này tương ứng với thực hành nào. | Cao | Một câu ở Intro/§4.3 nối label averaging với cách mạng giải label thô (coarse label resolution), và nói rõ đây là cơ chế, không phải đo đạc trên sampler thương mại. |
| V6 | Trình bày | Bài nén: hình mở đầu (flow portrait) và hình proof template đã chuyển xuống phụ lục; 9 kết quả hình thức trong 9 trang. | Trung bình–cao | Ưu tiên thay một kết quả phụ bằng hình learned composition (E2) thay vì thêm chữ. |
| V7 | Kỹ thuật | Định lý transfer có điều kiện; với trường bị chặn, sai số scaled bằng độ lệch endpoint (bài đã tự nêu). EXP-B có số đo `K=m/r` nhưng chưa vào bài. | Trung bình | Thêm 1–2 câu EXP-B vào §5 hoặc phụ lục; sửa "have not measured". |
| V8 | Thực nghiệm | 38% off-atom CIFAR ở h=6 chưa giải thích. EXP-C cho thấy còn 0.254 ± 0.047 sau RK4 gap 1e-4 (run `heff` khác, không phải run 38%). | Trung bình | Ghi EXP-C như chẩn đoán: sai lệch còn lại sau khi tinh chỉnh solver/cutoff đã thử; không quy nhân quả. |
| V9 | Novelty | Memorisation của empirical minimiser đã biết; kernel/Nadaraya–Watson reading đã có. Đóng góp mới là hội tụ + basin null trên common finite support, composition và tiêu chí phổ. | Trung bình | Related work đã phân biệt; giữ câu "is therefore a reference, not a new identity". |
| V10 | Thống kê | Năm seed, mean ± population SD, nguồn ghép cặp chung giữa các seed. | Trung bình | Ghi rõ SD là giữa training seed với nguồn chung, không phải 5 ước lượng độc lập. |
| V11 | Thực nghiệm | Không có so sánh với benchmark/metric chuẩn (FID, v.v.). | Thấp–trung bình | Bài phân loại support, không đề xuất phương pháp; nói thẳng điều này. |
| V12 | Định dạng | Ethics và LLM-use statement đang là bản nháp; style file là ICLR 2027. | Thấp (nhưng bắt buộc) | Tác giả rà lại; đổi style khi venue đích phát hành. |

## 2. Câu hỏi reviewer dự kiến, xếp theo khả năng

Q1–Q2 thay đổi nhiều nhất so với bản 28/10 vì dữ liệu learned composition đã có. Câu trả lời
nháp viết bằng tiếng Anh để dùng trực tiếp trong rebuttal.

### Q1 — Rất cao: "Does the composition mechanism appear in trained networks?"
**Lý do:** headline là exact-field; reviewer ICLR muốn thấy mô hình học.
**Trả lời được:** Có, **nếu đưa learned composition vào bài**. Bảng B=1: exact 0.406 ở w=2w_c;
`cfm_x_s` 0.401 ± 0.006; `cfm_v` 0.000 ± 0.000. Tam giác 2D: exact ≈ 0.133–0.138; `cfm_x_s`
0.143 ± 0.004; `cfm_v` 0.000.
**Nháp:** "In matched two-atom and triangle experiments, a data-predicting network with a
rescaled input reproduces the exact midpoint mass across guidance strengths (0.401 ± 0.006 versus
0.406 at B=1, w=2w_c), while a standard velocity-parametrised CFM network places no mass there.
The mechanism is therefore learnable, but whether a given network realises it depends on the
parametrisation; we do not claim it occurs in every trained sampler."

### Q2 — Rất cao: "Why does the standard velocity network fail, and is the success due to the output, the loss weighting, or the extra input?"
**Lý do:** V2–V3.
**Trả lời được:** Một phần. `cfm_x_s` đổi ba thứ cùng lúc; ablation `cfm_v_s`/`cfm_x` chưa có
kết quả ở local.
**Nháp (nếu ablation chưa xong):** "The successful variant changes the output, the loss weighting
and the input together; we have not yet separated their contributions. The exact field has a
boundary layer of width $(1-t)^2$ near the tie, which a velocity output must resolve at scale
$(1-t)^{-1}$; this motivates the rescaled input but is not yet an attribution."
**Việc cần làm:** lấy kết quả `results/composition_ablation_20261029` từ server.

### Q3 — Cao: "What do the exact-field results say about trained generators in general?"
**Trả lời được:** Một phần (Thm 5.1, Prop 5.2 có điều kiện; EXP-1/CIFAR collapse ở cutoff hữu hạn).
**Nháp:** giữ nguyên Q1 của bản 28/10, thêm câu dẫn tới learned composition.

### Q4 — Cao: "Is this more than a two-point construction?"
**Trả lời được:** Có trong giả thiết đã nêu: Thm 4.8, Cor B.x (matrix threshold), Table 9 (tam
giác, simplex 9 đỉnh, chữ nhật, hộp 256 đỉnh), Prop 4.7 (nhiễu priors/weights/guidance).
**Nháp:** như Q3 bản 28/10; thêm learned 2D triangle như bằng chứng ngoài 1D.

### Q5 — Cao: "Where does guided label averaging occur in practice?"
**Lý do:** V5.
**Trả lời được:** Một phần, bằng lập luận: mạng giải label thô tương đương trung bình trường theo
label (Prop 4.2), và CFG được áp lên trường đó lúc lấy mẫu.
**Nháp:** "A network that resolves labels only coarsely implements a label-averaged field, and
classifier-free guidance is then applied to that field at sampling time; the composite is exactly
the object of Theorem 4.6. We identify the mechanism and its threshold; measuring how often
deployed samplers operate above it is outside our scope."

### Q6 — Cao: "What does the spectral criterion add over the trace test?"
**Trả lời được:** Có. Chữ nhật/hộp ở w=1 có trace âm nhưng là saddle, basin null (Table 9).

### Q7 — Cao: "Isn't the transfer bound tautological?"
**Trả lời được:** Có như một giới hạn đã tự nêu (§5); thêm EXP-B: K=m/r tăng từ ≈1.46 ở gap 0.5
lên ≈2.06e5 ở 1e-3, cho thấy sai số trên teacher law khác sai số dọc quỹ đạo học.

### Q8 — Trung bình–cao: "What explains the off-atom CIFAR samples?"
**Trả lời được:** Không về nhân quả; có về tương thích. EXP-C: 0.298 ± 0.058 (Euler 50, gap 1e-3)
→ 0.254 ± 0.047 (RK4, gap 1e-4); exact RK4 = 0.
**Nháp:** "Refining the solver and the cutoff on fixed checkpoints leaves about a quarter of the
samples off-atom, while the exact field at the same cutoff has none; the remaining discrepancy is
therefore not explained by the refinements we tried. We do not attribute it further."

### Q9 — Trung bình–cao: "Are the numerical endpoint classifications solver artifacts?"
Giữ nguyên Q9 bản 28/10 (stopping rule forward-invariant, lưu bốn lần thất bại adaptive). Thêm:
learned composition dùng ROS2 với hai tolerance; các lần đầu dùng RK4 bước cố định đã sai trên
sink cứng và bị loại.

### Q10 — Trung bình: "How novel is this relative to memorisation and score-mixing work?"
Giữ nguyên Q8 bản 28/10 (Liu–Zuazua và các tham chiếu trong Related work).

### Q11 — Trung bình: "Zero hits in d=8 at 1.1 and 2 w_c — is the basin there at all?"
Giữ nguyên Q6 bản 28/10: 0/2048 cho cận trên một phía 95% ≈ 0.00146 cho sự kiện số; định lý
khẳng định basin dương nhưng không chặn khối lượng Gaussian.

### Q12 — Trung bình: "Does leaving the training set improve sample quality?"
Không. Composition tạo thêm một atom ở circumcentre, không phải mẫu posterior hợp lệ; bài không
claim chất lượng.

## 3. Ablation nên trình bày

| Ưu tiên | Nghiên cứu | Trạng thái | Vị trí |
|---|---|---|---|
| A1 | Learned composition 1D: `cfm_v` / `cfm_x_s` / distillation / exact, quét w/w_c, B=1,2,3 | **Đã có**, đã kiểm lại 19,008 occupancy entries (bản 28/10 §4) | Phần chính: một hình thay thế một kết quả phụ |
| A2 | Learned composition 2D tam giác | Đã có | Phụ lục + một câu ở phần chính |
| A3 | Tách output / loss / feature (`cfm_v_s`, `cfm_x`) | Hàng đợi 29/10, kết quả chưa có ở local | Phụ lục; quyết định cách viết Q2 |
| A4 | Threshold exact B=1,2,3 | Đã có (Fig. composition) | Giữ ở phần chính |
| A5 | Saddle trace âm vs sink (chữ nhật/hộp) | Đã có (Table 9) | Phụ lục, đã có pointer |
| A6 | Cấu hình exact có atom xa không tie | Chưa chạy | Phụ lục; không cần huấn luyện |
| A7 | EXP-B (K=m/r) và EXP-C (CIFAR solver/cutoff) | Đã có | Phụ lục + một câu mỗi mục |

Distillation (`distill_x_s`) dùng exact posterior mean và mẫu boundary-layer: chỉ là positive
control, không được trình bày như thành công của CFM học từ dữ liệu.

## 4. Đề xuất sửa trước khi nộp

**Trạng thái 5/11/2026:** E1 (riêng phần composition), E2, E3, E4, E5 (riêng protocol learned
composition) và E6 (riêng learned composition) đã áp dụng cho cả TMLR và ICLR. Để giữ 9 trang, bản
ICLR chuyển Prop 4.7, hình exact composition, các câu nhiễu loạn tham số và pilot EXP-1 xuống phụ
lục. Câu "have not measured" (EXP-B) và EXP-C chưa đưa vào bài. Ablation `cfm_v_s`/`cfm_x` đang
chạy trên server (`results/composition_ablation_20261105`); khi có kết quả, sửa câu "these runs do
not separate them" ở §6.2 và câu tương ứng ở Limitations.

**E1. Limitations (`main.tex:970–976`).** Sửa hai câu đã lỗi thời. Thay "which we do not infer
from the loss and have not measured" bằng "which we do not infer from the loss; Appendix X reports
measurements along learned EXP-1 trajectories". Thay "The composition theorem has no
trained-network counterpart yet" bằng "A standard velocity-parametrised network does not reproduce
the composition basin in our two-atom and triangle experiments, whereas a data-predicting network
with a rescaled input does; which of these changes is responsible is not yet separated."

**E2. §6.2, đoạn "Guided label averaging".** Thêm học được vs exact: một hình hai panel (occupancy
theo w/w_c cho exact, `cfm_x_s`, `cfm_v` ở B=1; và tam giác 2D). Để giữ 9 trang, chuyển Prop 4.7
hoặc Thm 4.5 (guidance schedule) xuống phụ lục với pointer một câu, giống cách đã làm với Prop 5.2.

**E3. Intro, bullet thứ hai.** Thêm nửa câu: "a data-predicting network reproduces this basin in
controlled experiments, a standard velocity network does not (Section 6.2)".

**E4. §4.3 hoặc Intro.** Một câu nối composition với thực hành (Q5): label averaging là trường
của mạng giải label thô, guidance được áp lúc sampling.

**E5. Phụ lục thực nghiệm.** Thêm protocol learned composition (ROS2, hai tolerance, 2048 nguồn
ghép cặp, cutoff 1e-2–1e-5, bán kính 0.02/0.05/0.1), EXP-B và EXP-C, với nhãn "outside atom and
midpoint neighborhoods" thay cho "off all atoms" ở bảng 2D (bản đánh giá 28/10 §3, điểm 5).

**E6. Kiểm số.** `verify_paper_numbers.py` chưa bao phủ learned composition/EXP-B/EXP-C; thêm
kiểm tra cho các số mới trước khi đưa vào bài.

## 5. Kết quả âm nên giữ

- `cfm_v` không tái hiện basin: đây là phát hiện chính về khả năng học, không phải thất bại cần giấu.
- `cfm_v` ở B=3 có occupancy dương giả ngay cả dưới threshold (≈0.048 ± 0.083 ở w=0): giữ và giải
  thích là sai lệch của trường học, không phải basin exact.
- Bốn lần thất bại adaptive gần tie, 0/2048 ở d=8, 38%/25% off-atom CIFAR: giữ như trong bài.

## 6. Bằng chứng và giới hạn của lượt đánh giá này

Đã đọc: phần chính bản ICLR, `reviewer_defense_2026-10-28.md`, `worktree_reuse_assessment_2026-10-28.md`,
`composition_ablation_2026-10-29.md`, `results/learned_composition_20261021/SUMMARY.md`,
`results/learned_composition_2d_20261021/SUMMARY.md`. Số EXP-B/EXP-C lấy từ bản đánh giá 28/10,
không tính lại ở lượt này. Không chạy huấn luyện hay ODE mới; không kiểm chứng lại chứng minh;
không khảo sát tài liệu mới. `verify_paper_numbers.py`: 429 passed, 0 failed trên working copy.
