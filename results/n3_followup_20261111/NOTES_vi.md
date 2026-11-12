# Đề xuất 1 và 2: swap denoiser và đo μ (nexai-sv20, A30, 2026-11-11 01:16–02:02 UTC)

Hai model: EDM public cond-VP (train trên 50k ảnh) và model sub1000 (1000 ảnh, mới train 0,5 Mimg).
Cả hai đều cho 100% mẫu off-atom (d1/d2 >= 1/3), nên chưa tính được AUC on/off cho μ.
Chi tiết ở SWAP_SUMMARY.md và MU_SUMMARY.md.

## Swap (500 mẫu mỗi model)

- **net->exact** (model dùng cho sigma > s, exact field cho sigma <= s): 0% off-atom ở mọi s,
  kể cả s = 0,02 (t = 0,98). Chỉ cần thay field ở 2% thời gian cuối là mọi mẫu chuyển từ 100%
  off-atom sang 100% on-atom. "Có chạm ảnh train hay không" được quyết định ở cuối.
- **Ảnh nào được chọn** thì quyết định sớm. Tỉ lệ net->exact chạm đúng ảnh gần nhất với endpoint
  learned:

  | s | 5 | 2 | 1 | 0,5 | 0,2 | ≤ 0,1 |
  |---|---|---|---|---|---|---|
  | public | 31% | 56% | 90% | 96% | 99% | ~100% |
  | sub1000 | 49% | 63% | 88% | 95% | 98% | 100% |

  Đường learned chọn ảnh trong khoảng sigma 5 → 1 (t 0,17–0,5), tức ở noise trung bình. Điều này
  khớp với Dodson et al.
- **exact->net** (exact field cho sigma > s, network cho sigma <= s):
  - s >= 1: gần như toàn bộ off-atom. Phần cuối của network kéo mẫu ra khỏi ảnh mà exact field
    đã chọn.
  - s <= 0,1: on-atom, nhưng d1 không giảm mà xấp xỉ tỉ lệ với s: median 2,6 / 1,4 / 0,6 ở
    s = 0,1 / 0,05 / 0,02.
  - Nghĩa là network giữ nguyên độ lệch tại lúc giao (μ ≈ 1, không co), còn exact field sẽ đưa
    nó về 0.

## μ = (1+sigma) λ_max(sym ∂D/∂x) dọc đường learned (double-VJP, 20 vòng lặp)

- **public**, median μ: 4,9 → 2,7 → 1,7 → 2,1 → 1,00 ở t = 0,34 / 0,63 / 0,88 / 0,98 / 0,998.
  Chưa có mẫu nào μ < 1 cho đến t = 0,98.
- **sub1000**: 3,5 → 1,9 → 1,17 → 1,00 → 0,99. μ chỉ xuống dưới 1 ở bước cuối cùng, và chỉ chênh
  rất ít.
- **exact field** μ* (đo tại cùng điểm): bằng 0 từ t ≥ 0,63, tức posterior đã collapse.

## Đối chiếu với lý thuyết

- **Khớp:**
  - Exact field co mạnh (μ* = 0) nên net->exact luôn kết thúc trên ảnh train.
  - Network có μ ≥ 1 trên [t1, 1) với mọi t1 ≤ 0,98 nên không co, và kết thúc off-atom.
  - exact->net với s nhỏ giữ nguyên độ lệch, đúng trường hợp biên μ ≈ 1.
- **Hoà giải với Dodson:** ảnh nào được chọn là do noise trung bình; có chạm ảnh hay không là do
  field ở cuối. Phép swap của Dodson là giữa hai network, đều có μ ≈ 1, nên không thấy được hiệu
  ứng thứ hai.
- **Chưa kiểm được:** μ < 1 có báo trước mẫu memorize hay không. Để kiểm, cần một model
  memorize thật, tức train subset lâu hơn nhiều.
