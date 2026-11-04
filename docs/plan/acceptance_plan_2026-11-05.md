# Kế hoạch nâng bài lên mức accept — 5/11/2026

Căn cứ: `docs/review/reviewer_defense_2026-11-04.md` (V1–V12, Q1–Q12). Sau commit 8caa438, V1
(learned composition vắng mặt) đã xử lý. Các điểm yếu còn lại, theo thứ tự ảnh hưởng tới quyết
định accept:

| # | Điểm yếu còn lại | Việc làm | Loại | Trạng thái |
|---|---|---|---|---|
| P1 | V2: `cfm_x_s` đổi output, loss và input cùng lúc; chưa biết thay đổi nào quyết định | Ablation `cfm_v_s`, `cfm_x` (5 seed mỗi biến thể), đọc kết quả, viết câu attribution ở §6.2 và Limitations | Server | Đang chạy (`results/composition_ablation_20261105`) |
| P2 | V2/V3: chưa có lý thuyết giải thích vì sao một parametrisation học được basin còn cái kia không | Mệnh đề mới (§5 + phụ lục): (a) trường có hằng số Lipschitz khả tích tới $t=1$ cho endpoint law liên tục tuyệt đối, không có atom nào; (b) với data prediction có giới hạn đều tại $t=1$, endpoint là điểm bất động của dự đoán tại $t=1$, nên ngưỡng $w_c$ (sống ở thang $(1-t)^2$) không nhìn thấy được. Dự đoán kiểm được: `cfm_x` không bám ngưỡng | Toán | Bắt đầu |
| P3 | V7: thực nghiệm nhỏ, chưa có ví dụ ảnh cho composition | Exact composite trên cặp ảnh CIFAR-10 có midpoint là circumcentre (cặp được chọn bằng điều kiện candidate), hình mẫu off-atom; nếu khả thi, thêm mạng đã huấn luyện | Server | Thiết kế |
| P4 | Q7/Q8: EXP-B ($K=m/r$) và EXP-C (CIFAR solver/cutoff) đã đo nhưng chưa có trong bài | Đưa vào phụ lục, sửa câu "have not measured" | Viết | Chờ |
| P5 | V5: liên hệ thực tiễn | Đã có một câu ở §4.3; thêm hệ quả của P2 cho CFG thực tế | Viết | Sau P2 |
| P6 | Tam giác 2D chỉ có `cfm_v`, `cfm_x_s` | Thêm `cfm_x` (và `cfm_v_s` nếu P1 cho thấy cần) trên tam giác | Server | Sau P1 |
| P7 | V6: bài nén | Đọc lại toàn bộ phần chính ICLR sau P1–P5, giữ 9 trang | Viết | Cuối |

Quy tắc thực hiện:
- Mỗi chứng minh mới qua quy trình math-olympiad: solver độc lập, verifier đối kháng ngữ cảnh sạch
  (4 HOLDS để xác nhận, 2 HOLE để bác). Chứng minh mới được đánh dấu là mới trong báo cáo cho tác
  giả; tác giả kiểm lại trước khi nộp.
- Mỗi số mới trong bài có kiểm tra trong `scripts/verify_paper_numbers.py`.
- Bản TMLR là bản chuẩn; bản ICLR giữ 9 trang bằng `\moveblock`.
- Server: GPU A30 (index 2, PCI order), không theo dõi job dài, không xoá file.
- Kết quả âm được giữ và báo cáo.
