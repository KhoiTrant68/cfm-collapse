# Mathematical strengthening and contribution assessment — 16 October 2026

**Kết luận:** đã tích hợp các chứng minh được kiểm tra vào bản thảo chính và sửa những phát biểu toán học quá mạnh. Trục lý thuyết rõ hơn là **tính nguyên tử của endpoint dưới các can thiệp conditioning, cùng giới hạn của chứng nhận từ training loss**. Chưa đủ căn cứ để chứng nhận bài đã sẵn sàng hoặc sẽ được nhận ở ICLR/ICML. Độ đúng, tính mới, ý nghĩa đối với ML và chất lượng bằng chứng là các câu hỏi riêng.

## Revision và phạm vi

- Canonical source: [main.tex](../../paper/main.tex); compiled [main.pdf](../../paper/main.pdf), **89 trang**, main text kết thúc ở trang10, giữ template TMLR hiện có.
- Source SHA256: `02e27310ce7a409ca74c9c4125ab0cf5420c7d460c98595c7ec64d5820c659ac`.
- Baseline trước lượt tích hợp: `47c0d29b085263619f61ee967c4bfd7e1c623078c5f0d212631f48b9fb95a0fa`. Bản backup ở `tmp/theory-integration-2026-10-16/main.before.tex` và PDF cùng thư mục. Các Methods edits trước đó được giữ lại.
- Chỉ root chỉnh canonical TeX. Các solver/verifier toán nhận clean statements/proofs và suy luận không dùng web hoặc tính toán. Việc kiểm tra literature chạy riêng, không dùng để tìm lời giải cho các chứng minh.
- Đây là tích hợp các kết quả cụ thể, không phải chứng nhận rằng mọi phát biểu cũ hoặc toàn bộ89trang đã qua bốn lượt kiểm tra mới. Các kết quả cũ còn lại thừa kế phạm vi rà soát trong [inventory trước](../audit/research_agent_2026-10-16/06_Math_Formalization.md).

## Các gói toán học đã đưa vào paper

| Gói / vị trí | Thay đổi contract và proof | Kiểm tra |
|---|---|---|
| `prop:filtered`, proof Appendix E.2 | Bỏ tiền đề giả sử hội tụ và tránh ties. Mọi trajectory hội tụ; source absolutely continuous cho endpoint atom hầu chắc chắn. Normalized log-partition tạo finite kinetic energy; finite circumcenter set cho convergence; divergence/Jacobian/Fatou cho null non-atom basins. | Các kết quả V/A của lượt trước:4 fresh HOLDS mỗi kết quả. |
| `prop:cfgatom`, proof Appendix A.23 | Với distinct atoms, fixed finite w≥0 và positive conditional weights: mọi positive-bandwidth CFG trajectory hội tụ, endpoint atom a.s. Hard conditioning mạnh hơn: mọi initial point hội tụ đúng atom được condition, với bound tường minh. | Các kết quả B/H:4 fresh HOLDS mỗi kết quả. |
| `cor:floor` và proof A.20 | Nâng lower bound thành equality inf L₀=d/(3L) trong toàn bộ measurable spatially L-Lipschitz class, với uniform time/Gaussian source/identifying labels. Có analytic attainer. Bỏ suy luận lower bound nhỏ loại được architecture error. | Kết quả L:4 fresh HOLDS. |
| `lem:nonpositive-filter` | Chứng minh 1−exp(−a abs(ω)^(−ζ)) không là characteristic function của probability measure, a,ζ>0. Fatou không cần giả thiết second moment. | Kết quả G:4 fresh HOLDS. |
| `prop:nwrate` | Phân biệt population ratio μ_h^∞ và empirical ratio. Dưới assumptions cũ chỉ khẳng định stochastic O_P error. Expected bias/MSE bounds có thêm global bounded-response assumption; chứng minh bằng denominator good/bad event. Bandwidth rate cân bằng upper bound, không gọi là actual optimum vô điều kiện. | Gói N mới: `verify_risk_1`–`verify_risk_4`,4 HOLDS. |
| `thm:risktransfer`, Appendix D.6 | Bound W₂ và mean/sqrt-trace tại T<1 từ teacher risk khi có envelope m(t)≤K(t)r(t) giữa generated-path và teacher-path errors. Density domination chỉ là một sufficient condition, không được suy ra từ loss. | Gói T mới: cùng4 fresh verifiers,4 HOLDS. |
| `prop:loss-no-certificate`, Appendix D.6 | Explicit affine-field counterexample: teacher loss→0 nhưng endpoint N(a,I_d), total variance d. Mỗi field có finite spatial Lipschitz constant; không có cap chung khi loss→0; time dependence piecewise continuous. | Gói C mới: cùng4 fresh verifiers,4 HOLDS. |

Sáu kết quả H/L/G/V/A/B đã được xác nhận ở lượt trước; N/T/C là ba kết quả được kiểm tra thêm. Việc gộp H/B vào một proposition và V/A vào một proposition giúp paper có một lập luận liên tục thay vì quảng bá nhiều lemma rời. Đây là kiểm tra phản biện bằng các ngữ cảnh mô hình riêng, không phải Lean/formal verification hay đánh giá độc lập của chuyên gia con người.

Hai equation labels nội bộ của proof CFG cũ (`eq:cfgfixed`, `eq:pf:cfgatom:1`) được bỏ cùng proof thay thế; không còn consumer của chúng. Các labels của public statements được giữ. Consumers, abstract và conclusion được cập nhật sau khi đổi contract.

## Kết quả mới nối theory với cách đọc training loss

Với ε_t=1−t, teacher Y_t=ta+ε_tX₀ và learned flow Z_t, đặt r(t)=E|Δ(Y_t,t)|² và m(t)=E|Δ(Z_t,t)|². Khi m≤Kr,

\[
W_2(\operatorname{Law}(Z_T),\operatorname{Law}(Y_T))
\le (1-T)\int_0^T\frac{\sqrt{K(t)r(t)}}{1-t}\,dt.
\]

Mean và square root of covariance trace cũng lệch không quá bound này. Không cần coi trained network là một NW mixture. Tuy nhiên K có thể lớn hoặc vô hạn; paper không tuyên bố đo được K cho các network hiện có.

Counterexample chọn δ∈(0,1/2), A_δ=log(1/δ), với slope −1/(1−t) trước 1−δ, slope 2A_δ/δ trên một boundary layer dài δ/2, rồi slope0. Trajectory co lại rồi được khuếch đại trở về scale ban đầu. Chính xác:

\[
L_0(v_\delta)=d\delta\left(1+\tfrac32\log(1/\delta)
+\tfrac76\log^2(1/\delta)\right)\to0,
\qquad Z_1\sim\mathcal N(a,I_d).
\]

Vì vậy không tồn tại universal vanishing endpoint certificate chỉ phụ thuộc teacher loss trong lớp đã nêu. Kết quả không chứng minh một architecture cố định thực hiện construction này, và không bác guarantees có common regularity cap.

## Các diễn giải đã sửa

1. Moment fit và interval overlap không xác định distribution hay proximity của vector fields. Abstract, contribution list, KGF discussion, audit protocol và conclusion nay phân biệt hai việc này.
2. Sai số trace covariance √(2/(M−1)) được ghi là Gaussian relative-standard-error approximation, không còn là bound phân phối bất kỳ.
3. Exact finite-M rank null được giới hạn bởi exchangeability và absence of ties. Paper nói rõ archived deterministic midranks chưa được recompute bằng randomized ties. Không âm thầm đổi metric hoặc số liệu cũ.
4. Fixed-h coverage theorem không tự áp dụng sau khi chọn h bằng responses. Đã thêm finite-grid union-bound repair với log(G/δ).
5. Bỏ upper-bound inference về gain của endpoint smoothing; đưa counterexample W₂² gain=2/π dù atom obstruction=0. Moment matching bằng h vàρ cần đúng các vector/matrix equations.
6. Cùng solver ở h0 và positive h không loại được discretization error. Bỏ attribution off-atom outputs hoàn toàn cho finite capacity.
7. Relative nearest-neighbour criterion không là exact atom membership. Mở rộng candidate set và dùng 8-bit grids cũng không tự tạo lower bound cho metric trên raw samples.
8. Heteroscedastic finite-support example được sửa thành asymptotic population statement với exponentially small boundary correction.

## Đánh giá contribution cho ICLR/ICML

**Novelty positioning: REVISE; priority của các định lý mới: NOT_ASSESSED.** Nguồn và các vị trí theorem cụ thể ở [venue evidence](venue_contribution_evidence_2026-10-16.md). Bản thảo đã thêm [Baptista et al., Theorem6.4](https://arxiv.org/html/2501.15785v2#S6.SS3), sửa cách trình bày cell-subset result của [Dasgupta et al., §3.3](https://arxiv.org/html/2603.14135v3#S3.SS3), và giữ rõ external-label bandwidth khác spatial bandwidth.

Hạt nhân có khả năng bảo vệ tốt hơn là: **which conditioning interventions preserve atomic endpoints, and why teacher loss alone cannot certify those endpoints**. Exact NW reference và bandwidth diagnostics hỗ trợ hạt nhân này; conditional empirical collapse riêng nó không đủ gánh novelty. Chưa thực hiện một priority search đầy đủ cho H/V/A/B hoặc counterexample loss mới, nên không dùng chữ “first”.

[ICLR2027 reviewer guidelines](https://iclr.cc/Conferences/2027/ReviewerGuidelines) và [ICML2026 reviewer instructions](https://icml.cc/Conferences/2026/ReviewerInstructions) tách soundness khỏi contribution/impact. Có proof đúng không suy ra acceptance. Bản hiện tại vẫn có ba khoảng trống thực nghiệm có thể quyết định đánh giá:

| Ưu tiên | Câu hỏi cần trả lời | Contrast và acceptance cần đóng băng trước khi chạy |
|---|---|---|
| 1 | Off-atom spread đến từ solver/truncation hay learned field? | Same checkpoint và same x₀; oracle/learned fields; nhiều ε và step sizes. Chỉ diễn giải learned effect khi solver change nhỏ hơn uncertainty và nhỏ hơn contrast chính. |
| 2 | Các intervention của theorem cho hành vi gì trong learned models? | Phân biệt label noise, averaging fields và CFG; matched budgets, repeated seeds; endpoint distances và atom frequencies. Oracle là control, không dùng exact-field theorem làm chứng nhận trained network. |
| 3 | Một bandwidth có dự đoán full law ở conditions chưa fit không? | Fit riêng, đo held-out distribution discrepancy; Gaussian/Laplace/Cauchy/kNN và free baselines; aggregate theo độc lập seeds, không coi checkpoints là replicates độc lập. |

Một numerical illustration rẻ của counterexample mới là tích phân field đã cho trên các δ, báo loss và endpoint variance cùng solver convergence; thí nghiệm minh họa implementation, không thay proof. Trước calibration runs mới cần tie-aware null controls. Detailed future pilot/access constraints vẫn ở [protocol trước](../audit/research_agent_2026-10-16/23_Feasibility_Pilot_Protocol.md); lượt này không chạy training hoặc model sampling.

## Verification và giới hạn bản giao

- `scripts/verify_paper_numbers.py`: **359 passed,0 failed**. Đây là kiểm tra saved-result numbers của script hiện có, không chứng nhận mọi câu trong bản thảo.
- Static source check: **221 unique labels**,37 cited keys,51 graphic occurrences; không thiếu target hoặc asset;37 formal results và3 assumptions.
- PDF89trang: không undefined references/citations, không overfull box, không oversized float trong final log. Còn các underfull/Math-in-bookmark warnings không phải lỗi chứng minh.
- Đã kiểm tra trực quan các trang thay đổi và các trang lân cận của lời phát biểu, proof, abstract/conclusion, bảng related work và các float được sửa. Đây không phải fresh full-page audit của cả89trang.
- Giữ bản thảo TMLR và main text10trang; chưa chuyển template/rút theo conference, chưa submit/push, chưa chạy full experiments.
- Machine-readable hashes/checks ở `tmp/theory-integration-2026-10-16/verification.json`.

**Đánh giá cuối:** có bản thảo toán học mạnh hơn, với proof hoàn chỉnh cho các kết quả cụ thể ở trên. Việc gọi contribution “đủ ICLR/ICML” vẫn cần đóng novelty comparison, đánh giá significance và ba empirical contrasts; hiện chưa có bằng chứng để khẳng định điều đó.
