# Kế hoạch cho venue tiếp theo — 9/11/2026

Căn cứ: panel 2 (`docs/review/panel_2026-11-07/synthesis.md`, Major Revision; phần toán không có
bước sai), commit 944b323 (xử lý 9 mục bắt buộc), commit 44cac7b (Option B và S10), và đánh giá
ngày 9/11. Mục tiêu: không nộp ICLR 2027, nhắm venue tiếp theo. Phần toán đã ổn; rủi ro còn lại
nằm ở câu "so what" và quy mô bằng chứng thực nghiệm.

| # | Điểm yếu | Việc làm | Loại | Trạng thái |
|---|---|---|---|---|
| N1 | AUC 0.985 của sai số cuối gần như là đồng nhất thức: ở cutoff, sai số cuối bằng $d_1$ trong vòng 0.2% với mọi mẫu, mà tiêu chí off-atom lại dựa trên $d_1$ | Viết lại App. C.4 và ý (iii): giá trị cuối chỉ là kiểm tra sổ sách; bằng chứng là AUC 0.97/0.95 tại $t\approx0.53$ và AUC dọc quỹ đạo exact ≈0.5 | Viết | Xong 9/11; verifier có check "within 0.2%" |
| N2 | Claim $(1-t)^{-2}$ trên EXP-1 chưa có check | Kiểm từ cột K của EXP-B: số mũ cục bộ là 1.8 và 2.0 ở hai thập phân cuối (1.4 ở thập phân trước đó); viết chính xác hơn trong App. C.4 | Viết | Xong 9/11 |
| N3 | Mọi thí nghiệm ảnh là CIFAR-10 với N=2000, một mask, network tự train | **Thí nghiệm chính** (chi tiết bên dưới): đo sai số trên một model public train trên đủ 50k ảnh, và trên model train ở các N nhỏ | Server | Chưa làm |
| N4 | Chưa có baseline rẻ hơn cho ý (iii) | Trên cùng các mẫu: AUC của (a) khoảng cách từ $\hat m$ tại $t\approx0.5$ tới ảnh train gần nhất, (b) $\lvert D(x,c)-D(x,\varnothing)\rvert$ (kiểu Wen et al. 2024), so với AUC của $(1-t)\lvert\Delta\rvert$. Nếu (a) ngang bằng thì ý (iii) phải viết lại | Server | Chưa làm; cần checkpoint S10 (còn trên server?) hoặc N3 |
| N5 | Related work còn thiếu, nằm sát framing mới | Đặt vị trí so với "From Navigation to Refinement" (CVPR 2026, oracle velocity, hai giai đoạn, CFG interval) và "A Kinetic-Energy Perspective of Flow Matching" (arXiv 2602.07928, soft landing cuối sampling giảm memorisation); thêm S11/S12 của panel: Wen et al. 2024, Bradley & Nakkiran 2024, autoguidance (Karras et al. 2024). Chạy citation check trước khi cite | Viết | Chưa làm |
| N6 | Bản ICLR vượt 9 trang (Limitations và Conclusion sang trang 10) | Khi chọn venue: kiểm giới hạn trang của venue đó, rồi cắt hoặc dùng `\moveblock`. Đoạn "What this means in practice" là ứng viên đầu tiên để rút gọn | Viết | Chờ chọn venue |
| N7 | Placeholder: OpenReview `XXXX` (dòng 94), `% CHECK` ở mục khai báo LLM, `TODO (citation)` ở phụ lục | Tác giả xác nhận mục LLM; điền link khi có; tìm trích dẫn cho bước $C^1$ Lyapunov–Perron | Tác giả | Chưa làm |
| N8 | Các mục gợi ý còn mở của panel 2 (S1–S9, S13, S18–S21) | Rà từng mục so với `main.tex` hiện tại, đánh dấu cái nào 944b323/44cac7b đã xử lý | Viết | Chưa rà |

## Thiết kế N3 (thí nghiệm chính)

Câu hỏi: trên một model không do mình train, sai số của field đã học so với exact field, đo giữa
quá trình sampling, có phát hiện được mẫu sát ảnh train không?

- **Model:** checkpoint EDM class-conditional CIFAR-10 public của NVlabs. Dùng framework denoiser
  của EDM: $\hat m = D_\theta(x,\sigma,c)$, còn $m^*(x,\sigma,c)$ là trung bình hậu nghiệm Gaussian
  trên các ảnh train của lớp $c$. Cả hai tính trực tiếp, không cần chuyển sang dạng CFM. Exact
  field trên 5000 ảnh/lớp × 3072 chiều chạy được trên A30.
- **Thang N:** model public (N=50k) gần như không memorise, nên thêm model EDM train trên các tập
  con N ∈ {500, 1000, 2000, 5000}, nơi memorisation đã biết là cao. Điều này cho thấy tín hiệu đi
  từ "nhiều mẫu off-atom" sang "hầu như không".
- **Đo:** dọc quỹ đạo sampler EDM (Heun, các bước mặc định), lấy $\lvert\hat m-m^*\rvert$ theo
  từng mẫu tại mọi $\sigma$; ở endpoint lấy $d_1/d_2$ và cờ near-copy (ngưỡng 1/3 như App. C.4,
  thêm SSCD nếu cần). Báo AUC theo $\sigma$ cùng hai baseline của N4.
- **Phạm vi lý thuyết:** label lớp không phải identifying label, nên chỉ Prop. `localtransfer`
  (cục bộ) áp dụng. Viết đây là kiểm tra tính nhất quán, không phải hệ quả của Theorem `transfer`.
- **Kết quả âm vẫn báo cáo:** nếu tín hiệu giữa quá trình không vượt baseline (a), ý (iii) chỉ
  còn là phát biểu lý thuyết.

Quy tắc giữ như kế hoạch 5/11: mỗi số mới có check trong `scripts/verify_paper_numbers.py`;
server dùng GPU A30, không theo dõi job dài, không xoá file; chứng minh mới do tác giả kiểm lại.
