"""When does the index posterior collapse? Exact, no training.

The theory says where a conditional flow ends. It does not say how fast it gets there,
and that is the gap the paper concedes in Section 3.7. What can be computed exactly is
the time at which the flow's own weights select one atom. Along a trajectory of the
exact population flow the index posterior is

    w_i(x_t, t, y)  proportional to  pi_0((x_t - t x^i)/(1-t)) K_h(y - y^i),

and its effective number of atoms n_eff(t) = 1 / sum_i w_i^2 falls from the label
window's size at t=0 to 1 at t=1. This script draws that fall.

  (a) n_eff(t) along exact trajectories on the real EXP-1 instance (d=2, N=200) for
      several bandwidths, and for the unconditional field (h = infinity). The label
      factor sets where the curve starts; the spatial factor sets when it reaches 1.
  (b) the time t_c at which the spatial factor alone has selected one atom (median
      n_eff <= 2) for Gaussian atoms in dimension d. This is the "collapse time" of
      Biroli et al. (2024) for the flow-matching clock, computed rather than assumed.

    uv run python -m scripts.make_collapse_time_figure

Writes paper/figures/fig_collapse_time.png and results/collapse_time/collapse_time.json.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.figstyle import COLORS, H_COLORS, OI, panel_tag, save, use_paper_style  # noqa: E402

use_paper_style()

RESULTS = Path("results/collapse_time")
T_END = 1.0 - 1e-3


def graded(n_steps: int) -> np.ndarray:
    """Uniform in t up to 0.9, geometric in 1-t after: the early collapse at large d needs the former."""
    n_early = n_steps // 2
    early = np.linspace(0.0, 0.9, n_early, endpoint=False)
    late = 1.0 - np.geomspace(0.1, 1.0 - T_END, n_steps - n_early + 1)
    return np.concatenate([early, late])


def log_spatial(x: np.ndarray, t: float, X: np.ndarray) -> np.ndarray:
    """log pi_0((x - t x^i)/(1-t)) up to a constant, for every row of x and every atom."""
    s2 = (1.0 - t) ** 2
    # ||x - t x^i||^2 = ||x||^2 - 2 t x.x^i + t^2 ||x^i||^2 ; the first term is constant in i
    cross = x @ X.T
    return (2.0 * t * cross - t * t * np.sum(X * X, axis=1)[None, :]) / (2.0 * s2)


def weights(x: np.ndarray, t: float, X: np.ndarray, log_label: np.ndarray | None) -> np.ndarray:
    lg = log_spatial(x, t, X)
    if log_label is not None:
        lg = lg + log_label[None, :]
    lg -= lg.max(axis=1, keepdims=True)
    w = np.exp(lg)
    return w / w.sum(axis=1, keepdims=True)


def field(x: np.ndarray, t: float, X: np.ndarray, log_label: np.ndarray | None) -> np.ndarray:
    w = weights(x, t, X, log_label)
    return (w @ X - x) / (1.0 - t)


def n_eff_curve(X: np.ndarray, log_label, x0: np.ndarray, n_steps: int, rk4: bool) -> np.ndarray:
    ts = graded(n_steps)
    x = x0.copy()
    out = np.empty((len(ts), len(x0)))
    for k, (a, b) in enumerate(zip(ts[:-1], ts[1:])):
        w = weights(x, a, X, log_label)
        out[k] = 1.0 / np.sum(w * w, axis=1)
        dt = b - a
        if rk4:
            k1 = field(x, a, X, log_label)
            k2 = field(x + dt / 2 * k1, a + dt / 2, X, log_label)
            k3 = field(x + dt / 2 * k2, a + dt / 2, X, log_label)
            k4 = field(x + dt * k3, b, X, log_label)
            x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        else:
            x = x + dt * field(x, a, X, log_label)
    w = weights(x, ts[-1], X, log_label)
    out[-1] = 1.0 / np.sum(w * w, axis=1)
    return ts, out


def panel_a() -> dict:
    import torch
    from src.problems.linear_gaussian import LinearGaussianProblem

    prob = LinearGaussianProblem.create(d=2, k=1, sigma_obs=0.1, seed=0)
    Xt, Yt = prob.sample_dataset(200, seed=1)
    X, Y = Xt.to(torch.float64).numpy(), Yt.to(torch.float64).numpy()
    i = int(np.argmin(np.abs(Y[:, 0] - np.median(Y[:, 0]))))
    y = Y[i]
    rng = np.random.default_rng(0)
    x0 = rng.normal(size=(160, 2))
    out = {}
    for h in (0.05, 0.1, 0.5, np.inf):
        if np.isinf(h):
            ll = None
        else:
            d2 = np.sum((Y - y[None, :]) ** 2, axis=1)
            ll = -d2 / (2.0 * h * h)
        ts, curves = n_eff_curve(X, ll, x0, 300, rk4=True)
        out[h] = (ts, curves)
    return out


def panel_b(dims, sizes, n_paths=24, n_steps=220) -> dict:
    res = {}
    for N in sizes:
        rng = np.random.default_rng(N)
        row = []
        for d in dims:
            if N * d > 12_000_000 and d > 512:
                row.append(None)
                continue
            X = rng.normal(size=(N, d))
            x0 = rng.normal(size=(n_paths, d))
            ts, curves = n_eff_curve(X, None, x0, n_steps, rk4=False)
            med = np.median(curves, axis=1)
            hit = np.nonzero(med <= 2.0)[0]
            row.append(float(ts[hit[0]]) if len(hit) else None)
            print(f"  N={N:5d} d={d:5d}  t_c={row[-1]}")
        res[N] = row
    return res


def main() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    a = panel_a()
    dims = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 3072]
    sizes = [50, 500, 2000]
    b = panel_b(dims, sizes)

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.6))
    ax = axes[0]
    labels = {0.05: "h = 0.05", 0.1: "h = 0.1", 0.5: "h = 0.5", np.inf: "unconditional"}
    for h, (ts, curves) in a.items():
        c = H_COLORS.get(h, COLORS["path"]) if not np.isinf(h) else OI["black"]
        med = np.median(curves, axis=1)
        lo, hi = np.percentile(curves, [10, 90], axis=1)
        x = 1.0 - ts
        ax.plot(x, med, color=c, lw=1.8, label=labels[h])
        ax.fill_between(x, lo, hi, color=c, alpha=0.15, lw=0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.invert_xaxis()
    ax.set_xlabel(r"$1-t$")
    ax.set_ylabel(r"$n_{\mathrm{eff}}$ of the index posterior")
    ax.axhline(1.0, color=COLORS["theory"], ls="--", lw=0.9)
    ax.legend(loc="upper right", fontsize=8)
    panel_tag(ax, "a")

    ax = axes[1]
    cols = {50: OI["sky"], 500: OI["green"], 2000: OI["blue"]}
    for N, row in b.items():
        xs = [d for d, v in zip(dims, row) if v is not None]
        ys = [v for v in row if v is not None]
        ax.plot(xs, ys, "o-", color=cols[N], lw=1.6, ms=4, label=fr"$N={N}$")
    ax.set_xscale("log")
    ax.set_xlabel(r"dimension $d$")
    ax.set_ylabel(r"collapse time $t_c$ (spatial factor)")
    dd = np.geomspace(dims[0], dims[-1], 100)
    for N in sizes:
        r = 2.0 * np.sqrt(np.log(N) / dd)
        ax.plot(dd, r / (1.0 + r), color=cols[N], ls=":", lw=1.1)
    ax.plot([], [], color="0.3", ls=":", lw=1.1, label=r"$t_c/(1-t_c)=2\sqrt{\log N/d}$")
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower left", fontsize=8)
    panel_tag(ax, "b")

    fig.tight_layout()
    save(fig, "fig_collapse_time.png")

    payload = {
        "panel_b": {str(N): {"dims": dims, "t_c": row} for N, row in b.items()},
        "panel_a_final_n_eff": {("inf" if np.isinf(h) else str(h)):
                                float(np.median(curves[-1])) for h, (ts, curves) in a.items()},
        "panel_a_initial_n_eff": {("inf" if np.isinf(h) else str(h)):
                                  float(np.median(curves[0])) for h, (ts, curves) in a.items()},
    }
    (RESULTS / "collapse_time.json").write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload["panel_a_initial_n_eff"]), json.dumps(payload["panel_a_final_n_eff"]))


if __name__ == "__main__":
    main()
