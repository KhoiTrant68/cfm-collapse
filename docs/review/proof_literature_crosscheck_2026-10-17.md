# Đối chiếu chứng minh với nguồn gốc — 17/10/2026

## Kết luận và phạm vi

Chưa phát hiện lỗ hổng toán học mới trong các bước được kiểm tra dưới đây. Đây là kiểm tra có giới hạn, không phải chứng nhận hình thức cho toàn bộ manuscript, không phải kết luận novelty hay bảo đảm chấp nhận tại hội nghị.

Đã đối chiếu trực tiếp các lập luận atomicity của `paper/main.tex` (đặc biệt proof `prop:cfgatom` và `prop:filtered`) và supplement `contribution_extension_proofs_2026-10-17.tex`: hội tụ trajectory, loại basin ngoài training set, guidance thay đổi theo thời gian, và basin ngoài training set của phép composition. Các phần thống kê, quantization, thực nghiệm và mọi citation khác của manuscript không nằm trong lượt audit này.

Supplement được kiểm tra có SHA256 `41013960b0918efc5695635813deabb35e490aab35ec8087f229bd380c03fa8b`. Không sửa phát biểu hoặc proof của supplement trong lượt này, nên hồ sơ phản biện và PDF trước đó vẫn gắn đúng source. Không sửa manuscript chính.

## Các nguồn đã đọc và cách sử dụng hợp lệ

| Nguồn gốc | Vị trí đã đối chiếu | Đối chiếu với bài mình | Giới hạn áp dụng |
|---|---|---|---|
| [Liu–Zuazua, Geometric Asymptotics of Score Mixing and Guidance](https://arxiv.org/html/2605.12231) | Theorem 3.16; §7.4, (7.9)–(7.12); Lemma 7.2; Theorem 3.18 và Remark 3.19 | Khuôn energy → loại cluster point → tập giới hạn hữu hạn → hội tụ rất gần | §7.4 xét inclusion tự trị giới hạn; Theorem 3.18 cho flow gốc có điều kiện. Remark 3.19 để mở tránh critical point không cực tiểu trong thiết lập tổng quát của họ. |
| [Liu–Zuazua, A PDE Perspective on Generative Diffusion Models, v3](https://arxiv.org/html/2511.05940v3) | Theorem 3.7(i)–(iii) | Đối chứng cho almost-everywhere endpoint thuộc support khi chỉ dùng một score | Không tự suy ra kết quả cho trung bình các conditional field hay signed CFG; trọng số endpoint không tự được xác định. |
| [Wainwright–Jordan, Graphical Models, Exponential Families, and Variational Inference](https://people.eecs.berkeley.edu/~jordan/sail/readings/wainwright-jordan-fnt.pdf) | §3.5.1, Proposition **2**, (3.41a,b), trang in 61–62 của bản tác giả | Đạo hàm log-partition bằng mean; Hessian bằng covariance | Bản PDF này đánh số Proposition 2, không dùng số Proposition 3.1 từ bản khác. Tính PSD của từng covariance không chuyển sang tổ hợp có hệ số âm. |
| [Lee–Simchowitz–Jordan–Recht, Gradient Descent Only Converges to Minimizers](https://proceedings.mlr.press/v49/lee16.pdf) | Theorem **4**, Theorem 7, Proposition 8 và proof ở §4 | Đối chứng cách basin ngoại lệ trở thành tập null rồi kéo ngược qua diffeomorphism | Cần objective tự trị C², strict saddle và bước nhỏ hơn 1/L. Không phải định lý áp dụng trực tiếp cho flow phụ thuộc thời gian với singular endpoint của bài mình. |
| [Ames et al., Control Barrier Functions: Theory and Applications](https://arxiv.org/pdf/1903.11199) | §I-A, điều kiện Nagumo trên biên | Khuôn inward boundary cho interval bất biến của biến u=βx | Invariance riêng lẻ chưa chứng minh x→0 hoặc basin có xác suất dương. Cần thêm β→∞ và kéo ngược interval qua finite-time flow. |
| [Aliyari Ghassabeh, On the Convergence of the Mean Shift Algorithm with the Gaussian Kernel](https://www.cs.toronto.edu/~aliyari/papers/JMVA.pdf) | §2; §4.2, Theorem 1 | Đối chứng việc phải có cấu trúc bổ sung mới suy ra hội tụ một điểm | Nguồn yêu cầu stationary points isolated. Không được suy ra Gaussian mixture luôn có hữu hạn stationary points chỉ từ số atom hữu hạn. |
| [Jiang–Ma, Analytic Distribution of Classifier-Free Guidance for Schedule Design](https://arxiv.org/html/2607.19725) | Theorems 4.2–4.3, đặc biệt giả thiết của 4.3 | Đối chứng rằng guidance theo thời gian cần nêu regularity và flow assumptions rõ | Công thức mật độ trên [t₀,T] với positive smooth densities, W¹,¹ schedule và integrals hữu hạn không tự cho atomic endpoint ở thời gian singular. |

Các nguồn được dùng làm đối chiếu giả thiết và bước proof, không dùng làm “bỏ phiếu” xác nhận kết quả. Truy vấn CLI ban đầu cho bốn kết quả Crossref không phù hợp và không có kết quả arXiv; không dùng chúng làm bằng chứng. Raw response giữ ở `tmp/proof-literature-search-20261017.json`.

## Kiểm tra lại những bước quyết định

### 1. Energy hữu hạn chưa đủ để suy ra hội tụ

Phản ví dụ cho suy luận tắt: x(s)=sin(log(1+s)) không hội tụ, dù ∫₀∞|x′(s)|²ds≤1. Vì thế phải giữ cả ba bước trong proof hiện tại:

1. Với z ngoài C_A, khoảng cách đến aff N(z) dương. Các atom không gần nhất có score gap dương đều trong một lân cận đủ nhỏ; fixed positive priors cho khối lượng ngoài N(z) tiến về 0 đều ở đó.
2. Bounded guidance và bounded actual speed buộc mỗi lần quay lại lân cận nhỏ phải tiêu hao một lượng energy dương cố định, hoặc ở lại mãi và tiêu hao energy vô hạn.
3. Mọi cluster point nằm trong C_A hữu hạn. Omega-limit của continuous bounded trajectory là compact, connected, nonempty, nên chỉ có một điểm.

Tính hữu hạn của C_A được chứng minh trực tiếp bằng hình học equidistance trong affine hull của từng subset atom; không viện đến một khẳng định tổng quát về stationary points của Gaussian mixtures. Với positive averaging dùng conv N(z); với signed guidance phải dùng aff N(z).

### 2. Covariance có dấu: cần đẳng thức riêng

Với s cố định, đạo hàm finite sum cho ∇H_p=m_p và D_xm_p=β Cov_p(a). Không cần strict positive definiteness hoặc atom full affine span.

Đặt u=m_c−z, v=m_u−z, μ=(1+w)u−wv. Đại số trực tiếp cho

\[
-(1+w)|u|^2+w|v|^2=-|\mu|^2+w(1+w)|u-v|^2.
\]

Gần một non-atom endpoint z, các nearest atoms đều có khoảng cách r>0 đến z, nên

\[
T=(1+w)\operatorname{tr}\operatorname{Cov}_c-w\operatorname{tr}\operatorname{Cov}_u
=r^2-|\mu|^2+w(1+w)|u-v|^2+o(1).
\]

Đây là bước sử dụng w≥0 và cấu trúc hai posterior trên cùng support. Đẳng thức không nói T≥0 mọi nơi và không áp dụng cho signed combination tùy ý. Khi w bounded nhưng oscillating, remainder vẫn o(1).

### 3. Jacobian–Fatou: không cần tail estimate đều theo source

Với β=e²ˢ−eˢ và g(s)=|f(x(s),s)|²∈L¹, tách integral tại S cố định cho

\[
\int_{s_0}^s\beta g=o(\beta(s)),\qquad
\int_{s_0}^s\beta\zeta=o(\beta(s))\quad(\zeta\to0),\qquad
\int_{s_0}^s\beta=\tfrac12\beta(s)+o(\beta(s)).
\]

Vì μ=f+x−z, chúng cho log J_s≥r²β(s)/2+o(β(s))−O(s)→∞ trong robustness theorem. Điều này đúng riêng tại từng source xấu. Liouville áp dụng cho cùng finite-time flow, khởi tạo bằng identity ở s₀, nên J_s>0. Basin Borel do endpoint map là pointwise limit của continuous maps. Mỗi bounded source ball có chung bounded image ball K, vì vậy ∫_E J_s≤Leb(K). Fatou theo thời gian nguyên đủ để suy ra Leb(E)=0; không cần chọn một thời điểm bắt đầu chung cho mọi source trong E. Locally Lipschitz inverse chuyển nullity về thời gian 0.

Một fresh verifier chỉ nhận clean lemma và proof inline, không có tool, lịch sử suy luận hoặc verdict trước đó: **HOLDS**, với lưu ý phải đồng nhất thời gian khởi tạo và dùng |det| nếu không khởi tạo identity. Source hiện tại đã nêu đúng cả hai điều kiện. Đây là kiểm tra bổ sung cho lemma, không thay thế hồ sơ bốn lượt phản biện trước của toàn supplement.

Volume expansion chỉ là điều kiện đủ: hệ x′=x, y′=−2y có stable basin của gốc là đường x=0 (null), nhưng determinant=e⁻ˢ. Vì thế không được gọi divergence dương là điều kiện cần để tránh saddle.

### 4. Schedule và perturbation: kiểm tra chain rule trước khi viện dẫn

Với D(q∥p)=Σ_j q_j log(q_j/p_j), trực tiếp từ finite partition sum:

\[
\partial_sH_p=-\alpha'D(q_p\Vert p)-\frac{e^{-s}}2\mathbb E_{q_p}|a|^2.
\]

Partition ratio là weighted average của p_c,j/p_u,j, nên |H_c−H_u|≤α max_j|log(p_c,j/p_u,j)|. Bởi vậy đạo hàm schedule trong U đóng góp w′(H_u−H_c), được chặn bởi Lα|w′|. Giả thiết weighted integrability trong supplement kiểm soát đúng hạng này, kể cả khi schedule không hội tụ. Young inequality kiểm soát f·R bằng (|f|²+ρ²)/2. Điều kiện div R≥−ηβ, η→0, được dùng riêng ở bước volume; amplitude nhỏ không tự thay thế điều kiện derivative này.

Không suy diễn uniform field controls từ teacher loss hoặc từ việc đo trên hữu hạn samples.

### 5. Composition: linear instability không tự cho phase diagram

Ở đây lời giải cần toàn bộ factorization của F, không chỉ dấu F′(0). Với q=tanh b, z=tanh u:

\[
F(u)=\frac{z[1-(1+w)q^2+wq^2z^2]}{1-q^2z^2},\qquad
w_c=\sinh(b)^{-2}.
\]

Ở w=w_c, F(u)>0 khi u>0 dù F′(0)=0: trường hợp tới hạn đã được xét. Khi w>w_c, inward boundaries trong biến u tạo interval bất biến; β→∞ cho x=u/β→0. Finite-time inverse flow kéo interior về một open source interval, có Gaussian mass dương. Order preservation và tập escape mở xác định basin đóng [−R*,R*]. Tensor product chỉ dùng posterior và source factorization đã nêu; không mở rộng sang arbitrary high-dimensional perturbations.

Không tìm thấy trong các nguồn đã đọc một theorem cung cấp trực tiếp sharp threshold này. Điều đó chưa chứng minh priority. PDF toàn văn Blohm–Garg trên OpenReview vẫn bị chặn truy cập; so sánh theorem-level với nguồn đó còn mở. Không thay thế bằng abstract hoặc author blog.

## Cách đưa vào paper

Giữ các proof tự đầy đủ. Có thể bổ sung citation tại: log-partition/covariance; energy và finite-critical-set convergence; inward trapping. Phải giữ riêng lập luận signed covariance và Jacobian–Fatou. Không viết “follows from stable-manifold theorem” hoặc “follows from mean-shift convergence”.

Hai extension vẫn là supplement nghiên cứu. Trước khi đưa thành contribution chính: hoàn tất so sánh Blohm–Garg và kiểm tra thực nghiệm phase threshold, basin mass, sai số theo cutoff/solver và robustness envelope. Lượt này không chạy thí nghiệm mới và không thay đổi kết luận novelty đang chờ đối chiếu.
