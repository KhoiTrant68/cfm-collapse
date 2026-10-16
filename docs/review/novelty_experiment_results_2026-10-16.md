# Kết quả thí nghiệm theo novelty audit — 16/10/2026

Đã chạy trên server-01 và hoàn tất ba nhóm primary. Không huấn luyện lại. Full evaluator dùng cùng script snapshot SHA256 `096a6b42e0038787525206ee453816918968dcd4bc51a590046612b2d564dc5d`; smoke outputs không gộp vào bảng primary. Đã tải raw arrays và tái tính độc lập 984 dòng metrics.

Protocol, đối chứng, resources, commands và các thay đổi posthoc nằm trong [kế hoạch đã khóa](novelty_experiment_plan_2026-10-16.md). Số liệu máy đọc được và raw data ở `results/novelty_interventions_20261016/`.

## A. Exact fields: kết quả phù hợp atomicity trong các trường hợp đã đo

Năm geometry seeds, hai dimensions (2,8), random/near-duplicate atoms, hai bandwidths (.3,1), CFG strengths0/3/12 cùng field-average và prior-average controls tạo thành200 cells. Các contrasts dùng cùng initial sources; không coi200 cells là200 independent problem seeds.

Tại terminal gap1e-6:

- q95 nearest-atom distance lớn nhất trong200 cells là **6.11937e-6**;
- không có mẫu nào vượt threshold đã định trước1% minimum atom separation;
- coarse/fine không đổi nearest-atom assignment trên các mẫu đã đo;
- mean paired solver displacement lớn nhất là **7.54797e-13**.

Điều này phù hợp với endpoint atomicity, vượt ngoài affine-hull-only diagnosis trong các instances N12>d. Nó không chứng minh support của limiting law, mọi trajectory hoặc exceptional-set measure bằng0.

Field averaging và prior averaging không cho cùng basins trên tất cả cases: paired assignment disagreement lớn nhất **31.25%** trong40 instance–bandwidth comparisons. Đây là mô tả hữu hạn mẫu, không phải phép nhận dạng exact endpoint probabilities. Không thay field-average theorem bằng một mixture-of-endpoint-laws argument.

CUDA cdist sử dụng squared-distance expansion nên roundoff gần atoms hơi khác direct norms; max discrepancy của mean-distance khi tái tính là1.57e-10. Verification dùng absolute tolerance2e-9 và kiểm tra lại threshold/assignments. Không đổi trajectories hoặc primary threshold để làm kết quả qua.

## B. Ties và biên giả thiết

Primary gồm81 trajectories, mỗi trajectory đo tại4 gaps, tổng324rows. Exact symmetric source0 ở ngoài atoms ±1 tại mọi cutoff. Hard-label field averaging có nghiệm x(eps)=eps*x0 và endpoint0: đây là control **ngoài h>0**, cho thấy giả thiết positive bandwidth không thể bỏ tùy tiện.

Với h1, các positive offsets rất nhỏ đã tiến gần atom ở cutoff đo. Với h.05/.2, một số near-tie sources chưa thoát tại gap1e-8. Chỉ từ kết quả finite-time này không thể kết luận chúng có non-atom limiting endpoints.

### Follow-up có giới hạn solver

Đã thêm chẩn đoán riêng, không thay primary: stable sinh/cosh formula trong log space, cutoff đến1e-18 và DOP853 với atol1e-30. Fixed-step refinement cho thấy các positive offsets thoát về phía atom khi đi tới gap nhỏ hơn; source0 tiếp tục giữ0.

Tuy nhiên, **4/6 adaptive integrations không hoàn tất** ở h.05/.2, với thông báo `Required step size is less than spacing between numbers.` Hai cases h1 hoàn tất. Vì vậy không chứng nhận adaptive convergence cho các near-tie cases h nhỏ. Đây là evidence về giới hạn số khi theo dõi departure rất sắc; chưa chẩn đoán được một nguyên nhân duy nhất và không gọi là phản ví dụ toán học.

Attempt đầu dừng ở assertion khi adaptive solver báo failure; log được giữ. Attempt sau ghi toàn bộ successes/failures và partial outputs, status `completed_with_solver_limits`. Không nới tolerance để biến failure thành success. Raw fixed-step outputs của follow-up phải được đọc cùng giới hạn này.

Đã đối chiếu84 dòng follow-up với raw arrays. Max paired fixed-step displacement là3.25231e-4; max adaptive/fixed-step difference trên những timepoints adaptive thực sự trả về là4.20487e-7. Điều này không cấp chứng nhận cho các timepoints chưa đạt tới. Follow-up mất23.4s trênCPU.

## C. Learned-field bridge: averaging rộng không tự chuyển theorem sang network

Năm checkpoint MLP đã có ở h.1, cùng checkpoint200k, hai training queries và hai fresh queries mỗi seed,128 nguồn ghép cặp. Chỉ thay inference field bằng average của ba label predictions. Reference là exact average của cùng ba fields, không phải prior average. Đây là năm problem seeds cũ được đánh giá thêm, không phải5 new training replicates.

| Averaging radius / label std | Mean normalized energy: training | Mean normalized energy: fresh | Range fresh qua5 seed means |
|---|---:|---:|---:|
| 0 | 0.005627 | 0.007227 | 0.001876–0.009327 |
| 0.5 | 0.011200 | 0.011054 | 0.001887–0.018859 |
| 1.5 | 0.289771 | 0.143176 | 0.001758–0.544995 |

Mức averaging rộng làm mean discrepancy tăng, nhưng **không tăng trên mọi seed**. Mean fresh nearest-atom distance của network tăng0.0573→0.0916→0.1106; exact-average reference tại cùng T=.999 là0.00183→0.00328→0.00479. Mean learned solver displacements theo các groups khoảng7e-7–1.7e-6; oracle paired displacement lớn nhất qua cells6.89e-7. Những chênh lệch này lớn hơn step-refinement changes đã đo, nhưng refinement hữu hạn không phải certified bound.

Energy statistic dùng128 mẫu và chưa trừ reference-vs-reference baseline trong study này; không gọi các giá trị nhỏ là distributional equality hoặc dùng chúng như hypothesis-test p-values. Hai fresh queries/seed là pilot nhỏ. Không suy ra cải thiện/giảm chất lượng posterior chỉ từ khoảng cách tới empirical reference. Không có trained CFG test trong nhóm này vì không có unconditional checkpoint cùng problem seeds để làm đối chứng hợp lệ.

## Hệ quả cho paper

1. Đưa A vào main/appendix như kiểm tra intervention atomicity, có paired solver check và adversarial near-duplicate geometry.
2. Dùng B để trình bày exact tie, nonuniform finite-time behavior và sự cần thiết của h>0. Báo nguyên trạng adaptive failures của follow-up.
3. Dùng C để chặn bước suy diễn exact-field theorem thành trained-network theorem; averaging labels trong model hữu hạn không tự động làm sampler đúng reference hơn.
4. Các thí nghiệm này làm rõ contribution và giới hạn, không xác nhận ưu tiên literature hoặc thay thế proof audit. Không có lý do từ số liệu hiện tại để mở một broad training sweep chỉ nhằm giải quyết novelty.

## Artifact và runtime

- `results/novelty_interventions_20261016/SUMMARY.md`: bảng primary;
- `summary.json`: aggregates, hashes và984row verification;
- `novelty_experiments.png` / `.pdf`: scientific figure;
- các folders theo suite: raw `.npz`, per-cell JSON và PID/host/config;
- `tie-cutoff-refinement-recorded/`: posthoc fixed-step và partial adaptive outputs;
- scripts `novelty_interventions.py`, `novelty_ties_refined.py`, `summarize_novelty_interventions.py`.

Evaluator runtimes primary: A74.9s trênGPU0, C36.9s trênGPU1, B12.2s trênserverCPU; ba nhóm chạy chồng thời gian. GPU process list đã rỗng lúc kiểm tra23:03:58 Bangkok. Không có training job đang chạy tiếp. Main manuscript chưa sửa trong lượt này.
