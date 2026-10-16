# Tổng hợp 10 runs trên seeds mới — 16/10/2026

Cả 10 runs đã hoàn tất 200.000 iterations và đánh giá cuối. Mỗi mức h có 5 problem seeds 1001–1005. Mỗi run dùng 20 training conditions để fit bandwidth, 64 conditions mới để đánh giá, 512 samples/condition. So sánh tại cùng checkpoint 200k; không chọn seed theo kết quả.

**Kết luận:** h=0.1 làm Gaussian reference gần sampler hơn, nhưng dữ liệu không xác nhận một bandwidth mô tả đúng toàn bộ phân phối. h=0 có một condition cực trị chưa qua solver screen; giữ nguyên trong số liệu chính.

| training h | seed | h_eff | mean excess energy | conditions trên q95 tham chiếu (diagnostic) | solver pass |
|---|---|---|---|---|---|
| 0.0 | 1001 | 0.043296 | 0.430079 | 64/64 | 64/64 |
| 0.0 | 1002 | 0.0146093 | 0.126044 | 62/64 | 64/64 |
| 0.0 | 1003 | 0.0406899 | 0.282378 | 64/64 | 64/64 |
| 0.0 | 1004 | 0.00396685 | 4.08458 | 63/64 | 63/64 |
| 0.0 | 1005 | 0.0150699 | 0.446561 | 64/64 | 64/64 |
| 0.1 | 1001 | 0.106508 | 0.0213366 | 42/64 | 64/64 |
| 0.1 | 1002 | 0.109866 | 0.00811803 | 36/64 | 64/64 |
| 0.1 | 1003 | 0.091197 | 0.020624 | 50/64 | 64/64 |
| 0.1 | 1004 | 0.11333 | 0.00425349 | 22/64 | 64/64 |
| 0.1 | 1005 | 0.0733866 | 0.0020552 | 14/64 | 64/64 |

Energy được chuẩn hóa bằng sqrt(trace posterior giải tích); excess trừ mean reference-vs-reference cùngM và cùng finite terminal time. Giá trị nhỏ hơn nghĩa là gần reference hơn, không tự động là posterior chất lượng cao hơn.

| h | mean qua 5 seeds | median qua 5 seeds | khoảng qua 5 seeds | Gaussian tốt nhất trong 4 families |
|---|---|---|---|---|
| 0.0 | 1.07393 | 0.430079 | 0.126044–4.08458 | 0/5 |
| 0.1 | 0.0112775 | 0.00811803 | 0.0020552–0.0213366 | 5/5 |

## Giới hạn và outlier

Phép thử này đánh giá generalization tại labels mới. Ở h=0, empirical conditional law chỉ được xác định tại training labels; sự thất bại ở label mới không bác bỏ định lý atomicity/hard conditioning tại training labels. Kết luận cần thu hẹp là cách diễn giải Gaussian effective-bandwidth như một law tổng quát của trained sampler ngoài tập conditions đã fit.

q95 chỉ dùng 16 reference pairs/condition, không phải một kiểm định có hiệu chỉnh multiple testing. Có 5 problem seeds độc lập, không phải 320 replicates mô hình. Không dùng khoảng bootstrap qua conditions như uncertainty giữa problem seeds.

h=0, seed 1004, condition 50 có saved energy 253.092, paired solver displacement chuẩn hóa 118.101 và trace khoảng 1.70e12. Solver chưa được tách khỏi learned-field error ở condition này. Không được gọi tất cả 640 conditions đã hội tụ; 639/640 qua practical screen. Outlier không bị loại khỏi primary mean. Median qua seeds được báo song song, không thay thế primary đã khóa.

Raw check: query y=1.61918, training-label range=[-1.1735473035279602, 1.183615676877379]; 2/512 endpoints có norm>100, max norm=2.95188e+07, median norm=4.83337. Đây là quan sát số, chưa là chẩn đoán nguyên nhân.
Sensitivity posthoc: mean excess của seed 1004 nếu bỏ riêng condition 50 là 0.132074; con số này không thay thế mean chính.

## Reference-family comparison

Gaussian tốt nhất trên cả 5 seeds khi h=0.1; khi h=0, một family khác gần sampler hơn ở cả 5 seeds. Các scales được chọn bằng fit variance trên 20 training conditions, không tối ưu energy trên held-out data. Vì vậy đây là so sánh các reference đã fit theo protocol, không chứng minh family nào tối ưu trên mọi tham số.

## Teacher error và rollout error

Ở t=0.999, h=0, learned-path/teacher-error ratio là 2.575e+05–6.067e+05 qua 5 seeds. Đây là fixed-time diagnostic tại training conditions, không phải training loss tích phân theo thời gian hay một risk-transfer bound toàn cục.

Đồ thị loss EMA chỉ theo dõi quá trình học trong từng run. Hai mức h tối ưu các objective conditioning khác nhau; không xếp hạng chất lượng posterior bằng cách so trực tiếp giá trị loss của hai objective.

## Hệ quả cho paper

- Giữ các định lý oracle/atomicity trong đúng giả thiết và tách khỏi hành vi của network hữu hạn.
- Thu hẹp h_eff thành diagnostic về moment; không trình bày Gaussian-reference fit như đồng nhất toàn bộ phân phối.
- Báo cả outlier và giới hạn solver; không quy mọi sai lệch cho một cơ chế chưa kiểm tra.
- Kết quả lặp lại trên seeds mới, nhưng chưa xác nhận novelty hay đủ điều kiện được ICLR chấp nhận.

Raw checks: 640 Gaussian model-reference energies, 640 same-moment-control energies; 10 Gaussian scale fits được tái tính khi --verify-raw được bật. Secondary-family energies trong báo cáo lấy từ JSON của evaluator. Full checkpoints và raw artifacts được giữ trên server.

Run IDs, hashes và bảng secondary families: summary.json. Bảng theo seed: per_seed.csv. Không chỉnh bản thảo hoặc thay số cũ trong paper trong bước tổng hợp này.
