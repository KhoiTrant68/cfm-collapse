"""One visual language for every figure in the paper.

The figures used to be written one script at a time, each with its own colours,
fonts and legend placement. This module holds the choices that must be the same
everywhere, and the three drawing idioms the paper borrows from the flow-matching
and model-collapse literature:

  * ``trajectory_bundle`` -- source samples, the paths they follow, and where they
    land, drawn together (Delay FM, ICLR 2026, Fig. 2). Collapse is a statement
    about where trajectories *go*, so it should be visible in trajectory space and
    not only in a scalar curve.
  * ``weight_scatter`` -- marker area proportional to a mixture weight (Source-
    Guided FM, arXiv:2508.14807, Fig. 3). Theorem 1's endpoint law is exactly a
    weighted sum of point masses, so its weights are drawn on the atoms.
  * ``theory_vs_measured`` -- theory as a line, measurements as crosses on top,
    the predicted value as a labelled dashed rule (Preventing Model Collapse,
    ICLR 2026, Figs. 1-2). Every figure that compares a prediction with a
    measurement uses this and nothing else.

Colours are Okabe-Ito, which stays legible in greyscale and for colour-blind
readers, and every role below keeps its colour across all figures: a reader who
learns "vermillion is what the model generated" in Figure 1 keeps that in the
appendix.

    from scripts.figstyle import use_paper_style, COLORS, trajectory_bundle
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse

FIGDIR = Path("paper/figures")

# Okabe-Ito, fixed order.
OI = {
    "black": "#000000", "orange": "#E69F00", "sky": "#56B4E9",
    "green": "#009E73", "yellow": "#F0E442", "blue": "#0072B2",
    "vermillion": "#D55E00", "purple": "#CC79A7",
}

# What each colour *means*. Fixed for the whole paper.
COLORS = {
    "source": OI["sky"],          # x_0 ~ pi_0, where trajectories start
    "atom": OI["black"],          # training examples x^i
    "generated": OI["vermillion"],  # what the flow actually produces
    "reference": OI["blue"],      # the kernel reference law / true posterior
    "theory": OI["black"],        # a predicted value (drawn dashed)
    "path": "#6E6E6E",            # integrated trajectories
    "accent": OI["green"],        # a second measured series when one is not enough
}

# One colour per bandwidth, wherever several h are shown together.
H_COLORS = {0.0: OI["black"], 0.01: OI["orange"], 0.05: OI["sky"],
            0.1: OI["green"], 0.5: OI["blue"], 4.0: OI["orange"],
            5.0: OI["green"], 6.0: OI["blue"]}


def use_paper_style() -> None:
    """Apply the shared rcParams. Call once at the top of every figure script."""
    plt.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": 200, "font.size": 11,
        "axes.titlesize": 11.5, "axes.labelsize": 10.5,
        "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "legend.fontsize": 9,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": "#cccccc", "grid.alpha": 0.4,
        "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False,
        "lines.linewidth": 2.0, "lines.markersize": 7,
        "figure.constrained_layout.use": False,
    })


def style(ax) -> None:
    """Thin the spines and ticks of one axis."""
    ax.tick_params(length=3, width=0.8)
    for s in ("left", "bottom"):
        ax.spines[s].set_linewidth(0.8)


def portrait_axis(ax) -> None:
    """A 2-D state-space panel: no ticks, equal aspect, faint frame."""
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect("equal")
    ax.grid(False)
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_alpha(0.35)
        s.set_linewidth(0.8)


def panel_tag(ax, letter: str, dx: float = -0.04, dy: float = 1.06) -> None:
    """(a), (b), ... above the top-left corner of a panel."""
    ax.text(dx, dy, f"({letter})", transform=ax.transAxes, ha="left", va="bottom",
            fontsize=10.5, fontweight="bold")


def shared_legend(fig, entries, *, loc: str = "upper center", ncol: int | None = None,
                  y: float | None = None):
    """One legend for a whole row of panels, as the reference papers do.

    ``entries`` is a list of ``(label, kind, colour)`` with kind in
    {"marker", "line", "dashed", "cross", "patch"}.
    """
    handles = []
    labels = []
    for label, kind, colour in entries:
        if kind == "marker":
            h = Line2D([], [], marker="o", linestyle="none", color=colour,
                       markersize=7, markeredgecolor="white", markeredgewidth=0.7)
        elif kind == "cross":
            h = Line2D([], [], marker="x", linestyle="none", color=colour,
                       markersize=7, markeredgewidth=1.6)
        elif kind == "dashed":
            h = Line2D([], [], linestyle="--", color=colour, linewidth=1.8)
        elif kind == "patch":
            h = Line2D([], [], marker="s", linestyle="none", color=colour,
                       markersize=8, alpha=0.45)
        else:
            h = Line2D([], [], linestyle="-", color=colour, linewidth=2.0)
        handles.append(h)
        labels.append(label)
    kw = {"loc": loc, "ncol": ncol or len(entries), "frameon": False,
          "handletextpad": 0.5, "columnspacing": 1.6}
    if y is not None:
        kw["bbox_to_anchor"] = (0.5, y)
    return fig.legend(handles, labels, **kw)


# --------------------------------------------------------------------------- #
# drawing idioms
# --------------------------------------------------------------------------- #
def posterior_ellipse(ax, mu, Sigma, *, label: str | None = None) -> None:
    """The true conditional law, at 1 and 2 standard deviations."""
    vals, vecs = np.linalg.eigh(np.asarray(Sigma, dtype=float))
    ang = np.degrees(np.arctan2(vecs[1, -1], vecs[0, -1]))
    for k in (2.0, 1.0):
        ax.add_patch(Ellipse(mu, 2 * k * np.sqrt(vals[-1]), 2 * k * np.sqrt(vals[0]),
                             angle=ang, fill=(k == 2.0), facecolor=COLORS["source"],
                             alpha=0.22 if k == 2.0 else 1.0,
                             edgecolor=COLORS["reference"], lw=1.6, zorder=0,
                             label=label if k == 2.0 else None))


def trajectory_bundle(ax, paths, *, show_source: bool = True,
                      show_ends: bool = True, path_alpha: float = 0.16,
                      end_size: float = 26.0, end_alpha: float = 0.75) -> None:
    """Draw integrated trajectories with their start and end points.

    ``paths`` has shape (n_times, n_paths, 2): the output of ``flow_exact`` or
    ``flow_model``.
    """
    ax.plot(paths[:, :, 0], paths[:, :, 1], color=COLORS["path"], alpha=path_alpha,
            lw=0.7, zorder=1)
    if show_source:
        ax.scatter(paths[0, :, 0], paths[0, :, 1], s=6, color=COLORS["source"],
                   alpha=0.55, zorder=2, linewidths=0)
    if show_ends:
        ax.scatter(paths[-1, :, 0], paths[-1, :, 1], s=end_size,
                   color=COLORS["generated"], alpha=end_alpha, zorder=4,
                   edgecolors="white", linewidths=0.5)


def weight_scatter(ax, X, w, *, floor: float = 1e-3, scale: float = 900.0,
                   color: str | None = None, label: str | None = None) -> None:
    """Atoms with marker area proportional to their mixture weight."""
    X = np.asarray(X, dtype=float)
    w = np.asarray(w, dtype=float)
    keep = w > floor
    ax.scatter(X[keep, 0], X[keep, 1], s=8 + scale * w[keep],
               color=color or COLORS["generated"], alpha=0.72, zorder=4,
               edgecolors="white", linewidths=0.8, label=label)


def theory_vs_measured(ax, x, theory, measured, *, theory_label: str = "theory",
                       measured_label: str = "measured", measured_err=None,
                       color: str | None = None) -> None:
    """A predicted curve as a line, the measurements as crosses on top of it."""
    c = color or COLORS["accent"]
    ax.plot(x, theory, color=COLORS["theory"], lw=1.8, zorder=2, label=theory_label)
    if measured_err is None:
        ax.plot(x, measured, linestyle="none", marker="x", markersize=8,
                markeredgewidth=1.8, color=c, zorder=3, label=measured_label)
    else:
        ax.errorbar(x, measured, yerr=measured_err, linestyle="none", marker="x",
                    markersize=8, markeredgewidth=1.8, color=c, capsize=3,
                    elinewidth=1.0, zorder=3, label=measured_label)


def predicted_rule(ax, value: float, text: str, *, axis: str = "y",
                   where: float = 0.02) -> None:
    """A dashed rule at a value the theory predicts, labelled in place."""
    if axis == "y":
        ax.axhline(value, linestyle="--", color=COLORS["theory"], lw=1.4, zorder=1)
        ax.text(where, value, text, transform=ax.get_yaxis_transform(),
                va="bottom", ha="left", fontsize=9, color=COLORS["theory"])
    else:
        ax.axvline(value, linestyle="--", color=COLORS["theory"], lw=1.4, zorder=1)
        ax.text(value, where, text, transform=ax.get_xaxis_transform(),
                va="bottom", ha="left", rotation=90, fontsize=9,
                color=COLORS["theory"])


# --------------------------------------------------------------------------- #
# flows: the exact population field, and a trained model
# --------------------------------------------------------------------------- #
def graded_times(n_steps: int = 400, t_end: float = 1.0 - 1e-3) -> np.ndarray:
    """Time grid graded towards t=1, where the collapsed field is singular."""
    return 1.0 - np.geomspace(1.0, 1.0 - t_end, n_steps + 1)


def _rk4(field, x0: torch.Tensor, ts: np.ndarray) -> np.ndarray:
    x = x0.clone()
    traj = [x.clone()]
    for a, b in zip(ts[:-1], ts[1:]):
        dt = b - a
        k1 = field(a, x)
        k2 = field(a + dt / 2, x + dt / 2 * k1)
        k3 = field(a + dt / 2, x + dt / 2 * k2)
        k4 = field(b, x + dt * k3)
        x = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        traj.append(x.clone())
    return np.stack([p.numpy() for p in traj])


def flow_exact(X, Y, y, h: float, x0, *, source_std: float = 1.0,
               n_steps: int = 400, t_end: float = 1.0 - 1e-3) -> np.ndarray:
    """Integrate the exact population field of the paper. Returns (T, n, d)."""
    from src.metrics.kernel_theory import kernel_field

    x = torch.as_tensor(np.asarray(x0), dtype=torch.float64)

    def field(t: float, xx: torch.Tensor) -> torch.Tensor:
        t_vec = torch.full((xx.shape[0],), float(t), dtype=torch.float64)
        return kernel_field(xx, t_vec, y, X, Y, h, source_std)

    return _rk4(field, x, graded_times(n_steps, t_end))


@torch.no_grad()
def flow_model(model, x0, y, *, n_steps: int = 400,
               t_end: float = 1.0 - 1e-3) -> np.ndarray:
    """Integrate a trained velocity model, keeping the whole path.

    ``src.flows.ode_solver.integrate`` returns only the endpoint; the figures need
    the trajectory, so the same RK4 is run here on the same graded grid used for
    the exact field, which keeps the two panels comparable.
    """
    x = torch.as_tensor(np.asarray(x0), dtype=torch.float32)
    yv = None if y is None else torch.as_tensor(np.asarray(y), dtype=torch.float32)
    if yv is not None and yv.dim() == 1:
        yv = yv[None, :].expand(x.shape[0], -1)

    def field(t: float, xx: torch.Tensor) -> torch.Tensor:
        t_vec = torch.full((xx.shape[0],), float(t), dtype=torch.float32)
        return model(xx, t_vec, yv)

    return _rk4(field, x, graded_times(n_steps, t_end))


def load_exp1_model(ckpt: str | Path, *, d: int = 2, k: int = 1,
                    cfg: dict | None = None):
    """Rebuild the EXP-1 MLP from a checkpoint written by ``src.train``."""
    import yaml

    from src.models.mlp_velocity import build_model

    ckpt = Path(ckpt)
    if cfg is None:
        cfg_path = ckpt.parent.parent / "config.yaml"
        with open(cfg_path, encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
    cond_dim = k if cfg["model"].get("conditional", True) else 0
    model = build_model(cfg, data_dim=d, cond_dim=cond_dim)
    state = torch.load(ckpt, map_location="cpu", weights_only=False)["model_state"]
    model.load_state_dict(state)
    model.eval()
    return model


def save(fig, name: str, *, pad: float = 0.02) -> Path:
    """Write a figure into paper/figures and report the path."""
    FIGDIR.mkdir(parents=True, exist_ok=True)
    out = FIGDIR / name
    fig.savefig(out, bbox_inches="tight", pad_inches=pad)
    plt.close(fig)
    print(f"  wrote {out}")
    return out
