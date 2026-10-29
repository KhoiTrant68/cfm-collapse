# Những phần có thể dùng từ .claude/worktrees — 28/10/2026

> **Cập nhật sau merge, 29/10/2026:** `main` và `origin/main` đã chứa `a25bbfe` cùng bốn commit được liệt kê bên dưới. Các mô tả “chưa merge”, “chưa nằm trong main” và so sánh working copy là trạng thái tại thời điểm rà soát, không phải việc còn phải làm. Merge đưa các artifact thí nghiệm và sửa câu chữ vào repository; không đồng nghĩa mọi thí nghiệm đã được tích hợp vào nội dung paper. Các đường dẫn worktree trong JSON là provenance tại thời điểm kiểm tra, được giữ nguyên. Sau merge, 429 kiểm tra số liệu, 4 regression tests và build LaTeX đã đạt; đây không phải kiểm chứng lại toàn bộ chứng minh hay chạy lại thí nghiệm.

## Kết luận và đính chính

Worktree `phd-skills-reviewer-defense-5171d8` chứa các thí nghiệm learned composition 1D/2D, transfer và CIFAR chưa được đưa vào main. Vì vậy nhận định trước đây rằng chưa có learned-composition pilot chỉ đúng với nội dung main, không đúng với toàn bộ workspace. Không nên chạy lại pilot từ đầu.

Phần có giá trị nhất cho bài hội nghị là đối chiếu: exact composition có attractor ngoài tập train; mạng CFM velocity chuẩn trong các thử nghiệm này không tái hiện attractor; mạng dự đoán dữ liệu có thêm tọa độ boundary-layer thì tái hiện khá sát. Câu chuyện mới là điều kiện để mạng biểu diễn được cơ chế lý thuyết, bao gồm cả kết quả dương và âm.

Đây là rà soát khả năng tái sử dụng. Chưa merge/cherry-pick, chưa sửa manuscript hoặc file LaTeX đang mở, chưa huấn luyện hay chạy lại ODE.

## 1. Tình trạng Git

| Worktree | Tình trạng | Cách dùng |
|---|---|---|
| `paper-verification-2963f8` | HEAD `997b15a`, sạch; đã nằm trong main qua merge `f3beed4`/PR #32 | Không có commit mới cần mang sang. |
| `phd-skills-reviewer-defense-5171d8` | HEAD `a25bbfe`, có 4 commit chưa nằm trong main: `3549904`, `0f2b21c`, `f2eef6d`, `a25bbfe` | Nguồn dữ liệu và sửa manuscript cần xem xét. |

Worktree thứ hai có 3 thư mục untracked: hai thư mục EXP-1 seed 1001 và `results/learned_composition_20261021/cfm_v_sep_seed2/`. Không được coi mọi thư mục tồn tại là một run hợp lệ trong bộ kết quả cuối.

`docs/theory/new_theorems_2026-10-20.tex` trong worktree reviewer-defense trùng với bản đang mở. T1/T2/T3 không phải các định lý mới được phát hiện trong worktree này; chúng vẫn là bản nháp riêng, chưa tích hợp vào manuscript của worktree.

Git diff theo commit cho thấy manuscript thay đổi lớn so với main đã commit, nhưng so với working copy main hiện tại chỉ còn 55 dòng thêm/43 dòng bỏ. Cần đối chiếu với working copy hiện tại để bảo toàn thay đổi của tác giả.

## 2. Những kết quả dùng được

### A. Learned composition 1D — ưu tiên cao nhất

Nguồn: `results/learned_composition_20261021/`, cùng các script `learned_composition.py`, `learned_composition_exact.py`, `summarize_learned_composition.py`.

Protocol hiện hành: 2048 nguồn Gaussian chung, các cutoff 1e-2 đến 1e-5, các bán kính 0.02/0.05/0.1, ROS2 với hai tolerance; B=1,2,3, quét w/wc và các nhánh đối chứng. Có 5 seed cho cfm_v, cfm_v_tis, cfm_x_s, distill_x_s; 4 seed cfm_v_sep.

Tại B=1, w=2wc, cutoff 1e-5, bán kính midpoint 0.05:

| Trường | Tỉ lệ ở gần midpoint |
|---|---:|
| Exact, xác suất endpoint trong bảng | khoảng 0.406 |
| Exact trên các nguồn ghép cặp trong bảng | khoảng 0.407 |
| CFM velocity chuẩn | 0.000 ± 0.000 |
| Dự đoán dữ liệu + đầu vào rescale (`cfm_x_s`) | 0.4011 ± 0.0059 |
| Distillation control | 0.4072 ± 0.0000 |

Các số learned được tính lại từ `final_states.npz`. ± là population SD giữa training seeds; nguồn lấy mẫu chung nên không phải 5 phép ước lượng độc lập của xác suất Gaussian.

**Cách dùng:** một hình chính nối guidance → occupancy → Jacobian hoặc sai số boundary-layer. Giữ thất bại của CFM chuẩn cạnh kết quả thành công. Đây là bằng chứng về một kiến trúc cụ thể ở cutoff hữu hạn, chưa phải kết quả tổng quát cho mạng thông thường.

### B. Learned composition trên tam giác 2D — dùng làm kiểm tra ngoài 1D

Nguồn: `results/learned_composition_2d_20261021/`, `learned_composition_2d.py`, `summarize_learned_composition_2d.py`.

Tại w=2wc, cutoff 1e-5, bán kính 0.05: cfm_v có occupancy 0; cfm_x_s là 0.14336 ± 0.00421; distill_x_s là 0.14004 ± 0.00396. Reference exact báo khoảng 0.133 trên 4096 nguồn; trên 2048 nguồn ghép cặp khoảng 0.138. Khi so sánh paired phải dùng cùng tập nguồn, không đổi mẫu số giữa các cột.

Jacobian của cfm_x_s trong đơn vị profile gần −0.271 so với −0.268 của exact ở cuối, còn cfm_v tiến gần 0. Các số Jacobian này đọc từ summary và code tổng hợp, chưa được tái tính bằng autograd trong lượt này. Script 2D lấy trị riêng của phần đối xứng Jacobian learned; không nên gọi đó là toàn bộ phổ Jacobian của một trường learned bất kỳ nếu chưa kiểm phần phản đối xứng.

### C. EXP-B — dùng để giải thích vì sao loss chưa chứng nhận endpoint

Nguồn: `results/exp_b_transfer_20261022/`, 50 file JSON = 10 run × 5 checkpoint; `scripts/exp_b_transfer_exp1.py`.

Ở h=0, 200k bước, summary báo K=m/r tăng từ khoảng 1.46 tại gap 0.5 lên 2.06e5 tại 1e-3 và 1.97e7 tại 1e-4. Khoảng cách learned–teacher khoảng 0.636, còn biểu thức thay K bằng 1 chỉ khoảng 0.00652.

**Cách dùng:** bằng chứng thực nghiệm về sự khác nhau giữa sai số trên teacher law và sai số dọc learned trajectory. Không gọi biểu thức K=1 là một cận hợp lệ bị vi phạm: giả thiết để nó là cận đã không được xác nhận. Cũng không nói Minkowski tự động cho dấu bằng; nó cho bất đẳng thức, sự gần bằng là quan sát của các run này.

Các phép thử quả cầu ở h>0 không cung cấp chứng nhận uniform trong không gian và tới t=1. Cần ghi rõ phạm vi mẫu, lưới, run và cutoff, thay vì nói mệnh đề được kiểm nghiệm hoặc tiền đề thất bại trên mọi network.

### D. EXP-C — dùng làm diagnostic CIFAR, giữ đúng provenance

Nguồn: `results/exp_c_cifar_transfer_20261022/`, `scripts/exp_c_cifar_transfer.py`.

Đã tính lại từ JSON 3 run h=6, theo 2000 ảnh train của từng run:

| Protocol | Off-atom theo tiêu chí d1/d2 |
|---|---:|
| Learned Euler 50, gap 1e-3 | 0.29774 ± 0.05825 |
| Learned RK4, gap 1e-3 | 0.25434 ± 0.04726 |
| Learned RK4, gap 1e-4 | 0.25391 ± 0.04735 |
| Exact RK4, gap 1e-3 | 0 |

Các kết quả cho thấy sai lệch với reference còn lại sau các refinement đã thử; không phải chứng minh cutoff đóng góp bằng 0 hay phép phân rã nhân quả cộng tính. Exact ở thời gian hữu hạn được phân loại on-atom theo ngưỡng, không phải đúng bằng atom.

Không dùng các run `heff` này để tuyên bố đã giải thích chính xác con số 38% của run `exp3_cifar_ddpm_h6` khác, không còn checkpoint. 48 điều kiện × 16 nguồn/run ở EXP-C cũng khác M=256 trong phép đo cũ.

### E. Sửa toán và câu chữ — dùng có chọn lọc

Nguồn: `docs/review/main_tex_fixes_2026-10-25.patch`, `docs/audit/independent_audit_2026-10-21.md`, `docs/review/math_evaluation_2026-10-25.md`, các commit `f2eef6d`/`a25bbfe`.

Các sửa hữu ích gồm: điều kiện h>0 cho mật độ đầy đủ; bổ sung log(p_i/p_i') vào logit trên tied atoms; làm rõ phát biểu graph của bổ đề Lyapunov–Perron; giữ điều kiện prior dương và identifying label trong câu tóm tắt; sửa “prediction does not converge” thành không hội tụ về training example.

Đây là các sửa cần đối chiếu từng hunk với working copy main, không chép đè cả manuscript. Báo cáo verifier cũ là tài liệu hỗ trợ; lượt này không xác nhận lại toàn bộ chứng minh.

## 3. Điểm mới cần xử lý trước khi dùng làm bằng chứng hội nghị

1. **Ablation còn thiếu:** `cfm_x_s` đồng thời đổi output từ velocity sang data prediction, đổi loss từ velocity MSE sang data MSE, và thêm `asinh(tx/(1-t)^2)`. Hai loss có cùng minimizer không giới hạn theo từng (x,t,y), nhưng trọng số thời gian và bài toán tối ưu hữu hạn khác nhau. Chưa thể kết luận nguyên nhân duy nhất là đầu vào rescale. Bổ sung tối thiểu data prediction không có s và velocity prediction có s; khi cần tách loss weighting, thêm control được weighting phù hợp.
2. **Distillation là positive control:** code dùng exact posterior mean và cả mẫu boundary-layer. Không mô tả nó như thành công của CFM chỉ học từ dữ liệu thông thường.
3. **Run legacy không được trộn:** `cfm_v_sep_seed2` chưa tracked, không có metadata ROS2/rtol, ghi 16384 nguồn trong khi protocol hiện hành dùng 2048. Giữ riêng, xác minh/tái đánh giá nếu muốn đưa vào aggregate. Không tự động nâng bảng 4 seed lên 5.
4. **Solver là một phần bắt buộc của protocol:** các lần đầu dùng fixed-step RK4 đã sai trên sink cứng. Dùng output ROS2 cuối, giữ test exact và sửa time embedding float64 đi cùng script. Không dùng bảng hoặc output cũ chỉ vì tên run giống nhau.
5. **Nhãn cột 2D gây hiểu nhầm:** `learned off all atoms` được code tính bằng class==4, loại cả midpoint class==3. Vì midpoint cũng ngoài training atoms, nên đổi nhãn thành “outside atom and midpoint neighborhoods”, hoặc tính lại đúng off-training-atom rate. Không dùng nguyên nhãn hiện tại.
6. **Nhận xét nhân quả trong report cũ quá mạnh:** các câu “truncation contributes nothing”, “remainder is the learned-field error”, và “the theory says why the architecture succeeds” cần thu hẹp theo những controls thực sự đã chạy.

## 4. Kiểm tra độc lập trong lượt này

- 39 run ROS2 hiện hành có `summary.json`, `final_states.npz` và `field.pt` trên đĩa.
- Tái tính **19,008 occupancy entries** từ saved states ở 3 bán kính và 4 cutoff: **0 sai lệch** với JSON. Đây là kiểm tra tổng hợp dữ liệu, không chạy lại inference hoặc xác nhận solver.
- 300 control arm keys không có arrays endpoint theo chính sách lưu có chủ đích của script; không tái tính được các entry đó từ arrays trong lượt này.
- Có một legacy run untracked đã loại khỏi kiểm tra chính. Checkpoint tồn tại không đồng nghĩa đã được Git đóng gói hoặc có provenance hoàn chỉnh.
- Tái tính các mean/SD CIFAR nói trên từ JSON của ba run từng bandwidth. EXP-B được kiểm inventory và đọc protocol/summary, chưa tái dựng metric từ quỹ đạo thô.
- Chi tiết và hash JSON từng run: `docs/review/worktree_evidence_check_2026-10-28.json`.

## 5. Kế hoạch cập nhật

Ưu tiên 1: đưa EXP-A 1D/2D cùng protocol và thất bại của CFM chuẩn vào bản nháp paper, sau khi sửa nhãn metric và trình bày đúng sự thay đổi đồng thời của parametrization/loss/features.

Ưu tiên 2: chạy ablation tối thiểu để tách data prediction khỏi feature s. Đây là thí nghiệm mới đáng làm hơn việc lặp pilot bốn nhánh vốn đã có.

Ưu tiên 3: thêm EXP-B/C ở appendix hoặc một đoạn ngắn trong main; cập nhật Limitations “not measured” và “no trained-network counterpart”. Giữ sự phân biệt synthetic engineered model với conventional image sampler.

Ưu tiên 4: áp dụng từng sửa toán/câu chữ chưa có trong working copy; kiểm lại LaTeX và số liệu sau tích hợp. Các script kiểm số hiện tại 429 checks không tự bao phủ toàn bộ EXP-A/B/C mới.

T1/T2/T3 và nghiên cứu basin theo tie dimension vẫn là hướng phát triển tiếp. Worktree này không làm chúng thành kết quả đã tích hợp hoặc đã được kiểm chứng lại.
