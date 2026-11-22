# Bản phân chia nội dung A/B cho các tác nhân viết và duyệt (bản nháp 2026-11-22, chờ nhóm duyệt)

**Trạng thái.** Việc tách bài vẫn **tạm thời, chưa chốt**. `paper/main.tex` vẫn là bản chính. File này chỉ quy định các tác nhân được làm gì trên hai bản nháp `paper_theory/` (A) và `paper_mechanism/` (B). Phương án là bản lai: giữ đường cắt và bản nháp ngày 21/11, lấy một số đề xuất của `final_report.md` (22/11), bỏ những đề xuất mà bản kiểm lại đã bác.

**Căn cứ.**
- `docs/plan/paper_split_plan_2026-11-21.md`, `paper_theory/README.md`, `paper_mechanism/README.md`.
- `final_report.md` (báo cáo tổng hợp của 6 tác nhân cloud, 22/11).
- Hai báo cáo kiểm lại ngày 22/11: so sánh phương án chia và venue; kiểm lỗi `final_report.md`.

---

## 1. Quy trình và quyền sửa file

- Nhánh gốc: `paper-split-drafts` (commit `1979b9b`). Mỗi tác nhân làm trong worktree riêng tách từ nhánh này. Không ai push.
- Mỗi file chỉ có một tác nhân được sửa:

| Tác nhân | Được sửa | Chỉ đọc |
|---|---|---|
| Viết A | `paper_theory/main.tex`, `paper_theory/refs.bib` | mọi thứ khác |
| Duyệt hình A | các script vẽ hình của A (mục 4), `paper_theory/figures/` | `main.tex` (caption chỉ đề xuất) |
| Viết B | `paper_mechanism/main.tex`, `paper_mechanism/refs.bib` | mọi thứ khác |
| Duyệt hình B | các script vẽ hình của B (mục 4), `paper_mechanism/figures/` | `main.tex` (caption chỉ đề xuất) |
| Kiểm số, định lý, build, trùng lặp | không sửa gì | tất cả |
| Giám sát tuân thủ | không sửa gì | tất cả |

- Không sửa `paper/main.tex`, `results/`, `src/`, `configs/`. Không chạy train hay inference mới.
- Đề xuất sửa caption: tác nhân duyệt hình ghi vào báo cáo của mình. Tác nhân viết là người áp vào `main.tex`.

## 2. Định lý, kết quả và bằng chứng: thuộc bài nào

Không định lý nào là đóng góp của cả hai bài. Không đoạn văn, hình hay con số nào xuất hiện ở cả hai bài (luật no-reuse của TMLR; ICML coi bài nộp đồng thời là prior work).

| Bài A (exact field) | Bài B (field đã học, EDM) |
|---|---|
| `prop:collapse`, `prop:kernel-field`, `thm:endpoint` (đóng góp) | Ba kết quả này chỉ **phát biểu lại bằng lời khác**, không chứng minh lại, trích nguồn (mục 3) |
| Toàn bộ phần can thiệp: posmix, cfgatom, schedule, composition, spectral, `cor:twofields`, `prop:twoatom`, `rem:generic`, conjunction, `prop:bottleneck`, `prop:tgtnoise`, `prop:regular` | `thm:transfer` (hạ xuống bổ đề), `prop:localtransfer`, `thm:relerr` (headline), `thm:risktransfer`, `prop:loss-no-certificate`, `prop:trap`, `prop:heun` |
| Numerics exact field, positive control, signed combinations, composition trên cặp ảnh CIFAR, learned composition, pilot label averaging | EXP-1 và CIFAR hard-conditioning collapse, measured transfer, toàn bộ EDM (landing, swap, late contraction, Heun) |
| **Kernel tracking** (label smoothing so với `tr Cov_h`, bảng `tab:p7kernel`, slope CIFAR, số 0.276) | Không còn kernel tracking. Đoạn "Label smoothing and the kernel reference" (B, khoảng dòng 575–581) và các panel liên quan chuyển sang A |

Việc chuyển kernel tracking cần hai tác nhân viết làm khớp nhau: B xoá, A thêm (vào phần numerical evidence hoặc phụ lục). Tác nhân giám sát kiểm hai bên khớp.

## 3. B dựa vào đâu cho các kết quả exact field

- Hiện B trích `companionA` 13 lần. Không dùng được nếu B nộp trước khi A công khai: đến hạn nộp B, A chưa nộp ở đâu và chưa có trên arXiv.
- **Mặc định cho tác nhân viết B:** viết B tự chứa. Các sự kiện ở h=0 trích Wan et al. 2025 (`wan2025elucidating`, hiện chỉ có trong `paper_theory/refs.bib`, cần chép sang `paper_mechanism/refs.bib`) và Baptista et al. 2025. Giữ `companionA` chỉ ở các chỗ thật sự cần và đánh dấu `% DECISION` để nhóm quyết (mục 7).
- Viết lại mục "Background: the exact reference" của B bằng lời của B. Hiện mục này trùng khoảng 64% (8-gram) với A.

## 4. Hình

- A: `fig_unrolled_exact`, `fig_composition`, `fig_signed_combinations`, `fig_learned_composition`, `fig_cifar_composition`, `fig_intervention_validation`, các hình tikz (proof template). Thêm panel kernel tracking nếu chuyển sang (vẽ từ cùng dữ liệu, không chép file hình của B).
- B: `fig_teaser`, `fig_mechanism`, `fig_collapse`, `fig_collapse_details`, `fig_swap`, `fig_landing`, `fig_heun`, `fig_posterior_choice`, `fig_image_class`, `fig_image_training`. Bỏ panel kernel tracking khỏi `fig_collapse` / `fig_collapse_details` khi chuyển sang A.
- Script tương ứng: A dùng `make_theory_hero_figure.py`, `make_composition_figure.py`, `make_signed_combinations_figure.py`, `make_learned_composition_figure.py`, `make_theory_cifar_composition_figure.py`, `make_intervention_validation_figure.py`. B dùng `make_paperB_figures_v2.py`, `make_swap_figure.py`, `make_collapse_choice_figure.py`, `make_edm_figures.py`. Style chung: `scripts/figstyle.py`.
- Hai script `figstyle.py` và `make_swap_figure.py` đang gắn cứng `/mnt/data/khoitm8/...` (font, CIFAR). Trên máy khác: không có thư mục font đó thì `figstyle.py` lùi về Helvetica, Arial, Liberation Sans hoặc DejaVu Sans (font trên hình sẽ khác bản hiện tại); `make_swap_figure.py` cần truyền `--cifar <thư mục cifar-10-batches-py>`. Tác nhân duyệt hình không đổi hai script này nếu chưa được nhóm đồng ý; chỉ vẽ lại những hình chạy được, và ghi rõ hình nào không vẽ lại được và vì sao.
- Tiêu chí duyệt hình dữ liệu (matplotlib): skill `dataviz` là chuẩn chính (dạng biểu đồ, bảng màu kiểm cho người mù màu, trục, legend, chú thích). Lấy thêm vòng lặp "render, chụp ảnh, tự đánh giá, chỉnh" của SciVisAgentSkills (bản tải về ở `../SciVisAgentSkills`; repo này dành cho ParaView/napari/VMD/TTK nên chỉ dùng làm tham khảo phụ). Mọi hình phải vẽ lại từ `results/`, giữ nguyên dữ liệu và các số ghi trên hình.
- Mỗi bài thêm **một hình sơ đồ tổng quan** theo phong cách hình kiến trúc của paper CV (khối màu, mũi tên có nghĩa, legend ở góc, ghi tham số dưới khối), vẽ bằng TikZ trong `figures/tikz/` của bài đó. Tham khảo `../PlotNeuralNet` (chỉ để mượn phong cách khối; kiến trúc mạng không phải đóng góp của bài).
  - A: tập train hữu hạn và nhãn đi vào exact field; các can thiệp (label noise, label averaging, guidance, schedule) đều dẫn về endpoint là ảnh train; riêng composition (guidance trên field đã label-average) dẫn tới blend, kèm ngưỡng w > 1/sinh²B.
  - B: nhiễu đi qua sampler EDM, khối denoiser D(x;σ) ở từng mức σ, trục thời gian có ba mốc (chọn ảnh; bản sao xuất hiện trong D; trạng thái chạm ảnh khi ϱ < 1), cạnh đó là sơ đồ hai kiểu swap net→exact và exact→net.
  - Tác nhân duyệt hình tạo file TikZ và kiểm nó build được độc lập; tác nhân viết chèn vào `main.tex` và viết caption.

## 5. Lấy gì, bỏ gì từ `final_report.md`

**Lấy:**
- Không dùng chung văn bản, hình, số (mục 2).
- B: `thm:relerr` làm headline; transfer hạ xuống bổ đề; late contraction và "bound never violated" chỉ để mô tả hoặc kiểm code.
- Kernel tracking về A (mục 2); B tự chứa (mục 3).
- Sửa F3 trong B (dòng 605 "We test Theorem relerr"): code `scripts/n3_directional_q.py` (khoảng dòng 126) đo |x−a|, là đại lượng của `prop:trap`. Sửa bằng câu chữ, không đo lại.

**Không lấy:**
- Không đổi headline của A sang mệnh đề AND/nhãn lớp. Trường hợp w=0 đã có trong Liu–Zuazua v2 (Thm 2.5); phần w≠0 chưa kiểm; ngưỡng AND trong báo cáo bị phát biểu sai (0<w<½ đã cho blend, ngưỡng ½ chỉ thuộc guidance âm). A giữ headline hiện tại.
- Không mở bài B bằng swap ngược exact→net. Trên sub500 swap này cho 0% off-atom ở mọi s (`results/n3_followup_sub500_20261111/SWAP_SUMMARY.md`); chỉ dùng nó để phân biệt model memorise và model không memorise.
- Không "sửa lỗi `n2` NaN": đó là chế độ `--forward-only` của `n3_directional_q.py`, không phải lỗi dữ liệu. Nếu cần tiêu chí trạng thái, dùng `n3_rho_20261117/sub500` (n2 hữu hạn).
- Không đặt số 0.276 vào phần hard-conditioning của B: đó là số h=6 của kernel tracking (A). SD mẫu là ±0.008.
- Không thêm việc cần inference hay train mới (đường cong bắt giữ, swap sub2000, CelebA-32). Ghi chúng vào Limitations hoặc "planned experiments" nếu cần.

## 6. Quy tắc viết (cho tác nhân viết A và B)

- Người đọc là reviewer chuyên ngành (TMLR / NeurIPS / ICML). Mục tiêu: một người ngoài nhóm đọc abstract, introduction và đoạn mở đầu mỗi section thì hiểu bài làm gì, để làm gì, có ích cho ai, và đóng góp của nhóm là gì.
- Lấy các nguyên tắc viết rõ ràng của skill cover-letter (câu ngắn, nói thẳng, có bằng chứng, không sáo rỗng, không phóng đại), **không** lấy giọng thư xin việc cá nhân.
- Phạm vi viết lại: abstract, introduction, related work, đoạn "What this means in practice", đoạn mở đầu và kết mỗi section, limitations, conclusion, caption.
- **Không sửa** phát biểu định lý, chứng minh, ký hiệu, giả thiết, hay con số. Nếu thấy chỗ sai, ghi `% FLAG:` kèm lý do và để tác nhân kiểm tra xử lý.
- Không thêm khẳng định mà `results/` không hỗ trợ. Không thêm trích dẫn chưa kiểm được; trích dẫn mới phải có trong refs.bib với thông tin xuất bản kiểm được.
- Giữ ASCII trong code và script; tiếng Anh trong paper.

## 7. Các quyết định chỉ nhóm được làm (tác nhân không tự quyết)

1. Có tách bài hay không; headline cuối của A và của B.
2. Thứ tự nộp và venue (A: TMLR rồi J2C; B: NeurIPS 2027 mặc định, ICML 2027 nếu đủ điều kiện ở mốc 5/1).
3. A có đăng arXiv trước để B trích được không (ảnh hưởng mục 3).
4. Có đưa mệnh đề AND/nhãn lớp vào A không (cần A3 và kiểm phần w≠0).
5. Câu khai báo dùng LLM ở cả hai bài.
6. Tự kiểm ba chứng minh mới của A: `cor:twofields`, `prop:twoatom`, `rem:generic`.

Tác nhân gặp các điểm này thì đánh dấu `% DECISION:` trong `main.tex` và nêu trong báo cáo, không tự chọn.

## 8. Tác nhân kiểm tra chạy gì sau mỗi lượt viết

- Build cả A và B (`latexmk -pdf`), không lỗi, không reference hay citation hỏng; ghi số trang main text.
- Đối chiếu từng phát biểu định lý, mệnh đề, giả thiết của A và B với `paper/main.tex` (trừ 3 kết quả mới của A); báo mọi khác biệt.
- Đối chiếu mọi con số trong A và B với `results/` (dùng `scripts/verify_paper_numbers.py` và các script `paperB_verify_*` khi áp dụng được; torch không có trên máy này).
- Đo trùng lặp 8-gram giữa A và B theo từng section; báo section nào còn trùng.
- Kiểm mục 2–5 được tuân thủ; liệt kê mọi `% FLAG:` và `% DECISION:`.
