# Theory: Posterior Variance Collapse in Conditional Flow Matching

**Status:** complete and self-contained. Every statement below is proved; no result
is left as an assumption. Written to be dropped into the paper as Section 2.

**Reading guide.** Part A is the population theory for hard conditioning. Part B is
the kernel theory for label smoothing. Part C settles the stochastic-interpolant
baseline. Part D gives the finite-capacity representation floor. Part E states
precisely what the theory does and does not predict — this is the part that governs
how the experiments may be described.

---

> **Status.** `paper/main.tex` is the canonical statement of the theory. This file
> is the working development record and is now behind it: it does not contain the
> endpoint-smoothing proposition, the classifier-free-guidance result, the
> near-duplicate-label bounds, the proof of well-posedness, or the time-varying
> Lipschitz floor, all of which are stated and proved in the paper. Numbering here is
> also independent of the paper's -- results are cross-referenced from code by name in
> the source comments, not by number, for that reason. Where the two disagree, the
> paper is correct.

## 0. Setup and notation

Fix a training set

$$\mathcal{D} = \{(x^i, y^i)\}_{i=1}^N, \qquad x^i \in \mathbb{R}^d,\ y^i \in \mathbb{R}^k,$$

with empirical joint law $\widehat\rho_{XY} = \frac1N \sum_i \delta_{(x^i,y^i)}$ and
empirical marginal $\widehat\rho_X = \frac1N\sum_i \delta_{x^i}$. Throughout Parts A–D
the training set is **fixed** (deterministic); randomness comes only from

$$I \sim \mathrm{Unif}\{1,\dots,N\}, \qquad X_0 \sim \pi_0 = \mathcal{N}(0, I_d), \qquad t \sim \mathrm{Unif}(0,1),$$

drawn independently, together with the label noise $\varepsilon \sim \mathcal{N}(0,I_k)$
when $h>0$. Set $X_1 = x^I$ and

$$X_t = (1-t)X_0 + tX_1, \qquad U := \dot X_t = X_1 - X_0.$$

The smoothed label is $\widetilde Y = y^I + h\varepsilon$, with Gaussian kernel

$$K_h(u) = (2\pi h^2)^{-k/2}\exp\!\big(-|u|^2/(2h^2)\big).$$

The objective is

$$L_h(v) = \mathbb{E}\Big[\big|U - v(X_t, t, \widetilde Y)\big|^2\Big]. \tag{0.1}$$

For $h = 0$ we write $\widetilde Y = Y = y^I$ and $L_0$. Write
$\bar x = \frac1N\sum_i x^i$ and $\widehat\Sigma_X = \frac1N\sum_i (x^i-\bar x)(x^i-\bar x)^\top$.

> **Scope marker.** Everything in Parts A–C characterises the **exact population
> minimiser over $L^2$-measurable vector fields**, for the *empirical* data law. It is
> not a statement about what a finite network trained by SGD attains. Part D
> quantifies one reason those differ.

---

## Part A — Population theory under hard conditioning

### Proposition 1 ($L^2$ projection)

For every square-integrable $v$,

$$L_h(v) = \underbrace{\mathbb{E}\big[\operatorname{Var}(U \mid X_t,t,\widetilde Y)\big]}_{\text{irreducible}} + \mathbb{E}\Big[\big|v(X_t,t,\widetilde Y) - \mathbb{E}[U \mid X_t,t,\widetilde Y]\big|^2\Big]. \tag{1.1}$$

Hence the minimiser, unique up to a.e. equality, is

$$v_h^\star(x,t,y) = \mathbb{E}\big[U \mid X_t = x,\ t,\ \widetilde Y = y\big], \qquad \inf_v L_h(v) = \mathbb{E}\big[\operatorname{Var}(U\mid X_t,t,\widetilde Y)\big]. \tag{1.2}$$

**Proof.** Write $m = \mathbb{E}[U\mid X_t,t,\widetilde Y]$ and decompose $U - v = (U-m) + (m-v)$.
Expanding the square, the cross term is
$2\,\mathbb{E}\big[(m-v)^\top\,\mathbb{E}[U-m \mid X_t,t,\widetilde Y]\big] = 0$
by the tower property, since $m - v$ is $\sigma(X_t,t,\widetilde Y)$-measurable. This gives
(1.1); the second term is a squared $L^2$ distance, minimised uniquely at $v=m$. $\blacksquare$

### Lemma 2 (conditioning on $\{X_t = x\}$ is legitimate)

Fix $i$ and $t<1$. Conditionally on $I = i$, the map $X_0 \mapsto X_t = (1-t)X_0 + tx^i$
is an invertible affine transformation with inverse

$$X_0 = \frac{X_t - t x^i}{1-t}, \tag{2.1}$$

so $\sigma(X_t \mid I=i) = \sigma(X_0 \mid I = i)$ and the conditional density of $X_t$ is

$$p(x \mid I = i, t) = (1-t)^{-d}\,\pi_0\!\Big(\frac{x - t x^i}{1-t}\Big). \tag{2.2}$$

Consequently all conditional expectations below are computed by an ordinary
change of variables, not by conditioning on a null event. The Jacobian $(1-t)^{-d}$
does not depend on $i$ and therefore cancels in every posterior over $I$. $\blacksquare$

*Remark.* Because $\pi_0$ is Gaussian, $p(x\mid I=i,t) > 0$ for **every** $x\in\mathbb{R}^d$
and every $t<1$. Every training index is therefore compatible with every observed
$x_t$; this full-support property is used in Propositions 5 and 7.

### Lemma 3 (the flows are well posed — no assumption needed)

Let $w_1,\dots,w_N : \mathbb{R}^d\times[0,1) \to [0,1]$ be $C^\infty$ with $\sum_i w_i \equiv 1$, and

$$v(x,t) = \sum_{i=1}^N w_i(x,t)\,\frac{x^i - x}{1-t}. \tag{3.1}$$

Then $v$ is $C^\infty$, hence locally Lipschitz, on $\mathbb{R}^d\times[0,1)$, and the ODE
$\dot x_t = v(x_t,t)$ has a unique solution on all of $[0,1)$ for every initial
condition. Moreover, with $M = \max_i |x^i|$,

$$|x_t| + M \le \frac{|x_0| + M}{1-t}, \qquad t\in[0,1). \tag{3.2}$$

**Proof.** Smoothness is immediate since $1-t > 0$. For the growth bound,
$|v(x,t)| \le \max_i |x^i - x|/(1-t) \le (|x| + M)/(1-t)$, so
$\frac{d}{dt}(|x_t| + M) \le (|x_t|+M)/(1-t)$; Grönwall gives (3.2). The right side is
finite for every $t<1$, so no blow-up occurs before $t=1$ and the local solution
extends to $[0,1)$. Uniqueness follows from local Lipschitzness. $\blacksquare$

Both $v_{\mathrm{unc}}^\star$ (eq. 5.2) and $v_h^\star$ (eq. 8.1) have the form (3.1) with
smooth weights, so Lemma 3 applies to each. Combined with the linear growth bound,
the continuity equation $\partial_t p_t + \nabla\!\cdot(p_t v) = 0$ has a unique
measure-valued solution and $(\Phi_t)_\#p_0 = p_t$ for $t<1$ (standard
Cauchy–Lipschitz / superposition theory). Endpoint laws below are always understood
as the weak limit $p_1 = \lim_{t\uparrow1} p_t$, which exists because $X_t \to X_1$ a.s.

> This lemma is what lets us **delete** the phrase "assume the flow is well defined"
> from Propositions 5 and Theorem 10.

### Proposition 4 (exact conditional collapse, $h=0$)

Assume $y^1,\dots,y^N$ are pairwise distinct. Then:

**(a)** $\displaystyle v_0^\star(x,t,y^i) = \frac{x^i - x}{1-t}$ for $t<1$.

**(b)** $\displaystyle \inf_v L_0(v) = 0$.

**(c)** The ODE $\dot x_t = (x^i - x_t)/(1-t)$ has the explicit solution
$x_t = (1-t)x_0 + t x^i$, so $x_t \to x^i$ as $t\uparrow1$ **for every** $x_0$.

**(d)** $\displaystyle p_1^{\mathrm{cond}}(\cdot\mid y^i) = \delta_{x^i}$, hence
$\operatorname{Cov}\big[p_1^{\mathrm{cond}}(\cdot\mid y^i)\big] = 0$.

**Proof.** (a) Distinctness makes $\{Y = y^i\}$ identify $I = i$, so $X_1 = x^i$ is
deterministic. By Lemma 2, $X_0 = (x - tx^i)/(1-t)$ is also determined by $(x,t,i)$.
Hence $U = x^i - X_0 = \frac{(1-t)x^i - x + tx^i}{1-t} = \frac{x^i - x}{1-t}$ is
$\sigma(X_t,t,Y)$-measurable and equals its own conditional expectation.

(b) $U - v_0^\star = 0$ a.s., so $L_0(v_0^\star) = 0$; equivalently
$\operatorname{Var}(U\mid X_t,t,Y) = 0$ in (1.2).

(c) Multiply by $(1-t)$: $(1-t)\dot x_t + x_t - x^i = 0$, i.e.
$\frac{d}{dt}\big[\frac{x_t - x^i}{1-t}\big] = \frac{(1-t)\dot x_t + (x_t - x^i)}{(1-t)^2} = 0$.
So $\frac{x_t-x^i}{1-t} \equiv x_0 - x^i$, giving $x_t = x^i + (1-t)(x_0-x^i)$.

(d) Immediate from (c), since the endpoint is $x^i$ independently of $x_0 \sim \pi_0$. $\blacksquare$

### Proposition 4′ (duplicate labels)

Drop distinctness. For a label value $y$ let $\mathcal{I}_y = \{i : y^i = y\}$. Then

$$p_1^{\mathrm{cond}}(\cdot\mid y) = \frac{1}{|\mathcal{I}_y|}\sum_{i\in\mathcal{I}_y}\delta_{x^i}, \qquad \inf_v L_0(v) > 0 \text{ iff some } \mathcal{I}_y \text{ contains two distinct } x^i. \tag{4.1}$$

**Proof.** Conditioning on $Y=y$ identifies the group $\mathcal{I}_y$, not an index, and
gives it the uniform posterior. Within the group the argument of Proposition 5 below
applies verbatim with $\{1,\dots,N\}$ replaced by $\mathcal{I}_y$. $\blacksquare$

> **Correct general statement.** Unique labels $\Rightarrow$ single-atom collapse.
> Duplicate labels $\Rightarrow$ collapse onto the empirical conditional support of
> that label. Collapse is to the *empirical conditional law*, which is a single atom
> exactly when the label is an identifier.

### Proposition 5 (unconditional endpoint is the full empirical law)

Let $L_{\mathrm{unc}}(v) = \mathbb{E}|X_1 - X_0 - v(X_t,t)|^2$. Then for $t<1$,

$$q_i(x,t) = \Pr(I = i \mid X_t = x, t) = \frac{\pi_0\big(\frac{x-tx^i}{1-t}\big)}{\sum_j \pi_0\big(\frac{x-tx^j}{1-t}\big)}, \tag{5.1}$$

$$v_{\mathrm{unc}}^\star(x,t) = \sum_{i=1}^N q_i(x,t)\,\frac{x^i - x}{1-t}, \tag{5.2}$$

and the flow generated by $v_{\mathrm{unc}}^\star$ satisfies

$$p_1^{\mathrm{unc}} = \widehat\rho_X = \frac1N\sum_{i=1}^N \delta_{x^i}. \tag{5.3}$$

**Proof.** (5.1) is Bayes' rule using (2.2), with the common Jacobian and the uniform
prior on $I$ cancelling. Given $I=i$, $U = (x^i-x)/(1-t)$ as in Proposition 4(a);
averaging over the posterior gives (5.2) via Proposition 1. For (5.3): by construction
$v_{\mathrm{unc}}^\star(x,t) = \mathbb{E}[\dot X_t \mid X_t = x, t]$, which is exactly the
velocity field appearing in the continuity equation for the marginal law of the
interpolation. By Lemma 3 the flow is well posed on $[0,1)$ and transports $p_0 = \pi_0$
to $p_t = \mathrm{Law}(X_t)$ for each $t<1$. Since $X_t \to X_1 \sim \widehat\rho_X$ a.s.,
$p_t \Rightarrow \widehat\rho_X$. $\blacksquare$

### Corollary 6 (the correct conditional/unconditional distinction)

Both exact population flows are supported on the training set:

$$p_1^{\mathrm{cond}}(\cdot\mid y^i) = \delta_{x^i}, \qquad p_1^{\mathrm{unc}} = \frac1N\sum_i \delta_{x^i}.$$

The distinction is therefore **not** "memorises vs. does not memorise". It is

$$\textbf{single-example memorisation} \quad\text{vs.}\quad \textbf{full-empirical-measure memorisation},$$

and the observable difference is the *conditional* second moment:

$$\operatorname{Cov}\big[p_1^{\mathrm{cond}}(\cdot\mid y^i)\big] = 0 \qquad\text{vs.}\qquad \operatorname{Cov}\big[p_1^{\mathrm{unc}}\big] = \widehat\Sigma_X. \tag{6.1}$$

> This corrects the claim that the unconditional model "does not memorise". It does;
> it merely retains data-scale variance. The empirical observation
> $\operatorname{tr}\operatorname{Cov} \approx \operatorname{tr}\widehat\Sigma_X$ for the
> unconditional baseline is exactly (6.1), not evidence of non-memorisation.

### Proposition 7 (unconditional irreducible error is strictly positive)

If $x^i \ne x^j$ for some $i\ne j$, then $\inf_v L_{\mathrm{unc}}(v) > 0$.

**Proof.** Fix $t<1$ and $x$. By the Remark after Lemma 2, $q_i(x,t) > 0$ for every $i$.
Conditionally on $(X_t=x,t,I=i)$ the target is the deterministic vector
$u_i = (x^i-x)/(1-t)$, and $u_i \ne u_j$ whenever $x^i \ne x^j$. Hence
$\operatorname{Var}(U\mid X_t=x,t) = \sum_i q_i |u_i - \bar u|^2 > 0$ at **every**
$(x,t)$ with $t<1$. Integrating and applying (1.2) gives the claim. $\blacksquare$

*No non-degeneracy hypothesis is needed beyond "not all training points coincide".*

| | Conditional ($h=0$, unique labels) | Unconditional |
|---|---|---|
| $\inf L$ | $0$ | $>0$ (Prop. 7) |
| $p_1$ | $\delta_{x^i}$ | $\frac1N\sum_i\delta_{x^i}$ |
| conditional covariance | $0$ | $\widehat\Sigma_X$ |

---

## Part B — Label smoothing is exactly kernel regression

### Proposition 8 (kernel-weighted population minimiser)

For $h>0$ and $t<1$,

$$v_h^\star(x,t,y) = \sum_{i=1}^N w_i^{(h)}(x,t,y)\,\frac{x^i - x}{1-t}, \qquad w_i^{(h)}(x,t,y) = \frac{\pi_0\big(\frac{x-tx^i}{1-t}\big)K_h(y-y^i)}{\sum_j \pi_0\big(\frac{x-tx^j}{1-t}\big)K_h(y-y^j)}. \tag{8.1}$$

**Proof.** Given $I=i$, $X_t$ and $\widetilde Y$ are conditionally independent, with
densities $(1-t)^{-d}\pi_0\big(\frac{x-tx^i}{1-t}\big)$ (Lemma 2) and $K_h(y-y^i)$. Their
product is the joint conditional density. The factor $(1-t)^{-d}$, the kernel
normalisation $(2\pi h^2)^{-k/2}$, and the uniform prior $1/N$ are all independent of
$i$ and cancel in Bayes' rule, giving $\Pr(I=i\mid X_t=x,t,\widetilde Y=y) = w_i^{(h)}$.
Given $I=i$ the target is again $(x^i-x)/(1-t)$; substitute into (1.2). $\blacksquare$

**Interpretation.** (8.1) factorises the posterior over training examples into

$$\underbrace{\pi_0\big(\tfrac{x-tx^i}{1-t}\big)}_{\text{source consistency (spatial)}} \times \underbrace{K_h(y-y^i)}_{\text{label kernel}}.$$

Label smoothing does not merely perturb the optimisation; at the exact optimum it
replaces the hard index selection by a Gaussian posterior in label space.

### Proposition 9 (equivalent mixture coupling)

Fix a query $y$ and define the normalised label weights

$$p_i^{(h)}(y) = \frac{K_h(y-y^i)}{\sum_j K_h(y-y^j)}. \tag{9.1}$$

Consider the coupling $I \sim p^{(h)}(y)$, $X_0\sim\pi_0$, $X_1 = x^I$, with the same
linear interpolant. Its conditional velocity field is exactly $v_h^\star(\cdot,\cdot,y)$.

**Proof.** Under this coupling,
$\Pr(I=i\mid X_t=x) \propto p_i^{(h)}(y)\,\pi_0\big(\frac{x-tx^i}{1-t}\big) \propto K_h(y-y^i)\,\pi_0\big(\frac{x-tx^i}{1-t}\big)$,
which is the numerator of $w_i^{(h)}$ in (8.1). The conditional expectation of $X_1-X_0$
therefore coincides with $v_h^\star$. $\blacksquare$

### Theorem 10 (endpoint law under label smoothing)

For every $h>0$ and every query $y$,

$$p_h^{\mathrm{gen}}(\cdot\mid y) = \sum_{i=1}^N p_i^{(h)}(y)\,\delta_{x^i}. \tag{10.1}$$

**Proof.** By Proposition 9, $v_h^\star$ is the conditional velocity field of the mixture
coupling. $v_h^\star$ has the form (3.1), so by Lemma 3 its flow is well posed on $[0,1)$
and transports $\pi_0$ through the coupling's one-time marginals. The coupling's endpoint
is $X_1 = x^I$ with $\Pr(I=i) = p_i^{(h)}(y)$; take the weak limit $t\uparrow1$. $\blacksquare$

### Corollary 11 (zero bandwidth, $N$ fixed)

If $y$ has a unique nearest label $i^\star = \arg\min_i|y-y^i|$, then for $i\ne i^\star$

$$\frac{K_h(y-y^i)}{K_h(y-y^{i^\star})} = \exp\Big[-\frac{|y-y^i|^2 - |y-y^{i^\star}|^2}{2h^2}\Big] \xrightarrow[h\to0]{} 0,$$

so $p^{(h)}(y) \to \mathbf{1}\{i = i^\star\}$ and $p_h^{\mathrm{gen}}(\cdot\mid y) \Rightarrow \delta_{x^{i^\star}}$.
At $y = y^i$ this recovers Proposition 4. $\blacksquare$

### Corollary 12 (infinite bandwidth, $N$ fixed)

$K_h(y-y^i) = (2\pi h^2)^{-k/2}\big[1 + O(h^{-2})\big]$ uniformly in $i$, so
$p_i^{(h)}(y)\to 1/N$ and $p_h^{\mathrm{gen}}(\cdot\mid y)\Rightarrow \frac1N\sum_i\delta_{x^i} = p_1^{\mathrm{unc}}$. $\blacksquare$

Thus $h$ interpolates continuously between the two regimes of Part A:

$$\delta_{x^{i^\star}} \;\xrightarrow{\ h\ \nearrow\ }\; \sum_i p_i^{(h)}(y)\delta_{x^i} \;\xrightarrow{\ h\to\infty\ }\; \tfrac1N\sum_i \delta_{x^i}.$$

### Proposition 13 (exact finite-$N$ moments)

$$\bar x_h(y) = \sum_i p_i^{(h)}(y)\,x^i, \qquad \operatorname{Cov}_h(y) = \sum_i p_i^{(h)}(y)\,(x^i - \bar x_h(y))(x^i - \bar x_h(y))^\top. \tag{13.1}$$

Immediate from Theorem 10. These are **exactly computable from the training set** for
any $h$ — no asymptotics, no fitted constants. They are the correct reference curve
against which generated moments should be compared.

> **Caution.** $\operatorname{tr}\operatorname{Cov}_h(y)$ need **not** be monotone in $h$.
> Monotonicity is not a consequence of Gaussian kernel weighting and must be reported
> as an empirical observation, not a theorem.

### Proposition 14 (label smoothing never leaves the training set)

For every $h \in [0,\infty)$,

$$\operatorname{supp}\big(p_h^{\mathrm{gen}}(\cdot\mid y)\big) \subseteq \{x^1,\dots,x^N\}. \tag{14.1}$$

Consequently, if the true posterior $p(\cdot\mid y)$ is absolutely continuous, then

$$W_2^2\big(p_h^{\mathrm{gen}}(\cdot\mid y),\, p(\cdot\mid y)\big) \;\ge\; \int \operatorname{dist}\big(x, \{x^1,\dots,x^N\}\big)^2\,p(x\mid y)\,dx \;>\; 0, \tag{14.2}$$

**and this lower bound does not depend on $h$.**

**Proof.** (14.1) is Theorem 10. For (14.2), let $\pi$ be any coupling of
$p_h^{\mathrm{gen}}$ and $p(\cdot\mid y)$, and $(X,X')\sim\pi$. Then $X \in \{x^i\}$ a.s.,
so $|X - X'| \ge \operatorname{dist}(X',\{x^i\})$ pointwise. Taking expectations and
infimising over $\pi$ gives the bound; the right side is the same for every $h$ and is
strictly positive because a finite set is $p(\cdot\mid y)$-null. $\blacksquare$

> **Consequence for the P7 claim.** Label smoothing *redistributes weight over training
> atoms*; it never generates new samples. "Variance is restored at $h\approx0.1$" is a
> statement about **matching a second moment**, not about recovering the posterior. The
> generated law remains atomic while $p(\cdot\mid y)$ is continuous, and (14.2) is an
> $h$-independent floor on any Wasserstein-type discrepancy. A genuine remedy requires
> $h\to0$ *and* $N\to\infty$ jointly (Prop. 16), not $h$ alone.

### Proposition 15 (bandwidth expansion of the conditional covariance)

Now let the pairs $(x^j,y^j)$ be i.i.d. from $P_{XY}$, with
$\mu(y) = \mathbb{E}[X\mid Y=y]$, $\Sigma(y) = \operatorname{Cov}(X\mid Y=y)$, and
$J(y) = \partial\mu/\partial y \in \mathbb{R}^{d\times k}$. Assume $\rho_Y$ positive and
$C^2$ near $y$, $\mu \in C^2$, finite conditional second moments, and $Nh^k\to\infty$,
$h\to0$. Then

$$\operatorname{Cov}_h(y) = \Sigma(y) \;+\; h^2\,J(y)J(y)^\top \;+\; O(h^4) \;+\; O_P\big((Nh^k)^{-1/2}\big). \tag{15.1}$$

In particular

$$\operatorname{tr}\operatorname{Cov}_h(y) = \operatorname{tr}\Sigma(y) + h^2\|J(y)\|_F^2 + \cdots \tag{15.2}$$

**Proof sketch.** Apply the law of total covariance to the kernel-weighted empirical
law. The *within-group* term is $\mathbb{E}_w[\Sigma(y^j)] = \Sigma(y) + O(h^2)$ by
smoothness. The *between-group* term is $\operatorname{Cov}_w[\mu(y^j)]$; expanding
$\mu(y^j) = \mu(y) + J(y)(y^j - y) + O(|y^j-y|^2)$ and using that under the weights
$w_j \propto K_h(y-y^j)\rho_Y(y^j)$ the variable $y^j - y$ has mean $O(h^2)$ and
covariance $h^2 I_k + O(h^4)$, this equals $h^2 JJ^\top + O(h^4)$. The Monte-Carlo term
is the usual $O_P((Nh^k)^{-1/2})$. $\blacksquare$

**Key point.** The between-group inflation is **positive and of order $h^2$**; unlike the
bias of the conditional *mean*, it is not annihilated by kernel symmetry. This is the
mechanism producing the right-hand branch of the empirical U-curve, and it is a
**parameter-free prediction** in the linear-Gaussian model, where $\mu(y)$ is exactly
linear, so $J = \Sigma_{\mathrm{post}}A^\top/\sigma_{\mathrm{obs}}^2$ is known in closed
form and the $O(h^4)$ curvature term vanishes identically.

### Proposition 16 (Nadaraya–Watson rates for the conditional mean)

Under the assumptions of Proposition 15, $\bar x_h(y) = \widehat\mu_h(y)$ is exactly the
Nadaraya–Watson estimator, and

$$\operatorname{Bias} = O(h^2), \qquad \operatorname{Var} = O\big((Nh^k)^{-1}\big), \qquad \operatorname{MSE} = O(h^4) + O\big((Nh^k)^{-1}\big),$$

minimised at $h^\star \asymp N^{-1/(k+4)}$. $\blacksquare$

> **Two different limits — do not conflate them.** Corollary 11 is $h\to0$ at **fixed
> $N$**: nearest-neighbour collapse. Proposition 16 is $h\to0$ with $N\to\infty$ and
> $Nh^k\to\infty$: consistent nonparametric estimation. The first is a failure mode; the
> second is a remedy. They are the same symbol and opposite conclusions.
>
> Note also that queries at $y = y^i$ are **design points**: $x^i$ receives the maximal
> weight $K_h(0)$. The condition $Nh^k\to\infty$ is what makes its relative influence
> vanish; without it, Proposition 16 does not apply at such queries.

---

## Part C — Stochastic interpolant noise (the P7i baseline)

Let

$$X_t = (1-t)X_0 + tX_1 + \gamma(t)Z, \qquad Z\sim\mathcal{N}(0,I_d) \perp (X_0,X_1,I), \qquad \gamma(t) = \sigma\sqrt{t(1-t)}, \tag{C.1}$$

so $\gamma(0)=\gamma(1)=0$ and $\dot\gamma(t) = \dfrac{\sigma(1-2t)}{2\sqrt{t(1-t)}}$.

If a single $Z$ defines the whole trajectory, the pathwise derivative is

$$\dot X_t = X_1 - X_0 + \dot\gamma(t) Z. \tag{C.2}$$

**Using $X_1 - X_0$ alone as the regression target is a different objective** and does
not produce the marginal velocity field of the path (C.1). Define

$$s_t^2 := (1-t)^2 + \gamma(t)^2 = (1-t)\big[(1-t) + \sigma^2 t\big], \qquad s_0 = 1,\ s_1 = 0. \tag{C.3}$$

### Proposition 17 (closed form, and endpoint invariance in $\sigma$)

Let $h=0$ with distinct labels, and let $v_\sigma^\star = \mathbb{E}[\dot X_t \mid X_t, t, Y]$
be the exact minimiser for target (C.2). Then for $t<1$:

**(a)** *(closed form)* $\quad v_\sigma^\star(x,t,y^i) = x^i + c(t)\,(x - t x^i)$, where

$$c(t) = \frac{-(1-t) + \tfrac{\sigma^2}{2}(1-2t)}{s_t^2} = \frac12\frac{d}{dt}\log s_t^2. \tag{17.1}$$

**(b)** *(flow)* The ODE $\dot x_t = v_\sigma^\star(x_t,t,y^i)$ has the explicit solution

$$x_t = t\,x^i + s_t\,x_0. \tag{17.2}$$

**(c)** *(endpoint invariance)* Since $s_1 = 0$,

$$\boxed{\;p_1^{\mathrm{cond}}(\cdot\mid y^i) = \delta_{x^i} \quad\text{for every } \sigma \ge 0.\;} \tag{17.3}$$

**Proof.** (a) Given $I=i$, write $r = x - tx^i$, so $r = (1-t)X_0 + \gamma(t)Z =: W \sim \mathcal{N}(0,s_t^2 I_d)$.
Since $X_0, Z$ are independent standard Gaussians,
$\mathbb{E}[X_0\mid W=r] = \frac{(1-t)}{s_t^2}r$ and $\mathbb{E}[Z\mid W=r] = \frac{\gamma(t)}{s_t^2}r$.
Hence
$$\mathbb{E}[\dot X_t \mid X_t=x, I=i] = x^i + \frac{-(1-t) + \dot\gamma(t)\gamma(t)}{s_t^2}\,r,$$
and $\dot\gamma\gamma = \tfrac12(\gamma^2)' = \tfrac{\sigma^2}{2}(1-2t)$, giving (17.1).
The identity $c = \tfrac12 (\log s_t^2)'$ follows from
$\frac{d}{dt}s_t^2 = -2(1-t) + \sigma^2(1-2t) = 2 s_t^2 c(t)$.
Distinct labels make $\{Y=y^i\}$ identify $i$, so this is $v_\sigma^\star$.

(b) Put $u_t = x_t - t x^i$. Then $\dot u_t = \dot x_t - x^i = c(t)u_t$, so
$u_t = u_0\exp\!\int_0^t c = x_0\,\exp\big[\tfrac12\log(s_t^2/s_0^2)\big] = s_t x_0$.

(c) $s_1 = 0$, so $x_1 = x^i$ for every $x_0$. $\blacksquare$

**Sanity check.** At $\sigma = 0$: $s_t = 1-t$, $c(t) = -1/(1-t)$, and
$v_0^\star = x^i - \frac{x-tx^i}{1-t} = \frac{x^i-x}{1-t}$ — Proposition 4(a). Also (17.2)
reduces to $x_t = (1-t)x_0 + tx^i$. Both verified symbolically.

Note that (17.2) maps $x_0\sim\mathcal{N}(0,I_d)$ to $\mathcal{N}(tx^i, s_t^2 I_d)$, which is
exactly $\mathrm{Law}(X_t\mid I=i)$ — the marginals match by direct computation, so
Proposition 17 needs no appeal to a marginal-preservation theorem.

### Corollary 18 (what interpolant noise does and does not change)

- **Does not change** the population endpoint law: (17.3). Interpolation noise is
  *not* a remedy at the level of the exact minimiser, for any $\sigma$. The same argument
  applies unconditionally, so $p_1^{\mathrm{unc}}$ is likewise $\sigma$-invariant.
- **Does change** the irreducible error: $\inf_v L_\sigma > 0$ for $\sigma>0$
  (the target (C.2) retains $Z$-randomness given $(X_t,t,Y)$), whereas $\inf_v L_0 = 0$.
- **Does change** the representation difficulty: from (17.1),
  $\operatorname{Lip}_x v_\sigma^\star = |c(t)|$ and

  $$\lim_{t\uparrow1}\,(1-t)\,|c(t)| = \begin{cases} 1, & \sigma = 0,\\[2pt] \tfrac12, & \sigma > 0.\end{cases} \tag{18.1}$$

  The blow-up rate is **halved** by any positive $\sigma$. Via Corollary 20 this
  relaxes the finite-Lipschitz floor by a factor of $2$ — a small effect, in the right
  direction, and of the observed size.

> **Consequence for the P7i table.** The measured failure of interpolant noise to
> restore conditional variance is *predicted*, not an artefact of the mis-specified
> target: by (17.3) the population endpoint is $\delta_{x^i}$ regardless of $\sigma$.
> The target must still be corrected to (C.2), but for measuring **rates and floors**
> — the qualitative conclusion stands either way. This cleanly separates the present
> mechanism from the unconditional remedy of the gradient-variance literature, which
> operates through attainability rather than through the population optimum.

### Proposition 19 (the two mechanisms act on different factors)

In the factorisation (8.1) of the posterior over training indices:

| mechanism | factor modified |
|---|---|
| label smoothing $\widetilde Y = y^I + h\varepsilon$ | $p(\tilde y\mid I=i) = K_h(y-y^i)$ |
| interpolant noise $\gamma(t)Z$ | $p(x_t \mid I=i) = \mathcal{N}(tx^i, s_t^2 I_d)$ |

Label smoothing flattens the label-space posterior over $i$ and therefore changes
$p_1$ (Theorem 10). Interpolant noise rescales the spatial factor **isotropically and
identically for every $i$**, so it leaves the endpoint law unchanged (Prop. 17).
This is why the two remedies are not interchangeable. $\blacksquare$

---

## Part D — Finite capacity: a genuine representation floor

### Proposition 20 (Lipschitz lower bound)

Fix $i$ and $t<1$, let $f_i(x,t) = (x^i-x)/(1-t)$, and suppose $v(\cdot,t,y^i)$ is
$L$-Lipschitz in $x$. Under $X_t\mid I=i \sim \mathcal{N}(tx^i,(1-t)^2 I_d)$,

$$\mathbb{E}\Big[\big|v(X_t,t,y^i) - f_i(X_t,t)\big|^2 \,\Big|\, I=i\Big] \;\ge\; d\,\big[1 - L(1-t)\big]_+^2. \tag{20.1}$$

**Proof.** Let $X, X'$ be i.i.d. copies of $X_t\mid I=i$ and $e(\cdot) = f_i(\cdot,t) - v(\cdot,t,y^i)$.
Since $f_i(X,t) - f_i(X',t) = -(X-X')/(1-t)$ and $X - X' \sim \mathcal{N}(0, 2(1-t)^2 I_d)$,

$$\mathbb{E}|f_i(X)-f_i(X')|^2 = \frac{2(1-t)^2 d}{(1-t)^2} = 2d.$$

By Lipschitzness, $\mathbb{E}|v(X)-v(X')|^2 \le L^2\,\mathbb{E}|X-X'|^2 = 2dL^2(1-t)^2$. Also
$\mathbb{E}|e(X)-e(X')|^2 = 2\mathbb{E}|e|^2 - 2|\mathbb{E}e|^2 \le 2\mathbb{E}|e|^2$.
Applying the $L^2$ triangle inequality to
$f_i(X)-f_i(X') = [e(X)-e(X')] + [v(X)-v(X')]$:

$$\sqrt{2d} \;\le\; \sqrt{2\,\mathbb{E}|e(X)|^2} + \sqrt{2d}\,L(1-t),$$

hence $\sqrt{\mathbb{E}|e(X)|^2} \ge \sqrt d\,[1-L(1-t)]_+$. $\blacksquare$

*(The step $\mathbb{E}|e(X)-e(X')|^2 \le 2\mathbb{E}|e|^2$ rather than the crude $4\mathbb{E}|e|^2$
is what preserves the constant; do not weaken it.)*

### Corollary 21 (loss floor under a uniform Lipschitz constraint)

Let $\mathcal{F}_L = \{v : \operatorname{Lip}_x v(\cdot,t,y^i) \le L\ \forall t,i\}$ with $L\ge1$, and
let $t\sim\mathrm{Unif}(0,1)$. Then

$$\inf_{v\in\mathcal{F}_L} L_0(v) \;\ge\; d\int_{1-1/L}^{1}\big[1-L(1-t)\big]^2\,dt \;=\; \frac{d}{3L} \;>\; 0. \tag{21.1}$$

**Proof.** Substituting $s = 1-t$, $\int_0^{1/L}(1-Ls)^2 ds = \frac{1}{3L}$. The bound
(20.1) holds for every $i$, so it survives averaging over $I$. $\blacksquare$

### Remark 22 (error decomposition — and a warning about it)

With $\mathcal{F}_\theta$ the architecture's realisable class,

$$L^\star_{\mathrm{all}} = \inf_{v\in L^2}L(v) = 0 \;\le\; L^\star_{\mathrm{model}} = \inf_{v\in\mathcal{F}_\theta}L(v) \;\le\; L_{\mathrm{trained}},$$

$$\underbrace{L^\star_{\mathrm{model}} - L^\star_{\mathrm{all}}}_{\text{representation gap}} \;+\; \underbrace{L_{\mathrm{trained}} - L^\star_{\mathrm{model}}}_{\text{optimisation gap}}. \tag{22.1}$$

Two warnings:

1. **Do not claim $L^\star_{\mathrm{model}} > 0$ without a constraint.** Corollary 21
   bounds $\mathcal{F}_L$, a *uniformly Lipschitz-bounded* class. An MLP with unbounded
   weights is not contained in any fixed $\mathcal{F}_L$, and by universal approximation
   $\inf_\theta L(v_\theta)$ may well be $0$. The correct statement is conditional:
   *for any architecture with $\operatorname{Lip}_x v_\theta \le L$, the loss cannot fall
   below $d/(3L)$.*

2. **Corollary 21 probably does not bind in the current experiments.** With $d=2$ and an
   observed plateau $L_{\mathrm{trained}}\approx0.36$, the bound demands only $L\ge1.85$;
   a trained 4-layer width-128 MLP has $\operatorname{Lip}_x$ of order $10^1$–$10^2$,
   giving a floor of order $10^{-2}$ — one to two orders of magnitude below the plateau.
   Corollary 21 is therefore best used as a **measurement**: estimate $L$, compare
   $d/(3L)$ against $L_{\mathrm{trained}}$, and report which gap dominates. The likely
   (and clean) conclusion is that the plateau is optimisation-limited, which is also
   consistent with the divergence observed under a fixed learning rate at very long
   horizons.

---

## Part D2 — Finite-sample memorization and exact non-representability

*(This part closes two gaps exposed by comparing against the finite-sample and
representability arguments of the unconditional gradient-variance/ReFlow literature
— see the note on 2510.18118 at the end of Part E. Both results are new; neither
appears in Parts A–D.)*

### Lemma 22′ (generic non-intersection of finite interpolant segments)

Let $x_0^1,\dots,x_0^N \stackrel{\text{iid}}{\sim}\pi_0$ and, independently,
$x^1,\dots,x^N\stackrel{\text{iid}}{\sim}\rho_1$, both absolutely continuous on
$\mathbb{R}^d$, paired as $N$ **unconditional** source–target pairs (no labels).
Define the segments $\ell_i(t) = (1-t)x_0^i + t\,x^i$, $t\in[0,1]$. Then:

**(a)** If $d\ge 2$: for any fixed $i\ne j$, $\Pr\big[\exists\, t\in(0,1): \ell_i(t)=\ell_j(t)\big]=0$.

**(b)** If $d> 2$: for any fixed $i\ne j$, $\Pr\big[\exists\, t_i,t_j\in(0,1),\ t_i\ne t_j: \ell_i(t_i)=\ell_j(t_j)\big]=0$.

**Proof.** (a) Fix $\hat t\in(0,1)$ and suppose $\ell_i(\hat t)=\ell_j(\hat t)$. Solving,

$$x^j = \frac{1-\hat t}{\hat t}\big(x_0^i - x_0^j\big) + x^i,$$

which pins $x^j$ to a specific one-dimensional affine subspace of $\mathbb{R}^d$
determined by $(x_0^i,x_0^j,x^i,\hat t)$. A one-dimensional affine subspace is
Lebesgue-null whenever $d\ge2$, and $\rho_1$ is absolutely continuous, so
conditionally on $(x_0^i,x_0^j,x^i)$ this event has probability $0$; integrating
over $(x_0^i,x_0^j,x^i)$ preserves probability $0$. Since $\hat t$ ranges over an
interval and the argument is uniform in $\hat t$, the same conclusion holds for
"some $t=\hat t$" (a union over $\hat t$ of null events under the joint law, made
rigorous exactly as in the source argument: the constraint is on $x^j$ alone, so
the null set does not depend on which $\hat t$ occurs). Finitely many pairs
$(i,j)$: union bound. (b) With $t_i\ne t_j$ both free, solving for $x^j$ pins it to
a two-dimensional affine subspace, Lebesgue-null when $d>2$; the rest of the
argument is identical. $\blacksquare$

*(This is the same generic-position mechanism used in the source material's
Proposition 3; it is reproduced here in the repo's own notation because Part A
never needs it — Lemma 2 gets injectivity for free from the affine invertibility
$X_0\mapsto X_t$ given $I=i$, valid for **any** $\pi_0$, no genericity argument
required. Lemma 22′ is the tool needed once labels are removed and the source
points are also finite and fixed, i.e. Proposition 23 below.)*

### Proposition 23 (a memorizing field always exists on a fixed finite unconditional batch)

Fix $N$ unconditional pairs $\{(x_0^i,x^i)\}_{i=1}^N$ as in Lemma 22′ (with $d>2$,
$x^i$ pairwise distinct a.s.), and sample $m$ time points $t^{(i,j)}\in(0,1)$,
$j=1,\dots,m$, independently across $(i,j)$ (e.g. uniformly). Let

$$X_t^{(i,j)} = (1-t^{(i,j)})x_0^i + t^{(i,j)}x^i, \qquad
L_{\mathrm{MC}}^{\mathrm{unc}}(v) = \frac1{Nm}\sum_{i=1}^N\sum_{j=1}^m
\big\|(x^i - x_0^i) - v\big(X_t^{(i,j)}, t^{(i,j)}\big)\big\|^2.$$

Then, almost surely over the draw of $\{(x_0^i,x^i)\}$ and $\{t^{(i,j)}\}$, there
exists a (deterministic, non-parametric) $v$ with $L_{\mathrm{MC}}^{\mathrm{unc}}(v) = 0$
— **even though** $\inf_v L_{\mathrm{unc}}(v) > 0$ at the population level whenever the
$x^i$ are not all equal (Proposition 7).

**Proof.** By Lemma 22′(a)–(b) applied to every pair $i\ne j$ and union-bounded over
the $\binom N2$ pairs, almost surely no two of the $N$ full segments
$\{\ell_i(t):t\in(0,1)\}$ intersect at all, hence in particular the finitely many
sampled points $(X_t^{(i,j)}, t^{(i,j)})$ never collide across different $i$. On
this full-measure event, the map $(z,t)\mapsto i$ is well defined on
$\{(X_t^{(i,j)},t^{(i,j)})\}_{i,j}$, so

$$v(z,t) := x^{i(z,t)} - x_0^{i(z,t)} \quad\text{on the sample},\qquad v(z,t):=0 \text{ elsewhere},$$

is a well-defined function, and by construction
$v\big(X_t^{(i,j)},t^{(i,j)}\big) = x^i - x_0^i$ exactly for every sampled $(i,j)$, making
every summand of $L_{\mathrm{MC}}^{\mathrm{unc}}$ vanish. $\blacksquare$

### Remark 24 (why SGD does not land here — reconciling with Corollary 6)

Proposition 23 shows the *finite-batch* unconditional objective always has an
exact zero-loss "lookup" solution, in apparent tension with Proposition 5–7's
positive population loss. There is no contradiction: the standard CFM training
loop **resamples $x_0^i$ (and typically the time samples) independently every
epoch**. Proposition 23's construction is only valid for a *fixed* finite sample —
across resampled epochs, the lookup table for epoch $k$ is checked against fresh
points $(X_t^{(i,j)})$ from epoch $k+1$ for which it was never fit, and no single
lookup table stays consistent with the growing stream of $(x_0,t)$ draws. This is
the rigorous form of the informal claim (repeated throughout the unconditional
memorization literature, e.g. in the source material's discussion of "why doesn't
CFM memorize random pairings") that *independent resampling of $x_0$*, not mere
continuity of $\pi_0$, is what forces training toward the population optimum of
Proposition 5 rather than toward a per-example memorizing solution. It also gives
a precise mechanism for prediction **P6**: at fixed network capacity, larger $N$
makes the epoch-consistent lookup table harder to realize with a smooth,
finite-parameter function, pushing the attained solution back toward Proposition 5.

*(Note the asymmetry with the conditional case of Part A: Proposition 4 needs no
such genericity argument and no "fixed-batch" caveat, because $y^i$ pins down $i$
deterministically for every $x_0$, not merely with probability $1$ on one finite
draw. Resampling $x_0$ every epoch does nothing to prevent conditional collapse —
this is exactly why $P4$ ["collapse is far weaker/absent for unconditional CFM"]
holds while conditional collapse is universal.)*

### Lemma 25 (the collapse field cannot be exactly represented by a finite network)

Let $g(t) = 1/(1-t)$ on $[0,1)$. Let $f_\theta:\mathbb R\to\mathbb R$ be **any**
finite-depth, finite-width feedforward network with finite real weights, built
from affine layers and activations that are globally Lipschitz (this covers every
activation used in `src/models/mlp_velocity.py`, and indeed ReLU, leaky-ReLU,
tanh, sigmoid, GELU/SiLU, softplus, etc.). Then

$$\sup_{t\in[0,1)}\big|f_\theta(t) - g(t)\big| = \infty.$$

**Proof.** A finite composition of affine maps (finite weight matrices, hence
finite operator norm) and globally Lipschitz activations is globally Lipschitz
on $\mathbb R$, with constant equal to the product of the layer constants — finite
because there are finitely many layers and finite weights. A Lipschitz function
is bounded on any bounded set (fix $t_0\in[0,1)$; for all $t\in[0,1)$,
$|f_\theta(t)|\le |f_\theta(t_0)| + K|t-t_0| \le |f_\theta(t_0)| + K$). So
$\sup_{t\in[0,1)}|f_\theta(t)| < \infty$. But $g(t)\to\infty$ as $t\uparrow 1$, so
$g$ is unbounded on $[0,1)$. Hence $f_\theta - g$ is unbounded on $[0,1)$. $\blacksquare$

**Consequence.** For $x\ne x^i$ fixed, $t\mapsto v_0^\star(x,t,y^i) = (x^i-x)/(1-t)$
has exactly this $1/(1-t)$ blow-up along the direction $x^i-x$. By Lemma 25 (applied
coordinatewise to that direction), **no finite MLP of the kind used in this repo can
represent $v_0^\star$ exactly on all of $[0,1)$** — the representation gap
$L^\star_{\mathrm{model}} - L^\star_{\mathrm{all}}$ in Remark 22 is provably strictly
positive for *every* finite architecture, not merely for a Lipschitz-capped class
$\mathcal F_L$ as in Corollary 21.

*(This does **not** contradict the universal approximation theorem, and does not
retract Remark 22's warning against claiming $L^\star_{\mathrm{model}}>0$ without a
constraint: UAT guarantees arbitrarily good **uniform** approximation only on
**compact** sets, and every compact subset $[0,1-\delta]$, $\delta>0$, is disjoint
from the singularity. Lemma 25 is a statement strictly about the open boundary
$t\to1^-$ — exactly the regime the sampler must traverse to reach the collapse
point $x^i$, and exactly where `flows/ode_solver.py`'s $t=1$ singularity handling
matters in practice.)*

---

## Part E — Scope: what is and is not predicted

### Proved (exact population consequences)

| | statement |
|---|---|
| P-1 | $h=0$, unique labels $\Rightarrow p_1(\cdot\mid y^i) = \delta_{x^i}$, $\inf L_0 = 0$ (Prop. 4) |
| P-2 | duplicate labels $\Rightarrow$ collapse to the label's empirical conditional law (Prop. 4′) |
| P-3 | unconditional $\Rightarrow p_1 = \frac1N\sum_i\delta_{x^i}$, $\inf L_{\mathrm{unc}}>0$ (Props. 5, 7) |
| P-4 | $h>0 \Rightarrow p_1(\cdot\mid y) = \sum_i p_i^{(h)}(y)\delta_{x^i}$ (Thm. 10) |
| P-5 | $h\to0$ at fixed $N$ $\Rightarrow$ nearest-neighbour collapse; $h\to\infty \Rightarrow$ unconditional law (Cors. 11, 12) |
| P-6 | generated law is atomic for every $h$; $h$-independent $W_2$ floor (Prop. 14) |
| P-7 | $\operatorname{tr}\operatorname{Cov}_h = \operatorname{tr}\Sigma + h^2\|J\|_F^2 + \cdots$ (Prop. 15) |
| P-8 | interpolant noise leaves $p_1$ unchanged for all $\sigma$; halves the Lipschitz blow-up rate (Prop. 17, Cor. 18) |
| P-9 | $\operatorname{Lip}_x v_\theta \le L \Rightarrow L_0(v_\theta)\ge d/(3L)$ (Cor. 21) |
| P-10 | a fixed finite unconditional batch always admits an exact zero-loss memorizing field, despite $\inf L_{\mathrm{unc}}>0$ at the population level (Prop. 23) |
| P-11 | resampling $x_0$ every epoch, not mere continuity of $\pi_0$, is what defeats P-10's construction and forces training toward the Prop. 5 mixture (Rmk. 24) |
| P-12 | no finite Lipschitz-activation network exactly represents $v_0^\star$ on all of $[0,1)$ — the representation gap is strictly positive for every finite architecture (Lem. 25) |

### Explicitly **not** determined by the population theory

- number of SGD iterations to approach the optimum, and the transition point;
- dependence of observed collapse on $N$ at **fixed architecture** — the population
  optimum collapses for every finite $N$, so a non-collapsing $N=5000$ experiment probes
  representation/optimisation, it does not contradict Proposition 4;
- dependence of observed collapse on $\sigma_{\mathrm{obs}}$ — the theory implies no
  monotonicity, so a flat sweep is *consistent with*, not a falsification of, the theory;
- monotonicity of $\operatorname{tr}\operatorname{Cov}_h$ in $h$;
- residual loss reached by a particular optimiser; finite-sample error bars.

> **Mandatory phrasing rule.** A quantity in the second list must never be described as
> a "theoretical prediction" that "matched" or "failed". Correct form: *"The exact
> population theory does not determine X; the observed behaviour of X is an empirical
> finding."*

### Positioning relative to existing work

The fact that exact minimisation against a finite empirical measure induces
memorisation is **not new**; it is established in the diffusion memorisation
literature: score-based models detect and memorise the empirical support
[Pidstrigach 2022]; the denoising-score-matching optimum can only replicate
training data, with memorisation strongest on small datasets [Gu et al. 2023];
generalisation appears only once $N$ is large enough that independently trained
networks converge to the same score [Kadkhodaie et al. 2024]; the phenomenon has
a statistical-physics / symmetry-breaking description [Biroli & Mézard 2023]; and
locality/equivariance turn memorisation into nearest-patch recombination
[Kamb & Ganguli 2024]. Our contribution is *not* the observation that the
empirical minimiser memorises — it is the conditional and kernel-regression
structure listed below.

The specific contributions here are:

1. the *conditional* sharpening — hard conditioning turns full-empirical-measure
   memorisation into **single-atom** memorisation, i.e. zero conditional variance
   (Cor. 6);
2. the exact identification **label smoothing $\equiv$ kernel regression over training
   atoms** (Thm. 10), which converts a $0/1$ statement into a quantitative,
   parameter-free reference curve (Prop. 13);
3. the **separation of the two remedies**: label noise changes the population endpoint,
   interpolant noise provably does not (Prop. 17, Prop. 19);
4. the **atomicity obstruction** (Prop. 14), which bounds how much any $h$ can achieve;
5. the **representation floor** (Cor. 21) as a measurable quantity separating
   representation from optimisation error;
6. two results (Part D2) that translate the finite-sample and exact-representability
   arguments of the unconditional ReFlow/gradient-variance literature (2510.18118,
   their Propositions 2–3 and Extra-Lemma 1) into this repo's setting: a finite fixed
   batch always admits an exact-zero-loss unconditional memorizing field despite
   positive population loss (Prop. 23, mirroring their Prop. 2 via the same
   generic-position argument, their Prop. 3, reproduced as Lemma 22′), with the
   resampling-of-$x_0$ mechanism made precise (Rmk. 24); and an exact (not merely
   Lipschitz-capped) non-representability statement for the collapse field's
   $1/(1-t)$ blow-up (Lemma 25, the boundedness analogue of their scaling argument
   for $1/x$).

Summarised in one line:

$$\textbf{Conditional collapse is the zero-bandwidth limit of a kernel-weighted empirical conditional flow.}$$

### References

- **[Pidstrigach 2022]** J. Pidstrigach. *Score-Based Generative Models Detect Manifolds.* NeurIPS 2022. arXiv:2206.01018.
- **[Gu et al. 2023]** X. Gu, C. Du, T. Pang, C. Li, M. Lin, Y. Wang. *On Memorization in Diffusion Models.* arXiv:2310.02664, 2023.
- **[Kadkhodaie et al. 2024]** Z. Kadkhodaie, F. Guth, E. P. Simoncelli, S. Mallat. *Generalization in Diffusion Models Arises from Geometry-Adaptive Harmonic Representations.* ICLR 2024 (Oral).
- **[Biroli & Mézard 2023]** G. Biroli, M. Mézard. *Generative diffusion in very large dimensions.* J. Stat. Mech. (2023) 093402; arXiv:2306.03518.
- **[Kamb & Ganguli 2024]** M. Kamb, S. Ganguli. *An analytic theory of creativity in convolutional diffusion models.* arXiv:2412.20292, 2024 (ICML 2025).

*(For the unconditional "resample $x_0$" mechanism that this work contrasts against,
see the stochastic-interpolant / gradient-variance line of work referenced in the
project spec as 2510.18118. That paper's Proposition 2 constructs, for a **finite**
i.i.d. sample of unconditional pairs with no labels, a deterministic vector field
attaining zero *Monte-Carlo* loss, using their Proposition 3's generic-position
argument (interpolant segments a.s. don't cross) to make the pair index recoverable
from $(x_t,t)$ alone. This is existence of a zero-loss field on a **finite empirical
batch**; it says nothing about the population $L^2$ minimiser, and indeed their own
Section 3 (gradient variance) is precisely about which of several zero-training-loss
solutions optimisation actually prefers. Proposition 4 above is a different kind of
statement — an exact closed-form characterisation of the **population** minimiser,
made possible without any genericity assumption because $y^i$, not generic position,
supplies the injectivity. Part D2 restates their Propositions 2–3 and Extra-Lemma 1
in this repo's notation (Lemma 22′, Prop. 23, Lemma 25) so the two levels of
statement — finite-batch existence vs. population characterisation — sit side by
side rather than being conflated, and so that the resampling mechanism they describe
qualitatively (Remark 24) has a precise if-and-only-if role: it is exactly what is
absent from the conditional case, which is why P4 holds.)*
