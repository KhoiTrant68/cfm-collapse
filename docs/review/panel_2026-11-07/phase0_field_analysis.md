# Field Analysis Report — Phase 0 (review panel, 7/11/2026)

## Thông tin cơ bản
- **Tiêu đề**: Atomic Endpoints of Averaged and Guided Empirical Conditional Flows
- **Bản được review**: `paper/main_iclr.tex` → bản build ICLR 2027 (53 trang, phần chính kết thúc ở trang 9), nội dung chuẩn ở `paper/main.tex` (TMLR, 54 trang); commit 7679050
- **Số tài liệu tham khảo**: 40
- **Thay đổi so với panel 5/11** (các commit cd088cc → 7679050): đưa headline lên đầu và đọc định lý composition như một kết quả tồn tại; so sánh với Liu & Zuazua theo từng phát biểu; Prop. bottleneck mới; luật tuyến tính gần ngưỡng (luật hình thức); CIFAR sensitivity cho cả tám cặp; thí nghiệm bottleneck và input lệch tie trên tam giác; ablation tam giác; nói rõ U-Net off-atom chưa được giải thích. Verifier báo 762 kiểm tra đúng.

## Phân tích lĩnh vực

| Chiều | Kết quả |
|---|---|
| Lĩnh vực chính | Machine learning, lý thuyết generative models (flow matching, diffusion, memorisation) |
| Lĩnh vực phụ | Hệ động lực và ODE (basin, hyperbolic fixed points, Liouville, tiệm cận gần ngưỡng); thống kê phi tham số (Nadaraya–Watson); xác suất (weak limits of endpoint laws) |
| Paradigm | Lý thuyết là chính, kèm thực nghiệm số |
| Loại phương pháp | Chứng minh toán học về exact field; tính số exact field; huấn luyện mạng nhỏ (MLP, d ≤ 10); DDPM U-Net và exact field trên CIFAR-10 |
| Venue mục tiêu | ICLR 2027 (main track), do tác giả chọn; TMLR là bản thay thế. `criteria_binding_unavailable`: chưa có Target Criteria Brief chính thức, nên panel không khẳng định khớp tiêu chí venue ngoài các chuẩn chung của ICLR |
| Độ hoàn thiện | Pre-submission, bản sửa lần hai: cấu trúc đầy đủ, có phụ lục chứng minh, kiểm số tự động, hai bản build sạch |

## Review Strategy Recommendations
- Đây là vòng review thứ hai trên cùng bài. Panel này là một full review mới, không phải re-review theo hợp đồng ba cổng: các reviewer không được xem báo cáo 5/11. Synthesizer có thể so kết quả với panel cũ sau khi các seat đã commit.
- Có ba phần toán mới mà tác giả chưa kiểm: Prop. bottleneck, luật gần ngưỡng (ghi là luật hình thức) và Prop 5.3. Panel đánh giá phát biểu và cách dùng, không thay cho việc tác giả kiểm chứng minh.
- Thực nghiệm mới có cả kết quả âm (input lệch tie, biến thể đặt tâm ở atom bị dừng vì không đánh giá được, endpoint không đáng tin ở guidance lớn). Reviewer cần xét xem các kết quả này được trình bày trung thực hay làm yếu thông điệp chính.
- Căng thẳng dễ thấy vẫn như vòng trước: R1 hỏi độ chặt của giả thiết; R3 hỏi "so what" cho sampler thật, nhất là sau khi bài thừa nhận composition chỉ học được khi mạng biết tie nằm ở đâu.

## Reviewer Configuration Cards

### Reviewer Configuration Card #1

**Role**: EIC
**Display role**: Journal-Fit Reviewer
**Identity Description**: Area Chair ICLR nhiều năm ở mảng generative models và lý thuyết diffusion/flow matching, từng chair các phiên về memorisation và generalisation của diffusion models.
**Review Focus**:
  1. Headline trong 9 trang có rõ và có đáng quan tâm với cộng đồng ICLR không, sau khi bài được đóng khung lại thành kết quả tồn tại.
  2. Mức độ mới so với các kết quả memorisation đã biết của empirical minimiser (Pidstrigach, Gu et al., Kamb & Ganguli, Baptista et al., Bertrand et al., Liu & Zuazua), nhất là phần so sánh mới với Liu & Zuazua.
  3. Phần chính có tự đứng được không, hay phải nhảy sang phụ lục liên tục.
**Will particularly care about**: Một reviewer ICLR có rút ra được một điều mới, kiểm được, cho sampler thật không, hay chỉ thấy một chuỗi định lý kỹ thuật về một đối tượng lý tưởng hoá.
**Possible blind spots**: Có thể không kiểm từng bước chứng minh; có thể đánh giá thấp giá trị của các kết quả âm.

### Reviewer Configuration Card #2

**Role**: Peer Reviewer 1
**Display role**: Peer Reviewer 1 — Methodology (toán học và tính số)
**Identity Description**: Nhà toán học ứng dụng chuyên về non-autonomous ODE, dynamical systems và matched asymptotics (stable/unstable manifolds, Carathéodory solutions, Liouville/Grönwall, boundary layers), có kinh nghiệm review các bài lý thuyết diffusion cho COLT/ICML.
**Review Focus**:
  1. Độ chặt của phát biểu và giả thiết: Theorem 4.1, 4.5–4.7, Theorem 5.1, Prop 5.3 và Prop. bottleneck mới; các điều kiện "null set", "a.s.", "hyperbolic profile".
  2. Luật gần ngưỡng: phép đổi biến, phương trình Bernoulli, giá trị separatrix C* = 1; chỗ nào cần chặn để nâng luật hình thức thành định lý; bài có trình bày nó đúng mức không.
  3. Tính số: stiff solver, hand-off, sensitivity CIFAR, solver disagreement trong các lần chạy học được; các kết quả số được trình bày như bằng chứng hay chỉ là consistency check.
**Will particularly care about**: Định lý có phát biểu nhiều hơn những gì chứng minh cho phép không, và mọi kết luận suy từ số có đủ kiểm soát sai số không.
**Possible blind spots**: Có thể ít quan tâm tới venue fit và ý nghĩa thực tiễn; có thể chấp nhận giả thiết mạnh nếu chứng minh đúng.

### Reviewer Configuration Card #3

**Role**: Peer Reviewer 2
**Display role**: Peer Reviewer 2 — Domain (memorisation trong diffusion/flow matching)
**Identity Description**: Nhà nghiên cứu về memorisation và generalisation trong diffusion và flow-matching models, quen với closed-form/empirical-optimal denoisers, classifier-free guidance, và các giải thích kiểu patch-mosaic/locality (Kamb & Ganguli, Niedoba et al., Kadkhodaie et al., Carlini, Somepalli).
**Review Focus**:
  1. Positioning và literature: kết quả nào đã biết, kết quả nào thật sự mới; phần trích Niedoba et al. mới thêm có đúng và đủ không.
  2. Setting có liên quan tới sampler thật không: label averaging, label bottleneck, CFG; việc composition chỉ học được với input đặt tâm tại tie làm hẹp tầm áp dụng tới đâu.
  3. Thực nghiệm: EXP-1/2/3, CIFAR-10 (exact composite và U-Net), learned composition, ablation và bottleneck; kết luận có vượt dữ liệu không.
**Will particularly care about**: Bài có giải thích được off-atom samples và tác động của CFG ở model thật không, hay chỉ xử lý exact field.
**Possible blind spots**: Có thể không đánh giá hết độ khó kỹ thuật của các chứng minh.

### Reviewer Configuration Card #4

**Role**: Peer Reviewer 3
**Display role**: Peer Reviewer 3 — Cross-disciplinary (thống kê phi tham số / privacy và thực hành)
**Identity Description**: Nhà thống kê phi tham số chuyên về kernel smoothing và statistical learning theory, đồng thời làm privacy/memorisation audit cho generative models trong thực tế.
**Review Focus**:
  1. Cách đọc thống kê: endpoint law kiểu Nadaraya–Watson, label bandwidth h, bottleneck như một phép lượng tử hoá nhãn; "matching moments ≠ posterior".
  2. Ý nghĩa thực tiễn: điều gì kiểm được cho privacy (training-data extraction), cho người dùng CFG và guidance schedule; ngưỡng 1/sinh²B và luật tuyến tính có dùng được làm chẩn đoán không.
  3. Giả định ngầm: label nhận dạng, số atom hữu hạn, linear interpolant, việc biết vị trí tie; điều gì thay đổi khi dữ liệu lớn hoặc label chia sẻ.
**Will particularly care about**: Hệ quả kiểm được ngoài bài toán đồ chơi, và bài có nói quá tầm áp dụng không.
**Possible blind spots**: Có thể không quen với chi tiết ODE và huấn luyện flow matching.

## Ghi chú
- Seat thứ năm là Devil's Advocate cố định, không có card.
- Không thấy chỉ dẫn nào trong manuscript nhắm vào reviewer.
