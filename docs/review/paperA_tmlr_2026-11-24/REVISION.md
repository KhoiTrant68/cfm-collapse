# Paper A sau vòng sửa ngày 25/11/2026

**Khuyến nghị nội bộ.** Có thể chuyển bản TMLR cho hai đồng tác giả duyệt lần cuối. Lỗi solver làm đảo chiều đường cong CIFAR đã được sửa ở cả đường chạy mới và replay. Các phát biểu về tính mới, điều kiện của định lý và số liệu CIFAR đã được thu hẹp theo kết quả kiểm tra.

| Vấn đề trong review ban đầu | Kết quả trên bản sửa |
|---|---|
| Đường cong CIFAR giảm giả ở guidance cao | Với 8 cặp, số midpoint là 109, 917, 2075, 2608 trên 4096 tổ hợp cặp–nguồn ở 1,1; 2; 5; 10 lần ngưỡng. Hình 9 và bảng theo cặp dùng nhãn đã tính lại. |
| Solver và độ nhạy | Hai cách phân loại khớp trên 59.390 handoff. Trong 95.232 quyết định được đối chiếu, 35.842 quyết định trước handoff được giữ lại. 12 tổ hợp được chạy lại với trường đủ 2000 ảnh trước handoff; ba tổ hợp gần biên cũng được thử khi khởi tạo đúng tại thời gian 0. Tất cả khớp. Một nguồn ở nhóm ngẫu nhiên chưa phân loại. |
| Positive control của RK4 | Sau phép dịch, RK4 bỏ sót cả 108 và 252 nguồn trong basin ở 2 và 10 lần ngưỡng. Bài ghi rõ giới hạn này. |
| Phạm vi lý thuyết | Abstract, bảng và kết luận nêu rõ điều kiện prior dương cùng support và lượng từ gần như mọi điểm khởi tạo. Bản sửa phân biệt lấy trung bình prior với lấy trung bình trường, đưa hai phản ví dụ vào bài và để mở trường hợp đúng ngưỡng trên CIFAR. |
| Đóng góp so với prior work | Phụ lục trình bày phép kết hợp Jiang–Ma và Liu–Zuazua cho guidance cố định. Bài phân biệt hệ quả này với lịch guidance biến thiên và tổ hợp ba trường tạo midpoint. |
| Bản gửi reviewer | PDF TMLR ẩn danh 59 trang; bảng đối chiếu và hình CIFAR đã được kiểm tra trên trang render. ZIP 47,0 MB. Từ ZIP, replay khớp từng byte với cả sáu tệp nhãn và summary; hình tái tạo khớp từng pixel ở 120 dpi. Bốn regression test và 1064 kiểm tra số liệu đều đạt. |

**Phần còn mở.** Việc thay trường đủ bằng hai ảnh tại handoff là xấp xỉ. Kết quả trên các cặp CIFAR dùng chung 512 nguồn Gaussian và không xác lập xu hướng cho mọi cặp ảnh. Ba mục chứng minh cần xác nhận trực tiếp của đồng tác giả trước khi nộp. [Checklist đồng tác giả](../round3_2026-11-23/proof_checklist.md) · [Dữ liệu và lệnh tái tạo](../../../results/cifar_composition_replay/README.md)
