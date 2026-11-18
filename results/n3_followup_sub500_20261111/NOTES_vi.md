# Kết quả sub500 (2026-11-16)

Model: EDM cond ddpmpp, 500 ảnh CIFAR-10 (50/lớp), 10 Mimg, batch 128, chạy lại trên GPU 3 từ
2026-11-15 13:38 UTC (lần đầu bị kill ở 4354 kimg). Snapshot: network-snapshot-010000.pkl.
Train: results/n3_edm_sub500_20261115/. Follow-up: thư mục này (tên giữ ngày 20261111).

## Memorization (N3, n = 1000)
- Off-atom 4,1% → model memorize 95,9% mẫu. Field exact: 0% off-atom.
- Trong các mẫu on-atom, network chỉ trùng ảnh với field exact 35,8%: network memorize nhưng chọn ảnh khác.
- AUC theo t: e_learned lên 0,885 ở t = 0,11, 0,974 ở t = 0,16, ≥ 0,999 từ t = 0,34. nn_hat (baseline ảnh gần nhất)
  lên nhanh hơn hoặc bằng ở mọi t (0,959 ở t = 0,11; 1,000 từ t = 0,34). e_exact ~0,52–0,68, cond_diff ≤ 0,79.
- Lưu ý: chỉ 41 mẫu off-atom.

## Swap (n = 500; learned off-atom 3,8%)
- Net→exact on-atom ở mọi s. Trùng ảnh với network (=L): 92,8% (s = 5), 98,2% (s = 2), 99,6% (s = 1), 100% từ s ≤ 0,2.
  So với model public (31/56/90%): network memorize chọn ảnh sớm hơn nhiều.
- Exact→net on-atom ở mọi s, giữ ảnh của field exact (=E ≥ 95,4%), endpoint cách endpoint network ~27.
  Median d1 giảm 1,67 → 0,45 khi s giảm 5 → 0,02: network không kéo về sát ảnh sau khi nhận tay.

## μ và ρ (n = 200, 13 mẫu off-atom)
| σ | median μ off / on | tỉ lệ μ<1 off / on | AUC μ | median ρ off / on |
|---|---|---|---|---|
| 1.923 | 2.37 / 0.58 | 23% / 95% | 0.863 | −11.8 / −2.1 |
| 0.585 | 1.12 / 1.02 | 38% / 34% | 0.641 | −0.68 / −0.52 |
| 0.140 | 1.16 / 1.13 | 0% / 6% | 0.716 | −0.10 / −0.07 |
| 0.023 | 0.96 / 0.96 | 85% / 99,5% | 0.519 | 0.061 / 0.060 |
| 0.002 | 0.96 / 0.96 | 100% / 100% | 0.466 | 0.042 / 0.040 |
Field exact: μ* = 0 ở mọi σ trong bảng.

## Đối chiếu dự đoán
- Khớp: net→exact luôn on-atom; exact→net giữ on-atom; μ* = 0.
- KHÔNG khớp: dự đoán mẫu memorize có μ < 1 ở cuối còn mẫu off-atom có μ ≥ 1. Thực tế ở cuối (σ ≤ 0,023) cả hai nhóm
  đều μ ≈ 0,96 và ρ ≈ 0,04–0,06, AUC ~0,5. Tách nhóm chỉ xuất hiện ở σ ≈ 1,9 (AUC 0,86), đúng giai đoạn chọn ảnh.
- ρ ≈ 0,04 nghĩa là λ_max(sym J_D) ≈ 0,96: hướng co yếu nhất gần như không co. [sửa 2026-11-16] ρ chỉ cho mức co
  TỐI THIỂU được đảm bảo (~10% từ σ = 0,023 xuống 0,002), không chặn mức co tối đa. Mức co tối đa do λ_min quyết định:
  median μ_min on-atom 0,089 (σ = 0,023) và 0,60 (σ = 0,002), tức λ_min ≈ 0,09 và 0,60, nên có những hướng co mạnh.
  Khoảng cách tới ảnh co theo thương Rayleigh dọc hướng x − x^i (nằm giữa λ_min và λ_max), chưa được đo.
- Hệ quả: μ (hướng xấu nhất) không phân biệt on/off ở cuối, nhưng điều đó chưa nói được landing có nhờ co muộn hay không.
  Cần đo hệ số co theo hướng tới ảnh. Tách nhóm rõ nhất ở σ ≈ 1,9 (giai đoạn chọn ảnh).
- [2026-11-17, đo q theo Prop. E, results/n3_q_20261117/Q_SUMMARY.md] Landing CÓ xảy ra muộn, theo hướng tới ảnh:
  log|x − x¹| giảm −2,01 (σ 1,09 → 0,14) và −1,54 (σ 0,14 → 0,002) ở mẫu on-atom, so với −0,91 và −0,05 ở mẫu off-atom.
  q₁ on-atom ≈ 0,22 ở σ 0,30–0,14 (off 0,53–0,76); AUC q₁ = 0,97 ở σ = 1,09, ≥ 0,99 từ σ = 0,59, 1,000 ở σ 0,14–0,023.
  μ (λ_max tại x) không thấy điều này. Model public: q₁ → 1 từ σ ≈ 0,06 và log n₁ chỉ giảm −0,07 ở cửa sổ cuối (không landing).
- [2026-11-17, đo ϱ theo Định lý T1, results/n3_rho_20261117] Mẫu on-atom có ϱ = |D − m*|/|x − x¹| < 1 ở mọi bước
  (median 0,19 ở σ 0,14; 0,73 ở σ 0,023); off-atom và model public có ϱ → 1 từ σ ≈ 0,14. AUC ϱ = 1,000 ở σ ≤ 1,09.
  Tỉ số hướng tâm rad₁ dự đoán đúng thay đổi của log|x − x¹| (−2,01 so với −2,01; −1,60 so với −1,54).
  Lưu ý: q₁ cầu phương 4 điểm của lần đo trước bị thổi phồng ở σ 0,1–1; độ dốc cát tuyến thật của mẫu on-atom ≈ 0,02–0,06.
- [2026-11-17, chứng chỉ Định lý T3 cho sampler Heun, results/n3_t3_20261117] Chặn c_k·n_k + b_k không bị vượt
  ở bước nào (1500 quỹ đạo × 17 bước). ϱ tại điểm dự đoán x̃_k luôn lớn hơn tại x_k (≈ ϱ ở mức σ kế tiếp) nên
  nó là điểm quyết định. Chứng chỉ (c_k < 1) phủ ≥ 99,7% mẫu on-atom ở bước 0–13 (σ ≥ 0,14), 47% ở bước 14,
  0% ở bước 15–16. Ở đó chặn > 1 trong khi hệ số co thực là 0,58 / 0,81 / 0,95. Mẫu off-atom và model public
  có hệ số ≈ 1 từ σ ≈ 0,06.
- [2026-11-17, ablation số bước Heun, results/n3_steps_20261117] Với 36 và 64 bước, mọi r_k ≥ 1/2 nên chứng chỉ
  T3 phủ mọi bước cho 99,5% mẫu on-atom (18 bước: 0%). Tỉ lệ memorize (off-atom 4,1 / 4,0 / 3,9%) và ảnh được
  chọn (99,3–99,4% trùng với 18 bước) không đổi. Đây là dự đoán của T3 được xác nhận trên dữ liệu.
- [2026-11-17, neo dự báo + bootstrap, results/n3_anchor_20261117 và results/n3_robust_20261117/ROBUSTNESS.md]
  ϱ neo vào ảnh gần nhất của D(x_k) (không dùng endpoint) cho AUC trùng với neo endpoint; ảnh neo trùng ảnh
  endpoint 90% (σ 8,4), 97% (σ 5,3), ≥ 99,4% từ σ ≤ 3,3. e_learned thua nn_hat có ý nghĩa ở σ 3,3–19,4
  (−0,074 [−0,099, −0,049] ở σ 8,4). radA thắng nn_hat ở σ 19,4 (+0,106 [0,056, 0,159]), ngang ở 12,9, thua nhẹ
  ở 5,3–8,4. Kết quả không đổi với ngưỡng off-atom 0,2 / 1/3 / 0,5.
- [2026-11-18, sub2000 s0 và sub500 s1, results/n3_edm_sub{2000,500s1}_2026111*, results/n3_rho2_20261118]
  sub500 s1: off-atom 4,4% (lặp lại 4,1% của s0); mọi kết luận ϱ, AUC, chứng chỉ T3 giống s0.
  sub2000: off-atom 50,1% (chế độ cân bằng). Model sub1000 cũ (100% off-atom) gần như chắc chưa train đủ.
  Ở sub2000, câu "ϱ < 1 ở mọi bước với on-atom, ϱ → 1 với off-atom" KHÔNG còn phân biệt: 99,8% mẫu off-atom cũng
  có ϱ < 1 ở mọi bước, và median on-atom cũng lên 0,997 ở bước cuối. Khác biệt nằm ở MỨC CO TÍCH LŨY
  ∫(1 − ϱ) d log σ trên cửa sổ muộn σ 0,59 → 0,002: on 1,75 so với off 0,68, AUC 0,983 (baseline ảnh gần nhất 0,985).
  ϱ tại từng σ: AUC 0,99 ở σ 0,59, giảm còn 0,93 ở σ 0,002. Chứng chỉ T3: 0 vi phạm; phủ 100% on-atom tới bước 12,
  89% bước 13, 0% từ bước 14.
  Hệ quả cho paper: phải viết lại các câu ở abstract và Mục 6.3 theo mức co tích lũy (đúng đại lượng của định lý),
  không theo "ϱ < 1 tại mọi bước".
- Rủi ro reviewer: e_learned không dự đoán memorization tốt hơn baseline ảnh gần nhất (nn_hat ≥ e_learned ở mọi t).

Task n3-sub500-results có thể tắt.
