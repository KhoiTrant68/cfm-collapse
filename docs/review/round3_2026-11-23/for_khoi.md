# Gửi Khôi: cần kiểm gì trước khi nộp

Repo `cfm-collapse`, nhánh `paper-split-drafts`. "A:735" là dòng 735 của
`paper_theory/main.tex`, "B:468" là dòng 468 của `paper_mechanism/main.tex`.

## Bài gốc được tách thế nào

Bản cũ `paper/main.tex` gộp hai câu hỏi khác nhau, nên được tách làm hai bài:

| | Bài A (lý thuyết) | Bài B (cơ chế) |
|---|---|---|
| Thư mục | `paper_theory/` | `paper_mechanism/` |
| Câu hỏi | Với trường **chính xác** (exact field), can thiệp nào ở sampler giữ điểm cuối trên ảnh train? | Mạng **đã huấn luyện** copy ảnh train như thế nào? |
| Kết quả chính | label noise, label averaging, guidance, tổ hợp hai trường: không rời ảnh train; ba trường (phép hội) thì có thể | thm:relerr (radial ratio), prop:trap, prop:heun; thí nghiệm EDM CIFAR-10 |
| Nơi nộp | TMLR trước, rồi arXiv | NeurIPS 2027 (đang chờ style) |

Quy tắc khi tách: hai bài không được chung một câu, một hình hay một con số (TMLR cấm
"reuse" với bài nộp song song). B trích A như một bài khác (`companionA`, hai lần: B:252, B:575)
và không chứng minh lại gì của A. Số liệu s10 chỉ nằm ở A. Code cũng tách theo bài: ví dụ
`kernel_tracking_uncertainty.py` là của A, `paperB_uncertainty.py` là của B.

## Việc cần Khôi làm (khoảng 2 giờ)

1. **Ba chứng minh của A**, cùng Khang (khoảng 1 giờ 45 phút): theo `proof_checklist.md` cùng
   thư mục. Vì sao: phần khai báo LLM của A (A:1422) ghi rằng tác giả đã kiểm các chứng minh do
   mô hình soạn. Câu đó chỉ đúng khi có người kiểm thật.
2. **Ba chứng minh của B**: thm:relerr (B:1440), prop:trap (B:1503), prop:heun (B:1570). Vì
   sao: phần khai báo LLM của B (B:1098) cũng ghi "verified". Ở prop:heun, phần (b) và (e) vừa
   thêm giả thiết `e(x_{K-1}, sigma_{K-1}) <= rho n_{K-1} + gamma`. Kiểm xem giả thiết này có
   đủ không và có thừa không.
3. **Đọc lướt A so với B** (khoảng 15 phút): xem còn đoạn nào gần trùng nguyên văn giữa hai bài
   không, nhất là phần Related work và phần mô tả thí nghiệm EXP-1.

## Hai câu cần Khôi quyết

- **Tên `e` và `e_t` trong thm:relerr (B:468):** `e` đang chỉ vectơ `Z - a`, `e_t` chỉ sai số,
  dễ nhầm. Giữ nguyên hay đổi tên?
- **Trích A lần thứ ba trong B (X2):** prop:regular(b) của A là trường hợp một chiều của
  thm:relerr. Có thêm một câu nhắc điều này ở B không? Nhóm đã quyết chỉ trích A hai lần.

## Đã xong, không cần làm lại

Trích dẫn (Wan, Baptista, Benton, Liu, Sontag cho A7, Guillemin và Pollack), số liệu chạy lại
bằng code độc lập, các câu nói quá, bộ build gói nộp `submit/build.py`. Báo cáo chi tiết của từng
lượt kiểm nằm trong cùng thư mục này (`proof_audit_*.md`, `cite_*.md`, `a_vs_b.md`, ...).
