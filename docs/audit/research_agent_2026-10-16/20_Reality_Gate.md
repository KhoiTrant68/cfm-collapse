# Research Reality Gate — 16 October 2026

**Reality verdict: BLOCK** đối với full training/model-sampling campaign mới. Đã hoàn tất audit đọc nguồn, saved-result recomputation, và bounded metric counterexamples. Cho phép tiếp tục chứng minh, sửa phát biểu và kiểm tra measurement offline; chưa có human approval cho full run. **Novelty: REVISE**, độc lập với execution gate.

## Revision và evidence

- Git HEAD: `54f1f9de868894829fdf21c6c13556d76426ccf7`.
- Canonical manuscript: `paper/main.tex`, SHA256 `47c0d29b085263619f61ee967c4bfd7e1c623078c5f0d212631f48b9fb95a0fa` tại lúc kiểm tra. Có Methods edits chưa commit từ yêu cầu trước; audit này không ghi đè chúng.
- [claim_checks.json](claim_checks.json) lưu số đếm, input hashes, counterexamples và access audit. [heldout_family.json](heldout_family.json) lưu 48 rows của phép thử bỏ condition.
- Đã đọc source các formal statements/proofs, `docs/theory/lemma_L1.tex`, `docs/theory/theorem_B.tex`, theory plans, metric implementation, fit scripts, và các results được dẫn dưới đây. Quyết định toán học riêng ở [formalization](06_Math_Formalization.md); novelty ở [literature grounding](05_Lit_Grounding.md).

## Claim ledger

| ID / paper location | Trạng thái | Evidence đã kiểm tra | Điều chưa được chứng minh / smallest repair |
|---|---|---|---|
| C1 `prop:collapse`, `thm:endpoint` | supported trong exact population setting | Explicit trajectory/coupling proof; fresh mathematical packet review | Không suy ra mọi trained network collapse; h=0 ngoài observed labels không định nghĩa canonical extension. |
| C2 `prop:heffid` và synthetic paragraph | partially-supported | 48/48 interval overlap; median log-trace R²=0.8601; 12 runs, 3 seeds | Residual không phải known error bound; 25 derivative evaluations không chứng nhận infimum. Need independent conditioning/error certificate. |
| C3 “one bandwidth describes the network” | partially-supported / universal reading contradicted | CIFAR h=0: 0/18 overlap, median log-trace R²=−193.51; h4:18/18, median .5928; h5:13/18, median .1727; h6:8/18 | Chỉ phát biểu selected regimes, fit moments; exact law cần distributional falsifier. |
| C4 Gaussian là family duy nhất | unverified | New condition-LOO Gaussian vs Laplace wins35/48; h0 wins6/12 | Chênh nhỏ, cùng data, chưa independent holdout. |
| C5 bandwidth predicts calibration | partially-supported | Synthetic local Gaussian proxy R²=.90015 across75 checkpoints; incremental ΔR²=.03885, CI[−.036,.216] trong `audit_incremental_r2.json` | Không có reliable gain ngoài baseline miễn phí; actual heterogeneous atoms không thỏa iid fixed-weight model. |
| C6 bandwidth sets image calibration | contradicted như universal claim | `results/exp3/_rerun/calib_image_summary.json`: Spearman h_eff .627 vs raw spread .979; joint32 coverage .469–.766 ở9positive-h60krows | Không chuyển synthetic conclusion sang images. |
| C7 Gaussian RSE bound distribution-free | contradicted | Bernoulli(.001), M128: exact relative SE2.7909 vs claimed Gaussian ceiling.12549 | Add Gaussian hypothesis or fourth-moment formula; bootstrap không tự sửa heavy-tail guarantee. |
| C8 deterministic midrank exact uniform under calibrated sampling with ties | contradicted | Calibrated point mass: every rank=.5, coverage1; tie-free reference59/65=.90769 | Randomized ties + exchangeable score construction. Không kết luận archived CIFAR sai do ties khi chưa đo ties. |
| C9 NW expected bias/variance under current local design assumptions; `eq:lgbias` | contradicted as written | Heavy-tail counterexample; empirical ratio differs population ratio | Separate μ_h^∞ and empirical estimator; add global integrability/denominator control before expected-risk rates. |
| C10 KGF = positive NW kernel | contradicted as universal identity | Theorem G; `results/theory/t1_equivalent_kernel.json` signed filters and failed high-resolution positive-NW fidelity | Retain spectral scale as idealization, finite moment fit as observation. |
| C11 fixed NTK explains actual network dynamics | unverified | `results/theory/e3_ntk_label.json`: normalized NTK change .68–1.23 for h≤.1 | Fixed-kernel surrogate is not a verified causal mechanism. |
| C12 regularization/LR explains floor above h | unverified | `results/exp1/_heff/e2_floor_compare.json`; no decisive predicted floor across3seeds | Small Lipschitz lower bound cannot rule out architecture error; new sharp theorem describes a larger function class. |
| C13 endpoint smoothing gain ≤ removed atom obstruction | contradicted | Addendum Counterexample: obstruction0, W₂² improvement2/π; continuous/positive-weight perturbations preserve contradiction | Keep nearest-atom lower bound, delete upper-bound inference. |
| C14 h and ρ always match posterior mean/covariance | contradicted as unrestricted guarantee | Necessary/sufficient moment equations in addendum | State existence conditions; isotropic covariance deficit required. |
| C15 averaged-label convergence and a.s. atomicity | supported by new proofs V/A, review ledger in formalization | Normalized log-partition Lyapunov; finite critical set; Jacobian-volume argument | Non-atom tie limits possible only on a null basin for an absolutely continuous source. Không suy ra learned field. |
| C16 hard CFG w≥0 endpoint = conditioned atom | supported by new theorem H | Entropy inequality gives explicit ε²log(1/ε) bound | Exact fields only; positive-bandwidth case được đóng riêng bằng B, không suy trực tiếp từ H. |
| C17 positive-bandwidth CFG convergence/a.s. atomicity | supported by new theorem B | Signed log-partition finite energy; weighted covariance identity; Jacobian/Fatou | Fixed finite w≥0, distinct atoms, positive conditional weights, absolutely continuous source; endpoint weights not identified. |

## Measurement and access certificates

`scripts/test_calibration.py` passed its existing continuous Gaussian checks (max deviations pixel/PC/joint .004/.011/.048), collapse and overdispersion controls. These do not test ties. Mathematical counterexamples above show which additional controls are required, not whether a particular archived row is biased.

Synthetic checkpoints and `results/exp1/_heff/family_stats.npz` are accessible locally. Twelve inspected CIFAR DDPM run directories contain **zero local checkpoint files**. The historical remote listing in `results/exp3/_heff/env.txt` is not confirmation of current access. Smaller image-model checkpoints cannot substitute for the 35.75M model without changing the claim.

`src/train_exp3.py` uses Euler50 with terminal ε=.001; low-dimensional sampling uses RK4. Off-atom image samples cannot be assigned solely to learned spatial error before a matched-source step-size/terminal-time convergence check.

## Decision and learning value

The exact empirical-flow backbone remains useful. The new proofs strengthen narrow population statements and expose which network interpretations remain hypotheses. Current evidence supports studying bandwidth as a descriptive diagnostic. It does not support a universal Gaussian NW law or a verified mechanism for the trained-network floor.

Owner of corrective work: agent/researcher in this repository. Acceptance: corrected measurement contracts and null controls, accessible exact checkpoints, frozen held-out contrast and bounded timing pilot. Maximum next-step cost: offline checks plus a five-minute loading/timing smoke; stop on missing checkpoint, metric-null failure, nonfinite outputs, or model/config mismatch. Do not launch a broad training grid before the branch is reopened. The [future protocol](23_Feasibility_Pilot_Protocol.md) states measurable acceptance and kill conditions; it has not been executed.
