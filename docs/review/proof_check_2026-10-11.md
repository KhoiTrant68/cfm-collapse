# Proof check, 2026-10-11 (math-olympiad adversarial protocol)

- **Scope**: the proofs behind the main-text claims of `paper/main.tex` at `602eb2d`, and two
  proofs the main-track plan needs (`docs/plan/main_track_plan_2026-10-11.md` §6).
- **Protocol**: each bundle was given, as LaTeX statements and proofs with the macro file
  and the setup, to three independent fresh-context verifiers.
  - The three used different attacks: general adversarial; one-line-lemma extraction with
    2×2 counterexamples plus hypothesis re-checks; and a consecutive-pass trace.
  - Verifiers made one Read of their bundle, ran no computation, and did not see each
    other's verdicts.
  - Rule: two holes refute; four holds confirm. With three verifiers per bundle, nothing is
    yet *confirmed* in the skill's sense: a fourth pass is pending for every result that
    held 3/3.
- **Bundles**: A endpoint chain, B `prop:heffid`, C `thm:calib`, D `prop:specbias` and
  `prop:filtered`, E `prop:prop17` and `prop:tgtnoise`, F the new positivity lemma L1,
  G the draft statement T2 (attacked as a statement; no proof exists).

## Verdicts

C = correct, G = gap, I = incorrect. "Refuted" means two or more verifiers found the same
hole. Every refutation below is a fixable gap in the statement or the proof, not a false
theorem, except T2.

| Bundle | Result | V1 | V2 | V3 | Outcome | Fix |
|---|---|---|---|---|---|---|
| A | `prop:collapse`, `lem:cov`, `lem:wellposed`, `lem:mixture-coupling`, `prop:kernel-field`, `thm:endpoint`, `cor:zerobw`, `prop:moments` | C | C | C | holds 3/3 | wording only: `cor:zerobw` "recovers (d)"; `prop:moments` "for any h>0"; `lem:wellposed`(c) leaves the backward-flow/compact-support step implicit (valid by linear growth) |
| A | `cor:infbw` | G | G | G | **refuted** | the proof shows p₁^{(h)} ⇒ ρ̂_X but never that p₁^{unc} = ρ̂_X. One sentence: the unconditional field is the mixture-coupling field with I ~ Unif, so the argument of `thm:endpoint` applies verbatim |
| A | `prop:atomicity` | C | C (cosmetic) | G | holds, one citation missing | the h=0 case must cite `prop:collapse`(d); `thm:endpoint` covers h>0 only |
| B | `prop:heffid`: derivative identities, large-h limit, stability bound | C | C | C | holds 3/3 | define T (log T = F(h_true)+e); e also denotes the exponential |
| B | grid parenthetical in the proof ("replace e by the misfit at the grid point nearest h∘") | G | G | G | **refuted** (two independent counterexamples) | recentre at the grid point g: \|ĥ−h_true\| ≤ 2\|e′\|/κ + \|g−h_true\| |
| B | "likewise for h_mean" | G | C | C (caveat) | holds once the norm is fixed | h_mean minimises a sum of per-condition norms; state the bound with ∑_c\|e_c\| (ℓ₂,₁ ≥ ℓ₂, so the MVT step goes through) |
| C | `thm:calib`(a) | C | C | C | holds 3/3 | "almost surely, for each fixed y" |
| C | `thm:calib`(b) | C | G | C | holds; hypotheses to state | "level-α" must mean exact coverage α; exact regions need an atomless posterior (fails for priors with atoms); {(x,y): x∈R(y)} jointly measurable |
| C | `thm:calib`(c) strictness | G | G | G | **refuted** (non sequitur) | "strict on an event meeting {χ²>q}" does not imply Pr(∑λg² ≤ q < ∑g²) > 0. One line: an open neighbourhood of c·e_j with c² ∈ (q_α, q_α/λ_j); requires α ∈ (0,1) |
| C | `thm:calib`(d) | C (caveat) | G | G | **refuted as stated** | needs weights fixed (independent of the atoms) and nonnegative; x* absolutely continuous and independent of the atoms; "the region" defined. Counterexample to n_eff=1 ⇒ one weight is 1: w = (2/3, 2/3, −1/3) |
| D | `prop:specbias`(a), `prop:filtered`(a), (b) | C | C | C | holds 3/3 | `filtered`(b): add the line from a.s. trajectory convergence to the endpoint law; the conclusion is conditional on convergence ("never moves them" is stronger than proved) |
| D | `prop:specbias`(b) | G | G | G | **refuted as stated** | assumes a stationary kernel without saying so; for ζ ≥ 1 no kernel function has spectrum a\|ω\|^{-ζ} (T_k is an unbounded multiplier); f⋆−c ∉ L²(ℝ). Restate: T_k the positive self-adjoint multiplier on L²(ℝ), f⋆−c ∈ L² |
| E | `prop:prop17` algebra (field, flow, s₁ = 0 endpoint) | C | C | C | holds 3/3 | — |
| E | `prop:prop17` framing as a population minimiser | C (caveat) | G | G | **refuted** | with γ = σ√(t(1−t)), ∫γ̇² = ∞, so E[Var(U\|X_t,t,Y)] = ∞ and L_σ(v) = ∞ for every v; `prop:projection` does not apply. Use the centred loss E\|v\|² − 2E⟨Ẋ_t,v⟩ (finite, same conditional-mean minimiser), or a schedule with γ̇ ∈ L² such as σt(1−t) |
| E | `prop:tgtnoise` (field, endpoint law, moments) | C | C | C | holds 3/3 | x̄ overloaded (data mean vs endpoint mean) |
| F | **L1** positivity (k=1, exponential kernel) | C | C | C | holds 3/3 | Remark: "(k+1)/2 fractional" is false for odd k (write "order (k+1)/2 > 1"); "signed weights expected for k ≥ 2" is a conjecture: at N=2 the weights are nonnegative in every dimension (triangle inequality), so any counterexample needs N ≥ 3 |
| G | **T2** draft statement | false | false | — | **false as written** | see below |

## T2: why the draft is false, and what is true

Both attackers, high confidence:

1. **Atoms in s(X) break the two-sided bound.** With π = ½δ₋₁ + ½δ₊₁, s = id and α = 0.3,
   coverage → ≥0.997 while the right-hand side → 0. Closed central intervals of an atomic
   law over-cover. Only the one-sided bound coverage ≥ α − (terms) survives without an
   atomless conditional law.
2. **ρ_min cannot hold.** Y has full support, so inf ρ_Y = 0. Use a bounded set A and add
   Pr(Y ∉ A).
3. **C₁Lh² double-counts and has the wrong units.** With a Gaussian kernel and Gaussian
   noise, the NW population limit is exactly π_h(·|y), so τ_h is the whole bias. Under
   rescaling y → cy, the term L h² scales like c while everything else is invariant.
   Merely Lipschitz F would give O(Lh√k), not h².
4. **1/(2n_eff) is the wrong discreteness term**, and n_eff (random, y-dependent) is
   undefined. The overshoot is the weight of the atom at the quantile, up to max_i p_i ≤
   n_eff^{-1/2}.

**True candidates** (proposed by the attackers; to be proved and re-verified):

- **T2′** (marginal coverage, uniform route; atomless s(X), h ≤ σ, bounded A with
  ρ_A = inf_A ρ_h): with probability 1−δ,

  |cov − α| ≤ τ_h + Pr(Y_h ∉ A) + C_k √((k log(eR_A/h) + log(2/δ)) / (N h^k ρ_A)).

  The discreteness term is absorbed.
- **Theorem B** (data-dependent, no τ_h, no ρ_min; atomless F, L-Lipschitz in y):

  |cov − α| ≤ 2L·E[r_h(Y*)] + 8·E[n_eff(Y*)^{-1/2}] + √(2 a_max log(1/δ)),

  where r_h(y) = ∑_i p_i(y)\|y^i − y\| and a_i = E p_i(Y*).
- **Proof ingredients.**
  - Lemma 0: sup-norm CDF error D ⇒ \|coverage − α\| ≤ 2D for an atomless target.
  - The exact Gaussian convolution identity.
  - TV(P, P_h) = τ_h.
  - Kernel-weighted empirical-process bounds (Einmahl & Mason; Hall, Wolff & Yao) or
    symmetrisation plus McDiarmid.
- **The window becomes empty fast in k.** N must grow super-exponentially in k for a
  non-empty calibration window, so consequence (a) is meaningful for small k only.
- **Consequence (c), checkpoint selection by held-out PIT**, is O(√(log(J/δ)/m)). It needs
  pairs i.i.d. and independent of the checkpoints, J fixed in advance, randomised PIT
  (atomic laws) and a fresh split for reporting. Marginal PIT cannot see over-smoothing.

## Re-verification after the fixes (2026-10-12)

All fixes above were applied to `paper/main.tex` (and propagated to the workshop version).
Bundles A–E were rebuilt from the revised source, and every bundle went to three new
fresh-context verifiers (same three attack variants, none told of earlier verdicts). L1 got
a fourth verifier (would-it-prove-too-much). The written proof of Theorem B (the corrected
T2) got four.

| Bundle | Results | New verdicts | Total holds | Status |
|---|---|---|---|---|
| A | `prop:collapse`, `lem:cov`, `lem:wellposed`, `lem:mixture-coupling`, `prop:kernel-field`, `thm:endpoint`, `cor:zerobw`, `prop:moments` | C C C | 6 | **confirmed** |
| A | `cor:infbw` (now cites `prop:uncond`), `prop:uncond`, `prop:atomicity` (now cites `prop:collapse`(d) at h=0) | C C C | 3 (`atomicity` 5) | holds 3/3 after the fix (`atomicity` confirmed) |
| B | `prop:heffid`: derivatives, large-h limit, stability, grid not containing h_true (recentred at g), h_mean in the norm ∑_c\|e_c\| | C C C | 6 for the unchanged parts, 3 for the grid and h_mean parts | **confirmed**; grid and h_mean hold 3/3 |
| C | `thm:calib` (a), (b) | C C C | 6 | **confirmed** |
| C | `thm:calib` (c) strictness (open set), (d) (fixed nonnegative weights, x* independent) | C C C | 3 | holds 3/3 after the fix |
| D | `prop:specbias`(a), `prop:filtered`(a), (b) | C C C | 6 | **confirmed** |
| D | `prop:specbias`(b) (multiplier setting, f⋆−c ∈ L²) | C C C | 3 | holds 3/3 after the fix |
| E | `prop:prop17` algebra, `prop:tgtnoise` | C C C | 6 | **confirmed** |
| E | `prop:prop17` framing (minimiser of the t(1−t)-weighted loss), `cor:prop18` | C C C | 3 | holds 3/3 after the fix |
| F | **L1** positivity, k=1 | C (4th) | 4 | **confirmed** |
| F | L1 remark ("signed weights in k≥2 open") | **I** | — | **refuted**: false already at N=3 in k=2 (equilateral triangle: a negative weight far away, sum > 1 at the centre; checked numerically). Corrected in `docs/theory/lemma_L1.tex` |
| H | **Theorem B** (label-weighted mixtures, coverage bound) | C C C C | 4 | **confirmed** |
| H | Theorem B remark | C C C G | — | one GAP: "n_eff grows with h" holds for the Gaussian kernel, not for every kernel (step-kernel counterexample). Corrected in `docs/theory/theorem_B.tex` |

No new hole was found in any main-text proof. The nits raised by two or more verifiers
were then applied to `main.tex`:
- `specbias`(b): the multiplier is unbounded for every ζ>0, and the solution is in the
  semigroup sense, with a uniqueness line.
- `cor:prop18`: inf L_σ = E Var by the conditional decomposition in [0,∞], not by
  `prop:projection`, whose L² hypothesis fails.
- The lead-in to `prop:prop17`: the loss is infinite because the conditional variance is
  not integrable, not merely because the target is not.
- `heffid`: the symbol m was overloaded (now ā); κ_g in the grid case; the CIFAR κ values
  are local slopes.
- `filtered`(b): "nearest atom location".
- `calib`: Σ_x ≻ 0 in (c), and the Bayes-formula version of π_h(·|y).

Recurring nit not acted on: the bundles did not contain the definition of p_i^{(h)}(y). It
is in the main text (Section 3, before `prop:kernel-field`); the bundle extractor stopped
before it.

## Still to do

1. Fourth verifier for the results that now hold 3/3 after a fix (`cor:infbw`,
   `prop:uncond`, `heffid` grid and h_mean, `calib`(c)(d), `specbias`(b), `prop17`
   framing, `cor:prop18`).
2. T2′ (uniform route) has no proof yet; Theorem B is the version to use.
3. Not covered by this check: `prop:survival`, `cor:lossform`, `prop:expansion`,
   `prop:nwrate`, `prop:cfg`, `prop:cfgatom`, `prop:nearduplicate` and the
   non-representability results. These are appendix-only and outside the main claims.
