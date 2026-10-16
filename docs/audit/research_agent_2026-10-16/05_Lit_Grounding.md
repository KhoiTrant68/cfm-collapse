# Literature grounding — 16 October 2026

**Novelty gate: REVISE.** Phạm vi có thể bảo vệ là một chẩn đoán bandwidth dựa trên moment cho những regime được kiểm tra, kèm giới hạn và falsifier. Không nên đặt novelty vào conditional expectation, empirical memorization, hay đồng nhất mọi network với một kernel NW. Đây là kết luận từ các nguồn đã đọc, không phải chứng nhận đã tìm hết literature.

## Nguồn gần nhất và phần đóng góp còn lại

| Nguồn sơ cấp đã kiểm tra | Vị trí và kết quả liên quan | Hệ quả đối với bài hiện tại |
|---|---|---|
| [Baptista et al., 2501.15785](https://arxiv.org/html/2501.15785), v2 | §6.3, Theorem 6.4: empirical conditional score chỉ dùng các index tương ứng với label; label duy nhất làm conditional mixture còn một component. Ngoài các empirical label cần xác định extension. | Phải bổ sung vào related work/bibliography. Không gọi unique-label collapse là phát hiện chưa có tiền lệ. |
| [Dasgupta et al., 2603.14135](https://arxiv.org/html/2603.14135v3) | §3.2, eq. 38–41; §3.3, eq. 44–46: label cells chọn subset; endpoint thuộc các training point trong cell. | Bảng related work hiện chỉ nói “a point” là chưa phản ánh đầy đủ phạm vi conditional của nguồn này. |
| [Smola, 2605.13386](https://arxiv.org/html/2605.13386v1) | §3.1–3.2, Propositions 1–2: NW biểu diễn spatial empirical score, với bandwidth theo thời gian. | Kernel identity đã có; cần phân biệt spatial bandwidth với label bandwidth độc lập của bài. |
| [Pfrommer et al., 2512.18736](https://arxiv.org/html/2512.18736) | §4, Theorem 3 và eq. 4.2: regularity theo conditioning variable, Fourier multiplier của regularization và self-guidance. | Đây là đối thủ gần cho cơ chế label resolution; không chỉ dẫn như background chung. Kết quả mới G trong addendum phân biệt spectral filter với probability kernel. |
| [Scarvelis et al., 2310.12395](https://arxiv.org/html/2310.12395) | §3–4: empirical score memorization và spatial smoothing tạo barycenter/novel samples. | Câu “chỉ endpoint noise thay đổi support” chỉ đúng trong ba intervention đã định nghĩa của bài; không phải khẳng định về mọi regularization. |
| [Bertrand et al., 2506.03719](https://arxiv.org/html/2506.03719) | §2–3: empirical closed-form flow, memorization, và khoảng cách giữa neural/closed-form velocity. | Conditional expectation theo latent endpoint trong CFM phải phân biệt với external conditioning label. |
| [Buchanan et al., 2508.17689](https://arxiv.org/html/2508.17689) | §4: capacity và memorization transition, loss forecasting. | So sánh với bandwidth theo checkpoint; memorization ratio theo nearest neighbor không đồng nghĩa exact atom membership. |
| [Li et al., 2606.08554](https://arxiv.org/html/2606.08554v1) | Oracle recovery, estimation và Euler discretization. | Solver error phải được kiểm tra trước khi gán off-atom samples cho learned spatial error. Không sử dụng proof trong nguồn như certificate cho các lemma mới ở đây. |
| [Lemos et al., TARP, 2302.03026](https://arxiv.org/html/2302.03026) | §3, Theorem 3: sample-based coverage và lựa chọn credible regions. | Marginal coverage không chứng nhận toàn bộ conditional distribution; nên đặt calibration diagnostics vào literature SBI. |

## Residual delta có thể kiểm tra

1. Một scalar bandwidth có dự đoán được **held-out conditional distributions**, vượt Gaussian/Laplace/Cauchy/kNN và baseline miễn phí, hay chỉ fit trace tốt?
2. Mean-fit và trace-fit thống nhất ở synthetic được hỗ trợ; việc đó không suy ra equality của law. CIFAR hard conditioning đã là counter-regime.
3. Các theorem bổ sung H, L, G, convergence và almost-sure atomicity trong [proof addendum](proof_addendum.tex) có giá trị toán học trong phạm vi chính xác của chúng. Chưa thực hiện priority search riêng cho từng theorem; không tuyên bố chúng là first result trong literature.

## Falsifier đã chạy trên saved statistics

Đọc [heldout_family.json](heldout_family.json): bỏ từng condition khỏi **fit bandwidth**, fit trên 19 condition còn lại rồi dự đoán log trace ở condition bị bỏ. Gaussian thắng Laplace **35/48** checkpoint; median RMSE Gaussian **0.1333**, Laplace **0.1532**, Cauchy **0.3384**, kNN **0.4949**. Ở h=0 chỉ thắng **6/12**. Chênh lệch median ghép cặp Laplace−Gaussian là **0.02243**.

Đơn vị độc lập là **3 problem seeds / 12 selected runs**, không phải 48 checkpoint độc lập. Đây là chẩn đoán post hoc trên cùng bộ dữ liệu, không phải validation độc lập; chưa kiểm tra distributional shape. Nó hỗ trợ một descriptive fit, chưa đóng cơ chế Gaussian NW duy nhất. Chạy lại bằng [recompute_heldout_family.py](recompute_heldout_family.py); lượt kiểm tra tái lập đủ 48 rows và đúng 35 wins/median gap.

Các truy vấn literature đã dùng gồm conditional flow matching/effective bandwidth/memorization và label-noise/NW. Phạm vi tìm kiếm này không đủ để chứng minh không có prior work. Quyết định tiếp theo: thực hiện falsifier phân phối ở [protocol](23_Feasibility_Pilot_Protocol.md), sau khi sửa metric và chốt provenance.
