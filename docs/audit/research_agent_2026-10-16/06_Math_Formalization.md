# Mathematical audit and proof ledger — 16 October 2026

## Phạm vi và tiêu chuẩn

Đọc các formal statements/proofs trong `paper/main.tex`, consequences liên quan, và hai theory notes `docs/theory/lemma_L1.tex`, `docs/theory/theorem_B.tex`. Source hash và revision ở [Reality Gate](20_Reality_Gate.md). Có **34 formal results**: 3 theorem,20 proposition,4 lemma,7 corollary, cùng3 assumptions. Inventory dưới đây đi theo source, không chỉ những mệnh đề thuận lợi cho bài. `lem:norepr` là label của remark, không phải lemma environment.

**Tách ba cách hiểu:** (i) exact population empirical field, (ii) surrogate KGF/label average, (iii) trained neural sampler. Một proof ở (i) hoặc (ii) không tự chuyển sang (iii). Số checkpoint agreement và numerical ODE convergence không phải proof bước còn thiếu.

Workflow áp dụng `math-olympiad`: solver/attackers reasoning-only; fresh verifiers chỉ nhận clean statement/proof, không thấy phiếu của nhau; confirm ở 4 HOLDS. Các bài toán convergence và almost-sure atomicity được đưa qua deep-mode sau vòng đầu chưa đóng được: tìm được entropy Lyapunov và Jacobian-volume argument bằng suy luận, không web hay numerical search. **Sáu kết quả mới ở dưới đạt 4 fresh confirmations mỗi kết quả.** Các 34 kết quả cũ được chia thành 3 packet review toán độc lập và root reread; không tuyên bố mỗi kết quả cũ đã qua 4 fresh verifiers. Kết quả “chưa thấy lỗi” dưới đây có độ kiểm tra thấp hơn confirmed mới.

## Sáu kết quả đã hoàn tất chứng minh

Xem source [proof_addendum.tex](proof_addendum.tex) và [PDF chứng minh](proof_addendum.pdf).

| ID | Phát biểu chính xác / giá trị bổ sung | Fresh verification ledger |
|---|---|---|
| H | Hard-conditioned exact CFG, w≥0, **mọi finite x0** hội tụ đúng conditioned atom; bound ∥x_t−ta_i∥²≤ε²[C+2wlogN log(t(1−t0)/(t0ε))]. Không cần giả thiết limit tồn tại hay unique nearest atom. | `math_dynamics`, `verify_hard_guidance_2`, `verify_new_results_3`, `verify_new_results_4`:4HOLDS. |
| L | Với distinct identifying labels, independent uniform time và Gaussian source, inf trên **mọi measurable spatially L-Lipschitz field** bằng d/(3L), L≥1. Analytic attainer dùng slope min{L,1/ε}. | `verify_new_results_4`, `verify_new_results_5`, `verify_filter_6`, `verify_final_repairs`:4HOLDS với explicit uniform time. Các lượt trước thiếu time assumption không tính vào4phiếu này. |
| G | 1−exp(−a abs(ω)^(−ζ)), a,ζ>0, không là characteristic function của probability measure. Fatou ép second moment0, do đó δ0, contradiction. | `verify_new_results_3`, `verify_new_results_4`, `verify_new_results_5`, `verify_filter_6`:4HOLDS. |
| V | Với finite atoms và arbitrary probability label average, mọi positive finite measurable label coefficients cho trajectory hội tụ vào z∈conv N(z). Normalized log-partition + entropy sign cho finite kinetic energy; critical circumcenter set hữu hạn. Không cần log-ratio integrability. | Deep solver `deep_convergence`; fresh `verify_convergence_1`–`verify_convergence_4`:4HOLDS. |
| A | Trong V, mọi source absolutely continuous cho endpoint atom **hầu chắc chắn**. Covariance dương tách khỏi simplex vertices làm divergence tăng; Jacobian→∞ trên non-atom basins, bounded-volume/Fatou ép basin null. | Deep solver `deep_remaining_atomicity`; fresh `verify_atomicity_1`–`verify_atomicity_4`:4HOLDS. |
| B | Với distinct atoms, fixed positive conditional weights, unconditional uniform weights và finite w≥0: **mọi CFG trajectory hội tụ**, và endpoint là atom hầu chắc chắn dưới absolutely continuous source. Signed log-partition cho finite energy; signed covariance được kiểm soát trên unit intervals. | Cùng clean-packet verification `verify_atomicity_1`–`verify_atomicity_4`:4HOLDS cho B riêng. |

H mạnh hơn `prop:cfgatom(b)` và L làm sắc `cor:floor`. V bỏ convergence premise của `prop:filtered(b)`; A đóng tiếp a.s. atomicity. B đóng cả convergence và a.s. atomicity cho positive-bandwidth exact CFG. Ví dụ ±a, equal weights, x0=0 vẫn cho limit0 ngoài atoms: đây là exceptional initial point, không mâu thuẫn null-basin theorem. G bác inference từ spectral low-pass sang positive NW kernel, không bác descriptive Gaussian fit ở hữu hạn conditions. Chưa có priority/novelty claim cho sáu theorem mới trước một search riêng.

## Inventory toàn bộ formal results

“Giữ” nghĩa chưa thấy lỗi trong packet review với hypotheses ghi ở hàng đó; không phải certificate4phiếu.

| Source line / label | Audit và hướng chứng minh/sửa | Cần thí nghiệm gì? |
|---|---|---|
| 257 `prop:projection` | Giữ: orthogonal L² projection; square-integrable target cần đủ, a.e. uniqueness không là pointwise everywhere uniqueness. | Không cần để chứng minh. |
| 278 `prop:collapse` | Giữ: explicit x_t=ta_i+εx0 ở observed unique label. Trường extension ngoài labels không tự được định nghĩa ởh0. | Oracle integration làm sanity check. |
| 294 `cor:distinction` | Giữ: conditional index degeneracy khác unconditional mixture; dependency đúng vào unique labels. | Không cần. |
| 325 `prop:kernel-field` | Giữ: Bayes weights + conditional mean. Gaussian kernel positive, finite dataset. | Oracle numerical identity chỉ QA. |
| 340 `thm:endpoint` | Giữ: change of variables/continuity equation, mixture coupling; h>0 fixedN. Với P2source có thể nâng convergence tớiW2. | Matched finite-time reference ởP1/P2. |
| 352 `cor:zerobw` | Giữ: fixedN, unique nearest label **index**, khác case repeated labels; off-label hard objective extension không canonical. | Near-tie label control nếu minh họa. |
| 359 `cor:infbw` | Giữ: finite sums weights→1/N. | Không cần. |
| 367 `prop:moments` | Giữ: weighted finite-atom mean/covariance exact. Hai moment không xác định law. | Distributional falsifier, không chỉ traceR². |
| 382 `prop:atomicity` | Giữ: every coupling pays≥∫dist(x,A)²dP. Wasserstein cần P2 hoặc nói extended cost; không suy ra upper bound on improvement. | Đo actual floor nếu dùng quantitative relevance. |
| 557 `prop:heffid` | Derivative identities và conditional inverse stability giữ; log trace cần positive trace, mean fit dùng ℓ2,1norm. Fitted residual≠known e;25gridpoints≠certified κinf. | Sensitivity/profile + held-out fits; không gọi bootstrap width certificate từ lemma. |
| 596 `thm:calib` | (a–c) giữ với independent noises và measurable exact-mass regions; (d) giữ đúng fixed-weight iid atom statement. Actual label-dependent heterogeneous atoms cần conditional identities trong addendum. | Separate exact Gaussian proxy from real weighted reference. |
| 682 `prop:filtered` | (a) giữ; (b) đúng có điều kiện như viết. V chứng minh convergence; A đóng tie avoidance a.s. với absolutely continuous source. “Mọi initial point đều tới atom” vẫn sai. | Symmetry/perturbed-basin control là minh họa, null basin nay có proof. |
| 774 `lem:cov` | Giữ: spatial affine change of variables, determinantε^d, không dùngt1. | Không cần. |
| 801 `lem:wellposed` | Giữ trên mọi compact intervalt<1: smooth finite positive mixture + linear growth. Không suy ra terminal uniqueness. | Solver convergence là QA. |
| 869 `lem:mixture-coupling` | Giữ: continuity equation + finite-time uniqueness xác định marginals; explicit interpolant coupling không phải individual ODE paths. | Không cần. |
| 960 `cor:repeated` | Giữ: conditional index law trên repeated-label group. | Repeat-label control. |
| 994 `prop:uncond` | Giữ: full empirical mixture endpoint, không collapse tất cả vào một atom. | Không cần. |
| 1329 `cor:prop18` | Giữ: interpolant path noise endpoint0; unweighted derivative-target risk∞, time-weighted risk dùng đúng objective. Residual per coordinate σ²/[4t((1−t)+σ²t)]; manuscript equivalent formula đúng. | Không gán formula sai từ audit draft cho paper. |
| 1407 `prop:expansion` | Population covariance expansion và stochastic O_P giữ với local homoscedasticity và fourth moment. Heteroscedastic h² correction cùng order; finite uniform-support example chỉ asymptotic, không exactΣ+h² mọih do boundary. | P3varyN,h; negative heteroscedastic control. |
| 1491 `prop:nwrate` | **Sửa:** current assumptions không đủ expected bias/variance/MSE. `eq:lgbias` viết empirical ratio bằng population integral, sai finiteN. Tách μ_h^∞, thêm tail/UI và denominator control; injectiveB nếu nói b(y)≠0 mọi y≠0. | Tail stress test minh họa; proof assumptions phải sửa trước. |
| 1616 `prop:cfg` | Giữ: coefficients sum1 dù signed, affine orthogonal component=εq0. Subsequence endpoint support trong affine hull không là atom theorem. | Oracle projection identity. |
| 2119 `thm:labelmix` | Giữ: conditional symmetrization/Doob, McDiarmid; labels-only weights, continuous score CDF cho two-sided. **Fittedh uses responses**: add finite-grid union bound hoặc split selection. | P0selection/null checks. |
| 2184 `prop:tgtnoise` | Gaussian convolution endpoint và moments giữ. Following prose gain-bound sai (counterexampleC); two scalars match moments chỉ khi vector/matrix equations có nghiệm. | P1non-atomic comparator; test actual gain thay vì lower-bound inference. |
| 2244 `prop:prop17` | Giữ: Gaussian regression coefficient s'_t/s_t, explicit pathta_i+s_tx0, endpoint invariantσ. Weighted loss finite, unweighted infinite khiσ>0. | Oracle check nếu cần. |
| 2321 `lem:nonintersect` | Giữ generic non-intersection với dimension/genericity conditions đã ghi; finite sampled batch. | Không cần. |
| 2347 `prop:memorize` | Finite-batch measurable zero empirical-loss lookup field tồn tại. Tên “memorising field” không chứng minh an arbitrary generated ODE endpoint memorizes: field mới chỉ specified on finite curves. | Muốn claim neural realizability phải thêm approximation/regularity theorem; không có test thay proof. |
| 2471 `prop:nearduplicate` | Finite-N inequalities giữ. Nếu N đổi, phải yêu cầu η=(N−card(C))/card(C) exp(−gap²/2h²)→0; relative neff cần cluster growth control. | Cluster size/separation sweep có thể QA, không mở rộng limit thiếu condition. |
| 2493 `prop:factors` | Giữ algebra: label weights vs spatial spread trong exact models được định nghĩa. Không là universal taxonomy mọi regularizer. | Matched intervention nếu muốn causal claim. |
| 2821 `prop:cfgatom` | Conditional nearest-atom proof giữ. H removes premises cho hard case. B đóng positive-h CFG convergence và a.s. atomicity qua signed-energy/Jacobian proof riêng; không dùng V như thể signed weights vẫn positive. | P3 w/ε/solver controls chỉ QA; a.s. kết luận nay có proof. |
| 2895 `prop:liplb` | Giữ variance-copy inequality, positive part essential. | Analytic attainer check. |
| 2902 `cor:floor` | Giữ lower bound; L proves equality cho full class/time/source specified. Lower bound nhỏ không bác architecture gap. | No training required for L. |
| 2992 `prop:survival` | Giữ integrating-factor exact error identity/bound với specified integrability; không tự thế training loss dọc learned path. | Time-profile injected-error control. |
| 3092 `cor:lossform` | Giữ under Lipschitz-error assumption và trajectory comparison/coupling. Gaussian concentration hypothesis phải đúnglaw. | Profile error and bound on required support, không chỉ average loss. |
| 3395 `prop:specbias` | Finite SPD exponential convergence giữ; continuum multiplier theorem giữ như idealized unbounded operator. Không finite diagonal kernel, không positive probability kernel (G), không implied neural floor/rate. | Fixed-kernel empirical fit + NTK stability; saved results hiện chưa đóng mechanism. |

Assumptions cần giữ nguyên phạm vi: `as:standing` line234 (finite empirical setup); `as:design` line1386 (local random design, không đủ expected-risk tails); `as:lipschitz` line3085 (error regularity dùng cho lossform). Remark `lem:norepr` line2396 chỉ cho pointwise nonrepresentation: không suy ra infimum expected loss>0 nếu chưa có quantitative separation.

## Những phép sửa có proof, với review depth riêng

- **Endpoint smoothing counterexample C:** clean proof trong addendum;2freshHOLDS (`verify_new_results_5`, `verify_final_repairs`). ObstructionF=0 nhưngW2²gain=2/π; continuous target/positive atom weights vẫn có counterexample qua continuity. Giữ lower bound, bỏ upper-bound inference.
- **Response-selected finite-grid coverage R:** addendum union-bound proof;1freshHOLDS (`verify_final_repairs`). Replace log(1/δ) bylog(G/δ); không bao phủcontinuous search tự động.
- **Fourth-moment sample trace variance, randomized ties, heterogeneous conditional moments, NW heavy-tail counterexample:** proof/algebra trong addendum + statistics packet review. Chưa đạt4freshchecks; ghi rõ để không nhầm với H/L/G/V.
- **`docs/theory/lemma_L1.tex`:** positive exponential-kernel1D RKHS representer proof qua một fresh packet review chưa thấy lỗi; historical review counts trong note không tính vào lượt4fresh hiện tại. Không extend kết quả này sang arbitrary neural network.
- **`docs/theory/theorem_B.tex`:** cùng label-mixture coverage argument như manuscript; giữ labels-only/continuity assumptions. Không là theorem riêng chứng minh actual h_eff calibration.

## Bài toán còn mở sau lượt này

1. **Gaussian NW law cho trained sampler và floor/rate:** current moment fits không chứng minh. G loại một đường suy diễn universal từ continuum KGF. Cần falsifier phân phối P1 và solver P2 trước khi tìm bridge theorem có assumptions kiểm chứng được.
2. **Expected NW risk:** có counterexample đối với theorem hiện tại. Muốn theorem mới cần chọn rõ global moment/denominator-tail assumptions rồi chứng minh, không chỉ thêm citation “standard”.
3. **Endpoint weights của label-averaged/guided flows:** A/B chứng minh support, không xác định basin probabilities hoặc cho chúng bằng original NW weights. Đây là nghĩa mạnh hơn chưa có proof ở đây.

Hai nghĩa vụ từng còn mở trong vòng đầu (a.s. atomicity và positive-h CFG convergence) đã được đóng bằng A/B trong deep-mode rồi kiểm tra lại độc lập. Không giữ chúng trong danh sách open sau khi có proof.

Các experiments ưu tiên và stop rules nằm ở [future protocol](23_Feasibility_Pilot_Protocol.md). Audit này không sửa formal contracts trong canonical manuscript; addendum là bản chứng minh reviewable để tác giả quyết định tích hợp sau.
