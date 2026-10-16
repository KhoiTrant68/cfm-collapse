# Frozen atomicity review packet

Read-only exact manuscript excerpts. Review mathematical validity, not venue acceptance or novelty. All atoms lie in a finite-dimensional Euclidean space; t is in [0,1); source pi_0 is standard Gaussian. The label kernel is K_h(u)=(2*pi*h^2)^(-k/2) exp(-|u|^2/(2h^2)), h>0. Conditional weights p_i^(h)(y)=K_h(y-y_i)/sum_j K_h(y-y_j). The exact conditional field is sum_i q_i(x,t,y)(a_i-x)/(1-t), q_i proportional to K_h(y-y_i) exp(-|x-t*a_i|^2/(2(1-t)^2)). The unconditional field uses uniform prior weights. CFG is (1+w) times the conditional field minus w times the unconditional field. For hard identifying label y_i the conditional field is (a_i-x)/(1-t).

Macro meanings: R=real numbers; eps=varepsilon; vstar=v_h^star; fat{i}=(x^i-x)/(1-t); KK{i}=K_h(y-y^i); src{i}=pi_0((x-t*x^i)/(1-t)); pih{i}=p_i^(h); law=Law; proofin is an appendix pointer, not a hypothesis. No outside results are assumed for the proofs beyond standard ODE flow/Jacobian, integration and measure theory facts stated here.

## Label averaging

\begin{proposition}[Label resolution reweights the atoms and never moves them]
\label{prop:filtered}
Let $h>0$, $\varphi$ a probability measure on $\R^k$ and
$v_\varphi(x,t,y)=\int\vstar(x,t,y-u)\,\varphi(du)$. (a) $v_\varphi=\sum_i\tilde
w_i(x,t,y)(x^i-x)/(1-t)$ with $\tilde w_i\ge0$, $\sum_i\tilde w_i=1$, and $\tilde
w_i(x,0,y)=q_i(y):=\int p_i^{(h)}(y-u)\,\varphi(du)$. (b) Every trajectory converges. If
$N(z)=\{x^j:|z-x^j|=\min_\ell|z-x^\ell|\}$, its limit satisfies
$z\in\operatorname{conv}N(z)$. For any absolutely continuous source, including
$\pi_0$, the limit is a training atom almost surely. Thus the endpoint law is
$\sum_i\tilde q_i(y)\delta_{x^i}$ for some probability weights $\tilde q(y)$.
\proofin{apx:pf-filtered}
\end{proposition}

\begin{proof}[Proof of Proposition~\ref{prop:filtered}]
\label{apx:pf-filtered}
(a) By Proposition~\ref{prop:kernel-field}, $\vstar(x,t,y')=\sum_iw_i(x,t,y')(x^i-x)/(1-t)$
with $w_i=a_ib_i/\sum_ja_jb_j$, $a_i=\pi_0(\frac{x-tx^i}{1-t})$, $b_i=K_h(y'-y^i)$;
averaging over $y'=y-u$ gives $\tilde w_i=\int w_i(x,t,y-u)\varphi(du)$, which is
nonnegative and sums to one. At $t=0$ all $a_i$ equal $\pi_0(x)$, so $w_i=p_i^{(h)}(y')$.
(b) Write $a_j=x^j$, set $c_j(u)=K_h(y-u-y^j)>0$, and use
$\phi=\varphi$. The index weights are
$q_j(x,t,u)\propto c_j(u)\exp(-|x-ta_j|^2/(2(1-t)^2))$; their averaged mean is
$m(x,t)=\int\sum_jq_j(x,t,u)a_j\,d\phi(u)$, and the flow is
$\dot x=(m-x)/(1-t)$. Set $\eps=1-t$. Below the integration variable for these coefficients is
denoted by $y'$; it is distinct from the fixed query $y$.

The original field is locally Lipschitz on compact intervals $t<1$, including
$t=0$: its spatial softmax derivatives are bounded independently of the
coefficients there. Since $m$ is in the convex hull of the atoms,
variation of constants gives existence on all of $[0,1)$ and a bounded trajectory.
We now prove convergence of this trajectory.

\emph{Convergence.}
Normalize $p_j(y')=c_j(y')/\sum_\ell c_\ell(y')$. Start at any $t_0>0$ and set
\[
\tau=-\log(1-t),\quad \alpha=\frac{\eps^2}{t},\quad
b_j=x\cdot a_j-\frac t2\lVert a_j\rVert^2,\quad R=\max_j\lVert a_j\rVert.
\]
From now on dots denote differentiation with respect to $\tau$, with
$t=1-e^{-\tau}$. Then $q_j\propto p_je^{b_j/\alpha}$ and $\dot x=m-x$,
which also gives a bounded $\tau$-speed. Define
\[
F=\int\alpha\log\sum_jp_j(y')e^{b_j/\alpha}\,d\phi(y'),\qquad
W=\tfrac12\lVert x\rVert^2-F+\tfrac12\eps R^2.
\]
The integrand lies between $\min b_j$ and $\max b_j$. Treating $t$ and $\alpha$
as independent arguments, differentiation gives
\[
\nabla_xF=m,\qquad \partial_\alpha F=-\int D_{\rm KL}(q\Vert p)\,d\phi,
\qquad \partial_tF=-\tfrac12\int\sum_jq_j\lVert a_j\rVert^2\,d\phi.
\]
These derivatives pass under the integral on compact positive-time intervals:
the spatial and time derivatives are bounded, and
\[
0\le D_{\rm KL}(q\Vert p)
=\frac{\sum_jq_jb_j}{\alpha}-\log\sum_jp_je^{b_j/\alpha}
\le\frac{\max_jb_j-\min_jb_j}{\alpha}
\]
is uniform in $y'$. Since $\dot\alpha<0$ and $\dot t=\eps$,
\[
\dot W=-\lVert\dot x\rVert^2+\dot\alpha\int D_{\rm KL}(q\Vert p)\,d\phi
+\frac\eps2\left(\int\sum_jq_j\lVert a_j\rVert^2\,d\phi-R^2\right)
\le-\lVert\dot x\rVert^2.
\]
Moreover $F\le\max_jb_j$, so
\[
W\ge\min_j\left\{\tfrac12\lVert x-a_j\rVert^2
+\tfrac\eps2(R^2-\lVert a_j\rVert^2)\right\}\ge0.
\]
Thus $\int_{\tau_0}^\infty\lVert\dot x\rVert^2\,d\tau<\infty$.

\emph{A finite set of possible limits.}
If $x_n\to z$ and $\tau_n\to\infty$, every weight on an atom outside $N(z)$
tends to zero for each $y'$, by the positive distance gap and the fixed positive
coefficient ratios. Bounded convergence gives the same conclusion after
averaging over $y'$. Every limit of $m(x_n,t_n)$ therefore lies in
$\operatorname{conv}N(z)$.

Let $C=\{z:z\in\operatorname{conv}N(z)\}$. This set is finite. For each
nonempty subset $S$ of atoms, there is at most one point in
$\operatorname{aff}S$ equidistant from all atoms of $S$: the difference of two
such points lies both in $\operatorname{span}(S-S)$ and its orthogonal
complement. A point of $C$ is one of these finitely many candidates.
On any compact set disjoint from $C$, the speed is eventually bounded below
by a positive constant. Otherwise a sequence of points there with speed tending
to zero would, by compactness and the preceding concentration argument, have
a limit in $C$.

An omega-limit point outside $C$ admits a closed ball disjoint from $C$.
Infinitely many visits to its inner half force residence for a fixed positive
time in the ball, because the speed is bounded above. If the trajectory remains
in the ball forever, the eventual positive lower speed bound already contradicts
finite energy. Otherwise choose disjoint visits; each spends a fixed positive
amount of energy, again a contradiction. Hence the omega-limit set is contained
in $C$. It is nonempty, compact, and connected, as the intersection of the nested
closures of the bounded connected trajectory tails. Being contained in a finite
set, it is a singleton.

\emph{Atomic endpoints almost surely.}
We may assume the atoms distinct, summing coefficients at repeated locations.
Use the $\tau$ variables above and write $\beta=1/\alpha$.
For a point $r$ in the closed probability simplex, define
\[
Q_j(y',r)=\frac{p_j(y')r_j}{\sum_\ell p_\ell(y')r_\ell},\quad
M(r)=\int\sum_jQ_j(y',r)a_j\,d\phi,\quad
V(r)=\int\operatorname{tr}\Cov_{Q(y',r)}(a)\,d\phi.
\]
All denominators are positive for each $y'$ outside one fixed null set.
The integrands are continuous in $r$ and uniformly bounded. Dominated
convergence makes $M,V$ continuous on the closed simplex. Positivity of the
coefficients and distinctness of the atoms imply that $V(r)=0$ exactly at its
vertices. Compactness therefore gives, for each $\delta>0$, a constant
$\kappa_\delta>0$ such that
\[
\dist(M(r),A)\ge\delta\quad\Longrightarrow\quad V(r)\ge\kappa_\delta,
\qquad A=\{a_1,\ldots,a_N\},
\]
whenever the set on the left is nonempty.
For the actual unconditional softmax vector $r_j\propto e^{b_j/\alpha}$,
the averaged $\tau$-field $f=m-x$ has divergence
\[
\operatorname{div}f=\beta V(r)-d.
\]

Consider a trajectory converging to a non-atom $z$, with $\rho=\dist(z,A)>0$.
Eventually $\lVert x-z\rVert<\rho/4$. At good times
$\lVert\dot x\rVert\le\rho/4$, the identity $m=x+\dot x$ gives
$\dist(m,A)\ge\rho/2$, hence $V\ge\kappa_{\rho/2}$.
The complementary times have finite measure by the finite energy proved above.
Their measure in the last unit interval therefore tends to zero. Good times
thus occupy at least half of every sufficiently late unit interval. Since
$V\ge0$ everywhere and $\beta(\tau)=(1-e^{-\tau})e^{2\tau}$,
\[
\int_{\tau_0}^\tau\operatorname{div}f(x(s),s)\,ds
\ge\kappa_{\rho/2}\int_{\mathrm{good}\cap[\tau-1,\tau]}\beta(s)\,ds
-d(\tau-\tau_0)\longrightarrow+\infty.
\]

The finite-time flow maps $F_\tau=F_{\tau,\tau_0}$ from $\tau_0>0$ are $C^1$
diffeomorphisms: spatial derivatives are locally uniformly bounded, and linear
growth permits both forward and backward solutions on finite intervals.
Liouville's formula gives
\[
J_\tau(\xi):=\det DF_\tau(\xi)
=\exp\!\left(\int_{\tau_0}^\tau
\operatorname{div}f(F_s(\xi),s)\,ds\right)>0.
\]
Thus $J_\tau\to\infty$ at every non-atom-convergent initial point.
For a bounded initial ball $K$, boundedness of $m$ places all $F_\tau(K)$
in one fixed ball $B$. Let $E\subset K$ be the non-atom basin; it is measurable,
since the limit map is a pointwise limit of continuous flow maps. Injectivity
and change of variables give $\int_EJ_\tau\,dx\le\operatorname{Leb}(B)$.
Fatou's lemma along integer times forces $\operatorname{Leb}(E)=0$.
Exhaust the initial space by bounded balls and take the preimage of the null
set under the finite-time diffeomorphism from $t=0$ to $t(\tau_0)$. Its inverse
is locally Lipschitz and preserves Lebesgue-null sets. Absolute continuity
of the source proves the assertion.
The limit map is measurable, and bounded convergence for continuous bounded test
functions identifies the weak endpoint law as the stated finite mixture.
\end{proof}

## Signed guidance

\begin{proposition}[Guidance lands on a training atom]
\label{prop:cfgatom}
Assume $x^1,\dots,x^N$ are distinct and fix a finite $w\ge0$.
The exact guided field has a unique trajectory on $[0,1)$ from every finite
initial point. Then:
\begin{enumerate}[label=(\alph*),leftmargin=2em]
\item if $h>0$, every trajectory converges to a point
  $z\in\operatorname{aff}N(z)$, where $N(z)$ is its set of nearest atoms.
  For an absolutely continuous source, the endpoint is a training atom almost surely;
\item if $h=0$ at an identifying label $y^i$, every trajectory converges to $x^i$,
  without an exceptional set of initial points.
\end{enumerate}
\end{proposition}

\begin{proof}[Proof of Proposition~\ref{prop:cfgatom}]
Write $a_j=x^j$, $A=\{a_1,\dots,a_N\}$, $\eps=1-t$,
$\tau=-\log\eps$, $\alpha=\eps^2/t$, and $\beta=1/\alpha$, starting
the energy argument at any $t_0>0$. Dots in part (a) denote $\tau$ derivatives.
Set $b_j=x\cdot a_j-t|a_j|^2/2$ and
$q_{p,j}\propto p_j\exp(b_j/\alpha)$, normalized over $j$.
For $h>0$, take $p_c=(p_j^{(h)}(y))_j$ and $p_u=(1/N)_j$;
both are fixed strictly positive vectors. Their means are $m_c,m_u$.

\emph{(a) Positive bandwidth.}
\emph{Convergence.}
Put $H_p=\alpha\log\sum_jp_je^{b_j/\alpha}$ and
\[
U=\tfrac12\lVert x\rVert^2-(1+w)H_{p_c}+wH_{p_u}.
\]
The mean $(1+w)m_c-wm_u$ is bounded, so trajectories and $\tau$-speeds
are bounded and finite-time flows are well posed. We have $\nabla_xU=-\dot x$.
For fixed positive $p$, $D_{\rm KL}(q_p\Vert p)\le\log(1/\min_jp_j)$.
Direct differentiation gives $\nabla_xH_p=m_p$,
$\partial_\alpha H_p=-D_{\rm KL}(q_p\Vert p)$ and
$\partial_tH_p=-\tfrac12\sum_jq_{p,j}|a_j|^2$, treating $t$ and $\alpha$
as independent arguments. Consequently,
\[
\dot U=-\lVert\dot x\rVert^2+\mathcal R(\tau),\qquad
|\mathcal R(\tau)|\le C(|\dot\alpha|+\dot t).
\]
The latter bound is integrable. The min--max bounds on $H_p$ show that $U$
is bounded below on a bounded trajectory. Hence its squared speed is integrable.

Near any cluster point $z$, the non-nearest softmax weights tend uniformly to
zero at large times. Thus the signed mean approaches $\operatorname{aff}N(z)$.
If $z$ were outside that affine hull, its orthogonal distance would force a
positive lower speed bound in a fixed neighborhood at late times. Bounded upper
speed and recurrent visits would then contradict finite energy, as in
the convergence argument in the proof of Proposition~\ref{prop:filtered}. Each cluster point consequently lies in
$\operatorname{aff}N(z)$. There are finitely many such equidistant candidates,
and connectedness of the omega-limit set proves convergence.

\emph{The non-atom basins have zero volume.}
Consider a limit $z\notin A$, and let $r>0$ be the common distance of its nearest
atoms. Write $\mu_c=m_c-z$, $\mu_u=m_u-z$, and
$\mu_w=(1+w)\mu_c-w\mu_u$. Write $\Cov_c,\Cov_u$ for covariance under
$q_{p_c},q_{p_u}$, respectively. The signed covariance trace is
\begin{align*}
T&=(1+w)\operatorname{tr}\Cov_c(a)-w\operatorname{tr}\Cov_u(a)\\
 &=r^2-(1+w)\lVert\mu_c\rVert^2+w\lVert\mu_u\rVert^2+o(1)\\
 &=r^2-\lVert\mu_w\rVert^2+
 \frac{w}{1+w}\lVert\mu_u-\mu_w\rVert^2+o(1)
 \ge r^2-\lVert\mu_w\rVert^2+o(1).
\end{align*}
The error tends to zero along the whole trajectory, since non-nearest mass
vanishes and the atoms are finite. Since $\mu_w=\dot x+x-z$, convergence and
finite energy give $\int_n^{n+1}\lVert\mu_w\rVert^2\,d\tau\to0$.
On each late unit interval the ratio $\beta_{\max}/\beta_{\min}$ is bounded.
Writing the preceding error as at worst $-\eta_n$ throughout that interval,
where $\eta_n\to0$, yields
\[
\int_n^{n+1}\beta T\,d\tau
\ge(r^2-\eta_n)\beta(n)-\beta(n+1)
\int_n^{n+1}\lVert\mu_w\rVert^2\,d\tau
\ge\tfrac14 r^2\beta(n)
\]
eventually. The divergence is $\beta T-d$, so its accumulated integral tends
to infinity along integer times. The same bounded-image-ball,
change-of-variables, and Fatou argument as in Proposition~\ref{prop:filtered}
makes every non-atom basin null. Absolute continuity completes the proof.

\emph{(b) Hard conditioning.}
Dots now denote derivatives in the original time $t$.
The conditional mean is $a_i$ and the unconditional mean is
$m=\sum_jq_j a_j$, with $q_j\propto\exp(-|x-ta_j|^2/(2\eps^2))$.
The following estimate also quantifies convergence: for $0<t_0<t<1$,
\begin{equation}
|x_t-ta_i|^2\le\eps^2\left[
\frac{|x_{t_0}-t_0a_i|^2}{(1-t_0)^2}
+2w\log N\log\frac{t(1-t_0)}{t_0(1-t)}\right].
\label{eq:guided-hard-rate}
\end{equation}
On every compact time interval below $1$ the field is smooth, locally Lipschitz,
and has linear growth, since $m$ lies in the convex hull of the finite atoms.
These properties give existence and uniqueness on $[0,1)$.

Write $D_j=\lVert x-ta_j\rVert^2$ and $H(q)=-\sum_jq_j\log q_j$.
The Gibbs identity and the contribution of index $i$ to the partition function give
\[
\sum_jq_jD_j=2\eps^2\bigl(H(q)-\log\sum_je^{-D_j/(2\eps^2)}\bigr)
\le D_i+2\eps^2\log N.
\]
With $z=x-ta_i$, expanding $D_j-D_i$ therefore gives
\[
2t z\cdot(a_i-m)+t^2\sum_jq_j\lVert a_i-a_j\rVert^2
\le2\eps^2\log N.
\]
Along the flow, $\dot z=(-z+w(a_i-m))/\eps$. Dropping the nonnegative
sum for $t>0$ and using $w\ge0$, $Y=\lVert z\rVert^2$ satisfies
\[
Y'\le-\frac{2Y}{\eps}+\frac{2w\eps\log N}{t},\qquad
\left(\frac{Y}{\eps^2}\right)'\le\frac{2w\log N}{t(1-t)}.
\]
Integration yields \eqref{eq:guided-hard-rate}. Its right side tends to zero, so
$x_t-ta_i\to0$ and $x_t\to a_i$.
\end{proof}