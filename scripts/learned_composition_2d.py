"""Learned guided label averaging on the equilateral triangle (Section 6.2, Theorem thm:spectral).

Three atoms a_k on the unit circle around z = 0, one-hot labels e_k in R^3 with Gaussian label
noise h = 1. At the query y = B e_k the label weights are p_j ~ exp(B 1{j=k}), the conditional
priors of the triangle in Section 6.2, so the composite

    v^{phi,w} = (1+w)/3 sum_k v(., B e_k) - w v_unc

has the exact profile Jacobian Gamma_w(0) = ((1-m^2) - w m^2)/2 I at z = 0, m = (e^B-1)/(e^B+2),
and its midpoint basin has positive measure for w > w_c = (1-m^2)/m^2
(Corollary cor:spectral-threshold). The question is whether a trained network's Jacobian at
the tie changes sign at the same place, and whether its samples stay at 0.

Training, variants and the stiff (ROS2) evaluation follow scripts/learned_composition.py, with the
variants cfm_v (main), cfm_x_s (data prediction with input asinh(beta x)) and the positive
control distill_x_s. Arms: L1 label average, L2 single-label guidance at B e_0, L3 the composite,
L4 guided prior average (1+w) v(., 0) - w v_unc, whose exact field is v_unc.

--exact classifies the first N_EXACT shared sources under the exact composite with the profile
integration of scripts/spectral_criterion_check.py (bounded profile |xi| < 5 at u = 1e4 means
the midpoint), and records the exact state at t = 1 - 1e-2.

    python -u -m scripts.learned_composition_2d --variant cfm_v --seed 0
    python -u -m scripts.learned_composition_2d --exact
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

from scripts.learned_composition import (DELTAS, EPS_DIAG, EPS_OUT, EVAL_RTOL, N_EVAL, N_SOURCES, P_DROP,
                                         SOURCE_SEED, TAU_OUT, ros2_states)
from scripts.spectral_criterion_check import Field as ExactField
from scripts.spectral_criterion_check import simplex, vertex_priors
from src.models.mlp_velocity import MLPVelocity

ATOMS = simplex(3)                                   # (3, 2), on the unit circle around 0
H = 1.0
B = 2.0                                              # the triangle of Section 6.2
R_LIST = (0.0, 0.5, 0.9, 1.1, 2.0, 5.0, 10.0)
R_CONTROLS = (0.0, 2.0, 10.0)
VARIANTS = ("cfm_v", "cfm_x_s", "distill_x_s")
N_EXACT = 4096
U_END = 1e4
XI_GRID = np.stack(np.meshgrid(np.linspace(-3, 3, 21), np.linspace(-3, 3, 21)), -1).reshape(-1, 2)
OUT = "results/learned_composition_2d_20261021"


def m_of(Bv: float) -> float:
    return (math.exp(Bv) - 1) / (math.exp(Bv) + 2)


def w_c(Bv: float = B) -> float:
    m = m_of(Bv)
    return (1 - m * m) / (m * m)


def atoms_on(device):
    return torch.tensor(ATOMS, dtype=torch.float32, device=device)


def exact_m(x, eps, y, cond):
    """Exact posterior mean: softmax over atoms of beta <x, a_j> + <y, e_j>/h^2 (labels kept)."""
    A = atoms_on(x.device)
    logits = (1 - eps) / eps ** 2 * x @ A.T + torch.where(cond, y / H ** 2, torch.zeros_like(y))
    return torch.softmax(logits, -1) @ A


class Field2D(torch.nn.Module):
    def __init__(self, variant: str, width: int = 128, depth: int = 4):
        super().__init__()
        self.data_pred = variant != "cfm_v"
        self.sfeat = variant.endswith("_s")
        # Condition (y * mask, mask) as in 1D; the s-variants add asinh(beta x), beta = t/(1-t)^2.
        self.net = MLPVelocity(2, cond_dim=3 + 1 + 2 * self.sfeat, width=width, depth=depth)

    def forward(self, x, eps, y, cond):
        """x: (n, 2); eps: (n, 1); y: (n, 3); cond: (n, 1) bool. Returns (m_hat, v)."""
        t = 1 - eps
        c = cond.to(x.dtype)
        feats = [torch.asinh(t * x / eps ** 2)] if self.sfeat else []
        out = self.net(x, t, torch.cat([y * c, c] + feats, -1))
        if self.data_pred:
            return out, (out - x) / eps
        return x + eps * out, out


def sample_batch(n, gen, device):
    i = torch.randint(0, 3, (n,), generator=gen, device=device)
    a = atoms_on(device)[i]
    y = torch.nn.functional.one_hot(i, 3).float() + H * torch.randn(n, 3, generator=gen, device=device)
    x0 = torch.randn(n, 2, generator=gen, device=device)
    eps = torch.rand(n, 1, generator=gen, device=device).clamp_min(1e-7)
    cond = torch.rand(n, 1, generator=gen, device=device) > P_DROP
    return dict(a=a, y=y, eps=eps, xt=eps * x0 + (1 - eps) * a, u=a - x0, cond=cond)


def boundary_layer_batch(n, gen, device):
    """Points x = eps^2 xi / t with xi ~ U([-6, 6]^2), eps log-uniform on [1e-6, 0.5] (as in 1D:
    eps = 1 would put t = 0 in the denominator); labels from the label law."""
    lo, hi = math.log(1e-6), math.log(0.5)
    eps = torch.exp(lo + (hi - lo) * torch.rand(n, 1, generator=gen, device=device))
    xi = 12 * torch.rand(n, 2, generator=gen, device=device) - 6
    b = sample_batch(n, gen, device)
    return dict(xt=eps ** 2 * xi / (1 - eps), eps=eps, y=b["y"], cond=b["cond"])


def loss_fn(field, b, variant):
    m, v = field(b["xt"], b["eps"], b["y"], b["cond"])
    if variant == "cfm_x_s":
        return ((m - b["a"]) ** 2).mean()
    if variant == "distill_x_s":
        return ((m - exact_m(b["xt"], b["eps"], b["y"], b["cond"])) ** 2).mean()
    return ((v - b["u"]) ** 2).mean()


def train(field, variant, steps, batch, lr, seed, device, log_every=1000):
    # shortcut: copy of learned_composition.train with this file's samplers; that module was left
    # untouched while its queue was starting runs from it. Merge once both queues are done.
    gen = torch.Generator(device=device).manual_seed(seed)
    opt = torch.optim.AdamW(field.parameters(), lr=lr, weight_decay=0.0)
    warm = min(1000, steps // 10)
    sched = torch.optim.lr_scheduler.LambdaLR(
        opt, lambda k: min(1.0, (k + 1) / warm) * (0.01 + 0.99 * 0.5 * (1 + math.cos(math.pi * k / steps))))
    curve, run, t0 = [], 0.0, time.time()
    for k in range(steps):
        if variant == "distill_x_s":
            b1, b2 = sample_batch(batch // 2, gen, device), boundary_layer_batch(batch // 2, gen, device)
            b = {key: torch.cat([b1[key], b2[key]]) for key in ("xt", "eps", "y", "cond")}
        else:
            b = sample_batch(batch, gen, device)
        loss = loss_fn(field, b, variant)
        opt.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(field.parameters(), 1.0)
        opt.step(); sched.step()
        run += loss.item() if (k + 1) % 50 == 0 else 0.0
        if (k + 1) % log_every == 0:
            curve.append({"step": k + 1, "loss": run / (log_every // 50), "seconds": time.time() - t0})
            run = 0.0
            if (k + 1) % (20 * log_every) == 0:
                print(f"  step {k+1} loss {curve[-1]['loss']:.5f} {curve[-1]['seconds']:.0f}s", flush=True)
    return curve


def arm(name, w, device):
    """Branch queries (a label in R^3, or None for unconditional) and coefficients summing to one."""
    e = torch.eye(3, device=device)
    if name == "L1":
        return [B * e[k] for k in range(3)], [1 / 3] * 3
    if name == "L2":
        return [B * e[0], None], [1 + w, -w]
    if name == "L3":
        return [B * e[k] for k in range(3)] + [None], [(1 + w) / 3] * 3 + [-w]
    if name == "L4":
        return [torch.zeros(3, device=device), None], [1 + w, -w]
    raise ValueError(name)


def branch_labels(queries, n, device):
    y = torch.cat([torch.zeros(n, 3, device=device) if q is None else q.expand(n, 3) for q in queries])
    cond = torch.cat([torch.full((n, 1), q is not None, device=device) for q in queries])
    return y, cond


def learned_mean(field, queries, coefs, device):
    """F(x, tau) for ros2_states: the arm's learned composite posterior mean on (n, 2) positions at
    per-source times tau (n,), in float64 and differentiable in both."""
    f64 = copy.deepcopy(field).double()
    coef = torch.tensor(coefs, dtype=torch.float64, device=device)[:, None, None]

    def F(x, tau):
        n = x.shape[0]
        y, cond = branch_labels(queries, n, device)
        m, _ = f64(x.repeat(len(queries), 1), torch.exp(-tau)[:, None].repeat(len(queries), 1),
                   y.double(), cond)
        return (coef * m.view(len(queries), n, 2)).sum(0)
    return F


def classify(x, delta):
    """0, 1, 2 near that atom; 3 near the midpoint; 4 near none of them."""
    A = atoms_on(x.device)
    c = torch.full(x.shape[:-1], 4, dtype=torch.int8, device=x.device)
    for k in range(3):
        c[(x - A[k]).norm(dim=-1) < delta] = k
    c[x.norm(dim=-1) < delta] = 3
    return c


def sources(device):
    return torch.randn(N_SOURCES, 2, generator=torch.Generator().manual_seed(SOURCE_SEED)).to(device)


def evaluate_arms(field, device, smoke=False):
    x0 = sources(device)[:512 if smoke else N_EVAL].double()
    configs = [("L1", 0.0)] + [("L3", r) for r in R_LIST] + [(a, r) for a in ("L2", "L4") for r in R_CONTROLS]
    rows, finals = [], {}
    for name, r in configs[:3] if smoke else configs:
        w = r * w_c()
        F = learned_mean(field, *arm(name, w, device), device)
        # ros2_states returns (n, 2, len(EPS_OUT)); kept as (len(EPS_OUT), n, 2).
        xs = ros2_states(F, x0, rtol=EVAL_RTOL[0]).permute(2, 0, 1)
        tight = ros2_states(F, x0, rtol=EVAL_RTOL[1]).permute(2, 0, 1) if name == "L3" else None
        row = {"arm": name, "B": B, "r": r, "w": w, "by_eps": []}
        for i, eps in enumerate(EPS_OUT):
            fine = xs[i]
            e = {"eps": eps, "max_abs": float(fine.abs().max()), "solver_class_disagree": None if tight is None
                 else float((classify(fine, 0.1) != classify(tight[i], 0.1)).float().mean())}
            for d in DELTAS:
                cls = classify(fine, d)
                e[f"occ_{d}"] = float((cls == 3).float().mean())
                if tight is not None:
                    e[f"occ_{d}_tight"] = float((classify(tight[i], d) == 3).float().mean())
                e[f"atoms_{d}"] = float((cls < 3).float().mean())
                e[f"ambiguous_{d}"] = float((cls == 4).float().mean())
            row["by_eps"].append(e)
        rows.append(row)
        if name in ("L3", "L1"):
            finals[f"{name}_r{r:g}"] = xs.cpu().numpy().astype(np.float32)
        print(f"  {name} r={r:g}: occ_0.05@1e-5 = {row['by_eps'][-1]['occ_0.05']:.4f}"
              f"  solver disagree {row['by_eps'][-1]['solver_class_disagree']}", flush=True)
    return rows, finals


def field_diagnostics(field, device):
    """Jacobian of m_hat at the tie x = 0, and boundary-layer error on x = eps^2 xi / t."""
    queries = [B * torch.eye(3, device=device)[k] for k in range(3)] + [torch.zeros(3, device=device), None]
    K = len(queries)
    jac = np.zeros((len(EPS_DIAG), K, 2, 2)); m0 = np.zeros((len(EPS_DIAG), K, 2))
    ebl = np.zeros((len(EPS_DIAG), K))
    grid = torch.tensor(XI_GRID, dtype=torch.float32, device=device)
    for i, eps in enumerate(EPS_DIAG):
        y, cond = branch_labels(queries, 1, device)
        x = torch.zeros(K, 2, device=device, requires_grad=True)
        m, _ = field(x, torch.full((K, 1), eps, device=device), y, cond)
        for j in range(2):
            (g,) = torch.autograd.grad(m[:, j].sum(), x, retain_graph=True)
            jac[i, :, j] = g.cpu().numpy()                # d m_j / d x
        m0[i] = m.detach().cpu().numpy()
        with torch.no_grad():
            n = grid.shape[0]
            y, cond = branch_labels(queries, n, device)
            xs = (eps ** 2 * grid / (1 - eps)).repeat(K, 1)
            e = torch.full((n * K, 1), eps, device=device)
            ebl[i] = ((field(xs, e, y, cond)[0] - exact_m(xs, e, y, cond)) ** 2).sum(1).view(K, n).mean(1).cpu().numpy()
    return {"jac0": jac, "m0": m0, "ebl": ebl}


def exact_classes(w, x0):
    """Exact composite from x0 (n, 2): endpoint class (0-2 atom, 3 midpoint) and x at t = 1 - 1e-2."""
    fld = ExactField(ATOMS, vertex_priors(3, B), w)
    n = len(x0)
    tau0, h = math.log(2.0), math.log(2.0) / 2000          # RK4 in x up to t = 1/2

    def f1(x, tau):
        return fld.M((1 - math.exp(-tau)) * math.exp(2 * tau) * x) - x
    x, tau = x0.copy(), 0.0
    for _ in range(2000):
        k1 = f1(x, tau); k2 = f1(x + h / 2 * k1, tau + h / 2)
        k3 = f1(x + h / 2 * k2, tau + h / 2); k4 = f1(x + h * k3, tau + h)
        x = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4); tau += h

    def f2(u, y):                                          # profile xi = beta x in the fast time u
        xi, tau = y[:-1].reshape(n, 2), y[-1]
        t = -math.expm1(-tau); beta = t * math.exp(2 * tau)
        return np.concatenate([(fld.M(xi) + xi / (t * beta)).ravel(), [1 / beta]])

    gap = lambda u, y: y[-1] - TAU_OUT[0]                 # noqa: E731
    sol = solve_ivp(f2, (0.0, U_END), np.concatenate([(2.0 * x).ravel(), [tau0]]), method="RK45",
                    rtol=1e-8, atol=1e-10, events=gap)
    assert sol.success, sol.message
    xi = sol.y[:-1, -1].reshape(n, 2)
    cls = np.where(np.linalg.norm(xi, axis=1) < 5, 3, np.argmax(xi @ ATOMS.T, 1))
    out = {"classes": cls, "tau_end": float(sol.y[-1, -1])}
    if len(sol.y_events[0]):
        ye = sol.y_events[0][0]
        t = -math.expm1(-ye[-1]); beta = t * math.exp(2 * ye[-1])
        out["x_eps_1e-2"] = ye[:-1].reshape(n, 2) / beta
    return out


def run_exact(out):
    x0 = sources("cpu")[:N_EXACT].double().numpy()
    rows, arrays = [], {}
    for r in R_LIST:
        w = r * w_c()
        start = time.time()
        res = exact_classes(w, x0)
        arrays[f"classes_r{r:g}"] = res["classes"].astype(np.int8)
        row = {"r": r, "w": w, "midpoint_fraction": float((res["classes"] == 3).mean()),
               "gamma0": ((1 - m_of(B) ** 2) - w * m_of(B) ** 2) / 2, "tau_end": res["tau_end"],
               "seconds": time.time() - start}
        if "x_eps_1e-2" in res:
            row["occ_0.05_eps_1e-2"] = float((np.linalg.norm(res["x_eps_1e-2"], axis=1) < 0.05).mean())
        rows.append(row)
        print(row, flush=True)
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "exact_classes.npz", **arrays)
    (out / "exact.json").write_text(json.dumps({"B": B, "w_c": w_c(), "n_sources": N_EXACT, "u_end": U_END,
                                                "rows": rows}, indent=1), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", choices=VARIANTS, default="cfm_v")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--steps", type=int, default=200_000)
    ap.add_argument("--batch", type=int, default=2048)
    ap.add_argument("--lr", type=float, default=3e-3)     # the 1D pilot's choice
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--exact", action="store_true")
    ap.add_argument("--eval-only", action="store_true", help="reload field.pt and re-evaluate the arms")
    args = ap.parse_args()
    if args.exact:
        run_exact(pathlib.Path(args.out) / "exact")
        return 0
    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch.manual_seed(args.seed)
    out = pathlib.Path(args.out) / f"{args.variant}_seed{args.seed}"
    out.mkdir(parents=True, exist_ok=True)
    start = time.time()
    field = Field2D(args.variant).to(device)
    if args.eval_only:
        field.load_state_dict(torch.load(out / "field.pt", map_location=device))
        summary = json.loads((out / "summary.json").read_text())
        summary.pop("dtau", None)                  # left by the RK4 evaluation it replaces
    else:
        curve = train(field, args.variant, args.steps, args.batch, args.lr, args.seed, device)
        torch.save(field.state_dict(), out / "field.pt")
        summary = {"variant": args.variant, "seed": args.seed, "steps": args.steps, "batch": args.batch,
                   "lr": args.lr, "B": B, "w_c": w_c(), "p_drop": P_DROP, "h": H, "atoms": ATOMS.tolist(),
                   "curve": curve, "python": sys.version, "torch": torch.__version__}
    field.eval()
    np.savez_compressed(out / "field_diagnostics.npz", eps_diag=np.array(EPS_DIAG), xi_grid=XI_GRID,
                        **field_diagnostics(field, device))
    rows, finals = evaluate_arms(field, device, smoke=args.smoke)
    np.savez_compressed(out / "final_states.npz", **finals)
    summary.update(arms=rows, eps_out=EPS_OUT, solver="ROS2 per source, step doubling; x then xi = beta x", rtol=EVAL_RTOL,
                   n_sources=N_EVAL, source_seed=SOURCE_SEED, seconds=time.time() - start)
    (out / "summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    print(f"wrote {out} in {summary['seconds']:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
