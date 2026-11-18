# Theory extensions after the EDM swap and μ runs (2026-11-11, revised 2026-11-12)

Draft by Claude, **not yet verified by the author**. It extends
`docs/plan/theorem_sketch_late_error_2026-11-10.md` (Claims 1–4, verified there) with three statements:

- **P**: the parametrization proposition, why an EDM-style network cannot collapse;
- **L**: a local version of Corollary 2, which removes the "for all x" hypothesis;
- **T**: the two-clocks decomposition behind the swap results.

**Revision of 2026-11-12.** The adversarial verification round (section "Verification" at the end)
found:
- in P, an overclaimed informal conclusion and a wrong rate in (iv);
- in L, only wording issues;
- in T, two wrong bounds in (ii) and an inequality in (i) that was read in the wrong direction.

Everything below is the corrected version. Changes are marked **[rev]**.

The prior-art check is in `research_notes/Khoảng trống novelty sai số muộn/fulltext_check_2026-11-11.md`.
Items A–D are novel there, provided the citations below are given.

## Setting in EDM coordinates

The probability-flow ODE is dx/dσ = (x − D(x,σ))/σ, and sampling runs σ from σ_max down to 0. The
CFM coordinates of the paper are Z = t x with t = 1/(1+σ), and x̂(Z,t) = D(Z/t, σ). Then
J_x̂ = J_D, μ_cfm = (1+σ)·λ_max(sym J_D), ε_t = 1−t = σ/(1+σ), and dt/ε_t = −dσ/(σ(1+σ)).

**Standing assumptions [rev].**
- D (equivalently F) and J_D are jointly continuous in (x, σ), so that solutions exist, are unique,
  and the Grönwall/comparison steps apply. **[rev2]** Separate continuity in σ is not enough for Peano;
  the same applies to x̂ in (x, t) in L and T.
- The training images are distinct.

For two solutions x, x′ with δ = x − x′ and the averaged Jacobian J̄ = ∫₀¹ J_D(x′ + sδ) ds,
dδ/dσ = (I − J̄)δ/σ. Along the sampling direction (σ decreasing):

  d|δ|/d(−σ) = −(1 − q)|δ|/σ,  where q = ⟨δ, sym J̄ δ⟩/|δ|² ∈ [λ_min, λ_max] of sym J̄.   (★)

(★) is Claim 1's computation in σ-time. q = 1 is neutral, q < 1 contracts and q > 1 expands. The
exact denoiser has J_D = Cov_w/σ² → 0 after collapse, so q → 0 and |δ| ∝ σ → 0.

The EDM preconditioners write D(x,σ) = c_skip(σ)·x + c_out(σ)·F(c_in(σ)·x, σ), so
J_D = c_skip I + c_out c_in J_F. The coefficients are:

| | c_skip | c_out·c_in | as σ → 0 |
|---|---|---|---|
| EDMPrecond | σ_d²/(σ²+σ_d²) | σσ_d/(σ²+σ_d²) | c_skip = 1 − O(σ²), c_out·c_in ≤ σ/σ_d |
| VPPrecond | 1 | −σ/√(σ²+1) | |c_out·c_in| ≤ σ |

P depends on this structure (1 − c_skip = O(σ²), c_out c_in = O(σ)).

**[rev3]** For an x-prediction network (c_skip = 0), the bound in (ii) contains the term ∫dσ/σ = ∞,
so A = ∞ and (ii)–(iii) give nothing. (i) still applies, but ∫(1 − inf λ_min)/σ must then be
checked directly.

The earlier claim "∫ρ′/σ = ∞ always" was false. Counterexample: D = x has ρ′ = 0. That claim does
hold when inf λ_min(sym J_D) ≤ 1 − ε, for example for a bounded or saturating D.

## P. The parametrization proposition

Let Λ(σ) = sup_x ‖sym J_F(·,σ)‖_op, and ρ′(σ) = 1 − inf_x λ_min(sym J_D(x,σ)).

**Proposition P.**

(i) For 0 < σ_a < σ_b and any two solutions,
  |δ(σ_a)| ≥ |δ(σ_b)|·exp(−∫_{σ_a}^{σ_b} ρ′(σ)/σ dσ).
If ρ′ ≤ ρ̄ on [σ_a, σ_b], the factor is at least (σ_a/σ_b)^{ρ̄}. **[rev]** This holds for either
sign of ρ̄. It gives a lower bound at σ = 0 only when the partial integrals ∫_{σ_a}^{σ_b} ρ′/σ stay
bounded above as σ_a → 0. A constant ρ̄ > 0 does not give one. **[rev3]** ρ′ can be negative;
"= ∞" below means unbounded above, that is, coming from the positive part.

Collapse with x(0) existing forces this divergence. If x(σ₂) has no atoms and x(0) ∈ S with positive
probability, two distinct trajectories reach the same point, so |δ(σ_a)| → 0.

(ii) ρ′(σ) ≤ (1 − c_skip) + |c_out c_in|·Λ(σ). For EDMPrecond,
  ∫₀^{σ₂} ρ′/σ dσ ≤ A := σ₂²/(2σ_d²) + (1/σ_d)∫₀^{σ₂} Λ(σ) dσ.
For VPPrecond, A := ∫₀^{σ₂} Λ dσ.

(iii) Suppose ∫₀^{σ₂} Λ dσ < ∞ and |F(y,σ)| ≤ M(1+|y|), with M uniform in σ ∈ (0, σ₂].
Then:
- the flow map Φ: x(σ₂) ↦ x(0) exists;
- Φ is bi-Lipschitz with constants e^{±A};
- if x(σ₂) has a density bounded by p_max, then for any set S of N training images,
  P(dist(x(0), S) ≤ r) ≤ N·p_max·e^{dA}·ω_d·r^d.

In particular P(x(0) ∈ S) = 0, and no two trajectories merge.

**[rev3]** These two consequences need only an absolutely continuous x(σ₂), since Φ⁻¹ maps null sets
to null sets; p_max is needed only for the r^d bound. Φ is onto ℝ^d, by invariance of domain plus a
closed image. That onto-ness is what lets each preimage Φ⁻¹(B(s, r)) be centred, giving the
constant ω_d e^{dA}.

**[rev]** This is a qualitative statement. With d = 3072 on CIFAR-10, the factor e^{dA} makes the
bound vacuous at practical r unless A is tiny. What it rules out is exact collapse and merging, not
near-copies.

(iv) **[rev2]** For the exact denoiser, c_out c_in sym J_F = J_{D*} − c_skip I with J_{D*} = Cov_w/σ².
Hence Λ_exact(σ) ≥ c_skip/|c_out c_in|, which is σ_d/σ for EDM and √(σ²+1)/σ for VP.

The bound is attained at every x when d > N − 1, since then Cov_w has a zero eigenvalue. Otherwise
(e.g. CIFAR-10, N = 50 000 > d) it is approached as |x| → ∞ along a generic direction, where one
weight dominates and Cov_w → 0.

Near ties Λ_exact is larger still (≈ gap²/(4σ³σ_d) for EDM). Either way ∫₀ Λ_exact = ∞. Note that
F* grows like (σ_d/σ)|y|, so the exact field also violates the uniform growth hypothesis of (iii).

**Correct reading [rev, rev2].** Contrapositive of (iii), for networks whose F satisfies the
uniform growth bound (so that x(0) exists): exact collapse onto a finite set needs ∫₀ Λ dσ = ∞.

Given that x(0) exists, (i) gives the sharper necessary condition ∫₀ ρ′/σ dσ = ∞. Because Λ is a
global sup and two-sided in sign, ∫Λ = ∞ can come from regions no trajectory visits, or from
expanding directions, so on its own it carries little evidential weight.

These conditions are necessary only. They do **not** say:
- that ‖J_F‖ must grow like 1/σ. Λ ~ 1/(σ log(1/σ)) also diverges. A d = 1 example: D = (1 − a(σ))x
  with a(σ) = 1/log(1/σ) collapses every trajectory onto 0, with Λ = o(1/σ).
- that ρ must stay bounded away from 0. In the same example ρ′ = a(σ) → 0.

The λ_max-based share ρ = 1 − λ_max(sym J_D)/c_skip plays the *sufficient* side. **[rev2]** It does
so only when the bound holds on the segment (or tube) between two trajectories, not merely at points
of one trajectory.

If ρ ≥ ρ₀ ∈ (0, 1] there, for every σ in [σ_a, σ_b], then **[rev3]**
1 − λ_max ≥ (1 − c_skip) + c_skip ρ₀ ≥ ρ₀. So |δ(σ_a)| ≤ (σ_a/σ_b)^{ρ₀}|δ(σ_b)|. Along a
single trajectory the condition gives only linearized contraction (DΦ → 0 at that point). The local
sufficient condition for landing is L's tube hypothesis. "Equivalently" in the earlier draft was
wrong.

The necessary conditions are also not specific to memorization. Any concentration of the output
onto a Lebesgue-null set needs ∫Λ = ∞. That includes a generalizing denoiser that projects onto a
low-dimensional manifold, which has J_F ≈ (P_tan − I)σ_d/σ in the normal directions. So P explains
why an EDM-parametrized network with integrable Λ *cannot* collapse. It does not show that
divergent Λ implies memorization.

**Proof sketch.**

(i) q = ∫₀¹⟨u, sym J_D(x′+sδ) u⟩ ds (u = δ/|δ|) is an average of Rayleigh quotients, so
q ≥ inf_x λ_min(sym J_D). Then (★)
gives d|δ|/d(−σ) ≥ −ρ′|δ|/σ, and Grönwall finishes. δ ≠ 0 for σ > 0 by uniqueness.

(ii) λ_min(sym J_D) ≥ c_skip − |c_out c_in|Λ. For EDM, 1 − c_skip = σ²/(σ²+σ_d²) ≤ σ²/σ_d² and
|c_out c_in| ≤ σ/σ_d. Divide by σ and integrate.

(iii) **[rev]** Existence down to σ = 0 comes from the growth bound, not from ∫Λ < ∞. The velocity is
((1−c_skip)x − c_out F)/σ. Its size is ≤ C(1+|x|) uniformly in σ, because (1−c_skip)/σ = O(σ),
|c_out|/σ ≤ 1 and c_in ≤ 1/σ_d. So there is no blow-up, and x(σ) is Cauchy as σ → 0.

For the two-sided Lipschitz bounds, |1 − q| ≤ (1 − c_skip) + |c_out c_in|Λ, and (★) gives both. Pass
to the limit σ_a → 0.

For the density bound, only the lower constant is needed. Φ⁻¹ is e^A-Lipschitz on the image, so
Leb(Φ⁻¹(B)) ≤ e^{dA} Leb(B). The push-forward density is therefore ≤ p_max e^{dA}. Integrate over N
balls of radius r.

Bounded density at σ₂ follows the same way on [σ₂, σ_max] when Λ is bounded there.

(iv) **[rev2]** ‖sym J_F‖ ≥ c_skip/|c_out c_in| wherever J_{D*} has an eigenvalue 0 (case d > N−1),
and → c_skip/|c_out c_in| as |x| → ∞ generically (otherwise). Positive semidefiniteness of J_{D*} alone
does not give the bound: the earlier sentence citing it had the direction wrong.

[GAP: (iii) uses sup over all x of ‖J_F‖. A trajectory-wise version (sup over a tube) is what the
data support. It needs a tube version of the density argument, which is not done.]

**Relation to prior work.**
- López Amado et al. (2609.39648), Prop. B.4: a fixed point of the iterated D_σ at fixed σ is an
  attractor iff the eigenvalues of ∇D_σ are below 1. P is about the time-dependent ODE and the
  parametrization's σ → 0 limit. Cite B.4 as the fixed-σ analogue.
- Dodson et al., App. D, notes that J_D → I for the Gaussian denoiser (credited to Lukoianov et al.).
  P turns this into a quantitative non-collapse statement.
- Kwon et al. 2022: their (A2) and Thm 1 use the same Grönwall integrating factor, applied to a W₂
  bound with no threshold.
- Al-Jaff et al. (ICML 2026) find that the target (x, ε, v) changes memorization at matched FID.
  P suggests an order: an x-prediction network has c_skip = 0, so P gives no protection; ε- and
  EDM-preconditioned networks start from J_D ≈ I. **Their order could not be checked: only their
  abstract is accessible.** Fetch the PDF before claiming agreement.

**Data so far** (`results/n3_followup_20261111/MU_SUMMARY.md`, both models 100% off-atom):

| | σ = 0.023 | σ = 0.002 |
|---|---|---|
| sub1000 (EDMPrecond), median ρ | 0.016 | 0.014 |
| public (VPPrecond), median ρ | −1.03 (expanding) | 0.001 |

These are λ_max-based medians along trajectories (ρ, the sufficient side). They show that the
sufficient condition for landing fails: with ρ ≈ 0.015, contraction over σ ∈ [0.002, 0.1] is at
most a factor of about 0.94.

They do not by themselves verify P's hypothesis, which is a sup over x of ‖J_F‖. The sub500 run
records λ_min (`mu_min`), which gives the trajectory-wise ρ′.

## L. Local version of Corollary 2

Fix one initial point. Y is the exact path and Z the learned path, D = Z − Y, and
e_Y(t) = |x̂(Y_t,t) − m*(Y_t,t)|, as in Claim 1. There may be N ≥ 1 atoms.

**[rev]** The start time t₁ is arbitrary, and the reference path may be *any* exact path on
[t₁, 1): the proof uses only the ODE on [t₁, 1). The error level is written η, to avoid a clash with
ε_t.

**Proposition L.** Suppose that for t ∈ [t₁, 1):
- (a) sup over x ∈ B(Y_t, R) of λ_max(sym J(x,t)) ≤ μ̄ < 1;
- (b) e_Y(t) ≤ η;
- (c) max(|D_{t₁}|, η/(1−μ̄)) < R.

Then |D_t| < R for all t ∈ [t₁, 1), and
  |D_t| ≤ w_t|D_{t₁}| + (1 − w_t)·η/(1−μ̄), with w_t = (ε_t/ε_{t₁})^{1−μ̄}.
Hence limsup_{t↑1} |Z_t − Y₁| ≤ η/(1−μ̄), **provided Y_t → Y₁**.

Suppose moreover that **Y₁ is a training image** and η/(1−μ̄) < g/4, with g the smallest gap
between training images. Then there is T < 1 such that for all t ∈ [T, 1), Z_t is on-atom in the
sense of App. C.4 (d₁/d₂ < 1/3), with nearest image Y₁: d₁ < g/4 and d₂ ≥ g − d₁ > 3g/4. **[rev]**
Z_t need not converge. Example **[rev3]**: N = 1, x̂ = x¹ + μ̄(x − x¹) + c(t), with
c(t) = η(cos log(1/ε_t), sin log(1/ε_t), 0, …). Then Z settles on a rotating circle of radius
η/√((1−μ̄)² + 1). So "ends on-atom" means "on-atom for all t close to 1".

"On-atom" means within g/4 of a training image, which implies d₁/d₂ < 1/3.

The constant is sharp. **[rev2]** Take N = 1, x̂(x,t) = x¹ + μ̄(x − x¹) + c with |c| = η, and
Y ≡ x¹, which is an exact path because m* ≡ x¹. Then
  D_t = w_t D_{t₁} + (1 − w_t)c/(1 − μ̄),
and equality holds whenever D_{t₁} is a nonnegative multiple of c.

**Proof.**

1. Let τ = sup{t ≥ t₁ : |D_s| < R on [t₁, t]}. Then τ > t₁ by (c) and continuity.
2. On [t₁, τ) the segment [Y_t, Z_t] lies in the convex ball B(Y_t, R), so μ(t) ≤ μ̄. Both terms of
   Claim 1 are nondecreasing in μ, since the coefficients |D_{t₁}| and e_Y/ε are ≥ 0. So Claim 1
   applies with μ ≡ μ̄. The integral term equals η(1 − w_t)/(1−μ̄). This gives the displayed bound,
   which is a convex combination and hence ≤ K := max(|D_{t₁}|, η/(1−μ̄)) < R.
3. If τ < 1, continuity gives |D_τ| ≤ K < R, contradicting the definition of τ. Hence τ = 1.
4. w_t → 0. The on-atom claim follows from the triangle inequality: for every j ≠ i,
   |Z_t − x^j| ≥ g − |Z_t − x^i|.

**Convergence of the exact path.** It is needed only for "Y₁ is a training image".

The exceptional set is real. With atoms ±1 and X₀ = 0, symmetry keeps Y_t ≡ 0, the midpoint.

For almost every X₀, the following is a sketch (not a full proof):
- The exact flow pushes N(0, I) to p_t, and p_t → (1/N)Σδ_{x^i}.
- Once Y_t is inside the scaled Voronoi cell of x^i with a margin, the other weights are
  exp(−c/ε_t²), and Y_t → x^i.

[GAP: show that a.e. trajectory eventually enters such a margin region. Until this is proved or
cited, state L with the hypothesis "Y_t → x^i".]

**Scope.** (a) up to t = 1 is a memorization-regime assumption. A generalizing denoiser has
J_D → I near the data, so μ → 1 and the bound degenerates. This is exactly what the μ measurements
show for both EDM models.

## T. Two clocks (decomposition behind the swap)

**Basins.** For t < 1, B_i(t) = {x : the exact flow from (x, t) ends at x^i}. **[rev]** The B_i(t):
- are open and disjoint;
- are carried along by the exact flow, Φ_{t→u}(B_i(t)) = B_i(u);
- cover ℝ^d up to a closed set N(t) that is Lebesgue-null.

The null-set claim uses the a.e. convergence above and inherits L's GAP. As t → 1, B_i(t) tends to
the Voronoi cell V_i. **[rev3]** Precisely: for every compact K ⊂ int V_i there is t_K < 1 with
K ⊂ B_i(t) for all t ∈ [t_K, 1).

N(t) is defined as ℝ^d minus the union of the basins. Space-time openness of
{(x,t) : x ∈ B_i(t)} makes t_sel and i(Z) measurable. The swap is taken to integrate the exact ODE
with no discretization error.

For a learned trajectory Z, define:
- **the selection clock** t_sel = inf{s : Z_t ∈ B_i(t) for all t ∈ [s, 1), for one fixed i}, with
  t_sel := 1 when no such s exists, and i(Z) the index;
- **the landing quantity**, the late distance |Z_t − x^i| as t → 1.

The basin set in space-time is open, so the inf is not attained when t_sel > 0.

**Proposition T. [rev]**

(i) The net→exact swap at level s (CFM time t_s) ends at x^i exactly when Z_{t_s} ∈ B_i(t_s), by
definition. It ends at no image iff Z_{t_s} ∈ N(t_s).

Let A(s) = P(swap endpoint = x^{i(Z)}), with the event taken as empty when t_sel = 1. Let
F(s) = P(t_sel < t_s). Then
  F(s) ≤ inf_{t_u ≥ t_s} A(u) ≤ A(s),   A(s) − F(s) = P(Z_{t_s} ∈ B_{i(Z)}(t_s), t_sel ≥ t_s).
**[rev2]** The inf runs over *later* hand-over times, that is smaller noise levels σ_u ≤ σ_s. The
difference A − F is the excursion mass: Z is in its final basin at t_s, leaves, and returns.

Suppose Z₁ = lim Z_t exists and has a unique nearest image j. Then t_sel < 1 and i(Z) = j.

The proof goes through the scaled Voronoi cells. At time s the dominant weight is that of the
nearest image to x/s, so the exact cells are s·V_i. A compact ball around Z₁ inside int V_j then
lies in B_j(t) for t near 1.

So the "=L" event of the experiments coincides with {swap endpoint = x^{i(Z)}} except on Voronoi ties
of the endpoint.

**Reading [rev2].** The "=L" curve, after its monotone envelope, is an **upper** bound on the CDF of
t_sel. Selection happens no earlier than the curve suggests, and the bound can be loose at large σ,
where basins are large.

If Z₁ exists a.s. and P(Z₁ on a Voronoi boundary) = 0, then A(s) → 1 as s → 1 for any learned flow,
so the limit is uninformative.

Without these conditions the limit can fail. A d = 1 learned field that is constant in x but
oscillating in t makes Z cross the tie infinitely often, so t_sel = 1 a.s. The finite-σ values do
carry information about the network, as upper bounds.

(ii) Landing.

(a) Sufficient condition (via L, restarted at t₁). Let Ŷ be the exact path from (Z_{t₁}, t₁), with
Z_{t₁} ∈ B_i(t₁), so that Ŷ₁ = x^i. Suppose that on [t₁, 1):
- sup over B(Ŷ_t, R) of λ_max(sym ∂x̂) ≤ μ̄ < 1;
- |x̂(Ŷ_t) − m*(Ŷ_t)| ≤ η;
- η/(1−μ̄) < R.

Then limsup |Z_t − x^i| ≤ η/(1−μ̄). The hypotheses sit along Ŷ, not along the exact path from Z's
initial point (the earlier draft used the wrong path).

(b) Lower bound (via the computation of P(i) with a source term). Write e = Z − x^i in EDM
coordinates and b(σ) = D(x^i, σ) − x^i, the network's reconstruction residual at the training
image. Suppose ρ′ ≤ ρ̄ on [σ_min, σ₁], where ρ′ is the inf of λ_min over the segment [x^i, Z]. Then
  |e(σ_min)| ≥ (σ_min/σ₁)^{ρ̄}|e(σ₁)| − σ_min^{ρ̄}∫_{σ_min}^{σ₁} s^{−ρ̄−1}|b(s)| ds.

The earlier draft omitted the source term. That was wrong: D = x − δσ has ρ′ = 0, yet it carries Z
onto x^i, a pure translation with |b| = δσ. The corrected bound is attained in that example.

So ρ ≈ 0 late means no late attraction to x^i **only when** the residual integral
∫|b|/s ds is also small.

**[rev2]** The derivation needs two remarks:
- Where e = 0, |e| is not differentiable. Use upper Dini derivatives, or absolute continuity; the
  conclusion is unchanged.
- ρ̄ here is stated in EDM coordinates (J_D = t·∂_Z x̂). It agrees with the flow-matching quantity of
  (ii)(a) only as σ → 0.

(iii) **Remark (not a theorem).** For Dodson et al.'s network→network swap, the relevant quantity is
the field difference ∫|D_A − D_B|(Z, s)/s ds, controlled by a λ_max growth factor and compared with
the basin margin. "Both ρ ≈ 0" alone does not imply that neither clock changes.

What the data say is empirical:
- network→network at small σ: 91% → 91% (Dodson);
- net→exact: 100% on-atom at every s;
- exact→net with s ≤ 0.1: d₁ ∝ s.

These are consistent with: no landing without a contracting late field.

**Data** (`results/n3_followup_20261111/SWAP_SUMMARY.md`): "=L" is 31%, 56%, 90%, 99% and 100% at
s = 5, 2, 1, 0.2 and 0.02 for the public model. By (i), at most 31% of samples have selected by
σ = 5, at most 56% by σ = 2, and at most 90% by σ = 1.

The limit of 100% as s → 0 is automatic, given that the endpoints exist and are not on ties. The
values at s ≳ 1 are informative, as upper bounds.

**Honest assessment.**
- (i) is close to a definition. Its value is that it makes the selection clock measurable from the
  swap, as an upper bound on its CDF.
- (ii)(a) is L. (ii)(b) is a short Grönwall computation.
- (iii) is a remark.
- A sharper result would bound t_sel in terms of the posterior-collapse time of the exact field
  (Biroli et al.'s t_C). That remains proposal 5.

## E. Directional contraction toward an image (added 2026-11-16, after the sub500 run)

**Why.** On the memorizing sub500 model, μ = (1+σ)λ_max(sym ∂D) is ≈ 0.96 for on-atom and off-atom samples
alike at σ ≤ 0.023 (AUC ≈ 0.5), while λ_min is ≈ 0.09 (σ = 0.023). λ_max is the worst direction; the
distance to an image moves at the rate of the Rayleigh quotient along the direction to that image. E makes
this exact. It also corrects a misreading: ρ = 1 − λ_max/c_skip bounds the contraction from below
(guaranteed contraction), not from above.

**Setting.** 0 < σ_min < σ_max; D continuous, C¹ in x, J = ∂_x D jointly continuous; x(σ) a C¹ solution of
dx/dσ = (x − D(x,σ))/σ (sampling runs from σ_max down to σ_min). Fix y (a training image), e = x − y,
b(σ) = D(y,σ) − y (residual at y), e ≠ 0 on the interval, ê = e/|e|,
  q(σ) = ∫₀¹ êᵀ J(y + τe, σ) ê dτ,  Φ(a,s) = exp(−∫_a^s (1 − q(u))/u du).
q is the mean Rayleigh quotient of sym J on the segment [y, x] in the direction of e. 1 − q is the
contraction rate of |e| per unit log σ.

**Proposition E.**
- (★) n = |e| satisfies n' = (1 − q) n/σ − ê·b/σ exactly.
- (a) Exact representation: |e(σ_min)| = Φ(σ_min,σ_max)|e(σ_max)| + ∫_{σ_min}^{σ_max} Φ(σ_min,s) ê·b/s ds.
  A positive ê·b (the residual at y points toward x) keeps the sample away from y.
- (b) Λ⁻ ≤ q ≤ Λ⁺, with Λ^± the inf/sup over the segment of λ_min/λ_max of sym J. Hence
  Φ⁻|e(σ_max)| − ∫Φ⁺|b|/s ≤ |e(σ_min)| ≤ Φ⁺|e(σ_max)| + ∫Φ⁺|b|/s (Φ^± built from Λ^±; the residual in the
  lower bound carries Φ⁺). With b = 0 this is the logarithmic-norm Grönwall bound. λ_max alone does not
  decide the shrinkage: for D = diag(1, 1 − m)x, λ_max ≡ 1, yet starts (0,1) and (1,0) shrink by κ^{−m} and 1
  (κ = σ_max/σ_min); for D = [[0,2],[0,0]]x from (1,0), q ≡ 0 and the true factor is κ^{−1} while λ_max = 1.
- (c) Landing time. For σ_a ∈ (σ_min, σ_max], ρ̄ = sup_{[σ_min,σ_a]}(1 − q), β = sup|b|:
  |e(σ_a)| ≤ (σ_a/σ_min)^{ρ̄}|e(σ_min)| + β g(ρ̄), g(ρ̄) = ((σ_a/σ_min)^{ρ̄} − 1)/ρ̄, g(0) = log(σ_a/σ_min).
  This bounds the error at the higher noise level σ_a by the endpoint error (the reverse of the sampling
  direction): with small directional rate ρ̄ late, a sample that ends near y was already near y at σ_a.
  Tight for D = ax, y = 0.
- (d) Two images y₁, y₂, r = |x − y₁|/|x − y₂|:
  log r(σ_min) − log r(σ_max) = ∫(q₁ − q₂)/s ds + ∫[ê₁·b₁/|e₁| − ê₂·b₂/|e₂|]/s ds.
  With small residuals, the ratio d1/d2 (the on-atom criterion) falls exactly where q₁ < q₂, i.e. where the
  flow contracts more along the direction to y₁ than along the direction to y₂. A bound that uses λ_max at x
  gives the same factor for both images and cannot see this (example: A = diag(1, 1 − m), y₁ = 0,
  y₂ = (c, 0), start (0, h), h ≠ 0: r → 0 while λ_max ≡ 1).

**Proof.** τ ↦ D(y+τe) is C¹, so D(x) − D(y) = Me with M = ∫₀¹ J(y+τe) dτ; then e' = (e − Me − b)/σ and
n n' = eᵀe' = (n² − n² êᵀMê − e·b)/σ, which is (★) since êᵀMê = q. q, b are continuous (joint continuity
on a compact set), so p = (1 − q)/σ is continuous and F(s) = Φ(σ_min,s)n(s) has F' = −Φ ê·b/s; integrate
for (a) (the same works on any subinterval). (b): Rayleigh pointwise, average over τ; Λ^± continuous
(Weyl + compactness); 1 − Λ⁺ ≤ 1 − q ≤ 1 − Λ⁻ gives Φ⁻ ≤ Φ ≤ Φ⁺, and Φ ê·b ≥ −Φ⁺|b|. (c): solve the
subinterval form of (a) for n(σ_a); ∫_s^{σ_a} p ≤ ρ̄ log(σ_a/s) for either sign of ρ̄; −ê·b ≤ β;
substitute t = log(σ_a/s). (d): (log n_k)' = (1 − q_k)/σ − ê_k·b_k/(σ n_k) from (★); subtract and integrate.

**Honest reading.** By the fundamental theorem of calculus, q·|e| = ê·(D(x) − D(y)). q is the secant slope of
D toward y, not a local Jacobian quantity, and (★) is the radial projection of the ODE, d log|e|/d log σ =
1 − ê·(D(x) − y)/|e|. Its content is the comparison in (b): local one-sided Lipschitz constants (μ, λ_max)
only bound the secant slope, and they can miss contraction that the secant sees. q small means D maps the
whole segment [y, x] close to y: the sample sits in a memorization basin of y.

**Measured** (`results/n3_q_20261117/Q_SUMMARY.md`, 2026-11-17; sub500 n = 1000 with 41 off-atom, public
n = 200 all off-atom; q by 4-point quadrature of VJP Rayleigh quotients). The identity holds on the
trajectories: actual change of log|x − y₁| = contraction + residual up to a Heun gap of −0.26 (σ 1.09 → 0.14)
and −0.04 (σ 0.14 → 0.002) for on-atom samples.

| window σ | Δlog\|x − y₁\| on | off | public |
|---|---|---|---|
| 80 → 5.3 | −2.71 | −2.71 | −2.71 |
| 5.3 → 1.09 | −1.58 | −1.50 | −1.54 |
| 1.09 → 0.14 | −2.01 | −0.91 | −1.07 |
| 0.14 → 0.002 | −1.54 | −0.05 | −0.07 |

- The on/off difference is made in the last two windows (σ ≤ 1.09): about 2.6 in log, a factor ≈ 13. Landing
  is late, along the direction to the image. μ missed it because λ_max at x is ≈ 1 in other directions.
- q₁ separates on from off: AUC 0.81 (σ 5.3), 0.92 (σ 1.9), 0.97 (σ 1.09), ≥ 0.99 from σ 0.59, 1.000 at
  σ 0.14–0.023. Median q₁ on-atom ≈ 0.22 at σ 0.30–0.14 against 0.53–0.76 off-atom.
- The one-point proxy q₁x (at x only) does not separate late (0.97 on vs 0.69 off at σ 0.14, reversed): the
  contraction lives in the interior of the segment, not at x.
- q₁ − q₂ (differential contraction, (d)) separates with AUC 0.84–0.91 at σ ≤ 0.14.
- Public model: q₁ → 1 by σ ≈ 0.06; almost no late contraction toward the nearest image.
- Caveat: q₁ uses the endpoint's nearest image, so it is not a predictor available before the end; and,
  being ê·(D(x) − D(y))/|e|, it is related to the nearest-image distance of D (Lemma R). It explains the
  mechanism; it is not claimed as a better detector.

## R. Field error and nearest-image distance coincide late (added 2026-11-16)

**Why.** On sub500, AUC(nn_hat) ≥ AUC(e_learned) at every t and both reach 1.0 from t ≈ 0.34
(`results/n3_edm_sub500_20261115/N3_SUMMARY.md`). R shows this is expected once the exact posterior has
concentrated, so equal AUCs are not evidence against the field-error view; they also mean the field error
should not be sold as a better memorization detector than nearest-image distance.

**Setting.** Training images x¹, …, x^N distinct, Δ = diameter, D_j = max_k |x^j − x^k|. At (y, σ):
posterior weights w_j(y) ∝ exp(−|y − x^j|²/(2σ²)), exact denoiser m(y) = Σ w_j x^j. For a network output v:
e(v) = |v − m(y)| (the field error e_learned) and n(v) = min_j |v − x^j| (nn_hat).

**Lemma R.**
- (a) n − (1 − w_max)D_i ≤ e ≤ n + (1 − w_{j*})D_{j*}, with i an argmax of w and j* a nearest image of v.
  The lower bound holds for every index i. The constant is attained (N = 2).
- (b) If |y − x^i| ≤ ρ δ_i(y), δ_i(y) = min_{k≠i}|y − x^k|, 0 ≤ ρ < 1, then
  1 − w_i(y) ≤ (N − 1) exp(−(1 − ρ²)δ_i(y)²/(2σ²)).
- (c) If two scores satisfy |s − s'| ≤ ε on every sample, then |AUC(s) − AUC(s')| is at most the fraction of
  (off, on) pairs whose s'-scores are within 2ε (ties counted ½).
- (d) Fix σ. If every sample z has an index i(z) with |y_z − x^{i(z)}| ≤ ρ δ_{i(z)}(y_z), let
  δ = min_z δ_{i(z)}(y_z) and η = (N − 1)Δ exp(−(1 − ρ²)δ²/(2σ²)).
  - (d1) Unconditionally, with d_i(z) = |v_z − x^{i(z)}|: |e − d_i| ≤ η on every sample, so the AUCs of e and
    d_i differ by at most the fraction of pairs with |d_i(a) − d_i(b)| ≤ 2η.
  - (d2) Under (H), "x^{i(z)} is a nearest image of v_z" (sufficient: |v_z − x^{i(z)}| ≤ half the gap from
    x^{i(z)} to the other images), d_i = n and the same holds for the AUCs of e and n.
  - (d3) Without (H) the n-version is false: d = 1, x¹ = 0, x² = 1, y_a = y_b = 0, v_a = 1, v_b = 0.3 gives
    AUC(n) = 0, AUC(e) → 1 while the bound → 0.

**Proof.** Σw_k = 1 gives m − x^j = Σ_{k≠j} w_k(x^k − x^j), so |m − x^j| ≤ (1 − w_j)D_j; two triangle
inequalities give (a). (b): w_k = w_i exp((|y − x^i|² − |y − x^k|²)/(2σ²)) ≤ exp(−(1 − ρ²)δ_i²/(2σ²)) for
k ≠ i; sum. (c): if |t'| > 2ε the pair's indicator is unchanged. (d1): ||v − m| − |v − x^i|| ≤ |m − x^i|,
then (b) and δ ≤ δ_{i(z)}, then (c).

**For the paper.** Report the d_i version (no (H) needed) or check (H) on the data; report the pair
fraction within 2η. The value of the field-error view is causal (the swap), not predictive (AUC).

## T1–T2. Main theory rewritten around the field error relative to the distance to the image (2026-11-17)

**Why.** Bổ đề 1 / Hệ quả 2 / Mệnh đề 3 of `theorem_sketch_late_error_2026-11-10.md` use μ = λ_max(sym ∂x̂),
which the sub500 data show does not decide landing (E above). T1–T2 state landing directly in the paper's
own quantity, the late field error err = |x̂ − m*| along the learned path, divided by the distance to the
selected image. No Jacobian enters. Bổ đề 1 and Hệ quả 2 stay as the global (uniform-in-x) special case.

**Theorem T1 (landing criterion; paper coordinates, ε = 1 − t).** x̂ continuous, Z C¹ with
Z' = (x̂(Z,t) − Z)/ε on [t₁,1); m* = Σ_j w_j x^j for any continuous weights w_j ≥ 0, Σ w_j = 1 (in
particular the exact posterior). Fix an image x^i; n = |Z − x^i|, err(t) = |x̂(Z_t,t) − m*(Z_t,t)|,
ω(t) = (1 − w_i(Z_t,t)) D_i, D_i = max_k |x^i − x^k|. All conditions are along the trajectory.
- (a) n is locally Lipschitz; where Z ≠ x^i, n' = (⟨ê, x̂ − x^i⟩ − n)/ε (exact radial identity); a.e.
  n' ≤ (err + ω − n)/ε, using |m* − x^i| ≤ (1 − w_i)D_i.
- (b) Landing. If err ≤ ϱ̄ n + γ with a constant ϱ̄ < 1 and continuous γ ≥ 0, η = γ + ω, then
  n_t ≤ (ε_t/ε_{t₁})^{1−ϱ̄} n_{t₁} + ∫_{t₁}^t (η/ε_s)(ε_t/ε_s)^{1−ϱ̄} ds, and η → 0 implies Z_t → x^i.
- (c) Non-landing. If n_{t₁} > 0 and ⟨ê, x̂ − x^i⟩ ≥ (1 − δ)n whenever n > 0 with ∫_{t₁}^1 δ⁺/ε < ∞
  (improper), then n_t ≥ n_{t₁}exp(−∫δ⁺/ε) > 0 for all t, and err ≥ (1 − δ)n − ω: the relative error is
  ≥ 1 − δ − ω/n.
- (d) The constant ϱ̄ < 1 in (b) cannot be taken equal to 1 (N = 1, x̂ = x¹ + ϱ(z − x¹): n ∝ ε^{1−ϱ}).

**Theorem T2 (trapping and landing; EDM coordinates).** Gaussian posterior w_j(x,σ), exact denoiser m*, ODE
dx/dσ = (x − D)/σ run from σ₁ down to 0. g = min_{k≠i}|x^i − x^k|, 0 < r ≤ g/4, ρ = r/(g − r) ≤ 1/3,
Ω(σ) = (N − 1)D_i exp(−(1 − ρ²)(g − r)²/(2σ²)). If (H1) err ≤ ϱ̄ n + γ whenever n ≤ r, (H2) n(σ₁) < r,
(H3) γ + Ω < (1 − ϱ̄) r on (0, σ₁], then
- (i) |x − x^i| ≤ r implies 1 − w_i ≤ (N − 1)exp(−(1 − ρ²)(g − r)²/(2σ²));
- (ii) n < r on (0, σ₁] (trapping, barrier argument at the largest σ with n ≥ r);
- (iii) n(σ) ≤ (σ/σ₁)^{1−ϱ̄} n(σ₁) + ∫_σ^{σ₁} ((γ + Ω)/s)(σ/s)^{1−ϱ̄} ds, and γ → 0 implies x(σ) → x^i;
- (iv) Ω < (1 − ϱ̄) r/2 for σ ≤ σ* = ((1 − ρ²)(g − r)²/(4 log(1/q)))^{1/2},
  q = (1 − ϱ̄) r/(2(N − 1)D_i) ≤ 1/8. So (H3) holds when σ₁ ≤ σ* and γ ≤ (1 − ϱ̄) r/2.
Reading: once the learned trajectory is within g/4 of an image at a noise level where the posterior has
concentrated, a learned denoiser whose error stays below ϱ̄ < 1 times the distance to that image (up to γ)
traps the sample and lands it exactly on the image.

**Proofs.** T1: Lemma by convexity; (a) radial derivative + Cauchy–Schwarz, interior-minimum argument
at zeros; (b) integrating factor ε^{−(1−ϱ̄)} on the absolutely continuous n, split-integral limit;
(c) log n on the maximal positive interval plus continuation; (d) explicit solution. T2: (i) w_k/w_i
bound with r² = ρ²(g − r)²; (★) n' ≥ ((1 − ϱ̄)n − γ − Ω)/σ for 0 < n ≤ r; (ii) at σ̄ = sup{n ≥ r},
(★) and (H3) give n'(σ̄) > 0 while right difference quotients are negative; (iii) integrating factor
σ^{−(1−ϱ̄)} on [σ, σ₁]; (iv) monotonicity of Ω. Full cleaned proofs (as verified) of E, R, T1, T2:
`docs/plan/proofs_E_R_T1_T2_2026-11-17.md`.

**What T1–T2 do and do not say (from the verifiers).**
- Sufficient, not necessary. ϱ̄ < 1 is sharp only among constants. A rotational error (x̂ = x¹ + R(z − x¹),
  R a 90° rotation) has err = n and still lands, and ϱ(t) = 1 − 1/log(1/ε) lands too. The quantity that
  decides landing is the radial one in (a): d log n/d log(1/ε) = 1 − ⟨ê, x̂ − x^i⟩/n. T1(b) bounds it by
  err; T1(c) uses it directly.
- The radial quantity is the secant q of Prop. E plus the residual (in EDM coordinates
  ⟨ê, D − x^i⟩/n = q + ê·b/n), so E is the measured form of T1(a) and T1 explains why q decides landing.
- ϱ̄ = 1 makes (H3) unsatisfiable; the necessity examples (D = x^i + λ(x − x^i), λ ≥ 1; D = x^i + v) show
  why each hypothesis is there, not cases where the theorem fails with its hypotheses met.
- Relation to the old Bổ đề 1 / Hệ quả 2: those need a uniform bound μ̄ < 1 on sym ∂x̂ over all x; T1–T2 need
  a bound only along the trajectory, in terms of err/n, and deliver exact landing on x^i (not just an L²
  bound to a). Mệnh đề 3 (μ > 1 repels) becomes T1(c).

**Measured** (`results/n3_rho_20261117/Q_SUMMARY.md`, 2026-11-17; same samples and seed as the q run;
sub500 n = 1000 with 41 off-atom, public n = 200 all off-atom). ϱ = |D − m*|/|x − x¹| and the radial ratio
rad₁ = ⟨ê, D − x¹⟩/|x − x¹| (two forward passes, no Jacobian).

| σ | ϱ on | ϱ off | ϱ public | rad₁ on | rad₁ off | rad₁ public | AUC ϱ | AUC rad₁ |
|---|---|---|---|---|---|---|---|---|
| 5.3 | 0.008 | 0.077 | 0.027 | 0.000 | 0.009 | 0.004 | 0.974 | 0.979 |
| 1.92 | 0.015 | 0.231 | 0.146 | 0.001 | 0.058 | 0.034 | 0.999 | 0.999 |
| 0.59 | 0.043 | 0.613 | 0.499 | 0.009 | 0.379 | 0.282 | 1.000 | 1.000 |
| 0.14 | 0.185 | 0.957 | 0.925 | 0.065 | 0.915 | 0.874 | 1.000 | 1.000 |
| 0.023 | 0.725 | 0.998 | 0.997 | 0.627 | 0.997 | 0.996 | 1.000 | 1.000 |
| 0.002 | 0.988 | 1.000 | 1.000 | 0.988 | 1.000 | 1.000 | 0.995 | 0.996 |

- T1 holds on the data. On-atom samples have ϱ < 1 at every step (100% of samples); off-atom samples and the
  public model have ϱ → 1 by σ ≈ 0.14 and rad₁ → 1, the non-landing regime of T1(c).
- The radial identity T1(a) predicts the change of log|x − x¹| from rad₁ almost exactly: −2.01 predicted vs
  −2.01 actual (σ 1.09 → 0.14) and −1.60 vs −1.54 (σ 0.14 → 0.002) for on-atom samples; −0.92 vs −0.91 and
  −0.06 vs −0.05 for off-atom samples.
- ϱ on-atom rises to ≈ 0.99 at the last step, so the constant-ϱ̄ hypothesis of T1(b) does not hold all the way
  to σ = 0. By then the sample is already within the on-atom criterion (d1/d2 < 1/3). The data support
  landing to that criterion, not exact landing.
- **Correction to the q numbers of E.** rad₁ − r₁ is the exact secant; the 4-point quadrature q₁ of the earlier
  run overestimates it at σ 0.1–1 (median |rad₁ − q₁ − r₁| on-atom 0.08–0.20 there, ≤ 0.03 elsewhere). The
  true secant slope of on-atom samples at σ 0.3–0.14 is ≈ 0.02–0.06, not 0.22. The conclusions of E
  (separation, late landing) stand; rad₁ is the quantity to report.

## T3. Landing and trapping for the discrete Heun sampler (2026-11-17)

**Why.** T1–T2 are about the continuous ODE. The experiments use the 18-step EDM Heun sampler, which ends with
a pure Euler step to σ = 0. T3 states the contraction and trapping results for the sampler itself, with an
arbitrary denoiser D (no continuity or Lipschitz assumption). Full statement and proof:
`proofs_E_R_T1_T2_2026-11-17.md`, section T3.

**Statement (short).** r_k = σ_{k+1}/σ_k, n_k = |x_k − x^i|, x̃_k the Euler predictor.
- (a) Exact affine form. x̃_k = r x_k + (1−r)D_k and x_{k+1} = r x_k + α D_k + β D̃_k, with
  α = (1−r)(2r−1)/(2r), β = (1−r)/(2r) and r + α + β = 1. The last step gives x_K = D_{K−1}.
  **α < 0 when r < 1/2**: in that case the corrector extrapolates past D_k.
- (b) One-step bound. If err ≤ ϱ_k·dist + γ at x_k and at x̃_k, then n_{k+1} ≤ c_k n_k + b_k with
  c_k = r + |α|ϱ + βϱ(r + (1−r)ϱ). b_k collects γ and the off-image mass ω.
- (c) Threshold. For r ≥ 1/2, c_k < 1 for every ϱ < 1. For r < 1/2, c_k < 1 iff
  ϱ < ϱ_crit(r) = (−1 + √(1 + 8r/(1−r)))/2 ∈ (0, 1).
- (d) Sharpness.
  - On the linear field, n_{k+1} = |p| n_k with |p| ≤ c_k. p is **negative** for r < 3 − 2√2 and some ϱ:
    the step overshoots the image.
  - Over all D with err ≤ ϱ·dist (d ≥ 2), the sharp one-step factor is c* = max_s Φ(s). It is attained,
    c* = c_k for r ≥ 1/2, and c* < c_k for r < 1/2. So for r < 1/2 the norm bound is not tight; the true
    threshold ϱ* satisfies ϱ_crit < ϱ* ≤ 1, with no closed form.
- (e) Multi-step certificate and discrete trapping.
  - The unrolled bound n_{K−1} ≤ ∏c_k·n_0 + Σ b_j ∏c_k gives the multi-step certificate.
  - Trapping: assume n_0 ≤ R ≤ g/4 and, at each step, (C1) ϱ_k R + γ_k + Ω(σ_k) ≤ R (this keeps x̃_k in the
    ball) and (C2) c_k R + … ≤ R. Then n_k ≤ R for all k. If also (C3) ϱ_{K−1}R + γ + Ω(σ_{K−1}) < g/4, the
    output is on-atom (d1/d2 < 1/3). The strict inequality in (C3) is needed.

**On the EDM schedule (18 steps, ρ = 7, σ ∈ [0.002, 80]).** r_k falls from 0.72 to 0.27. r_k ≥ 1/2 for the
first 12 steps (σ ≥ 0.30), so there any ϱ < 1 contracts. The last five Heun steps have r < 1/2:

| step | σ_k → σ_{k+1} | r_k | ϱ_crit |
|---|---|---|---|
| 12 | 0.296 → 0.140 | 0.471 | 0.924 |
| 13 | 0.140 → 0.060 | 0.430 | 0.825 |
| 14 | 0.060 → 0.023 | 0.383 | 0.720 |
| 15 | 0.023 → 0.0075 | 0.328 | 0.608 |
| 16 | 0.0075 → 0.002 | 0.266 | 0.487 |

**Reading against the data.**
- Measured median on-atom ϱ is 0.19 at σ = 0.14, below ϱ_crit for steps 12–13. It is 0.73 at σ = 0.023,
  above ϱ_crit = 0.61 for step 15. So the norm certificate (b)–(c) covers the trajectory down to σ ≈ 0.06,
  and fails for the last two Heun steps at the median.
- This does not contradict the measured contraction. By (d)(ii) the norm bound is loose exactly when r < 1/2,
  and the radial identity (T1(a)) is what the data follow. By then the sample is already within the on-atom
  criterion.
- **Practical consequence:** a coarser schedule in the last steps (smaller r) needs a smaller ϱ to be
  guaranteed to contract, and the Heun corrector can overshoot the image there.
- ~~Not yet measured: ϱ at the predictor x̃_k.~~ Measured below.

**Measured certificate** (2026-11-17, `results/n3_t3_20261117/Q_SUMMARY.md`; sub500 n = 1000 (41 off-atom),
public n = 500 (all off-atom); γ = 0, ω from the exact posterior; ϱ_k = max(ϱ at x_k, ϱ at x̃_k)). Medians,
on-atom unless marked:

| step | σ_k | r_k | ϱ_crit | ϱ at x_k | ϱ at x̃_k | c_k < 1 | actual n_{k+1}/n_k | bound (c_k n_k + b_k)/n_k | actual, public |
|---|---|---|---|---|---|---|---|---|---|
| 10 | 1.09 | 0.538 | 1 | 0.024 | 0.042 | 100% | 0.540 | 0.549 | 0.600 |
| 11 | 0.585 | 0.506 | 1 | 0.043 | 0.085 | 100% | 0.512 | 0.530 | 0.680 |
| 12 | 0.296 | 0.471 | 0.924 | 0.086 | 0.182 | 100% | 0.485 | 0.535 | 0.829 |
| 13 | 0.140 | 0.430 | 0.825 | 0.185 | 0.397 | 99.7% | 0.482 | 0.640 | 0.946 |
| 14 | 0.060 | 0.383 | 0.720 | 0.400 | 0.730 | 47% | 0.581 | 1.011 | 0.989 |
| 15 | 0.023 | 0.328 | 0.608 | 0.725 | 0.937 | 0% | 0.807 | 1.575 | 0.998 |
| 16 | 0.0075 | 0.266 | 0.487 | 0.929 | 0.990 | 0% | 0.953 | 2.265 | 1.000 |
| last (Euler) | 0.002 | – | – | – | – | – | 0.988 | 0.988 | 1.000 |

- **The bound is never violated.** Across 1500 trajectories × 17 Heun steps, no step has
  n_{k+1} > c_k n_k + b_k. This is the expected sanity check: (b) is an algebraic inequality.
- **The predictor is the binding point.** ϱ at x̃_k is larger than ϱ at x_k for every on-atom sample and
  step. It is about equal to ϱ at x_{k+1}, because x̃_k is evaluated at σ_{k+1}. ω/n is 0 at these steps:
  sub500 images are far apart.
- **The certificate covers the trajectory down to σ ≈ 0.14** (steps 0–13: c_k < 1 for ≥ 99.7% of on-atom
  samples). It covers half the samples at step 14 and none at steps 15–16. There ϱ at x̃_k exceeds ϱ_crit,
  and the bound is > 1 while the actual factor is 0.58, 0.81 and 0.95. This is the looseness that (d)(ii)
  predicts for r < 1/2.
- **On-atom vs off-atom.** On-atom samples contract by a factor 0.48–0.58 per step at σ 0.06–0.3. Off-atom
  and public samples have actual ≈ 1 from σ ≈ 0.06 (no landing).
- **Consequence for the paper.** A rigorous per-trajectory certificate holds where the image is selected
  (σ ≥ 0.14). The last three steps need the sharp factor c* or the radial identity, not the norm bound.

**Step-count ablation: a prediction of T3, tested** (2026-11-17, `results/n3_steps_20261117`; same
initial noise, same sub500 and public models, 18 / 36 / 64 Heun steps).

- **Prediction.** More steps raise r_k at the end of the schedule. Once every r_k ≥ 1/2, (c) gives c_k < 1
  for any ϱ < 1, so the certificate should cover the whole trajectory. The memorization outcome should not
  change.
- **Result.** Each row is one step count; "certified" is the fraction of on-atom samples with c_k < 1 at
  every step:

| Heun steps | min r_k | off-atom (sub500) | certified | bound violations | same image as 18 steps (sub500 / public) |
|---|---|---|---|---|---|
| 18 | 0.266 | 4.1% | 0% | 0 | – |
| 36 | 0.509 | 4.0% | 99.5% | 0 | 99.4% / 94.8% |
| 64 | 0.682 | 3.9% | 99.5% | 0 | 99.3% / 94.4% |

- At 36 and 64 steps every r_k ≥ 1/2, and the T3 certificate holds at every step for 99.5% of on-atom
  samples, down to σ = 0.002. At 18 steps it fails at the last steps for all of them.
- Memorization and the selected image are unchanged (99.3–99.4% the same image for sub500). So the
  failure at 18 steps comes from the discretisation and the norm bound, not from the model: the coarse last
  steps (r < 1/2, α < 0) are where the Heun corrector can extrapolate past the image.
- At 64 steps, ϱ at the predictor still rises to 0.99 at the end and the per-step factor rises to 0.99. The
  late contraction weakens but stays < 1, consistent with the continuous T1/T2 picture.

## Verification (math-olympiad workflow, 2026-11-12)

Nine verifiers, three per proposition, each with fresh context and no tools. They saw only the
statement and the proof. The checks were:
- P: general attack, hypotheses, proves-too-much;
- L: general attack, small cases, short steps;
- T: general attack, landing bound, definitions.

| | Verdicts | Findings (all fixed above unless marked GAP) |
|---|---|---|
| P | GAP ×3 | (i)–(iii) hold. The informal "grow like 1/σ" / "equivalently ρ bounded away from 0" was wrong, shown by the counterexample D = (1−1/log(1/σ))x. (iv) rate wrong at ties; now a lower bound. Existence at σ = 0 comes from the growth bound. e^{dA} makes (iii) qualitative. Not specific to memorization. |
| L | CORRECT ×1, GAP ×2 | Analytic core and sharp constant confirmed. Need Y₁ to be an atom (midpoint counterexample). Z need not converge. Time regularity. Rename ε → η. (c) weakened to max. |
| T | INCORRECT ×2, GAP ×1 | (ii)(b) false without the residual term (counterexample D = x − δσ). (ii)(a) used the wrong reference path. (i) "lower envelope" was backwards: "=L" upper-bounds the CDF of t_sel. ≤ → <. Caveat vacuous except at ties. (iii) is a remark. |

**Round 2** (same day). Six fresh verifiers, two per proposition, ran on the revised statements.
None of them found a counterexample to a formal claim. The wording fixes are marked **[rev2]** above.

| | Verdicts | Findings |
|---|---|---|
| P | GAP ×2 | (i)–(iii) hold, with no substitute breaking (iii). The proof of (iv) cited J_{D*} ⪰ 0, which is the wrong direction; replaced by the zero-eigenvalue / \|x\|→∞ argument. "Sufficient side" needs the bound on the segment or tube, not one trajectory. "Necessary" is conditional on x(0) existing (uniform growth). Joint continuity is needed. |
| L | CORRECT ×2 | Sharpness example fixed (N = 1, centred at x¹). Joint continuity in (x, t). Define "on-atom". Restarting at t₁ with any exact Y is legitimate. |
| T | CORRECT ×1, GAP ×1 | The decomposition, (ii)(a) and (ii)(b) hold; (ii)(b) is sharp. "A → 1 automatically" needs Z₁ to exist and not lie on ties (counterexample: oscillating field). The inf must run over later t. Add the convention for t_sel = 1. |

Vote tally on the current statements:
- L: 3 CORRECT (one in round 1 on the essentially unchanged core, two in round 2), with no hole.
- T: 1 CORRECT, 1 GAP.
- P: 2 GAP, both on wording.

By the workflow's rule (4 HOLDS to confirm, 2 HOLE to refute), none is formally confirmed yet. No
verifier refuted a formal claim in round 2.

**Round 3** (same day). Eight fresh verifiers ran on the [rev2] statements. Each was told to report
HOLE only for a false claim or an unproven load-bearing step.

| | Verdicts | Findings |
|---|---|---|
| P | HOLDS ×3, HOLE ×1 | All four agree that (i)–(iv) hold. The hole was the READING sentence "x-prediction ⇒ ∫ρ′/σ = ∞ always", refuted by D = x; corrected [rev3]. Sufficient-side rate sharpened to (σ_a/σ_b)^{ρ₀}. Sign of ρ′; absolute continuity suffices for the null-set claims; Φ is onto. |
| L | HOLDS ×1 | No hole. Added an explicit non-convergence example. |
| T | HOLDS ×3 | No hole. Uniform form of the Voronoi fact; measurability via space-time openness; define N(t); exact swap integration. Stiffness of the exact field near t = 1 is not a hidden requirement of (ii)(a). |

**Tally on the current statements:**
- **L: confirmed** (4 HOLDS: one in round 1, two in round 2, one in round 3; 0 holes on the current
  version).
- **T: confirmed** (4 HOLDS: one in round 2, three in round 3). The round-2 GAP was fixed in [rev2].
- **P, formal parts (i)–(iv): confirmed.** Four round-3 verifiers agree they hold, and no verifier in
  any round broke them. One READING sentence was refuted and then corrected; the corrected sentence
  has not been re-verified.

"Confirmed" means it passed the adversarial workflow. It is not the author's verification, which is
still required. The open GAPs below remain.

**E and R** (2026-11-16). Two solvers each, no tools. Both solvers of E found that the lower bound in
(b) needs Φ⁺ in the residual term; both solvers of R found that (d) as first posed was false and needed
(H), with the counterexample now in (d3). Four fresh verifiers each on the cleaned statements:

| | Verdicts | Notes |
|---|---|---|
| E | HOLDS ×4 | (★), (a), (d) re-derived independently; examples recomputed; own tests with b ≠ 0 and q > 1. Cosmetic: (c) runs against the sampling direction; Λ^± depend on the trajectory; h ≠ 0 in the (d) example. |
| R | HOLDS ×4 | Sharpness and (d3) recomputed; own N = 3 tests. Cosmetic: lower bound in (a) holds for any i; δ_i > 0 uses the hypothesis plus distinctness; O, A finite. |

**E and R: confirmed** (4 HOLDS each, 0 holes).

**T1 and T2** (2026-11-17). Two solvers each (both found the zero-set and continuation details and fixed
them); four fresh verifiers each on the cleaned statements.

| | Verdicts | Notes |
|---|---|---|
| T1 | HOLDS ×4 | Own tests: N = 2 crossing, slow ϱ → 1, δ < 0, rotation. Not a hole but must be stated: ϱ̄ < 1 is sharp only among constants, not necessary; conditions are along the trajectory; ∫δ⁺/ε is improper. |
| T2 | HOLDS ×4 | (i) attained with equality for N = 2; σ* checked (1/q ≥ 8); barrier direction checked. Notes: (iv) covers only Ω, γ < (1 − ϱ̄)r/2 is a separate requirement; "r < g/2 needed" means "needed for a non-trivial (i)"; the factor 4 in σ* is not tight. |

**T1 and T2: confirmed** (4 HOLDS each, 0 holes).

**T3** (2026-11-17). Three solvers (direct algebra, extremal case, boundary cases), all complete and in
agreement. All three found the same error in the posed (d)(i): n_{k+1} = p·n_k fails when p < 0; corrected to
|p|. Four fresh verifiers on the cleaned statement:

| | Verdicts | Notes |
|---|---|---|
| T3 | HOLDS ×4 | All algebra recomputed (α, β, ϱ_crit, discriminant, example p = −0.4625). Ω used only at points shown to be in the ball. Notes, folded into the statement: (d)(ii) is a one-step sup over D and x_k with n_k > 0 (along a full trajectory, earlier values of D must be chosen so that x̃_{k−1} ≠ x_k; possible); N = 1 conventions; ρ in (d)(ii) ranges over [0,1), so ϱ* ≤ 1 is automatic; d ≥ 2 is needed; the tail lemma only needs R < g. |

**T3: confirmed** (4 HOLDS, 0 holes).

## To verify (author)

- [ ] P (i)–(iv) as revised, in particular the extension to σ = 0 and the density bound.
- [ ] L, and the GAP on almost-sure convergence of the exact path (needed for L and for the basins in T).
- [ ] T (i) decomposition A − F, and (ii)(b) with the residual term.
- [ ] Al-Jaff's parametrization order: needs the PDF.
- [ ] E (★) and (a)–(d), in particular the sign of the residual term and Φ⁺ in the lower bound of (b).
- [ ] R (a)–(d), and whether (H) holds on the sub500 data (else use the d_i version).
- [x] T1 (a)–(d) and T2 (i)–(iv) (verified by the author 2026-11-19; in the paper as Theorem thm:relerr and
  Proposition prop:trap, next to the existing transfer results).
- [x] T3 (a)–(e) (verified by the author 2026-11-19; Proposition prop:heun).
