# Field Analysis Report — Phase 0 (review panel, 5/11/2026)

## Thông tin cơ bản
- **Tiêu đề**: Atomic Endpoints of Averaged and Guided Empirical Conditional Flows
- **Abstract**: khoảng 260 từ
- **Phần chính ICLR**: khoảng 6.300 từ trong 9 trang; toàn bộ bản ICLR khoảng 34.000 từ (50 trang, kể cả phụ lục)
- **Số tài liệu tham khảo**: 39
- **Bản được review**: `paper/main_iclr.tex` → `paper/main_iclr.pdf` (ICLR 2027), nội dung chuẩn ở `paper/main.tex` (TMLR); commit baf15b8 cộng các thay đổi trong docs

## Phân tích lĩnh vực

| Chiều | Kết quả |
|---|---|
| Lĩnh vực chính | Machine learning, lý thuyết generative models (flow matching, diffusion, memorisation) |
| Lĩnh vực phụ | Hệ động lực và ODE (basin, hyperbolic fixed points, Liouville); thống kê phi tham số (Nadaraya–Watson); xác suất (weak limits of endpoint laws) |
| Paradigm | Lý thuyết là chính, kèm thực nghiệm số |
| Loại phương pháp | Chứng minh toán học (định lý về exact field); tính số các trường exact; thí nghiệm huấn luyện mạng nhỏ (MLP, d ≤ 10) và một DDPM U-Net trên CIFAR-10 |
| Venue mục tiêu | ICLR 2027 (main track, conference paper), do tác giả chọn; TMLR là bản chuẩn thay thế. `criteria_binding_unavailable`: chưa có Target Criteria Brief chính thức, nên panel không khẳng định khớp tiêu chí venue ngoài các chuẩn chung của ICLR |
| Độ hoàn thiện | Pre-submission: cấu trúc đầy đủ, có phụ lục chứng minh, có kiểm số tự động (699 kiểm tra), có hai bản build sạch |

## Review Strategy Recommendations
- Bài dài và dày định lý. Phần chính dồn nén, còn nhiều chứng minh và thí nghiệm nằm trong phụ lục. Reviewer ICLR thường chỉ đọc 9 trang, nên phải đánh giá xem phần chính có đứng vững một mình không.
- Có nhiều chứng minh mới viết gần đây (Prop 5.3 viết trong session này; Prop 4.7 và phần spectral). Panel đánh giá phát biểu và cách dùng các kết quả, không thay cho việc tác giả kiểm lại chứng minh.
- Căng thẳng dễ thấy: theory reviewer (R1) sẽ hỏi độ chặt của giả thiết; ML-practice reviewer (R3) sẽ hỏi "so what" cho các sampler thật. Synthesizer cần cân hai phía.
- Một số chi tiết tự nêu dễ bị hiểu nhầm (ví dụ "a.s." và null set có thể là hyperplane, hay "consistent with" trong phần thực nghiệm). Devil's Advocate nên thử các chỗ này.

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Area Chair ICLR nhiều năm ở mảng generative models và lý thuyết diffusion/flow matching, từng chair các phiên về memorisation và generalisation của diffusion models.
**Review Focus**:
  1. Đóng góp chính có rõ trong 9 trang không: câu hỏi "can interventions move endpoints off the training set" có đáng để cộng đồng ICLR quan tâm không.
  2. Mức độ mới so với các kết quả memorisation đã biết của empirical minimiser (Pidstrigach, Gu et al., Kamb & Ganguli, Baptista et al., Bertrand et al., Liu & Zuazua).
  3. Bài có dễ đọc với người đọc ICLR không: phần chính có tự đứng được không, hay phải nhảy sang phụ lục liên tục.
**Will particularly care about**: Có một "headline" rõ cho cộng đồng ML (ví dụ: guided label averaging có ngưỡng chính xác 1/sinh²B và nó xuất hiện cả trên CIFAR) hay chỉ là chuỗi định lý kỹ thuật.
**Possible blind spots**: Có thể không kiểm từng bước chứng minh; có thể đánh giá thấp giá trị của các kết quả âm và phủ định.

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1 — Methodology (toán học và tính số)
**Identity Description**: Nhà toán học ứng dụng chuyên về non-autonomous ODE và dynamical systems (stable/unstable manifolds, Carathéodory solutions, Liouville/Grönwall), có kinh nghiệm review các bài lý thuyết diffusion cho COLT/ICML.
**Review Focus**:
  1. Độ chặt của phát biểu định lý và giả thiết: Theorem 4.1, 4.5, 4.6, 4.7, Theorem 5.1, Proposition 5.3; điều kiện "null set", "a.s.", "hyperbolic profile", face condition.
  2. Khung chứng minh hai bước (convergence + null basins qua Liouville và Fatou): có lỗ hổng ở t → 1, ở schedule có bounded variation, ở Proposition 5.3(b) không.
  3. Tính số: các thí nghiệm exact field có thật sự hỗ trợ phát biểu không (stiff solver, hand-off, sensitivity, chỉ "finite-time").
**Will particularly care about**: Định lý có chứng minh nhiều hơn những gì nó phát biểu không, và các kết quả số có được trình bày như bằng chứng cho định lý hay chỉ là consistency check.
**Possible blind spots**: Có thể ít quan tâm tới venue fit và ý nghĩa thực tiễn; có thể chấp nhận giả thiết mạnh nếu chứng minh đúng.

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2 — Domain (diffusion/flow matching memorisation)
**Identity Description**: Nhà nghiên cứu về memorisation và generalisation trong diffusion và flow-matching models, quen thuộc với closed-form/empirical-optimal denoisers, classifier-free guidance và các nghiên cứu memorisation ở image scale (Carlini, Somepalli, Kadkhodaie, Kamb & Ganguli).
**Review Focus**:
  1. Literature coverage và positioning: kết quả nào đã biết (Nadaraya–Watson endpoint, empirical memorisation), kết quả nào thật sự mới (composition threshold, spectral criterion, transfer, Prop 5.3).
  2. Mức liên quan của setting (exact empirical conditional field, Gaussian label noise, label averaging, CFG) với sampler thật; idealisation "label averaging = coarse label resolution" có hợp lý không.
  3. Thực nghiệm: EXP-1/2/3, CIFAR-10 U-Net, learned composition và ablation; các kết luận có vượt quá dữ liệu không.
**Will particularly care about**: Bài có giải thích được hiện tượng quan sát được ở các model thật (off-atom samples, CFG gây memorisation) hay chỉ xử lý một đối tượng lý tưởng hoá.
**Possible blind spots**: Có thể không đánh giá hết độ khó kỹ thuật của các chứng minh.

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3 — Cross-disciplinary (nonparametric statistics / privacy and practice)
**Identity Description**: Nhà thống kê phi tham số chuyên về kernel smoothing và statistical learning theory, đồng thời làm về privacy/memorisation audit cho generative models trong thực tế.
**Review Focus**:
  1. Cách đọc thống kê: endpoint law là Nadaraya–Watson, label bandwidth h và kernel tracking; giới hạn của "matching moments ≠ posterior"; liên hệ với bias–variance và bandwidth selection.
  2. Ý nghĩa thực tiễn: kết quả nói gì cho privacy (training-data extraction), cho người dùng CFG và guidance schedule, cho thiết kế input/parametrisation của mạng.
  3. Giả định ngầm: label nhận dạng (identifying labels), số atom hữu hạn, linear interpolant; điều gì thay đổi khi dữ liệu lớn hoặc label chia sẻ.
**Will particularly care about**: Hệ quả có thể kiểm tra được ngoài bài toán đồ chơi, và bài có nói quá về tầm áp dụng không.
**Possible blind spots**: Có thể không quen với các chi tiết của ODE và flow-matching training.

## Ghi chú
- Seat thứ năm là Devil's Advocate cố định, không có card.
- Không phát hiện chỉ dẫn nào trong manuscript nhắm vào reviewer.
