# Các mở rộng toán học để tăng contribution — 17/10/2026

Đã viết hai định lý, hai hệ quả và một bổ đề trong [bản chứng minh LaTeX](contribution_extension_proofs_2026-10-17.tex), cùng [PDF](contribution_extension_proofs_2026-10-17.pdf). Bốn lượt phản biện mới, không xem ý kiến của nhau, không dùng computation/web, đều trả HOLDS cho các lập luận A–D bên dưới. Đây là kiểm định lập luận độc lập, không phải formal verification hoặc chứng nhận novelty.

Bản paper chính đã push vẫn được giữ nguyên trong lượt nghiên cứu này. Các kết quả mới nằm trong supplement để có thể đối chiếu prior work và kiểm tra thực nghiệm trước khi thay đổi contribution chính.

## 1. Kết quả đáng ưu tiên nhất: averaging rồi CFG có thể tạo atom ngoài training set

Với atoms và labels ±1, Gaussian source, label noise có độ lệch chuẩn h>0, đặt b=h⁻² và

\[
F(u)=\frac{1+w}{2}\{\tanh(u+b)+\tanh(u-b)\}-w\tanh u.
\]

Đây là field thu được bằng cách average hai exact conditional fields tại queries ±1 rồi áp dụng CFG với unconditional exact field. Trong logarithmic time s=−log(1−t), phương trình là x′=F(βx)−x, β=t/(1−t)².

**Theorem 2 chứng minh ngưỡng chính xác**

\[
w_c(h)=\sinh(h^{-2})^{-2}.
\]

- Nếu 0≤w≤w_c, mọi source dương tới +1, source âm tới −1; source 0 giữ nguyên. Gaussian endpoint law là ½δ₋₁+½δ₁.
- Nếu w>w_c, tồn tại R*>0 hữu hạn sao cho toàn bộ interval [−R*,R*] tới 0, ngoài interval tới ±1. Endpoint law có atom ngoài training set với mass 2Φ(R*)−1>0.

Đây không chỉ là một trajectory đối xứng có measure zero. Chứng minh xây được một shrinking tube invariant và lấy preimage của nó dưới finite-time flow để thu một interval mở ở time zero. Factorization chính xác của F cho global convergence và dạng toàn bộ basin.

**Lemma 1** cho thấy basin này tồn tại cả khi phá odd symmetry: chỉ cần một interval [l,r] với G(l)>0 và G(r)<0, boundedness và local Lipschitz của G. Không suy ra mọi perturbation nhiều chiều đều giữ tính chất đó.

**Corollary 2** đưa construction lên A={±1}^d, label y(a)=a₁. Tập training có full affine span và N=2^d>d khi d≥2. Endpoint law đặt mass dương trên {0}×{±1}^{d−1}, hoàn toàn ngoài training set. Vì vậy đây không phải hệ quả của việc training atoms nằm trên một affine hull thiếu chiều.

Điểm cần diễn đạt đúng: kết quả tạo **atoms mới**, không chứng minh posterior liên tục, generalization hay chất lượng mẫu tốt hơn. Nó cho thấy tính chất “endpoint nằm trong training set” không đóng dưới phép ghép hai can thiệp đã nêu.

## 2. Mở rộng dương tính: scheduled CFG và sai số trường có kiểm soát

**Theorem 1** mở rộng fixed CFG trên cùng finite support sang schedule 0≤w(s)≤W với

\[
\int_{s_0}^{\infty}\alpha(s)|w'(s)|\,ds<\infty,
\qquad \alpha=(1-t)^2/t.
\]

Không cần w hội tụ. Ví dụ w(s)=1+½sin(e^s) vẫn thỏa điều kiện. Với perturbed log-time field x′=f+R, theorem còn cho phép:

\[
\sup_x|R(x,s)|\le\rho(s),\quad \rho\to0,\quad \int\rho^2<\infty,
\qquad \inf_x\operatorname{div}R(x,s)\ge-\eta(s)\beta(s),\quad\eta\to0,
\]

kèm các điều kiện regularity và local boundedness trong phát biểu đầy đủ. Mọi trajectory hội tụ về một tập ứng viên hình học hữu hạn; non-training endpoint basins có measure zero. Với source absolutely continuous, endpoint vẫn nằm trên training atoms almost surely.

Điểm mới so với phát biểu hiện tại là xử lý đồng thời schedule và scaled perturbations, chứ không chỉ thay một hằng số trong proof. Bước quan trọng là bound |H_c−H_u|≤Lα, biến schedule derivative thành error tích phân được; sau đó dùng weighted-tail estimate để điều khiển signed divergence.

**Corollary 1** cho điều kiện cụ thể |R|+||DₓR||≤Ce⁻ᵞˢ, γ>0. Trong thời gian gốc, R=(1−t)Δ, nên chấp nhận Δ=O((1−t)⁻¹⁺ᵞ) cùng bound cho spatial derivative. Khi trajectory đã tới một atom, các tốc độ là:

| Miền γ | Tốc độ trong s | Trong thời gian gốc |
|---|---|---|
| γ>1 | O(e⁻ˢ) | O(1−t) |
| γ=1 | O(se⁻ˢ) | O((1−t)log(1/(1−t))) |
| 0<γ<1 | O(e⁻ᵞˢ) | O((1−t)ᵞ) |

Các điều kiện uniform này **không suy ra từ training loss nhỏ**. Chúng cũng không tự động đúng cho một fixed neural network có field regular tới t=1. Đây là sufficient theorem cho lớp approximations được nêu, chưa phải chứng nhận cho checkpoint thực tế.

## 3. Phương pháp và định lý được dùng

Không cần thêm tiên đề. Cần các giả thiết toán học kiểm tra được và giới hạn rõ phạm vi của chúng.

| Công cụ | Vai trò thực sự |
|---|---|
| Log-partition differentiation, Gibbs/KL bounds | Xây potential và bound thời gian thay đổi của field |
| Lyapunov/quasi-dissipation estimate | Chứng minh finite energy dù có schedule và perturbation |
| Nearest-atom concentration với positive priors | Loại cluster points không phù hợp hình học |
| Connected omega-limit set và tập ứng viên hữu hạn | Từ boundedness và finite energy tới convergence; finite energy riêng lẻ không đủ |
| Signed covariance identity | Giữ đúng dấu trong CFG; không giả sử signed covariance luôn dương |
| Weighted-tail lemma với β tăng | Biến L² energy thành o(β) trong divergence integral |
| Liouville + change of variables + Fatou | Chứng minh non-atom basins null; không chỉ tìm equilibria |
| Scalar order preservation và invariant tube | Chứng minh positive-volume off-training basin và ngưỡng sharp |
| Tensor factorization | Mở counterexample sang training set full affine span |
| Variation of constants | Suy endpoint rates sau khi đã tới vùng có unique nearest atom |

Không áp dụng LaSalle hoặc stable-manifold theorem trực tiếp mà bỏ qua non-autonomous time dependence và spatial derivatives tăng vô hạn gần endpoint.

## 4. Đối chiếu novelty và giới hạn hiện tại

Các nguồn dưới đây đã được đọc theo phạm vi ghi rõ. Đây là targeted search, chưa phải exhaustive priority search.

| Nguồn primary | Điều đã có và phần cần phân biệt |
|---|---|
| [Liu–Zuazua, Geometric Asymptotics, Theorem 3.18/Remark 3.19](https://arxiv.org/html/2605.12231) | Có original-flow convergence criterion dưới giả thiết loại nonminimising critical omega-limit points. Theorem 1 của supplement chứng minh null basins trong common-support setting với schedule/error conditions; không giải quyết mọi different-support mixture. |
| [Jiang–Ma, Analytic Distribution of CFG, Theorems 4.2–4.3](https://arxiv.org/html/2607.19725) | Đã có path-integral characterization và time-dependent guidance trên interval có cutoff dương, kèm flow/integrability assumptions. Không được gọi “lần đầu phân tích scheduled CFG”. Cần phân biệt singular endpoint/null-basin result với finite-cutoff density identity. |
| [Du et al., Reduce, Reuse, Recycle](https://arxiv.org/html/2302.11552) | Sai lệch của naïve diffusion composition đã có. Không đặt novelty ở nhận xét chung composition có thể sai. |
| [Lee et al., Refining Compositional Diffusion](https://arxiv.org/html/2605.03075) | Mode averaging và mẫu giữa các modes đã được thảo luận trong planning. Candidate delta ở đây là exact finite-support fields, sharp w_c, positive-measure endpoint basin và full-affine-rank construction. |
| [Blohm–Garg, Composition of Pretrained Diffusion Models: A Logic-Based Calculus](https://openreview.net/forum?id=ADLiUSC7Qm) | Có nghiên cứu bất nhất của composition operators. Đã kiểm tra abstract được index và [official code](https://github.com/Aalto-QuML/logic-diffusion-composition); truy cập full PDF gặp OpenReview challenge. Chưa đủ dữ liệu để kết luận theorem-level non-overlap với nguồn này. |
| [Soiffer et al., Catastrophic Compositional Generation](https://arxiv.org/html/2606.23920) | Có phân tích composition/generalization failure, gồm Gaussian constructions. Không xem đây là một vấn đề hoàn toàn chưa ai nghiên cứu. |

Đánh giá hiện tại: mathematical arguments **supported by independent reasoning review**; novelty **REVISE**, chưa PASS, vì cần so sánh theorem-level đầy đủ với composition literature, đặc biệt Blohm–Garg. Đây không phải lý do để bỏ kết quả; là ranh giới giữa proof correctness và research contribution.

Ứng viên đóng góp chính tốt hơn là: **điều kiện đủ giữ empirical support dưới scheduled/perturbed CFG, cùng một sharp counterexample cho thấy điều đó thất bại khi compose với label averaging**. Các tốc độ là supporting corollary, không nên chia thành nhiều “major contributions”.

## 5. Những phần chưa thể kết luận hoặc không nên cố chứng minh theo cách tổng quát

- “Loss nhỏ ⇒ đúng endpoint law”: sai nếu thiếu kiểm soát khác; không sửa bằng giả thiết ngầm.
- “Moment fit ⇒ equality of laws/calibration”: không suy ra; các independent tests hiện có cũng không chứng nhận điều này.
- “Mọi signed mixture giữ training support”: construction mới bác bỏ cách mở rộng đó.
- Characterization cần và đủ cho mọi signed multi-field mixture: chưa có lời giải trong lượt này.
- Endpoint weights cho general geometry, R*(h,w) dạng closed form, hoặc tính sharp của robustness assumptions: chưa được chứng minh. Theorem 2 xác định đúng ngưỡng tồn tại positive off-training mass, không cung cấp closed form cho R*.
- NTK/spectral-bias dynamics ⇒ hành vi của network feature-learning đang chạy: chưa có bridge được kiểm định; thêm các định lý kernel chuẩn không tự đóng được gap.

## 6. Thí nghiệm quyết định tiếp theo

Chưa chạy thí nghiệm mới trong lượt này. Có thể bắt đầu bằng một CPU feasibility pilot, không cần huấn luyện model mới; ngưỡng thực thi đề xuất tối đa 30 phút trước khi mở rộng.

1. **Threshold và basin:** scalar h grid, w/w_c bên dưới, đúng và bên trên 1; ghép cùng Gaussian sources. Báo mass tới midpoint và ±1, cùng số trajectories chưa phân loại ở cutoff. Không gọi gần midpoint tại finite cutoff là endpoint0 chỉ dựa vào nearest distance.
2. **Đối chứng đúng phép toán:** một conditional field, positive average, single-field CFG, averaged-field CFG, và prior-averaged field. Phân biệt field averaging với average priors và average endpoint laws.
3. **Stiffness:** dùng implicit solver có analytic Jacobian, cross-check resolution/tolerances; giữ failures. Có thể dừng theo trap/escape conditions của proof, nhưng kết luận certificate cho numerical path đòi verified error enclosure, không chỉ float output.
4. **Phá symmetry:** thay prior logits/query weights nhỏ để giữ hai boundary signs của Lemma 1, kiểm tra basin có probability dương. Không đòi endpoint law đối xứng sau perturbation.
5. **Full-rank controls:** tensor data d=2 và d=8, so product endpoint frequencies với scalar law; không gọi các coordinates là independent problem seeds.
6. **Positive theorem:** schedules đơn giản và perturbations có amplitude/divergence envelope chứng minh giải tích được, để kiểm tra support/rate predictions. Giữ riêng một negative control vi phạm assumptions.

Chỉ sau khi đóng các contrasts này mới cần đánh giá learned-field composition trên checkpoint thực tế và xác định tác động thực tiễn. Không claim các ảnh đẹp/khác training chứng minh posterior recovery.

## 7. Kiểm định và provenance

Ba solver độc lập xem ba bài toán: composition, schedules, perturbations. Sau đó editor hợp nhất schedule và perturbation thành Theorem 1, làm sạch các proof arguments và đưa A–D cho bốn verifier fresh-context. Các verifier không dùng tools/computation/web, không biết votes của nhau.

| Verifier | A: robustness | B: rates/schedules | C: sharp composition | D: tube/tensor |
|---|---|---|---|---|
| extensions_verify_1 | HOLDS | HOLDS | HOLDS | HOLDS |
| extensions_verify_2 | HOLDS | HOLDS | HOLDS | HOLDS |
| extensions_verify_3 | HOLDS | HOLDS | HOLDS | HOLDS |
| extensions_verify_4 | HOLDS | HOLDS | HOLDS | HOLDS |

Verifier 2–4 yêu cầu giữ explicit w≥0 trong scalar construction; đã ghi rõ constant w≥0. Presentation review bổ sung time origin s₀ cho Jacobian/source sets, observation model cho tanh shifts, điều kiện source phải charge open basin để có positive mass, và cách nói full affine span. Các sửa này không thay mathematical conclusions.

Xem [presentation review](contribution_extension_presentation_2026-10-17.md). Không có numerical verification được dùng như proof. PDF có 6 trang; compiler trong app và MiKTeX đều biên dịch được, không có undefined references hay overfull boxes. Source/PDF hashes và kiểm tra cuối được lưu trong `contribution_extension_verification_2026-10-17.json`.

Việc có định lý đúng không bảo đảm đạt ICLR/ICML/NeurIPS. Để đánh giá khả năng nộp cần novelty comparison hoàn chỉnh, bằng chứng thực nghiệm cho cơ chế chính và một bản paper tập trung vào hai kết quả này.
