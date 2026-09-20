"""Flow portraits: the collapse, and the four interventions, in trajectory space.

The paper's claims are about where a conditional flow *sends* its samples, so the
figures here draw the trajectories themselves rather than summarising them by a
scalar (the idiom of Delay Flow Matching, ICLR 2026, Fig. 2), put the mixture
weight of Theorem 1 on the atoms as marker area (Source-Guided Flow Matching,
arXiv:2508.14807, Fig. 3), and keep one colour per role across every panel.

Everything is computed on the real EXP-1 instance ($d=2$, $k=1$, $N=200$,
$\\sigma_{obs}=0.1$, seed 0) -- the same problem and the same 200 atoms the
trained runs in ``results/exp1`` used. Trained panels integrate the network from
its checkpoint; theory panels integrate the closed-form population field. Nothing
is sketched.

    uv run python -m scripts.make_flow_portraits            # all three figures
    uv run python -m scripts.make_flow_portraits --only body

Writes into paper/figures:
    fig_flow_portrait.png     body Figure 1: trained early / trained late /
                              population optimum at h* / endpoint smoothing
    fig_collapse_training.png appendix: the same condition as training proceeds
    fig_interventions.png     appendix: the four interventions side by side

Self-checks (printed, and asserted) before anything is drawn:
    * the generic field reduces to ``kernel_theory.kernel_field`` at rho = sigma = 0;
    * the bisected h* really solves tr Cov_h = tr Sigma_post;
    * the endpoint-smoothed flow's own samples reproduce Cov_h + rho^2 I.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import torch

from scripts.figstyle import (COLORS, flow_exact, flow_model, graded_times,
                              load_exp1_model, panel_tag, portrait_axis,
                              posterior_ellipse, save, shared_legend,
                              trajectory_bundle, use_paper_style, weight_scatter)
from src.metrics.kernel_theory import (kernel_field, kernel_moments,
                                       kernel_weights, n_eff)
from src.problems.linear_gaussian import LinearGaussianProblem

import matplotlib.pyplot as plt

RUN_H0 = Path("results/exp1/exp1_cond_seed0_mr")   # conditional, h=0, checkpoints kept
N_PATHS = 160
N_STEPS = 400
T_END = 1.0 - 1e-3


# --------------------------------------------------------------------------- #
# the population field of every intervention, in one formula
# --------------------------------------------------------------------------- #
def atom_field(x: torch.Tensor, t: float, X: torch.Tensor, Y: torch.Tensor,
               y: torch.Tensor, h: float, *, rho: float = 0.0,
               sigma: float = 0.0, label_weights: torch.Tensor | None = None
               ) -> torch.Tensor:
    """v*(x,t,y) for the linear interpolant, with optional endpoint/path noise.

    Conditioning on the index, X_t is Gaussian about t x^i with scale s_t, and the
    L2-optimal velocity is an index-posterior average of per-atom affine fields:

        v*(x,t) = sum_i w_i [ x^i + c(t) (x - t x^i) ],
        w_i     ∝ phi_{s_t}(x - t x^i) K_h(y - y^i),

    with, writing r = x - t x^i,

        plain / label smoothing   s_t^2 = (1-t)^2,               c = -(1-t)/s_t^2
        endpoint smoothing (rho)  s_t^2 = (1-t)^2 + t^2 rho^2,   c = (t rho^2 - (1-t))/s_t^2
        interpolant noise (sigma) s_t^2 = (1-t)^2 + gamma^2,     c = (gamma' gamma - (1-t))/s_t^2

    where gamma(t) = sigma sqrt(t(1-t)), so gamma' gamma = sigma^2 (1-2t)/2. The
    first is the c = -1/(1-t) of Proposition 8; the second is eq. (tgtfield); the
    third is the field of the corrected pathwise target. ``label_weights`` lets a
    caller override K_h (used for the unconditional branch of guidance).
    """
    x = x.to(torch.float64)
    one_m_t = max(1.0 - t, 1e-6)
    gam2 = (sigma ** 2) * t * one_m_t
    s2 = one_m_t ** 2 + (t ** 2) * (rho ** 2) + gam2
    c = (t * rho ** 2 + 0.5 * (sigma ** 2) * (1.0 - 2.0 * t) - one_m_t) / s2

    r = x[:, None, :] - t * X[None, :, :]                      # (P,N,d)
    log_spatial = -0.5 * (r ** 2).sum(-1) / s2                 # (P,N)
    if label_weights is None:
        log_label = torch.log(kernel_weights(y, Y, h).clamp_min(1e-300))
    else:
        log_label = torch.log(label_weights.clamp_min(1e-300))
    w = torch.softmax(log_spatial + log_label[None, :].to(torch.float64), dim=1)
    per_atom = X[None, :, :] + c * r                           # (P,N,d)
    return (w[:, :, None] * per_atom).sum(dim=1)


def flow_atoms(X, Y, y, h, x0, *, rho=0.0, sigma=0.0, guidance=0.0,
               n_steps=N_STEPS, t_end=T_END) -> np.ndarray:
    """Integrate ``atom_field`` (optionally guided) and keep the whole path."""
    ts = graded_times(n_steps, t_end)
    x = torch.as_tensor(np.asarray(x0), dtype=torch.float64)
    uniform = torch.full((X.shape[0],), 1.0 / X.shape[0], dtype=torch.float64)

    def f(t, xx):
        v = atom_field(xx, float(t), X, Y, y, h, rho=rho, sigma=sigma)
        if guidance > 0.0:
            v_unc = atom_field(xx, float(t), X, Y, y, h, rho=rho, sigma=sigma,
                               label_weights=uniform)
            v = (1.0 + guidance) * v - guidance * v_unc
        return v

    traj = [x.clone()]
    for a, b in zip(ts[:-1], ts[1:]):
        dt = b - a
        k1 = f(a, x)
        k2 = f(a + dt / 2, x + dt / 2 * k1)
        k3 = f(a + dt / 2, x + dt / 2 * k2)
        k4 = f(b, x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        traj.append(x.clone())
    return np.stack([p.numpy() for p in traj])


def bandwidth_matching_posterior(X, Y, y, target, lo=1e-3, hi=5.0) -> float:
    """Bisect for the h with tr Cov_h(y) = tr Sigma_post."""
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        _, cov, _ = kernel_moments(y, X, Y, mid)
        if float(torch.trace(cov)) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# --------------------------------------------------------------------------- #
# the instance every panel is computed on
# --------------------------------------------------------------------------- #
class Instance:
    def __init__(self) -> None:
        self.problem = LinearGaussianProblem.create(d=2, k=1, sigma_obs=0.1, seed=0)
        Xt, Yt = self.problem.sample_dataset(200, seed=1)
        self.X, self.Y = Xt.to(torch.float64), Yt.to(torch.float64)
        self.Xn = self.X.numpy()
        med = np.median(self.Y[:, 0].numpy())
        self.i = int(np.argmin(np.abs(self.Y[:, 0].numpy() - med)))
        self.y = self.Y[self.i]
        self.xi = self.Xn[self.i]
        self.Sigma = self.problem.Sigma_post.numpy().astype(float)
        self.mu = self.problem.posterior_mean(
            self.Y[self.i:self.i + 1].to(torch.float32)).numpy()[0].astype(float)
        self.tr_post = float(np.trace(self.Sigma))
        self.h_star = bandwidth_matching_posterior(self.X, self.Y, self.y, self.tr_post)
        rng = np.random.default_rng(0)
        self.x0 = rng.normal(size=(N_PATHS, 2))
        self.rng = rng

    def weights(self, h: float) -> np.ndarray:
        return kernel_weights(self.y, self.Y, h).numpy()


def self_checks(inst: Instance) -> None:
    """The figures may not say anything the closed forms do not."""
    print("self-checks")
    # 1. the generic field is the paper's kernel field when rho = sigma = 0.
    xs = torch.tensor(inst.rng.normal(size=(64, 2)), dtype=torch.float64)
    worst = 0.0
    for t in (0.05, 0.3, 0.7, 0.95, 0.999):
        a = atom_field(xs, t, inst.X, inst.Y, inst.y, inst.h_star)
        b = kernel_field(xs, torch.full((64,), t, dtype=torch.float64), inst.y,
                         inst.X, inst.Y, inst.h_star)
        worst = max(worst, float((a - b).abs().max()))
    print(f"  generic field vs kernel_field, max |diff| over t: {worst:.3e}")
    assert worst < 1e-8, "the generic field does not reduce to the paper's field"

    # 2. the bisected bandwidth solves tr Cov_h = tr Sigma_post.
    _, cov, _ = kernel_moments(inst.y, inst.X, inst.Y, inst.h_star)
    tr_h = float(torch.trace(cov))
    print(f"  h* = {inst.h_star:.4f}: tr Cov_h = {tr_h:.6f} vs "
          f"tr Sigma_post = {inst.tr_post:.6f}  (n_eff = "
          f"{n_eff(kernel_weights(inst.y, inst.Y, inst.h_star)):.1f} of {len(inst.Xn)})")
    assert abs(tr_h - inst.tr_post) < 1e-6 * max(1.0, inst.tr_post)

    # 3. endpoint smoothing: the flow's own endpoints carry Cov_h + rho^2 I.
    rho = 0.30
    rng = np.random.default_rng(1)
    x0 = rng.normal(size=(1200, 2))
    ends = flow_atoms(inst.X, inst.Y, inst.y, inst.h_star, x0, rho=rho,
                      n_steps=200)[-1]
    tr_meas = float(np.trace(np.cov(ends.T)))
    tr_pred = tr_h + 2 * rho ** 2
    print(f"  endpoint smoothing rho={rho}: tr Cov measured {tr_meas:.4f} vs "
          f"predicted tr Cov_h + rho^2 d = {tr_pred:.4f}")
    assert abs(tr_meas - tr_pred) < 0.12 * tr_pred, "endpoint law is not Cov_h + rho^2 I"
    # 4. the weights drawn as marker area, n_eff and tr Cov_h agree with a plain-numpy
    #    re-derivation from Theorem 1's definition p_i = K_h(y-y^i) / sum_j K_h(y-y^j),
    #    which shares no code with src/metrics/kernel_theory.py.
    Yn, Xn, yn = inst.Y.numpy(), inst.Xn, inst.y.numpy()
    for h in (0.05, 0.1, inst.h_star, 0.5, 2.0):
        z = -np.sum((Yn - yn) ** 2, axis=1) / (2.0 * h * h)
        p = np.exp(z - z.max())
        p /= p.sum()
        mean = p @ Xn
        tr_ref = float(np.sum(p * np.sum((Xn - mean) ** 2, axis=1)))
        neff_ref = 1.0 / float(np.sum(p ** 2))
        w = inst.weights(h)
        _, cov_h, _ = kernel_moments(inst.y, inst.X, inst.Y, h)
        assert np.abs(w - p).max() < 1e-10, f"p_i^(h) differs at h={h}"
        assert abs(float(torch.trace(cov_h)) - tr_ref) < 1e-9 * max(1.0, tr_ref), \
            f"tr Cov_h differs at h={h}"
        assert abs(n_eff(torch.as_tensor(w)) - neff_ref) < 1e-8 * neff_ref, \
            f"n_eff differs at h={h}"
    print("  weights, n_eff and tr Cov_h match the numpy re-derivation at 5 bandwidths")
    print("  ok\n")


# --------------------------------------------------------------------------- #
# figures
# --------------------------------------------------------------------------- #
def endpoint_stats(inst: Instance, ends: np.ndarray) -> dict:
    """What a bundle's endpoints actually did, so a caption can quote it."""
    d = np.linalg.norm(ends[:, None, :] - inst.Xn[None, :, :], axis=-1)
    nn = d.argmin(1)
    uniq, cnt = np.unique(nn, return_counts=True)
    return {"tr": float(np.trace(np.cov(ends.T))),
            "n_atoms": int(len(uniq)),
            "top_share": float(cnt.max() / len(nn)),
            "top_is_target": int(uniq[cnt.argmax()]) == inst.i,
            "mean_dist": float(d.min(1).mean())}


def _frame(ax, inst: Instance, *, atoms: bool = True) -> None:
    posterior_ellipse(ax, inst.mu, inst.Sigma)
    if atoms:
        ax.scatter(inst.Xn[:, 0], inst.Xn[:, 1], s=9, color=COLORS["atom"],
                   alpha=0.40, zorder=2, linewidths=0)
    portrait_axis(ax)


def _lock_limits(axes, pad: float = 0.04) -> None:
    xs = [ax.get_xlim() for ax in axes]
    ys = [ax.get_ylim() for ax in axes]
    xlo, xhi = min(a for a, _ in xs), max(b for _, b in xs)
    ylo, yhi = min(a for a, _ in ys), max(b for _, b in ys)
    dx, dy = pad * (xhi - xlo), pad * (yhi - ylo)
    for ax in axes:
        ax.set_xlim(xlo - dx, xhi + dx)
        ax.set_ylim(ylo - dy, yhi + dy)


LEGEND = [("source $x_0\\sim\\pi_0$", "marker", COLORS["source"]),
          ("training atoms $x^i$", "marker", COLORS["atom"]),
          ("generated endpoints", "marker", COLORS["generated"]),
          ("true posterior $p(\\cdot\\mid y)$", "patch", COLORS["source"])]


def fig_body(inst: Instance) -> None:
    """Body Figure 1: what the trained model does, and what the theory says."""
    ck = RUN_H0 / "checkpoints"
    early, late = 1000, 200000
    m_early = load_exp1_model(ck / f"ckpt_{early}.pt")
    m_late = load_exp1_model(ck / f"ckpt_{late}.pt")

    p_early = flow_model(m_early, inst.x0, inst.y.to(torch.float32))
    p_late = flow_model(m_late, inst.x0, inst.y.to(torch.float32))
    p_star = flow_exact(inst.X, inst.Y, inst.y, inst.h_star, inst.x0)
    p_rho = flow_atoms(inst.X, inst.Y, inst.y, inst.h_star, inst.x0, rho=0.30)

    w = inst.weights(inst.h_star)
    st_early = endpoint_stats(inst, p_early[-1])
    st_late = endpoint_stats(inst, p_late[-1])
    print(f"  trained {early} it.: tr Cov = {st_early['tr']:.3f} against the "
          f"posterior's {inst.tr_post:.3f}, over {st_early['n_atoms']} atoms")
    print(f"  trained {late} it.: tr Cov = {st_late['tr']:.3f}, "
          f"{st_late['top_share'] * 100:.1f}% of paths on the labelled atom "
          f"(is it x^i: {st_late['top_is_target']})")
    assert abs(st_early["tr"] - inst.tr_post) < 0.3 * inst.tr_post, \
        "the early checkpoint is not the calibrated one this panel claims it is"
    assert st_late["top_share"] > 0.9 and st_late["top_is_target"], \
        "the late checkpoint does not concentrate on the labelled atom"

    fig, axes = plt.subplots(1, 4, figsize=(13.2, 3.5))
    for ax in axes:
        _frame(ax, inst)

    trajectory_bundle(axes[0], p_early)
    axes[0].set_title(f"trained model, {early:,} it.", pad=7)

    trajectory_bundle(axes[1], p_late, end_size=150, end_alpha=1.0)
    axes[1].set_title(f"same model, {late:,} it.", pad=7)

    trajectory_bundle(axes[2], p_star, show_ends=False)
    weight_scatter(axes[2], inst.Xn, w)
    axes[2].set_title(f"population optimum, $h^\\star={inst.h_star:.2f}$", pad=7)

    trajectory_bundle(axes[3], p_rho)
    axes[3].set_title("endpoint smoothing, $\\rho=0.30$", pad=7)

    tr_star = float(torch.trace(kernel_moments(inst.y, inst.X, inst.Y, inst.h_star)[1]))
    neff = n_eff(kernel_weights(inst.y, inst.Y, inst.h_star))
    notes = [
        f"still calibrated: $\\mathrm{{tr}}\\,\\mathrm{{Cov}}={st_early['tr']:.2f}$"
        f" against the\nposterior's ${inst.tr_post:.2f}$, over "
        f"{st_early['n_atoms']} atoms",
        f"collapsing: {st_late['top_share'] * 100:.0f}% of paths land on $x^i$,\n"
        f"$\\mathrm{{tr}}\\,\\mathrm{{Cov}}={st_late['tr']:.2f}$; the limit is "
        "$p_1=\\delta_{x^i}$",
        f"area $\\propto p^{{(h)}}_i$; $\\mathrm{{tr}}\\,\\mathrm{{Cov}}_h"
        f"={tr_star:.2f}$ matches the\nposterior exactly, on "
        f"$n_{{\\mathrm{{eff}}}}={neff:.0f}$ of {len(inst.Xn)} atoms",
        "support leaves the atoms:\nabsolutely continuous",
    ]
    # The panel notes are what the caption says, so the body figure keeps only the
    # titles (as the reference papers do) and spends its height on the panels.
    for j, note in enumerate(notes):
        print(f"  panel ({'abcd'[j]}): {note.replace(chr(10), ' ')}")
    for j, ax in enumerate(axes):
        panel_tag(ax, "abcd"[j])
    _lock_limits(list(axes))
    shared_legend(fig, LEGEND, loc="lower center", y=-0.06)
    fig.tight_layout()
    save(fig, "fig_flow_portrait.png")


def fig_training(inst: Instance) -> None:
    """Appendix: the same condition, as training proceeds, against the limit."""
    iters = [100, 1000, 10000, 30000, 200000]
    ck = RUN_H0 / "checkpoints"
    fig, axes = plt.subplots(1, len(iters) + 1, figsize=(3.0 * (len(iters) + 1), 3.6))
    for j, it in enumerate(iters):
        model = load_exp1_model(ck / f"ckpt_{it}.pt")
        paths = flow_model(model, inst.x0, inst.y.to(torch.float32))
        _frame(axes[j], inst)
        trajectory_bundle(axes[j], paths,
                          end_size=110 if it >= 100000 else 26,
                          end_alpha=1.0 if it >= 100000 else 0.75)
        st = endpoint_stats(inst, paths[-1])
        axes[j].set_title(f"{it:,} iterations", pad=7)
        axes[j].text(0.5, -0.03,
                     f"$\\mathrm{{tr}}\\,\\mathrm{{Cov}}={st['tr']:.2f}$, "
                     f"{st['n_atoms']} atoms reached",
                     transform=axes[j].transAxes, ha="center", va="top",
                     fontsize=8.6)
        panel_tag(axes[j], "abcdef"[j])
        print(f"  {it:>7} it.: tr Cov = {st['tr']:.3f}, atoms = {st['n_atoms']}, "
              f"top share = {st['top_share']:.3f}")
    ax = axes[-1]
    _frame(ax, inst)
    exact = flow_exact(inst.X, inst.Y, inst.y, 0.0, inst.x0)
    trajectory_bundle(ax, exact, end_size=150, end_alpha=1.0)
    st = endpoint_stats(inst, exact[-1])
    ax.set_title("population optimum ($h=0$)", pad=7)
    ax.text(0.5, -0.03,
            f"$\\mathrm{{tr}}\\,\\mathrm{{Cov}}={st['tr']:.0e}$, one atom",
            transform=ax.transAxes, ha="center", va="top", fontsize=8.6)
    panel_tag(ax, "f")
    assert st["n_atoms"] == 1 and st["top_is_target"], \
        "the exact h=0 flow must land every path on the labelled atom"
    _lock_limits(list(axes))
    shared_legend(fig, LEGEND, loc="lower center", y=-0.10)
    fig.tight_layout()
    save(fig, "fig_collapse_training.png")


def fig_interventions(inst: Instance) -> None:
    """Appendix: the four interventions, all as exact population flows."""
    sigma, rho, w_cfg = 0.5, 0.30, 3.0
    runs = [
        ("hard conditioning\n$h=0$", flow_atoms(inst.X, inst.Y, inst.y, 0.0, inst.x0),
         "one atom", None),
        (f"label smoothing\n$h={inst.h_star:.2f}$",
         flow_atoms(inst.X, inst.Y, inst.y, inst.h_star, inst.x0),
         "reweighting: the same atoms", inst.h_star),
        (f"interpolant noise\n$\\sigma={sigma}$",
         flow_atoms(inst.X, inst.Y, inst.y, 0.0, inst.x0, sigma=sigma),
         "inert: still one atom", None),
        (f"guidance\n$w={w_cfg:.0f}$",
         flow_atoms(inst.X, inst.Y, inst.y, 0.0, inst.x0, guidance=w_cfg),
         "atom-preserving", None),
        (f"endpoint smoothing\n$\\rho={rho}$",
         flow_atoms(inst.X, inst.Y, inst.y, inst.h_star, inst.x0, rho=rho),
         "support-moving", None),
    ]
    fig, axes = plt.subplots(1, len(runs), figsize=(3.0 * len(runs), 3.8))
    for j, (title, paths, note, h_w) in enumerate(runs):
        ax = axes[j]
        _frame(ax, inst)
        if h_w is not None and j == 1:
            trajectory_bundle(ax, paths, show_ends=False)
            weight_scatter(ax, inst.Xn, inst.weights(h_w))
        else:
            trajectory_bundle(ax, paths, end_size=110 if j in (0, 2, 3) else 26,
                              end_alpha=1.0 if j in (0, 2, 3) else 0.75)
        ax.set_title(title, pad=7, fontsize=10.5)
        ax.text(0.5, -0.03, note, transform=ax.transAxes, ha="center", va="top",
                fontsize=8.6)
        panel_tag(ax, "abcde"[j])
    _lock_limits(list(axes))
    shared_legend(fig, LEGEND, loc="lower center", y=-0.12)
    fig.tight_layout()
    save(fig, "fig_interventions.png")


TRAINED_H = {0.0: RUN_H0,
             0.05: Path("results/exp1/p7yck_h0.05_seed0"),
             0.1: Path("results/exp1/p7yck_h0.1_seed0"),
             0.5: Path("results/exp1/p7yck_h0.5_seed0")}


def fig_bandwidths(inst: Instance) -> None:
    """Appendix: the reference law and the model trained at the same bandwidth.

    Top row is Theorem 1 -- the exact population endpoint law at each h, with the
    Nadaraya-Watson weights as marker area. Bottom row is what an MLP trained at
    that same h actually does after 200000 iterations. The pair is the paper's
    P7 claim in one picture: the reference is what the model is converging to,
    and the gap is optimisation, not a different law.
    """
    hs = [0.0, 0.05, 0.1, 0.5]
    fig, axes = plt.subplots(2, len(hs), figsize=(3.05 * len(hs), 6.6))
    for j, h in enumerate(hs):
        tr_ref = float(torch.trace(kernel_moments(inst.y, inst.X, inst.Y, h)[1]))
        ne = n_eff(kernel_weights(inst.y, inst.Y, h))

        ax = axes[0, j]
        _frame(ax, inst)
        paths = flow_exact(inst.X, inst.Y, inst.y, h, inst.x0)
        if h > 0:
            trajectory_bundle(ax, paths, show_ends=False)
            weight_scatter(ax, inst.Xn, inst.weights(h))
        else:
            trajectory_bundle(ax, paths, end_size=150, end_alpha=1.0)
        ax.set_title(f"$h={h:g}$", pad=7)
        ax.text(0.5, -0.03,
                f"reference: $\\mathrm{{tr}}\\,\\mathrm{{Cov}}_h={tr_ref:.2f}$,\n"
                f"$n_{{\\mathrm{{eff}}}}={ne:.0f}$",
                transform=ax.transAxes, ha="center", va="top", fontsize=8.6)
        panel_tag(ax, "abcd"[j])

        ax = axes[1, j]
        _frame(ax, inst)
        ck = TRAINED_H[h] / "checkpoints" / "ckpt_200000.pt"
        model = load_exp1_model(ck)
        tpaths = flow_model(model, inst.x0, inst.y.to(torch.float32))
        st = endpoint_stats(inst, tpaths[-1])
        trajectory_bundle(ax, tpaths, end_size=110 if h == 0 else 26,
                          end_alpha=1.0 if h == 0 else 0.75)
        # At h = 0 the reference is a point mass, so the ratio to it is not a
        # number; the panel reports how concentrated the model is instead.
        second = (f"ratio to reference ${st['tr'] / tr_ref:.2f}$" if tr_ref > 0
                  else f"{st['top_share'] * 100:.0f}% of paths on one atom")
        ax.text(0.5, -0.03,
                f"trained: $\\mathrm{{tr}}\\,\\mathrm{{Cov}}={st['tr']:.2f}$,\n"
                + second,
                transform=ax.transAxes, ha="center", va="top", fontsize=8.6)
        panel_tag(ax, "efgh"[j])
        ratio = f"{st['tr'] / tr_ref:.3f}" if tr_ref > 0 else "n/a"
        print(f"  h={h:<5} reference {tr_ref:.3f} (n_eff {ne:5.1f})  "
              f"trained {st['tr']:.3f}  ratio {ratio:>5}  atoms {st['n_atoms']}")
        if h == 0:
            assert st["top_share"] > 0.9, "the h=0 model should sit on one atom"

    _lock_limits(list(axes.ravel()))
    axes[0, 0].set_ylabel("population optimum", fontsize=10)
    axes[1, 0].set_ylabel("trained, $200000$ it.", fontsize=10)
    shared_legend(fig, LEGEND, loc="lower center", y=-0.03)
    fig.tight_layout(h_pad=3.0)
    save(fig, "fig_bandwidth_portrait.png")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["body", "training", "interventions",
                                       "bandwidths", "all"],
                    default="all")
    args = ap.parse_args()

    use_paper_style()
    inst = Instance()
    self_checks(inst)
    if args.only in ("body", "all"):
        fig_body(inst)
    if args.only in ("training", "all"):
        fig_training(inst)
    if args.only in ("interventions", "all"):
        fig_interventions(inst)
    if args.only in ("bandwidths", "all"):
        fig_bandwidths(inst)


if __name__ == "__main__":
    main()
