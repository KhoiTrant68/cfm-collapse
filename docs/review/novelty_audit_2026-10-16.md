# Đối chiếu novelty của bản thảo — 16/10/2026

**Kết luận:** ứng viên novelty đáng bảo vệ nhất là hội tụ của các exact fields đã can thiệp và việc chứng minh các basin kết thúc ngoài atoms có độ đo Lebesgue bằng không. Phát biểu chung “loss nhỏ không bảo đảm sinh mẫu đúng” đã có tiền lệ rõ; risk-transfer bound hiện tại là một chứng nhận chuyên biệt với công cụ ổn định chuẩn. Không nên đặt hai phần đó ngang hàng như hai phát hiện nền tảng hoàn toàn mới.

Đây là đánh giá theo các nguồn đã kiểm tra, không phải chứng nhận không tồn tại prior work. Bản thảo được đối chiếu có SHA256 `c38aacedd1b31a9c11838a7c85244c76331357605e86286bb67bdff4db178cf4`. Lượt này không sửa manuscript hoặc chứng minh.

## 1. Bảng quyết định theo từng claim

| Claim trong bài | Đối chiếu quan trọng | Đánh giá và cách dùng |
|---|---|---|
| Empirical conditional minimizer memorises | Baptista, Theorem 6.4; Dasgupta, Sections 3.2–3.3 | Đã có. Dùng làm nền tảng. |
| Gaussian label noise dẫn đến NW weights và atomic reference | Công thức conditional expectation/Bayes và empirical flow recovery | Công thức cụ thể hữu ích, nhưng phép suy ra ngắn. Novelty khái niệm thấp; không đủ tự gánh paper. |
| Positive label-field averaging: mọi trajectory hội tụ, a.s. endpoint là atom (`prop:filtered`) | Pfrommer Theorems 2–3; Liu–Zuazua single-score and mixed-score papers | Ứng viên mở rộng thực chất. Phải nhấn mạnh averaging các fields, không phải averaging endpoint laws; chưa tìm thấy nguồn đã đọc bao hàm đúng arbitrary probability measure trong phát biểu này. Mức tin cậy về khoảng trống: vừa. |
| Signed CFG, fixed finite nonnegative strength: mọi trajectory hội tụ, a.s. atom (`prop:cfgatom`, h>0) | Liu–Zuazua, Geometric Asymptotics, Theorem 3.18 và Remark 3.19 | Ứng viên mạnh nhất. Nguồn gần nhất vẫn cần điều kiện trên omega-limit set; bài hiện tại chứng minh hội tụ và null exceptional basins trong trường hợp support chung. Mức tin cậy: vừa, không phải ưu tiên đã chứng nhận. |
| Hard CFG tại nhãn định danh hội tụ tới atom đó từ mọi initial point | Hard-label collapse đã biết; mixed-score geometry rộng hơn | Một kết quả bổ sung rõ, nhưng cấu trúc singleton làm trường hợp này đặc biệt. Không mở rộng thành claim về mọi điều kiện hoặc guidance schedule. |
| Small teacher loss nhưng endpoint variance không mất (`prop:loss-no-certificate`) | Benton Section 3; Beltran-Velez et al., Appendix D.1 | Ý tưởng tổng quát đã có. Điểm riêng là closed-form affine construction, fixed singular teacher và exact nonvanishing endpoint covariance. Giá trị minh họa tốt, novelty độc lập thấp đến vừa. |
| Finite-time W2/mean/variance certificate under risk transfer (`thm:risktransfer`) | Benton Theorem 1/Proposition 2; standard coupling/variation of constants | Chuyên biệt hóa hữu ích; proof mechanism chuẩn. Chưa có cơ sở coi là phương pháp ổn định mới. |
| Atomic W2 floor; target/interpolant-noise distinctions | Finite-support transport/quantization; Bertrand closed-form FM | Các hệ quả chuẩn hoặc mở rộng cụ thể. Nên để làm consequences/context. |
| Effective bandwidth, calibration và 5-seed negative validation | Kernel diagnostics; Pfrommer schedule deviation là hướng khác | Có giá trị phân tích thực nghiệm, nhưng moment fit không nhận dạng law. Các thí nghiệm mới kiểm tra giới hạn, không tự xác nhận novelty toán học. |

Các mức trên là nhận định nghiên cứu. “Chưa thấy bị bao hàm” yếu hơn “định lý mới đầu tiên”.

## 2. Những nguồn làm thay đổi đánh giá

### 2.1 Benton–Deligiannidis–Doucet: không được trình bày loss obstruction như mới

[Error Bounds for Flow Matching Methods, Section 3, Theorem 1, Proposition 2](https://arxiv.org/html/2305.16860v2): bound W2 phụ thuộc L2 approximation error và tích phân Lipschitz của learned field. Phần trước theorem đã mô tả error nhỏ dưới teacher nhưng lớn dưới rollout; cuối proof cũng chỉ ra sự bất đối xứng giữa hai distribution. Vì vậy cả obstruction lẫn công cụ ổn định không mới ở mức tổng quát. Metadata TMLR 2024 xuất hiện trong [DBLP](https://dblp.org/db/journals/tmlr/tmlr2024.html); trang đầy đủ bị access challenge khi mở, nội dung theorem đối chiếu trên arXiv v2.

**Suy luận của lượt audit:** theorem hiện tại không tự kiểm soát K(t). Nó dùng một điều kiện trực tiếp về error dưới rollout thay cho regularity của learned field. Đây là khác biệt về giả thiết, chưa phải một certificate mạnh hơn trên cùng lớp fields.

### 2.2 Beltran-Velez và cộng sự: prior work gần hơn cho phản ví dụ

[The Reward Was in Your Data All Along, Appendix D.1, Propositions D.1 và D.3](https://arxiv.org/html/2606.19162): có Gaussian linear variance-inflation example và radial-shell construction với teacher error nhỏ nhưng endpoint reward sai. Bài này cũng phân biệt teacher và rollout marginals. Không nên tuyên bố lần đầu phát hiện distribution-shift obstruction. Khác biệt của construction hiện tại là teacher atom cố định, loss tích phân tiến tới zero và endpoint đúng N(a,I), thay vì concentrated Gaussian targets/reward certificates. Reward gap không tự đồng nhất với W2 hay endpoint variance.

### 2.3 Liu–Zuazua: almost-sure convergence của ordinary score đã có

[A PDE Perspective on Generative Diffusion Models, v3, Theorem 3.7](https://arxiv.org/html/2511.05940v3): với compact support, Lebesgue-almost every terminal point hội tụ về support; finite support có trajectory-wise rate. Bản v3 sửa ngày 07/10/2026 theo [submission history](https://arxiv.org/abs/2511.05940). Vì vậy so sánh chỉ với câu hỏi bỏ ngỏ trong Baptista là thiếu. Phạm vi riêng cần là các fields đã averaging/guidance, không phải ordinary exact-score a.s. memorisation. Không khẳng định toàn bộ theorem này đã hiện diện từ v1 năm 2025.

### 2.4 Liu–Zuazua: nguồn gần nhất với CFG theorem

[Geometric Asymptotics of Score Mixing and Guidance in Diffusion Models, v1, Theorems 3.16/3.18 và Remark 3.19](https://arxiv.org/html/2605.12231): xét hai supports tổng quát; autonomous limiting system hội tụ, còn original flow cần loại trừ non-minimizing critical points trong omega-limit set. Remark 3.19 nêu almost-everywhere avoidance còn mở. So với đó, bài hiện tại xét conditional/unconditional weights có cùng finite support ở h>0 và chứng minh null exceptional basins. Đây là một kết quả hẹp hơn về supports nhưng mạnh hơn về kết luận hội tụ trong trường hợp ấy; không được nói đã giải quyết bài toán supports khác nhau.

### 2.5 Pfrommer: label smoothness không mới, nhưng theorem không tự bao hàm averaging hiện tại

[Is Your Conditional Diffusion Model Actually Denoising?, Theorems 2–3](https://arxiv.org/html/2512.18736): minimum-curvature label interpolation và Fourier convolution. Các hệ số không nhất thiết là probability weights. Bài hiện tại không bao hàm mọi regularizer trong nguồn này; ngược lại nguồn đó cũng không cung cấp ngay theorem a.s. atomicity cho positive field averages đang xét.

## 3. Kiểm tra bao hàm ở mức toán học

### 3.1 Vì sao mixed-score literature thật sự liên quan

Đây là phép đổi biến suy ra từ công thức của manuscript, không phải một theorem mới được viện dẫn. Với original time t>0, đặt z=x/t và s=(1-t)^2/(2t^2). Với fixed atom weights p, density của z là

\[
q_{p,s}(z)=\sum_i p_i\,\mathcal N(z;x^i,2sI).
\]

Nếu m_p là posterior atom mean thì grad log q=(m_p-z)/(2s). Field dx/dt=(m_p-x)/(1-t) cho

\[
\frac{dz}{dt}=\frac{m_p-z}{t(1-t)},\qquad
\frac{ds}{dt}=-\frac{1-t}{t^3},\qquad
\frac{dz}{ds}=-\nabla\log q_{p,s}(z).
\]

CFG có hệ số tổng bằng một, nên phép đổi biến giữ nguyên signed combination, với lambda=1+w. Nó nằm trong đúng loại mixed-score dynamics, không thể bỏ qua literature đó chỉ vì ký hiệu flow matching khác diffusion.

Ở h>0, hai bộ weights đều dương trên A={x^1,...,x^N}; geometric potential trong nguồn mixed-score rút về dist(z,A)^2. Điều đó xác định limiting geometry nhưng chưa tự chứng minh hội tụ original non-autonomous trajectories hoặc null exceptional basins. Khoảng cách logic ấy là nơi cần đặt theorem hiện tại. Ở h=0 conditional support là singleton và unconditional support là A, nên không dùng lập luận support chung.

Đối với label averaging, average của grad log q là gradient của average log q, thường không phải score của một heat evolution. Bởi vậy không được áp dụng thẳng single-score theorem. Arbitrary probability averaging trong manuscript còn rộng hơn average của đúng hai fields.

### 3.2 Vì sao risk-transfer theorem có novelty thấp về kỹ thuật

Đặt e_t=Z_t-Y_t. Công thức của manuscript là

\[
\dot e_t=-e_t/(1-t)+\Delta(Z_t,t),\qquad
e_T=(1-T)\int_0^T\Delta(Z_t,t)/(1-t)\,dt.
\]

Shared-source coupling và Minkowski cho W2 không vượt quá integral L2 của vế phải. Thế m(t)≤K(t)r(t) cho đúng B_T trong bài; weighted Cauchy–Schwarz và các bất đẳng thức moment cho phần còn lại. Hệ số sqrt(T(1-T)) đến từ tích phân trực tiếp của (1-t)^(-2). Không có bước stability mới khó ở đây. Giá trị là công thức rõ và chỉ ra điều kiện cần kiểm tra, không phải tự động chuyển teacher loss thành endpoint guarantee.

Construction phản ví dụ có spatial Lipschitz scale khoảng log(1/delta)/delta. Nó không bác bỏ bounds có regularity constants đồng đều. Time jumps cũng khiến nó không phải một instance nguyên xi của mọi smooth-field theorem.

## 4. Các nguồn liên quan nhưng không trùng kết luận

| Nguồn đã kiểm tra | Nội dung cần phân biệt |
|---|---|
| [Su et al., On Flow Matching KL Divergence, Proposition 6.1 / Theorem B.2](https://arxiv.org/html/2511.05480) | Weak continuity solutions: loss nhỏ nhưng terminal KL lớn. KL không đồng nhất W2/variance; không coi là exact duplicate. |
| [Zhou–Liu, ICML 2025](https://proceedings.mlr.press/v267/zhou25l.html) | End-to-end estimation và W2 convergence với assumptions. Không phải theorem cho arbitrary small-loss fields không kiểm soát complexity. |
| [Kunkel, Lipschitz guarantees](https://arxiv.org/html/2509.02337) và [Stéphanovitch, regularity theory](https://arxiv.org/html/2604.06065) | Nhấn mạnh kiểm soát regularity để có sampling bounds; không biến K trong bài hiện tại thành đại lượng tự suy từ loss. |
| [Maduabuchi, Entropy-Controlled Flow Matching, Appendix I.2](https://arxiv.org/html/2602.22265v3) | Nguồn phát biểu interior singular collapse với endpoint matching giữ nguyên; không phải endpoint variance counterexample của manuscript. Không kiểm chứng lại toàn bộ proofs của nguồn này trong lượt audit. |
| [PerturbCellRL, Proposition 1](https://arxiv.org/html/2606.27752) | Loss minimizer trong restricted model family có thể sai target dù family chứa target law; khác vanishing-loss sequence đang xét. HTML và một số metadata provider dùng các title khác nhau; dùng ID để định danh. |
| [Li–Wang–Qu, NeurIPS 2025](https://papers.neurips.cc/paper_files/paper/2025/file/5ac55a8d65fb5ecd9ccaa852e21325db-Paper-Conference.pdf) | Linear CFG / contrastive principal components; khác finite empirical atomic endpoint theorem. |
| [Bertrand et al., NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/0ca819b3e8126e19a008c38cd0c371ea-Abstract-Conference.html) | Closed-form empirical FM và vai trò target stochasticity đã có. |
| [Baptista, Theorem 6.4](https://arxiv.org/html/2501.15785v2) | Hard empirical conditional trên observed labels và sự không xác định ngoài support. |

## 5. Định vị nên dùng và sửa cụ thể

**Đóng góp chính đề xuất:**

Tiêu đề tập trung hơn để cân nhắc: **Atomic Endpoints of Averaged and Guided Empirical Conditional Flows**. Loss obstruction và certificate có thể giữ như kết quả bổ trợ, với provenance rõ.

> We establish trajectory convergence and almost-sure atomic endpoints for positive label averages and the specified signed classifier-free guidance of empirical conditional fields. In the shared finite-support setting, our analysis treats exceptional tie basins rather than imposing their avoidance as a premise.

Sau đó mới nêu explicit hard-label counterexample như minh họa chuyên biệt của obstruction đã biết, và risk-transfer bound như sufficient condition chuyên biệt. Các negative experiments cho biết exact results chuyển sang trained models đến đâu.

Một câu trong Appendix B hiện cần sửa về logic định vị: “This change of distribution is a separate assumption in any certificate based on training loss.” Các certificates khác có thể kiểm soát vấn đề bằng regularity, không cần giả thiết trực tiếp m≤Kr. Câu thay thế đề xuất:

> Relating training error to generated trajectories requires additional control, which may be supplied by learned-field regularity or by a direct risk-transfer condition. We use the latter to obtain an explicit certificate for the collapsing hard-label reference.

Related work cần bổ sung ít nhất Benton, hai bài Liu–Zuazua và Beltran-Velez. Không cần tiếp tục chạy broad GPU sweeps để giải quyết vấn đề novelty này. Công việc ưu tiên là giải thích rõ phần theorem nào không suy ra từ các nguồn trên; nếu muốn nâng trọng lượng lý thuyết tiếp nữa, cần một kết quả vượt shared finite support hoặc một sufficient condition kiểm tra được cho transfer. Đó là nghiên cứu mới, chưa phải kết quả đã chứng minh.

**Đánh giá đóng góp:** còn một hướng novelty toán học có thể bảo vệ, nhưng hẹp hơn cách đặt hai trọng tâm trong title/abstract hiện tại. Chưa có cơ sở nói paper chắc chắn đủ ICLR/ICML, hoặc chắc chắn thiếu novelty. Trước khi nộp cần independent proof audit và bổ sung các comparisons nêu trên.

## 6. Phạm vi và log tìm kiếm

Đã tìm theo ba nhóm phrasing: empirical/atomic/Voronoi convergence; classifier-free guidance/score mixing/label averaging; small loss/endpoint error/counterexample/Lipschitz stability. Có truy vấn giới hạn proceedings ICLR, ICML/PMLR và NeurIPS cùng các preprints gần đây. Đây là targeted venue mining, không phải đọc toàn bộ proceedings 2024–2026. Backward chaining nối Benton tới Albergo/Alekseev–Gröbner và các mixed-score papers tới ordinary-score convergence. Không có complete forward-citation census.

Paper Search CLI chạy arXiv/Crossref, JSON errors={} cho các truy vấn đã lưu. Một số truy vấn literal-title trả về nhiều kết quả không đúng title; không xem chúng là evidence bao hàm hoặc evidence không có prior work. CORE/DOAJ thiếu optional keys và Unpaywall chưa cấu hình email; không sử dụng các providers đó. OpenReview PDF vES22INUKm và DBLP full page có challenge; thay bằng primary PMLR/arXiv và DBLP search metadata. Không dựa vào các trang tóm tắt thứ cấp để kết luận theorem.

Log CLI ở `tmp/reviewer-revision-2026-10-16/novelty-cli-*.json`. Không xuất BibTeX mới vì một số records chưa kiểm tra DBLP đầy đủ; metadata tác giả và title của các preprints chính được kiểm tra trên arXiv. Chưa kiểm chứng code của prior work; đây là audit novelty của statements/proof mechanisms, không phải reproduction.
