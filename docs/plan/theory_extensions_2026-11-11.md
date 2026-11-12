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

## To verify (author)

- [ ] P (i)–(iv) as revised, in particular the extension to σ = 0 and the density bound.
- [ ] L, and the GAP on almost-sure convergence of the exact path (needed for L and for the basins in T).
- [ ] T (i) decomposition A − F, and (ii)(b) with the residual term.
- [ ] Al-Jaff's parametrization order: needs the PDF.
