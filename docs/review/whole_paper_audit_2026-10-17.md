# Whole-paper audit — 17 October 2026

## Quyết định

**REVISE — chưa đạt điều kiện một bản thảo đã được kiểm tra hoàn chỉnh để gửi.** Hai kết quả chính về positive averaging và fixed finite nonnegative CFG vượt qua lượt kiểm tra độc lập này. Tuy nhiên, có phát biểu phụ sai, giả thiết bị thiếu, và nhiều diễn giải thực nghiệm trong appendix mạnh hơn bằng chứng hoặc mâu thuẫn với phần chính. Chúng phải được sửa trước khi gọi toàn paper là đúng và nhất quán.

Đây là audit toàn manuscript, không phải chứng nhận hình thức hay bảo đảm chấp nhận tại ICLR/ICML/NeurIPS. Không chạy training mới. Không sửa `paper/main.tex`, bibliography hoặc PDF canonical trong lượt audit này.

## Bản đóng băng và cách kiểm tra

- Canonical: `paper/main.tex`, Git HEAD khi bắt đầu `99e08688cb68d47070195ae36c790fdb847f32ab`.
- SHA256 source: `a0f319683cee5b0390d29757974b435f7e23623bea86732a62c6b472a47b351c`.
- SHA256 bibliography: `41541985f42e9ec6d8e2a4a3788aaa4ff7ea4ff6b8438fbc401c37baa95a6304`.
- SHA256 PDF canonical: `36eb24ba8948e0ce7f98141a768fba193f1b9737f0595647d392bf7086f9b207`.
- 95 trang; 37 kết quả có đánh số: 21 propositions, 7 corollaries, 4 theorems, 5 lemmas; thêm 3 assumptions, 5 remarks và 38 proof environments.
- Trong 37 kết quả: **32 AUDITED**, **5 OPEN cần sửa hoặc làm rõ** (`prop:expansion`, `prop:cfg`, `prop:nearduplicate`, `prop:tgtnoise`, `prop:loss-no-certificate`). Các mục OPEN không đồng nghĩa cả công thức đều sai: expansion có parenthesis sai; bốn mục còn lại cần boundary hypotheses hoặc proof/notation clarification. Prose vẫn có lỗi riêng dù formal theorem đúng.
- Rà toàn văn theo thứ tự phát biểu, proof và consumers; independent reviewers đọc source thực tế ở cùng hash. Kiểm tra source/code/results và nguồn gốc tách khỏi kiểm tra chứng minh. Editor duy nhất giữ canonical source; reviewers chỉ đọc.
- Style authority hiện tại là **TMLR**, không phải README cũ ghi ICLR. Giữ macro và notation hiện có. Audit không chuyển venue hoặc tự thay đổi mathematical contracts.
- Quyền sử dụng: đọc repo/nguồn công khai, chạy kiểm tra có sẵn và build trong `tmp/whole-paper-audit-2026-10-17/`; ghi báo cáo/ledger. Không commit, push hoặc submission.

## Các vấn đề toán học cần sửa

### M01 — P1: Số mũ Zador không cho sai số hữu hạn chiều cao đã khẳng định

**Vị trí:** `paper/main.tex:420–425`, `3167–3193`.

Giá trị số `2000^(-1/3072)=0.9975` không chứng minh rằng sai số còn trong 0.25% của one-atom error. Tiệm cận với d cố định có hằng số phụ thuộc phân phối và chiều; nó không tự chuẩn hóa theo N=1 hoặc cho bound hữu hạn N.

Phản ví dụ full-rank, có mật độ dương: P bằng hỗn hợp hai Gaussian với tâm ±a e₁ và covariance ε²I_d. Quantizer hai tâm có squared cost không quá dε²; optimal one-atom cost bằng a²+dε². Tỷ số root error có thể tiến về 0 khi ε/a→0, kể cả d=3072 và cho phép đến 2000 atom. Vì thế full rank không cứu kết luận này.

**Sửa nhỏ nhất:** bỏ diễn giải sai số/one-atom ratio; giữ số mũ như gợi ý định tính, hoặc phát biểu một nonasymptotic bound cho một posterior được chỉ định với giả thiết thích hợp. Câu Zador còn cần điều kiện moment thích hợp; một absolutely continuous Cauchy target có quadratic quantization error vô hạn với mọi finite codebook. Không đồng nhất một intrinsic dimension tùy ý với Euclidean dimension trong theorem được trích.

### M02 — P1: Finite-range fits bị nâng thành định lý tiệm cận

**Vị trí:** `3176–3182`.

Các slope và tỷ số được đo trên 200≤N≤3200 không chứng minh `F_N=Θ(log N/N)` hoặc “the exponent is attained”. Script dùng 12 random-codebook replicates và Monte Carlo queries, trong khi câu tiệm cận không chỉ rõ expectation, high probability hay almost sure.

**Sửa:** báo cáo “phù hợp với exponent ứng viên trên khoảng đã thử” và logarithmic correction mô tả khoảng đo tốt hơn; muốn giữ Θ phải có theorem riêng với probability mode rõ ràng.

### M03 — P2: Điều kiện cần trong Proposition expansion là sai

**Vị trí:** `1682`, `prop:expansion`.

Câu “h² term is identifiable only if Nh^(k+4)→∞” không suy từ generic upper bound và sai trong các trường hợp được phép. Lấy k=d=1, Y~N(0,1), X=Y và query 0: Σ=0, J=1. Weighted empirical covariance chia cho h² hội tụ về 1 khi Nh→∞, vì weighted local first/second moments có fluctuations O_P((Nh)^(-1/2)). Chọn h=N^(-1/3): Nh→∞ nhưng Nh⁵→0.

**Sửa:** điều kiện mạnh hơn là **đủ để tách h² khỏi generic stochastic error được hiển thị**, không phải điều kiện cần. Displayed expansion vẫn được proof hỗ trợ.

### M04 — P2: Resampling không loại mọi measurable lookup table

**Vị trí:** `2766–2778`, `rem:resample`, và consumers `2893–2910`.

Một countably infinite stream độc lập gần như chắc chắn có các input (X_t,t) khác nhau. Gán prescribed target tại từng input và 0 ở ngoài tập đếm được tạo một Borel field khớp toàn stream. Nó thậm chí bằng 0 như một phần tử của population L². Vì thế “no single lookup table stays consistent” sai trong chính measurable-field class của Proposition memorize.

**Sửa:** phân biệt một finite table đã cố định thất bại trên fresh inputs với một hàm được chọn sau toàn stream. Resampling riêng lẻ chưa chứng minh SGD hội tụ hay generalization; larger-N explanation phải được đánh dấu hypothesis. “Unconditional memorisation is not universal” cũng phải phân biệt single-pair lookup với memorization của toàn empirical law.

### M05 — P2: Bound cho deviation bị gọi thành bound cho actual spread

**Vị trí:** `3499–3500`, consumer của `cor:lossform`.

Chọn exact field v=v₀*: loss=0, Δ=0, L_Δ=0. Tuy nhiên ở cutoff 1−δ, actual conditional standard deviation vẫn là δ√d. Vì vậy bound `e^{L_Δ}√(L_i δ)` không thể một mình chặn actual spread. Formal corollary đã có term truncation đúng; câu giải thích bỏ mất nó.

**Sửa:** dùng deviation so với exact trajectory, hoặc thêm term truncation; bound quanh atom là `e^{L_Δ}√(L_i δ)+δ(E|X₀−xⁱ|²)^(1/2)`. Không thay đổi formal corollary chỉ để khớp câu prose sai.

### M06 — P2/P3: Giả thiết biên và notation cần ghi đủ

- `prop:cfg`, `1931`: h=0 phải giới hạn query ở observed/identifying labels, nếu không field ở unseen label không được objective xác định. `prop:cfgatom` đã nêu đúng điều kiện này.
- `prop:nearduplicate`, `1969–1984` và `2858–2872`: cần `C≠∅` và `h>0`; hiện công thức chia cho |C| và h² mà không loại các trường hợp này.
- Proof `prop:tgtnoise`, `1529–1540`: lời khẳng định regularity tới t=1 và absolute continuity phải có ρ>0. Endpoint formula ở ρ=0 đúng nhưng cần xử lý bằng endpoint theorem riêng.
- `prop:loss-no-certificate`, `3573–3599`: proof ở một fixed label gọi conditional loss là global L₀. Có thể viết `vδ(x,t,yʲ)=xʲ+kδ(t)(x−txʲ)` ở mọi observed label, hoặc đổi notation thành conditional loss. Counterexample mechanism và integral đúng.
- Conventions `3142–3152`: h=0 không có thêm null-label-slice ambiguity tại observed label, nhưng vẫn có a.e. ambiguity trong (x,t). Smooth representative convention cần tiếp tục được giữ.

### M07 — P3: Endpoint value chưa đủ thay cho endpoint limit

**Vị trí:** `2646–2649`, `2830–2835`, `rem:notsampler`.

Câu “any schedule with γ(1)=0 has X_t→xⁱ” cần điều kiện γ(t)→0 khi t↑1, cùng regularity/well-posedness phù hợp. Ví dụ γ(t)=1 ở t<1 và γ(1)=0 thỏa endpoint value nhưng limiting noise không biến mất. Square-root schedule thực sự được proof xét không có lỗi này; cần giới hạn câu khái quát hoặc nêu rõ continuity.

## Bằng chứng thực nghiệm và diễn giải

### E01 — P1: Khớp moment không chứng minh learned endpoint law

**Vị trí:** `4343–4347`, `4363–4367`, `4703–4706`, `5208–5211`, `5374–5379`, `5418–5421`, `5530–5535`.

Các đoạn “verification of endpoint law”, “generated law remains atomic”, “model converges to the atomic law” và gọi variance match là calibration không được variance, effective bandwidth, MMD hay nearest-atom assignments chứng minh. Chúng trái với phần chính `768–775` và independent distributional evaluation `683–691`.

**Sửa:** thống nhất toàn paper: atomicity là theorem cho exact reference; empirical claim chỉ là agreement của metric đã đo. Finite-run completions giống nhau bằng mắt không chứng minh bằng nhau chính xác hoặc limiting support.

### E02 — P2: CIFAR finite-cutoff không cô lập endpoint hoặc solver error

**Vị trí:** `725–728`, `4273–4279`; bản giải thích thận trọng đã có ở `2951–2967`, `4084–4087`.

Hard-label integration thành công không loại solver/truncation error của một smoothed learned field khác. Dùng nhất quán kết luận rằng samples được đo phản ánh đồng thời learned field, cutoff và solver. `4088–4090` cũng nên nói “approaches atoms at this cutoff”, không phải xác nhận mọi endpoint.

### E03 — P2: Objective interpolant-noise trong code khác objective lý thuyết

**Vị trí:** `562–563`, `2621–2632`, `4415–4423`, `5555–5558`.

Lý thuyết dùng time-weighted loss để target có finite second moment. Code `src/flows/cfm.py:90` dùng ordinary squared loss; `src/flows/interpolants.py:45,65` clamp time vào [10⁻⁴,1−10⁻⁴]. Đây là một regularized empirical objective và phải công bố. Không gọi nó là kiểm nghiệm nguyên xi weighted theorem hoặc nói noise “changes nothing” cho trained models.

### E04 — P2: Theorem không bao trùm caption randomization/CADS bất kỳ

**Vị trí:** `2979–2988`, `3114–3121`, `3323–3328`.

Token/caption replacement và inference-time annealed noise không đồng nhất với fixed additive Gaussian training-label noise. Đổi “exactly” thành connection có giới hạn, hoặc chứng minh theorem mở rộng riêng. Không dùng kết quả fixed-prior để ngầm xử lý schedule khác.

### E05 — P2: Two-slice variance không phải full variance decomposition

**Vị trí:** `4996–5027`, headline `510–513`.

Hai slices giữ cố định hai yếu tố khác nhau không định lượng interactions hoặc mọi EXP-1 error bar. Tỷ số `0.1261²/(0.1261²+0.0675²)=78%` là descriptive quadrature share của hai slices, không chứng minh 78% cho mọi setup hoặc không còn nguồn biến thiên đáng kể.

### E06 — P2: Một reference-family sweep không chặn mọi trained model

**Vị trí:** `4592–4608`, `4714–4716`.

Không có theorem đảm bảo mọi sufficiently expressive architecture được SGD đưa đến population optimum. Arbitrary learned fields có thể rời atomic reference family; sweep chỉ chặn những families đã đánh giá. Narrow optimizer/regularization sweeps cũng chưa loại các yếu tố ấy nói chung (`4112–4117`).

### E07 — P2: Null score không phải resolution threshold; Sinkhorn không phải W₂

- `4388–4391`, `4747–4755`: mean null discrepancy không phải standard error của paired difference. Một gain nhỏ hơn mean null score vẫn có thể đo được. Muốn nói không phân biệt được cần paired uncertainty hoặc test phù hợp.
- `5199–5203`, `5223–5225`: √S_ε có cùng physical units không làm nó bằng W₂. Giữ notation √S_ε và gọi đúng regularized discrepancy.
- `4452–4457`: pooled rank correlations chỉ cho association, không chứng minh bandwidth “matters only through” n_eff.

### E08 — P3: Summary và caption chưa đồng bộ

`915–919` nói agree từ 5k trở đi nhưng kết quả thực là 31/36 checkpoints với 5 misses. `5618–5620` nói identical/equal training image trong khi residual variance dương. Sửa theo giá trị đã đo và dùng “visually similar/strongly concentrated” khi phù hợp.

## Trích dẫn và phép chuyển từ nguồn sang bài

Source reviewer đã rà đủ **40 cited keys**, tách xác minh metadata khỏi xác minh claim, với tám findings R01–R08 trong `whole_paper_sources_2026-10-17.md`. Những mục trùng E04/M01 được gộp về cùng repair, không đếm như lỗi độc lập.

- **R01, P2:** `106–110`, `3095–3100`: [Smola, §2](https://arxiv.org/html/2605.13386) dùng fixed atoms, query x/t và scale (1−t)/t ở t>0. Scale 1−t của bài mình đúng trên moving centers txⁱ; cần nói rõ hai coordinate conventions khi attribution.
- **R02/R04, P2:** CADS và caption interventions bị đồng nhất với theorem training-label noise; xem E04. [CADS](https://arxiv.org/html/2310.17347) mô tả inference schedule; [Somepalli §7](https://arxiv.org/html/2305.20086) gồm nhiều interventions khác Gaussian training embedding noise.
- **R03, P2:** Zador assumptions và cách diễn giải factor: xem M01–M02. [Bài của Graf–Luschgy–Pagès, §1 và (2.3)](https://numdam.org/item/10.1051/ps:2007044.pdf) cho moment condition và distribution-dependent constant; exact book theorem chưa truy cập toàn văn được.
- **R05, P2:** `83–85`, `2654–2657`, `2700–2704`: [Reu et al. §4](https://arxiv.org/html/2510.18118) không trực tiếp thiết lập external-observation posterior-calibration collapse hoặc remedy resample-x₀ như đang gán. Cần phân biệt CFM construction với external conditioning và ghi nguồn đúng cho từng claim.
- **R06, P2:** `3853–3855`: arbitrary fixed kernel học **large-eigenvalue modes** trước; không phải mọi kernel học Fourier low frequencies trước. Cần thêm stationary/design/spectral ordering assumptions hoặc đổi câu motivation. Formal multiplier proposition đã ghi giả thiết spectrum riêng và vẫn đúng.
- **R07/R08, P3:** original Nadaraya–Watson entries chưa được cite; published Sesmat title có thêm “the”. Đây là provenance/metadata repairs, không phải lỗ hổng của các proof tự suy ra trong bài.

Các so sánh chính với Liu–Zuazua PDE Theorem3.7, mixed-score Theorem3.18/Remark3.19 và các antecedents của risk counterexample có nguồn gốc hỗ trợ. Exact Yoon threshold và theorem-level overlap với Blohm–Garg còn OPEN do OpenReview challenge. Exact AGS2008 text chưa đọc được; proof cơ chế có bản2005 và manuscript có backward-test argument tự đầy đủ. Không tuyên bố toàn bộ metadata/point-of-use claims đã được xác nhận khi report ghi partial/limited.

## Kiểm tra đã thực hiện được

- `scripts/verify_paper_numbers.py`: **368 passed, 0 failed**. Script chủ yếu so hardcoded expected constants với result files và một số substring trong TeX, không parse độc lập mọi numerical claim.
- `scripts/test_calibration.py`: tất cả calibration checks qua với known calibrated, collapsed và overdispersed samplers.
- Independent raw recomputation của **600 exact-field stress rows**: sai khác lớn nhất của mean nearest distance so với recorded metric là `1.5669739×10⁻¹⁰`; final q95 lớn nhất `6.1193695×10⁻⁶`; paired resolution displacement lớn nhất `7.5479686×10⁻¹³`; assignments không đổi.
- Independent aggregation của 10 run JSON trong independent-seed evaluation: means `1.0739273533` và `0.01127746664`; exceedances `317/320` và `164/320`; giữ nguyên sole failed screen `(1004,h=0,condition50)`. Đây là recomputation từ per-condition metrics, không phải tính lại tất cả 640 raw energy statistics.
- Learned-average aggregates và evaluator hash khớp manuscript. Không chạy lại training hay toàn bộ stochastic experiments.
- Source structure: 230 labels duy nhất; không dangling refs hoặc missing bibliography keys; 40 cited entries trong 45 BibTeX entries; 52 includegraphics commands đều có file.

## Build, layout và công cụ cũ

Build độc lập bằng pdflatex/BibTeX trong thư mục audit thành công: **95 trang, main text kết thúc trang 15**, không undefined references/citations và không overfull hbox. Có bốn hyperref warnings bỏ math delimiters khỏi hai appendix bookmarks và các underfull spacing warnings.

Đối chiếu normalized extracted text từng trang giữa PDF canonical và fresh build: **95/95 trang giống nhau**; log tại `tmp/whole-paper-audit-2026-10-17/pdf_source_comparison.json`. PDF metadata Author trống. Điều này kiểm tra provenance/text consistency, không thay thế visual review hay kiểm tra mọi interactive link.

**T01 — P2:** `scripts/check_paper.py` báo pass nhưng đang đọc `paper/main.aux`/`.log` cũ: main kết thúc trang 9, log của PDF 77 trang. Nó không chứng nhận source/PDF hiện tại. Fresh-build aux ghi endmain trang 15. Script còn hardcode ICLR 9-page gate trong khi canonical đang dùng TMLR. Cần cập nhật build provenance và venue gate trước khi dùng như submission check.

**T02 — P3:** `paper/README.md` vẫn ghi ICLR 2027, 7 references và inventory figures cũ; không phản ánh TMLR, 45 bibliography entries hoặc bản hiện tại.

Rendered reader độc lập đã xem **mọi trang 1–95 ở 100 dpi**. Ghi chi tiết trong `whole_paper_render_review_2026-10-17.md`. Các vấn đề cần sửa gồm theorem bị float ngắt, whitespace lớn ở trang 60, plot annotations quá nhỏ ở trang 50/62, image grids nhỏ trang 86–87, header chồng nhau ở Figure 42 trang 88. Không phát hiện clipping toán học ở lượt đọc đó. Không đánh dấu TYPESET-AUDITED khi các vấn đề còn mở.

Không phải mọi nghi vấn của reviewer đều là lỗi: dấu (*) có thật ở Proposition collapse dòng 300; equations 29–33 tồn tại ở statement chính sau các proof restatements. Đây là khó khăn điều hướng, không phải undefined labels. Warnings về missing destinations ở build thử đầu tiên xuất phát từ việc đọc auxiliary cache cũ; đã loại bằng local-first TEXINPUTS rồi build lại, nên không tính chúng là lỗi canonical.

## Hồ sơ, thứ tự sửa và giới hạn

Ledger theo từng formal statement và dependency được lưu tại `whole_paper_statement_ledger_2026-10-17.json`. Source/citation audit và full visual review có báo cáo riêng cùng ngày. Những mục cần sửa được để mở; không nâng trạng thái chỉ vì build qua hoặc numerical checker xanh.

Thứ tự sửa: M01–M05 và E01 trước; sau đó các boundary contracts M06, disclosure E02–E07; cuối cùng đồng bộ captions, build checks và layout. Bất kỳ đổi giả thiết/kết luận nào đều phải ghi old/new contract và re-review consumers, theo skill; không âm thầm làm yếu một phát biểu để đóng finding.

Các proof correctness ở đây là independent reasoning review. Exact prior/novelty comparison còn phụ thuộc nguồn toàn văn truy cập được; metadata đúng không chứng minh claim attribution đúng. Những source hoặc comparison chưa xác minh đủ sẽ được để OPEN trong citation report. Paper chưa được đổi sang format hội nghị, chưa được rút độ dài và chưa có kết luận “đủ tiêu chuẩn chấp nhận”.
