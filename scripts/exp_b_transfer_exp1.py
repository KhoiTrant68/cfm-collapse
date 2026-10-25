"""EXP-B: is the error along learned trajectories controlled by the training loss? (EXP-1)

Theorem thm:risktransfer bounds the endpoint by the error along the learned path,
m(t) = E|Delta(Z_t, t)|^2, while training only controls the error on the teacher law,
r(t) = E|Delta(Y_t, t)|^2; the ratio K(t) = m(t)/r(t) is what decides whether a small loss
certifies the endpoint. This script measures both on the trained EXP-1 networks
(results/exp1/linear-gaussian-mlp-{h0,h0p1}-seed100{1..5}-200k, checkpoints 1k ... 200k) at the
20 training conditions that src/train.py evaluates, with N_SOURCES shared Gaussian sources each:

  Y_t   the exact flow from X0: t a + (1-t) X0 at h = 0, the exact kernel flow at h > 0;
  Z_t   the network's flow from the same X0;
  Delta = v_theta - v*, with v* the exact field at the condition, so (1-t) Delta = m_hat - m*;
  B_T = eps_T int sqrt(m) dtau   (h = 0: >= ||Z_T - Y_T||_{L2} by Minkowski; a consistency check.
        At h > 0 the teacher field is not linear and B_T bounds nothing; it is not reported),
  B_T^loss = eps_T int sqrt(r) dtau, what a loss-only argument (K = 1) would claim (h = 0),
  ||Z_T - Y_T||_{L2}, measured, at T = 1 - eps_T for eps_T in EPS_T.

Theorem thm:transfer (h = 0): per trajectory, |Z_T - a| against (1-T)|Delta(Z_T, T)|; the paper
notes these coincide whenever v_theta stays bounded, so this is reported as a sanity check only.

Proposition prop:localtransfer (h > 0): at t0 in T0, for each trajectory let a be the atom nearest
to Z_{t0}, D its distance to the next atom and rho = RHO_FRACTION D. Premise on the path:
|Z_{t0} - a| < rho/4 and (1-t)|Delta(Z_t, t)| <= rho/4 on the grid t >= t0. Premise on the ball
(the proposition's): the same bound and |m*(x, t) - a| <= rho/4 at BALL_POINTS points of
B(a, rho) at every grid time t >= t0. Conclusion: |Z_t - a| < rho on the grid t >= t0.

Both flows are integrated by ros2_states (scripts/learned_composition.py) in tau = -log(1-t),
float64, without the blow-up variable (these trajectories end at atoms, not at a tie).

    python -u -m scripts.exp_b_transfer_exp1 --runs linear-gaussian-mlp-h0-seed1001-200k
    python -u -m scripts.exp_b_transfer_exp1 --summarize
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
import time

import numpy as np
import torch

from scripts.learned_composition import ros2_states
from src.models.mlp_velocity import build_model
from src.problems.linear_gaussian import LinearGaussianProblem
from src.utils import load_yaml

EXP1 = pathlib.Path("results/exp1")
OUT = pathlib.Path("results/exp_b_transfer_20261022")
RUNS = [f"linear-gaussian-mlp-{h}-seed{s}-200k" for h in ("h0", "h0p1") for s in range(1001, 1006)]
N_SOURCES = 1000
SOURCE_SEED = 20261022
EPS_T = (1e-2, 1e-3, 1e-4)
TAU_GRID = np.union1d(np.linspace(0.0, math.log(1e4), 186), [math.log(1 / e) for e in EPS_T])
T0 = (0.99, 0.999, 0.9999)
RHO_FRACTION = 0.4                   # rho = 0.4 D, inside the proposition's (0, D/2)
BALL_POINTS = 256
RTOL = 1e-6


def trapezoid(f, x):
    return float(((f[1:] + f[:-1]) / 2 * np.diff(x)).sum())


def load_run(name, device):
    """Config, problem, training set and the evaluated condition indices of one EXP-1 run."""
    run = EXP1 / name
    cfg = load_yaml(run / "config.yaml")
    dc = cfg["data"]
    seed = int(dc.get("problem_seed", cfg["seed"]))
    problem = LinearGaussianProblem.create(d=dc["d"], k=dc["k"], sigma_obs=dc["sigma_obs"], seed=seed,
                                           prior_std=dc.get("prior_std", 1.0), A_kind=dc.get("A_kind", "random"))
    saved = json.loads((run / "problem.json").read_text())
    assert np.allclose(problem.A.numpy(), saved["A"]), f"{name}: regenerated operator differs"
    X, Y = problem.sample_dataset(dc["N"], seed=seed + 1)
    idx = sorted(set(torch.linspace(0, X.shape[0] - 1, cfg["eval"]["n_eval_train"]).round().long().tolist()))
    return cfg, X.to(device), Y.to(device), idx


def exact_mean(X, Y, h):
    """m*(x, tau) at the conditions y (one per row): the posterior mean over the atoms X."""
    def m(x, tau, y):
        t, eps = -torch.expm1(-tau)[:, None], torch.exp(-tau)[:, None]
        logit = -((x[:, None, :] - t[:, :, None] * X[None]) ** 2).sum(-1) / (2 * eps ** 2)
        if h > 0:
            logit = logit - ((y[:, None, :] - Y[None]) ** 2).sum(-1) / (2 * h ** 2)
        else:   # hard label: only the condition's own atom (labels identify, Assumption as:standing)
            logit = logit + torch.where(((y[:, None, :] - Y[None]) ** 2).sum(-1) == 0, 0.0, -math.inf)
        return torch.softmax(logit, 1) @ X
    return m


def learned_mean(model):
    """m_hat(x, tau, y) = x + (1-t) v_theta(x, t, y), float64."""
    def m(x, tau, y):
        return x + torch.exp(-tau)[:, None] * model(x, -torch.expm1(-tau)[:, None], y)
    return m


def at_grid(fn, xs, y):
    """fn(x, tau, y) on states xs (n, d, len(TAU_GRID)) -> (n, d, len(TAU_GRID))."""
    tg = torch.tensor(TAU_GRID, dtype=xs.dtype, device=xs.device)
    with torch.no_grad():
        return torch.stack([fn(xs[:, :, j], tg[j].expand(len(xs)), y) for j in range(len(tg))], -1)


def evaluate(cfg, model, X, Y, idx, device):
    h = float(cfg["train"].get("y_noise_h", 0.0))
    d = X.shape[1]
    x0 = torch.randn(N_SOURCES, d, generator=torch.Generator().manual_seed(SOURCE_SEED), dtype=torch.float64)
    x0 = x0.to(device).repeat(len(idx), 1)                         # (conditions * sources, d)
    y = Y[idx].repeat_interleave(N_SOURCES, 0)
    a = X[idx].repeat_interleave(N_SOURCES, 0)
    m_star, m_hat = exact_mean(X, Y, h), learned_mean(model)

    Z = ros2_states(m_hat, x0, TAU_GRID, rtol=RTOL, blowup=False, aux=y)
    if h > 0:
        Yt = ros2_states(m_star, x0, TAU_GRID, rtol=RTOL, blowup=False, aux=y)
    else:
        t = torch.tensor(-np.expm1(-TAU_GRID), dtype=torch.float64, device=device)
        Yt = t * a[:, :, None] + (1 - t) * x0[:, :, None]
    eps = torch.tensor(np.exp(-TAU_GRID), dtype=torch.float64, device=device)
    scaled_Z = at_grid(m_hat, Z, y) - at_grid(m_star, Z, y)         # (1-t) Delta(Z_t, t)
    scaled_Y = at_grid(m_hat, Yt, y) - at_grid(m_star, Yt, y)
    per = lambda v: v.view(len(idx), N_SOURCES, *v.shape[1:])       # noqa: E731
    m = per((scaled_Z ** 2).sum(1)).mean(1) / eps ** 2              # (conditions, grid)
    r = per((scaled_Y ** 2).sum(1)).mean(1) / eps ** 2

    rows = []
    for c, i in enumerate(idx):
        row = {"condition": i, "tau": TAU_GRID.tolist(), "m": m[c].tolist(), "r": r[c].tolist(), "at_T": []}
        for e_T in EPS_T:
            j = int(np.argmin(np.abs(TAU_GRID - math.log(1 / e_T))))
            tg = TAU_GRID[: j + 1]
            gap = per(Z[:, :, j] - Yt[:, :, j])[c]
            zT = per(Z[:, :, j])[c]
            row["at_T"].append({
                "eps_T": e_T,
                "B_T": e_T * trapezoid(np.sqrt(m[c, : j + 1].cpu().numpy()), tg),
                "B_T_loss": e_T * trapezoid(np.sqrt(r[c, : j + 1].cpu().numpy()), tg),
                "dist_ZY_L2": float((gap ** 2).sum(1).mean().sqrt()),
                "dist_Z_atom_L2": float(((zT - X[i]) ** 2).sum(1).mean().sqrt()),
                "trace_cov_Z": float(torch.trace(torch.cov(zT.T))),
                # Theorem thm:transfer at T: |Z_T - a| and (1-T)|Delta(Z_T, T)| per trajectory
                "thm51_dist": per((Z[:, :, j] - a).norm(dim=1))[c].median().item(),
                "thm51_scaled_err": per(scaled_Z[:, :, j].norm(dim=1))[c].median().item()})
        rows.append(row)
    out = {"h": h, "rows": rows}
    if h > 0:
        out["prop52"] = local_transfer(Z, scaled_Z, X, y, m_star, m_hat, len(idx), device)
    return out


def local_transfer(Z, scaled_Z, X, y, m_star, m_hat, n_cond, device):
    """Premises and conclusion of Proposition prop:localtransfer along the paths and on the ball."""
    tg = torch.tensor(TAU_GRID, dtype=torch.float64, device=device)
    t_grid = -torch.expm1(-tg)
    D_all = torch.cdist(X, X) + torch.eye(len(X), dtype=X.dtype, device=device) * 1e9
    gen = torch.Generator(device=device).manual_seed(5)
    res = []
    for t0 in T0:
        j0 = int(torch.searchsorted(t_grid, torch.tensor(t0, dtype=t_grid.dtype, device=device)))
        z0 = Z[:, :, j0]
        k = torch.cdist(z0, X).argmin(1)                           # nearest atom at t0
        a, rho = X[k], RHO_FRACTION * D_all[k].min(1).values
        p1 = (z0 - a).norm(dim=1) < rho / 4
        tail = scaled_Z[:, :, j0:].norm(dim=1)                       # (n, grid >= t0)
        p2_path = (tail <= (rho / 4)[:, None]).all(1)
        concl = ((Z[:, :, j0:] - a[:, :, None]).norm(dim=1) < rho[:, None]).all(1)
        # the proposition's premise on the whole ball, once per (condition, atom) pair
        p2_ball = torch.zeros_like(p1)
        pair = (torch.arange(len(z0), device=device) // N_SOURCES) * len(X) + k
        for key in torch.unique(pair[p1]).tolist():
            sel = pair == key
            i0 = int(sel.nonzero()[0])
            u = torch.randn(BALL_POINTS, X.shape[1], generator=gen, device=device, dtype=torch.float64)
            u = u / u.norm(dim=1, keepdim=True) * torch.rand(BALL_POINTS, 1, generator=gen, device=device,
                                                             dtype=torch.float64) ** (1 / X.shape[1])
            pts = a[i0] + rho[i0] * u
            yy = y[i0].expand(BALL_POINTS, -1)
            ok = True
            for j in range(j0, len(tg)):
                tt = tg[j].expand(BALL_POINTS)
                with torch.no_grad():
                    ms, mh = m_star(pts, tt, yy), m_hat(pts, tt, yy)
                if (mh - ms).norm(dim=1).max() > rho[i0] / 4 or (ms - a[i0]).norm(dim=1).max() > rho[i0] / 4:
                    ok = False
                    break
            p2_ball[sel] = ok
        frac = lambda v: float(v.double().mean())                    # noqa: E731
        res.append({"t0": t0, "p1": frac(p1), "p1_p2_path": frac(p1 & p2_path),
                    "p1_p2_ball": frac(p1 & p2_ball),
                    "conclusion_given_path": frac(concl[p1 & p2_path]) if (p1 & p2_path).any() else None,
                    "conclusion_given_ball": frac(concl[p1 & p2_ball]) if (p1 & p2_ball).any() else None,
                    "conclusion_all": frac(concl)})
    return res


def run(names, device):
    for name in names:
        cfg, X, Y, idx = load_run(name, device)
        for ck in sorted((EXP1 / name / "checkpoints").glob("ckpt_*.pt"), key=lambda p: int(p.stem[5:])):
            out_path = OUT / name / f"{ck.stem}.json"
            if out_path.exists():
                continue
            start = time.time()
            model = build_model(cfg, data_dim=X.shape[1], cond_dim=Y.shape[1])
            model.load_state_dict(torch.load(ck, map_location="cpu")["model_state"])
            model = model.double().to(device).eval()
            res = evaluate(cfg, model, X, Y, idx, device)
            res.update(run=name, checkpoint=int(ck.stem[5:]), n_sources=N_SOURCES, source_seed=SOURCE_SEED,
                       rtol=RTOL, seconds=time.time() - start, torch=torch.__version__, python=sys.version)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(res), encoding="utf-8")
            print(f"{name} {ck.stem}: {res['seconds']:.0f}s", flush=True)


def summarize():
    """Median over the 20 conditions, then mean +- population sd over the 5 seeds."""
    recs = [json.loads(p.read_text()) for p in sorted(OUT.glob("*/ckpt_*.json"))]
    L = ["# EXP-B: error along learned trajectories against the training-law error", "",
         f"{len({r['run'] for r in recs})} runs; per condition {N_SOURCES} sources; median over the 20 conditions, "
         "then mean ± sd over seeds. K(t) = m(t)/r(t).", ""]
    fmt = lambda v: f"{np.mean(v):.3g} ± {np.std(v):.2g}"            # noqa: E731
    eps_rows = (0.5, 0.1, 1e-2, 1e-3, 1e-4)
    for h in sorted({r["h"] for r in recs}):
        L += [f"## h = {h:g}", "",
              "| checkpoint | " + " | ".join(f"K at 1-t={e:g}" for e in eps_rows) + " | ‖Z_T−Y_T‖ (ε_T=1e-3) | B_T | "
              "B_T^loss | ‖Z_T−a‖ |", "|---|" + "---|" * (len(eps_rows) + 4)]
        if h > 0:
            L[-2] = L[-2].replace(" | B_T | B_T^loss | ‖Z_T−a‖ |", " | B_T | B_T^loss | ‖Z_T−a‖ (own atom) |")
            L.insert(len(L) - 2, "B_T and B_T^loss bound nothing at h > 0 (Theorem C.1 needs the hard-label "
                     "teacher); they are shown only for comparison with h = 0.\n")
        for ck in sorted({r["checkpoint"] for r in recs if r["h"] == h}):
            rs = [r for r in recs if r["h"] == h and r["checkpoint"] == ck]
            tau = np.array(rs[0]["rows"][0]["tau"])
            ks = {e: [] for e in eps_rows}
            at = {k: [] for k in ("dist_ZY_L2", "B_T", "B_T_loss", "dist_Z_atom_L2")}
            for r in rs:
                K = np.array([np.array(c["m"]) / np.array(c["r"]) for c in r["rows"]])
                for e in eps_rows:
                    ks[e].append(np.median(K[:, int(np.argmin(np.abs(tau - math.log(1 / e))))]))
                for key in at:
                    at[key].append(np.median([c["at_T"][1][key] for c in r["rows"]]))
            L.append(f"| {ck} | " + " | ".join(fmt(ks[e]) for e in eps_rows) + " | " +
                     " | ".join(fmt(at[k]) for k in ("dist_ZY_L2", "B_T", "B_T_loss", "dist_Z_atom_L2")) + " |")
        if h > 0:
            L += ["", "Proposition 5.2 (fractions of all trajectories; conclusion rates among those meeting the premise):", "",
                  "| checkpoint | t0 | P1 | P1∧P2 path | P1∧P2 ball | conclusion given path | conclusion given ball |",
                  "|---|---|---|---|---|---|---|"]
            for ck in sorted({r["checkpoint"] for r in recs if r["h"] == h}):
                rs = [r for r in recs if r["h"] == h and r["checkpoint"] == ck]
                for i, t0 in enumerate(T0):
                    vals = [r["prop52"][i] for r in rs]
                    g = lambda k: fmt([v[k] for v in vals if v[k] is not None]) if any(v[k] is not None for v in vals) else "–"  # noqa: E731
                    L.append(f"| {ck} | {t0} | {g('p1')} | {g('p1_p2_path')} | {g('p1_p2_ball')} | "
                             f"{g('conclusion_given_path')} | {g('conclusion_given_ball')} |")
        L.append("")
    (OUT / "SUMMARY.md").write_text("\n".join(L), encoding="utf-8")
    figure(recs)
    print("wrote", OUT / "SUMMARY.md", "and fig_exp_b.pdf")


def figure(recs):
    """(a) K(t) against 1-t; (b) measured ||Z_T - Y_T|| against the loss-only B_T^loss, h = 0."""
    from scripts.figstyle import COLORS, OI, panel_tag, style, use_paper_style
    import matplotlib.pyplot as plt
    use_paper_style()
    fig, (a, b) = plt.subplots(1, 2, figsize=(10, 3.8))
    colors = {1000: OI["sky"], 30000: OI["orange"], 200000: COLORS["generated"]}
    for h, ls in ((0.0, "-"), (0.1, "--")):
        for ck, col in colors.items():
            rs = [r for r in recs if r["h"] == h and r["checkpoint"] == ck]
            if not rs:
                continue
            eps = np.exp(-np.array(rs[0]["rows"][0]["tau"]))
            K = np.mean([np.median([np.array(c["m"]) / np.array(c["r"]) for c in r["rows"]], 0) for r in rs], 0)
            a.loglog(eps, K, ls, color=col, lw=1.5, label=f"h={h:g}, {ck // 1000}k steps")
    e = np.geomspace(1e-4, 1e-1, 10)
    a.loglog(e, 0.5 * e ** -2, ":", color=COLORS["theory"], lw=1, label=r"$\propto(1-t)^{-2}$")
    a.invert_xaxis(); a.set_xlabel(r"$1-t$"); a.set_ylabel(r"$K(t)=m(t)/r(t)$")
    a.set_title("error on learned paths / on the teacher law"); a.legend(fontsize=7)
    cks = sorted({r["checkpoint"] for r in recs if r["h"] == 0.0})
    for key, col, lab in (("dist_ZY_L2", COLORS["generated"], r"measured $\|Z_T-Y_T\|_{L^2}$"),
                          ("B_T_loss", COLORS["reference"], r"loss-only bound $B_T$ with $K\equiv1$")):
        v = [[np.median([c["at_T"][1][key] for c in r["rows"]]) for r in recs if r["h"] == 0.0 and r["checkpoint"] == ck]
             for ck in cks]
        b.errorbar(cks, [np.mean(x) for x in v], yerr=[np.std(x) for x in v], marker="o", ms=4, capsize=2,
                   color=col, label=lab)
    b.set_xscale("log"); b.set_yscale("log"); b.set_xlabel("training step"); b.set_ylabel(r"at $T=1-10^{-3}$, $h=0$")
    b.set_title("what the loss certifies against the endpoint"); b.legend(fontsize=7)
    for ax, tag in ((a, "a"), (b, "b")):
        style(ax); panel_tag(ax, tag)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_exp_b.{ext}", bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    global N_SOURCES
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", default=RUNS)
    ap.add_argument("--summarize", action="store_true")
    ap.add_argument("--n-sources", type=int, default=N_SOURCES, help="fewer for a smoke run")
    args = ap.parse_args()
    N_SOURCES = args.n_sources
    if args.summarize:
        summarize()
    else:
        run(args.runs, "cuda" if torch.cuda.is_available() else "cpu")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
