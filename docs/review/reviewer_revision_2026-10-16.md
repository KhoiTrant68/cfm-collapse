# Bản sửa sau reviewer defense — 16/10/2026

**Cập nhật novelty sau lượt sửa:** [audit sâu hơn](novelty_audit_2026-10-16.md)
đã bổ sung stability literature và hai bài Liu–Zuazua. Không còn nên xem
small-loss obstruction hoặc risk-transfer bound là novelty chính độc lập.
Các đề xuất citation và thay câu trong audit chưa được áp dụng vào manuscript.

Đã sửa bản chính `paper/main.tex`, biên dịch `paper/main.pdf` và hoàn tất ba kiểm tra bổ sung trên server `server-01`. Các job này chỉ đánh giá checkpoint đã lưu, không huấn luyện lại. Tất cả đã kết thúc thành công.

## Nội dung đã sửa

- Đổi tiêu đề thành **Empirical Conditional Flows: Atomicity and the Limits of Loss Certification**.
- Sửa abstract, định vị related work, contribution, Methods, cách diễn giải effective bandwidth, limitations và conclusion. Không suy từ khớp variance sang đúng posterior hoặc đúng toàn bộ phân phối.
- Nêu rõ: objective hard conditioning không xác định field tại nhãn ngoài tập training. Kết quả mới ở nhãn đó kiểm tra khả năng mở rộng của network, không bác bỏ định lý ở nhãn training.
- Thêm Section 4.2 và Table 2: mười runs, năm problem seeds mới, đánh giá tại checkpoint 200k trên 64 nhãn mới/run, 512 mẫu/nhãn. Mean excess energy qua seeds là 1.073927 ở h=0 và 0.011277 ở h=0.1; giữ outlier trong mean chính và báo median song song.
- Thêm pilot coverage CIFAR và Appendix F với protocol, finite-time reference, oracle illustrations, matched-loss illustration và solver diagnosis. Ghi rõ số đơn vị độc lập, giới hạn diagnostic null, lựa chọn trường hợp sau khi xem kết quả và giới hạn covariance joint score.
- Giữ nguyên từng byte nội dung 78 khối toán học: 3 assumptions, 21 propositions, 7 corollaries, 4 theorems, 5 lemmas và 38 proofs. Đây là kiểm tra bảo toàn nội dung, không phải một lượt chứng minh độc lập mới.

## Kết quả kiểm tra bổ sung

**Synthetic outlier:** h=0, seed 1004, condition 50, nhãn 1.61918 nằm ngoài khoảng nhãn training. RK4 400/800/1600/3200 ở hai kiểu số và DOP853 độc lập đều tái hiện hai quỹ đạo cực trị. Với ba sources đã chọn, chênh lệch tương đối lớn nhất giữa DOP853 và RK4 float64 3200 bước là 8.872e-6. Trace RK4 float64 đi từ 1.70434e12 lên 1.70555e12. Float32 time embedding của kiến trúc gốc vẫn được giữ. Kết quả hỗ trợ chẩn đoán ngoại suy của learned field; không phải chứng nhận sai số ODE đồng đều.

**CIFAR:** h=4, seed 1, ba ảnh 2/3/5 được chọn do thay đổi phân loại coverage ở 50→400 bước. Euler 400/800/1600 và RK4 100/200/400 giữ nguyên joint ranks 0.924242/0.954545/0.954545, đều ngoài vùng upper-rank 90%. Cross-method RMS Euler1600–RK4400 là 0.000628/0.002570/0.001344. Đã tải raw arrays và tái tính độc lập 18 dòng; điều kiện, source, training images và PCA basis trùng khớp chính xác giữa hai solver. Không suy kết quả này sang toàn bộ tám ảnh hoặc mọi checkpoint.

Artifacts mới nằm trong `results/intervention_cifar_pilot_20261016/`:

- `targeted_synthetic_solver.json`;
- `targeted_cifar_euler.json` và `.npz`;
- `targeted_cifar_rk4.json` và `.npz`;
- `targeted_verification.json`.

Server giữ raw synthetic, checkpoint, log và các manifest của cả ba follow-ups. Thời gian evaluator CIFAR khoảng 171 giây cho Euler và 182 giây cho RK4.

## Novelty và việc còn lại

[Đối chiếu gần nhất ở mức định lý](theorem_comparison_2026-10-16.md) phân biệt phạm vi với Baptista, Dasgupta, Pfrommer, Li và Jain. Đã bổ sung citation Jain về CFG/memorisation và không trình bày hiện tượng đó như phát hiện mới. So sánh này có phạm vi giới hạn; chưa chứng nhận ưu tiên trong toàn bộ literature. Đặc biệt, cần đối chiếu sâu hơn với các định lý stability trước khi tuyên bố novelty của loss counterexample hoặc risk-transfer certificate.

Bản hiện tại vẫn là **TMLR**, 92 trang gồm tài liệu tham khảo và phụ lục; phần chính kết thúc ở trang 12. Chưa chuyển sang template và giới hạn độ dài ICLR. Bản sửa làm rõ đóng góp có thể bảo vệ và bổ sung bằng chứng âm, không phải tuyên bố đã đủ điều kiện được ICLR chấp nhận. Các giới hạn còn lại là novelty chưa được xác nhận đầy đủ, pilot ảnh nhỏ và chứng nhận solver mới chỉ trên các trường hợp chọn để chẩn đoán.

## Kiểm tra bản xuất

359 kiểm tra số liệu cũ qua; 14 giá trị của bảng seeds mới đối chiếu lại với JSON; 18 dòng CIFAR mới tái tính từ raw. Không có undefined references/citations, overfull boxes hay oversized floats. Đã render và xem 14 trang thay đổi/lân cận. PDF chính trùng build đã kiểm tra. MiKTeX chỉ còn thông báo chưa chạy update check; biên dịch thành công.

Snapshot trước sửa, script kiểm tra, build và hashes: `tmp/reviewer-revision-2026-10-16/verification.json`. Không commit hay push.
