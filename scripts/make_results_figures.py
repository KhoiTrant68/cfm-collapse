"""Result figures for Section 6, drawn from the saved experiment outputs.

    uv run python -m scripts.make_results_figures      (from the repo root)

Writes into paper/figures:
    fig_exp1_collapse.pdf    EXP-1 at h=0, five seeds (Table tab:exp1): (a) generated trace
                             against iteration, constant and cosine schedules, with the
                             unconditional baseline; (b) distance of the generated mean to
                             the training atom and to the posterior mean; (c) relative
                             velocity error against the collapsed field (*).
    fig_cifar_collapse.pdf   CIFAR-10 U-Net at h=0: (a) generated trace against iteration for
                             the three instances; (b) completions of one condition at three
                             checkpoints, cut from the grids the run saved.
    fig_kernel_tracking.pdf  Label smoothing: (a) EXP-1 generated trace against the kernel
                             reference tr Cov_h and tr Sigma_post (Table tab:p7kernel);
                             (b) the ratio to the reference with n_eff; (c) CIFAR-10
                             per-condition measured against reference variance at h=4 and 6.

Every plotted value is read from results/; nothing is typed in.
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scripts.figstyle import COLORS, FIGDIR, H_COLORS, OI, panel_tag, style, use_paper_style
from scripts.make_image_bandwidth_figure import cells

EXP1 = Path("results/exp1")
EXP3 = Path("results/exp3")


def seed_mean(pattern: str, group: str, col: str) -> pd.DataFrame:
    frames = [pd.read_csv(f) for f in sorted(glob.glob(pattern))]
    assert len(frames) == 5, pattern
    d = pd.concat(frames)
    d = d[d["group"] == group]
    g = d.groupby("iter")[col]
    return pd.DataFrame({"m": g.mean(), "sd": g.std(ddof=0)})


def band(ax, df, color, label, ls="-", marker="o"):
    x = df.index.to_numpy(float)
    ax.plot(x, df["m"], color=color, ls=ls, marker=marker, ms=4, lw=1.8, label=label)
    ax.fill_between(x, df["m"] - df["sd"], df["m"] + df["sd"], color=color, alpha=0.15,
                    lw=0)


# --------------------------------------------------------------------------- #
def fig_exp1() -> None:
    const = f"{EXP1}/exp1_cond_seed[0-4]/raw/metrics.csv"
    cosine = f"{EXP1}/exp1_ext_sched_seed[0-4]/raw/metrics.csv"
    uncond = f"{EXP1}/exp1_uncond_seed[0-4]/raw/metrics.csv"

    tr_c = seed_mean(const, "train", "trace_cov_mean")
    tr_s = seed_mean(cosine, "train", "trace_cov_mean")
    tr_u = seed_mean(uncond, "uncond", "trace_cov_mean")
    post = seed_mean(const, "train", "trace_post")["m"].mean()
    data = seed_mean(uncond, "uncond", "trace_data")["m"].mean()
    # the numbers the paper quotes
    assert abs(tr_c.loc[200000, "m"] - 0.396) < 5e-4, tr_c.loc[200000, "m"]
    assert abs(tr_s.loc[1000000, "m"] - 0.120) < 5e-4, tr_s.loc[1000000, "m"]

    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.55))
    ax = axes[0]
    band(ax, tr_u, COLORS["accent"], "unconditional")
    band(ax, tr_c, COLORS["generated"], r"conditional, $h=0$")
    band(ax, tr_s, COLORS["generated"], "conditional, cosine schedule", ls="--",
         marker="s")
    ax.axhline(data, color=COLORS["accent"], ls=":", lw=1.3)
    ax.text(0.98, data * 1.08, r"$\mathrm{tr}\,\widehat\Sigma_X$", fontsize=9,
            color=COLORS["accent"], ha="right", transform=ax.get_yaxis_transform())
    ax.axhline(post, color=COLORS["reference"], ls=":", lw=1.3)
    ax.text(0.98, post * 1.08, r"$\mathrm{tr}\,\Sigma_{\mathrm{post}}$", fontsize=9,
            color=COLORS["reference"], ha="right", transform=ax.get_yaxis_transform())
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("training iteration")
    ax.set_ylabel(r"generated $\mathrm{tr}\,\mathrm{Cov}$")
    ax.legend(loc="lower left", fontsize=7)

    ax = axes[1]
    band(ax, seed_mean(const, "train", "mean_err_train_point_mean"), COLORS["atom"],
         r"to the atom $x^i$")
    band(ax, seed_mean(const, "train", "mean_err_post_mean"), COLORS["reference"],
         r"to the posterior mean")
    band(ax, seed_mean(cosine, "train", "mean_err_train_point_mean"), COLORS["atom"],
         None, ls="--", marker="s")
    band(ax, seed_mean(cosine, "train", "mean_err_post_mean"), COLORS["reference"],
         None, ls="--", marker="s")
    ax.set_xscale("log")
    ax.set_xlabel("training iteration")
    ax.set_ylabel("distance of the generated mean")
    ax.legend(loc="center left", bbox_to_anchor=(0.0, 0.42), fontsize=7)

    ax = axes[2]
    band(ax, seed_mean(const, "train", "vel_rel_err_mean_mean"), COLORS["generated"],
         "constant learning rate")
    band(ax, seed_mean(cosine, "train", "vel_rel_err_mean_mean"), COLORS["generated"],
         "cosine schedule", ls="--", marker="s")
    ax.set_xscale("log")
    ax.set_ylim(bottom=0)
    ax.set_xlabel("training iteration")
    ax.set_ylabel(r"relative velocity error to $(\star)$")
    ax.legend(loc="lower left", fontsize=7)

    for j, ax in enumerate(axes):
        style(ax)
        panel_tag(ax, "abc"[j], dx=-0.16)
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_exp1_collapse.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote fig_exp1_collapse.pdf")


# --------------------------------------------------------------------------- #
def fig_cifar() -> None:
    runs = {"instance 1": "exp3_cifar_ddpm_h0", "instance 2": "exp3_cifar_ddpm_h0_seed1",
            "instance 3": "exp3_cifar_ddpm_h0_seed2"}
    colors = [COLORS["generated"], OI["orange"], OI["purple"]]
    first = pd.read_csv(EXP3 / runs["instance 1"] / "raw" / "metrics.csv")
    assert abs(first.set_index("iter").loc[500, "trace_cov_mean"] - 179.1) < 0.05
    assert abs(first.set_index("iter").loc[60000, "trace_cov_mean"] - 0.431) < 5e-4

    iters = (500, 8000, 60000)
    cond, cols = 0, (0, 1, 2, 3, 7, 8)   # observed, three completions, true, nearest
    heads = ["observed", "completions", "", "", "true", "nearest\ntraining image"]

    fig = plt.figure(figsize=(7.6, 2.55))
    gs = fig.add_gridspec(len(iters), 1 + len(cols), width_ratios=[5.0] + [1] * len(cols),
                          left=0.06, right=0.995, top=0.88, bottom=0.15,
                          wspace=0.05, hspace=0.06)
    ax = fig.add_subplot(gs[:, 0])
    for (name, run), c in zip(runs.items(), colors):
        m = pd.read_csv(EXP3 / run / "raw" / "metrics.csv")
        ax.plot(m["iter"], m["trace_cov_mean"], marker="o", ms=4, color=c, lw=1.8,
                label=name)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("training iteration")
    ax.set_ylabel(r"generated $\mathrm{tr}\,\mathrm{Cov}$")
    ax.legend(loc="lower left", fontsize=7)
    style(ax)
    panel_tag(ax, "a", dx=-0.2, dy=1.03)

    for r, it in enumerate(iters):
        sheet = cells(EXP3 / runs["instance 1"] / "figures" / f"grid_it{it}.png")
        for k, c in enumerate(cols):
            a = fig.add_subplot(gs[r, 1 + k])
            a.imshow(sheet[cond][c], interpolation="nearest")
            a.set_xticks([])
            a.set_yticks([])
            a.grid(False)
            for s in a.spines.values():
                s.set_visible(False)
            if r == 0 and heads[k]:
                a.set_title(heads[k], fontsize=7.5, pad=3, loc="left" if k == 1 else "center")
            if k == 0:
                a.text(-0.12, 0.5, f"{it:,}", transform=a.transAxes, rotation=90,
                       ha="right", va="center", fontsize=9)
                if r == 0:
                    panel_tag(a, "b", dx=-0.45, dy=1.12)
    fig.savefig(FIGDIR / "fig_cifar_collapse.pdf", bbox_inches="tight", dpi=200)
    plt.close(fig)
    print("wrote fig_cifar_collapse.pdf")


# --------------------------------------------------------------------------- #
def ols(x, y):
    xc, yc = x - x.mean(), y - y.mean()
    slope = float((xc * yc).sum() / (xc * xc).sum())
    resid = yc - slope * xc
    se = float(np.sqrt((resid ** 2).sum() / (len(x) - 2) / (xc * xc).sum()))
    return slope, float(y.mean() - slope * x.mean()), se


def fig_kernel() -> None:
    df = pd.read_csv(EXP1 / "_theory" / "raw" / "p7_kernel.csv")
    g = df.groupby("h")
    hs = sorted(df["h"].unique())
    x = np.arange(len(hs))
    meas, meas_sd = g["trace_meas"].mean()[hs], g["trace_meas"].std(ddof=0)[hs]
    kern, post = g["trace_kernel"].mean()[hs], g["trace_post"].mean()[hs]
    ratio, ratio_sd = g["ratio_to_kernel"].mean()[hs], g["ratio_to_kernel"].std(ddof=0)[hs]
    neff = g["n_eff"].mean()[hs]
    assert np.allclose(ratio.to_numpy(), [1.308, 1.002, 0.994, 1.011], atol=5e-4), ratio

    rows = json.loads((EXP3 / "_cifar_ddpm" / "reeval.json").read_text(encoding="utf-8"))
    by_h = {float(r["h"]): r for r in rows}

    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.55),
                             gridspec_kw={"width_ratios": [1, 1, 1.05]})
    ax = axes[0]
    ax.errorbar(x, meas, yerr=meas_sd, marker="x", ms=8, mew=1.8, ls="none", capsize=3,
                color=COLORS["generated"], label=r"generated (5 seeds)", zorder=3)
    ax.plot(x, kern, ls="--", marker="s", ms=5, color=COLORS["theory"], lw=1.5,
            label=r"reference $\mathrm{tr}\,\mathrm{Cov}_h$")
    ax.plot(x, post, ls=":", color=COLORS["reference"], lw=1.5,
            label=r"$\mathrm{tr}\,\Sigma_{\mathrm{post}}$")
    ax.set_xticks(x, [f"{h:g}" for h in hs])
    ax.set_xlabel("label bandwidth $h$")
    ax.set_ylabel(r"$\mathrm{tr}\,\mathrm{Cov}$ (EXP-1)")
    ax.legend(loc="upper left", fontsize=7)

    ax = axes[1]
    ax.axhline(1.0, color=COLORS["theory"], ls="--", lw=1.3)
    ax.errorbar(x, ratio, yerr=ratio_sd, marker="x", ms=8, mew=1.8, ls="none", capsize=3,
                color=COLORS["generated"])
    ax.set_xticks(x, [f"{h:g}\n{v:.1f}" for h, v in zip(hs, neff)])
    ax.set_xlabel(r"$h$ (top) and $n_{\mathrm{eff}}$ (bottom)")
    ax.set_ylabel(r"ratio to $\mathrm{tr}\,\mathrm{Cov}_h$ (EXP-1)")

    ax = axes[2]
    lo, hi = np.inf, -np.inf
    for h in (4.0, 6.0):
        r = by_h[h]
        ref = np.asarray(r["trace_kernel_per_condition"], float)
        mv = np.asarray(r["ratio_per_condition"], float) * ref
        ok = (ref > 0) & (mv > 0)
        lx, ly = np.log10(ref[ok]), np.log10(mv[ok])
        slope, icpt, se = ols(lx, ly)
        c = H_COLORS[h]
        ax.plot(lx, ly, ls="none", marker="x", ms=6, mew=1.3, color=c,
                label=rf"$h={h:g}$: slope ${slope:.2f}\pm{se:.2f}$")
        xs = np.linspace(lx.min(), lx.max(), 2)
        ax.plot(xs, icpt + slope * xs, color=c, lw=1.6)
        lo, hi = min(lo, lx.min(), ly.min()), max(hi, lx.max(), ly.max())
    lo, hi = lo - 0.3, hi + 0.3
    ax.plot([lo, hi], [lo, hi], color=COLORS["theory"], ls="--", lw=1.3)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_xlabel(r"$\log_{10}$ reference $\mathrm{tr}\,\mathrm{Cov}_h$ (CIFAR-10)")
    ax.set_ylabel(r"$\log_{10}$ generated $\mathrm{tr}\,\mathrm{Cov}$")
    ax.legend(loc="lower right", fontsize=7)

    for j, ax in enumerate(axes):
        style(ax)
        panel_tag(ax, "abc"[j], dx=-0.16)
    fig.tight_layout()
    fig.savefig(FIGDIR / "fig_kernel_tracking.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote fig_kernel_tracking.pdf")


if __name__ == "__main__":
    use_paper_style()
    fig_exp1()
    fig_cifar()
    fig_kernel()
