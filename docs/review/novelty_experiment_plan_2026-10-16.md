# Thí nghiệm theo novelty audit — protocol khóa trước khi chạy

Mục đích là kiểm tra các hệ quả và giới hạn của intervention atomicity, không dùng numerical evidence để chứng minh novelty hay zero-measure basins. Ngày 16/10/2026, timezone Asia/Bangkok. Chưa sửa manuscript trong đợt chạy này.

| Nhóm | Câu hỏi / factor | Thiết kế cố định | Số trường hợp |
|---|---|---|---|
| A — exact-field stress | Thay guidance strength hoặc loại averaging có làm mất atomicity? | 5 geometry seeds 201–205; d=2,8; N=12; random và near-duplicate geometry; h=.3,1; M=128 nguồn Gaussian ghép cặp | 20 geometry instances × 10 arms = 200 cells, mỗi cell 3 terminal gaps |
| B — ties và biên giả thiết | Điểm tie chính xác và các lân cận nhỏ khác nhau thế nào? h>0 và h=0 khác nhau thế nào? | Hai atoms ±1, labels ±1; nguồn 0 và ±1e-12, ±1e-8, ±1e-4, ±1e-2; h=.05,.2,1; average fields / average priors / hard-label average | 81 trajectories × 4 terminal gaps = 324 rows |
| C — learned-field bridge | Averaging một trained field có tuân theo exact-field picture không? | 5 checkpoint MLP h=.1, seeds1001–1005, 200k; baseline và radius .5/1.5 label std; 2 training + 2 fresh queries; M=128 ghép cặp | 5 × 3 × 4 = 60 model–condition cells |

A dùng baseline single-label field tại w=0, CFG w=3/12, average của 5 label fields tại offsets [-2,-1,0,1,2]h và field tạo từ average của 5 priors. Hai phép average nói chung khác nhau. h thay riêng trong các contrasts; geometry gần trùng chỉ thay atom thứ hai để cách atom thứ nhất .02, giữ labels và sources. d được phân tích riêng, không coi các dimensions của một seed là independent replicates.

B dùng công thức tanh một chiều để bảo toàn symmetry của tie chính xác. Positive label average là trung bình hai fields ở labels ±1. Average priors là uniform-prior field. Hard-label average là field -x, có endpoint 0 ngoài atoms: đây là control **ngoài giả thiết h>0**, không phải phản ví dụ cho theorem. Các terminal gaps là 1e-2,1e-4,1e-6,1e-8. Sáu trường hợp đã định trước (h=.2,1; x0=0,1e-4,1e-8) được kiểm tra bằng DOP853 độc lập. Không suy từ hữu hạn initial points rằng một basin có độ đo zero.

C giữ nguyên training objective, model architecture, weights và dữ liệu. Chỉ thay field tại inference bằng trung bình ba predictions tại query và query±radius. Reference là exact average của cùng ba conditional fields, không phải average endpoint weights. Fresh queries dùng seed20261019+problem_seed, sources seed20261020+problem_seed; không chọn theo kết quả. Đây là một diagnostic bridge trên năm problem seeds đã có, không phải năm seeds mới và không phải trained CFG experiment. Không thay thế missing unconditional checkpoint bằng một model khác.

## Integration và metrics

- A: float64 log-time RK4, 256/512 bước **mỗi segment** giữa gaps 1,1e-2,1e-4,1e-6, tổng 768/1536 steps. Giữ cùng nguồn giữa resolutions/arms.
- B: log-time RK4 512/1024 bước mỗi segment, tổng 2048/4096 steps. DOP853 rtol1e-10, atol1e-13.
- C: learned float32 RK4 400/800 bước original time đến T=.999; exact average float64 log-time RK4 768/1536 bước đến cùng T. Giữ float32 time embedding của model.
- Primary A: nearest-atom distance theo terminal gap, chuẩn hóa bằng minimum atom separation; báo mean/q95/max và fraction vượt 1% separation. Đây là ngưỡng mô tả đã định trước, không phải test significance.
- Primary B: signed endpoint / nearest-atom distance từng initial offset, h và gap; exact zero trajectory và near-zero trajectories báo riêng.
- Primary C: energy statistic giữa network và exact-average reference, chia sqrt(analytic posterior trace); nearest-atom distance và learned/oracle solver displacement báo riêng. Không dùng energy statistic chưa trừ finite-M baseline như một equivalence test.
- Secondary: trace, coarse/fine atom-assignment disagreement, sample displacement. So sánh cell ghép cặp; tổng hợp seed means và range, không pseudo-replicate samples/conditions. Không gán đúng NW weights cho guided/averaged endpoints.

## Dự đoán và xử lý thất bại

A: distances kỳ vọng giảm về atoms khi gap nhỏ trong các arms thuộc theorem; averaging fields có thể đổi basin weights so với averaging priors. B: exact tie giữ nguyên ngoài atoms; các nguồn lân cận có thể thoát rất muộn, nhất là h nhỏ; hard-field averaging giữ endpoint ngoài atoms. C: không giả định theorem exact-field đúng cho network; sai khác là kết quả được phép và phải báo.

Mỗi cell giữ raw states và sources. Nếu coarse/fine assignment khác hoặc displacement lớn so với nearest-atom scale, đánh dấu solver-sensitive, không gọi là theorem failure. Không loại cell xấu khỏi primary summaries. Run lỗi lưu status failed và exception; chỉ chạy lại vào output directory mới, giữ dấu vết. Nếu có lỗi mô hình/metric, sửa trước full launch và ghi lại.

## Tài nguyên và preflight

Server server-01 có 2 L40, mỗi GPU còn khoảng45GB và utilization0% lúc kiểm tra22:49 Bangkok; disk còn563GB. Không có training job của tài khoản đang chiếm GPU. Scripts tự ghi PID, host, hashes, args, progress và status JSON; log stdout có flush. Không có experiment-tracker/API charge. Reuse code theo quy trình ponytail, không thêm dependency.

Ước lượng ban đầu 10–30 phút, dưới1 GPU-hour; calibrate bằng smoke trước full launch. A và C chạy trên hai GPUs riêng. Sau smoke, B được đặt trên server CPU vì scalar tanh không cần GPU, nên chạy đồng thời mà không tranh GPU. Timeout cứng lần lượt1800/1800/600 giây, tổng tối đa60 GPU-min và10 CPU-min nếu tất cả chạm trần. Storage dự kiến dưới100MB, không tạo checkpoint mới. ETA sẽ được cập nhật theo smoke/runtime thực tế; không dùng estimate như trạng thái completed.

Preflight hoàn tất22:55 Bangkok: năm checkpoint/config đều tồn tại; evaluator SHA256 `096a6b42e0038787525206ee453816918968dcd4bc51a590046612b2d564dc5d`. Smoke server A/B/C thành công lần lượt1.7/2.4/1.1 giây, low-step outputs chỉ dùng kiểm tra pipeline. Local tie smoke không chạy được vì local venv thiếu SciPy; server đã có SciPy và smoke thích hợp đã qua. Không cài dependency mới.

## Follow-up chẩn đoán sau khi xem primary results

Không đổi primary protocol/data. Các nguồn gần tie ở h=.05/.2 chưa thoát tại gap1e-8; direct tanh differences có thể mất precision khi hai terms bão hòa. Vì vậy thêm `novelty_ties_refined.py`: stable sinh/cosh identity trong log space; gaps thêm1e-10,1e-14,1e-18; x0=0,1e-12,1e-8,1e-4; paired512/1024 bước mỗi segment; DOP853 rtol1e-11/atol1e-30 cho sáu positive-offset cases. Lưu vào thư mục mới `tie-cutoff-refinement`, timeout300s trên CPU. Kết quả là posthoc sensitivity diagnosis, không phải independent validation hoặc thay primary. Local distance verification cũng đo roundoff của CUDA cdist gần atoms; sai lệch mean lớn nhất1.57e-10, không đổi outputs hoặc threshold1% separation.

## Lệnh chạy đã dùng trên server

Từ `/mnt/home/guess03/cfm-collapse`, dùng interpreter `/mnt/home/guess03/clic/venv/bin/python` và `PYTHONPATH=.`. Để tái chạy, đổi `ROOT` thành một output root mới (evaluator từ chối overwrite).

```bash
CODE_ROOT=results/novelty_interventions_20261016/code
ROOT=results/novelty_interventions_20261016
CODE=$CODE_ROOT/novelty_interventions.py
CUDA_VISIBLE_DEVICES=0 ~/clic/venv/bin/python -u "$CODE" --suite stress --out "$ROOT/exact-field-stress-five-seeds" --seeds 201 202 203 204 205 --M 128 --steps 256
CUDA_VISIBLE_DEVICES=1 ~/clic/venv/bin/python -u "$CODE" --suite learned --out "$ROOT/learned-label-averaging-five-seeds" --seeds 1001 1002 1003 1004 1005 --M 128 --steps 400 --oracle-steps 768
~/clic/venv/bin/python -u "$CODE" --suite ties --device cpu --out "$ROOT/tie-neighborhood-boundary" --steps 512
~/clic/venv/bin/python -u "$CODE_ROOT/novelty_ties_refined_v2.py" --out "$ROOT/tie-cutoff-refinement-recorded"
```

Các lệnh thực tế có timeout và stdout/stderr logs như mô tả phía trên; A/C chạy song song, B/diagnosis chạy CPU. Không mở thêm một training sweep.

Đối chiếu reference config C: giữ d2/k1/N200/sigma_obs.1, MLP4×128, h.1 và checkpoint200k. Chỉ evaluation queries/M/integration/averaging thay có chủ đích so với evaluation cũ M64/steps100. Script mới `scripts/novelty_interventions.py`; server snapshot trong `results/novelty_interventions_20261016/code/`. Controls: exact single-atom affine solution và zero-radius field identity. Smoke dùng ít mẫu/bước để kiểm tra pipeline, không đưa vào primary results.
