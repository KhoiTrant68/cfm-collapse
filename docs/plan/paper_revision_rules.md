# Bộ rule chỉnh sửa paper (Paper A và Paper B)

Bản 2026-11-27. Đây là bộ rule mà mọi session đang dùng khi sửa hai paper. Nó gom lại từ self-feedback của tác giả,
[REVIEW.md](../review/presentation_2026-11-25/REVIEW.md), [shared_notation.md](../notation/shared_notation.md) và
[plan agent](presentation_revision_agents_2026-11-25.md).

**Nguyên tắc cốt lõi:** để toán gánh lập luận, để chữ gánh trực giác.

---

## R1. Ký hiệu

1. **Một bảng ký hiệu chung** cho cả hai paper: [shared_notation.md](../notation/shared_notation.md). Không đặt ký
   hiệu mới khi chưa có trong bảng này.
2. **Ký hiệu toàn cục** giữ một nghĩa duy nhất ở cả hai paper, ở cả main text lẫn appendix.
3. **Ký hiệu cục bộ** trong proof phải được khai báo ở dòng đầu của proof, và không được trùng với ký hiệu toàn cục.
4. **Sao trên** (`v^\star`, `m^\star`) chỉ đánh dấu đối tượng của exact field. **Sao dưới** (`\xi_\star`, `i_\star`)
   đánh dấu điểm hoặc chỉ số đặc biệt.
5. Trong phát biểu ở main text, `\delta` chỉ dùng cho Dirac.
6. `\varepsilon := 1-t` được định nghĩa ở Section 3 và dùng ở mọi chỗ sau đó; không viết `(1-t)` nữa.
7. Mỗi khái niệm chỉ có một tên gọi bằng chữ: label noise, hard conditioning, exact field, blend (A), off-atom (B).
8. `math_commands.tex` của hai paper phải giống hệt nhau từng byte.

## R2. Văn bản

1. Câu đầu tiên của mỗi đoạn là kết luận; các câu sau là bằng chứng.
2. Đoạn có từ 4 con số trở lên thì chuyển số vào bảng. Văn bản chỉ giữ con số quan trọng nhất kèm so sánh.
3. Đoạn dài quá 12 dòng thì cắt ra, hoặc chuyển thành list.
4. Mỗi section kết thúc bằng một câu takeaway.
5. Abstract khoảng 150 từ. Contributions tối đa 4 mục, mỗi mục tối đa 2 dòng, có trỏ tới theorem.
6. Mỗi ý chỉ nói một lần ở main text. Chi tiết phương pháp số, lỗi của bộ giải và kết quả phụ thì đưa vào appendix.
7. Chuyển văn xuôi thành bảng không được làm đổi con số nào. Có gate kiểm việc này (R8).

## R3. Viết toán (self-feedback của tác giả)

- Dùng display equation cho biểu thức quan trọng hoặc phức tạp; inline math chỉ dành cho ký hiệu ngắn và đơn giản.
- Tách định nghĩa, giả thiết, điều kiện và kết luận thành các khối logic riêng.
- Mỗi khối phương trình chỉ phục vụ một mục đích logic.
- Dẫn vào phương trình bằng câu toán học ngắn và trực tiếp: "Set", "Then", "Hence", "By (k)".
- Tránh nhồi quá nhiều ký hiệu vào một câu hay một đoạn; mỗi câu tối đa 2 biểu thức inline.
- Gom các phương trình liên quan và canh theo dấu bằng hoặc dấu bất đẳng thức.
- Chia các phép biến đổi dài thành từng bước canh thẳng hàng, dễ đọc.
- Đánh số các phương trình quan trọng và tham chiếu bằng số, không chép lại biểu thức.
- Giữ khoảng cách dọc nhất quán và đủ rộng quanh display equation.
- Xen kẽ câu chữ ngắn với display equation để mạch logic tự nhiên.
- Bỏ giải thích thừa và các chỗ lặp lại toán học không cần thiết.
- Ưu tiên dễ đọc và rõ ràng logic hơn là viết thật gọn.
- Khi tái cấu trúc, giữ nguyên mọi định nghĩa, giả thiết, ký hiệu và tính đúng của proof.
- Ưu tiên biểu thức toán hơn mô tả bằng lời khi biểu thức truyền đạt rõ hơn.
- Dùng ký hiệu toán để viết thẳng giả thiết, ràng buộc, quan hệ phụ thuộc và phép suy ra.
- Thay lời giải thích dài dòng về quan hệ toán học bằng phương trình hoặc phép suy diễn tường minh.
- Diễn đạt lập luận toán bằng các bước ký hiệu ngắn, nối tiếp nhau.
- Dùng lượng từ (`\forall`, `\exists`) và dấu suy ra (`\Rightarrow`) khi chúng làm câu chính xác và dễ đọc hơn.
- Không nhắc lại bằng lời những gì phương trình đã cho thấy rõ.
- Dùng pseudocode hoặc thuật toán cho mô tả thủ tục và tính toán.
- Chỉ dùng văn xuôi cho động cơ, diễn giải, lý do không hiển nhiên và bối cảnh cần thiết.
- Bỏ các cụm từ chuyển tiếp không cần thiết và các giải thích lặp lại.
- Ưu tiên phép suy diễn toán tường minh hơn mô tả dài bằng lời về phép thế hay phép biến đổi.
- Giảm tối đa sự thừa lời, nhưng không hy sinh tính chặt chẽ hay giả thiết cần thiết.
- Chọn cách trình bày gọn nhất phù hợp với nội dung: phương trình cho quan hệ toán, pseudocode cho thủ tục, văn xuôi
  cho ý tưởng.

## R4. Statement và chứng minh

1. Không chia một kết quả thành nhiều tầng Corollary, Proposition hay Remark. Trường hợp đặc biệt thì gộp thành một
   phần (a)/(b)/… của statement chính, hoặc nêu trong một câu "In particular".
2. Kết quả đã biết thì gọi là "Fact" và kèm trích dẫn; không đặt ngang hàng với đóng góp mới.
3. Ví dụ phản chứng thì đặt tên là "Example", không phải "Proposition".
4. Statement được gộp phải phát biểu đúng hợp các giả thiết và kết luận cũ, không mạnh hơn, không yếu hơn.
5. Appendix chỉ giữ những lemma dùng chung (được dùng từ 2 lần trở lên). Mọi bước khác viết thẳng trong proof.
6. Mỗi proof có khung cố định: **Setup** (khai báo biến cục bộ) → **Step 1…n** (tiêu đề của mỗi step là claim của
   step đó) → **Conclusion**.
7. Proof sketch ở main text tối đa 6 dòng. Dài hơn thì bỏ, vì proof đầy đủ đã có ở appendix.
8. Mỗi proof chỉ được trình bày một lần.
9. Proof là của tác giả. Agent chỉ tái cấu trúc cách trình bày, không viết lại lập luận, và không bao giờ ghi rằng
   proof do AI viết.

## R5. Proof template

1. Template dùng chung chỉ xuất hiện **một lần** ở main text, dưới dạng một khung implication:
   (S1) năng lượng hữu hạn ⇒ hội tụ về candidate; (S2) Θ > 0 ⇒ basin null; (S1) ∧ (S2) ⇒ endpoint là atom.
2. Ngay sau khung là một bảng cho biết mỗi kết quả kiểm S1 và S2 bằng cách nào, và kết luận ra sao.
3. Không dùng flowchart cho lập luận logic. Không dùng pseudocode cho proof; pseudocode chỉ dành cho thủ tục tính toán.

## R6. Figure

1. **Một font math** cho mọi figure: chữ dùng sans, math dùng Computer Modern hoặc Latin Modern cho khớp với thân
   bài. Không để font fallback như STIX.
2. Chữ nhỏ nhất sau khi scale không dưới 7pt (trừ chỉ số trên và dưới).
3. Nhãn trong figure theo đúng bảng ký hiệu (R1).
4. Figure ý tưởng thì làm theo mẫu trong `D:\AwesomeCV\reference`:
   - cùng một khung hình học lặp lại qua các panel, chỉ thay đổi can thiệp;
   - trường hợp của paper đặt cuối, có viền nổi bật;
   - phân biệt bằng màu kèm nhãn, có ✓ và ✗ cho từng tiêu chí.
5. Caption mở đầu bằng một câu kết luận.
6. Một kết quả chỉ được vẽ ở một figure; không vẽ trùng.
7. Schematic thì vẽ bằng TikZ; dữ liệu thì vẽ bằng matplotlib theo `scripts/figstyle.py`.

## R7. Quy trình

1. Hai writer không bao giờ sửa cùng một `main.tex` cùng lúc. Mỗi writer làm trong worktree và branch riêng.
2. Mỗi commit chỉ đổi một ký hiệu hoặc một hạng mục, để dễ review và dễ revert.
3. Không sửa đoạn "Use of large language models"; tác giả tự viết đoạn này.
4. Script sửa LaTeX phải viết bằng Write tool, không dùng Bash heredoc, vì heredoc làm mất dấu `\`.
5. Trên server dùng chung: không đụng driver NVIDIA, không xóa file khi chưa hỏi, không đụng `~/clic`. Job dài thì
   chỉ khởi chạy rồi đọc kết quả khi xong, không theo dõi tiến độ.
6. Không push hay merge khi tác giả chưa đồng ý.

## R8. Gate trước mỗi lần merge

| Gate | Lệnh hoặc cách làm | Đạt khi |
|---|---|---|
| Notation lint | `python scripts/check_notation.py` | in ra `clean` |
| Build và leak scan | `python submit/build.py A_tmlr A_arxiv B_neurips` | exit 0 |
| Tham chiếu | `pdftotext … \| grep -c '??'` | 0 |
| Con số | `python scripts/pdf_numbers.py compare <pdf> docs/plan/baseline_numbers_{A,B}.txt` | mọi khác biệt đều giải thích được (dời chỗ, xuống dòng, lỗi đọc text của figure) |
| Font | `pdffonts <pdf>` | không còn STIXGeneral |
| Bất biến toán | Agent kiểm tra độc lập với context sạch, chỉ đọc diff | PASS |
| Tác giả duyệt | Danh sách proof bị chạm | đồng ý |
