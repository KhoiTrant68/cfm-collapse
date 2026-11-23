# Kế hoạch hành động cho hai bài (2026-11-21, cập nhật cuối ngày)

Dựa trên `docs/plan/paper_split_plan_2026-11-21.md`, sau khi session tách bài đã dựng xong bài A trong `paper_theory/`.

Ràng buộc chạy code: mọi tính toán chạy trên **lab09**, chỉ trong `/mnt/data/khoitm8/`, và luôn `source /mnt/data/khoitm8/env.sh` (`CUDA_VISIBLE_DEVICES=6`). Repo được đồng bộ sang `/mnt/data/khoitm8/cfm-collapse/`. LaTeX dùng `tectonic` trong conda env `/mnt/data/khoitm8/miniconda3/envs/cfm`, build bằng `bash scripts/build_papers.sh [paper_theory] [paper_mechanism]`.

GPU 6 bận suốt ngày vì các job khác của bạn (khoảng 77/80 GB, 100% compute). Vì vậy đợt 1 không chạy job GPU nào. E1 và E7 của session kia chạy trên CPU.

## Đợt 1: đã làm

### Hạ tầng
- [x] Env `cfm` trên lab09 (numpy, scipy, matplotlib, tectonic, poppler), `scripts/build_papers.sh`, `scripts/contact_sheet.py`.
- [x] Font Helvetica dạng TrueType cho hình (`scripts/make_tt_fonts.py`), style chung `scripts/figstyle.py`.
- [x] CIFAR-10 ở `/mnt/data/khoitm8/datasets/cifar10/`.

### Bài A: `paper_theory/` (TMLR), 53 trang
- [x] Compile sạch: không có reference hay citation hỏng, không có overfull box.
- [x] Hình mới: bản đồ vùng hút (Hình 1), bảng các công thức sampler (Hình 4), pitchfork và thu gọn ngưỡng (Hình 3), parity learned so với exact (Hình 5), CIFAR composition vẽ lại.
- [x] Định vị lại đóng góp theo Liu & Zuazua v2 (arXiv 2605.12231v2), Azangulov et al. 2026 và Wan et al. 2025. Điểm còn mới: kết quả "hầu hết điểm đầu kết thúc trên một atom", hỗn hợp tổng quát, schedule có biến phân bị chặn, blend khi có từ ba trường, tiêu chí phổ, tổ hợp có dấu.
- [x] Kết quả mới: trên tam giác, conjunction exact còn kết thúc ở các trung điểm cạnh. Phân phối tâm/cạnh/điểm train là 13/41/46% ở 2w_c; cạnh hút khi w > 1.368 w_c. Hai bộ tích phân độc lập đều cho kết quả này.
- Chi tiết: `docs/review/changes_paperA_2026-11-21.md`.

### Bài B: `paper_mechanism/` (NeurIPS 2027, đang dùng style TMLR), 35 trang
- [x] Dựng từ `paper/main.tex`. Phần viết mới: abstract, intro, related work, mục swap, limitations.
- [x] Hình mới: Hình 1 "một latent, hai đồng hồ", hình cơ chế, hình collapse (gộp 3 hình cũ), hình swap, hình landing. Main text giảm từ 8 hình xuống 5.
- [x] Sửa theo bản ghi nhớ của session kia, sau khi kiểm chứng độc lập (`docs/review/memo_verification_2026-11-21.json`). Các điểm chính: net→exact luôn hạ cánh là do cấu trúc sampler; đoạn "Two times"; so sánh AUC chỉ là sổ sách; slope h = 6 không lặp lại được; định vị so với Bertrand và Liu et al. 2025.
- [x] Thêm E1 (swap theo cửa sổ; dự đoán P1.2 bị bác bỏ) và E7 (collapse của exact posterior; để ở appendix).
- Chi tiết: `docs/review/changes_paperB_2026-11-21.md`.

## Đợt 2: cần GPU 6 rảnh

Bài B, theo thứ tự ưu tiên:
1. Swap trên model 2000 ảnh, và ghi lại khoảng cách lúc bàn giao.
2. E1 trên các model subset (cần chép checkpoint subset sang lab09).
3. Can thiệp vào cửa sổ σ mà ϱ chỉ ra, dự đoán trước tỉ lệ memorization.
4. Lưới N ∈ {500, 1k, 2k, 5k} × 3 seed, có augmentation, so với Bonnaire et al.
5. CFG trên model thật; tăng quy mô (CIFAR-10 đầy đủ hoặc ImageNet-64).

Bài A: không cần GPU. Cần thêm một script tái lập cho con số "learned networks gần trung điểm cạnh", và một cách dựng tam giác/simplex cố định, vì `simplex()` xoay theo bản LAPACK.

## Quyết định của tác giả (còn mở)
- Bài B dài hơn 9 trang NeurIPS (main text tới trang 15 ở style TMLR). Cần chọn phần chuyển sang appendix.
- Bài A: giữ hay bỏ mệnh đề về sampler ngẫu nhiên (Azangulov) trong abstract. Abstract hiện khoảng 260 từ.
- Bài B: tên mục 5.3 ("stays open until late") và cách gọi các mức swap là "nominal".
- Tên script `paperB_*` trong reproducibility statement có thể làm lộ việc tách bài khi nộp ẩn danh.
- Tự kiểm chứng các chứng minh mới của bài A (`cor:twofields`, `prop:twoatom`, `rem:generic`) và câu khai báo dùng LLM ở cả hai bài.
