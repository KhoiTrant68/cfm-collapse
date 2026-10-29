"""Learned guided label averaging on the two atoms of Theorem thm:composition.

Trains flow-matching networks on D = {(-1,-ell), (1,ell)} with ell = 1 and Gaussian label
noise h = 1, then integrates, from one shared set of Gaussian sources, the learned composite

    v^{phi,w} = (1+w) (v(., +u0) + v(., -u0)) / 2 - w v_unc,      B = u0 ell / h^2 = u0,

and its controls. One network serves every B: only the query offsets u0 change. The exact
threshold is w_c = 1/sinh^2 B; guidance is swept as w = r w_c.

Variants (one network per seed unless noted):

  cfm_v        standard CFM: velocity output, t ~ U(0,1), condition dropout 0.1     [main]
  cfm_v_s      as cfm_v, with the boundary-layer coordinate asinh(s) as an extra input
  cfm_x        data prediction with data MSE, without the boundary-layer input
  cfm_v_tis    as cfm_v, but eps = 1-t is drawn half uniform, half log-uniform on
               [1e-5, 1], with importance weights so the objective is unchanged
  cfm_v_sep    as cfm_v, with a separate unconditional network instead of dropout
  cfm_x_s      data prediction m(x,t,y) with loss |m - X1|^2 (same minimiser as CFM) and
               the boundary-layer coordinate asinh(s), s = t x/(1-t)^2, as an extra input;
               trained on CFM samples only
  distill_x_s  POSITIVE CONTROL, not a CFM model: as cfm_x_s, but regressed on the exact
               posterior mean at CFM samples and at boundary-layer points

Arms integrated from the shared sources (Lk learned; the exact counterparts are computed by
scripts/learned_composition_exact.py):

  L0  conditional field at the query 0 (its exact field is the unconditional one)
  L1  label average (v(.,+u0) + v(.,-u0))/2                      exact: atoms a.s.
  L2  single-label guidance (1+w) v(.,+u0) - w v_unc              exact: atoms a.s.
  L3  guided label average, the composite above                  exact: midpoint basin iff w > w_c
  L4  guided prior average (1+w) v(.,0) - w v_unc; the prior average of the two label
      priors is uniform, so its exact field is v_unc for every w

Learned arms are integrated by ros2_states, a per-source adaptive stiff solver, in tau = -log(1-t):
dx/dtau = m_hat(x,t) - x with m_hat = x + (1-t) v, then the blow-up variable s = beta x, at two
tolerances; states are recorded at the terminal gaps eps = 1e-2 ... 1e-5. On the exact composite
it reproduces the certified basins of scripts/learned_composition_exact.py. (A fixed-step RK4 is
unstable once beta |slope| dtau > 2.8 and ejects every trajectory a field really holds at the tie;
it was used before 22 Oct 2026 and gave no midpoint mass even for the positive control.) The main variant sweeps every arm over R_LIST; the ablation variants sweep L3
over R_LIST and the controls L2, L4 over R_CONTROLS_ABLATION.

    python -u -m scripts.learned_composition --variant cfm_v --seed 0 --out results/learned_composition_20261021
    python -u -m scripts.learned_composition --variant cfm_v --seed 0 --steps 300 --smoke
    python -u -m scripts.learned_composition --variant cfm_v --seed 0 --eval-only
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import pathlib
import sys
import time

import numpy as np
import torch
from scipy.integrate import solve_ivp
from scipy.sparse import identity, kron

from scripts.composition_counterexample import ATOL, BURN_IN
from src.models.mlp_velocity import MLPVelocity

ELL, H = 1.0, 1.0
P_DROP = 0.1
B_LIST = (1.0, 2.0, 3.0)
R_LIST = (0.0, 0.5, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5, 2.0, 5.0, 10.0)
R_CONTROLS_ABLATION = (0.0, 1.0, 2.0, 10.0)
EPS_OUT = (1e-2, 1e-3, 1e-4, 1e-5)
TAU_OUT = tuple(math.log(1 / e) for e in EPS_OUT)
EVAL_RTOL = (1e-5, 1e-7)             # ROS2 tolerance of every learned arm; the second checks L3
N_SOURCES = 16384
N_EVAL = 2048                        # learned arms use the first N_EVAL sources (float64 cost)
SOURCE_SEED = 20261021               # the same sources for every arm, model and seed
DELTAS = (0.02, 0.05, 0.1)
EPS_DIAG = (0.7, 0.5, 0.4, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 1e-3, 1e-4, 1e-5)
DIAG_QUERIES = (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0)   # conditional branches; plus unconditional
S_GRID = np.linspace(-3.0, 3.0, 601)
X_GRID = 1.5 * np.sinh(12.0 * np.linspace(-1.0, 1.0, 801)) / math.sinh(12.0)  # dense near 0
VARIANTS = ("cfm_v", "cfm_v_tis", "cfm_v_sep", "cfm_x_s", "distill_x_s", "cfm_v_s", "cfm_x")
TIS_EPS_MIN = 1e-5


def w_c(B: float) -> float:
    return 1.0 / math.sinh(B) ** 2


def beta_of(tau: float) -> float:
    """beta = t/(1-t)^2 at t = 1 - exp(-tau)."""
    return -math.expm1(-tau) * math.exp(2 * tau)


def x_at(x0s, F, taus=TAU_OUT, rtol=1e-10):
    """States at the increasing times taus (default: every EPS_OUT) for independent sources x0s,
    shape (n,) or (n, d), at t = 0; returns shape (n, len(taus)) or (n, d, len(taus)).

    F(x, tau) is the field's posterior mean at x (dx/dtau = F - x). Burn-in in x to tau = BURN_IN,
    then the blow-up variable s = beta x, ds/dtau = beta F(s/beta, tau) + s/t, which stays O(1) at
    a tie. Sources do not interact, so Radau is told the Jacobian is block diagonal. (Passing the
    analytic diagonal Jacobian of an exact field made Radau take ~10^5 steps in the midpoint basin.)
    """
    x0s, taus = np.asarray(x0s, float), np.asarray(taus, float)
    shape = x0s.shape
    d = 1 if x0s.ndim == 1 else shape[1]
    early, late = taus[taus <= BURN_IN], taus[taus > BURN_IN]
    sparsity = kron(identity(shape[0]), np.ones((d, d)))

    def burn_rhs(tau, x):
        return F(x.reshape(shape), tau).ravel() - x

    burn = solve_ivp(burn_rhs, (0.0, BURN_IN), x0s.ravel(), method="Radau", jac_sparsity=sparsity,
                     t_eval=np.union1d(early, [BURN_IN]), rtol=rtol, atol=ATOL)
    assert burn.success, burn.message
    out = [burn.y[:, :len(early)]]
    if len(late):
        def rhs(tau, s):
            b = beta_of(tau)
            return b * F((s / b).reshape(shape), tau).ravel() + s / -math.expm1(-tau)

        sol = solve_ivp(rhs, (BURN_IN, late[-1]), beta_of(BURN_IN) * burn.y[:, -1], method="Radau",
                        jac_sparsity=sparsity, t_eval=late, rtol=rtol, atol=ATOL)
        assert sol.success, sol.message
        eps = np.exp(-late)
        out.append(sol.y * eps ** 2 / (1 - eps))
    return np.concatenate(out, 1).reshape(*shape, len(taus))


def exact_m(x, eps, y, cond):
    """Exact posterior mean of X1: tanh(s + y ell/h^2) at a label, tanh(s) unconditionally."""
    s = (1 - eps) * x / eps ** 2
    return torch.tanh(s + torch.where(cond, y * ELL / H ** 2, torch.zeros_like(y)))


class Field(torch.nn.Module):
    """Predicted endpoint mean m_hat(x, t, y) and velocity, for every variant."""

    def __init__(self, variant: str, width: int = 128, depth: int = 4):
        super().__init__()
        self.variant = variant
        self.data_pred = variant in ("cfm_x", "cfm_x_s", "distill_x_s")
        self.sfeat = variant.endswith("_s")
        extra = int(self.sfeat)
        if variant == "cfm_v_sep":
            self.cond_net = MLPVelocity(1, cond_dim=1 + extra, width=width, depth=depth)
            self.unc_net = (MLPVelocity(1, cond_dim=extra, width=width, depth=depth))
        else:
            # The condition enters as (y * mask, mask), so the dropped condition is not y = 0.
            self.net = MLPVelocity(1, cond_dim=2 + extra, width=width, depth=depth)

    def forward(self, x, eps, y, cond):
        """x, eps, y: (n, 1); cond: (n, 1) bool. Returns (m_hat, v)."""
        t = 1 - eps
        feats = [torch.asinh(t * x / eps ** 2)] if self.sfeat else []
        if self.variant == "cfm_v_sep":
            # Each network only on its own rows.
            c, u = cond.squeeze(1), ~cond.squeeze(1)
            out = torch.empty_like(x)
            out[c] = self.cond_net(x[c], t[c], torch.cat([y[c]] + [f[c] for f in feats], -1))
            out[u] = self.unc_net(x[u], t[u], torch.cat([f[u] for f in feats], -1) if feats else None)
        else:
            c = cond.to(x.dtype)
            out = self.net(x, t, torch.cat([y * c, c] + feats, -1))
        if self.data_pred:
            return out, (out - x) / eps
        return x + eps * out, out


def sample_batch(n, gen, device, eps_law="uniform"):
    a = (torch.randint(0, 2, (n, 1), generator=gen, device=device) * 2 - 1).float()
    y = a * ELL + H * torch.randn(n, 1, generator=gen, device=device)
    x0 = torch.randn(n, 1, generator=gen, device=device)
    u = torch.rand(n, 1, generator=gen, device=device)
    weight = torch.ones_like(u)
    if eps_law == "uniform":
        eps = u.clamp_min(1e-7)
    else:  # half U(0,1), half log-uniform on [TIS_EPS_MIN, 1]; weight = 1/q(eps)
        lu = torch.exp(math.log(TIS_EPS_MIN) * torch.rand(n, 1, generator=gen, device=device))
        pick = torch.rand(n, 1, generator=gen, device=device) < 0.5
        eps = torch.where(pick, u.clamp_min(1e-7), lu)
        q = 0.5 + 0.5 * (eps >= TIS_EPS_MIN).float() / (eps * math.log(1 / TIS_EPS_MIN))
        weight = 1.0 / q
    xt = eps * x0 + (1 - eps) * a
    cond = torch.rand(n, 1, generator=gen, device=device) > P_DROP
    return dict(a=a, y=y, x0=x0, eps=eps, xt=xt, u=a - x0, cond=cond, weight=weight)


def boundary_layer_batch(n, gen, device):
    """Points x = eps^2 s / t with s ~ U(-6, 6), eps log-uniform on [1e-6, 0.5]; labels from the
    label law. (eps up to 1 put t = 0 in the denominator whenever rand() returned 0: NaN.)"""
    lo, hi = math.log(1e-6), math.log(0.5)
    eps = torch.exp(lo + (hi - lo) * torch.rand(n, 1, generator=gen, device=device))
    s = 12 * torch.rand(n, 1, generator=gen, device=device) - 6
    a = (torch.randint(0, 2, (n, 1), generator=gen, device=device) * 2 - 1).float()
    y = a * ELL + H * torch.randn(n, 1, generator=gen, device=device)
    cond = torch.rand(n, 1, generator=gen, device=device) > P_DROP
    return dict(xt=eps ** 2 * s / (1 - eps), eps=eps, y=y, cond=cond)


def loss_fn(field, b, variant):
    if variant == "cfm_v_sep":
        ones = torch.ones_like(b["cond"])
        _, vc = field(b["xt"], b["eps"], b["y"], ones)
        _, vu = field(b["xt"], b["eps"], b["y"], ~ones)
        return ((vc - b["u"]) ** 2).mean() + ((vu - b["u"]) ** 2).mean()
    m, v = field(b["xt"], b["eps"], b["y"], b["cond"])
    if variant in ("cfm_x", "cfm_x_s"):
        return ((m - b["a"]) ** 2).mean()
    if variant == "distill_x_s":
        return ((m - exact_m(b["xt"], b["eps"], b["y"], b["cond"])) ** 2).mean()
    return ((v - b["u"]) ** 2 * b["weight"]).mean()


def train(field, variant, steps, batch, lr, seed, device, log_every=1000):
    gen = torch.Generator(device=device).manual_seed(seed)
    opt = torch.optim.AdamW(field.parameters(), lr=lr, weight_decay=0.0)
    warm = min(1000, steps // 10)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda k: min(1.0, (k + 1) / warm) * (0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * k / steps))))
    eps_law = "tilted" if variant == "cfm_v_tis" else "uniform"
    curve, run, t0 = [], 0.0, time.time()
    for k in range(steps):
        if variant == "distill_x_s":
            b1, b2 = sample_batch(batch // 2, gen, device), boundary_layer_batch(batch // 2, gen, device)
            b = {key: torch.cat([b1[key], b2[key]]) for key in ("xt", "eps", "y", "cond")}
        else:
            b = sample_batch(batch, gen, device, eps_law)
        loss = loss_fn(field, b, variant)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(field.parameters(), 1.0)
        opt.step(); sched.step()
        if (k + 1) % 50 == 0:
            loss_value = loss.item()
            if not math.isfinite(loss_value):
                raise RuntimeError(f"Non-finite training loss at step {k + 1}")
            run += loss_value
        if (k + 1) % log_every == 0:
            curve.append({"step": k + 1, "loss": run / (log_every // 50), "seconds": time.time() - t0})
            run = 0.0
            if (k + 1) % (20 * log_every) == 0:
                print(f"  step {k+1} loss {curve[-1]['loss']:.5f} {curve[-1]['seconds']:.0f}s", flush=True)
    return curve


@torch.no_grad()
def validation(field, device, n=1 << 18):
    """CFM loss and excess risk |m_hat - m*|^2 on held-out interpolant samples, by t-bin."""
    gen = torch.Generator(device=device).manual_seed(12345)
    b = sample_batch(n, gen, device)
    edges = [0.0, 0.5, 0.8, 0.9, 0.95, 0.99, 0.999, 1.0]
    t = (1 - b["eps"]).squeeze(1)
    out = []
    for cond_val in (True, False):
        cond = torch.full_like(b["cond"], cond_val)
        m, v = field(b["xt"], b["eps"], b["y"], cond)
        ms = exact_m(b["xt"], b["eps"], b["y"], cond)
        cfm = ((v - b["u"]) ** 2).squeeze(1)
        exc = ((m - ms) ** 2).squeeze(1)
        for lo, hi in zip(edges[:-1], edges[1:]):
            sel = (t >= lo) & (t < hi)
            out.append({"branch": "cond" if cond_val else "unc", "t_lo": lo, "t_hi": hi,
                        "n": int(sel.sum()), "cfm_loss": float(cfm[sel].mean()),
                        "excess_m": float(exc[sel].mean()),
                        "excess_m_max": float(exc[sel].max())})
    return out


def branch_inputs(x, queries, device):
    """Stack x once per branch; a query None is the unconditional branch."""
    n = x.shape[0]
    xs = x.repeat(len(queries), 1)
    y = torch.cat([torch.full((n, 1), 0.0 if q is None else q, device=device) for q in queries])
    cond = torch.cat([torch.full((n, 1), q is not None, device=device) for q in queries])
    return xs, y, cond


def arm_coefficients(arm, B, w):
    """Branch queries and coefficients (summing to one) of each learned arm."""
    if arm == "L0":
        return [0.0], [1.0]
    if arm == "L1":
        return [B, -B], [0.5, 0.5]
    if arm == "L2":
        return [B, None], [1 + w, -w]
    if arm == "L3":
        return [B, -B, None], [(1 + w) / 2, (1 + w) / 2, -w]
    if arm == "L4":
        return [0.0, None], [1 + w, -w]
    raise ValueError(arm)


def learned_mean(field, queries, coefs, device, dtype=torch.float64):
    """F(x, tau) for ros2_states: the arm's learned composite posterior mean sum_k c_k m_hat_k on
    (n, 1) positions at per-source times tau (n,), differentiable in both, returned in float64. The
    network must run in float64: in float32, t = 1 - eps is quantised and the field is a step
    function of time near t = 1, where the stiff solver then stalls (tested on the positive
    control: float32 reaches tau = 2 and stops; float64 reaches tau = 11.5 in about 20 s)."""
    net = copy.deepcopy(field).to(dtype)
    coef = torch.tensor(coefs, dtype=torch.float64, device=device)[:, None, None]

    def F(x, tau):
        n = x.shape[0]
        xs, y, cond = branch_inputs(x, queries, device)
        m, _ = net(xs.to(dtype), torch.exp(-tau)[:, None].repeat(len(queries), 1).to(dtype), y.to(dtype), cond)
        return (coef * m.double().view(len(queries), n, 1)).sum(0)
    return F


def ros2_states(F, x0, taus=TAU_OUT, rtol=1e-6, atol=1e-9, h0=1e-3, max_iter=1_000_000, blowup=True,
                aux=None):
    """States at the increasing times taus for independent sources x0 (n, d), float64 torch.

    F(x, tau) is the posterior mean at positions x (n, d) and per-source times tau (n,),
    differentiable in both; with aux (n, ...), F(x, tau, aux) gets each source's own row of it
    (F is only ever called on the sources still running). The flow dx/dtau = F - x is integrated in x up to BURN_IN, then (if
    blowup; for flows into a tie at 0) in the blow-up variable s = beta x
    (ds/dtau = beta F(s/beta) + s/t), with ROS2 (Verwer et al. 1999),
    an L-stable Rosenbrock method of order 2, time carried as an extra state and exact Jacobians
    from autograd. The error is estimated by step doubling: ROS2's embedded order-1 solution is not
    L-stable, so its estimate stays ~0.4|y| on stiff attracting components and the steps never
    grow; one step against two half steps is small there and large on fast repelling components,
    which keeps those accurate. Every source has its own step size, so one source's fast transient
    does not hold back the others, as it does for a shared-step solver. Returns (n, d, len(taus)).
    """
    n, d = x0.shape
    g = 1 + 1 / math.sqrt(2)
    switch = BURN_IN if blowup else math.inf                    # tau at which x becomes s
    stops = torch.tensor(sorted(set(float(t) for t in taus) | ({switch} if blowup else set())),
                         dtype=x0.dtype, device=x0.device)
    keep = [int((stops == t).nonzero()) for t in taus]
    y, tau = x0.clone(), torch.zeros(n, dtype=x0.dtype, device=x0.device)
    h = torch.full_like(tau, h0)
    nxt = torch.zeros(n, dtype=torch.long, device=x0.device)     # index of each source's next stop
    out = torch.empty(n, d, len(stops), dtype=x0.dtype, device=x0.device)

    def rhs(y, tau, blown, Fa):
        t = -torch.expm1(-tau)[:, None]
        bl = blown[:, None]
        # The unused branch must stay finite: t = 0 at tau = 0, and where() passes NaN gradients.
        b = torch.where(bl, t * torch.exp(2 * tau)[:, None], torch.ones_like(t))
        tt = torch.where(bl, t, torch.ones_like(t))
        m = Fa(y / b, tau)
        return torch.where(bl, b * m + y / tt, m - y)

    def jacobian(y, tau, blown, Fa):
        """rhs, d rhs/dy (n, d, d) and d rhs/dtau at (y, tau); sources are independent."""
        with torch.enable_grad():
            yv, tv = y.detach().requires_grad_(True), tau.detach().requires_grad_(True)
            f = rhs(yv, tv, blown, Fa)
            J = torch.empty(len(y), d, d, dtype=y.dtype, device=y.device)
            ft = torch.empty_like(f)
            for c in range(d):
                gy, gt = torch.autograd.grad(f[:, c].sum(), (yv, tv), retain_graph=c < d - 1)
                J[:, c], ft[:, c] = gy, gt
        return f.detach(), J, ft

    def solve(W, b):
        """W^{-1} b, NaN where W is singular (g h J = 1 on a repelling component): that step is rejected."""
        x, info = torch.linalg.solve_ex(W, b)
        return torch.where((info == 0)[:, None], x, torch.nan)

    def step(y, tau, h, blown, Fa, f0, J, ft):
        """One ROS2 step, time carried as an extra state."""
        W = torch.eye(d, dtype=y.dtype, device=y.device) - g * h[:, None, None] * J
        k1 = solve(W, f0 + g * h[:, None] * ft)
        with torch.no_grad():
            f1 = rhs(y + h[:, None] * k1, tau + h, blown, Fa)
        k2 = solve(W, f1 - 2 * k1 - g * h[:, None] * ft)
        return y + h[:, None] * (1.5 * k1 + 0.5 * k2)

    for _ in range(max_iter):
        act = (nxt < len(stops)).nonzero().squeeze(1)
        if len(act) == 0:
            break
        ya, ta, h_try = y[act], tau[act], h[act]
        blown = ta >= switch
        Fa = F if aux is None else (lambda x, t, a=aux[act]: F(x, t, a))
        ha = torch.minimum(h_try, stops[nxt[act]] - ta)               # do not step past a stop
        jac0 = jacobian(ya, ta, blown, Fa)
        y_full = step(ya, ta, ha, blown, Fa, *jac0)
        y_half = step(ya, ta, ha / 2, blown, Fa, *jac0)
        y_new = step(y_half, ta + ha / 2, ha / 2, blown, Fa, *jacobian(y_half, ta + ha / 2, blown, Fa))
        scale = atol + rtol * torch.maximum(ya.abs(), y_new.abs())
        err = (((y_new - y_full) / 3 / scale) ** 2).mean(1).sqrt()      # step doubling, order 2
        err = torch.nan_to_num(err, nan=math.inf)                      # singular W: retry at h/5
        ok = err <= 1
        y[act[ok]], tau[act[ok]] = y_new[ok], ta[ok] + ha[ok]
        # An accepted step that was shortened to land on a stop keeps the step it was trying.
        fac = torch.clamp(0.9 * err.clamp_min(1e-12) ** (-1 / 3), 0.2, 5.0)
        h[act] = torch.where(ok & (ha < h_try), h_try, ha * fac)
        i = act[ok & (tau[act] >= stops[nxt[act]] - 1e-12)]        # sources that reached a stop
        if len(i):
            k = nxt[i]
            st = stops[k]
            beta = (-torch.expm1(-st) * torch.exp(2 * st))[:, None]
            tau[i] = st
            out[i, :, k] = torch.where((st > switch)[:, None], y[i] / beta, y[i])
            y[i] = torch.where((st == switch)[:, None], y[i] * beta, y[i])   # x -> s at the switch
            nxt[i] = k + 1
    else:
        raise RuntimeError(f"ros2_states: {int((nxt < len(stops)).sum())} sources unfinished")
    return out[:, :, keep]


def classify(x, delta):
    """-1, 0, 1 for a state within delta of that endpoint, 2 when near none of them."""
    c = torch.full_like(x, 2, dtype=torch.int8)
    for e in (-1, 0, 1):
        c[(x - e).abs() < delta] = e
    return c


def evaluate_arms(field, device, smoke=False):
    x0 = torch.randn(N_SOURCES, generator=torch.Generator().manual_seed(SOURCE_SEED)).double().to(device)[:N_EVAL, None]
    if smoke:
        x0 = x0[:512]
    # The ablation variants sweep the controls L2, L4 on fewer guidance levels (evaluation time).
    r_controls = R_LIST if field.variant == "cfm_v" else R_CONTROLS_ABLATION
    configs = [("L0", 0.0, 0.0, 0.0)]
    for B in B_LIST:
        configs.append(("L1", B, 0.0, 0.0))
        for r in R_LIST:
            for arm in ("L2", "L3", "L4"):
                if arm == "L3" or r in r_controls:
                    configs.append((arm, B, r, r * w_c(B)))
    if smoke:
        # Exercise the stiff composite above the exact threshold, not just r=0 controls.
        configs = [("L0", 0.0, 0.0, 0.0), ("L3", 1.0, 2.0, 2.0 * w_c(1.0))]
    rows, finals = [], {}
    for arm, B, r, w in configs:
        F = learned_mean(field, *arm_coefficients(arm, B, w), device)
        xs = ros2_states(F, x0, rtol=EVAL_RTOL[0])[:, 0].T                    # (len(EPS_OUT), n)
        tight = ros2_states(F, x0, rtol=EVAL_RTOL[1])[:, 0].T if arm == "L3" else None
        if not torch.isfinite(xs).all() or (tight is not None and not torch.isfinite(tight).all()):
            raise RuntimeError(f"Non-finite trajectories: {arm}, B={B}, r={r}")
        row = {"arm": arm, "B": B, "r": r, "w": w, "by_eps": []}
        for i, eps in enumerate(EPS_OUT):
            fine = xs[i]
            e = {"eps": eps, "finite": bool(torch.isfinite(fine).all()),
                 "max_abs": float(fine.abs().max()), "solver_max_diff": None, "solver_class_disagree": None}
            if tight is not None:
                e["solver_max_diff"] = float((fine - tight[i]).abs().max())
                e["solver_class_disagree"] = float((classify(fine, 0.1) != classify(tight[i], 0.1)).float().mean())
            for d in DELTAS:
                e[f"occ_{d}"] = float((fine.abs() < d).float().mean())
                if tight is not None:
                    e[f"occ_{d}_tight"] = float((tight[i].abs() < d).float().mean())
                cls = classify(fine, d)
                e[f"frac_minus_{d}"] = float((cls == -1).float().mean())
                e[f"frac_plus_{d}"] = float((cls == 1).float().mean())
                e[f"ambiguous_{d}"] = float((cls == 2).float().mean())
            row["by_eps"].append(e)
        rows.append(row)
        if arm in ("L3", "L1", "L0") or (arm in ("L2", "L4") and r in (0.0, 1.0, 2.0, 10.0)):
            finals[f"{arm}_B{B:g}_r{r:g}"] = xs.cpu().numpy().astype(np.float32)
        print(f"  {arm} B={B:g} r={r:g}: occ_0.05@1e-5 = {row['by_eps'][-1]['occ_0.05']:.4f}"
              f"  solver disagree {row['by_eps'][-1]['solver_class_disagree']}", flush=True)
    return rows, finals


def field_diagnostics(field, device):
    """m_hat and d m_hat/dx on the boundary-layer grid x = eps^2 s/t and on X_GRID."""
    queries = list(DIAG_QUERIES) + [None]
    out = {}
    for name, grid in (("s", S_GRID), ("x", X_GRID)):
        m_all = np.zeros((len(EPS_DIAG), len(queries), len(grid)), np.float64)
        d_all = np.zeros_like(m_all)
        for i, eps in enumerate(EPS_DIAG):
            g = torch.tensor(grid, dtype=torch.float32, device=device)[:, None]
            x = eps ** 2 * g / (1 - eps) if name == "s" else g
            xs, y, cond = branch_inputs(x, queries, device)
            xs = xs.clone().requires_grad_(True)
            m, _ = field(xs, torch.full_like(xs, eps), y, cond)
            (dm,) = torch.autograd.grad(m.sum(), xs)
            m_all[i] = m.detach().view(len(queries), -1).cpu().numpy()
            d_all[i] = dm.view(len(queries), -1).cpu().numpy()
        out[f"m_{name}"] = m_all
        out[f"dmdx_{name}"] = d_all
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=VARIANTS, default="cfm_v")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--steps", type=int, default=200_000)
    ap.add_argument("--batch", type=int, default=2048)
    # 3e-3 had the lowest held-out CFM loss of {3e-4, 1e-3, 3e-3} at 50k steps (cfm_v, seed 0;
    # results/learned_composition_20261021/pilot).
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--out", default="results/learned_composition_20261021")
    ap.add_argument("--tag", default="")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--no-eval", action="store_true", help="train and validate only (LR pilot)")
    ap.add_argument("--eval-only", action="store_true", help="reload field.pt and re-evaluate the arms")
    args = ap.parse_args()
    if args.steps < 10 or args.batch < 2:
        ap.error("--steps must be at least 10 and --batch at least 2")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(args.seed)
    name = f"{args.variant}_seed{args.seed}{args.tag}"
    out = pathlib.Path(args.out) / name
    out.mkdir(parents=True, exist_ok=True)
    start = time.time()
    field = Field(args.variant).to(device)
    print(f"{name}: {sum(p.numel() for p in field.parameters())} parameters on {device}", flush=True)
    if args.eval_only:
        field.load_state_dict(torch.load(out / "field.pt", map_location=device))
        summary = json.loads((out / "summary.json").read_text())
        summary.pop("dtau", None)                  # left by the RK4 evaluation it replaces
    else:
        curve = train(field, args.variant, args.steps, args.batch, args.lr, args.seed, device)
        torch.save(field.state_dict(), out / "field.pt")
        summary = {"variant": args.variant, "seed": args.seed, "steps": args.steps, "batch": args.batch,
                   "lr": args.lr, "p_drop": P_DROP, "ell": ELL, "h": H,
                   "optimizer": "AdamW wd=0, cosine, clip 1", "train_seconds": time.time() - start,
                   "curve": curve, "python": sys.version, "torch": torch.__version__}
        summary.update(data_prediction=field.data_pred, boundary_layer_input=field.sfeat,
                       parameter_count=sum(p.numel() for p in field.parameters()),
                       cuda_version=torch.version.cuda,
                       device=torch.cuda.get_device_name() if device == "cuda" else "cpu")
    field.eval()
    summary["validation"] = validation(field, device)
    if not args.no_eval:
        summary["field_grids"] = {"eps_diag": EPS_DIAG, "queries": list(DIAG_QUERIES) + ["unc"]}
        np.savez_compressed(out / "field_diagnostics.npz", s_grid=S_GRID, x_grid=X_GRID,
                            eps_diag=np.array(EPS_DIAG), **field_diagnostics(field, device))
        rows, finals = evaluate_arms(field, device, smoke=args.smoke)
        summary.update(arms=rows, eps_out=EPS_OUT, solver="ROS2 per source, step doubling; x then s = beta x", rtol=EVAL_RTOL,
                       n_sources=512 if args.smoke else N_EVAL, source_seed=SOURCE_SEED,
                       smoke=args.smoke)
        np.savez_compressed(out / "final_states.npz", **finals)
    summary["seconds"] = time.time() - start
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(f"wrote {out} in {summary['seconds']:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
