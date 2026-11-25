# Kế hoạch agent cho đợt sửa trình bày (2026-11-25)

Đầu vào: [REVIEW.md](../review/presentation_2026-11-25/REVIEW.md) và [shared_notation.md](../notation/shared_notation.md) (đã chốt).

## Nguyên tắc

- **Hai paper là hai file `main.tex`.** Không bao giờ để hai writer sửa cùng một file cùng lúc. Writer nào cũng
  làm trong worktree và branch riêng; session chính merge theo thứ tự.
- **Session chính (orchestrator) là người giám sát.** Không tạo thêm một agent "supervisor": nó chỉ đọc lại những
  gì session chính đã biết, mà lại tốn thêm chi phí. Việc giám sát dựa trên các gate tất định (mục Gate) và các
  checker chỉ đọc.
- **Proof là của tác giả.** Agent chỉ tái cấu trúc cách trình bày. Mọi diff chạm vào proof phải qua checker
  "math invariance" **và** được tác giả duyệt. Không agent nào được ghi rằng proof do AI viết.
- Job dài trên lab09 hoặc nexai-sv20 thì chỉ launch rồi đọc kết quả khi xong; không theo dõi tiến độ.

## Các agent

| # | Agent | Loại | Sửa file | Skill | Giai đoạn |
|---|---|---|---|---|---|
| W1 | Notation-A | session, worktree | `paper_theory/main.tex`, `math_commands.tex` (cả hai bản) | `phd-skills:paper-writing` | 1 |
| W2 | Notation-B | session, worktree | `paper_mechanism/main.tex` | `phd-skills:paper-writing` | 1 |
| W3 | Figures | session, worktree | `scripts/figstyle.py`, `*/figures/tikz/*.tex` (file mới) | `scientific-figure-making`, `opentikz:using-opentikz` | 1 (song song) |
| W4 | Structure-A | session, worktree | A main text, §1–9 | `academic-research-skills:academic-paper` (revision mode, dùng REVIEW.md làm roadmap), `ml-paper-writing` | 2 |
| W5 | Proofs-A | session, worktree | A appendix | `phd-skills:paper-writing` | 3 (chạy sau W4, vì W4 đổi số thứ tự theorem) |
| W6 | Text-B | session, worktree | B main text và appendix | `academic-research-skills:academic-paper` (revision), `ml-paper-writing` | 2 (song song với W4) |
| C1 | Math-invariance | subagent, chỉ đọc | — | không cần skill; agent mới với context sạch, chỉ nhận diff cũ/mới | sau mỗi writer chạm vào toán |
| C2 | Consistency audit | subagent, chỉ đọc | — | `phd-skills:xray` (numbers, terminology, code-paper, citation, eval) | Gate 2 và Gate 3 |
| C3 | Harsh re-review | subagent, chỉ đọc | — | `academic-research-skills:academic-paper-reviewer` (quick, hoặc full nếu cần panel) | Gate 3 |

Tổng cộng: **6 writer** (tối đa 3 chạy cùng lúc), **3 checker**, và session chính đóng vai orchestrator.

## Giai đoạn và gate

**Giai đoạn 1 (song song): W1, W2, W3**
- W1 và W2 áp mục 3 của `shared_notation.md`, mỗi lần một ký hiệu và commit riêng cho từng ký hiệu (dễ review,
  dễ revert). W1 thêm macro vào `math_commands.tex` rồi chép sang paper B.
- W3 sửa font (`mathtext.fontset="cm"`, bỏ fallback stixsans), chạy lại mọi figure script trên lab09, và vẽ
  A-F1…A-F3, B-F1 thành các file TikZ mới (chưa chèn vào tex).

**Gate 1:** notation lint (script grep các ký hiệu bị cấm, sẽ viết ở giai đoạn 0), `python submit/build.py`,
và C1 trên diff của W1 và W2. Tác giả duyệt. Merge W1 → W2 → W3.

**Giai đoạn 2 (song song): W4 (A body) và W6 (B)**
- W4: gộp 20 statement → 8, cắt trang 11–21, chuyển số liệu thành bảng, thêm khung proof template và
  Algorithm, chèn figure của W3.
- W6: cắt §5 của B, bảng AUC và bảng window-swap, thêm Algorithm cho swap, chèn B-F1.

**Gate 2:** C1 trên mọi phát biểu theorem đã gộp; C2 (`xray`) để chắc không con số nào thay đổi khi chuyển từ
văn xuôi sang bảng; build; so số trang. Tác giả duyệt. Merge.

**Giai đoạn 3: W5 (proof ở appendix A)**
- Viết lại cấu trúc theo khung Setup → Step → Conclusion; chỉ giữ hai lemma dùng chung (B.2, B.3).

**Gate 3:** C1 trên từng proof, đối chiếu từng bước. C2 chạy lần cuối. C3 đọc lại cả hai PDF bằng giọng reviewer
khó tính. Tác giả duyệt.

## Gate tất định (không cần agent)

| Gate | Cách làm |
|---|---|
| Build và leak scan | `python submit/build.py A_tmlr A_arxiv B_neurips` |
| Không còn tham chiếu `??` | `pdftotext` rồi grep |
| Notation lint | Script mới: grep các mẫu bị cấm (`w_i^{(h)}`, `\omega_t`, `w_c^{\rm spec}`, `label smoothing`, …). Exit khác 0 nếu còn sót |
| Con số không đổi | So multiset các số trong PDF trước và sau mỗi giai đoạn; mọi khác biệt phải có lý do |
| Font | `pdffonts` không còn STIXGeneral |
