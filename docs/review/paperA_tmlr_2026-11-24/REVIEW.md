# Phản biện trước khi nộp Paper A tại TMLR

Ngày 24/11/2026 · Bản đọc `f6caa4c` · [Manuscript](../../../paper_theory/main.tex)

**Khuyến nghị của người tổng hợp: sửa lớn trước khi nộp.** Kết quả phân biệt hai và ba trường chính xác phù hợp với độc giả TMLR. Có một lỗi tính toán làm đảo chiều một kết luận thực nghiệm trên CIFAR-10. Ba câu diễn giải toán học cần thu hẹp. Các kiểm tra dưới đây chưa phát hiện phản ví dụ cho hệ quả hai trường có prior dương cùng support hoặc định lý ba trường đối xứng với ngưỡng sắc. Đây là đánh giá kỹ thuật nội bộ, chưa qua bộ xác thực quyết định chính thức của ARS. [Tiêu chí TMLR](https://www.jmlr.org/tmlr/acceptance-criteria.html)

## 1. Kết quả CIFAR-10 cần tính lại

Ở dòng 63–68, bộ phân loại đọc điểm cuối cùng mà SciPy trả về rồi gán nhãn kể cả khi Radau dừng sớm. Đại lượng dùng để gán nhãn là tích của một hệ số tăng gần như mũ và một tọa độ rất nhỏ. Nhãn cuối vì thế nhạy với sai số tuyệt đối. Khi chạy lại cặp 1104/1984, nguồn số 23 (đếm từ 0), tại mức 2 lần ngưỡng, Radau báo bước thời gian nhỏ hơn độ phân giải số tại τ = 20,18, trước đích τ = 40. Lần chạy lại trả về midpoint, còn bản lưu ghi atom 1984. Riêng ca này xác nhận bộ phân loại có thể gán nhãn sau thất bại. Phép kiểm bên dưới mới xác định chiều sai lệch trên toàn tập. [Bộ phân loại](../../../scripts/cifar_composition_exact.py) · [Bảng đã lưu](../../../results/cifar_composition_exact_20261105/SUMMARY.md)

Tám cặp được chọn, 512 nguồn mỗi cặp. Cả ba cột dùng cùng trạng thái bàn giao và giữ nguyên các quyết định kết thúc sớm ở một atom.

| Guidance | Midpoint đã lưu / 4096 | Khoảng theo điều kiện bất biến | Tích phân ngược trong tọa độ profile |
|---|---:|---:|---:|
| 1,1 × ngưỡng | 102 | 0–216 | 109 |
| 2 × ngưỡng | 761 | 872–960 | 917 |
| 5 × ngưỡng | 613 | 2072–2086 | 2075 |
| 10 × ngưỡng | 172 | 2607–2611 | 2608 |

**Vì sao kiểm được mà không phải tin một solver khác?** Đặt u = exp(τ) − 1 và s = βrq theo định nghĩa trong code. Phương trình tiếp diễn cho ds/du = s/u + r²uF(s). Do F lẻ, chỉ cần xét s ≥ 0. Nếu tại s₀ > 0 vế phải âm thì tại cùng biên s₀ nó còn âm cho mọi u lớn hơn. Quỹ đạo bị giữ trong [−s₀,s₀], suy ra q → 0. Phía ngoài nghiệm dương ngoài cùng, F ≥ 0, quỹ đạo đi ra ngoài và thoát khỏi midpoint. Đếm hai loại ở thời điểm bàn giao rồi cho các ca chưa xác định vào cận trên tạo ra cột khoảng. Chỉ riêng ba khoảng rời nhau đã xác định xu hướng tăng. Các phép tính dùng số thực dấu phẩy động. [Script kiểm trực tiếp, chỉ cần Python](check_cifar_handoffs.py)

Phép kiểm thứ hai tích phân ngược từ hai phía của biên phân cách tại τ = 3, thay dung sai và so từng trạng thái bàn giao. Nhóm 12 cặp lấy ngẫu nhiên có cùng chiều thay đổi: ở 2 và 5 lần ngưỡng, số midpoint cũ là 255 và 236 trên 6144 nguồn; số tính lại là 309 và 874. Ở mức 5 còn một nguồn chưa được phân loại trước bàn giao. Đây là kiểm tra bước tiếp diễn **hai ảnh**. Bước thay trường 2000 ảnh bằng hai ảnh khi khối lượng posterior còn lại dưới dung sai vẫn là xấp xỉ. [Script tích phân ngược, cần NumPy và SciPy](replay_cifar_handoffs.py)

**Yêu cầu sửa.** Tính lại hình CIFAR và các bảng phụ bằng bộ phân loại có trạng thái thất bại rõ ràng. Kiểm độ nhạy theo dung sai của cả bước trước và sau bàn giao. Sửa câu ở dòng 3636 khẳng định mức giảm sau 2 lần ngưỡng không do solver. Tách xác suất mới đo được khỏi kết quả tồn tại suy ra từ định lý. Các giá trị bằng 0 dưới ngưỡng được cài sẵn trong luật phân loại. [Thí nghiệm trong phụ lục](../../../paper_theory/main.tex#L3592)

**Positive control bổ sung.** Với 256 nguồn đầu của seed 20261121, dịch cả hai atom thêm (0,25; 0). Với cùng nguồn, nghiệm chính xác dịch thêm t lần vectơ đó nên các nguồn trong basin giữ nguyên. Ở 2 và 10 lần ngưỡng, có 108 và 252 nguồn trong basin. Với tâm ở gốc, RK4 nhận đủ cả hai nhóm; sau phép dịch nó nhận 0 ở cả ba cutoff. Reviewer thử 256 và 512 bước mỗi đoạn; người tổng hợp chạy lại với 256. Giới hạn tuyên bố về positive control vào cấu hình tâm ở gốc, hoặc bổ sung một phương pháp vượt qua phép thử dịch. [Oracle và RK4](../../../scripts/stress_positive_control.py)

## 2. Ba kết luận cần sửa phạm vi

**Hai điều kiện ưu tiên hai atom khác nhau.** Dòng 992–993 bỏ qua giả thiết cân bằng chung và điều kiện covariance của hệ quả tại dòng 929–939. Có phản ví dụ cho cách hiểu rằng tăng guidance đủ lớn sẽ tạo blend. Lấy odds điều kiện bằng 3 và 4/5, odds vô điều kiện bằng 1, hai điều kiện có trọng số bằng nhau. Đặt x = exp(2ζ). Khử mẫu số dương trong phương trình profile cho đa thức

$$P(x)=\tfrac{12}{5}x^3+(\tfrac{12}{5}+w)x^2+(-1+\tfrac95w)x-1.$$

Với mọi w ≥ 0, dãy hệ số có đúng một lần đổi dấu. Có đúng một nghiệm dương tính theo bội, nó đơn và cắt trục theo chiều đi lên. Profile đó đẩy quỹ đạo ra; xác suất kết thúc ở midpoint bằng 0. Người tổng hợp khai triển lại các hệ số bằng phân số chính xác. Ví dụ đối xứng ±2B và hệ quả có đủ giả thiết vẫn đứng. [Phát biểu và công thức](../../../paper_theory/main.tex#L992)

**Ngưỡng có thể xuất hiện khi đạo hàm dự đoán vẫn bị chặn.** Dòng 1128–1129 suy ra một điều kiện cần mạnh hơn Proposition về learned fields. Đặt H(x) = tanh(x) + 2 tanh³(x), chọn a,b > 0 và a/b = w_c. Dùng hai dự đoán trơn bị chặn g_av = H + a tanh và g_u = H + (a+b)tanh. Dự đoán guided có đạo hàm tại 0 bằng 1+a−bw: midpoint hút phía trên ngưỡng và đẩy phía dưới. Tại ngưỡng, H(x)−x = (5/3)x³ + O(x⁵), nên midpoint vẫn đẩy. Mọi đạo hàm không gian bậc một ở đây đều bị chặn. Thu hẹp câu về việc tái tạo **hình dạng trường trong lớp co ở thang (1−t)²**. Một mạng có thể có cùng ngưỡng hút mà không tái tạo lớp ấy. [Lập luận learned field](../../../paper_theory/main.tex#L1104)

**Trường hợp đúng tại ngưỡng trên CIFAR.** Dòng 3639–3641 viện dẫn định lý phổ để khẳng định “exactly when”. Tại w = w_c, eigenvalue liên quan bằng 0 và giả thiết hyperbolic mất hiệu lực. Chứng minh giá trị tới hạn của mô hình đúng hai atom dùng tính đối xứng. Với 1998 atom khác, nhóm cần biện luận thêm về nhiễu ngoài cặp hoặc chỉ phát biểu hai phía bất đẳng thức nghiêm. Phép chạy số hiện tại cũng không quyết định ca bằng ngưỡng. [Định lý phổ](../../../paper_theory/main.tex#L891) · [Suy luận trên CIFAR](../../../paper_theory/main.tex#L3637)

## 3. Đóng góp, tài liệu liên quan và người đọc

Reviewer ODE lần theo chuỗi năng lượng hữu hạn, hội tụ, phân kỳ tích lũy và bước Liouville–Fatou. Reviewer phản biện đối kháng thử phá điều kiện support chung. Hai lượt kiểm đều giữ được kết luận gần như chắc chắn của hai trường dưới các giả thiết đã nêu. Trong ví dụ ba trường đối xứng, dấu của F′(0) đổi ở 1/sinh²(B), và phụ lục xử lý riêng ca bằng ngưỡng. Đây là phần nên đứng ở trung tâm bài. [Chứng minh hai trường](../../../paper_theory/main.tex#L2325) · [Ngưỡng hai atom](../../../paper_theory/main.tex#L2555)

Reviewer tài liệu xác nhận Wan et al. xử lý endpoint law đơn trường, còn Liu–Zuazua chứng minh hội tụ về cân bằng cho hai trường cố định. Có thêm một so sánh quan trọng với công thức mật độ CFG ở cutoff dương của Jiang–Ma. **Suy luận của panel:** với hai luật heat-smoothed p,q trên cùng support hữu hạn với prior dương, p/q bị chặn đều. Với guidance cố định w ≥ 0, công thức đặc trưng cho mật độ do ODE sinh ra một cận trên tỉ lệ với p^(1+w) q^(−w), rồi với q. Có thể lấy giới hạn để tập trung khối lượng vào các atom và kết hợp hội tụ từng quỹ đạo của Liu–Zuazua. Tác giả nên kiểm từng giả thiết, phép đổi thời gian và hệ số chuẩn hóa, rồi phân định đóng góp của trường hợp cố định với hỗn hợp tổng quát, lịch BV và phân loại ba trường. Hai bài trước không phát biểu nguyên văn kết quả suy ra này. [Wan et al.](https://proceedings.mlr.press/v267/wan25e.html) · [Liu–Zuazua, Thm. 2.5](https://arxiv.org/html/2605.12231v2#S2) · [Jiang–Ma, Thm. 4.2](https://arxiv.org/html/2607.19725v2#S4.SS3)

Reviewer theo tiêu chí TMLR và reviewer đối kháng cùng chỉ ra ba chỗ dễ gây hiểu nhầm.

- Abstract đồng nhất việc mạng chỉ nhận biết nhãn ở độ phân giải thô với việc sampler lấy trung bình nhiều trường. Proposition ở dòng 2407 nói rõ bottleneck tối ưu lấy trung bình **prior** trước khi tạo trường. Phép lấy trung bình các trường đã tạo có thể cho kết quả khác.
- Định nghĩa “copy” trong practical implications. Tăng bandwidth có thể làm giảm xác suất trả về **một record cụ thể** ngay tại nghiệm chính xác, trong khi xác suất trả về **một record nào đó trong tập train** vẫn bằng 1.
- Nêu positive priors trên support chung cạnh câu hai trường. Với hard labels, trọng số q và 1−q đưa mọi nguồn đến qa+(1−q)b. Điểm đó trùng midpoint khi q = 1/2. Gắn điều kiện hyperbolic và hình học của face vào câu về điều kiện phổ cần và đủ. [Abstract](../../../paper_theory/main.tex#L104) · [Practical implications](../../../paper_theory/main.tex#L292) · [Bottleneck](../../../paper_theory/main.tex#L2407)

## Quyết định trước khi nộp

1. Sửa bộ phân loại và các số liệu phụ thuộc, kiểm lại phép dịch và ca solver thất bại.
2. Thu hẹp ba phát biểu toán ở trên và chỉnh các câu tương ứng trong abstract, bảng và phụ lục.
3. Đối chiếu phần đóng góp cho guidance cố định với tài liệu liên quan. Hai tác giả tự ký nhận những chứng minh thực sự đã kiểm và đồng bộ phần khai báo LLM ở dòng 1422–1430.

Panel gồm năm tác nhân cùng họ mô hình, mỗi vai được giao trong một ngữ cảnh mới. Ba vai đầu chạy song song; hai vai còn lại vào khi có chỗ. Các reviewer không được gửi biên bản của nhau trước khi đưa kết luận. Người tổng hợp đã biết nội dung repo từ lượt trước và kiểm lại đại số, hai phép đọc trạng thái bàn giao và positive control. Cuộc review không đánh giá xác suất được nhận, không tái huấn luyện mạng và không thay cho kiểm chứng của đồng tác giả.
