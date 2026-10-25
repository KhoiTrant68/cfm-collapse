"""EXP-C: where do the off-atom CIFAR-10 samples come from? (Section sec:cifarddpm)

At h = 6 the paper reports 38% of finite-cutoff completions off the training atoms by the
nearest-neighbour criterion d1/d2 < 1/3, measured on saved sample grids of runs whose weights
were not kept. This script uses the checkpointed reruns of the same configuration
(results/exp3/exp3_cifar_heff_h{0,4,5,6}_s{0,1,2}; configs/exp3_cifar_ddpm_heff.yaml is
exp3_cifar_ddpm.yaml unchanged) and, from the same Gaussian sources (N_COND training conditions
x M sources), integrates

  A  the learned field with the paper's sampler: Euler, 50 steps in t, to T = 1 - 1e-3;
  B  the learned field with RK4 in tau = -log(1-t) at steps DTAU and 2 DTAU, to eps in EPS_OUT;
  C  the exact field of the training set (Theorem thm:endpoint): the Nadaraya-Watson kernel field
     at h > 0, in float64, with the same RK4; at h = 0 the exact flow t a + (1-t) x0.

so that the off-atom share at T = 1 - 1e-3 splits into discretisation (A - B), learned-field
error (B - C) and truncation (C at 1e-3 against C at the last cutoff, whose limit is atomic).
"On an atom" is d1/d2 < 1/3 for the nearest and second-nearest image, over the run's 2000
training images and, as in scripts/grid_nearest_training_image.py, over all 50000 CIFAR-10
training images. Paired: does the learned sample sit on the same atom as the exact one?

Along the flows it also records the EXP-B quantities (scripts/exp_b_transfer_exp1.py):
r(t) = E|Delta(Y_t)|^2 on the exact flow and m(t) = E|Delta(Z_t)|^2 on the learned one,
Delta = v_theta - v*, and, for the exact field, beta tr Cov of its posterior (an upper bound on
its Jacobian) times DTAU_EXACT, the RK4 stability check.

    python -u -m scripts.exp_c_cifar_transfer --runs exp3_cifar_heff_h6_s0
    python -u -m scripts.exp_c_cifar_transfer --summarize
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import pickle
import sys
import time

import numpy as np
import torch

from src.problems.inpainting import InpaintingProblem
from src.train_exp3 import cond_vectors
from src.utils import load_yaml

EXP3 = pathlib.Path("results/exp3")
OUT = pathlib.Path("results/exp_c_cifar_transfer_20261022")
RUNS = [f"exp3_cifar_heff_h{h}_s{s}" for h in (6, 0, 4, 5) for s in (0, 1, 2)]
N_COND, M = 48, 16
SOURCE_SEED = 20261022
EPS_OUT = (1e-2, 1e-3, 1e-4)
DTAU = 0.02                          # learned field (checked against 2 DTAU)
DTAU_EXACT = 0.005                   # exact field: beta tr Cov * dtau must stay below RK4's 2.8
GRID_EVERY = 0.25                    # tau spacing of the r(t), m(t) records
RATIO = 1.0 / 3.0
MICRO = 128                          # U-Net micro-batch


def build_unet(cfg, C, device):
    from src.models.unet import UNet
    m = cfg["model"]
    return UNet(in_channels=2 * C + 1, out_channels=C, base=m.get("base", 128),
                ch_mult=tuple(m.get("ch_mult", [1, 2, 2, 2])), num_res_blocks=m.get("num_res_blocks", 2),
                attn_resolutions=tuple(m.get("attn_resolutions", [16])),
                temb_dim=m.get("temb_dim", 512)).to(device)


@torch.no_grad()
def velocity(model, x, t, cond):
    """v_theta in micro-batches; x (n, C, 32, 32) float32, t (n,), cond (n, C+1, 32, 32)."""
    return torch.cat([model(x[i:i + MICRO], t[i:i + MICRO], cond[i:i + MICRO])
                      for i in range(0, len(x), MICRO)])


def exact_mean(Xflat, Yvec, y_rows, h, s0):
    """m*(x, t) at the rows' conditions, float64: posterior mean of the atoms (h > 0)."""
    sq_atoms = (Xflat ** 2).sum(1)
    label_logit = -torch.cdist(y_rows, Yvec) ** 2 / (2 * h ** 2)          # (n, N), fixed per row

    def m(x, t):
        eps = 1 - t
        d2 = (x ** 2).sum(1, keepdim=True) - 2 * t * x @ Xflat.T + t ** 2 * sq_atoms[None]
        w = torch.softmax(label_logit - d2 / (2 * s0 ** 2 * eps ** 2), 1)
        return w @ Xflat, w
    return m


def rk4_tau(f, x0, taus, dtau):
    """RK4 in tau for dx/dtau = f(x, tau); states at the increasing taus."""
    x, tau, out = x0.clone(), 0.0, []
    for te in taus:
        k = max(1, math.ceil((te - tau) / dtau)); hh = (te - tau) / k
        for _ in range(k):
            k1 = f(x, tau); k2 = f(x + hh / 2 * k1, tau + hh / 2)
            k3 = f(x + hh / 2 * k2, tau + hh / 2); k4 = f(x + hh * k3, tau + hh)
            x = x + hh / 6 * (k1 + 2 * k2 + 2 * k3 + k4); tau += hh
        tau = te
        out.append(x.clone())
    return out


def nn_ratio(states, ref, chunk=2500):
    """d1/d2 and the nearest index of each flattened state among the reference images."""
    d1 = torch.full((len(states),), math.inf, device=states.device); d2 = d1.clone()
    i1 = torch.zeros(len(states), dtype=torch.long, device=states.device)
    for s in range(0, len(ref), chunk):
        d = torch.cdist(states.float(), ref[s:s + chunk].float())         # (n, chunk)
        v, j = d.topk(2, dim=1, largest=False)
        for col in range(2):
            better = v[:, col] < d1
            d2 = torch.where(better, d1, torch.minimum(d2, v[:, col]))
            i1 = torch.where(better, j[:, col] + s, i1)
            d1 = torch.where(better, v[:, col], d1)
    return d1 / d2, i1


def cifar_all(root, device):
    xs = []
    for i in range(1, 6):
        with open(pathlib.Path(root) / "cifar-10-batches-py" / f"data_batch_{i}", "rb") as f:
            xs.append(pickle.load(f, encoding="bytes")[b"data"])
    x = torch.from_numpy(np.concatenate(xs)).to(device).float() / 255.0 * 2 - 1   # (50000, 3072), CHW
    return x


def evaluate(run, ck, device, cifar50k):
    cfg = load_yaml(EXP3 / run / "config.yaml")
    dc = cfg["data"]
    problem = InpaintingProblem.create(N=dc["N"], seed=cfg["seed"], data_root=dc.get("data_root", "data"),
                                       mask_kind=dc.get("mask_kind", "bottom_half"), dataset=dc["dataset"],
                                       cond_kind=dc.get("cond_kind", "inpaint"))
    C, s0, h = problem.channels, float(dc.get("source_std", 1.0)), float(cfg["train"]["y_noise_h"])
    model = build_unet(cfg, C, device)
    model.load_state_dict(torch.load(ck, map_location=device, weights_only=False)["model_state"])  # our own file
    model.eval()
    Xflat = problem.X.flatten(1).to(device, torch.float64)
    Yvec = cond_vectors(problem).to(device, torch.float64)
    idx = sorted(set(np.linspace(0, problem.N - 1, N_COND).round().astype(int).tolist()))
    rows = torch.tensor(idx, device=device).repeat_interleave(M)
    cond = problem.condition(problem.X[idx]).to(device).repeat_interleave(M, 0)
    x0 = s0 * torch.randn(len(idx) * M, C, 32, 32, generator=torch.Generator().manual_seed(SOURCE_SEED)).to(device)
    shape = x0.shape

    def learned_f(x, tau):
        eps = math.exp(-tau)
        t = torch.full((len(x),), 1 - eps, device=device)
        return eps * velocity(model, x, t, cond)

    def euler50():
        x, ts = x0.clone(), torch.linspace(0.0, 1.0 - 1e-3, 51)
        for i in range(50):
            x = x + float(ts[i + 1] - ts[i]) * velocity(model, x, torch.full((len(x),), float(ts[i]), device=device), cond)
        return x

    taus_out = [math.log(1 / e) for e in EPS_OUT]
    grid = sorted(set(np.round(np.arange(GRID_EVERY, taus_out[-1], GRID_EVERY), 6).tolist()) | set(taus_out))
    start = time.time()
    A = euler50()
    B = rk4_tau(learned_f, x0, grid, DTAU)
    B2 = rk4_tau(learned_f, x0, taus_out, 2 * DTAU)
    print(f"  learned flows {time.time()-start:.0f}s", flush=True)

    m_star = exact_mean(Xflat, Yvec, Yvec[rows], h, s0) if h > 0 else None
    stab = []
    if h > 0:
        def exact_f(x, tau):
            t = -math.expm1(-tau)
            m, w = m_star(x.flatten(1).double(), t)
            beta = t / math.exp(-2 * tau)
            cov_tr = (w * (Xflat ** 2).sum(1)[None]).sum(1) - (m ** 2).sum(1)
            stab.append(float(beta * cov_tr.max()) * DTAU_EXACT)
            return (m.view(shape) - x.double())
        Cx = rk4_tau(exact_f, x0.double(), grid, DTAU_EXACT)
    else:
        a = Xflat[rows].view(shape)
        Cx = [(-math.expm1(-tg)) * a + math.exp(-tg) * x0.double() for tg in grid]
    print(f"  exact flow {time.time()-start:.0f}s", flush=True)

    def mean_star(x, tau):
        t = -math.expm1(-tau)
        if h > 0:
            return m_star(x.flatten(1).double(), t)[0]
        return Xflat[rows]

    def mean_hat(x, tau):
        return (x + learned_f(x.float(), tau)).flatten(1).double()

    # r(t), m(t) on the grid: Delta = (m_hat - m*)/eps
    r_t, m_t = [], []
    for j, tg in enumerate(grid):
        eps = math.exp(-tg)
        m_t.append(float(((mean_hat(B[j], tg) - mean_star(B[j], tg)) ** 2).sum(1).mean()) / eps ** 2)
        r_t.append(float(((mean_hat(Cx[j].float(), tg) - mean_star(Cx[j], tg)) ** 2).sum(1).mean()) / eps ** 2)

    def atom_stats(x):
        flat = x.flatten(1)
        r_run, i_run = nn_ratio(flat, Xflat)
        r_all, _ = nn_ratio(flat, cifar50k)
        return {"on_atom_run": float((r_run < RATIO).float().mean()),
                "on_atom_50k": float((r_all < RATIO).float().mean()),
                "median_ratio_run": float(r_run.median())}, i_run

    res = {"run": run, "h": h, "checkpoint": int(ck.stem[5:]), "n_conditions": len(idx), "M": M,
           "grid_tau": grid, "r": r_t, "m": m_t,
           "exact_rk4_max_beta_trcov_dtau": max(stab) if stab else 0.0, "cutoffs": []}
    jA = grid.index(taus_out[1])
    sA, iA = atom_stats(A)
    res["euler50_T1e-3"] = sA
    for k, e in enumerate(EPS_OUT):
        j = grid.index(taus_out[k])
        sB, iB = atom_stats(B[j])
        sB2, iB2 = atom_stats(B2[k])
        sC, iC = atom_stats(Cx[j])
        res["cutoffs"].append({"eps": e, "learned": sB, "learned_2dtau": sB2, "exact": sC,
                               "same_atom_learned_exact": float((iB == iC).float().mean()),
                               "same_atom_learned_2dtau": float((iB == iB2).float().mean()),
                               "dist_learned_exact_rmse": float(((B[j].double() - Cx[j]) ** 2).flatten(1).mean(1).sqrt().mean())})
    res["same_atom_euler50_exact_1e-3"] = float((iA == atom_stats(Cx[jA])[1]).float().mean())
    return res


def run(names, ckpt_iter, device):
    cifar50k = cifar_all("data", device)
    for name in names:
        ck = EXP3 / name / "checkpoints" / f"ckpt_{ckpt_iter}.pt"
        out = OUT / name / f"ckpt_{ckpt_iter}.json"
        if out.exists() or not ck.exists():
            continue
        start = time.time()
        print(f"{name} ckpt {ckpt_iter}", flush=True)
        res = evaluate(name, ck, device, cifar50k)
        res.update(seconds=time.time() - start, dtau=DTAU, dtau_exact=DTAU_EXACT, eps_out=EPS_OUT, source_seed=SOURCE_SEED,
                   torch=torch.__version__, python=sys.version)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(res), encoding="utf-8")
        c = res["cutoffs"][1]
        print(f"  off-atom (run, 50k) at T=1-1e-3: Euler50 {1-res['euler50_T1e-3']['on_atom_run']:.3f}/"
              f"{1-res['euler50_T1e-3']['on_atom_50k']:.3f}  RK4 {1-c['learned']['on_atom_run']:.3f}/"
              f"{1-c['learned']['on_atom_50k']:.3f}  exact {1-c['exact']['on_atom_run']:.3f}/"
              f"{1-c['exact']['on_atom_50k']:.3f}  same atom {c['same_atom_learned_exact']:.3f}  "
              f"{res['seconds']:.0f}s", flush=True)


def summarize():
    recs = [json.loads(p.read_text()) for p in sorted(OUT.glob("*/ckpt_*.json"))]
    fmt = lambda v: f"{np.mean(v):.3f} ± {np.std(v):.3f}"             # noqa: E731
    L = ["# EXP-C: decomposing the off-atom CIFAR-10 samples", "",
         f"{N_COND} conditions x {M} shared sources per run; mean ± sd over seeds. Off-atom = 1 - share with "
         "d1/d2 < 1/3 (over the run's 2000 training images | over all 50000 CIFAR-10 images).", "",
         "| h | ckpt | Euler 50, T=1-1e-3 | learned RK4, 1e-3 | exact, 1e-3 | exact, 1e-4 | learned RK4, 1e-4 | "
         "same atom as exact (1e-3) | K at 1-t≈1e-3 |", "|---|---|---|---|---|---|---|---|---|"]
    for h in sorted({r["h"] for r in recs}):
        for ck in sorted({r["checkpoint"] for r in recs if r["h"] == h}):
            rs = [r for r in recs if r["h"] == h and r["checkpoint"] == ck]
            off = lambda get: f"{fmt([1 - get(r)['on_atom_run'] for r in rs])} \\| {fmt([1 - get(r)['on_atom_50k'] for r in rs])}"  # noqa: E731
            K = []
            for r in rs:
                g = np.array(r["grid_tau"]); j = int(np.argmin(np.abs(g - math.log(1e3))))
                K.append(r["m"][j] / r["r"][j] if r["r"][j] > 0 else float("nan"))
            L.append(f"| {h:g} | {ck} | {off(lambda r: r['euler50_T1e-3'])} | {off(lambda r: r['cutoffs'][1]['learned'])} | "
                     f"{off(lambda r: r['cutoffs'][1]['exact'])} | {off(lambda r: r['cutoffs'][2]['exact'])} | "
                     f"{off(lambda r: r['cutoffs'][2]['learned'])} | {fmt([r['cutoffs'][1]['same_atom_learned_exact'] for r in rs])} | "
                     f"{fmt(K)} |")
    L += ["", "Solver checks: largest beta tr Cov * dtau of the exact field along its RK4 path (stable below 2.8): "
          f"{max((r['exact_rk4_max_beta_trcov_dtau'] for r in recs), default=float('nan')):.3g}; learned RK4 at dtau "
          f"and 2 dtau agree on the nearest atom for at least "
          f"{min((c['same_atom_learned_2dtau'] for r in recs for c in r['cutoffs']), default=float('nan')):.3f} of samples.", ""]
    (OUT / "SUMMARY.md").write_text("\n".join(L), encoding="utf-8")
    print("wrote", OUT / "SUMMARY.md")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", default=RUNS)
    ap.add_argument("--checkpoint", type=int, default=60000)
    ap.add_argument("--summarize", action="store_true")
    args = ap.parse_args()
    if args.summarize:
        summarize()
    else:
        run(args.runs, args.checkpoint, "cuda" if torch.cuda.is_available() else "cpu")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
