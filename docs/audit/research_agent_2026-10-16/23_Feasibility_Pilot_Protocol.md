# Conditional future experiment protocol — NOT AUTHORIZED

**NOT AUTHORIZED for execution. Current gate: BLOCK.** Đây là đề xuất thí nghiệm theo yêu cầu của tác giả, không phải lịch chạy hay full-run approval. Chỉ corrective offline evidence work hiện đủ điều kiện. Sau khi sửa measurement và xác nhận checkpoint/config, có thể xét `FEASIBILITY_PILOT_ONLY`; full run vẫn cần kết quả pilot hợp lệ và quyết định của tác giả.

## P0 — Sửa measurement trước khi đo thêm

**Câu hỏi:** metric có đúng null dưới contract thực sự không?

- Kiểm tra exact calibrated Gaussian continuous, calibrated point mass, Gaussian có ties do quantization, collapsed sampler và overdispersed sampler.
- Dùng randomized tie rank với RNG seed ghi rõ; joint score phải đối xứng giữa truth và generated draws, bao gồm ridge/PCA rule. Báo tỷ lệ ties trong archived image outputs trước khi diễn giải ảnh hưởng.
- Với trace covariance, dùng fourth-moment variance hoặc ghi rõ Gaussian approximation; không dùng √(2/(M−1)) như bound phân phối bất kỳ.
- Nếu h_eff được chọn từ response, dùng fixed independent selection set hoặc uniform finite-grid theorem với log(G/δ), không plug trực tiếp vào fixed-h theorem.

**Acceptance:** analytic point-mass rank null đúng sau randomization; các Gaussian controls nằm trong binomial uncertainty đã định trước; đối xứng score qua permutation. **Cost ceiling:** offline kiểm tra nhỏ ≤5 phút sau khi implementation xong. **Stop:** null thất bại thì chưa diễn giải coverage mới. Không tự động sửa lại archived numbers khi chưa có raw samples.

## P1 — Falsifier ưu tiên: cùng moment có thật sự cùng law?

**Primary contrast:** trained sampler vs finite-time exact Gaussian-label NW reference; Gaussian vs Laplace/Cauchy/kNN là đối chứng family. Claim cần phân biệt: “moment diagnostic tốt” và “một bandwidth mô tả phân phối”.

**Unit/provenance:** 3 problem seeds, h∈{0,.1}, checkpoint200k; dùng đúng local MLP checkpoints và training config. Fit h trên20 training conditions như protocol cũ; tạo8 held-out conditions bằng rule/seed cố định trước khi xem kết quả. Không xem48checkpoint như48replicate độc lập. Bắt đầu một seed/một h để timing; chỉ mở rộng khi fit/memory/output hợp lệ.

**Controls:** so sánh law tại cùng terminal ε, tức Σ_i p_i N((1−ε)a_i, ε²I), thay vì so samples ở t=1−ε với delta ở t=1. Sinh ref-vs-ref null và non-atomic control có cùng mean/covariance. Dùng nguồn random ghép cặp giữa solver/family khi phù hợp. Freeze metric chính là energy distance chuẩn hóa theo posterior scale, kèm MMD hoặc projected CDF như diagnostic; M=256 ở pilot,512 nếu timing cho phép. Ghi Monte Carlo reference uncertainty.

**Tiêu chí đã khóa cho pilot:** excess discrepancy so với ref-vs-ref null phải có interval theo seed/condition; không đặt threshold sau khi nhìn output. Nếu mọi candidate atomic mixture đều lệch có hệ thống nhưng same-moment control không bị moment test loại, drop exact-law reading và giữ descriptive-moment claim. Một pilot không có power không được tính là xác nhận law. Không fit lại bằng held-out conditions.

**Cost ceiling/stop:** loading/timing≤5 phút; chọn batch theo timing để tổng CPU wall≤30 phút (hard ceiling60 phút chỉ khi đã định trước và được mở gate). Đây là ceiling, không phải dự báo runtime. Stop nếu thiếu checkpoint, config sai, NaN, hoặc projection/metric đổi sau khi xem output. Không retrain.

## P2 — Tách solver error khỏi learned spatial error

Với P1 checkpoint/source samples cố định, so RK4 steps100/200/400 tại ε=10⁻³; chỉ thử ε=10⁻⁴ sau khi step-size đã hội tụ. Primary: paired endpoint displacement, distance-to-nearest-atom, energy distance và covariance-trace thay đổi. Một thay đổi do solver lớn ngang alleged off-atom signal thì chưa gán signal cho network.

**Acceptance:** 200→400 change nhỏ hơn Monte Carlo uncertainty và nhỏ hơn một phần mười contrast network-vs-reference đang giải thích; rule ghi trước output. **Stop:** nếu không đạt ở400 bước, báo unresolved discretization và dừng inference cơ chế. Chạy oracle field cùng source làm positive control; time ceiling dùng chung P1, không âm thầm tăng.

**Image branch:** kiểm tra exact 35.75M DDPM checkpoint trước; sau đó mới đề xuất Euler50/100/200/400 với cùng x0 và ε. Hiện branch này BLOCK do chưa có local checkpoint và chưa xác nhận remote access. Không thay bằng small U-Net rồi gán kết luận cho model cũ.

## P3 — Những theorem mới cần kiểm nghiệm gì?

| Kết quả | Kiểm tra numerical hữu ích | Điều thí nghiệm không chứng minh |
|---|---|---|
| H: hard CFG endpoint | Oracle w=0,3,12; cùng x0; vẽ ∥x_t−ta_i∥²/ε² dưới entropy bound; symmetric w=−1 làm negative control | Không suy ra learned network thỏa cùng bound. |
| L: sharp Lipschitz floor | Tính trực tiếp analytic attainer v_L; quadrature loss đối chiếu d/(3L) | Không cần huấn luyện để “chứng minh”; architecture-constrained infimum có thể lớn hơn. |
| G: spectral filter không phải probability kernel | Signed inverse-filter diagnostic là minh họa; không cần sweep để xác nhận theorem | Fit Gaussian ở finite conditions không bác G, G cũng không bác finite fit. |
| Averaged-label / CFG endpoint | Two symmetric atoms, x0=0 cho exceptional tie limit; perturbed x0 và unequal label weights kiểm tra basin; nhiều ε/step sizes | Null basin đã có proof A/B; finite simulation chỉ minh họa và kiểm tra implementation. |
| Covariance expansion | Fixed local homoscedastic design, nhiều N và h với Nh^(k+4) tăng; heteroscedastic negative control; compare full matrix | Không suy ra h²JJᵀ ở CIFAR. |
| Survival bound | Inject spatial errors có profile theo t, cùng x0, so exact endpoint error với integral bound | Một số successful perturbations không cho universal guarantee cho network. |

## P4 — Chỉ sau khi falsifier sống sót

Chỉ khi P0–P2 hợp lệ mới xem xét independent data/seeds để kiểm tra incremental prediction của h_eff so raw spread/loss/iteration và kiểm tra NTK stability bằng checkpoints tương ứng. Hiện saved NTK đổi mạnh và baseline spread giải thích image coverage tốt hơn; không có lý do chạy một full grid cơ chế trước khi phân phối và solver được tách.

**Learning value:** P1 thất bại vẫn trả lời đúng câu hỏi exact-law claim có cần bỏ không. P2 thất bại chỉ ra measurement chưa tách được numerical error. Không tự chuyển mọi null result thành một câu chuyện theory mới. Các proof và claim contracts nằm ở [formalization](06_Math_Formalization.md), evidence/gates ở [Reality Gate](20_Reality_Gate.md).
