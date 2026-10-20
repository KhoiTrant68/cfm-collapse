# Check of the Direction A drafts — 20 October 2026

Scope: the four working drafts in the 20 October synthesis report (Appendices A–D: spectral
criterion; saddle-basin theorem; Lyapunov–Perron fast–slow classification; global
completeness). This is a structural read of the main steps, done against the notation of
`paper/main.tex` (Appendix B). It is not a line-by-line certification. Before any of it enters
the paper, it needs the usual four-verifier protocol.

## 1. Consistency with the paper

- **Variables.** $\xi=\beta(x-tz)$ with $\beta=t/(1-t)^2$ is the paper's $s=tx/(1-t)^2$ when
  $z=0$. Restricted Gibbs weights $\propto p_je^{\langle\xi,a_j\rangle}$ give the paper's posterior
  mean $\tanh(s+b)$ for log-odds $2b$. Checked.
- **Off-tie logit.** At $x=tz+\xi/\beta+(1-t)P_{L^\perp}z+\eta$ the logit difference for
  $j\notin S$, $i\in S$ is $-\tfrac{\beta t}{2}\delta_j+\beta\langle\eta+(1-t)P_{L^\perp}z,a_j-a_i\rangle+\langle\xi,a_j-a_i\rangle+\log(p_j/p_i)$,
  with $\delta_j=\|a_j-z\|^2-r^2$. Within $S$, only $\langle\xi,a_i-a_{i'}\rangle$ survives. Checked
  from $-\|x-ta_j\|^2/(2\eps^2)=-\|x\|^2/(2\eps^2)+\beta b_j$ (Appendix B.1).
- **Blown-up equation.** $d\beta/d\tau=\beta(1+1/t)$, so $d\xi/d\tau=\xi/t+\beta P_L(\bar m-z)$ and
  $d\xi/du=G(\xi)+(1-t)^2\xi/t^2+P_L(\bar m_t-M)$. Checked.
- **Two-atom threshold.** $C_{\mathrm{av}}=\operatorname{sech}^2B$, $C_{\mathrm u}=1$ and
  $D=\tanh^2B$ give $1/\sinh^2B$, as in Theorem 4.7. The roots of $F_w$ also match the
  classification. For $w>w_c$, $s=0$ is a sink with an open basin and $\pm s_u$ have $F'>0$
  with null basins; for $w<w_c$, $s=0$ has $F'(0)>0$ with a null basin. The case $w=w_c$ is
  nonhyperbolic. The drafts do not cover it, and the paper's Step 4 already handles it through
  the cubic lower bound $F_w\ge\kappa\min\{s^3,1\}$.
- **Closed form in Section 13.2.** $F_w(s)=\sinh2s\,[\cosh2s+1-2w\sinh^2B]/([\cosh2s+\cosh2B][\cosh2s+1])$
  equals the paper's (eq. composition-mean). Checked.

## 2. Issues found

1. **Draft 1 (Appendix A) only applies when the tie atoms span $\R^d$.** For $j\in S$, all
   $a_j$ share the $L^\perp$ component, so $DM(\xi)=\sum_kc_k\Cov_{\pi_k}(a)$ vanishes on
   $L^\perp$. The hypothesis $DM(\xi_\star)\prec0$ on $\R^d$, and $D\succ0$ in its corollary, can
   therefore hold only if $\dim L=d$, that is, $|S|\ge d+1$ affinely independent tie atoms. The
   proof is consistent with this: the normal part of $\xi=\beta(x-tz)$ grows like $e^{\tau}$, so
   a full-dimensional ball in $\xi$ is not invariant. Drafts 2–4 fix this with the unscaled
   normal coordinate $\eta=P_{L^\perp}(x-z)$. **Use Drafts 3–4 and drop Draft 1**, or restate
   Draft 1 with $L=\R^d$.
2. **The spectral threshold has to be stated on $L$.** $C_{\mathrm{av}}$, $C_{\mathrm u}$ and $D$
   are restrictions to $L$, and $D\succ0$ means on $L$. Draft 3, Section 5 already does this;
   Draft 1's corollary does not.
3. **The common-equilibrium assumption** $M_{\mathrm{av}}(\xi_\star)=M_{\mathrm u}(\xi_\star)=z$
   holds in symmetric configurations. For generic data it is a codimension condition. The
   threshold corollary is then a statement about symmetric ties, and the general theorem
   (Draft 3, Theorem "Sink–saddle classification") is the one to lead with.
4. **Direction B (Section 12) overlaps existing results.** The Lipschitz–Grönwall Wasserstein
   bound is close to Benton et al. (2024, Theorem 1), which the paper already cites. It is also
   close to the paper's own Theorem C.1 (risk transfer with $K(t)$). The computation is correct
   ($d[(Z-Y)/(1-t)]/dt=\Delta(Z)/(1-t)$, then Minkowski and Grönwall). As a separate result its
   novelty is low; at most it fits as a remark under Theorem C.1.

## 3. Steps that held up on this read

- **Draft 3, Lemma LP.** In $\tau$-time the fast block has generator $\beta H$. The Green
  kernels integrate to $\le a^{-1}$, and the normal block decays like $e^{-(t-s)}$. All the
  required perturbation smallness holds:
  - $D_yF$ is small because $DN(0)=0$ and $(1-t)^2/t^2\to0$;
  - $D_\eta F=O(\beta e^{-c\beta})$;
  - $D_yg$ and $D_\eta g$ are exponentially small;
  - $F(0,0,\tau)$ and $g(0,0,\tau)\to0$.

  The stable directions are $L^s\oplus L^\perp$, so the codimension is $n_+(H_\star)$.
- **Draft 4, potential.** $\nabla_L\Psi=G$ because $\sum_kc_k=1$, and $|\Psi|\le C(1+\|\xi\|)$.
  Along an endpoint trajectory $\xi=o(\beta)$ and $u\sim\beta/2$, so $\xi/u\to0$. The excursion
  bound, $\text{duration}\le\operatorname{osc}_{\partial B}\Psi/c_0$, and the final contradiction
  $\Psi\ge c_0u-O(1)$ against $o(u)$ are sound.
- **Draft 4, convergence.** $\int\|R\|^2du\le C\int\beta^{-1}d\tau<\infty$ and
  $\Psi'\ge\tfrac12\|G\|^2-\tfrac12\|R\|^2$ give $\int\|G\|^2du<\infty$. With Barbalat and isolated
  roots, $\xi(u)$ converges.
- **Draft 4, Lemma (E).** Gibbs mass concentrates on the exposed face $F(v)$. With
  $\sum_kc_k=1$, limits lie in $\operatorname{aff}F(v)$ even with negative $c_k$. Every nonzero
  $v\in L$ gives a proper face, because the $b_j$ span $P_Lz+L$. Example: for a right triangle
  of tie atoms the circumcentre lies on the hypotenuse, so (E) fails. That is a genuine
  face-escape case.

## 4. What Direction A adds to the paper

The paper's Step 2 (Lemma B.3) uses the **trace** $\Theta=\tr H$: $\operatorname{div}f=\beta\Theta-d$.

- A profile with $\tr H_\star>0$ already has a null basin by Lemma B.3.
- Direction A adds two things:
  - saddles with $\tr H_\star\le0$ but one positive eigenvalue still have null basins;
  - sinks ($H_\star\prec0$ on $L$) have open basins in any dimension.
- In $d=1$, trace and eigenvalue coincide, which is why Theorem 4.7 is an "if and only if".

This answers the review's Q3 directly and turns Theorem 4.7 into an instance of a general
criterion.

**Still conditional.** The full endpoint basin needs condition (E) and hyperbolicity of all
roots. The nonhyperbolic and face-escape cases remain open and must stay listed as open.

## 5. Before integration

1. Run the four-verifier protocol on Drafts 3–4, the parts that would enter the paper.
2. Numerical check of the criterion (synthesis report, Section 15) using
   `composition_counterexample.py`-style certified exact integration in $d\in\{2,8\}$ with
   $N\ge3$ symmetric ties. Do this before claiming that it predicts basins beyond $d=1$.
3. Novelty: Liu–Zuazua (2605.12231) Remark 3.19 leaves almost-everywhere avoidance of
   non-minimising critical points open in their setting. Drafts 3–4 settle the analogous question
   for the flow-matching Gibbs layer under (E) and hyperbolicity. Claim this and nothing more.
