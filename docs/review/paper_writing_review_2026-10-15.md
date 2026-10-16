# Đánh giá bản thảo ngày 15/10/2026

Bản được đánh giá: `paper/main.tex`, “Trained Conditional Flows Memorise at an Effective Bandwidth”, định dạng TMLR, nguồn cập nhật ngày 12/10/2026. Đây là đánh giá nội dung và cách viết theo skill paper-writing; không chỉnh sửa manuscript. Đã đối chiếu các chứng minh và script liên quan đến những nhận xét dưới đây, dữ liệu kết quả đã lưu, và ba hình mechanism/heff. Không phải chứng nhận đã kiểm chứng từng chứng minh hoặc tái chạy toàn bộ training.

## Nhận định

**Major revision trước khi nộp.** Paper có một câu chuyện nghiên cứu rõ và đủ dữ liệu để xây dựng một bài phân tích tốt: luật endpoint của empirical conditional flow là một họ phân phối tham chiếu chính xác; các moment của network có thể được đặt tương đối với họ đó; mức độ phù hợp và giới hạn thay đổi theo regime. Điểm yếu chính là một số câu chuyển từ “phù hợp về moment” sang “đúng phân phối”, hoặc từ một mô hình giải thích dùng posterior đã biết sang lợi ích thực hành rộng hơn.

Không nên coi số thí nghiệm/checkpoint là số lần xác nhận độc lập. Cũng không nên tiếp tục mở rộng appendix để trả lời mọi phản biện; việc ưu tiên hiện tại là làm cho title, abstract, contributions, figures và conclusion nói cùng một kết luận được dữ liệu hỗ trợ.

## Điểm mạnh

- **Đối tượng lý thuyết được xác định rõ.** Dataset cố định; randomness đến từ interpolation; minimiser trên không gian vector field; phân biệt conditional single-atom memorisation và unconditional empirical-measure memorisation.
- **Endpoint law tạo tham chiếu hữu ích.** Phân tích Bayes của weights, coupling và continuity equation nối được objective với endpoint. Trong phần đã đọc kỹ, không thấy lỗi đại số ở kernel weights, endpoint law, đạo hàm identifiability hoặc Gaussian covariance identity của theorem calibration.
- **Bài không giấu kết quả bất lợi.** CIFAR hard conditioning không phù hợp một bandwidth; Gaussian không phải family duy nhất có interval overlap; spread dự báo image coverage tốt hơn h_eff; incremental R² chưa đáng tin cậy. Đây là những giới hạn quan trọng đã có trong bản hiện tại.
- **Có kiểm soát thực nghiệm đáng kể.** Competing families, held-out conditions, label permutation, kiểm tra seed và replication image capacity khiến bài vượt khỏi một quan sát toy đơn lẻ.

## Các vấn đề cần sửa, theo mức ưu tiên

### 1. Cao — Khớp moment chưa chứng minh network tuân theo cùng một luật phân phối

**Vị trí:** `paper/main.tex:161`, `:207`, `:544`, `:729`; phát biểu tương tự ở `:3434`.

Estimator chỉ dùng mean vector và trace covariance. Hai đại lượng này không xác định covariance matrix, modality, tails hoặc support. Ngay cả khớp mean và toàn bộ covariance cũng chưa đủ xác định phân phối. Vì thế “follows the same law … exactly in low dimension” và “travels the same family of laws” vượt quá kiểm chứng hiện có. Median log-space R²=0.86 cũng là một mức phù hợp thực nghiệm, không phải đẳng thức.

Kiểm tra family endpoint-smoothed không cải thiện dự đoán không chứng minh tính atomic của model; nó chỉ cho thấy thành phần isotropic spread bổ sung chưa giúp family cụ thể đó trên metric được dùng. Laplace gần Gaussian, và kNN cũng overlap 48/48.

**Sửa:** thống nhất cách nói “its conditional means and variance traces are well described by the reference family”. Giới hạn title, chẳng hạn **“Effective Bandwidths of Trained Conditional Flows”**. Nếu muốn giữ kết luận về distribution, cần thêm phép kiểm tra phân phối ngoài những statistic đã dùng để fit, tại điều kiện chưa dùng để fit; đánh giá sai lệch weights, covariance orientation hoặc sample discrepancy với uncertainty phù hợp. Không nhất thiết phải làm thêm thí nghiệm nếu thu hẹp claim.

Ví dụ LaTeX-ready cho conclusion:

```latex
On the low-dimensional problems studied, a single effective bandwidth describes
the trained models' conditional means and variance traces. At image scale this
description holds in the tested smoothed regimes, but fails under hard conditioning
and does not establish agreement of the endpoint distributions.
```

### 2. Cao — Phần định lượng quantisation suy diễn quá mức từ tốc độ tiệm cận

**Vị trí:** `paper/main.tex:408–416`, `:2781–2814`.

Bất đẳng thức floor theo nearest atom là hợp lý. Vấn đề nằm ở việc dùng N^(-1/d)=0.9975 để kết luận error tại N=2000, d=3072 chỉ giảm một phần tư phần trăm so với one-atom error. Một tốc độ tiệm cận theo N, với d và distribution cố định, không cho tỉ số error hữu hạn giữa N=2000 và N=1. Hằng số phụ thuộc distribution/dimension và ngưỡng bước vào regime tiệm cận chưa được kiểm soát. Hai con số 0.071 và 0.9975 chỉ là giá trị của nhân tử N^(-1/d), không phải floor được đo hay finite-N lower bound cụ thể.

Tương tự, một sweep hữu hạn N=200…3200 có scaling phù hợp log(N)/N chưa chứng minh mệnh đề Theta(log(N)/N). Cần trích dẫn một định lý đúng cho distribution đang xét, chứng minh riêng, hoặc nói “consistent with … over the tested range”.

**Sửa:** giữ obstruction định tính và floor được đo; gắn rõ các giá trị của rate factor là minh họa. Bỏ kết luận “within a quarter of one percent of its one-atom value”. Không dùng scaling d nhỏ như một kết quả định lượng ở image dimension.

### 3. Cao — Lợi ích “không cần coverage labels” cần công khai thông tin posterior được sử dụng

**Vị trí:** `paper/main.tex:69–71`, `:170–173`, `:618–631`, `:3285–3310`; `scripts/theory_t3_coverage.py`, các hàm `smoothed`, `V_of`, `coverage_local_model`.

Dự đoán R²=0.90 không fit coverage labels, nhưng dùng prior covariance, A, observation noise và Gaussian local-atom model. Đây là một kết quả giải thích trong bài toán có posterior đã biết, chưa phải diagnostic dự đoán coverage trong bài toán posterior chưa biết. Variant “exact finite reference” còn đánh giá region bằng held-out truth. Cần phân biệt hai variant khi nêu lợi ích.

Theorem calibration(d) chứng minh hai identity moment cho fixed weights và i.i.d. atoms, cùng kết quả coverage tại n_eff=1. Nó không tự chứng minh công thức coverage của weighted, label-dependent empirical sample ở n_eff hữu hạn. Mô hình local Gaussian là bước xấp xỉ bổ sung; điều kiện trên labels cho các atom independent nhưng thường không identically distributed.

**Sửa:** thay claim bằng “predicts coverage without fitting coverage labels in the known linear-Gaussian setting”. Nêu rõ Gaussian local model là approximation được đánh giá thực nghiệm, không gọi R² là hệ quả trực tiếp của (d). Giữ negative result ΔR²=0.04, CI chứa 0 ngay gần claim lợi ích.

### 4. Trung bình–cao — Near-atom criterion và cùng integrator không chứng minh atomic support hoặc loại trừ solver error

**Vị trí:** `paper/main.tex:2559–2580`; `src/metrics/memorization.py`; cấu hình DDPM `n_steps: 50`, `ode_eps: 0.001`.

Paper giải thích đúng metric “on-atom” thực tế là tỉ số khoảng cách nearest/second-nearest, không phải equality. Tuy vậy, các câu sau vẫn dùng kết quả này như phép đo support, và kết luận h=0 đạt 1.000 “rules out ODE discretisation … since the same integrator is used throughout”. Tỉ số 1.000 chỉ nói mọi sample vượt threshold relative-distance. Sai số của cùng integrator có thể khác giữa các velocity field/bandwidth, nhất là vùng cuối flow.

**Sửa:** gọi metric là near-atom/memorisation fraction. Bỏ câu loại trừ solver error, hoặc bổ sung convergence study giữ cố định checkpoint và source draws, tăng steps và giảm endpoint cutoff, ở h=0 và ít nhất một h>0. Báo cáo absolute nearest-atom distance cùng metric tương đối. Chưa thể kết luận numerical error là nguyên nhân; điểm hiện tại là bằng chứng chưa loại trừ được nó.

### 5. Trung bình — Interval overlap và các checkpoint lồng nhau cần được diễn giải đúng

**Vị trí:** `paper/main.tex:62–64`, `:543–546`, `:579–590`, `:649–653`, `:3231–3245`; `scripts/heff_family_test.py:328` trở đi.

“48/48 agreement” thực chất là overlap hai bootstrap interval; không phải equivalence test hoặc 48 lần xác nhận law độc lập. Các checkpoint chung run phụ thuộc nhau. Mean và trace cũng được đo từ cùng generated draws; “disjoint statistics” không có nghĩa là independent estimates. Một số bandwidth chung seed còn dùng cùng problem instance.

Bootstrap so sánh Gaussian–Laplace hiện resample checkpoint. Tôi tính lại từ JSON đã lưu, 10,000 bootstrap draws, median log-RMSE gap dương nghiêng Gaussian:

| Đơn vị resample | 95% percentile interval |
|---|---|
| Checkpoint | [0.0109, 0.0236] |
| Run | [0.0130, 0.0246] |
| Problem seed | [0.0094, 0.0246] |

Ở dữ liệu này clustering không đảo chiều preference. Vì chỉ có ba problem seeds, interval cuối không đủ để khẳng định robustness rộng; nên báo cáo cả per-seed effects. Đây là yêu cầu thống kê và diễn đạt, không phải bằng chứng rằng kết quả Gaussian preference đã sai.

**Sửa:** gọi đúng là interval overlap, báo cáo gap hoặc paired-bootstrap log(h_eff/h_mean), dùng margin equivalence định trước nếu muốn nói agreement. Giữ checkpoint counts như mô tả, báo rõ số run và số problem instances độc lập.

### 6. Trung bình — Áp dụng identifiability bound vào uncertainty chưa phải chứng nhận

**Vị trí:** `paper/main.tex:570–574`; `scripts/theory_t1_check.py:47–60`, `:120–145`.

Proposition cho bound khi có h_true, perturbation e quanh F(h_true), local slope lower bound và điều kiện global separation. Script thay e bằng fitted residual quanh h_eff, tính minimum slope trên 25 grid points, rồi so với bootstrap half-width. Fitted residual không tự là bound cho measurement/model error quanh h_true; minimum trên grid cũng chưa chứng minh lower bound trên cả interval; global separation chưa được xác nhận bởi phép đo này.

**Sửa:** trình bày phép so sánh như sensitivity diagnostic thực nghiệm tương quan với interval widths. Tránh gọi nó là validated uncertainty guarantee. Nếu cần guarantee, phải thêm noise model, kiểm soát slope giữa grid points và xử lý multiple branches/global separation.

### 7. Trung bình — Giả thiết convergence/unique nearest atom bị mất trong các câu tóm tắt

**Vị trí:** `paper/main.tex:676–696`, `:3473–3477`, `:2827–2830`.

Proposition filtered(b) và cfgatom là các phát biểu có điều kiện: trajectory phải hội tụ, limit có unique nearest atom, hoặc các điều kiện đó đúng gần như chắc chắn. Các câu “cannot produce off-atom samples”, “never reaches anything else”, “needs an error in the spatial dependence” bỏ những điều kiện ấy. Phần cuối appendix về CFG đã thừa nhận almost-sure convergence chưa được chứng minh; main text nên có phạm vi tương ứng. Đồng thời phép đo tại t=1-eps không phải endpoint limit.

**Sửa:** “under the convergence and non-tie conditions of Proposition …”. Phân biệt mệnh đề pathwise với kết luận law/support cho almost every source draw.

### 8. Trung bình — Bố cục chưa đưa bằng chứng chính đến đúng chỗ

**Vị trí:** abstract `:55–76`, main experiments `:532–704`, hai hình cốt lõi `:3133–3154`.

Title hướng đến trained effective bandwidth nhưng phần chính ưu tiên derivation/reference và figure spectral-bias surrogate. Hai hình trực tiếp chứng minh h_eff/h_mean và trajectory của trained models nằm appendix. Trong khi đó paper tự đo được network training không ở fixed-kernel/lazy regime. Hình surrogate hữu ích cho intuition nhưng không nên chiếm vị trí của bằng chứng trained-model claim.

**Sửa:** đưa hai hình heff vào main text dưới dạng figure gộp, chuyển figure spectral-bias xuống appendix. Rút contributions còn ba ý rõ: exact reference; empirical moment description + identifiability; calibration audit + failure regimes. Giảm abstract xuống khoảng 180–230 từ, giữ một vài kết quả quyết định thay vì dày đặc số.

Có một lỗi cụ thể trong hình synthetic: heading panel (a) nói “stops at h”, còn text/caption nói “stops just above h”; đường h=0.05 hiện cũng còn trên dashed h. Cần sửa heading thành “approaches the training bandwidth”.

### 9. Trung bình/thấp — Presentation và tooling chưa đồng bộ

- Abstract báo rank coverage 0.77–0.87 so với 0.91; main text báo quantile coverage 0.72–0.81 so với 0.87. Hai protocol đều có giải thích ở appendix, không phải numerical contradiction, nhưng người đọc main text rất dễ tưởng là mâu thuẫn. Chọn một protocol chính và ghi tên protocol cạnh kết quả.
- Cụm “a correct Bayesian sampler” tại `paper/main.tex:461–463` dựa trên variance tracking là quá mạnh. Dùng “approximately matches posterior variance”, hoặc viện dẫn kiểm tra distribution/calibration cụ thể cho cùng checkpoint.
- Tương tự, suy ra nguyên nhân thất bại của image fit là heteroscedasticity từ slope beta=0.481 ở `:2210–2213`, `:2876–2880` chưa tách được các giả thuyết khác như approximation/optimisation error. Nên nói result không được theorem đó bao phủ.
- Var của random vector nên được định nghĩa là trace covariance ngay Setup; hiện việc giải nghĩa rõ xuất hiện muộn trong proof noisy interpolant. Ký hiệu kappa có nhiều vai trò ở identifiability và conditional law; đổi conditional law sang ký hiệu khác để đọc dễ hơn.
- `paper/README.md` còn mô tả ICLR và trạng thái cũ. `scripts/check_paper.py` vẫn hardcode giới hạn ICLR 9 trang và kiểm tra anonymity bằng iclrfinalcopy; không nên coi check đó là kiểm tra đầy đủ cho TMLR.

## Novelty và định vị

Memorisation/collapse và việc đọc kernel từ empirical flow đã có tiền lệ. Nguồn gốc được kiểm tra trên các bài gốc: [Dasgupta et al.](https://arxiv.org/abs/2603.14135) phân tích selective memorisation trong conditional inverse problems; [Smola](https://arxiv.org/html/2605.13386v1) liên hệ empirical velocity với NW smoothing có bandwidth phụ thuộc flow time; [Li et al.](https://arxiv.org/abs/2606.08554) phân tích training-sample recovery và sai lệch do numerical/estimation errors.

Theo đánh giá của tôi, đóng góp nên được đặt ở **label-bandwidth endpoint reference và việc dùng moment của nó để mô tả network, kèm các chế độ thất bại**. Cách này phù hợp với scope boundary mà introduction đã xây dựng. Đây không phải một literature audit toàn diện; chưa kết luận đã loại trừ mọi công trình trùng ý.

## Kiểm tra đã thực hiện và giới hạn

- Chạy `.venv/Scripts/python.exe scripts/verify_paper_numbers.py`: **359 passed, 0 failed**. Điều này xác nhận các phép đối chiếu script hiện có, không chứng minh toàn bộ mọi số/câu trong paper; một số check dùng claimed constants viết sẵn và chỉ kiểm tra một số string có mặt trong tex.
- Chạy phần kiểm tra source: **216 labels duy nhất**, mọi ref/eqref có label; **45 figures**, **19 tables** đều được reference theo checker; không thiếu citation keys hoặc image assets. Chưa chứng nhận vị trí cross-reference đúng về ngữ nghĩa.
- Đọc trực quan ba hình PNG mechanism, synthetic h_eff, CIFAR h_eff. Chưa kiểm tra font/float/spacing trong PDF mới nhất.
- Thử compile bản nguồn vào `tmp/paper-review-2026-10-15/`, nhưng MiKTeX báo fresh installation và không truy cập được thư mục cấu hình người dùng. Không xác nhận compile thành công. PDF có sẵn ngày 02/10 cũ hơn tex ngày 12/10 nên không dùng nó để chứng nhận layout bản hiện tại.
- Không chạy lại training/GPU hoặc sửa manuscript. Các review cũ được dùng làm bối cảnh; các findings trên được kiểm tra lại trong source/code hiện tại.

## Thứ tự chỉnh sửa đề xuất

1. Sửa claims về law/exactness, quantisation và posterior-free utility trước. Đây là những thay đổi quyết định độ đúng của kết luận.
2. Chuyển figure h_eff lên main text, thống nhất coverage protocol, rút abstract/title/conclusion theo cùng scope.
3. Sửa diễn giải atomicity/solver; bổ sung solver convergence study nếu còn muốn giữ attribution về off-atom spread.
4. Gắn đúng assumptions của filtered/CFG và giới hạn thực nghiệm của identifiability diagnostic; đổi uncertainty summaries sang clustered reporting.
5. Đồng bộ README/checker với TMLR, compile lại và đọc PDF trước khi nộp.

Không cần mở một loạt benchmark mới để giải quyết các vấn đề viết hiện tại. Bản thảo sẽ thuyết phục hơn khi phân biệt rõ **định lý chính xác**, **mô hình xấp xỉ**, **quan sát thực nghiệm** và **lợi ích thực hành đã được chứng minh đến đâu**.
